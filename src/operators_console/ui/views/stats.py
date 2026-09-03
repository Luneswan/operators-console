"""Progress: the numbers, honestly, including the ones that are not flattering."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem,
    QVBoxLayout,
)

from ..widgets.charts import ActivityGrid, BarChart
from ..widgets.common import (
    Card, StatTile, heading, label, muted,
)
from .base import View

CONFIDENCE = ("Never touched", "Read about it", "Followed a tutorial",
              "Built with it", "Could teach it")


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
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Phase", "Checks", "Exercises", "Quiz", "Gate", "Projects"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, 6):
            header.setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents)
        phases_card.add(self.table)
        self.scroller.add(phases_card)

        skills_card = Card()
        skills_card.add(heading("Self-assessment"))
        skills_card.add(muted(
            "Rate yourself honestly. The gap between this and your exercise "
            "results is the most useful signal in the app."))
        self.skills = QVBoxLayout()
        self.skills.setSpacing(7)
        skills_card.box.addLayout(self.skills)
        self.scroller.add(skills_card)
        self.scroller.add_stretch()

    def refresh(self) -> None:
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
        self.table.setRowCount(0)
        for pid in plan:
            phase = self.ctx.curriculum.phase(pid)
            row_stats = stats.get(pid)
            if phase is None or row_stats is None or not row_stats.total:
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            cells = [
                "%s  %s" % (phase.num, phase.name),
                "%d/%d" % (row_stats.done, row_stats.total),
                ("%d/%d" % (row_stats.exercises_done,
                            row_stats.exercises_total)
                 if row_stats.exercises_total else "-"),
                ("%d%%" % round(row_stats.quiz_best * 100)
                 if self.ctx.curriculum.quizzes_for(pid) else "-"),
                ("%d/%d" % (row_stats.gate_done, row_stats.gate_total)
                 if row_stats.gate_total else "-"),
                ("%d/%d" % (row_stats.projects_shipped,
                            row_stats.projects_total)
                 if row_stats.projects_total else "-"),
            ]
            for column, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, item)

    def _size_table(self) -> None:
        """Let the page scroll rather than the table."""
        height = self.table.horizontalHeader().height() + 4
        for row in range(self.table.rowCount()):
            height += self.table.rowHeight(row)
        self.table.setFixedHeight(height)

    def _fill_skills(self) -> None:
        _empty(self.skills)
        for entry in self.ctx.curriculum.matrix:
            row = QHBoxLayout()
            row.setSpacing(9)
            name = label(entry.skill, wrap=False)
            name.setFixedWidth(150)
            name.setStyleSheet("font-weight: 600; font-size: 12.5px;")
            row.addWidget(name)
            row.addWidget(muted(entry.covers), 1)
            picker = QComboBox()
            picker.addItems(CONFIDENCE)
            picker.setCurrentIndex(self.ctx.store.rating(entry.skill))
            picker.setFixedWidth(160)
            picker.currentIndexChanged.connect(
                lambda value, s=entry.skill: self._rate(s, value))
            picker.setToolTip("Proof it: " + entry.proof)
            row.addWidget(picker)
            self.skills.addLayout(row)

    def _rate(self, skill: str, value: int) -> None:
        self.ctx.store.set_rating(skill, value)

    def on_theme(self) -> None:
        if not self._built:
            return
        self.activity.set_theme(self.ctx.palette)
        self.forecast.set_theme(self.ctx.palette)


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
