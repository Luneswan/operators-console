"""Application bootstrap."""
from __future__ import annotations

import hashlib
import sys
import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .version import APP_ID, APP_NAME, ORG_NAME, __version__

#: What a second copy sends the first. The content does not matter; that a
#: connection arrived at all is the message.
RAISE = b"raise"

#: How long a second copy waits for the first to answer. Long enough for a
#: busy machine, short enough that a stale socket never delays a launch.
HANDOVER_MS = 400

#: The file that decides which of two copies started together is the one.
LOCK_NAME = "instance.lock"

#: How long a copy that finds another one still starting waits for it to
#: answer before carrying on alone. The owner listens within milliseconds of
#: taking the lock, so this is only ever reached when something is wrong.
STARTUP_WAIT_S = 10.0


def instance_key(data_dir=None) -> str:
    """The name of this data folder's socket.

    Derived from the folder rather than from the application, so a portable
    copy pointed at its own ``OPERATORS_CONSOLE_HOME`` is a separate instance
    and is allowed to run beside an installed one. Two copies sharing one
    SQLite file are not: settings are last-writer-wins, and the older copy
    silently overwrote what the newer one had just saved.
    """
    from .core import paths
    if data_dir is None:
        data_dir = paths.data_dir()
    digest = hashlib.sha256(str(data_dir).encode("utf-8", "replace"))
    return "%s-%s" % (APP_ID, digest.hexdigest()[:16])


def hand_over(key: str, timeout_ms: int = HANDOVER_MS) -> bool:
    """Ask a copy already running on this data folder to come forward.

    True when one answered, which means this copy should exit without opening
    anything. Any failure at all is False: the socket machinery must never be
    the reason the app will not start.
    """
    try:
        from PySide6.QtNetwork import QLocalSocket
        socket = QLocalSocket()
        socket.connectToServer(key)
        if not socket.waitForConnected(timeout_ms):
            return False
        socket.write(RAISE)
        socket.waitForBytesWritten(timeout_ms)
        socket.disconnectFromServer()
        return True
    except Exception:
        return False


def listen_for_raise(key: str, on_raise):
    """Hold the socket for this data folder and answer the next copy.

    Returns the server, or None when it could not be held - in which case the
    app carries on alone, exactly as it did before any of this existed.
    """
    try:
        from PySide6.QtNetwork import QLocalServer

        # A crash leaves the socket file behind on Unix, and listen() then
        # fails forever. Nothing else may own this name, so removing it is
        # safe.
        QLocalServer.removeServer(key)
        server = QLocalServer()
        server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        if not server.listen(key):
            return None

        def greet() -> None:
            connection = server.nextPendingConnection()
            if connection is None:
                return

            def answer() -> None:
                if connection.property("answered"):
                    return          # the message and the hang-up both arrive
                connection.setProperty("answered", True)
                connection.deleteLater()
                try:
                    on_raise()
                except Exception:
                    pass

            connection.readyRead.connect(answer)
            connection.disconnected.connect(answer)

        server.newConnection.connect(greet)
        return server
    except Exception:
        return None


class Claim:
    """This copy's hold on its data folder: the lock and the socket."""

    def __init__(self, lock=None, server=None):
        self.lock = lock
        self.server = server

    def release(self) -> None:
        try:
            if self.server is not None:
                self.server.close()
        except Exception:
            pass
        try:
            if self.lock is not None:
                self.lock.unlock()
        except Exception:
            pass


def _lock_file(path):
    """A QLockFile for *path*, or None if one cannot be made."""
    try:
        from PySide6.QtCore import QLockFile
        lock = QLockFile(str(path))
        # Never stale by age: the app stays open for hours. A lock whose
        # process has died is still recognised as stale and taken over.
        lock.setStaleLockTime(0)
        return lock
    except Exception:
        return None


def claim_instance(key: str, lock_path, on_raise,
                   wait_s: float = STARTUP_WAIT_S):
    """Become the one copy for this data folder, or hand over to it.

    Returns a Claim when this copy should open, or None when another copy
    answered and this one should exit.

    Asking the socket alone is not enough. Two copies started within
    milliseconds of each other - an old build's updater and the installer
    both reopening the app, or an impatient double-click - both find nobody
    listening, because the first does not listen until its window is built.
    So the copy that takes the lock file listens at once, before it opens the
    database, and a copy that finds the lock taken waits for that socket to
    answer instead of opening beside it.

    Like the socket, the lock may never be the reason the app will not start:
    if it cannot be used, or the owner never answers, this copy carries on.
    """
    if hand_over(key):
        return None

    def own(lock):
        return Claim(lock, listen_for_raise(key, on_raise))

    lock = _lock_file(lock_path)
    if lock is None:
        return own(None)
    try:
        if lock.tryLock(0):
            return own(lock)
        from PySide6.QtCore import QLockFile
        if lock.error() != QLockFile.LockError.LockFailedError:
            return own(None)            # permissions, a full disk: carry on
    except Exception:
        return own(None)

    # Another live copy holds the lock and is on its way up.
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        if hand_over(key, timeout_ms=250):
            return None
        try:
            if lock.tryLock(0):         # it gave up, or closed, meanwhile
                return own(lock)
        except Exception:
            break
        time.sleep(0.05)
    # Open, but do not listen: listening would take the socket name away
    # from the copy that holds the lock.
    return Claim()


def raise_window(window) -> None:
    """Bring the copy that is already running to the front."""
    try:
        if window.isMinimized() or not window.isVisible():
            window.showNormal()
        window.raise_()
        window.activateWindow()
    except Exception:
        pass


def run(argv=None) -> int:
    argv = list(argv or [])

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(__version__)
    QApplication.setOrganizationName(ORG_NAME)
    QApplication.setDesktopFileName(APP_ID)

    app = QApplication(sys.argv[:1] + argv)
    app.setStyle("Fusion")

    from .core import paths
    icon_file = paths.icon_path()
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    # One copy per data folder. Settled before the database is opened, so a
    # second copy never joins the first on the same SQLite file: both would
    # write settings, and the last writer won.
    shown = []

    def come_forward() -> None:
        if shown:                   # a copy still starting shows itself anyway
            raise_window(shown[0])

    try:
        data = paths.data_dir()
        key = instance_key(data)
        lock_path = data / LOCK_NAME
    except Exception:
        key, lock_path = "", None
    claim = (claim_instance(key, lock_path, come_forward) if key
             else Claim())
    if claim is None:
        return 0
    try:
        return _open(app, shown)
    finally:
        claim.release()


def _open(app, shown) -> int:
    """Open the database and the window, then run until the app quits."""
    from .core.storage import Store
    from .ui.context import AppContext
    from .ui.main_window import MainWindow
    from .ui.onboarding import Onboarding

    try:
        store = Store()
    except Exception as exc:
        QMessageBox.critical(
            None, APP_NAME,
            "Your progress database could not be opened.\n\n%s\n\n"
            "The file is in your application data folder. Move it aside and "
            "restart to begin again, or restore a backup." % exc)
        return 1

    try:
        ctx = AppContext(store=store)
    except Exception as exc:
        # Something in the stored progress the app cannot work with. Say so,
        # rather than vanishing without a window.
        QMessageBox.critical(
            None, APP_NAME,
            "Your progress could be opened but not read.\n\n%s\n\n"
            "Restore a snapshot from the backups folder, or move the "
            "database aside to begin again." % exc)
        store.close()
        return 1
    ctx.set_dark_hint(_system_is_dark(app))
    app.styleHints().colorSchemeChanged.connect(
        lambda _s: ctx.set_dark_hint(_system_is_dark(app)))

    window = MainWindow(ctx)
    window.show()
    # The socket has been listening since before the database was opened;
    # from here on a later launch brings this window forward.
    shown.append(window)
    # An update leaves a copy of its helper behind, and a failed one its
    # package; clear them once the window is up, so the cleanup never
    # delays the first paint.
    from PySide6.QtCore import QTimer
    from .core import updates
    QTimer.singleShot(3000, updates.tidy_staging)
    QTimer.singleShot(5000, lambda: _daily_snapshot(store))

    if not store.setting("onboarded", False):
        Onboarding(ctx, window).exec()
        window.go("today")

    return app.exec()


def _daily_snapshot(store) -> None:
    """One automatic copy a day. A snapshot must never break a session."""
    if not getattr(store, "is_open", False):
        return
    try:
        store.backup_daily()
    except Exception:
        pass


def _system_is_dark(app) -> bool:
    try:
        return app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except AttributeError:
        return False
