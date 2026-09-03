"""Immutable curriculum objects.

These describe the *content* of the course. Anything the learner changes lives
in the database instead, keyed by the ids defined here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Resource:
    name: str
    kind: str
    why: str
    url: str


@dataclass(frozen=True, slots=True)
class Item:
    id: str
    text: str


@dataclass(frozen=True, slots=True)
class Section:
    id: str
    title: str
    items: tuple[Item, ...]


@dataclass(frozen=True, slots=True)
class Gate:
    note: str
    items: tuple[Item, ...]


@dataclass(frozen=True, slots=True)
class Phase:
    id: str
    num: str
    name: str
    when: str
    aim: str
    no_progress: bool
    est_hours: int
    level: int
    tags: tuple[str, ...]
    prereq: tuple[str, ...]
    resources: tuple[Resource, ...]
    sections: tuple[Section, ...]
    snippet: str
    gate: Gate | None

    @property
    def items(self) -> tuple[Item, ...]:
        return tuple(i for s in self.sections for i in s.items)

    @property
    def trackable_ids(self) -> tuple[str, ...]:
        """Ids that count toward the progress meter."""
        if self.no_progress:
            return ()
        ids = [i.id for i in self.items]
        if self.gate:
            ids.extend(g.id for g in self.gate.items)
        return tuple(ids)


@dataclass(frozen=True, slots=True)
class Question:
    id: str
    prompt: str
    choices: tuple[str, ...]
    correct: int
    explain: str


@dataclass(frozen=True, slots=True)
class Quiz:
    id: str
    phase: str
    name: str
    desc: str
    questions: tuple[Question, ...]


@dataclass(frozen=True, slots=True)
class TestCase:
    name: str
    code: str


@dataclass(frozen=True, slots=True)
class Exercise:
    id: str
    phase: str
    topic: str
    title: str
    difficulty: int
    prompt: str
    starter: str
    tests: tuple[TestCase, ...]
    hints: tuple[str, ...]
    solution: str
    setup: str = ""


@dataclass(frozen=True, slots=True)
class Project:
    id: str
    phase: str
    title: str
    kind: str
    brief: str
    why: str
    requirements: tuple[str, ...]
    stretch: tuple[str, ...]
    rubric: tuple[str, ...]

    @property
    def requirement_ids(self) -> tuple[str, ...]:
        return tuple(f"{self.id}.r{i}" for i in range(len(self.requirements)))


@dataclass(frozen=True, slots=True)
class Link:
    name: str
    url: str


@dataclass(frozen=True, slots=True)
class Field:
    id: str
    group: str
    name: str
    blurb: str
    build: str
    libs: tuple[Link, ...]


@dataclass(frozen=True, slots=True)
class Cert:
    id: str
    name: str
    by: str
    cost: str
    time: str
    what: str
    worth: str
    url: str


@dataclass(frozen=True, slots=True)
class Group:
    group: str
    items: tuple[Link, ...]


@dataclass(frozen=True, slots=True)
class ChannelItem:
    name: str
    url: str
    why: str


@dataclass(frozen=True, slots=True)
class ChannelGroup:
    group: str
    items: tuple[ChannelItem, ...]


@dataclass(frozen=True, slots=True)
class MatrixRow:
    skill: str
    covers: str
    proof: str


@dataclass(frozen=True, slots=True)
class Track:
    """A named goal that reorders the roadmap."""
    id: str
    name: str
    blurb: str
    tags: tuple[str, ...]
    core: tuple[str, ...]
    optional: tuple[str, ...]
