"""Colour, type and stylesheet for the whole application.

The palette is carried over from the original console page: a warm paper
ground, near-black ink, and a single oxide-red accent used only for the current
position and for progress. Restraint is the point - when everything is
highlighted, nothing is.
"""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette


@dataclass(frozen=True, slots=True)
class Palette:
    name: str
    paper: str
    paper_2: str
    shell: str
    ink: str
    ink_soft: str
    ink_faint: str
    rule: str
    accent: str
    accent_soft: str
    done: str
    warn: str
    bad: str
    code_bg: str
    selection: str


LIGHT = Palette(
    name="light",
    paper="#E7EAE3",
    paper_2="#DFE3DA",
    shell="#F3F5EF",
    ink="#16201C",
    ink_soft="#4B5750",
    ink_faint="#78837B",
    rule="#C4CBBF",
    accent="#9E3B1B",
    accent_soft="#C9714F",
    done="#2C6B4F",
    warn="#9A6B14",
    bad="#A3301F",
    code_bg="#EDEFE8",
    selection="#D6DCCE",
)

DARK = Palette(
    name="dark",
    paper="#14171A",
    paper_2="#1B1F23",
    shell="#1F242A",
    ink="#E8EBE6",
    ink_soft="#A9B2AC",
    ink_faint="#7B857F",
    rule="#2E353B",
    accent="#E0713F",
    accent_soft="#B85E34",
    done="#5CB98C",
    warn="#D9A441",
    bad="#E2705C",
    code_bg="#191D21",
    selection="#2A3138",
)


PALETTES = {"light": LIGHT, "dark": DARK}

# Preferred families, in order. The first one present on the machine wins, so
# the app looks native everywhere without shipping font files.
SANS_STACK = ("Archivo", "Inter", "Segoe UI Variable Text", "Segoe UI",
              "SF Pro Text", "Helvetica Neue", "Cantarell", "Ubuntu",
              "DejaVu Sans")
MONO_STACK = ("IBM Plex Mono", "JetBrains Mono", "Cascadia Mono", "Consolas",
              "SF Mono", "Menlo", "DejaVu Sans Mono", "Liberation Mono")


def _first_available(candidates: tuple) -> str:
    """Pick the first installed family, or the last fallback.

    QFontDatabase needs a live QGuiApplication and aborts the process without
    one, so this is guarded: a stylesheet built during a test or a CLI run
    still gets a sensible family name.
    """
    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        return candidates[-1]
    try:
        families = set(QFontDatabase.families())
    except Exception:
        return candidates[-1]
    for name in candidates:
        if name in families:
            return name
    return candidates[-1]


def sans_family() -> str:
    return _first_available(SANS_STACK)


def mono_family() -> str:
    return _first_available(MONO_STACK)


def resolve(theme: str, dark_hint: bool) -> Palette:
    """Turn the stored preference into a concrete palette."""
    if theme == "dark":
        return DARK
    if theme == "light":
        return LIGHT
    return DARK if dark_hint else LIGHT


def apply_qpalette(app, palette: Palette) -> None:
    """Native widgets that ignore the stylesheet still read the QPalette."""
    qp = QPalette()
    ink = QColor(palette.ink)
    paper = QColor(palette.paper)
    shell = QColor(palette.shell)
    qp.setColor(QPalette.ColorRole.Window, paper)
    qp.setColor(QPalette.ColorRole.WindowText, ink)
    qp.setColor(QPalette.ColorRole.Base, shell)
    qp.setColor(QPalette.ColorRole.AlternateBase, QColor(palette.paper_2))
    qp.setColor(QPalette.ColorRole.Text, ink)
    qp.setColor(QPalette.ColorRole.Button, QColor(palette.paper_2))
    qp.setColor(QPalette.ColorRole.ButtonText, ink)
    qp.setColor(QPalette.ColorRole.Highlight, QColor(palette.accent))
    qp.setColor(QPalette.ColorRole.HighlightedText, QColor(palette.shell))
    qp.setColor(QPalette.ColorRole.ToolTipBase, shell)
    qp.setColor(QPalette.ColorRole.ToolTipText, ink)
    qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(palette.ink_faint))
    qp.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                QColor(palette.ink_faint))
    qp.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                QColor(palette.ink_faint))
    app.setPalette(qp)


def base_font(scale: float = 1.0) -> QFont:
    font = QFont(sans_family())
    font.setPointSizeF(max(8.0, 10.0 * scale))
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    return font


QSS = """
* { outline: none; }

QWidget { color: %(ink)s; }
QMainWindow, QDialog { background: %(paper)s; }

QToolTip {
    background: %(shell)s; color: %(ink)s;
    border: 1px solid %(rule)s; padding: 5px 7px;
}

/* ---- side navigation ---- */
#Sidebar { background: %(paper_2)s; border-right: 1px solid %(rule)s; }
#SidebarTitle {
    color: %(ink)s; font-size: 15px; font-weight: 800;
    letter-spacing: -0.4px; padding: 16px 16px 2px;
}
#SidebarSubtitle {
    color: %(ink_faint)s; font-size: 11px; padding: 0 16px 12px;
}
QPushButton[nav="true"] {
    text-align: left; padding: 9px 14px; border: none;
    border-left: 3px solid transparent; color: %(ink_soft)s;
    font-size: 13px; font-weight: 600; background: transparent;
}
QPushButton[nav="true"]:hover { background: %(shell)s; color: %(ink)s; }
QPushButton[nav="true"][active="true"] {
    border-left-color: %(accent)s; color: %(ink)s; background: %(shell)s;
}
#NavBadge {
    background: %(accent)s; color: %(shell)s; border-radius: 8px;
    padding: 1px 6px; font-size: 10px; font-weight: 700;
}

/* ---- headings and text ---- */
#PageTitle {
    font-size: 26px; font-weight: 800; letter-spacing: -0.6px;
    color: %(ink)s;
}
#PageKicker {
    font-size: 11px; font-weight: 700; letter-spacing: 1.1px;
    color: %(accent)s;
}
#PageAim { color: %(ink_soft)s; font-size: 13px; }
#SectionTitle {
    font-size: 13px; font-weight: 700; color: %(ink)s;
    padding-bottom: 5px; border-bottom: 1px solid %(rule)s;
}
#Muted { color: %(ink_faint)s; font-size: 11px; }
#Soft { color: %(ink_soft)s; font-size: 12px; }
#Big {
    font-size: 40px; font-weight: 800; letter-spacing: -1.4px; color: %(ink)s;
}
#Mono { font-family: "%(mono)s"; font-size: 12px; color: %(ink_soft)s; }

/* ---- cards ---- */
#Card {
    background: %(shell)s; border: 1px solid %(rule)s; border-radius: 4px;
}
#CardFlat { background: %(shell)s; border-radius: 4px; }
#Divider { background: %(rule)s; max-height: 1px; min-height: 1px; border: none; }

/* ---- buttons ---- */
QPushButton {
    background: %(shell)s; border: 1px solid %(rule)s; border-radius: 3px;
    padding: 6px 13px; color: %(ink)s; font-size: 12px; font-weight: 600;
}
QPushButton:hover { border-color: %(ink_faint)s; }
QPushButton:pressed { background: %(paper_2)s; }
QPushButton:disabled { color: %(ink_faint)s; border-color: %(rule)s; }
QPushButton[kind="primary"] {
    background: %(accent)s; border-color: %(accent)s; color: %(shell)s;
}
QPushButton[kind="primary"]:hover { background: %(accent_soft)s; }
QPushButton[kind="primary"]:disabled {
    background: %(rule)s; border-color: %(rule)s; color: %(ink_faint)s;
}
QPushButton[kind="quiet"] {
    background: transparent; border-color: transparent; color: %(ink_soft)s;
}
QPushButton[kind="quiet"]:hover { color: %(ink)s; background: %(paper_2)s; }
QPushButton[kind="good"] {
    background: %(done)s; border-color: %(done)s; color: %(shell)s;
}
QPushButton[kind="bad"] {
    background: %(bad)s; border-color: %(bad)s; color: %(shell)s;
}

/* ---- inputs ---- */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
QDateEdit {
    background: %(shell)s; border: 1px solid %(rule)s; border-radius: 3px;
    padding: 6px 8px; selection-background-color: %(accent)s;
    selection-color: %(shell)s; color: %(ink)s;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border-color: %(accent)s;
}
QComboBox { padding-right: 22px; }
QSpinBox, QDoubleSpinBox { padding-right: 18px; }
QComboBox QAbstractItemView {
    background: %(shell)s; border: 1px solid %(rule)s;
    selection-background-color: %(selection)s; selection-color: %(ink)s;
}
"""

QSS += """
/* ---- checkable rows ---- */
QCheckBox { spacing: 9px; color: %(ink)s; font-size: 13px; }
QCheckBox::indicator {
    width: 15px; height: 15px; border: 1px solid %(ink_soft)s;
    border-radius: 3px; background: %(shell)s;
}
QCheckBox::indicator:hover { border-color: %(accent)s; }
QCheckBox::indicator:checked {
    background: %(done)s; border-color: %(done)s;
    image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-apply-16.png);
}
QCheckBox:disabled { color: %(ink_faint)s; }

/* ---- scrollbars ---- */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: transparent; width: 10px; margin: 0;
}
QScrollBar::handle:vertical {
    background: %(rule)s; border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: %(ink_faint)s; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 0; }
QScrollBar::handle:horizontal {
    background: %(rule)s; border-radius: 5px; min-width: 30px;
}
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

/* ---- progress ---- */
QProgressBar {
    background: %(paper_2)s; border: none; border-radius: 2px;
    height: 6px; text-align: center; color: transparent;
}
QProgressBar::chunk { background: %(accent)s; border-radius: 2px; }
QProgressBar[tone="done"]::chunk { background: %(done)s; }

/* ---- lists and tables ---- */
QListWidget, QTreeWidget, QTableWidget {
    background: %(shell)s; border: 1px solid %(rule)s; border-radius: 3px;
    alternate-background-color: %(paper_2)s;
}
QListWidget::item, QTreeWidget::item { padding: 6px 8px; border: none; }
QListWidget::item:selected, QTreeWidget::item:selected,
QTableWidget::item:selected {
    background: %(selection)s; color: %(ink)s;
}
QHeaderView::section {
    background: %(paper_2)s; border: none;
    border-bottom: 1px solid %(rule)s; padding: 6px 8px;
    font-size: 11px; font-weight: 700; color: %(ink_soft)s;
}
QTableWidget { gridline-color: %(rule)s; }

/* ---- tabs ---- */
QTabWidget::pane { border: none; border-top: 1px solid %(rule)s; }
QTabBar::tab {
    background: transparent; padding: 8px 14px; color: %(ink_soft)s;
    font-size: 12px; font-weight: 600; border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: %(ink)s; border-bottom-color: %(accent)s; }
QTabBar::tab:hover { color: %(ink)s; }

/* ---- code ---- */
#Code, QPlainTextEdit[role="code"] {
    font-family: "%(mono)s"; font-size: 12px;
    background: %(code_bg)s; border: 1px solid %(rule)s; border-radius: 3px;
    padding: 9px; color: %(ink)s;
}

/* ---- pills ---- */
#Pill {
    background: %(paper_2)s; color: %(ink_soft)s; border-radius: 9px;
    padding: 2px 9px; font-size: 10px; font-weight: 700;
}
#Pill[tone="accent"] { background: %(accent)s; color: %(shell)s; }
#Pill[tone="done"] { background: %(done)s; color: %(shell)s; }
#Pill[tone="warn"] { background: %(warn)s; color: %(shell)s; }
#Pill[tone="bad"] { background: %(bad)s; color: %(shell)s; }

/* ---- misc chrome ---- */
QStatusBar { background: %(paper_2)s; border-top: 1px solid %(rule)s; }
QStatusBar::item { border: none; }
QMenuBar { background: %(paper_2)s; }
QMenuBar::item:selected { background: %(selection)s; }
QMenu { background: %(shell)s; border: 1px solid %(rule)s; padding: 4px; }
QMenu::item { padding: 6px 22px 6px 14px; }
QMenu::item:selected { background: %(selection)s; }
QSplitter::handle { background: %(rule)s; }
QSlider::groove:horizontal { height: 4px; background: %(paper_2)s; }
QSlider::handle:horizontal {
    background: %(accent)s; width: 13px; margin: -5px 0; border-radius: 6px;
}
"""


def stylesheet(palette: Palette) -> str:
    values = {
        "paper": palette.paper, "paper_2": palette.paper_2,
        "shell": palette.shell, "ink": palette.ink,
        "ink_soft": palette.ink_soft, "ink_faint": palette.ink_faint,
        "rule": palette.rule, "accent": palette.accent,
        "accent_soft": palette.accent_soft, "done": palette.done,
        "warn": palette.warn, "bad": palette.bad,
        "code_bg": palette.code_bg, "selection": palette.selection,
        "mono": mono_family(),
    }
    return QSS % values
