"""Restore and import against damaged backups, and other store edges.

Found by the 2026-09-22 edge-case sweep; each failed before its fix. The
Settings page catches OSError and ValueError, so "raises anything else" meant
a click that did nothing and said nothing.
"""
from __future__ import annotations

import json
from datetime import date, datetime

import pytest

from operators_console.core import paths, storage
from operators_console.core.export import export_backup, import_backup

UI_CATCHES = (OSError, ValueError)


# ---------------------------------------------------------------------------
# import: files the Settings page cannot report on
# ---------------------------------------------------------------------------

def test_importing_a_json_array_is_refused_with_a_message(store, tmp_path):
    source = tmp_path / "not-a-backup.json"
    source.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(UI_CATCHES):         # observed: AttributeError
        import_backup(store, source)


def test_importing_a_backup_with_a_null_schema_is_refused_with_a_message(
        store, tmp_path):
    payload = store.dump()
    payload["schema"] = None
    source = tmp_path / "b.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(UI_CATCHES):         # observed: TypeError
        import_backup(store, source)


def test_a_backup_with_an_unstorable_value_is_refused_with_a_message(store):
    """test_storage_hardening accepts any Exception here; the UI does not."""
    store.set_checked("p01.s0.0", True)
    payload = store.dump()
    payload["tables"]["checks"] = [{"item_id": ["a", "list"], "done_at": "x"}]
    with pytest.raises(UI_CATCHES):         # observed: sqlite3.ProgrammingError
        store.restore(payload)
    assert store.is_checked("p01.s0.0")


def test_a_backup_row_missing_a_required_column_is_refused_with_a_message(
        store):
    """Only rows[0] decides the column list; a later short row hits NOT NULL."""
    payload = store.dump()
    payload["tables"]["checks"] = [
        {"item_id": "a", "done_at": "2026-01-01T00:00:00+00:00"},
        {"item_id": "b"},
    ]
    with pytest.raises(UI_CATCHES):         # observed: sqlite3.IntegrityError
        store.restore(payload)


def test_a_backup_saved_by_notepad_with_a_bom_imports(store, tmp_path):
    """Windows editors (and PowerShell 5 Set-Content -Encoding UTF8) write a
    UTF-8 BOM. read_text('utf-8') keeps it and json.loads refuses the file."""
    store.set_checked("p01.s0.0", True)
    target = export_backup(store, tmp_path / "backup.json")
    text = target.read_text(encoding="utf-8")
    target.write_text(text, encoding="utf-8-sig")
    store.reset_progress()
    import_backup(store, target)            # observed: JSONDecodeError 'Unexpected UTF-8 BOM'
    assert store.is_checked("p01.s0.0")


# ---------------------------------------------------------------------------
# import: files that are accepted and then break the app
# ---------------------------------------------------------------------------

def _review_queue(store, curriculum):
    from operators_console.core.progress import Progress
    from operators_console.core.review import ReviewQueue
    return ReviewQueue(curriculum, store, Progress(curriculum, store))


def test_a_restored_schedule_row_with_an_unknown_state_is_refused(
        store, curriculum):
    """restore() checks shape, not values. state=9 is accepted, and every
    later read of that card raises ValueError out of State(9) - the Review
    page and anything that counts cards."""
    from operators_console.core.progress import Progress
    first = Progress(curriculum, store).active_phase_ids()[0]
    question = next(q for quiz in curriculum.quizzes if quiz.phase == first
                    for q in quiz.questions)
    payload = store.dump()
    payload["tables"]["srs"] = [{
        "card_id": question.id, "kind": "quiz", "phase": first,
        "stability": 1.0, "difficulty": 5.0, "state": 9, "step": 0,
        "due": "2026-01-01T00:00:00+00:00",
        "last_review": "2025-12-31T00:00:00+00:00",
        "reps": 1, "lapses": 0, "suspended": 0}]
    try:
        store.restore(payload)
    except ValueError:
        return                               # refusing it is a fine answer
    _review_queue(store, curriculum).counts()   # observed: ValueError: 9 is not a valid State


def test_a_restored_retention_outside_the_scheduler_range_is_refused(
        store, curriculum):
    """AppContext builds a ReviewQueue at startup outside app.py's try, so a
    restored desired_retention of 0.5 stops the app from opening at all."""
    payload = store.dump()
    payload["tables"]["settings"] = [
        {"key": "desired_retention", "value": "0.5"}]
    try:
        store.restore(payload)
    except ValueError:
        return
    _review_queue(store, curriculum)         # observed: ValueError: desired_retention must be between 0.70 and 0.99


# ---------------------------------------------------------------------------
# snapshots
# ---------------------------------------------------------------------------

def test_a_snapshot_that_cannot_be_written_raises_what_the_menu_catches(
        store, monkeypatch):
    """backup() fails inside sqlite3.connect with OperationalError ('unable to
    open database file' - also what a full disk or a blocked folder gives),
    which is not an OSError, so Snapshot fails silently."""
    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 22, 12, 0, 0, tzinfo=tz)

    monkeypatch.setattr(storage, "datetime", Frozen)
    (paths.backups_dir() / "progress-20260922-120000-manual.db").mkdir()
    with pytest.raises(OSError):             # observed: sqlite3.OperationalError
        store.backup(tag="manual")


# ---------------------------------------------------------------------------
# activity counters
# ---------------------------------------------------------------------------

def test_deleting_a_log_entry_removes_its_study_time(store):
    """add_log adds minutes to `activity`; delete_log never takes them away.
    A mistaken 8-hour entry deleted from the journal still shows on the
    activity chart and still keeps the streak alive."""
    today = date.today().isoformat()
    log_id = store.add_log(today, "oops", 8.0, "", "", "")
    store.delete_log(log_id)
    assert store.total_hours() == 0.0
    minutes = store.activity(days=1).get(today, {}).get("minutes", 0)
    assert minutes == 0, minutes             # observed: 480
    assert store.streak() == (0, 0)
