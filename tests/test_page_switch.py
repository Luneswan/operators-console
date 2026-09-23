"""Switching pages is a lookup, not a rebuild.

The walkthrough measured 34 ms per page switch: the Phase page rebuilt every
check row on every visit, Today and Quiz redrew, the status line recomputed
the whole overview, and all eleven nav buttons were re-polished each time.
"""
from __future__ import annotations

from conftest import pump

from operators_console.ui.widgets.common import CheckRow


def _rows(window):
    return window.views["phase"].findChildren(CheckRow)


def test_a_phase_revisited_unchanged_keeps_its_rows(qt_app, window,
                                                     curriculum):
    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    first = _rows(window)[0]
    window.go("today", "")
    pump(qt_app)
    window.go("phase", "")
    pump(qt_app)
    assert _rows(window)[0] is first
    first.box.setChecked(True)          # a write: the next visit redraws
    pump(qt_app)
    window.go("today", "")
    pump(qt_app)
    window.go("phase", "")
    pump(qt_app)
    assert _rows(window)[0] is not first
    assert _rows(window)[0].box.isChecked()


def test_opening_another_phase_still_redraws(qt_app, window, curriculum):
    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    first = _rows(window)[0]
    window.go("phase", curriculum.phases[2].id)
    pump(qt_app)
    assert window.views["phase"].current_id == curriculum.phases[2].id
    assert _rows(window)[0] is not first


def test_the_status_line_is_recomputed_only_when_the_store_moved(
        qt_app, window, store, monkeypatch):
    window.go("roadmap", "")
    pump(qt_app)
    written = []
    monkeypatch.setattr(window.status_right, "setText",
                        lambda text: written.append(text))
    for _ in range(10):
        window.go("library", "")
        window.go("roadmap", "")
    pump(qt_app)
    assert written == []                      # nothing to recompute
    store.set_setting("learner_name", "Eve")  # any write moves the key
    window.go("library", "")
    pump(qt_app)
    assert len(written) == 1


def test_only_the_two_nav_buttons_that_change_are_repolished(qt_app, window):
    window.go("today", "")
    pump(qt_app)
    polished = []

    class Spy:
        def __init__(self, real, button):
            self.real, self.button = real, button

        def polish(self, target):
            polished.append(self.button)
            return self.real.polish(target)

        def unpolish(self, target):
            return self.real.unpolish(target)
    for button in window.nav_buttons.values():
        spy = Spy(button.style(), button)
        button.style = (lambda s=spy: s)
    window.go("roadmap", "")
    assert set(polished) == {window.nav_buttons["today"],
                             window.nav_buttons["roadmap"]}
