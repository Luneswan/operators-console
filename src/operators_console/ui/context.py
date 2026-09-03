"""The object every view is handed.

Bundling the services in one place keeps view constructors short and gives a
single point to emit change notifications from, so a checkbox ticked in the
phase view updates the dashboard without either knowing about the other.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..core.adaptive import Planner
from ..core.curriculum import Curriculum, load
from ..core.history import History
from ..core.progress import Progress
from ..core.review import ReviewQueue
from ..core.search import SearchIndex
from ..core.storage import Store
from ..core.today import TodayPlan
from .theme import Palette, resolve


class AppContext(QObject):
    """Shared services plus the signals that keep views in step."""

    progress_changed = Signal()
    settings_changed = Signal()
    theme_changed = Signal()
    navigate = Signal(str, str)      # view name, target id
    history_changed = Signal()
    toast = Signal(str)

    def __init__(self, store: Store | None = None,
                 curriculum: Curriculum | None = None,
                 parent=None) -> None:
        super().__init__(parent)
        self.curriculum: Curriculum = curriculum or load()
        self.store: Store = store or Store()
        self.progress = Progress(self.curriculum, self.store)
        self.planner = Planner(self.curriculum, self.store, self.progress)
        self.today = TodayPlan(self.curriculum, self.store, self.progress,
                               self.planner)
        self.review = ReviewQueue(self.curriculum, self.store, self.progress)
        self.index = SearchIndex(self.curriculum)
        self.history = History()
        self._palette = resolve(self.store.setting("theme", "system"), False)
        self._dark_hint = False

    # -- theme -------------------------------------------------------------

    @property
    def palette(self) -> Palette:
        return self._palette

    def set_dark_hint(self, dark: bool) -> None:
        self._dark_hint = dark
        self.refresh_palette()

    def refresh_palette(self) -> None:
        self._palette = resolve(self.store.setting("theme", "system"),
                                self._dark_hint)
        self.theme_changed.emit()

    # -- convenience -------------------------------------------------------

    def rebuild_review(self) -> None:
        """Pick up a changed retention target without restarting."""
        self.review = ReviewQueue(self.curriculum, self.store, self.progress)

    def announce(self, message: str) -> None:
        self.toast.emit(message)

    def changed(self) -> None:
        self.progress_changed.emit()

    # -- undo and redo -----------------------------------------------------

    def record(self, label: str, undo, redo) -> None:
        """Remember a reversible change and refresh the undo buttons."""
        self.history.record(label, undo, redo)
        self.history_changed.emit()

    def set_checked(self, item_id: str, done: bool) -> None:
        """Tick or untick a line, and make it undoable.

        Views call this rather than the store directly, so that every
        checkbox in the app is covered by one implementation.
        """
        self.store.set_checked(item_id, done)
        self.record(
            "tick" if done else "untick",
            lambda: self._restore_check(item_id, not done),
            lambda: self._restore_check(item_id, done))
        self.changed()

    def _restore_check(self, item_id: str, done: bool) -> None:
        self.store.set_checked(item_id, done)
        self.changed()

    def set_project_status(self, project_id: str, status: str) -> None:
        previous = self.store.project(project_id)["status"]
        self.store.set_project(project_id, status=status)
        self.record(
            "project status",
            lambda: self._restore_project(project_id, previous),
            lambda: self._restore_project(project_id, status))
        self.changed()

    def _restore_project(self, project_id: str, status: str) -> None:
        self.store.set_project(project_id, status=status)
        self.changed()

    def set_cert_status(self, cert_id: str, status: int) -> None:
        previous = self.store.cert_status(cert_id)
        self.store.set_cert_status(cert_id, status)
        self.record(
            "certificate status",
            lambda: self._restore_cert(cert_id, previous),
            lambda: self._restore_cert(cert_id, status))

    def _restore_cert(self, cert_id: str, status: int) -> None:
        self.store.set_cert_status(cert_id, status)
        self.changed()

    def set_rating(self, topic: str, value: int) -> None:
        previous = self.store.rating(topic)
        self.store.set_rating(topic, value)
        self.record(
            "self-assessment",
            lambda: self._restore_rating(topic, previous),
            lambda: self._restore_rating(topic, value))

    def _restore_rating(self, topic: str, value: int) -> None:
        self.store.set_rating(topic, value)
        self.changed()

    def undo(self) -> str:
        label = self.history.undo()
        self.history_changed.emit()
        return label

    def redo(self) -> str:
        label = self.history.redo()
        self.history_changed.emit()
        return label
