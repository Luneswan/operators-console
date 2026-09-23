"""Undo and redo at the edges where it could lie to the learner.

The stack holds closures, not data. That is cheap and it works, right up to
the moment the rows those closures describe stop existing - after a reset, or
after restoring a backup. An undo offered then would write a fragment of the
old world into the new one and call it a correction.
"""
from __future__ import annotations

import pytest

from operators_console.core.history import History


def test_a_zero_limit_really_keeps_nothing():
    """`del stack[:-0]` deletes nothing, so limit 0 kept everything."""
    history = History(limit=0)
    for i in range(5):
        history.record("x%d" % i, lambda: None, lambda: None)
    assert not history.can_undo


def test_a_limit_of_one_keeps_only_the_last():
    history = History(limit=1)
    history.record("first", lambda: None, lambda: None)
    history.record("second", lambda: None, lambda: None)
    assert history.undo_label() == "second"
    history.undo()
    assert not history.can_undo


def test_an_undo_that_fails_stays_undoable():
    """A failed reversal must not strand the action on neither stack.

    Popping before running meant an exception left the change unreachable
    from both directions: no undo, no redo, and no way back.
    """
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("the row is gone")

    history = History()
    history.record("tick", flaky, lambda: None)
    with pytest.raises(RuntimeError):
        history.undo()
    assert history.can_undo, "the action vanished from both stacks"
    assert history.undo_label() == "tick"
    assert history.undo() == "tick"
    assert history.can_redo


def test_a_reset_drops_the_undo_stack(store):
    """Undo must not resurrect progress the learner deliberately wiped."""
    history = History(store=store)
    store.set_checked("p01.s0.0", True)
    history.record("tick",
                   lambda: store.set_checked("p01.s0.0", False),
                   lambda: store.set_checked("p01.s0.0", True))
    assert history.can_undo

    store.reset_progress()
    assert not history.can_undo, "undo still offered after a wipe"
    assert not history.can_redo
    assert history.undo() == ""
    assert not store.checked_ids(), "undo resurrected wiped progress"


def test_restoring_a_backup_drops_the_undo_stack(store):
    """A redo must not contaminate freshly restored data.

    The learner restores a backup precisely because the current state is
    wrong. Replaying a change recorded against that wrong state puts part of
    it back, into a database that no longer has any context for it.
    """
    store.set_checked("old-world", True)
    snapshot = store.dump()
    store.set_checked("the-mistake", True)

    history = History(store=store)
    history.record("tick",
                   lambda: store.set_checked("the-mistake", False),
                   lambda: store.set_checked("the-mistake", True))
    history.undo()
    assert history.can_redo

    store.restore(snapshot)
    assert not history.can_redo
    assert history.redo() == ""
    assert sorted(store.checked_ids()) == ["old-world"]


def test_an_ordinary_edit_does_not_drop_the_stack(store):
    history = History(store=store)
    store.set_checked("a", True)
    history.record("tick",
                   lambda: store.set_checked("a", False),
                   lambda: store.set_checked("a", True))
    store.set_checked("b", True)
    store.set_rating("loops", 2)
    assert history.can_undo
    history.undo()
    assert not store.is_checked("a")
    assert store.is_checked("b")


def test_undoing_across_a_reset_cannot_half_apply(store):
    """Several recorded actions, one wipe: none of them may survive."""
    history = History(store=store)
    for i in range(5):
        item = "item-%d" % i
        store.set_checked(item, True)
        history.record(
            "tick",
            lambda item=item: store.set_checked(item, False),
            lambda item=item: store.set_checked(item, True))
    store.reset_progress()
    for _ in range(5):
        assert history.undo() == ""
    assert not store.checked_ids()


def test_a_history_with_no_store_still_works():
    """The stack is usable on its own, for tests and for tools."""
    seen = []
    history = History()
    history.record("x", lambda: seen.append("undo"), lambda: seen.append("redo"))
    history.undo()
    history.redo()
    assert seen == ["undo", "redo"]
