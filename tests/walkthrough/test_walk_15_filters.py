"""Every filter, search and sort control added in the filter round, pressed.

Ctrl+K bringing a live query back, saying "no match", and reaching the
Library shelf; the Library's per-tab counts; the Projects FIND box, its
empty state and its way back; the Progress table's SORT choice and its
clickable headings; Practice's "Where this is taught"; and the filters
coming back after a theme change.
"""
from __future__ import annotations

import pytest

from .harness import REC, click, press, pump, shortcut, step, type_text

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]

#: Steps that build a page from nothing are allowed a page's worth of time.
PAGE_DRAW = 20000


def _warm(walk_app, window, *keys) -> None:
    """Build the pages first, so a step's clock measures only the step."""
    for key in keys:
        window.go(key, "")
        pump(walk_app, 2)
    window.go("today", "")
    pump(walk_app, 2)


def _flip_theme(walk_app, window, store, theme: str) -> None:
    store.set_setting("theme", theme)
    window.ctx.refresh_palette()
    pump(walk_app, 3)


def test_ctrl_k_says_no_match_and_brings_a_query_back(walk_app, window,
                                                      curriculum):
    from PySide6.QtCore import Qt
    _warm(walk_app, window, "library")

    with step(walk_app, "search", "type a word that is nowhere", window):
        shortcut(walk_app, window, "Ctrl+K")
        type_text(walk_app, window.search, "zzqqxxnothing")
        assert window.results.isVisible()
        assert window.results.item(0).text().startswith("No match for")
        assert window.search_hits() == []
        press(walk_app, window.search, Qt.Key.Key_Return)
        assert window.search.text() == "zzqqxxnothing"   # nothing opened

    with step(walk_app, "search", "Escape, then Ctrl+K again", window):
        press(walk_app, window.search, Qt.Key.Key_Escape)
        assert window.results.isHidden()
        window.search.setText("decorator")
        pump(walk_app, 2)
        window.results.hide()
        shortcut(walk_app, window, "Ctrl+K")
        assert window.results.isVisible() and window.search_hits()

    link = curriculum.shelf[0].items[-1]
    with step(walk_app, "search", "open a shelf book from Ctrl+K", window,
              budget=PAGE_DRAW):
        window.search.setText(link.name)
        pump(walk_app, 2)
        hits = window.search_hits()
        row = next(i for i, hit in enumerate(hits)
                   if hit.kind == "shelf" and hit.title == link.name)
        window.results.setCurrentRow(row)
        press(walk_app, window.search, Qt.Key.Key_Return)
        pump(walk_app, 3)
        assert window.current_key == "library"
        view = window.views["library"]
        assert view.tabs.currentIndex() == 0
    REC.bump("shelf hits opened")


def test_the_library_says_where_the_other_matches_are(walk_app, window,
                                                      curriculum):
    window.go("library", "")
    pump(walk_app, 3)
    view = window.views["library"]
    name = curriculum.channels[0].items[0].name

    with step(walk_app, "library", "filter for a channel on the Shelf tab",
              window):
        view.tabs.setCurrentIndex(0)
        type_text(walk_app, view.filter, name)
        pump(walk_app, 2)
        assert "more on Video" in view.filter_note.text()
        assert view.tabs.tabText(2).startswith("Video (")

    with step(walk_app, "library", "follow the count to the Video tab",
              window):
        view.tabs.setCurrentIndex(2)
        pump(walk_app, 2)
        assert not view.filter_note.text().startswith("0 of")

    with step(walk_app, "library", "clear the filter", window):
        view.filter.clear()
        pump(walk_app, 2)
        assert view.tabs.tabText(2) == "Video"
        assert view.filter_note.text() == ""
    REC.bump("library tab counts read", 4)


def test_projects_find_empty_state_and_way_back(walk_app, window,
                                                curriculum):
    window.go("projects", "")
    pump(walk_app, 3)
    view = window.views["projects"]

    with step(walk_app, "projects", "SHOW Shipped with nothing shipped",
              window):
        view.filter.setCurrentText("Shipped")
        pump(walk_app, 2)
        assert view.empty_title.text() == "Nothing is shipped yet."
        assert view._empty.isVisible()

    with step(walk_app, "projects", "press Show every project", window):
        click(walk_app, view.show_all)
        assert view.filter.currentText() == "All"
        assert not view._empty.isVisible()

    with step(walk_app, "projects", "type in FIND", window):
        word = curriculum.projects[0].title.split()[-1]
        type_text(walk_app, view.find, word)
        assert not view.card_for(curriculum.projects[0].id).isHidden()
        view.find.setText("zzqqxx")
        pump(walk_app, 2)
        assert view.empty_title.text().startswith("No project matches")
        click(walk_app, view.show_all)
        assert view.find.text() == ""
    REC.bump("projects filters pressed", 3)


def test_the_progress_table_sorts(walk_app, window):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    from operators_console.ui.views.stats import SORT_ROLE
    window.go("stats", "")
    pump(walk_app, 3)
    view = window.views["stats"]
    header = view.table.horizontalHeader()

    with step(walk_app, "stats", "click the Checks heading", window):
        spot = QPoint(header.sectionViewportPosition(1) + 6,
                      header.height() // 2)
        QTest.mouseClick(header.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, spot)
        pump(walk_app, 2)
        values = [view.table.item(r, 1).data(SORT_ROLE)
                  for r in range(view.table.rowCount())]
        assert values == sorted(values)
        assert view.sort_by.currentData() == 1

    with step(walk_app, "stats", "pick every SORT choice", window):
        for index in range(view.sort_by.count()):
            view.sort_by.setCurrentIndex(index)
            pump(walk_app, 1)
            column = view.sort_by.currentData()
            values = [view.table.item(r, column).data(SORT_ROLE)
                      for r in range(view.table.rowCount())]
            assert values == sorted(values), view.sort_by.currentText()
        view.sort_by.setCurrentIndex(0)
        pump(walk_app, 1)
    REC.bump("sort choices tried", view.sort_by.count())


def test_where_this_is_taught_after_a_failed_run(walk_app, window,
                                                 curriculum):
    from operators_console.core.runner import RunResult
    window.go("practice", "")
    pump(walk_app, 3)
    view = window.views["practice"]
    exercise = curriculum.exercises[0]

    with step(walk_app, "practice", "fail a run, then Where this is taught",
              window, budget=PAGE_DRAW):
        assert view._select_id(exercise.id)
        view._on_result(exercise.id, RunResult(ok=False, error="NameError"))
        pump(walk_app, 2)
        assert view.taught_button is not None
        click(walk_app, view.taught_button)
        assert window.current_key == "phase"
        assert window.views["phase"].resume_target() == exercise.phase
    REC.bump("where-taught presses")


def test_the_filters_survive_a_theme_change(walk_app, window, store):
    _warm(walk_app, window, "practice", "library", "projects", "journal")
    practice = window.views["practice"]
    library = window.views["library"]
    projects = window.views["projects"]

    with step(walk_app, "settings", "set filters, then change the theme",
              window, budget=PAGE_DRAW):
        window.go("practice", "")
        pump(walk_app, 2)
        practice.search.setText("loop")
        practice.status_filter.setCurrentText("Not passed")
        window.go("library", "")
        pump(walk_app, 2)
        library.filter.setText("python")
        window.go("projects", "")
        pump(walk_app, 2)
        projects.filter.setCurrentText("In progress")
        window.go("today", "")
        pump(walk_app, 2)
        _flip_theme(walk_app, window, store, "dark")
        assert not practice._built and not library._built

    with step(walk_app, "settings", "come back to each page", window,
              budget=PAGE_DRAW):
        window.go("practice", "")
        pump(walk_app, 2)
        assert practice.search.text() == "loop"
        assert practice.status_filter.currentText() == "Not passed"
        window.go("library", "")
        pump(walk_app, 3)
        assert library.filter.text() == "python"
        window.go("projects", "")
        pump(walk_app, 2)
        assert projects.filter.currentText() == "In progress"
        _flip_theme(walk_app, window, store, "light")
    REC.bump("filters kept across a theme change", 3)
