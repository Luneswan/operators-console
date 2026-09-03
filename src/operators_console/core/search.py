"""One search box over the whole course.

The index is built once at startup from the bundled content, which is small
enough (a few thousand short strings) that a linear scan with a scoring
function beats the complexity of a real inverted index.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .curriculum import Curriculum

PHASE = "phase"
ITEM = "item"
RESOURCE = "resource"
EXERCISE = "exercise"
PROJECT = "project"
QUESTION = "question"
FIELD = "field"
CERT = "cert"


@dataclass(frozen=True, slots=True)
class Hit:
    kind: str
    title: str
    context: str
    target: str
    phase: str
    score: float = 0.0


def _plain(text: str) -> str:
    return re.sub(r"</?em>", "", text)


class SearchIndex:
    def __init__(self, curriculum: Curriculum) -> None:
        self.c = curriculum
        self.entries: list = []
        self._build()

    def _add(self, kind: str, title: str, context: str, target: str,
             phase: str, extra: str = "") -> None:
        haystack = " ".join((title, context, extra)).lower()
        self.entries.append((haystack, Hit(kind, title, context, target, phase)))

    def _build(self) -> None:
        for phase in self.c.phases:
            self._add(PHASE, "%s %s" % (phase.num, phase.name), phase.aim,
                      phase.id, phase.id, " ".join(phase.tags) + " " + phase.when)
            for section in phase.sections:
                for item in section.items:
                    self._add(ITEM, _plain(item.text),
                              "%s %s / %s" % (phase.num, phase.name, section.title),
                              item.id, phase.id)
            if phase.gate:
                for item in phase.gate.items:
                    self._add(ITEM, _plain(item.text),
                              "%s %s / Gate" % (phase.num, phase.name),
                              item.id, phase.id)
            for res in phase.resources:
                self._add(RESOURCE, res.name, res.why, res.url, phase.id, res.kind)

        for exercise in self.c.exercises:
            self._add(EXERCISE, exercise.title, exercise.topic, exercise.id,
                      exercise.phase, _plain(exercise.prompt))
        for project in self.c.projects:
            self._add(PROJECT, project.title, project.brief, project.id,
                      project.phase, " ".join(project.requirements))
        for quiz in self.c.quizzes:
            for question in quiz.questions:
                self._add(QUESTION, question.prompt, quiz.name, question.id,
                          quiz.phase, question.explain)
        for field in self.c.fields:
            self._add(FIELD, field.name, field.blurb, field.id, "",
                      field.build + " " + " ".join(l.name for l in field.libs))
        for cert in self.c.certs:
            self._add(CERT, cert.name, "%s - %s" % (cert.by, cert.cost),
                      cert.id, "", cert.what)

    def search(self, query: str, limit: int = 60) -> list:
        query = query.strip().lower()
        if len(query) < 2:
            return []
        terms = [t for t in re.split(r"\s+", query) if t]
        results = []
        for haystack, hit in self.entries:
            score = 0.0
            for term in terms:
                pos = haystack.find(term)
                if pos < 0:
                    score = 0.0
                    break
                score += 3.0 if pos < len(hit.title) else 1.0
                if re.search(r"\b" + re.escape(term), haystack):
                    score += 1.0
            if score:
                if hit.kind == PHASE:
                    score += 2.0
                results.append((score, hit))
        results.sort(key=lambda pair: (-pair[0], pair[1].title))
        return [hit for _score, hit in results[:limit]]
