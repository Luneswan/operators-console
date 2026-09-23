"""Shared fixtures. Every test runs against a throwaway data directory."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Never touch the real profile, on any platform."""
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    yield tmp_path


@pytest.fixture
def store(isolated_home):
    from operators_console.core.storage import Store
    instance = Store()
    yield instance
    instance.close()


@pytest.fixture(scope="session")
def curriculum():
    from operators_console.core.curriculum import load
    return load()


@pytest.fixture
def progress(curriculum, store):
    from operators_console.core.progress import Progress
    return Progress(curriculum, store)


# -- the interface ------------------------------------------------------

@pytest.fixture(scope="session")
def qt_app():
    """One QApplication for the whole session, on the offscreen platform."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    yield app


@pytest.fixture
def window(qt_app, store, curriculum):
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow

    store.set_setting("onboarded", True)
    ctx = AppContext(store=store, curriculum=curriculum)
    main = MainWindow(ctx)
    main.show()
    qt_app.processEvents()
    yield main
    main.close()
    # Destroy, not just close. The window and its context reference each
    # other through signal connections held on the C++ side, which Python's
    # collector cannot break, so every closed window stayed alive - 31 of
    # them and 17,394 widgets after test_ui.py - with timers still able to
    # fire against a store that had already closed.
    from PySide6.QtCore import QCoreApplication, QEvent
    main.deleteLater()
    ctx.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qt_app.processEvents()


def pump(app, rounds=3):
    for _ in range(rounds):
        app.processEvents()


def wait_for(app, predicate, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return True
        time.sleep(0.02)
    return False
