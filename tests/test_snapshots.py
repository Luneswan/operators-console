"""Snapshots: taken automatically, kept sensibly, and restorable from the app.

Before 2026-09-22 the app took a copy of the database before every reset,
import and upgrade - then told the learner the reset "cannot be undone from
inside the app", because nothing could read those copies back.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime as real_datetime, timedelta

import pytest

from operators_console.core import paths, storage
from operators_console.core.storage import Store, describe_snapshot


@pytest.fixture
def clock(monkeypatch):
    """A clock that moves one minute per call, so every snapshot has a name."""
    state = {"now": real_datetime(2026, 9, 1, 9, 0, 0)}

    class Clock(real_datetime):
        @classmethod
        def now(cls, tz=None):
            state["now"] += timedelta(minutes=1)
            value = state["now"]
            return value.replace(tzinfo=tz) if tz else value

    monkeypatch.setattr(storage, "datetime", Clock)
    return state


def _names():
    return [p.name for p in Store.snapshots()]


def test_the_daily_snapshot_is_taken_once_a_day(store, monkeypatch):
    first = store.backup_daily()
    assert first is not None and first.name.endswith("-daily.db")
    assert store.backup_daily() is None

    class Tomorrow(storage.date):
        @classmethod
        def today(cls):
            return real_datetime.now().date() + timedelta(days=1)
    monkeypatch.setattr(storage, "date", Tomorrow)
    assert store.backup_daily() is not None


def test_a_week_of_daily_snapshots_never_pushes_out_the_one_before_a_reset(
        store, clock):
    store.set_checked("p01.s0.0", True)
    store.reset_progress()
    for _ in range(20):
        store.backup(tag="daily")
    names = _names()
    assert sum(n.endswith("-daily.db") for n in names) == Store.KEEP_DAILY
    assert any(n.endswith("-pre-reset.db") for n in names)


def test_other_snapshots_keep_the_last_twelve(store, clock):
    for _ in range(15):
        store.backup(tag="manual")
    for _ in range(3):
        store.backup(tag="daily")
    names = _names()
    assert sum(n.endswith("-manual.db") for n in names) == Store.KEEP_SNAPSHOTS
    assert sum(n.endswith("-daily.db") for n in names) == 3


def test_a_reset_can_be_undone_by_restoring_its_snapshot(store, clock):
    store.set_checked("p01.s0.0", True)
    store.set_project("p01.proj", status="shipped", notes="my notes")
    store.reset_progress()
    assert not store.is_checked("p01.s0.0")
    before_reset = next(p for p in Store.snapshots()
                        if p.name.endswith("-pre-reset.db"))

    store.restore_snapshot(before_reset)

    assert store.is_checked("p01.s0.0")
    assert store.project("p01.proj")["notes"] == "my notes"
    # ...and the restore itself can be undone the same way.
    assert any(n.endswith("-pre-restore.db") for n in _names())


def test_restoring_an_old_snapshot_upgrades_a_copy_not_the_backup(store,
                                                                  clock):
    store.set_checked("p01.s0.0", True)
    old = store.backup(tag="manual")
    raw = sqlite3.connect(old)
    raw.execute("DROP TABLE meta")          # written before versioning
    raw.commit()
    raw.close()
    untouched = old.read_bytes()

    store.reset_progress()
    store.restore_snapshot(old)

    assert store.is_checked("p01.s0.0")
    assert old.read_bytes() == untouched
    assert not [n for n in _names() if "pre-migration" in n], (
        "opening the copy dropped an extra backup into the real folder")


def test_a_summary_reads_a_snapshot_without_touching_it(store):
    store.set_checked("p01.s0.0", True)
    store.set_checked("p01.s0.1", True)
    store.record_exercise_run("p01.001", "print('hi')", passed=True)
    store.set_project("p01.proj", status="shipped")
    snapshot = store.backup(tag="manual")
    untouched = snapshot.read_bytes()

    assert Store.snapshot_summary(snapshot) == {
        "ticked": 2, "exercises": 1, "projects": 1}
    assert snapshot.read_bytes() == untouched
    assert not list(snapshot.parent.glob(snapshot.name + "-*")), (
        "reading a snapshot left -wal/-shm files beside it")


def test_a_damaged_snapshot_is_refused_with_a_reason(store):
    broken = paths.backups_dir() / "progress-20260901-090000-manual.db"
    broken.write_bytes(b"not a database at all" * 50)
    assert Store.snapshot_summary(broken) is None
    store.set_checked("p01.s0.0", True)
    with pytest.raises(ValueError):
        store.restore_snapshot(broken)
    assert store.is_checked("p01.s0.0"), "a failed restore changed the store"


def test_a_snapshot_that_vanished_is_refused(store, tmp_path):
    with pytest.raises(ValueError, match="no longer"):
        store.restore_snapshot(tmp_path / "gone.db")


def test_snapshots_are_listed_newest_first(store, clock):
    first = store.backup(tag="manual")
    second = store.backup(tag="daily")
    assert Store.snapshots()[:2] == [second, first]


@pytest.mark.parametrize("name, reason", [
    ("progress-20260922-170409.db", "Snapshot"),
    ("progress-20260922-170409-manual.db", "Snapshot you took"),
    ("progress-20260922-170409-daily.db", "Daily automatic snapshot"),
    ("progress-20260922-170409-pre-reset.db",
     "Taken just before a progress reset"),
    ("progress-20260922-170409-pre-restore.db",
     "Taken just before a restore or an import"),
    ("progress-20260922-170409-pre-migration-v1.db",
     "Taken just before an upgrade changed the database"),
])
def test_every_snapshot_says_why_it_exists(name, reason):
    when, why = describe_snapshot(paths.backups_dir() / name)
    assert when == real_datetime(2026, 9, 22, 17, 4, 9)
    assert why == reason


def test_an_oddly_named_file_still_gets_a_description():
    when, why = describe_snapshot(paths.backups_dir() / "progress-x.db")
    assert when is None and why


def test_a_restore_brings_back_progress_but_keeps_todays_preferences(store,
                                                                     clock):
    store.set_setting("onboarded", False)          # the first-day snapshot
    store.set_setting("track", "backend")
    store.set_checked("p01.s0.0", True)
    early = store.backup(tag="daily")
    store.set_setting("onboarded", True)
    store.set_setting("track", "data")
    store.set_setting("theme", "dark")
    store.set_checked("p01.s0.0", False)

    store.restore_snapshot(early)

    assert store.is_checked("p01.s0.0")
    assert store.setting("onboarded") is True
    assert store.setting("track") == "data"
    assert store.setting("theme") == "dark"
