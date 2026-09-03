"""Undo and redo for anything the learner can change by accident.

Every reversible action is recorded as a small object that knows how to put
things back. That is deliberately narrower than a full transaction log: the
point is to rescue a mis-click, not to version the database. Actions that are
genuinely destructive already take a backup of their own, and actions that
cannot be undone honestly are simply not recorded.

The stack is capped and lives only for the session. Nothing here is persisted,
because an undo offered after a restart would promise more than it can deliver.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

LIMIT = 100


@dataclass(frozen=True, slots=True)
class Action:
    """One reversible change, with a label the interface can show."""

    label: str
    undo: Callable[[], None]
    redo: Callable[[], None]


class History:
    """A bounded undo and redo stack."""

    def __init__(self, limit: int = LIMIT) -> None:
        self.limit = limit
        self._undo: list[Action] = []
        self._redo: list[Action] = []
        self._applying = False

    # -- recording ---------------------------------------------------------

    def record(self, label: str, undo: Callable[[], None],
               redo: Callable[[], None]) -> None:
        """Remember a change that has already happened.

        Calls made while undoing or redoing are ignored, so a view that
        rebuilds itself in response cannot push the same action back on.
        """
        if self._applying:
            return
        self._undo.append(Action(label, undo, redo))
        del self._undo[:-self.limit]
        self._redo.clear()

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    # -- state -------------------------------------------------------------

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo_label(self) -> str:
        return self._undo[-1].label if self._undo else ""

    def redo_label(self) -> str:
        return self._redo[-1].label if self._redo else ""

    # -- applying ----------------------------------------------------------

    def undo(self) -> str:
        if not self._undo:
            return ""
        action = self._undo.pop()
        self._run(action.undo)
        self._redo.append(action)
        return action.label

    def redo(self) -> str:
        if not self._redo:
            return ""
        action = self._redo.pop()
        self._run(action.redo)
        self._undo.append(action)
        return action.label

    def _run(self, call: Callable[[], None]) -> None:
        self._applying = True
        try:
            call()
        finally:
            self._applying = False
