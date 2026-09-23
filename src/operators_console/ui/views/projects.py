"""Projects: the work that actually proves a phase happened.

Every card is built once and then kept in step with the store. The page used
to tear down and rebuild all of them - requirements, stretch goals, rubric,
repo field and notes box, about 2,100 widgets - on every visit and on every
status press, so arriving here or pressing "In progress" froze the window for
half a second or more.

Projects in the learner's plan come first. The ones outside their track are
genuinely optional, so they sit folded under one line, the same way optional
reading does elsewhere, and the counter agrees with Today's.
"""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLineEdit, QPlainTextEdit, QVBoxLayout,
)

from ...core.textmatch import contains, haystack, terms
from ..widgets.common import (
    Card, CheckRow, Disclosure, button, divider, heading, label, meter,
    muted, pill, repolish,
)
from .base import View

STATUSES = (("not-started", "Not started", ""),
            ("in-progress", "In progress", "warn"),
            ("shipped", "Shipped", "done"))

# Notes are saved once the typing stops, not on every keystroke: each save is
# a committed, fsynced transaction.
NOTES_SAVE_MS = 450

EXTRA_KEY = "projects:outside-track"

#: The SHOW choices, in the order they are offered.
MODES = ("All", "Not started", "In progress", "Shipped")

#: What an empty page says for each SHOW choice, before the way back.
EMPTY_WORDS = {
    "All": "No project matches that search.",
    "Not started": "Every project has been started.",
    "In progress": "Nothing is in progress.",
    "Shipped": "Nothing is shipped yet.",
}


class _ProjectCard(Card):
    """One project, built once, updated in place by `sync`."""

    def __init__(self, view: "ProjectsView", project) -> None:
        super().__init__()
        self.view = view
        self.project = project
        ctx = view.ctx
        phase = ctx.curriculum.phase(project.phase)
        # What the FIND box searches, folded once: the card's own words.
        self.text = haystack(
            project.title, project.brief, project.why, project.kind,
            phase.num if phase else "", phase.name if phase else "",
            " ".join(project.requirements), " ".join(project.stretch))

        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(pill(phase.num if phase else "--"))
        title = label(project.title, wrap=True)
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        top.addWidget(title, 1)
        top.addWidget(pill(project.kind.upper()))
        self.status_pill = pill("")
        top.addWidget(self.status_pill)
        self.box.addLayout(top)

        self.add(label(project.brief, "Soft"))
        self.add(muted(project.why))

        self.meter = meter(0)
        self.add(self.meter)
        self.done_label = muted("")
        self.add(self.done_label)

        self.add(heading("Requirements"))
        self.rows = {}
        for req_id, text in zip(project.requirement_ids, project.requirements,
                                strict=True):
            row = CheckRow(req_id, text, False)
            row.toggled.connect(self._toggled)
            self.rows[req_id] = row
            self.add(row)

        # One label per list rather than one per bullet: the text is static.
        if project.stretch:
            self.add(heading("Stretch goals"))
            self.add(muted("\n".join("- " + t for t in project.stretch)))
        if project.rubric:
            self.add(heading("Rubric"))
            self.add(muted("\n".join("- " + t for t in project.rubric)))

        self.add(divider())
        repo_row = QHBoxLayout()
        repo_row.setSpacing(8)
        repo_row.addWidget(muted("REPO"))
        self.repo = QLineEdit()
        self.repo.setPlaceholderText("https://github.com/you/the-project")
        self.repo.editingFinished.connect(self._repo_finished)
        repo_row.addWidget(self.repo, 1)
        self.open_button = button("Open", "quiet")
        self.open_button.clicked.connect(
            lambda _=False: _open(self.repo.text()))
        repo_row.addWidget(self.open_button)
        # A button that opens nothing is a broken button. It comes alive as
        # the address is typed, not on the next visit to the page.
        self.repo.textChanged.connect(lambda _text: self._sync_open())
        self._sync_open()
        self.box.addLayout(repo_row)

        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Decisions, blockers, what you would do "
                                      "differently.")
        self.notes.setFixedHeight(72)
        self.notes.textChanged.connect(self._notes_changed)
        self._notes_timer = QTimer(self)
        self._notes_timer.setSingleShot(True)
        self._notes_timer.setInterval(NOTES_SAVE_MS)
        self._notes_timer.timeout.connect(self.flush_notes)
        self._syncing = False
        self._notes_dirty = False       # typed but not yet saved
        self.add(self.notes)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.status_buttons = {}
        for value, text, _tone in STATUSES:
            widget = button(text, "quiet")
            widget.clicked.connect(
                lambda _=False, v=value: view._set_status(project.id, v))
            self.status_buttons[value] = widget
            controls.addWidget(widget)
        controls.addStretch(1)
        go_phase = button("Go to phase %s" % (phase.num if phase else ""),
                          "quiet")
        go_phase.clicked.connect(
            lambda _=False: ctx.navigate.emit("phase", project.phase))
        controls.addWidget(go_phase)
        self.box.addLayout(controls)

    # -- keeping in step with the store ------------------------------------

    def sync(self, status: str, state: dict, checked: set) -> None:
        self._syncing = True
        try:
            self._set_pill(status)
            for req_id, row in self.rows.items():
                want = req_id in checked
                if row.box.isChecked() != want:
                    row.set_checked(want)
            self._set_meter(checked)
            for value, widget in self.status_buttons.items():
                kind = "primary" if value == status else "quiet"
                if widget.property("kind") != kind:
                    widget.setProperty("kind", kind)
                    repolish(widget)
            # Never overwrite what the learner is typing, or a save that has
            # not happened yet.
            repo = state.get("repo_url") or ""
            if not self.repo.hasFocus() and self.repo.text() != repo:
                self.repo.setText(repo)
            notes = state.get("notes") or ""
            if (not self.notes.hasFocus() and not self._notes_dirty
                    and self.notes.toPlainText() != notes):
                self.notes.setPlainText(notes)
        finally:
            self._syncing = False

    def _set_pill(self, status: str) -> None:
        text = _label_of(status).upper()
        tone = _tone_of(status)
        if self.status_pill.text() != text:
            self.status_pill.setText(text)
        if (self.status_pill.property("tone") or "") != tone:
            self.status_pill.setProperty("tone", tone)
            repolish(self.status_pill)

    def _set_meter(self, checked: set) -> None:
        ids = self.project.requirement_ids
        done = sum(1 for i in ids if i in checked)
        self.meter.setValue(round(done / len(ids) * 100) if ids else 0)
        tone = "done" if ids and done == len(ids) else ""
        if (self.meter.property("tone") or "") != tone:
            self.meter.setProperty("tone", tone)
            repolish(self.meter)
        self.done_label.setText("%d of %d requirements met" % (done, len(ids)))

    # -- the learner's edits -----------------------------------------------

    def _toggled(self, item_id: str, done: bool) -> None:
        self.view.ctx.set_checked(item_id, done)
        # The bar and the count move with the tick, not on the next visit.
        self._set_meter(self.view.ctx.store.checked_ids())

    def _sync_open(self) -> None:
        url = self.repo.text().strip()
        ready = _is_url(url)
        self.open_button.setEnabled(ready)
        self.open_button.setToolTip(
            "Open %s" % url if ready
            else "Put the repository's address in the field first.")

    def _repo_finished(self) -> None:
        self.view.ctx.store.set_project(self.project.id,
                                        repo_url=self.repo.text().strip())

    def _notes_changed(self) -> None:
        if not self._syncing:
            self._notes_dirty = True
            self._notes_timer.start()

    def flush_notes(self) -> None:
        """Save typed notes now if a save is waiting.

        Dirtiness is tracked in memory, so a flush with nothing to save never
        touches the store - it runs from hide paths that can come after the
        store has closed.
        """
        self._notes_timer.stop()
        if not self._notes_dirty:
            return
        self.view.ctx.store.set_project(self.project.id,
                                        notes=self.notes.toPlainText())
        self._notes_dirty = False


class ProjectsView(View):
    title = "Projects"

    def build(self) -> None:
        self.header("Projects", "portfolio projects",
                    "Each project proves one skill. Tick a requirement only "
                    "when it is done.")
        row = QHBoxLayout()
        row.setSpacing(8)
        self.filter = QComboBox()
        self.filter.addItems(list(MODES))
        self.filter.setAccessibleName("Show projects by status")
        self.filter.currentIndexChanged.connect(lambda _i: self._sync())
        row.addWidget(muted("SHOW"))
        row.addWidget(self.filter)
        row.addWidget(muted("FIND"))
        self.find = QLineEdit()
        self.find.setPlaceholderText("Title, brief or requirement")
        self.find.setAccessibleName("Search the projects")
        self.find.setClearButtonEnabled(True)
        self.find.setMaximumWidth(320)
        self.find.textChanged.connect(lambda _t: self._sync())
        row.addWidget(self.find, 1)
        self.counter = muted("")
        row.addWidget(self.counter, 1)
        self.scroller.add_layout(row)
        self.scroller.add(divider())
        # The empty state, built on first need and kept.
        self.empty_slot = QVBoxLayout()
        self.empty_slot.setSpacing(0)
        self.scroller.add_layout(self.empty_slot)
        self._empty = None
        self.holder = QVBoxLayout()
        self.holder.setSpacing(16)
        self.scroller.add_layout(self.holder)
        self.extra_slot = QVBoxLayout()
        self.extra_slot.setSpacing(0)
        self.scroller.add_layout(self.extra_slot)
        self.scroller.add_stretch()
        self.pending = ""
        self._cards = {}
        self._extra = None
        self._plan = None

    # -- lifecycle ---------------------------------------------------------

    def refresh(self) -> None:
        self._sync()

    def show_target(self, target: str) -> None:
        self.ensure_built()
        self.pending = target
        # A filter must not hide the target.
        self._clear_filters(sync=False)
        self._sync()

    def _clear_filters(self, sync: bool = True) -> None:
        for control in (self.filter, self.find):
            control.blockSignals(True)
        self.filter.setCurrentIndex(0)
        self.find.clear()
        for control in (self.filter, self.find):
            control.blockSignals(False)
        if sync:
            self._sync()

    def save_state(self):
        return {"mode": self.filter.currentIndex(), "find": self.find.text()}

    def restore_state(self, state) -> None:
        for control in (self.filter, self.find):
            control.blockSignals(True)
        mode = int(state.get("mode", 0))
        if 0 <= mode < self.filter.count():
            self.filter.setCurrentIndex(mode)
        self.find.setText(state.get("find", ""))
        for control in (self.filter, self.find):
            control.blockSignals(False)
        self._sync()

    def hideEvent(self, event) -> None:
        self.flush_notes()
        super().hideEvent(event)

    def teardown(self) -> None:
        if not self._built:
            return
        self.flush_notes()
        super().teardown()
        self._cards = {}
        self._extra = None
        self._empty = None
        self._plan = None

    def flush_notes(self) -> None:
        # Qt hides the page when the stack first adopts it, before build().
        for card in getattr(self, "_cards", {}).values():
            card.flush_notes()

    def card_for(self, project_id: str):
        """The card showing one project, or None before the page is built."""
        return getattr(self, "_cards", {}).get(project_id)

    # -- building and arranging --------------------------------------------

    def _plan_ids(self) -> tuple:
        progress = self.ctx.progress
        return tuple(p.id for p in self.ctx.curriculum.projects
                     if progress.is_in_plan(p.phase))

    def _arrange(self, plan: tuple) -> None:
        """Place the cards: the plan first, the rest folded. Runs when the
        plan changes (first visit, or a new track), never on a plain visit."""
        for project in self.ctx.curriculum.projects:
            if project.id not in self._cards:
                self._cards[project.id] = _ProjectCard(self, project)
        for card in self._cards.values():
            self.holder.removeWidget(card)
        if self._extra is not None:
            for card in self._cards.values():
                self._extra.stack.removeWidget(card)
            self.extra_slot.removeWidget(self._extra)
            self._extra.setParent(None)
            self._extra.deleteLater()
            self._extra = None

        in_plan = set(plan)
        outside = []
        for project in self.ctx.curriculum.projects:
            card = self._cards[project.id]
            if project.id in in_plan:
                self.holder.addWidget(card)
            else:
                outside.append(card)
        if outside:
            self._extra = Disclosure(len(outside), "outside your track",
                                     store=self.ctx.store, key=EXTRA_KEY,
                                     tag="")
            for card in outside:
                self._extra.add(card)
            self.extra_slot.addWidget(self._extra)
        self._plan = plan

    def _sync(self) -> None:
        plan = self._plan_ids()
        if plan != self._plan:
            self._arrange(plan)

        checked = self.ctx.store.checked_ids()
        states = self.ctx.store.project_states()
        mode = self.filter.currentText()
        wanted = terms(self.find.text())
        shown = 0
        visible_ids = set()
        for project in self.ctx.curriculum.projects:
            card = self._cards[project.id]
            state = states.get(project.id, {})
            status = state.get("status") or "not-started"
            card.sync(status, state, checked)
            visible = ((mode == "All" or _label_of(status) == mode)
                       and contains(card.text, wanted))
            card.setVisible(visible)
            shown += visible
            if visible:
                visible_ids.add(project.id)
        self._sync_extra(plan, visible_ids)
        self._sync_empty(shown, mode, bool(wanted))

        in_plan = set(plan)
        planned = [p for p in self.ctx.curriculum.projects if p.id in in_plan]
        shipped = sum(1 for p in planned
                      if states.get(p.id, {}).get("status") == "shipped")
        extra = len(self.ctx.curriculum.projects) - len(planned)
        words = "%d shown  -  %d of %d in your plan shipped" % (
            shown, shipped, len(planned))
        if extra:
            words += "  -  %d more outside your track" % extra
        self.counter.setText(words)

        if self.pending:
            target, self.pending = self.pending, ""
            self._reveal(target)

    def _sync_extra(self, plan: tuple, visible_ids: set) -> None:
        """Keep the "outside your track" fold honest about what it holds.

        With a filter on, it used to keep promising every project outside
        the track and open onto an empty box. It now counts the ones the
        filter kept, and goes away when that is none.
        """
        if self._extra is None:
            return
        in_plan = set(plan)
        left = sum(1 for p in self.ctx.curriculum.projects
                   if p.id not in in_plan and p.id in visible_ids)
        self._extra.set_count(left)
        self._extra.setVisible(left > 0)

    def _sync_empty(self, shown: int, mode: str, searching: bool) -> None:
        """Say so when the filters leave nothing, and offer the way back."""
        if shown:
            if self._empty is not None:
                self._empty.setVisible(False)
            return
        if self._empty is None:
            self._empty = Card()
            self.empty_title = label("", "RowTitle")
            self._empty.add(self.empty_title)
            self.empty_text = muted("")
            self._empty.add(self.empty_text)
            self.show_all = button("Show every project", "quiet")
            self.show_all.clicked.connect(
                lambda _=False: self._clear_filters())
            row = QHBoxLayout()
            row.addWidget(self.show_all)
            row.addStretch(1)
            self._empty.box.addLayout(row)
            self.empty_slot.addWidget(self._empty)
        total = len(self.ctx.curriculum.projects)
        query = " ".join(self.find.text().split())
        if searching and mode != "All":
            title = 'No %s project matches "%s".' % (mode.lower(), query)
            back = ("Clear the FIND box, or switch SHOW back to All, to see "
                    "all %d." % total)
        elif searching:
            title = 'No project matches "%s".' % query
            back = "Clear the FIND box to see all %d." % total
        else:
            title = EMPTY_WORDS.get(mode, "Nothing matches that filter.")
            back = "Switch SHOW back to All to see all %d." % total
        self.empty_title.setText(title)
        self.empty_text.setText(back)
        self._empty.setVisible(True)

    def _reveal(self, project_id: str) -> None:
        card = self._cards.get(project_id)
        if card is None:
            return
        if (self._extra is not None and self._extra.isAncestorOf(card)
                and not self._extra.is_open):
            self._extra.set_open(True, animate=False)
        # After the layout has placed it, not before. The card's TOP goes to
        # the top of the page: ensureWidgetVisible bottom-aligns a card taller
        # than the viewport, which cut its title off.
        QTimer.singleShot(0, lambda: self._scroll_to_top_of(card))

    def _scroll_to_top_of(self, card) -> None:
        content = self.scroller.widget()
        if content is None or not content.isAncestorOf(card):
            return
        y = card.mapTo(content, card.rect().topLeft()).y()
        bar = self.scroller.verticalScrollBar()
        bar.setValue(max(bar.minimum(), min(bar.maximum(), y - 16)))

    # -- actions -----------------------------------------------------------

    def _set_status(self, project_id: str, status: str) -> None:
        self.ctx.set_project_status(project_id, status)
        if status == "shipped":
            self.ctx.announce("Marked shipped.")
        self._sync()

    def _set_repo(self, project_id: str, url: str) -> None:
        self.ctx.store.set_project(project_id, repo_url=url.strip())

    def _set_notes(self, project_id: str, text: str) -> None:
        self.ctx.store.set_project(project_id, notes=text)


def _label_of(status: str) -> str:
    for value, text, _tone in STATUSES:
        if value == status:
            return text
    return "Not started"


def _tone_of(status: str) -> str:
    for value, _text, tone in STATUSES:
        if value == status:
            return tone
    return ""


def _is_url(text: str) -> bool:
    """Whether the repo field holds something a browser could open.

    A note to self is not a link, and the Open button beside it should say
    so by being unpressable rather than by doing nothing.
    """
    text = (text or "").strip()
    if not text.lower().startswith(("http://", "https://")):
        return False
    return len(text.split("://", 1)[-1].strip("/")) > 2


def _open(url: str) -> None:
    from ..widgets.common import open_url
    open_url(url.strip())
