"""The snapshot controls, driven the way a learner would use them."""
from __future__ import annotations

from datetime import datetime as real_datetime, timedelta

import pytest
from PySide6.QtWidgets import QMessageBox

from conftest import pump

from operators_console.core import paths, storage
from operators_console.core.storage import Store
from operators_console.ui import snapshots
from operators_console.ui.snapshots import SnapshotDialog


@pytest.fixture
def clock(monkeypatch):
    state = {"now": real_datetime(2026, 9, 1, 9, 0, 0)}

    class Clock(real_datetime):
        @classmethod
        def now(cls, tz=None):
            state["now"] += timedelta(minutes=1)
            value = state["now"]
            return value.replace(tzinfo=tz) if tz else value

    monkeypatch.setattr(storage, "datetime", Clock)


def _settings(qt_app, window):
    window.go("settings")
    pump(qt_app)
    return window.views["settings"]


def _choose(monkeypatch, pick):
    """Stand in for the modal loop: pick a row, press Restore."""
    seen = {}

    def run(dialog):
        seen["rows"] = [dialog.list.item(i).text()
                        for i in range(dialog.list.count())]
        row = pick(dialog)
        if row is None:
            return SnapshotDialog.DialogCode.Rejected
        dialog.list.setCurrentRow(row)
        dialog.restore_button.click()
        return dialog.result()
    monkeypatch.setattr(SnapshotDialog, "exec", run)
    return seen


def test_snapshot_now_takes_one(qt_app, window):
    view = _settings(qt_app, window)
    said = []
    window.ctx.toast.connect(said.append)
    view.snapshot_button.click()
    assert [p for p in Store.snapshots() if p.name.endswith("-manual.db")]
    assert said and "Snapshot saved" in said[-1]


def test_a_reset_is_undone_from_settings(qt_app, window, store, clock,
                                         monkeypatch):
    store.set_checked("p01.s0.0", True)
    view = _settings(qt_app, window)
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    view._reset()
    assert not store.is_checked("p01.s0.0")

    seen = _choose(monkeypatch, lambda d: next(
        i for i in range(d.list.count())
        if "before a progress reset" in d.list.item(i).text()))
    said = []
    window.ctx.toast.connect(said.append)
    view.restore_snapshot()

    assert store.is_checked("p01.s0.0")
    assert any("1 ticked" in row for row in seen["rows"])
    assert said and said[-1].startswith("Restored: ")


def test_the_list_is_newest_first_and_says_what_each_holds(qt_app, window,
                                                           store, clock,
                                                           monkeypatch):
    store.backup(tag="manual")
    store.set_checked("p01.s0.0", True)
    store.backup(tag="daily")
    seen = _choose(monkeypatch, lambda d: None)
    _settings(qt_app, window).restore_snapshot()
    assert "Daily automatic snapshot" in seen["rows"][0]
    assert "1 ticked" in seen["rows"][0]
    assert "Snapshot you took" in seen["rows"][1]
    assert "0 ticked" in seen["rows"][1]


def test_no_snapshots_says_so_and_offers_nothing_to_press(qt_app, window,
                                                          monkeypatch):
    seen = {}

    def run(dialog):
        seen["empty"] = dialog.empty.isVisibleTo(dialog)
        seen["enabled"] = dialog.restore_button.isEnabled()
        return SnapshotDialog.DialogCode.Rejected
    monkeypatch.setattr(SnapshotDialog, "exec", run)
    _settings(qt_app, window).restore_snapshot()
    assert seen == {"empty": True, "enabled": False}


def test_a_damaged_snapshot_is_labelled_and_refused(qt_app, window, store,
                                                    monkeypatch):
    broken = paths.backups_dir() / "progress-20260901-090000-manual.db"
    broken.write_bytes(b"garbage" * 300)
    store.set_checked("p01.s0.0", True)
    warned = []
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: warned.append(a))
    seen = _choose(monkeypatch, lambda d: 0)
    _settings(qt_app, window).restore_snapshot()

    assert "Cannot be read" in seen["rows"][0]
    assert warned, "a failed restore said nothing"
    assert store.is_checked("p01.s0.0")


def test_cancel_changes_nothing(qt_app, window, store, clock, monkeypatch):
    store.backup(tag="manual")
    store.set_checked("p01.s0.0", True)
    _choose(monkeypatch, lambda d: None)
    _settings(qt_app, window).restore_snapshot()
    assert store.is_checked("p01.s0.0")


def test_the_file_menu_can_restore_too(qt_app, window, monkeypatch):
    actions = [a.text() for a in window.menuBar().actions()[0].menu().actions()]
    assert "Restore a snapshot..." in actions
    opened = []
    monkeypatch.setattr(SnapshotDialog, "exec",
                        lambda d: opened.append(1) or 0)
    window._restore_snapshot()
    assert opened == [1] and window.current_key == "settings"


def test_the_daily_snapshot_never_breaks_a_session(store, monkeypatch):
    from operators_console import app

    def boom():
        raise OSError("disk full")
    monkeypatch.setattr(store, "backup_daily", boom)
    app._daily_snapshot(store)              # swallowed
    store.close()
    app._daily_snapshot(store)              # a closed store is skipped


def test_titles_read_like_a_date_not_a_filename():
    title = snapshots.snapshot_title(
        paths.backups_dir() / "progress-20260922-170409-pre-reset.db")
    assert title == ("Tue 22 Sep 2026, 17:04  -  Taken just before a "
                     "progress reset")
