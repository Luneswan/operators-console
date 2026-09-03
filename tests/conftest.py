"""Shared fixtures. Every test runs against a throwaway data directory."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

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
