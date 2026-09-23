"""Searching your own writing, driving the results with the keyboard, and
the library you can filter and mark as read.
"""
from __future__ import annotations

import pytest

from .harness import (
    REC, click, press, pump, shortcut, step, trigger, type_text,
)

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _hits(window):
    from PySide6.QtCore import Qt
    return [window.results.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(window.results.count())]


def _write_some_of_your_own(store, curriculum):
    """What a learner has after a fortnight: notes, a repo and a log."""
    store.set_note("phase:p01", "myceliumnote - decorators are just functions")
    project = curriculum.projects[0]
    store.set_project(project.id, notes="pangolinnote on the rubric",
                      repo_url="https://example.invalid/pangolinrepo")
    store.add_log("2026-09-23", "narwhalfocus", 2.0, "a chat server",
                  "the event loop", "write the tests")
    return project


# -- the box finds what you wrote ------------------------------------------


def _warm(walk_app, window, *keys) -> None:
    """Build the pages this test will land on, before the clock starts.

    A page is built the first time it is shown, which in a fresh window is
    the better part of a second of widget construction. That is the cost of
    opening a page, not the cost of the step under test, so it is paid here
    - the same way the other walk files open a page before stepping into it.
    """
    for key in keys:
        window.go(key, "")
        pump(walk_app, 2)
    window.go("today", "")
    pump(walk_app, 2)


def test_search_reaches_your_notes_your_repo_and_your_log(walk_app, window,
                                                          store, curriculum):
    project = _write_some_of_your_own(store, curriculum)
    _warm(walk_app, window, "phase", "projects", "journal")

    with step(walk_app, "search", "open the box with Ctrl+K", window):
        shortcut(walk_app, window, "Ctrl+K")
        assert window.search.placeholderText() == (
            "Search the curriculum and your notes   (Ctrl+K)")

    with step(walk_app, "search", "find a phase note written minutes ago",
              window):
        window.search.setText("myceliumnote")
        pump(walk_app, 2)
        found = [hit for hit in _hits(window) if hit.kind == "note"]
        assert found, "the note is not in the index"
        window._open_result(window.results.item(0))
        pump(walk_app, 2)
        assert window.current_key == "phase"
    REC.bump("notes found by search")

    with step(walk_app, "search", "find your own project note", window):
        window.search.setText("pangolinnote")
        pump(walk_app, 2)
        assert _hits(window), "the project note is not in the index"
        window._open_result(window.results.item(0))
        pump(walk_app, 2)
        assert window.current_key == "projects"

    with step(walk_app, "search", "find a project by its repository url",
              window):
        window.search.setText("pangolinrepo")
        pump(walk_app, 2)
        found = [hit for hit in _hits(window)
                 if hit.kind == "note" and hit.target == project.id]
        assert found, "the repo url is not searchable"
        window.search.clear()
        pump(walk_app, 1)

    with step(walk_app, "search", "find a log entry and open the log",
              window):
        window.search.setText("narwhalfocus")
        pump(walk_app, 2)
        found = [hit for hit in _hits(window) if hit.kind == "log"]
        assert found, "the log entry is not in the index"
        window._open_hit(found[0])
        pump(walk_app, 2)
        assert window.current_key == "journal"
    REC.bump("log entries found by search")


# -- the popup has a keyboard ----------------------------------------------


def test_the_results_can_be_driven_without_a_mouse(walk_app, window):
    from PySide6.QtCore import Qt

    with step(walk_app, "search", "type a query", window):
        window.search.setText("")
        type_text(walk_app, window.search, "python")
        pump(walk_app, 2)
        assert window.results.count() > 3
        assert window.results.currentRow() == 0

    with step(walk_app, "search", "walk down and back up the results",
              window):
        for expected in (1, 2, 3):
            press(walk_app, window.search, Qt.Key.Key_Down)
            assert window.results.currentRow() == expected
        press(walk_app, window.search, Qt.Key.Key_Up)
        assert window.results.currentRow() == 2
    REC.bump("result rows walked with the keyboard", 4)

    with step(walk_app, "search", "page down and page up the results",
              window):
        press(walk_app, window.search, Qt.Key.Key_PageDown)
        press(walk_app, window.search, Qt.Key.Key_PageUp)
        assert window.results.currentRow() == 2

    with step(walk_app, "search", "open the selected hit with Enter", window,
              allow_dialog=True):
        selected = window.results.currentItem().data(
            Qt.ItemDataRole.UserRole)
        press(walk_app, window.search, Qt.Key.Key_Return)
        pump(walk_app, 2)
        assert window.results.isHidden()
        assert window.search.text() == ""
        assert selected is not None

    with step(walk_app, "search", "close the results with Escape", window):
        window.search.setText("python")
        pump(walk_app, 2)
        assert not window.results.isHidden()
        press(walk_app, window.search, Qt.Key.Key_Escape)
        assert window.results.isHidden()
        assert window.search.text() == "python"
        window.search.clear()
        pump(walk_app, 1)


# -- every kind of hit lands somewhere -------------------------------------


def test_a_field_and_a_certificate_open_their_own_card(walk_app, window,
                                                       curriculum):
    from operators_console.core.search import Hit

    _warm(walk_app, window, "library")
    view = window.views["library"]
    for kind, thing, tab in (("field", curriculum.fields[0], 1),
                             ("cert", curriculum.certs[0], 3)):
        with step(walk_app, "library", "open the %s %s from search"
                  % (kind, thing.id), window):
            window._open_hit(Hit(kind, thing.name, "", thing.id, ""))
            pump(walk_app, 3)
            assert window.current_key == "library"
            assert view.tabs.currentIndex() == tab
            card = view._targets[thing.id][1]
            assert card.objectName() == "FocusCard", "the card is not marked"
            assert card.isVisible()
            view._unflash()
            assert card.objectName() == "Card"
        REC.bump("library cards opened from search")


def test_a_question_is_read_rather_than_answered(walk_app, window,
                                                 curriculum):
    from operators_console.core.search import Hit
    from operators_console.ui.main_window import QuestionDialog

    question = curriculum.all_questions[0]
    window.go("today", "")
    pump(walk_app, 2)
    with step(walk_app, "search", "open a question from search", window,
              allow_dialog=True):
        window._open_hit(Hit("question", question.prompt, "", question.id,
                             "p01"))
        pump(walk_app, 2)
        assert window.current_key == "today", "search started a quiz attempt"
        assert not window.views["quiz"].busy

    with step(walk_app, "search", "read the question and close it", window):
        from PySide6.QtWidgets import QLabel
        dialog = QuestionDialog(window, question,
                                curriculum.quiz_of_question(question.id))
        dialog.show()
        pump(walk_app, 2)
        words = "\n".join(child.text()
                          for child in dialog.findChildren(QLabel))
        assert question.prompt in words
        assert question.explain in words
        click(walk_app, dialog.close_button)
        pump(walk_app, 2)
        assert dialog.isHidden(), "the Close button did not close it"
        dialog.deleteLater()
    REC.bump("questions read without an attempt")


# -- the library, filtered and marked --------------------------------------


def test_the_library_can_be_filtered_and_marked_as_read(walk_app, window,
                                                        store, curriculum):
    window.go("library", "")
    pump(walk_app, 3)
    view = window.views["library"]

    with step(walk_app, "library", "filter the library to nothing", window):
        type_text(walk_app, view.filter, "zzzznothingmatchesthis")
        pump(walk_app, 2)
        rows = [row for row in view._rows if row.tab == 0 and row.fold is None]
        assert rows and not any(row.widget.isVisible() for row in rows)
        assert "0 of" in view.filter_note.text()

    with step(walk_app, "library", "filter the library to one shelf entry",
              window):
        view.filter.setText("")
        pump(walk_app, 1)
        wanted = curriculum.shelf[0].items[0].name
        view.filter.setText(wanted)
        pump(walk_app, 2)
        shown = [row for row in view._rows
                 if row.tab == 0 and row.widget.isVisible()]
        assert shown, "the row the filter names is hidden"
        view.filter.clear()
        pump(walk_app, 2)
    REC.bump("library filters typed", 2)

    marked = 0
    for tab in (0, 1, 2):
        boxes = [(box, item_id) for box, item_id in view._reads
                 if item_id.split(":")[1] == ("shelf", "fields", "video")[tab]]
        assert boxes, "tab %d has nothing to mark as read" % tab
        with step(walk_app, "library", "mark a row on tab %d as read" % tab,
                  window):
            view.tabs.setCurrentIndex(tab)
            pump(walk_app, 2)
            box, item_id = boxes[0]
            click(walk_app, box)
            assert store.is_checked(item_id), "the tick was not stored"
            marked += 1
        with step(walk_app, "library", "take the mark on tab %d back" % tab,
                  window):
            click(walk_app, box)
            assert not store.is_checked(item_id)
    REC.bump("library rows marked as read", marked)

    with step(walk_app, "library", "undo the last read mark", window):
        box, item_id = view._reads[0]
        click(walk_app, box)
        assert store.is_checked(item_id)
        window.undo()
        pump(walk_app, 2)
        assert not store.is_checked(item_id)
        assert not box.isChecked(), "the tick did not follow the undo"


# -- the new keys ----------------------------------------------------------


def test_ctrl_zero_and_ctrl_l_both_reach_the_library(walk_app, window):
    _warm(walk_app, window, "library")
    for key in ("Ctrl+0", "Ctrl+L"):
        window.go("today", "")
        pump(walk_app, 1)
        with step(walk_app, "navigation", "press %s" % key, window):
            shortcut(walk_app, window, key)
            assert window.current_key == "library", key
        REC.bump("library shortcuts pressed")

    with step(walk_app, "navigation", "open the library from the Go menu",
              window):
        window.go("today", "")
        pump(walk_app, 1)
        trigger(walk_app, window.go_actions["library"])
        assert window.current_key == "library"


# -- the first launch ------------------------------------------------------


def test_a_first_launch_is_pointed_at_the_guide(walk_app, raw_window, store):
    from operators_console.ui.main_window import GUIDE_HINT

    with step(walk_app, "first run", "read the status bar on a first launch",
              raw_window):
        assert raw_window.status_label.text() == GUIDE_HINT
        assert store.setting("guide_pointed") is True
    REC.bump("first run hints shown")
