"""Helpers for authoring the project bank."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

PROJECTS: list = []
_SEEN: set = set()


def d(text: str) -> str:
    return textwrap.dedent(text).strip("\n").strip()


def pr(pid, phase, title, kind, brief, why, requirements, stretch=(), rubric=()):
    if pid in _SEEN:
        raise ValueError("duplicate project id: " + pid)
    _SEEN.add(pid)
    PROJECTS.append({
        "id": pid,
        "phase": phase,
        "title": title,
        "kind": kind,
        "brief": d(brief),
        "why": d(why),
        "requirements": [d(r) for r in requirements],
        "stretch": [d(s) for s in stretch],
        "rubric": [d(r) for r in rubric],
    })


DEFAULT_RUBRIC = (
    "It runs from a clean checkout by following the README alone.",
    "Every behaviour you claim is covered by a test that fails when you break it.",
    "The commit history shows the work, not one giant commit.",
    "You can explain every design decision, including the ones you rejected.",
)


def dump(path: Path) -> None:
    for project in PROJECTS:
        if not project["rubric"]:
            project["rubric"] = list(DEFAULT_RUBRIC)
    Path(path).write_text(
        json.dumps({"schema": 1, "projects": PROJECTS}, ensure_ascii=False,
                   indent=1), encoding="utf-8")
    by_phase: dict = {}
    for project in PROJECTS:
        by_phase[project["phase"]] = by_phase.get(project["phase"], 0) + 1
    print("projects:", len(PROJECTS))
    for key in sorted(by_phase):
        print("  %-5s %d" % (key, by_phase[key]))
