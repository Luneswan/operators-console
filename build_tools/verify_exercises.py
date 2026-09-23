"""Check the shipped exercise bank against the rules every exercise must keep.

An exercise whose solution fails is a bug in the course, not in the learner.
Beyond that, each exercise must:

* fail its own starter, or it teaches nothing;
* offer at least two hints, so the hint ladder has a nudge before the answer;
* fail a stub that returns the same constant from every function, or its
  checks can be passed without reading the input at all.

Run from anywhere: python build_tools/verify_exercises.py
"""
import ast
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from operators_console.core.runner import run_exercise  # noqa: E402
from operators_console.core.models import TestCase  # noqa: E402

BANK = ROOT / "src" / "operators_console" / "data" / "exercises.json"
MIN_HINTS = 2
#: What a do-nothing function most often returns. Each must fail somewhere.
CONSTANTS = ("None", "0", "1", "True", "False", "''", "[]", "{}", "()", "-1")


def constant_stubs(solution: str) -> list:
    """The solution with every top-level function body replaced by `return c`.

    One stub per constant. Classes are left alone - a class that ignores its
    input is caught by the starter check - so an exercise with no top-level
    function gets no stubs.
    """
    try:
        tree = ast.parse(solution)
    except SyntaxError:
        return []
    functions = [node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not functions:
        return []
    stubs = []
    for constant in CONSTANTS:
        value = ast.parse(constant, mode="eval").body
        for node in functions:
            node.body = [ast.Return(value=value)]
        stubs.append((constant, ast.unparse(ast.fix_missing_locations(tree))))
    return stubs


def _run(code, entry):
    tests = tuple(TestCase(t["name"], t["code"]) for t in entry["tests"])
    return run_exercise(code, tests, entry.get("setup", ""), timeout=30)


def audit(entry) -> dict:
    """Every problem with one exercise, keyed by rule."""
    problems = {}
    result = _run(entry["solution"], entry)
    if not result.ok:
        problems["solution"] = result
    if _run(entry["starter"], entry).ok:
        problems["starter"] = True
    if len(entry.get("hints") or []) < MIN_HINTS:
        problems["hints"] = len(entry.get("hints") or [])
    passing = [constant for constant, stub in constant_stubs(entry["solution"])
               if _run(stub, entry).ok]
    if passing:
        problems["stub"] = passing
    return problems


def main() -> int:
    data = json.loads(BANK.read_text(encoding="utf-8"))
    entries = data["exercises"]
    with ThreadPoolExecutor(max_workers=8) as pool:
        reports = list(pool.map(audit, entries))

    pairs = list(zip(entries, reports, strict=True))
    failures = [(e["id"], r["solution"]) for e, r in pairs if "solution" in r]
    starter_passes = [e["id"] for e, r in pairs if "starter" in r]
    thin_hints = [(e["id"], r["hints"]) for e, r in pairs if "hints" in r]
    stub_passes = [(e["id"], r["stub"]) for e, r in pairs if "stub" in r]

    print("checked", len(entries), "exercises")
    print("solution failures:", len(failures))
    for eid, result in failures:
        print("  -", eid, "|", result.summary)
        if result.error:
            print("     ", result.error.strip().replace("\n", "\n      ")[:600])
        for case in result.cases:
            if not case.passed:
                print("      x", case.name, "->", case.message[:200])
    print("starter already passes:", starter_passes)
    print("fewer than %d hints:" % MIN_HINTS, thin_hints)
    print("a constant-returning stub passes:", stub_passes)
    return 1 if failures or starter_passes or thin_hints or stub_passes else 0


if __name__ == "__main__":
    sys.exit(main())
