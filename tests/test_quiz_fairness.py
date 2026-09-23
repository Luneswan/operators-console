"""The quiz bank has to measure knowledge, not test-taking tricks.

The bank once shipped with 163 of 167 answers at the second choice and the
correct answer the longest option 93% of the time, so a learner who read
nothing scored 97.6%, and every signal fed by quiz results (the phase meter,
the weak-area detector, the review deck) measured button position. Every
existing shape test passed on that data. These pin the fairness itself.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter

import pytest

from operators_console.core.curriculum import _question

# sha256 of the sorted ids of the 167 questions shipped before the bank was
# extended. Ids are positional ("q04.7" is the eighth question of q04) and
# learners' review cards and history are keyed on them, so these ids must
# survive every later edit: questions are edited in place or appended, never
# reordered or deleted.
ORIGINAL_167 = "30ea2562b7542f46969046e40c504d669b6341f1cc71f7fcaf8854fef5b15c2d"
ORIGINAL_COUNTS = {
    "q00": 8, "q01": 10, "q02": 10, "q03": 8, "q04": 9, "q05": 9, "q06": 8,
    "q07": 9, "q08": 9, "q09": 9, "q10": 8, "q11": 10, "q12": 8, "q13": 9,
    "q14": 10, "q15": 9, "q16": 8, "q17": 8, "q18": 8,
}


@pytest.fixture(scope="module")
def questions(curriculum):
    return curriculum.all_questions


def _score(questions, choose) -> float:
    return sum(choose(q) == q.correct for q in questions) / len(questions)


def _first_max(values) -> int:
    values = list(values)
    return values.index(max(values))


def test_the_original_question_ids_are_unchanged(curriculum):
    ids = [q.id for quiz in curriculum.quizzes for q in quiz.questions
           if quiz.id in ORIGINAL_COUNTS
           and int(q.id.rsplit(".", 1)[1]) < ORIGINAL_COUNTS[quiz.id]]
    assert len(ids) == 167
    digest = hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
    assert digest == ORIGINAL_167


def test_question_ids_are_positional(curriculum):
    for quiz in curriculum.quizzes:
        for i, q in enumerate(quiz.questions):
            assert q.id == "%s.%d" % (quiz.id, i)


def test_no_answer_position_is_over_or_under_used(questions):
    counts = Counter(q.correct for q in questions)
    n = len(questions)
    for position in range(4):
        share = counts.get(position, 0) / n
        assert 0.15 <= share <= 0.35, (position, dict(counts))


def test_no_quiz_leans_on_one_position(curriculum):
    for quiz in curriculum.quizzes:
        counts = Counter(q.correct for q in quiz.questions)
        worst = max(counts.values()) / len(quiz.questions)
        assert worst <= 0.6, (quiz.id, dict(counts))


@pytest.mark.parametrize("position", range(4))
def test_always_pressing_one_button_fails(questions, position):
    assert _score(questions, lambda q: position) < 0.40


def test_picking_the_longest_choice_fails(questions):
    assert _score(questions, lambda q: _first_max(map(len, q.choices))) < 0.40


def test_picking_the_wordiest_choice_fails(questions):
    score = _score(questions, lambda q: _first_max(
        len(c.split()) for c in q.choices))
    assert score < 0.40


def test_the_correct_answer_is_not_usually_the_longest(questions):
    longest = sum(len(q.choices[q.correct]) == max(map(len, q.choices))
                  for q in questions)
    assert longest / len(questions) < 0.45


def test_the_correct_answer_is_not_padded(questions):
    """Within 1.6x the mean length of the distractors, so length alone does
    not give the answer away."""
    for q in questions:
        others = [len(c) for i, c in enumerate(q.choices) if i != q.correct]
        assert len(q.choices[q.correct]) <= 1.6 * sum(others) / len(others), q.id


ABSOLUTE = re.compile(r"\b(always|never|only|cannot|guarantees?)\b", re.I)


def test_absolutes_do_not_mark_the_distractors(questions):
    """'always', 'never' and friends confined to wrong answers are a
    test-wiseness cue; keep that pattern rare."""
    confined = sum(
        1 for q in questions
        if any(ABSOLUTE.search(c) for i, c in enumerate(q.choices)
               if i != q.correct)
        and not ABSOLUTE.search(q.choices[q.correct]))
    assert confined / len(questions) <= 0.10


def test_every_choice_has_its_own_explanation(questions):
    for q in questions:
        assert len(q.explain_choice) == len(q.choices), q.id
        assert q.explain_choice[q.correct] == "", q.id
        for i, note in enumerate(q.explain_choice):
            if i != q.correct:
                assert note.strip(), (q.id, i)


def test_every_question_has_four_distinct_choices(questions):
    for q in questions:
        assert len(q.choices) == 4, q.id
        assert len(set(q.choices)) == 4, q.id


def test_teaches_names_a_real_checklist_item(curriculum, questions):
    items = {i.id for p in curriculum.phases for i in p.items}
    items |= {g.id for p in curriculum.phases if p.gate for g in p.gate.items}
    # A few older questions check an item another phase teaches (q00.5 asks
    # about the src layout from p03), so the phase is not required to match.
    for q in questions:
        if q.teaches:
            assert q.teaches in items, q.id


def test_every_phase_with_trackable_work_has_a_quiz(curriculum):
    quizzed = {quiz.phase for quiz in curriculum.quizzes}
    for phase in curriculum.scored_phases:
        assert phase.id in quizzed, phase.id


def test_every_quiz_is_in_some_tracks_plan(curriculum):
    """p18 and p99 were in no track's core or optional list, so their quiz
    and checks never reached Today, the meter or the review deck."""
    planned = set()
    for track in curriculum.tracks:
        planned |= set(track.core) | set(track.optional)
    for quiz in curriculum.quizzes:
        assert quiz.phase in planned, quiz.id
    for phase in curriculum.scored_phases:
        assert phase.id in planned, phase.id


def test_a_bundle_without_the_new_fields_still_loads():
    old = {"id": "q00.0", "prompt": "Why?", "choices": ["a", "b", "c", "d"],
           "correct": 2, "explain": "Because."}
    q = _question(old)
    assert q.explain_choice == ()
    assert q.teaches == ""
    assert q.correct == 2
    assert getattr(q, "explain_choice", ()) == ()


def test_a_note_list_of_the_wrong_length_is_dropped_not_misaligned():
    bad = {"id": "q00.0", "prompt": "Why?", "choices": ["a", "b", "c", "d"],
           "correct": 0, "explain": "Because.", "explain_choice": ["", "x"]}
    assert _question(bad).explain_choice == ()
