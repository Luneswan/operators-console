"""How much new material is left, how fast this learner gets through it, and
when they finish.

Every phase carries an estimate in hours. That estimate is split into
minutes per unit of work - each checklist line, gate check, exercise (by
difficulty), quiz and required project - so "what is left" is the sum of
the units not done yet.

The pace is measured, not declared. A timed session records when it started
and stopped; everything the store marked done in that window (ticks, passed
exercises, quizzes, shipped projects) is the work it produced. Pace is time
spent on new material divided by the estimated minutes of that work, blended
with ten hours of evidence at the book rate so one session cannot swing it.
Review cards are upkeep, not new material: their time is taken out of the
session before the ratio, and out of each week before the finish date.

The finish date divides what is left, at this learner's pace, by the hours
a week they actually study (the last four weeks, once there are two weeks of
history) or, before that, by the hours a week they said they would.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta

from .progress import QUIZ_PROOF, _number

# How a phase's hours divide between its kinds of work. A phase without one
# of them shares its part out among the rest.
SHARES = (("steps", 0.50), ("gate", 0.10), ("exercises", 0.20),
          ("quiz", 0.05), ("project", 0.15))
REVIEW_SECONDS = 20          # one review card, answered and rated
PRIOR_MINUTES = 600.0        # ten hours at the book rate, before any session
PACE_LIMITS = (0.33, 3.0)    # three times faster or slower than the book
SESSION_CREDIT_CAP = 3       # ticking off old work credits at most 3x the time
RECENT_DAYS = 28
HISTORY_DAYS = 14            # study history needed before it sets the rate
MIN_NEW_SHARE = 0.25         # reviews never eat more than 3/4 of a week


@dataclass(frozen=True, slots=True)
class Pace:
    """Minutes this learner takes per estimated minute, and the evidence."""
    factor: float
    sessions: int
    timed_minutes: float          # on new material, reviews taken out
    credited_minutes: float       # estimated minutes of work those produced

    @property
    def measured(self) -> bool:
        return self.sessions > 0

    def describe(self) -> str:
        if not self.measured:
            return "the course estimate (no timed sessions yet)"
        if abs(self.factor - 1.0) < 0.05:
            speed = "on the estimate"
        elif self.factor < 1.0:
            speed = "%d%% faster than the estimate" % round(
                (1 / self.factor - 1) * 100)
        else:
            speed = "%d%% slower than the estimate" % round(
                (self.factor - 1) * 100)
        return "%s, from %d timed session%s" % (
            speed, self.sessions, "" if self.sessions == 1 else "s")


@dataclass(frozen=True, slots=True)
class PhaseTime:
    phase_id: str
    total_minutes: float          # the whole phase, at the book rate
    left_minutes: float           # what is not done, at the book rate
    left_personal: float          # what is not done, at this learner's pace
    finish: date | None           # when it is done, in plan order
    start: date | None = None     # when work on it begins, in plan order


@dataclass(frozen=True, slots=True)
class Estimate:
    total_minutes: float          # the whole plan, at the book rate
    left_minutes: float           # not done yet, at the book rate
    left_personal: float          # not done yet, at this learner's pace
    pace: Pace
    plan_week_hours: float        # what the learner said they would study
    recent_week_hours: float | None   # what they studied, last four weeks
    review_week_hours: float      # of each week, spent on review cards
    basis: str                    # "recent" or "plan"
    finish: date | None
    finish_plan: date | None
    finish_recent: date | None
    phases: tuple
    plan_day_hours: float = 0.0   # the plan, as entered: hours a study day
    plan_days: int = 0            # and study days a week

    @property
    def week_hours(self) -> float:
        if self.basis == "recent" and self.recent_week_hours:
            return self.recent_week_hours
        return self.plan_week_hours

    @property
    def new_week_hours(self) -> float:
        return new_hours(self.week_hours, self.review_week_hours)

    @property
    def left_hours(self) -> float:
        return self.left_personal / 60.0

    @property
    def done_fraction(self) -> float:
        if self.total_minutes <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - self.left_minutes / self.total_minutes))

    def phase(self, phase_id: str) -> PhaseTime | None:
        for row in self.phases:
            if row.phase_id == phase_id:
                return row
        return None


@dataclass(frozen=True, slots=True)
class SessionWork:
    """What one stretch of time produced."""
    seconds: int
    steps: int
    gate: int
    exercises: int
    quizzes: int
    projects: int
    reviews: int
    credited_minutes: float       # estimated minutes of that work

    @property
    def new_minutes(self) -> float:
        """Session time minus the time its review cards took."""
        return max(0.0, self.seconds / 60.0
                   - self.reviews * REVIEW_SECONDS / 60.0)

    @property
    def nothing(self) -> bool:
        return not (self.steps or self.gate or self.exercises or self.quizzes
                    or self.projects or self.reviews)

    def lines(self) -> list:
        """One plain line per kind of work done, for summaries."""
        out = []
        for count, one, many in (
                (self.steps, "study step ticked", "study steps ticked"),
                (self.gate, "gate check ticked", "gate checks ticked"),
                (self.exercises, "exercise passed", "exercises passed"),
                (self.quizzes, "quiz taken", "quizzes taken"),
                (self.projects, "project shipped", "projects shipped"),
                (self.reviews, "review card answered",
                 "review cards answered")):
            if count:
                out.append("%d %s" % (count, one if count == 1 else many))
        return out


def new_hours(week_hours: float, review_hours: float) -> float:
    return max(week_hours - review_hours, week_hours * MIN_NEW_SHARE)


def finish_date(minutes: float, week_hours: float, start: date) -> date | None:
    """The day ``minutes`` of work is done at ``week_hours`` a week."""
    if minutes <= 0:
        return None
    if week_hours <= 0:
        return None
    days = math.ceil(minutes / 60.0 / week_hours * 7.0)
    return start + timedelta(days=max(1, days))


def format_hours(minutes: float) -> str:
    """'45 min', '3.5 h', '120 h': the precision a reader can use."""
    if minutes < 60:
        return "%d min" % max(0, round(minutes))
    hours = minutes / 60.0
    if hours < 10:
        return "%.1f h" % hours
    return "%d h" % round(hours)


def format_day(day: date | None, today: date | None = None) -> str:
    if day is None:
        return "done"
    today = today or date.today()
    if day.year == today.year:
        return "%d %s" % (day.day, day.strftime("%b"))
    return "%d %s %d" % (day.day, day.strftime("%b"), day.year)


class Estimator:
    def __init__(self, curriculum, store, progress, today=date.today) -> None:
        self.c = curriculum
        self.s = store
        self.progress = progress
        self._today = today
        self._units = None
        self._memo = None

    # -- minutes per unit of work -------------------------------------------

    def units(self) -> dict:
        """Estimated minutes for every id that can be marked done: checklist
        lines, gate checks, exercises, ``quiz:<id>`` and projects."""
        if self._units is not None:
            return self._units
        units: dict = {}
        for phase in self.c.phases:
            if phase.no_progress or phase.est_hours <= 0:
                continue
            steps = list(phase.core_items)
            stretch = [i for i in phase.items if i not in steps]
            gate = list(phase.gate.items) if phase.gate else []
            exercises = list(self.c.exercises_for(phase.id))
            quizzes = list(self.c.quizzes_for(phase.id))
            projects = [p for p in self.c.projects_for(phase.id)
                        if not getattr(p, "optional", False)]
            present = {"steps": bool(steps), "gate": bool(gate),
                       "exercises": bool(exercises), "quiz": bool(quizzes),
                       "project": bool(projects)}
            weight = sum(share for kind, share in SHARES if present[kind])
            if weight <= 0:
                continue
            minutes = phase.est_hours * 60.0
            part = {kind: minutes * share / weight
                    for kind, share in SHARES if present[kind]}
            if steps:
                each = part["steps"] / len(steps)
                for item in steps:
                    units[item.id] = each
                # Stretch lines are real work when done, but never "left".
                for item in stretch:
                    units[item.id] = each
            for item in gate:
                units[item.id] = part["gate"] / len(gate)
            if exercises:
                total = sum(max(1, e.difficulty) for e in exercises)
                for e in exercises:
                    units[e.id] = part["exercises"] * max(1, e.difficulty) / total
            for quiz in quizzes:
                units["quiz:" + quiz.id] = part["quiz"] / len(quizzes)
            for project in projects:
                units[project.id] = part["project"] / len(projects)
        self._units = units
        return units

    def phase_minutes(self, phase, checked=None, passed=None,
                      statuses=None) -> tuple:
        """(total, left) estimated minutes for one phase."""
        units = self.units()
        checked = self.s.checked_ids() if checked is None else checked
        passed = self.s.passed_exercise_ids() if passed is None else passed
        statuses = self.s.project_statuses() if statuses is None else statuses
        total = left = 0.0
        if phase.no_progress:
            return 0.0, 0.0
        for item in phase.core_items:
            value = units.get(item.id, 0.0)
            total += value
            if item.id not in checked:
                left += value
        for item in (phase.gate.items if phase.gate else ()):
            value = units.get(item.id, 0.0)
            total += value
            if item.id not in checked:
                left += value
        for e in self.c.exercises_for(phase.id):
            value = units.get(e.id, 0.0)
            total += value
            if e.id not in passed:
                left += value
        for quiz in self.c.quizzes_for(phase.id):
            value = units.get("quiz:" + quiz.id, 0.0)
            total += value
            best = self.s.best_quiz_score(quiz.id)
            if not best or not best[1] or best[0] / best[1] < QUIZ_PROOF:
                left += value
        for project in self.c.projects_for(phase.id):
            value = units.get(project.id, 0.0)
            total += value
            if value and statuses.get(project.id) != "shipped":
                left += value
        return total, left

    # -- what a stretch of time produced -------------------------------------

    def work(self, start: str, end: str, seconds: int) -> SessionWork:
        units = self.units()
        done = self.s.work_between(start, end)
        gate_ids = {g.id for p in self.c.phases if p.gate
                    for g in p.gate.items}
        steps = [i for i in done["checked"] if i not in gate_ids]
        gate = [i for i in done["checked"] if i in gate_ids]
        credited = sum(units.get(i, 0.0) for i in done["checked"])
        credited += sum(units.get(i, 0.0) for i in done["passed"])
        credited += sum(units.get(i, 0.0) for i in done["shipped"])
        quizzes_seen = set()
        for attempt in done["quizzes"]:
            qid = attempt["quiz_id"]
            if qid in quizzes_seen or not attempt["total"]:
                continue
            quizzes_seen.add(qid)
            credited += units.get("quiz:" + qid, 0.0) * min(
                1.0, attempt["score"] / attempt["total"])
        return SessionWork(
            seconds=max(0, int(seconds)), steps=len(steps), gate=len(gate),
            exercises=len(done["passed"]), quizzes=len(done["quizzes"]),
            projects=len(done["shipped"]), reviews=done["reviews"],
            credited_minutes=credited)

    # -- pace ------------------------------------------------------------------

    def pace(self) -> Pace:
        timed = credited = 0.0
        count = 0
        for row in self.s.sessions(limit=200):
            seconds = int(row["seconds"] or 0)
            if seconds < 60:
                continue
            work = self.work(row["started_at"], row["ended_at"], seconds)
            new = work.new_minutes
            if new <= 0:
                continue
            count += 1
            timed += new
            # Ticking off lines done before the timer started would read as
            # superhuman speed; a session is credited at most a few times
            # its own length.
            credited += min(work.credited_minutes, new * SESSION_CREDIT_CAP)
        factor = (timed + PRIOR_MINUTES) / (credited + PRIOR_MINUTES)
        factor = max(PACE_LIMITS[0], min(PACE_LIMITS[1], factor))
        return Pace(factor=factor, sessions=count, timed_minutes=timed,
                    credited_minutes=credited)

    # -- weekly hours ------------------------------------------------------------

    def plan(self) -> tuple:
        """(hours a study day, study days a week) as the learner set them."""
        per_day = max(_number(self.s.setting("hours_per_day", 3.0), 3.0), 0.25)
        days = max(1, min(7, int(_number(
            self.s.setting("days_per_week", 5), 5.0))))
        return per_day, days

    def plan_week_hours(self) -> float:
        per_day, days = self.plan()
        return per_day * days

    def recent_week_hours(self) -> float | None:
        """Hours a week actually studied, once there is enough history."""
        today = self._today()
        first = self.s.first_study_day()
        if not first:
            return None
        try:
            first_day = date.fromisoformat(first)
        except ValueError:
            return None
        history = (today - first_day).days + 1
        if history < HISTORY_DAYS:
            return None
        span = min(history, RECENT_DAYS)
        since = (today - timedelta(days=span - 1)).isoformat()
        minutes, _days = self.s.minutes_since(since)
        if minutes <= 0:
            return None
        return minutes / 60.0 / (span / 7.0)

    def review_week_hours(self) -> float:
        today = self._today()
        since = (today - timedelta(days=13)).isoformat()
        per_day = self.s.reviews_since(since) / 14.0
        return per_day * 7 * REVIEW_SECONDS / 3600.0

    # -- the whole estimate --------------------------------------------------------

    def _version(self):
        db = getattr(self.s, "db", None)
        try:
            return (id(self.s), db.total_changes,
                    db.execute("PRAGMA data_version").fetchone()[0],
                    self._today())
        except Exception:
            return None

    def estimate(self) -> Estimate:
        key = self._version()
        if key is not None and self._memo is not None and self._memo[0] == key:
            return self._memo[1]
        result = self._estimate()
        self._memo = (key, result)
        return result

    def _estimate(self) -> Estimate:
        today = self._today()
        pace = self.pace()
        checked = self.s.checked_ids()
        passed = self.s.passed_exercise_ids()
        statuses = self.s.project_statuses()
        plan_hours = self.plan_week_hours()
        recent = self.recent_week_hours()
        reviews = self.review_week_hours()
        basis = "recent" if recent else "plan"
        week = recent if recent else plan_hours
        new_week = new_hours(week, reviews)

        rows = []
        total = left = 0.0
        running = 0.0
        for pid in self.progress.active_phase_ids():
            phase = self.c.phase(pid)
            if phase is None:
                continue
            phase_total, phase_left = self.phase_minutes(
                phase, checked, passed, statuses)
            total += phase_total
            left += phase_left
            personal = phase_left * pace.factor
            begins = finish_date(running, new_week, today) or today
            running += personal
            rows.append(PhaseTime(
                phase_id=pid, total_minutes=phase_total,
                left_minutes=phase_left, left_personal=personal,
                finish=finish_date(running, new_week, today)
                if phase_left > 0 else None,
                start=begins if phase_left > 0 else None))
        personal_left = left * pace.factor
        finish_plan = finish_date(personal_left,
                                  new_hours(plan_hours, reviews), today)
        finish_recent = (finish_date(personal_left, new_hours(recent, reviews),
                                     today) if recent else None)
        return Estimate(
            total_minutes=total, left_minutes=left,
            left_personal=personal_left, pace=pace,
            plan_week_hours=plan_hours, recent_week_hours=recent,
            review_week_hours=reviews, basis=basis,
            finish=finish_recent if recent else finish_plan,
            finish_plan=finish_plan, finish_recent=finish_recent,
            phases=tuple(rows), plan_day_hours=self.plan()[0],
            plan_days=self.plan()[1])
