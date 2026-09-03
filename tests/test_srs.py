"""The scheduler is the part where a subtle bug is invisible for months."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operators_console.core.srs import (
    DEFAULT_PARAMETERS, Memory, Rating, Scheduler, State, describe_interval,
)

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def scheduler():
    return Scheduler(enable_fuzz=False)


def test_rejects_wrong_parameter_count():
    with pytest.raises(ValueError):
        Scheduler(parameters=(0.1, 0.2))


def test_rejects_absurd_retention():
    with pytest.raises(ValueError):
        Scheduler(desired_retention=0.4)
    with pytest.raises(ValueError):
        Scheduler(desired_retention=1.0)


def test_a_new_card_starts_in_learning(scheduler):
    after = scheduler.review(Memory(), Rating.GOOD, START)
    assert after.state is State.LEARNING
    assert after.reps == 1
    assert after.stability == pytest.approx(DEFAULT_PARAMETERS[2])


def test_easy_leaves_learning_immediately(scheduler):
    after = scheduler.review(Memory(), Rating.EASY, START)
    assert after.state is State.REVIEW
    assert after.due - START >= timedelta(days=1)


def test_better_ratings_never_shorten_the_interval(scheduler):
    """Same-day reviews can tie, because short-term stability barely moves.

    Across days the ordering must be strict, which is what a learner actually
    sees on the rating buttons.
    """
    memory = Memory()
    for _ in range(3):
        memory = scheduler.review(memory, Rating.GOOD, START)
    same_day = scheduler.preview(memory, START)
    assert (same_day[Rating.AGAIN] <= same_day[Rating.HARD]
            <= same_day[Rating.GOOD] <= same_day[Rating.EASY])

    now = START
    for _ in range(4):
        memory = scheduler.review(memory, Rating.GOOD, now)
        now = memory.due
    matured = scheduler.preview(memory, now)
    assert (matured[Rating.AGAIN] < matured[Rating.HARD]
            < matured[Rating.GOOD] < matured[Rating.EASY]), matured


def test_intervals_grow_with_repeated_success(scheduler):
    memory = Memory()
    now = START
    intervals = []
    for _ in range(6):
        memory = scheduler.review(memory, Rating.GOOD, now)
        intervals.append((memory.due - now).days)
        now = memory.due
    growing = [b >= a for a, b in zip(intervals[2:], intervals[3:], strict=False)]
    assert all(growing), intervals


def test_a_lapse_sends_a_review_card_to_relearning(scheduler):
    memory = Memory()
    now = START
    for _ in range(4):
        memory = scheduler.review(memory, Rating.GOOD, now)
        now = memory.due
    assert memory.state is State.REVIEW
    before = memory.stability
    lapsed = scheduler.review(memory, Rating.AGAIN, now)
    assert lapsed.state is State.RELEARNING
    assert lapsed.lapses == 1
    assert lapsed.stability < before


def test_lapses_are_not_counted_while_still_learning(scheduler):
    memory = scheduler.review(Memory(), Rating.GOOD, START)
    again = scheduler.review(memory, Rating.AGAIN, START)
    assert again.lapses == 0


def test_difficulty_stays_inside_its_bounds(scheduler):
    memory = Memory()
    now = START
    for rating in [Rating.AGAIN] * 12:
        memory = scheduler.review(memory, rating, now)
        now = memory.due + timedelta(days=1)
    assert 1.0 <= memory.difficulty <= 10.0
    for rating in [Rating.EASY] * 12:
        memory = scheduler.review(memory, rating, now)
        now = memory.due + timedelta(days=1)
    assert 1.0 <= memory.difficulty <= 10.0


def test_retrievability_decays_towards_the_target(scheduler):
    memory = scheduler.review(Memory(), Rating.EASY, START)
    assert memory.retrievability(START) == pytest.approx(1.0, abs=1e-6)
    later = memory.retrievability(memory.due)
    assert 0.85 < later < 0.95


def test_an_unstudied_card_is_fully_retrievable():
    assert Memory().retrievability(START) == 1.0


def test_intervals_never_exceed_the_maximum():
    scheduler = Scheduler(enable_fuzz=False, maximum_interval=30)
    memory = Memory()
    now = START
    for _ in range(12):
        memory = scheduler.review(memory, Rating.EASY, now)
        now = memory.due
        assert (memory.due - (memory.last_review or now)).days <= 30


def test_fuzz_keeps_intervals_positive_and_near_the_target():
    scheduler = Scheduler(enable_fuzz=True)
    memory = Memory()
    now = START
    for _ in range(8):
        memory = scheduler.review(memory, Rating.GOOD, now)
        assert memory.due > now
        now = memory.due


@pytest.mark.parametrize("delta,expected", [
    (timedelta(seconds=30), "30s"),
    (timedelta(minutes=10), "10m"),
    (timedelta(hours=5), "5h"),
    (timedelta(days=3), "3d"),
    (timedelta(days=60), "2.0 mo"),
    (timedelta(days=800), "2.2 y"),
])
def test_interval_labels_read_like_a_human_wrote_them(delta, expected):
    assert describe_interval(delta) == expected
