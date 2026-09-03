"""The window: navigation, search, status and the stack of pages."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QStackedWidget, QStatusBar, QVBoxLayout, QWidget,
)

from ..version import APP_NAME, __version__
from .context import AppContext
from .theme import apply_qpalette, base_font, stylesheet
from .updater import UpdateDialog, UpdateManager
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
from .widgets.common import muted

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


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle(APP_NAME)
        self.resize(1220, 840)
        self.setMinimumSize(QSize(940, 620))

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
        self.status_label = QLabel("")
        self.statusBar().addWidget(self.status_label, 1)
        self.status_right = QLabel("")
        self.statusBar().addPermanentWidget(self.status_right)

        self.update_button = QPushButton("")
        self.update_button.setProperty("kind", "primary")
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.setVisible(False)
        self.update_button.clicked.connect(self.show_update)
        self.statusBar().addPermanentWidget(self.update_button)

        self.updates = UpdateManager(ctx, self)
        self.updates.available.connect(self._on_update_available)

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._clear_toast)

        self._build_menu()
        ctx.navigate.connect(self.go)
        ctx.history_changed.connect(self._refresh_history_buttons)
        ctx.progress_changed.connect(self._on_progress)
        ctx.theme_changed.connect(self.apply_theme)
        ctx.toast.connect(self.toast)

        self.current_key = ""
        self._refresh_history_buttons()
        self.go("today", "")
        self.apply_theme()
        QTimer.singleShot(2500, self.updates.maybe_check)

    # -- chrome ------------------------------------------------------------

    def _build_sidebar(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("Sidebar")
        panel.setFixedWidth(212)
        column = QVBoxLayout(panel)
        column.setContentsMargins(0, 0, 0, 10)
        column.setSpacing(0)

        title = QLabel("Operator's\nConsole")
        title.setObjectName("SidebarTitle")
        column.addWidget(title)
        subtitle = QLabel("A Python curriculum")
        subtitle.setObjectName("SidebarSubtitle")
        column.addWidget(subtitle)

        self.nav_buttons = {}
        for key, text, _factory in NAV:
            button = QPushButton(text)
            button.setProperty("nav", True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _=False, k=key: self.go(k, ""))
            column.addWidget(button)
            self.nav_buttons[key] = button

        column.addStretch(1)
        self.sidebar_footer = QLabel("")
        self.sidebar_footer.setObjectName("SidebarSubtitle")
        self.sidebar_footer.setWordWrap(True)
        column.addWidget(self.sidebar_footer)
        return panel

    def _build_searchbar(self) -> QWidget:
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.setContentsMargins(20, 12, 20, 8)
        row.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search the whole curriculum   (Ctrl+K)")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._on_search)
        self.search.returnPressed.connect(self._open_first_result)
        row.addWidget(self.search, 1)

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
        self.results.setWindowFlags(Qt.WindowType.Popup)
        self.results.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        for index, (key, text, _factory) in enumerate(NAV, start=1):
            action = QAction(text, self)
            if index <= 9:
                action.setShortcut(QKeySequence("Ctrl+%d" % index))
            action.triggered.connect(lambda _=False, k=key: self.go(k, ""))
            go_menu.addAction(action)
        edit_menu = menu.addMenu("&Edit")
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        edit_menu.addAction(self.undo_action)
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcuts([QKeySequence.StandardKey.Redo,
                                       QKeySequence("Ctrl+Y")])
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
            button.setProperty("active", nav_key == key)
            button.style().unpolish(button)
            button.style().polish(button)
        self.current_key = key
        view.refresh()
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

    def _on_search(self, text: str) -> None:
        query = text.strip()
        if len(query) < 2:
            self.results.hide()
            return
        hits = self.ctx.index.search(query, limit=40)
        self.results.clear()
        for hit in hits:
            item = QListWidgetItem("%-9s %s   -   %s"
                                   % (hit.kind.upper(), hit.title[:78],
                                      hit.context[:60]))
            item.setData(Qt.ItemDataRole.UserRole, hit)
            self.results.addItem(item)
        if not hits:
            self.results.hide()
            return
        point = self.search.mapToGlobal(self.search.rect().bottomLeft())
        self.results.setGeometry(point.x(), point.y() + 2,
                                 self.search.width(),
                                 min(360, 26 * len(hits) + 8))
        self.results.show()

    def _open_first_result(self) -> None:
        if self.results.count():
            self._open_result(self.results.item(0))

    def _open_result(self, item) -> None:
        hit = item.data(Qt.ItemDataRole.UserRole)
        self.results.hide()
        self.search.clear()
        if hit.kind == "exercise":
            self.go("practice", hit.target)
        elif hit.kind == "project":
            self.go("projects", hit.target)
        elif hit.kind == "question":
            self.go("quiz", hit.phase)
        elif hit.kind == "resource":
            from .widgets.common import open_url
            open_url(hit.target)
        elif hit.kind in ("field", "cert"):
            self.go("library", "")
        else:
            self.go("phase", hit.phase or hit.target)

    # -- theme and chrome --------------------------------------------------

    def apply_theme(self) -> None:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        palette = self.ctx.palette
        scale = float(self.ctx.store.setting("font_scale", 1.0))
        app.setFont(base_font(scale))
        apply_qpalette(app, palette)
        app.setStyleSheet(stylesheet(palette))
        for view in self.views.values():
            handler = getattr(view, "on_theme", None)
            if callable(handler):
                handler()
        practice = self.views.get("practice")
        if practice is not None and practice._built:
            practice.editor.set_theme(palette)

    def toast(self, message: str) -> None:
        self.status_label.setText(message)
        self._toast_timer.start(5000)

    def _clear_toast(self) -> None:
        self.status_label.setText("")

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
        self.update_button.setText("Update to %s" % release.label)
        self.update_button.setToolTip(
            "A new version is ready. Click to install it and reopen the app.")
        self.update_button.setVisible(True)
        self.toast("Version %s is available." % release.label)

    def show_update(self) -> None:
        release = self.updates.release
        if release is None:
            self.toast("Checking for a new version...")
            self.updates.maybe_check(force=True)
            return
        UpdateDialog(self.ctx, release, self).exec()

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
            "Everything saves the instant you change it. There is no save "
            "button and nothing is uploaded anywhere.")

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

    def closeEvent(self, event) -> None:
        practice = self.views.get("practice")
        if practice is not None and getattr(practice, "current", None):
            practice._save_code()
        phase = self.views.get("phase")
        if phase is not None and phase._built:
            phase.flush_note()
        try:
            self.ctx.store.close()
        except Exception:
            pass
        super().closeEvent(event)
