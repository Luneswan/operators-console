"""Quizzes: a graded run through one phase's questions, with explanations."""
from __future__ import annotations

import random
import time

from PySide6.QtWidgets import (
    QButtonGroup, QHBoxLayout, QRadioButton, QVBoxLayout,
)

from ...core.srs import Rating
from ..widgets.common import (
    Card, button, divider, heading, label, meter, muted, pill,
)
from .base import View


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

    def build(self) -> None:
        self.kicker = label("", "PageKicker", wrap=False)
        self.scroller.add(self.kicker)
        self.title_label = label("", "PageTitle")
        self.scroller.add(self.title_label)
        self.desc = label("", "PageAim")
        self.scroller.add(self.desc)
        self.progress = meter(0)
        self.scroller.add(self.progress)
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
        if self.quiz is None:
            self._pick_screen()

    def _pick_screen(self) -> None:
        _empty(self.stage)
        self.kicker.setText("SELF CHECK")
        self.title_label.setText("Quizzes")
        self.desc.setText(
            "One quiz per phase. Questions you get wrong are added to your "
            "review deck automatically.")
        self.progress.setVisible(False)
        for quiz in self.ctx.curriculum.quizzes:
            phase = self.ctx.curriculum.phase(quiz.phase)
            card = Card()
            row = QHBoxLayout()
            row.setSpacing(9)
            row.addWidget(pill(phase.num if phase else "--"))
            title = label(quiz.name, wrap=False)
            title.setStyleSheet("font-weight: 700; font-size: 14px;")
            row.addWidget(title, 1)
            best = self.ctx.store.best_quiz_score(quiz.id)
            if best:
                tone = "done" if best[0] / best[1] >= 0.8 else "warn"
                row.addWidget(pill("BEST %d/%d" % best, tone))
            start = button("Start", "primary" if not best else "")
            start.clicked.connect(lambda _=False, q=quiz: self._start(q))
            row.addWidget(start)
            card.box.addLayout(row)
            card.add(muted("%s  -  %d questions" % (quiz.desc,
                                                    len(quiz.questions))))
            self.stage.addWidget(card)

    def _start(self, quiz) -> None:
        self.quiz = quiz
        self.order = list(range(len(quiz.questions)))
        random.shuffle(self.order)
        self.position = 0
        self.answers = {}
        self.started = time.monotonic()
        phase = self.ctx.curriculum.phase(quiz.phase)
        self.kicker.setText("QUIZ  -  PHASE %s" % (phase.num if phase else "--"))
        self.title_label.setText(quiz.name)
        self.desc.setText(quiz.desc)
        self.progress.setVisible(True)
        self._render_question()

    # -- one question ------------------------------------------------------

    def _render_question(self) -> None:
        _empty(self.stage)
        question = self.quiz.questions[self.order[self.position]]
        self.progress.setRange(0, len(self.order))
        self.progress.setValue(self.position)

        card = Card()
        card.add(muted("Question %d of %d"
                       % (self.position + 1, len(self.order))))
        prompt = label(question.prompt)
        prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
        card.add(prompt)

        self.group = QButtonGroup(card)
        self.group.setExclusive(True)
        for index, choice in enumerate(question.choices):
            option = QRadioButton(choice)
            option.setStyleSheet("padding: 5px 0; font-size: 13px;")
            self.group.addButton(option, index)
            card.add(option)
        self.stage.addWidget(card)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        skip = button("Skip", "quiet")
        skip.clicked.connect(lambda: self._answer(-1))
        controls.addWidget(skip)
        controls.addStretch(1)
        submit = button("Check answer", "primary")
        submit.clicked.connect(
            lambda: self._answer(self.group.checkedId()))
        controls.addWidget(submit)
        self.stage.addLayout(controls)

    def _answer(self, chosen: int) -> None:
        question = self.quiz.questions[self.order[self.position]]
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
        card.add(label(question.explain, "Soft"))
        self.stage.addWidget(card)

        # A wrong answer goes straight into spaced repetition.
        rating = Rating.GOOD if correct else Rating.AGAIN
        cards = {c.id: c for c in self.ctx.review.all_cards()}
        card_obj = cards.get(question.id)
        if card_obj is not None:
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

    def _advance(self) -> None:
        if self.position >= len(self.order) - 1:
            self._finish()
            return
        self.position += 1
        self._render_question()

    def _finish(self) -> None:
        _empty(self.stage)
        questions = {q.id: q for q in self.quiz.questions}
        score = sum(1 for qid, chosen in self.answers.items()
                    if chosen == questions[qid].correct)
        total = len(self.quiz.questions)
        seconds = int(time.monotonic() - self.started)
        self.ctx.store.record_quiz(self.quiz.id, score, total, seconds)
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
        self._pick_screen()


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
