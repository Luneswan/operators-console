"""Quizzes: a graded run through one phase's questions, with explanations."""
from __future__ import annotations

import random
import time

from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QHBoxLayout, QLineEdit, QMessageBox,
    QRadioButton, QVBoxLayout, QWidget,
)

from ...core.progress import QUIZ_PROOF
from ...core.review import choice_feedback, choice_order, valid_order
from ...core.srs import Rating
from ..widgets.common import (
    Card, Disclosure, button, clear_layout, divider, heading, label, meter,
    muted, pill,
)
from .base import View

try:                                    # another change adds a shared matcher
    from ...core import textmatch as _textmatch
except ImportError:                     # pragma: no cover - until it lands
    _textmatch = None

#: The SHOW filter on the picker. A quiz counts as passed at the same score
#: that proves a phase, so the two never disagree about what "passed" means.
SHOW_ALL = "All quizzes"
SHOW_NEW = "Not attempted"
SHOW_BELOW = "Below %d%%" % round(QUIZ_PROOF * 100)
SHOW_PASSED = "Passed"
SHOW_CHOICES = (SHOW_ALL, SHOW_NEW, SHOW_BELOW, SHOW_PASSED)


class QuizView(View):
    title = "Quiz"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(ctx, parent)
        self.quiz = None
        self.order: list = []
        self.position = 0
        self.answers: dict = {}
        self.started = 0.0
        self.group = None
        # question id -> the stored choice index drawn at each position.
        self.choice_orders: dict = {}
        self.rng = random.Random()

    def build(self) -> None:
        self.kicker = label("", "PageKicker", wrap=False)
        self.scroller.add(self.kicker)
        self.title_label = label("", "PageTitle")
        self.scroller.add(self.title_label)
        self.desc = label("", "PageAim")
        self.scroller.add(self.desc)
        self.progress = meter(0)
        self.scroller.add(self.progress)

        # Nineteen quizzes, most of them outside a short track, needed a way
        # in that is not reading every card.
        self.filters = QWidget()
        row = QHBoxLayout(self.filters)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search quiz names and descriptions")
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName("Search the quizzes")
        row.addWidget(muted("FIND"))
        row.addWidget(self.search, 1)
        self.show_filter = QComboBox()
        self.show_filter.addItems(list(SHOW_CHOICES))
        self.show_filter.setAccessibleName("Filter quizzes by your score")
        row.addWidget(muted("SHOW"))
        row.addWidget(self.show_filter)
        self.counter = muted("")
        row.addWidget(self.counter)
        self.search.textChanged.connect(lambda _t: self._refilter())
        self.show_filter.currentIndexChanged.connect(
            lambda _i: self._refilter())
        self.scroller.add(self.filters)
        self.scroller.add(divider())

        self.stage = QVBoxLayout()
        self.stage.setSpacing(12)
        self.scroller.add_layout(self.stage)
        self.scroller.add_stretch()

    # -- entry -------------------------------------------------------------

    def show_target(self, target: str) -> None:
        self.ensure_built()
        quiz = self.ctx.curriculum.quiz(target)
        if quiz is None:
            quizzes = self.ctx.curriculum.quizzes_for(target)
            quiz = quizzes[0] if quizzes else None
        if quiz is not None:
            self._start(quiz)

    def refresh(self) -> None:
        if self.quiz is None and not self.store_unchanged():
            self._pick_screen()
            self.mark_drawn()

    @property
    def busy(self) -> bool:
        return self.quiz is not None        # an attempt is under way

    def save_state(self):
        """The picker's filters, so a theme change does not empty them."""
        text, show = self.search.text(), self.show_filter.currentIndex()
        if not text and show <= 0:
            return None
        return {"text": text, "show": show}

    def restore_state(self, state) -> None:
        if not isinstance(state, dict):
            return
        self.search.setText(str(state.get("text") or ""))
        show = state.get("show", 0)
        if isinstance(show, int) and 0 <= show < self.show_filter.count():
            self.show_filter.setCurrentIndex(show)

    def _pick_screen(self) -> None:
        clear_layout(self.stage)
        self.kicker.setText("SELF CHECK")
        self.title_label.setText("Quizzes")
        self.desc.setText(
            "One quiz per phase. The questions are shuffled every time, and "
            "the ones you get wrong join your review deck, with the line that "
            "teaches them.")
        self.progress.setVisible(False)
        self.filters.setVisible(True)
        self._offer_resume()
        self._fill_picker()

    def _refilter(self) -> None:
        if self.quiz is None and self._built:
            self._pick_screen()

    def _status(self, quiz) -> str:
        best = self.ctx.store.best_quiz_score(quiz.id)
        if not best or not best[1]:
            return SHOW_NEW
        return (SHOW_PASSED if best[0] / best[1] >= QUIZ_PROOF - 1e-9
                else SHOW_BELOW)

    def visible_quizzes(self) -> tuple:
        """``(in the plan, outside it)`` after the FIND and SHOW filters."""
        needle = self.search.text().strip()
        show = self.show_filter.currentText() or SHOW_ALL
        plan = set(self.ctx.progress.active_phase_ids())
        order = {pid: index for index, pid in
                 enumerate(self.ctx.progress.active_phase_ids())}
        inside, outside = [], []
        for quiz in self.ctx.curriculum.quizzes:
            if needle and not quiz_matches(quiz, needle):
                continue
            if show != SHOW_ALL and self._status(quiz) != show:
                continue
            (inside if quiz.phase in plan else outside).append(quiz)
        inside.sort(key=lambda q: order.get(q.phase, len(order)))
        return inside, outside

    def _fill_picker(self) -> None:
        inside, outside = self.visible_quizzes()
        total = len(self.ctx.curriculum.quizzes)
        shown = len(inside) + len(outside)
        passed = sum(1 for q in self.ctx.curriculum.quizzes
                     if self._status(q) == SHOW_PASSED)
        text = "%d of %d passed" % (passed, total)
        if shown != total:
            text = "%d shown  -  %s" % (shown, text)
        self.counter.setText(text)

        for quiz in inside:
            self.stage.addWidget(self._quiz_card(quiz))
        if outside:
            filtering = bool(self.search.text().strip()
                             or self.show_filter.currentIndex() > 0)
            # Folded, never hidden: every quiz stays startable. A search that
            # only matches out here opens the fold rather than looking empty.
            more = Disclosure(
                len(outside),
                "quiz%s outside your track" % ("" if len(outside) == 1
                                               else "zes"),
                store=None if filtering else self.ctx.store,
                key="" if filtering else "quiz:outside-track", tag="")
            for quiz in outside:
                more.add(self._quiz_card(quiz, in_plan=False))
            if filtering and not inside:
                more.set_open(True, animate=False)
            self.stage.addWidget(more)
        if not shown:
            self.stage.addWidget(muted(
                "No quiz matches. Clear the search or set SHOW to %s."
                % SHOW_ALL))

    def _quiz_card(self, quiz, in_plan: bool = True) -> Card:
        phase = self.ctx.curriculum.phase(quiz.phase)
        card = Card()
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(pill(phase.num if phase else "--"))
        title = label(quiz.name, "RowTitle", wrap=False)
        row.addWidget(title, 1)
        if not in_plan:
            row.addWidget(pill("NOT IN YOUR PLAN"))
        best = self.ctx.store.best_quiz_score(quiz.id)
        if best:
            tone = ("done" if best[1] and best[0] / best[1] >= QUIZ_PROOF
                    - 1e-9 else "warn")
            row.addWidget(pill("BEST %d/%d" % best, tone))
        start = button("Start", "primary" if not best and in_plan else "")
        start.setAccessibleName("Start %s" % quiz.name)
        start.clicked.connect(lambda _=False, q=quiz: self._start(q))
        row.addWidget(start)
        card.box.addLayout(row)
        card.add(muted("%s  -  %d questions" % (quiz.desc,
                                                len(quiz.questions))))
        return card

    # -- an attempt you can walk away from ---------------------------------

    def _offer_resume(self) -> None:
        """The attempt the app was closed in the middle of, on the picker."""
        saved = self._saved_attempt()
        if saved is None:
            return
        quiz, order, position, answers, _orders = saved
        card = Card(padding=16, spacing=8)
        card.setObjectName("FocusCard")
        card.add(label("UNFINISHED", "PageKicker", wrap=False))
        card.add(label(quiz.name, "FocusTitle"))
        card.add(muted(
            "You stopped at question %d of %d, with %d answered. Everything "
            "you answered is already scored and in your review deck."
            % (min(position + 1, len(order)), len(order), len(answers))))
        row = QHBoxLayout()
        row.setSpacing(8)
        resume = button("Resume", "primary")
        resume.clicked.connect(self._resume)
        row.addWidget(resume)
        over = button("Start over", "quiet")
        over.clicked.connect(lambda _=False, q=quiz: self._restart(q))
        row.addWidget(over)
        row.addStretch(1)
        card.box.addLayout(row)
        self.stage.addWidget(card)

    def _saved_attempt(self):
        """The stored attempt, or None when there is nothing usable.

        The curriculum can be replaced by an update under a saved attempt, so
        every index is checked against the quiz as it is now.
        """
        saved = self.ctx.store.setting("quiz_in_progress", None)
        if not isinstance(saved, dict):
            return None
        quiz = self.ctx.curriculum.quiz(str(saved.get("quiz_id") or ""))
        if quiz is None:
            return None
        order = [i for i in (saved.get("order") or [])
                 if isinstance(i, int) and 0 <= i < len(quiz.questions)]
        if len(order) != len(quiz.questions) or len(set(order)) != len(order):
            return None
        position = saved.get("position", 0)
        if not isinstance(position, int) or not 0 <= position < len(order):
            return None
        answers = saved.get("answers")
        if not isinstance(answers, dict):
            answers = {}
        known = {q.id for q in quiz.questions}
        answers = {qid: value for qid, value in answers.items()
                   if qid in known and isinstance(value, int)}
        # The order the choices were drawn in. An attempt saved by a build
        # that did not shuffle has none; its questions get a fresh one.
        sizes = {q.id: len(q.choices) for q in quiz.questions}
        raw = saved.get("choices")
        orders = {}
        if isinstance(raw, dict):
            orders = {qid: list(value) for qid, value in raw.items()
                      if qid in sizes and valid_order(value, sizes[qid])}
        return quiz, order, position, answers, orders

    def _remember(self) -> None:
        """Write the attempt down on every answer.

        Closing the app in the middle of a quiz used to throw the whole
        attempt away without ever saying that it would.
        """
        if self.quiz is None:
            return
        self.ctx.store.set_setting("quiz_in_progress", {
            "quiz_id": self.quiz.id,
            "order": [int(i) for i in self.order],
            "position": int(self.position),
            "answers": {str(k): int(v) for k, v in self.answers.items()},
            "choices": {str(k): [int(i) for i in v]
                        for k, v in self.choice_orders.items()},
        })

    def _forget(self) -> None:
        if self.ctx.store.setting("quiz_in_progress", None) is not None:
            self.ctx.store.set_setting("quiz_in_progress", None)

    def _resume(self) -> None:
        saved = self._saved_attempt()
        if saved is None:
            self._forget()
            self._pick_screen()
            return
        quiz, order, position, answers, orders = saved
        self.quiz = quiz
        self.order = order
        self.answers = answers
        self.choice_orders = orders
        self.started = time.monotonic()
        self._head(quiz)
        if len(answers) >= len(order):
            # Closed on the last explanation: the score is still owed.
            self.position = len(order) - 1
            self._finish()
            return
        while (position < len(order) - 1
               and quiz.questions[order[position]].id in answers):
            position += 1
        self.position = position
        self._render_question()

    def _restart(self, quiz) -> None:
        self._forget()
        self._start(quiz)

    def _leave(self) -> None:
        confirm = QMessageBox.question(
            self, "Leave this quiz?",
            "What you have answered is already scored and scheduled for "
            "review.\n\nThe rest of this attempt is dropped, and the quiz "
            "starts from the beginning next time. Leave it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._forget()
        self._reset_to_picker()
        self.ctx.announce("Left the quiz. Nothing you answered was lost.")

    # -- one attempt -------------------------------------------------------

    def _head(self, quiz) -> None:
        phase = self.ctx.curriculum.phase(quiz.phase)
        self.kicker.setText("QUIZ  -  PHASE %s" % (phase.num if phase else "--"))
        self.title_label.setText(quiz.name)
        self.desc.setText(quiz.desc)
        self.progress.setVisible(True)
        self.filters.setVisible(False)

    def _start(self, quiz) -> None:
        self.quiz = quiz
        self.order = list(range(len(quiz.questions)))
        self.rng.shuffle(self.order)
        self.position = 0
        self.answers = {}
        self.choice_orders = {}
        self.started = time.monotonic()
        self._head(quiz)
        self._render_question()

    # -- one question ------------------------------------------------------

    def _render_question(self) -> None:
        clear_layout(self.stage)
        question = self.quiz.questions[self.order[self.position]]
        self.progress.setRange(0, len(self.order))
        self.progress.setValue(self.position)

        card = Card()
        card.add(muted("Question %d of %d"
                       % (self.position + 1, len(self.order))))
        prompt = label(question.prompt)
        prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
        card.add(prompt)

        # Drawn in a shuffled order, but every button's id is the choice's
        # stored index, so what is scored, stored and rated never depends on
        # where the choice happened to be drawn.
        self.group = QButtonGroup(card)
        self.group.setExclusive(True)
        for stored in self.choices_shown(question):
            option = QRadioButton(question.choices[stored])
            option.setStyleSheet("padding: 5px 0; font-size: 13px;")
            self.group.addButton(option, stored)
            card.add(option)
        self.stage.addWidget(card)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        # It was labelled "Skip" and scored as a wrong answer without a word.
        skip = button("Skip (counts as wrong)", "quiet",
                      "Scored as a wrong answer, so this question comes back "
                      "sooner in your review deck.")
        skip.clicked.connect(lambda: self._answer(-1))
        controls.addWidget(skip)
        leave = button("Leave this quiz", "quiet")
        leave.clicked.connect(self._leave)
        controls.addWidget(leave)
        controls.addStretch(1)
        submit = button("Check answer", "primary")
        submit.clicked.connect(
            lambda: self._answer(self.group.checkedId()))
        controls.addWidget(submit)
        self.stage.addLayout(controls)
        self._question_controls = (skip, submit)

    def choices_shown(self, question) -> list:
        """Stored choice indexes in the order this attempt draws them.

        Made once per question per attempt and saved with it, so a resumed
        attempt shows the same order it was answered in.
        """
        order = self.choice_orders.get(question.id)
        if not valid_order(order, len(question.choices)):
            order = choice_order(len(question.choices), self.rng)
            self.choice_orders[question.id] = order
        return list(order)

    def _answer(self, chosen: int) -> None:
        question = self.quiz.questions[self.order[self.position]]
        if question.id in self.answers:
            return          # a second press would score, and schedule, twice
        # Gone as soon as the question is answered: left live, a second press
        # added another feedback card and another rating to the schedule.
        for control in getattr(self, "_question_controls", ()):
            control.setVisible(False)
        if chosen < 0 and self.group.checkedId() >= 0:
            chosen = self.group.checkedId()
        correct = chosen == question.correct
        self.answers[question.id] = chosen

        card = Card()
        card.add(pill("CORRECT" if correct else "NOT QUITE",
                      "done" if correct else "bad"))
        if not correct:
            card.add(label("The answer was: %s"
                           % question.choices[question.correct], "Soft"))
        note = choice_feedback(question, chosen)
        if note:
            card.add(label("About the one you picked: %s" % note, "Soft"))
        card.add(label(question.explain, "Soft"))
        self.stage.addWidget(card)

        # A wrong answer goes straight into spaced repetition.
        rating = Rating.GOOD if correct else Rating.AGAIN
        # Off-plan phases are not in the review deck yet; the answer still
        # counts, and the phase joins the deck now that it has been touched.
        card_obj = self.ctx.review.card_for_question(question, self.quiz)
        self.ctx.review.answer(card_obj, rating)

        controls = QHBoxLayout()
        controls.addStretch(1)
        last = self.position >= len(self.order) - 1
        nxt = button("See your score" if last else "Next question", "primary")
        nxt.clicked.connect(self._advance)
        controls.addWidget(nxt)
        self.stage.addLayout(controls)

        for button_widget in self.group.buttons():
            button_widget.setEnabled(False)
        self._remember()

    def _advance(self) -> None:
        if self.position >= len(self.order) - 1:
            self._finish()
            return
        self.position += 1
        # Drawn first, then saved: the saved attempt carries the order the
        # question on screen is shown in, so a resume shows the same one.
        self._render_question()
        self._remember()

    def _finish(self) -> None:
        clear_layout(self.stage)
        questions = {q.id: q for q in self.quiz.questions}
        score = sum(1 for qid, chosen in self.answers.items()
                    if chosen == questions[qid].correct)
        total = len(self.quiz.questions)
        seconds = int(time.monotonic() - self.started)
        self.ctx.store.record_quiz(self.quiz.id, score, total, seconds)
        self._forget()
        self.ctx.changed()

        self.progress.setValue(len(self.order))
        card = Card()
        ratio = score / total if total else 0
        card.add(label("%d / %d" % (score, total), "Big", wrap=False))
        verdict = ("Solid. Move on." if ratio >= 0.85
                   else "Close. Re-read the ones you missed, then retake it."
                   if ratio >= 0.6
                   else "Not yet. Go back to the phase before retaking this.")
        card.add(label(verdict, "Soft"))
        card.add(muted("Took %d minutes %d seconds. Everything you got wrong "
                       "is now scheduled for review."
                       % (seconds // 60, seconds % 60)))
        self.stage.addWidget(card)

        wrong = [questions[qid] for qid, chosen in self.answers.items()
                 if chosen != questions[qid].correct]
        if wrong:
            review_card = Card()
            review_card.add(heading("What to look at again"))
            for question in wrong:
                review_card.add(label(question.prompt, "Soft"))
                note = choice_feedback(question, self.answers.get(question.id,
                                                                  -1))
                if note:
                    review_card.add(muted(note))
                review_card.add(muted(question.explain))
            self.stage.addWidget(review_card)

        controls = QHBoxLayout()
        retake = button("Retake", "quiet")
        retake.clicked.connect(lambda: self._start(self.quiz))
        controls.addWidget(retake)
        back_to_phase = button("Back to the phase", "quiet")
        back_to_phase.clicked.connect(
            lambda: self.ctx.navigate.emit("phase", self.quiz.phase))
        controls.addWidget(back_to_phase)
        controls.addStretch(1)
        others = button("Other quizzes", "primary")
        others.clicked.connect(self._reset_to_picker)
        controls.addWidget(others)
        self.stage.addLayout(controls)

    def _reset_to_picker(self) -> None:
        self.quiz = None
        self.choice_orders = {}
        self._pick_screen()


def quiz_matches(quiz, needle: str) -> bool:
    """FIND on the picker: the quiz's name, description and id."""
    texts = (quiz.name, quiz.desc, quiz.id)
    if _textmatch is not None:
        # Every word, in any order, across the three fields - the same rule
        # as every other search box in the app.
        return _textmatch.matches(needle, *texts)
    folded = needle.casefold()
    return any(folded in (text or "").casefold() for text in texts)

