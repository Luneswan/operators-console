"""The gaps this round closed: search over your own writing, a keyboard in
the results popup, hits that land on the thing they found, a library you can
mark and filter, and feedback a screen reader can hear.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible
from PySide6.QtTest import QTest

from conftest import pump

# ---------------------------------------------------------------------------
# 1. the index reaches what the learner wrote
# ---------------------------------------------------------------------------


def _index(curriculum, store):
    from operators_console.core.search import SearchIndex
    return SearchIndex(curriculum, store)


def _kinds(hits):
    return {hit.kind for hit in hits}


def test_a_note_typed_after_the_index_was_built_is_found(curriculum, store):
    index = _index(curriculum, store)
    assert index.search("myceliumnote") == []
    store.set_note("phase:p01", "myceliumnote: decorators finally clicked")
    hits = index.search("myceliumnote")
    assert hits, "a note written a minute ago is not findable"
    hit = hits[0]
    assert hit.kind == "note"
    assert hit.target == "p01" and hit.phase == "p01"
    phase = curriculum.phase("p01")
    assert hit.context == "%s %s" % (phase.num, phase.name)
    assert hit.title.startswith("myceliumnote")


def test_an_edited_note_replaces_what_it_said_before(curriculum, store):
    index = _index(curriculum, store)
    store.set_note("phase:p02", "aardvarkone")
    assert index.search("aardvarkone")
    store.set_note("phase:p02", "aardvarktwo")
    assert index.search("aardvarkone") == []
    assert index.search("aardvarktwo")


def test_a_deleted_note_stops_being_found(curriculum, store):
    index = _index(curriculum, store)
    store.set_note("phase:p03", "quokkaquokka")
    assert index.search("quokkaquokka")
    store.set_note("phase:p03", "")
    assert index.search("quokkaquokka") == []


def test_a_project_note_and_its_repo_url_are_both_found(curriculum, store):
    project = curriculum.projects[0]
    index = _index(curriculum, store)
    store.set_project(project.id, notes="pangolinnote about the rubric",
                      repo_url="https://example.invalid/pangolinrepo")
    for query in ("pangolinnote", "pangolinrepo"):
        hits = index.search(query)
        assert hits, query
        assert hits[0].kind == "note"
        assert hits[0].target == project.id
        assert hits[0].phase == project.phase


def test_a_log_entry_is_found_by_every_field_it_holds(curriculum, store):
    index = _index(curriculum, store)
    store.add_log("2026-09-23", "narwhalfocus", 2.0, "narwhalbuilt",
                  "narwhalstuck", "narwhalnext")
    for query in ("narwhalfocus", "narwhalbuilt", "narwhalstuck",
                  "narwhalnext"):
        hits = [h for h in index.search(query) if h.kind == "log"]
        assert hits, query
        assert hits[0].title.startswith("2026-09-23")
        assert "narwhalbuilt" in hits[0].context


def test_the_shipped_index_still_holds_only_curriculum_entries(curriculum,
                                                               store):
    """`entries` is what the content tests walk; the store lives beside it."""
    index = _index(curriculum, store)
    store.set_note("phase:p01", "a note of my own")
    store.add_log("2026-09-23", "focus", 1.0, "built", "stuck", "next")
    index.search("note")            # fills the live half
    assert {hit.kind for _hay, hit in index.entries}.isdisjoint({"note",
                                                                 "log"})
    assert _kinds(hit for _h, hit in index.live_entries()) <= {"note", "log"}


def test_your_own_words_come_before_a_line_that_mentions_them(curriculum,
                                                              store):
    """A note about a common word must not sink under a thousand others."""
    index = _index(curriculum, store)
    assert index.search("decorator")[0].kind != "note"
    store.set_note("phase:p01", "a decorator is a function that wraps one")
    top = index.search("decorator")[0]
    assert top.kind == "note" or index.search("decorator")[1].kind == "note"


def test_an_index_without_a_store_searches_the_curriculum_alone(curriculum):
    from operators_console.core.search import SearchIndex
    index = SearchIndex(curriculum)
    assert index.live_entries() == []
    assert index.search("decorator")


def test_a_closed_store_costs_the_curriculum_nothing(curriculum, store):
    index = _index(curriculum, store)
    store.set_note("phase:p01", "somethingwritten")
    assert index.search("somethingwritten")
    store.close()
    assert index.live_entries() == []
    assert index.search("decorator"), "the shipped half must survive"


# ---------------------------------------------------------------------------
# 2. the results popup has a keyboard
# ---------------------------------------------------------------------------


def test_the_placeholder_says_notes_are_searched_too(qt_app, window):
    assert window.search.placeholderText() == (
        "Search the curriculum and your notes   (Ctrl+K)")


def test_down_and_up_move_the_selection(qt_app, window):
    window.search.setText("python")
    pump(qt_app)
    assert window.results.count() > 2
    assert window.results.currentRow() == 0
    QTest.keyClick(window.search, Qt.Key.Key_Down)
    pump(qt_app)
    assert window.results.currentRow() == 1
    QTest.keyClick(window.search, Qt.Key.Key_Down)
    pump(qt_app)
    assert window.results.currentRow() == 2
    QTest.keyClick(window.search, Qt.Key.Key_Up)
    pump(qt_app)
    assert window.results.currentRow() == 1
    # And it wraps rather than sticking at the top.
    QTest.keyClick(window.search, Qt.Key.Key_Up)
    QTest.keyClick(window.search, Qt.Key.Key_Up)
    pump(qt_app)
    assert window.results.currentRow() == window.results.count() - 1


def test_enter_opens_the_selected_hit_not_always_the_first(qt_app, window):
    window.search.setText("python")
    pump(qt_app)
    QTest.keyClick(window.search, Qt.Key.Key_Down)
    pump(qt_app)
    wanted = window.results.currentItem().data(Qt.ItemDataRole.UserRole)
    opened = []
    window._open_hit = lambda hit: opened.append(hit)
    QTest.keyClick(window.search, Qt.Key.Key_Return)
    pump(qt_app)
    assert opened and opened[0] is wanted
    assert window.results.isHidden() and window.search.text() == ""


def test_escape_closes_the_popup_and_keeps_the_query(qt_app, window):
    window.search.setText("python")
    pump(qt_app)
    assert not window.results.isHidden()
    QTest.keyClick(window.search, Qt.Key.Key_Escape)
    pump(qt_app)
    assert window.results.isHidden()
    assert window.search.text() == "python"


def test_typing_puts_the_selection_back_on_the_first_hit(qt_app, window):
    window.search.setText("python")
    pump(qt_app)
    QTest.keyClick(window.search, Qt.Key.Key_Down)
    pump(qt_app)
    window.search.setText("python o")
    pump(qt_app)
    assert window.results.currentRow() == 0


# ---------------------------------------------------------------------------
# 3. every kind of hit lands somewhere useful
# ---------------------------------------------------------------------------


def _hit(kind, target, phase=""):
    from operators_console.core.search import Hit
    return Hit(kind, "title", "context", target, phase)


def test_a_field_hit_opens_its_own_card_in_the_library(qt_app, window,
                                                       curriculum):
    field = curriculum.fields[-1]
    window._open_hit(_hit("field", field.id))
    pump(qt_app, 3)
    view = window.views["library"]
    assert window.current_key == "library"
    assert view.tabs.currentIndex() == 1
    card = view._targets[field.id][1]
    assert card.objectName() == "FocusCard", "the card was not marked"
    view._unflash()
    assert card.objectName() == "Card"


def test_a_certificate_hit_opens_its_own_card(qt_app, window, curriculum):
    cert = curriculum.certs[-1]
    window._open_hit(_hit("cert", cert.id))
    pump(qt_app, 3)
    view = window.views["library"]
    assert view.tabs.currentIndex() == 3
    assert view._targets[cert.id][1].objectName() == "FocusCard"
    assert view.resume_target() == cert.id


def test_a_question_hit_reads_the_question_instead_of_starting_a_quiz(
        qt_app, window, curriculum, monkeypatch):
    from operators_console.ui import main_window as mw
    question = curriculum.all_questions[0]
    seen = []
    monkeypatch.setattr(mw.QuestionDialog, "exec",
                        lambda self: seen.append(self) or 0)
    window.go("today", "")
    window._open_hit(_hit("question", question.id, "p01"))
    pump(qt_app, 2)
    assert seen, "no dialog was opened"
    dialog = seen[0]
    assert question.prompt in _text_of(dialog)
    assert question.explain in _text_of(dialog)
    assert question.choices[question.correct] in _text_of(dialog)
    assert window.current_key == "today", "search started a quiz attempt"
    assert not window.views["quiz"].busy


def test_the_question_dialog_closes_on_its_own_button(qt_app, window,
                                                      curriculum):
    from operators_console.ui.main_window import QuestionDialog
    question = curriculum.all_questions[1]
    dialog = QuestionDialog(window, question,
                            curriculum.quiz_of_question(question.id))
    dialog.show()
    pump(qt_app)
    dialog.close_button.click()
    pump(qt_app)
    assert dialog.result() == int(QuestionDialog.DialogCode.Accepted)
    dialog.deleteLater()


def _text_of(widget) -> str:
    from PySide6.QtWidgets import QLabel
    return "\n".join(child.text() for child in widget.findChildren(QLabel))


def test_a_phase_note_hit_opens_its_phase(qt_app, window, store):
    store.set_note("phase:p04", "a line of my own")
    window.search.setText("a line of my own")
    pump(qt_app, 2)
    hits = [window.results.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(window.results.count())]
    notes = [hit for hit in hits if hit.kind == "note"]
    assert notes, [hit.kind for hit in hits]
    window._open_hit(notes[0])
    pump(qt_app, 2)
    assert window.current_key == "phase"
    assert window.views["phase"].current_id == "p04"


def test_a_project_note_hit_opens_the_projects_page(qt_app, window, store,
                                                    curriculum):
    project = curriculum.projects[0]
    store.set_project(project.id, notes="wombatnote")
    window._open_hit(_hit("note", project.id, project.phase))
    pump(qt_app, 2)
    assert window.current_key == "projects"


def test_a_log_hit_opens_the_journal(qt_app, window, store):
    store.add_log("2026-09-23", "asyncio", 1.5, "a server", "nothing",
                  "tests")
    window._open_hit(_hit("log", "1"))
    pump(qt_app, 2)
    assert window.current_key == "journal"


# ---------------------------------------------------------------------------
# 4. the library can be marked and filtered
# ---------------------------------------------------------------------------


def _library(qt_app, window):
    window.go("library", "")
    pump(qt_app, 3)
    return window.views["library"]


def test_a_shelf_row_can_be_marked_as_read_and_unmarked(qt_app, window,
                                                        store):
    view = _library(qt_app, window)
    box, item_id = view._reads[0]
    assert item_id.startswith("lib:shelf:")
    assert not box.isChecked()
    box.setChecked(True)
    pump(qt_app)
    assert store.is_checked(item_id)
    box.setChecked(False)
    pump(qt_app)
    assert not store.is_checked(item_id)


def test_every_tab_that_can_be_read_has_marks_of_its_own(qt_app, window):
    view = _library(qt_app, window)
    prefixes = {item_id.split(":")[1] for _box, item_id in view._reads}
    assert prefixes == {"shelf", "fields", "video"}


def test_a_read_mark_survives_leaving_the_page(qt_app, window, store):
    view = _library(qt_app, window)
    _box, item_id = view._reads[0]
    store.set_checked(item_id, True)
    window.go("today", "")
    pump(qt_app, 2)
    view = _library(qt_app, window)
    box = next(b for b, i in view._reads if i == item_id)
    assert box.isChecked(), "the tick was not read back from the store"


def test_undoing_a_read_mark_puts_the_tick_back(qt_app, window, store):
    view = _library(qt_app, window)
    box, item_id = view._reads[0]
    box.setChecked(True)
    pump(qt_app)
    assert store.is_checked(item_id)
    window.undo()
    pump(qt_app, 2)
    assert not store.is_checked(item_id)
    assert not next(b for b, i in view._reads if i == item_id).isChecked()


def test_the_filter_hides_the_rows_that_do_not_match(qt_app, window):
    view = _library(qt_app, window)
    # The rows on show: a folded one is hidden by its own group, not by us.
    rows = [row for row in view._rows if row.tab == 0 and row.fold is None]
    assert rows
    assert all(row.widget.isVisible() for row in rows)
    view.filter.setText("zzzznothingmatchesthis")
    pump(qt_app, 2)
    assert not any(row.widget.isVisible() for row in rows)
    assert "0 of" in view.filter_note.text()
    view.filter.setText("")
    pump(qt_app, 2)
    assert all(row.widget.isVisible() for row in rows)
    assert view.filter_note.text() == ""


def test_the_filter_keeps_the_rows_that_do_match(qt_app, window, curriculum):
    view = _library(qt_app, window)
    wanted = curriculum.shelf[0].items[0].name
    view.filter.setText(wanted)
    pump(qt_app, 2)
    shown = [row for row in view._rows if row.tab == 0 and row.widget.isVisible()]
    assert shown, "the row the filter was typed for is hidden"
    # Every word of the query, folded - the one matcher every box uses.
    from operators_console.core.textmatch import matches
    assert all(matches(wanted, row.text) for row in shown)


def test_the_filter_opens_a_fold_that_hides_a_match(qt_app, window):
    view = _library(qt_app, window)
    folded = [row for row in view._rows if row.fold is not None]
    assert folded
    row = folded[0]
    row.fold.set_open(False, animate=False)
    pump(qt_app)
    view.filter.setText(row.text.split()[0])
    pump(qt_app, 2)
    assert row.fold.is_open, "a match stayed folded away"


def test_a_search_target_clears_a_filter_that_would_hide_it(qt_app, window,
                                                            curriculum):
    view = _library(qt_app, window)
    view.filter.setText("zzzznothingmatchesthis")
    pump(qt_app, 2)
    field = curriculum.fields[0]
    window._open_hit(_hit("field", field.id))
    pump(qt_app, 2)
    assert view.filter.text() == ""
    assert view._targets[field.id][1].isVisible()


def test_the_library_still_has_its_four_tabs_and_its_certificate_control(
        qt_app, window, curriculum):
    from PySide6.QtWidgets import QPushButton
    view = _library(qt_app, window)
    assert view.tabs.count() == 4
    view.tabs.setCurrentIndex(3)
    pump(qt_app, 2)
    marks = [b for b in view.certs_tab.findChildren(QPushButton)
             if b.text().startswith("Mark: ")]
    assert len(marks) == len(curriculum.certs)


# ---------------------------------------------------------------------------
# 5. shortcuts, and feedback anyone can hear
# ---------------------------------------------------------------------------


def _menu_actions(window):
    for top in window.menuBar().actions():
        if top.menu() is not None:
            yield from top.menu().actions()


def test_ctrl_zero_and_ctrl_l_both_open_the_library(qt_app, window):
    from PySide6.QtGui import QKeySequence
    action = window.go_actions["library"]
    keys = {key.toString() for key in action.shortcuts()}
    assert keys == {"Ctrl+0", "Ctrl+L"}
    window.go("today", "")
    action.trigger()
    pump(qt_app, 2)
    assert window.current_key == "library"
    # And no other menu action claims either key.
    for other in _menu_actions(window):
        if other is action:
            continue
        assert not ({k.toString() for k in other.shortcuts()} & keys), \
            other.text()
    assert QKeySequence("Ctrl+0") in action.shortcuts()


def test_the_go_menu_reaches_every_page_by_key(qt_app, window):
    from operators_console.ui.main_window import NAV
    bound = {key for key, action in window.go_actions.items()
             if action.shortcuts()}
    assert bound == {key for key, _text, _factory in NAV}


def test_a_toast_is_announced_to_a_screen_reader(qt_app, window, monkeypatch):
    seen = []
    monkeypatch.setattr(QAccessible, "updateAccessibility",
                        staticmethod(lambda event: seen.append(event)))
    window.toast("Snapshot saved as today.db")
    pump(qt_app)
    assert window.status_label.text() == "Snapshot saved as today.db"
    assert window.status_label.accessibleName() == "Snapshot saved as today.db"
    assert seen, "nothing was posted for a reader"
    assert seen[-1].object() is window.status_label
    assert seen[-1].type() == QAccessible.Event.Alert


def test_clearing_a_toast_does_not_shout(qt_app, window, monkeypatch):
    seen = []
    monkeypatch.setattr(QAccessible, "updateAccessibility",
                        staticmethod(lambda event: seen.append(event)))
    window._clear_toast()
    pump(qt_app)
    assert seen == []
    assert window.status_label.accessibleName() == "Status"


def test_announce_survives_a_platform_without_accessibility(qt_app, window,
                                                            monkeypatch):
    def explode(_event):
        raise RuntimeError("no accessibility here")

    monkeypatch.setattr(QAccessible, "updateAccessibility",
                        staticmethod(explode))
    window.toast("still fine")          # must not raise
    assert window.status_label.text() == "still fine"


# ---------------------------------------------------------------------------
# 6. the first launch points at the guide
# ---------------------------------------------------------------------------


def test_the_first_launch_points_at_the_guide_once(qt_app, store, curriculum):
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import GUIDE_HINT, MainWindow

    store.set_setting("onboarded", True)
    assert store.setting("guide_pointed", False) is False
    ctx = AppContext(store=store, curriculum=curriculum)
    first = MainWindow(ctx)
    try:
        pump(qt_app, 2)
        assert first.status_label.text() == GUIDE_HINT
        assert "Help > How this app works" in GUIDE_HINT
        assert store.setting("guide_pointed") is True
    finally:
        _drop(qt_app, first, ctx)

    ctx2 = AppContext(store=store, curriculum=curriculum)
    second = MainWindow(ctx2)
    try:
        pump(qt_app, 2)
        assert second.status_label.text() == "", "the hint was said twice"
    finally:
        _drop(qt_app, second, ctx2)


def _drop(qt_app, window, ctx) -> None:
    from PySide6.QtCore import QCoreApplication, QEvent
    window._toast_timer.stop()
    window.deleteLater()
    ctx.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    pump(qt_app)
