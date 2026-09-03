"""Run every official solution against its own checks.

An exercise whose solution fails is a bug in the course, not in the learner.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from operators_console.core.runner import run_exercise  # noqa: E402
from operators_console.core.models import TestCase  # noqa: E402

data = json.loads((ROOT / "src" / "operators_console" / "data" /
                   "exercises.json").read_text(encoding="utf-8"))

failures = []
starter_passes = []
for entry in data["exercises"]:
    tests = tuple(TestCase(t["name"], t["code"]) for t in entry["tests"])
    result = run_exercise(entry["solution"], tests, entry.get("setup", ""),
                          timeout=30)
    if not result.ok:
        failures.append((entry["id"], result))
    # The starter must NOT pass, or the exercise teaches nothing.
    starter = run_exercise(entry["starter"], tests, entry.get("setup", ""),
                           timeout=30)
    if starter.ok:
        starter_passes.append(entry["id"])

print("checked", len(data["exercises"]), "exercises")
print("solution failures:", len(failures))
for eid, result in failures:
    print("  -", eid, "|", result.summary)
    if result.error:
        print("     ", result.error.strip().replace("\n", "\n      ")[:600])
    for case in result.cases:
        if not case.passed:
            print("      x", case.name, "->", case.message[:200])
print("starter already passes:", starter_passes)
sys.exit(1 if failures or starter_passes else 0)
