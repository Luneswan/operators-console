"""The object every view is handed.

Bundling the services in one place keeps view constructors short and gives a
single point to emit change notifications from, so a checkbox ticked in the
phase view updates the dashboard without either knowing about the other.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..core.adaptive import Planner
from ..core.curriculum import Curriculum, load
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
