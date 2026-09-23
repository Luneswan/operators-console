"""Every keyboard shortcut, in one window (Help > Keyboard shortcuts, F1).

The menu part is read from the window's own actions, so the list cannot
drift from what is actually bound. The editor's keys live in its
keyPressEvent rather than in actions, so they are listed here by hand.
"""
from __future__ import annotations

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QVBoxLayout

from .widgets.common import button, label, muted

EDITOR_SHORTCUTS = (
    ("Ctrl+Enter", "Run the checks"),
    ("Ctrl+/", "Comment or uncomment the selected lines"),
    ("Tab, Shift+Tab", "Indent or outdent the selected lines"),
    ("Ctrl+Z", "Undo in the editor - Reset included"),
)

# Review's keys live in ReviewView.keyPressEvent rather than in actions, for
# the same reason the editor's do: they are page keys, not application ones.
REVIEW_SHORTCUTS = (
    ("Space, Enter", "Reveal the line, or check the option you picked"),
    ("A, B, C, D", "Pick that multiple-choice option"),
    ("1, 2, 3, 4", "Again, Hard, Good, Easy - once the answer is showing"),
    ("S", "Skip this card. Skipped twice, it moves to tomorrow"),
    ("Ctrl+Z", "Undo the answer you just gave"),
)


def menu_shortcuts(window) -> list:
    """(keys, what they do) for every menu action that has a shortcut."""
    rows = []
    for top in window.menuBar().actions():
        menu = top.menu()
        if menu is None:
            continue
        section = top.text().replace("&", "")
        for action in menu.actions():
            keys = []
            for key in action.shortcuts():      # Redo's standard keys repeat
                text = key.toString(QKeySequence.SequenceFormat.NativeText)
                if text and text not in keys:
                    keys.append(text)
            if keys:
                rows.append(("  or  ".join(keys), "%s: %s" % (
                    section, action.text().replace("&", "").rstrip("."))))
    return rows


class ShortcutsDialog(QDialog):
    def __init__(self, window) -> None:
        super().__init__(window)
        self.setWindowTitle("Keyboard shortcuts")
        self.setModal(True)
        self.setMinimumWidth(480)
        column = QVBoxLayout(self)
        column.setContentsMargins(26, 22, 26, 20)
        column.setSpacing(12)
        column.addWidget(label("Keyboard shortcuts", "PageTitle"))

        self.rows = menu_shortcuts(window)
        # One grid for both sections, so the descriptions share one column.
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)
        line = 0
        for title, rows in (("Anywhere", self.rows),
                            ("In review", REVIEW_SHORTCUTS),
                            ("In the code editor", EDITOR_SHORTCUTS)):
            heading = label(title, "SectionTitle", wrap=False)
            if line:
                heading.setContentsMargins(0, 10, 0, 0)
            grid.addWidget(heading, line, 0, 1, 2)
            line += 1
            for keys, meaning in rows:
                grid.addWidget(label(keys, "Mono", wrap=False), line, 0)
                grid.addWidget(label(meaning, wrap=True), line, 1)
                line += 1
        column.addLayout(grid)
        column.addWidget(muted(
            "Ctrl+K searches phases, exercises, projects, the library, your "
            "notes and your log. Arrow keys move through results. Enter opens "
            "one."))

        row = QHBoxLayout()
        row.addStretch(1)
        close = button("Close", "primary")
        close.clicked.connect(self.accept)
        row.addWidget(close)
        column.addLayout(row)
