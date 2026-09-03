"""Undo and redo: the safety net for a mis-click."""
from __future__ import annotations

from operators_console.core.history import History


def test_a_fresh_history_offers_nothing():
    history = History()
    assert not history.can_undo and not history.can_redo
    assert history.undo() == "" and history.redo() == ""


def test_undo_runs_the_reversal_once():
    state = {"value": 1}
    history = History()
    state["value"] = 2
    history.record("change",
                   lambda: state.__setitem__("value", 1),
                   lambda: state.__setitem__("value", 2))
    assert history.undo() == "change"
    assert state["value"] == 1
    assert not history.can_undo and history.can_redo


def test_redo_puts_it_back():
    state = {"value": 1}
    history = History()
    history.record("change",
                   lambda: state.__setitem__("value", 1),
                   lambda: state.__setitem__("value", 2))
    history.undo()
    assert history.redo() == "change"
    assert state["value"] == 2
    assert history.can_undo and not history.can_redo


def test_a_new_change_discards_the_redo_branch():
    history = History()
    history.record("first", lambda: None, lambda: None)
    history.undo()
    assert history.can_redo
    history.record("second", lambda: None, lambda: None)
    assert not history.can_redo


def test_undoing_does_not_record_itself():
    """Without this guard a view that rebuilds would loop forever."""
    history = History()
    log = []

    def undo():
        history.record("echo", lambda: None, lambda: None)
        log.append("undone")

    history.record("change", undo, lambda: None)
    history.undo()
    assert log == ["undone"]
    assert not history.can_undo


def test_the_stack_is_bounded():
    history = History(limit=5)
    for index in range(20):
        history.record("change %d" % index, lambda: None, lambda: None)
    assert len(history._undo) == 5
    assert history.undo_label() == "change 19"


def test_many_steps_unwind_in_order():
    order = []
    history = History()
    for index in range(4):
        history.record("step %d" % index,
                       lambda i=index: order.append(("undo", i)),
                       lambda i=index: order.append(("redo", i)))
    for _ in range(4):
        history.undo()
    assert order == [("undo", 3), ("undo", 2), ("undo", 1), ("undo", 0)]
    for _ in range(4):
        history.redo()
    assert order[4:] == [("redo", 0), ("redo", 1), ("redo", 2), ("redo", 3)]


def test_clear_empties_both_stacks():
    history = History()
    history.record("change", lambda: None, lambda: None)
    history.undo()
    history.record("другое", lambda: None, lambda: None)
    history.clear()
    assert not history.can_undo and not history.can_redo
