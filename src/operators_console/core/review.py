"""The review queue.

Cards come from three places:

    quiz      every multiple-choice question in the curriculum
    gate      every gate check of a phase the learner has reached - they are
              already written as "do this from memory" statements
    concept   any roadmap line the learner has sent to review, and the line
              that teaches a quiz question the learner got wrong

Only material from phases the learner has actually reached enters the queue, so
review never asks about a topic before it has been taught. Daily limits keep a
long break from turning into an unopenable backlog.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, timezone

from .curriculum import Curriculum
from .progress import Progress
from .srs import Memory, Rating, Scheduler, State
from .storage import Store

QUIZ = "quiz"
CONCEPT = "concept"
GATE = "gate"

#: Kinds answered by recalling a line and revealing it, not by picking.
RECALL_KINDS = (CONCEPT, GATE)


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


def concept_cue(text: str) -> str:
    """The front of a saved line: enough to recall it by, not the line.

    The card used to ask "Can you explain, and use, this from memory?"
    without ever saying what "this" was. The topic before a dash or a colon
    is the cue when there is one; otherwise the first half of the sentence,
    to be finished from memory.
    """
    plain = text.replace("<em>", "").replace("</em>", "").strip()
    for mark in (" — ", " - ", ": "):
        head, found, _rest = plain.partition(mark)
        if found and 2 <= len(head.split()) <= 12:
            return head.rstrip(".") + " ..."
    words = plain.split()
    if len(words) <= 4:
        return plain
    return " ".join(words[:max(3, len(words) // 2)]) + " ..."


def choice_order(count: int, rng=None) -> list:
    """A fresh order to show ``count`` choices in, as stored indexes.

    ``order[shown_position]`` is the stored index of the choice drawn there.
    Almost every correct answer in the bank sits in the same stored slot, so
    showing the choices as stored let a learner who always pressed the second
    option score nearly full marks without reading a word.
    """
    order = list(range(max(0, int(count))))
    (rng or random).shuffle(order)
    return order


def valid_order(order, count: int) -> bool:
    """True when ``order`` is a permutation of ``range(count)``."""
    if not isinstance(order, (list, tuple)) or len(order) != count:
        return False
    if not all(isinstance(i, int) and not isinstance(i, bool) for i in order):
        return False
    return sorted(order) == list(range(count))


def choice_feedback(question, chosen: int) -> str:
    """What the chosen option gets wrong (or right), when it was written.

    ``explain_choice`` is indexed by the stored choice index. An empty entry,
    a missing field or a skipped question (``chosen`` below zero) gives "",
    and the general explanation stands on its own.
    """
    notes = getattr(question, "explain_choice", ()) or ()
    if not isinstance(chosen, int) or chosen < 0 or chosen >= len(notes):
        return ""
    return str(notes[chosen] or "").strip()


def teaching_item(curriculum, question) -> str:
    """The id of the line that teaches ``question``, when it names a real one."""
    item_id = str(getattr(question, "teaches", "") or "").strip()
    if not item_id or curriculum.item_text(item_id) == item_id:
        return ""
    return item_id


def _retention(value) -> float:
    """The setting, held inside the range the scheduler accepts.

    The queue is built while the app starts, so a value from a hand-edited
    or imported backup that the scheduler refuses would stop the app from
    opening at all.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.90
    if value != value:              # NaN
        return 0.90
    return min(0.99, max(0.70, value))


class ReviewQueue:
    """Builds and serves the day's cards."""

    def __init__(self, curriculum: Curriculum, store: Store,
                 progress: Progress) -> None:
        self.c = curriculum
        self.s = store
        self.p = progress
        self.scheduler = Scheduler(desired_retention=_retention(
            self.s.setting("desired_retention", 0.90)))

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
        # A phase with a scheduled card has been touched, plan or not: a quiz
        # taken off the plan must not leave its wrong answers unreviewable.
        out.update(row["phase"] for row in self.s.db.execute(
            "SELECT DISTINCT phase FROM srs WHERE phase != ''"))
        return out

    def card_for_question(self, question, quiz) -> Card:
        return self._card_for_question(question, quiz)

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

    # -- burying -----------------------------------------------------------

    def suspended_ids(self) -> set:
        """Every card the learner has buried.

        Read straight from the row rather than through ``Memory``: burying is
        a property of the deck, not of the memory, and nothing in the
        scheduler has an opinion about it.
        """
        return {row["card_id"] for row in self.s.db.execute(
            "SELECT card_id FROM srs WHERE suspended=1")}

    def bury(self, card: Card) -> None:
        """Put one card away, answered or not.

        ``Store.suspend_card`` updates the card's row, and a card nobody has
        answered yet has no row to update: burying went through the motions
        and changed nothing. Writing the memory the card already carries
        gives the flag somewhere to live without inventing a schedule.
        """
        self.s.save_memory(card.id, card.kind, card.phase, card.memory)
        self.s.suspend_card(card.id, True)

    def restore_suspended(self) -> int:
        """Bring every buried card back, and say how many that was."""
        buried = self.suspended_ids()
        if buried:
            with self.s.tx():
                self.s.db.execute("UPDATE srs SET suspended=0 "
                                  "WHERE suspended=1")
        return len(buried)

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
            front=concept_cue(text),
            choices=(), correct=-1, back=text,
            memory=self.s.memory(item_id),
        )

    def _card_for_gate(self, phase, item) -> Card:
        """A gate check as a recall card: the cue on the front, the check behind.

        Gate checks lean on the note above them ("For each structure you
        implemented ...") and on each other; the Review page shows that note
        beside the check when it is revealed (``gate_note``).
        """
        return Card(
            id=item.id, kind=GATE, phase=phase.id,
            front=concept_cue(item.text),
            choices=(), correct=-1, back=item.text,
            memory=self.s.memory(item.id),
        )

    def gate_note(self, card: Card) -> str:
        """The note a gate check is read under, for the back of its card."""
        if card.kind != GATE:
            return ""
        phase = self.c.phase(card.phase)
        if phase is None or phase.gate is None:
            return ""
        return (phase.gate.note or "").strip()

    def all_cards(self) -> list:
        """Every card the deck can offer today.

        Buried cards are dropped here rather than in ``session``, so that the
        counts the page shows and the queue it hands out agree: a card the
        learner has put away must not keep appearing in "due now".
        """
        eligible = self.eligible_phase_ids()
        buried = self.suspended_ids()
        cards = []
        for quiz in self.c.quizzes:
            if quiz.phase not in eligible:
                continue
            for question in quiz.questions:
                if question.id in buried:
                    continue
                cards.append(self._card_for_question(question, quiz))
        concepts = self.concept_ids()
        for item_id in sorted(concepts):
            if item_id in buried:
                continue
            card = self._card_for_concept(item_id)
            if card is not None:
                cards.append(card)
        # Gate checks join the deck once their phase is reached. A check the
        # learner already sent to review by hand stays the one card it was.
        for phase in self.c.phases:
            if phase.id not in eligible or phase.gate is None:
                continue
            for item in phase.gate.items:
                if item.id in buried or item.id in concepts:
                    continue
                cards.append(self._card_for_gate(phase, item))
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
        fresh = _interleave(fresh)

        # The cap is for mature reviews. A card failed a minute ago is still
        # in its learning steps and has to come back today, or the learner is
        # offered new cards while the ones they just got wrong are withheld.
        stepping = [c for c in due
                    if c.memory.state in (State.LEARNING, State.RELEARNING)]
        mature = [c for c in due if c not in stepping][:review_limit]
        chosen = sorted(stepping + mature, key=lambda c: (c.memory.due or now))

        introduced = self._new_introduced_today()
        room = max(0, new_limit - introduced)
        return chosen + fresh[:room]

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
        if card.kind == QUIZ and rating is Rating.AGAIN:
            self.enrol_teaching(self.c.question(card.id))
        return updated

    def enrol_teaching(self, question) -> str:
        """Put the line that teaches a missed question into the deck.

        A wrong answer used to bring back only the multiple-choice question,
        which can be relearned as "the second one". The prose it tests comes
        back too, as a recall card. Returns the item id, or "" when the
        question names no line or the line is already in the deck. Taking the
        answer back leaves the line in the deck: it was still missed once.
        """
        if question is None:
            return ""
        item_id = teaching_item(self.c, question)
        if not item_id or item_id in self.concept_ids():
            return ""
        self.add_concept(item_id)
        return item_id

    def undo_answer(self, card: Card, previous: Memory) -> None:
        """Take back the last answer given to this card.

        Restoring the schedule is only half of it. ``Store.log_review`` also
        wrote a row in ``reviews`` and counted a review against the day, and
        both are read back: by the accuracy figure, by the daily ceiling, and
        by the count of new cards introduced today. Left behind, a rating the
        learner took back would still be shortening their session and
        dragging their accuracy down.
        """
        self.s.save_memory(card.id, card.kind, card.phase, previous)
        row = self.s.db.execute(
            "SELECT id, day FROM reviews WHERE card_id=? "
            "ORDER BY id DESC LIMIT 1", (card.id,)).fetchone()
        if row is None:
            return
        with self.s.tx():
            self.s.db.execute("DELETE FROM reviews WHERE id=?", (row["id"],))
            self.s.db.execute(
                "UPDATE activity SET reviews=max(0, reviews-1) WHERE day=?",
                (row["day"],))

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


def _interleave(cards: list) -> list:
    """New cards in turn by kind - a question, a gate check, a saved line.

    Sorted by id alone, every gate check of every reached phase came before
    the first quiz question, so a day's new cards were one kind of card.
    """
    lanes: dict = {}
    for card in sorted(cards, key=lambda c: c.id):
        lanes.setdefault(card.kind, []).append(card)
    order = [QUIZ, GATE, CONCEPT] + sorted(
        k for k in lanes if k not in (QUIZ, GATE, CONCEPT))
    queues = [lanes[k] for k in order if k in lanes]
    out = []
    while any(queues):
        for lane in queues:
            if lane:
                out.append(lane.pop(0))
    return out
