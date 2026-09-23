"""Exercises: write code, run it, get graded, keep the work."""
from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QSplitter, QVBoxLayout, QWidget,
)

from ...core.runner import RunHandle, run_exercise
from ...core.textmatch import matches as _text_matches
from ..widgets.common import (
    Card, button, clear_layout, label, muted, pill, soft,
)
from ..widgets.editor import CodeEditor
from .base import View

#: The five states an exercise can be in, as the learner meets them.
#: "revealed" and "read" both mean the solution was shown; they are kept
#: apart because passing after reading is a different thing from not having
#: passed at all, and the list should not pretend otherwise.
STATUS_TONE = {"passed": "done", "revealed": "accent", "read": "warn",
               "attempted": "warn", "new": ""}
STATUS_MARK = {"passed": "PASSED", "revealed": "PASSED - READ",
               "read": "ANSWER READ", "attempted": "ATTEMPTED", "new": ""}
STATUS_WORD = {"passed": "passed", "revealed": "solved after reading",
               "read": "answer read, not passed yet",
               "attempted": "not passed yet", "new": "not started"}

#: The Show filter, and which stored statuses each choice keeps.
SHOW_CHOICES = ("All", "Not passed", "Passed", "Revealed")

LAST_IN_FILTER = "That is the last one in this filter."
NO_HINTS = "No hints for this one."
ALL_HINTS = "That is every hint for this one."


def effective_status(status: str, revealed) -> str:
    """What the list shows, once reading the answer is taken into account."""
    if revealed:
        return "revealed" if status == "passed" else "read"
    return status or "new"


class _RunSignals(QObject):
    finished = Signal(str, object)


class _RunJob(QRunnable):
    """Grade one submission off the interface thread.

    The handle is a plain Python object rather than the job itself: Qt
    deletes a finished QRunnable, and Stop must stay safe to press right up
    to the moment the result arrives.
    """

    def __init__(self, exercise_id: str, code: str, tests, setup: str,
                 timeout: int) -> None:
        super().__init__()
        self.signals = _RunSignals()
        self.exercise_id = exercise_id
        self.code = code
        self.tests = tests
        self.setup = setup
        self.timeout = timeout
        self.handle = RunHandle()

    def run(self) -> None:
        from ...core.runner import RunResult
        if self.handle.cancelled:
            # Stopped while it was still queued: never started, so nothing
            # to kill and nothing to report but the stop itself.
            self.signals.finished.emit(
                self.exercise_id,
                RunResult(ok=False, cancelled=True, error="Stopped."))
            return
        try:
            result = run_exercise(self.code, self.tests, self.setup,
                                  self.timeout, handle=self.handle)
        except Exception as exc:  # never let a worker kill the app
            result = RunResult(ok=False, error="Runner failure: %s" % exc)
        self.signals.finished.emit(self.exercise_id, result)


class PracticeView(View):
    title = "Practice"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(ctx, parent)
        self.pool = QThreadPool.globalInstance()
        self.current = None
        self.hint_index = 0
        self._hints_shown = []
        self._loading = False
        # Which store, and which generation of it, the open exercise came
        # from. A restore swaps the contents underneath; the editor then holds
        # code from before it and must neither stay nor be saved.
        self._loaded_from = None
        self._running = False
        self._handle = None
        # What the store said last time it was read, so the control sync that
        # runs on every keystroke never has to go back to it.
        self._passing_code = ""
        self._retryable = False
        self._autosave = QTimer(self)
        self._autosave.setSingleShot(True)
        self._autosave.setInterval(700)
        self._autosave.timeout.connect(self._save_code)
        self.taught_button = None

    def build(self) -> None:
        self.scroller.setWidgetResizable(True)
        # The same top and side margins as every other page, so the
        # header does not jump when switching to it.
        self.scroller.column.setContentsMargins(24, 24, 24, 20)

        self.header("Practice", "graded exercises",
                    "Each exercise runs your code against real checks.")

        # Ninety-six exercises need a way in that is not scrolling: a search
        # of its own line, so a long phase name never squeezes it out.
        find_row = QHBoxLayout()
        find_row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search titles, topics and briefs")
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName("Search the exercises")
        self.search.textChanged.connect(lambda _t: self._fill_list())
        find_row.addWidget(muted("FIND"))
        find_row.addWidget(self.search, 1)
        self.scroller.add_layout(find_row)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.phase_filter = QComboBox()
        self.phase_filter.setAccessibleName("Filter by phase")
        self.phase_filter.currentIndexChanged.connect(
            lambda _i: self._fill_list())
        filter_row.addWidget(muted("PHASE"))
        filter_row.addWidget(self.phase_filter, 1)
        self.status_filter = QComboBox()
        self.status_filter.addItems(list(SHOW_CHOICES))
        self.status_filter.setAccessibleName("Filter by progress")
        self.status_filter.currentIndexChanged.connect(
            lambda _i: self._fill_list())
        filter_row.addWidget(muted("SHOW"))
        filter_row.addWidget(self.status_filter)
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItem("Any", 0)
        for level in range(1, 6):
            self.difficulty_filter.addItem("%d of 5" % level, level)
        self.difficulty_filter.setAccessibleName("Filter by difficulty")
        self.difficulty_filter.currentIndexChanged.connect(
            lambda _i: self._fill_list())
        filter_row.addWidget(muted("LEVEL"))
        filter_row.addWidget(self.difficulty_filter)
        self.counter = muted("")
        filter_row.addWidget(self.counter)
        self.scroller.add_layout(filter_row)

        split = QSplitter(Qt.Orientation.Horizontal)
        self.list = QListWidget()
        self.list.setMinimumWidth(190)
        # Long titles wrap instead of hiding behind a sideways scrollbar.
        self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.currentItemChanged.connect(self._on_select)
        split.addWidget(self.list)
        split.addWidget(self._workspace())
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([260, 700])
        # 560 put Run checks below the fold on a 768- or 864-pixel screen.
        split.setMinimumHeight(420)
        self.scroller.add(split, 1)

    def _workspace(self) -> QWidget:
        panel = QWidget()
        column = QVBoxLayout(panel)
        column.setContentsMargins(14, 0, 0, 0)
        column.setSpacing(8)

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

        # The same three things for every exercise, read off its own data:
        # what a right answer looks like, and that the checks do the calling.
        self.brief = QLabel("")
        self.brief.setObjectName("Soft")
        self.brief.setWordWrap(True)
        self.brief.setTextFormat(Qt.TextFormat.RichText)
        self.brief.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        column.addWidget(self.brief)

        self.editor = CodeEditor(self.ctx.palette)
        self.editor.setMinimumHeight(240)
        self.editor.textChanged.connect(self._on_edit)
        self.editor.run_requested.connect(self._run)
        column.addWidget(self.editor, 1)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.run_button = button("Run checks", "primary", "Ctrl+Enter")
        self.run_button.clicked.connect(self._run)
        controls.addWidget(self.run_button)
        # Stop takes the same place on the row rather than appearing beside
        # Run: one slot, one meaning, and nothing moves under the pointer.
        self.stop_button = button("Stop", "danger",
                                  "Stop this run and record nothing")
        self.stop_button.clicked.connect(self._stop)
        self.stop_button.setVisible(False)
        controls.addWidget(self.stop_button)
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
        self.next_button = button("Next", "quiet", "The next exercise")
        self.next_button.clicked.connect(self._next_exercise)
        controls.addWidget(self.next_button)
        column.addLayout(controls)

        # The two ways back. Both are hidden until there is something to go
        # back to, so the ordinary row above stays four buttons wide.
        self.recovery = QWidget()
        recovery_row = QHBoxLayout(self.recovery)
        recovery_row.setContentsMargins(0, 0, 0, 0)
        recovery_row.setSpacing(8)
        self.restore_button = button(
            "Restore my passing version", "quiet",
            "Put back the code that last passed these checks")
        self.restore_button.clicked.connect(self._restore_passing)
        recovery_row.addWidget(self.restore_button)
        self.again_button = button(
            "Try this one again from scratch", "quiet",
            "Back to the starter code, and the exercise counts as unsolved "
            "again")
        self.again_button.clicked.connect(self._try_again)
        recovery_row.addWidget(self.again_button)
        recovery_row.addStretch(1)
        self.recovery.setVisible(False)
        column.addWidget(self.recovery)

        self.hint_label = soft("")
        self.hint_label.setTextFormat(Qt.TextFormat.RichText)
        self.hint_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
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

    def resume_target(self) -> str:
        return self.current.id if self.current is not None else ""

    @property
    def busy(self) -> bool:
        return self._running

    def teardown(self) -> None:
        if not self._built:
            return
        self._save_code()
        self._autosave.stop()
        self.current = None
        self._loaded_from = None
        self.taught_button = None
        super().teardown()

    # -- surviving a theme or text-size change -----------------------------

    def save_state(self):
        return {
            "search": self.search.text(),
            "phase": self.phase_filter.currentData() or "",
            "status": self.status_filter.currentIndex(),
            "level": self.difficulty_filter.currentData() or 0,
            "exercise": self.current.id if self.current is not None else "",
        }

    def restore_state(self, state) -> None:
        """The four filters, then the exercise that was open, if it shows."""
        self._loading = True
        try:
            self.search.setText(state.get("search", ""))
            index = self.phase_filter.findData(state.get("phase", ""))
            self.phase_filter.setCurrentIndex(max(0, index))
            status = int(state.get("status", 0))
            if 0 <= status < self.status_filter.count():
                self.status_filter.setCurrentIndex(status)
            index = self.difficulty_filter.findData(state.get("level", 0))
            self.difficulty_filter.setCurrentIndex(max(0, index))
        finally:
            self._loading = False
        self._fill_list()
        wanted = state.get("exercise", "")
        if wanted and (self.current is None or self.current.id != wanted):
            self._select_id(wanted)

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
            if not self._select_id(target):
                # A search or a level filter is hiding it. Being sent
                # somewhere must always arrive, so the filters give way.
                self._clear_filters()
                self._select_id(target)
            return
        if self.ctx.curriculum.phase(target) is not None:
            index = self.phase_filter.findData(target)
            if index >= 0:
                self.phase_filter.setCurrentIndex(index)

    def _clear_filters(self) -> None:
        self._loading = True
        self.search.clear()
        self.status_filter.setCurrentIndex(0)
        self.difficulty_filter.setCurrentIndex(0)
        self._loading = False
        self._fill_list()

    def _visible_exercises(self, rows: dict | None = None) -> list:
        pid = self.phase_filter.currentData() or ""
        mode = self.status_filter.currentText()
        level = self.difficulty_filter.currentData() or 0
        needle = self.search.text()
        rows = self.ctx.store.exercise_rows() if rows is None else rows
        out = []
        for exercise in self.ctx.curriculum.exercises:
            if pid and exercise.phase != pid:
                continue
            if level and exercise.difficulty != level:
                continue
            state = rows.get(exercise.id) or {}
            status = state.get("status", "new")
            if mode == "Passed" and status != "passed":
                continue
            if mode == "Not passed" and status == "passed":
                continue
            if mode == "Revealed" and not state.get("revealed"):
                continue
            if not _matches(exercise, needle):
                continue
            out.append(exercise)
        return out

    def _fill_list(self) -> None:
        if self._loading:
            return
        keep = self.current.id if self.current else None
        self.list.blockSignals(True)
        self.list.clear()
        rows = self.ctx.store.exercise_rows()
        visible = self._visible_exercises(rows)
        for exercise in visible:
            state = rows.get(exercise.id) or {}
            status = effective_status(state.get("status", "new"),
                                      state.get("revealed"))
            # An icon, not a text mark: "✓ ", "· " and two spaces are three
            # different widths, so the titles never lined up.
            item = QListWidgetItem(self._status_icon(status), exercise.title)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, "%s, %s" % (
                exercise.title, STATUS_WORD.get(status, "not started")))
            item.setData(Qt.ItemDataRole.UserRole, exercise.id)
            item.setToolTip("%s - difficulty %d/5 - %s"
                            % (exercise.topic, exercise.difficulty,
                               STATUS_WORD.get(status, "not started")))
            self.list.addItem(item)
        self.list.blockSignals(False)

        total = len(self.ctx.curriculum.exercises)
        passed = len(self.ctx.store.passed_exercise_ids())
        shown = len(visible)
        # Kept short on purpose: the filter row has three dropdowns on it,
        # and a longer sentence here wraps and pushes the row taller.
        text = "%d of %d passed" % (passed, total)
        if shown != total:
            text = "%d shown  -  %s" % (shown, text)
        self.counter.setText(text)

        if keep and self._select_id(keep):
            self._sync_controls()
            return
        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self._clear_workspace()
        self._sync_controls()

    def _status_icon(self, status: str):
        """A check for passed, a ring for read, a dot for tried, else blank."""
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

        palette = self.ctx.palette
        key = (status, palette.done, palette.ink_faint, palette.warn)
        cache = self.__dict__.setdefault("_icons", {})
        if key in cache:
            return cache[key]
        ratio = max(1.0, self.devicePixelRatioF())
        pixmap = QPixmap(round(14 * ratio), round(14 * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if status in ("passed", "revealed"):
            # A pass earned after reading the answer is still a pass; a
            # quieter colour is the honest way to say which it was.
            colour = palette.done if status == "passed" else palette.ink_faint
            pen = QPen(QColor(colour), 2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline([QPointF(3, 7.5), QPointF(6, 10.5),
                                  QPointF(11, 3.5)])
        elif status == "read":
            painter.setPen(QPen(QColor(palette.warn), 1.6))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(7, 7), 3.2, 3.2)
        elif status == "attempted":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(palette.ink_faint))
            painter.drawEllipse(QPointF(7, 7), 2.5, 2.5)
        painter.end()
        cache[key] = QIcon(pixmap)
        return cache[key]

    def _select_id(self, exercise_id: str) -> bool:
        for row in range(self.list.count()):
            item = self.list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == exercise_id:
                self.list.setCurrentRow(row)
                return True
        return False

    def _store_key(self):
        store = self.ctx.store
        return (id(store), getattr(store, "generation", 0))

    def _on_select(self, item, _previous) -> None:
        if item is None:
            return
        exercise_id = item.data(Qt.ItemDataRole.UserRole)
        if self._loaded_from == self._store_key():
            if self.current is not None and exercise_id == self.current.id:
                # The list was refilled around the open exercise (after every
                # run, and on every visit). Reloading it here hid the result
                # the learner had just produced, and the hint with it.
                self._sync_controls()
                return
            self._save_code()
        exercise = self.ctx.curriculum.exercise(exercise_id)
        if exercise is not None:
            self._load(exercise)

    # -- workspace ---------------------------------------------------------

    def _clear_workspace(self) -> None:
        self.current = None
        self._passing_code = ""
        self._retryable = False
        self.ex_title.setText("Nothing matches that filter")
        self.ex_meta.setText("Widen the search, the phase or the level to "
                             "see exercises again.")
        self.prompt.setText("")
        self.brief.setText("")
        self.editor.setPlainText("")
        self.editor.setEnabled(False)
        self.ex_status.setVisible(False)
        self.hint_label.setVisible(False)
        self.recovery.setVisible(False)
        self.results.setVisible(False)

    def _load(self, exercise) -> None:
        self.current = exercise
        self._loaded_from = self._store_key()
        self.hint_index = 0
        self._hints_shown = []
        self.hint_label.setVisible(False)
        self.results.setVisible(False)
        self.editor.setEnabled(True)

        state = self._show_header(exercise)
        self.prompt.setText(_markup(exercise.prompt))
        self.brief.setText(_brief_html(exercise))

        self._loading = True
        self.editor.set_code(state.get("code") or exercise.starter)
        self._loading = False
        self._sync_controls()

    def _show_header(self, exercise) -> dict:
        """Title, status and attempts. Also called after every run."""
        phase = self.ctx.curriculum.phase(exercise.phase)
        state = self.ctx.store.exercise(exercise.id)
        status = effective_status(state.get("status", "new"),
                                  state.get("revealed"))

        self.ex_title.setText(exercise.title)
        self.ex_status.setText(STATUS_MARK.get(status, ""))
        self.ex_status.setProperty("tone", STATUS_TONE.get(status, ""))
        self.ex_status.setVisible(bool(STATUS_MARK.get(status)))
        _restyle(self.ex_status)

        attempts = state.get("attempts", 0)
        parts = ["%s" % (phase.num if phase else ""), exercise.topic,
                 "difficulty %d of 5" % exercise.difficulty,
                 "%d attempt%s" % (attempts, "" if attempts == 1 else "s")]
        hints = int(state.get("hints_used", 0) or 0)
        if hints:
            parts.append("%d hint%s used" % (hints, "" if hints == 1 else "s"))
        self.ex_meta.setText("  -  ".join(part for part in parts if part))

        # One read of the store serves the header and the two recovery
        # buttons, which are re-evaluated on every keystroke.
        self._passing_code = state.get("passing_code") or ""
        self._retryable = bool(state.get("revealed")
                               or state.get("status") == "passed")
        return state

    # -- actions -----------------------------------------------------------

    def _on_edit(self) -> None:
        self._autosave.start()
        self._sync_controls()

    def _sync_controls(self) -> None:
        """Every control's enabled state and tooltip, in one place.

        Buttons that quietly disappeared, lied about what they would do or
        did nothing at all were the bulk of what was wrong with this page.
        """
        exercise = self.current
        running = self._running
        self.run_button.setVisible(not running)
        self.run_button.setEnabled(exercise is not None and not running)
        self.stop_button.setVisible(running)
        self.stop_button.setEnabled(running)

        hints = _hints_for(exercise) if exercise is not None else ()
        # Shown either way: a button that vanishes reads as a bug, and the
        # tooltip says why it cannot be pressed.
        self.hint_button.setVisible(True)
        if not hints:
            self.hint_button.setEnabled(False)
            self.hint_button.setText("Hint")
            self.hint_button.setToolTip(NO_HINTS)
        else:
            left = len(hints) - self.hint_index
            self.hint_button.setEnabled(left > 0 and not running)
            self.hint_button.setText("Hint  (%d)" % len(hints))
            self.hint_button.setToolTip(
                ALL_HINTS if left <= 0
                else "%d of %d still to read" % (left, len(hints)))

        self.reset_button.setEnabled(exercise is not None and not running)
        self.solution_button.setEnabled(
            exercise is not None and bool(exercise.solution) and not running)

        last = self.list.currentRow() + 1 >= self.list.count()
        self.next_button.setEnabled(not last)
        self.next_button.setToolTip(
            LAST_IN_FILTER if last else "The next exercise")

        passing = self._passing_code if exercise is not None else ""
        can_restore = bool(passing) and passing != self.editor.code()
        self.restore_button.setVisible(can_restore)
        self.restore_button.setEnabled(can_restore and not running)
        can_retry = exercise is not None and self._retryable
        self.again_button.setVisible(can_retry)
        self.again_button.setEnabled(can_retry and not running)
        self.recovery.setVisible(can_restore or can_retry)

    def _save_code(self) -> None:
        if self._loading or self.current is None:
            return
        if self._loaded_from != self._store_key():
            return          # code from before a restore must not overwrite it
        self.ctx.store.save_exercise_code(self.current.id, self.editor.code())

    def _run(self) -> None:
        if self._running:
            self._stop()
            return
        if self.current is None or not self.run_button.isEnabled():
            return
        self._save_code()
        self._running = True
        self._sync_controls()
        self._show_message("Running your code...", "")
        timeout = int(self.ctx.store.setting("exercise_timeout", 10))
        job = _RunJob(self.current.id, self.editor.code(), self.current.tests,
                      self.current.setup, timeout)
        self._handle = job.handle
        job.signals.finished.connect(self._on_result)
        self.pool.start(job)

    def _stop(self) -> None:
        """Kill the grader and everything it started, and record nothing."""
        if not self._running or self._handle is None:
            return
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stopping...")
        self._handle.cancel()
        self.ctx.announce("Stopping the run.")

    def _on_result(self, exercise_id: str, result) -> None:
        self._running = False
        self._handle = None
        if not getattr(self.ctx.store, "is_open", True) or not self._built:
            return          # the window closed mid-run; nothing to report to
        self.stop_button.setText("Stop")
        if self.current is None or self.current.id != exercise_id:
            self._sync_controls()
            return

        if result.cancelled:
            # A run the learner called off is not an attempt. Recording one
            # would punish them for stopping an endless loop.
            self._show_message(
                "Stopped. Nothing was recorded for this run.", "")
            self._sync_controls()
            self.ctx.announce("Stopped.")
            return

        already = self.ctx.store.exercise(exercise_id)["status"] == "passed"
        self.ctx.store.record_exercise_run(exercise_id, self.editor.code(),
                                           result.ok)
        self._render_result(result)
        self.ctx.changed()
        self._fill_list()
        self._show_header(self.current)
        self._sync_controls()
        QTimer.singleShot(0, self._reveal_results)
        if result.ok and not already:
            self.ctx.announce("Passed. %s" % self.current.title)

    def _reveal_results(self) -> None:
        """Bring the start of the result into view if it landed below it.

        ensureWidgetVisible bottom-aligns anything taller than the viewport,
        which would show the end of a long result rather than its verdict.
        """
        if not self.results.isVisible():
            return
        bar = self.scroller.verticalScrollBar()
        top = self.results.mapTo(self.scroller.widget(), self.results.rect().topLeft()).y()
        view = self.scroller.viewport().height()
        if top + 48 > bar.value() + view:          # the verdict is off screen
            bar.setValue(min(bar.maximum(), top - int(view * 0.4)))

    def _render_result(self, result) -> None:
        clear_layout(self.results.box)
        self.taught_button = None
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
            mark.setMinimumWidth(44)
            row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
            # One sentence beside the name, and the values that back it up
            # underneath in monospace - a caret under the character that
            # differs only lines up in a fixed-width font.
            body = QVBoxLayout()
            body.setSpacing(2)
            body.setContentsMargins(0, 0, 0, 0)
            text = case.name if case.passed else "%s  -  %s" % (case.name,
                                                                case.message)
            # The grader writes `code` in backticks ("is a `return`
            # missing?"); shown raw, the backticks read as noise.
            sentence = label(_markup(text), "Soft")
            sentence.setTextFormat(Qt.TextFormat.RichText)
            body.addWidget(sentence)
            detail = getattr(case, "detail", "")
            if not case.passed and detail:
                body.addWidget(label(detail, "Mono", selectable=True))
            row.addLayout(body, 1)
            self.results.box.addLayout(row)

        why = getattr(result, "why", "")
        if why:
            self.results.add(label("What went wrong", "SectionTitle",
                                   wrap=False))
            explained = label(_markup(why), "Soft")
            explained.setTextFormat(Qt.TextFormat.RichText)
            self.results.add(explained)
        if result.error:
            self.results.add(label("What Python said", "SectionTitle",
                                   wrap=False))
            self.results.add(label(result.error, "Code", selectable=True))
        if result.stdout.strip():
            self.results.add(label("Your output", "SectionTitle", wrap=False))
            self.results.add(label(result.stdout.rstrip(), "Code",
                                   selectable=True))
        if not result.ok:
            self._offer_the_lesson()

    def _offer_the_lesson(self) -> None:
        """A way back to the phase that teaches this, after a failed run.

        Rereading the part of the course an exercise came from is usually a
        better next step than a fourth guess, and it was three pages away.
        """
        exercise = self.current
        phase = (self.ctx.curriculum.phase(exercise.phase)
                 if exercise is not None else None)
        if phase is None:
            return
        row = QHBoxLayout()
        row.setSpacing(8)
        taught = button("Where this is taught", "quiet",
                        "Open phase %s - %s, where %s is covered"
                        % (phase.num, phase.name, exercise.topic or "this"))
        taught.clicked.connect(
            lambda _=False, pid=phase.id: self.ctx.navigate.emit("phase", pid))
        row.addWidget(taught)
        row.addWidget(muted("Phase %s - %s" % (phase.num, phase.name)), 1)
        self.results.box.addLayout(row)
        self.taught_button = taught

    def _show_message(self, text: str, tone: str) -> None:
        clear_layout(self.results.box)
        self.results.setVisible(True)
        self.results.add(label(text, "Soft"))

    def _next_hint(self) -> None:
        hints = _hints_for(self.current) if self.current is not None else ()
        if not hints:
            return
        total = len(hints)
        if self.hint_index >= total:
            # It used to wrap silently back to hint 1 while the label still
            # counted up, so "Hint 4 of 3" showed the first hint again.
            self.ctx.announce(ALL_HINTS)
            self._sync_controls()
            return
        title, body = hints[self.hint_index]
        self.hint_index += 1
        self._hints_shown.append(
            "<b>Hint %d of %d%s</b><br>%s"
            % (self.hint_index, total, " - " + title if title else "", body))
        # Every hint read so far stays on screen: hint 2 usually only makes
        # sense next to hint 1.
        self.hint_label.setText("<br><br>".join(self._hints_shown))
        self.hint_label.setVisible(True)
        self.ctx.store.use_hint(self.current.id, self.hint_index)
        self._show_header(self.current)
        self._sync_controls()

    def _reset(self) -> None:
        if self.current is None:
            return
        if self.editor.code() == self.current.starter:
            self.ctx.announce("This is already the starter code.")
            return
        # One click next to Hint used to destroy the learner's work for good.
        self.editor.replace_code(self.current.starter)
        self._save_code()
        self.editor.setFocus()      # so Ctrl+Z reaches the editor, not the app
        self._sync_controls()
        self.ctx.announce("Starter code is back. Ctrl+Z in the editor "
                          "brings your code back.")

    def _restore_passing(self) -> None:
        """Put back the last version that passed. Undoable, like Reset."""
        if self.current is None:
            return
        passing = self.ctx.store.exercise(self.current.id).get("passing_code")
        if not passing or passing == self.editor.code():
            self.ctx.announce("This is already your passing version.")
            self._sync_controls()
            return
        self.editor.replace_code(passing)
        self._save_code()
        self.editor.setFocus()
        self._sync_controls()
        self.ctx.announce("Your passing version is back. Ctrl+Z in the "
                          "editor undoes this.")

    def _try_again(self) -> None:
        """Back to the starter, with the exercise counted as unsolved."""
        if self.current is None:
            return
        self.editor.replace_code(self.current.starter)
        self._save_code()
        self.ctx.store.rearm_exercise(self.current.id)
        self.editor.setFocus()
        self.hint_label.setVisible(False)
        self._hints_shown = []
        self.hint_index = 0
        self.results.setVisible(False)
        self.ctx.changed()
        self._fill_list()
        self._show_header(self.current)
        self._sync_controls()
        self.ctx.announce("Starter code is back and this one counts as "
                          "unsolved again. Ctrl+Z undoes the editor change.")

    def _show_solution(self) -> None:
        if self.current is None or not self.current.solution:
            return
        from PySide6.QtWidgets import QMessageBox
        state = self.ctx.store.exercise(self.current.id)
        if state["status"] != "passed" and not state.get("revealed"):
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Show the solution?")
            confirm.setText(
                "You have not passed this one.\n\nIf you read the answer, it "
                "is marked as read, not solved. Try another hint first?")
            confirm.setIcon(QMessageBox.Icon.Question)
            show = confirm.addButton("Show it anyway",
                                     QMessageBox.ButtonRole.DestructiveRole)
            confirm.addButton("Keep trying", QMessageBox.ButtonRole.RejectRole)
            confirm.exec()
            if confirm.clickedButton() is not show:
                return
        self.ctx.store.reveal_solution(self.current.id)
        clear_layout(self.results.box)
        self.results.setVisible(True)
        self.results.add(label("One correct solution", "SectionTitle",
                               wrap=False))
        self.results.add(label(self.current.solution, "Code", selectable=True))
        self.results.add(muted(
            "Type it out instead of pasting. Tomorrow, write it again from "
            "memory."))
        self.ctx.changed()
        self._fill_list()
        self._show_header(self.current)
        self._sync_controls()

    def _next_exercise(self) -> None:
        row = self.list.currentRow()
        if row + 1 < self.list.count():
            self.list.setCurrentRow(row + 1)
        else:
            self.ctx.announce(LAST_IN_FILTER)
        self._sync_controls()


def _matches(exercise, query: str) -> bool:
    """Every word of the query in the title, topic, id or brief.

    Through core.textmatch, like every other box in the app: case, accents,
    dashes and extra spaces never decide it, and word order does not matter.
    """
    return _text_matches(query, exercise.title, exercise.topic, exercise.id,
                         exercise.prompt)


SHAPE_TITLE = "the shape of an answer"


def _hints_for(exercise) -> tuple:
    """(title, html) for every hint: the written ones, then the shape.

    The written hints nudge; the last one shows how the solution is built -
    its `def`, loops, branches and returns - with every expression taken
    out, so there is a step between the last nudge and the whole answer.
    """
    import html

    from ...core.exercise_brief import skeleton
    out = [("", _markup(str(h))) for h in (exercise.hints or ())]
    shape = skeleton(exercise.solution)
    if shape:
        out.append((SHAPE_TITLE,
                    "Replace each <code>...</code> with code.<pre>%s</pre>" % html.escape(shape)))
    return tuple(out)


def _brief_html(exercise) -> str:
    """Worked examples from the checks, and how the work is judged."""
    import html

    from ...core.exercise_brief import examples, how_checked
    parts = []
    pairs = examples(exercise)
    if pairs:
        rows = "<br>".join(
            "<code>%s</code> &nbsp;&rarr;&nbsp; <code>%s</code>"
            % (html.escape(call), html.escape(value)) for call, value in pairs)
        parts.append("<b>For example</b><br>" + rows)
    parts.append("<b>How it is checked</b><br>" + _markup(how_checked(exercise)))
    return "<br><br>".join(parts)


def _markup(text: str) -> str:
    """Render the authored prompt: backticks become code, blank lines split."""
    import html
    import re
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    # *word* is emphasis in the authored prompts ("the second largest
    # *distinct* value") and used to reach the screen with its asterisks.
    # Code spans are left alone: `a*b*c` is arithmetic, not italics.
    parts = re.split(r"(<code>.*?</code>)", escaped)
    escaped = "".join(
        part if part.startswith("<code>")
        else re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<i>\1</i>",
                    part)
        for part in parts)
    paragraphs = [p.replace("\n", " ") for p in escaped.split("\n\n")]
    return "<br><br>".join(paragraphs)


def _restyle(widget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
