"""Second round: no stray windows, folded optional resources, and contrast.

The flash test here is the one that matters. Before the fix, tearing a page
down called ``setParent(None)`` on widgets that were still laid out inside a
shown window. Qt promotes such a widget to a top-level ``Qt::Window``, gives
it a native handle and shows it, and it only goes away when the deferred
delete runs - which is the flicker of small windows opening and closing that
this suite now refuses to let back in.
"""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QWidget

from conftest import pump, wait_for


# ---------------------------------------------------------------------------
# the instrument
# ---------------------------------------------------------------------------

class WindowWatch(QObject):
    """Records every widget that is shown as a window of its own."""

    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        self.shown = []

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.Show and isinstance(obj, QWidget)
                and obj.isWindow() and obj is not self.main):
            self.shown.append((type(obj).__name__, obj.objectName(),
                               obj.parent() is None))
        return False

    @property
    def transient(self):
        """Windows that were never meant to be windows.

        The search popup and real dialogs carry Qt window flags on purpose;
        a card or a button appearing as a window never is.
        """
        allowed = {"QListWidget", "QMenu", "QDialog", "QMessageBox",
                   "Onboarding", "UpdateDialog", "QComboBoxPrivateContainer"}
        return [hit for hit in self.shown if hit[0] not in allowed]


def stray_windows(app, main):
    """Visible top-level widgets that are not the main window or a popup."""
    allowed = {"QListWidget", "QMenu", "QDialog", "QMessageBox",
               "Onboarding", "UpdateDialog", "QComboBoxPrivateContainer"}
    return sorted(type(w).__name__ for w in app.topLevelWidgets()
                  if w is not main and not w.isHidden()
                  and type(w).__name__ not in allowed)


@pytest.fixture
def watch(qt_app, window):
    probe = WindowWatch(window)
    qt_app.installEventFilter(probe)
    yield probe
    qt_app.removeEventFilter(probe)


# ---------------------------------------------------------------------------
# 1. no stray windows
# ---------------------------------------------------------------------------

def test_walking_every_page_opens_no_window_of_its_own(qt_app, window, watch):
    from operators_console.ui.main_window import NAV

    for key, _text, _factory in NAV:
        window.go(key, "")
        pump(qt_app)
        assert stray_windows(qt_app, window) == [], \
            "%s left a widget on screen as its own window" % key
    assert watch.transient == [], watch.transient


def test_revisiting_a_page_never_flashes_a_window(qt_app, window, watch):
    """The regression itself: a rebuild orphaned dozens of live widgets."""
    for phase_id in ("p01", "p02", "p03", "p01", "p02"):
        window.go("phase", phase_id)
        pump(qt_app)
        assert stray_windows(qt_app, window) == []
    for _ in range(3):
        window.go("library", "")
        window.go("today", "")
        window.go("stats", "")
        pump(qt_app)
    assert watch.transient == [], watch.transient


def test_the_search_popup_is_the_only_window_the_app_opens(qt_app, window,
                                                           watch):
    window.search.setText("decorator")
    pump(qt_app)
    assert window.results.count() > 0
    tops = [type(w).__name__ for w in qt_app.topLevelWidgets()
            if w is not window and not w.isHidden()]
    assert tops == ["QListWidget"], tops
    window.search.setText("")
    pump(qt_app)
    assert stray_windows(qt_app, window) == []
    assert watch.transient == [], watch.transient


def test_running_an_exercise_opens_no_window(qt_app, window, store, watch):
    window.go("practice", "p01.001")
    pump(qt_app)
    view = window.views["practice"]
    view.editor.set_code("def greet(name):\n    return f'Hello, {name}!'\n")
    view._run()
    assert wait_for(qt_app, lambda: view.run_button.isEnabled())
    assert stray_windows(qt_app, window) == []
    assert watch.transient == [], watch.transient


def test_onboarding_opens_exactly_one_window(qt_app, window, store, watch):
    from operators_console.ui.onboarding import Onboarding

    store.set_setting("onboarded", False)
    wizard = Onboarding(window.ctx, window)
    pump(qt_app)
    wizard._skip()
    pump(qt_app)
    assert watch.transient == [], watch.transient
    assert stray_windows(qt_app, window) == []


def test_teardown_hides_a_widget_before_it_is_detached(qt_app):
    """The mechanism, in isolation, so the reason is not lost."""
    from PySide6.QtWidgets import QPushButton, QVBoxLayout

    from operators_console.ui.widgets.common import discard

    host = QWidget()
    column = QVBoxLayout(host)
    victim = QPushButton("victim")
    column.addWidget(victim)
    host.show()
    pump(qt_app)
    assert not victim.isWindow()

    column.takeAt(0)
    discard(victim)
    pump(qt_app)
    assert not victim.isVisible(), "the orphan was left showing as a window"
    host.close()


# ---------------------------------------------------------------------------
# 2. optional resources, best one first
# ---------------------------------------------------------------------------

def test_every_optional_group_has_exactly_one_primary(curriculum):
    from operators_console.core.models import primary_of

    groups = []
    for phase in curriculum.phases:
        if phase.resources:
            groups.append(("phase " + phase.id, phase.resources,
                           phase.resources_optional))
    for group in curriculum.shelf:
        groups.append(("shelf " + group.group, group.items, group.optional))
    for group in curriculum.channels:
        groups.append(("channels " + group.group, group.items, group.optional))
    for field in curriculum.fields:
        if field.libs:
            groups.append(("field " + field.id, field.libs,
                           field.libs_optional))

    assert groups
    for name, items, optional in groups:
        marked = [i for i in items if getattr(i, "primary", False)]
        if optional:
            assert len(marked) == 1, \
                "%s: %d resources marked primary, expected 1" % (name,
                                                                 len(marked))
            assert primary_of(items) is marked[0]
        else:
            assert marked == [], "%s is not optional but marks a primary" % name


def test_gates_exercises_projects_and_steps_are_never_optional(curriculum):
    """Required work is never folded away, whatever the resources do."""
    for phase in curriculum.phases:
        for section in phase.sections:
            for item in section.items:
                assert not hasattr(item, "primary")
                assert not hasattr(item, "optional")
        if phase.gate:
            assert not hasattr(phase.gate, "optional")
    for exercise in curriculum.exercises:
        assert not hasattr(exercise, "optional")
    for project in curriculum.projects:
        assert not hasattr(project, "optional")


def test_a_phase_with_no_resources_is_not_marked_optional(curriculum):
    for phase in curriculum.phases:
        if not phase.resources:
            assert not phase.resources_optional


def test_split_optional_leaves_required_groups_whole(curriculum):
    from operators_console.core.models import split_optional

    phase = curriculum.phase("p00")
    shown, folded = split_optional(phase.resources, phase.resources_optional)
    assert len(shown) == 1 and shown[0].primary
    assert len(folded) == len(phase.resources) - 1

    shown, folded = split_optional(phase.resources, False)
    assert folded == ()
    assert len(shown) == len(phase.resources)


def test_the_phase_page_shows_the_primary_and_folds_the_rest(qt_app, window):
    from operators_console.ui.widgets.common import Disclosure, LinkRow

    window.go("phase", "p00")
    pump(qt_app)
    view = window.views["phase"]
    discs = view.findChildren(Disclosure)
    assert len(discs) == 1
    fold = discs[0]
    assert not fold.is_open
    assert fold.caption.text() == "4 more to study"

    rows = view.findChildren(LinkRow)
    visible = [r for r in rows if not r.isHidden()
               and not _inside_folded_body(r, fold)]
    assert len(visible) == 1
    assert visible[0].title.text() == "GitHub Skills — Introduction to Git"
    assert visible[0].title.property("lead") == "true"


def _inside_folded_body(widget, fold):
    parent = widget
    while parent is not None:
        if parent is fold.body:
            return True
        parent = parent.parent()
    return False


def test_collapsed_rows_are_hidden_and_cannot_be_tabbed_to(qt_app, window):
    from operators_console.ui.widgets.common import Disclosure

    window.go("phase", "p00")
    pump(qt_app)
    fold = window.views["phase"].findChildren(Disclosure)[0]
    assert not fold.body.isVisible()
    buttons = fold.body.findChildren(QWidget)
    focusable = [w for w in buttons
                 if w.focusPolicy() != Qt.FocusPolicy.NoFocus]
    assert focusable == [], \
        "a collapsed row can still be reached with Tab: %r" % focusable

    fold.set_open(True, animate=False)
    pump(qt_app)
    assert fold.body.isVisible()
    from PySide6.QtWidgets import QPushButton
    opens = [b for b in fold.body.findChildren(QPushButton)
             if b.text() == "Open"]
    assert opens and all(b.focusPolicy() != Qt.FocusPolicy.NoFocus
                         for b in opens)


def test_the_toggle_says_which_state_it_is_in(qt_app, window):
    from operators_console.ui.widgets.common import Disclosure

    window.go("phase", "p00")
    pump(qt_app)
    fold = window.views["phase"].findChildren(Disclosure)[0]

    caption, action = fold.words()
    assert caption == "4 more to study"
    assert action == "Show 4 more to study"
    assert fold.toggle.accessibleName() == caption

    fold.set_open(True, animate=False)
    caption, action = fold.words()
    assert caption == "Showing 4 more to study"
    assert action == "Hide the 4 optional ones"
    assert fold.toggle.toolTip() == action
    assert fold.toggle.property("open") == "true"


def test_enter_and_space_toggle_the_group(qt_app, window):
    from PySide6.QtGui import QKeyEvent
    from operators_console.ui.widgets.common import Disclosure

    window.go("phase", "p00")
    pump(qt_app)
    fold = window.views["phase"].findChildren(Disclosure)[0]
    assert not fold.is_open
    for key in (Qt.Key.Key_Return, Qt.Key.Key_Space, Qt.Key.Key_Enter):
        was = fold.is_open
        fold.keyPressEvent(
            QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))
        pump(qt_app)
        assert fold.is_open is (not was)


def test_an_opened_group_is_still_open_next_time(qt_app, window, store):
    from operators_console.ui.widgets.common import Disclosure

    window.go("phase", "p00")
    pump(qt_app)
    window.views["phase"].findChildren(Disclosure)[0].set_open(
        True, animate=False)
    pump(qt_app)
    assert store.disclosure_open("phase:p00") is True

    window.go("today", "")
    window.go("phase", "p00")
    pump(qt_app)
    again = window.views["phase"].findChildren(Disclosure)[0]
    assert again.is_open, "the group forgot that it had been opened"
    assert again.body.isVisible()


def test_reduced_motion_arrives_at_the_same_place_instantly(qt_app, window,
                                                            monkeypatch):
    from operators_console.ui.widgets import common
    from operators_console.ui.widgets.common import Disclosure

    monkeypatch.setattr(common, "reduced_motion", lambda: True)
    window.go("phase", "p01")
    pump(qt_app)
    fold = window.views["phase"].findChildren(Disclosure)[0]
    fold.set_open(True)
    assert fold.body.isVisible()
    assert fold.body.maximumHeight() > 0
    assert fold.chevron.get_angle() == 90.0
    fold.set_open(False)
    assert not fold.body.isVisible()
    assert fold.chevron.get_angle() == 0.0


def test_the_library_folds_its_shelves_and_channels(qt_app, window):
    from operators_console.ui.widgets.common import Disclosure

    window.go("library", "")
    pump(qt_app)
    view = window.views["library"]
    assert len(view.shelf_tab.findChildren(Disclosure)) == 7
    assert len(view.channels_tab.findChildren(Disclosure)) == 5
    assert view.fields_tab.findChildren(Disclosure)


# ---------------------------------------------------------------------------
# 3. the look
# ---------------------------------------------------------------------------

def _luminance(hex_colour: str) -> float:
    hex_colour = hex_colour.lstrip("#")
    channels = []
    for offset in (0, 2, 4):
        value = int(hex_colour[offset:offset + 2], 16) / 255.0
        channels.append(value / 12.92 if value <= 0.04045
                        else ((value + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(front: str, back: str) -> float:
    a, b = _luminance(front), _luminance(back)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


BODY_PAIRS = (
    ("ink", "paper"), ("ink", "shell"), ("ink", "paper_2"),
    ("ink", "code_bg"), ("ink_soft", "shell"), ("ink_soft", "paper_2"),
    ("ink_faint", "shell"), ("ink_faint", "paper_2"),
    ("accent", "paper"), ("accent", "shell"),
)
ON_ACCENT = ("accent", "accent_soft", "accent_press", "done", "warn", "bad")


@pytest.mark.parametrize("theme", ("light", "dark"))
def test_body_text_clears_four_and_a_half_to_one(theme):
    from operators_console.ui.theme import PALETTES

    palette = PALETTES[theme]
    for front, back in BODY_PAIRS:
        ratio = contrast(getattr(palette, front), getattr(palette, back))
        assert ratio >= 4.5, "%s: %s on %s is only %.2f:1" % (
            theme, front, back, ratio)


@pytest.mark.parametrize("theme", ("light", "dark"))
def test_text_on_a_filled_control_clears_four_and_a_half_to_one(theme):
    from operators_console.ui.theme import PALETTES

    palette = PALETTES[theme]
    for token in ON_ACCENT:
        ratio = contrast(palette.on_accent, getattr(palette, token))
        assert ratio >= 4.5, "%s: label on %s is only %.2f:1" % (
            theme, token, ratio)


@pytest.mark.parametrize("theme", ("light", "dark"))
def test_the_border_of_a_control_clears_three_to_one(theme):
    from operators_console.ui.theme import PALETTES

    palette = PALETTES[theme]
    for back in ("shell", "paper_2", "paper"):
        ratio = contrast(palette.rule_strong, getattr(palette, back))
        assert ratio >= 3.0, "%s: control border on %s is %.2f:1" % (
            theme, back, ratio)


@pytest.mark.parametrize("theme", ("light", "dark"))
def test_no_eleven_pixel_body_text(theme):
    """11px is a label size. Anything you have to read is 12px or more."""
    import re

    from operators_console.ui.theme import PALETTES, stylesheet

    sheet = stylesheet(PALETTES[theme])
    labels = ("#PageKicker", "#Pill", "#NavBadge", "#NavSection")
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", sheet):
        selector, body = block.group(1).strip(), block.group(2)
        size = re.search(r"font-size:\s*([\d.]+)px", body)
        if not size or float(size.group(1)) >= 12:
            continue
        assert any(tag in selector for tag in labels), \
            "%s sets %spx body text" % (selector, size.group(1))


@pytest.mark.parametrize("theme", ("light", "dark"))
def test_every_pressable_state_repeats_its_radius(theme):
    """A state rule that forgets the radius squares the corner on hover."""
    import re

    from operators_console.ui.theme import PALETTES, stylesheet

    sheet = stylesheet(PALETTES[theme])
    missing = []
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", sheet):
        selector, body = block.group(1).strip(), block.group(2)
        if not re.search(r":(hover|pressed|focus|checked|disabled)", selector):
            continue
        if "QPushButton" not in selector and "Disclosure" not in selector:
            continue
        if "border-radius" not in body:
            missing.append(selector)
    assert missing == [], missing


def test_pressing_a_button_never_moves_it(qt_app, window):
    """Press feedback is colour, not geometry."""
    import re

    from operators_console.ui.theme import PALETTES, stylesheet

    sheet = stylesheet(PALETTES["light"])
    for block in re.finditer(r"([^{}]+):pressed[^{]*\{([^{}]*)\}", sheet):
        body = block.group(2)
        assert "margin" not in body and "padding-top" not in body, \
            "pressed state moves the control: %s" % block.group(0)


def test_open_buttons_line_up_in_a_card(qt_app, window):
    from operators_console.ui.widgets.common import Disclosure, LinkRow

    window.go("phase", "p00")
    pump(qt_app)
    view = window.views["phase"]
    view.findChildren(Disclosure)[0].set_open(True, animate=False)
    pump(qt_app)
    lefts = {row.open_button.mapTo(view, row.open_button.rect().topLeft()).x()
             for row in view.findChildren(LinkRow)
             if row.open_button is not None and row.isVisible()}
    assert len(lefts) == 1, "Open buttons sit at %d different x positions" % len(lefts)


def test_the_sidebar_shows_which_page_you_are_on(qt_app, window):
    window.go("library", "")
    pump(qt_app)
    active = [key for key, b in window.nav_buttons.items()
              if b.property("active")]
    assert active == ["library"]


def test_an_empty_page_says_what_would_fill_it(qt_app, window):
    """A blank rectangle reads as a bug; a sentence reads as a state."""
    from operators_console.ui.widgets.common import empty_state

    card = empty_state("Nothing here yet.", "Finish a phase and it fills up.")
    lines = [w.text() for w in card.findChildren(QWidget)
             if hasattr(w, "text")]
    assert "Nothing here yet." in lines
    assert "Finish a phase and it fills up." in lines
    named = [w for w in card.findChildren(QWidget)
             if w.objectName() == "EmptyState"]
    assert named


def test_a_phase_with_nothing_in_it_falls_back_to_a_sentence(qt_app, window,
                                                             monkeypatch):
    from operators_console.core.models import Phase

    view = window.views["phase"]
    window.go("phase", "p01")
    pump(qt_app)
    bare = Phase(id="zz", num="zz", name="Bare", when="", aim="",
                 no_progress=True, est_hours=0, level=0, tags=(), prereq=(),
                 resources=(), sections=(), snippet="", gate=None)
    view._fill_body(bare)
    pump(qt_app)
    named = [w for w in view.findChildren(QWidget)
             if w.objectName() == "EmptyState"]
    assert named, "an empty phase rendered as a blank page"


def test_an_empty_review_deck_explains_itself(qt_app, window):
    window.go("review", "")
    pump(qt_app)
    view = window.views["review"]
    assert view.card is not None or view.stage.count() > 0


# ---------------------------------------------------------------------------
# 4. the update button
# ---------------------------------------------------------------------------

def _release(tag="v99.1.0", notes="Small fixes."):
    from operators_console.core.updates import Asset, Release, parse_version
    return Release(
        version=parse_version(tag), tag=tag, name="Release " + tag,
        notes=notes, url="https://example.invalid/r",
        assets=tuple(Asset(n, "https://example.invalid/" + n, 24 * 1024 * 1024)
                     for n in (
                         "operators-console-9.9.9-windows-setup.exe",
                         "operators-console-9.9.9-macos-arm64.dmg",
                         "operators-console-9.9.9-x86_64.AppImage")))


def test_the_update_button_is_absent_until_there_is_one(qt_app, window):
    assert not window.update_button.isVisible()
    assert window.update_button.release is None


def test_an_offer_names_the_version_and_its_size(qt_app, window, monkeypatch):
    from operators_console.core import updates

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")
    window._on_update_available(_release())
    pump(qt_app)
    button = window.update_button
    assert button.isVisibleTo(window.sidebar)
    assert button.text() == "Update to 99.1.0"
    assert "24 MB" in button.toolTip()
    assert button.isEnabled()


def test_the_download_states_are_words_not_just_a_bar(qt_app, window,
                                                      monkeypatch):
    from operators_console.core import updates

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")
    window._on_update_available(_release())
    button = window.update_button

    button._on_progress(6 * 1024 * 1024, 24 * 1024 * 1024)
    assert button.text() == "Downloading... 25%"
    assert "24 MB" in button.toolTip()
    button._on_progress(24 * 1024 * 1024, 24 * 1024 * 1024)
    assert button.text() == "Downloading... 100%"
    assert button.state == button.WORKING or button.state == button.IDLE


def test_a_failed_download_says_why_and_gives_the_offer_back(qt_app, window,
                                                             monkeypatch):
    from operators_console.core import updates

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")
    window._on_update_available(_release())
    button = window.update_button

    button._on_downloaded(None, "the server hung up")
    pump(qt_app)
    assert button.state == button.FAILED
    assert button.text() == "Try the update again"
    assert "the server hung up" in button.toolTip()
    assert "the server hung up" in window.update_note.text()
    assert window.update_note.isVisibleTo(window.sidebar)
    assert button.isEnabled(), "a failed update left a dead button"

    button._offer_again()
    assert button.text() == "Update to 99.1.0"
    assert button.state == button.IDLE
    assert not window.update_note.isVisible()


def test_a_release_with_nothing_for_this_platform_cannot_be_pressed(
        qt_app, window, monkeypatch):
    from operators_console.core import updates
    from operators_console.core.updates import Asset, Release, parse_version

    monkeypatch.setattr(updates.sys, "platform", "win32")
    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    release = Release(version=parse_version("v99.1.0"), tag="v99.1.0",
                      name="n", notes="", url="https://example.invalid/r",
                      assets=(Asset("something-else.tar.gz",
                                    "https://example.invalid/x", 10),))
    window._on_update_available(release)
    pump(qt_app)
    assert not window.update_button.isEnabled()


def test_reduced_motion_still_fills_the_meter(qt_app, window, monkeypatch):
    from operators_console.core import updates
    from operators_console.ui import updater

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")
    monkeypatch.setattr(updater, "reduced_motion", lambda: True)
    window._on_update_available(_release())
    button = window.update_button
    button.state = button.WORKING
    button._on_progress(12 * 1024 * 1024, 24 * 1024 * 1024)
    assert abs(button.get_fill() - 0.5) < 0.001
