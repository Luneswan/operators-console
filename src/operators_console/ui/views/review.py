"""Spaced review: the thing that stops phase 1 leaking away by phase 8."""
from __future__ import annotations

import random
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QButtonGroup, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QRadioButton, QTextEdit, QVBoxLayout,
)

from ...core.review import (
    GATE, QUIZ, choice_feedback, teaching_item,
)
from ...core.srs import Rating, describe_interval
from ..widgets.common import (
    Card, StatTile, button, clear_layout, divider, heading, label, meter,
    muted, pill,
)
from .base import View

RATING_LABEL = {
    # Outlined: in the light theme the solid red was the same red as the
    # suggested rating, so "Again" looked like the recommendation.
    Rating.AGAIN: ("Again", "danger", "I could not recall it"),
    Rating.HARD: ("Hard", "", "I got there, slowly"),
    Rating.GOOD: ("Good", "", "I knew it"),
    Rating.EASY: ("Easy", "good", "Instant - show it far less often"),
}

#: The four ratings, on the four keys under the left hand. The number is
#: printed on the button as well as listed in Help > Keyboard shortcuts:
#: a key nobody can see is a key nobody presses.
RATING_KEY = {
    Rating.AGAIN: "1",
    Rating.HARD: "2",
    Rating.GOOD: "3",
    Rating.EASY: "4",
}
KEY_RATING = {key: rating for rating, key in RATING_KEY.items()}

#: Multiple choice is answered by letter, not by number, so that picking an
#: option can never be confused with rating the card you have just answered.
OPTION_KEYS = "ABCDEFGH"

#: Skipping twice says the card is not worth today. Two is the count because
#: one skip is "not this second" and three is a card being avoided.
SKIP_LIMIT = 2

#: Typing beats every page key. A learner in the search box means the letter
#: S, not "skip the card behind this box".
_TEXT_ENTRY = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox)


def _is_typing() -> bool:
    return isinstance(QApplication.focusWidget(), _TEXT_ENTRY)


class ReviewView(View):
    title = "Review"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(ctx, parent)
        self.queue: list = []
        self.card = None
        self.shown_at = 0.0
        self.done_today = 0
        self.group = None
        self.revealed = False
        self.skips: dict = {}          # card id -> skips this session
        self.dropped: set = set()      # skipped twice: not again today
        self._last_answer = None       # (card, rating, memory before it)
        self._rating_live = False
        # The stored choice index drawn at each letter, for the card in front.
        self.shown_order: list = []
        self.rng = random.Random()
        # A wrong answer is rated Again at once, then stays on screen with its
        # explanation until the learner moves on. It used to be replaced by
        # the next card in the same instant, so the explanation of a mistake
        # - the one moment it matters - was never seen.
        self._pending_next = False
        self._hold_after_rating = False
        # The page itself takes the keyboard, so Space, 1-4 and S work the
        # moment a card appears rather than only after something is tabbed to.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def build(self) -> None:
        self.header("Review", "spaced repetition",
                    "Cards come back exactly as often as your own answers say "
                    "they need to. Answer honestly - the schedule is only as "
                    "good as the ratings.")
        self.summary = QHBoxLayout()
        self.summary.setSpacing(12)
        self.tile_due = StatTile("0", "Due now")
        self.tile_new = StatTile("0", "New available")
        self.tile_known = StatTile("0", "Known")
        self.tile_accuracy = StatTile("-", "Accuracy, 30 days")
        for tile in (self.tile_due, self.tile_new, self.tile_known,
                     self.tile_accuracy):
            self.summary.addWidget(tile)
        self.scroller.add_layout(self.summary)
        self.session_meter = meter(0)
        self.session_meter.setVisible(False)
        self.scroller.add(self.session_meter)
        self.scroller.add(divider())
        self.stage = QVBoxLayout()
        self.stage.setSpacing(12)
        self.scroller.add_layout(self.stage)
        self.scroller.add_stretch()

    # -- lifecycle ---------------------------------------------------------

    def _update_tiles(self) -> None:
        # Undo reaches this page from anywhere, including after a theme
        # change has thrown the widgets away. The numbers wait for the
        # rebuild; the store has already been put back.
        if not self._built:
            return
        counts = self.ctx.review.counts()
        card_counts = self.ctx.store.card_counts()
        correct, total = self.ctx.store.review_accuracy(30)
        self.tile_due.set_value(str(counts.due))
        self.tile_new.set_value(str(counts.new))
        self.tile_known.set_value(str(card_counts["mature"]))
        self.tile_accuracy.set_value(
            "%d%%" % round(correct / total * 100) if total else "-")

    def refresh(self) -> None:
        """Update the headline numbers, and start a session only if idle.

        Restarting on every refresh would rebuild the queue underneath a
        session in progress, which silently drops whichever card was next.
        """
        self._update_tiles()
        if self.card is None and not self.queue:
            self._start_or_idle()

    def show_target(self, target: str) -> None:
        self.ensure_built()
        self.refresh()

    @property
    def busy(self) -> bool:
        return self.card is not None        # a session is under way

    def _start_or_idle(self) -> None:
        self.queue = [card for card in self.ctx.review.session()
                      if card.id not in self.dropped]
        self.done_today = 0
        if not self.queue:
            self._idle_screen()
        else:
            self._next_card()

    def _idle_screen(self) -> None:
        clear_layout(self.stage)
        self.session_meter.setVisible(False)
        card = Card()
        counts = self.ctx.review.counts()
        if counts.new == 0 and counts.due == 0:
            card.add(label("Nothing due. Come back tomorrow.", "Soft"))
            card.add(muted(
                "Cards appear here once you have started the phase they belong "
                "to. Start a phase, or add a line from any phase to the deck "
                "by right-clicking it."))
        else:
            card.add(label("You have hit today's limit.", "Soft"))
            card.add(muted(
                "Daily limits exist so a week away does not turn into an "
                "unopenable wall. Raise them in Settings if you want more."))
        self._add_buried_row(card)
        forecast = self.ctx.store.forecast(14)
        if any(forecast):
            card.add(divider())
            card.add(heading("Coming up"))
            for offset, count in enumerate(forecast[:7]):
                when = "Today" if offset == 0 else (
                    "Tomorrow" if offset == 1 else "In %d days" % offset)
                row = QHBoxLayout()
                row.addWidget(muted(when))
                row.addWidget(meter(count, max(1, max(forecast))), 1)
                row.addWidget(muted(str(count)))
                card.box.addLayout(row)
        self.stage.addWidget(card)

    # -- burying -----------------------------------------------------------

    def _add_buried_row(self, card: Card) -> None:
        """Say how many cards are put away, and offer them back.

        A buried card is invisible everywhere else in the app. Without this
        line the learner has no way of knowing the deck is smaller than it
        looks, and no way of changing their mind.
        """
        buried = self.ctx.review.suspended_ids()
        if not buried:
            return
        card.add(divider())
        restore = button("Restore", "quiet",
                         "Put every buried card back into the deck")
        restore.clicked.connect(self._restore_buried)
        card.add_row(muted("%d buried card%s"
                           % (len(buried), "" if len(buried) == 1 else "s")),
                     None, restore)

    def _restore_buried(self) -> None:
        ids = sorted(self.ctx.review.suspended_ids())
        if not ids:
            return
        self.ctx.review.restore_suspended()
        self.ctx.record("restore buried cards",
                        lambda: self._set_suspended(ids, True),
                        lambda: self._set_suspended(ids, False))
        self.ctx.announce("%d card%s back in the deck."
                          % (len(ids), "" if len(ids) == 1 else "s"))
        self.ctx.changed()
        self.card = None
        self.queue = []
        self._update_tiles()
        self._start_or_idle()

    def _set_suspended(self, ids, suspended: bool) -> None:
        for card_id in ids:
            self.ctx.store.suspend_card(card_id, suspended)
        self.ctx.changed()
        self._update_tiles()

    def _bury(self) -> None:
        """Put the card in front away, and move on.

        The one thing a learner cannot do with a card they keep failing is
        stop being asked about it. The schedule is left exactly as the rating
        left it, so restoring later resumes rather than restarts.
        """
        card = self.card
        if card is None:
            return
        self.ctx.review.bury(card)
        self.ctx.record("bury card",
                        lambda: self._set_suspended([card.id], False),
                        lambda: self._set_suspended([card.id], True))
        self.ctx.announce("Buried. Restore it from the review summary.")
        self.ctx.changed()
        self.card = None
        self._rating_live = False
        self._update_tiles()
        self._next_card()

    # -- one card ----------------------------------------------------------

    def _next_card(self) -> None:
        if not self.queue:
            self._session_finished()
            return
        self.card = self.queue.pop(0)
        self.revealed = False
        self._rating_live = False
        self._pending_next = False
        self._hold_after_rating = False
        self.shown_at = time.monotonic()
        self.session_meter.setVisible(True)
        self.session_meter.setRange(0, self.done_today + len(self.queue) + 1)
        self.session_meter.setValue(self.done_today)
        self._render_front()

    def _render_front(self) -> None:
        clear_layout(self.stage)
        phase = self.ctx.curriculum.phase(self.card.phase)
        card = Card()
        top = QHBoxLayout()
        top.addWidget(pill(phase.num if phase else "--"))
        top.addWidget(muted(phase.name if phase else ""), 1)
        if self._last_answer is not None:
            # The rating that has just gone by is the one people want back,
            # and they want it back here, not from the Edit menu.
            undo = button("Undo that answer", "quiet",
                          "Ctrl+Z - put the card you just rated back")
            undo.clicked.connect(self._undo_last)
            top.addWidget(undo)
        top.addWidget(pill("NEW" if self.card.is_new else "REVIEW",
                           "warn" if self.card.is_new else ""))
        card.box.addLayout(top)

        prompt = label(self.card.front)
        prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
        card.add(prompt)

        if self.card.kind == QUIZ:
            # Drawn in a fresh order every time the card is shown; each
            # button's id is the choice's stored index, and the letters
            # follow the order on screen.
            self.shown_order = self._fresh_order(self.card)
            self.group = QButtonGroup(card)
            self.group.setExclusive(True)
            for position, stored in enumerate(self.shown_order):
                option = QRadioButton(self._option_text(
                    position, self.card.choices[stored]))
                option.setStyleSheet("padding: 5px 0; font-size: 13px;")
                self.group.addButton(option, stored)
                card.add(option)
            action = button("Check  (Space)", "primary",
                            "Space or Enter - mark the option you picked")
            action.clicked.connect(self._check_choice)
        else:
            self.group = None
            self.shown_order = []
            if self.card.kind == GATE:
                card.add(muted("A gate check for this phase. Say how you "
                               "would do it - out loud, from memory - then "
                               "reveal the check."))
            else:
                card.add(muted("Finish the line from memory, out loud, and "
                               "say where you would use it. Then reveal it."))
            action = button("Reveal  (Space)", "primary",
                            "Space or Enter - show the line you saved")
            action.clicked.connect(self._reveal_concept)

        self.stage.addWidget(card)
        controls = QHBoxLayout()
        skip = button("Skip for now  (S)", "quiet",
                      "S - come back to this one later in the session")
        skip.clicked.connect(self._skip)
        controls.addWidget(skip)
        controls.addStretch(1)
        controls.addWidget(action)
        self.stage.addLayout(controls)
        self._card_controls = (skip, action)
        # Nothing here animates and nothing steals a mouse user's place: the
        # page only claims the keyboard while it is the page on screen.
        if self.isVisible():
            self.setFocus()


    def _fresh_order(self, card) -> list:
        """A new order, with the right answer under a new letter.

        Where the answer sat last time is kept per card, so seeing a card
        again - later today or next week - never rewards remembering that
        the answer was C.
        """
        from ...core.quiz_session import fresh_choice_order
        saved = self.ctx.store.setting("review_correct_at", None)
        saved = dict(saved) if isinstance(saved, dict) else {}
        last = saved.get(card.id)
        order = fresh_choice_order(len(card.choices), card.correct, self.rng,
                                   last if isinstance(last, int) else None)
        if card.correct in order:
            saved[card.id] = order.index(card.correct)
            self.ctx.store.set_setting("review_correct_at", saved)
        return order
    @staticmethod
    def _option_text(index: int, choice: str) -> str:
        if index >= len(OPTION_KEYS):
            return choice
        return "%s.  %s" % (OPTION_KEYS[index], choice)

    def _answered(self) -> None:
        """Take away Check/Reveal and Skip once the card has been answered.

        Left live, a second press drew a second result and a second row of
        ratings, and Skip let a card be dropped after its answer was seen.
        """
        for control in getattr(self, "_card_controls", ()):
            control.setVisible(False)
        self._card_controls = ()

    def _check_choice(self) -> None:
        if self.group is None or not getattr(self, "_card_controls", ()):
            return
        chosen = self.group.checkedId()
        if chosen < 0:
            self.ctx.announce("Pick an answer first.")
            return
        self._answered()
        elapsed = time.monotonic() - self.shown_at
        correct = chosen == self.card.correct
        for widget in self.group.buttons():
            widget.setEnabled(False)

        question = self.ctx.curriculum.question(self.card.id)
        result = Card()
        result.add(pill("CORRECT" if correct else "NOT QUITE",
                        "done" if correct else "bad"))
        if not correct:
            result.add(label("The answer was: %s"
                             % self.card.choices[self.card.correct], "Soft"))
        note = choice_feedback(question, chosen) if question else ""
        if note:
            result.add(label("About the one you picked: %s" % note, "Soft"))
        result.add(label(self.card.back, "Soft"))
        self.stage.addWidget(result)

        if correct:
            hesitated = elapsed > 25
            self._rating_buttons(
                suggested=Rating.HARD if hesitated else Rating.GOOD)
            return
        card = self.card
        self._hold_after_rating = True
        self._apply(Rating.AGAIN)
        if self._pending_next:
            self._after_wrong(card, question)

    def taught_at(self, card=None) -> str:
        """Where "Where this is taught" goes: the line, or else the phase."""
        card = card or self.card
        if card is None:
            return ""
        question = self.ctx.curriculum.question(card.id)
        item_id = (teaching_item(self.ctx.curriculum, question)
                   if question is not None else "")
        return item_id or card.phase

    def _after_wrong(self, card, question) -> None:
        """The row under a wrong answer: back to the material, or move on."""
        row = QHBoxLayout()
        row.setSpacing(8)
        target = self.taught_at(card)
        taught = button("Where this is taught", "quiet",
                        "Open the phase page at the line this question tests")
        taught.clicked.connect(
            lambda _=False, t=target: self.ctx.navigate.emit("phase", t))
        row.addWidget(taught)
        row.addStretch(1)
        nxt = button("Next card  (Space)", "primary",
                     "Space or Enter - this one is already rated Again")
        nxt.clicked.connect(self._continue)
        row.addWidget(nxt)
        self.stage.addLayout(row)
        self._wrong_controls = (taught, nxt)
        if self.isVisible():
            self.setFocus()

    def _continue(self) -> None:
        """Leave a wrong answer's explanation for the next card."""
        if not self._pending_next:
            return
        self._pending_next = False
        self._wrong_controls = ()
        self.card = None
        self._next_card()

    def _reveal_concept(self) -> None:
        if not getattr(self, "_card_controls", ()):
            return
        self._answered()
        self.revealed = True
        result = Card()
        result.add(heading("The gate check" if self.card.kind == GATE
                           else "The line"))
        answer = label(self.card.back)
        answer.setStyleSheet("font-size: 15px;")
        result.add(answer)
        note = self.ctx.review.gate_note(self.card)
        if note:
            result.add(muted("Phase gate: %s" % note))
        self.stage.addWidget(result)
        self._rating_buttons(suggested=Rating.GOOD)

    def _rating_buttons(self, suggested: Rating) -> None:
        holder = Card(flat=True, padding=14, spacing=8)
        holder.add(muted("How did that go?"))
        row = QHBoxLayout()
        row.setSpacing(8)
        preview = self.ctx.review.preview(self.card)
        for rating in (Rating.AGAIN, Rating.HARD, Rating.GOOD, Rating.EASY):
            text, kind, tip = RATING_LABEL[rating]
            key = RATING_KEY[rating]
            # The word stays alone on the first line: the second line carries
            # the key and the interval, so the buttons still read as a scale.
            widget = button(
                "%s\n(%s)  %s" % (text, key,
                                  describe_interval(preview[rating])),
                kind if rating is not suggested else "primary",
                "%s - press %s" % (tip, key))
            widget.setMinimumHeight(46)
            widget.clicked.connect(
                lambda _=False, r=rating: self._apply(r))
            row.addWidget(widget, 1)
        holder.box.addLayout(row)
        bury = button("Bury this card", "quiet",
                      "Stop showing it. Restore it from the review summary.")
        bury.clicked.connect(self._bury)
        holder.add_row(bury, None)
        self.stage.addWidget(holder)
        self._rating_live = True

    def _apply(self, rating: Rating) -> None:
        card = self.card
        if card is None:
            return
        previous = card.memory
        self.ctx.review.answer(card, rating)
        self.done_today += 1
        self._last_answer = (card, rating, previous)
        self.ctx.record("review answer",
                        lambda: self._undo_answer(card, previous),
                        lambda: self._redo_answer(card, rating))
        self.ctx.changed()
        self._rating_live = False
        if self._hold_after_rating:
            # A wrong choice: rated, and left on screen to be read.
            self._hold_after_rating = False
            self._pending_next = True
            self._update_tiles()
            return
        self.card = None
        self._update_tiles()
        self._next_card()

    # -- taking an answer back ---------------------------------------------

    def _undo_last(self) -> None:
        """The header button. One implementation, shared with Ctrl+Z."""
        if self._last_answer is not None:
            self.ctx.undo()

    def _undo_answer(self, card, previous) -> None:
        self.ctx.review.undo_answer(card, previous)
        self._last_answer = None
        self.done_today = max(0, self.done_today - 1)
        self.dropped.discard(card.id)
        self.ctx.announce("Answer taken back.")
        self.ctx.changed()
        if not self._built:
            # Undone from another page after this one was torn down. The
            # store is right; the next visit builds a session that has it.
            self.queue = []
            self.card = None
            return
        if self._pending_next:
            # The card on screen is the one being taken back.
            self._pending_next = False
            self.card = None
        if self.card is not None:
            self.queue.insert(0, self.card)
        self.queue.insert(0, card)      # back at the front, where it was
        self.card = None
        self._update_tiles()
        self._next_card()

    def _redo_answer(self, card, rating) -> None:
        self.ctx.review.answer(card, rating)
        self.done_today += 1
        self._last_answer = (card, rating, card.memory)
        self.ctx.changed()
        if not self._built:
            self.queue = []
            self.card = None
            return
        self.queue = [item for item in self.queue if item.id != card.id]
        if self.card is not None and self.card.id == card.id:
            self.card = None
            self._pending_next = False
            self._rating_live = False
            self._update_tiles()
            self._next_card()
        else:
            self._update_tiles()

    # -- skipping ----------------------------------------------------------

    def _skip(self) -> None:
        """Put the card back - but only once.

        Appending every time made a queue of one card that could never be
        emptied: the learner skipped, was handed the same card, skipped
        again, forever. The second skip is taken as an answer of a kind.
        """
        card = self.card
        if card is None:
            self._next_card()
            return
        if self._pending_next:
            self._continue()            # answered already: nothing to skip
            return
        self.card = None
        self._rating_live = False
        count = self.skips.get(card.id, 0) + 1
        self.skips[card.id] = count
        if count >= SKIP_LIMIT:
            self.dropped.add(card.id)
            self.ctx.announce("Skipped twice - it will come back tomorrow.")
        else:
            self.queue.append(card)
        self._next_card()

    def _session_finished(self) -> None:
        self.card = None
        self._pending_next = False
        self._rating_live = False
        clear_layout(self.stage)
        self.session_meter.setValue(self.session_meter.maximum())
        card = Card()
        card.add(label("Queue clear.", "Big", wrap=False))
        card.add(label(
            "%d card%s reviewed. Everything you got wrong will come back "
            "sooner than the rest." % (self.done_today,
                                       "" if self.done_today == 1 else "s"),
            "Soft"))
        again = button("Check for more", "quiet")
        again.clicked.connect(self._start_or_idle)
        card.add_row(None, again)
        self._add_buried_row(card)
        self.stage.addWidget(card)
        self._update_tiles()

    # -- the keyboard ------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        """Space to reveal, a letter to pick, 1-4 to rate, S to skip.

        Review is the page opened every single day, and it was the one page
        with no keys at all. Nothing here animates: a key press is an
        instruction, not a gesture, and a card that slid in would only make
        the next key land late.
        """
        if self._handle_key(event):
            event.accept()
            return
        super().keyPressEvent(event)

    def _handle_key(self, event) -> bool:
        if self.card is None or _is_typing():
            return False
        # Ctrl, Alt and Meta belong to the window's own shortcuts - Ctrl+Z
        # in particular, which is how an answer is taken back.
        claimed = (Qt.KeyboardModifier.ControlModifier
                   | Qt.KeyboardModifier.AltModifier
                   | Qt.KeyboardModifier.MetaModifier)
        if event.modifiers() & claimed:
            return False
        key = event.key()
        typed = event.text().upper()

        if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._pending_next:
                self._continue()
                return True
            return self._key_answer()
        if typed in KEY_RATING and self._rating_live:
            self._apply(KEY_RATING[typed])
            return True
        if typed == "S" and getattr(self, "_card_controls", ()):
            self._skip()
            return True
        if typed and typed in OPTION_KEYS:
            return self._key_option(OPTION_KEYS.index(typed))
        return False

    def _key_answer(self) -> bool:
        """Space and Enter: reveal a concept, or check a chosen option."""
        if not getattr(self, "_card_controls", ()):
            return False        # already answered: rate it with 1-4
        if self.card.kind == QUIZ:
            self._check_choice()
        else:
            self._reveal_concept()
        return True

    def _key_option(self, index: int) -> bool:
        """A letter picks the option drawn at that letter, not a stored slot."""
        if self.group is None or not getattr(self, "_card_controls", ()):
            return False
        if not 0 <= index < len(self.shown_order):
            return False
        option = self.group.button(self.shown_order[index])
        if option is None or not option.isEnabled():
            return False
        option.setChecked(True)
        return True
