"""The gaps the review page left: no keyboard, no way out, no way back.

Five things a learner needed every day and could not do: answer a card
without a mouse, bury a card they keep failing, take back a rating, stop a
skipped card looping forever, and reach a line's menu without right-clicking
it.
"""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMenu, QPushButton

from conftest import pump
from operators_console.core.review import CONCEPT, QUIZ, ReviewQueue
from operators_console.core.srs import Rating, State


# -- helpers ---------------------------------------------------------------


def _queue(curriculum, store, progress):
    return ReviewQueue(curriculum, store, progress)


def _concept_card(ctx):
    item = ctx.curriculum.phase("p00").items[0]
    ctx.review.add_concept(item.id)
    return next(c for c in ctx.review.all_cards() if c.id == item.id)


def _quiz_card(ctx):
    return next(c for c in ctx.review.all_cards() if c.kind == QUIZ)


def _open_review(window, qt_app, cards):
    """Show the review page with an exact queue, whatever the deck holds."""
    window.go("review", "")
    pump(qt_app, 2)
    view = window.views["review"]
    view.card = None
    view.queue = list(cards)
    view._next_card()
    pump(qt_app, 2)
    return view


def _buttons(view, prefix):
    return [b for b in view.findChildren(QPushButton)
            if b.text().startswith(prefix)]


def _one(view, prefix):
    found = _buttons(view, prefix)
    assert found, "no %r button on the page" % prefix
    return found[0]


def _rows(window, phase_id="p01"):
    from operators_console.ui.widgets.common import CheckRow
    window.go("phase", phase_id)
    return window.views["phase"].findChildren(CheckRow)


# -- 1. the keyboard -------------------------------------------------------


def test_space_reveals_a_concept_card_and_a_number_rates_it(qt_app, window):
    view = _open_review(window, qt_app, [_concept_card(window.ctx)])
    card = view.card
    QTest.keyClick(view, Qt.Key.Key_Space)
    pump(qt_app)
    assert view.revealed, "Space did not reveal the line"
    assert _buttons(view, "Good"), "no ratings after a keyboard reveal"

    QTest.keyClick(view, Qt.Key.Key_3)
    pump(qt_app)
    assert window.ctx.store.memory(card.id).reps == 1
    assert window.ctx.store.memory(card.id).state is not State.NEW


def test_enter_checks_a_quiz_card_and_letters_pick_the_option(qt_app, window):
    view = _open_review(window, qt_app, [_quiz_card(window.ctx)])
    card = view.card
    # The choices are shuffled on screen, and the letters follow the screen.
    letter = "ABCDEFGH"[view.shown_order.index(card.correct)]
    QTest.keyClick(view, getattr(Qt.Key, "Key_" + letter))
    pump(qt_app)
    assert view.group.checkedId() == card.correct, "the letter picked nothing"
    assert view.group.button(view.shown_order[0]).text().startswith("A.")

    QTest.keyClick(view, Qt.Key.Key_Return)
    pump(qt_app)
    assert _buttons(view, "Easy"), "Enter did not check the answer"
    QTest.keyClick(view, Qt.Key.Key_4)
    pump(qt_app)
    assert window.ctx.store.memory(card.id).reps == 1


def test_every_rating_key_is_bound_and_printed_on_its_button(qt_app, window):
    from operators_console.ui.views.review import RATING_KEY
    for rating, key in RATING_KEY.items():
        view = _open_review(window, qt_app, [_concept_card(window.ctx)])
        card = view.card
        QTest.keyClick(view, Qt.Key.Key_Space)
        pump(qt_app)
        name = {Rating.AGAIN: "Again", Rating.HARD: "Hard",
                Rating.GOOD: "Good", Rating.EASY: "Easy"}[rating]
        widget = _one(view, name)
        assert "(%s)" % key in widget.text(), widget.text()
        assert key in widget.toolTip()
        QTest.keyClick(view, getattr(Qt.Key, "Key_" + key))
        pump(qt_app)
        assert window.ctx.store.memory(card.id).reps >= 1
        window.ctx.review.remove_concept(card.id)


def test_s_skips_and_the_key_is_on_the_button(qt_app, window):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [first, second])
    assert "(S)" in _one(view, "Skip").text()
    QTest.keyClick(view, Qt.Key.Key_S)
    pump(qt_app)
    assert view.card.id == second.id, "S did not move on"
    assert window.ctx.store.memory(first.id).reps == 0


def test_keys_do_nothing_while_a_text_box_has_the_focus(qt_app, window):
    view = _open_review(window, qt_app, [_concept_card(window.ctx)])
    window.activateWindow()
    window.search.setFocus()
    pump(qt_app, 2)
    assert QApplication.focusWidget() is window.search
    QTest.keyClick(view, Qt.Key.Key_Space)
    QTest.keyClick(view, Qt.Key.Key_S)
    pump(qt_app)
    assert not view.revealed, "a page key fired while the search box had focus"
    assert view.card is not None


def test_the_windows_own_ctrl_keys_are_left_alone(qt_app, window):
    """Ctrl+S must not read as the skip key."""
    view = _open_review(window, qt_app, [_concept_card(window.ctx)])
    card = view.card
    QTest.keyClick(view, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
    pump(qt_app)
    assert view.card is card


def test_the_shortcut_window_lists_the_review_keys(qt_app, window):
    from operators_console.ui.shortcuts import REVIEW_SHORTCUTS, ShortcutsDialog
    keys = [row[0] for row in REVIEW_SHORTCUTS]
    assert "Space, Enter" in keys and "1, 2, 3, 4" in keys and "S" in keys
    dialog = ShortcutsDialog(window)
    try:
        from PySide6.QtWidgets import QLabel
        shown = [w.text() for w in dialog.findChildren(QLabel)]
        assert "In review" in shown
        for combination in keys:
            assert combination in shown
    finally:
        dialog.deleteLater()


# -- 2. burying and restoring ----------------------------------------------


def test_a_buried_card_leaves_the_deck_and_comes_back(curriculum, store,
                                                      progress):
    queue = _queue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    queue.answer(card, Rating.AGAIN)
    store.suspend_card(card.id, True)

    assert card.id in queue.suspended_ids()
    assert card.id not in {c.id for c in queue.all_cards()}
    assert card.id not in {c.id for c in queue.session()}

    assert queue.restore_suspended() == 1
    assert queue.suspended_ids() == set()
    assert card.id in {c.id for c in queue.all_cards()}


def test_a_card_nobody_has_answered_can_still_be_buried(curriculum, store,
                                                        progress):
    """A new card has no schedule row, and it is the one worth burying.

    `Store.suspend_card` was an UPDATE, so it matched nothing and burying
    did nothing at all; it upserts now, and `ReviewQueue.bury` writes the
    memory first either way.
    """
    queue = _queue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    assert card.memory.state is State.NEW
    store.suspend_card(card.id, True)
    assert queue.suspended_ids() == {card.id}, "the store lost the bury"
    assert queue.restore_suspended() == 1

    queue.bury(card)
    assert card.id in queue.suspended_ids()
    assert card.id not in {c.id for c in queue.session()}
    assert card.id not in {c.id for c in queue.all_cards()}


def test_burying_from_the_answered_state_moves_on_and_undoes(qt_app, window):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [first, second])
    QTest.keyClick(view, Qt.Key.Key_Space)
    pump(qt_app)
    bury = _one(view, "Bury this card")
    bury.click()
    pump(qt_app, 2)
    assert first.id in window.ctx.review.suspended_ids()
    assert view.card is not None and view.card.id == second.id

    window.ctx.undo()
    pump(qt_app)
    assert first.id not in window.ctx.review.suspended_ids()


def test_the_summary_says_how_many_are_buried_and_gives_them_back(qt_app,
                                                                  window):
    card = _concept_card(window.ctx)
    window.ctx.review.bury(card)
    view = _open_review(window, qt_app, [_quiz_card(window.ctx)])
    assert card.id in window.ctx.review.suspended_ids()
    view._apply(Rating.GOOD)            # empties the queue: summary screen
    pump(qt_app, 2)
    assert _buttons(view, "Check for more"), "not on the summary screen"
    from PySide6.QtWidgets import QLabel
    said = [w.text() for w in view.findChildren(QLabel)]
    assert "1 buried card" in said, "the summary never said anything was away"
    restore = _one(view, "Restore")
    restore.click()
    pump(qt_app, 2)
    assert window.ctx.review.suspended_ids() == set()


def test_a_line_already_in_the_deck_offers_removal(qt_app, window):
    rows = _rows(window)
    pump(qt_app)
    row = rows[0]
    assert [a.text() for a in row.build_menu().actions()][0] \
        == "Add to review deck"
    window.ctx.review.add_concept(row.item_id)
    assert row.is_in_deck()
    menu = row.build_menu()
    assert [a.text() for a in menu.actions()][0] == "Remove from review deck"
    menu.actions()[0].trigger()
    pump(qt_app)
    assert row.item_id not in window.ctx.review.concept_ids()


# -- 3. taking an answer back ----------------------------------------------


def test_undo_answer_forgets_the_schedule_and_the_logged_row(curriculum, store,
                                                             progress):
    queue = _queue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    previous = card.memory
    queue.answer(card, Rating.GOOD)
    rows = store.db.execute("SELECT COUNT(*) AS n FROM reviews "
                            "WHERE card_id=?", (card.id,)).fetchone()["n"]
    assert rows == 1
    assert store.review_accuracy(30) == (1, 1)

    queue.undo_answer(card, previous)
    assert store.memory(card.id).state is State.NEW
    assert store.memory(card.id).reps == 0
    assert store.db.execute("SELECT COUNT(*) AS n FROM reviews "
                            "WHERE card_id=?", (card.id,)).fetchone()["n"] == 0
    assert store.review_accuracy(30) == (0, 0)
    day = list(store.activity(days=1).values())
    assert not day or day[-1]["reviews"] == 0


def test_the_next_card_offers_the_answer_back_and_ctrl_z_does_it(qt_app,
                                                                 window):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [first, second])
    QTest.keyClick(view, Qt.Key.Key_Space)
    QTest.keyClick(view, Qt.Key.Key_3)
    pump(qt_app, 2)
    assert view.card.id == second.id
    assert window.ctx.store.memory(first.id).reps == 1

    undo = _one(view, "Undo that answer")
    undo.click()
    pump(qt_app, 2)
    assert window.ctx.store.memory(first.id).reps == 0
    assert view.card is not None and view.card.id == first.id, \
        "the card did not go back to the front of the queue"
    assert second.id in [c.id for c in view.queue]

    window.ctx.redo()
    pump(qt_app, 2)
    assert window.ctx.store.memory(first.id).reps == 1


def test_undo_survives_the_page_being_thrown_away(qt_app, window):
    """Ctrl+Z reaches here from any page, including after a theme change."""
    view = _open_review(window, qt_app, [_concept_card(window.ctx)])
    card = view.card
    QTest.keyClick(view, Qt.Key.Key_Space)
    QTest.keyClick(view, Qt.Key.Key_2)
    pump(qt_app, 2)
    assert view.card is None            # the queue emptied
    view.teardown()
    pump(qt_app)
    window.ctx.undo()
    pump(qt_app)
    assert window.ctx.store.memory(card.id).reps == 0


# -- 4. skipping ------------------------------------------------------------


def test_a_card_skipped_twice_leaves_today(qt_app, window):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [first, second])
    said = []
    window.ctx.toast.connect(said.append)

    QTest.keyClick(view, Qt.Key.Key_S)          # skip one: it goes to the back
    pump(qt_app)
    assert first.id in [c.id for c in view.queue] or view.card.id == first.id
    while view.card is not None and view.card.id != first.id:
        QTest.keyClick(view, Qt.Key.Key_S)
        pump(qt_app)
    assert view.card is not None and view.card.id == first.id

    QTest.keyClick(view, Qt.Key.Key_S)          # skip two: gone for today
    pump(qt_app)
    assert first.id not in [c.id for c in view.queue]
    assert first.id in view.dropped
    assert any("Skipped twice" in message for message in said), said
    view.card = None
    view.queue = []
    view._start_or_idle()
    pump(qt_app)
    assert first.id not in [c.id for c in view.queue]
    assert view.card is None or view.card.id != first.id


# -- 5. the row's menu ------------------------------------------------------


def test_the_row_can_be_reached_by_keyboard(qt_app, window):
    row = _rows(window)[0]
    pump(qt_app)
    assert row.focusPolicy() != Qt.FocusPolicy.NoFocus
    assert row.focusProxy() is row.box, "the row is a second Tab stop"
    row.setFocus()
    pump(qt_app)
    assert row.hasFocus()


@pytest.mark.parametrize("key,modifier", [
    (Qt.Key.Key_Menu, Qt.KeyboardModifier.NoModifier),
    (Qt.Key.Key_F10, Qt.KeyboardModifier.ShiftModifier),
])
def test_the_menu_key_and_shift_f10_open_the_row_menu(qt_app, window, key,
                                                      modifier):
    row = _rows(window)[0]
    pump(qt_app)
    QTest.keyClick(row, key, modifier)
    pump(qt_app, 2)
    menus = [m for m in row.findChildren(QMenu) if m.isVisible()]
    assert menus, "no menu opened"
    assert [a.text() for a in menus[0].actions()] == ["Add to review deck",
                                                      "Copy text"]
    menus[0].close()
    pump(qt_app)


def test_the_more_handle_is_not_built_until_it_is_wanted(qt_app, window):
    """A QPushButton per line is re-polished on every theme change.

    Eagerly built on 155 lines it cost a second and a half of a theme
    switch, for a control only the hovered row ever shows.
    """
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QEnterEvent
    rows = _rows(window)
    pump(qt_app)
    assert rows, "no roadmap lines on the page"
    assert all(row._more is None for row in rows), "every line built one"
    assert not rows[0].findChildren(QPushButton)

    width = rows[0].sizeHint().width()
    handle = rows[0].more                       # asking is what builds it
    assert isinstance(handle, QPushButton)
    assert rows[0].more is handle, "a second ask built a second button"
    assert abs(rows[0].sizeHint().width() - width) <= 2, \
        "the line moved when its handle appeared"

    spot = QPointF(2.0, 2.0)
    rows[1].enterEvent(QEnterEvent(spot, spot, spot))
    assert rows[1]._more is not None, "hovering the row showed nothing"


def test_the_more_button_opens_the_same_menu(qt_app, window):
    row = _rows(window)[0]
    pump(qt_app)
    assert row.more.text() == "..."
    assert row.more.focusPolicy() == Qt.FocusPolicy.NoFocus
    row.more.click()
    pump(qt_app, 2)
    menus = [m for m in row.findChildren(QMenu) if m.isVisible()]
    assert menus, "the ... button opened nothing"
    actions = [a.text() for a in menus[0].actions()]
    assert "Add to review deck" in actions
    menus[0].close()
    pump(qt_app)


def test_the_row_keeps_its_signals_and_its_strike_through(qt_app, window):
    row = _rows(window)[0]
    pump(qt_app)
    sent = []
    row.toggled.connect(lambda item_id, state: sent.append((item_id, state)))
    row.review_requested.connect(lambda item_id: sent.append(("review",
                                                              item_id)))
    row.remove_requested.connect(lambda item_id: sent.append(("remove",
                                                              item_id)))
    row.box.setChecked(True)
    pump(qt_app)
    assert sent and sent[0] == (row.item_id, True)
    assert "<s>" in row.text.text(), "a finished line lost its strike-through"
    row.set_checked(False)
    assert "<s>" not in row.text.text()

    row.build_menu().actions()[0].trigger()         # Add to review deck
    pump(qt_app)
    assert ("review", row.item_id) in sent
    window.ctx.review.add_concept(row.item_id)
    row.build_menu().actions()[0].trigger()         # Remove from review deck
    pump(qt_app)
    assert ("remove", row.item_id) in sent


def test_a_project_requirement_is_not_offered_to_the_deck(qt_app, window):
    """Its id is not a curriculum line, so the deck could never card it."""
    from operators_console.ui.widgets.common import CheckRow
    window.go("projects", "")
    pump(qt_app, 2)
    rows = [r for r in window.views["projects"].findChildren(CheckRow)
            if r.item_id.startswith("pj.")]
    assert rows, "no project requirement rows on the page"
    assert [a.text() for a in rows[0].build_menu().actions()] == ["Copy text"]


def test_an_orphan_row_still_builds_a_menu(qt_app):
    """A row outside any page has no services to ask, and must not crash."""
    from operators_console.ui.widgets.common import CheckRow
    row = CheckRow("p00.1", "a line <em>with code</em>", False)
    try:
        assert row.is_in_deck() is False
        assert [a.text() for a in row.build_menu().actions()][0] \
            == "Add to review deck"
        row.set_in_deck(True)
        assert [a.text() for a in row.build_menu().actions()][0] \
            == "Remove from review deck"
        row._leave_deck()               # no context: must be a quiet no-op
        assert row.is_in_deck() is False
    finally:
        row.deleteLater()


def test_concept_cards_still_answer_normally(curriculum, store, progress):
    """The deck's own behaviour is unchanged by any of the above."""
    queue = _queue(curriculum, store, progress)
    item = curriculum.phase("p00").items[0]
    queue.add_concept(item.id)
    card = next(c for c in queue.all_cards() if c.id == item.id)
    assert card.kind == CONCEPT
    queue.answer(card, Rating.GOOD)
    assert store.memory(item.id).state is not State.NEW
