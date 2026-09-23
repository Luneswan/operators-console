"""The update button and the dialog behind it.

The check runs on a worker thread at startup, every few minutes after, and
whenever the window comes back to the front, so opening the app is never
delayed by the network and a new release shows up almost as soon as it is
published. When there is nothing to install the
button does not exist, which keeps the chrome quiet.
"""
from __future__ import annotations

import time
from datetime import date

from PySide6.QtCore import (
    Property, QEasingCurve, QObject, QPropertyAnimation, QRunnable, Qt,
    QThreadPool, QTimer, Signal,
)
from PySide6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QProgressBar, QPushButton, QVBoxLayout,
)

from ..core import updates
from ..version import __version__
from .theme import reduced_motion
from .widgets.common import button, divider, label, muted, open_url, repolish


class _CheckSignals(QObject):
    done = Signal(object)


class _CheckJob(QRunnable):
    """One release lookup, off the interface thread."""

    def __init__(self) -> None:
        super().__init__()
        self.signals = _CheckSignals()

    def run(self) -> None:
        try:
            release = _release_now()
        except Exception:
            release = None
        self.signals.done.emit(release)


class _DownloadSignals(QObject):
    progress = Signal(int, int)
    finished = Signal(object, str)


class _DownloadJob(QRunnable):
    def __init__(self, asset, destination) -> None:
        super().__init__()
        self.signals = _DownloadSignals()
        self.asset = asset
        self.destination = destination
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        try:
            path = updates.download(
                self.asset, self.destination,
                progress=lambda done, total: self.signals.progress.emit(done, total),
                cancelled=lambda: self._cancelled)
        except InterruptedError:
            self.signals.finished.emit(None, "")
        except Exception as exc:
            self.signals.finished.emit(None, "%s" % exc)
        else:
            self.signals.finished.emit(path, "")


# GitHub answers an unchanged release with a 304, which does not count
# against its unauthenticated limit (core.updates keeps the ETag), so the
# only cost of looking often is a few hundred bytes.
POLL_MINUTES = 5
# Coming back to the window looks again, but not on every alt-tab.
REFOCUS_SECONDS = 60


class UpdateManager(QObject):
    """Owns the check schedule and hands the window something to show.

    One look shortly after every launch, one every POLL_MINUTES while the
    window stays open, and one whenever the app comes back to the front
    after REFOCUS_SECONDS away: a release shows up on the button within
    minutes of being published, no restart needed. The same release is
    announced once.
    """

    available = Signal(object)

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.release = None
        self.announced = None
        self.pool = QThreadPool.globalInstance()
        self._poll = QTimer(self)
        self._poll.setInterval(POLL_MINUTES * 60 * 1000)
        self._poll.timeout.connect(self.poll)
        self._poll.start()
        self._last_look = 0.0
        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(self._on_app_state)

    def _on_app_state(self, state) -> None:
        if state != Qt.ApplicationState.ApplicationActive:
            return
        if time.monotonic() - self._last_look < REFOCUS_SECONDS:
            return
        self.poll()

    def latest(self):
        """Ask the core engine what is out there. Blocking - worker only."""
        return _release_now()

    def maybe_check(self, force: bool = False) -> None:
        if not getattr(self.ctx.store, "is_open", True):
            return          # the window closed before the timer came round
        if not force:
            if not self.ctx.store.setting("check_for_updates", True):
                return
            if not updates.can_self_update():
                return
        # Every launch looks: a release published an hour after this
        # morning's check must not wait until tomorrow. The date is kept
        # only as a record of when the app last asked.
        self.ctx.store.set_setting("last_update_check", date.today().isoformat())
        self._start_job()

    def poll(self) -> None:
        """The periodic look while the app is open: never gated by the day."""
        if not getattr(self.ctx.store, "is_open", True):
            return
        if not self.ctx.store.setting("check_for_updates", True):
            return
        if not updates.can_self_update():
            return
        self._start_job()

    def _start_job(self) -> None:
        self._last_look = time.monotonic()
        job = _CheckJob()
        job.signals.done.connect(self._on_result)
        self.pool.start(job)

    def _on_result(self, release) -> None:
        if not updates.is_newer(release):
            return
        if self.announced is not None and self.announced.tag == release.tag:
            return              # already on the button; no second toast
        self.release = release
        self.announced = release
        self.available.emit(release)


class UpdateDialog(QDialog):
    """What the small button opens: what is new, and one button to take it."""

    def __init__(self, ctx, release, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.release = release
        self.job = None
        self.package = None

        self.setWindowTitle("Update available")
        self.setModal(True)
        self.setMinimumWidth(520)

        column = QVBoxLayout(self)
        column.setContentsMargins(26, 22, 26, 20)
        column.setSpacing(12)

        column.addWidget(label("VERSION %s" % release.label, "PageKicker",
                               wrap=False))
        column.addWidget(label(release.name or "A new version is ready",
                               "PageTitle"))
        column.addWidget(muted("You are running %s." % __version__))
        column.addWidget(divider())

        self.asset = updates.pick_asset(release)
        if self.asset is None:
            column.addWidget(label(
                "This release has no download for your platform. Check the "
                "releases page.", "Soft"))
        else:
            size = self.asset.size / (1024 * 1024)
            column.addWidget(label(
                "Downloads %s (%.0f MB), installs it and restarts the app. "
                "Your progress is kept."
                % (self.asset.name, size), "Soft"))

        notes = (release.notes or "").strip()
        if notes:
            trimmed = notes if len(notes) < 700 else notes[:700] + "..."
            body = label(trimmed, "Soft")
            body.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            column.addWidget(body)

        self.status = muted("")
        column.addWidget(self.status)

        self.meter = QProgressBar()
        self.meter.setRange(0, 100)
        self.meter.setTextVisible(False)
        self.meter.setFixedHeight(6)
        self.meter.setVisible(False)
        column.addWidget(self.meter)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.page_button = button("Open the releases page", "quiet")
        self.page_button.clicked.connect(self._open_page)
        row.addWidget(self.page_button)
        row.addStretch(1)
        self.later_button = button("Not now", "quiet")
        self.later_button.clicked.connect(self.reject)
        row.addWidget(self.later_button)
        self.go_button = button("Update and restart", "primary")
        self.go_button.setEnabled(self.asset is not None)
        self.go_button.clicked.connect(self._start)
        row.addWidget(self.go_button)
        column.addLayout(row)

    # -- actions -----------------------------------------------------------

    def _open_page(self) -> None:
        from .widgets.common import open_url
        open_url(self.release.url or
                 "https://github.com/%s/releases" % updates.REPO)

    def _start(self) -> None:
        if self.asset is None:
            return
        self.go_button.setEnabled(False)
        self.later_button.setText("Cancel")
        self.page_button.setEnabled(False)
        self.meter.setVisible(True)
        self.status.setText("Downloading...")

        destination = updates.staging_dir() / self.asset.name
        self.job = _DownloadJob(self.asset, destination)
        self.job.signals.progress.connect(self._on_progress)
        self.job.signals.finished.connect(self._on_downloaded)
        QThreadPool.globalInstance().start(self.job)

    def _on_progress(self, done: int, total: int) -> None:
        if total:
            self.meter.setValue(int(done / total * 100))
        megabytes = done / (1024 * 1024)
        self.status.setText("Downloading... %.0f MB" % megabytes)

    def _on_downloaded(self, path, error: str) -> None:
        if path is None:
            self.meter.setVisible(False)
            self.go_button.setEnabled(True)
            self.later_button.setText("Not now")
            self.page_button.setEnabled(True)
            self.status.setText(
                "The download failed: %s" % error if error
                else "The download was cancelled.")
            return

        self.package = path
        self.status.setText("Installing. The app will restart.")
        self.meter.setRange(0, 0)
        # Give the label a moment to paint before the process goes away.
        QTimer.singleShot(400, self._hand_over)

    def _hand_over(self) -> None:
        try:
            updates.launch_helper(self.package)
        except Exception as exc:
            self.meter.setRange(0, 100)
            self.meter.setVisible(False)
            self.status.setText("Could not start the updater: %s" % exc)
            self.go_button.setEnabled(True)
            return
        self.accept()
        _close_for_restart(self.parent())

    def reject(self) -> None:
        if self.job is not None:
            self.job.cancel()
        super().reject()


# ---------------------------------------------------------------------------
# the one control an update ever needs
# ---------------------------------------------------------------------------

# The core update engine is owned elsewhere. This module only drives it, and
# only through these three names, so the mechanism can change underneath:
#
#   updates.available()             -> a release, or None
#   updates.download(asset, path, progress=cb, cancelled=cb) -> Path
#   updates.apply_and_restart(path) -> hands over and quits
#
# Older names are still accepted while the core side lands, so neither half
# has to wait for the other.

def _release_now():
    fetch = getattr(updates, "available", None) or updates.fetch_latest
    return fetch()


def _close_for_restart(window) -> None:
    """Quit so the helper can swap the build, remembering the open page."""
    if window is not None:
        remember = getattr(window, "remember_place", None)
        if remember is not None:
            try:
                remember()
            except Exception:
                pass        # a lost bookmark must never block the update
        window.close()
    QApplication.instance().quit()


def _hand_over(package) -> None:
    go = getattr(updates, "apply_and_restart", None)
    if go is not None:
        go(package)
        return
    updates.launch_helper(package)


class UpdateButton(QPushButton):
    """One button that carries the whole update, words and all.

    It is invisible until there is something to install. Pressing it turns the
    button itself into the progress meter: a fill behind a label that always
    says, in words, what is happening. Nothing else in the application is
    blocked while it runs, and a failure puts the offer back rather than
    leaving a dead control.
    """

    IDLE, WORKING, FAILED = "idle", "working", "failed"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.release = None
        self.asset = None
        self.job = None
        self.package = None
        self.failure = ""
        self.state = self.IDLE
        self._fill = 0.0
        self.note = None

        self.setObjectName("UpdateButton")
        self.setProperty("kind", "primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setVisible(False)
        self.setMinimumHeight(30)
        self.clicked.connect(self._press)

        self._sweep = QPropertyAnimation(self, b"fill", self)
        self._sweep.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._sweep.setDuration(150)

        self._recover = QTimer(self)
        self._recover.setSingleShot(True)
        self._recover.setInterval(6000)
        self._recover.timeout.connect(self._offer_again)

    def set_note_target(self, label) -> None:
        """A line beneath the button for anything too long to fit on it.

        A 180px button cannot hold "the connection was reset by peer", and
        eliding the reason to nothing is worse than not saying it. The button
        keeps the verb; this line keeps the explanation.
        """
        self.note = label
        self._show_note("")

    def _show_note(self, words: str) -> None:
        if self.note is None:
            return
        self.note.setText(words)
        self.note.setVisible(bool(words))

    # -- the meter drawn inside the button ---------------------------------

    def get_fill(self) -> float:
        return self._fill

    def set_fill(self, value: float) -> None:
        self._fill = max(0.0, min(1.0, float(value)))
        self.update()

    fill = Property(float, get_fill, set_fill)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.state != self.WORKING or self._fill <= 0:
            return
        from PySide6.QtGui import QColor, QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        # A bar along the bottom edge, under the words rather than over
        # them: the translucent overlay dropped the label below 4.5:1.
        tint = QColor(self.ctx.palette.shell)
        tint.setAlpha(210)
        painter.setBrush(tint)
        box = self.rect().adjusted(4, self.height() - 6, -4, -3)
        box.setWidth(max(0, int(box.width() * self._fill)))
        painter.drawRoundedRect(box, 1.5, 1.5)
        painter.end()

    # -- what it says ------------------------------------------------------

    def announce(self, release) -> None:
        """A newer version exists: make the offer, in words, with its size."""
        self.release = release
        self.asset = updates.pick_asset(release)
        self._offer_again()

    def _offer_again(self) -> None:
        if self.release is None:
            return
        self.state = self.IDLE
        self.set_fill(0.0)
        self.setEnabled(self.asset is not None)
        label_text = "Update to %s" % self.release.label
        self.setText(label_text)
        self._show_note("")
        self.setToolTip(self._summary())
        self.setAccessibleName(label_text)
        self.setAccessibleDescription(self._summary())
        self.setVisible(True)
        repolish(self)

    def _summary(self) -> str:
        if self.asset is None:
            return ("Version %s is out, but there is no download for this "
                    "platform yet." % self.release.label)
        size = self.asset.size / (1024 * 1024)
        notes = (self.release.notes or "").strip().splitlines()
        head = notes[0][:120] if notes else "A new version is ready."
        return ("%s\n\n%.0f MB. Installs and restarts the app. Your progress "
                "is kept." % (head, size))

    def _long_notes(self) -> bool:
        return len((self.release.notes or "").strip()) > 320

    # -- running it --------------------------------------------------------

    def _press(self) -> None:
        if self.state == self.WORKING or self.release is None:
            return
        if self.asset is None:
            open_url(self.release.url or
                     "https://github.com/%s/releases" % updates.REPO)
            return
        if self._long_notes():
            # Only a release with a real changelog earns a window.
            UpdateDialog(self.ctx, self.release, self.window()).exec()
            return
        self.start()

    def start(self) -> None:
        self._recover.stop()
        self.state = self.WORKING
        self.set_fill(0.0)
        self._say("Starting...")
        destination = updates.staging_dir() / self.asset.name
        self.job = _DownloadJob(self.asset, destination)
        self.job.signals.progress.connect(self._on_progress)
        self.job.signals.finished.connect(self._on_downloaded)
        QThreadPool.globalInstance().start(self.job)

    def _say(self, words: str) -> None:
        self.setText(words)
        self.setToolTip(words)
        self.setAccessibleName(words)
        repolish(self)

    def _on_progress(self, done: int, total: int) -> None:
        megabytes = total / (1024 * 1024) if total else 0
        share = (done / total) if total else 0.0
        if total:
            # The size lives in the tooltip: "Downloading 124 MB... 96%"
            # did not fit a 158px button.
            self._say("Downloading... %d%%" % round(share * 100))
            self.setToolTip("Downloading %.0f MB" % megabytes)
        else:
            self._say("Downloading %.0f MB..." % (done / (1024 * 1024)))
        if reduced_motion():
            self.set_fill(share)
            return
        self._sweep.stop()
        self._sweep.setStartValue(self._fill)
        self._sweep.setEndValue(share)
        self._sweep.start()

    def _on_downloaded(self, path, error: str) -> None:
        if path is None:
            self._fail(error or "the download was cancelled")
            return
        self.package = path
        self.set_fill(1.0)
        self._say("Verifying...")
        QTimer.singleShot(200, self._restart)

    def _restart(self) -> None:
        self._say("Restarting...")
        try:
            _hand_over(self.package)
        except Exception as exc:
            self._fail("%s" % exc)
            return
        _close_for_restart(self.window())

    def _fail(self, why: str) -> None:
        self.state = self.FAILED
        self.set_fill(0.0)
        self.failure = why
        self._say("Try the update again")
        self.setToolTip("Failed: %s." % why)
        self._show_note("Last try failed: %s." % why)
        self.setEnabled(True)
        self.ctx.announce("The update did not install: %s" % why)
        # The offer comes back on its own, so the control is never dead.
        self._recover.start()
