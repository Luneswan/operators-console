"""Spaced review: the thing that stops phase 1 leaking away by phase 8."""
from __future__ import annotations

import time

from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QRadioButton, QVBoxLayout

from ...core.review import QUIZ
from ...core.srs import Rating, describe_interval
from ..widgets.common import (
    Card, StatTile, button, divider, heading, label, meter, muted, pill,
)
from .base import View

RATING_LABEL = {
    Rating.AGAIN: ("Again", "bad", "I could not recall it"),
    Rating.HARD: ("Hard", "", "I got there, slowly"),
    Rating.GOOD: ("Good", "", "I knew it"),
    Rating.EASY: ("Easy", "good", "Instant - show it far less often"),
}


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

    def _start_or_idle(self) -> None:
        self.queue = self.ctx.review.session()
        self.done_today = 0
        if not self.queue:
            self._idle_screen()
        else:
            self._next_card()

    def _idle_screen(self) -> None:
        _empty(self.stage)
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

    # -- one card ----------------------------------------------------------

    def _next_card(self) -> None:
        if not self.queue:
            self._session_finished()
            return
        self.card = self.queue.pop(0)
        self.revealed = False
        self.shown_at = time.monotonic()
        self.session_meter.setVisible(True)
        self.session_meter.setRange(0, self.done_today + len(self.queue) + 1)
        self.session_meter.setValue(self.done_today)
        self._render_front()

    def _render_front(self) -> None:
        _empty(self.stage)
        phase = self.ctx.curriculum.phase(self.card.phase)
        card = Card()
        top = QHBoxLayout()
        top.addWidget(pill(phase.num if phase else "--"))
        top.addWidget(muted(phase.name if phase else ""), 1)
        top.addWidget(pill("NEW" if self.card.is_new else "REVIEW",
                           "warn" if self.card.is_new else ""))
        card.box.addLayout(top)

        prompt = label(self.card.front)
        prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
        card.add(prompt)

        if self.card.kind == QUIZ:
            self.group = QButtonGroup(card)
            self.group.setExclusive(True)
            for index, choice in enumerate(self.card.choices):
                option = QRadioButton(choice)
                option.setStyleSheet("padding: 5px 0; font-size: 13px;")
                self.group.addButton(option, index)
                card.add(option)
            action = button("Check", "primary")
            action.clicked.connect(self._check_choice)
        else:
            self.group = None
            card.add(muted("Say the answer out loud, then reveal it."))
            action = button("Reveal", "primary")
            action.clicked.connect(self._reveal_concept)

        self.stage.addWidget(card)
        controls = QHBoxLayout()
        skip = button("Skip for now", "quiet")
        skip.clicked.connect(self._skip)
        controls.addWidget(skip)
        controls.addStretch(1)
        controls.addWidget(action)
        self.stage.addLayout(controls)

    def _check_choice(self) -> None:
        if self.group is None:
            return
        chosen = self.group.checkedId()
        if chosen < 0:
            self.ctx.announce("Pick an answer first.")
            return
        elapsed = time.monotonic() - self.shown_at
        correct = chosen == self.card.correct
        for widget in self.group.buttons():
            widget.setEnabled(False)

        result = Card()
        result.add(pill("CORRECT" if correct else "NOT QUITE",
                        "done" if correct else "bad"))
        if not correct:
            result.add(label("The answer was: %s"
                             % self.card.choices[self.card.correct], "Soft"))
        result.add(label(self.card.back, "Soft"))
        self.stage.addWidget(result)

        if correct:
            hesitated = elapsed > 25
            self._rating_buttons(
                suggested=Rating.HARD if hesitated else Rating.GOOD)
        else:
            self._apply(Rating.AGAIN)

    def _reveal_concept(self) -> None:
        self.revealed = True
        result = Card()
        result.add(heading("The line you saved"))
        answer = label(self.card.back)
        answer.setStyleSheet("font-size: 15px;")
        result.add(answer)
        self.stage.addWidget(result)
        self._rating_buttons(suggested=Rating.GOOD)

    def _rating_buttons(self, suggested: Rating) -> None:
        holder = Card(flat=True, padding=0, spacing=6)
        holder.add(muted("How did that go?"))
        row = QHBoxLayout()
        row.setSpacing(8)
        preview = self.ctx.review.preview(self.card)
        for rating in (Rating.AGAIN, Rating.HARD, Rating.GOOD, Rating.EASY):
            text, kind, tip = RATING_LABEL[rating]
            widget = button(
                "%s\n%s" % (text, describe_interval(preview[rating])),
                kind if rating is not suggested else "primary", tip)
            widget.setMinimumHeight(46)
            widget.clicked.connect(
                lambda _=False, r=rating: self._apply(r))
            row.addWidget(widget, 1)
        holder.box.addLayout(row)
        self.stage.addWidget(holder)

    def _apply(self, rating: Rating) -> None:
        if self.card is None:
            return
        self.ctx.review.answer(self.card, rating)
        self.done_today += 1
        self.ctx.changed()
        self.card = None
        self._update_tiles()
        self._next_card()

    def _skip(self) -> None:
        if self.card is not None:
            self.queue.append(self.card)
            self.card = None
        self._next_card()

    def _session_finished(self) -> None:
        self.card = None
        _empty(self.stage)
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
        self.stage.addWidget(card)
        self._update_tiles()


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
