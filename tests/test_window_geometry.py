"""The window opens the size and place the learner left it."""
from __future__ import annotations

from conftest import pump


def _another(window):
    from operators_console.ui.main_window import MainWindow
    return MainWindow(window.ctx)


def _destroy(qt_app, other):
    from PySide6.QtCore import QCoreApplication, QEvent
    other.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qt_app.processEvents()


def test_the_saved_geometry_is_what_the_next_window_restores(qt_app, window,
                                                             monkeypatch):
    """Byte for byte. (Pixels cannot be compared here: the offscreen
    platform's screen is smaller than the window's minimum size, and Qt
    rightly fits a restored window onto the screen it opens on.)"""
    from operators_console.ui.main_window import MainWindow

    window.resize(1010, 700)
    pump(qt_app)
    window._save_geometry()
    expected = bytes(window.saveGeometry())
    restored = []
    real = MainWindow.restoreGeometry
    monkeypatch.setattr(MainWindow, "restoreGeometry",
                        lambda self, data: restored.append(bytes(data))
                        or real(self, data))
    other = _another(window)
    try:
        assert restored == [expected]
    finally:
        _destroy(qt_app, other)


def test_closing_saves_it(qt_app, window, store, monkeypatch):
    window.resize(1030, 710)
    pump(qt_app)
    saved = []
    real = store.set_setting
    monkeypatch.setattr(store, "set_setting",
                        lambda k, v: (saved.append(k), real(k, v)))
    window.close()
    assert "window_geometry" in saved


def test_nonsense_in_the_setting_falls_back_to_the_default(qt_app, window,
                                                           store):
    for junk in ("%%% not base64 %%%", "aGVsbG8=", 12, ["x"]):
        store.set_setting("window_geometry", junk)
        other = _another(window)
        try:
            assert (other.width(), other.height()) == (1220, 840), junk
        finally:
            _destroy(qt_app, other)


def test_a_closed_store_cannot_stop_the_window_closing(qt_app, window, store):
    store.close()
    window._save_geometry()         # must not raise
