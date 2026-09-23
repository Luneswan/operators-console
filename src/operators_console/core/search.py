"""One search box over the whole course, and over what you wrote in it.

The curriculum half of the index is built once at startup from the bundled
content, which is small enough (a few thousand short strings) that a linear
scan with a scoring function beats the complexity of a real inverted index.

The other half is yours: phase notes, project notes and repo URLs, and log
entries. Those change while the app is open - a note typed a minute ago has
to be findable - so they are read again whenever the store has moved, keyed
on the same change counter the pages use to decide whether to redraw. There
are only ever a few hundred of them, so re-reading costs a few queries.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import chain

from .curriculum import Curriculum
from .textmatch import haystack as _haystack
from .textmatch import slug, terms

PHASE = "phase"
ITEM = "item"
RESOURCE = "resource"
EXERCISE = "exercise"
PROJECT = "project"
QUESTION = "question"
FIELD = "field"
CERT = "cert"
SHELF = "shelf"
VIDEO = "video"
NOTE = "note"
LOG = "log"

#: How much of a note stands in for it in a one line result.
SNIPPET = 90


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


def _snippet(body: str) -> str:
    """The first line of a note, on one line and short enough to read."""
    text = " ".join(str(body or "").split())
    if len(text) <= SNIPPET:
        return text
    return text[:SNIPPET - 1].rstrip() + "…"


def _store_key(store):
    """Where the store is now. Mirrors ``ui.views.base.store_key``.

    Core must not import the interface, and the interface's version carries
    a widget's own extras, so the two lines live in both places rather than
    the interface reaching down or core reaching up.
    """
    try:
        version = store.db.execute("PRAGMA data_version").fetchone()[0]
        return (store.db.total_changes, version)
    except Exception:
        return None         # closed, or mid-restore: treat as unreadable


class SearchIndex:
    def __init__(self, curriculum: Curriculum, store=None) -> None:
        self.c = curriculum
        self.store = store
        self.entries: list = []
        self._live: list = []
        self._live_key = ()
        self._build()

    def _add(self, kind: str, title: str, context: str, target: str,
             phase: str, extra: str = "") -> None:
        self.entries.append((_haystack(title, context, extra),
                             Hit(kind, title, context, target, phase)))

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
                      field.build + " " + " ".join(x.name for x in field.libs))
        for cert in self.c.certs:
            self._add(CERT, cert.name, "%s - %s" % (cert.by, cert.cost),
                      cert.id, "", cert.what)
        # The Library's shelf and its video list. Both open their own card
        # on the Library page, under the same id the page files the card's
        # read mark under, rather than leaving the app for a browser.
        for group in self.c.shelf:
            for link in group.items:
                self._add(SHELF, link.name, group.group,
                          library_target(SHELF, link.name), "", link.url)
        for group in self.c.channels:
            for item in group.items:
                self._add(VIDEO, item.name, group.group,
                          library_target(VIDEO, item.name), "", item.why)

    # -- what the learner wrote -------------------------------------------

    def live_entries(self) -> list:
        """The learner's own writing, re-read whenever the store moved."""
        if self.store is None:
            return []
        key = _store_key(self.store)
        if key is None:
            return []
        if key != self._live_key:
            self._live = self._scan_store()
            self._live_key = key
        return self._live

    def _scan_store(self) -> list:
        out: list = []

        def add(kind, title, context, target, phase, extra=""):
            if not title:
                return
            out.append((_haystack(title, context, extra),
                        Hit(kind, title, context, target, phase)))

        store = self.store
        try:
            notes = store.all_notes()
        except Exception:
            return out
        for scope in sorted(notes):
            body = (notes[scope] or "").strip()
            # Only scopes that lead somewhere are indexed: every hit the box
            # offers has to open a page when it is pressed.
            if not body or not scope.startswith("phase:"):
                continue
            phase = self.c.phase(scope.split(":", 1)[1])
            if phase is None:
                continue
            # The kind already says "Note"; the context says where it is,
            # in the same words an item from that phase would use.
            add(NOTE, _snippet(body), "%s %s" % (phase.num, phase.name),
                phase.id, phase.id, body)

        # One query for every project that has a row, rather than one SELECT
        # per project on every keystroke that moved the store.
        try:
            states = store.project_states()
        except Exception:
            return out
        for project in self.c.projects:
            row = states.get(project.id) or {}
            body = (row.get("notes") or "").strip()
            repo = (row.get("repo_url") or "").strip()
            if not body and not repo:
                continue
            add(NOTE, _snippet(body) or repo,
                project.title if body else "%s - repository" % project.title,
                project.id, project.phase, " ".join((body, repo)))

        try:
            rows = store.logs()
        except Exception:
            return out
        for row in rows:
            entry = dict(row)
            day = str(entry.get("day") or "")
            focus = (entry.get("focus") or "").strip()
            built = (entry.get("built") or "").strip()
            add(LOG, ("%s - %s" % (day, focus)) if focus else day,
                "built: %s" % _snippet(built) if built else "your log",
                str(entry.get("id") or ""), "",
                " ".join(str(entry.get(field) or "")
                         for field in ("built", "stuck", "next_up")))
        return out

    # -- searching ---------------------------------------------------------

    def search(self, query: str, limit: int = 60) -> list:
        # The same folding the page filters use (core/textmatch): case,
        # accents, dashes, arrows and spacing never decide a match.
        words = terms(query)
        if len("".join(words)) < 2:
            return []
        starts = [re.compile(r"\b" + re.escape(word)) for word in words]
        results = []
        for haystack, hit in chain(self.entries, self.live_entries()):
            score = 0.0
            # The title is the first line of the haystack.
            title_end = haystack.find("\n")
            if title_end < 0:
                title_end = len(haystack)
            for word, start in zip(words, starts, strict=True):
                pos = haystack.find(word)
                if pos < 0:
                    score = 0.0
                    break
                score += 3.0 if pos < title_end else 1.0
                if start.search(haystack):
                    score += 1.0
            if score:
                if hit.kind == PHASE:
                    score += 2.0
                elif hit.kind in (NOTE, LOG):
                    # Your own words about a word you searched for beat a
                    # curriculum line that merely mentions it: there are a
                    # handful of them and a thousand of the others, and a
                    # note nobody can reach is a note that was not indexed.
                    score += 1.5
                results.append((score, hit))
        results.sort(key=lambda pair: (-pair[0], pair[1].title))
        return [hit for _score, hit in results[:limit]]


def library_target(kind: str, name: str) -> str:
    """The id the Library files a shelf or video card under.

    The same string as ``ui.views.library.read_id`` gives the card's read
    mark: "lib:shelf:<slug>" or "lib:video:<slug>".
    """
    return "lib:%s:%s" % (kind, slug(name))
