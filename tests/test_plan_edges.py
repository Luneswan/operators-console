"""The plan, the review queue and numeric settings at their edges.

Found by the 2026-09-22 edge-case sweep; each failed before its fix: goal
phases on the Roadmap counted nowhere else, the review cap withheld cards
failed a minute earlier, and NaN or Infinity in a setting crashed the plan.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operators_console.core.adaptive import Planner
from operators_console.core.progress import Progress
from operators_console.core.review import ReviewQueue
from operators_console.core.srs import Rating, State
from operators_console.core.today import TodayPlan


def plan_for(curriculum, store):
    progress = Progress(curriculum, store)
    planner = Planner(curriculum, store, progress)
    return progress, planner, TodayPlan(curriculum, store, progress, planner)


# ---------------------------------------------------------------------------
# Phases the roadmap adds for a goal are invisible to review and progress
# ---------------------------------------------------------------------------

@pytest.fixture
def beginner_who_wants_web(curriculum, store):
    """The onboarding shape: a track plus goals. Planner.roadmap() adds p13
    and p15 as 'extra' rows ("Added because you said you care about ..."),
    but Progress.active_phase_ids() reads only track.core + track.optional."""
    store.set_setting("track", "beginner")
    store.set_setting("goals", ["web"])
    progress, planner, _today = plan_for(curriculum, store)
    extras = [r.phase_id for r in planner.roadmap() if r.role == "extra"]
    assert "p13" in extras, extras
    phase = curriculum.phase("p13")
    store.set_many_checked([i.id for i in phase.items][:3], True)
    return progress


def test_a_started_goal_phase_feeds_its_quiz_into_review(
        curriculum, store, beginner_who_wants_web):
    """quiz.py says 'A wrong answer goes straight into spaced repetition', but
    it looks the question up in review.all_cards(), which filters by the
    track-only plan - so wrong answers on p13's quiz are silently dropped."""
    queue = ReviewQueue(curriculum, store, beginner_who_wants_web)
    assert "p13" in queue.eligible_phase_ids()
    ids = {c.id for c in queue.all_cards()}
    p13_questions = {q.id for quiz in curriculum.quizzes_for("p13")
                     for q in quiz.questions}
    assert p13_questions & ids, "no p13 question can ever be reviewed"


def test_a_goal_phase_on_the_roadmap_counts_toward_the_plan(
        curriculum, store, beginner_who_wants_web):
    """Overview %, Today's next step and the report all use
    active_phase_ids(); ticks in p13 move none of them."""
    phase_ids = beginner_who_wants_web.active_phase_ids()
    assert "p13" in phase_ids, "the roadmap lists p13, the meter ignores it"


# ---------------------------------------------------------------------------
# The review cap hides cards the learner failed a minute ago
# ---------------------------------------------------------------------------

def test_failed_learning_cards_come_back_even_after_the_review_cap(
        curriculum, store):
    """session() subtracts *every* answer today (new cards included) from
    max_reviews_per_day and then applies that to due learning-step cards too.
    With the cap at the UI minimum of 10, failing 10 new cards leaves them
    hidden until tomorrow while 5 brand-new cards are still offered."""
    progress = Progress(curriculum, store)
    plan = progress.active_phase_ids()
    # Open enough phases for >= 10 questions.
    store.set_many_checked([i.id for i in curriculum.phase(plan[3]).items][:2],
                           True)
    store.set_setting("max_reviews_per_day", 10)
    store.set_setting("new_cards_per_day", 15)
    queue = ReviewQueue(curriculum, store, progress)
    start = datetime.now(timezone.utc)
    first = queue.session(start)
    assert len(first) >= 10
    failed = []
    for card in first[:10]:
        after = queue.answer(card, Rating.AGAIN, start)
        assert after.state is State.LEARNING
        failed.append(card.id)
    later = queue.session(start + timedelta(minutes=2))
    offered = {c.id for c in later}
    assert set(failed) <= offered, (
        "%d failed cards withheld, %d new ones offered"
        % (len(set(failed) - offered), len(offered - set(failed))))


# ---------------------------------------------------------------------------
# _number() lets NaN and Infinity through
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hours", [float("nan"), float("inf")])
def test_a_nan_or_infinite_study_budget_does_not_crash_the_plan(
        curriculum, store, hours):
    """json.loads accepts the NaN / Infinity literals, float() accepts them,
    and int(nan * 60) / int(inf * 60) raise out of TodayPlan.build()."""
    store.set_setting("hours_per_day", hours)
    _progress, _planner, today = plan_for(curriculum, store)
    assert today.build()


@pytest.mark.parametrize("hours", [float("nan"), float("inf")])
def test_a_nan_or_infinite_pace_gives_a_finite_estimate(curriculum, store,
                                                        hours):
    store.set_setting("hours_per_day", hours)
    store.set_setting("days_per_week", hours)
    estimate = Progress(curriculum, store).estimated_days_left()
    assert isinstance(estimate, int) and estimate >= 0
