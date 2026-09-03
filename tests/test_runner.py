"""The grader must be correct, and must never take the app down with it."""
from __future__ import annotations


from operators_console.core.models import TestCase as Case
from operators_console.core.runner import run_exercise

CASES = (Case("adds", "assert add(2, 3) == 5"),
         Case("negatives", "assert add(-1, 1) == 0"))


def test_a_correct_submission_passes():
    result = run_exercise("def add(a, b):\n    return a + b\n", CASES)
    assert result.ok
    assert result.passed_count == 2
    assert result.summary == "2 of 2 checks passed"


def test_a_wrong_submission_reports_which_check_failed():
    result = run_exercise("def add(a, b):\n    return a - b\n", CASES)
    assert not result.ok
    assert result.passed_count == 0
    assert [case.name for case in result.cases if not case.passed] == \
        ["adds", "negatives"]


def test_a_syntax_error_is_reported_without_grader_frames():
    result = run_exercise("def add(a, b)\n    return a + b\n", CASES)
    assert not result.ok
    assert "SyntaxError" in result.error
    assert "runner.py" not in result.error


def test_a_runtime_error_names_the_learner_file():
    result = run_exercise("raise ValueError('boom')\n", CASES)
    assert not result.ok
    assert "boom" in result.error


def test_a_missing_function_fails_rather_than_crashing():
    result = run_exercise("x = 1\n", CASES)
    assert not result.ok
    assert any("NameError" in case.message for case in result.cases)


def test_printed_output_is_captured_and_returned():
    result = run_exercise("print('hello from the exercise')\n"
                          "def add(a, b):\n    return a + b\n", CASES)
    assert result.ok
    assert "hello from the exercise" in result.stdout


def test_an_endless_loop_is_killed():
    result = run_exercise("while True:\n    pass\n", CASES, timeout=3)
    assert result.timed_out
    assert not result.ok
    assert "endless loop" in result.summary


def test_a_process_exit_does_not_break_grading():
    result = run_exercise("import sys\ndef add(a, b):\n    return a + b\n"
                          "sys.exit(3)\n", CASES)
    assert result.ok


def test_setup_code_runs_before_the_submission():
    setup = "SEED = 41\n"
    cases = (Case("uses the seed", "assert bump() == 42"),)
    result = run_exercise("def bump():\n    return SEED + 1\n", cases, setup)
    assert result.ok


def test_a_broken_setup_is_reported_as_such():
    cases = (Case("never runs", "assert True"),)
    result = run_exercise("pass\n", cases, setup="1 / 0\n")
    assert not result.ok
    assert "setup failed" in result.error.lower()


def test_each_check_gets_its_own_names_but_shares_objects():
    """The documented contract, relied on by the database exercises."""
    bindings = (Case("first", "extra = 1\nassert extra == 1"),
                Case("second", "assert 'extra' not in dir()"))
    assert run_exercise("value = []\n", bindings).ok

    shared = (Case("first", "value.append(1)\nassert len(value) == 1"),
              Case("second", "assert len(value) == 1"))
    result = run_exercise("value = []\n", shared)
    assert result.ok, [c.message for c in result.cases]


def test_the_submission_can_be_introspected():
    cases = (Case("has a loop",
                      "import inspect\n"
                      "assert 'for ' in inspect.getsource(count)"),)
    result = run_exercise("def count(items):\n    total = 0\n"
                          "    for _ in items:\n        total += 1\n"
                          "    return total\n", cases)
    assert result.ok, [c.message for c in result.cases]


def test_dataclasses_work_inside_the_grader():
    cases = (Case("equal by value", "assert P(1, 2) == P(1, 2)"),)
    result = run_exercise("from dataclasses import dataclass\n\n"
                          "@dataclass\nclass P:\n    x: int\n    y: int\n",
                          cases)
    assert result.ok, [c.message for c in result.cases]


def test_an_empty_check_list_is_not_a_pass():
    result = run_exercise("x = 1\n", ())
    assert not result.ok


def test_huge_output_is_truncated():
    cases = (Case("ok", "assert True"),)
    result = run_exercise("print('x' * 100000)\n", cases)
    assert len(result.stdout) < 30000
    assert "truncated" in result.stdout
