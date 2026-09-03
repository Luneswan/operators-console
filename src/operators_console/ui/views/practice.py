"""Exercises: write code, run it, get graded, keep the work."""
from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QSplitter,
    QVBoxLayout, QWidget,
)

from ...core.runner import run_exercise
from ..widgets.common import (
    Card, button, label, muted, pill, soft,
)
from ..widgets.editor import CodeEditor
from .base import View

STATUS_TONE = {"passed": "done", "attempted": "warn", "new": ""}
STATUS_MARK = {"passed": "PASSED", "attempted": "IN PROGRESS", "new": ""}


class _RunSignals(QObject):
    finished = Signal(str, object)


class _RunJob(QRunnable):
    """Grade one submission off the interface thread."""

    def __init__(self, exercise_id: str, code: str, tests, setup: str,
                 timeout: int) -> None:
        super().__init__()
        self.signals = _RunSignals()
        self.exercise_id = exercise_id
        self.code = code
        self.tests = tests
        self.setup = setup
        self.timeout = timeout

    def run(self) -> None:
        try:
            result = run_exercise(self.code, self.tests, self.setup,
                                  self.timeout)
        except Exception as exc:  # never let a worker kill the app
            from ...core.runner import RunResult
            result = RunResult(ok=False, error="Runner failure: %s" % exc)
        self.signals.finished.emit(self.exercise_id, result)


class PracticeView(View):
    title = "Practice"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(ctx, parent)
        self.pool = QThreadPool.globalInstance()
        self.current = None
        self.hint_index = 0
        self._loading = False
        self._autosave = QTimer(self)
        self._autosave.setSingleShot(True)
        self._autosave.setInterval(700)
        self._autosave.timeout.connect(self._save_code)

    def build(self) -> None:
        self.scroller.setWidgetResizable(True)
        self.scroller.column.setContentsMargins(20, 18, 20, 20)

        self.header("Practice", "write it yourself",
                    "Every exercise is graded by running your code against real "
                    "checks. Nothing here is multiple choice.")

        filter_row = QHBoxLayout()
        filter_row.setSpacing(9)
        self.phase_filter = QComboBox()
        self.phase_filter.currentIndexChanged.connect(
            lambda _i: self._fill_list())
        filter_row.addWidget(muted("PHASE"))
        filter_row.addWidget(self.phase_filter, 1)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Not passed", "Passed"])
        self.status_filter.currentIndexChanged.connect(
            lambda _i: self._fill_list())
        filter_row.addWidget(muted("SHOW"))
        filter_row.addWidget(self.status_filter)
        self.counter = muted("")
        filter_row.addWidget(self.counter)
        self.scroller.add_layout(filter_row)

        split = QSplitter(Qt.Orientation.Horizontal)
        self.list = QListWidget()
        self.list.setMinimumWidth(230)
        self.list.currentItemChanged.connect(self._on_select)
        split.addWidget(self.list)
        split.addWidget(self._workspace())
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([260, 700])
        split.setMinimumHeight(560)
        self.scroller.add(split, 1)

    def _workspace(self) -> QWidget:
        panel = QWidget()
        column = QVBoxLayout(panel)
        column.setContentsMargins(14, 0, 0, 0)
        column.setSpacing(10)

        top = QHBoxLayout()
        self.ex_title = label("Pick an exercise", wrap=True)
        self.ex_title.setStyleSheet("font-size: 18px; font-weight: 700;")
        top.addWidget(self.ex_title, 1)
        self.ex_status = pill("")
        top.addWidget(self.ex_status, 0, Qt.AlignmentFlag.AlignTop)
        column.addLayout(top)

        self.ex_meta = muted("")
        column.addWidget(self.ex_meta)

        self.prompt = QLabel("")
        self.prompt.setWordWrap(True)
        self.prompt.setTextFormat(Qt.TextFormat.RichText)
        self.prompt.setObjectName("PageAim")
        self.prompt.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        column.addWidget(self.prompt)

        self.editor = CodeEditor(self.ctx.palette)
        self.editor.setMinimumHeight(240)
        self.editor.textChanged.connect(lambda: self._autosave.start())
        self.editor.run_requested.connect(self._run)
        column.addWidget(self.editor, 1)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.run_button = button("Run checks", "primary", "Ctrl+Enter")
        self.run_button.clicked.connect(self._run)
        controls.addWidget(self.run_button)
        self.hint_button = button("Hint", "quiet")
        self.hint_button.clicked.connect(self._next_hint)
        controls.addWidget(self.hint_button)
        self.reset_button = button("Reset", "quiet")
        self.reset_button.clicked.connect(self._reset)
        controls.addWidget(self.reset_button)
        self.solution_button = button("Show solution", "quiet")
        self.solution_button.clicked.connect(self._show_solution)
        controls.addWidget(self.solution_button)
        controls.addStretch(1)
        self.next_button = button("Next exercise", "quiet")
        self.next_button.clicked.connect(self._next_exercise)
        controls.addWidget(self.next_button)
        column.addLayout(controls)

        self.hint_label = soft("")
        self.hint_label.setVisible(False)
        column.addWidget(self.hint_label)

        self.results = Card(padding=12, spacing=6)
        self.results.setVisible(False)
        column.addWidget(self.results)
        return panel

    # -- list --------------------------------------------------------------

    def refresh(self) -> None:
        current_phase = self.phase_filter.currentData()
        self._loading = True
        self.phase_filter.clear()
        self.phase_filter.addItem("Everything", "")
        phases = sorted({e.phase for e in self.ctx.curriculum.exercises})
        for pid in phases:
            phase = self.ctx.curriculum.phase(pid)
            if phase is not None:
                self.phase_filter.addItem("%s  %s" % (phase.num, phase.name),
                                          pid)
        index = self.phase_filter.findData(current_phase or "")
        self.phase_filter.setCurrentIndex(max(0, index))
        self._loading = False
        self._fill_list()

    def show_target(self, target: str) -> None:
        """Accepts an exercise id, a quiz id or a phase id."""
        if target.startswith("q"):
            self.ctx.navigate.emit("quiz", target)
            return
        self.ensure_built()
        exercise = self.ctx.curriculum.exercise(target)
        if exercise is not None:
            index = self.phase_filter.findData(exercise.phase)
            if index >= 0:
                self.phase_filter.setCurrentIndex(index)
            self._select_id(target)
            return
        if self.ctx.curriculum.phase(target) is not None:
            index = self.phase_filter.findData(target)
            if index >= 0:
                self.phase_filter.setCurrentIndex(index)

    def _visible_exercises(self) -> list:
        pid = self.phase_filter.currentData() or ""
        mode = self.status_filter.currentText()
        statuses = self.ctx.store.exercise_statuses()
        out = []
        for exercise in self.ctx.curriculum.exercises:
            if pid and exercise.phase != pid:
                continue
            status = statuses.get(exercise.id, "new")
            if mode == "Passed" and status != "passed":
                continue
            if mode == "Not passed" and status == "passed":
                continue
            out.append(exercise)
        return out

    def _fill_list(self) -> None:
        if self._loading:
            return
        keep = self.current.id if self.current else None
        self.list.blockSignals(True)
        self.list.clear()
        statuses = self.ctx.store.exercise_statuses()
        for exercise in self._visible_exercises():
            status = statuses.get(exercise.id, "new")
            mark = {"passed": "✓ ", "attempted": "· "}.get(status, "  ")
            item = QListWidgetItem("%s%s" % (mark, exercise.title))
            item.setData(Qt.ItemDataRole.UserRole, exercise.id)
            item.setToolTip("%s - difficulty %d/5"
                            % (exercise.topic, exercise.difficulty))
            self.list.addItem(item)
        self.list.blockSignals(False)

        total = len(self.ctx.curriculum.exercises)
        passed = len(self.ctx.store.passed_exercise_ids())
        self.counter.setText("%d of %d passed overall" % (passed, total))

        if keep and self._select_id(keep):
            return
        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self._clear_workspace()

    def _select_id(self, exercise_id: str) -> bool:
        for row in range(self.list.count()):
            item = self.list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == exercise_id:
                self.list.setCurrentRow(row)
                return True
        return False

    def _on_select(self, item, _previous) -> None:
        if item is None:
            return
        self._save_code()
        exercise = self.ctx.curriculum.exercise(
            item.data(Qt.ItemDataRole.UserRole))
        if exercise is not None:
            self._load(exercise)

    # -- workspace ---------------------------------------------------------

    def _clear_workspace(self) -> None:
        self.current = None
        self.ex_title.setText("Nothing matches that filter")
        self.ex_meta.setText("")
        self.prompt.setText("")
        self.editor.setPlainText("")
        self.editor.setEnabled(False)
        self.run_button.setEnabled(False)
        self.results.setVisible(False)

    def _load(self, exercise) -> None:
        self.current = exercise
        self.hint_index = 0
        self.hint_label.setVisible(False)
        self.results.setVisible(False)
        self.editor.setEnabled(True)
        self.run_button.setEnabled(True)

        phase = self.ctx.curriculum.phase(exercise.phase)
        state = self.ctx.store.exercise(exercise.id)
        status = state.get("status", "new")

        self.ex_title.setText(exercise.title)
        self.ex_status.setText(STATUS_MARK.get(status, ""))
        self.ex_status.setProperty("tone", STATUS_TONE.get(status, ""))
        self.ex_status.setVisible(bool(STATUS_MARK.get(status)))
        _restyle(self.ex_status)

        self.ex_meta.setText(
            "%s  -  %s  -  difficulty %d of 5  -  %d attempt%s"
            % (phase.num if phase else "", exercise.topic,
               exercise.difficulty, state.get("attempts", 0),
               "" if state.get("attempts", 0) == 1 else "s"))
        self.prompt.setText(_markup(exercise.prompt))

        self._loading = True
        self.editor.set_code(state.get("code") or exercise.starter)
        self._loading = False
        self.hint_button.setEnabled(bool(exercise.hints))
        self.hint_button.setText(
            "Hint  (%d)" % len(exercise.hints) if exercise.hints else "Hint")
        self.solution_button.setEnabled(bool(exercise.solution))

    # -- actions -----------------------------------------------------------

    def _save_code(self) -> None:
        if self._loading or self.current is None:
            return
        self.ctx.store.save_exercise_code(self.current.id, self.editor.code())

    def _run(self) -> None:
        if self.current is None or not self.run_button.isEnabled():
            return
        self._save_code()
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self._show_message("Running your code...", "")
        timeout = int(self.ctx.store.setting("exercise_timeout", 10))
        job = _RunJob(self.current.id, self.editor.code(), self.current.tests,
                      self.current.setup, timeout)
        job.signals.finished.connect(self._on_result)
        self.pool.start(job)

    def _on_result(self, exercise_id: str, result) -> None:
        self.run_button.setEnabled(True)
        self.run_button.setText("Run checks")
        if self.current is None or self.current.id != exercise_id:
            return

        already = self.ctx.store.exercise(exercise_id)["status"] == "passed"
        self.ctx.store.record_exercise_run(exercise_id, self.editor.code(),
                                           result.ok)
        self._render_result(result)
        self.ctx.changed()
        self._fill_list()
        if result.ok and not already:
            self.ctx.announce("Passed. %s" % self.current.title)

    def _render_result(self, result) -> None:
        _empty(self.results.box)
        self.results.setVisible(True)
        tone = "done" if result.ok else "bad"
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        header_row.addWidget(pill("PASSED" if result.ok else "NOT YET", tone))
        header_row.addWidget(label(result.summary, "Soft"), 1)
        header_row.addWidget(muted("%d ms" % result.duration_ms))
        self.results.box.addLayout(header_row)

        for case in result.cases:
            row = QHBoxLayout()
            row.setSpacing(8)
            mark = label("PASS" if case.passed else "FAIL", "Mono", wrap=False)
            mark.setStyleSheet(
                "color: %s; font-weight: 700;"
                % (self.ctx.palette.done if case.passed else self.ctx.palette.bad))
            mark.setFixedWidth(44)
            row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
            text = case.name if case.passed else "%s  -  %s" % (case.name,
                                                                case.message)
            row.addWidget(label(text, "Soft"), 1)
            self.results.box.addLayout(row)

        if result.error:
            self.results.add(label("What Python said", "SectionTitle",
                                   wrap=False))
            self.results.add(label(result.error, "Code", selectable=True))
        if result.stdout.strip():
            self.results.add(label("Your output", "SectionTitle", wrap=False))
            self.results.add(label(result.stdout.rstrip(), "Code",
                                   selectable=True))

    def _show_message(self, text: str, tone: str) -> None:
        _empty(self.results.box)
        self.results.setVisible(True)
        self.results.add(label(text, "Soft"))

    def _next_hint(self) -> None:
        if self.current is None or not self.current.hints:
            return
        hint = self.current.hints[self.hint_index % len(self.current.hints)]
        self.hint_index += 1
        self.hint_label.setText("Hint %d of %d - %s"
                                % (min(self.hint_index, len(self.current.hints)),
                                   len(self.current.hints), hint))
        self.hint_label.setVisible(True)

    def _reset(self) -> None:
        if self.current is None:
            return
        self.editor.set_code(self.current.starter)
        self._save_code()

    def _show_solution(self) -> None:
        if self.current is None or not self.current.solution:
            return
        from PySide6.QtWidgets import QMessageBox
        state = self.ctx.store.exercise(self.current.id)
        if state["status"] != "passed" and not state.get("revealed"):
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Show the solution?")
            confirm.setText(
                "You have not passed this one yet.\n\nReading the answer now "
                "costs you the exercise. Try one more hint first?")
            confirm.setIcon(QMessageBox.Icon.Question)
            show = confirm.addButton("Show it anyway",
                                     QMessageBox.ButtonRole.DestructiveRole)
            confirm.addButton("Keep trying", QMessageBox.ButtonRole.RejectRole)
            confirm.exec()
            if confirm.clickedButton() is not show:
                return
        self.ctx.store.reveal_solution(self.current.id)
        _empty(self.results.box)
        self.results.setVisible(True)
        self.results.add(label("One correct solution", "SectionTitle",
                               wrap=False))
        self.results.add(label(self.current.solution, "Code", selectable=True))
        self.results.add(muted(
            "Type it out rather than pasting it, then come back tomorrow and "
            "write it again from memory."))

    def _next_exercise(self) -> None:
        row = self.list.currentRow()
        if row + 1 < self.list.count():
            self.list.setCurrentRow(row + 1)


def _markup(text: str) -> str:
    """Render the authored prompt: backticks become code, blank lines split."""
    import html
    import re
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    paragraphs = [p.replace("\n", " ") for p in escaped.split("\n\n")]
    return "<br><br>".join(paragraphs)


def _restyle(widget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
