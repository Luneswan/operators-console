"""The review queue.

Cards come from two places:

    quiz      every multiple-choice question in the curriculum
    concept   any roadmap line the learner has explicitly sent to review

Only material from phases the learner has actually reached enters the queue, so
review never asks about a topic before it has been taught. Daily limits keep a
long break from turning into an unopenable backlog.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from .curriculum import Curriculum
from .progress import Progress
from .srs import Memory, Rating, Scheduler, State
from .storage import Store

QUIZ = "quiz"
CONCEPT = "concept"


@dataclass(frozen=True, slots=True)
class Card:
    id: str
    kind: str
    phase: str
    front: str
    choices: tuple
    correct: int
    back: str
    memory: Memory

    @property
    def is_new(self) -> bool:
        return self.memory.state is State.NEW


@dataclass(frozen=True, slots=True)
class QueueCounts:
    due: int
    new: int
    learning: int
    backlog: int


class ReviewQueue:
    """Builds and serves the day's cards."""

    def __init__(self, curriculum: Curriculum, store: Store,
                 progress: Progress) -> None:
        self.c = curriculum
        self.s = store
        self.p = progress
        self.scheduler = Scheduler(
            desired_retention=float(self.s.setting("desired_retention", 0.90)))

    # -- eligibility -------------------------------------------------------

    def eligible_phase_ids(self) -> set:
        """Everything the learner has reached.

        That means any phase they have started, plus every earlier phase in
        the plan. Without the second half, someone who skipped ahead never
        sees review material for the ground they walked past, and the deck
        looks empty when it should not.
        """
        plan = self.p.active_phase_ids()
        stats = self.p.all_phases()
        started = {pid for pid in plan
                   if (stats.get(pid) and stats[pid].is_started)}
        out = set(started)
        if started:
            furthest = max(plan.index(pid) for pid in started)
            out.update(plan[:furthest + 1])
        elif plan:
            out.add(plan[0])
        return out

    def concept_ids(self) -> set:
        raw = self.s.setting("concept_cards", []) or []
        return set(raw)

    def add_concept(self, item_id: str) -> None:
        ids = self.concept_ids()
        ids.add(item_id)
        self.s.set_setting("concept_cards", sorted(ids))

    def remove_concept(self, item_id: str) -> None:
        ids = self.concept_ids()
        ids.discard(item_id)
        self.s.set_setting("concept_cards", sorted(ids))
        with self.s.tx():
            self.s.db.execute("DELETE FROM srs WHERE card_id=?", (item_id,))

    # -- building ----------------------------------------------------------

    def _card_for_question(self, question, quiz) -> Card:
        return Card(
            id=question.id, kind=QUIZ, phase=quiz.phase,
            front=question.prompt, choices=question.choices,
            correct=question.correct, back=question.explain,
            memory=self.s.memory(question.id),
        )

    def _card_for_concept(self, item_id: str) -> Card | None:
        text = self.c.item_text(item_id)
        if text == item_id:
            return None
        phase_id = item_id.split(".")[0]
        return Card(
            id=item_id, kind=CONCEPT, phase=phase_id,
            front="Can you explain, and use, this from memory?",
            choices=(), correct=-1, back=text,
            memory=self.s.memory(item_id),
        )

    def all_cards(self) -> list:
        eligible = self.eligible_phase_ids()
        cards = []
        for quiz in self.c.quizzes:
            if quiz.phase not in eligible:
                continue
            for question in quiz.questions:
                cards.append(self._card_for_question(question, quiz))
        for item_id in sorted(self.concept_ids()):
            card = self._card_for_concept(item_id)
            if card is not None:
                cards.append(card)
        return cards

    def counts(self, now: datetime | None = None) -> QueueCounts:
        now = now or datetime.now(timezone.utc)
        due = new = learning = 0
        for card in self.all_cards():
            m = card.memory
            if m.state is State.NEW:
                new += 1
            elif m.is_due(now):
                due += 1
                if m.state in (State.LEARNING, State.RELEARNING):
                    learning += 1
        limit = int(self.s.setting("max_reviews_per_day", 120))
        return QueueCounts(due=due, new=new, learning=learning,
                           backlog=max(0, due - limit))

    def session(self, now: datetime | None = None) -> list:
        """The ordered cards to study now, honouring the daily limits."""
        now = now or datetime.now(timezone.utc)
        new_limit = int(self.s.setting("new_cards_per_day", 15))
        review_limit = int(self.s.setting("max_reviews_per_day", 120))
        today = date.today().isoformat()
        studied = self.s.activity(days=1).get(today, {})
        already = int(studied.get("reviews", 0))
        review_limit = max(0, review_limit - already)

        due, fresh = [], []
        for card in self.all_cards():
            m = card.memory
            if m.state is State.NEW:
                fresh.append(card)
            elif m.is_due(now):
                due.append(card)

        due.sort(key=lambda c: (c.memory.due or now))
        fresh.sort(key=lambda c: c.id)

        introduced = self._new_introduced_today()
        room = max(0, new_limit - introduced)
        return due[:review_limit] + fresh[:room]

    def _new_introduced_today(self) -> int:
        today = date.today().isoformat()
        row = self.s.db.execute(
            "SELECT COUNT(DISTINCT card_id) AS n FROM reviews r WHERE r.day=? "
            "AND NOT EXISTS (SELECT 1 FROM reviews e WHERE e.card_id=r.card_id "
            "AND e.day<?)", (today, today)).fetchone()
        return int(row["n"] or 0)

    # -- answering ---------------------------------------------------------

    def answer(self, card: Card, rating: Rating,
               now: datetime | None = None) -> Memory:
        now = now or datetime.now(timezone.utc)
        updated = self.scheduler.review(card.memory, rating, now)
        self.s.save_memory(card.id, card.kind, card.phase, updated)
        self.s.log_review(card.id, int(rating), correct=rating is not Rating.AGAIN)
        return updated

    def preview(self, card: Card, now: datetime | None = None) -> dict:
        return self.scheduler.preview(card.memory, now)

    @staticmethod
    def rating_for_choice(card: Card, chosen: int, hesitated: bool) -> Rating:
        """Map a multiple-choice answer onto an FSRS rating.

        A wrong answer is always Again. A right answer that took a long time,
        or came after changing the selection, is Hard rather than Good, since
        slow recall predicts faster forgetting.
        """
        if chosen != card.correct:
            return Rating.AGAIN
        return Rating.HARD if hesitated else Rating.GOOD
