"""The library: books, courses, channels, fields of work and certificates."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QTabWidget

from ..widgets.common import (
    Card, LinkRow, Scroller, button, heading, label, muted, pill,
)
from .base import View

CERT_STATES = ("Not started", "In progress", "Earned")
CERT_TONES = ("", "warn", "done")


class LibraryView(View):
    title = "Library"

    def build(self) -> None:
        self.scroller.column.setContentsMargins(24, 20, 24, 20)
        self.header("Library", "everything worth reading",
                    "Curated rather than exhaustive. If something is not here, "
                    "it did not earn a place.")
        self.tabs = QTabWidget()
        self.scroller.add(self.tabs, 1)

        self.shelf_tab = Scroller(margins=(4, 12, 4, 20))
        self.fields_tab = Scroller(margins=(4, 12, 4, 20))
        self.channels_tab = Scroller(margins=(4, 12, 4, 20))
        self.certs_tab = Scroller(margins=(4, 12, 4, 20))
        self.tabs.addTab(self.shelf_tab, "Shelf")
        self.tabs.addTab(self.fields_tab, "Fields of work")
        self.tabs.addTab(self.channels_tab, "Video")
        self.tabs.addTab(self.certs_tab, "Certificates")

    def refresh(self) -> None:
        self._fill_shelf()
        self._fill_fields()
        self._fill_channels()
        self._fill_certs()

    def _fill_shelf(self) -> None:
        self.shelf_tab.clear()
        for group in self.ctx.curriculum.shelf:
            card = Card()
            card.add(heading(group.group))
            for link in group.items:
                card.add(LinkRow(link.name, "", link.url))
            self.shelf_tab.add(card)
        self.shelf_tab.add_stretch()

    def _fill_fields(self) -> None:
        self.fields_tab.clear()
        self.fields_tab.add(muted(
            "Pick one or two. Breadth without depth reads as inexperience."))
        current_group = None
        for field in self.ctx.curriculum.fields:
            if field.group != current_group:
                current_group = field.group
                self.fields_tab.add(heading(current_group))
            card = Card()
            title = label(field.name, wrap=False)
            title.setStyleSheet("font-size: 15px; font-weight: 700;")
            card.add(title)
            card.add(label(field.blurb, "Soft"))
            card.add(muted("Build to prove it: " + field.build))
            row = QHBoxLayout()
            row.setSpacing(6)
            for link in field.libs:
                widget = button(link.name, "quiet", link.url)
                widget.clicked.connect(
                    lambda _=False, u=link.url: _open(u))
                row.addWidget(widget)
            row.addStretch(1)
            card.box.addLayout(row)
            self.fields_tab.add(card)
        self.fields_tab.add_stretch()

    def _fill_channels(self) -> None:
        self.channels_tab.clear()
        self.channels_tab.add(muted(
            "Watching is not learning. Use these to unblock a concept, then "
            "close the tab and write code."))
        for group in self.ctx.curriculum.channels:
            card = Card()
            card.add(heading(group.group))
            for item in group.items:
                card.add(LinkRow(item.name, item.why, item.url))
            self.channels_tab.add(card)
        self.channels_tab.add_stretch()

    def _fill_certs(self) -> None:
        self.certs_tab.clear()
        self.certs_tab.add(muted(
            "A certificate is a receipt for time spent. A shipped project is "
            "evidence of ability. Prefer the second."))
        for cert in self.ctx.curriculum.certs:
            state = self.ctx.store.cert_status(cert.id)
            card = Card()
            top = QHBoxLayout()
            top.setSpacing(9)
            title = label(cert.name, wrap=True)
            title.setStyleSheet("font-size: 15px; font-weight: 700;")
            top.addWidget(title, 1)
            top.addWidget(pill(CERT_STATES[state].upper(), CERT_TONES[state]))
            card.box.addLayout(top)
            card.add(muted("%s  -  %s  -  %s" % (cert.by, cert.cost, cert.time)))
            card.add(label(cert.what, "Soft"))
            card.add(muted("Worth it? " + cert.worth))
            row = QHBoxLayout()
            row.setSpacing(8)
            cycle = button("Mark: " + CERT_STATES[(state + 1) % 3], "quiet")
            cycle.clicked.connect(
                lambda _=False, c=cert.id, s=state: self._cycle(c, s))
            row.addWidget(cycle)
            if cert.url:
                open_button = button("Open", "quiet")
                open_button.clicked.connect(
                    lambda _=False, u=cert.url: _open(u))
                row.addWidget(open_button)
            row.addStretch(1)
            card.box.addLayout(row)
            self.certs_tab.add(card)
        self.certs_tab.add_stretch()

    def _cycle(self, cert_id: str, state: int) -> None:
        self.ctx.store.set_cert_status(cert_id, (state + 1) % 3)
        self._fill_certs()


def _open(url: str) -> None:
    from ..widgets.common import open_url
    open_url(url)
