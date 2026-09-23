"""Base class for every page in the main window."""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..context import AppContext
from ..widgets.common import Scroller, label


def store_key(store, extra: tuple = ()) -> tuple:
    """What a page drew from: moves when anything in the store could have.

    total_changes counts this connection's writes; data_version moves when
    any other connection - a second copy of the app - commits.
    """
    try:
        version = store.db.execute("PRAGMA data_version").fetchone()[0]
    except Exception:
        version = None
    return (id(store), getattr(store.db, "total_changes", None), version,
            extra)


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

    @property
    def busy(self) -> bool:
        """True while the page holds work a rebuild would throw away."""
        return False

    def teardown(self) -> None:
        """Drop the page's widgets; the next visit builds them again.

        A new stylesheet re-polishes every live widget at about a millisecond
        each, so a theme change with every page built froze the app for
        seconds. Pages are cheap to build and already build lazily; the ones
        not on screen simply stop existing until they are needed.
        """
        if not self._built:
            return
        self.scroller.reset()
        self._built = False
        self._drawn_key = None

    # -- surviving a rebuild -----------------------------------------------

    _saved_state = None

    def save_state(self):
        """What the learner set on this page that a rebuild would lose.

        Filters, mostly. Return None when there is nothing worth keeping.
        Called while the widgets still exist, just before `teardown`.
        """
        return None

    def restore_state(self, state) -> None:
        """Put back what `save_state` returned, on a freshly built page.

        Called after the first `refresh` of the rebuilt page, so the page's
        lists are filled and a saved choice can find its row again. Anything
        that no longer exists (a restore took it away) is simply skipped.
        """

    def retire(self) -> None:
        """Tear the page down, remembering its filters for the next visit.

        A theme or text-size change retires every page that is not on
        screen. Before this, doing so quietly emptied every filter box and
        closed the exercise that was open.
        """
        if not self._built:
            return
        try:
            state = self.save_state()
        except RuntimeError:
            state = None            # a widget went early: keep nothing
        self.teardown()
        self._saved_state = state

    def restore_pending(self) -> None:
        """Hand a retired page its state back, once, after it is rebuilt."""
        state, self._saved_state = self._saved_state, None
        if state is None or not self._built:
            return
        self.restore_state(state)

    def show_target(self, target: str) -> None:
        """Navigate within the page, if it supports it."""

    def resume_target(self) -> str:
        """What `show_target` needs to bring a restarted app back here."""
        return ""

    def store_unchanged(self, *extra) -> bool:
        """True when nothing this page reads can have changed since it drew.

        SQLite counts every row this connection has ever inserted, updated or
        deleted (`Connection.total_changes`). A page that reads only the store
        and the static curriculum can skip its rebuild while that number - and
        anything else it depends on, passed as `extra` (the date, say) - is
        where it was. No change signal has to be remembered for this to stay
        correct: any write, from any path, moves the counter.

        Call it first in `refresh`, then `mark_drawn` once the page is drawn.
        """
        return self._drawn_key is not None and self._drawn_key == self._key(extra)

    def mark_drawn(self, *extra) -> None:
        """Remember the state the page now shows (see `store_unchanged`)."""
        self._drawn_key = self._key(extra)

    def _key(self, extra: tuple) -> tuple:
        return store_key(self.ctx.store, extra)

    _drawn_key = None

    # -- helpers -----------------------------------------------------------

    def header(self, title: str, kicker: str = "", aim: str = "") -> None:
        if kicker:
            self.scroller.add(label(kicker.upper(), "PageKicker", wrap=False))
        self.scroller.add(label(title, "PageTitle", wrap=True))
        if aim:
            self.scroller.add(label(aim, "PageAim"))
