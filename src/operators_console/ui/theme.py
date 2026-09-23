"""Colour, type, shape and the stylesheet: one design system for both themes.

The tokens follow the 12-step ladder that Radix and Geist use: app background,
subtle background, element, hovered element, active element, hairline,
element border, operable border, solid accent, hovered accent, low-contrast
text, high-contrast text. Elevation is tonal - each layer a step lighter than
the one under it - rather than drawn with shadows, which is what Material's
dark-theme guidance and every premium dark interface do. Every text/surface
pair is held at 4.5:1 and every control border at 3:1 (WCAG 2.2 AA); the
numbers were checked with a solver, not by eye, and tests keep them there.

One accent, warm copper, in an otherwise neutral cool grey. Semantic colours
are desaturated in the dark theme so they do not vibrate against it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette


@dataclass(frozen=True, slots=True)
class Palette:
    name: str
    # surfaces, darkest to lightest in the dark theme (lightest to darkest in
    # the light theme): app background, sidebar, card, hovered / field, active
    bg: str
    bg_2: str
    surface: str
    surface_2: str
    surface_3: str
    # borders: hairline, element, operable control (3:1 on every surface)
    rule: str
    rule_2: str
    rule_strong: str
    # text: high contrast, secondary, muted (4.5:1 on every surface)
    ink: str
    ink_soft: str
    ink_faint: str
    # the accent as a fill, its hover and press, as text, as a tint, and the
    # text that goes on top of any solid fill (accent, done, warn, bad)
    accent: str
    accent_hover: str
    accent_press: str
    accent_text: str
    accent_subtle: str
    on_accent: str
    done: str
    done_text: str
    done_subtle: str
    warn: str
    warn_text: str
    warn_subtle: str
    bad: str
    bad_text: str
    bad_subtle: str
    code_bg: str
    selection: str
    focus: str
    tooltip_bg: str
    tooltip_ink: str

    # Older names, kept so every caller and test keeps working.
    @property
    def paper(self) -> str:
        return self.bg

    @property
    def paper_2(self) -> str:
        return self.bg_2

    @property
    def shell(self) -> str:
        return self.surface

    @property
    def accent_soft(self) -> str:
        return self.accent_hover


DARK = Palette(
    name="dark",
    bg="#0F1114",
    bg_2="#141619",
    surface="#1A1D21",
    surface_2="#20242A",
    surface_3="#272C33",
    rule="#2B3036",
    rule_2="#353B43",
    rule_strong="#6E7681",
    ink="#EDEFF2",
    ink_soft="#AEB4BC",
    ink_faint="#8F969F",
    accent="#E5793F",
    accent_hover="#EE8A55",
    accent_press="#D66C34",
    accent_text="#F2A072",
    accent_subtle="#36231A",
    on_accent="#1A1005",
    done="#4FC08D",
    done_text="#6FD3A3",
    done_subtle="#16302A",
    warn="#E3A83C",
    warn_text="#F0BC5A",
    warn_subtle="#332A16",
    bad="#F0705E",
    bad_text="#F4857A",
    bad_subtle="#3A1E1B",
    code_bg="#15181C",
    selection="#2C3541",
    focus="#F2A072",
    tooltip_bg="#272C33",
    tooltip_ink="#EDEFF2",
)

LIGHT = Palette(
    name="light",
    bg="#F4F5F7",
    bg_2="#EDEEF1",
    surface="#FFFFFF",
    surface_2="#F7F8FA",
    surface_3="#EEF0F3",
    rule="#E3E6EA",
    rule_2="#D5D9DF",
    rule_strong="#7C838D",
    ink="#15181D",
    ink_soft="#4A515C",
    ink_faint="#646C77",
    accent="#B8471C",
    accent_hover="#C24B21",
    accent_press="#9E3B15",
    accent_text="#A63F18",
    accent_subtle="#FAE8DF",
    on_accent="#FFFFFF",
    done="#1F7A4D",
    done_text="#1F6F46",
    done_subtle="#E4F3EA",
    warn="#9A6410",
    warn_text="#8A5A0E",
    warn_subtle="#FBF0D9",
    bad="#B8321F",
    bad_text="#A82D1C",
    bad_subtle="#FBE5E1",
    code_bg="#F7F8FA",
    selection="#E6EAF0",
    focus="#B8471C",
    tooltip_bg="#15181D",
    tooltip_ink="#FFFFFF",
)

PALETTES = {"light": LIGHT, "dark": DARK}

# Preferred families, in order. The first one present on the machine wins, so
# the app looks native everywhere without shipping font files.
SANS_STACK = ("Inter", "Segoe UI Variable Text", "Segoe UI", "SF Pro Text",
              "Helvetica Neue", "Cantarell", "Ubuntu", "DejaVu Sans")
MONO_STACK = ("JetBrains Mono", "Cascadia Mono", "IBM Plex Mono", "Consolas",
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


def reduced_motion() -> bool:
    """Whether this machine has asked for animation to be kept still.

    Honoured in order: an explicit override in the environment (which is what
    the tests use), then the platform setting. Anything that animates must
    still arrive at the same end state instantly when this is true; only the
    movement is dropped, never the change itself.
    """
    import os

    override = os.environ.get("OPERATORS_CONSOLE_REDUCED_MOTION", "")
    if override:
        return override.strip().lower() not in ("0", "false", "no", "")
    import sys
    if sys.platform == "win32":
        try:
            import ctypes

            SPI_GETCLIENTAREAANIMATION = 0x1042
            enabled = ctypes.c_int()
            ok = ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETCLIENTAREAANIMATION, 0, ctypes.byref(enabled), 0)
            if ok:
                return not bool(enabled.value)
        except Exception:
            return False
    return False


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
    qp.setColor(QPalette.ColorRole.Window, QColor(palette.bg))
    qp.setColor(QPalette.ColorRole.WindowText, ink)
    qp.setColor(QPalette.ColorRole.Base, QColor(palette.surface))
    qp.setColor(QPalette.ColorRole.AlternateBase, QColor(palette.surface_2))
    qp.setColor(QPalette.ColorRole.Text, ink)
    qp.setColor(QPalette.ColorRole.Button, QColor(palette.surface_2))
    qp.setColor(QPalette.ColorRole.ButtonText, ink)
    qp.setColor(QPalette.ColorRole.Highlight, QColor(palette.accent))
    qp.setColor(QPalette.ColorRole.HighlightedText, QColor(palette.on_accent))
    qp.setColor(QPalette.ColorRole.ToolTipBase, QColor(palette.tooltip_bg))
    qp.setColor(QPalette.ColorRole.ToolTipText, QColor(palette.tooltip_ink))
    qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(palette.ink_faint))
    qp.setColor(QPalette.ColorRole.Link, QColor(palette.accent_text))
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


# ---------------------------------------------------------------------------
# the sheet
#
# Sizes are on a 4px grid. Corners: 6px on controls, 10px on cards and lists,
# 12px on floating panels. Type: 11px labels, 12-13px body, 15-16px lead,
# 26px page title, 34px headline number.
# ---------------------------------------------------------------------------

QSS = """
* { outline: none; }

QWidget { color: %(ink)s; }
QMainWindow, QDialog { background: %(bg)s; }

QToolTip {
    background: %(tooltip_bg)s; color: %(tooltip_ink)s;
    border: 1px solid %(tooltip_bg)s; border-radius: 6px;
    padding: 6px 9px; font-size: 12px;
}

/* ---- side navigation ---- */
#Sidebar { background: %(bg_2)s; border-right: 1px solid %(rule)s; }
#SidebarScroll, #SidebarBody { background: transparent; border: none; }
#SidebarTitle {
    color: %(ink)s; font-size: 14px; font-weight: 700;
    letter-spacing: -0.2px; padding: 0;
}
#SidebarSubtitle {
    color: %(ink_faint)s; font-size: 12px; letter-spacing: 0; padding: 0 8px;
}
#NavSection {
    color: %(ink_faint)s; font-size: 11px; font-weight: 700;
    letter-spacing: 0.9px; padding: 14px 10px 4px;
}
QPushButton[nav="true"] {
    text-align: left; padding: 7px 10px; margin: 1px 0;
    border: 1px solid transparent; border-radius: 6px;
    color: %(ink_soft)s; font-size: 13px; font-weight: 500;
    background: transparent;
}
QPushButton[nav="true"]:hover {
    background: %(surface_2)s; color: %(ink)s; border-radius: 6px;
}
QPushButton[nav="true"]:pressed {
    background: %(surface_3)s; color: %(ink)s; border-radius: 6px;
}
QPushButton[nav="true"][kbd="true"]:focus {
    border: 1px solid %(focus)s; border-radius: 6px; color: %(ink)s;
}
QPushButton[nav="true"][active="true"] {
    background: %(surface_3)s; color: %(ink)s; font-weight: 600;
    border-radius: 6px;
}
QPushButton[nav="true"][active="true"]:hover {
    background: %(surface_3)s; border-radius: 6px;
}
QPushButton[nav="true"][active="true"][kbd="true"]:focus {
    border: 1px solid %(focus)s; background: %(surface_3)s;
    border-radius: 6px;
}

/* ---- headings and text ---- */
#PageTitle {
    font-size: 26px; font-weight: 700; letter-spacing: -0.7px;
    color: %(ink)s;
}
#PageKicker {
    font-size: 11px; font-weight: 700; letter-spacing: 1.2px;
    color: %(accent_text)s;
}
#PageAim { color: %(ink_soft)s; font-size: 13px; letter-spacing: 0; }
#SectionTitle {
    font-size: 13px; font-weight: 700; color: %(ink)s; letter-spacing: 0;
    padding-bottom: 2px; border: none;
}
#Muted { color: %(ink_faint)s; font-size: 12px; letter-spacing: 0; }
#Soft { color: %(ink_soft)s; font-size: 12.5px; letter-spacing: 0; }
#Big {
    font-size: 34px; font-weight: 700; letter-spacing: -1.2px; color: %(ink)s;
}
#Mono { font-family: "%(mono)s"; font-size: 12px; color: %(ink_soft)s; }
#LinkTitle {
    font-size: 13px; font-weight: 600; color: %(ink)s; letter-spacing: 0;
}
#LinkTitle[lead="true"] {
    font-size: 13.5px; font-weight: 700; letter-spacing: -0.1px;
}
#EmptyState { color: %(ink_soft)s; font-size: 13px; letter-spacing: 0; }

/* ---- cards: a tonal step up from the page, and a hairline ---- */
#Card {
    background: %(surface)s; border: 1px solid %(rule)s; border-radius: 10px;
}
#CardFlat { background: %(surface)s; border-radius: 10px; }
#Divider { background: %(rule)s; max-height: 1px; min-height: 1px; border: none; }
#VDivider { background: %(rule)s; max-width: 1px; min-width: 1px; border: none; }
#StatStrip {
    background: %(surface)s; border: 1px solid %(rule)s; border-radius: 10px;
}
#FocusCard {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 %(accent_subtle)s, stop: 1 %(surface)s);
    border: 1px solid %(rule_2)s; border-radius: 12px;
}
#FocusTitle {
    font-size: 18px; font-weight: 700; letter-spacing: -0.3px; color: %(ink)s;
}
#RowTitle { font-size: 13.5px; font-weight: 600; color: %(ink)s; }
#ActionRow { background: transparent; border-radius: 6px; }
#ActionRow:hover { background: %(surface_2)s; }
#TimelineRow { background: transparent; }
#TimelineTitle {
    font-size: 15px; font-weight: 700; letter-spacing: -0.2px; color: %(ink)s;
}
#RingValue {
    font-size: 17px; font-weight: 700; letter-spacing: -0.5px;
    color: %(ink)s; background: transparent;
}

/* ---- disclosure: the optional half of a group ---- */
#DisclosureToggle {
    background: transparent; border: 1px solid transparent;
    border-radius: 6px; padding: 0 6px; text-align: left;
}
#DisclosureToggle:hover { background: %(surface_2)s; border-radius: 6px; }
#DisclosureToggle:pressed { background: %(surface_3)s; border-radius: 6px; }
#DisclosureToggle[kbd="true"]:focus {
    border-radius: 6px; background: %(surface_2)s;
    border: 1px solid %(focus)s;
}
#DisclosureCaption {
    color: %(ink_faint)s; font-size: 12.5px; font-weight: 600;
    letter-spacing: 0; background: transparent;
}
#DisclosureBody { background: transparent; }

/* ---- buttons ---- */
QPushButton {
    background: %(surface_2)s; border: 1px solid %(rule_2)s;
    border-radius: 6px; padding: 6px 14px; color: %(ink)s;
    font-size: 12.5px; font-weight: 600; letter-spacing: 0;
}
QPushButton:hover {
    background: %(surface_3)s; border-color: %(rule_2)s; border-radius: 6px;
}
QPushButton:pressed {
    background: %(surface_3)s; border-color: %(rule_strong)s;
    border-radius: 6px;
}
QPushButton[kbd="true"]:focus { border-color: %(focus)s; border-radius: 6px; }
QPushButton:disabled {
    color: %(ink_faint)s; border-color: %(rule)s; background: %(surface_2)s;
    border-radius: 6px;
}
QPushButton[kind="primary"] {
    background: %(accent)s; border-color: %(accent)s; color: %(on_accent)s;
    border-radius: 6px;
}
QPushButton[kind="primary"]:hover {
    background: %(accent_hover)s; border-color: %(accent_hover)s;
    border-radius: 6px;
}
QPushButton[kind="primary"]:pressed {
    background: %(accent_press)s; border-color: %(accent_press)s;
    border-radius: 6px;
}
QPushButton[kind="primary"][kbd="true"]:focus {
    border-color: %(ink)s; border-radius: 6px;
}
QPushButton[kind="primary"]:disabled {
    background: %(surface_3)s; border-color: %(surface_3)s;
    color: %(ink_faint)s; border-radius: 6px;
}
QPushButton[kind="quiet"] {
    background: transparent; border-color: transparent; color: %(ink_soft)s;
    border-radius: 6px;
}
QPushButton[kind="quiet"]:hover {
    color: %(ink)s; background: %(surface_2)s; border-color: transparent;
    border-radius: 6px;
}
QPushButton[kind="quiet"]:pressed {
    background: %(surface_3)s; border-color: transparent; border-radius: 6px;
}
QPushButton[kind="quiet"][kbd="true"]:focus {
    border-color: %(focus)s; border-radius: 6px; color: %(ink)s;
}
QPushButton[kind="quiet"]:disabled {
    color: %(ink_faint)s; background: transparent; border-color: transparent;
    border-radius: 6px;
}
QPushButton[kind="good"] {
    background: %(done)s; border-color: %(done)s; color: %(on_accent)s;
    border-radius: 6px;
}
QPushButton[kind="good"]:hover { background: %(done)s; border-radius: 6px; }
QPushButton[kind="good"]:pressed {
    background: %(done)s; border-color: %(ink)s; border-radius: 6px;
}
QPushButton[kind="bad"] {
    background: %(bad)s; border-color: %(bad)s; color: %(on_accent)s;
    border-radius: 6px;
}
QPushButton[kind="bad"]:hover { background: %(bad)s; border-radius: 6px; }
QPushButton[kind="bad"]:pressed {
    background: %(bad)s; border-color: %(ink)s; border-radius: 6px;
}
QPushButton[kind="danger"] {
    background: transparent; border-color: %(bad)s; color: %(bad_text)s;
    border-radius: 6px;
}
QPushButton[kind="danger"]:hover {
    background: %(bad_subtle)s; border-color: %(bad)s; border-radius: 6px;
}
QPushButton[kind="danger"]:pressed {
    background: %(bad_subtle)s; border-color: %(ink)s; border-radius: 6px;
}
QPushButton[kind="good"][kbd="true"]:focus,
QPushButton[kind="bad"][kbd="true"]:focus,
QPushButton[kind="danger"][kbd="true"]:focus {
    border: 2px solid %(ink)s; padding: 5px 13px; border-radius: 6px;
}

#UpdateButton {
    font-size: 12px; font-weight: 700; letter-spacing: 0;
    padding: 7px 10px; border-radius: 6px; text-align: center;
}

/* ---- inputs ---- */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
QDateEdit {
    background: %(surface_2)s; border: 1px solid %(rule_2)s;
    border-radius: 6px; padding: 6px 10px;
    selection-background-color: %(accent)s;
    selection-color: %(on_accent)s; color: %(ink)s; font-size: 13px;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover,
QDateEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
    border-color: %(rule_strong)s; border-radius: 6px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border-color: %(focus)s; border-radius: 6px;
}
QComboBox { padding-right: 26px; }
QSpinBox, QDoubleSpinBox { padding-right: 20px; }
QComboBox QAbstractItemView {
    background: %(surface)s; border: 1px solid %(rule_2)s;
    border-radius: 8px; padding: 4px;
    selection-background-color: %(surface_3)s; selection-color: %(ink)s;
}
QComboBox QAbstractItemView::item { padding: 6px 8px; border-radius: 5px; }
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    subcontrol-origin: border; width: 18px; border: none;
    background: transparent;
}
QAbstractSpinBox::up-button { subcontrol-position: top right; }
QAbstractSpinBox::down-button { subcontrol-position: bottom right; }
QAbstractSpinBox::up-arrow {
    image: url("%(arrow_up)s"); width: 10px; height: 9px;
}
QAbstractSpinBox::down-arrow {
    image: url("%(arrow_down)s"); width: 10px; height: 9px;
}
QComboBox::drop-down, QDateEdit::drop-down {
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 24px; border: none; background: transparent;
}
QComboBox::down-arrow, QDateEdit::down-arrow {
    image: url("%(arrow_down)s"); width: 10px; height: 9px;
}

/* ---- checkable rows ---- */
QCheckBox { spacing: 8px; color: %(ink)s; font-size: 13px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 1px solid %(rule_strong)s;
    border-radius: 4px; background: %(surface_2)s;
}
QCheckBox::indicator:hover { border-color: %(accent)s; border-radius: 4px; }
QCheckBox::indicator:pressed {
    border-color: %(accent)s; background: %(surface_3)s; border-radius: 4px;
}
QCheckBox[kbd="true"]::indicator:focus { border-color: %(focus)s; border-radius: 4px; }
QCheckBox::indicator:checked {
    background: %(done)s; border-color: %(done)s; border-radius: 4px;
    image: url("%(check_mark)s"); width: 16px; height: 16px;
}
QCheckBox[kbd="true"]::indicator:checked:focus { border-color: %(ink)s; }
QCheckBox[kbd="true"]:focus { color: %(accent_text)s; }
QCheckBox:disabled { color: %(ink_faint)s; }

QRadioButton { spacing: 8px; color: %(ink)s; }
QRadioButton::indicator {
    width: 14px; height: 14px; border: 1px solid %(rule_strong)s;
    border-radius: 8px; background: %(surface_2)s;
}
QRadioButton::indicator:hover { border-color: %(accent)s; }
QRadioButton::indicator:checked {
    width: 6px; height: 6px; border: 5px solid %(accent)s;
    border-radius: 8px; background: %(surface)s;
}
QRadioButton::indicator:disabled { border-color: %(rule_2)s; }
QRadioButton::indicator:checked:disabled { border-color: %(ink_faint)s; }
QRadioButton[kbd="true"]::indicator:focus { border-color: %(focus)s; background: %(surface_3)s; }
QRadioButton[kbd="true"]::indicator:checked:focus { border-color: %(ink)s; }
QRadioButton[kbd="true"]:focus { color: %(accent_text)s; }

/* ---- scrollbars: thin, and out of the way ---- */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical {
    background: %(rule_2)s; border-radius: 3px; min-height: 32px;
}
QScrollBar::handle:vertical:hover { background: %(rule_strong)s; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal {
    background: %(rule_2)s; border-radius: 3px; min-width: 32px;
}
QScrollBar::handle:horizontal:hover { background: %(rule_strong)s; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

/* ---- progress ---- */
QProgressBar {
    background: %(surface_3)s; border: none; border-radius: 3px;
    height: 6px; text-align: center; color: transparent;
}
QProgressBar::chunk { background: %(accent)s; border-radius: 3px; }
QProgressBar[tone="done"]::chunk { background: %(done)s; border-radius: 3px; }
QProgressBar[tone="warn"]::chunk { background: %(warn)s; border-radius: 3px; }
QProgressBar[tone="bad"]::chunk { background: %(bad)s; border-radius: 3px; }

/* ---- lists and tables ---- */
QListWidget, QTreeWidget, QTableWidget {
    background: %(surface)s; border: 1px solid %(rule)s;
    border-radius: 10px; alternate-background-color: %(surface_2)s;
    font-size: 13px; padding: 4px;
}
QListWidget::item, QTreeWidget::item {
    padding: 7px 10px; border: none; border-radius: 6px;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background: %(surface_2)s; border-radius: 6px;
}
QListWidget::item:selected, QTreeWidget::item:selected,
QTableWidget::item:selected {
    background: %(surface_3)s; color: %(ink)s; border-radius: 6px;
}
QListWidget[kbd="true"]:focus, QTreeWidget[kbd="true"]:focus,
QTableWidget[kbd="true"]:focus {
    border-color: %(focus)s;
}
QHeaderView::section {
    background: transparent; border: none;
    border-bottom: 1px solid %(rule)s; padding: 8px 10px;
    font-size: 12px; font-weight: 600; color: %(ink_faint)s;
    letter-spacing: 0.3px;
}
QTableWidget { gridline-color: %(rule)s; }
QTableWidget::item { padding: 6px 10px; }

#SearchResults {
    background: %(surface)s; border: 1px solid %(rule_2)s;
    border-radius: 10px; padding: 6px;
}
#SearchResults::item { padding: 8px 10px; border-radius: 6px; }

/* ---- tabs ---- */
QTabWidget::pane { border: none; border-top: 1px solid %(rule)s; }
QTabBar::tab {
    background: transparent; padding: 8px 14px; color: %(ink_soft)s;
    font-size: 13px; font-weight: 600; border-bottom: 2px solid transparent;
    border-radius: 0;
}
QTabBar::tab:selected {
    color: %(ink)s; border-bottom-color: %(accent)s; border-radius: 0;
}
QTabBar::tab:hover { color: %(ink)s; border-radius: 0; }
QTabBar::tab:pressed { background: %(surface_2)s; border-radius: 0; }
QTabBar[kbd="true"]::tab:focus {
    color: %(ink)s; background: %(surface_3)s; border-radius: 0;
    border-bottom-color: %(focus)s;
}

/* ---- code ---- */
#Code, QPlainTextEdit[role="code"] {
    font-family: "%(mono)s"; font-size: 12.5px;
    background: %(code_bg)s; border: 1px solid %(rule)s; border-radius: 8px;
    padding: 10px; color: %(ink)s;
}
QPlainTextEdit[role="code"]:hover { border-color: %(rule_2)s; }
QPlainTextEdit[role="code"]:focus { border-color: %(focus)s; }

/* ---- pills: a tint, and the same hue as text ---- */
#Pill {
    background: %(surface_3)s; color: %(ink_soft)s; border-radius: 9px;
    padding: 2px 8px; font-size: 11px; font-weight: 700;
    letter-spacing: 0.4px; min-height: 14px;
}
#Pill[tone="accent"] { background: %(accent_subtle)s; color: %(accent_text)s; }
#Pill[tone="done"] { background: %(done_subtle)s; color: %(done_text)s; }
#Pill[tone="warn"] { background: %(warn_subtle)s; color: %(warn_text)s; }
#Pill[tone="bad"] { background: %(bad_subtle)s; color: %(bad_text)s; }

/* ---- chrome ---- */
QStatusBar { background: %(bg_2)s; border-top: 1px solid %(rule)s; }
QStatusBar::item { border: none; }
QStatusBar QLabel { font-size: 12px; color: %(ink_soft)s; padding: 0 8px; }
QMenuBar { background: %(bg_2)s; font-size: 12.5px; }
QMenuBar::item { padding: 5px 10px; border-radius: 5px; }
QMenuBar::item:selected { background: %(surface_3)s; border-radius: 5px; }
QMenuBar::item:pressed { background: %(surface_3)s; border-radius: 5px; }
QMenu {
    background: %(surface)s; border: 1px solid %(rule_2)s; padding: 6px;
    border-radius: 8px;
}
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 5px; }
QMenu::item:selected { background: %(surface_3)s; border-radius: 5px; }
QMenu::separator { height: 1px; background: %(rule)s; margin: 5px 6px; }
QSplitter::handle { background: transparent; }
QSlider::groove:horizontal {
    height: 4px; background: %(surface_3)s; border-radius: 2px;
}
QSlider::handle:horizontal {
    background: %(accent)s; width: 14px; margin: -5px 0; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: %(accent_hover)s; }
QSlider::handle:horizontal:pressed { background: %(accent_press)s; }
"""


def stylesheet(palette: Palette, scale: float = 1.0) -> str:
    """The whole sheet for one palette, with every font size scaled.

    The text-size setting used to grow only plain labels: headings, buttons
    and muted text are sized here in px, so a checklist line ended up larger
    than its own heading.
    """
    arrows = _arrow_images(palette)
    values = {
        "bg": palette.bg, "bg_2": palette.bg_2,
        "surface": palette.surface, "surface_2": palette.surface_2,
        "surface_3": palette.surface_3,
        "rule": palette.rule, "rule_2": palette.rule_2,
        "rule_strong": palette.rule_strong,
        "ink": palette.ink, "ink_soft": palette.ink_soft,
        "ink_faint": palette.ink_faint,
        "accent": palette.accent, "accent_hover": palette.accent_hover,
        "accent_press": palette.accent_press,
        "accent_text": palette.accent_text,
        "accent_subtle": palette.accent_subtle,
        "on_accent": palette.on_accent,
        "done": palette.done, "done_text": palette.done_text,
        "done_subtle": palette.done_subtle,
        "warn": palette.warn, "warn_text": palette.warn_text,
        "warn_subtle": palette.warn_subtle,
        "bad": palette.bad, "bad_text": palette.bad_text,
        "bad_subtle": palette.bad_subtle,
        "code_bg": palette.code_bg, "selection": palette.selection,
        "focus": palette.focus,
        "tooltip_bg": palette.tooltip_bg, "tooltip_ink": palette.tooltip_ink,
        "mono": mono_family(),
        "arrow_up": arrows["up"], "arrow_down": arrows["down"],
        "check_mark": _check_image(palette),
    }
    sheet = QSS % values
    if abs(scale - 1.0) > 1e-6:
        sheet = re.sub(
            r"font-size:\s*([\d.]+)px",
            lambda m: "font-size: %gpx" % round(float(m.group(1)) * scale, 1),
            sheet)
    return sheet


def scaled_px(size: float, scale: float) -> str:
    """For the few sizes set inline on a widget rather than in the sheet."""
    return "%gpx" % round(size * scale, 1)


def _check_image(palette: Palette) -> str:
    """The tick inside a checked box, in the theme's own ink.

    Qt ships one at
    `:/qt-project.org/styles/commonstyle/images/standardbutton-apply-16.png`
    and the sheet used to point at it: a bright green plate that covered the
    box whole, ignored the theme and looked nothing like the rest of the
    app. This draws the same stroke the rest of the interface uses, in the
    colour that belongs on a filled control.
    """
    import tempfile
    from pathlib import Path

    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QImage, QPainter, QPen

    colour = palette.on_accent
    folder = Path(tempfile.gettempdir()) / "operators-console-theme"
    target = folder / ("check-%s.png" % colour.lstrip("#"))
    if not target.exists():
        try:
            folder.mkdir(parents=True, exist_ok=True)
            image = QImage(32, 32, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(colour), 4.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline([QPointF(8, 16.5), QPointF(14, 22.5),
                                  QPointF(24, 10)])
            painter.end()
            image.save(str(target))
        except OSError:
            pass                # a plain filled box is plain, not broken
    return target.as_posix()


def _arrow_images(palette: Palette) -> dict:
    """Small arrows in the theme's own ink, as files the sheet can point at.

    Qt draws a sub-control's border as a rectangle, so the CSS triangle trick
    gives bars, and Qt's built-in arrow images are dark grey in either theme.
    Drawn at twice their size so they stay sharp when scaled; cached by
    colour in the temp folder.
    """
    import tempfile
    from pathlib import Path

    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QImage, QPainter, QPolygonF

    folder = Path(tempfile.gettempdir()) / "operators-console-theme"
    colour = palette.ink_soft
    shapes = {"up": ((2, 13), (10, 5), (18, 13)),
              "down": ((2, 5), (10, 13), (18, 5))}
    out = {}
    for name, points in shapes.items():
        target = folder / ("arrow-%s-%s.png" % (name, colour.lstrip("#")))
        if not target.exists():
            try:
                folder.mkdir(parents=True, exist_ok=True)
                image = QImage(20, 18, QImage.Format.Format_ARGB32)
                image.fill(Qt.GlobalColor.transparent)
                painter = QPainter(image)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(colour))
                painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))
                painter.end()
                image.save(str(target))
            except OSError:
                pass            # no arrows is ugly, not broken
        out[name] = target.as_posix()
    return out
