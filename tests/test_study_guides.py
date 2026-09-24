"""Every checklist line says how to do it, where to learn it and how to tell
it is done.

Owner, 09-24: "the weeks are just check marks, can make them lost. You can
add how to, where to learn or some other data, just flesh everything out
more so it's easy and useful to follow".
"""
from __future__ import annotations

import re

from conftest import pump

FLUFF = re.compile(r"\b(simply|just|easily|you'll love|pro tip)\b|!",
                   re.IGNORECASE)


def _lines(curriculum):
    return [i for p in curriculum.phases for s in p.sections for i in s.items]


def test_every_line_has_a_complete_guide(curriculum):
    missing = [i.id for i in _lines(curriculum)
               if not (i.how and i.done and 1 <= len(i.where) <= 2)]
    assert missing == []


def test_every_section_says_how_to_work_through_it(curriculum):
    missing = [s.id for p in curriculum.phases for s in p.sections
               if not s.guide]
    assert missing == []


def test_guide_links_are_https_pages(curriculum):
    bad = [(i.id, link.url) for i in _lines(curriculum) for link in i.where
           if not link.url.startswith("https://") or " " in link.url
           or not link.name]
    assert bad == []


def test_guides_stay_short_enough_to_read(curriculum):
    long = [i.id for i in _lines(curriculum)
            if len(i.how) > 360 or len(i.done) > 200]
    long += [s.id for p in curriculum.phases for s in p.sections
             if len(s.guide) > 440]
    assert long == []


def test_guides_are_written_flat(curriculum):
    """The owner asked for direct wording with no fluff, everywhere."""
    fluffy = [i.id for i in _lines(curriculum)
              if FLUFF.search(i.how) or FLUFF.search(i.done)]
    fluffy += [s.id for p in curriculum.phases for s in p.sections
               if FLUFF.search(s.guide)]
    assert fluffy == []


def test_a_guide_adds_to_its_line_rather_than_repeating_it(curriculum):
    same = [i.id for i in _lines(curriculum)
            if i.how.strip().lower() == i.text.strip().lower()]
    assert same == []


# -- the page ------------------------------------------------------------------

def _guided(window, qt_app, phase_id="p01"):
    from operators_console.ui.widgets.guide import GuidedItem
    window.go("phase", phase_id)
    pump(qt_app)
    return window.views["phase"].scroller.body.findChildren(GuidedItem)


def test_the_next_step_opens_with_its_guide(qt_app, window, curriculum):
    guided = _guided(window, qt_app)
    opened = [g for g in guided if g.is_open]
    assert [g.item.id for g in opened] == [curriculum.phase("p01").items[0].id]
    assert opened[0].next_step


def test_how_opens_and_closes_one_guide(qt_app, window):
    guided = _guided(window, qt_app)[3]
    assert not guided.is_open
    assert guided.panel is None             # built only when first opened
    guided.toggle_link.linkActivated.emit("how")
    assert guided.is_open
    assert "Hide" in guided.toggle_link.text()
    guided.toggle()
    assert not guided.is_open


def test_show_all_guides_is_remembered(qt_app, window):
    view = window.views["phase"]
    guided = _guided(window, qt_app)
    view.guides_button.click()
    assert all(g.is_open for g in guided if g.has_guide)
    assert window.ctx.store.setting("guides_open") is True
    view.guides_button.click()
    assert window.ctx.store.setting("guides_open") is False


def test_learn_it_links_open_in_the_browser(qt_app, window, monkeypatch):
    from PySide6.QtWidgets import QLabel
    from operators_console.ui.widgets import common
    opened = []
    monkeypatch.setattr(common, "open_url", opened.append)
    guided = _guided(window, qt_app)[0]
    where = [w for w in guided.panel.findChildren(QLabel)
             if "Learn it" in w.text()][0]
    where.linkActivated.emit(guided.item.where[0].url)
    assert opened == [guided.item.where[0].url]


def test_the_row_menu_offers_the_guide(qt_app, window):
    guided = _guided(window, qt_app)[2]
    menu = guided.row.build_menu()
    assert "Show or hide how to do this" in [a.text() for a in menu.actions()]
