"""Going back to an earlier point: the list of snapshots and one button.

A restore replaces everything, so it gets a window of its own - but not a
second "are you sure?" on top. The current state is snapshotted before the
restore runs, which makes the restore itself undoable the same way.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox,
    QVBoxLayout,
)

from ..core import paths
from ..core.storage import Store, describe_snapshot
from .widgets.common import button, label, muted


def snapshot_title(snapshot) -> str:
    when, why = describe_snapshot(snapshot)
    if when is None:
        return why
    return "%s, %s  -  %s" % (when.strftime("%a %d %b %Y"),
                              when.strftime("%H:%M"), why)


def snapshot_contents(summary) -> str:
    if summary is None:
        return "Cannot be read - it may be damaged."
    return "%d ticked  -  %d exercises passed  -  %d projects shipped" % (
        summary["ticked"], summary["exercises"], summary["projects"])


class SnapshotDialog(QDialog):
    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.restored = None
        self.setWindowTitle("Restore a snapshot")
        self.setModal(True)
        self.setMinimumWidth(560)

        column = QVBoxLayout(self)
        column.setContentsMargins(26, 22, 26, 20)
        column.setSpacing(12)
        column.addWidget(label("YOUR SNAPSHOTS", "PageKicker", wrap=False))
        column.addWidget(label("Go back to an earlier point", "PageTitle"))
        column.addWidget(muted(
            "The app takes one each day you open it, and before every reset, "
            "import or upgrade. Restoring replaces your current progress. The "
            "current state is snapshotted first, so a restore can be undone. "
            "Settings are not changed."))

        self.list = QListWidget()
        self.list.setObjectName("SnapshotList")
        self.list.setMinimumHeight(260)
        self.list.itemDoubleClicked.connect(lambda _item: self._restore())
        self.list.currentItemChanged.connect(lambda *_: self._sync())
        column.addWidget(self.list, 1)
        self.empty = muted(
            "No snapshots yet. The first is taken a few seconds after the app "
            "opens.")
        column.addWidget(self.empty)

        row = QHBoxLayout()
        row.setSpacing(8)
        folder = button("Open the backups folder", "quiet")
        folder.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(paths.backups_dir()))))
        row.addWidget(folder)
        row.addStretch(1)
        cancel = button("Cancel", "quiet")
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)
        self.restore_button = button("Restore this snapshot", "primary")
        self.restore_button.clicked.connect(self._restore)
        row.addWidget(self.restore_button)
        column.addLayout(row)
        self._fill()

    def _fill(self) -> None:
        self.list.clear()
        for snapshot in Store.snapshots():
            item = QListWidgetItem("%s\n%s" % (
                snapshot_title(snapshot),
                snapshot_contents(Store.snapshot_summary(snapshot))))
            item.setData(Qt.ItemDataRole.UserRole, str(snapshot))
            self.list.addItem(item)
        has_any = self.list.count() > 0
        self.list.setVisible(has_any)
        self.empty.setVisible(not has_any)
        if has_any:
            self.list.setCurrentRow(0)
        self._sync()

    def _sync(self) -> None:
        self.restore_button.setEnabled(self.list.currentItem() is not None)

    def selected(self):
        item = self.list.currentItem()
        return Path(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def _restore(self) -> None:
        snapshot = self.selected()
        if snapshot is None:
            return
        try:
            self.ctx.store.restore_snapshot(snapshot)
        except (OSError, ValueError, sqlite3.Error) as exc:
            QMessageBox.warning(self, "Restore failed", str(exc))
            self._fill()
            return
        self.restored = snapshot
        self.accept()
