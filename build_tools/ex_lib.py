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


def apply_hint_rewrites() -> None:
    """Swap in the plain-words hints from hint_rewrites.json (see its _comment)."""
    rewrites = json.loads((Path(__file__).parent / "hint_rewrites.json")
                          .read_text(encoding="utf-8"))
    rewrites = {k: v for k, v in rewrites.items() if not k.startswith("_")}
    by_id = {e["id"]: e for e in EXERCISES}
    unknown = sorted(set(rewrites) - set(by_id))
    if unknown:
        raise SystemExit("hint_rewrites.json names unknown exercises: %s"
                         % unknown)
    for eid, hints in rewrites.items():
        if not hints or not all(isinstance(h, str) and h.strip()
                                for h in hints):
            raise SystemExit("hint_rewrites.json: %s has an empty hint" % eid)
        by_id[eid]["hints"] = list(hints)


def dump(path: Path) -> None:
    apply_hint_rewrites()
    payload = {"schema": 1, "exercises": EXERCISES}
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    by_phase: dict = {}
    for e in EXERCISES:
        by_phase[e["phase"]] = by_phase.get(e["phase"], 0) + 1
    print("exercises:", len(EXERCISES))
    for k in sorted(by_phase):
        print("  %-5s %d" % (k, by_phase[k]))
