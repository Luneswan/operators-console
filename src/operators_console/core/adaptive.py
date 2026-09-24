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

# Onboarding interests map onto the tags carried by each phase. Every Python
# career pathway has a goal here, and every goal matches at least one phase
# that teaches it (tests/test_pathways.py holds that line).
GOALS = (
    ("web", "Websites and APIs", ("backend", "web", "sql")),
    ("data", "Data analysis and engineering", ("data", "analysis", "sql", "engineering")),
    ("ai", "Machine learning and AI", ("ai", "ml")),
    ("vision", "Computer vision", ("vision",)),
    ("nlp", "Language and text (NLP)", ("nlp",)),
    ("automation", "Automation and scraping", ("automation", "scraping")),
    ("bots", "Bots and integrations", ("bots",)),
    ("gui", "Desktop and mobile apps", ("gui", "desktop")),
    ("cli", "Command-line tools", ("cli",)),
    ("games", "Games, graphics and media", ("games", "graphics", "media")),
    ("science", "Science and optimization", ("science", "optimization")),
    ("finance", "Finance and trading", ("finance", "quant")),
    ("devops", "Infrastructure and deployment", ("devops", "linux", "deployment")),
    ("netauto", "Network automation", ("netauto", "networking")),
    ("security", "Security", ("security", "networking")),
    ("testing", "Testing and QA", ("testing", "qa")),
    ("embedded", "Hardware, IoT and robotics", ("embedded", "hardware")),
    ("blockchain", "Blockchain", ("blockchain",)),
    ("interview", "Pass a technical interview", ("interview", "algorithms")),
    ("fundamentals", "How computers work", ("cs", "systems", "internals")),
    ("langtools", "Compilers and language tools", ("internals", "projects")),
)


def _is_specialization(phase) -> bool:
    return phase.num.startswith("S")


def plan_order(curriculum, ids) -> list:
    """`ids` in dependency order: every phase after its in-plan prerequisites.

    Core phases keep the course's teaching order. A specialization is placed
    right after the last phase it builds on, so a learner who picks games
    meets the games phase as soon as they are ready for it, not after every
    other phase in their track.
    """
    wanted = [pid for pid in dict.fromkeys(ids) if curriculum.phase(pid)]
    index = {p.id: i for i, p in enumerate(curriculum.phases)}
    rank: dict = {}

    def rank_of(pid, depth=0):
        if pid in rank:
            return rank[pid]
        phase = curriculum.phase(pid)
        if phase is None or depth > 50:
            return 999.0
        value = float(index.get(pid, 999))
        if _is_specialization(phase) and phase.prereq:
            value = max(rank_of(q, depth + 1) for q in phase.prereq) + 0.5
        rank[pid] = value
        return value

    pending = set(wanted)
    done: list = []
    while pending:
        ready = [pid for pid in pending
                 if not (set(curriculum.phase(pid).prereq) & pending)]
        if not ready:                    # a cycle: fall back to course order
            ready = list(pending)
        ready.sort(key=lambda pid: (rank_of(pid), index.get(pid, 999)))
        nxt = ready[0]
        done.append(nxt)
        pending.discard(nxt)
    return done


def with_prerequisites(curriculum, ids, have) -> list:
    """`ids` plus every prerequisite, recursively, that is not in `have`."""
    out = list(dict.fromkeys(ids))
    queue = list(out)
    while queue:
        phase = curriculum.phase(queue.pop())
        for req in (phase.prereq if phase else ()):
            if req not in have and req not in out:
                out.append(req)
                queue.append(req)
    return out

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
        return self.p.goal_tags()       # one definition, shared with the plan

    def roadmap(self) -> list:
        """The personal plan, in the order to study it.

        The track's core phases and every phase matching a chosen goal come
        first, together, in dependency order: a goal's specialization sits
        right after what it builds on, not behind the whole track. The
        track's remaining optional phases follow, also in dependency order,
        ending with the mastery phases.
        """
        track = self.c.track(self.s.setting("track", "generalist"))
        if track is not None and not any(
                self.c.phase(pid) for pid in (*track.core, *track.optional)):
            track = None               # names nothing that exists: whole course
        core = list(track.core) if track else [p.id for p in self.c.phases
                                               if not p.no_progress]
        optional = list(track.optional) if track else []
        tags = self.goal_tags()
        experience = self.s.setting("experience", "none")
        stats = self.p.all_phases()

        matched = [p.id for p in self.c.phases
                   if not p.no_progress and p.id not in core
                   and tags.intersection(p.tags)]
        # A goal brings what it builds on: vision needs AI engineering even
        # on a track where that phase is optional or absent.
        goal_ids = with_prerequisites(self.c, matched, set(core))
        first = plan_order(self.c, core + goal_ids)
        later = plan_order(self.c, [pid for pid in optional
                                    if pid not in goal_ids])

        rows: list[PlannedPhase] = []
        for pid in first + later:
            if pid in core:
                role = "core"
                reason = self._core_reason(pid, experience)
            elif pid in goal_ids:
                role = "extra"
                hit = self._goal_names(self.c.phase(pid))
                if hit:
                    reason = "Added for your goal%s: %s." % (
                        "s" if len(hit) > 1 else "", ", ".join(hit))
                else:
                    needs = [self.c.phase(g).name for g in goal_ids
                             if pid in self.c.phase(g).prereq]
                    reason = "Needed before %s." % ", ".join(needs)
            else:
                role = "optional"
                reason = ("Recommended for your track, after the core "
                          "phases.")
            rows.append(self._row(pid, len(rows), role, reason, stats))
        return rows

    def _goal_names(self, phase) -> list:
        """The chosen goals whose tags this phase carries, by their labels."""
        picked = set(self.s.setting("goals", []) or [])
        return [label for gid, label, gtags in GOALS
                if gid in picked and set(gtags) & set(phase.tags)]

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
            return "Do this first. Every later phase uses Git."
        if pid == "p01" and experience in ("other", "working"):
            return ("You already program. Try the gate first and study only "
                    "what you miss.")
        if not phase.prereq:
            return "Every later phase depends on this."
        names = [self.c.phase(r).name for r in phase.prereq
                 if self.c.phase(r) is not None]
        return "Builds on %s." % ", ".join(names)

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
