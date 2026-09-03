"""Loads the bundled course content into immutable objects, once per process."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import paths
from .models import (
    Cert, ChannelGroup, ChannelItem, Exercise, Field, Gate, Group, Item, Link,
    MatrixRow, Phase, Project, Question, Quiz, Resource, Section, TestCase,
    Track,
)


def _read(name: str) -> dict:
    path: Path = paths.bundled_data_dir() / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class Curriculum:
    """Everything the app knows about the course, addressable by id."""

    def __init__(self) -> None:
        raw = _read("curriculum.json")
        self.schema: int = raw["schema"]
        self.generated: str = raw["generated"]

        self.phases: tuple[Phase, ...] = tuple(_phase(p) for p in raw["phases"])
        self.quizzes: tuple[Quiz, ...] = tuple(_quiz(q) for q in raw["quizzes"])
        self.fields: tuple[Field, ...] = tuple(
            Field(f["id"], f["group"], f["name"], f["blurb"], f["build"],
                  tuple(Link(l["name"], l["url"]) for l in f["libs"]))
            for f in raw["fields"]
        )
        self.certs: tuple[Cert, ...] = tuple(
            Cert(c["id"], c["name"], c["by"], c["cost"], c["time"], c["what"],
                 c["worth"], c.get("url", ""))
            for c in raw["certs"]
        )
        self.channels: tuple[ChannelGroup, ...] = tuple(
            ChannelGroup(c["group"], tuple(
                ChannelItem(i["name"], i["url"], i["why"]) for i in c["items"]))
            for c in raw["channels"]
        )
        self.shelf: tuple[Group, ...] = tuple(
            Group(s["group"], tuple(Link(i["name"], i["url"]) for i in s["items"]))
            for s in raw["shelf"]
        )
        self.matrix: tuple[MatrixRow, ...] = tuple(
            MatrixRow(m["skill"], m["covers"], m["proof"]) for m in raw["matrix"]
        )

        self.exercises: tuple[Exercise, ...] = tuple(
            _exercise(e) for e in _read("exercises.json")["exercises"]
        )
        self.projects: tuple[Project, ...] = tuple(
            _project(p) for p in _read("projects.json")["projects"]
        )
        self.tracks: tuple[Track, ...] = tuple(
            Track(t["id"], t["name"], t["blurb"], tuple(t["tags"]),
                  tuple(t["core"]), tuple(t["optional"]))
            for t in _read("tracks.json")["tracks"]
        )

        self._phase_by_id = {p.id: p for p in self.phases}
        self._quiz_by_id = {q.id: q for q in self.quizzes}
        self._exercise_by_id = {e.id: e for e in self.exercises}
        self._project_by_id = {p.id: p for p in self.projects}
        self._track_by_id = {t.id: t for t in self.tracks}
        self._item_text = {
            i.id: i.text for p in self.phases for i in p.items
        }
        for p in self.phases:
            if p.gate:
                for g in p.gate.items:
                    self._item_text[g.id] = g.text

    # -- lookups ---------------------------------------------------------

    def phase(self, pid: str) -> Phase | None:
        return self._phase_by_id.get(pid)

    def quiz(self, qid: str) -> Quiz | None:
        return self._quiz_by_id.get(qid)

    def exercise(self, eid: str) -> Exercise | None:
        return self._exercise_by_id.get(eid)

    def project(self, pid: str) -> Project | None:
        return self._project_by_id.get(pid)

    def track(self, tid: str) -> Track | None:
        return self._track_by_id.get(tid)

    def item_text(self, item_id: str) -> str:
        return self._item_text.get(item_id, item_id)

    def quizzes_for(self, phase_id: str) -> tuple[Quiz, ...]:
        return tuple(q for q in self.quizzes if q.phase == phase_id)

    def exercises_for(self, phase_id: str) -> tuple[Exercise, ...]:
        return tuple(e for e in self.exercises if e.phase == phase_id)

    def projects_for(self, phase_id: str) -> tuple[Project, ...]:
        return tuple(p for p in self.projects if p.phase == phase_id)

    @property
    def scored_phases(self) -> tuple[Phase, ...]:
        """Phases that contribute to the completion meter."""
        return tuple(p for p in self.phases if not p.no_progress and p.trackable_ids)

    @property
    def all_questions(self) -> tuple[Question, ...]:
        return tuple(q for quiz in self.quizzes for q in quiz.questions)

    def question(self, qid: str) -> Question | None:
        for quiz in self.quizzes:
            for q in quiz.questions:
                if q.id == qid:
                    return q
        return None

    def quiz_of_question(self, qid: str) -> Quiz | None:
        for quiz in self.quizzes:
            if any(q.id == qid for q in quiz.questions):
                return quiz
        return None


def _phase(p: dict) -> Phase:
    gate = None
    if p.get("gate"):
        gate = Gate(
            p["gate"].get("note", ""),
            tuple(Item(i["id"], i["text"]) for i in p["gate"]["items"]),
        )
    return Phase(
        id=p["id"], num=p["num"], name=p["name"], when=p["when"], aim=p["aim"],
        no_progress=p["no_progress"], est_hours=p["est_hours"], level=p["level"],
        tags=tuple(p["tags"]), prereq=tuple(p["prereq"]),
        resources=tuple(Resource(r["name"], r["kind"], r["why"], r["url"])
                        for r in p["resources"]),
        sections=tuple(
            Section(s["id"], s["title"],
                    tuple(Item(i["id"], i["text"]) for i in s["items"]))
            for s in p["sections"]
        ),
        snippet=p["snippet"], gate=gate,
    )


def _quiz(q: dict) -> Quiz:
    return Quiz(
        q["id"], q["phase"], q["name"], q["desc"],
        tuple(Question(x["id"], x["prompt"], tuple(x["choices"]), x["correct"],
                       x["explain"]) for x in q["questions"]),
    )


def _exercise(e: dict) -> Exercise:
    return Exercise(
        id=e["id"], phase=e["phase"], topic=e["topic"], title=e["title"],
        difficulty=e["difficulty"], prompt=e["prompt"], starter=e["starter"],
        tests=tuple(TestCase(t["name"], t["code"]) for t in e["tests"]),
        hints=tuple(e.get("hints", ())), solution=e.get("solution", ""),
        setup=e.get("setup", ""),
    )


def _project(p: dict) -> Project:
    return Project(
        id=p["id"], phase=p["phase"], title=p["title"], kind=p["kind"],
        brief=p["brief"], why=p["why"],
        requirements=tuple(p["requirements"]), stretch=tuple(p.get("stretch", ())),
        rubric=tuple(p.get("rubric", ())),
    )


@lru_cache(maxsize=1)
def load() -> Curriculum:
    """The process-wide curriculum singleton."""
    return Curriculum()
