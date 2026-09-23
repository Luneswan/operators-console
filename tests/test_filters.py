"""Every filter, search and sort control, on the real shipped content.

One matcher (core/textmatch) now sits behind every box, so the first half
checks it once at the function level - case, spacing, punctuation, regular
expression characters - against each page's own helper. The second half
drives each page: filter combinations, counts, empty states, clearing, and
surviving a theme or text-size change.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest
from PySide6.QtCore import Qt

from conftest import pump
from operators_console.core import textmatch
from operators_console.core.runner import RunResult

# ---------------------------------------------------------------------------
# 1. the matcher itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("query, text, expected", [
    ("", "anything at all", True),
    ("   ", "anything at all", True),
    ("DECORATORS", "Decorators and closures", True),
    ("  decorators   closures ", "Decorators and closures", True),
    ("closures decorators", "Decorators and closures", True),     # any order
    ("decorators generators", "Decorators and closures", False),  # every word
    ("functions -> calculator", "functions → calculator", True),
    ("a - b", "a – b", True),
    ("a-b", "a—b", True),
    ("x-1", "x−1", True),
    ("cafe", "café", True),
    ("don't", "don’t", True),
    ("strasse", "Straße", True),
    ("non breaking", "non breaking", True),
    ("(", "print(x)", True),
    ("[0]", "items[0]", True),
    (".*", "a.*b", True),
    (".*", "abc", False),              # not a regular expression
    ("c++", "C++ interop", True),
    ("\\d", "no digits here", False),
    ("a|b", "a", False),
    ("?", "why?", True),
])
def test_the_one_matcher(query, text, expected):
    assert textmatch.matches(query, text) is expected


def test_a_word_never_matches_across_two_fields():
    # "ab" is in neither field; joined with a space it would be in both.
    assert not textmatch.matches("ab", "xa", "by")
    assert textmatch.matches("xa by", "xa", "by")


def test_slug_is_the_library_one():
    from operators_console.ui.views.library import slug
    for name in ("Python docs", "Fluent Python, 2nd ed.", "  --Odd--  "):
        assert slug(name) == textmatch.slug(name)
    assert textmatch.slug("Fluent Python, 2nd ed.") == "fluent-python-2nd-ed"


class _Exercise:
    def __init__(self, title, topic="", ex_id="p01.001", prompt=""):
        self.title, self.topic, self.id, self.prompt = (title, topic, ex_id,
                                                        prompt)


def _journal_row(**fields):
    row = {"focus": "", "built": "", "stuck": "", "next_up": ""}
    row.update(fields)
    return row


@pytest.mark.parametrize("query, expected", [
    ("SOCKETS", True), ("  sockets  ", True), ("echo   sockets", True),
    ("server - echo", True), ("->", True), ("(", False), ("[a-z]", False),
    ("sockets asyncio", False),
])
def test_practice_and_journal_agree_with_the_matcher(query, expected):
    from operators_console.ui.views.journal import _matches as journal
    from operators_console.ui.views.practice import _matches as practice
    title = "Echo server – sockets → bytes"
    assert practice(_Exercise(title), query) is expected
    assert journal(_journal_row(focus=title), query) is expected
    assert textmatch.matches(query, title) is expected


# ---------------------------------------------------------------------------
# 2. Ctrl+K
# ---------------------------------------------------------------------------


def _index(curriculum, store=None):
    from operators_console.core.search import SearchIndex
    return SearchIndex(curriculum, store)


def test_every_shelf_and_video_name_is_findable(curriculum):
    index = _index(curriculum)
    missing = []
    for kind, groups in (("shelf", curriculum.shelf),
                         ("video", curriculum.channels)):
        for group in groups:
            for item in group.items:
                hits = index.search(item.name)
                if not any(hit.kind == kind and hit.title == item.name
                           for hit in hits):
                    missing.append(item.name)
    assert not missing, missing


def test_plain_ascii_finds_typographic_punctuation(curriculum):
    index = _index(curriculum)
    # Titles written with an arrow and an em dash, typed the plain way.
    arrow = next(item for phase in curriculum.phases
                 for section in phase.sections for item in section.items
                 if "→" in item.text)
    before, after = arrow.text.split("→", 1)
    query = "%s -> %s" % (before.split()[-1], after.split()[0])
    assert any(hit.target == arrow.id for hit in index.search(query)), query


def test_extra_spaces_and_case_do_not_change_the_hits(curriculum):
    index = _index(curriculum)
    plain = [hit.target for hit in index.search("list comprehension")]
    assert plain
    assert [hit.target for hit in
            index.search("  LIST    Comprehension  ")] == plain


@pytest.mark.parametrize("query", ["(", "[", "*", ".*", "\\", "a|b", "^$"])
def test_metacharacters_are_plain_text_in_search(curriculum, query):
    assert isinstance(_index(curriculum).search(query), list)


def test_a_shelf_hit_opens_its_own_card(qt_app, window, curriculum):
    group = next(g for g in curriculum.shelf if len(g.items) > 1)
    link = group.items[-1]              # the last is usually folded away
    window.search.setText(link.name)
    pump(qt_app)
    hit = next(hit for hit in window.search_hits()
               if hit.kind == "shelf" and hit.title == link.name)
    window._open_hit(hit)
    pump(qt_app, 3)
    view = window.views["library"]
    assert window.current_key == "library"
    tab, card, fold, spot = view._targets[hit.target]
    assert view.tabs.currentIndex() == tab == 0
    assert card.objectName() == "FocusCard"
    if fold is not None:
        assert fold.is_open, "the fold hiding the line was not opened"
    assert spot.isVisible()


def test_a_video_hit_opens_the_video_tab(qt_app, window, curriculum):
    item = curriculum.channels[0].items[0]
    window.search.setText(item.name)
    pump(qt_app)
    hit = next(hit for hit in window.search_hits() if hit.kind == "video")
    window._open_hit(hit)
    pump(qt_app, 3)
    view = window.views["library"]
    assert view.tabs.currentIndex() == 2
    assert view._targets[hit.target][1].objectName() == "FocusCard"


def test_no_match_says_so_and_cannot_be_opened(qt_app, window):
    window.search.setText("zzqqxxnothing")
    pump(qt_app)
    assert window.results.isVisible()
    assert window.results.count() == 1
    item = window.results.item(0)
    assert item.text().startswith('No match for "zzqqxxnothing"')
    assert item.flags() == Qt.ItemFlag.NoItemFlags
    assert window.search_hits() == []
    window._open_selected()             # Enter on it does nothing
    window._open_first_result()
    pump(qt_app)
    assert window.search.text() == "zzqqxxnothing"


def test_a_one_letter_query_stays_quiet(qt_app, window):
    window.search.setText("d")
    pump(qt_app)
    assert window.results.isHidden()


def test_ctrl_k_brings_a_live_query_back(qt_app, window):
    window.search.setText("decorator")
    pump(qt_app)
    assert window.results.isVisible()
    window.results.hide()                       # Escape, or a page change
    window._focus_search()
    pump(qt_app)
    assert window.results.isVisible()
    assert window.search_hits()


# ---------------------------------------------------------------------------
# 3. Practice
# ---------------------------------------------------------------------------


def _practice(qt_app, window):
    window.go("practice", "")
    pump(qt_app)
    return window.views["practice"]


def _listed(view) -> list:
    return [view.list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(view.list.count())]


def test_practice_filters_combine(qt_app, window, curriculum, store):
    view = _practice(qt_app, window)
    total = len(curriculum.exercises)
    assert view.list.count() == total
    phase = curriculum.exercises[0].phase
    in_phase = [e for e in curriculum.exercises if e.phase == phase]
    passed = in_phase[0]
    store.record_exercise_run(passed.id, passed.starter, True)

    view.phase_filter.setCurrentIndex(view.phase_filter.findData(phase))
    pump(qt_app)
    assert _listed(view) == [e.id for e in in_phase]

    view.status_filter.setCurrentText("Passed")
    pump(qt_app)
    assert _listed(view) == [passed.id]

    view.status_filter.setCurrentText("Not passed")
    level = in_phase[1].difficulty
    view.difficulty_filter.setCurrentIndex(
        view.difficulty_filter.findData(level))
    pump(qt_app)
    want = [e.id for e in in_phase
            if e.id != passed.id and e.difficulty == level]
    assert _listed(view) == want

    word = in_phase[1].title.split()[0].upper()
    view.search.setText("  %s  " % word)
    pump(qt_app)
    assert _listed(view) == [e.id for e in in_phase
                             if e.id in want
                             and textmatch.matches(word, e.title, e.topic,
                                                   e.id, e.prompt)]
    assert in_phase[1].id in _listed(view)

    view._clear_filters()
    view.phase_filter.setCurrentIndex(0)
    pump(qt_app)
    assert view.list.count() == total
    assert "shown" not in view.counter.text()


def test_practice_filters_survive_a_theme_change(qt_app, window, store,
                                                 curriculum):
    view = _practice(qt_app, window)
    exercise = curriculum.exercises[5]
    view.phase_filter.setCurrentIndex(
        view.phase_filter.findData(exercise.phase))
    view.difficulty_filter.setCurrentIndex(
        view.difficulty_filter.findData(exercise.difficulty))
    view.status_filter.setCurrentText("Not passed")
    view.search.setText(exercise.title.split()[0])
    pump(qt_app)
    assert view._select_id(exercise.id)
    pump(qt_app)
    before = view.save_state()
    listed = _listed(view)

    window.go("today", "")
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    assert not view._built

    window.go("practice", "")
    pump(qt_app)
    assert view.search.text() == before["search"]
    assert view.phase_filter.currentData() == exercise.phase
    assert view.status_filter.currentText() == "Not passed"
    assert view.difficulty_filter.currentData() == exercise.difficulty
    assert _listed(view) == listed
    assert view.current is not None and view.current.id == exercise.id


def test_a_text_size_change_keeps_the_filters_too(qt_app, window, store):
    view = _practice(qt_app, window)
    view.search.setText("loop")
    pump(qt_app)
    window.go("today", "")
    store.set_setting("font_scale", 1.15)
    window.apply_theme()
    pump(qt_app)
    assert not view._built
    window.go("practice", "")
    pump(qt_app)
    assert view.search.text() == "loop"
    store.set_setting("font_scale", 1.0)
    window.apply_theme()


def test_a_target_still_beats_a_restored_filter(qt_app, window, store,
                                                curriculum):
    view = _practice(qt_app, window)
    view.search.setText("zzqqxx")
    pump(qt_app)
    window.go("today", "")
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    target = curriculum.exercises[3]
    window.go("practice", target.id)
    pump(qt_app)
    assert view.current is not None and view.current.id == target.id


def test_a_failed_run_offers_where_it_is_taught(qt_app, window, curriculum):
    view = _practice(qt_app, window)
    exercise = curriculum.exercises[0]
    assert view._select_id(exercise.id)
    pump(qt_app)
    view._on_result(exercise.id, RunResult(ok=True))
    pump(qt_app)
    assert view.taught_button is None, "a pass needs no way back"

    view._on_result(exercise.id, RunResult(ok=False, error="NameError: x"))
    pump(qt_app)
    assert view.taught_button is not None
    assert view.taught_button.text() == "Where this is taught"
    assert view.taught_button.property("kind") == "quiet"
    assert view.taught_button.focusPolicy() != Qt.FocusPolicy.NoFocus
    view.taught_button.click()
    pump(qt_app)
    assert window.current_key == "phase"
    assert window.views["phase"].resume_target() == exercise.phase


# ---------------------------------------------------------------------------
# 4. Journal
# ---------------------------------------------------------------------------


def _day(back: int) -> str:
    return (date.today() - timedelta(days=back)).isoformat()


def _journal(qt_app, window):
    window.go("journal", "")
    pump(qt_app)
    return window.views["journal"]


def test_the_journal_counter_says_how_big_the_log_is(qt_app, window, store):
    for back in range(20):
        store.add_log(_day(back), "entry %d" % back, 1.0,
                      "sockets" if back < 2 else "", "", "")
    view = _journal(qt_app, window)
    assert view.counter.text() == "20 entries, 20 shown"
    view.filter.setText("SOCKETS")
    pump(qt_app)
    assert view.counter.text() == "2 of 20 entries match, 2 shown"
    view.filter.setText("  ")
    pump(qt_app)
    assert view.counter.text() == "20 entries, 20 shown"


def test_the_journal_text_and_range_combine(qt_app, window, store):
    store.add_log(_day(0), "echo – sockets", 1.0, "", "", "")
    store.add_log(_day(200), "sockets, long ago", 1.0, "", "", "")
    store.add_log(_day(0), "asyncio", 1.0, "", "", "")
    view = _journal(qt_app, window)
    view.filter.setText("sockets")
    pump(qt_app)
    assert view.counter.text() == "2 of 3 entries match, 2 shown"
    view.range.setCurrentIndex(1)                   # last 3 months
    pump(qt_app)
    assert view.counter.text() == "1 of 3 entries match, 1 shown"
    view.filter.setText("echo - sockets")           # a hyphen for the dash
    pump(qt_app)
    assert view.counter.text() == "1 of 3 entries match, 1 shown"
    view.filter.clear()
    view.range.setCurrentIndex(2)
    pump(qt_app)
    assert view.counter.text() == "3 entries, 3 shown"


def test_the_journal_filter_survives_a_theme_change(qt_app, window, store):
    store.add_log(_day(0), "sockets", 1.0, "", "", "")
    view = _journal(qt_app, window)
    view.filter.setText("sockets")
    view.range.setCurrentIndex(0)
    pump(qt_app)
    window.go("today", "")
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    window.go("journal", "")
    pump(qt_app)
    assert view.filter.text() == "sockets"
    assert view.range.currentIndex() == 0


# ---------------------------------------------------------------------------
# 5. Library
# ---------------------------------------------------------------------------


def _library(qt_app, window):
    window.go("library", "")
    pump(qt_app, 3)
    return window.views["library"]


def test_the_library_counts_every_tab(qt_app, window, curriculum):
    view = _library(qt_app, window)
    name = curriculum.channels[0].items[0].name     # only on the Video tab
    view.tabs.setCurrentIndex(0)
    view.filter.setText(name)
    pump(qt_app, 2)
    counts = view.tab_matches()
    assert counts[2] >= 1
    note = view.filter_note.text()
    shelf_rows = sum(1 for row in view._rows if row.tab == 0)
    assert note.startswith("%d of %d here" % (counts[0], shelf_rows))
    assert "more on Video" in note, note
    assert view.tabs.tabText(2) == "Video (%d)" % counts[2]
    view.filter.clear()
    pump(qt_app, 2)
    assert view.filter_note.text() == ""
    assert [view.tabs.tabText(i) for i in range(4)] == [
        "Shelf", "Fields of work", "Video", "Certificates"]


def test_nothing_anywhere_is_said_plainly(qt_app, window):
    view = _library(qt_app, window)
    view.filter.setText("zzqqxxnothing")
    pump(qt_app, 2)
    assert "none on the other tabs either" in view.filter_note.text()


def test_clearing_closes_exactly_the_folds_the_filter_opened(qt_app, window):
    view = _library(qt_app, window)
    folds = []
    for row in view._rows:
        if row.fold is not None and row.fold not in folds:
            folds.append(row.fold)
    assert len(folds) >= 2
    by_hand, forced = folds[0], folds[1]
    for fold in folds:
        fold.set_open(False, animate=False)
    by_hand.set_open(True, animate=False)
    target = next(row for row in view._rows if row.fold is forced)
    words = target.text.split("\n")[0]
    view.filter.setText(words)
    pump(qt_app, 2)
    assert forced.is_open
    view.filter.clear()
    pump(qt_app, 2)
    assert not forced.is_open, "the fold the filter opened stayed open"
    assert by_hand.is_open, "a fold opened by hand was closed"
    assert not any(row.widget.isHidden() for row in view._rows), (
        "clearing the filter left a row hidden")


def test_the_library_filter_survives_a_theme_change(qt_app, window, store):
    view = _library(qt_app, window)
    view.tabs.setCurrentIndex(2)
    view.filter.setText("python")
    pump(qt_app, 2)
    window.go("today", "")
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    assert not view._built
    view = _library(qt_app, window)
    assert view.filter.text() == "python"
    assert view.tabs.currentIndex() == 2
    assert view.filter_note.text().startswith(
        "%d of" % view.tab_matches()[2])


# ---------------------------------------------------------------------------
# 6. Projects
# ---------------------------------------------------------------------------


def _projects(qt_app, window):
    window.go("projects", "")
    pump(qt_app)
    return window.views["projects"]


def _visible(view, curriculum) -> list:
    return [p.id for p in curriculum.projects
            if not view.card_for(p.id).isHidden()]


def test_each_projects_mode_keeps_the_right_cards(qt_app, window,
                                                  curriculum):
    projects = curriculum.projects
    window.ctx.set_project_status(projects[0].id, "shipped")
    window.ctx.set_project_status(projects[1].id, "in-progress")
    window.ctx.set_project_status(projects[2].id, "in-progress")
    view = _projects(qt_app, window)
    expected = {
        "All": [p.id for p in projects],
        "Shipped": [projects[0].id],
        "In progress": [projects[1].id, projects[2].id],
        "Not started": [p.id for p in projects[3:]],
    }
    for mode, ids in expected.items():
        view.filter.setCurrentText(mode)
        pump(qt_app)
        assert _visible(view, curriculum) == ids, mode
        assert view.counter.text().startswith("%d shown" % len(ids))
        assert view._empty is None or view._empty.isHidden()


def test_projects_empty_state_names_the_mode(qt_app, window, curriculum):
    view = _projects(qt_app, window)
    view.filter.setCurrentText("Shipped")
    pump(qt_app)
    assert _visible(view, curriculum) == []
    assert view._empty is not None and not view._empty.isHidden()
    assert view.empty_title.text() == "Nothing is shipped yet."
    assert ("all %d" % len(curriculum.projects)) in view.empty_text.text()
    view.show_all.click()
    pump(qt_app)
    assert view.filter.currentText() == "All"
    assert view._empty.isHidden()
    assert len(_visible(view, curriculum)) == len(curriculum.projects)


def test_projects_find_box_and_mode_combine(qt_app, window, curriculum):
    view = _projects(qt_app, window)
    project = curriculum.projects[4]
    window.ctx.set_project_status(project.id, "in-progress")
    view.refresh()
    word = project.title.split()[-1]
    view.find.setText("  %s " % word.upper())
    pump(qt_app)
    shown = _visible(view, curriculum)
    assert project.id in shown
    view.filter.setCurrentText("In progress")
    pump(qt_app)
    assert _visible(view, curriculum) == [project.id]
    view.find.setText("zzqqxx")
    pump(qt_app)
    assert view.empty_title.text() == 'No in progress project matches "zzqqxx".'
    view.show_all.click()
    pump(qt_app)
    assert view.find.text() == ""
    assert len(_visible(view, curriculum)) == len(curriculum.projects)


def test_the_outside_track_fold_counts_what_the_filter_kept(
        qt_app, window, store, curriculum):
    store.set_setting("track", "beginner")
    view = _projects(qt_app, window)
    outside = [p for p in curriculum.projects
               if not window.ctx.progress.is_in_plan(p.phase)]
    assert outside and view._extra is not None
    assert view._extra.count == len(outside)
    view.filter.setCurrentText("Shipped")
    pump(qt_app)
    assert view._extra.isHidden(), "a fold that holds nothing is still shown"
    window.ctx.set_project_status(outside[0].id, "shipped")
    view.refresh()
    pump(qt_app)
    assert not view._extra.isHidden()
    assert view._extra.count == 1
    assert view._extra.caption.text().startswith("1 more")
    view.filter.setCurrentText("All")
    pump(qt_app)
    assert view._extra.count == len(outside)


def test_projects_filters_survive_a_theme_change(qt_app, window, store):
    view = _projects(qt_app, window)
    view.filter.setCurrentText("In progress")
    view.find.setText("cli")
    pump(qt_app)
    window.go("today", "")
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    view = _projects(qt_app, window)
    assert view.filter.currentText() == "In progress"
    assert view.find.text() == "cli"


# ---------------------------------------------------------------------------
# 7. Progress: the phase table sorts by number
# ---------------------------------------------------------------------------


def _stats(qt_app, window):
    window.go("stats", "")
    pump(qt_app)
    return window.views["stats"]


def _column(view, column) -> list:
    from operators_console.ui.views.stats import SORT_ROLE
    return [view.table.item(row, column).data(SORT_ROLE)
            for row in range(view.table.rowCount())]


def test_the_phase_table_sorts_numerically(qt_app, window, store,
                                           curriculum):
    # Enough ticks in the first phase that "10/.." against "9/.." would
    # sort the wrong way as text.
    first = curriculum.phases[0]
    items = [item for section in first.sections for item in section.items]
    for item in items[:10]:
        store.set_checked(item.id, True)
    view = _stats(qt_app, window)
    course = [view.table.item(r, 0).text()
              for r in range(view.table.rowCount())]
    assert view.table.rowCount() > 3

    view.table.horizontalHeader().sectionClicked.emit(1)
    pump(qt_app)
    values = _column(view, 1)
    assert values == sorted(values)
    assert view.sort_by.currentData() == 1

    view.table.horizontalHeader().sectionClicked.emit(1)   # again: reversed
    pump(qt_app)
    values = _column(view, 1)
    assert values == sorted(values, reverse=True)

    view.sort_by.setCurrentIndex(view.sort_by.findData(0))
    pump(qt_app)
    assert [view.table.item(r, 0).text()
            for r in range(view.table.rowCount())] == course

    # A sorted row still opens its own phase.
    view.sort_by.setCurrentIndex(view.sort_by.findData(2))
    pump(qt_app)
    pid = view.table.item(0, 0).data(Qt.ItemDataRole.UserRole)
    view._open_row(0)
    pump(qt_app)
    assert window.views["phase"].resume_target() == pid
