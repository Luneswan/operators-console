"""The log kept for months: paging, filtering, correcting, undoing, reading.

Walk 08 writes a handful of entries and deletes them again. This is the same
page after week nine, when the history is longer than one screenful, an entry
turns out to be wrong, a delete was a mis-click, a day gets logged twice, and
the notes written across the curriculum are wanted back.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from .harness import REC, click, pump, shortcut, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]

#: A budget that measures the page rather than the instrument.
#:
#: The sensors stamp every QPushButton with the source line that made it,
#: which walks the Python frames and resolves a filesystem path for each one.
#: A history card carries two buttons, so drawing a sixty-card page costs
#: roughly forty times here what it costs in the application: measured with
#: the sensors off, the first page takes 213 ms, a further sixty 325 ms and
#: the last ten 88 ms. Only the steps that draw a whole page get this.
PAGE_DRAW = 20000

#: The first note opened on a project builds the Projects page - twenty-two
#: cards, each with several controls. That is the Projects page's cost, and
#: walk 07 measures it where it belongs.
FIRST_PROJECTS_BUILD = 20000


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def _all_named(root, text) -> list:
    from PySide6.QtWidgets import QPushButton
    return [w for w in root.findChildren(QPushButton) if w.text() == text]


def _cards(layout) -> list:
    out = []
    for index in range(layout.count()):
        widget = layout.itemAt(index).widget()
        if widget is not None:
            out.append(widget)
    return out


def _texts(root) -> str:
    from PySide6.QtWidgets import QLabel
    return "\n".join(w.text() for w in root.findChildren(QLabel))


def _day(offset: int) -> str:
    return (date.today() - timedelta(days=offset)).isoformat()


def _journal(app, window):
    window.go("journal", "")
    pump(app, 2)
    return window.views["journal"]


# -- a history longer than one screenful -----------------------------------


def test_nine_weeks_of_history_can_all_be_reached(walk_app, window, store):
    for index in range(130):
        store.add_log(_day(index), "day %d" % index, 1.0,
                      "a thing that got built", "", "")
    view = _journal(walk_app, window)

    with step(walk_app, "journal", "the history opens on the newest sixty",
              window):
        assert len(_cards(view.history)) == 60
        assert view.counter.text() == "130 entries, 60 shown"
        assert view.more.isEnabled(), "nothing offers the older entries"

    with step(walk_app, "journal", "press Show older for the next sixty",
              window, budget=PAGE_DRAW):
        click(walk_app, view.more)
        assert len(_cards(view.history)) == 120
        assert view.counter.text() == "130 entries, 120 shown"

    with step(walk_app, "journal", "press Show older for the last ten",
              window):
        click(walk_app, view.more)
        assert len(_cards(view.history)) == 130
        assert view.counter.text() == "130 entries, 130 shown"
        assert not view.more.isEnabled()
    REC.bump("log entries paged into view", 130)

    with step(walk_app, "journal", "find one entry among a hundred", window):
        view.filter.setText("day 97")
        pump(walk_app, 2)
        assert len(_cards(view.history)) == 1
        assert "day 97" in _texts(view)

    with step(walk_app, "journal", "a filter that matches nothing says so",
              window):
        view.filter.setText("a word never written")
        pump(walk_app, 2)
        assert view.counter.text() == "0 of 130 entries match, 0 shown"
        assert "No entry matches that filter" in _texts(view)
        view.filter.clear()
        pump(walk_app, 2)

    with step(walk_app, "journal", "narrow the range, then widen it again",
              window, budget=PAGE_DRAW):
        for index in (0, 1, 2):
            view.range.setCurrentIndex(index)
            pump(walk_app, 2)
            assert view.counter.text().endswith("shown")
        assert len(_cards(view.history)) == 60      # back to All, first page
    REC.bump("log ranges tried", 3)


# -- an entry that turned out to be wrong ----------------------------------


def test_an_entry_is_corrected_and_the_correction_undone(walk_app, window,
                                                         store):
    store.add_log(_day(2), "generators", 2.5, "a streaming pipeline",
                  "the loop variable", "read itertools")
    view = _journal(walk_app, window)

    with step(walk_app, "journal", "load an old entry back into the form",
              window):
        edit = _named(_cards(view.history)[0], "Edit")
        assert edit is not None, "no way to correct an entry"
        click(walk_app, edit)
        assert view.focus.text() == "generators"
        assert view.built.toPlainText() == "a streaming pipeline"
        assert view.stuck.toPlainText() == "the loop variable"
        assert view.next_up.text() == "read itertools"
        assert view.hours.value() == 2.5
        assert view.date.date().toString("yyyy-MM-dd") == _day(2)
        assert view.save.text() == "Save changes"

    with step(walk_app, "journal", "save the correction", window):
        view.focus.setText("generators, properly")
        view.hours.setValue(4.0)
        click(walk_app, view.save)
        rows = store.logs()
        assert len(rows) == 1, "the correction added a row instead of one edit"
        assert rows[0]["focus"] == "generators, properly"
        assert store.total_hours() == 4.0
        assert view.save.text() == "Log today"

    with step(walk_app, "journal", "take the correction back with Ctrl+Z",
              window):
        shortcut(walk_app, window, "Ctrl+Z")
        rows = store.logs()
        assert len(rows) == 1
        assert rows[0]["focus"] == "generators", (
            "one undo did not restore the whole entry")
        assert store.total_hours() == 2.5

    with step(walk_app, "journal", "and put it back with Ctrl+Y", window):
        shortcut(walk_app, window, "Ctrl+Y")
        assert store.logs()[0]["focus"] == "generators, properly"
    REC.bump("log entries corrected")

    with step(walk_app, "journal", "start an edit and cancel out of it",
              window):
        view = _journal(walk_app, window)
        click(walk_app, _named(_cards(view.history)[0], "Edit"))
        assert view.cancel.isVisibleTo(view)
        click(walk_app, view.cancel)
        assert view.save.text() == "Log today"
        assert view.focus.text() == ""
        assert len(store.logs()) == 1


# -- a delete that was a mis-click -----------------------------------------


def test_a_deleted_entry_comes_back(walk_app, window, store):
    store.add_log(_day(1), "generators", 2.5, "built it", "stuck on it",
                  "next thing")
    view = _journal(walk_app, window)

    with step(walk_app, "journal", "delete an entry by mistake", window):
        click(walk_app, _named(_cards(view.history)[0], "Delete"))
        assert store.logs() == []

    with step(walk_app, "journal", "Ctrl+Z brings the whole entry back",
              window):
        shortcut(walk_app, window, "Ctrl+Z")
        rows = store.logs()
        assert len(rows) == 1, "a mis-clicked delete was unrecoverable"
        row = rows[0]
        assert (row["day"], row["focus"], row["hours"]) == (
            _day(1), "generators", 2.5)
        assert (row["built"], row["stuck"], row["next_up"]) == (
            "built it", "stuck on it", "next thing")
        assert store.total_hours() == 2.5
        assert store.activity()[_day(1)]["minutes"] == 150

    with step(walk_app, "journal", "Ctrl+Y deletes it again", window):
        shortcut(walk_app, window, "Ctrl+Y")
        assert store.logs() == []
        assert store.total_hours() == 0
    REC.bump("log entries deleted and restored")


# -- a day logged twice ----------------------------------------------------


def test_a_second_entry_for_one_day_warns_before_it_stacks(walk_app, window,
                                                           store):
    view = _journal(walk_app, window)

    with step(walk_app, "journal", "log today for the first time", window):
        assert not view.dup.isVisibleTo(view), "a warning with nothing to warn"
        view.focus.setText("Generators")
        view.hours.setValue(2.5)
        click(walk_app, view.save)
        assert len(store.logs()) == 1

    with step(walk_app, "journal", "the form warns before the day stacks",
              window):
        assert view.dup.isVisibleTo(view), (
            "a second entry for today would stack with no warning")
        assert view.dup_text.text() == (
            "You already logged 2.5 h today - this adds to it")

    with step(walk_app, "journal", "log today again anyway", window):
        view.focus.setText("Generators, again")
        view.hours.setValue(1.0)
        click(walk_app, view.save)
        assert len(store.logs()) == 2
        assert store.total_hours() == 3.5
        assert view.dup_text.text() == (
            "You already logged 3.5 h today - this adds to it")
    REC.bump("duplicate days warned about")


# -- the notes written all over the curriculum -----------------------------


def test_every_note_is_gathered_and_opens_its_own_page(walk_app, window,
                                                       store, curriculum):
    phases = curriculum.phases[1:5]
    projects = curriculum.projects[:3]
    for phase in phases:
        store.set_note("phase:" + phase.id, "What %s finally taught me."
                       % phase.name)
    for project in projects:
        store.set_project(project.id,
                          notes="What %s still needs." % project.title)
    view = _journal(walk_app, window)

    with step(walk_app, "journal", "every note written is listed here",
              window):
        cards = _cards(view.notes)
        assert len(cards) == len(phases) + len(projects), (
            "%d notes listed for %d written"
            % (len(cards), len(phases) + len(projects)))
        written = _texts(view)
        for phase in phases:
            assert phase.name in written
        for project in projects:
            assert project.title in written
    REC.bump("notes gathered onto the log", len(phases) + len(projects))

    with step(walk_app, "journal", "the filter searches the notes too",
              window):
        view.filter.setText(projects[0].title)
        pump(walk_app, 2)
        assert len(_cards(view.notes)) == 1
        view.filter.clear()
        pump(walk_app, 2)

    total = len(phases) + len(projects)
    for index in range(total):
        with step(walk_app, "journal", "open note %d from the log" % index,
                  window, budget=FIRST_PROJECTS_BUILD):
            view = _journal(walk_app, window)
            opens = []
            for card in _cards(view.notes):
                opens += _all_named(card, "Open")
            assert len(opens) == total
            click(walk_app, opens[index])
            assert window.current_key in ("phase", "projects"), (
                "Open did not navigate anywhere")
    REC.bump("notes opened from the log", total)


def test_the_empty_notes_section_says_what_would_fill_it(walk_app, window):
    view = _journal(walk_app, window)
    with step(walk_app, "journal", "the notes section with nothing in it",
              window):
        assert len(_cards(view.notes)) == 1
        assert ("Notes you write on phase and project pages collect here."
                in _texts(view))
