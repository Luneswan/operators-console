"""Base class for every page in the main window."""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..context import AppContext
from ..widgets.common import Scroller, label


class View(QWidget):
    """A page. Subclasses fill `build()` and refresh themselves on demand."""

    title = ""
    kicker = ""

    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._built = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.scroller = Scroller()
        outer.addWidget(self.scroller)

    # -- lifecycle ---------------------------------------------------------

    def ensure_built(self) -> None:
        if not self._built:
            self.build()
            self._built = True

    def build(self) -> None:
        """Create the page. Called once, lazily, on first display."""

    def refresh(self) -> None:
        """Re-read state and update. Called every time the page is shown."""

    def show_target(self, target: str) -> None:
        """Navigate within the page, if it supports it."""

    # -- helpers -----------------------------------------------------------

    def header(self, title: str, kicker: str = "", aim: str = "") -> None:
        if kicker:
            self.scroller.add(label(kicker.upper(), "PageKicker", wrap=False))
        self.scroller.add(label(title, "PageTitle", wrap=True))
        if aim:
            self.scroller.add(label(aim, "PageAim"))
