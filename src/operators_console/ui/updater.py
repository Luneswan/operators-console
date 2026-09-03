"""The update button and the dialog behind it.

The check runs on a worker thread at startup and then once a day, so opening
the app is never delayed by the network. When there is nothing to install the
button does not exist, which keeps the chrome quiet.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QProgressBar, QVBoxLayout,
)

from ..core import updates
from ..version import __version__
from .widgets.common import button, divider, label, muted


class _CheckSignals(QObject):
    done = Signal(object)


class _CheckJob(QRunnable):
    """One release lookup, off the interface thread."""

    def __init__(self) -> None:
        super().__init__()
        self.signals = _CheckSignals()

    def run(self) -> None:
        try:
            release = updates.fetch_latest()
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


class UpdateManager(QObject):
    """Owns the check schedule and hands the window something to show."""

    available = Signal(object)

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.release = None
        self.pool = QThreadPool.globalInstance()

    def maybe_check(self, force: bool = False) -> None:
        if not force:
            if not self.ctx.store.setting("check_for_updates", True):
                return
            if not updates.can_self_update():
                return
            today = date.today().isoformat()
            if self.ctx.store.setting("last_update_check", "") == today:
                return
        self.ctx.store.set_setting("last_update_check", date.today().isoformat())
        job = _CheckJob()
        job.signals.done.connect(self._on_result)
        self.pool.start(job)

    def _on_result(self, release) -> None:
        if updates.is_newer(release):
            self.release = release
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
                "This release has no download for your platform yet. It is "
                "worth checking the releases page directly.", "Soft"))
        else:
            size = self.asset.size / (1024 * 1024)
            column.addWidget(label(
                "The app will download %s (%.0f MB), install it, and reopen "
                "itself on the new version. Your progress is untouched."
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
        self.status.setText("Installing. The app will reopen by itself.")
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
        from PySide6.QtWidgets import QApplication
        window = self.parent()
        if window is not None:
            window.close()
        QApplication.instance().quit()

    def reject(self) -> None:
        if self.job is not None:
            self.job.cancel()
        super().reject()
