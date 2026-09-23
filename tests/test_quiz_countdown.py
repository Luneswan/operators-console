"""Quizzes: a countdown per question, a new layout every attempt, and results
that say what to study.

Owner, 09-23: "add countdowns per question and you lose marks if ... you
answer after it finishes", "questions and answers should appear shuffled
... the same questions should not be the same organization if you retook
the quiz", "what to look at again needs to be better ... find what you need
to study exactly ... and gives you ways to go there directly", and the
results said "Took 279 minutes 25 seconds".
"""
from __future__ import annotations

import random

from PySide6.QtWidgets import QPushButton

from conftest import pump

from operators_console.core import quiz_session as qs


# -- the rules, without a window ------------------------------------------


def test_every_question_gets_a_sensible_countdown(curriculum):
    for quiz in curriculum.quizzes:
        for question in quiz.questions:
            seconds = qs.question_seconds(question)
            assert qs.MIN_SECONDS <= seconds <= qs.MAX_SECONDS
            assert seconds % 5 == 0


def test_a_longer_question_gets_longer(curriculum):
    questions = [q for z in curriculum.quizzes for q in z.questions]
    by_words = sorted(questions, key=lambda q: len(
        " ".join([q.prompt, *q.choices]).split()))
    assert qs.question_seconds(by_words[0]) < qs.question_seconds(by_words[-1])


def test_a_retake_never_repeats_the_question_order_or_the_first_question():
    rng = random.Random(1)
    last = list(range(8))
    for _ in range(300):
        order = qs.fresh_order(8, rng, last)
        assert sorted(order) == list(range(8))
        assert order != last and order[0] != last[0]
        last = order


def test_the_right_answer_never_keeps_its_letter():
    rng = random.Random(2)
    at = None
    for _ in range(300):
        order = qs.fresh_choice_order(4, 2, rng, at)
        assert sorted(order) == [0, 1, 2, 3]
        if at is not None:
            assert order.index(2) != at
        at = order.index(2)


def test_durations_read_like_speech():
    assert qs.format_duration(45) == "45 s"
    assert qs.format_duration(192) == "3 min 12 s"
    assert qs.format_duration(120) == "2 min"
    assert qs.format_duration(16765) == "4 h 39 min"


def test_every_question_names_the_line_that_teaches_it(curriculum):
    for quiz in curriculum.quizzes:
        for question in quiz.questions:
            assert question.teaches, question.id
            assert curriculum.item_text(question.teaches) != question.teaches


def test_the_study_plan_groups_by_section_in_course_order(curriculum):
    quiz = curriculum.quiz("q05")
    plan = qs.study_plan(curriculum, quiz, list(quiz.questions))
    assert sum(len(g["questions"]) for g in plan) == len(quiz.questions)
    keys = [g["sort"] for g in plan]
    assert keys == sorted(keys)
    assert all(g["items"] for g in plan)


# -- the page -------------------------------------------------------------


def _start(qt_app, window, curriculum, quiz_id="q00"):
    window.go("quiz", quiz_id)
    pump(qt_app)
    return window.views["quiz"]


def _answer_current(view, qt_app, right=True):
    question = view.quiz.questions[view.order[view.position]]
    chosen = question.correct if right else (question.correct + 1) % len(
        question.choices)
    view.group.button(chosen).setChecked(True)
    view._question_controls[1].click()
    pump(qt_app, 1)
    return question


def test_each_question_shows_a_running_countdown(qt_app, window, curriculum):
    view = _start(qt_app, window, curriculum)
    assert view._tick.isActive()
    assert view.clock.text().count(":") == 1
    question = view.quiz.questions[view.order[view.position]]
    assert view.budget == qs.question_seconds(question)


def test_a_right_answer_after_the_countdown_earns_no_mark(
        qt_app, window, store, curriculum):
    view = _start(qt_app, window, curriculum)
    view.question_started -= view.budget + 1          # the clock ran out
    view._on_tick()
    assert not view._tick.isActive()
    assert view.clock_note.isVisible()
    question = _answer_current(view, qt_app, right=True)
    assert question.id in view.late
    for _ in range(len(view.order) - 1):
        view._advance()
        pump(qt_app)
        _answer_current(view, qt_app, right=True)
    view._advance()
    pump(qt_app)
    attempts = store.quiz_attempts("q00")
    assert attempts[0]["score"] == len(view.order) - 1
    assert attempts[0]["total"] == len(view.order)


def test_running_out_of_time_survives_closing_the_app(
        qt_app, window, store, curriculum):
    view = _start(qt_app, window, curriculum)
    qid = view.quiz.questions[view.order[view.position]].id
    view.question_started -= view.budget + 1
    view._on_tick()
    saved = store.setting("quiz_in_progress")
    assert qid in saved["late"]


def test_a_retake_draws_a_new_layout(qt_app, window, curriculum):
    view = _start(qt_app, window, curriculum)
    first = list(view.order)
    first_q = view.quiz.questions[first[0]]
    at = view.choice_orders[first_q.id].index(first_q.correct)
    view._start(view.quiz)
    pump(qt_app)
    assert view.order != first and view.order[0] != first[0]
    view.choices_shown(first_q)
    assert view.choice_orders[first_q.id].index(first_q.correct) != at


def test_choices_carry_letters_in_the_order_drawn(qt_app, window, curriculum):
    view = _start(qt_app, window, curriculum)
    for position, option in enumerate(view.group.buttons()):
        assert option.text().startswith("ABCD"[position] + ".  ")


def _finish_with_misses(qt_app, window, curriculum, misses=3):
    view = _start(qt_app, window, curriculum)
    for index in range(len(view.order)):
        _answer_current(view, qt_app, right=index >= misses)
        view._advance()
        pump(qt_app)
    return view


def test_the_results_say_what_to_study_and_go_there(
        qt_app, window, curriculum):
    view = _finish_with_misses(qt_app, window, curriculum)
    texts = [w.text() for w in view.findChildren(type(view.clock))]
    assert any(t == "What to study" for t in texts)
    assert any(t == "Question by question" for t in texts)
    assert not any("minutes" in t and "seconds" in t for t in texts)
    opens = [b for b in view.findChildren(QPushButton)
             if b.text() == "Open this line" and b.isVisibleTo(view)]
    assert opens
    opens[0].click()
    pump(qt_app)
    assert window.current_key == "phase"


def test_practising_the_missed_ones_is_not_a_quiz_score(
        qt_app, window, store, curriculum):
    view = _finish_with_misses(qt_app, window, curriculum, misses=2)
    before = len(store.quiz_attempts("q00"))
    again = next(b for b in view.findChildren(QPushButton)
                 if b.text().startswith("Practise the 2"))
    again.click()
    pump(qt_app)
    assert view.practice_round and len(view.order) == 2
    for _ in range(2):
        _answer_current(view, qt_app, right=True)
        view._advance()
        pump(qt_app)
    assert len(store.quiz_attempts("q00")) == before


def test_letters_pick_and_enter_checks_then_moves_on(
        qt_app, window, curriculum):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    view = _start(qt_app, window, curriculum)
    view.setFocus()
    question = view.quiz.questions[view.order[view.position]]
    drawn = view.choice_orders[question.id]
    QTest.keyClick(view, Qt.Key.Key_C)
    assert view.group.checkedId() == drawn[2]
    QTest.keyClick(view, Qt.Key.Key_Return)
    pump(qt_app)
    assert question.id in view.answers
    QTest.keyClick(view, Qt.Key.Key_Return)
    pump(qt_app)
    assert view.position == 1


def test_the_status_bar_says_the_score_not_times_up(
        qt_app, window, curriculum):
    view = _finish_with_misses(qt_app, window, curriculum, misses=1)
    assert view.quiz is not None
    assert window.status_label.text().startswith("Scored ")
