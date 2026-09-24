"""The career ladder: the level reached, and what the next one asks for."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ...core.progress import LEVELS
from .common import Card, label, meter, muted, pill

#: What each rung asks for, in the words shown on the Progress page.
RULES = (
    "Where everyone starts.",
    "Prove your first language phase.",
    "Prove Python foundations, engineering, and packaging.",
    "Prove half of the core phases in your plan.",
    "Prove every core phase in your plan.",
    "Also prove a mastery phase: architecture, beyond senior, or the "
    "final-boss ladder.",
)


class CareerCard(Card):
    """Today's summary: level, a bar to the next one, and the next proofs."""

    def __init__(self, parent=None) -> None:
        super().__init__(padding=14, spacing=6, parent=parent)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(muted("LEVEL"))
        self.level = pill("", "accent")
        top.addWidget(self.level)
        self.next = label("", "Soft")
        top.addWidget(self.next, 1)
        self.box.addLayout(top)
        self.bar = meter(0, 100)
        self.box.addWidget(self.bar)
        self.needs = muted("")
        self.box.addWidget(self.needs)

    def show_career(self, career) -> None:
        self.level.setText(career.name.upper())
        if career.top:
            self.next.setText("The top of the ladder. Keep your reviews up.")
            self.bar.setValue(100)
            self.needs.setVisible(False)
            return
        self.next.setText("Next: %s - %d%% of the way"
                          % (career.next_name, round(career.fraction * 100)))
        self.bar.setValue(round(career.fraction * 100))
        self.needs.setText("To get there, prove: %s." % ", ".join(career.needs)
                           if career.needs else "")
        self.needs.setVisible(bool(career.needs))


class Ladder(QWidget):
    """Every rung, with the reached ones marked."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(0, 0, 0, 0)
        self.column.setSpacing(6)
        self.rows = []
        for index, name in enumerate(LEVELS):
            row = QHBoxLayout()
            row.setSpacing(10)
            mark = pill("", "")
            mark.setMinimumWidth(92)
            row.addWidget(mark)
            text = label("%s. %s" % (name, RULES[index]), "Soft")
            row.addWidget(text, 1)
            self.column.addLayout(row)
            self.rows.append((mark, text))

    def show_career(self, career) -> None:
        from .common import repolish
        for index, (mark, _text) in enumerate(self.rows):
            if index < career.level:
                mark.setText("REACHED")
                mark.setProperty("tone", "done")
            elif index == career.level:
                mark.setText("YOU ARE HERE")
                mark.setProperty("tone", "accent")
            else:
                mark.setText("AHEAD")
                mark.setProperty("tone", "")
            repolish(mark)
        # One width for every mark, so the rule texts start in one column
        # whatever the widest mark says.
        width = max(mark.sizeHint().width() for mark, _text in self.rows)
        for mark, _text in self.rows:
            mark.setFixedWidth(width)
