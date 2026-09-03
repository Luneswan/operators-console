"""Every shipped solution must pass its own checks, and no starter may.

This is the test that stops a broken exercise reaching a learner, where it
would read as their mistake rather than ours. It is slow, so it is marked and
can be deselected during quick runs with -m "not slow".
"""
from __future__ import annotations

import pytest

from operators_console.core.runner import run_exercise


def _ids(curriculum):
    return [exercise.id for exercise in curriculum.exercises]


@pytest.mark.slow
def test_every_solution_passes(curriculum):
    broken = []
    for exercise in curriculum.exercises:
        result = run_exercise(exercise.solution, exercise.tests,
                              exercise.setup, timeout=30)
        if not result.ok:
            failed = [c.name for c in result.cases if not c.passed]
            broken.append((exercise.id, result.summary, failed,
                           result.error[:200]))
    assert not broken, broken


@pytest.mark.slow
def test_no_starter_passes_without_work(curriculum):
    """A starter that already passes teaches nothing."""
    free = []
    for exercise in curriculum.exercises:
        result = run_exercise(exercise.starter, exercise.tests,
                              exercise.setup, timeout=30)
        if result.ok:
            free.append(exercise.id)
    assert not free, free
