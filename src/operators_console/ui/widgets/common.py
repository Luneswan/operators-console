"""Small building blocks shared by every view."""
from __future__ import annotations

import re
from contextlib import contextmanager

from PySide6.QtCore import (
    Property, QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer,
    Signal,
)
from PySide6.QtGui import QDesktopServices, QFont, QPainter, QPalette
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ..theme import mono_family, reduced_motion

_EM = re.compile(r"</?em>")


def plain(text: str) -> str:
    """Strip the curriculum's inline code markers."""
    return _EM.sub("", text)


def rich(text: str, struck: bool = False) -> str:
    """Render the curriculum's <em> markers as inline code.

    `struck` strikes the prose of a finished item and leaves its code spans
    whole: a line through monospace text made the very thing the item was
    about unreadable.
    """
    escaped = (text.replace("&", "&amp;")
               .replace("<em>", "\x01").replace("</em>", "\x02")
               .replace("<", "&lt;").replace(">", "&gt;"))
    if struck:
        parts = re.split(r"(\x01.*?\x02)", escaped)
        escaped = "".join(
            part if part.startswith("\x01") else ("<s>%s</s>" % part if part
                                                  else "")
            for part in parts)
    return escaped.replace("\x01", "<code>").replace("\x02", "</code>")


def label(text: str, object_name: str = "", wrap: bool = True,
          selectable: bool = False) -> QLabel:
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    widget.setWordWrap(wrap)
    if selectable:
        widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
    return widget


def heading(text: str) -> QLabel:
    return label(text, "SectionTitle", wrap=False)


def muted(text: str) -> QLabel:
    return label(text, "Muted")


def soft(text: str) -> QLabel:
    return label(text, "Soft")


def divider() -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    return line


def spacer(height: int = 0) -> QWidget:
    widget = QWidget()
    if height:
        widget.setFixedHeight(height)
    else:
        widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Expanding)
    return widget


def button(text: str, kind: str = "", tooltip: str = "") -> QPushButton:
    btn = QPushButton(text)
    if kind:
        btn.setProperty("kind", kind)
    if tooltip:
        btn.setToolTip(tooltip)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def pill(text: str, tone: str = "") -> QLabel:
    widget = QLabel(text)
    widget.setObjectName("Pill")
    if tone:
        widget.setProperty("tone", tone)
    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return widget


def meter(value: int, maximum: int = 100, tone: str = "") -> QProgressBar:
    bar = QProgressBar()
    bar.setRange(0, max(maximum, 1))
    bar.setValue(value)
    bar.setTextVisible(False)
    bar.setFixedHeight(6)
    if tone:
        bar.setProperty("tone", tone)
    return bar


def mono_label(text: str) -> QLabel:
    widget = label(text, "Mono", wrap=False)
    font = QFont(mono_family())
    font.setPointSize(10)
    widget.setFont(font)
    return widget


class Card(QFrame):
    """A bordered panel with a vertical layout already in place."""

    def __init__(self, flat: bool = False, padding: int = 16,
                 spacing: int = 8, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CardFlat" if flat else "Card")
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(padding, padding, padding, padding)
        self.box.setSpacing(spacing)

    def add(self, widget: QWidget, stretch: int = 0):
        self.box.addWidget(widget, stretch)
        return widget

    def add_row(self, *widgets, spacing: int = 8) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(spacing)
        row.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            if widget is None:
                row.addStretch(1)
            else:
                row.addWidget(widget)
        self.box.addLayout(row)
        return row


def empty_state(title: str, hint: str = "") -> "Card":
    """What a page says when it has nothing to show.

    An empty page should still tell you where you are and what would fill it,
    rather than leaving a blank rectangle that reads as a bug.
    """
    card = Card(flat=True, padding=18, spacing=6)
    card.add(label(title, "EmptyState", wrap=True))
    if hint:
        card.add(muted(hint))
    return card


class ElidedLabel(QLabel):
    """A label that cuts its text with an ellipsis rather than asking for room.

    ``text()`` is the whole message; the paint shows what fits and the
    tooltip carries the rest. The status bar uses it so a long message can
    never widen the window.
    """

    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Ignored,
                           QSizePolicy.Policy.Preferred)

    def paintEvent(self, _event) -> None:
        rect = self.contentsRect()
        whole = self.text()
        shown = self.fontMetrics().elidedText(
            whole, Qt.TextElideMode.ElideRight, rect.width())
        if shown != whole:
            if self.toolTip() != whole:
                self.setToolTip(whole)
        elif self.toolTip():
            self.setToolTip("")
        painter = QPainter(self)
        self.style().drawItemText(
            painter, rect, int(self.alignment()) | Qt.TextFlag.TextSingleLine,
            self.palette(), self.isEnabled(), shown,
            QPalette.ColorRole.WindowText)
        painter.end()


class Scroller(QScrollArea):
    """A vertical scroll area with a ready-made content column."""

    def __init__(self, margins=(24, 24, 24, 40), spacing: int = 16,
                 parent=None) -> None:
        super().__init__(parent)
        self._margins, self._spacing = margins, spacing
        self.setWidgetResizable(True)
        # Content that cannot fit the width scrolls sideways rather than
        # losing its right edge. At every supported window size nothing
        # needs to; a 1.6x text size in a 1024 px window does.
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Not a Tab stop: focused, it showed nothing, so Tab seemed to vanish.
        # Tabbing onto a control inside still scrolls it into view.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.body = QWidget()
        self.column = QVBoxLayout(self.body)
        self.column.setContentsMargins(*margins)
        self.column.setSpacing(spacing)
        self.setWidget(self.body)

    def add(self, widget: QWidget, stretch: int = 0):
        self.column.addWidget(widget, stretch)
        return widget

    def add_layout(self, layout):
        self.column.addLayout(layout)
        return layout

    def add_stretch(self) -> None:
        self.column.addStretch(1)

    def clear(self) -> None:
        with frozen(self.body):
            clear_layout(self.column)

    def reset(self) -> None:
        """Throw the whole content tree away in one move.

        `clear` walks the layout and retires every widget from Python, which
        costs a Python round trip each: emptying a built page of three
        thousand widgets took seconds, and a theme change does it to every
        page at once. Handing the scroll area a fresh body instead lets Qt
        delete the old tree in C++, and the page is rebuilt on its next
        visit either way.
        """
        old = self.body
        old.hide()                      # never let it flash as a window
        self.body = QWidget()
        self.column = QVBoxLayout(self.body)
        self.column.setContentsMargins(*self._margins)
        self.column.setSpacing(self._spacing)
        # setWidget deletes the widget it replaces, tree and all, in C++.
        self.setWidget(self.body)

    @contextmanager
    def rebuilding(self):
        """Empty and refill this column with a single repaint at the end."""
        with frozen(self.body):
            clear_layout(self.column)
            yield self


class Column(QWidget):
    """A Scroller's content column without the scrolling.

    For content inside a page that already scrolls. A scroll area inside the
    scrolling page gave the Library's tabs a 260-pixel window on a 640-pixel
    screen, and kept the page header pinned while only the tab moved.
    """

    def __init__(self, margins=(0, 0, 0, 0), spacing: int = 16,
                 parent=None) -> None:
        super().__init__(parent)
        self.body = self
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(*margins)
        self.column.setSpacing(spacing)

    def add(self, widget: QWidget, stretch: int = 0):
        self.column.addWidget(widget, stretch)
        return widget

    def add_layout(self, layout):
        self.column.addLayout(layout)
        return layout

    def add_stretch(self) -> None:
        self.column.addStretch(1)

    @contextmanager
    def rebuilding(self):
        with frozen(self):
            clear_layout(self.column)
            yield self


def discard(widget: QWidget) -> None:
    """Retire a widget without ever letting it become a window of its own.

    ``setParent(None)`` on a widget that is currently laid out inside a shown
    window promotes it to a top-level ``Qt::Window``. Qt has already marked it
    created and not-hidden, so it is given a real native handle and shown: a
    small empty window appears at the corner of the screen and vanishes again
    when the deferred delete runs. Rebuilding a page orphans dozens of widgets
    at once, which is the flicker of tiny windows opening and closing.

    Hiding first sets WA_WState_Hidden together with WA_WState_ExplicitShowHide,
    so the detach that follows is silent.
    """
    widget.hide()
    widget.setParent(None)
    widget.deleteLater()


def clear_layout(layout) -> None:
    """Empty a layout, discarding every widget and nested layout in it.

    Painting on the owning widget is suspended until control returns to the
    event loop. Every caller clears and refills in one go, so this turns a
    rebuild into a single repaint instead of one per widget landing.
    """
    _freeze_for_this_turn(layout.parentWidget())
    _strip(layout)


def _strip(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            discard(widget)
        else:
            child = item.layout()
            if child is not None:
                _strip(child)
                child.deleteLater()


def _freeze_for_this_turn(widget) -> None:
    if widget is None or not widget.updatesEnabled():
        return
    widget.setUpdatesEnabled(False)

    def thaw(target=widget):
        try:
            target.setUpdatesEnabled(True)
        except RuntimeError:
            pass          # the page was torn down before the loop came back

    QTimer.singleShot(0, thaw)


@contextmanager
def frozen(widget: QWidget):
    """Suspend painting while a subtree is torn down and rebuilt.

    Without this the intermediate states of a rebuild reach the screen one
    widget at a time, which reads as flicker even when no window is created.
    """
    was_enabled = widget.updatesEnabled()
    widget.setUpdatesEnabled(False)
    try:
        yield
    finally:
        widget.setUpdatesEnabled(was_enabled)


# Kept for callers that still import the private name.
_drop_layout = clear_layout


class CheckRow(QWidget):
    """One curriculum line with its checkbox, plus a menu of its own.

    The menu used to be on the right mouse button and nothing else, on a row
    that could not take the focus: "Add to review deck" - the only way into
    the review deck there is - was unreachable without a mouse, and invisible
    to anyone who never thought to right-click a line. It now opens three
    ways: the right button, Shift+F10 or the Menu key while the row's
    checkbox has the focus, and the quiet "..." that appears at the row's
    right edge as the mouse reaches it.

    The row takes the focus through the checkbox rather than beside it, so a
    page of forty lines is still forty Tab stops rather than eighty.
    """

    toggled = Signal(str, bool)
    review_requested = Signal(str)
    remove_requested = Signal(str)

    MORE_WIDTH = 26
    # (text, handler) pairs a page adds to this row's menu.
    menu_extras: tuple = ()

    def __init__(self, item_id: str, text: str, checked: bool,
                 parent=None, in_deck: bool | None = None) -> None:
        super().__init__(parent)
        self.item_id = item_id
        self.raw_text = text
        self._in_deck = in_deck
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(8)

        self.box = QCheckBox()
        self.box.setChecked(checked)
        self.box.setFixedWidth(20)
        self.box.stateChanged.connect(self._on_toggle)
        row.addWidget(self.box, 0, Qt.AlignmentFlag.AlignTop)

        self.text = QLabel(rich(text))
        self.text.setWordWrap(True)
        self.text.setTextFormat(Qt.TextFormat.RichText)
        self.text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        # Top, beside its checkbox. Centred, the line floated away from the
        # box whenever anything made the row taller than one line.
        self.text.setAlignment(Qt.AlignmentFlag.AlignLeft
                               | Qt.AlignmentFlag.AlignTop)
        row.addWidget(self.text, 1, Qt.AlignmentFlag.AlignTop)

        # The "..." is built the first time the mouse comes near the row,
        # into space reserved from the start so that nothing moves when it
        # appears. See the `more` property for why it is not built here.
        self._line = row
        self._more = None
        # A spacer put there by addSpacing takes no spacing of its own, so
        # the gap has to stand in for the button and for the gap beside it.
        row.addSpacing(self.MORE_WIDTH + row.spacing())

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocusProxy(self.box)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)
        self._restyle(checked)

    def _on_toggle(self) -> None:
        state = self.box.isChecked()
        self._restyle(state)
        self.toggled.emit(self.item_id, state)

    def _restyle(self, checked: bool) -> None:
        self.text.setProperty("done", "true" if checked else "false")
        self.text.setText(rich(self.raw_text, struck=checked))
        self.text.setStyleSheet(
            "color: palette(placeholder-text);" if checked else "")

    def set_checked(self, checked: bool) -> None:
        blocked = self.box.blockSignals(True)
        self.box.setChecked(checked)
        self.box.blockSignals(blocked)
        self._restyle(checked)

    # -- the "..." handle --------------------------------------------------

    @property
    def more(self) -> QPushButton:
        """The handle that opens this row's menu, built on first demand.

        A QPushButton on every one of a hundred roadmap lines is not free:
        the sheet has a dozen QPushButton rules to match against each of
        them, and a theme change re-polishes the lot. Built for every line,
        it put the theme-switch budget in `test_theme_switch` over its 2.5 s
        limit; built on demand it costs nothing until a mouse arrives. The
        space it will take is reserved from the start, so the line does not
        move as it appears.
        """
        if self._more is None:
            self._more = button("...", "quiet",
                                "More for this line (Shift+F10)")
            self._more.setFixedWidth(self.MORE_WIDTH)
            # No taller than the checkbox line: a full-height button built
            # on first hover made the row grow under the mouse, and every
            # line dropped as the pointer passed over it.
            self._more.setFixedHeight(self.line_height())
            # Not a Tab stop: the keyboard opens this menu from the row.
            self._more.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._more.clicked.connect(self._menu_from_button)
            gap = self._line.takeAt(self._line.count() - 1)
            del gap                 # the reserved space, now filled
            self._line.addWidget(self._more, 0, Qt.AlignmentFlag.AlignTop)
            # A child added to a live layout is not shown until the parent
            # gets round to it, and a hidden widget takes no space: without
            # this the line does shift, by exactly the width reserved.
            self._more.show()
        return self._more

    def line_height(self) -> int:
        """The height of the checkbox line, which the handle must not pass."""
        return max(self.box.sizeHint().height(),
                   self.text.fontMetrics().height())

    def enterEvent(self, event) -> None:
        self.more                   # noqa: B018 - builds it on first hover
        super().enterEvent(event)

    # -- the review deck ---------------------------------------------------

    def set_in_deck(self, in_deck: bool | None) -> None:
        """Say whether this line is already a review card.

        ``None`` puts the question back to the page the row is sitting in.
        """
        self._in_deck = in_deck

    def is_in_deck(self) -> bool:
        if self._in_deck is not None:
            return bool(self._in_deck)
        review = self._review()
        try:
            return review is not None and self.item_id in review.concept_ids()
        except Exception:
            return False            # a closed store is not a crash here

    def _reviewable(self) -> bool:
        """Whether this line could become a review card at all.

        A project requirement is a CheckRow like any other, but it is not a
        curriculum line: the deck can never build a card from its id, so
        "Add to review deck" there was an entry that did nothing. Where there
        is no page to ask, the entry stays exactly as it was.
        """
        curriculum = getattr(self._context(), "curriculum", None)
        if curriculum is None:
            return True
        try:
            return curriculum.item_text(self.item_id) != self.item_id
        except Exception:
            return True

    def _context(self):
        """The services of whichever page this row was laid out in."""
        node = self.parentWidget()
        while node is not None:
            ctx = getattr(node, "ctx", None)
            if ctx is not None:
                return ctx
            node = node.parentWidget()
        return None

    def _review(self):
        return getattr(self._context(), "review", None)

    def _join_deck(self) -> None:
        self.review_requested.emit(self.item_id)

    def _leave_deck(self) -> None:
        review = self._review()
        if review is not None:
            review.remove_concept(self.item_id)
        if self._in_deck is not None:
            self._in_deck = False
        context = self._context()
        if context is not None:
            context.announce("Removed from the review deck.")
        self.remove_requested.emit(self.item_id)

    # -- the menu ----------------------------------------------------------

    def build_menu(self):
        """The row's menu, built but not shown.

        Kept apart from showing it so that the three ways in share one list,
        and so a test can read what is on offer without a modal popup.
        """
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        if self.is_in_deck():
            menu.addAction("Remove from review deck", self._leave_deck)
        elif self._reviewable():
            menu.addAction("Add to review deck", self._join_deck)
        menu.addAction(
            "Copy text",
            lambda: _copy(plain(self.raw_text)))
        for text, handler in self.menu_extras:
            menu.addAction(text, handler)
        menu.aboutToHide.connect(menu.deleteLater)
        return menu

    def _popup(self, point) -> None:
        # popup(), not exec(): a nested event loop inside a key handler is
        # what makes a menu impossible to drive and easy to get stuck in.
        self.build_menu().popup(self.mapToGlobal(point))

    def _menu(self, point) -> None:
        self._popup(point)

    def _menu_from_button(self) -> None:
        self._popup(self.more.geometry().bottomLeft())

    def keyPressEvent(self, event) -> None:
        """Shift+F10 and the Menu key open the row's menu.

        Both arrive here from the checkbox, which ignores them. Accepting
        them also stops Windows raising its own context menu on top of this
        one when the platform sees the key go unhandled.
        """
        menu_key = event.key() == Qt.Key.Key_Menu
        shift_f10 = (event.key() == Qt.Key.Key_F10
                     and event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if menu_key or shift_f10:
            self._popup(self.rect().bottomLeft())
            event.accept()
            return
        super().keyPressEvent(event)


def _copy(text: str) -> None:
    from PySide6.QtWidgets import QApplication
    QApplication.clipboard().setText(text)


class LinkRow(QWidget):
    """A resource line: name, why it is worth your time, and an open button.

    The trailing block is a fixed width so that every Open button in a card
    lands on the same vertical line, whatever the kind pill says.
    """

    TRAILING_WIDTH = 150

    def __init__(self, name: str, why: str, url: str, kind: str = "",
                 primary: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.url = url
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(8)

        column = QVBoxLayout()
        column.setSpacing(2)
        self.title = QLabel(name)
        self.title.setObjectName("LinkTitle")
        self.title.setProperty("lead", "true" if primary else "false")
        self.title.setWordWrap(True)
        column.addWidget(self.title)
        if why:
            column.addWidget(muted(why))
        row.addLayout(column, 1)

        trailing = QWidget(self)
        trailing.setMinimumWidth(self.TRAILING_WIDTH)
        bar = QHBoxLayout(trailing)
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(8)
        bar.addStretch(1)
        if kind:
            # Centred on the Open button beside it, not hung from the top.
            bar.addWidget(pill(kind), 0, Qt.AlignmentFlag.AlignVCenter)
        self.open_button = None
        if url:
            self.open_button = button(
                "Open", "primary" if primary else "quiet", url)
            self.open_button.setMinimumWidth(62)
            self.open_button.clicked.connect(lambda: open_url(url))
            bar.addWidget(self.open_button, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(trailing, 0, Qt.AlignmentFlag.AlignTop)


def open_url(url: str) -> None:
    from PySide6.QtCore import QUrl
    if url:
        QDesktopServices.openUrl(QUrl(url))


class StatTile(Card):
    """A single headline number with a caption."""

    def __init__(self, value: str, caption: str, hint: str = "",
                 parent=None) -> None:
        super().__init__(padding=16, spacing=4, parent=parent)
        self.value_label = label(value, "Big", wrap=False)
        self.box.addWidget(self.value_label)
        self.caption_label = label(caption, "Soft", wrap=False)
        self.box.addWidget(self.caption_label)
        if hint:
            self.box.addWidget(muted(hint))

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class _Chevron(QWidget):
    """A small chevron that turns a quarter-circle when its group opens."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._angle = 0.0
        self.setFixedSize(12, 12)

    def get_angle(self) -> float:
        return self._angle

    def set_angle(self, value: float) -> None:
        self._angle = float(value)
        self.update()

    angle = Property(float, get_angle, set_angle)

    def paintEvent(self, event) -> None:
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QPainter, QPen, QPolygonF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.rotate(self._angle)
        pen = QPen(self.palette().placeholderText().color())
        pen.setWidthF(1.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolyline(QPolygonF([QPointF(-2.0, -3.6),
                                        QPointF(1.8, 0.0),
                                        QPointF(-2.0, 3.6)]))
        painter.end()


class _ToggleRow(QPushButton):
    """A pressable row whose height comes from the widgets laid out inside it.

    QPushButton sizes itself from its own text and icon and ignores a layout
    put inside it, which clips the caption. This asks the layout instead.
    """

    def sizeHint(self) -> QSize:
        base = super().sizeHint()
        box = self.layout()
        if box is None:
            return base
        hint = box.totalSizeHint()
        return QSize(max(base.width(), hint.width()),
                     max(base.height(), hint.height()))

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()


class Disclosure(QWidget):
    """The primary row, and everything optional folded beneath it.

    Only groups the curriculum marks optional are ever folded. The one
    resource worth starting with stays in full view; the rest sit behind a
    quiet line that says how many there are and what they are for. Open or
    closed is remembered per group, so opening it once is enough.
    """

    REVEAL_MS = 180

    toggled_open = Signal(bool)

    def __init__(self, count: int, noun: str = "to study", store=None,
                 key: str = "", tag: str = "OPTIONAL", more: bool = True,
                 parent=None) -> None:
        super().__init__(parent)
        # "more" only when something is already showing above the fold.
        self._more_word = "more " if more else ""
        self._store = store
        self._key = key
        self._count = count
        self._noun = noun
        self._open = False
        if store is not None and key:
            self._open = bool(store.disclosure_open(key))

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)

        self.toggle = _ToggleRow(self)
        self.toggle.setObjectName("DisclosureToggle")
        self.toggle.setCheckable(True)
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toggle.clicked.connect(
            lambda _=False: self.set_open(not self._open))
        row = QHBoxLayout(self.toggle)
        row.setContentsMargins(0, 5, 0, 5)
        row.setSpacing(8)
        self.chevron = _Chevron(self.toggle)
        row.addWidget(self.chevron, 0, Qt.AlignmentFlag.AlignVCenter)
        self.caption = QLabel("", self.toggle)
        self.caption.setObjectName("DisclosureCaption")
        row.addWidget(self.caption, 0, Qt.AlignmentFlag.AlignVCenter)
        # What is folded here is the optional half of the group, and a
        # three-word caption is a weak place to say so.
        self.tag = pill(tag) if tag else None
        if self.tag is not None:
            row.addWidget(self.tag, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addStretch(1)
        column.addWidget(self.toggle)

        self.body = QWidget(self)
        self.body.setObjectName("DisclosureBody")
        self.stack = QVBoxLayout(self.body)
        # Folded rows sit a step in from the one that matters.
        self.stack.setContentsMargins(16, 2, 0, 0)
        self.stack.setSpacing(0)
        column.addWidget(self.body)

        self._reveal = QPropertyAnimation(self.body, b"maximumHeight", self)
        self._reveal.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._reveal.finished.connect(self._settle)
        self._turn = QPropertyAnimation(self.chevron, b"angle", self)
        self._turn.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._sync(animate=False)

    # -- content -----------------------------------------------------------

    def add(self, widget: QWidget) -> QWidget:
        """Add one folded row. Call before the group is first shown."""
        self.stack.addWidget(widget)
        self._sync(animate=False)
        return widget

    # -- state -------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self._open

    @property
    def count(self) -> int:
        return self._count

    def set_count(self, count: int) -> None:
        """Say how many rows the fold holds now - after a filter, say.

        Only the words change: the fold stays open or closed as it was, and
        nothing is written to the store.
        """
        count = max(0, int(count))
        if count == self._count:
            return
        self._count = count
        caption, action = self.words()
        self.caption.setText(caption)
        self.toggle.setToolTip(action)
        self.toggle.setAccessibleName(caption)
        self.toggle.setAccessibleDescription(action)

    def set_open(self, is_open: bool, animate: bool = True) -> None:
        is_open = bool(is_open)
        if is_open == self._open:
            return
        self._open = is_open
        if self._store is not None and self._key:
            self._store.set_disclosure_open(self._key, is_open)
        self._sync(animate=animate)
        self.toggled_open.emit(is_open)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                           Qt.Key.Key_Space):
            self.set_open(not self._open)
            event.accept()
            return
        super().keyPressEvent(event)

    # -- presentation ------------------------------------------------------

    def words(self) -> tuple[str, str]:
        """The caption, and what pressing it will do - both in words."""
        thing = "%d %s%s" % (self._count, self._more_word, self._noun)
        if self._open:
            return ("Showing " + thing,
                    "Hide the %d optional one%s"
                    % (self._count, "" if self._count == 1 else "s"))
        return thing, "Show " + thing

    def _sync(self, animate: bool) -> None:
        caption, action = self.words()
        self.caption.setText(caption)
        self.toggle.setChecked(self._open)
        self.toggle.setToolTip(action)
        self.toggle.setAccessibleName(caption)
        self.toggle.setAccessibleDescription(action)
        self.toggle.setProperty("open", "true" if self._open else "false")
        repolish(self.toggle)

        self._focusable(self._open)
        self._reveal.stop()
        self._turn.stop()
        full = max(self.body.sizeHint().height(), 1)
        target = full if self._open else 0

        if not animate or reduced_motion():
            self.body.setVisible(self._open)
            self.body.setMaximumHeight(target)
            self.chevron.set_angle(90.0 if self._open else 0.0)
            self._settle()
            return

        start = self.body.height() if self.body.isVisible() else 0
        self.body.setVisible(True)
        self.body.setMaximumHeight(start)
        # An interrupted reveal finishes in proportion to what is left, so a
        # quick second press never replays the whole distance.
        span = min(1.0, abs(target - start) / full)
        self._reveal.setDuration(max(60, int(self.REVEAL_MS * span)))
        self._reveal.setStartValue(start)
        self._reveal.setEndValue(target)
        self._reveal.start()
        self._turn.setDuration(self.REVEAL_MS)
        self._turn.setStartValue(self.chevron.get_angle())
        self._turn.setEndValue(90.0 if self._open else 0.0)
        self._turn.start()

    def _settle(self) -> None:
        if self._open:
            self.body.setMaximumHeight(16777215)
        else:
            self.body.setVisible(False)
        self.updateGeometry()

    def _focusable(self, can_focus: bool) -> None:
        """A row that cannot be reached must not be reachable by Tab either."""
        for child in self.body.findChildren(QWidget):
            if can_focus:
                saved = child.property("_saved_focus")
                if saved is not None:
                    child.setFocusPolicy(Qt.FocusPolicy(saved))
            elif child.focusPolicy() != Qt.FocusPolicy.NoFocus:
                child.setProperty("_saved_focus",
                                  int(child.focusPolicy().value))
                child.setFocusPolicy(Qt.FocusPolicy.NoFocus)


def repolish(widget: QWidget) -> None:
    """Make a changed dynamic property take effect in the stylesheet."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
