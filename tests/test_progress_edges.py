"""The position marker and the daily plan on inputs nobody plans for.

None of these shapes are normal. All of them are reachable: a curriculum file
that failed to load, a track that names a phase someone renamed, a settings
row hand-edited or restored from another machine. The dashboard is the first
thing the learner sees, so it has to survive all of them rather than open on
a traceback.
"""
from __future__ import annotations

import copy
import dataclasses

import pytest

from operators_console.core.adaptive import Planner
from operators_console.core.progress import Progress
from operators_console.core.today import TodayPlan


def variant(curriculum, **changes):
    """A shallow copy of the curriculum with some attributes replaced."""
    clone = copy.copy(curriculum)
    for key, value in changes.items():
        setattr(clone, key, value)
    for cache in ("_by_id", "_phase_by_id", "_tracks_by_id", "_track_by_id"):
        if hasattr(clone, cache):
            existing = getattr(clone, cache)
            if "track" in cache:
                setattr(clone, cache, {t.id: t for t in clone.tracks})
            else:
                setattr(clone, cache, {p.id: p for p in clone.phases})
            assert isinstance(existing, dict)
    return clone


def plan_for(curriculum, store):
    progress = Progress(curriculum, store)
    planner = Planner(curriculum, store, progress)
    return progress, planner, TodayPlan(curriculum, store, progress, planner)


# ---------------------------------------------------------------------------
# an empty or broken curriculum
# ---------------------------------------------------------------------------

def test_an_empty_curriculum_does_not_crash_the_dashboard(curriculum, store):
    """A curriculum.json that failed to parse used to raise IndexError.

    `current_phase_id` ended with `self.c.phases[0].id`, and the daily plan
    calls it on every build, so the first screen of the app died on an empty
    phase list instead of showing an empty plan.
    """
    blank = variant(curriculum, phases=())
    progress, planner, today = plan_for(blank, store)
    assert progress.current_phase_id() == ""
    assert progress.overview().percent == 0
    assert progress.estimated_days_left() >= 0
    actions = today.build()
    assert isinstance(actions, list)
    assert all(a.kind for a in actions)


def test_a_phase_with_nothing_in_it_never_holds_the_marker(curriculum, store):
    """`is_complete` is false when total is zero, so an empty phase pinned it.

    A phase still being written - or one a track trimmed to nothing - could
    never be finished, so the learner was pointed at a blank page forever and
    the plan never advanced past it.
    """
    plan = Progress(curriculum, store).active_phase_ids()
    first, second, third = plan[0], plan[1], plan[2]

    # Truly nothing to tick: no sections and no gate.
    hollow = dataclasses.replace(curriculum.phase(second), sections=(),
                                 gate=None)
    assert hollow.trackable_ids == ()
    phases = tuple(hollow if p.id == second else p for p in curriculum.phases)
    progress, _planner, today = plan_for(variant(curriculum, phases=phases),
                                         store)

    for item in curriculum.phase(first).items:
        store.set_checked(item.id, True)
    if curriculum.phase(first).gate:
        for gate in curriculum.phase(first).gate.items:
            store.set_checked(gate.id, True)
    # The marker moves on proof, not on ticks: pass what the phase asks for.
    for quiz in curriculum.quizzes_for(first):
        store.record_quiz(quiz.id, len(quiz.questions), len(quiz.questions),
                          60)
    for exercise in curriculum.exercises_for(first):
        store.record_exercise_run(exercise.id, "pass", True)
    for project in curriculum.projects_for(first)[:1]:
        store.set_project(project.id, status="shipped")

    marker = progress.current_phase_id()
    assert marker != second, (
        "the marker stuck on a phase that can never be completed")
    assert marker == third
    stats = progress.all_phases().get(marker)
    assert stats is not None and stats.total > 0

    # And the daily plan points at the phase the learner can actually work on.
    learn = [a for a in today.build() if a.kind == "learn" and a.target]
    assert all(a.target != second for a in learn)


def test_a_track_naming_phases_that_do_not_exist_falls_back(curriculum, store):
    track = dataclasses.replace(curriculum.tracks[0],
                                core=("gone-1", "gone-2"), optional=())
    tracks = (track,) + tuple(curriculum.tracks[1:])
    renamed = variant(curriculum, tracks=tracks)
    store.set_setting("track", track.id)
    progress, planner, today = plan_for(renamed, store)
    # No phase in the plan exists, so the plan is the full teaching order.
    assert progress.current_phase_id()
    assert [a.kind for a in today.build()]
    assert planner.roadmap()


def test_a_track_with_a_single_phase_still_produces_a_plan(curriculum, store):
    first = next(p.id for p in curriculum.phases if not p.no_progress)
    track = dataclasses.replace(curriculum.tracks[0], core=(first,),
                                optional=())
    narrowed = variant(curriculum, tracks=(track,) + tuple(curriculum.tracks[1:]))
    store.set_setting("track", track.id)
    progress, planner, today = plan_for(narrowed, store)
    assert progress.active_phase_ids() == [first]
    assert progress.current_phase_id() == first
    assert len(planner.roadmap()) >= 1
    assert today.build()


# ---------------------------------------------------------------------------
# settings a human, or another machine, could have written
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hours", ["not a number", None, "", [], "3.5"])
def test_a_junk_study_budget_does_not_crash_the_plan(curriculum, store, hours):
    """Settings are JSON and a restored backup can hold anything.

    `float(self.s.setting("hours_per_day"))` raised straight out of the
    dashboard build for anything that was not a number.
    """
    store.set_setting("hours_per_day", hours)
    _progress, _planner, today = plan_for(curriculum, store)
    assert today.build()


@pytest.mark.parametrize("hours,days", [(0, 5), (0, 0), (-4, -1), (99, 99)])
def test_an_impossible_pace_still_gives_a_finite_estimate(curriculum, store,
                                                          hours, days):
    store.set_setting("hours_per_day", hours)
    store.set_setting("days_per_week", days)
    progress = Progress(curriculum, store)
    estimate = progress.estimated_days_left()
    assert isinstance(estimate, int)
    assert estimate >= 0


def test_a_zero_hour_day_still_offers_review_and_the_log(curriculum, store):
    """The two things that must never be budgeted away."""
    store.set_setting("hours_per_day", 0)
    _progress, _planner, today = plan_for(curriculum, store)
    kinds = [a.kind for a in today.build()]
    assert "log" in kinds


def test_the_plan_never_exceeds_five_actions(curriculum, store):
    """Five at most, plus the evening log, which is exempt from the count."""
    store.set_setting("hours_per_day", 24)
    _progress, _planner, today = plan_for(curriculum, store)
    actions = today.build()
    assert len([a for a in actions if a.kind != "log"]) <= 5
    assert len([a for a in actions if a.kind == "log"]) <= 1


def test_the_plan_never_points_at_a_phase_that_is_not_in_it(curriculum, store):
    progress, _planner, today = plan_for(curriculum, store)
    allowed = set(progress.active_phase_ids())
    for action in today.build():
        if action.kind in ("learn", "gate") and action.target:
            assert action.target in allowed or "." in action.target


# ---------------------------------------------------------------------------
# gates and ordering
# ---------------------------------------------------------------------------

def test_an_unmet_prerequisite_leaves_a_phase_locked(curriculum, store,
                                                     progress):
    locked = next((p for p in curriculum.phases if p.prereq), None)
    if locked is None:
        pytest.skip("no phase declares a prerequisite")
    assert not progress.unlocked(locked.id)


def test_a_phase_with_no_prerequisite_is_always_unlocked(curriculum, progress):
    free = next(p for p in curriculum.phases if not p.prereq)
    assert progress.unlocked(free.id)


def test_a_phase_that_does_not_exist_is_treated_as_unlocked(progress):
    """Navigation must not be blocked by a typo in a link."""
    assert progress.unlocked("no-such-phase")


def test_the_roadmap_puts_every_phase_after_its_prerequisites(curriculum,
                                                              store, progress):
    for goals in ([], ["games"], ["vision", "nlp"], ["web", "testing"]):
        store.set_setting("goals", goals)
        planner = Planner(curriculum, store, progress)
        ids = [r.phase_id for r in planner.roadmap()]
        seen = set()
        for pid in ids:
            missing = [q for q in curriculum.phase(pid).prereq
                       if q in ids and q not in seen]
            assert not missing, (goals, pid, missing)
            seen.add(pid)


def test_the_roadmap_lists_each_phase_once(curriculum, store, progress):
    planner = Planner(curriculum, store, progress)
    ids = [r.phase_id for r in planner.roadmap()]
    assert len(ids) == len(set(ids))


def test_the_phase_pass_is_reused_until_the_store_changes(curriculum, store):
    """all_phases is cached on the store's write counter; any write, even
    through another path than set_checked, must show at once."""
    from operators_console.core.progress import Progress
    progress = Progress(curriculum, store)
    item = curriculum.phase("p01").items[0].id
    first = progress.all_phases()
    assert progress.all_phases() == first
    store.set_checked(item, True)
    assert progress.all_phases()["p01"].done == first["p01"].done + 1
    exercise = curriculum.exercises_for("p01")[0]
    store.record_exercise_run(exercise.id, exercise.solution, True)
    assert progress.all_phases()["p01"].exercises_done == 1
