"""The exercise bank keeps its promises to the learner.

Each rule here was broken once. A check that enforced something the prompt
never said failed correct answers; a check with `or True` on the end could
not fail at all; a source grep for `sorted(` rejected a helper called
merge_sorted; a tolerance check or an `A and B` assert gave the learner no
values to look at; an exception check never said what came back instead.

The first half reads the bank and is fast. The second half grades real
answers - correct ones written differently from the official solution, and
cheats that used to pass - through the real grader, so it is marked slow.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

import pytest

from operators_console.core.models import TestCase as Case
from operators_console.core.runner import run_exercise

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "src" / "operators_console" / "data" / "exercises.json"


def _bank() -> list:
    return json.loads(BANK.read_text(encoding="utf-8"))["exercises"]


def _exercise(eid: str) -> dict:
    for entry in _bank():
        if entry["id"] == eid:
            return entry
    raise LookupError(eid)


def _checks():
    for entry in _bank():
        for test in entry["tests"]:
            yield entry["id"], test["name"], test["code"]


def _grade(eid: str, code: str):
    entry = _exercise(eid)
    tests = tuple(Case(t["name"], t["code"]) for t in entry["tests"])
    return run_exercise(code, tests, entry.get("setup", ""), timeout=30)


def _failed(result) -> dict:
    return {case.name: case.message for case in result.cases
            if not case.passed}


# ---------------------------------------------------------------------------
# the shape of the bank
# ---------------------------------------------------------------------------

def test_every_exercise_has_at_least_two_hints():
    thin = [(e["id"], len(e["hints"])) for e in _bank() if len(e["hints"]) < 2]
    assert not thin, thin


def test_no_hint_is_empty_or_repeated():
    for entry in _bank():
        hints = [hint.strip() for hint in entry["hints"]]
        assert all(hints), entry["id"]
        assert len(set(hints)) == len(hints), entry["id"]


def test_no_check_is_written_so_it_cannot_fail():
    vacuous = [(eid, name) for eid, name, code in _checks()
               if "or True" in code or "assert True" in code]
    assert not vacuous, vacuous


def test_tolerance_checks_use_round_so_the_float_explanation_runs():
    """`abs(a - b) < 1e-9` explains nothing; `round(a, 9) == b` does."""
    old_shape = [(eid, name) for eid, name, code in _checks()
                 if "< 1e-" in code]
    assert not old_shape, old_shape


def _asserts(code: str):
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Assert):
            yield node


def test_no_assert_joins_two_facts_with_and():
    joined = [(eid, name) for eid, name, code in _checks()
              for node in _asserts(code)
              if isinstance(node.test, ast.BoolOp) and node.msg is None]
    assert not joined, joined


def test_no_assert_chains_comparisons():
    """`a < b < c` falls through the explainer; two compares do not."""
    chained = [(eid, name) for eid, name, code in _checks()
               for node in _asserts(code)
               if isinstance(node.test, ast.Compare)
               and len(node.test.ops) > 1]
    assert not chained, chained


def test_rules_about_source_are_read_off_the_syntax_tree():
    """A substring grep mistakes merge_sorted for sorted and docstrings for code."""
    grepped = [(eid, name) for eid, name, code in _checks()
               if "getsource" in code and "ast.parse" not in code]
    assert not grepped, grepped


def test_exception_checks_say_what_happened_instead():
    for eid, name, code in _checks():
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Try) and node.orelse):
                continue
            for stmt in node.orelse:
                if isinstance(stmt, ast.Raise):
                    text = ast.unparse(stmt)
                    assert "but it" in text, (eid, name, text)


def test_the_raises_builder_reports_the_returned_value(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "build_tools"))
    builders = importlib.import_module("ex_p01a")

    def said(check: str, namespace: dict) -> str:
        try:
            exec(check, dict(namespace))
        except AssertionError as exc:
            return str(exc)
        raise AssertionError("the check passed code that never raises")

    check = builders.raises("grade(101)")
    assert said(check, {"grade": lambda score: "F"}) == (
        "grade(101) should raise ValueError, but it returned 'F'")

    class Box:
        value = 0
    check = builders.raises("box.value = -1")
    assert said(check, {"box": Box()}) == (
        "`box.value = -1` should raise ValueError, but it went through")


# ---------------------------------------------------------------------------
# graded for real: fair to right answers, closed to cheats
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_counting_lines_with_read_text_is_accepted():
    """p01.029 once demanded a `with` block the prompt never asked for."""
    code = ("from pathlib import Path\n"
            "def count_lines(path):\n"
            "    text = Path(path).read_text(encoding='utf-8')\n"
            "    return sum(1 for line in text.splitlines() if line.strip())\n")
    assert _grade("p01.029", code).ok


@pytest.mark.slow
def test_counting_lines_with_a_remembered_answer_is_not():
    code = ("def count_lines(path):\n"
            "    with open(path, encoding='utf-8'):\n"
            "        return 3\n")
    assert not _grade("p01.029", code).ok


@pytest.mark.slow
def test_counting_lines_and_leaving_the_file_open_is_caught():
    code = ("def count_lines(path):\n"
            "    handle = open(path, encoding='utf-8')\n"
            "    return sum(1 for line in handle if line.strip())\n")
    failed = _failed(_grade("p01.029", code))
    assert list(failed) == ["closes the file"]
    assert "left the file open" in failed["closes the file"]


@pytest.mark.slow
def test_a_merge_sort_with_a_helper_called_merge_sorted_is_accepted():
    code = ("def merge_sorted(left, right):\n"
            "    out, i, j = [], 0, 0\n"
            "    while i < len(left) and j < len(right):\n"
            "        if right[j] < left[i]:\n"
            "            out.append(right[j]); j += 1\n"
            "        else:\n"
            "            out.append(left[i]); i += 1\n"
            "    return out + left[i:] + right[j:]\n"
            "def merge_sort(items):\n"
            "    if len(items) <= 1:\n"
            "        return list(items)\n"
            "    middle = len(items) // 2\n"
            "    return merge_sorted(merge_sort(items[:middle]),\n"
            "                        merge_sort(items[middle:]))\n")
    assert _grade("p05.004", code).ok


@pytest.mark.slow
def test_a_merge_sort_that_calls_sorted_is_named_as_such():
    code = "def merge_sort(items):\n    return sorted(items)\n"
    failed = _failed(_grade("p05.004", code))
    assert list(failed) == ["does not use sorted"]
    assert "found: sorted" in failed["does not use sorted"]


@pytest.mark.slow
def test_named_placeholders_are_parameterised_too():
    """p08.001 once rejected `:year`, which is as safe as `?`."""
    code = ("def books_after(conn, year):\n"
            "    rows = conn.execute('SELECT title FROM books WHERE year > :year'\n"
            "                        ' ORDER BY title', {'year': year})\n"
            "    return [row[0] for row in rows]\n")
    assert _grade("p08.001", code).ok


@pytest.mark.slow
def test_an_injectable_query_is_caught_by_what_it_does():
    code = ("def books_after(conn, year):\n"
            "    rows = conn.execute('SELECT title FROM books WHERE year > '\n"
            "                        + str(year) + ' ORDER BY title')\n"
            "    return [row[0] for row in rows]\n")
    failed = _failed(_grade("p08.001", code))
    assert "cannot be injected" in failed
    assert "parameterised" in failed


@pytest.mark.slow
def test_a_literal_answer_with_a_token_query_no_longer_passes():
    """p08.003: a stub returning the dict and running SELECT 1 used to pass."""
    code = ("def book_counts(conn):\n"
            "    conn.execute('SELECT 1')\n"
            "    return {'Le Guin': 2, 'Butler': 2, 'Lem': 1}\n")
    failed = _failed(_grade("p08.003", code))
    assert "an author with no books counts as zero" in failed


@pytest.mark.slow
def test_counting_in_two_queries_is_told_it_sent_two():
    code = ("def book_counts(conn):\n"
            "    names = [r[0] for r in conn.execute('SELECT name FROM authors')]\n"
            "    out = {}\n"
            "    for row in conn.execute('SELECT a.name, COUNT(b.id) FROM authors a'\n"
            "            ' LEFT JOIN books b ON b.author_id = a.id GROUP BY a.id'):\n"
            "        out[row[0]] = row[1]\n"
            "    return {name: out.get(name, 0) for name in names}\n")
    failed = _failed(_grade("p08.003", code))
    assert list(failed) == ["one query"]
    assert "sent 2 queries" in failed["one query"]


@pytest.mark.slow
def test_gluing_a_path_with_slashes_is_caught():
    """p03.001's rule ended in `or True`, so it could never fail."""
    code = ("from pathlib import Path\n"
            "def log_path(root, name):\n"
            "    folder = Path(str(root) + '/logs')\n"
            "    folder.mkdir(parents=True, exist_ok=True)\n"
            "    return Path(str(folder) + '/' + name + '.log')\n")
    failed = _failed(_grade("p03.001", code))
    assert list(failed) == ["no manual separators"]


@pytest.mark.slow
def test_a_docstring_that_mentions_a_slash_is_not_code():
    code = ('from pathlib import Path\n'
            'def log_path(root, name):\n'
            '    """Return root/logs/name.log, creating the folder."""\n'
            '    folder = Path(root) / "logs"\n'
            '    folder.mkdir(parents=True, exist_ok=True)\n'
            '    return folder / f"{name}.log"\n')
    assert _grade("p03.001", code).ok


@pytest.mark.slow
def test_guarding_only_the_first_vector_is_caught():
    code = ("import math\n"
            "def cosine(a, b):\n"
            "    if len(a) != len(b):\n"
            "        raise ValueError('length')\n"
            "    mag_a = math.sqrt(sum(x * x for x in a))\n"
            "    if mag_a == 0:\n"
            "        return 0.0\n"
            "    mag_b = math.sqrt(sum(y * y for y in b))\n"
            "    return sum(x * y for x, y in zip(a, b)) / (mag_a * mag_b)\n")
    failed = _failed(_grade("p14.001", code))
    assert list(failed) == ["second vector all zeros"]
    assert "ZeroDivisionError" in failed["second vector all zeros"]


@pytest.mark.slow
def test_versions_without_padding_are_caught():
    code = ("def newer(a, b):\n"
            "    return [int(p) for p in a.split('.')] > [int(p) for p in b.split('.')]\n")
    failed = _failed(_grade("p03.003", code))
    assert list(failed) == ["and the other way round"]


@pytest.mark.slow
def test_items_annotated_as_int_is_caught():
    code = ("def first_or_default(items: int, default: str = 'none') -> str:\n"
            "    return items[0] if items else default\n")
    failed = _failed(_grade("p02.016", code))
    assert set(failed) == {"items is a list", "of strings"}


@pytest.mark.slow
def test_reversing_through_a_python_list_is_caught():
    entry = _exercise("p04.003")
    code = entry["solution"].replace(
        "def reverse(head):",
        "def reverse(head):\n"
        "    return from_list(to_list(head)[::-1])\n\n\n"
        "def _unused(head):")
    failed = _failed(_grade("p04.003", code))
    assert set(failed) == {"reverses in place", "no list used in reverse"}


@pytest.mark.slow
def test_a_constant_deck_length_is_caught():
    code = ("class Deck:\n"
            "    def __init__(self):\n"
            "        self.cards = ['A', 'B', 'C', 'D', 'E']\n"
            "    def __len__(self):\n"
            "        return 5\n"
            "    def __getitem__(self, index):\n"
            "        return self.cards[index]\n")
    assert list(_failed(_grade("p02.009", code))) == ["follows its cards"]


@pytest.mark.slow
def test_a_wrong_boolean_is_explained_as_a_wrong_answer():
    """38 `is True/False` checks once told learners about object identity."""
    code = "def is_leap(year):\n    return year % 4 == 0\n"
    failed = _failed(_grade("p01.007", code))
    assert failed["century that is not"] == (
        "The check expects False and your code gave back True.")


@pytest.mark.slow
def test_an_exception_check_names_what_came_back():
    code = ("def grade(score):\n"
            "    for floor, letter in ((90, 'A'), (80, 'B'), (70, 'C'), (60, 'D')):\n"
            "        if score >= floor:\n"
            "            return letter\n"
            "    return 'F'\n")
    failed = _failed(_grade("p01.006", code))
    assert failed["rejects over 100"] == (
        "grade(101) should raise ValueError, but it returned 'A'")
    assert failed["rejects negative"] == (
        "grade(-1) should raise ValueError, but it returned 'F'")


def test_the_verifier_builds_a_constant_stub_for_every_function(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "build_tools"))
    verifier = importlib.import_module("verify_exercises")
    solution = ("import math\n\n"
                "def area(r):\n    return math.pi * r * r\n\n"
                "async def later():\n    return 1\n\n"
                "class Keep:\n    def method(self):\n        return 5\n")
    stubs = dict(verifier.constant_stubs(solution))
    assert set(stubs) == set(verifier.CONSTANTS)
    stub = stubs["0"]
    assert "def area(r):\n    return 0" in stub
    assert "async def later():\n    return 0" in stub
    assert "return 5" in stub               # classes are left alone
    assert verifier.constant_stubs("class Only:\n    pass\n") == []
