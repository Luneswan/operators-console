"""Review, driven the way a learner drives it: with the keyboard.

Walk 06 proves a session works under a mouse. This one presses every key the
page now answers to, buries a card and brings it back, takes a rating back,
skips a card until it leaves for the day, and opens a roadmap line's menu
without ever right-clicking it.
"""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QPushButton

from .harness import REC, click, press, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


# -- helpers ---------------------------------------------------------------


def _concept_card(ctx, index: int = 0):
    item = ctx.curriculum.phase("p00").items[index]
    ctx.review.add_concept(item.id)
    return next(c for c in ctx.review.all_cards() if c.id == item.id)


def _quiz_card(ctx):
    return next(c for c in ctx.review.all_cards() if c.kind == "quiz")


def _open(walk_app, window, cards):
    """Show review holding exactly these cards, so each key has a target."""
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    view.card = None
    view.queue = list(cards)
    view._next_card()
    pump(walk_app, 2)
    return view


def _buttons(view, prefix):
    return [b for b in view.findChildren(QPushButton)
            if b.text().startswith(prefix)]


def _one(view, prefix):
    found = _buttons(view, prefix)
    assert found, "no %r button on the review page" % prefix
    return found[0]


def _rows(window, phase_id="p01"):
    from operators_console.ui.widgets.common import CheckRow
    window.go("phase", phase_id)
    return window.views["phase"].findChildren(CheckRow)


def _row_menu(row):
    """The menu the row has just opened.

    A menu that has been triggered is still on screen until it is closed, and
    a closed one lives on as a child until Qt runs the deferred delete, so
    the newest visible menu is the one that was just asked for.
    """
    menus = [m for m in row.findChildren(QMenu) if m.isVisible()]
    return menus[-1] if menus else None


# -- the keyboard ----------------------------------------------------------


def test_a_concept_card_is_revealed_and_rated_without_a_mouse(walk_app, window,
                                                              store):
    view = _open(walk_app, window, [_concept_card(window.ctx)])
    card = view.card
    with step(walk_app, "review", "press Space to reveal the saved line",
              window):
        assert "(Space)" in _one(view, "Reveal").text()
        press(walk_app, view, Qt.Key.Key_Space)
        assert view.revealed, "Space revealed nothing"
    with step(walk_app, "review", "press 3 to rate it Good", window):
        good = _one(view, "Good")
        assert "(3)" in good.text(), good.text()
        press(walk_app, view, Qt.Key.Key_3)
        assert store.memory(card.id).reps == 1
    REC.bump("review cards answered from the keyboard")


def test_a_quiz_card_is_picked_by_letter_and_checked_by_enter(walk_app, window,
                                                              store):
    view = _open(walk_app, window, [_quiz_card(window.ctx)])
    card = view.card
    with step(walk_app, "review", "pick a multiple choice option by letter",
              window):
        # Shuffled on screen: the letters follow the order drawn.
        assert view.group.button(view.shown_order[0]).text().startswith("A.")
        letter = "ABCDEFGH"[view.shown_order.index(card.correct)]
        press(walk_app, view, getattr(Qt.Key, "Key_" + letter))
        assert view.group.checkedId() == card.correct
        REC.bump("quiz options picked by letter")
    with step(walk_app, "review", "press Enter to check it", window):
        press(walk_app, view, Qt.Key.Key_Return)
        assert _buttons(view, "Again"), "Enter checked nothing"
    with step(walk_app, "review", "press 4 for Easy", window):
        press(walk_app, view, Qt.Key.Key_4)
        assert store.memory(card.id).reps == 1


def test_every_rating_key_answers_a_card(walk_app, window, store):
    """1, 2, 3 and 4, each one pressed against a card of its own."""
    used = []
    for key, name in ((Qt.Key.Key_1, "Again"), (Qt.Key.Key_2, "Hard"),
                      (Qt.Key.Key_3, "Good"), (Qt.Key.Key_4, "Easy")):
        view = _open(walk_app, window,
                     [_concept_card(window.ctx, index=len(used))])
        card = view.card
        with step(walk_app, "review", "answer with the %s key" % name, window):
            press(walk_app, view, Qt.Key.Key_Space)
            assert _buttons(view, name), "no %s button to press" % name
            press(walk_app, view, key)
            memory = store.memory(card.id)
            assert memory.reps == 1 or memory.lapses == 1, card.id
        used.append(name)
    REC.bump("rating keys pressed", len(used))
    assert used == ["Again", "Hard", "Good", "Easy"]


def test_typing_in_the_search_box_is_not_reviewing(walk_app, window):
    view = _open(walk_app, window, [_concept_card(window.ctx)])
    with step(walk_app, "review", "type in the search box with a card open",
              window):
        window.activateWindow()
        window.search.setFocus()
        pump(walk_app, 2)
        press(walk_app, view, Qt.Key.Key_S)
        press(walk_app, view, Qt.Key.Key_Space)
        assert not view.revealed, "a page key fired while typing"
        assert view.card is not None
        window.search.clear()


# -- burying ---------------------------------------------------------------

def test_a_card_can_be_buried_and_brought_back(walk_app, window, store):
    first = _concept_card(window.ctx, 0)
    second = _concept_card(window.ctx, 1)
    view = _open(walk_app, window, [first, second])
    with step(walk_app, "review", "bury the card in front of you", window):
        press(walk_app, view, Qt.Key.Key_Space)
        click(walk_app, _one(view, "Bury this card"))
        assert first.id in window.ctx.review.suspended_ids()
        assert view.card is not None and view.card.id == second.id
        REC.bump("cards buried")
    with step(walk_app, "review", "the summary offers the buried card back",
              window):
        press(walk_app, view, Qt.Key.Key_Space)
        press(walk_app, view, Qt.Key.Key_3)
        assert view.card is None, "the queue should be empty now"
        click(walk_app, _one(view, "Restore"))
        assert window.ctx.review.suspended_ids() == set()
        assert first.id in {c.id for c in window.ctx.review.all_cards()}
        assert store.memory(second.id).reps == 1


# -- taking an answer back --------------------------------------------------


def test_a_rating_can_be_taken_back_from_the_next_card(walk_app, window,
                                                       store):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open(walk_app, window, [first, second])
    with step(walk_app, "review", "answer one card, then take it back",
              window):
        press(walk_app, view, Qt.Key.Key_Space)
        press(walk_app, view, Qt.Key.Key_3)
        assert store.memory(first.id).reps == 1
        click(walk_app, _one(view, "Undo that answer"))
        assert store.memory(first.id).reps == 0, "the schedule stood"
        assert view.card.id == first.id, "the card did not come back first"
        REC.bump("review answers taken back")
    with step(walk_app, "review", "Ctrl+Z takes the next one back too",
              window):
        press(walk_app, view, Qt.Key.Key_Space)
        press(walk_app, view, Qt.Key.Key_1)
        window.ctx.undo()
        pump(walk_app, 2)
        assert store.memory(first.id).reps == 0


# -- skipping ---------------------------------------------------------------


def test_a_skipped_card_does_not_come_round_for_ever(walk_app, window):
    first, second = _concept_card(window.ctx), _quiz_card(window.ctx)
    view = _open(walk_app, window, [first, second])
    with step(walk_app, "review", "skip the same card twice", window):
        click(walk_app, _one(view, "Skip"))
        rounds = 0
        while view.card is not None and view.card.id != first.id \
                and rounds < 6:
            press(walk_app, view, Qt.Key.Key_S)
            rounds += 1
        assert view.card is not None and view.card.id == first.id
        press(walk_app, view, Qt.Key.Key_S)
        assert first.id in view.dropped
        assert first.id not in [c.id for c in view.queue]
        REC.bump("cards skipped out of the day")


# -- the roadmap row's menu -------------------------------------------------


def test_a_line_reaches_the_review_deck_without_a_right_click(walk_app,
                                                              window):
    rows = _rows(window)
    pump(walk_app, 2)
    assert rows, "no roadmap lines on the page"
    row = rows[0]
    with step(walk_app, "phase", "open a line's menu with the ... button",
              window):
        click(walk_app, row.more)
        menu = _row_menu(row)
        assert menu is not None, "the ... button opened nothing"
        assert [a.text() for a in menu.actions()] == ["Add to review deck",
                                                      "Copy text"]
        menu.close()
        pump(walk_app, 2)
    with step(walk_app, "phase", "open the same menu with Shift+F10", window):
        press(walk_app, row, Qt.Key.Key_F10,
              Qt.KeyboardModifier.ShiftModifier)
        menu = _row_menu(row)
        assert menu is not None, "Shift+F10 opened nothing"
        menu.actions()[0].trigger()
        menu.close()
        pump(walk_app, 2)
        assert row.item_id in window.ctx.review.concept_ids()
        REC.bump("lines sent to the deck from the keyboard")
    with step(walk_app, "phase", "the Menu key offers to take it out again",
              window):
        press(walk_app, row, Qt.Key.Key_Menu)
        menu = _row_menu(row)
        assert menu is not None, "the Menu key opened nothing"
        assert [a.text() for a in menu.actions()][0] \
            == "Remove from review deck"
        menu.actions()[0].trigger()
        menu.close()
        pump(walk_app, 2)
        assert row.item_id not in window.ctx.review.concept_ids()
        REC.bump("lines taken out of the deck")
