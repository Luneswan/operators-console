"""FSRS-6 pinned against the reference implementation.

Every number here was produced by open-spaced-repetition/py-fsrs with the
default parameters, either as one of its own published test cases or by
running the reference formulas on a fixed input. A change to srs.py that
alters a learner's schedule has to change one of these, which is the point:
scheduling is the part of the app nobody can eyeball.

Where this implementation deliberately differs from the reference, the
difference is asserted too, so it stays deliberate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operators_console.core.srs import (
    DEFAULT_PARAMETERS, Memory, Rating, Scheduler, State,
)

START = datetime(2022, 11, 29, 12, 30, 0, 0, timezone.utc)


@pytest.fixture
def exact():
    """A scheduler with the fuzz off, so intervals are reproducible."""
    return Scheduler(enable_fuzz=False)


# ---------------------------------------------------------------------------
# published vectors
# ---------------------------------------------------------------------------

def test_the_reference_interval_history_reproduces_exactly(exact):
    """py-fsrs test_review_card: Good x6, Again x2, Good x5."""
    memory = Memory()
    now = START
    intervals = []
    for rating in ([Rating.GOOD] * 6 + [Rating.AGAIN] * 2 + [Rating.GOOD] * 5):
        memory = exact.review(memory, rating, now)
        intervals.append((memory.due - memory.last_review).days)
        now = memory.due
    assert intervals == [0, 2, 11, 46, 163, 498, 0, 0, 2, 4, 7, 12, 21]


def test_the_reference_memory_state_reproduces_exactly():
    """py-fsrs test_memo_state: Again then Good x5 at 0/0/1/3/8/21 days."""
    scheduler = Scheduler()
    memory = Memory()
    now = START
    schedule = zip(
        (Rating.AGAIN, Rating.GOOD, Rating.GOOD, Rating.GOOD, Rating.GOOD,
         Rating.GOOD),
        (0, 0, 1, 3, 8, 21), strict=True)
    for rating, gap in schedule:
        now = now + timedelta(days=gap)
        memory = scheduler.review(memory, rating, now)
    assert memory.stability == pytest.approx(53.6269029, abs=1e-6)
    assert memory.difficulty == pytest.approx(6.3574871, abs=1e-6)


def test_the_first_four_buttons_offer_the_reference_intervals(exact):
    """What a brand new card's four buttons promise."""
    preview = exact.preview(Memory(), START)
    assert preview[Rating.AGAIN] == timedelta(minutes=1)
    assert preview[Rating.HARD] == timedelta(minutes=5, seconds=30)
    assert preview[Rating.GOOD] == timedelta(minutes=10)
    assert preview[Rating.EASY] == timedelta(days=8)


MIXED_TRACE = [
    # days from start, rating, stability, difficulty, state
    (0, Rating.GOOD, 2.306500, 2.118104, State.LEARNING),
    (10, Rating.GOOD, 25.108720, 2.111214, State.REVIEW),
    (35, Rating.HARD, 67.246419, 4.748285, State.REVIEW),
    (40, Rating.AGAIN, 2.792982, 8.259025, State.RELEARNING),
    (40, Rating.GOOD, 2.792982, 8.245995, State.REVIEW),
    (52, Rating.EASY, 18.258871, 7.645116, State.REVIEW),
]


def test_a_mixed_rating_trace_matches_the_reference_step_for_step(exact):
    memory = Memory()
    for days, rating, stability, difficulty, state in MIXED_TRACE:
        memory = exact.review(memory, rating, START + timedelta(days=days))
        assert memory.stability == pytest.approx(stability, abs=1e-6)
        assert memory.difficulty == pytest.approx(difficulty, abs=1e-6)
        assert memory.state is state


def test_a_hard_answer_within_the_day_cannot_lower_stability(exact):
    """The reference clamps the short-term increase for Hard as well as Good.

    The fourth row of the trace above only holds because of that clamp; this
    asserts the rule directly so a refactor cannot quietly drop it.
    """
    memory = exact.review(Memory(), Rating.GOOD, START)
    memory = exact.review(memory, Rating.GOOD, START + timedelta(days=10))
    before = memory.stability
    same_day = exact.review(memory, Rating.HARD,
                            START + timedelta(days=10, hours=2))
    assert same_day.stability >= before
    # Again is the one rating that is allowed to reduce it.
    failed = exact.review(memory, Rating.AGAIN,
                          START + timedelta(days=10, hours=2))
    assert failed.stability < before


# ---------------------------------------------------------------------------
# the step machine, where this implementation had drifted
# ---------------------------------------------------------------------------

def test_failing_a_card_never_graduates_it_to_review():
    """A card whose step ran past a shortened step list still restarts.

    Settings that shrink the learning steps leave existing cards with a step
    index past the end. Answering Again then used to send the card to Review
    with a multi-day interval - the app telling a learner who just failed a
    card to come back in three days.
    """
    scheduler = Scheduler(enable_fuzz=False,
                          learning_steps=(timedelta(minutes=1),))
    stranded = Memory(stability=5.0, difficulty=5.0, state=State.LEARNING,
                      step=1, last_review=START, reps=2)
    after = scheduler.review(stranded, Rating.AGAIN, START)
    assert after.state is State.LEARNING
    assert after.step == 0
    assert after.due - START == timedelta(minutes=1)


def test_failing_a_relearning_card_never_graduates_it_either():
    scheduler = Scheduler(enable_fuzz=False,
                          relearning_steps=(timedelta(minutes=10),))
    stranded = Memory(stability=5.0, difficulty=5.0, state=State.RELEARNING,
                      step=3, last_review=START, reps=9)
    after = scheduler.review(stranded, Rating.AGAIN, START)
    assert after.state is State.RELEARNING
    assert after.due - START == timedelta(minutes=10)


def test_hard_on_a_later_relearning_step_repeats_that_step():
    """Only the first step averages the first two; the rest repeat.

    With three relearning steps a card sitting on the second one used to be
    given the average of the first two - a shorter delay than the step it is
    actually on, so the card came back too soon for the rest of the session.
    """
    steps = (timedelta(minutes=10), timedelta(minutes=20),
             timedelta(minutes=30))
    scheduler = Scheduler(enable_fuzz=False, relearning_steps=steps)
    card = Memory(stability=5.0, difficulty=5.0, state=State.RELEARNING,
                  step=1, last_review=START, reps=9)
    after = scheduler.review(card, Rating.HARD, START)
    assert after.due - START == timedelta(minutes=20)

    first = Memory(stability=5.0, difficulty=5.0, state=State.RELEARNING,
                   step=0, last_review=START, reps=9)
    assert (scheduler.review(first, Rating.HARD, START).due - START
            == timedelta(minutes=15))


def test_a_scheduled_card_with_no_last_review_is_treated_as_forgotten():
    """A row restored from a partial backup must not freeze its stability."""
    scheduler = Scheduler(enable_fuzz=False)
    orphan = Memory(stability=10.0, difficulty=5.0, state=State.REVIEW,
                    step=0, due=START, last_review=None, reps=4)
    after = scheduler.review(orphan, Rating.GOOD, START)
    assert after.stability > 10.0
    assert after.last_review == START


# ---------------------------------------------------------------------------
# parameters
# ---------------------------------------------------------------------------

def test_the_default_weights_are_the_published_fsrs6_set():
    assert len(DEFAULT_PARAMETERS) == 21
    assert DEFAULT_PARAMETERS[0] == pytest.approx(0.212)
    assert DEFAULT_PARAMETERS[4] == pytest.approx(6.4133)
    assert DEFAULT_PARAMETERS[20] == pytest.approx(0.1542)


@pytest.mark.parametrize("index,value", [
    (4, 99.0),      # initial difficulty, far outside its range
    (7, 3.0),       # mean reversion weight, must stay under 0.75
    (20, 0.0),      # decay, must stay positive or the maths inverts
])
def test_a_weight_outside_its_published_range_is_refused(index, value):
    weights = list(DEFAULT_PARAMETERS)
    weights[index] = value
    with pytest.raises(ValueError, match="w%d" % index):
        Scheduler(parameters=tuple(weights))


def test_retrievability_ignores_a_stale_module_level_decay():
    """A custom decay must reach the calculation, not the import-time default."""
    memory = Memory(stability=10.0, last_review=START,
                    state=State.REVIEW, reps=1)
    later = START + timedelta(days=5)
    assert (memory.retrievability(later, decay=-0.5)
            != pytest.approx(memory.retrievability(later, decay=-0.1542)))
    assert (memory.retrievability(later)
            == pytest.approx(memory.retrievability(later, decay=-0.1542)))
    # At exactly one stability the answer is the retention target whatever
    # the decay, which is the identity the whole formula is built around.
    at_s = memory.retrievability(START + timedelta(days=10), decay=-0.5)
    assert at_s == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# deliberate differences from the reference
# ---------------------------------------------------------------------------

def test_elapsed_time_is_measured_in_fractional_days_on_purpose():
    """The reference floors to whole days; this counts the hours.

    py-fsrs computes ``(now - last_review).days``. Here a card reviewed at
    10 days and 12 hours is treated as 10.5 days old, which produces a
    slightly larger stability. It is deliberate - the app records a real
    timestamp and there is no reason to throw half of it away - but it is a
    documented divergence, so it is pinned rather than left to drift.
    """
    scheduler = Scheduler(enable_fuzz=False)
    memory = scheduler.review(Memory(), Rating.GOOD, START)
    whole = scheduler.review(memory, Rating.GOOD, START + timedelta(days=10))
    half = scheduler.review(memory, Rating.GOOD,
                            START + timedelta(days=10, hours=12))
    assert whole.stability == pytest.approx(25.1087202, abs=1e-6)
    assert half.stability == pytest.approx(25.6312045, abs=1e-6)


def test_the_maximum_interval_is_ten_years_not_a_hundred():
    """The reference allows 36500 days. A curriculum does not need it."""
    scheduler = Scheduler(enable_fuzz=False)
    ancient = Memory(stability=1e9, difficulty=1.0, state=State.REVIEW,
                     last_review=START, due=START, reps=50)
    after = scheduler.review(ancient, Rating.EASY, START + timedelta(days=400))
    assert (after.due - after.last_review).days == 3650


# ---------------------------------------------------------------------------
# clocks
# ---------------------------------------------------------------------------

def test_a_clock_that_jumps_backwards_never_produces_a_negative_age(exact):
    memory = exact.review(Memory(), Rating.GOOD, START)
    memory = exact.review(memory, Rating.GOOD, START + timedelta(days=10))
    backwards = exact.review(memory, Rating.GOOD, START + timedelta(days=5))
    assert backwards.stability > 0
    assert backwards.due > backwards.last_review
    assert backwards.last_review == START + timedelta(days=5)


def test_a_review_across_a_dst_boundary_uses_utc(exact):
    """Scheduling is UTC, so a one-hour civil shift changes nothing."""
    before = datetime(2026, 3, 29, 0, 30, tzinfo=timezone.utc)
    memory = exact.review(Memory(), Rating.GOOD, before)
    memory = exact.review(memory, Rating.GOOD, before + timedelta(days=10))
    shifted = exact.review(Memory(), Rating.GOOD, before)
    shifted = exact.review(shifted, Rating.GOOD, before + timedelta(days=10))
    assert memory.stability == shifted.stability
    assert memory.due == shifted.due
