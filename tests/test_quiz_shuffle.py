"""Choices are shuffled where they are shown, and scored where they are stored.

163 of the bank's 167 correct answers sit in the same stored slot. Both the
Quiz page and the Review page drew the choices in stored order, so a learner
who always pressed the second option scored 97.6% without reading a word -
and every quiz score, phase meter and review rating built on that measured
button position rather than knowledge.

Each attempt now draws its own order. What is scored, stored and rated is
always the stored index of the choice, whatever position it was drawn in.
"""
from __future__ import annotations

import random
from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from conftest import pump

from operators_console.core.review import (
    QUIZ, choice_feedback, choice_order, teaching_item, valid_order,
)

# Four choices a question: blind guessing scores about a quarter.
CHANCE_LOW, CHANCE_HIGH = 0.12, 0.40


# -- the permutation itself ------------------------------------------------


def test_an_order_is_a_permutation_of_the_stored_indexes():
    rng = random.Random(3)
    for count in range(0, 7):
        order = choice_order(count, rng)
        assert sorted(order) == list(range(count))
        assert valid_order(order, count)


def test_every_position_is_drawn_for_every_choice():
    rng = random.Random(11)
    seen = {(pos, stored) for _ in range(400)
            for pos, stored in enumerate(choice_order(4, rng))}
    assert seen == {(p, s) for p in range(4) for s in range(4)}


@pytest.mark.parametrize("bad", [
    None, "0123", [0, 1, 2], [0, 1, 2, 2], [0, 1, 2, 4], [0, 1, 2, "3"],
    [True, False, 2, 3], {"0": 1},
])
def test_a_saved_order_that_is_not_a_permutation_is_refused(bad):
    assert not valid_order(bad, 4)


def test_always_the_second_displayed_choice_scores_near_chance(curriculum):
    """The robot that aced the bank, run against shuffled choices."""
    rng = random.Random(20260923)
    questions = curriculum.all_questions
    assert len(questions) >= 150
    stored_second = sum(1 for q in questions if q.correct == 1)
    shuffled_second = 0
    for question in questions:
        order = choice_order(len(question.choices), rng)
        chosen = order[1]           # the second choice on screen
        shuffled_second += chosen == question.correct
    ratio = shuffled_second / len(questions)
    assert CHANCE_LOW < ratio < CHANCE_HIGH, (
        "always pressing the second option scored %.0f%% (unshuffled it "
        "would score %.0f%%)" % (ratio * 100,
                                 stored_second / len(questions) * 100))


# -- the Quiz page ---------------------------------------------------------


def _press_second_and_check(view, qt_app):
    question = view.quiz.questions[view.order[view.position]]
    shown = view.choice_orders[question.id]
    second = view.group.buttons()[1]
    assert second.text() == question.choices[shown[1]], (
        "the buttons are not drawn in the attempt's order")
    second.setChecked(True)
    _skip, submit = view._question_controls
    submit.click()
    pump(qt_app, 1)
    return question, shown[1]


def test_the_quiz_page_stores_and_scores_the_stored_index(qt_app, window,
                                                          store, curriculum):
    """Always the second button, over every quiz in the bank."""
    view = window.views["quiz"]
    view.rng = random.Random(7)
    right = asked = 0
    for quiz in curriculum.quizzes:
        window.go("quiz", quiz.id)
        pump(qt_app, 1)
        for _ in range(len(view.order)):
            question, stored = _press_second_and_check(view, qt_app)
            assert view.answers[question.id] == stored, (
                "the answer was stored as a screen position, not a choice")
            right += stored == question.correct
            asked += 1
            view._advance()
            pump(qt_app, 1)
        best = store.best_quiz_score(quiz.id)
        assert best is not None and best[1] == len(quiz.questions)
    assert asked == len(curriculum.all_questions)
    assert CHANCE_LOW < right / asked < CHANCE_HIGH, right / asked


def test_the_rating_follows_the_stored_index(qt_app, window, curriculum,
                                             monkeypatch):
    quiz = curriculum.quizzes[0]
    window.go("quiz", quiz.id)
    pump(qt_app)
    view = window.views["quiz"]
    rated = []
    monkeypatch.setattr(window.ctx.review, "answer",
                        lambda card, rating, now=None:
                        rated.append((card.id, card.correct, rating)))
    question = view.quiz.questions[view.order[view.position]]
    shown = view.choice_orders[question.id]
    position = shown.index(question.correct)
    view.group.buttons()[position].setChecked(True)
    view._question_controls[1].click()
    pump(qt_app)
    from operators_console.core.srs import Rating
    assert rated == [(question.id, question.correct, Rating.GOOD)]
    assert view.answers[question.id] == question.correct


def test_a_resumed_attempt_draws_the_same_order(qt_app, window, store,
                                                curriculum):
    quiz = max(curriculum.quizzes, key=lambda q: len(q.questions))
    window.go("quiz", quiz.id)
    pump(qt_app)
    view = window.views["quiz"]
    _press_second_and_check(view, qt_app)
    view._advance()
    pump(qt_app)
    current = view.quiz.questions[view.order[view.position]]
    drawn = [b.text() for b in view.group.buttons()]
    saved = store.setting("quiz_in_progress")
    assert saved["choices"][current.id] == view.choice_orders[current.id]

    # The app closes; a new page reads the attempt back.
    view.quiz = None
    view.choice_orders = {}
    view.rng = random.Random(999)       # a different draw, if it redrew
    view._reset_to_picker()
    view._resume()
    pump(qt_app)
    assert view.quiz.questions[view.order[view.position]].id == current.id
    assert [b.text() for b in view.group.buttons()] == drawn


def test_an_attempt_saved_before_shuffling_still_resumes(qt_app, window,
                                                         store, curriculum):
    """A build that did not shuffle saved no "choices": the update must not
    lose the learner's place."""
    quiz = curriculum.quizzes[0]
    store.set_setting("quiz_in_progress", {
        "quiz_id": quiz.id,
        "order": list(range(len(quiz.questions))),
        "position": 1,
        "answers": {quiz.questions[0].id: quiz.questions[0].correct},
    })
    window.go("quiz", "")
    pump(qt_app)
    view = window.views["quiz"]
    view._resume()
    pump(qt_app)
    question = view.quiz.questions[view.order[view.position]]
    assert question.id == quiz.questions[1].id
    assert valid_order(view.choice_orders[question.id],
                       len(question.choices))
    assert sorted(b.text() for b in view.group.buttons()) == sorted(
        question.choices)


def test_a_saved_order_that_no_longer_fits_is_redrawn(qt_app, window, store,
                                                      curriculum):
    quiz = curriculum.quizzes[0]
    first = quiz.questions[0]
    store.set_setting("quiz_in_progress", {
        "quiz_id": quiz.id,
        "order": list(range(len(quiz.questions))),
        "position": 0,
        "answers": {},
        "choices": {first.id: [0, 0, 1, 2]},
    })
    window.go("quiz", "")
    pump(qt_app)
    view = window.views["quiz"]
    view._resume()
    pump(qt_app)
    assert valid_order(view.choice_orders[first.id], len(first.choices))


# -- per-choice feedback ---------------------------------------------------


def _fake_quiz():
    question = SimpleNamespace(
        id="zz.shuffle.0", prompt="Which one?",
        choices=("Alpha", "Bravo", "Charlie", "Delta"), correct=2,
        explain="Charlie is the one because of the general reason.",
        explain_choice=("Alpha mixes up two ideas.", "",
                        "Right, and here is why.", "Delta is a trap."),
        teaches="")
    quiz = SimpleNamespace(id="zz.shuffle", phase="p00", name="Fake quiz",
                           desc="A quiz made for this test.",
                           questions=(question,))
    return quiz, question


def test_choice_feedback_reads_the_stored_index():
    _quiz, question = _fake_quiz()
    assert choice_feedback(question, 0) == "Alpha mixes up two ideas."
    assert choice_feedback(question, 1) == ""
    assert choice_feedback(question, -1) == ""
    assert choice_feedback(question, 9) == ""
    assert choice_feedback(SimpleNamespace(), 0) == ""


def test_the_quiz_page_shows_what_the_picked_choice_gets_wrong(qt_app,
                                                              window):
    from PySide6.QtWidgets import QLabel
    quiz, question = _fake_quiz()
    window.go("quiz", "")
    pump(qt_app)
    view = window.views["quiz"]
    view._start(quiz)
    pump(qt_app)
    position = view.choice_orders[question.id].index(3)
    view.group.buttons()[position].setChecked(True)
    view._question_controls[1].click()
    pump(qt_app)
    texts = [w.text() for w in view.findChildren(QLabel)]
    note = [t for t in texts if "Delta is a trap." in t]
    general = [t for t in texts if t == question.explain]
    assert note and general
    assert texts.index(note[0]) < texts.index(general[0]), (
        "the note on the picked choice belongs above the general one")
    view.quiz = None


# -- the Review page -------------------------------------------------------


def _quiz_card(ctx):
    return next(c for c in ctx.review.all_cards() if c.kind == QUIZ)


def _open_review(window, qt_app, cards, rng=None):
    window.go("review", "")
    pump(qt_app)
    view = window.views["review"]
    if rng is not None:
        view.rng = rng
    view.card = None
    view.queue = list(cards)
    view._next_card()
    pump(qt_app)
    return view


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_review_letters_follow_the_screen_and_score_the_stored_index(
        qt_app, window, seed):
    card = _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [card], random.Random(seed))
    for position, stored in enumerate(view.shown_order):
        button = view.group.button(stored)
        assert button.text().startswith("ABCD"[position] + ".")
        assert button.text().endswith(card.choices[stored])
    QTest.keyClick(view, Qt.Key.Key_B)
    pump(qt_app)
    assert view.group.checkedId() == view.shown_order[1]


def test_a_right_review_answer_by_letter_is_rated_as_right(qt_app, window):
    card = _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [card], random.Random(8))
    letter = "ABCD"[view.shown_order.index(card.correct)]
    QTest.keyClick(view, getattr(Qt.Key, "Key_" + letter))
    QTest.keyClick(view, Qt.Key.Key_Return)
    pump(qt_app)
    assert view._rating_live, "a right answer did not reach the ratings"


def test_a_wrong_review_answer_stays_with_its_explanation(qt_app, window,
                                                         store):
    """It was rated Again and replaced by the next card in one instant."""
    from PySide6.QtWidgets import QLabel, QPushButton
    first = _quiz_card(window.ctx)
    view = _open_review(window, qt_app, [first], random.Random(4))
    wrong = next(i for i in view.shown_order if i != first.correct)
    view.group.button(wrong).setChecked(True)
    QTest.keyClick(view, Qt.Key.Key_Space)
    pump(qt_app)
    assert store.memory(first.id).lapses >= 0
    assert store.memory(first.id).reps == 1, "the wrong answer was not rated"
    assert view.card is not None and view.card.id == first.id
    texts = [w.text() for w in view.findChildren(QLabel)]
    assert first.back in texts, "the explanation was not left on screen"
    names = [b.text() for b in view.findChildren(QPushButton)
             if b.isVisibleTo(view)]
    assert "Where this is taught" in names
    assert any(n.startswith("Next card") for n in names)
    QTest.keyClick(view, Qt.Key.Key_Space)
    pump(qt_app)
    assert view.card is None, "Space did not move on"


def test_the_review_page_shows_the_picked_choices_note(qt_app, window,
                                                      monkeypatch):
    from PySide6.QtWidgets import QLabel
    card = _quiz_card(window.ctx)
    real = window.ctx.curriculum.question(card.id)
    notes = tuple("Note on choice %d." % i for i in range(len(card.choices)))
    stand_in = SimpleNamespace(id=real.id, choices=real.choices,
                               correct=real.correct, explain=real.explain,
                               explain_choice=notes, teaches="")
    monkeypatch.setattr(window.ctx.curriculum, "question",
                        lambda qid: stand_in if qid == card.id else None)
    view = _open_review(window, qt_app, [card], random.Random(2))
    wrong = next(i for i in view.shown_order if i != card.correct)
    view.group.button(wrong).setChecked(True)
    view._check_choice()
    pump(qt_app)
    texts = [w.text() for w in view.findChildren(QLabel)]
    assert any(("Note on choice %d." % wrong) in t for t in texts), texts


def test_where_this_is_taught_opens_the_line_the_question_tests(
        qt_app, window, curriculum, monkeypatch):
    card = _quiz_card(window.ctx)
    phase = curriculum.phase(card.phase)
    line = phase.items[-1]
    real = curriculum.question(card.id)
    stand_in = SimpleNamespace(id=real.id, choices=real.choices,
                               correct=real.correct, explain=real.explain,
                               explain_choice=(), teaches=line.id)
    monkeypatch.setattr(window.ctx.curriculum, "question",
                        lambda qid: stand_in if qid == card.id else None)
    assert teaching_item(curriculum, stand_in) == line.id
    view = _open_review(window, qt_app, [card], random.Random(6))
    wrong = next(i for i in view.shown_order if i != card.correct)
    view.group.button(wrong).setChecked(True)
    view._check_choice()
    pump(qt_app)
    assert line.id in window.ctx.review.concept_ids(), (
        "the line behind a missed question did not join the deck")
    taught = view._wrong_controls[0]
    taught.click()
    pump(qt_app)
    page = window.views["phase"]
    assert window.stack.currentWidget() is page
    assert page.current_id == phase.id
    assert page.target_item == line.id
    assert page.row_for(line.id) is not None
