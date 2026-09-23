"""The window: navigation, search, status and the stack of pages."""
from __future__ import annotations

import time

from PySide6.QtCore import (
    QByteArray, QCoreApplication, QEvent, QSize, Qt, QTimer,
)
from PySide6.QtGui import (
    QAccessible, QAccessibleEvent, QAction, QKeySequence,
)
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QScrollArea, QStackedWidget, QStatusBar,
    QVBoxLayout, QWidget,
)

from ..version import APP_NAME, __version__
from .context import AppContext
from .theme import apply_qpalette, base_font, stylesheet
from .updater import UpdateButton, UpdateManager
from .views.dashboard import DashboardView
from .views.journal import JournalView
from .views.library import LibraryView
from .views.phase import PhaseView
from .views.practice import PracticeView
from .views.projects import ProjectsView
from .views.quiz import QuizView
from .views.review import ReviewView
from .views.roadmap import RoadmapView
from .views.settings import SettingsView
from .views.stats import StatsView
from .focus import install as install_focus
from .views.base import store_key
from .widgets.common import Card, ElidedLabel, divider, label, muted, pill

NAV = (
    ("today", "Today", DashboardView),
    ("roadmap", "Roadmap", RoadmapView),
    ("phase", "Phase", PhaseView),
    ("practice", "Practice", PracticeView),
    ("quiz", "Quizzes", QuizView),
    ("review", "Review", ReviewView),
    ("projects", "Projects", ProjectsView),
    ("journal", "Log", JournalView),
    ("stats", "Progress", StatsView),
    ("library", "Library", LibraryView),
    ("settings", "Settings", SettingsView),
)

# Where the learner was when an update restarted the app. Read once, then
# cleared; ignored if the restart never came (a stale note must not hijack
# an ordinary launch days later).
# The sidebar's sections, keyed by the item that opens each one.
NAV_SECTIONS = {"today": "Learn", "practice": "Practise", "journal": "Track",
                "library": "More"}

RESUME_SETTING = "resume_after_update"
GEOMETRY_SETTING = "window_geometry"
SIDEBAR_WIDTH = 212
RESUME_WITHIN_SECONDS = 15 * 60

# Said once, to the learner who has never opened the Help menu.
GUIDE_SETTING = "guide_pointed"
GUIDE_HINT = "New here? Help > How this app works explains every page"


def announce(widget) -> None:
    """Tell a screen reader that this widget has something to say.

    The status bar is the whole of the app's feedback: everything from
    "Snapshot saved" to "The update did not install" lands there and
    nowhere else. A label quietly changing its text is not an event any
    reader announces, so one is posted by hand.
    """
    try:
        QAccessible.updateAccessibility(
            QAccessibleEvent(widget, QAccessible.Event.Alert))
    except Exception:
        pass        # a platform without accessibility must not break a toast


def _clip(text: str, limit: int) -> str:
    """A query short enough to quote back on one line."""
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def _redo_keys() -> list:
    """Every redo key this platform knows, plus Ctrl+Shift+Z and Ctrl+Y.

    ``setShortcuts([StandardKey.Redo, "Ctrl+Y"])`` turned the standard key
    into its first binding alone - Ctrl+Y on Windows - so the action held
    the same key twice, Qt reported an ambiguous overload, and neither the
    key the Redo button advertises nor Ctrl+Y did anything.
    """
    keys = list(QKeySequence.keyBindings(QKeySequence.StandardKey.Redo))
    keys += [QKeySequence("Ctrl+Shift+Z"), QKeySequence("Ctrl+Y")]
    out, seen = [], set()
    for key in keys:
        text = key.toString()
        if text and text not in seen:
            seen.add(text)
            out.append(key)
    return out


class QuestionDialog(QDialog):
    """One review question, its answer and its explanation, to read.

    Searching for a question used to start a whole quiz attempt: eight more
    questions nobody asked for, and a wrong answer scheduled against a deck
    the learner was only looking something up in. Reading is not answering,
    so this shows the question and changes nothing.
    """

    def __init__(self, parent, question, quiz=None) -> None:
        # Local, so the window's own `for key, button in ...` loops cannot
        # shadow the factory at module level.
        from .widgets.common import button
        super().__init__(parent)
        self.question = question
        self.setWindowTitle("Question")
        self.setModal(True)
        self.setMinimumWidth(520)
        column = QVBoxLayout(self)
        column.setContentsMargins(26, 22, 26, 20)
        column.setSpacing(12)

        if quiz is not None:
            column.addWidget(label(quiz.name.upper(), "PageKicker", wrap=False))
        column.addWidget(label(question.prompt, "PageTitle"))
        column.addWidget(divider())

        card = Card()
        for index, choice in enumerate(question.choices):
            right = index == question.correct
            row = card.add_row(label(choice, "Soft"), None)
            if right:
                row.addWidget(pill("THE ANSWER", "done"))
        column.addWidget(card)
        if question.explain:
            column.addWidget(label(question.explain, "Soft"))
        column.addWidget(muted(
            "Reading this changes nothing. Answer it for real from Quizzes "
            "or Review."))

        row = QHBoxLayout()
        row.addStretch(1)
        self.close_button = button("Close", "primary")
        self.close_button.clicked.connect(self.accept)
        row.addWidget(self.close_button)
        column.addLayout(row)
        self.close_button.setDefault(True)


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle(APP_NAME)
        self.resize(1220, 840)
        self.setMinimumSize(QSize(940, 620))
        self._restore_geometry()

        central = QWidget()
        row = QHBoxLayout(central)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.setCentralWidget(central)

        self.sidebar = self._build_sidebar()
        row.addWidget(self.sidebar)

        right = QWidget()
        right_column = QVBoxLayout(right)
        right_column.setContentsMargins(0, 0, 0, 0)
        right_column.setSpacing(0)
        right_column.addWidget(self._build_searchbar())
        self.stack = QStackedWidget()
        right_column.addWidget(self.stack, 1)
        row.addWidget(right, 1)

        self.views = {}
        for key, _text, factory in NAV:
            view = factory(ctx)
            self.views[key] = view
            self.stack.addWidget(view)

        self.setStatusBar(QStatusBar())
        # A long message must never widen the window: the label cuts it
        # with an ellipsis and keeps the whole of it in its tooltip.
        self.status_label = ElidedLabel("")
        self.statusBar().addWidget(self.status_label, 1)
        self.status_right = QLabel("")
        self.statusBar().addPermanentWidget(self.status_right)

        self.updates = UpdateManager(ctx, self)
        self.updates.available.connect(self._on_update_available)

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._clear_toast)

        self._build_menu()
        # A ring belongs to the keyboard; a click must not leave one.
        from PySide6.QtWidgets import QApplication
        install_focus(QApplication.instance()).watch(self)
        ctx.navigate.connect(self.go)
        ctx.history_changed.connect(self._refresh_history_buttons)
        ctx.progress_changed.connect(self._on_progress)
        ctx.theme_changed.connect(self.apply_theme)
        ctx.toast.connect(self.toast)

        self.current_key = ""
        self._refresh_history_buttons()
        self.go("today", "")
        self._resume_after_update()
        self.apply_theme()
        # Nothing in the app ever pointed at the guide. The first launch
        # does, once, and then never again.
        self._point_at_guide()
        # Held rather than fired and forgotten, so closing the window in the
        # first few seconds does not leave a timer reaching into a shut store.
        self._first_check = QTimer(self)
        self._first_check.setSingleShot(True)
        self._first_check.setInterval(2500)
        # An update that did not install reopened this, the old version. Say
        # why, and look again today rather than tomorrow so the button can
        # come back.
        from ..core import updates as update_core
        failure = update_core.take_failure()
        if failure:
            QTimer.singleShot(0, lambda: self.toast(
                "The update did not install: %s." % failure))
        self._first_check.timeout.connect(
            lambda: self.updates.maybe_check(force=bool(failure)))
        self._first_check.start()

    # -- chrome ------------------------------------------------------------

    def _build_sidebar(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("Sidebar")
        panel.setFixedWidth(SIDEBAR_WIDTH)
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        # It scrolls when it runs out of height - a 640-pixel window, larger
        # text, or an update note - instead of squeezing the title and
        # stacking the update button on top of its own note.
        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        body = QWidget()
        body.setObjectName("SidebarBody")
        scroll.setWidget(body)
        outer.addWidget(scroll)
        column = QVBoxLayout(body)
        column.setContentsMargins(10, 0, 10, 8)
        column.setSpacing(0)

        brand = QHBoxLayout()
        brand.setContentsMargins(8, 18, 8, 14)
        brand.setSpacing(10)
        self.mark = QLabel()
        self.mark.setFixedSize(24, 24)
        brand.addWidget(self.mark, 0, Qt.AlignmentFlag.AlignTop)
        words = QVBoxLayout()
        words.setSpacing(0)
        title = QLabel("Operator's Console")
        title.setObjectName("SidebarTitle")
        words.addWidget(title)
        subtitle = QLabel("Python curriculum")
        subtitle.setObjectName("SidebarSubtitle")
        words.addWidget(subtitle)
        brand.addLayout(words, 1)
        column.addLayout(brand)

        self.nav_buttons = {}
        for key, text, _factory in NAV:
            section = NAV_SECTIONS.get(key)
            if section:
                caption = QLabel(section.upper())
                caption.setObjectName("NavSection")
                column.addWidget(caption)
            button = QPushButton(text)
            button.setProperty("nav", True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            # Tab reaches it; a click does not leave it looking selected.
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            button.setIconSize(QSize(16, 16))
            button.clicked.connect(lambda _=False, k=key: self.go(k, ""))
            column.addWidget(button)
            self.nav_buttons[key] = button
        self._refresh_nav_icons()

        column.addStretch(1)
        # The update offer lives where the eye already rests between pages,
        # not in a dialog that interrupts.
        self.update_button = UpdateButton(self.ctx, panel)
        holder = QWidget(panel)
        holder_row = QVBoxLayout(holder)
        holder_row.setContentsMargins(6, 4, 6, 8)
        holder_row.setSpacing(8)
        holder_row.addWidget(self.update_button)
        self.update_note = muted("")
        self.update_note.setVisible(False)
        holder_row.addWidget(self.update_note)
        self.update_button.set_note_target(self.update_note)
        column.addWidget(holder)
        self.sidebar_footer = QLabel("")
        self.sidebar_footer.setObjectName("SidebarSubtitle")
        self.sidebar_footer.setWordWrap(True)
        column.addWidget(self.sidebar_footer)
        return panel

    def _refresh_nav_icons(self) -> None:
        """Icons in the theme's ink; the open page's in full ink."""
        from .widgets import icons
        palette = self.ctx.palette
        ratio = self.devicePixelRatioF()
        for key, button in self.nav_buttons.items():
            active = button.property("active") is True
            colour = palette.ink if active else palette.ink_faint
            button.setIcon(icons.icon(key, colour, 16, ratio))
        self.mark.setPixmap(icons.mark(palette.accent, palette.on_accent,
                                       24, ratio))

    def _build_searchbar(self) -> QWidget:
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.setContentsMargins(24, 14, 24, 4)
        row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search the curriculum and your notes   (Ctrl+K)")
        self.search.setAccessibleName(
            "Search the curriculum and your notes")
        self.search.setClearButtonEnabled(True)
        # A field, not a bar: it stops at a comfortable reading width and
        # the rest of the row stays quiet.
        self.search.setMaximumWidth(520)
        self.search.textChanged.connect(self._on_search)
        self.search.returnPressed.connect(self._open_selected)
        # Down, Up, Enter and Escape belong to the list, which never takes
        # the focus; the field hands them over. See `_search_key`.
        self.search.installEventFilter(self)
        # Two shares of the slack to the field, one to the gap after it, so
        # a narrow window squeezes the gap before the placeholder.
        row.addWidget(self.search, 2)
        row.addStretch(1)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setProperty("kind", "quiet")
        self.undo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_button.clicked.connect(self.undo)
        row.addWidget(self.undo_button)

        self.redo_button = QPushButton("Redo")
        self.redo_button.setProperty("kind", "quiet")
        self.redo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.redo_button.clicked.connect(self.redo)
        row.addWidget(self.redo_button)

        self.breadcrumb = muted("")
        row.addWidget(self.breadcrumb)

        self.results = QListWidget(self)
        self.results.setObjectName("SearchResults")
        self.results.setWindowFlags(Qt.WindowType.Popup)
        self.results.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.results.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.results.itemActivated.connect(self._open_result)
        self.results.itemClicked.connect(self._open_result)
        self.results.hide()
        return bar

    def _build_menu(self) -> None:
        menu = self.menuBar()

        app_menu = menu.addMenu("&File")
        for text, handler, shortcut in (
                ("Export backup...", self._export, ""),
                ("Export progress report...", self._report, ""),
                ("Take a snapshot", self._snapshot, ""),
                ("Restore a snapshot...", self._restore_snapshot, ""),
        ):
            action = QAction(text, self)
            action.triggered.connect(handler)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            app_menu.addAction(action)
        app_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        app_menu.addAction(quit_action)

        go_menu = menu.addMenu("&Go")
        self.go_actions = {}
        for index, (key, text, _factory) in enumerate(NAV, start=1):
            action = QAction(text, self)
            if index <= 9:
                action.setShortcut(QKeySequence("Ctrl+%d" % index))
            elif key == "library":
                # The tenth page finishes the row of digits, and the letter
                # is what anyone reaches for: L for Library.
                action.setShortcuts([QKeySequence("Ctrl+0"),
                                     QKeySequence("Ctrl+L")])
            elif key == "settings":
                action.setShortcut(QKeySequence("Ctrl+,"))
            action.triggered.connect(lambda _=False, k=key: self.go(k, ""))
            go_menu.addAction(action)
            self.go_actions[key] = action
        edit_menu = menu.addMenu("&Edit")
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        edit_menu.addAction(self.undo_action)
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcuts(_redo_keys())
        self.redo_action.triggered.connect(self.redo)
        edit_menu.addAction(self.redo_action)

        go_menu.addSeparator()
        find = QAction("Find", self)
        find.setShortcut(QKeySequence("Ctrl+K"))
        find.triggered.connect(self._focus_search)
        go_menu.addAction(find)

        help_menu = menu.addMenu("&Help")
        guide = QAction("How this app works", self)
        guide.triggered.connect(self._show_guide)
        help_menu.addAction(guide)
        keys = QAction("Keyboard shortcuts", self)
        keys.setShortcut(QKeySequence("F1"))
        keys.triggered.connect(self._show_shortcuts)
        help_menu.addAction(keys)
        check = QAction("Check for updates", self)
        check.triggered.connect(self.check_for_updates)
        help_menu.addAction(check)
        about = QAction("About", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    # -- navigation --------------------------------------------------------

    def go(self, key: str, target: str = "") -> None:
        view = self.views.get(key)
        if view is None:
            return
        view.ensure_built()
        self.stack.setCurrentWidget(view)
        for nav_key, button in self.nav_buttons.items():
            active = nav_key == key
            if button.property("active") == active:
                continue        # a re-polish costs a millisecond a button
            button.setProperty("active", active)
            button.style().unpolish(button)
            button.style().polish(button)
        self._refresh_nav_icons()
        self.current_key = key
        view.refresh()
        # Filters a theme or text-size change took down with the page come
        # back before any target, so a target can still clear them.
        view.restore_pending()
        if target:
            view.show_target(target)
        self._update_status()
        self.results.hide()

    def _on_progress(self) -> None:
        self._update_status()
        current = self.views.get(self.current_key)
        if current is not None and self.current_key in ("today", "roadmap",
                                                        "stats"):
            current.refresh()

    def _update_status(self) -> None:
        # Runs on every navigation: skipped while the store is where it was
        # (and within the same ten minutes, since cards fall due with time).
        key = store_key(self.ctx.store, int(time.time() // 600))
        if getattr(self, "_status_key", None) == key:
            return
        self._status_key = key
        overview = self.ctx.progress.overview()
        # One aggregate query, rather than one row read per review card: this
        # runs on every navigation and every ticked checkbox.
        due = self.ctx.store.card_counts()["due"]
        self.status_right.setText(
            "%d%% complete   -   %d due   -   %d day streak"
            % (overview.percent, due, overview.streak))
        due_button = self.nav_buttons.get("review")
        if due_button is not None:
            due_button.setText("Review" + ("  (%d)" % due if due else ""))
        phase = self.ctx.curriculum.phase(self.ctx.progress.current_phase_id())
        if phase is not None:
            self.sidebar_footer.setText(
                "Current: phase %s\n%s" % (phase.num, phase.name))

    # -- search ------------------------------------------------------------

    def _focus_search(self) -> None:
        self.search.setFocus()
        self.search.selectAll()
        # A query already in the box gets its results back: the popup is
        # otherwise driven only by the text changing, so after Escape, or a
        # trip to another page, Ctrl+K showed the old words and nothing else.
        self._on_search(self.search.text())

    def search_hits(self) -> list:
        """The hits the popup is offering, without its "no match" line."""
        out = []
        for row in range(self.results.count()):
            hit = self.results.item(row).data(Qt.ItemDataRole.UserRole)
            if hit is not None:
                out.append(hit)
        return out

    def _on_search(self, text: str) -> None:
        query = " ".join(text.split())
        if len("".join(query.split())) < 2:
            # Too short to mean anything yet: stay quiet rather than flash
            # "no match" on every first keystroke.
            self.results.hide()
            return
        hits = self.ctx.index.search(query, limit=40)
        self.results.clear()
        for hit in hits:
            # Title first, whole: it is what was searched for. The kind
            # and context follow and are elided by the list, never cut
            # mid-word by a fixed slice or padded into a crooked column.
            item = QListWidgetItem("%s   -   %s: %s" % (
                hit.title, hit.kind.capitalize(), hit.context))
            item.setToolTip("%s\n%s: %s" % (hit.title, hit.kind.capitalize(),
                                             hit.context))
            item.setData(Qt.ItemDataRole.UserRole, hit)
            self.results.addItem(item)
        if not hits:
            # Said, not implied: a hidden popup reads the same as "still
            # typing" or "too short". The row cannot be selected or opened.
            item = QListWidgetItem(
                'No match for "%s" in the curriculum or your notes.'
                % _clip(query, 60))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results.addItem(item)
        else:
            # Something is always selected, so Enter has an obvious meaning
            # and Down starts from the top rather than from nothing.
            self.results.setCurrentRow(0)
        point = self.search.mapToGlobal(self.search.rect().bottomLeft())
        # Wider than the field it hangs from: a result is a title and its
        # context, and the field is sized for a query.
        width = max(self.search.width(), min(760, self.stack.width() - 8))
        self.results.setGeometry(point.x(), point.y() + 4, width,
                                 min(420, 34 * max(1, len(hits)) + 14))
        self.results.show()

    # -- driving the popup from the field ----------------------------------

    def eventFilter(self, watched, event):
        if (watched is self.search
                and event.type() == QEvent.Type.KeyPress
                and self._search_key(event)):
            return True
        return super().eventFilter(watched, event)

    def _search_key(self, event) -> bool:
        """Down, Up, Enter and Escape, forwarded to the results list.

        The list is a popup that deliberately never takes the focus - it
        must not, or the caret would leave the query mid word - so without
        this the keyboard could only ever open the first hit. True means the
        key was handled here and the field must not see it as well.
        """
        key = event.key()
        if key == Qt.Key.Key_Escape and self.results.isVisible():
            self.results.hide()
            return True
        if not self.results.isVisible() or not self.search_hits():
            return False
        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self._move_selection(1 if key == Qt.Key.Key_Down else -1)
            return True
        if key in (Qt.Key.Key_PageDown, Qt.Key.Key_PageUp):
            self._move_selection(8 if key == Qt.Key.Key_PageDown else -8)
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._open_selected()
            return True
        return False

    def _move_selection(self, step: int) -> None:
        """Move the highlight, wrapping at both ends."""
        count = self.results.count()
        if not count:
            return
        row = self.results.currentRow()
        row = (row + step) % count if row >= 0 else (0 if step > 0
                                                     else count - 1)
        self.results.setCurrentRow(max(0, min(count - 1, row)))
        current = self.results.currentItem()
        if current is not None:
            self.results.scrollToItem(current)

    def _open_selected(self) -> None:
        """Open the highlighted hit - the first one, until Down has moved."""
        item = self.results.currentItem()
        if item is None and self.results.count():
            item = self.results.item(0)
        if item is not None:
            self._open_result(item)

    def _open_first_result(self) -> None:
        if self.results.count():
            self._open_result(self.results.item(0))

    def _open_result(self, item) -> None:
        hit = item.data(Qt.ItemDataRole.UserRole)
        if hit is None:
            return          # the "no match" line: nothing to open
        self.results.hide()
        self.search.clear()
        self._open_hit(hit)

    def _open_hit(self, hit) -> None:
        """Where each kind of hit leads.

        Every kind lands somewhere that shows the thing that was found: a
        field or a certificate on its own card in the Library rather than at
        the top of the page, a question in a dialog rather than in a fresh
        quiz attempt, and a note back on the page it was written on.
        """
        kind = hit.kind
        if kind == "exercise":
            self.go("practice", hit.target)
        elif kind == "project":
            self.go("projects", hit.target)
        elif kind == "question":
            self._show_question(hit.target)
        elif kind == "resource":
            from .widgets.common import open_url
            open_url(hit.target)
        elif kind in ("field", "cert", "shelf", "video"):
            self.go("library", hit.target)
        elif kind == "log":
            self.go("journal", "")
        elif kind == "note":
            if self.ctx.curriculum.project(hit.target) is not None:
                self.go("projects", hit.target)
            else:
                self.go("phase", hit.phase or hit.target)
        else:
            self.go("phase", hit.phase or hit.target)

    def _show_question(self, question_id: str) -> None:
        """Read a question and its explanation without starting an attempt."""
        question = self.ctx.curriculum.question(question_id)
        if question is None:
            return
        quiz = self.ctx.curriculum.quiz_of_question(question_id)
        dialog = QuestionDialog(self, question, quiz)
        try:
            dialog.exec()
        finally:
            dialog.deleteLater()

    # -- theme and chrome --------------------------------------------------

    def apply_theme(self) -> None:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        palette = self.ctx.palette
        scale = float(self.ctx.store.setting("font_scale", 1.0))
        font = base_font(scale)
        sheet = stylesheet(palette, scale)
        # The font, the palette and the sheet each propagate through every
        # live widget, at about a millisecond a widget for the sheet. Pages
        # that are not on screen give their widgets up first and rebuild on
        # the next visit; a page in the middle of something keeps them. An
        # unchanged value is not re-applied at all.
        font_changed = app.font() != font
        palette_changed = (getattr(self, "_palette_applied", None)
                           != palette.name)
        sheet_changed = app.styleSheet() != sheet
        if font_changed or palette_changed or sheet_changed:
            torn = 0
            for key, view in self.views.items():
                if key != self.current_key and not view.busy and view._built:
                    # retire, not teardown: the page keeps what its filters
                    # and selection were, and gets them back on the next
                    # visit instead of coming back empty.
                    view.retire()
                    torn += 1
            if torn:
                # Retired widgets are deleted later, by the event loop. They
                # have to be gone now, or the new sheet polishes them anyway.
                QCoreApplication.sendPostedEvents(
                    None, QEvent.Type.DeferredDelete)
        if font_changed:
            app.setFont(font)
        if palette_changed:
            apply_qpalette(app, palette)
            self._palette_applied = palette.name
        self._refresh_nav_icons()
        # The sidebar's words grow with the text size; so does the sidebar,
        # and so does the least the search field may shrink to.
        self.sidebar.setFixedWidth(
            round(SIDEBAR_WIDTH * (1 + (max(1.0, scale) - 1) * 0.75)))
        self.search.setMinimumWidth(round(260 * max(1.0, scale)))
        if sheet_changed:
            app.setStyleSheet(sheet)
        for view in self.views.values():
            handler = getattr(view, "on_theme", None)
            if callable(handler):
                handler()
        practice = self.views.get("practice")
        if practice is not None and practice._built:
            practice.editor.set_theme(palette)

    def toast(self, message: str) -> None:
        self.status_label.setText(message)
        # The status bar is the app's only feedback channel, and a label
        # changing its text is silent to a screen reader.
        self.status_label.setAccessibleName(message or "Status")
        self.status_label.setAccessibleDescription(message)
        if message:
            announce(self.status_label)
        self._toast_timer.start(5000)

    def _clear_toast(self) -> None:
        self.status_label.setText("")
        self.status_label.setAccessibleName("Status")
        self.status_label.setAccessibleDescription("")

    # -- menu actions ------------------------------------------------------

    def _export(self) -> None:
        self.go("settings")
        self.views["settings"]._export()

    def _report(self) -> None:
        self.go("settings")
        self.views["settings"]._report()

    def _snapshot(self) -> None:
        try:
            target = self.ctx.store.backup(tag="manual")
        except OSError as exc:
            self.toast("Snapshot failed: %s" % exc)
            return
        self.toast("Snapshot saved as %s" % target.name)

    def _restore_snapshot(self) -> None:
        self.go("settings")
        self.views["settings"].restore_snapshot()

    # -- undo and redo -----------------------------------------------------

    def undo(self) -> None:
        label = self.ctx.undo()
        if label:
            self._after_history("Undid the %s." % label)

    def redo(self) -> None:
        label = self.ctx.redo()
        if label:
            self._after_history("Redid the %s." % label)

    def _after_history(self, message: str) -> None:
        """Rebuild the page so reverted state is actually on screen."""
        view = self.views.get(self.current_key)
        if view is not None:
            view.refresh()
        self._update_status()
        self.toast(message)

    def _refresh_history_buttons(self) -> None:
        history = self.ctx.history
        self.undo_button.setEnabled(history.can_undo)
        self.redo_button.setEnabled(history.can_redo)
        undo_label = history.undo_label()
        redo_label = history.redo_label()
        self.undo_button.setToolTip(
            "Undo the %s  (Ctrl+Z)" % undo_label if undo_label
            else "Nothing to undo")
        self.redo_button.setToolTip(
            "Redo the %s  (Ctrl+Shift+Z)" % redo_label if redo_label
            else "Nothing to redo")
        if hasattr(self, "undo_action"):
            self.undo_action.setEnabled(history.can_undo)
            self.redo_action.setEnabled(history.can_redo)

    # -- updates -----------------------------------------------------------

    def _on_update_available(self, release) -> None:
        self.update_button.announce(release)
        self.toast("Version %s is available. The button is in the sidebar."
                   % release.label)

    def remember_place(self) -> None:
        """Note the open page, so the app an update restarts opens on it."""
        view = self.views.get(self.current_key)
        target = view.resume_target() if view is not None and view._built else ""
        self.ctx.store.set_setting(RESUME_SETTING, {
            "key": self.current_key, "target": target, "at": time.time()})

    def _resume_after_update(self) -> None:
        place = self.ctx.store.setting(RESUME_SETTING, None)
        if not place:
            return
        self.ctx.store.set_setting(RESUME_SETTING, None)
        if not isinstance(place, dict):
            return
        try:
            age = time.time() - float(place.get("at") or 0)
        except (TypeError, ValueError):
            return
        key = place.get("key") or ""
        if 0 <= age <= RESUME_WITHIN_SECONDS and key in self.views:
            self.go(key, str(place.get("target") or ""))

    def show_update(self) -> None:
        release = self.updates.release
        if release is None:
            self.toast("Checking for a new version...")
            self.updates.maybe_check(force=True)
            return
        self.update_button.announce(release)
        self.update_button.setFocus()

    def check_for_updates(self) -> None:
        """The Help menu entry, which always reports back."""
        from ..core import updates as update_core
        if not update_core.can_self_update():
            self.toast("Running from source - update with git pull.")
            return
        self.toast("Checking for a new version...")
        self.updates.maybe_check(force=True)
        QTimer.singleShot(6000, self._report_check)

    def _report_check(self) -> None:
        if self.updates.release is None:
            self.toast("You are on the latest version.")

    def _point_at_guide(self) -> None:
        """Say where the explanation lives - on the first launch only.

        Written to the store before it is said, so a crash between the two
        costs the learner the hint rather than repeating it every launch.
        """
        store = self.ctx.store
        try:
            if store.setting(GUIDE_SETTING, False):
                return
            store.set_setting(GUIDE_SETTING, True)
        except Exception:
            return      # a store that cannot be written must not block a launch
        self.toast(GUIDE_HINT)

    def _show_guide(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "How this app works",
            "Today tells you what to do next. Follow it and you can ignore "
            "everything else.\n\n"
            "Roadmap is the plan, ordered so nothing depends on something you "
            "have not been taught. Phases are never locked.\n\n"
            "Practice runs your code against real checks. Quizzes catch "
            "misunderstandings. Anything you get wrong is scheduled for "
            "Review automatically.\n\n"
            "Review uses spaced repetition, so early phases do not leak away "
            "while you work on later ones.\n\n"
            "Projects are the proof. A phase is not finished until its gate "
            "and its project are.\n\n"
            "Ctrl+K searches everything: the curriculum, and the notes and "
            "log entries you wrote yourself. Arrow keys pick a result, Enter "
            "opens it. F1 lists every other key.\n\n"
            "Everything saves the instant you change it. There is no save "
            "button and nothing is uploaded anywhere.")

    def _show_shortcuts(self) -> None:
        from .shortcuts import ShortcutsDialog
        ShortcutsDialog(self).exec()

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        from ..core import paths
        QMessageBox.about(
            self, "About %s" % APP_NAME,
            "%s %s\n\n"
            "%d phases, %d graded exercises, %d review questions, %d projects."
            "\n\nScheduling by FSRS-6. Your data lives in:\n%s"
            % (APP_NAME, __version__, len(self.ctx.curriculum.phases),
               len(self.ctx.curriculum.exercises),
               len(self.ctx.curriculum.all_questions),
               len(self.ctx.curriculum.projects), paths.data_dir()))

    # -- lifecycle ---------------------------------------------------------

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # Qt hands first focus to the first Tab-focusable widget, the Today
        # button, which then wears a keyboard focus ring nobody asked for.
        QTimer.singleShot(0, self._settle_focus)

    def _settle_focus(self) -> None:
        from PySide6.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused is not None and focused.property("nav") is True:
            focused.clearFocus()

    def _restore_geometry(self) -> None:
        """Open where the learner left it: size, position, maximised.

        Qt moves a window saved on a monitor that is gone back onto one
        that is there, so a stale value cannot strand it off screen.
        """
        saved = self.ctx.store.setting(GEOMETRY_SETTING, "")
        if not isinstance(saved, str) or not saved:
            return
        data = QByteArray.fromBase64(saved.encode("ascii", "ignore"))
        if data.isEmpty() or not self.restoreGeometry(data):
            self.resize(1220, 840)

    def _save_geometry(self) -> None:
        try:
            self.ctx.store.set_setting(GEOMETRY_SETTING, bytes(
                self.saveGeometry().toBase64()).decode("ascii"))
        except Exception:
            pass            # losing the window size must never block quitting

    def closeEvent(self, event) -> None:
        # A field saves when it loses focus. Left to Qt, that happens as the
        # window hides - after the store below has closed - so a repo URL or
        # a name typed just before quitting was lost. Take the focus now.
        from PySide6.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused is not None and self.isAncestorOf(focused):
            focused.clearFocus()
        self._first_check.stop()
        self._save_geometry()
        self._toast_timer.stop()
        practice = self.views.get("practice")
        if practice is not None and getattr(practice, "current", None):
            practice._save_code()
        phase = self.views.get("phase")
        if phase is not None and phase._built:
            phase.flush_note()
        projects = self.views.get("projects")
        if projects is not None and projects._built:
            projects.flush_notes()      # typed in the last moments before quitting
        # Everything is saved; no timer under this window may fire against
        # the closed store below (the practice autosave did, 700 ms after
        # a quick quit).
        for timer in self.findChildren(QTimer):
            timer.stop()
        try:
            self.ctx.store.close()
        except Exception:
            pass
        super().closeEvent(event)
