"""Review: a whole session, every rating button, and the daily ceiling."""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _seed(store, curriculum, phases=3, per_phase=3):
    for phase in curriculum.phases[:phases]:
        ids = [i.id for i in phase.items][:per_phase]
        if ids:
            store.set_many_checked(ids, True)


def _rating_buttons(view):
    from PySide6.QtWidgets import QPushButton
    out = []
    for index in range(view.stage.count()):
        item = view.stage.itemAt(index)
        widget = item.widget() if item is not None else None
        if widget is not None:
            out += [b for b in widget.findChildren(QPushButton)
                    if b.text().split("\n")[0] in ("Again", "Hard", "Good",
                                                   "Easy")]
    return out


def _action(view, prefix):
    from PySide6.QtWidgets import QPushButton
    for index in range(view.stage.count()):
        item = view.stage.itemAt(index)
        layout = item.layout() if item is not None else None
        widget = item.widget() if item is not None else None
        candidates = []
        if layout is not None:
            candidates = [layout.itemAt(i).widget()
                          for i in range(layout.count())]
        elif widget is not None:
            candidates = widget.findChildren(QPushButton)
        for candidate in candidates:
            if isinstance(candidate, QPushButton) \
                    and candidate.text().startswith(prefix):
                return candidate
    return None


def test_an_empty_deck_says_so_and_forecasts(walk_app, window):
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    with step(walk_app, "review", "open Review with nothing started", window):
        assert view.tile_due.value_label.text() == "0"
        assert view.stage.count() >= 1


def test_a_whole_session_with_every_rating_button(walk_app, window, store,
                                                  curriculum):
    from operators_console.core.srs import Rating
    _seed(store, curriculum)
    window.ctx.rebuild_review()
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    assert view.card is not None, "nothing was offered to review"

    planned = len(window.ctx.review.session())
    REC.bump("cards planned for the first session", planned)
    ratings_used = set()
    seen = []
    order = [Rating.GOOD, Rating.HARD, Rating.EASY, Rating.AGAIN]
    index = 0
    while view.card is not None and index < planned:
        card_id = view.card.id
        seen.append(card_id)
        with step(walk_app, "review", "answer card %d of %d"
                  % (index + 1, planned), window):
            if view.card.kind == "quiz":
                choice = view.card.correct if index % 3 else (
                    0 if view.card.correct else 1)
                click(walk_app, view.group.button(choice), pump_rounds=0)
                check = _action(view, "Check")
                assert check is not None, "no Check button on a quiz card"
                click(walk_app, check, pump_rounds=0)
            else:
                reveal = _action(view, "Reveal")
                assert reveal is not None, "no Reveal button on a concept card"
                click(walk_app, reveal, pump_rounds=0)
            buttons = _rating_buttons(view)
            if buttons:
                wanted = order[index % len(order)]
                label = {Rating.AGAIN: "Again", Rating.HARD: "Hard",
                         Rating.GOOD: "Good", Rating.EASY: "Easy"}[wanted]
                chosen = [b for b in buttons
                          if b.text().startswith(label)]
                if chosen:
                    click(walk_app, chosen[0], pump_rounds=1)
                    ratings_used.add(label)
                else:
                    click(walk_app, buttons[0], pump_rounds=1)
            else:
                # A wrong multiple choice answer rates itself Again, and
                # stays on screen with its explanation until moved on from.
                ratings_used.add("Again")
                nxt = _action(view, "Next card")
                assert nxt is not None, "a wrong answer left no way on"
                assert _action(view, "Where this is taught") is not None
                click(walk_app, nxt, pump_rounds=1)
        assert store.memory(card_id).reps >= 1 or \
            store.memory(card_id).lapses >= 1, card_id
        index += 1
    REC.bump("review cards answered", len(seen))
    assert len(set(seen)) == len(seen), "a card was shown twice in one session"
    missing = {"Again", "Hard", "Good", "Easy"} - ratings_used
    assert not missing, "never pressed: %s" % sorted(missing)

    with step(walk_app, "review", "the session ends with a clear queue",
              window):
        assert view.card is None
        assert _action(view, "Check for more") is not None


def test_skipping_a_card_puts_it_back(walk_app, window, store, curriculum):
    _seed(store, curriculum)
    window.ctx.rebuild_review()
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    first = view.card.id
    with step(walk_app, "review", "skip the card in front of you", window):
        click(walk_app, _action(view, "Skip"))
        assert view.card is not None
        assert view.card.id != first or len(view.queue) == 0
        assert store.memory(first).reps == 0, "a skipped card was scheduled"


def test_the_daily_ceiling_holds(walk_app, window, store, curriculum):
    from operators_console.core.srs import Rating
    _seed(store, curriculum, phases=6, per_phase=6)
    store.set_setting("new_cards_per_day", 5)
    store.set_setting("max_reviews_per_day", 10)
    window.ctx.rebuild_review()
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    with step(walk_app, "review", "work to the daily limit", window):
        answered = 0
        while view.card is not None and answered < 50:
            view._apply(Rating.GOOD)
            pump(walk_app, 1)
            answered += 1
        assert answered <= 5, (
            "the new-card ceiling of 5 let %d through" % answered)
    REC.bump("cards allowed by a ceiling of five", answered)
    with step(walk_app, "review", "the idle screen explains the limit",
              window):
        assert view.stage.count() >= 1


def test_a_thousand_cards_do_not_wedge_the_page(walk_app, window, store,
                                                curriculum):
    """A learner back from a month away should still see a page."""
    import time
    from datetime import datetime, timedelta, timezone
    from operators_console.core.srs import Memory, State

    _seed(store, curriculum, phases=len(curriculum.phases), per_phase=2)
    past = datetime.now(timezone.utc) - timedelta(days=3)
    questions = list(curriculum.all_questions)
    made = 0
    with store.tx():
        for offset in range(1000):
            question = questions[offset % len(questions)]
            card_id = question.id if offset < len(questions) \
                else "%s#%d" % (question.id, offset)
            store.db.execute(
                "INSERT OR REPLACE INTO srs (card_id, kind, phase, state, "
                "stability, difficulty, due, last_review, reps, lapses, "
                "suspended) VALUES (?,?,?,?,?,?,?,?,?,?,0)",
                (card_id, "quiz", "p01", int(State.REVIEW), 5.0, 5.0,
                 past.isoformat(), past.isoformat(), 3, 0))
            made += 1
    store.set_setting("max_reviews_per_day", 1000)
    window.ctx.rebuild_review()
    started = time.perf_counter()
    with step(walk_app, "review", "open Review with a thousand cards due",
              window):
        window.go("review", "")
        pump(walk_app, 3)
        assert view_is_usable(window)
    elapsed = int((time.perf_counter() - started) * 1000)
    REC.bump("review cards seeded", made)
    REC.bump("milliseconds to open review with 1000 cards", elapsed)
    assert Memory is not None


def view_is_usable(window) -> bool:
    view = window.views["review"]
    return view.stage.count() >= 1 and view.tile_due.value_label.text() != ""
