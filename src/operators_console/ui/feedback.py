"""The report and request form: fill it in here, submit it on GitHub."""
from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QGridLayout, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QVBoxLayout,
)

from ..core import feedback
from .widgets.common import button, label, muted, open_url


class FeedbackDialog(QDialog):
    def __init__(self, ctx, parent=None, kind: str = "bug") -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("Report a problem or request a feature")
        self.setMinimumWidth(560)
        column = QVBoxLayout(self)
        column.setContentsMargins(24, 20, 24, 18)
        column.setSpacing(10)

        column.addWidget(label("Report or request", "PageTitle"))
        column.addWidget(muted(
            "This opens GitHub's new-issue page with your text filled in. "
            "You submit it from your GitHub account. Nothing is sent from "
            "the app. Without an account, copy the text and email or share "
            "it instead."))

        grid = QGridLayout()
        grid.setSpacing(8)
        self.kind = QComboBox()
        for kid, text, _label, _prefix in feedback.KINDS:
            self.kind.addItem(text, kid)
        self.kind.setCurrentIndex(max(0, self.kind.findData(kind)))
        self.kind.setAccessibleName("Kind of report")
        self.kind.currentIndexChanged.connect(lambda _i: self._sync())
        grid.addWidget(muted("TYPE"), 0, 0)
        grid.addWidget(self.kind, 0, 1)
        self.title = QLineEdit()
        self.title.setPlaceholderText("One line, for example: Quiz timer does not stop")
        self.title.setAccessibleName("Title")
        grid.addWidget(muted("TITLE"), 1, 0)
        grid.addWidget(self.title, 1, 1)
        column.addLayout(grid)

        self.details_label = muted("")
        column.addWidget(self.details_label)
        self.details = QPlainTextEdit()
        self.details.setAccessibleName("Details")
        self.details.setMinimumHeight(110)
        column.addWidget(self.details)
        self.steps_label = muted("Steps to reproduce (optional)")
        column.addWidget(self.steps_label)
        self.steps = QPlainTextEdit()
        self.steps.setAccessibleName("Steps to reproduce")
        self.steps.setPlaceholderText("1. Open ...\n2. Click ...\n3. See ...")
        self.steps.setMaximumHeight(90)
        column.addWidget(self.steps)

        self.include = QCheckBox("Include app version and operating system")
        self.include.setChecked(True)
        column.addWidget(self.include)
        column.addWidget(muted(feedback.system_details().replace("\n", "  -  ")))

        self.status = muted("")
        self.status.setVisible(False)
        column.addWidget(self.status)

        row = QHBoxLayout()
        row.setSpacing(8)
        copy = button("Copy text", "quiet")
        copy.clicked.connect(self._copy)
        row.addWidget(copy)
        row.addStretch(1)
        cancel = button("Cancel", "quiet")
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)
        self.open_button = button("Open on GitHub", "primary")
        self.open_button.clicked.connect(self._open)
        row.addWidget(self.open_button)
        column.addLayout(row)
        self._sync()

    def _sync(self) -> None:
        bug = self.kind.currentData() == "bug"
        self.details_label.setText("What happened, and what you expected"
                                   if bug else "Details")
        self.steps_label.setVisible(bug)
        self.steps.setVisible(bug)

    def _text(self):
        return feedback.issue_text(
            self.kind.currentData(), self.title.text(),
            self.details.toPlainText(), self.include.isChecked(),
            self.steps.toPlainText())

    def _say(self, text: str) -> None:
        self.status.setText(text)
        self.status.setVisible(True)

    def _copy(self) -> None:
        try:
            title, body = self._text()
        except ValueError as exc:
            self._say(str(exc))
            return
        QGuiApplication.clipboard().setText("%s\n\n%s" % (title, body))
        self._say("Copied to the clipboard.")

    def _open(self) -> None:
        try:
            title, body = self._text()
        except ValueError as exc:
            self._say(str(exc))
            return
        url, complete = feedback.issue_url(self.kind.currentData(), title, body)
        if not complete:
            QGuiApplication.clipboard().setText(body)
        open_url(url)
        self.ctx.announce("Opened GitHub. Submit the issue there."
                          if complete else
                          "Opened GitHub. The text was long: paste the rest "
                          "from the clipboard.")
        self.accept()
