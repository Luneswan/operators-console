"""The shape of the exercise bank, not its correctness.

test_content_solutions proves every exercise is solvable and no starter is
free. This file pins that practice reaches the whole course and that the
difficulty climbs a step at a time, so no phase goes silent and no learner
meets a cliff.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from itertools import pairwise

# Phases where a graded function is the wrong tool: p00 is environment and
# Git set-up, p18 is career-level judgement, and p99 is the capstone ladder,
# which is proven by projects.
NOT_CODE_PRACTISED = {"p00", "p18", "p99"}
MIN_PER_PHASE = 3

# The back-half phases filled in one pass. Their exercises are held to the
# full authoring contract.
TAIL_PHASES = {"p06", "p07", "p12", "p15", "p16", "p17"}


def _by_phase(curriculum):
    groups = defaultdict(list)
    for exercise in curriculum.exercises:
        groups[exercise.phase].append(exercise)
    return groups


def test_every_code_phase_has_graded_practice(curriculum):
    groups = _by_phase(curriculum)
    thin = {phase.id: len(groups.get(phase.id, []))
            for phase in curriculum.scored_phases
            if phase.id not in NOT_CODE_PRACTISED
            and len(groups.get(phase.id, [])) < MIN_PER_PHASE}
    assert thin == {}


def test_difficulty_climbs_one_level_at_a_time(curriculum):
    """In the order Practice lists them, the next exercise in a phase is
    never more than one level harder than the one before it."""
    cliffs = []
    for exercises in _by_phase(curriculum).values():
        for before, after in pairwise(exercises):
            if after.difficulty - before.difficulty > 1:
                cliffs.append((before.id, before.difficulty,
                               after.id, after.difficulty))
    assert cliffs == []


def test_p04_opens_with_a_warm_up(curriculum):
    """p04 used to open at level 3 and reach 5 by its fourth exercise."""
    levels = [e.difficulty for e in curriculum.exercises_for("p04")]
    assert levels[0] <= 2
    assert levels[:3] == sorted(levels[:3])


def test_ids_belong_to_their_phase(curriculum):
    phase_ids = {phase.id for phase in curriculum.phases}
    ids = [exercise.id for exercise in curriculum.exercises]
    assert len(ids) == len(set(ids))
    wrong = [e.id for e in curriculum.exercises
             if e.phase not in phase_ids or not e.id.startswith(e.phase + ".")
             or not 1 <= e.difficulty <= 5]
    assert wrong == []


def _public_names(solution: str) -> set[str]:
    tree = ast.parse(solution)
    return {node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            and not node.name.startswith("_")}


def test_prompts_name_what_the_checks_call(curriculum):
    """A check that calls a function the prompt never mentions is a rule
    the learner cannot know about."""
    unnamed = []
    for exercise in curriculum.exercises:
        checks = "\n".join(test.code for test in exercise.tests)
        for name in _public_names(exercise.solution):
            if name in checks and name not in exercise.prompt:
                unnamed.append((exercise.id, name))
    assert unnamed == []


def test_tail_exercises_meet_the_authoring_contract(curriculum):
    """Two hints and four to six uniquely named checks. Whether the starter
    fails is test_content_solutions' job."""
    broken = []
    for exercise in curriculum.exercises:
        if exercise.phase not in TAIL_PHASES:
            continue
        if len(exercise.hints) != 2:
            broken.append((exercise.id, "hints", len(exercise.hints)))
        if not 4 <= len(exercise.tests) <= 6:
            broken.append((exercise.id, "checks", len(exercise.tests)))
        if len({test.name for test in exercise.tests}) != len(exercise.tests):
            broken.append((exercise.id, "duplicate check names"))
    assert broken == []


def test_tail_phases_ramp_within_the_phase(curriculum):
    """Each filled phase starts no harder than it ends."""
    for phase in TAIL_PHASES:
        levels = [e.difficulty for e in curriculum.exercises_for(phase)]
        assert levels, phase
        assert levels == sorted(levels), (phase, levels)
