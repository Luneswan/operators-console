"""One phase in detail: what to learn, the resources, the gate, the notes."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
)

from ...core.models import split_optional
from ...core.progress import proof_line
from ..widgets.common import (
    Card, CheckRow, Disclosure, LinkRow, button, clear_layout, divider,
    empty_state, frozen, heading, label,
    meter, muted, plain, soft,
)
from .base import View

#: The notes box starts here and follows what is written in it. Past the
#: ceiling the phase's own content would be pushed off the page instead.
NOTE_MIN_HEIGHT = 120
NOTE_MAX_HEIGHT = 360


class PhaseView(View):
    title = "Phase"

    def build(self) -> None:
        picker_row = QHBoxLayout()
        picker_row.setSpacing(8)
        self.picker = QComboBox()
        self.picker.setMinimumWidth(300)
        self.picker.setMaximumWidth(480)
        # Sized to its longest phase name, so a larger text size does not
        # elide "11  Async, concurrency & performance" inside 300 px.
        self.picker.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.picker.currentIndexChanged.connect(self._on_pick)
        picker_row.addWidget(muted("PHASE"), 0, Qt.AlignmentFlag.AlignVCenter)
        picker_row.addWidget(self.picker, 1)
        picker_row.addStretch(1)
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
        # Reading is the meter; proof is what finishes the phase. Both are
        # said, so a full bar never passes for a finished phase.
        self.proof_caption = label("", "Soft")
        self.scroller.add(self.proof_caption)

        self.jump_row = QHBoxLayout()
        self.jump_row.setSpacing(8)
        self.scroller.add_layout(self.jump_row)

        self.scroller.add(divider())
        self.body = QVBoxLayout()
        self.body.setSpacing(16)
        self.scroller.add_layout(self.body)

        self.scroller.add(heading("Your notes for this phase"))
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText(
            "What clicked, what did not, and what to pick up next time.")
        self.notes.setFixedHeight(NOTE_MIN_HEIGHT)
        self._note_timer = QTimer(self)
        self._note_timer.setSingleShot(True)
        self._note_timer.setInterval(600)
        self._note_timer.timeout.connect(self._save_note)
        self.notes.textChanged.connect(self._queue_note_save)
        self.notes.textChanged.connect(self._grow_notes)
        self.scroller.add(self.notes)
        self.scroller.add_stretch()

        self.current_id = self.build_state()
        # The phase whose text is currently in the notes box. A pending save
        # belongs to it, not to whatever phase is opened next.
        self._note_scope = ""
        self._loading = False

    # -- navigation --------------------------------------------------------

    def show_target(self, target: str) -> None:
        """Open a phase, or the phase of one line and scroll to that line.

        A line id arrives from "Where this is taught" on a missed review
        card: the page opens at the line the question tests, with the focus
        on its checkbox and the line read out on the status bar.
        """
        if not target:
            return
        if self.ctx.curriculum.phase(target) is not None:
            self.target_item = ""
            self.current_id = target
            self.refresh()
            return
        text = self.ctx.curriculum.item_text(target)
        phase_id = target.split(".")[0]
        if text == target or self.ctx.curriculum.phase(phase_id) is None:
            return
        self.current_id = phase_id
        self.target_item = target
        self.refresh()
        row = self.row_for(target)
        if row is None:
            return
        row.setFocus(Qt.FocusReason.OtherFocusReason)
        QTimer.singleShot(0, lambda r=row: self._reveal_row(r))
        self.ctx.announce("Taught here: %s" % plain(text))

    target_item = ""

    def row_for(self, item_id: str):
        """The check row drawn for ``item_id`` on the current page, if any."""
        for row in self.scroller.body.findChildren(CheckRow):
            if row.item_id == item_id:
                return row
        return None

    def _reveal_row(self, row) -> None:
        try:
            self.scroller.ensureWidgetVisible(row, 0, 120)
        except RuntimeError:
            pass            # the page was rebuilt before the scroll ran

    def resume_target(self) -> str:
        return self.current_id or ""

    def teardown(self) -> None:
        if not self._built:
            return
        self.flush_note()
        kept = self.current_id
        super().teardown()
        self._kept_phase = kept         # build() starts from it again

    def build_state(self) -> str:
        return getattr(self, "_kept_phase", "")

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
        # Every visit used to rebuild the whole page - the picker, the jump
        # row and every check row - even with nothing changed.
        if self.store_unchanged(phase.id):
            return
        self.flush_note()

        self._loading = True
        self.picker.clear()
        for candidate in self.ctx.curriculum.phases:
            self.picker.addItem("%s  %s" % (candidate.num, candidate.name),
                                candidate.id)
        ids = self._phase_ids()
        # Wide enough for its longest name at the current text size; the
        # adjust-to-contents policy alone did not grow it inside a layout.
        metrics = self.picker.fontMetrics()
        widest = max((metrics.horizontalAdvance(self.picker.itemText(i))
                      for i in range(self.picker.count())), default=0)
        self.picker.setMinimumWidth(min(480, max(300, widest + 64)))
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
        self.proof_caption.setVisible(not phase.no_progress
                                      and stats.total > 0)
        if not phase.no_progress:
            self._show_progress(phase, stats)

        with frozen(self.scroller.body):
            self._fill_jumps(phase, stats)
            self._fill_body(phase)
        self.mark_drawn(phase.id)

        self._loading = True
        self.notes.setPlainText(self.ctx.store.note("phase:" + phase.id))
        self._note_scope = phase.id
        self._loading = False

    def _show_progress(self, phase, stats) -> None:
        self.progress_meter.setValue(stats.percent)
        self.progress_caption.setText(
            "%d of %d checks done - about %d hours of work in this phase"
            % (stats.done, stats.total, phase.est_hours))
        self.proof_caption.setText(proof_line(stats))

    def _fill_jumps(self, phase, stats) -> None:
        clear_layout(self.jump_row)
        exercises = self.ctx.curriculum.exercises_for(phase.id)
        quizzes = self.ctx.curriculum.quizzes_for(phase.id)
        projects = self.ctx.curriculum.projects_for(phase.id)

        if exercises:
            btn = button("Exercises  %d/%d"
                         % (stats.exercises_done, len(exercises)))
            btn.clicked.connect(
                lambda _=False, p=phase.id: self.ctx.navigate.emit("practice", p))
            self.jump_row.addWidget(btn)
        if quizzes:
            btn = button("Quiz")
            btn.clicked.connect(
                lambda _=False, q=quizzes[0].id:
                self.ctx.navigate.emit("quiz", q))
            self.jump_row.addWidget(btn)
        if projects:
            btn = button("Projects  %d" % len(projects))
            btn.clicked.connect(
                lambda _=False, p=projects[0].id:
                self.ctx.navigate.emit("projects", p))
            self.jump_row.addWidget(btn)
        self.jump_row.addStretch(1)

    def _fill_body(self, phase) -> None:
        clear_layout(self.body)

        if phase.resources:
            card = Card()
            card.add(heading("Start here"))
            shown, folded = split_optional(phase.resources,
                                           phase.resources_optional)
            for res in shown:
                card.add(LinkRow(res.name, res.why, res.url, res.kind,
                                 primary=res.primary))
            if folded:
                more = Disclosure(len(folded), "to study",
                                  store=self.ctx.store,
                                  key="phase:" + phase.id)
                for res in folded:
                    more.add(LinkRow(res.name, res.why, res.url, res.kind))
                card.add(more)
            self.body.addWidget(card)

        checked = self.ctx.store.checked_ids()
        if phase.sections:
            # The right-click menu on every line has been there all along
            # with nothing anywhere saying so, which is the same as it not
            # being there.
            self.body.addWidget(muted(
                "Any line can join your review deck: right-click it, "
                "press the ... at its right edge, or Shift+F10."))
        for section in phase.sections:
            card = Card()
            top = QHBoxLayout()
            top.addWidget(heading(section.title), 1)
            done = sum(1 for item in section.items if item.id in checked)
            counter = muted("%d/%d" % (done, len(section.items)))
            top.addWidget(counter, 0, Qt.AlignmentFlag.AlignRight)
            card.box.addLayout(top)
            # Stretch work folds behind the same OPTIONAL pill the reading
            # list uses, and counts for nothing, so the main list is what
            # the page asks for.
            fold = None
            if section.optional:
                fold = Disclosure(len(section.items),
                                  "stretch goal%s" % (
                                      "" if len(section.items) == 1 else "s"),
                                  store=self.ctx.store,
                                  key="section:" + section.id, more=False)
                card.add(fold)
            for item in section.items:
                row = CheckRow(item.id, item.text, item.id in checked)
                row.toggled.connect(self._toggle)
                row.review_requested.connect(self._add_to_review)
                if fold is not None:
                    fold.add(row)
                else:
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

        if not self.body.count():
            self.body.addWidget(empty_state(
                "This phase has no checklist of its own.",
                "It sets the rules the rest of the curriculum follows. Use "
                "the Roadmap to pick the phase you are actually working on."))

    # -- actions -----------------------------------------------------------

    def _toggle(self, item_id: str, done: bool) -> None:
        phase = self.ctx.curriculum.phase(self.current_id)
        was_proven = (phase is not None and not phase.no_progress
                      and self.ctx.progress.phase(phase).is_proven)
        self.ctx.set_checked(item_id, done)
        if phase is not None and not phase.no_progress:
            stats = self.ctx.progress.phase(phase)
            self._show_progress(phase, stats)
            if stats.is_proven and not was_proven:
                self.ctx.announce("Phase %s proven. That is real progress."
                                  % phase.num)
            elif stats.is_read and done and not stats.is_proven:
                self.ctx.announce(
                    "Every line in phase %s is ticked. To prove it: %s."
                    % (phase.num, ", ".join(stats.outstanding())))

    def _add_to_review(self, item_id: str) -> None:
        self.ctx.review.add_concept(item_id)
        self.ctx.announce("Added to your review deck.")

    def _copy(self, text: str) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        self.ctx.announce("Copied.")

    def _grow_notes(self) -> None:
        """Let the notes box follow its content, between a floor and a ceiling.

        A fixed 120 px meant the fifth line of a note was being written into
        a two-line window with a scrollbar of its own - the worst place in
        the app to be writing anything. The box now grows to about fifteen
        lines and the page scrolls past that.
        """
        notes = getattr(self, "notes", None)
        if notes is None:
            return
        if notes.viewport().width() < 40:
            return          # not laid out yet; the next change sizes it
        # A plain text document's layout reports its height in *lines*, not
        # pixels - wrapped ones included - so this is the one place the two
        # have to be multiplied rather than used as they come.
        document = notes.document()
        lines = max(1.0, float(document.size().height()))
        wanted = int(lines * notes.fontMetrics().lineSpacing()
                     + 2 * document.documentMargin()
                     + 2 * notes.frameWidth() + 6)
        height = max(NOTE_MIN_HEIGHT, min(NOTE_MAX_HEIGHT, wanted))
        if height != notes.height():
            notes.setFixedHeight(height)

    def resizeEvent(self, event) -> None:
        """A narrower page wraps the note into more lines, and needs more room."""
        super().resizeEvent(event)
        if not self._built:
            return
        try:
            self._grow_notes()
        except RuntimeError:
            pass        # the page is being torn down underneath us

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

