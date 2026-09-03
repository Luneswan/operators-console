"""Persistence: the promise is that nothing is ever lost."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

import pytest

from operators_console.core import paths
from operators_console.core.srs import Memory, State
from operators_console.core.storage import SCHEMA_VERSION, Store


def test_a_fresh_database_is_stamped_with_the_schema(store):
    assert int(store.get_meta("schema_version")) == SCHEMA_VERSION
    assert store.get_meta("created_at")


def test_settings_round_trip_every_json_type(store):
    store.set_setting("a_string", "hello")
    store.set_setting("a_number", 3.5)
    store.set_setting("a_bool", True)
    store.set_setting("a_list", ["x", "y"])
    assert store.setting("a_string") == "hello"
    assert store.setting("a_number") == 3.5
    assert store.setting("a_bool") is True
    assert store.setting("a_list") == ["x", "y"]


def test_unknown_settings_fall_back_to_the_documented_default(store):
    assert store.setting("hours_per_day") == 3.0
    assert store.setting("nothing_like_this", "fallback") == "fallback"


def test_checks_persist_across_a_reopen(store):
    store.set_checked("p01.s0.0", True)
    store.close()
    reopened = Store()
    try:
        assert reopened.is_checked("p01.s0.0")
    finally:
        reopened.close()


def test_unchecking_removes_the_row(store):
    store.set_checked("x", True)
    store.set_checked("x", False)
    assert not store.is_checked("x")
    assert store.checked_ids() == set()


def test_checking_twice_does_not_double_count(store):
    store.set_checked("x", True)
    store.set_checked("x", True)
    assert len(store.checked_ids()) == 1


def test_ratings_are_clamped_to_the_scale(store):
    store.set_rating("Git", 99)
    assert store.rating("Git") == 4
    store.set_rating("Git", -5)
    assert store.rating("Git") == 0


def test_an_empty_note_is_deleted_rather_than_stored(store):
    store.set_note("phase:p01", "something")
    assert store.note("phase:p01") == "something"
    store.set_note("phase:p01", "   ")
    assert store.note("phase:p01") == ""


def test_memory_round_trips_through_the_database(store):
    from datetime import datetime, timezone
    now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    memory = Memory(stability=12.5, difficulty=5.25, state=State.REVIEW,
                    step=0, due=now, last_review=now, reps=4, lapses=1)
    store.save_memory("q01.0", "quiz", "p01", memory)
    loaded = store.memory("q01.0")
    assert loaded.stability == pytest.approx(12.5)
    assert loaded.difficulty == pytest.approx(5.25)
    assert loaded.state is State.REVIEW
    assert loaded.reps == 4 and loaded.lapses == 1
    assert loaded.due == now


def test_an_unknown_card_reads_back_as_new(store):
    assert store.memory("never-seen").state is State.NEW


def test_due_cards_respect_the_clock(store):
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 5, 1, tzinfo=timezone.utc)
    store.save_memory("past", "quiz", "p01",
                      Memory(stability=1, difficulty=5, state=State.REVIEW,
                             due=now - timedelta(days=1), last_review=now))
    store.save_memory("future", "quiz", "p01",
                      Memory(stability=1, difficulty=5, state=State.REVIEW,
                             due=now + timedelta(days=1), last_review=now))
    assert store.due_cards(now) == ["past"]


def test_a_suspended_card_never_comes_due(store):
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 5, 1, tzinfo=timezone.utc)
    store.save_memory("c", "quiz", "p01",
                      Memory(stability=1, difficulty=5, state=State.REVIEW,
                             due=now - timedelta(days=2), last_review=now))
    store.suspend_card("c")
    assert store.due_cards(now) == []


def test_quiz_best_score_prefers_the_highest_ratio(store):
    store.record_quiz("q01", 4, 8, 60)
    store.record_quiz("q01", 7, 8, 60)
    store.record_quiz("q01", 5, 8, 60)
    assert store.best_quiz_score("q01") == (7, 8)


def test_a_pass_is_never_downgraded_by_a_later_failure(store):
    store.record_exercise_run("p01.001", "good", True)
    store.record_exercise_run("p01.001", "broken", False)
    state = store.exercise("p01.001")
    assert state["status"] == "passed"
    assert state["attempts"] == 2


def test_project_timestamps_follow_the_status(store):
    store.set_project("pj.1", status="in-progress")
    assert store.project("pj.1")["started_at"]
    assert store.project("pj.1")["finished_at"] is None
    store.set_project("pj.1", status="shipped")
    assert store.project("pj.1")["finished_at"]
    store.set_project("pj.1", status="not-started")
    assert store.project("pj.1")["started_at"] is None


def test_certificate_status_cycles_through_three_states(store):
    for expected in (1, 2, 0):
        store.set_cert_status("c-cs50p", store.cert_status("c-cs50p") + 1)
        assert store.cert_status("c-cs50p") == expected


def test_streak_counts_consecutive_days_only(store):
    today = date.today()
    for offset in (0, 1, 2, 5):
        store.bump_activity(items=1, day=(today - timedelta(days=offset)).isoformat())
    current, longest = store.streak()
    assert current == 3
    assert longest == 3


def test_a_streak_survives_until_the_end_of_the_following_day(store):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    store.bump_activity(items=1, day=yesterday)
    current, _longest = store.streak()
    assert current == 1


def test_no_activity_means_no_streak(store):
    assert store.streak() == (0, 0)


def test_forecast_buckets_by_day_and_folds_overdue_into_today(store):
    from datetime import datetime, time, timezone
    today = date.today()
    for offset in (-3, 0, 2, 2):
        due = datetime.combine(today + timedelta(days=offset), time(9, 0),
                               tzinfo=timezone.utc)
        store.save_memory("c%d" % (offset + 10 + len(store.seen_cards())),
                          "quiz", "p01",
                          Memory(stability=1, difficulty=5, state=State.REVIEW,
                                 due=due, last_review=due))
    forecast = store.forecast(10)
    assert forecast[0] == 2
    assert forecast[2] == 2


def test_backup_creates_a_readable_database(store):
    store.set_checked("x", True)
    target = store.backup(tag="test")
    assert target.exists()
    other = sqlite3.connect(target)
    try:
        rows = other.execute("SELECT COUNT(*) FROM checks").fetchone()
        assert rows[0] == 1
    finally:
        other.close()


def test_backups_are_pruned_to_the_last_twelve(store):
    for _ in range(15):
        store.backup()
    kept = list(paths.backups_dir().glob("progress-*.db"))
    assert len(kept) <= 12


def test_dump_and_restore_round_trip(store):
    store.set_checked("a", True)
    store.set_rating("Git", 3)
    store.add_log("2026-01-01", "Focus", 2.0, "built", "stuck", "next")
    store.set_setting("track", "backend")
    payload = store.dump()

    store.reset_progress()
    assert store.checked_ids() == set()

    store.restore(payload)
    assert store.is_checked("a")
    assert store.rating("Git") == 3
    assert store.total_hours() == 2.0
    assert store.setting("track") == "backend"


def test_restore_refuses_a_file_from_another_application(store):
    with pytest.raises(ValueError):
        store.restore({"app": "something-else", "tables": {}})


def test_restore_refuses_a_newer_schema(store):
    with pytest.raises(ValueError):
        store.restore({"app": "operators-console",
                       "schema": SCHEMA_VERSION + 5, "tables": {}})


def test_reset_keeps_settings_and_takes_a_backup(store):
    store.set_setting("learner_name", "Sam")
    store.set_checked("a", True)
    store.reset_progress()
    assert store.setting("learner_name") == "Sam"
    assert store.checked_ids() == set()
    assert list(paths.backups_dir().glob("*pre-reset*"))


def test_opening_a_future_schema_is_refused(store, tmp_path):
    store.set_meta("schema_version", str(SCHEMA_VERSION + 1))
    store.close()
    with pytest.raises(RuntimeError):
        Store()
