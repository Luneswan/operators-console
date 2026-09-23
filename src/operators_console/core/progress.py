"""Turning raw checkmarks into the numbers the interface shows."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .curriculum import Curriculum
from .models import Phase
from .storage import Store


def _number(value, fallback: float) -> float:
    """Settings arrive as JSON and a hand-edited backup can hold anything.

    Including NaN and Infinity, which json and float() both accept and which
    then crash the first int() they reach.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


#: The best quiz score, as a fraction, that counts as proof for a phase.
QUIZ_PROOF = 0.85

#: The share of a phase's graded exercises that has to pass.
EXERCISE_PROOF = 0.60


def exercises_needed(total: int) -> int:
    """How many of ``total`` exercises have to pass for the phase to count."""
    if total <= 0:
        return 0
    return max(1, math.ceil(EXERCISE_PROOF * total - 1e-9))


@dataclass(frozen=True, slots=True)
class PhaseProgress:
    """Where one phase stands, read two ways.

    *Read* is the tick meter: every line and gate check ticked. *Proven* is
    what a phase needs before it counts as finished: the gate ticked, the
    phase's quiz passed at 85% or better, at least 60% of its exercises
    passed and one of its required projects shipped - each only where the
    phase has one. Ticking every box used to finish a phase, unlock the next
    and move the marker with no exercise, quiz or project behind it.
    """
    phase_id: str
    done: int
    total: int
    gate_done: int
    gate_total: int
    exercises_done: int
    exercises_total: int
    quiz_best: float
    projects_shipped: int
    projects_total: int
    quizzes_total: int = 0
    core_projects_shipped: int = 0
    core_projects_total: int = 0

    @property
    def ratio(self) -> float:
        return self.done / self.total if self.total else 0.0

    @property
    def percent(self) -> int:
        return round(self.ratio * 100)

    @property
    def is_read(self) -> bool:
        """Every line and gate check in the phase is ticked."""
        return self.total > 0 and self.done >= self.total

    @property
    def is_complete(self) -> bool:
        """The old name for ``is_read``, kept for callers that meant reading.

        Anything that decides where the learner is, what unlocks or whether
        the plan is finished reads ``is_proven`` instead.
        """
        return self.is_read

    @property
    def is_started(self) -> bool:
        return self.done > 0

    @property
    def gate_cleared(self) -> bool:
        return self.gate_total > 0 and self.gate_done >= self.gate_total

    # -- proof ---------------------------------------------------------------

    def proof(self) -> list:
        """Each thing the phase asks for, as ``(name, met, fraction)``.

        Only what the phase actually has is listed: a phase with no quiz is
        not held back by one.
        """
        parts = []
        if self.gate_total:
            parts.append(("gate", self.gate_cleared,
                          min(1.0, self.gate_done / self.gate_total)))
        if self.quizzes_total:
            parts.append(("quiz", self.quiz_best >= QUIZ_PROOF - 1e-9,
                          min(1.0, self.quiz_best / QUIZ_PROOF)))
        if self.exercises_total:
            needed = exercises_needed(self.exercises_total)
            parts.append(("exercises", self.exercises_done >= needed,
                          min(1.0, self.exercises_done / needed)))
        if self.core_projects_total:
            parts.append(("project", self.core_projects_shipped >= 1,
                          1.0 if self.core_projects_shipped else 0.0))
        return parts

    @property
    def is_proven(self) -> bool:
        """The phase is finished: its gate, quiz, exercises and a project.

        A phase that asks for none of them - no gate, no quiz, no exercise,
        no project - falls back to its reading, since there is nothing else
        it could be measured by.
        """
        if self.total <= 0:
            return False
        parts = self.proof()
        if not parts:
            return self.is_read
        return all(met for _name, met, _fraction in parts)

    @property
    def proof_ratio(self) -> float:
        parts = self.proof()
        if not parts:
            return self.ratio
        return sum(fraction for _n, _m, fraction in parts) / len(parts)

    @property
    def proof_percent(self) -> int:
        return 100 if self.is_proven else min(99, round(self.proof_ratio * 100))

    def outstanding(self) -> list:
        """What is still missing before the phase counts, in plain words."""
        out = []
        for name, met, _fraction in self.proof():
            if met:
                continue
            if name == "gate":
                left = self.gate_total - self.gate_done
                out.append("%d gate check%s" % (left, "" if left == 1 else "s"))
            elif name == "quiz":
                out.append("the quiz at %d%% or better (best so far %d%%)"
                           % (round(QUIZ_PROOF * 100),
                              round(self.quiz_best * 100)))
            elif name == "exercises":
                needed = exercises_needed(self.exercises_total)
                left = needed - self.exercises_done
                out.append("%d more exercise%s passed (%d of %d needed)"
                           % (left, "" if left == 1 else "s", needed,
                              self.exercises_total))
            elif name == "project":
                out.append("one project shipped")
        return out


def proof_line(stats) -> str:
    """"Read 100% - Proven 60%", and what is still outstanding."""
    head = "Read %d%%  -  Proven %d%%" % (stats.percent, stats.proof_percent)
    if stats.is_proven:
        return head + ". This phase counts as finished."
    missing = stats.outstanding()
    if not missing:
        return head + "."
    return "%s. Still to prove it: %s." % (head, ", ".join(missing))


@dataclass(frozen=True, slots=True)
class Overview:
    done: int
    total: int
    phases_complete: int
    phases_total: int
    hours: float
    streak: int
    longest_streak: int
    due_cards: int
    exercises_done: int
    exercises_total: int
    projects_shipped: int
    projects_total: int
    #: Phases with every line ticked. ``phases_complete`` counts proven ones.
    phases_read: int = 0

    @property
    def percent(self) -> int:
        return round(self.done / self.total * 100) if self.total else 0


class Progress:
    """Read-only view over the store, scoped by the learner's active track."""

    def __init__(self, curriculum: Curriculum, store: Store) -> None:
        self.c = curriculum
        self.s = store

    # -- track scoping ----------------------------------------------------

    def active_phase_ids(self) -> list:
        """Phase ids in the learner's plan, in teaching order.

        The plan is what the Roadmap shows: the track's core and optional
        phases plus the phases added for the learner's goals. The meter,
        Today, Projects and Review all read it here, so a phase the Roadmap
        lists is never invisible to the rest of the app - ticks in a goal
        phase used to move nothing, and its quiz mistakes were never reviewed.
        """
        track = self.c.track(self.s.setting("track", "generalist"))
        ordered = [p.id for p in self.c.phases if not p.no_progress]
        if track is None:
            return ordered
        chosen = set(track.core) | set(track.optional)
        chosen |= set(self.goal_phase_ids(chosen))
        return [pid for pid in ordered if pid in chosen]

    def goal_tags(self) -> set:
        from .adaptive import GOALS      # adaptive imports this module
        picked = set(self.s.setting("goals", []) or [])
        tags: set = set()
        for goal_id, _label, goal_tags in GOALS:
            if goal_id in picked:
                tags.update(goal_tags)
        return tags

    def goal_phase_ids(self, already: set) -> list:
        """Phases outside `already` that match one of the learner's goals."""
        tags = self.goal_tags()
        if not tags:
            return []
        return [p.id for p in self.c.phases
                if not p.no_progress and p.id not in already
                and tags.intersection(p.tags)]

    def is_in_plan(self, phase_id: str) -> bool:
        return phase_id in set(self.active_phase_ids())

    # -- per phase --------------------------------------------------------

    def phase(self, phase: Phase) -> PhaseProgress:
        checked = self.s.checked_ids()
        item_ids = [i.id for i in phase.items]
        gate_ids = [g.id for g in phase.gate.items] if phase.gate else []
        exercises = self.c.exercises_for(phase.id)
        passed = self.s.passed_exercise_ids()
        quizzes = self.c.quizzes_for(phase.id)

        best = 0.0
        if quizzes:
            scores = []
            for q in quizzes:
                b = self.s.best_quiz_score(q.id)
                scores.append(b[0] / b[1] if b and b[1] else 0.0)
            best = sum(scores) / len(scores)

        projects = self.c.projects_for(phase.id)
        statuses = self.s.project_statuses()
        shipped = sum(1 for p in projects
                      if statuses.get(p.id) == "shipped")
        # A project the curriculum marks optional never holds a phase back.
        core = [p for p in projects if not getattr(p, "optional", False)]

        return PhaseProgress(
            phase_id=phase.id,
            done=sum(1 for i in item_ids + gate_ids if i in checked),
            total=len(item_ids) + len(gate_ids),
            gate_done=sum(1 for i in gate_ids if i in checked),
            gate_total=len(gate_ids),
            exercises_done=sum(1 for e in exercises if e.id in passed),
            exercises_total=len(exercises),
            quiz_best=best,
            projects_shipped=shipped,
            projects_total=len(projects),
            quizzes_total=len(quizzes),
            core_projects_shipped=sum(1 for p in core
                                      if statuses.get(p.id) == "shipped"),
            core_projects_total=len(core),
        )

    def all_phases(self) -> dict:
        return {p.id: self.phase(p) for p in self.c.phases}

    # -- whole course ------------------------------------------------------

    def overview(self) -> Overview:
        plan = set(self.active_phase_ids())
        checked = self.s.checked_ids()
        done = total = complete = read = 0
        for phase in self.c.phases:
            if phase.no_progress or phase.id not in plan:
                continue
            ids = phase.trackable_ids
            if not ids:
                continue
            hit = sum(1 for i in ids if i in checked)
            done += hit
            total += len(ids)
            if hit == len(ids):
                read += 1
            if self.phase(phase).is_proven:
                complete += 1

        exercises = [e for e in self.c.exercises if e.phase in plan]
        passed = self.s.passed_exercise_ids()
        projects = [p for p in self.c.projects if p.phase in plan]
        statuses = self.s.project_statuses()
        current, longest = self.s.streak()

        return Overview(
            done=done,
            total=total,
            phases_complete=complete,
            phases_total=sum(1 for p in self.c.phases
                             if p.id in plan and p.trackable_ids),
            hours=self.s.total_hours(),
            streak=current,
            longest_streak=longest,
            due_cards=self.s.card_counts()["due"],
            exercises_done=sum(1 for e in exercises if e.id in passed),
            exercises_total=len(exercises),
            projects_shipped=sum(1 for p in projects
                                 if statuses.get(p.id) == "shipped"),
            projects_total=len(projects),
            phases_read=read,
        )

    # -- position in the course --------------------------------------------

    def current_phase_id(self) -> str:
        """The first phase in the plan that is not proven.

        Proven, not read: ticking every line of a phase no longer moves the
        marker on. The gate, the quiz, the exercises and a project do (see
        ``PhaseProgress.is_proven``).

        A phase with nothing to tick is skipped rather than treated as
        unfinished. ``is_proven`` is false whenever ``total`` is zero, so
        without this an empty phase - one still being written, or one trimmed
        by a track - would hold the position marker forever and the learner
        would be told to study a page with no content on it.
        """
        plan = self.active_phase_ids()
        stats = self.all_phases()
        for pid in plan:
            st = stats.get(pid)
            if st and st.total and not st.is_proven:
                return pid
        if plan:
            return plan[-1]
        return self.c.phases[0].id if self.c.phases else ""

    @property
    def is_finished(self) -> bool:
        """True once every trackable phase in the plan is proven.

        ``current_phase_id`` has to name a phase whatever the state, so when
        the plan runs out it falls through to the last one. That is a
        sensible place to stand, but it is not a position: read on its own it
        pins "YOU ARE HERE" to the final phase for ever and tells a learner
        who has finished the whole curriculum that there is nothing
        outstanding today. The interfaces ask this first and say something
        else entirely.

        A plan with nothing trackable in it - an empty curriculum, a track
        trimmed to phases that have no checklist - is not finished; there was
        never anything to finish.
        """
        stats = self.all_phases()
        tracked = [st for st in (stats.get(pid)
                                 for pid in self.active_phase_ids())
                   if st is not None and st.total]
        return bool(tracked) and all(st.is_proven for st in tracked)

    def started_on(self) -> str:
        """The day the learner set the plan up, as an ISO date, if known.

        Onboarding writes it. A profile restored from a backup taken before
        that setting existed has nothing, so the first day with any recorded
        activity stands in for it.
        """
        stamp = str(self.s.setting("started_on", "") or "").strip()
        if stamp:
            return stamp
        days = self.s.active_days()
        return days[0] if days else ""

    def unlocked(self, phase_id: str) -> bool:
        """A phase is unlocked once its in-plan prerequisites are proven.

        It used to be 80% of the ticks, which a learner could reach without
        passing anything. Nothing is ever hard-locked: the state is advisory,
        so a learner who already knows a topic can skip ahead. The interface
        shows it rather than blocking navigation.
        """
        phase = self.c.phase(phase_id)
        if phase is None or not phase.prereq:
            return True
        plan = set(self.active_phase_ids())
        stats = self.all_phases()
        for req in phase.prereq:
            if req not in plan:
                continue
            st = stats.get(req)
            if st and st.total and not st.is_proven:
                return False
        return True

    def estimated_days_left(self) -> int:
        """Rough finish estimate from remaining work and declared study time."""
        plan = set(self.active_phase_ids())
        stats = self.all_phases()
        hours = 0.0
        for phase in self.c.phases:
            if phase.id not in plan:
                continue
            st = stats.get(phase.id)
            if not st or not st.total or st.is_proven:
                continue
            # Half the work is the reading and half is the proof: a phase
            # read to the end with nothing passed still has hours in it.
            done = (st.ratio + st.proof_ratio) / 2
            hours += phase.est_hours * (1.0 - done)
        per_day = max(_number(self.s.setting("hours_per_day", 3.0), 3.0), 0.25)
        days_per_week = max(int(_number(
            self.s.setting("days_per_week", 5), 5.0)), 1)
        weeks = hours / (per_day * days_per_week)
        return int(round(weeks * 7))
