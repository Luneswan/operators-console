r"""Where the app keeps its files on each platform.

Everything the user creates lives in one directory so that backing the app up
is a matter of copying a single folder. The location follows the platform
convention rather than inventing one:

    Windows   %APPDATA%\Operator's Console
    macOS     ~/Library/Application Support/Operator's Console
    Linux     $XDG_DATA_HOME/operators-console  (default ~/.local/share/...)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from ..version import APP_ID, ORG_NAME


def _base_dir() -> Path:
    override = os.environ.get("OPERATORS_CONSOLE_HOME")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        root = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        return Path(root) / ORG_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / ORG_NAME
    root = os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share")
    return Path(root) / APP_ID


def data_dir() -> Path:
    """The app's writable home, created on first access."""
    d = _base_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def db_path() -> Path:
    return data_dir() / "progress.db"


def backups_dir() -> Path:
    d = data_dir() / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def workspace_dir() -> Path:
    """Scratch space for the exercise runner."""
    d = data_dir() / "workspace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def bundled_data_dir() -> Path:
    """The read-only curriculum shipped inside the application."""
    return Path(__file__).resolve().parent.parent / "data"


def icon_path() -> Path:
    """The application icon, bundled beside the curriculum."""
    return bundled_data_dir() / "icons" / "operators-console-256.png"
