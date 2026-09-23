"""Every control the application defines, read straight out of the source.

The denominator for coverage has to come from the code rather than from what
the walk happened to build, otherwise a page that is never opened silently
shrinks the total and the number flatters itself.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

from .harness import SRC

BUTTON_CALLS = {"button", "QPushButton"}
ACTION_CALLS = {"QAction"}
SHORTCUT_METHODS = {"setShortcut", "setShortcuts"}
#: Controls Qt builds for us, which the source never names.
LINE_TOLERANCE = 6


@dataclass(frozen=True)
class Site:
    file: str
    line: int
    kind: str
    label: str


def _literal(node) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "<f-string>"
    if isinstance(node, ast.BinOp):
        return "<computed>"
    if isinstance(node, ast.Name):
        return "<%s>" % node.id
    if isinstance(node, ast.Attribute):
        return "<%s>" % node.attr
    if isinstance(node, ast.Call):
        return "<call>"
    return "<dynamic>"


def _factory_lines(tree) -> set:
    """Lines inside the shared ``button()`` factory itself.

    The ``QPushButton(...)`` in there builds every button in the app; it is
    plumbing, not a control, and counting it would put one entry in the
    denominator that can never be pressed.
    """
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "button":
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    out.add(child.lineno)
    return out


def scan() -> list:
    """Find every button, action and shortcut declared under src/."""
    sites = []
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(SRC).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        except SyntaxError:
            continue
        skip = (_factory_lines(tree)
                if rel.endswith("widgets/common.py") else set())
        for node in ast.walk(tree):
            if getattr(node, "lineno", None) in skip:
                continue
            if not isinstance(node, ast.Call):
                continue
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in BUTTON_CALLS:
                label = _literal(node.args[0]) if node.args else ""
                sites.append(Site(rel, node.lineno, "button", label))
            elif name in ACTION_CALLS:
                label = _literal(node.args[0]) if node.args else ""
                sites.append(Site(rel, node.lineno, "action", label))
            elif name in SHORTCUT_METHODS:
                sites.append(Site(rel, node.lineno, "shortcut",
                                  _shortcut_text(node)))
    return sites


def _shortcut_text(node) -> str:
    for arg in node.args:
        for sub in ast.walk(arg):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                return sub.value
            if isinstance(sub, ast.Attribute):
                return "StandardKey.%s" % sub.attr
    # setShortcuts(_redo_keys()): the helper's name stands for its keys.
    if (node.args and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Name)):
        return "<%s()>" % node.args[0].func.id
    return "<dynamic>"


def coverage(sites, hits, shortcut_hits) -> tuple:
    """Match recorded creation sites against the declared ones.

    A frame's line number for a multi line call can land a little past the
    line the parser reports, so a hit claims the nearest declaration in the
    same file within a few lines.
    """
    by_file = {}
    for index, site in enumerate(sites):
        by_file.setdefault(site.file, []).append((site.line, index))
    covered = set()
    unmatched = []
    for file, line in sorted(hits):
        candidates = by_file.get(file, [])
        best, best_distance = None, LINE_TOLERANCE + 1
        for site_line, index in candidates:
            distance = abs(site_line - line)
            if distance < best_distance:
                best, best_distance = index, distance
        if best is None:
            unmatched.append((file, line))
        else:
            covered.add(best)

    for index, site in enumerate(sites):
        if site.kind != "shortcut":
            continue
        for pressed in shortcut_hits:
            if pressed and _shortcut_matches(pressed, site.label):
                covered.add(index)
    return covered, unmatched


# A declaration names a standard key or a format string; the walk records
# the sequence it actually sent. These are the same shortcut.
STANDARD_KEYS = {
    "standardkey.undo": ("ctrl+z",),
    "standardkey.redo": ("ctrl+shift+z", "ctrl+y"),
    "<_redo_keys()>": ("ctrl+shift+z", "ctrl+y"),
    "standardkey.quit": ("ctrl+q",),
    "standardkey.find": ("ctrl+f",),
}


def _shortcut_matches(pressed: str, label: str) -> bool:
    pressed, label = pressed.lower(), label.lower()
    if pressed in label or label in pressed:
        return True
    if pressed in STANDARD_KEYS.get(label, ()):
        return True
    if "%d" in label:
        import re
        pattern = re.escape(label).replace("%d", r"\d")
        return re.fullmatch(pattern, pressed) is not None
    return False
