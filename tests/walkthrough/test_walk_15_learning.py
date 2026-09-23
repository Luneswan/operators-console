"""Learning, not button position: every control added to make it so.

The Quiz picker's FIND box, SHOW filter, counter and the fold of quizzes
outside the track; shuffled choices on the Quiz and Review pages; a wrong
review answer that now stays on screen with "Where this is taught" and
"Next card"; gate checks as review cards; and the "Read - Proven" line on
the Phase page, the Roadmap and Today. Each is pressed the way a learner
presses it.
"""
from __future__ import annotations

import random

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from .harness import REC, click, press, pump, step, type_text

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


# -- helpers ---------------------------------------------------------------


def _buttons(root, prefix):
    return [b for b in root.findChildren(QPushButton)
            if b.text().startswith(prefix) and b.isVisibleTo(root)]


def _text(root) -> str:
    return "\n".join(w.text() for w in root.findChildren(QLabel))


def _prove(store, curriculum, phase_id):
    store.set_many_checked(curriculum.phase(phase_id).trackable_ids, True)
    for quiz in curriculum.quizzes_for(phase_id):
        store.record_quiz(quiz.id, len(quiz.questions), len(quiz.questions),
                          60)
    for exercise in curriculum.exercises_for(phase_id):
        store.record_exercise_run(exercise.id, "pass", True)
    for project in curriculum.projects_for(phase_id)[:1]:
        store.set_project(project.id, status="shipped")


# -- the quiz picker --------------------------------------------------------


def test_the_quiz_picker_find_show_and_the_fold(walk_app, window, store,
                                                curriculum):
    window.go("quiz", "")
    pump(walk_app, 2)
    view = window.views["quiz"]
    total = len(curriculum.quizzes)
    plan = set(window.ctx.progress.active_phase_ids())
    outside = [q for q in curriculum.quizzes if q.phase not in plan]

    with step(walk_app, "quiz", "read the picker and its counter", window):
        assert view.search.isVisibleTo(view)
        assert view.counter.text() == "0 of %d passed" % total
        inside, folded = view.visible_quizzes()
        assert [q.id for q in inside + folded] != []
        assert {q.id for q in folded} == {q.id for q in outside}

    if outside:
        with step(walk_app, "quiz", "open the quizzes outside the track",
                  window):
            toggles = [w for w in view.findChildren(QPushButton)
                       if w.objectName() == "DisclosureToggle"]
            assert toggles, "no fold for the quizzes outside the track"
            assert "outside your track" in _text(toggles[0])
            click(walk_app, toggles[0])
            assert "NOT IN YOUR PLAN" in _text(view)
            REC.bump("quiz folds opened")

    with step(walk_app, "quiz", "type into FIND", window):
        target = curriculum.quizzes[1]
        word = target.name.split()[0]
        type_text(walk_app, view.search, word)
        pump(walk_app, 2)
        inside, folded = view.visible_quizzes()
        shown = inside + folded
        assert target in shown
        assert all(word.casefold() in (q.name + " " + q.desc + " " + q.id)
                   .casefold() for q in shown)
        if len(shown) != total:
            assert view.counter.text().startswith("%d shown" % len(shown))
        REC.bump("quiz searches typed")

    with step(walk_app, "quiz", "a search that matches nothing", window):
        view.search.setText("zzzz no such quiz")
        pump(walk_app, 2)
        assert view.visible_quizzes() == ([], [])
        assert "No quiz matches." in _text(view)
        view.search.clear()
        pump(walk_app, 2)

    with step(walk_app, "quiz", "SHOW each status in turn", window):
        passed = curriculum.quizzes[0]
        below = curriculum.quizzes[2]
        store.record_quiz(passed.id, 9, 10, 30)
        store.record_quiz(below.id, 4, 10, 30)
        view._refilter()
        for index, wanted in ((1, None), (2, below.id), (3, passed.id)):
            view.show_filter.setFocus()
            view.show_filter.setCurrentIndex(index)
            pump(walk_app, 2)
            inside, folded = view.visible_quizzes()
            ids = {q.id for q in inside + folded}
            if wanted is None:
                assert passed.id not in ids and below.id not in ids
                assert len(ids) == total - 2
            else:
                assert ids == {wanted}, (index, ids)
        view.show_filter.setCurrentIndex(0)
        pump(walk_app, 2)
        assert view.counter.text() == "1 of %d passed" % total
        REC.bump("quiz status filters chosen", 3)

    with step(walk_app, "quiz", "start a quiz from the filtered list",
              window):
        view.search.setText(curriculum.quizzes[3].id)
        pump(walk_app, 2)
        start = [b for b in view.findChildren(QPushButton)
                 if b.text() == "Start" and b.isVisibleTo(view)]
        assert start, "the filtered picker has no Start button"
        click(walk_app, start[0])
        assert view.quiz is not None
        assert not view.filters.isVisibleTo(view), (
            "the picker's filters stayed up during an attempt")
        view._reset_to_picker()
        view.search.clear()
        pump(walk_app, 2)


# -- a shuffled quiz, answered by its second button ------------------------


def test_a_quiz_answered_by_position_scores_by_content(walk_app, window,
                                                       store, curriculum):
    quiz = max(curriculum.quizzes, key=lambda q: len(q.questions))
    view = window.views["quiz"]
    view.rng = random.Random(15)
    window.go("quiz", quiz.id)
    pump(walk_app, 2)
    right = 0
    with step(walk_app, "quiz", "press the second choice every time",
              window):
        for _ in range(len(view.order)):
            question = view.quiz.questions[view.order[view.position]]
            second = view.group.buttons()[1]
            stored = view.choice_orders[question.id][1]
            click(walk_app, second, pump_rounds=1)
            click(walk_app, _buttons(view, "Check answer")[0],
                  pump_rounds=1)
            assert view.answers[question.id] == stored
            right += stored == question.correct
            nxt = (_buttons(view, "Next question")
                   or _buttons(view, "See your score"))
            click(walk_app, nxt[0], pump_rounds=1)
        best = store.best_quiz_score(quiz.id)
        assert best == (right, len(quiz.questions))
        assert right < len(quiz.questions), (
            "pressing the same button every time still aced the quiz")
    REC.bump("questions answered by position", len(quiz.questions))


# -- review: the wrong answer, the way back, the gate card -----------------


def _open_review(walk_app, window, cards):
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    view.card = None
    view.queue = list(cards)
    view._next_card()
    pump(walk_app, 2)
    return view


def test_a_wrong_review_answer_and_where_it_is_taught(walk_app, window,
                                                      store, curriculum):
    card = next(c for c in window.ctx.review.all_cards() if c.kind == "quiz")
    follow = next(c for c in window.ctx.review.all_cards()
                  if c.kind == "quiz" and c.id != card.id)
    view = _open_review(walk_app, window, [card, follow])

    with step(walk_app, "review", "pick a wrong option by its letter",
              window):
        wrong = next(p for p, s in enumerate(view.shown_order)
                     if s != card.correct)
        press(walk_app, view, getattr(Qt.Key, "Key_" + "ABCD"[wrong]))
        assert view.group.checkedId() == view.shown_order[wrong]
        press(walk_app, view, Qt.Key.Key_Return)
        assert store.memory(card.id).reps == 1, "the wrong answer went unrated"
        assert view.card is not None and view.card.id == card.id
        assert card.back in _text(view), "the explanation vanished"

    with step(walk_app, "review", "press Where this is taught", window):
        click(walk_app, _buttons(view, "Where this is taught")[0])
        page = window.views["phase"]
        assert window.stack.currentWidget() is page
        assert page.current_id == card.phase
        REC.bump("wrong answers traced to their phase")

    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]
    with step(walk_app, "review", "press Next card", window):
        assert view.card is not None and view.card.id == card.id
        click(walk_app, _buttons(view, "Next card")[0])
        assert view.card is not None and view.card.id == follow.id

    with step(walk_app, "review", "a second wrong answer, left with Space",
              window):
        wrong = next(s for s in view.shown_order if s != follow.correct)
        click(walk_app, view.group.button(wrong))
        click(walk_app, _buttons(view, "Check")[0])
        assert _buttons(view, "Next card"), "no way on after a wrong answer"
        press(walk_app, view, Qt.Key.Key_Space)
        assert view.card is None or view.card.id != follow.id


def test_a_gate_check_is_a_card_to_recall(walk_app, window, store,
                                          curriculum):
    card = next(c for c in window.ctx.review.all_cards() if c.kind == "gate")
    view = _open_review(walk_app, window, [card])
    with step(walk_app, "review", "reveal a gate check", window):
        assert card.front in _text(view)
        click(walk_app, _buttons(view, "Reveal")[0])
        text = _text(view)
        assert "The gate check" in text
        assert "Phase gate:" in text
    with step(walk_app, "review", "rate it Good", window):
        click(walk_app, _buttons(view, "Good")[0])
        assert store.memory(card.id).reps == 1
    REC.bump("gate checks recalled")


# -- read versus proven, on every page that shows a position -------------


def test_reading_is_not_proof_on_the_phase_roadmap_and_today(walk_app,
                                                             window, store,
                                                             curriculum):
    progress = window.ctx.progress
    first, second = progress.active_phase_ids()[:2]
    # Both read to the end; neither proven.
    store.set_many_checked(curriculum.phase(first).trackable_ids, True)
    store.set_many_checked(curriculum.phase(second).trackable_ids, True)

    with step(walk_app, "phase", "a phase read to the end", window):
        window.go("phase", first)
        pump(walk_app, 2)
        caption = window.views["phase"].proof_caption.text()
        assert caption.startswith("Read 100%  -  Proven "), caption
        assert "Still to prove it:" in caption

    with step(walk_app, "roadmap", "the roadmap says read, not proven",
              window):
        window.go("roadmap", "")
        pump(walk_app, 2)
        text = _text(window.views["roadmap"])
        assert progress.current_phase_id() == first, "reading moved the marker"
        assert "YOU ARE HERE" in text
        assert "READ, NOT PROVEN" in text, "the second phase reads as done"

    _prove(store, curriculum, first)
    with step(walk_app, "phase", "the same phase, proven", window):
        window.go("phase", first)
        pump(walk_app, 2)
        caption = window.views["phase"].proof_caption.text()
        assert caption.endswith("This phase counts as finished."), caption
        assert progress.current_phase_id() == second

    with step(walk_app, "today", "an earlier phase is mixed into today",
              window):
        store.set_setting("hours_per_day", 8)
        window.go("today", "")
        pump(walk_app, 2)
        titles = [a.title for a in window.ctx.today.build()]
        assert any(t.startswith("Mix in phase") for t in titles), titles
        assert "Proven" in _text(window.views["today"])
    REC.bump("phases proven in the walk")
