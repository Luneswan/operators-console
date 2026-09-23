"""Progress: the numbers, honestly, including the ones that are not flattering."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem,
    QVBoxLayout,
)

from ..widgets.charts import ActivityGrid, BarChart
from ..widgets.common import (
    Card, StatTile, clear_layout, heading, label, muted,
)
from .base import View

CONFIDENCE = ("Never touched", "Read about it", "Followed a tutorial",
              "Built with it", "Could teach it")

#: The phase table's columns, which are also the SORT choices.
COLUMNS = ("Phase", "Checks", "Exercises", "Quiz", "Gate", "Projects")

#: Where a cell's number lives. The display text stays as it was ("12/18",
#: "67%", "-"); sorting reads this instead, so 9/18 sorts below 12/18 and
#: not after it, as the strings would.
SORT_ROLE = Qt.ItemDataRole.UserRole + 1


class _SortItem(QTableWidgetItem):
    """A cell that sorts by its number, not by its text."""

    def __lt__(self, other) -> bool:
        mine = self.data(SORT_ROLE)
        theirs = other.data(SORT_ROLE)
        if mine is None or theirs is None:
            return super().__lt__(other)
        return mine < theirs


def _ratio(done: int, total: int) -> float:
    """How far through a column's count a phase is, 0 to 1; -1 for none.

    A phase with nothing to count ("-") sorts before one with nothing done,
    so the rows with real work in them stay together.
    """
    return done / total if total else -1.0


class StatsView(View):
    title = "Progress"

    def build(self) -> None:
        self.header("Progress", "the measurements",
                    "Checkboxes measure coverage. Exercises, quizzes and "
                    "reviews measure whether it stuck. Both are here.")

        tiles = QHBoxLayout()
        tiles.setSpacing(12)
        self.tile_percent = StatTile("0%", "Curriculum")
        self.tile_exercises = StatTile("0", "Exercises passed")
        self.tile_projects = StatTile("0", "Projects shipped")
        self.tile_retention = StatTile("-", "Review accuracy")
        for tile in (self.tile_percent, self.tile_exercises,
                     self.tile_projects, self.tile_retention):
            tiles.addWidget(tile)
        self.scroller.add_layout(tiles)

        activity_card = Card()
        activity_card.add(heading("Study activity"))
        self.activity = ActivityGrid(self.ctx.palette)
        activity_card.add(self.activity)
        self.scroller.add(activity_card)

        forecast_card = Card()
        forecast_card.add(heading("Review workload ahead"))
        self.forecast = BarChart(self.ctx.palette)
        forecast_card.add(self.forecast)
        self.forecast_caption = muted("")
        forecast_card.add(self.forecast_caption)
        self.scroller.add(forecast_card)

        phases_card = Card()
        phases_card.add(heading("Phase by phase"))
        phases_card.add(muted(
            "Click a row to open that phase, or select one and press Enter. "
            "Click a column heading, or use SORT, to put the weakest first. "
            "Hover the quiz column to see how the attempts went."))
        sort_row = QHBoxLayout()
        sort_row.setSpacing(8)
        sort_row.addWidget(muted("SORT"))
        self.sort_by = QComboBox()
        self.sort_by.addItem("Course order", 0)
        for column in range(1, len(COLUMNS)):
            self.sort_by.addItem("%s, least done first" % COLUMNS[column],
                                 column)
        self.sort_by.setAccessibleName("Sort the phase table")
        self.sort_by.currentIndexChanged.connect(self._sort_chosen)
        sort_row.addWidget(self.sort_by)
        sort_row.addStretch(1)
        phases_card.box.addLayout(sort_row)
        self._sort = (0, Qt.SortOrder.AscendingOrder)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(list(COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # The table looked like a control and was not one: rows could not be
        # selected, clicked or reached by keyboard, so the obvious way to get
        # from a bad number to the phase it came from did nothing at all. It
        # stays read-only; only opening is added.
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        self.table.cellClicked.connect(self._open_row)
        self.table.activated.connect(self._open_index)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(COLUMNS)):
            header.setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents)
        # The heading pressed and highlighted under the mouse and did
        # nothing. It now sorts, by number, and says which way.
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        header.sectionClicked.connect(self._header_clicked)
        phases_card.add(self.table)
        self.scroller.add(phases_card)

        skills_card = Card()
        skills_card.add(heading("Self-assessment"))
        skills_card.add(muted(
            "Rate yourself honestly. The gap between this and your exercise "
            "results is the most useful signal in the app."))
        self.skills = QVBoxLayout()
        self.skills.setSpacing(8)
        skills_card.box.addLayout(self.skills)
        self.scroller.add(skills_card)
        self.scroller.add_stretch()

    def refresh(self) -> None:
        # The heatmap and the forecast are anchored to today, so a new day
        # redraws even when nothing was written.
        from datetime import date
        today = date.today().isoformat()
        if self.store_unchanged(today):
            return
        self._draw()
        self.mark_drawn(today)

    def _draw(self) -> None:
        overview = self.ctx.progress.overview()
        correct, total = self.ctx.store.review_accuracy(30)
        self.tile_percent.set_value("%d%%" % overview.percent)
        self.tile_exercises.set_value(
            "%d/%d" % (overview.exercises_done, overview.exercises_total))
        self.tile_projects.set_value(
            "%d/%d" % (overview.projects_shipped, overview.projects_total))
        self.tile_retention.set_value(
            "%d%%" % round(correct / total * 100) if total else "-")

        self.activity.set_data(self.ctx.store.activity(370))

        forecast = self.ctx.store.forecast(21)
        labels = ["" for _ in forecast]
        labels[0] = "today"
        if len(labels) > 7:
            labels[7] = "+1w"
        if len(labels) > 14:
            labels[14] = "+2w"
        self.forecast.set_data(forecast, labels)
        self.forecast_caption.setText(
            "%d cards due over the next three weeks, peaking at %d in one day."
            % (sum(forecast), max(forecast) if forecast else 0))

        self._fill_table()
        self._fill_skills()
        self._size_table()

    def _fill_table(self) -> None:
        stats = self.ctx.progress.all_phases()
        plan = self.ctx.progress.active_phase_ids()
        # Rows are placed by position, so sorting waits until they are in.
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for order, pid in enumerate(plan):
            phase = self.ctx.curriculum.phase(pid)
            row_stats = stats.get(pid)
            if phase is None or row_stats is None or not row_stats.total:
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            has_quiz = bool(self.ctx.curriculum.quizzes_for(pid))
            numbers = [
                float(order),
                _ratio(row_stats.done, row_stats.total),
                _ratio(row_stats.exercises_done, row_stats.exercises_total),
                float(row_stats.quiz_best) if has_quiz else -1.0,
                _ratio(row_stats.gate_done, row_stats.gate_total),
                _ratio(row_stats.projects_shipped, row_stats.projects_total),
            ]
            cells = [
                "%s  %s" % (phase.num, phase.name),
                "%d/%d" % (row_stats.done, row_stats.total),
                ("%d/%d" % (row_stats.exercises_done,
                            row_stats.exercises_total)
                 if row_stats.exercises_total else "-"),
                ("%d%%" % round(row_stats.quiz_best * 100)
                 if has_quiz else "-"),
                ("%d/%d" % (row_stats.gate_done, row_stats.gate_total)
                 if row_stats.gate_total else "-"),
                ("%d/%d" % (row_stats.projects_shipped,
                            row_stats.projects_total)
                 if row_stats.projects_total else "-"),
            ]
            opens = "Open phase %s - %s" % (phase.num, phase.name)
            trend = self._quiz_trend(pid)
            for column, text in enumerate(cells):
                item = _SortItem(text)
                item.setData(Qt.ItemDataRole.UserRole, pid)
                item.setData(SORT_ROLE, numbers[column])
                item.setToolTip(trend if column == 3 else opens)
                if column:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, item)
        self._apply_sort()

    # -- sorting -----------------------------------------------------------

    def _apply_sort(self) -> None:
        column, order = self._sort
        self.table.sortItems(column, order)
        self.table.horizontalHeader().setSortIndicator(column, order)

    def sort_by_column(self, column: int, order=None) -> None:
        """Sort the table by one column; ascending puts the weakest first."""
        if not 0 <= column < len(COLUMNS):
            return
        if order is None:
            order = Qt.SortOrder.AscendingOrder
        self._sort = (column, order)
        self._apply_sort()
        index = self.sort_by.findData(column)
        if index >= 0 and self.sort_by.currentIndex() != index:
            blocked = self.sort_by.blockSignals(True)
            self.sort_by.setCurrentIndex(index)
            self.sort_by.blockSignals(blocked)

    def _header_clicked(self, column: int) -> None:
        """A second click on the same heading turns the order round."""
        current, order = self._sort
        if column == current:
            order = (Qt.SortOrder.DescendingOrder
                     if order == Qt.SortOrder.AscendingOrder
                     else Qt.SortOrder.AscendingOrder)
        else:
            order = Qt.SortOrder.AscendingOrder
        self.sort_by_column(column, order)

    def _sort_chosen(self, _index: int) -> None:
        column = self.sort_by.currentData()
        self.sort_by_column(int(column or 0))

    def save_state(self):
        column, order = self._sort
        return {"column": column,
                "descending": order == Qt.SortOrder.DescendingOrder}

    def restore_state(self, state) -> None:
        order = (Qt.SortOrder.DescendingOrder if state.get("descending")
                 else Qt.SortOrder.AscendingOrder)
        self.sort_by_column(int(state.get("column", 0)), order)

    def _quiz_trend(self, phase_id: str) -> str:
        """How this phase's quiz attempts went, oldest of the last few first.

        One best score says where the learner ended up; three in a row say
        whether it is moving, which is the thing worth knowing.
        """
        quizzes = self.ctx.curriculum.quizzes_for(phase_id)
        if not quizzes:
            return "No quiz in this phase."
        lines = []
        for quiz in quizzes:
            attempts = self.ctx.store.quiz_attempts(quiz.id, limit=3)
            # Three sittings in one session share a timestamp to the second,
            # so the query's order is not the order they happened in; the
            # row id is. Oldest first, because that is the story.
            attempts.sort(key=lambda row: (row["finished_at"], row["id"]))
            scores = ["%d%%" % round(row["score"] / row["total"] * 100)
                      for row in attempts if row["total"]]
            lines.append("%s: %s" % (
                quiz.name, " -> ".join(scores) if scores
                else "not attempted yet"))
        return "\n".join(lines)

    # -- opening a row -----------------------------------------------------

    def _open_row(self, row: int, _column: int = 0) -> None:
        item = self.table.item(row, 0)
        if item is None:
            return
        phase_id = item.data(Qt.ItemDataRole.UserRole)
        if phase_id:
            self.ctx.navigate.emit("phase", str(phase_id))

    def _open_index(self, index) -> None:
        """Enter on the selected row does what a click does."""
        if index.isValid():
            self._open_row(index.row())

    def _size_table(self) -> None:
        """Let the page scroll rather than the table."""
        height = self.table.horizontalHeader().height() + 4
        for row in range(self.table.rowCount()):
            height += self.table.rowHeight(row)
        self.table.setFixedHeight(height)
        # The name column stretches, and below the widest name it would
        # elide; the table asks for at least that much and the page scrolls
        # sideways instead (only ever at a large text size in a small window).
        metrics = self.table.fontMetrics()
        widest = max((metrics.horizontalAdvance(self.table.item(row, 0).text())
                      for row in range(self.table.rowCount())), default=0)
        header = self.table.horizontalHeader()
        others = sum(header.sectionSize(column)
                     for column in range(1, self.table.columnCount()))
        self.table.setMinimumWidth(
            widest + 28 + others + 2 * self.table.frameWidth())

    def _fill_skills(self) -> None:
        clear_layout(self.skills)
        for entry in self.ctx.curriculum.matrix:
            row = QHBoxLayout()
            row.setSpacing(8)
            name = label(entry.skill, wrap=False)
            name.setMinimumWidth(150)
            name.setStyleSheet("font-weight: 600; font-size: 12.5px;")
            row.addWidget(name)
            row.addWidget(muted(entry.covers), 1)
            picker = QComboBox()
            picker.addItems(CONFIDENCE)
            picker.setCurrentIndex(self.ctx.store.rating(entry.skill))
            picker.setMinimumWidth(160)
            picker.currentIndexChanged.connect(
                lambda value, s=entry.skill: self._rate(s, value))
            picker.setToolTip("Proof it: " + entry.proof)
            row.addWidget(picker)
            self.skills.addLayout(row)

    def _rate(self, skill: str, value: int) -> None:
        self.ctx.set_rating(skill, value)

    def on_theme(self) -> None:
        if not self._built:
            return
        self.activity.set_theme(self.ctx.palette)
        self.forecast.set_theme(self.ctx.palette)

