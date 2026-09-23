"""Quizzes: a graded run through one phase's questions, with explanations."""
from __future__ import annotations

import math
import random
import re
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox,
    QRadioButton, QVBoxLayout, QWidget,
)

from ...core.models import primary_of
from ...core.progress import QUIZ_PROOF
from ...core.quiz_session import (
    format_duration, fresh_choice_order, fresh_order, question_seconds,
    study_plan,
)
from ...core.review import choice_feedback, teaching_item, valid_order
from ...core.srs import Rating
from ..widgets.common import (
    Card, Disclosure, button, clear_layout, divider, heading, label, meter,
    muted, open_url, pill, repolish,
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

OPTION_KEYS = "ABCDEFGH"
#: The countdown turns amber for its last few seconds.
WARN_SECONDS = 10
TICK_MS = 200


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
        # The countdown: questions that ran out of time, and the seconds
        # spent answering each one (what "answering time" adds up).
        self.late: set = set()
        self.spent: dict = {}
        self.practice_round = False
        self.budget = 0
        self.question_started = 0.0
        self._saved_late: set = set()
        self._saved_spent: dict = {}
        self._tick = QTimer(self)
        self._tick.setInterval(TICK_MS)
        self._tick.timeout.connect(self._on_tick)

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
            "One quiz per phase. Questions and answers are reshuffled on "
            "every attempt. Each question is timed, and a late answer scores "
            "zero. Missed questions go to your review deck.")
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
            "Stopped at question %d of %d, %d answered. Answered questions "
            "are already scored."
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
        # Questions whose countdown ran out stay out of time after a restart:
        # closing the app is not a way to get the clock back.
        self._saved_late = {qid for qid in (saved.get("late") or [])
                            if qid in known}
        spent = saved.get("spent")
        self._saved_spent = ({qid: float(v) for qid, v in spent.items()
                              if qid in known and isinstance(v, (int, float))}
                             if isinstance(spent, dict) else {})
        return quiz, order, position, answers, orders

    def _remember(self) -> None:
        """Write the attempt down on every answer.

        Closing the app in the middle of a quiz used to throw the whole
        attempt away without ever saying that it would. A practice round of
        missed questions is not a quiz attempt and is not kept.
        """
        if self.quiz is None or self.practice_round:
            return
        self.ctx.store.set_setting("quiz_in_progress", {
            "quiz_id": self.quiz.id,
            "order": [int(i) for i in self.order],
            "position": int(self.position),
            "answers": {str(k): int(v) for k, v in self.answers.items()},
            "choices": {str(k): [int(i) for i in v]
                        for k, v in self.choice_orders.items()},
            "late": sorted(self.late),
            "spent": {str(k): round(float(v), 1)
                      for k, v in self.spent.items()},
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
        self.practice_round = False
        self.order = order
        self.answers = answers
        self.choice_orders = orders
        self.late = set(self._saved_late)
        self.spent = dict(self._saved_spent)
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
        self._tick.stop()
        confirm = QMessageBox.question(
            self, "Leave this quiz?",
            "Answered questions are already scored.\n\nThe rest of this "
            "attempt is discarded, and the quiz starts over next time. Leave?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            self._resume_clock()
            return
        self._forget()
        self._reset_to_picker()
        self.ctx.announce("Left the quiz. Your answers are saved.")

    # -- one attempt -------------------------------------------------------

    def _head(self, quiz) -> None:
        phase = self.ctx.curriculum.phase(quiz.phase)
        self.kicker.setText("QUIZ  -  PHASE %s" % (phase.num if phase else "--"))
        self.title_label.setText(quiz.name)
        self.desc.setText(quiz.desc)
        self.progress.setVisible(True)
        self.filters.setVisible(False)

    def _layouts(self) -> dict:
        saved = self.ctx.store.setting("quiz_layouts", None)
        return saved if isinstance(saved, dict) else {}

    def _last_layout(self, quiz_id: str) -> dict:
        layout = self._layouts().get(quiz_id)
        return layout if isinstance(layout, dict) else {}

    def _keep_layout(self, quiz_id: str, **changes) -> None:
        """Remember this attempt's layout, so the next one can avoid it."""
        layouts = self._layouts()
        layout = dict(layouts.get(quiz_id) or {})
        if "correct_at" in changes:
            merged = dict(layout.get("correct_at") or {})
            merged.update(changes.pop("correct_at"))
            layout["correct_at"] = merged
        layout.update(changes)
        layouts[quiz_id] = layout
        self.ctx.store.set_setting("quiz_layouts", layouts)

    def _start(self, quiz, only=None) -> None:
        """A new attempt, laid out unlike the last one.

        `only` is a list of question indexes for a practice round of the
        ones just missed: shuffled the same way, answered the same way, and
        not recorded as a quiz score.
        """
        self.quiz = quiz
        self.practice_round = only is not None
        if self.practice_round:
            self.order = list(only)
            self.rng.shuffle(self.order)
        else:
            last = self._last_layout(quiz.id).get("order")
            self.order = fresh_order(len(quiz.questions), self.rng, last)
            self._keep_layout(quiz.id, order=list(self.order))
        self.position = 0
        self.answers = {}
        self.choice_orders = {}
        self.late = set()
        self.spent = {}
        self._head(quiz)
        self._render_question()

    # -- one question ------------------------------------------------------

    def _render_question(self) -> None:
        self._tick.stop()
        clear_layout(self.stage)
        question = self.quiz.questions[self.order[self.position]]
        self.progress.setRange(0, len(self.order))
        self.progress.setValue(self.position)

        card = Card()
        top = QHBoxLayout()
        top.setSpacing(8)
        where = "Question %d of %d" % (self.position + 1, len(self.order))
        if self.practice_round:
            where += "  -  practice round, not scored"
        top.addWidget(muted(where), 1)
        self.clock = label("", "Mono", wrap=False)
        self.clock.setAccessibleName("Time left for this question")
        top.addWidget(self.clock, 0, Qt.AlignmentFlag.AlignRight)
        card.box.addLayout(top)
        self.clock_bar = meter(0, 1000)
        card.add(self.clock_bar)

        prompt = _rich(question.prompt)
        prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
        card.add(prompt)

        # Drawn in a shuffled order, but every button's id is the choice's
        # stored index, so what is scored, stored and rated never depends on
        # where the choice happened to be drawn. The letters follow the order
        # on screen, so the same answer rarely keeps its letter.
        self.group = QButtonGroup(card)
        self.group.setExclusive(True)
        for position, stored in enumerate(self.choices_shown(question)):
            option = QRadioButton(_option_text(
                position, _plain_code(question.choices[stored])))
            option.setStyleSheet("padding: 5px 0; font-size: 13px;")
            self.group.addButton(option, stored)
            card.add(option)
        self.clock_note = muted("")
        self.clock_note.setVisible(False)
        card.add(self.clock_note)
        self.stage.addWidget(card)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        # It was labelled "Skip" and scored as a wrong answer without a word.
        skip = button("Skip (counts as wrong)", "quiet",
                      "Counts as a wrong answer. It comes back sooner in "
                      "review.")
        skip.clicked.connect(lambda: self._answer(-1))
        controls.addWidget(skip)
        leave = button("Leave this quiz", "quiet")
        leave.clicked.connect(self._leave)
        controls.addWidget(leave)
        controls.addStretch(1)
        submit = button("Check answer", "primary",
                        "A to D picks an answer; Enter checks it")
        submit.clicked.connect(
            lambda: self._answer(self.group.checkedId()))
        controls.addWidget(submit)
        self.stage.addLayout(controls)
        self._question_controls = (skip, submit)

        self.budget = question_seconds(question)
        already = self.spent.get(question.id, 0.0)
        self.question_started = time.monotonic() - already
        self._show_clock()
        if question.id in self.late:
            self._time_up(question.id, save=False)
        else:
            self._tick.start()

    def _resume_clock(self) -> None:
        if (self.quiz is not None and self.group is not None
                and self._current_id() not in self.answers
                and self._current_id() not in self.late):
            self._tick.start()

    def _current_id(self) -> str:
        return self.quiz.questions[self.order[self.position]].id

    def _left(self) -> float:
        return self.budget - (time.monotonic() - self.question_started)

    def _show_clock(self) -> None:
        left = max(0.0, self._left())
        whole = int(math.ceil(left))
        self.clock.setText("%d:%02d" % divmod(whole, 60))
        self.clock_bar.setValue(int(1000 * left / self.budget)
                                if self.budget else 0)
        tone = "bad" if left <= 0 else "warn" if left <= WARN_SECONDS else ""
        if self.clock_bar.property("tone") != tone:
            self.clock_bar.setProperty("tone", tone)
            repolish(self.clock_bar)
            colour = {"bad": self.ctx.palette.bad,
                      "warn": self.ctx.palette.warn}.get(tone, "")
            self.clock.setStyleSheet(
                "font-weight: 700; color: %s;" % colour if colour
                else "font-weight: 700;")

    def _on_tick(self) -> None:
        if self.quiz is None or self.group is None:
            self._tick.stop()
            return
        self._show_clock()
        if self._left() <= 0:
            self._time_up(self._current_id())

    def _time_up(self, question_id: str, save: bool = True) -> None:
        self._tick.stop()
        self.late.add(question_id)
        self.clock.setText("0:00")
        self.clock_bar.setValue(0)
        self.budget = max(self.budget, 1)
        self.question_started = time.monotonic() - self.budget
        self._show_clock()
        self.clock_note.setText(
            "Time's up. You can still answer, but it will not score.")
        self.clock_note.setVisible(True)
        if save:
            self._remember()
            self.ctx.announce("Time's up on this question.")

    def choices_shown(self, question) -> list:
        """Stored choice indexes in the order this attempt draws them.

        Made once per question per attempt and saved with it, so a resumed
        attempt shows the same order it was answered in. A new attempt never
        puts the right answer under the letter it had last time.
        """
        order = self.choice_orders.get(question.id)
        if not valid_order(order, len(question.choices)):
            last = (self._last_layout(self.quiz.id).get("correct_at") or {}
                    ).get(question.id)
            order = fresh_choice_order(len(question.choices),
                                       question.correct, self.rng, last)
            self.choice_orders[question.id] = order
            if question.correct in order:
                self._keep_layout(self.quiz.id, correct_at={
                    question.id: order.index(question.correct)})
        return list(order)

    def _answer(self, chosen: int) -> None:
        question = self.quiz.questions[self.order[self.position]]
        if question.id in self.answers:
            return          # a second press would score, and schedule, twice
        self._tick.stop()
        # Gone as soon as the question is answered: left live, a second press
        # added another feedback card and another rating to the schedule.
        for control in getattr(self, "_question_controls", ()):
            control.setVisible(False)
        if chosen < 0 and self.group.checkedId() >= 0:
            chosen = self.group.checkedId()
        if self._left() <= 0:
            self.late.add(question.id)
        late = question.id in self.late
        self.spent[question.id] = min(self.budget,
                                      time.monotonic() - self.question_started)
        correct = chosen == question.correct
        self.answers[question.id] = chosen

        card = Card()
        if correct and late:
            card.add(pill("CORRECT, TOO LATE - NO MARK", "warn"))
        else:
            card.add(pill("CORRECT" if correct else "NOT QUITE",
                          "done" if correct else "bad"))
        if not correct:
            card.add(_rich("The answer was: %s"
                           % question.choices[question.correct], "Soft"))
        note = choice_feedback(question, chosen)
        if note:
            card.add(_rich("Why not that one: %s" % note, "Soft"))
        card.add(_rich(question.explain, "Soft"))
        self.stage.addWidget(card)

        # A wrong answer goes straight into spaced repetition; a right one
        # that needed longer than the clock is known, but not yet fluently.
        rating = (Rating.AGAIN if not correct
                  else Rating.HARD if late else Rating.GOOD)
        # Off-plan phases are not in the review deck yet; the answer still
        # counts, and the phase joins the deck now that it has been touched.
        card_obj = self.ctx.review.card_for_question(question, self.quiz)
        self.ctx.review.answer(card_obj, rating)

        controls = QHBoxLayout()
        controls.addStretch(1)
        last = self.position >= len(self.order) - 1
        nxt = button("See your score" if last else "Next question",
                     "primary", "Enter")
        nxt.clicked.connect(self._advance)
        controls.addWidget(nxt)
        self._next_button = nxt
        self.stage.addLayout(controls)

        for button_widget in self.group.buttons():
            button_widget.setEnabled(False)
        self._remember()

    # -- the keyboard ------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        """A to D picks the answer drawn at that letter; Enter checks it,
        and Enter again moves on - the same keys as the review page."""
        if self._handle_key(event):
            event.accept()
            return
        super().keyPressEvent(event)

    def _handle_key(self, event) -> bool:
        if self.quiz is None or self.group is None:
            return False
        focus = QApplication.focusWidget()
        if isinstance(focus, (QLineEdit, QComboBox)):
            return False
        claimed = (Qt.KeyboardModifier.ControlModifier
                   | Qt.KeyboardModifier.AltModifier
                   | Qt.KeyboardModifier.MetaModifier)
        if event.modifiers() & claimed:
            return False
        answered = self._current_id() in self.answers
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                           Qt.Key.Key_Space):
            if answered:
                nxt = getattr(self, "_next_button", None)
                if nxt is not None:
                    nxt.click()
                    return True
                return False
            if self.group.checkedId() >= 0:
                self._answer(self.group.checkedId())
                return True
            return False
        typed = event.text().upper()
        if typed and typed in OPTION_KEYS and not answered:
            order = self.choice_orders.get(self._current_id()) or []
            index = OPTION_KEYS.index(typed)
            if index < len(order):
                option = self.group.button(order[index])
                if option is not None and option.isEnabled():
                    option.setChecked(True)
                    return True
        return False

    def _advance(self) -> None:
        self._next_button = None
        if self.position >= len(self.order) - 1:
            self._finish()
            return
        self.position += 1
        # Drawn first, then saved: the saved attempt carries the order the
        # question on screen is shown in, so a resume shows the same one.
        self._render_question()
        self._remember()

    # -- results -----------------------------------------------------------

    def _finish(self) -> None:
        self._tick.stop()
        self.group = None
        self._next_button = None
        clear_layout(self.stage)
        asked = [self.quiz.questions[i] for i in self.order]
        right = [q for q in asked
                 if self.answers.get(q.id) == q.correct and q.id not in self.late]
        late_right = [q for q in asked
                      if self.answers.get(q.id) == q.correct and q.id in self.late]
        skipped = [q for q in asked if self.answers.get(q.id, -1) < 0]
        wrong = [q for q in asked if q not in right and q not in late_right]
        score, total = len(right), len(asked)
        seconds = int(round(sum(self.spent.values())))
        previous = self.ctx.store.best_quiz_score(self.quiz.id)
        if not self.practice_round:
            self.ctx.store.record_quiz(self.quiz.id, score, total, seconds)
            self._forget()
        self.ctx.changed()
        # Replaces "Time's up on this question", which must not outlive it.
        self.ctx.announce("Scored %d of %d." % (score, total))
        self.progress.setValue(len(self.order))

        ratio = score / total if total else 0.0
        self.stage.addWidget(self._score_card(
            score, total, ratio, seconds, wrong, late_right, skipped,
            previous))
        missed = [q for q in asked if q in wrong or q in late_right]
        if missed:
            self.stage.addWidget(self._study_card(missed))
            self.stage.addWidget(self._answers_card(missed))

        controls = QHBoxLayout()
        controls.setSpacing(8)
        if missed:
            again = button("Practise the %d you missed" % len(missed), "primary",
                           "Same questions, reshuffled, not scored")
            indexes = [self.quiz.questions.index(q) for q in missed]
            again.clicked.connect(
                lambda _=False, only=indexes: self._start(self.quiz, only))
            controls.addWidget(again)
        retake = button("Retake the whole quiz", "" if missed else "primary",
                        "New question order and answer positions")
        retake.clicked.connect(lambda: self._start(self.quiz))
        controls.addWidget(retake)
        controls.addStretch(1)
        back_to_phase = button("Back to the phase", "quiet")
        back_to_phase.clicked.connect(
            lambda: self.ctx.navigate.emit("phase", self.quiz.phase))
        controls.addWidget(back_to_phase)
        review = button("Review due cards", "quiet")
        review.clicked.connect(lambda: self.ctx.navigate.emit("review", ""))
        controls.addWidget(review)
        others = button("Other quizzes", "quiet")
        others.clicked.connect(self._reset_to_picker)
        controls.addWidget(others)
        self.stage.addLayout(controls)

    def _score_card(self, score, total, ratio, seconds, wrong, late_right,
                    skipped, previous) -> Card:
        card = Card(padding=20, spacing=10)
        card.setObjectName("FocusCard")
        top = QHBoxLayout()
        top.setSpacing(16)
        top.addWidget(label("%d / %d" % (score, total), "Big", wrap=False),
                      0, Qt.AlignmentFlag.AlignVCenter)
        column = QVBoxLayout()
        column.setSpacing(4)
        if self.practice_round:
            verdict, tone = "PRACTICE ROUND", ""
            words = ("Not recorded. Missed questions stay in your review deck.")
        elif ratio >= QUIZ_PROOF - 1e-9:
            verdict, tone = "PASSED", "done"
            words = "Passed. This counts toward proving the phase."
        elif ratio >= 0.6:
            verdict, tone = "CLOSE", "warn"
            words = ("Close. Study the lines below and retake it. Pass mark: "
                     "%d%%." % round(QUIZ_PROOF * 100))
        else:
            verdict, tone = "NOT YET", "bad"
            words = ("Not yet. Study the lines below before retaking it. Pass "
                     "mark: %d%%." % round(QUIZ_PROOF * 100))
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(pill(verdict, tone))
        head.addWidget(muted("%d%%" % round(ratio * 100)))
        if previous and previous[1] and not self.practice_round:
            head.addWidget(muted("best before: %d/%d" % previous))
        head.addStretch(1)
        column.addLayout(head)
        column.addWidget(label(words, "Soft"))
        top.addLayout(column, 1)
        card.box.addLayout(top)
        card.add(meter(score, max(total, 1), tone if tone == "done" else ""))

        facts = ["%d right" % score, "%d wrong" % (len(wrong) - len(skipped))]
        if skipped:
            facts.append("%d skipped" % len(skipped))
        if late_right:
            facts.append("%d right but out of time" % len(late_right))
        facts.append("answering time %s" % format_duration(seconds))
        card.add(muted("  -  ".join(facts)))
        if wrong or late_right:
            card.add(muted("Missed questions are in your review deck."))
        return card

    def _study_card(self, missed) -> Card:
        """What to study: the lines that teach what was missed, in course order."""
        card = Card(spacing=10)
        card.add(heading("What to study"))
        card.add(muted("Where each missed question is taught, in course order."))
        passed = self.ctx.store.passed_exercise_ids()
        offered = set()
        for group in study_plan(self.ctx.curriculum, self.quiz, missed):
            phase = group["phase"]
            card.add(divider())
            title = "Phase %s  -  %s" % (phase.num, phase.name) if phase else ""
            if group["section"]:
                title += "  -  %s" % group["section"]
            row = QHBoxLayout()
            row.setSpacing(8)
            row.addWidget(label(title, "RowTitle"), 1)
            count = len(group["questions"])
            row.addWidget(pill("%d MISSED" % count, "bad"))
            card.box.addLayout(row)
            for item_id, text in group["items"]:
                line = QHBoxLayout()
                line.setSpacing(8)
                line.addWidget(label(_plain(text), "Soft"), 1)
                go = button("Open this line", "quiet",
                            "Go to this line in phase %s" % (
                                phase.num if phase else ""))
                go.clicked.connect(
                    lambda _=False, t=item_id: self.ctx.navigate.emit(
                        "phase", t))
                line.addWidget(go, 0, Qt.AlignmentFlag.AlignTop)
                card.box.addLayout(line)
            if not group["items"] and phase is not None:
                line = QHBoxLayout()
                line.addWidget(label("Re-read this phase.", "Soft"), 1)
                go = button("Open the phase", "quiet")
                go.clicked.connect(
                    lambda _=False, p=phase.id: self.ctx.navigate.emit(
                        "phase", p))
                line.addWidget(go)
                card.box.addLayout(line)
            if phase is not None and phase.id not in offered:
                offered.add(phase.id)
                todo = [e for e in self.ctx.curriculum.exercises_for(phase.id)
                        if e.id not in passed]
                extras = QHBoxLayout()
                extras.setSpacing(8)
                if todo:
                    exercise = todo[0]
                    practise = button("Practise: %s" % exercise.title, "quiet",
                                      "An exercise from phase %s you have not "
                                      "passed yet" % phase.num)
                    practise.clicked.connect(
                        lambda _=False, e=exercise.id: self.ctx.navigate.emit(
                            "practice", e))
                    extras.addWidget(practise)
                lead = primary_of(phase.resources)
                if lead is not None and lead.url:
                    read = button("Read: %s" % lead.name, "quiet", lead.url)
                    read.clicked.connect(
                        lambda _=False, u=lead.url: open_url(u))
                    extras.addWidget(read)
                extras.addStretch(1)
                if extras.count() > 1:
                    card.box.addLayout(extras)
        return card

    def _answers_card(self, missed) -> Card:
        """Each missed question: what you chose, what was right, and why."""
        card = Card(spacing=6)
        card.add(heading("Question by question"))
        palette = self.ctx.palette
        for index, question in enumerate(missed):
            if index:
                card.add(divider())
            chosen = self.answers.get(question.id, -1)
            card.add(_rich(question.prompt, "RowTitle"))
            late = question.id in self.late
            if chosen < 0:
                yours, colour = "You skipped it.", palette.bad
            elif chosen == question.correct:
                yours = "Correct, but after time ran out."
                colour = palette.warn
            else:
                yours = "You chose: %s" % _plain_code(question.choices[chosen])
                colour = palette.bad
                if late:
                    yours += "  (out of time)"
            mine = label(yours, "Soft")
            mine.setStyleSheet("color: %s;" % colour)
            card.add(mine)
            if chosen != question.correct:
                right = _rich("Right answer: %s"
                              % question.choices[question.correct], "Soft")
                right.setStyleSheet("color: %s; font-weight: 600;"
                                    % palette.done)
                card.add(right)
                note = choice_feedback(question, chosen)
                if note:
                    card.add(_rich("Why yours is wrong: %s" % note, "Soft"))
            card.add(_rich(question.explain, "Soft"))
            item_id = teaching_item(self.ctx.curriculum, question)
            if item_id:
                row = QHBoxLayout()
                row.setSpacing(8)
                row.addWidget(muted("Taught in: %s" % _plain(
                    self.ctx.curriculum.item_text(item_id))), 1)
                go = button("Open", "quiet")
                go.clicked.connect(
                    lambda _=False, t=item_id: self.ctx.navigate.emit(
                        "phase", t))
                row.addWidget(go, 0, Qt.AlignmentFlag.AlignTop)
                card.box.addLayout(row)
        return card

    def _reset_to_picker(self) -> None:
        self._tick.stop()
        self.quiz = None
        self.group = None
        self.practice_round = False
        self.choice_orders = {}
        self._pick_screen()


def _option_text(index: int, choice: str) -> str:
    if index >= len(OPTION_KEYS):
        return choice
    return "%s.  %s" % (OPTION_KEYS[index], choice)


def _rich(text: str, object_name: str = "") -> QLabel:
    """A label that shows `code` as code, as the practice page does."""
    from .practice import _markup
    widget = label(_markup(text or ""), object_name)
    widget.setTextFormat(Qt.TextFormat.RichText)
    return widget


def _plain_code(text: str) -> str:
    """A radio button cannot render code spans; drop the backticks."""
    return re.sub(r"`([^`]+)`", lambda m: m.group(1), text or "")


def _plain(text: str) -> str:
    return re.sub(r"</?[a-z]+>", "", text or "")


def quiz_matches(quiz, needle: str) -> bool:
    """FIND on the picker: the quiz's name, description and id."""
    texts = (quiz.name, quiz.desc, quiz.id)
    if _textmatch is not None:
        # Every word, in any order, across the three fields - the same rule
        # as every other search box in the app.
        return _textmatch.matches(needle, *texts)
    folded = needle.casefold()
    return any(folded in (text or "").casefold() for text in texts)

