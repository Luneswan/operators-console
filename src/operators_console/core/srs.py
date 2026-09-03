"""Spaced repetition scheduling.

An implementation of FSRS-6 (Free Spaced Repetition Scheduler), the algorithm
Anki has shipped as its default since version 23.10. It models a memory with
three numbers instead of SM-2's single ease factor:

    stability      days until recall probability decays to the retention target
    difficulty     how intrinsically hard this material is for this learner
    retrievability probability of recall right now, derived from the other two

Reference implementation and the default weights come from
open-spaced-repetition/py-fsrs (MIT). The formulas below follow the published
FSRS-6 specification.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import IntEnum

# FSRS-6 default weights, fitted over roughly 500M Anki reviews.
DEFAULT_PARAMETERS: tuple[float, ...] = (
    0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001,
    1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014,
    1.8729, 0.5425, 0.0912, 0.0658, 0.1542,
)

STABILITY_MIN = 0.001
MIN_DIFFICULTY = 1.0
MAX_DIFFICULTY = 10.0
DEFAULT_RETENTION = 0.9
DEFAULT_MAX_INTERVAL = 3650

# Fuzz spreads due dates so a big cohort of cards learned on one day does not
# come back as one wall of reviews.
FUZZ_RANGES = (
    (2.5, 7.0, 0.15),
    (7.0, 20.0, 0.10),
    (20.0, math.inf, 0.05),
)


class Rating(IntEnum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class State(IntEnum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class Memory:
    """Scheduler state for one reviewable thing."""

    stability: float | None = None
    difficulty: float | None = None
    state: State = State.NEW
    step: int = 0
    due: datetime | None = None
    last_review: datetime | None = None
    reps: int = 0
    lapses: int = 0

    def retrievability(self, now: datetime | None = None,
                       decay: float = -DEFAULT_PARAMETERS[20]) -> float:
        """Probability of recall right now; 1.0 for anything never studied."""
        if self.stability is None or self.last_review is None:
            return 1.0
        now = now or utcnow()
        elapsed = max((now - self.last_review).total_seconds() / 86400.0, 0.0)
        factor = 0.9 ** (1 / decay) - 1
        return (1 + factor * elapsed / self.stability) ** decay

    def is_due(self, now: datetime | None = None) -> bool:
        return self.due is not None and self.due <= (now or utcnow())


class Scheduler:
    """Turns a rating into the next due date."""

    def __init__(
        self,
        parameters: tuple[float, ...] = DEFAULT_PARAMETERS,
        desired_retention: float = DEFAULT_RETENTION,
        learning_steps: tuple[timedelta, ...] = (
            timedelta(minutes=1), timedelta(minutes=10)),
        relearning_steps: tuple[timedelta, ...] = (timedelta(minutes=10),),
        maximum_interval: int = DEFAULT_MAX_INTERVAL,
        enable_fuzz: bool = True,
    ) -> None:
        if len(parameters) != 21:
            raise ValueError("FSRS-6 needs exactly 21 parameters")
        if not 0.70 <= desired_retention <= 0.99:
            raise ValueError("desired_retention must be between 0.70 and 0.99")
        self.w = parameters
        self.desired_retention = desired_retention
        self.learning_steps = learning_steps
        self.relearning_steps = relearning_steps
        self.maximum_interval = maximum_interval
        self.enable_fuzz = enable_fuzz
        self._decay = -parameters[20]
        self._factor = 0.9 ** (1 / self._decay) - 1

    # -- public ----------------------------------------------------------

    def review(self, memory: Memory, rating: Rating,
               now: datetime | None = None) -> Memory:
        """Apply a rating and return the updated memory."""
        now = now or utcnow()
        w = self.w

        if memory.state is State.NEW:
            stability = self._clamp_s(w[rating - 1])
            difficulty = self._initial_difficulty(rating)
        else:
            elapsed_days = 0.0
            if memory.last_review is not None:
                elapsed_days = max(
                    (now - memory.last_review).total_seconds() / 86400.0, 0.0)
            prior_s = memory.stability if memory.stability is not None \
                else w[rating - 1]
            prior_d = memory.difficulty if memory.difficulty is not None \
                else self._initial_difficulty(rating)
            difficulty = self._next_difficulty(prior_d, rating)
            if elapsed_days < 1.0:
                stability = self._short_term_stability(prior_s, rating)
            else:
                stability = self._next_stability(
                    difficulty=prior_d,
                    stability=prior_s,
                    retrievability=memory.retrievability(now, self._decay),
                    rating=rating,
                )

        state, step, interval = self._advance(memory, rating, stability)

        if self.enable_fuzz and state is State.REVIEW:
            interval = self._fuzz(interval)

        lapsed = rating is Rating.AGAIN and memory.state is State.REVIEW
        return replace(
            memory,
            stability=stability,
            difficulty=difficulty,
            state=state,
            step=step,
            due=now + interval,
            last_review=now,
            reps=memory.reps + 1,
            lapses=memory.lapses + (1 if lapsed else 0),
        )

    def preview(self, memory: Memory, now: datetime | None = None) -> dict:
        """What each button would schedule, so the UI can label them."""
        now = now or utcnow()
        saved_fuzz, self.enable_fuzz = self.enable_fuzz, False
        try:
            out: dict[Rating, timedelta] = {}
            for rating in Rating:
                after = self.review(memory, rating, now)
                out[rating] = (after.due - now) if after.due else timedelta(0)
            return out
        finally:
            self.enable_fuzz = saved_fuzz

    # -- internals -------------------------------------------------------

    def _advance(self, memory: Memory, rating: Rating, stability: float):
        state, step = memory.state, memory.step

        if state in (State.NEW, State.LEARNING):
            steps = self.learning_steps
            if not steps or (state is State.LEARNING and step >= len(steps)):
                return State.REVIEW, 0, self._review_interval(stability)
            if rating is Rating.AGAIN:
                return State.LEARNING, 0, steps[0]
            if rating is Rating.HARD:
                if step == 0 and len(steps) == 1:
                    return State.LEARNING, step, steps[0] * 1.5
                if step == 0:
                    return State.LEARNING, step, (steps[0] + steps[1]) / 2.0
                return State.LEARNING, step, steps[step]
            if rating is Rating.GOOD:
                if step + 1 >= len(steps):
                    return State.REVIEW, 0, self._review_interval(stability)
                return State.LEARNING, step + 1, steps[step + 1]
            return State.REVIEW, 0, self._review_interval(stability)

        if state is State.REVIEW:
            if rating is Rating.AGAIN and self.relearning_steps:
                return State.RELEARNING, 0, self.relearning_steps[0]
            return State.REVIEW, 0, self._review_interval(stability)

        steps = self.relearning_steps
        if not steps or step >= len(steps):
            return State.REVIEW, 0, self._review_interval(stability)
        if rating is Rating.AGAIN:
            return State.RELEARNING, 0, steps[0]
        if rating is Rating.HARD:
            if len(steps) == 1:
                return State.RELEARNING, step, steps[0] * 1.5
            return State.RELEARNING, step, (steps[0] + steps[1]) / 2.0
        if rating is Rating.GOOD:
            if step + 1 >= len(steps):
                return State.REVIEW, 0, self._review_interval(stability)
            return State.RELEARNING, step + 1, steps[step + 1]
        return State.REVIEW, 0, self._review_interval(stability)

    def _review_interval(self, stability: float) -> timedelta:
        days = (stability / self._factor) * (
            self.desired_retention ** (1 / self._decay) - 1)
        days = min(max(round(days), 1), self.maximum_interval)
        return timedelta(days=days)

    def _fuzz(self, interval: timedelta) -> timedelta:
        days = interval.days
        if days < 2.5:
            return interval
        delta = 1.0
        for low, high, weight in FUZZ_RANGES:
            delta += weight * max(min(days, high) - low, 0.0)
        low_day = max(int(round(days - delta)), 2)
        high_day = min(int(round(days + delta)), self.maximum_interval)
        low_day = min(low_day, high_day)
        return timedelta(days=random.randint(low_day, high_day))

    def _clamp_s(self, s: float) -> float:
        return max(s, STABILITY_MIN)

    def _clamp_d(self, d: float) -> float:
        return min(max(d, MIN_DIFFICULTY), MAX_DIFFICULTY)

    def _initial_difficulty(self, rating: Rating, clamp: bool = True) -> float:
        d = self.w[4] - math.exp(self.w[5] * (rating - 1)) + 1
        return self._clamp_d(d) if clamp else d

    def _next_difficulty(self, difficulty: float, rating: Rating) -> float:
        delta = -(self.w[6] * (rating - 3))
        damped = difficulty + (10.0 - difficulty) * delta / 9.0
        target = self._initial_difficulty(Rating.EASY, clamp=False)
        reverted = self.w[7] * target + (1 - self.w[7]) * damped
        return self._clamp_d(reverted)

    def _short_term_stability(self, stability: float, rating: Rating) -> float:
        increase = math.exp(self.w[17] * (rating - 3 + self.w[18])) * (
            stability ** -self.w[19])
        if rating is not Rating.AGAIN:
            increase = max(increase, 1.0)
        return self._clamp_s(stability * increase)

    def _next_stability(self, *, difficulty: float, stability: float,
                        retrievability: float, rating: Rating) -> float:
        if rating is Rating.AGAIN:
            s = self._forget_stability(difficulty, stability, retrievability)
        else:
            s = self._recall_stability(difficulty, stability, retrievability,
                                       rating)
        return self._clamp_s(s)

    def _forget_stability(self, difficulty: float, stability: float,
                          retrievability: float) -> float:
        w = self.w
        long_term = (w[11] * (difficulty ** -w[12])
                     * (((stability + 1) ** w[13]) - 1)
                     * math.exp((1 - retrievability) * w[14]))
        short_term = stability / math.exp(w[17] * w[18])
        return min(long_term, short_term)

    def _recall_stability(self, difficulty: float, stability: float,
                          retrievability: float, rating: Rating) -> float:
        w = self.w
        hard_penalty = w[15] if rating is Rating.HARD else 1.0
        easy_bonus = w[16] if rating is Rating.EASY else 1.0
        return stability * (
            1
            + math.exp(w[8])
            * (11 - difficulty)
            * (stability ** -w[9])
            * (math.exp((1 - retrievability) * w[10]) - 1)
            * hard_penalty
            * easy_bonus
        )


def describe_interval(delta: timedelta) -> str:
    """Human label for a scheduling button."""
    seconds = delta.total_seconds()
    if seconds < 60:
        return "%ds" % int(seconds)
    if seconds < 3600:
        return "%dm" % int(seconds // 60)
    if seconds < 86400:
        return "%dh" % int(seconds // 3600)
    days = seconds / 86400
    if days < 30:
        return "%dd" % round(days)
    if days < 365:
        return "%.1f mo" % (days / 30.44)
    return "%.1f y" % (days / 365.25)
