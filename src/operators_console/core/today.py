"""What to do right now.

The dashboard asks one question on the learner's behalf: given where I am,
what is the next hour supposed to look like? This module answers it as a short
ordered list of concrete actions, never more than a handful, so opening the app
never turns into a planning exercise.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from .adaptive import Planner
from .curriculum import Curriculum
from .progress import Progress
from .progress import _number as _parse_number
from .storage import Store

# action kinds the interface knows how to route
LEARN = "learn"
REVIEW = "review"
PRACTICE = "practice"
QUIZ = "quiz"
PROJECT = "project"
GATE = "gate"
LOG = "log"

#: Where "not today" is remembered: {"2026-09-23": ["quiz:q05", ...]}.
DISMISSED_SETTING = "plan_dismissed"

#: How old the learner's last "first thing tomorrow" may be before it is
#: stale enough to leave alone.
PROMISE_DAYS = 3

#: The most actions the list shows. The evening log is not counted: it is a
#: minute long and it feeds tomorrow's first action.
MAX_ACTIONS = 5

#: Once the plan is finished, a quiz below this is worth one more sitting.
MAINTENANCE_QUIZ = 0.90

# Retrieval before new reading: a quiz or an exercise on what was read
# yesterday does more for it than the next page does.
WEIGHT_PROMISE = 95
WEIGHT_QUIZ = 94
WEIGHT_PRACTICE = 92
WEIGHT_LEARN = 90
WEIGHT_MIXED = 55


def plan_key(action) -> str:
    """A name for an action that survives a rebuild of the plan.

    The kind and what it points at, never the title: "Clear 7 due reviews"
    becomes "Clear 6 due reviews" the moment one is answered, and an action
    pushed off until tomorrow has to stay pushed off across that.
    """
    return "%s:%s" % (action.kind, action.target)


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
        """Today's list: what to do, in order, minus anything hidden."""
        return self.split(now)[0]

    def split(self, now: datetime | None = None) -> tuple:
        """``(what to show, what was pushed off until tomorrow)``.

        Both halves in one pass: building the plan reads most of the store,
        and the dashboard needs the second number to offer them back.
        """
        now = now or datetime.now(timezone.utc)
        budget = int(_number(self.s.setting("hours_per_day", 3.0), 3.0) * 60)
        hidden_keys = self.dismissed_keys()
        candidates = self._candidates(now, budget)
        hidden = [a for a in candidates if plan_key(a) in hidden_keys]
        keep = [a for a in candidates if plan_key(a) not in hidden_keys]
        keep.sort(key=lambda a: -a.weight)
        reserved = self._reserved if self._reserved in keep else None
        return self._fit(keep, budget, reserved), hidden

    _reserved = None

    def _candidates(self, now: datetime, budget: int) -> list:
        actions: list[Action] = []
        self._reserved = None

        due = self.s.card_counts(now)["due"]
        if due:
            minutes = max(5, min(30, round(due * 0.4)))
            actions.append(Action(
                REVIEW,
                "Clear %d due review%s" % (due, "" if due == 1 else "s"),
                "Spaced repetition keeps earlier phases from decaying. "
                "Do this first, while it is small.",
                "", minutes, weight=100))

        # A finished plan has no current phase to study, practise or gate:
        # the marker still names the last one, and following it would offer
        # the same completed phase every morning for ever.
        finished = self.p.is_finished
        if finished:
            actions.extend(self._maintenance(budget))

        pid = "" if finished else self.p.current_phase_id()
        phase = self.c.phase(pid) if pid else None
        if phase is not None:
            stats = self.p.phase(phase)
            next_item = self._next_unchecked(pid)
            if next_item:
                actions.append(Action(
                    LEARN,
                    "Phase %s - %s" % (phase.num, phase.name),
                    next_item,
                    pid, max(30, min(90, budget // 3)),
                    weight=WEIGHT_LEARN))

            ex = self._next_exercise(pid)
            if ex:
                actions.append(Action(
                    PRACTICE,
                    "Practise: %s" % ex.title,
                    "%s - difficulty %d of 5. Write it yourself before "
                    "looking at the hints." % (ex.topic, ex.difficulty),
                    ex.id, 20, weight=WEIGHT_PRACTICE))

            quiz = self._weak_quiz(pid)
            if quiz is not None:
                best = self.s.best_quiz_score(quiz.id)
                label = ("Not attempted yet" if best is None
                         else "Best so far %d/%d" % best)
                actions.append(Action(
                    QUIZ, "Check yourself: %s" % quiz.name, label,
                    quiz.id, 10, weight=WEIGHT_QUIZ))

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

        mixed = None if finished else self._mixed_in(pid)
        if mixed is not None:
            actions.append(mixed)
            self._reserved = mixed

        promise, said_on = self.promise()
        if promise:
            actions.append(Action(
                LEARN, "You said you'd start with: %s" % promise,
                "Your own words in the log on %s." % said_on,
                "", 15, weight=WEIGHT_PROMISE))

        if not self._logged_today():
            actions.append(Action(
                LOG, "Write today's log entry",
                "One sentence on what you built and where you got stuck. "
                "Takes a minute and makes the next session start faster.",
                "", 5, weight=10))

        return actions

    # -- once the curriculum itself is done --------------------------------

    def _maintenance(self, budget: int) -> list:
        """What is left when every phase in the plan is complete.

        Finishing the reading is not the end of the work: the review deck
        still comes due, projects are the half of the course most people
        leave unbuilt, and a quiz that was scraped through is worth one more
        sitting. The due reviews are already on the list before this runs.
        """
        out: list[Action] = []
        plan = set(self.p.active_phase_ids())
        statuses = self.s.project_statuses()
        for project in self.c.projects:
            if project.phase not in plan:
                continue
            status = statuses.get(project.id, "not-started")
            if status == "shipped":
                continue
            out.append(Action(
                PROJECT,
                "%s: %s" % ("Start" if status == "not-started" else "Ship",
                            project.title),
                project.brief, project.id,
                max(45, budget // 3), weight=75))
        quiz = self._weakest_quiz(plan)
        if quiz is not None:
            best = self.s.best_quiz_score(quiz.id)
            out.append(Action(
                QUIZ, "Sit %s again" % quiz.name,
                ("Never attempted - the one piece of the plan you have no "
                 "measurement for." if best is None else
                 "Best so far %d/%d, the weakest score you have left." % best),
                quiz.id, 10, weight=60))
        return out

    def _weakest_quiz(self, plan: set):
        """The lowest-scoring quiz anywhere in the plan, if it is worth a revisit."""
        worst, worst_score = None, 2.0
        for quiz in self.c.quizzes:
            if quiz.phase not in plan:
                continue
            best = self.s.best_quiz_score(quiz.id)
            score = (best[0] / best[1]) if best and best[1] else 0.0
            if score < worst_score:
                worst, worst_score = quiz, score
        return worst if worst_score < MAINTENANCE_QUIZ else None

    # -- one slot for another phase ------------------------------------------

    def _mixed_in(self, pid: str):
        """One action from a phase other than the current one.

        Blocked practice - a whole day on one phase - feels productive and is
        forgotten faster than the same time mixed across topics. The weakest
        phase in the plan comes first; with none behind, the finished phase
        that was quizzed longest ago comes back instead. It has a slot of its
        own on the list, so the current phase's work never crowds it out.
        """
        plan = self.p.active_phase_ids()
        in_plan = set(plan)
        for weak in self.planner.weak_areas(limit=len(plan) or 1):
            if weak == pid or weak not in in_plan:
                continue
            wphase = self.c.phase(weak)
            if wphase is None:
                continue
            return Action(
                LEARN, "Shore up %s" % wphase.name,
                "Your scores here are behind the rest of the plan. A short "
                "session on it today, between the new work.",
                wphase.id, 25, weight=WEIGHT_MIXED)

        stats = self.p.all_phases()
        oldest, oldest_when = None, None
        for other in plan:
            st = stats.get(other)
            if other == pid or st is None or not st.is_proven:
                continue
            when = self._last_quizzed(other)
            if oldest is None or when < oldest_when:
                oldest, oldest_when = other, when
        phase = self.c.phase(oldest) if oldest else None
        if phase is None:
            return None
        quizzes = self.c.quizzes_for(phase.id)
        if quizzes:
            return Action(
                QUIZ, "Mix in phase %s: %s" % (phase.num, quizzes[0].name),
                "Finished a while ago. Answering it cold today is what keeps "
                "it.", quizzes[0].id, 10, weight=WEIGHT_MIXED)
        return Action(
            LEARN, "Mix in phase %s - %s" % (phase.num, phase.name),
            "Finished a while ago. Explain its gate checks from memory, then "
            "open the page to see what you missed.",
            phase.id, 15, weight=WEIGHT_MIXED)

    def _last_quizzed(self, phase_id: str) -> str:
        """When any quiz of the phase was last sat; "" when never."""
        latest = ""
        for quiz in self.c.quizzes_for(phase_id):
            rows = self.s.quiz_attempts(quiz.id, limit=1)
            if rows:
                latest = max(latest, str(rows[0]["finished_at"] or ""))
        return latest

    # -- what the learner told the log -------------------------------------

    def promise(self) -> tuple:
        """The last "first thing tomorrow" they wrote, and the day they wrote it.

        The Log asks for it every evening and then never mentioned it again,
        so the one line in the whole app written by the learner about what to
        do next was the one line nothing ever read. Anything older than
        ``PROMISE_DAYS`` is stale - already done, or it did not matter - and
        is left alone rather than nagged about.
        """
        today = date.today()
        cutoff = today - timedelta(days=PROMISE_DAYS)
        for row in self.s.logs(limit=60):
            try:
                day = date.fromisoformat(str(row["day"]))
            except (TypeError, ValueError):
                continue
            if day < cutoff:
                break               # rows arrive newest first
            if day > today:
                continue            # a day that has not happened yet
            text = str(row["next_up"] or "").strip()
            if text:
                return text, day.isoformat()
        return "", ""

    def hours_today(self) -> float:
        """Study time the learner has logged for today."""
        today = date.today().isoformat()
        total = 0.0
        for row in self.s.logs(limit=60):
            day = str(row["day"])
            if day > today:
                continue
            if day < today:
                break
            total += _number(row["hours"], 0.0)
        return total

    # -- "not today" -------------------------------------------------------

    def dismissed_keys(self, day: str = "") -> set:
        """Keys the learner pushed off until tomorrow, for one day."""
        day = day or date.today().isoformat()
        stored = self.s.setting(DISMISSED_SETTING, {})
        if not isinstance(stored, dict):
            return set()
        keys = stored.get(day) or []
        return {str(k) for k in keys} if isinstance(keys, list) else set()

    def dismiss(self, action, day: str = "") -> None:
        """Hide one action for the rest of the day.

        Only the current day is kept. Yesterday's "not today" is exactly
        that, and pruning on write means the setting can never grow without
        bound however long the app is used.
        """
        day = day or date.today().isoformat()
        key = action if isinstance(action, str) else plan_key(action)
        keys = self.dismissed_keys(day)
        if key in keys:
            return
        keys.add(key)
        self.s.set_setting(DISMISSED_SETTING, {day: sorted(keys)})

    def restore(self, day: str = "") -> None:
        """Bring back everything hidden today."""
        day = day or date.today().isoformat()
        if not self.dismissed_keys(day):
            return
        self.s.set_setting(DISMISSED_SETTING, {})

    # -- helpers -----------------------------------------------------------

    def _fit(self, actions: list, budget: int, reserved=None) -> list:
        """At most ``MAX_ACTIONS`` that fit the day, and the log after them.

        Reviews and the log are never cut for time, and the log is not cut
        for count either. ``reserved`` - the action from another phase -
        keeps a slot and its minutes whenever it fits the day at all, instead
        of being ranked out by the current phase's work.
        """
        if reserved is not None and reserved.minutes > budget:
            reserved = None
        cap = MAX_ACTIONS - (1 if reserved is not None else 0)
        room = budget - (reserved.minutes if reserved is not None else 0)
        out, logs, spent = [], [], 0
        for action in actions:
            if action is reserved:
                continue
            if action.kind == LOG:
                logs.append(action)
                continue
            if len(out) >= cap:
                continue
            if action.kind == REVIEW or spent + action.minutes <= room:
                out.append(action)
                spent += action.minutes
        if reserved is not None:
            out.append(reserved)
            out.sort(key=lambda a: -a.weight)
        return out + logs

    def _next_unchecked(self, phase_id: str) -> str:
        phase = self.c.phase(phase_id)
        if phase is None:
            return ""
        checked = self.s.checked_ids()
        for section in phase.sections:
            if section.optional:
                continue
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
        today = date.today().isoformat()
        return any(row["day"] == today for row in self.s.logs(limit=10))


def _number(value, fallback: float) -> float:
    """One parser for numeric settings; see progress._number."""
    return _parse_number(value, fallback)


def _plain(text: str) -> str:
    return text.replace("<em>", "").replace("</em>", "")
