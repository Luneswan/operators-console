"""A new release reaches a running app within minutes, for free.

The app looked every 30 minutes and only once per day at launch, so a
release could sit unseen for a day. Now it looks at every launch, every
POLL_MINUTES, and when the window comes back to the front; GitHub's ETag
makes an unchanged answer a 304 that costs nothing against its rate limit.
"""
from __future__ import annotations

import io
import json
import urllib.error

from PySide6.QtCore import Qt

from conftest import pump

from operators_console.core import updates
from operators_console.ui import updater

PAYLOAD = {
    "tag_name": "v9.9.9",
    "assets": [{"name": "operators-console-9.9.9-windows-setup.exe",
                "browser_download_url": "https://example.invalid/s.exe",
                "size": 4},
               {"name": "SHA256SUMS",
                "browser_download_url": "https://example.invalid/SHA256SUMS",
                "size": 80}],
}
SUMS = ("%s  operators-console-9.9.9-windows-setup.exe\n" % ("a" * 64)).encode()


class _Response(io.BytesIO):
    def __init__(self, data, headers=None):
        super().__init__(data)
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def _github(sent, etag='"abc"'):
    """GitHub, honouring If-None-Match the way the real API does."""
    def fake(url, timeout=None, headers=None):
        sent.append((url, dict(headers or {})))
        if url.endswith("SHA256SUMS"):
            return _Response(SUMS)
        if (headers or {}).get("If-None-Match") == etag:
            raise urllib.error.HTTPError(url, 304, "Not Modified", {}, None)
        return _Response(json.dumps(PAYLOAD).encode(), {"ETag": etag})
    return fake


def test_an_unchanged_release_is_asked_for_with_its_etag(monkeypatch):
    sent = []
    monkeypatch.setattr(updates, "_request", _github(sent))
    first = updates.fetch_latest()
    assert first is not None and first.verified
    api = updates.API % updates.REPO
    sent.clear()
    again = updates.fetch_latest()
    assert again == first
    # One request, conditional, and no second fetch of the checksums.
    assert sent == [(api, {"If-None-Match": '"abc"'})]


def test_a_changed_release_is_fetched_in_full(monkeypatch):
    sent = []
    monkeypatch.setattr(updates, "_request", _github(sent, '"abc"'))
    updates.fetch_latest()
    monkeypatch.setattr(updates, "_request", _github(sent, '"new"'))
    assert updates.fetch_latest() is not None
    assert updates._latest["etag"] == '"new"'


def test_a_304_without_a_remembered_answer_is_not_a_release(monkeypatch):
    def not_modified(url, timeout=None, headers=None):
        raise urllib.error.HTTPError(url, 304, "Not Modified", {}, None)
    monkeypatch.setattr(updates, "_request", not_modified)
    assert updates.fetch_latest() is None


def test_an_unverified_answer_is_not_reused(monkeypatch):
    payload = dict(PAYLOAD, assets=PAYLOAD["assets"][:1])
    monkeypatch.setattr(updates, "_request", lambda url, timeout=None,
                        headers=None: _Response(json.dumps(payload).encode(),
                                                {"ETag": '"x"'}))
    release = updates.fetch_latest()
    assert release is not None and not release.verified
    assert updates._latest["etag"] == ""


def test_the_poll_is_minutes_not_half_hours(window):
    assert window.updates._poll.interval() <= 5 * 60 * 1000


def test_coming_back_to_the_window_looks_again(qt_app, window, monkeypatch):
    looks = []
    monkeypatch.setattr(window.updates, "poll", lambda: looks.append(1))
    window.updates._last_look = 0.0
    window.updates._on_app_state(Qt.ApplicationState.ApplicationActive)
    assert looks == [1]


def test_alt_tabbing_does_not_look_every_time(qt_app, window, monkeypatch):
    looks = []
    monkeypatch.setattr(updater._CheckJob, "run", lambda self: None)
    monkeypatch.setattr(updates, "can_self_update", lambda: True)
    monkeypatch.setattr(window.updates.pool, "start",
                        lambda job: looks.append(job))
    window.updates.poll()
    assert len(looks) == 1
    window.updates._on_app_state(Qt.ApplicationState.ApplicationActive)
    window.updates._on_app_state(Qt.ApplicationState.ApplicationInactive)
    window.updates._on_app_state(Qt.ApplicationState.ApplicationActive)
    pump(qt_app)
    assert len(looks) == 1, "looked again within REFOCUS_SECONDS"
