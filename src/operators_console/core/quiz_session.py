"""The rules of one quiz attempt that do not need a window.

* Every attempt draws a new layout: the questions in a new order and each
  question's choices in a new order, and never the layout of the previous
  attempt - a retake whose first question, or whose right answer sits under
  the same letter as last time, rewards remembering positions, not ideas.
* Every question has a countdown sized to how much there is to read. An
  answer given after it runs out is still marked and explained, but earns
  no mark, and an answer that was right but late is scheduled as Hard.
* The results say what to study, grouped by the line of the curriculum that
  teaches each missed question, rather than repeating the questions.
"""
from __future__ import annotations

import math
import random
import re

#: Seconds a learner gets per question: a floor for thinking, reading time
#: on top, and a ceiling so no question waits forever.
THINK_SECONDS = 15
WORDS_PER_SECOND = 3.0          # about 180 words a minute, read carefully
CODE_BONUS = 10                 # code in the question takes longer to trace
MIN_SECONDS = 20
MAX_SECONDS = 120

_WORD = re.compile(r"\S+")


def question_seconds(question) -> int:
    """How long `question` gets, rounded up to five seconds."""
    text = " ".join([question.prompt, *question.choices])
    words = len(_WORD.findall(text))
    seconds = THINK_SECONDS + words / WORDS_PER_SECOND
    if "`" in text or "(" in question.prompt:
        seconds += CODE_BONUS
    seconds = max(MIN_SECONDS, min(MAX_SECONDS, seconds))
    return int(math.ceil(seconds / 5.0) * 5)


def fresh_order(count: int, rng=None, last=None) -> list:
    """A shuffled range(count) that is not `last` and does not start as it did.

    With one or two items there are not enough orders to promise both; the
    promise is kept as far as the count allows.
    """
    rng = rng or random
    order = list(range(max(0, int(count))))
    last = list(last) if isinstance(last, (list, tuple)) else None
    if count < 2 or not last or sorted(last) != order:
        rng.shuffle(order)
        return order
    for _ in range(200):
        rng.shuffle(order)
        if order != last and (count < 3 or order[0] != last[0]):
            return order
    return order


def fresh_choice_order(count: int, correct: int, rng=None,
                       last_correct_at=None) -> list:
    """Choices in a new order, with the right one under a different letter.

    `order[shown_position]` is the stored choice index drawn there, as in
    core.review.choice_order.
    """
    rng = rng or random
    order = list(range(max(0, int(count))))
    rng.shuffle(order)
    if (count < 2 or not isinstance(last_correct_at, int)
            or not 0 <= correct < count):
        return order
    for _ in range(200):
        if order.index(correct) != last_correct_at:
            return order
        rng.shuffle(order)
    return order


def format_duration(seconds) -> str:
    """45 s, 3 min 12 s, 1 h 4 min - the words a person would say."""
    seconds = max(0, int(round(seconds or 0)))
    if seconds < 60:
        return "%d s" % seconds
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return "%d min %d s" % (minutes, secs) if secs else "%d min" % minutes
    hours, minutes = divmod(minutes, 60)
    return "%d h %d min" % (hours, minutes) if minutes else "%d h" % hours


# -- what to study -------------------------------------------------------------


def study_plan(curriculum, quiz, missed) -> list[dict]:
    """Missed questions grouped by the section of the curriculum that teaches them.

    Each group: phase (the Phase), section (its title, or "" when the
    questions name no line), items [(item_id, text)] to re-read, and the
    questions in it. Groups come in phase then section order, so the plan
    reads in the order the course teaches it.
    """
    groups: dict = {}
    order: list = []
    for question in missed:
        item_id = _teaching_item(curriculum, question)
        phase_id = item_id.split(".")[0] if item_id else quiz.phase
        phase = curriculum.phase(phase_id) or curriculum.phase(quiz.phase)
        section_title, section_index = "", 10 ** 6
        if item_id and phase is not None:
            for index, section in enumerate(phase.sections):
                if any(i.id == item_id for i in section.items):
                    section_title, section_index = section.title, index
                    break
            else:
                if phase.gate and any(g.id == item_id for g in phase.gate.items):
                    section_title, section_index = "Gate", 10 ** 5
        key = (phase.id if phase else quiz.phase, section_title)
        if key not in groups:
            groups[key] = {"phase": phase, "section": section_title,
                           "sort": (phase.num if phase else "", section_index),
                           "items": [], "questions": []}
            order.append(key)
        group = groups[key]
        if item_id and all(item_id != i for i, _ in group["items"]):
            group["items"].append((item_id, curriculum.item_text(item_id)))
        group["questions"].append(question)
    return sorted((groups[k] for k in order), key=lambda g: g["sort"])


def _teaching_item(curriculum, question) -> str:
    item_id = str(getattr(question, "teaches", "") or "").strip()
    if not item_id or curriculum.item_text(item_id) == item_id:
        return ""
    return item_id
