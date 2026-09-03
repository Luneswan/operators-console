"""What to do right now.

The dashboard asks one question on the learner's behalf: given where I am,
what is the next hour supposed to look like? This module answers it as a short
ordered list of concrete actions, never more than a handful, so opening the app
never turns into a planning exercise.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .adaptive import Planner
from .curriculum import Curriculum
from .progress import Progress
from .storage import Store

# action kinds the interface knows how to route
LEARN = "learn"
REVIEW = "review"
PRACTICE = "practice"
QUIZ = "quiz"
PROJECT = "project"
GATE = "gate"
LOG = "log"


@dataclass(frozen=True, slots=True)
class Action:
    kind: str
    title: str
    detail: str
    target: str
    minutes: int
    weight: int = 0


class TodayPlan:
    """Builds the daily action list."""

    def __init__(self, curriculum: Curriculum, store: Store,
                 progress: Progress, planner: Planner) -> None:
        self.c = curriculum
        self.s = store
        self.p = progress
        self.planner = planner

    def build(self, now: datetime | None = None) -> list:
        now = now or datetime.now(timezone.utc)
        budget = int(float(self.s.setting("hours_per_day", 3.0)) * 60)
        actions: list[Action] = []

        due = self.s.card_counts(now)["due"]
        if due:
            minutes = max(5, min(30, round(due * 0.4)))
            actions.append(Action(
                REVIEW,
                "Clear %d due review%s" % (due, "" if due == 1 else "s"),
                "Spaced repetition keeps earlier phases from decaying. "
                "Do this first, while it is small.",
                "", minutes, weight=100))

        pid = self.p.current_phase_id()
        phase = self.c.phase(pid)
        if phase is not None:
            stats = self.p.phase(phase)
            next_item = self._next_unchecked(pid)
            if next_item:
                actions.append(Action(
                    LEARN,
                    "Phase %s - %s" % (phase.num, phase.name),
                    next_item,
                    pid, max(30, min(90, budget // 3)), weight=90))

            ex = self._next_exercise(pid)
            if ex:
                actions.append(Action(
                    PRACTICE,
                    "Practise: %s" % ex.title,
                    "%s - difficulty %d of 5. Write it yourself before "
                    "looking at the hints." % (ex.topic, ex.difficulty),
                    ex.id, 20, weight=80))

            quiz = self._weak_quiz(pid)
            if quiz is not None:
                best = self.s.best_quiz_score(quiz.id)
                label = ("Not attempted yet" if best is None
                         else "Best so far %d/%d" % best)
                actions.append(Action(
                    QUIZ, "Check yourself: %s" % quiz.name, label,
                    quiz.id, 10, weight=60))

            if stats.gate_total and not stats.gate_cleared and stats.ratio > 0.7:
                remaining = stats.gate_total - stats.gate_done
                actions.append(Action(
                    GATE,
                    "Clear the phase %s gate" % phase.num,
                    "%d of %d checks left. The gate is the proof, not the "
                    "reading." % (remaining, stats.gate_total),
                    pid, 45, weight=70))

            project = self._active_project(pid)
            if project is not None:
                state = self.s.project(project.id)
                verb = ("Start" if state["status"] == "not-started"
                        else "Push forward")
                actions.append(Action(
                    PROJECT, "%s: %s" % (verb, project.title),
                    project.brief, project.id,
                    max(45, budget // 3), weight=75))

        weak = self.planner.weak_areas(limit=1)
        if weak and weak[0] != pid:
            wphase = self.c.phase(weak[0])
            if wphase is not None:
                actions.append(Action(
                    LEARN, "Shore up %s" % wphase.name,
                    "Your scores here are behind the rest of the plan.",
                    wphase.id, 25, weight=50))

        if not self._logged_today():
            actions.append(Action(
                LOG, "Write today's log entry",
                "One sentence on what you built and where you got stuck. "
                "Takes a minute and makes the next session start faster.",
                "", 5, weight=10))

        actions.sort(key=lambda a: -a.weight)
        return self._fit(actions, budget)

    # -- helpers -----------------------------------------------------------

    def _fit(self, actions: list, budget: int) -> list:
        out, spent = [], 0
        for action in actions:
            if action.kind in (REVIEW, LOG) or spent + action.minutes <= budget:
                out.append(action)
                spent += action.minutes
            if len(out) >= 5:
                break
        return out

    def _next_unchecked(self, phase_id: str) -> str:
        phase = self.c.phase(phase_id)
        if phase is None:
            return ""
        checked = self.s.checked_ids()
        for section in phase.sections:
            for item in section.items:
                if item.id not in checked:
                    return "%s - %s" % (section.title, _plain(item.text))
        return ""

    def _next_exercise(self, phase_id: str):
        passed = self.s.passed_exercise_ids()
        pool = [e for e in self.c.exercises_for(phase_id) if e.id not in passed]
        if not pool:
            return None
        pool.sort(key=lambda e: (e.difficulty, e.id))
        return pool[0]

    def _weak_quiz(self, phase_id: str):
        quizzes = self.c.quizzes_for(phase_id)
        if not quizzes:
            return None
        worst, worst_score = None, 2.0
        for quiz in quizzes:
            best = self.s.best_quiz_score(quiz.id)
            score = (best[0] / best[1]) if best and best[1] else 0.0
            if score < worst_score:
                worst, worst_score = quiz, score
        return worst if worst_score < 0.85 else None

    def _active_project(self, phase_id: str):
        projects = self.c.projects_for(phase_id)
        if not projects:
            return None
        statuses = self.s.project_statuses()
        for project in projects:
            if statuses.get(project.id) == "in-progress":
                return project
        for project in projects:
            if statuses.get(project.id, "not-started") == "not-started":
                return project
        return None

    def _logged_today(self) -> bool:
        from datetime import date
        today = date.today().isoformat()
        return any(row["day"] == today for row in self.s.logs(limit=10))


def _plain(text: str) -> str:
    return text.replace("<em>", "").replace("</em>", "")
