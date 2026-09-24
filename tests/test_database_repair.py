"""A damaged progress file is caught on open and repaired from a snapshot.

Found 09-24 on the owner's machine: two days of changes sat in the
write-ahead log (every update closes the app from outside, before SQLite's
own checkpoint), a damaged page in it made the schema "malformed", and the
file no longer opened. The app now checks the file on open, offers a repair
that keeps everything it can, and checkpoints every few minutes.
"""
from __future__ import annotations

import sqlite3

import pytest

from operators_console.core import paths, storage
from operators_console.core.storage import DamagedDatabase, Store


def _damage_schema(path) -> None:
    """Give sqlite_master a second copy of an index, as the real case had."""
    db = sqlite3.connect(path)
    db.execute("PRAGMA writable_schema=ON")
    row = db.execute("SELECT type,name,tbl_name,rootpage,sql FROM sqlite_master"
                     " WHERE name='reviews_card'").fetchone()
    db.execute("INSERT INTO sqlite_master VALUES (?,?,?,?,?)", row)
    db.commit()
    db.close()


def _seeded(isolated_home):
    store = Store()
    store.set_checked("p01.s0.0", True)
    store.set_setting("learner_name", "Old")
    store.backup(tag="daily")
    store.set_checked("p01.s0.1", True)          # after the snapshot
    store.set_setting("learner_name", "Evan")    # after the snapshot
    store.close()
    return paths.db_path()


def test_a_malformed_schema_is_reported_as_damage(isolated_home):
    path = _seeded(isolated_home)
    _damage_schema(path)
    with pytest.raises(DamagedDatabase):
        Store()


def test_a_file_that_is_not_a_database_is_damage(isolated_home):
    paths.db_path().parent.mkdir(parents=True, exist_ok=True)
    paths.db_path().write_bytes(b"this is not sqlite" * 100)
    with pytest.raises(DamagedDatabase):
        Store()


def test_repair_brings_back_the_snapshot_and_keeps_what_reads(isolated_home):
    path = _seeded(isolated_home)
    _damage_schema(path)
    done = storage.repair()
    assert done["snapshot"].endswith("-daily.db")
    store = Store()                               # opens cleanly again
    try:
        assert store.db.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert store.is_checked("p01.s0.0")       # from the snapshot
        assert store.is_checked("p01.s0.1")       # salvaged, newer
        assert store.setting("learner_name") == "Evan"
        assert store.get_meta("repaired_at")
    finally:
        store.close()
    moved = list((paths.data_dir()).glob("damaged-*/progress.db"))
    assert len(moved) == 1                        # kept, never deleted


def test_repair_without_a_snapshot_still_opens(isolated_home):
    path = _seeded(isolated_home)
    for snap in Store.snapshots():
        snap.unlink()
    _damage_schema(path)
    done = storage.repair()
    assert done["snapshot"] == ""
    store = Store()
    try:
        assert store.setting("learner_name") == "Evan"
    finally:
        store.close()


def test_a_checkpoint_puts_committed_work_in_the_main_file(isolated_home):
    store = Store()
    try:
        store.set_checked("p02.s0.0", True)
        store.checkpoint()
        uri = paths.db_path().resolve().as_uri() + "?immutable=1"
        main_only = sqlite3.connect(uri, uri=True)   # ignores the WAL
        try:
            found = main_only.execute(
                "SELECT 1 FROM checks WHERE item_id='p02.s0.0'").fetchone()
        finally:
            main_only.close()
        assert found is not None
    finally:
        store.close()


def test_the_window_checkpoints_every_five_minutes(qt_app, window):
    assert window._checkpoint_timer.isActive()
    assert window._checkpoint_timer.interval() == 5 * 60 * 1000


# -- explained snippets and the plan's arithmetic ------------------------------

def test_every_snippet_is_explained(curriculum):
    for phase in curriculum.phases:
        if not phase.snippet:
            continue
        assert phase.snippet_title and phase.snippet_intro, phase.id
        assert len(phase.snippet_lines) == len(phase.snippet.splitlines())
        assert sum(1 for n in phase.snippet_lines if n) >= 4, phase.id


def test_only_real_commands_are_called_terminal_commands(curriculum):
    for pid in ("p02", "p04", "p15"):
        assert "terminal" not in curriculum.phase(pid).snippet_title.lower()


def test_the_windows_way_to_activate_a_venv_is_given(curriculum):
    notes = " ".join(curriculum.phase("p03").snippet_lines)
    assert ".venv\\Scripts\\activate" in notes


def test_the_phase_page_explains_each_line(qt_app, window):
    from conftest import pump
    from PySide6.QtWidgets import QLabel
    window.go("phase", "p00")
    pump(qt_app)
    texts = [w.text() for w in
             window.views["phase"].scroller.body.findChildren(QLabel)]
    assert "What each line does" in texts
    assert any(t.startswith("Turn the folder into a Git repository")
               for t in texts)


def test_the_plan_shows_its_arithmetic(qt_app, window):
    from operators_console.ui.widgets.time_left import basis_text
    store = window.ctx.store
    store.set_setting("hours_per_day", 5.0)
    store.set_setting("days_per_week", 1)
    text = basis_text(window.ctx.estimator.estimate())
    assert "5 h a day × 1 day a week = 5 h a week" in text
    assert "Settings > Pace" in text
