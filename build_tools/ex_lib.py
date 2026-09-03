"""Helpers for authoring the exercise bank."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

EXERCISES: list = []
_SEEN: set = set()


def d(text: str) -> str:
    """Dedent and strip an authored block."""
    return textwrap.dedent(text).strip("\n")


def ex(eid, phase, topic, title, diff, prompt, starter, tests,
       hints=(), solution="", setup=""):
    if eid in _SEEN:
        raise ValueError("duplicate exercise id: " + eid)
    _SEEN.add(eid)
    EXERCISES.append({
        "id": eid,
        "phase": phase,
        "topic": topic,
        "title": title,
        "difficulty": diff,
        "prompt": d(prompt),
        "starter": d(starter) + "\n",
        "tests": [{"name": n, "code": d(c)} for n, c in tests],
        "hints": list(hints),
        "solution": d(solution) + "\n" if solution else "",
        "setup": d(setup) + "\n" if setup else "",
    })


def dump(path: Path) -> None:
    payload = {"schema": 1, "exercises": EXERCISES}
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    by_phase: dict = {}
    for e in EXERCISES:
        by_phase[e["phase"]] = by_phase.get(e["phase"], 0) + 1
    print("exercises:", len(EXERCISES))
    for k in sorted(by_phase):
        print("  %-5s %d" % (k, by_phase[k]))
