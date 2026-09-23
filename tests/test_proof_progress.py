"""Proof, not reading, is the unit of progress.

A phase used to count as finished, move the "you are here" marker and
unlock its successor on ticked checkboxes alone: 0 of 36 exercises, a 0.0
quiz and no project were enough. Reading is still measured - it is the
meter - but a phase is finished only once it is proven: the gate ticked,
its quiz passed at 85%, 60% of its exercises passed and one project
shipped, each only where the phase has one.

The same change widens what review can ask about (gate checks become
cards, and a missed question brings the line that teaches it), puts
retrieval before new reading on Today, and keeps one slot there for a
phase other than the current one.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from operators_console.core.adaptive import Planner
from operators_console.core.progress import (
    EXERCISE_PROOF, QUIZ_PROOF, PhaseProgress, Progress, exercises_needed,
    proof_line,
)
from operators_console.core.review import (
    CONCEPT, GATE, QUIZ, ReviewQueue, concept_cue,
)
from operators_console.core.srs import Rating
from operators_console.core.today import (
    LEARN, LOG, MAX_ACTIONS, PRACTICE, QUIZ as QUIZ_ACTION, TodayPlan,
    WEIGHT_LEARN, WEIGHT_PRACTICE, WEIGHT_QUIZ,
)


# -- helpers ---------------------------------------------------------------


def read(store, curriculum, phase_id):
    store.set_many_checked(curriculum.phase(phase_id).trackable_ids, True)


def prove(store, curriculum, phase_id, quiz=(10, 10)):
    read(store, curriculum, phase_id)
    for q in curriculum.quizzes_for(phase_id):
        store.record_quiz(q.id, quiz[0], quiz[1], 30)
    for exercise in curriculum.exercises_for(phase_id):
        store.record_exercise_run(exercise.id, "pass", True)
    for project in curriculum.projects_for(phase_id)[:1]:
        store.set_project(project.id, status="shipped")


def stats(**changes) -> PhaseProgress:
    """A phase with a 5-check gate, one quiz, 10 exercises and a project."""
    base = dict(phase_id="px", done=20, total=20, gate_done=5, gate_total=5,
                exercises_done=6, exercises_total=10, quiz_best=0.9,
                projects_shipped=1, projects_total=2, quizzes_total=1,
                core_projects_shipped=1, core_projects_total=2)
    base.update(changes)
    return PhaseProgress(**base)


def plan_for(curriculum, store):
    progress = Progress(curriculum, store)
    planner = Planner(curriculum, store, progress)
    return progress, planner, TodayPlan(curriculum, store, progress, planner)


# -- PhaseProgress ---------------------------------------------------------


def test_everything_met_is_proven():
    st = stats()
    assert st.is_read and st.is_proven
    assert st.proof_percent == 100
    assert st.outstanding() == []


@pytest.mark.parametrize("change, missing", [
    (dict(gate_done=4), "1 gate check"),
    (dict(quiz_best=0.84), "the quiz at 85% or better"),
    (dict(exercises_done=5), "1 more exercise passed (6 of 10 needed)"),
    (dict(core_projects_shipped=0, projects_shipped=0),
     "one project shipped"),
])
def test_each_requirement_holds_the_phase_back_on_its_own(change, missing):
    st = stats(**change)
    assert not st.is_proven
    assert st.proof_percent < 100
    assert any(line.startswith(missing) for line in st.outstanding()), (
        st.outstanding())


def test_reading_everything_proves_nothing():
    st = stats(quiz_best=0.0, exercises_done=0, core_projects_shipped=0,
               projects_shipped=0)
    assert st.is_read and st.percent == 100
    assert not st.is_proven
    assert st.is_complete is st.is_read, "is_complete kept its old meaning"


def test_proof_does_not_need_every_line_read():
    st = stats(done=12)
    assert not st.is_read and st.is_proven


def test_what_a_phase_does_not_have_is_not_asked_for():
    st = stats(quizzes_total=0, quiz_best=0.0, exercises_total=0,
               exercises_done=0, core_projects_total=0,
               core_projects_shipped=0, projects_total=0, projects_shipped=0)
    assert [name for name, _m, _f in st.proof()] == ["gate"]
    assert st.is_proven


def test_a_phase_that_asks_for_nothing_falls_back_to_its_reading():
    empty = dict(gate_total=0, gate_done=0, quizzes_total=0, quiz_best=0.0,
                 exercises_total=0, exercises_done=0, core_projects_total=0,
                 core_projects_shipped=0, projects_total=0,
                 projects_shipped=0)
    assert stats(**empty).is_proven
    assert not stats(done=3, **empty).is_proven
    assert not stats(done=0, total=0, **empty).is_proven


def test_the_thresholds_are_the_ones_the_page_states():
    assert QUIZ_PROOF == 0.85 and EXERCISE_PROOF == 0.60
    assert stats(quiz_best=17 / 20).is_proven, "exactly 85% is a pass"
    assert [exercises_needed(n) for n in (0, 1, 2, 3, 4, 5, 10, 36)] == [
        0, 1, 2, 2, 3, 3, 6, 22]


def test_the_phase_line_says_read_and_proven_and_what_is_left():
    line = proof_line(stats(quiz_best=0.4, core_projects_shipped=0,
                            projects_shipped=0))
    assert line.startswith("Read 100%  -  Proven ")
    assert "Still to prove it:" in line
    assert "the quiz at 85% or better (best so far 40%)" in line
    assert "one project shipped" in line
    assert proof_line(stats()).endswith("This phase counts as finished.")


# -- Progress: the marker, the unlock, the finish ---------------------------


def test_ticking_a_phase_to_the_end_does_not_move_the_marker(curriculum,
                                                             store, progress):
    first, second = progress.active_phase_ids()[:2]
    read(store, curriculum, first)
    assert progress.phase(curriculum.phase(first)).is_read
    assert progress.current_phase_id() == first
    assert not progress.unlocked(second)
    prove(store, curriculum, first)
    assert progress.current_phase_id() == second
    assert progress.unlocked(second)


def test_proving_without_reading_every_line_moves_it(curriculum, store,
                                                     progress):
    """Nothing hard-locks: a learner who already knows it proves it."""
    first, second = progress.active_phase_ids()[:2]
    phase = curriculum.phase(first)
    prove(store, curriculum, first)
    store.set_checked(phase.items[0].id, False)
    assert not progress.phase(phase).is_read
    assert progress.current_phase_id() == second


def test_a_failed_quiz_keeps_the_phase_open(curriculum, store, progress):
    first = progress.active_phase_ids()[0]
    prove(store, curriculum, first, quiz=(1, 10))
    st = progress.phase(curriculum.phase(first))
    assert not st.is_proven
    assert progress.current_phase_id() == first


def test_the_plan_is_finished_only_when_every_phase_is_proven(curriculum,
                                                              store,
                                                              progress):
    plan = progress.active_phase_ids()
    for pid in plan:
        read(store, curriculum, pid)
    assert progress.is_finished is False
    assert progress.overview().phases_complete == 0
    assert progress.overview().phases_read == progress.overview().phases_total
    for pid in plan:
        prove(store, curriculum, pid)
    assert progress.is_finished is True
    assert progress.overview().phases_complete == \
        progress.overview().phases_total


def test_a_read_phase_still_has_hours_left_in_it(curriculum, store,
                                                 progress):
    before = progress.estimated_days_left()
    first = progress.active_phase_ids()[0]
    read(store, curriculum, first)
    after_reading = progress.estimated_days_left()
    prove(store, curriculum, first)
    after_proof = progress.estimated_days_left()
    assert before >= after_reading >= after_proof
    phase = curriculum.phase(first)
    if phase.est_hours >= 20:
        assert after_reading > after_proof, "reading counted as the whole job"


# -- Review: gate checks and the lines behind missed questions ------------


def test_gate_checks_of_a_reached_phase_are_cards(curriculum, store,
                                                  progress):
    queue = ReviewQueue(curriculum, store, progress)
    eligible = queue.eligible_phase_ids()
    cards = {c.id: c for c in queue.all_cards()}
    for phase in curriculum.phases:
        if phase.gate is None:
            continue
        for item in phase.gate.items:
            if phase.id in eligible:
                card = cards[item.id]
                assert card.kind == GATE and card.phase == phase.id
                assert card.front == concept_cue(item.text)
                assert card.back == item.text
                assert queue.gate_note(card) == phase.gate.note.strip()
            else:
                assert item.id not in cards, "asked before it was taught"


def test_a_gate_check_sent_to_review_by_hand_is_one_card(curriculum, store,
                                                         progress):
    queue = ReviewQueue(curriculum, store, progress)
    phase = curriculum.phase(progress.active_phase_ids()[0])
    item = phase.gate.items[0]
    queue.add_concept(item.id)
    matching = [c for c in queue.all_cards() if c.id == item.id]
    assert len(matching) == 1 and matching[0].kind == CONCEPT


def test_a_buried_gate_check_stays_buried(curriculum, store, progress):
    queue = ReviewQueue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == GATE)
    queue.bury(card)
    assert card.id not in {c.id for c in queue.all_cards()}


def test_new_cards_take_turns_by_kind(curriculum, store, progress):
    store.set_setting("new_cards_per_day", 6)
    queue = ReviewQueue(curriculum, store, progress)
    kinds = [c.kind for c in queue.session()]
    assert kinds[:2] == [QUIZ, GATE], kinds


def _teaching_stand_in(curriculum, monkeypatch, question, item_id):
    stand_in = SimpleNamespace(id=question.id, teaches=item_id,
                               explain_choice=())
    real = curriculum.question
    monkeypatch.setattr(curriculum, "question",
                        lambda qid: stand_in if qid == question.id
                        else real(qid))


def test_a_missed_question_brings_its_line_into_the_deck(curriculum, store,
                                                        progress,
                                                        monkeypatch):
    queue = ReviewQueue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    line = curriculum.phase(card.phase).items[0].id
    _teaching_stand_in(curriculum, monkeypatch,
                       curriculum.question(card.id), line)
    queue.answer(card, Rating.GOOD)
    assert line not in queue.concept_ids(), "a right answer enrolled it"
    queue.answer(card, Rating.AGAIN)
    assert line in queue.concept_ids()
    assert any(c.id == line and c.kind == CONCEPT
               for c in queue.all_cards())


def test_a_line_that_does_not_exist_is_not_enrolled(curriculum, store,
                                                    progress, monkeypatch):
    queue = ReviewQueue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    _teaching_stand_in(curriculum, monkeypatch,
                       curriculum.question(card.id), "p00.nowhere.9")
    queue.answer(card, Rating.AGAIN)
    assert queue.concept_ids() == set()


def test_questions_without_teaches_still_work(curriculum, store, progress):
    """Before the curriculum carries ``teaches`` nothing is enrolled."""
    queue = ReviewQueue(curriculum, store, progress)
    card = next(c for c in queue.all_cards() if c.kind == QUIZ)
    question = curriculum.question(card.id)
    queue.answer(card, Rating.AGAIN)
    expected = getattr(question, "teaches", "") or ""
    if expected and curriculum.item_text(expected) != expected:
        assert expected in queue.concept_ids()
    else:
        assert queue.concept_ids() == set()


# -- Today: retrieval first, one slot mixed in, the log on top ------------


def test_retrieval_comes_before_new_reading(curriculum, store):
    assert WEIGHT_QUIZ > WEIGHT_LEARN and WEIGHT_PRACTICE > WEIGHT_LEARN
    store.set_setting("hours_per_day", 8)
    progress, _planner, today = plan_for(curriculum, store)
    pid = progress.current_phase_id()
    read(store, curriculum, pid)
    store.set_checked(curriculum.phase(pid).items[-1].id, False)
    kinds = [a.kind for a in today.build()]
    assert LEARN in kinds
    for retrieval in (QUIZ_ACTION, PRACTICE):
        if retrieval in kinds:
            assert kinds.index(retrieval) < kinds.index(LEARN), kinds


def test_a_finished_earlier_phase_is_mixed_in(curriculum, store):
    store.set_setting("hours_per_day", 8)
    progress, _planner, today = plan_for(curriculum, store)
    first, second = progress.active_phase_ids()[:2]
    prove(store, curriculum, first)
    assert progress.current_phase_id() == second
    actions = today.build()
    quiz = curriculum.quizzes_for(first)[0]
    mixed = [a for a in actions if a.target == quiz.id]
    assert mixed and mixed[0].title.startswith("Mix in phase"), [
        a.title for a in actions]


def test_the_weakest_other_phase_takes_the_mixed_slot(curriculum, store):
    store.set_setting("hours_per_day", 8)
    progress, _planner, today = plan_for(curriculum, store)
    first, second, third = progress.active_phase_ids()[:3]
    prove(store, curriculum, first)
    # Started and scored badly: a weak area that is not the current phase.
    store.set_checked(curriculum.phase(third).items[0].id, True)
    for quiz in curriculum.quizzes_for(third):
        store.record_quiz(quiz.id, 1, 10, 30)
    actions = today.build()
    shore = [a for a in actions if a.title.startswith("Shore up")]
    assert shore and shore[0].target == third


def test_the_mixed_slot_survives_a_crowded_day(curriculum, store):
    store.set_setting("hours_per_day", 24)
    progress, _planner, today = plan_for(curriculum, store)
    first = progress.active_phase_ids()[0]
    prove(store, curriculum, first)
    store.add_log("2000-01-01", "old", 1.0, "", "", "promise me this")
    actions = today.build()
    quiz = curriculum.quizzes_for(first)[0]
    assert any(a.target == quiz.id for a in actions)
    assert len([a for a in actions if a.kind != LOG]) <= MAX_ACTIONS


def test_the_log_is_not_counted_against_the_five(curriculum, store):
    from operators_console.core.today import Action
    _progress, _planner, today = plan_for(curriculum, store)
    many = [Action(LEARN, "Thing %d" % i, "", "t%d" % i, 1, weight=90 - i)
            for i in range(8)]
    log = Action(LOG, "Write today's log entry", "", "", 5, weight=10)
    fitted = today._fit(many + [log], budget=600)
    assert len(fitted) == MAX_ACTIONS + 1
    assert fitted[-1] is log


def test_a_reserved_slot_that_does_not_fit_the_day_is_dropped(curriculum,
                                                             store):
    from operators_console.core.today import Action
    _progress, _planner, today = plan_for(curriculum, store)
    reserved = Action(LEARN, "Mixed", "", "m", 30, weight=55)
    fitted = today._fit([reserved], budget=10, reserved=reserved)
    assert fitted == []
