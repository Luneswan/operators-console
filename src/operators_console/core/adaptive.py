"""Reshaping the roadmap around the learner.

Three inputs move the plan:

    the chosen track      which phases are core, optional or out of scope
    declared goals        interest tags picked during onboarding
    measured performance  quiz scores, review lapses and exercise failures

The result is an ordered list of phases with a reason attached to each, so the
interface can always answer "why is this next?".
"""
from __future__ import annotations

from dataclasses import dataclass

from .curriculum import Curriculum
from .progress import Progress
from .storage import Store

# Onboarding interests map onto the tags carried by each phase.
GOALS = (
    ("web", "Build websites and APIs", ("backend", "web", "sql")),
    ("data", "Work with data", ("data", "sql", "engineering")),
    ("ai", "Machine learning and AI", ("ai", "ml")),
    ("automation", "Automate boring work", ("automation", "scraping")),
    ("games", "Games and graphics", ("language", "performance")),
    ("devops", "Infrastructure and deployment", ("devops", "linux", "deployment")),
    ("security", "Security and hacking", ("security", "networking")),
    ("interview", "Pass a technical interview", ("interview", "algorithms")),
    ("fundamentals", "Understand how computers work", ("cs", "systems", "internals")),
)

EXPERIENCE_LEVELS = (
    ("none", "Never written code before"),
    ("some", "Some Python, but it does not stick"),
    ("other", "Confident in another language"),
    ("working", "I write Python at work already"),
)


@dataclass(frozen=True, slots=True)
class PlannedPhase:
    phase_id: str
    order: int
    role: str          # 'core', 'optional' or 'extra'
    reason: str
    unlocked: bool
    percent: int


class Planner:
    """Builds the personalised phase ordering."""

    def __init__(self, curriculum: Curriculum, store: Store,
                 progress: Progress) -> None:
        self.c = curriculum
        self.s = store
        self.p = progress

    def goal_tags(self) -> set:
        chosen = set(self.s.setting("goals", []) or [])
        tags: set = set()
        for gid, _label, gtags in GOALS:
            if gid in chosen:
                tags.update(gtags)
        return tags

    def roadmap(self) -> list:
        """Ordered plan, core phases first, then goal-matched extras."""
        track = self.c.track(self.s.setting("track", "generalist"))
        core = list(track.core) if track else [p.id for p in self.c.phases
                                               if not p.no_progress]
        optional = list(track.optional) if track else []
        tags = self.goal_tags()
        experience = self.s.setting("experience", "none")
        stats = self.p.all_phases()

        # Someone already fluent in another language can move through the
        # absolute basics faster, but never skip them silently.
        teaching_order = {p.id: i for i, p in enumerate(self.c.phases)}

        def extras() -> list:
            out = []
            for phase in self.c.phases:
                if phase.no_progress or phase.id in core or phase.id in optional:
                    continue
                if tags and tags.intersection(phase.tags):
                    out.append(phase.id)
            return out

        rows: list[PlannedPhase] = []
        order = 0
        for pid in sorted(core, key=lambda x: teaching_order.get(x, 99)):
            rows.append(self._row(pid, order, "core",
                                  self._core_reason(pid, experience), stats))
            order += 1
        for pid in sorted(optional, key=lambda x: teaching_order.get(x, 99)):
            rows.append(self._row(pid, order, "optional",
                                  "Recommended for your track once the core is solid.",
                                  stats))
            order += 1
        for pid in sorted(extras(), key=lambda x: teaching_order.get(x, 99)):
            phase = self.c.phase(pid)
            matched = ", ".join(sorted(tags.intersection(phase.tags)))
            rows.append(self._row(pid, order, "extra",
                                  "Added because you said you care about %s." % matched,
                                  stats))
            order += 1
        return rows

    def _row(self, pid: str, order: int, role: str, reason: str,
             stats: dict) -> PlannedPhase:
        st = stats.get(pid)
        return PlannedPhase(
            phase_id=pid,
            order=order,
            role=role,
            reason=reason,
            unlocked=self.p.unlocked(pid),
            percent=st.percent if st else 0,
        )

    def _core_reason(self, pid: str, experience: str) -> str:
        phase = self.c.phase(pid)
        if phase is None:
            return ""
        if pid == "p00":
            return "Nothing else is safe to start until version control works."
        if pid == "p01" and experience in ("other", "working"):
            return ("You already program, so treat this as a fast audit: do the "
                    "gate first and only study what you miss.")
        if not phase.prereq:
            return "Foundation for everything that follows."
        names = [self.c.phase(r).name for r in phase.prereq
                 if self.c.phase(r) is not None]
        return "Builds directly on %s." % ", ".join(names)

    # -- weak spots ---------------------------------------------------------

    def weak_areas(self, limit: int = 5) -> list:
        """Phases where measured performance is worst, worst first."""
        rows = []
        for phase in self.c.phases:
            if phase.no_progress:
                continue
            st = self.p.phase(phase)
            signals = []
            if st.exercises_total:
                signals.append(st.exercises_done / st.exercises_total)
            quizzes = self.c.quizzes_for(phase.id)
            if quizzes:
                signals.append(st.quiz_best)
            if not signals or not st.is_started:
                continue
            score = sum(signals) / len(signals)
            if score < 0.75:
                rows.append((score, phase.id))
        rows.sort()
        return [pid for _score, pid in rows[:limit]]

    def suggested_track(self, goals: set) -> str:
        """Best-fitting preset for a set of onboarding goals."""
        if not goals:
            return "generalist"
        best, best_score = "generalist", -1
        wanted: set = set()
        for gid, _label, gtags in GOALS:
            if gid in goals:
                wanted.update(gtags)
        for track in self.c.tracks:
            score = len(wanted.intersection(track.tags))
            if score > best_score:
                best, best_score = track.id, score
        return best
