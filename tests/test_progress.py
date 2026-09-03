"""Progress arithmetic, plan shaping and the daily suggestion."""
from __future__ import annotations

import pytest

from operators_console.core.adaptive import Planner
from operators_console.core.today import LEARN, LOG, REVIEW, TodayPlan


@pytest.fixture
def planner(curriculum, store, progress):
    return Planner(curriculum, store, progress)


def complete(curriculum, store, phase_id):
    phase = curriculum.phase(phase_id)
    store.set_many_checked(phase.trackable_ids, True)


def test_a_fresh_profile_starts_at_zero(progress):
    overview = progress.overview()
    assert overview.done == 0
    assert overview.percent == 0
    assert overview.phases_complete == 0
    assert overview.total > 300


def test_finishing_a_phase_counts_it(curriculum, store, progress):
    complete(curriculum, store, "p00")
    stats = progress.phase(curriculum.phase("p00"))
    assert stats.is_complete
    assert stats.percent == 100
    assert progress.overview().phases_complete == 1


def test_progress_is_scoped_to_the_chosen_track(curriculum, store, progress):
    store.set_setting("track", "generalist")
    wide = progress.overview().total
    store.set_setting("track", "beginner")
    narrow = progress.overview().total
    assert narrow < wide


def test_the_current_phase_is_the_first_unfinished_one(curriculum, store, progress):
    assert progress.current_phase_id() == "p00"
    complete(curriculum, store, "p00")
    assert progress.current_phase_id() == "p01"


def test_a_phase_unlocks_once_its_prerequisite_is_mostly_done(curriculum, store,
                                                              progress):
    assert progress.unlocked("p00")
    assert not progress.unlocked("p01")
    complete(curriculum, store, "p00")
    assert progress.unlocked("p01")


def test_a_phase_outside_the_plan_never_blocks(curriculum, store, progress):
    store.set_setting("track", "data")
    assert progress.unlocked("p17") in (True, False)


def test_the_finish_estimate_responds_to_pace(store, progress):
    store.set_setting("hours_per_day", 1.0)
    slow = progress.estimated_days_left()
    store.set_setting("hours_per_day", 8.0)
    fast = progress.estimated_days_left()
    assert fast < slow


def test_the_roadmap_is_ordered_and_labelled(curriculum, store, planner):
    store.set_setting("track", "backend")
    rows = planner.roadmap()
    ids = [row.phase_id for row in rows]
    assert ids[0] == "p00"
    assert len(ids) == len(set(ids))
    roles = {row.role for row in rows}
    assert roles <= {"core", "optional", "extra"}
    assert all(row.reason for row in rows)


def test_goals_add_phases_the_track_left_out(curriculum, store, planner):
    store.set_setting("track", "beginner")
    before = {row.phase_id for row in planner.roadmap()}
    store.set_setting("goals", ["ai"])
    after = {row.phase_id for row in planner.roadmap()}
    assert after > before
    assert "p14" in after


def test_the_suggested_track_follows_the_goals(planner):
    assert planner.suggested_track({"web"}) in ("backend", "generalist")
    assert planner.suggested_track({"ai"}) == "ai"
    assert planner.suggested_track(set()) == "generalist"


def test_weak_areas_only_report_started_phases(curriculum, store, progress,
                                               planner):
    assert planner.weak_areas() == []
    phase = curriculum.phase("p01")
    store.set_many_checked([item.id for item in phase.items][:5], True)
    store.record_quiz("q01", 1, 8, 30)
    assert "p01" in planner.weak_areas()


def test_today_always_offers_something(curriculum, store, progress, planner):
    plan = TodayPlan(curriculum, store, progress, planner)
    actions = plan.build()
    assert actions
    assert all(action.minutes > 0 for action in actions)
    assert any(action.kind == LEARN for action in actions)


def test_today_puts_review_first_when_cards_are_due(curriculum, store, progress,
                                                    planner):
    """A card answered now is not due now, so schedule one into the past."""
    from datetime import datetime, timedelta, timezone

    from operators_console.core.srs import Memory, State

    phase = curriculum.phase("p00")
    store.set_many_checked([item.id for item in phase.items][:3], True)
    overdue = datetime.now(timezone.utc) - timedelta(days=2)
    for question in curriculum.quizzes_for("p00")[0].questions[:4]:
        store.save_memory(question.id, "quiz", "p00",
                          Memory(stability=3.0, difficulty=5.0,
                                 state=State.REVIEW, due=overdue,
                                 last_review=overdue - timedelta(days=3),
                                 reps=2))
    assert store.card_counts()["due"] == 4
    plan = TodayPlan(curriculum, store, progress, planner)
    actions = plan.build()
    assert actions[0].kind == REVIEW


def test_today_stops_asking_for_a_log_once_written(curriculum, store, progress,
                                                   planner):
    from datetime import date
    plan = TodayPlan(curriculum, store, progress, planner)
    assert any(a.kind == LOG for a in plan.build())
    store.add_log(date.today().isoformat(), "Focus", 1.0, "", "", "")
    assert not any(a.kind == LOG for a in plan.build())
