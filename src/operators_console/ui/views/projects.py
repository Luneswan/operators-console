"""Projects: the work that actually proves a phase happened."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLineEdit, QPlainTextEdit, QVBoxLayout,
)

from ..widgets.common import (
    Card, CheckRow, button, divider, heading, label, meter, muted, pill,
)
from .base import View

STATUSES = (("not-started", "Not started", ""),
            ("in-progress", "In progress", "warn"),
            ("shipped", "Shipped", "done"))


class ProjectsView(View):
    title = "Projects"

    def build(self) -> None:
        self.header("Projects", "build something real",
                    "Each one is scoped so that finishing it proves a specific "
                    "claim. Tick a requirement only when it is actually true.")
        row = QHBoxLayout()
        row.setSpacing(9)
        self.filter = QComboBox()
        self.filter.addItems(["All", "Not started", "In progress", "Shipped"])
        self.filter.currentIndexChanged.connect(lambda _i: self._fill())
        row.addWidget(muted("SHOW"))
        row.addWidget(self.filter)
        self.counter = muted("")
        row.addWidget(self.counter, 1)
        self.scroller.add_layout(row)
        self.scroller.add(divider())
        self.holder = QVBoxLayout()
        self.holder.setSpacing(14)
        self.scroller.add_layout(self.holder)
        self.scroller.add_stretch()
        self.pending = ""

    def refresh(self) -> None:
        self._fill()
        if self.pending:
            self.pending = ""

    def show_target(self, target: str) -> None:
        self.ensure_built()
        self.pending = target
        self._fill()

    def _fill(self) -> None:
        _empty(self.holder)
        mode = self.filter.currentText()
        statuses = self.ctx.store.project_statuses()
        shown = 0
        for project in self.ctx.curriculum.projects:
            status = statuses.get(project.id, "not-started")
            if mode != "All" and _label_of(status) != mode:
                continue
            self.holder.addWidget(self._card(project, status))
            shown += 1
        total = len(self.ctx.curriculum.projects)
        shipped = sum(1 for s in statuses.values() if s == "shipped")
        self.counter.setText("%d shown  -  %d of %d shipped"
                             % (shown, shipped, total))

    def _card(self, project, status: str) -> Card:
        card = Card()
        phase = self.ctx.curriculum.phase(project.phase)
        checked = self.ctx.store.checked_ids()
        state = self.ctx.store.project(project.id)

        top = QHBoxLayout()
        top.setSpacing(9)
        top.addWidget(pill(phase.num if phase else "--"))
        title = label(project.title, wrap=True)
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        top.addWidget(title, 1)
        top.addWidget(pill(project.kind.upper()))
        top.addWidget(pill(_label_of(status).upper(), _tone_of(status)))
        card.box.addLayout(top)

        card.add(label(project.brief, "Soft"))
        card.add(muted(project.why))

        ids = project.requirement_ids
        done = sum(1 for i in ids if i in checked)
        card.add(meter(round(done / len(ids) * 100) if ids else 0,
                       tone="done" if ids and done == len(ids) else ""))
        card.add(muted("%d of %d requirements met" % (done, len(ids))))

        card.add(heading("Requirements"))
        for req_id, text in zip(ids, project.requirements, strict=True):
            row = CheckRow(req_id, text, req_id in checked)
            row.toggled.connect(self._toggle)
            card.add(row)

        if project.stretch:
            card.add(heading("If you want more"))
            for text in project.stretch:
                card.add(muted("- " + text))

        if project.rubric:
            card.add(heading("What finished means"))
            for text in project.rubric:
                card.add(muted("- " + text))

        card.add(divider())
        repo_row = QHBoxLayout()
        repo_row.setSpacing(8)
        repo_row.addWidget(muted("REPO"))
        repo = QLineEdit(state["repo_url"])
        repo.setPlaceholderText("https://github.com/you/the-project")
        repo.editingFinished.connect(
            lambda p=project.id, w=repo: self._set_repo(p, w.text()))
        repo_row.addWidget(repo, 1)
        open_button = button("Open", "quiet")
        open_button.clicked.connect(
            lambda _=False, w=repo: _open(w.text()))
        repo_row.addWidget(open_button)
        card.box.addLayout(repo_row)

        notes = QPlainTextEdit(state["notes"])
        notes.setPlaceholderText("Decisions, blockers, what you would do "
                                 "differently.")
        notes.setFixedHeight(72)
        notes.textChanged.connect(
            lambda p=project.id, w=notes: self._set_notes(p, w.toPlainText()))
        card.add(notes)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        for value, text, _tone in STATUSES:
            widget = button(text, "primary" if value == status else "quiet")
            widget.clicked.connect(
                lambda _=False, p=project.id, v=value: self._set_status(p, v))
            controls.addWidget(widget)
        controls.addStretch(1)
        go_phase = button("Go to phase %s" % (phase.num if phase else ""),
                          "quiet")
        go_phase.clicked.connect(
            lambda _=False, pid=project.phase:
            self.ctx.navigate.emit("phase", pid))
        controls.addWidget(go_phase)
        card.box.addLayout(controls)
        return card

    # -- actions -----------------------------------------------------------

    def _toggle(self, item_id: str, done: bool) -> None:
        self.ctx.set_checked(item_id, done)

    def _set_status(self, project_id: str, status: str) -> None:
        self.ctx.set_project_status(project_id, status)
        if status == "shipped":
            self.ctx.announce("Shipped. Put it on your CV.")
        self._fill()

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


def _open(url: str) -> None:
    from ..widgets.common import open_url
    open_url(url.strip())


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
