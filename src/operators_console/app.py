"""Application bootstrap."""
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .version import APP_ID, APP_NAME, ORG_NAME, __version__


def run(argv=None) -> int:
    argv = list(argv or [])

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(__version__)
    QApplication.setOrganizationName(ORG_NAME)
    QApplication.setDesktopFileName(APP_ID)

    app = QApplication(sys.argv[:1] + argv)
    app.setStyle("Fusion")

    from .core import paths
    icon_file = paths.icon_path()
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    from .core.storage import Store
    from .ui.context import AppContext
    from .ui.main_window import MainWindow
    from .ui.onboarding import Onboarding

    try:
        store = Store()
    except Exception as exc:
        QMessageBox.critical(
            None, APP_NAME,
            "Your progress database could not be opened.\n\n%s\n\n"
            "The file is in your application data folder. Move it aside and "
            "restart to begin again, or restore a backup." % exc)
        return 1

    ctx = AppContext(store=store)
    ctx.set_dark_hint(_system_is_dark(app))
    app.styleHints().colorSchemeChanged.connect(
        lambda _s: ctx.set_dark_hint(_system_is_dark(app)))

    window = MainWindow(ctx)
    window.show()

    if not store.setting("onboarded", False):
        Onboarding(ctx, window).exec()
        window.go("today")

    return app.exec()


def _system_is_dark(app) -> bool:
    try:
        return app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except AttributeError:
        return False
