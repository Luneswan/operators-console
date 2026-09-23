"""The library: books, courses, channels, fields of work and certificates."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLineEdit, QTabWidget, QWidget,
)

from ...core.models import split_optional
from ...core.textmatch import contains, haystack, terms
from ...core.textmatch import slug as _slug
from ..widgets.common import (
    Card, Column, Disclosure, LinkRow, button, heading, label,
    muted, pill, repolish,
)
from .base import View

CERT_STATES = ("Not started", "In progress", "Earned")
CERT_TONES = ("", "warn", "done")

#: Tabs, in the order they are added. Used for the read marks' ids.
SHELF, FIELDS, VIDEO, CERTS = 0, 1, 2, 3
TAB_KEYS = {SHELF: "shelf", FIELDS: "fields", VIDEO: "video",
            CERTS: "certs"}
#: The tabs' own names; a live filter adds its count to each.
TAB_NAMES = {SHELF: "Shelf", FIELDS: "Fields of work", VIDEO: "Video",
             CERTS: "Certificates"}

#: How long a card found by search wears the accent before settling back.
FLASH_MS = 1800


def read_id(tab: int, slug: str) -> str:
    """The stable id a read mark is stored under: ``lib:<tab>:<slug>``.

    The store's checkbox table takes any string id, so a read mark is one
    more tick beside the curriculum's own - undoable, exported and restored
    with everything else, with no new table and no new setting.
    """
    return "lib:%s:%s" % (TAB_KEYS.get(tab, str(tab)), slug)


def slug(text: str) -> str:
    """A name reduced to something stable enough to store it under.

    The one in core.textmatch, so the search index names a shelf or video
    card with exactly the id this page files it under.
    """
    return _slug(text)


@dataclass
class _Row:
    """One filterable line, and everything the filter has to move with it."""
    tab: int
    widget: QWidget
    text: str
    card: QWidget | None = None
    fold: Disclosure | None = None
    heading: QWidget | None = None


class FittedTabs(QTabWidget):
    """Tabs as tall as the tab on show.

    QTabWidget sizes itself to its tallest page whatever the pages' size
    policies say, so in a scrolling page every tab left the scroll range of
    the longest one - a Certificates tab with empty screens under it.
    """

    def _fit(self, hint, base):
        page = self.currentWidget()
        if page is None:
            return base
        extra = self.tabBar().sizeHint().height() + 4
        return QSize(base.width(), hint(page).height() + extra)

    def sizeHint(self) -> QSize:
        return self._fit(lambda page: page.sizeHint(), super().sizeHint())

    def minimumSizeHint(self) -> QSize:
        return self._fit(lambda page: page.minimumSizeHint(),
                         super().minimumSizeHint())


class LibraryView(View):
    title = "Library"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(ctx, parent)
        self._static_built = False
        self._rows: list = []
        self._reads: list = []
        self._targets: dict = {}
        self._target = ""
        self._flashed = None
        # The folds the filter opened, so clearing it closes those and only
        # those - never one the learner opened by hand.
        self._forced: dict = {}
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._unflash)

    def build(self) -> None:
        self._rows = []
        self._reads = []
        self._targets = {}
        self._flashed = None
        self._forced = {}
        self.scroller.column.setContentsMargins(24, 24, 24, 20)
        self.header("Library", "everything worth reading",
                    "Curated rather than exhaustive. If something is not here, "
                    "it did not earn a place.")

        # One field over all four tabs: a shelf of eighty entries is a list
        # to search, not a list to read top to bottom.
        strip = QHBoxLayout()
        strip.setSpacing(10)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter the library")
        self.filter.setAccessibleName("Filter the library")
        self.filter.setClearButtonEnabled(True)
        self.filter.setMaximumWidth(360)
        self.filter.textChanged.connect(lambda _text: self._apply_filter())
        strip.addWidget(self.filter, 1)
        self.filter_note = muted("")
        strip.addWidget(self.filter_note)
        strip.addStretch(1)
        self.scroller.add_layout(strip)

        self.tabs = FittedTabs()
        self.scroller.add(self.tabs, 1)

        # Columns, not scroll areas: the page scrolls, header and all.
        self.shelf_tab = Column(margins=(4, 12, 4, 20))
        self.fields_tab = Column(margins=(4, 12, 4, 20))
        self.channels_tab = Column(margins=(4, 12, 4, 20))
        self.certs_tab = Column(margins=(4, 12, 4, 20))
        self.tabs.addTab(self.shelf_tab, TAB_NAMES[SHELF])
        self.tabs.addTab(self.fields_tab, TAB_NAMES[FIELDS])
        self.tabs.addTab(self.channels_tab, TAB_NAMES[VIDEO])
        self.tabs.addTab(self.certs_tab, TAB_NAMES[CERTS])
        self.tabs.currentChanged.connect(self._fit_tabs)
        self.tabs.currentChanged.connect(lambda _i: self._count_matches())
        self._fit_tabs(self.tabs.currentIndex())

    def _fit_tabs(self, _index: int) -> None:
        self.tabs.updateGeometry()

    def teardown(self) -> None:
        self._flash_timer.stop()
        self._flashed = None
        self._rows = []
        self._reads = []
        self._targets = {}
        self._forced = {}
        super().teardown()
        self._static_built = False

    # -- surviving a theme or text-size change -----------------------------

    def save_state(self):
        return {"filter": self.filter.text(),
                "tab": self.tabs.currentIndex()}

    def restore_state(self, state) -> None:
        tab = int(state.get("tab", 0))
        if 0 <= tab < self.tabs.count():
            self.tabs.setCurrentIndex(tab)
        self.filter.setText(state.get("filter", ""))

    # -- finding one card again -------------------------------------------

    def show_target(self, target: str) -> None:
        """Open the tab a card is on, and point at it.

        A field, a certificate, or one line of the shelf or the video list
        (those are filed under their read-mark id, "lib:shelf:<slug>"). A
        line folded away under "more" has its fold opened first.
        """
        self.ensure_built()
        self.refresh()
        entry = self._targets.get(target)
        if entry is None:
            return
        self._target = target
        tab, card, fold, spot = entry
        if self.filter.text():
            self.filter.clear()         # a filter must not hide the target
        if fold is not None and not fold.is_open:
            fold.set_open(True, animate=False)
        self.tabs.setCurrentIndex(tab)
        self._fit_tabs(tab)
        self._flash(card)
        # After the layout has caught up with the tab that just changed.
        QTimer.singleShot(0, lambda: self._scroll_to(spot))

    def resume_target(self) -> str:
        return self._target

    def _scroll_to(self, card) -> None:
        try:
            self.scroller.ensureWidgetVisible(card, 0, 60)
        except RuntimeError:
            pass            # the page was rebuilt before the layout settled

    def _flash(self, card) -> None:
        """Wear the accent for a moment, so the eye lands on the right card."""
        self._unflash()
        try:
            card.setObjectName("FocusCard")
            repolish(card)
        except RuntimeError:
            return
        self._flashed = card
        self._flash_timer.start(FLASH_MS)

    def _unflash(self) -> None:
        card, self._flashed = self._flashed, None
        if card is None:
            return
        try:
            card.setObjectName("Card")
            repolish(card)
        except RuntimeError:
            pass            # the card went with the page

    # -- the filter --------------------------------------------------------

    def _apply_filter(self) -> None:
        """Hide every row that does not match, and every card left empty."""
        if not self._built:
            return
        words = terms(self.filter.text())
        cards: dict = {}
        headings: dict = {}
        holding: set = set()        # folds that hold a match
        for row in self._rows:
            match = contains(row.text, words)
            row.widget.setVisible(match)
            if match and words and row.fold is not None:
                holding.add(id(row.fold))
                if not row.fold.is_open:
                    # A match nobody can see is not a match: open the fold
                    # it is hiding in, and remember that this filter did.
                    row.fold.set_open(True, animate=False)
                    self._forced[id(row.fold)] = row.fold
            if row.card is not None:
                live, card = cards.get(id(row.card), (False, row.card))
                cards[id(row.card)] = (live or match, card)
            if row.heading is not None:
                live, head = headings.get(id(row.heading),
                                          (False, row.heading))
                headings[id(row.heading)] = (live or match, head)
        for live, card in cards.values():
            card.setVisible(live)
        for live, head in headings.values():
            head.setVisible(live)
        self._close_forced(holding)
        self._count_matches()
        self._fit_tabs(self.tabs.currentIndex())

    def _close_forced(self, holding: set) -> None:
        """Close the folds this filter opened that no longer hold a match.

        With the box cleared that is all of them, so the page goes back to
        the shape it had before anything was typed.
        """
        for key, fold in list(self._forced.items()):
            if key in holding:
                continue
            del self._forced[key]
            try:
                if fold.is_open:
                    fold.set_open(False, animate=False)
            except RuntimeError:
                pass            # the fold went with a rebuild

    def _note_row(self, tab: int, widget: QWidget, parts, card=None,
                  fold=None, head=None) -> QWidget:
        """Register one row with the filter, under the words it can match."""
        text = haystack(*(str(part or "") for part in parts))
        self._rows.append(_Row(tab, widget, text, card, fold, head))
        return widget

    def tab_matches(self) -> dict:
        """How many rows on each tab the filter keeps, keyed by tab."""
        words = terms(self.filter.text())
        counts = {tab: 0 for tab in TAB_NAMES}
        for row in self._rows:
            if contains(row.text, words):
                counts[row.tab] = counts.get(row.tab, 0) + 1
        return counts

    def _count_matches(self) -> None:
        """Say how much of this tab the filter keeps, and where the rest are.

        Only the tab on show used to be counted, so a word that matched on
        another tab read as "no results". The tabs carry their own counts
        while a filter is on, and the note names the ones with matches.
        """
        if not self._built:
            return
        words = terms(self.filter.text())
        if not words:
            self.filter_note.setText("")
            for tab, name in TAB_NAMES.items():
                if self.tabs.tabText(tab) != name:
                    self.tabs.setTabText(tab, name)
            return
        counts = self.tab_matches()
        for tab, name in TAB_NAMES.items():
            self.tabs.setTabText(tab, "%s (%d)" % (name, counts.get(tab, 0)))
        here = self.tabs.currentIndex()
        rows = sum(1 for row in self._rows if row.tab == here)
        text = "%d of %d here" % (counts.get(here, 0), rows)
        elsewhere = ["%d on %s" % (counts[tab], TAB_NAMES[tab])
                     for tab in TAB_NAMES if tab != here and counts.get(tab)]
        if elsewhere:
            elsewhere[0] = elsewhere[0].replace(" on ", " more on ", 1)
            text += " - " + ", ".join(elsewhere)
        elif not counts.get(here):
            text += " - none on the other tabs either"
        self.filter_note.setText(text)

    # -- read marks --------------------------------------------------------

    def _read_box(self, tab: int, name: str) -> QCheckBox:
        """The small tick that says you have read this one."""
        item_id = read_id(tab, slug(name))
        box = QCheckBox("Read")
        box.setChecked(self.ctx.store.is_checked(item_id))
        box.setToolTip("Mark %s as read" % name)
        box.setAccessibleName("%s, read" % name)
        box.setCursor(Qt.CursorShape.PointingHandCursor)
        box.toggled.connect(
            lambda state, i=item_id: self.ctx.set_checked(i, bool(state)))
        self._reads.append((box, item_id))
        return box

    def _read_row(self, tab: int, row: QWidget, name: str) -> QWidget:
        """Put the read mark on the end of a row, and hand the row back.

        Into the row's own layout rather than into a wrapper around it: the
        library is already the heaviest page in the app, and a hundred spare
        container widgets are a hundred more to build, polish and delete on
        every theme change.
        """
        line = row.layout()
        if line is not None:
            line.addWidget(self._read_box(tab, name), 0,
                           Qt.AlignmentFlag.AlignTop)
        return row

    def _sync_reads(self) -> None:
        """Put every tick where the store says it is - undo included."""
        done = self.ctx.store.checked_ids()
        for box, item_id in self._reads:
            try:
                wanted = item_id in done
                if box.isChecked() == wanted:
                    continue
                blocked = box.blockSignals(True)
                box.setChecked(wanted)
                box.blockSignals(blocked)
            except RuntimeError:
                continue        # the row went with a rebuild

    def refresh(self) -> None:
        # The shelf, the fields and the channels are fixed content: building
        # them once instead of on every visit removes several hundred widget
        # teardowns and rebuilds from every trip to this page. The
        # certificates depend on the store and are redrawn when it changed.
        if self.store_unchanged():
            return
        if not self._static_built:
            self._fill_shelf()
            self._fill_fields()
            self._fill_channels()
            self._static_built = True
        self._fill_certs()
        self._sync_reads()
        self._apply_filter()
        self.mark_drawn()

    def _fill_shelf(self) -> None:
        with self.shelf_tab.rebuilding():
            for group in self.ctx.curriculum.shelf:
                card = Card()
                card.add(heading(group.group))
                shown, folded = split_optional(group.items, group.optional)
                for link in shown:
                    row = LinkRow(link.name, "", link.url,
                                  primary=link.primary)
                    holder = card.add(self._read_row(SHELF, row, link.name))
                    self._note_row(SHELF, holder,
                                   (link.name, group.group, link.url), card)
                    self._targets[read_id(SHELF, slug(link.name))] = (
                        SHELF, card, None, holder)
                if folded:
                    more = Disclosure(len(folded), "on this shelf",
                                      store=self.ctx.store,
                                      key="shelf:" + group.group)
                    for link in folded:
                        row = LinkRow(link.name, "", link.url)
                        holder = more.add(
                            self._read_row(SHELF, row, link.name))
                        self._note_row(SHELF, holder,
                                       (link.name, group.group, link.url),
                                       card, fold=more)
                        self._targets[read_id(SHELF, slug(link.name))] = (
                            SHELF, card, more, holder)
                    card.add(more)
                self.shelf_tab.add(card)
            self.shelf_tab.add_stretch()

    def _fill_fields(self) -> None:
        with self.fields_tab.rebuilding():
            self.fields_tab.add(muted(
                "Pick one or two. Breadth without depth reads as inexperience."))
            current_group = None
            group_heading = None
            for field in self.ctx.curriculum.fields:
                if field.group != current_group:
                    current_group = field.group
                    group_heading = self.fields_tab.add(
                        heading(current_group))
                card = Card()
                title = label(field.name, wrap=False)
                title.setStyleSheet("font-size: 15px; font-weight: 700;")
                card.add(title)
                card.add(label(field.blurb, "Soft"))
                card.add(muted("Build to prove it: " + field.build))
                shown, folded = split_optional(field.libs, field.libs_optional)
                row = QHBoxLayout()
                row.setSpacing(8)
                for link in shown:
                    widget = button(link.name,
                                    "primary" if link.primary else "quiet",
                                    link.url)
                    widget.clicked.connect(lambda _=False, u=link.url: _open(u))
                    row.addWidget(widget)
                row.addStretch(1)
                card.box.addLayout(row)
                if folded:
                    more = Disclosure(len(folded), "librar%s"
                                      % ("y" if len(folded) == 1 else "ies"),
                                      store=self.ctx.store,
                                      key="field:" + field.id)
                    shelf = QWidget()
                    strip = QHBoxLayout(shelf)
                    strip.setContentsMargins(0, 0, 0, 0)
                    strip.setSpacing(8)
                    for link in folded:
                        widget = button(link.name, "quiet", link.url)
                        widget.clicked.connect(
                            lambda _=False, u=link.url: _open(u))
                        strip.addWidget(widget)
                    strip.addStretch(1)
                    more.add(shelf)
                    card.add(more)
                row.addWidget(self._read_box(FIELDS, field.name), 0,
                              Qt.AlignmentFlag.AlignVCenter)
                self.fields_tab.add(card)
                self._note_row(FIELDS, card,
                               (field.name, field.group, field.blurb,
                                field.build,
                                " ".join(link.name for link in field.libs)),
                               head=group_heading)
                self._targets[field.id] = (FIELDS, card, None, card)
            self.fields_tab.add_stretch()

    def _fill_channels(self) -> None:
        with self.channels_tab.rebuilding():
            self.channels_tab.add(muted(
                "Watching is not learning. Use these to unblock a concept, then "
                "close the tab and write code."))
            for group in self.ctx.curriculum.channels:
                card = Card()
                card.add(heading(group.group))
                shown, folded = split_optional(group.items, group.optional)
                for item in shown:
                    row = LinkRow(item.name, item.why, item.url,
                                  primary=item.primary)
                    holder = card.add(self._read_row(VIDEO, row, item.name))
                    self._note_row(VIDEO, holder,
                                   (item.name, item.why, group.group), card)
                    self._targets[read_id(VIDEO, slug(item.name))] = (
                        VIDEO, card, None, holder)
                if folded:
                    more = Disclosure(len(folded), "channel%s"
                                      % ("" if len(folded) == 1 else "s"),
                                      store=self.ctx.store,
                                      key="channels:" + group.group)
                    for item in folded:
                        row = LinkRow(item.name, item.why, item.url)
                        holder = more.add(
                            self._read_row(VIDEO, row, item.name))
                        self._note_row(VIDEO, holder,
                                       (item.name, item.why, group.group),
                                       card, fold=more)
                        self._targets[read_id(VIDEO, slug(item.name))] = (
                            VIDEO, card, more, holder)
                    card.add(more)
                self.channels_tab.add(card)
            self.channels_tab.add_stretch()

    def _fill_certs(self) -> None:
        # The cards are rebuilt, so their rows have to leave the filter's
        # list with them or it would hold pointers to dead widgets.
        self._rows = [row for row in self._rows if row.tab != CERTS]
        self._targets = {key: value for key, value in self._targets.items()
                         if value[0] != CERTS}
        with self.certs_tab.rebuilding():
            self.certs_tab.add(muted(
                "A certificate is a receipt for time spent. A shipped project is "
                "evidence of ability. Prefer the second."))
            for cert in self.ctx.curriculum.certs:
                state = self.ctx.store.cert_status(cert.id)
                card = Card()
                top = QHBoxLayout()
                top.setSpacing(8)
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
                self._note_row(CERTS, card,
                               (cert.name, cert.by, cert.what, cert.worth))
                self._targets[cert.id] = (CERTS, card, None, card)
            self.certs_tab.add_stretch()

    def _cycle(self, cert_id: str, state: int) -> None:
        self.ctx.set_cert_status(cert_id, (state + 1) % 3)
        self._fill_certs()
        self._apply_filter()


def _open(url: str) -> None:
    from ..widgets.common import open_url
    open_url(url)
