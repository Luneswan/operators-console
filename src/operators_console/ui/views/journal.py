"""The log: what you did, what broke, what is next."""
from __future__ import annotations


from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QVBoxLayout,
)

from ..widgets.common import (
    Card, StatTile, button, divider, heading, label, muted, pill,
)
from .base import View


class JournalView(View):
    title = "Log"

    def build(self) -> None:
        self.header("Log", "one entry a day",
                    "The entry takes a minute and makes tomorrow start faster. "
                    "Hours recorded here feed the pace estimate on Today.")

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.tile_hours = StatTile("0", "Hours logged")
        self.tile_entries = StatTile("0", "Entries")
        self.tile_streak = StatTile("0", "Day streak")
        self.tile_best = StatTile("0", "Longest streak")
        for tile in (self.tile_hours, self.tile_entries, self.tile_streak,
                     self.tile_best):
            stats_row.addWidget(tile)
        self.scroller.add_layout(stats_row)

        form = Card()
        form.add(heading("Add an entry"))
        grid = QGridLayout()
        grid.setSpacing(8)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        grid.addWidget(muted("DATE"), 0, 0)
        grid.addWidget(self.date, 0, 1)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.0, 24.0)
        self.hours.setSingleStep(0.5)
        self.hours.setValue(float(self.ctx.store.setting("hours_per_day", 3.0)))
        self.hours.setSuffix(" h")
        grid.addWidget(muted("HOURS"), 0, 2)
        grid.addWidget(self.hours, 0, 3)
        self.focus = QLineEdit()
        self.focus.setPlaceholderText("What was today about?")
        grid.addWidget(muted("FOCUS"), 1, 0)
        grid.addWidget(self.focus, 1, 1, 1, 3)
        form.box.addLayout(grid)

        self.built = QPlainTextEdit()
        self.built.setPlaceholderText("What did you build or fix?")
        self.built.setFixedHeight(60)
        form.add(self.built)
        self.stuck = QPlainTextEdit()
        self.stuck.setPlaceholderText("Where did you get stuck, and why?")
        self.stuck.setFixedHeight(60)
        form.add(self.stuck)
        self.next_up = QLineEdit()
        self.next_up.setPlaceholderText("First thing tomorrow")
        form.add(self.next_up)

        save = button("Save entry", "primary")
        save.clicked.connect(self._save)
        form.add_row(None, save)
        self.scroller.add(form)

        self.scroller.add(divider())
        self.scroller.add(heading("History"))
        self.history = QVBoxLayout()
        self.history.setSpacing(9)
        self.scroller.add_layout(self.history)
        self.scroller.add_stretch()

    def refresh(self) -> None:
        store = self.ctx.store
        current, longest = store.streak()
        logs = store.logs()
        self.tile_hours.set_value("%.0f" % store.total_hours())
        self.tile_entries.set_value(str(len(logs)))
        self.tile_streak.set_value(str(current))
        self.tile_best.set_value(str(longest))
        self._fill_history(logs)

    def _fill_history(self, logs) -> None:
        _empty(self.history)
        if not logs:
            card = Card()
            card.add(muted("No entries yet. The first one is the hardest."))
            self.history.addWidget(card)
            return
        for row in logs[:60]:
            card = Card(padding=12, spacing=5)
            top = QHBoxLayout()
            top.setSpacing(8)
            top.addWidget(pill(row["day"]))
            focus = label(row["focus"] or "(no focus recorded)", wrap=True)
            focus.setStyleSheet("font-weight: 600;")
            top.addWidget(focus, 1)
            top.addWidget(muted("%.1f h" % row["hours"]))
            delete = button("Delete", "quiet")
            delete.clicked.connect(
                lambda _=False, i=row["id"]: self._delete(i))
            top.addWidget(delete)
            card.box.addLayout(top)
            if row["built"]:
                card.add(label("Built: " + row["built"], "Soft"))
            if row["stuck"]:
                card.add(label("Stuck: " + row["stuck"], "Soft"))
            if row["next_up"]:
                card.add(muted("Next: " + row["next_up"]))
            self.history.addWidget(card)

    def _save(self) -> None:
        day = self.date.date().toString("yyyy-MM-dd")
        self.ctx.store.add_log(
            day, self.focus.text().strip(), self.hours.value(),
            self.built.toPlainText().strip(), self.stuck.toPlainText().strip(),
            self.next_up.text().strip())
        self.focus.clear()
        self.built.clear()
        self.stuck.clear()
        self.next_up.clear()
        self.ctx.changed()
        self.ctx.announce("Logged.")
        self.refresh()

    def _delete(self, log_id: int) -> None:
        self.ctx.store.delete_log(log_id)
        self.ctx.changed()
        self.refresh()


def _empty(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _empty(item.layout())
