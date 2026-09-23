"""Quizzes: every quiz and every question in the bank."""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk]


def _start_every_phase(store, curriculum):
    """Review only offers material from phases the learner has reached."""
    for phase in curriculum.phases:
        ids = [i.id for i in phase.items][:1]
        if ids:
            store.set_many_checked(ids, True)


def _controls(view):
    from PySide6.QtWidgets import QPushButton
    out = []
    for index in range(view.stage.count()):
        item = view.stage.itemAt(index)
        widget = item.widget() if item is not None else None
        if widget is not None:
            out += widget.findChildren(QPushButton)
        child = item.layout() if item is not None else None
        if child is not None:
            for position in range(child.count()):
                inner = child.itemAt(position).widget()
                if isinstance(inner, QPushButton):
                    out.append(inner)
    return out


def _named(view, text):
    for widget in _controls(view):
        if widget.text() == text:
            return widget
    return None


@pytest.mark.walk_fast
def test_the_picker_lists_every_quiz(walk_app, window, curriculum):
    window.go("quiz", "")
    pump(walk_app, 2)
    view = window.views["quiz"]
    with step(walk_app, "quiz", "read the quiz picker", window):
        assert view.stage.count() == len(curriculum.quizzes), (
            "%d cards for %d quizzes"
            % (view.stage.count(), len(curriculum.quizzes)))
    REC.bump("quizzes listed", len(curriculum.quizzes))


@pytest.mark.walk_full
def test_every_question_can_be_answered_correctly(walk_app, window, store,
                                                  curriculum):
    view = window.views["quiz"]
    answered = 0
    for quiz in curriculum.quizzes:
        window.go("quiz", quiz.id)
        pump(walk_app, 2)
        assert view.quiz is not None and view.quiz.id == quiz.id
        with step(walk_app, "quiz", "answer all %d questions in %s correctly"
                  % (len(quiz.questions), quiz.id), window):
            for _ in range(len(view.order)):
                question = view.quiz.questions[view.order[view.position]]
                option = view.group.button(question.correct)
                assert option is not None, question.id
                click(walk_app, option, pump_rounds=0)
                submit = _named(view, "Check answer")
                assert submit is not None, "no Check answer button"
                click(walk_app, submit, pump_rounds=0)
                answered += 1
                nxt = (_named(view, "Next question")
                       or _named(view, "See your score"))
                assert nxt is not None, "no way forward after answering"
                click(walk_app, nxt, pump_rounds=0)
            best = store.best_quiz_score(quiz.id)
            assert best == (len(quiz.questions), len(quiz.questions)), (
                quiz.id, best)
        REC.bump("quizzes scored full marks")
    REC.bump("questions answered correctly", answered)
    assert answered == len(curriculum.all_questions), (
        "answered %d of %d questions" % (answered,
                                         len(curriculum.all_questions)))


@pytest.mark.walk_full
def test_every_wrong_answer_is_explained_and_scheduled(walk_app, window,
                                                       store, curriculum):
    _start_every_phase(store, curriculum)
    window.ctx.rebuild_review()
    view = window.views["quiz"]
    wrong_ids = []
    unscheduled = []
    for quiz in curriculum.quizzes:
        window.go("quiz", quiz.id)
        pump(walk_app, 2)
        with step(walk_app, "quiz", "get every question in %s wrong" % quiz.id,
                  window):
            for _ in range(len(view.order)):
                question = view.quiz.questions[view.order[view.position]]
                wrong = 0 if question.correct != 0 else 1
                if wrong < len(question.choices):
                    click(walk_app, view.group.button(wrong), pump_rounds=0)
                    wrong_ids.append(question.id)
                click(walk_app, _named(view, "Check answer"), pump_rounds=0)
                nxt = (_named(view, "Next question")
                       or _named(view, "See your score"))
                click(walk_app, nxt, pump_rounds=0)
            best = store.best_quiz_score(quiz.id)
            assert best == (0, len(quiz.questions)), (quiz.id, best)
        with step(walk_app, "quiz", "read the wrap-up for %s" % quiz.id,
                  window):
            assert _named(view, "Retake") is not None
            assert _named(view, "Other quizzes") is not None
            assert _named(view, "Back to the phase") is not None

    with step(walk_app, "review", "the wrong answers are waiting in review",
              window):
        window.ctx.rebuild_review()
        memories = {cid: store.memory(cid) for cid in wrong_ids}
        for card_id, memory in memories.items():
            if memory.reps == 0 and memory.lapses == 0:
                unscheduled.append(card_id)
    if unscheduled:
        phases = sorted({window.ctx.curriculum.quiz_of_question(q).phase
                         for q in unscheduled
                         if window.ctx.curriculum.quiz_of_question(q)})
        plan = window.ctx.progress.active_phase_ids()
        REC.find("major", "quiz",
                 "a wrong answer in an off-plan phase is silently dropped",
                 "On the default generalist track, open the quiz for a phase "
                 "that is not in your roadmap (phase 18), get a question "
                 "wrong. The score screen says 'Everything you got wrong is "
                 "now scheduled for review', but nothing is.",
                 "%d of %d wrong answers left no card. QuizView._answer looks "
                 "the question up in ReviewQueue.all_cards(), which filters "
                 "by eligible_phase_ids(); phases %s are not in the active "
                 "plan %s, so card_obj is None and the rating is thrown "
                 "away. Questions: %s"
                 % (len(unscheduled), len(wrong_ids), phases, plan,
                    unscheduled[:8]))
    REC.bump("questions answered wrongly", len(wrong_ids))
    REC.bump("wrong answers scheduled for review",
             len(wrong_ids) - len(unscheduled))


@pytest.mark.walk_fast
def test_skipping_retaking_and_leaving_a_quiz(walk_app, window, store,
                                              curriculum):
    view = window.views["quiz"]
    quiz = curriculum.quizzes[0]
    window.go("quiz", quiz.id)
    pump(walk_app, 2)
    with step(walk_app, "quiz", "skip every question without answering",
              window):
        for _ in range(len(view.order)):
            click(walk_app, _named(view, "Skip (counts as wrong)"),
                  pump_rounds=0)
            nxt = (_named(view, "Next question")
                   or _named(view, "See your score"))
            click(walk_app, nxt, pump_rounds=0)
        assert _named(view, "Retake") is not None, "no score screen appeared"
    with step(walk_app, "quiz", "retake it", window):
        click(walk_app, _named(view, "Retake"))
        assert view.position == 0
    with step(walk_app, "quiz", "go back to the picker", window):
        window.go("quiz", quiz.id)
        pump(walk_app, 1)
        view._reset_to_picker()
        pump(walk_app, 1)
        assert view.quiz is None
        assert view.stage.count() == len(curriculum.quizzes)
