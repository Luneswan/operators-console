"""All twenty-one phases: every step, every resource, every gate line."""
from __future__ import annotations

import re

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_full]

MORE = re.compile(r"\b\d+\s+more\b", re.I)


def test_the_picker_and_the_arrows_reach_every_phase(walk_app, window,
                                                     curriculum):
    view = window.views["phase"]
    window.go("phase", curriculum.phases[0].id)
    pump(walk_app)
    with step(walk_app, "phase", "walk Next through all %d phases"
              % len(curriculum.phases), window):
        assert not view.prev_button.isEnabled()
        for expected in curriculum.phases[1:]:
            click(walk_app, view.next_button, pump_rounds=1)
            assert view.current_id == expected.id
        assert not view.next_button.isEnabled()
    with step(walk_app, "phase", "walk Previous back to the first phase",
              window):
        for expected in reversed(curriculum.phases[:-1]):
            click(walk_app, view.prev_button, pump_rounds=1)
            assert view.current_id == expected.id
        assert not view.prev_button.isEnabled()
    with step(walk_app, "phase", "choose every phase from the picker", window):
        for index, phase in enumerate(curriculum.phases):
            view.picker.setCurrentIndex(index)
            pump(walk_app, 1)
            assert view.current_id == phase.id
    REC.bump("phases reachable from the picker", len(curriculum.phases))


def test_every_phase_opens_and_shows_what_it_should(walk_app, window,
                                                    curriculum):
    from operators_console.ui.widgets.common import CheckRow, LinkRow
    from PySide6.QtWidgets import QPushButton

    view = window.views["phase"]
    disclosures = 0
    for phase in curriculum.phases:
        with step(walk_app, "phase", "open phase %s %s"
                  % (phase.num, phase.name), window):
            window.go("phase", phase.id)
            pump(walk_app, 2)
            assert view.current_id == phase.id
            assert view.title_label.text() == phase.name
            assert view.aim_label.text() == phase.aim
            rows = view.findChildren(CheckRow)
            expected = len(phase.items) + (len(phase.gate.items)
                                           if phase.gate else 0)
            assert len(rows) == expected, (
                "phase %s drew %d check rows for %d curriculum lines"
                % (phase.id, len(rows), expected))
            links = view.findChildren(LinkRow)
            assert len(links) == len(phase.resources), (
                "phase %s drew %d resource rows for %d resources"
                % (phase.id, len(links), len(phase.resources)))
            disclosures += len([b for b in view.findChildren(QPushButton)
                                if MORE.search(b.text() or "")])
        REC.bump("phases opened")
        REC.bump("phase check rows drawn", len(view.findChildren(CheckRow)))
    if not disclosures:
        REC.cannot_reach(
            'the "N more" resource disclosure',
            "PhaseView._fill_body draws one LinkRow per resource with no "
            "collapse, so no disclosure control exists in this revision of "
            "src/operators_console/ui/views/phase.py")


def test_every_step_in_every_phase_ticks_and_unticks(walk_app, window, store,
                                                     curriculum):
    from operators_console.ui.widgets.common import CheckRow
    view = window.views["phase"]
    ticked = 0
    for phase in curriculum.phases:
        window.go("phase", phase.id)
        pump(walk_app, 2)
        rows = {r.item_id: r for r in view.findChildren(CheckRow)}
        item_ids = [i.id for i in phase.items]
        with step(walk_app, "phase", "tick every study step in %s" % phase.num,
                  window):
            for item_id in item_ids:
                row = rows.get(item_id)
                assert row is not None, "%s has no row" % item_id
                row.box.setChecked(True)
                ticked += 1
            pump(walk_app, 1)
            missing = [i for i in item_ids if not store.is_checked(i)]
            assert not missing, missing
        with step(walk_app, "phase", "untick every study step in %s"
                  % phase.num, window):
            for item_id in item_ids:
                rows[item_id].box.setChecked(False)
            pump(walk_app, 1)
            still = [i for i in item_ids if store.is_checked(i)]
            assert not still, still
    REC.bump("study steps ticked and unticked", ticked)


def test_every_gate_can_be_cleared_and_reopened(walk_app, window, store,
                                                curriculum):
    from operators_console.ui.widgets.common import CheckRow
    view = window.views["phase"]
    gates = 0
    for phase in curriculum.phases:
        if not phase.gate:
            continue
        gates += 1
        window.go("phase", phase.id)
        pump(walk_app, 2)
        rows = {r.item_id: r for r in view.findChildren(CheckRow)}
        gate_ids = [i.id for i in phase.gate.items]
        with step(walk_app, "phase", "clear the gate on %s" % phase.num,
                  window):
            for gate_id in gate_ids:
                assert gate_id in rows, "%s has no row" % gate_id
                rows[gate_id].box.setChecked(True)
            pump(walk_app, 1)
            stats = window.ctx.progress.phase(phase)
            assert stats.gate_done == stats.gate_total, (
                phase.id, stats.gate_done, stats.gate_total)
        with step(walk_app, "phase", "reopen the gate on %s" % phase.num,
                  window):
            for gate_id in gate_ids:
                rows[gate_id].box.setChecked(False)
            pump(walk_app, 1)
            assert window.ctx.progress.phase(phase).gate_done == 0
    REC.bump("gates cleared and reopened", gates)


def test_every_resource_open_button_records_a_url_and_opens_nothing(
        walk_app, window, curriculum):
    from operators_console.ui.widgets.common import LinkRow
    from PySide6.QtWidgets import QPushButton
    view = window.views["phase"]
    before = len(REC.urls)
    total = 0
    for phase in curriculum.phases:
        if not phase.resources:
            continue
        window.go("phase", phase.id)
        pump(walk_app, 2)
        with step(walk_app, "phase", "open every resource in %s" % phase.num,
                  window):
            for row in view.findChildren(LinkRow):
                for widget in row.findChildren(QPushButton):
                    if widget.text() == "Open":
                        click(walk_app, widget, pump_rounds=0)
                        total += 1
    pump(walk_app)
    assert len(REC.urls) - before == total, (
        "%d Open presses produced %d URLs"
        % (total, len(REC.urls) - before))
    REC.bump("resource links opened", total)


def test_the_extras_on_a_phase_page_all_work(walk_app, window, curriculum):
    from operators_console.ui.widgets.common import CheckRow
    from PySide6.QtWidgets import QPushButton
    view = window.views["phase"]
    snippets = jumps = 0
    for phase in curriculum.phases:
        window.go("phase", phase.id)
        pump(walk_app, 2)
        with step(walk_app, "phase", "use the jump row and snippet on %s"
                  % phase.num, window):
            for index in range(view.jump_row.count()):
                item = view.jump_row.itemAt(index)
                widget = item.widget() if item is not None else None
                if isinstance(widget, QPushButton):
                    click(walk_app, widget, pump_rounds=1)
                    jumps += 1
                    window.go("phase", phase.id)
                    pump(walk_app, 1)
            copies = [b for b in view.findChildren(QPushButton)
                      if b.text() == "Copy"]
            for widget in copies:
                click(walk_app, widget, pump_rounds=1)
                snippets += 1
                from PySide6.QtWidgets import QApplication
                assert QApplication.clipboard().text() == phase.snippet
    REC.bump("phase jump buttons used", jumps)
    REC.bump("snippets copied", snippets)

    with step(walk_app, "phase", "send a line to the review deck from the "
                                 "right click menu", window):
        window.go("phase", "p01")
        pump(walk_app, 2)
        row = view.findChildren(CheckRow)[0]
        row.review_requested.emit(row.item_id)
        pump(walk_app)
        assert row.item_id in window.ctx.review.concept_ids()


def test_notes_survive_an_impatient_switch_on_every_phase(walk_app, window,
                                                          store, curriculum):
    """Type into every phase's notes box and leave before the save timer."""
    from .harness import wait_for
    view = window.views["phase"]
    with step(walk_app, "phase", "type a note in each phase and leave at once",
              window):
        for phase in curriculum.phases:
            window.go("phase", phase.id)
            pump(walk_app, 1)
            view.notes.setPlainText("note for %s" % phase.id)
        window.go("today", "")
        pump(walk_app, 2)

    def saved():
        return not [p.id for p in curriculum.phases
                    if store.note("phase:" + p.id) != "note for %s" % p.id]

    landed = wait_for(walk_app, saved, seconds=3)
    missing = [p.id for p in curriculum.phases
               if store.note("phase:" + p.id) != "note for %s" % p.id]
    if missing:
        REC.find("major", "phase", "notes lost when leaving a phase quickly",
                 "Type into the notes box on a phase and switch to another "
                 "page inside 600 ms; the text never reaches the store.",
                 "phases that lost the note: %s" % missing[:10])
    assert landed and not missing, missing

    with step(walk_app, "phase", "the pending note is committed on quit",
              window):
        window.go("phase", "p05")
        pump(walk_app, 1)
        view.notes.setPlainText("written a moment before quitting")
        window.close()
        pump(walk_app, 2)
    from operators_console.core.storage import Store
    reopened = Store()
    try:
        assert reopened.note("phase:p05") == "written a moment before quitting"
    finally:
        reopened.close()
