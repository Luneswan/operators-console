"""A failing check has to say why it failed.

Before this, every failing exercise showed the same five words - "Wrong
result." - because a bare `assert` raises AssertionError with an empty
message and the grader had nothing else to print. A learner staring at five
identical FAIL lines learns nothing from them.

`describe_difference` is the part that has to be right for every shape of
value, so it is tested branch by branch here, and `explain_assertion` and
`explain_error` are tested on the assert shapes and the mistakes the
curriculum actually produces. The last few tests run real code through the
real child process, because the values only exist over there.
"""
from __future__ import annotations

from operators_console.core.models import TestCase as Case
from operators_console.core.runner import (
    describe_difference, explain_assertion, explain_error, run_exercise,
)


def _sentence(text: str) -> str:
    """The first line: what the results list shows beside the check name."""
    return text.splitlines()[0] if text else ""


def _fails(code: str, check: str):
    """Grade a wrong answer for real and hand back the one failed case."""
    result = run_exercise(code, [Case("the check", check)], timeout=30)
    assert result.cases, result.error
    return result.cases[0]


# ---------------------------------------------------------------------------
# describe_difference, one branch at a time
# ---------------------------------------------------------------------------

def test_none_is_called_out_as_a_missing_return():
    said = describe_difference(6, None)
    assert said == "Your function returned None. Is a `return` missing?"


def test_expecting_none_says_so_the_other_way_round():
    said = describe_difference(None, 6)
    assert "expects None" in said and "6" in said


def test_a_different_type_names_both_kinds():
    said = describe_difference([1, 2], (1, 2))
    assert said == "You returned a tuple; the check expects a list."


def test_a_different_type_uses_plain_words_for_str_and_int():
    assert "a string" in describe_difference(5, "5")
    assert "a whole number" in describe_difference("5", 5)


def test_a_wrong_length_counts_both_sides():
    said = describe_difference([1, 2, 3], [1, 2])
    assert said == "Your list has 2 items, 3 were expected."


def test_one_item_is_not_pluralised():
    said = describe_difference([1, 2], [9])
    assert said == "Your list has 1 item, 2 were expected."


def test_the_same_values_in_another_order_say_exactly_that():
    said = describe_difference([1, 2, 3], [3, 2, 1])
    assert said == "Right values, wrong order."


def test_out_of_order_is_found_even_when_the_items_are_unhashable():
    said = describe_difference([[1], [2]], [[2], [1]])
    assert said == "Right values, wrong order."


def test_one_wrong_item_names_the_index_and_both_values():
    said = describe_difference([1, 4, 3], [1, 9, 3])
    assert said == "First difference at index 1: expected 4, got 9."


def test_a_wrong_item_inside_a_list_of_lists_explains_the_inner_one_too():
    said = describe_difference([[1, 2], [3]], [[1, 2], [3, 4]])
    assert said.startswith("First difference at index 1:")
    assert "2 items, 1 was expected" in said     # the nested reason too


def test_a_missing_dictionary_key_is_named():
    said = describe_difference({"a": 1, "b": 2}, {"a": 1})
    assert said == "Your dictionary has no key 'b' in it."


def test_several_missing_keys_are_pluralised_and_listed():
    said = describe_difference({"a": 1, "b": 2, "c": 3}, {"a": 1})
    assert said.startswith("Your dictionary has no keys ")
    assert "'b' and 'c'" in said


def test_an_extra_dictionary_key_is_named():
    said = describe_difference({"a": 1}, {"a": 1, "b": 2})
    assert "'b'" in said and "does not expect" in said


def test_a_wrong_dictionary_value_names_the_key():
    said = describe_difference({"a": 1}, {"a": 2})
    assert said == "The value under 'a' is wrong: expected 1, got 2."


def test_a_set_reports_what_is_missing_and_what_does_not_belong():
    said = describe_difference({1, 2, 3}, {1, 2, 9})
    assert said == ("Your set is missing 3 and has 9 that should not be "
                    "there.")


def test_a_set_that_is_only_short_says_only_that():
    said = describe_difference({1, 2, 3}, {1, 2})
    assert said == "Your set is missing 3."


def test_a_set_with_only_extras_says_only_that():
    said = describe_difference({1, 2}, {1, 2, 9})
    assert said == "Your set has 9 in it that should not be there."


def test_a_wrong_character_is_pointed_at_with_a_caret():
    said = describe_difference("hello", "hellp")
    assert _sentence(said) == ("First difference at character 5: expected 'o', "
                               "got 'p'.")
    lines = said.splitlines()
    assert lines[1].strip().startswith("expected")
    assert lines[2].strip().startswith("got")
    # The caret sits under the character that differs, which only works
    # because the results panel prints the detail in a fixed-width font.
    assert lines[3].index("^") == lines[1].index("hello") + 4


def test_a_caret_is_left_out_when_a_line_break_would_break_it():
    said = describe_difference("one\ntwo", "one\nfour")
    assert "^" not in said
    assert said.startswith("First difference at character")


def test_only_the_capitals_being_wrong_is_said_in_so_many_words():
    said = describe_difference("Hello", "hello")
    assert said.startswith("Right letters, wrong capitals")


def test_only_the_spacing_being_wrong_is_said_in_so_many_words():
    said = describe_difference("a b", "ab")
    assert said.startswith("Right characters, wrong spacing")


def test_text_that_stops_early_says_what_is_missing():
    said = describe_difference("hello", "hell")
    assert said == "Your text is missing 'o' at the end."


def test_text_that_runs_on_says_what_is_extra():
    said = describe_difference("hell", "hello")
    assert said == "Your text has extra 'o' at the end."


def test_a_float_that_is_nearly_right_blames_floating_point():
    said = describe_difference(3, 3.0000000001)
    assert said == ("3.0000000001 is not exactly 3 because of floating-point "
                    "rounding. Compare with round() or math.isclose().")


def test_numbers_that_are_plainly_different_are_not_blamed_on_floats():
    said = describe_difference(10, 12)
    assert "floating point" not in said
    assert "10" in said and "12" in said


def test_true_is_not_the_same_as_one():
    said = describe_difference(1, True)
    assert said.startswith("True/False and 1/0 are different values")


def test_false_where_a_zero_was_wanted_is_caught_the_same_way():
    assert describe_difference(0, False).startswith("True/False")


def test_two_booleans_name_both_of_them():
    said = describe_difference(True, False)
    assert said == "The check expects True. Your code returned False."


def test_nothing_useful_to_say_is_an_empty_string_rather_than_a_guess():
    assert describe_difference(object(), object()) == ""


def test_a_value_whose_repr_explodes_does_not_take_the_run_with_it():
    class Awkward:
        def __repr__(self):
            raise RuntimeError("no")

    said = describe_difference([1], [Awkward()])
    assert isinstance(said, str)          # it said something, and survived


def test_a_huge_value_is_not_printed_whole():
    said = describe_difference(list(range(10000)), [])
    assert len(said) < 400


# ---------------------------------------------------------------------------
# explain_assertion: the shapes an authored check actually takes
# ---------------------------------------------------------------------------

def _explain(check: str, namespace: dict) -> str:
    """Run a check the way the grader does and explain the failure."""
    try:
        exec(compile(check, "<check>", "exec"), dict(namespace))
    except AssertionError as exc:
        return explain_assertion(check, exc)
    raise AssertionError("the check passed, so there was nothing to explain")


def test_a_bare_equality_check_names_the_reason_and_both_values():
    said = _explain("assert total == 6", {"total": 5})
    assert _sentence(said) == ("Wrong number. The check expects 6. Your code "
                               "returned 5.")
    assert "expected 6, got 5" in said


def test_the_values_come_from_the_line_that_actually_failed():
    check = "assert first == 1\nassert second == 2\n"
    said = _explain(check, {"first": 1, "second": 9})
    assert "expected 2, got 9" in said


def test_a_check_spread_over_several_lines_is_still_read():
    check = "assert (\n    total\n    == 6\n)\n"
    said = _explain(check, {"total": 5})
    assert "expected 6, got 5" in said


def test_an_author_s_own_message_is_kept_and_the_values_added_under_it():
    said = _explain("assert total == 6, 'count the evens'", {"total": 5})
    assert _sentence(said) == "count the evens"
    assert "expected 6, got 5" in said


def test_a_check_with_no_comparison_quotes_itself():
    said = _explain("assert is_prime(9)", {"is_prime": lambda n: False})
    assert _sentence(said) == "The check `assert is_prime(9)` was false."


def test_a_bare_name_check_also_says_what_the_name_held():
    said = _explain("assert result", {"result": []})
    assert _sentence(said) == "The check `assert result` was false."
    assert "its value was []" in said


def test_a_membership_check_says_what_was_not_in_what():
    said = _explain("assert 4 in numbers", {"numbers": [1, 3, 5]})
    assert _sentence(said) == "4 is not in [1, 3, 5]."


def test_a_not_in_check_reads_the_other_way_round():
    said = _explain("assert 3 not in numbers", {"numbers": [1, 3]})
    assert "should not be in" in _sentence(said)


def test_an_isinstance_check_names_the_kind_it_wanted():
    said = _explain("assert isinstance(total, int)", {"total": "5"})
    assert _sentence(said) == "Expected `total` to be `int`. It is a string."


def test_an_ordering_check_says_which_way_round_it_wanted_them():
    said = _explain("assert score > 10", {"score": 3})
    assert _sentence(said) == "3 is not greater than 10."


def test_an_is_none_check_is_not_reported_as_a_missing_return():
    said = _explain("assert value is None", {"value": 7})
    assert "Expected None" in _sentence(said)


def test_a_check_whose_operand_cannot_be_read_again_still_says_something():
    """Re-evaluating must never be the difference between a message and none."""
    check = "assert boom() == 1"

    def boom():
        raise RuntimeError("only works once")

    try:
        exec(compile("assert False", "<check>", "exec"), {})
    except AssertionError as exc:
        said = explain_assertion(check, exc)
    assert said                      # never blank, never an exception
    assert isinstance(said, str)


def test_an_unparseable_check_degrades_to_the_plain_message():
    try:
        raise AssertionError()
    except AssertionError as exc:
        said = explain_assertion("this is not python at all (", exc)
    assert said == "Wrong result."


def test_no_file_path_from_the_application_ever_reaches_the_learner():
    said = _explain("assert total == 6", {"total": 5})
    for leak in ("runner.py", "operators_console", "site-packages", "<check>"):
        assert leak not in said


# ---------------------------------------------------------------------------
# explain_error: everything that is not an assert
# ---------------------------------------------------------------------------

def _error(fn) -> str:
    try:
        fn()
    except BaseException as exc:
        return explain_error(exc)
    raise AssertionError("that did not raise")


def test_the_exception_line_is_still_the_first_thing_said():
    said = _error(lambda: 1 / 0)
    assert _sentence(said) == "ZeroDivisionError: division by zero"


def test_dividing_by_zero_suggests_guarding_the_divisor():
    assert "Division by zero" in _error(lambda: 1 / 0)


def test_a_missing_name_says_nothing_defines_it():
    said = _error(lambda: undefined_thing)          # noqa: F821
    assert "`undefined_thing` is not defined" in said


def test_the_wrong_number_of_arguments_points_at_the_def_line():
    def takes_one(a):
        return a

    said = _error(lambda: takes_one(1, 2))
    assert "Wrong number of arguments" in said


def test_an_index_past_the_end_explains_how_positions_count():
    said = _error(lambda: [1, 2, 3][9])
    assert "indexes 0, 1 and 2" in said


def test_a_missing_key_names_it_and_offers_get():
    said = _error(lambda: {"a": 1}["b"])
    assert "No key 'b'" in said and ".get()" in said


def test_a_dot_on_none_is_read_as_a_missing_return():
    said = _error(lambda: None.upper())
    assert "`.` on None" in said and "`return` missing" in said


def test_a_missing_attribute_on_a_real_object_says_to_check_the_spelling():
    said = _error(lambda: "text".uper())
    assert "has no `uper`" in said


def test_endless_recursion_says_it_needs_a_stopping_case():
    def forever(n):
        return forever(n + 1)

    said = _error(lambda: forever(0))
    assert "Add a base case" in said


def test_adding_a_string_to_a_number_suggests_converting_one():
    said = _error(lambda: "1" + 1)
    assert "Convert one first" in said


def test_calling_something_that_is_not_a_function_says_so():
    total = 5
    said = _error(lambda: total())
    assert "not a function" in said


def test_an_error_with_no_hint_is_just_the_exception_line():
    said = _error(lambda: (_ for _ in ()).throw(LookupError("x")))
    assert said.startswith("LookupError:")
    assert "\n" not in said


# ---------------------------------------------------------------------------
# through the real grader, in the child process
# ---------------------------------------------------------------------------

def test_a_wrong_answer_run_for_real_names_the_index_and_the_values():
    case = _fails(
        "def evens(n):\n    return [i for i in range(n) if i % 2]\n",
        "assert evens(6) == [0, 2, 4]")
    assert not case.passed
    assert case.message == "First difference at index 0: expected 0, got 1."
    assert case.detail == "expected [0, 2, 4], got [1, 3, 5]"


def test_the_five_identical_wrong_result_lines_are_gone():
    """The defect this whole module exists for."""
    result = run_exercise(
        "def double(n):\n    return n\n",
        [Case("two", "assert double(2) == 4"),
         Case("three", "assert double(3) == 6"),
         Case("four", "assert double(4) == 8")],
        timeout=30)
    messages = [c.message for c in result.cases]
    assert "Wrong result." not in messages
    assert len(set(messages)) == len(messages), messages


def test_the_list_line_stays_one_line_and_the_values_go_underneath():
    case = _fails("answer = 'hello'", "assert answer == 'hellp'")
    assert "\n" not in case.message
    assert case.detail


def test_a_run_that_prints_while_being_explained_keeps_the_output():
    """Working out why costs a second call; anything it prints is captured."""
    result = run_exercise(
        "def noisy(n):\n    print('called', n)\n    return n\n",
        [Case("check", "assert noisy(1) == 2")], timeout=30)
    assert not result.ok
    assert result.stdout.count("called 1") == 2
    assert result.cases[0].message


def test_a_named_check_keeps_the_author_s_message_first():
    case = _fails("total = 5", "assert total == 6, 'count them again'")
    assert case.message == "count them again"
    assert "expected 6, got 5" in case.detail


def test_an_explosive_repr_inside_the_child_still_produces_a_verdict():
    case = _fails(
        "class Odd:\n"
        "    def __eq__(self, other): return False\n"
        "    def __repr__(self): raise RuntimeError('no')\n"
        "value = Odd()\n",
        "assert value == 1")
    assert not case.passed
    assert case.message


def test_every_reference_solution_still_passes_its_own_checks(curriculum):
    """A message that explains a failure must not invent one.

    The whole bank lives in tests/test_content_solutions.py; three from
    different phases are enough here to catch an explanation path that
    accidentally turned a pass into a failure.
    """
    picked = [curriculum.exercises[0], curriculum.exercises[len(
        curriculum.exercises) // 2], curriculum.exercises[-1]]
    for exercise in picked:
        result = run_exercise(exercise.solution, exercise.tests,
                              exercise.setup, timeout=30)
        assert result.ok, "%s: %s" % (
            exercise.id, [(c.name, c.message) for c in result.cases])
        assert all(c.message == "" and c.detail == "" for c in result.cases)
