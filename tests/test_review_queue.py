"""The review deck: what enters it, what leaves it, and the daily limits."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operators_console.core.review import CONCEPT, QUIZ, ReviewQueue
from operators_console.core.srs import Rating, State


@pytest.fixture
def queue(curriculum, store, progress):
    return ReviewQueue(curriculum, store, progress)


def start_phase(curriculum, store, phase_id, count=3):
    phase = curriculum.phase(phase_id)
    store.set_many_checked([item.id for item in phase.items][:count], True)


def test_nothing_is_asked_about_before_it_is_taught(curriculum, store, queue):
    eligible = queue.eligible_phase_ids()
    assert eligible == {"p00"}
    assert all(card.phase == "p00" for card in queue.all_cards())


def test_reaching_a_later_phase_opens_the_earlier_ones(curriculum, store,
                                                       progress, queue):
    start_phase(curriculum, store, "p02")
    fresh = ReviewQueue(curriculum, store, progress)
    eligible = fresh.eligible_phase_ids()
    assert {"p00", "p01", "p02"} <= eligible


def test_a_saved_line_becomes_a_concept_card(curriculum, store, progress, queue):
    item = curriculum.phase("p00").items[0]
    queue.add_concept(item.id)
    fresh = ReviewQueue(curriculum, store, progress)
    cards = {card.id: card for card in fresh.all_cards()}
    assert item.id in cards
    assert cards[item.id].kind == CONCEPT
    assert cards[item.id].choices == ()


def test_removing_a_concept_forgets_its_schedule(curriculum, store, progress,
                                                 queue):
    item = curriculum.phase("p00").items[0]
    queue.add_concept(item.id)
    card = next(c for c in queue.all_cards() if c.id == item.id)
    queue.answer(card, Rating.GOOD)
    assert store.memory(item.id).state is not State.NEW
    queue.remove_concept(item.id)
    assert store.memory(item.id).state is State.NEW
    assert item.id not in queue.concept_ids()


def test_new_cards_are_capped_per_day(curriculum, store, progress):
    store.set_setting("new_cards_per_day", 3)
    queue = ReviewQueue(curriculum, store, progress)
    session = queue.session()
    assert len(session) == 3


def test_a_zero_new_limit_means_no_new_cards(curriculum, store, progress):
    store.set_setting("new_cards_per_day", 0)
    queue = ReviewQueue(curriculum, store, progress)
    assert queue.session() == []


def test_reviews_are_capped_per_day(curriculum, store, progress):
    overdue = datetime.now(timezone.utc) - timedelta(days=1)
    questions = curriculum.quizzes_for("p00")[0].questions
    from operators_console.core.srs import Memory
    for question in questions:
        store.save_memory(question.id, QUIZ, "p00",
                          Memory(stability=2.0, difficulty=5.0,
                                 state=State.REVIEW, due=overdue,
                                 last_review=overdue, reps=1))
    store.set_setting("max_reviews_per_day", 2)
    store.set_setting("new_cards_per_day", 0)
    queue = ReviewQueue(curriculum, store, progress)
    assert len(queue.session()) == 2


def test_answering_writes_both_a_schedule_and_a_history_row(curriculum, store,
                                                            queue):
    card = queue.session()[0]
    queue.answer(card, Rating.GOOD)
    assert store.memory(card.id).reps == 1
    correct, total = store.review_accuracy(1)
    assert (correct, total) == (1, 1)


def test_a_wrong_answer_is_recorded_as_incorrect(curriculum, store, queue):
    card = queue.session()[0]
    queue.answer(card, Rating.AGAIN)
    correct, total = store.review_accuracy(1)
    assert (correct, total) == (0, 1)


def test_the_preview_offers_four_intervals(queue):
    card = queue.session()[0]
    preview = queue.preview(card)
    assert set(preview) == set(Rating)


def test_a_wrong_choice_always_maps_to_again(queue):
    card = queue.session()[0]
    wrong = (card.correct + 1) % len(card.choices)
    assert ReviewQueue.rating_for_choice(card, wrong, False) is Rating.AGAIN


def test_a_slow_correct_answer_maps_to_hard(queue):
    card = queue.session()[0]
    assert ReviewQueue.rating_for_choice(card, card.correct, True) is Rating.HARD
    assert ReviewQueue.rating_for_choice(card, card.correct, False) is Rating.GOOD


def test_counts_add_up(curriculum, store, progress, queue):
    counts = queue.counts()
    assert counts.new == len(queue.all_cards())
    assert counts.due == 0
    assert counts.backlog == 0
