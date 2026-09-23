"""One copy of the app per data folder.

The learner whose settings "were not saved" had two copies open at once - an
old installed build and a new one - on the same SQLite file. Every setting is
a row in one table and every write is last-writer-wins, so the older copy
quietly put its own idea of `goals` and `started_on` back over the newer one's.

A second launch now hands over to the copy already running instead of opening.
Everything here runs in this process: two `QLocalSocket`s standing in for the
second and third launch, and no child process anywhere.
"""
from __future__ import annotations

import pytest

from conftest import pump, wait_for

from operators_console import app
from operators_console.version import APP_ID


@pytest.fixture
def key(tmp_path, qt_app):
    """A socket name of this test's own, released afterwards."""
    name = app.instance_key(tmp_path / "data")
    yield name
    from PySide6.QtNetwork import QLocalServer
    QLocalServer.removeServer(name)


# -- the name -------------------------------------------------------------


def test_the_key_follows_the_data_folder(tmp_path):
    """A portable copy with its own home is a different app, and allowed."""
    installed = app.instance_key(tmp_path / "roaming")
    portable = app.instance_key(tmp_path / "usb stick")
    assert installed != portable
    assert installed == app.instance_key(tmp_path / "roaming")
    assert installed.startswith(APP_ID)


def test_the_key_defaults_to_the_real_data_folder(isolated_home):
    from operators_console.core import paths
    assert app.instance_key() == app.instance_key(paths.data_dir())


# -- handing over ---------------------------------------------------------


def test_nothing_to_hand_over_to_when_nobody_is_listening(key):
    assert app.hand_over(key, timeout_ms=200) is False


def test_a_second_copy_hands_over_to_the_first(qt_app, key):
    raised = []
    server = app.listen_for_raise(key, lambda: raised.append("front"))
    assert server is not None, "the first copy could not hold the socket"
    try:
        assert app.hand_over(key) is True
        assert wait_for(qt_app, lambda: raised, seconds=5)
        assert raised == ["front"]
    finally:
        server.close()


def test_two_more_launches_both_bring_the_window_forward(qt_app, key):
    """Two QLocalSockets, in this process, standing in for two launches."""
    from PySide6.QtNetwork import QLocalSocket

    raised = []
    server = app.listen_for_raise(key, lambda: raised.append("front"))
    assert server is not None
    sockets = []
    try:
        for _ in range(2):
            socket = QLocalSocket()
            socket.connectToServer(key)
            assert socket.waitForConnected(2000), "the server refused a copy"
            socket.write(app.RAISE)
            # False here only means there was nothing left pending.
            socket.waitForBytesWritten(2000)
            sockets.append(socket)
        assert wait_for(qt_app, lambda: len(raised) == 2, seconds=5)
        assert len(raised) == 2, "one launch was answered and the other lost"
    finally:
        for socket in sockets:
            socket.disconnectFromServer()
        pump(qt_app, 2)
        server.close()


def test_each_connection_is_answered_exactly_once(qt_app, key):
    """The message and the hang-up both arrive; the window rises once."""
    from PySide6.QtNetwork import QLocalSocket

    raised = []
    server = app.listen_for_raise(key, lambda: raised.append("front"))
    assert server is not None
    try:
        socket = QLocalSocket()
        socket.connectToServer(key)
        assert socket.waitForConnected(2000)
        socket.write(app.RAISE)
        socket.waitForBytesWritten(2000)
        assert wait_for(qt_app, lambda: raised, seconds=5)
        socket.disconnectFromServer()
        pump(qt_app, 6)
        assert len(raised) == 1
    finally:
        server.close()


# -- it may never be the reason the app will not start --------------------


def test_a_socket_that_cannot_listen_leaves_the_app_alone(qt_app, key):
    from PySide6.QtNetwork import QLocalServer
    original = QLocalServer.listen

    def refuse(self, name=""):
        return False

    QLocalServer.listen = refuse
    try:
        assert app.listen_for_raise(key, lambda: None) is None
    finally:
        QLocalServer.listen = original


def test_a_socket_that_explodes_leaves_the_app_alone(qt_app, key):
    from PySide6.QtNetwork import QLocalServer, QLocalSocket

    def explode(*args, **kwargs):
        raise RuntimeError("no local sockets on this machine")

    original_listen = QLocalServer.listen
    original_connect = QLocalSocket.connectToServer
    QLocalServer.listen = explode
    QLocalSocket.connectToServer = explode
    try:
        assert app.listen_for_raise(key, lambda: None) is None
        assert app.hand_over(key) is False
    finally:
        QLocalServer.listen = original_listen
        QLocalSocket.connectToServer = original_connect


def test_a_handler_that_raises_does_not_take_the_socket_down(qt_app, key):
    from PySide6.QtNetwork import QLocalSocket

    def unhappy():
        raise RuntimeError("the window went away")

    server = app.listen_for_raise(key, unhappy)
    assert server is not None
    try:
        socket = QLocalSocket()
        socket.connectToServer(key)
        assert socket.waitForConnected(2000)
        socket.write(app.RAISE)
        socket.waitForBytesWritten(2000)
        pump(qt_app, 6)
        socket.disconnectFromServer()
        # Still listening: the next launch must still find a copy here.
        assert server.isListening()
    finally:
        server.close()


# -- coming to the front --------------------------------------------------


def test_raising_shows_a_window_that_was_hidden(qt_app):
    from PySide6.QtWidgets import QWidget
    widget = QWidget()
    try:
        assert not widget.isVisible()
        app.raise_window(widget)
        pump(qt_app, 2)
        assert widget.isVisible(), "the running copy stayed out of sight"
    finally:
        widget.close()
        widget.deleteLater()
        pump(qt_app, 2)


def test_raising_something_broken_is_survivable():
    class Gone:
        def isMinimized(self):
            raise RuntimeError("the window has been deleted")

    app.raise_window(Gone())        # must not raise
