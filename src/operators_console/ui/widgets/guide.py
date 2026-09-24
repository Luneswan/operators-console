"""A checklist line with its study guide: how to do it, where to learn it, how
to tell it is done, and roughly how long it takes at this learner's pace.

The guide panel is built the first time it opens. A phase page has up to
forty lines and most guides are never opened, so building them all would
cost every page visit and every theme change for nothing. The toggle is a
link label rather than a button for the same reason (see CheckRow.more).
"""
from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.estimate import format_hours
from . import common
from .common import CheckRow, rich


def _link_label(html: str, name: str = "") -> QLabel:
    widget = QLabel(html)
    widget.setTextFormat(Qt.TextFormat.RichText)
    widget.setWordWrap(True)
    widget.setOpenExternalLinks(False)
    widget.setTextInteractionFlags(
        Qt.TextInteractionFlag.LinksAccessibleByMouse
        | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        | Qt.TextInteractionFlag.TextSelectableByMouse)
    if name:
        widget.setObjectName(name)
    return widget


class GuidedItem(QWidget):
    """A CheckRow, a "How" link beside it, and the guide under it."""

    INDENT = 28           # the guide lines up with the line's text

    def __init__(self, item, checked: bool, minutes: float = 0.0,
                 opened: bool = False, next_step: bool = False,
                 parent=None) -> None:
        super().__init__(parent)
        self.item = item
        self.minutes = minutes
        self.next_step = next_step
        self.panel = None
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)
        self.row = CheckRow(item.id, item.text, checked)
        top.addWidget(self.row, 1)
        self.has_guide = bool(item.how or item.where or item.done)
        self.toggle_link = None
        if self.has_guide:
            self.row.menu_extras = (("Show or hide how to do this",
                                     self.toggle),)
            self.toggle_link = _link_label("", "GuideToggle")
            self.toggle_link.setAccessibleName("How to do this line")
            self.toggle_link.linkActivated.connect(lambda _href: self.toggle())
            top.addWidget(self.toggle_link, 0, Qt.AlignmentFlag.AlignTop)
        column.addLayout(top)
        self._label_toggle(False)
        if opened and self.has_guide:
            self.set_open(True)

    @property
    def is_open(self) -> bool:
        return self.panel is not None and not self.panel.isHidden()

    def toggle(self) -> None:
        self.set_open(not self.is_open)

    def set_open(self, opened: bool) -> None:
        if not self.has_guide:
            return
        if opened and self.panel is None:
            self.panel = self._build_panel()
            self.layout().addWidget(self.panel)
        if self.panel is not None:
            self.panel.setVisible(opened)
        self._label_toggle(opened)

    def _label_toggle(self, opened: bool) -> None:
        if self.toggle_link is not None:
            self.toggle_link.setText('<a href="how">%s</a>'
                                     % ("Hide" if opened else "How"))

    def _build_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("GuidePanel")
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        outer = QHBoxLayout(panel)
        outer.setContentsMargins(self.INDENT, 2, 0, 8)
        box = QFrame()
        box.setObjectName("GuideBox")
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lines = QVBoxLayout(box)
        lines.setContentsMargins(12, 10, 12, 10)
        lines.setSpacing(6)
        heading = "NEXT STEP" if self.next_step else "HOW TO DO IT"
        if self.minutes >= 1:
            heading += "  -  about %s at your pace" % format_hours(self.minutes)
        caption = QLabel(heading)
        caption.setObjectName("GuideCaption")
        lines.addWidget(caption)
        if self.item.how:
            how = _link_label(rich(self.item.how), "GuideText")
            lines.addWidget(how)
        if self.item.where:
            links = "  -  ".join(
                '<a href="%s">%s</a>' % (escape(link.url, quote=True),
                                         escape(link.name))
                for link in self.item.where)
            where = _link_label("<b>Learn it:</b> " + links, "GuideText")
            where.linkActivated.connect(
                lambda url: common.open_url(url))
            where.setToolTip("\n".join(link.url for link in self.item.where))
            lines.addWidget(where)
        if self.item.done:
            done = _link_label("<b>Done when:</b> " + rich(self.item.done),
                               "GuideMuted")
            lines.addWidget(done)
        outer.addWidget(box, 1)
        return panel
