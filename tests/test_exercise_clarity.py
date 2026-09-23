"""An exercise says what it wants, and a failure says why in plain words.

Owner, 09-23, with a screenshot of `greet(anas)` under the function and
nothing but `NameError: name 'anas' is not defined`: "this should be better
the questions what it wants, and hints should be written better".
"""
from __future__ import annotations

from operators_console.core import exercise_brief as brief
from operators_console.core import runner
from operators_console.core.models import TestCase

GREET = [TestCase("greets Ada", "assert greet('Ada') == 'Hello, Ada!'")]


def _why(code):
    return runner.run_exercise(code, GREET).why


def test_a_bare_word_is_explained_as_missing_quotes_and_an_unneeded_call():
    why = _why("def greet(ANAS):\n    pass\ngreet(anas)\n")
    assert "no quotes" in why and '"anas"' in why
    assert "Line 3" in why
    assert "checks call `greet` for you" in why


def test_a_parameter_used_outside_its_function_is_named_as_such():
    why = _why('def greet(name):\n    return name\nprint(greet(name))\n')
    assert "`name` is a parameter" in why


def test_a_capital_letter_is_called_a_capital_letter():
    why = _why('def greet(name):\n    return "Hi " + Name\ngreet("x")\n')
    assert "`Name` is not defined, but `name` is" in why


def test_a_missing_colon_is_explained():
    why = _why("def greet(name)\n    return 1\n")
    assert "Line 1" in why and "colon" in why


def test_the_explanation_reaches_a_failing_check_too():
    result = runner.run_exercise(
        'def greet(name):\n    return "Hi " + Name\n', GREET)
    assert "but `name` is" in result.cases[0].detail


def test_a_working_file_has_nothing_to_explain():
    result = runner.run_exercise(
        'def greet(name):\n    return f"Hello, {name}!"\n', GREET)
    assert result.ok and result.why == ""


def test_every_exercise_says_how_it_is_checked(curriculum):
    for exercise in curriculum.exercises:
        names = brief.entry_points(exercise)
        assert names, exercise.id
        assert "`%s`" % names[0] in brief.how_checked(exercise)


def test_examples_come_from_real_checks(curriculum):
    exercise = next(e for e in curriculum.exercises if e.id == "p01.001")
    assert ("greet('Ada')", "'Hello, Ada!'") in brief.examples(exercise)
    with_examples = [e for e in curriculum.exercises if brief.examples(e)]
    assert len(with_examples) >= 60


def test_every_exercise_has_a_shape_hint_that_is_not_the_answer(curriculum):
    for exercise in curriculum.exercises:
        shape = brief.skeleton(exercise.solution)
        assert shape, exercise.id
        assert "..." in shape or "pass" in shape, exercise.id
        assert shape.strip() != exercise.solution.strip(), exercise.id
        compile(shape, exercise.id, "exec")      # it is still valid Python


def test_the_practice_page_shows_the_brief(qt_app, window, curriculum):
    from conftest import pump
    window.go("practice", "p01.001")
    pump(qt_app)
    text = window.views["practice"].brief.text()
    assert "For example" in text and "greet(&#x27;Ada&#x27;)" in text
    assert "How it is checked" in text
