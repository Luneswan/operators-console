"""Main work is shown and counted; stretch work is folded and never counted.

Every checklist section used to be main, so a twelve-month portfolio target
held back the final phase's progress bar exactly like the ladder itself.
The curriculum now marks four stretch sections optional at the source
(build_tools/transform.py OPTIONAL_SECTIONS).
"""
from __future__ import annotations

from conftest import pump

from operators_console.core.progress import Progress
from operators_console.ui.widgets.common import CheckRow, Disclosure

OPTIONAL = {
    ("p05", "Challenge ladder"),
    ("p18", "Leverage"),
    ("p18", "Staying current after 2027"),
    ("p99", "Portfolio target — twelve months out"),
}


def test_exactly_the_decided_sections_are_optional(curriculum):
    marked = {(p.id, s.title) for p in curriculum.phases
              for s in p.sections if s.optional}
    assert marked == OPTIONAL


def test_the_week_by_week_work_is_main(curriculum):
    p01 = curriculum.phase("p01")
    assert p01.sections and not any(s.optional for s in p01.sections)


def test_optional_lines_do_not_count_toward_progress(curriculum, store):
    phase = curriculum.phase("p99")
    stretch = [i.id for s in phase.sections if s.optional for i in s.items]
    assert stretch
    assert not set(stretch) & set(phase.trackable_ids)
    progress = Progress(curriculum, store)
    before = progress.phase(phase)
    for item_id in stretch:
        store.set_checked(item_id, True)
    after = progress.phase(phase)
    assert (after.done, after.total) == (before.done, before.total)


def test_every_main_line_still_counts(curriculum):
    for phase in curriculum.phases:
        if phase.no_progress:
            continue
        main = [i.id for s in phase.sections if not s.optional
                for i in s.items]
        assert set(main) <= set(phase.trackable_ids), phase.id


def test_optional_sections_fold_on_the_phase_page(qt_app, window, curriculum):
    window.go("phase", "p18")
    pump(qt_app)
    view = window.views["phase"]
    folds = [d for d in view.findChildren(Disclosure)
             if "stretch goal" in d.words()[0]]
    assert len(folds) == 2
    for fold in folds:
        assert fold.tag is not None and fold.tag.text() == "OPTIONAL"
        assert fold.findChildren(CheckRow)       # still checkable inside
    # The two main sections are not folded.
    main_rows = [r for r in view.findChildren(CheckRow)
                 if not any(f.isAncestorOf(r) for f in folds)]
    phase = curriculum.phase("p18")
    main = sum(len(s.items) for s in phase.sections if not s.optional)
    gate = len(phase.gate.items) if phase.gate else 0
    assert len(main_rows) == main + gate
