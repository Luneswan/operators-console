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


def apply_edits() -> None:
    """Swap in the plain-language text from project_edits.json."""
    edits = json.loads((Path(__file__).parent / "project_edits.json")
                       .read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in PROJECTS}
    for pid, fields in edits.items():
        if pid.startswith("_"):
            continue
        if pid not in by_id:
            raise SystemExit("project_edits.json: unknown project %s" % pid)
        project = by_id[pid]
        for field, value in fields.items():
            if isinstance(value, str):
                project[field] = value
                continue
            for pair in value:
                items = project[field]
                if pair["old"] not in items:
                    raise SystemExit("project_edits.json: %s %s has no %r"
                                     % (pid, field, pair["old"]))
                items[items.index(pair["old"])] = pair["new"]


def dump(path: Path) -> None:
    apply_edits()
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
