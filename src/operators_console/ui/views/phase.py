"""One phase in detail: what to learn, the resources, the gate, the notes."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
)

from ..widgets.common import (
    Card, CheckRow, LinkRow, button, divider, heading, label, meter, muted,
    soft,
)
from .base import View


class PhaseView(View):
    title = "Phase"

    def build(self) -> None:
        picker_row = QHBoxLayout()
        picker_row.setSpacing(9)
        self.picker = QComboBox()
        self.picker.setMinimumWidth(300)
        self.picker.currentIndexChanged.connect(self._on_pick)
        picker_row.addWidget(muted("PHASE"), 0, Qt.AlignmentFlag.AlignVCenter)
        picker_row.addWidget(self.picker, 1)
        self.prev_button = button("Previous", "quiet")
        self.next_button = button("Next", "quiet")
        self.prev_button.clicked.connect(lambda: self._step(-1))
        self.next_button.clicked.connect(lambda: self._step(1))
        picker_row.addWidget(self.prev_button)
        picker_row.addWidget(self.next_button)
        self.scroller.add_layout(picker_row)

        self.kicker = label("", "PageKicker", wrap=False)
        self.scroller.add(self.kicker)
        self.title_label = label("", "PageTitle")
        self.scroller.add(self.title_label)
        self.aim_label = label("", "PageAim")
        self.scroller.add(self.aim_label)

        self.progress_meter = meter(0)
        self.scroller.add(self.progress_meter)
        self.progress_caption = muted("")
        self.scroller.add(self.progress_caption)

        self.jump_row = QHBoxLayout()
        self.jump_row.setSpacing(8)
        self.scroller.add_layout(self.jump_row)

        self.scroller.add(divider())
        self.body = QVBoxLayout()
        self.body.setSpacing(18)
        self.scroller.add_layout(self.body)

        self.scroller.add(heading("Your notes for this phase"))
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText(
            "What clicked, what did not, and what to pick up next time.")
        self.notes.setFixedHeight(120)
        self._note_timer = QTimer(self)
        self._note_timer.setSingleShot(True)
        self._note_timer.setInterval(600)
        self._note_timer.timeout.connect(self._save_note)
        self.notes.textChanged.connect(self._queue_note_save)
        self.scroller.add(self.notes)
        self.scroller.add_stretch()

        self.current_id = ""
        # The phase whose text is currently in the notes box. A pending save
        # belongs to it, not to whatever phase is opened next.
        self._note_scope = ""
        self._loading = False

    # -- navigation --------------------------------------------------------

    def show_target(self, target: str) -> None:
        if target and self.ctx.curriculum.phase(target) is not None:
            self.current_id = target
            self.refresh()

    def _phase_ids(self) -> list:
        return [p.id for p in self.ctx.curriculum.phases]

    def _on_pick(self, index: int) -> None:
        if self._loading or index < 0:
            return
        pid = self.picker.itemData(index)
        if pid and pid != self.current_id:
            self.current_id = pid
            self.refresh()

    def _step(self, delta: int) -> None:
        ids = self._phase_ids()
        if self.current_id not in ids:
            return
        index = max(0, min(len(ids) - 1, ids.index(self.current_id) + delta))
        self.current_id = ids[index]
        self.refresh()

    # -- refresh -----------------------------------------------------------

    def refresh(self) -> None:
        if not self.current_id:
            self.current_id = self.ctx.progress.current_phase_id()
        phase = self.ctx.curriculum.phase(self.current_id)
        if phase is None:
            return
        self.flush_note()

        self._loading = True
        self.picker.clear()
        for candidate in self.ctx.curriculum.phases:
            self.picker.addItem("%s  %s" % (candidate.num, candidate.name),
                                candidate.id)
        ids = self._phase_ids()
        self.picker.setCurrentIndex(ids.index(phase.id))
        self._loading = False

        position = ids.index(phase.id)
        self.prev_button.setEnabled(position > 0)
        self.next_button.setEnabled(position < len(ids) - 1)

        self.kicker.setText("PHASE %s  -  %s" % (phase.num, phase.when))
        self.title_label.setText(phase.name)
        self.aim_label.setText(phase.aim)

        stats = self.ctx.progress.phase(phase)
        self.progress_meter.setVisible(not phase.no_progress)
        self.progress_caption.setVisible(not phase.no_progress)
        if not phase.no_progress:
            self.progress_meter.setValue(stats.percent)
            self.progress_caption.setText(
                "%d of %d checks done - about %d hours of work in this phase"
                % (stats.done, stats.total, phase.est_hours))

        self._fill_jumps(phase, stats)
        self._fill_body(phase)

        self._loading = True
        self.notes.setPlainText(self.ctx.store.note("phase:" + phase.id))
        self._note_scope = phase.id
        self._loading = False

    def _fill_jumps(self, phase, stats) -> None:
        _clear(self.jump_row)
        exercises = self.ctx.curriculum.exercises_for(phase.id)
        quizzes = self.ctx.curriculum.quizzes_for(phase.id)
        projects = self.ctx.curriculum.projects_for(phase.id)

        if exercises:
            btn = button("Exercises  %d/%d"
                         % (stats.exercises_done, len(exercises)), "quiet")
            btn.clicked.connect(
                lambda _=False, p=phase.id: self.ctx.navigate.emit("practice", p))
            self.jump_row.addWidget(btn)
        if quizzes:
            btn = button("Quiz", "quiet")
            btn.clicked.connect(
                lambda _=False, q=quizzes[0].id:
                self.ctx.navigate.emit("quiz", q))
            self.jump_row.addWidget(btn)
        if projects:
            btn = button("Projects  %d" % len(projects), "quiet")
            btn.clicked.connect(
                lambda _=False, p=projects[0].id:
                self.ctx.navigate.emit("projects", p))
            self.jump_row.addWidget(btn)
        self.jump_row.addStretch(1)

    def _fill_body(self, phase) -> None:
        _clear(self.body)

        if phase.resources:
            card = Card()
            card.add(heading("Start here"))
            for res in phase.resources:
                card.add(LinkRow(res.name, res.why, res.url, res.kind))
            self.body.addWidget(card)

        checked = self.ctx.store.checked_ids()
        for section in phase.sections:
            card = Card()
            top = QHBoxLayout()
            top.addWidget(heading(section.title), 1)
            done = sum(1 for item in section.items if item.id in checked)
            counter = muted("%d/%d" % (done, len(section.items)))
            top.addWidget(counter, 0, Qt.AlignmentFlag.AlignRight)
            card.box.addLayout(top)
            for item in section.items:
                row = CheckRow(item.id, item.text, item.id in checked)
                row.toggled.connect(self._toggle)
                row.review_requested.connect(self._add_to_review)
                card.add(row)
            self.body.addWidget(card)

        if phase.snippet:
            card = Card()
            card.add(heading("Try this in a terminal"))
            snippet = label(phase.snippet, "Code", selectable=True)
            snippet.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            card.add(snippet)
            copy = button("Copy", "quiet")
            copy.clicked.connect(lambda: self._copy(phase.snippet))
            card.add_row(None, copy)
            self.body.addWidget(card)

        if phase.gate:
            card = Card()
            card.add(heading("Gate - prove it before you move on"))
            if phase.gate.note:
                card.add(soft(phase.gate.note))
            for item in phase.gate.items:
                row = CheckRow(item.id, item.text, item.id in checked)
                row.toggled.connect(self._toggle)
                row.review_requested.connect(self._add_to_review)
                card.add(row)
            self.body.addWidget(card)

    # -- actions -----------------------------------------------------------

    def _toggle(self, item_id: str, done: bool) -> None:
        self.ctx.set_checked(item_id, done)
        phase = self.ctx.curriculum.phase(self.current_id)
        if phase is not None and not phase.no_progress:
            stats = self.ctx.progress.phase(phase)
            self.progress_meter.setValue(stats.percent)
            self.progress_caption.setText(
                "%d of %d checks done - about %d hours of work in this phase"
                % (stats.done, stats.total, phase.est_hours))
            if stats.is_complete:
                self.ctx.announce(
                    "Phase %s complete. That is real progress." % phase.num)

    def _add_to_review(self, item_id: str) -> None:
        self.ctx.review.add_concept(item_id)
        self.ctx.announce("Added to your review deck.")

    def _copy(self, text: str) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        self.ctx.announce("Copied.")

    def _queue_note_save(self) -> None:
        if self._loading or not self._note_scope:
            return
        self._note_timer.start()

    def _save_note(self) -> None:
        if not self._note_scope:
            return
        self.ctx.store.set_note("phase:" + self._note_scope,
                                self.notes.toPlainText())

    def flush_note(self) -> None:
        """Commit a pending note before the box is reused for another phase."""
        if self._note_timer.isActive():
            self._note_timer.stop()
            self._save_note()


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())
