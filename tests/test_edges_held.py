"""Edge cases probed on 2026-09-22 that the code already handled.

Kept as regression coverage: each is an attempt to break storage, history,
the scheduler, the grader, the curriculum or search that did not break.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from operators_console.core import paths
from operators_console.core.history import History
from operators_console.core.models import TestCase as Case
from operators_console.core.runner import run_exercise
from operators_console.core.search import SearchIndex
from operators_console.core.srs import (
    DEFAULT_PARAMETERS, Memory, Rating, Scheduler, State,
)
from operators_console.core.storage import SCHEMA_VERSION, Store

START = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
VALUE = [Case("value is set", "assert value == 1")]


# ---------------------------------------------------------------------------
# storage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "emoji \U0001F600 and CJK 你好",
    "embedded\x00NUL",
    "LONG",
    "tabs\tand\r\nCRLF",
], ids=["emoji-cjk", "nul", "one-megabyte", "tab-crlf"])
def test_notes_survive_dump_json_and_restore(store, body):
    if body == "LONG":
        body = "x" * 1_000_000
    store.set_note("scope", body)
    payload = json.loads(json.dumps(store.dump(), ensure_ascii=False))
    store.reset_progress()
    store.restore(payload)
    assert store.note("scope") == body


def test_settings_and_projects_survive_a_restore(store):
    store.set_setting("learner_name", "Ada \U0001F600")
    store.set_setting("goals", ["web", "data"])
    store.set_project("pj.p00.1", status="shipped", repo_url="https://x/y",
                      notes="done")
    payload = json.loads(json.dumps(store.dump()))
    store.set_setting("learner_name", "")
    store.reset_progress()
    store.restore(payload)
    assert store.setting("learner_name") == "Ada \U0001F600"
    assert store.setting("goals") == ["web", "data"]
    assert store.project("pj.p00.1")["status"] == "shipped"
    assert store.project("pj.p00.1")["finished_at"]


def test_a_zero_byte_database_opens_as_an_empty_store(isolated_home):
    target = paths.db_path()
    target.write_bytes(b"")
    s = Store()
    try:
        assert s.get_meta("schema_version") == str(SCHEMA_VERSION)
        s.set_checked("x", True)
        assert s.is_checked("x")
    finally:
        s.close()


@pytest.mark.parametrize("fraction", [0.9, 0.5, 0.1])
def test_a_truncated_database_is_refused_at_open(isolated_home, fraction):
    """app.py catches the DatabaseError and shows its dialog."""
    s = Store()
    s.set_many_checked(["item-%05d-%s" % (i, "x" * 80) for i in range(3000)],
                       True)
    s.close()
    target = paths.db_path()
    data = target.read_bytes()
    target.write_bytes(data[: int(len(data) * fraction)])
    with pytest.raises(sqlite3.DatabaseError):
        Store()


def test_a_garbage_file_is_refused_and_left_unlocked(isolated_home):
    target = paths.db_path()
    target.write_bytes(b"not a database" * 100)
    with pytest.raises(sqlite3.DatabaseError):
        Store()
    moved = target.with_name("moved-aside.db")
    target.rename(moved)            # would fail on Windows if still open
    assert moved.exists()


def test_a_newer_schema_is_refused_and_the_file_stays_movable(store):
    store.set_meta("schema_version", str(SCHEMA_VERSION + 5))
    store.close()
    with pytest.raises(RuntimeError, match="newer"):
        Store()
    target = paths.db_path()
    target.rename(target.with_name("newer.db"))


# ---------------------------------------------------------------------------
# history
# ---------------------------------------------------------------------------

def test_a_long_chain_keeps_only_the_newest_hundred_and_unwinds_in_order():
    log = []
    history = History()
    for n in range(250):
        history.record(str(n), lambda n=n: log.append(-n), lambda n=n: log.append(n))
    undone = []
    while history.can_undo:
        undone.append(history.undo())
    assert undone == [str(n) for n in range(249, 149, -1)]
    redone = []
    while history.can_redo:
        redone.append(history.redo())
    assert redone == [str(n) for n in range(150, 250)]


def test_redo_is_gone_after_a_new_action_even_mid_chain():
    history = History()
    for n in range(5):
        history.record(str(n), lambda: None, lambda: None)
    history.undo()
    history.undo()
    history.record("new", lambda: None, lambda: None)
    assert not history.can_redo
    assert history.undo_label() == "new"


def test_undo_after_a_restore_and_after_a_reset_offers_nothing(store):
    history = History(store=store)
    store.set_checked("a", True)
    history.record("tick", lambda: store.set_checked("a", False),
                   lambda: store.set_checked("a", True))
    store.restore(store.dump())
    assert not history.can_undo and history.undo() == ""
    history.record("tick", lambda: None, lambda: None)
    store.reset_progress()
    assert not history.can_undo and not history.can_redo


# ---------------------------------------------------------------------------
# srs
# ---------------------------------------------------------------------------

@pytest.fixture
def exact():
    return Scheduler(enable_fuzz=False)


def test_ten_years_away_still_schedules_sanely(exact):
    memory = exact.review(Memory(), Rating.GOOD, START)
    memory = exact.review(memory, Rating.GOOD, START + timedelta(days=2))
    back = START + timedelta(days=3650)
    after = exact.review(memory, Rating.GOOD, back)
    assert after.state is State.REVIEW
    assert 1 <= (after.due - back).days <= 3650
    assert 0 < memory.retrievability(back) < 0.5


def test_zero_elapsed_and_same_second_duplicates_are_stable(exact):
    memory = exact.review(Memory(), Rating.GOOD, START)
    memory = exact.review(memory, Rating.GOOD, START + timedelta(days=5))
    again = memory
    for _ in range(20):
        again = exact.review(again, Rating.GOOD, START + timedelta(days=5))
    assert again.stability == pytest.approx(memory.stability)
    assert again.reps == memory.reps + 20


def test_many_lapses_keep_difficulty_and_intervals_in_bounds(exact):
    memory = Memory()
    now = START
    for n in range(60):
        memory = exact.review(memory, Rating.GOOD if n % 3 else Rating.AGAIN, now)
        assert 1.0 <= memory.difficulty <= 10.0
        assert memory.stability >= 0.001
        assert memory.due > now
        now = memory.due
    assert memory.lapses >= 1


def test_the_short_term_hard_clamp_matches_py_fsrs_main(exact):
    """py-fsrs main clamps the same-day increase to >= 1 for Hard, Good and
    Easy (checked against fsrs/scheduler.py on 2026-09-22)."""
    s = 7.5
    raw = (2.718281828459045 ** (DEFAULT_PARAMETERS[17]
                                 * (Rating.HARD - 3 + DEFAULT_PARAMETERS[18]))
           * s ** -DEFAULT_PARAMETERS[19])
    assert raw < 1.0
    assert exact._short_term_stability(s, Rating.HARD) == pytest.approx(s)


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

def test_input_with_no_stdin_fails_fast_and_keeps_the_prompt():
    result = run_exercise("name = input('Name? ')\nvalue = 1\n", VALUE,
                          timeout=20)
    assert not result.ok and not result.timed_out
    assert "EOFError" in result.error
    assert result.stdout == "Name? "


@pytest.mark.parametrize("code", [
    "if True:\r\n    value = 1\r\n",
    "if True:\r    value = 1\r",
])
def test_crlf_and_cr_line_endings_grade(code):
    assert run_exercise(code, VALUE, timeout=20).ok


def test_mixed_tabs_and_spaces_is_a_taberror():
    result = run_exercise("if True:\n\tx = 1\n        value = 1\n", VALUE,
                          timeout=20)
    assert "TabError" in result.summary


def test_keyboard_interrupt_and_deep_recursion_are_reported_not_hung():
    for code, expect in (("raise KeyboardInterrupt\n", "KeyboardInterrupt"),
                         ("def f(n): return f(n + 1)\nf(0)\n",
                          "RecursionError")):
        result = run_exercise(code, VALUE, timeout=20)
        assert not result.ok and not result.timed_out
        assert expect in result.summary


def test_a_main_guard_does_not_run_and_sys_exit_still_grades():
    assert run_exercise("value = 1\nif __name__ == '__main__':\n"
                        "    value = 2\n", VALUE, timeout=20).ok
    assert run_exercise("import sys\nvalue = 1\nsys.exit(3)\n", VALUE,
                        timeout=20).ok


def test_a_check_that_prints_nothing_passes():
    assert run_exercise("value = 1\n", [Case("silent", "pass")], timeout=20).ok


# ---------------------------------------------------------------------------
# curriculum and search
# ---------------------------------------------------------------------------

def test_card_ids_never_collide_across_questions_items_and_requirements(
        curriculum):
    """Question ids and concept item ids share the srs table; requirement
    ids share the checks table with items."""
    questions = [q.id for q in curriculum.all_questions]
    items = {i.id for p in curriculum.phases for i in p.items}
    items |= {g.id for p in curriculum.phases if p.gate for g in p.gate.items}
    reqs = {r for p in curriculum.projects for r in p.requirement_ids}
    assert len(questions) == len(set(questions))
    assert not set(questions) & items
    assert not set(questions) & reqs
    assert not items & reqs


def test_every_item_id_starts_with_its_phase_id(curriculum):
    """ReviewQueue._card_for_concept derives the phase from the id prefix."""
    for phase in curriculum.phases:
        ids = [i.id for i in phase.items]
        if phase.gate:
            ids += [g.id for g in phase.gate.items]
        assert all(i.split(".")[0] == phase.id for i in ids), phase.id


def test_every_quiz_points_at_a_real_phase(curriculum):
    known = {p.id for p in curriculum.phases}
    assert all(q.phase in known for q in curriculum.quizzes)


def test_every_search_target_resolves(curriculum):
    from operators_console.core.search import library_target
    index = SearchIndex(curriculum)
    shelf = {library_target("shelf", link.name)
             for group in curriculum.shelf for link in group.items}
    videos = {library_target("video", item.name)
              for group in curriculum.channels for item in group.items}
    check = {
        "shelf": lambda t: t in shelf,
        "video": lambda t: t in videos,
        "phase": lambda t: curriculum.phase(t) is not None,
        "item": lambda t: curriculum.item_text(t) != t,
        "exercise": lambda t: curriculum.exercise(t) is not None,
        "project": lambda t: curriculum.project(t) is not None,
        "question": lambda t: curriculum.question(t) is not None,
        "resource": lambda t: t.startswith("http"),
        "field": lambda t: any(f.id == t for f in curriculum.fields),
        "cert": lambda t: any(c.id == t for c in curriculum.certs),
    }
    for _haystack, hit in index.entries:
        assert check[hit.kind](hit.target), (hit.kind, hit.target)


@pytest.mark.parametrize("query", [
    "", " ", "a", "(", "[", "*", "?", ".*", "\\", "c++", "a.b", "%s", "\x00",
    "\U0001F600", "你好", "LONG", "\t\ngit\n",
])
def test_search_survives_any_query(curriculum, query):
    if query == "LONG":
        query = "x" * 10_000    # kept out of the test id: Windows caps env vars
    results = SearchIndex(curriculum).search(query)
    assert isinstance(results, list) and len(results) <= 60
