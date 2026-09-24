"""Immutable curriculum objects.

These describe the *content* of the course. Anything the learner changes lives
in the database instead, keyed by the ids defined here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Resource:
    """One thing to read, watch or work through.

    ``primary`` marks the single resource in its group that a learner should
    open first. Everything else in an optional group is study material they
    may never need, and the interface keeps it folded away until asked.
    """
    name: str
    kind: str
    why: str
    url: str
    primary: bool = False


@dataclass(frozen=True, slots=True)
class Item:
    id: str
    text: str
    # The study guide for a checklist line: what to do, where to learn it,
    # and how to tell it is done. Empty for gate checks and old bundles.
    how: str = ""
    where: tuple["Link", ...] = ()
    done: str = ""


@dataclass(frozen=True, slots=True)
class Section:
    id: str
    title: str
    items: tuple[Item, ...]
    # Stretch work: folded on the page and left out of progress.
    optional: bool = False
    guide: str = ""                 # how to work through the section


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
    resources_optional: bool = False
    # The snippet explained: a heading, why it is there, what each line does
    # (one entry per snippet line, "" where a line needs none), and how to
    # tell it worked.
    snippet_title: str = ""
    snippet_intro: str = ""
    snippet_lines: tuple[str, ...] = ()
    snippet_after: str = ""

    @property
    def items(self) -> tuple[Item, ...]:
        return tuple(i for s in self.sections for i in s.items)

    @property
    def core_items(self) -> tuple[Item, ...]:
        """The checklist lines that are the phase itself, not stretch work."""
        return tuple(i for s in self.sections if not s.optional
                     for i in s.items)

    @property
    def trackable_ids(self) -> tuple[str, ...]:
        """Ids that count toward the progress meter."""
        if self.no_progress:
            return ()
        ids = [i.id for i in self.core_items]
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
    # Per choice, indexed like `choices`: why a learner who picked it was
    # wrong ("" for the correct one). Empty for bundles older than 1.1.0.
    explain_choice: tuple[str, ...] = ()
    teaches: str = ""                   # the checklist item it checks


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
    primary: bool = False


@dataclass(frozen=True, slots=True)
class Field:
    id: str
    group: str
    name: str
    blurb: str
    build: str
    libs: tuple[Link, ...]
    libs_optional: bool = False


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
    optional: bool = False


@dataclass(frozen=True, slots=True)
class ChannelItem:
    name: str
    url: str
    why: str
    primary: bool = False


@dataclass(frozen=True, slots=True)
class ChannelGroup:
    group: str
    items: tuple[ChannelItem, ...]
    optional: bool = False


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


def primary_of(items) -> object | None:
    """The one item in a group marked as the place to start, if any."""
    for item in items:
        if getattr(item, "primary", False):
            return item
    return None


def split_optional(items, optional: bool):
    """Return (shown, folded) for a group of resources.

    A group that is not optional is never folded: gates, exercises, projects
    and study steps all come through here unchanged.
    """
    items = tuple(items)
    if not optional or len(items) < 2:
        return items, ()
    lead = primary_of(items)
    if lead is None:
        return items, ()
    return (lead,), tuple(i for i in items if i is not lead)
