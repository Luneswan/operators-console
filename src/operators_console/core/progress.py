"""Turning raw checkmarks into the numbers the interface shows."""
from __future__ import annotations

from dataclasses import dataclass

from .curriculum import Curriculum
from .models import Phase
from .storage import Store


@dataclass(frozen=True, slots=True)
class PhaseProgress:
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

    @property
    def ratio(self) -> float:
        return self.done / self.total if self.total else 0.0

    @property
    def percent(self) -> int:
        return round(self.ratio * 100)

    @property
    def is_complete(self) -> bool:
        return self.total > 0 and self.done >= self.total

    @property
    def is_started(self) -> bool:
        return self.done > 0

    @property
    def gate_cleared(self) -> bool:
        return self.gate_total > 0 and self.gate_done >= self.gate_total


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
        """Phase ids in the learner's plan, in teaching order."""
        track = self.c.track(self.s.setting("track", "generalist"))
        ordered = [p.id for p in self.c.phases if not p.no_progress]
        if track is None:
            return ordered
        chosen = set(track.core) | set(track.optional)
        return [pid for pid in ordered if pid in chosen]

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
        )

    def all_phases(self) -> dict:
        return {p.id: self.phase(p) for p in self.c.phases}

    # -- whole course ------------------------------------------------------

    def overview(self) -> Overview:
        plan = set(self.active_phase_ids())
        checked = self.s.checked_ids()
        done = total = complete = 0
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
        )

    # -- position in the course --------------------------------------------

    def current_phase_id(self) -> str:
        """The first phase in the plan that is not finished."""
        plan = self.active_phase_ids()
        stats = self.all_phases()
        for pid in plan:
            st = stats.get(pid)
            if st and not st.is_complete:
                return pid
        return plan[-1] if plan else self.c.phases[0].id

    def unlocked(self, phase_id: str) -> bool:
        """A phase is unlocked once its in-plan prerequisites are 80% done.

        Nothing is ever hard-locked: the gate is advisory, so a learner who
        already knows a topic can skip ahead. The interface shows the state
        rather than blocking navigation.
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
            if st and st.total and st.ratio < 0.8:
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
            if not st or not st.total:
                continue
            hours += phase.est_hours * (1.0 - st.ratio)
        per_day = max(float(self.s.setting("hours_per_day", 3.0)), 0.25)
        days_per_week = max(int(self.s.setting("days_per_week", 5)), 1)
        weeks = hours / (per_day * days_per_week)
        return int(round(weeks * 7))
