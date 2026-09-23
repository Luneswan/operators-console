"""The failure explainer tells the truth about `is`, shared lines and errors.

Three things it used to get wrong or leave out:

* `assert is_leap(1900) is False` failing because the function said True was
  explained as an object-identity problem. Thirty-eight checks in the bank
  have that shape, and the real bug in every one is the wrong answer.
* With two asserts on one line, the first was explained even when the second
  was the one that failed.
* OverflowError, StopIteration and ValueError came with no line saying what
  usually causes them.
"""
from __future__ import annotations

from operators_console.core.models import TestCase as Case
from operators_console.core.runner import (
    explain_assertion, explain_error, run_exercise,
)


def _sentence(text: str) -> str:
    return text.splitlines()[0] if text else ""


def _explain(check: str, namespace: dict) -> str:
    try:
        exec(compile(check, "<check>", "exec"), dict(namespace))
    except AssertionError as exc:
        return explain_assertion(check, exc)
    raise AssertionError("the check passed, so there was nothing to explain")


def _error(fn) -> str:
    try:
        fn()
    except BaseException as exc:
        return explain_error(exc)
    raise AssertionError("that did not raise")


# ---------------------------------------------------------------------------
# `is` and `is not`
# ---------------------------------------------------------------------------

def test_the_wrong_boolean_is_a_wrong_answer_not_an_identity_problem():
    said = _explain("assert f() is False", {"f": lambda: True})
    assert _sentence(said) == "The check expects False. Your code returned True."
    assert "separate objects" not in said
    assert "expected False, got True" in said


def test_the_other_way_round_too():
    said = _explain("assert f() is True", {"f": lambda: False})
    assert _sentence(said) == "The check expects True. Your code returned False."


def test_one_instead_of_true_names_the_kind_of_value():
    said = _explain("assert f() is True", {"f": lambda: 1})
    assert _sentence(said).startswith("True/False and 1/0 are different")


def test_a_wrong_value_against_a_class_says_how_they_differ():
    said = _explain("assert f() is expected", {"f": lambda: "7",
                                               "expected": 7})
    assert "separate objects" not in said
    assert _sentence(said) == "You returned a string; the check expects a whole number."


def test_equal_but_separate_objects_still_get_the_identity_story():
    said = _explain("assert f() is expected", {"f": lambda: [1, 2],
                                               "expected": [1, 2]})
    assert _sentence(said).startswith("These are two separate objects")


def test_none_keeps_its_own_sentence():
    said = _explain("assert f() is None", {"f": lambda: 3})
    assert _sentence(said) == "Expected None. Your code returned 3."


def test_is_not_none_says_what_came_back():
    said = _explain("assert f() is not None", {"f": lambda: None})
    assert _sentence(said) == ("Expected anything but None. Your code "
                               "returned None.")


def test_is_not_between_objects_keeps_the_identity_story():
    shared = [1]
    said = _explain("assert f() is not shared", {"f": lambda: shared,
                                                 "shared": shared})
    assert _sentence(said).startswith("The check needs two separate objects")


def test_through_the_real_grader_a_wrong_boolean_reads_as_one():
    code = "def is_leap(year):\n    return year % 4 == 0\n"
    result = run_exercise(code, [Case("century", "assert is_leap(1900) is False")],
                          timeout=30)
    case = result.cases[0]
    assert not case.passed
    assert case.message == "The check expects False. Your code returned True."
    assert case.detail == "expected False, got True"


# ---------------------------------------------------------------------------
# two asserts on one line
# ---------------------------------------------------------------------------

def test_the_second_assert_on_a_line_is_explained_when_it_fails():
    said = _explain("assert a == 1; assert b == 2", {"a": 1, "b": 9})
    assert "expected 2, got 9" in said


def test_the_first_assert_on_a_line_is_explained_when_it_fails():
    said = _explain("assert a == 1; assert b == 2", {"a": 5, "b": 9})
    assert "expected 1, got 5" in said
    assert "got 9" not in said


def test_an_assert_that_spans_lines_then_shares_its_last_line():
    check = "assert (a ==\n        1); assert b == 2\n"
    said = _explain(check, {"a": 1, "b": 9})
    assert "expected 2, got 9" in said
    said = _explain(check, {"a": 4, "b": 2})
    assert "expected 1, got 4" in said


def test_three_on_a_line_picks_the_one_in_the_middle():
    check = "assert a == 1; assert b == 2; assert c == 3"
    said = _explain(check, {"a": 1, "b": 7, "c": 8})
    assert "expected 2, got 7" in said


def test_asserts_inside_a_loop_on_one_line_still_read_the_right_values():
    check = "for n in [1, 2, 3]:\n    assert n < 3; assert n > 0\n"
    said = _explain(check, {})
    assert _sentence(said) == "3 is not less than 3."


# ---------------------------------------------------------------------------
# errors that now say what usually causes them
# ---------------------------------------------------------------------------

def test_overflow_suggests_subtracting_the_largest_value():
    import math
    said = _error(lambda: math.exp(1000))
    assert _sentence(said).startswith("OverflowError:")
    assert "too large for a float" in said
    assert "subtract the largest value first" in said


def test_stop_iteration_says_the_iterator_ran_dry():
    said = _error(lambda: next(iter([])))
    assert _sentence(said).startswith("StopIteration")
    assert "iterator empty" in said
    assert "default" in said


def test_int_of_text_says_the_text_is_not_a_number():
    said = _error(lambda: int("twelve"))
    assert _sentence(said).startswith("ValueError: invalid literal for int()")
    assert "not a whole number" in said


def test_float_of_text_says_the_text_is_not_a_number():
    said = _error(lambda: float("1,5"))
    assert "float() got text that is not a number" in said


def test_unpacking_the_wrong_count_says_so():
    def unpack():
        first, second = [1, 2, 3]
        return first, second
    said = _error(unpack)
    assert "number of names left of `=`" in said


def test_a_maths_domain_error_names_the_usual_cause():
    import math
    said = _error(lambda: math.sqrt(-1))
    assert "square root of a negative number" in said


def test_index_of_a_missing_value_suggests_in():
    said = _error(lambda: [1, 2].index(5))
    assert "Check with `in` first" in said


def test_any_other_value_error_still_gets_a_line():
    def bad():
        raise ValueError("size must be positive")
    said = _error(bad)
    assert _sentence(said) == "ValueError: size must be positive"
    assert len(said.splitlines()) == 2


def test_an_exception_with_no_known_cause_is_just_its_line():
    def bad():
        raise LookupError("nothing here")
    said = _error(bad)
    assert said == "LookupError: nothing here"


def test_the_overflow_hint_reaches_the_learner_through_the_grader():
    code = ("import math\n"
            "def softmax(scores):\n"
            "    exps = [math.exp(s) for s in scores]\n"
            "    return [e / sum(exps) for e in exps]\n")
    result = run_exercise(code, [Case("huge", "softmax([1000, 1001])")],
                          timeout=30)
    case = result.cases[0]
    assert case.message.startswith("OverflowError:")
    assert "subtract the largest value first" in case.detail
