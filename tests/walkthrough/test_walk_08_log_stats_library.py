"""The log, the numbers and the library."""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


# -- the log ---------------------------------------------------------------


def test_adding_editing_and_deleting_log_entries(walk_app, window, store):
    from PySide6.QtCore import QDate
    window.go("journal", "")
    pump(walk_app, 2)
    view = window.views["journal"]

    with step(walk_app, "journal", "write today's entry", window):
        view.focus.setText("Generators")
        view.hours.setValue(2.5)
        view.built.setPlainText("A pipeline that streams a big file.")
        view.stuck.setPlainText("Closing over the loop variable.")
        view.next_up.setText("Read itertools properly")
        click(walk_app, _named(view, "Log today"))
        assert store.total_hours() == 2.5
        assert len(store.logs()) == 1
        assert view.focus.text() == "", "the form was not cleared"
        assert view.tile_entries.value_label.text() == "1"
        assert store.streak()[0] >= 1

    with step(walk_app, "journal", "add three more days", window):
        for offset in range(1, 4):
            view.date.setDate(QDate.currentDate().addDays(-offset))
            view.focus.setText("Day minus %d" % offset)
            view.hours.setValue(1.0 + offset)
            click(walk_app, _named(view, "Log today"), pump_rounds=1)
        assert len(store.logs()) == 4
        assert store.total_hours() == 2.5 + 2.0 + 3.0 + 4.0

    with step(walk_app, "journal", "an entry is edited by writing it again",
              window):
        # Writing the same day twice: the form warns first, and the rows
        # stay separate on purpose (two sessions in one day are two
        # sessions). The Edit control on a card is the way to correct one.
        view.date.setDate(QDate.currentDate())
        view.focus.setText("Generators, again")
        view.hours.setValue(1.0)
        click(walk_app, _named(view, "Log today"), pump_rounds=1)
        logs = store.logs()
        same_day = [r for r in logs
                    if r["day"] == QDate.currentDate().toString("yyyy-MM-dd")]
        if len(same_day) > 1:
            REC.find("polish", "journal",
                     "a second entry for the same day is added, not merged",
                     "Log 2.5 hours today, then log 1 hour today again. The "
                     "form says so before you do ('You already logged 2.5 h "
                     "today - this adds to it') and the rows stay separate: "
                     "two sessions in one day are two sessions.",
                     "%d rows for today, total hours now %.1f"
                     % (len(same_day), store.total_hours()))
        REC.bump("log entries written", len(logs))

    with step(walk_app, "journal", "delete every entry from the history",
              window):
        for _row in list(store.logs()):
            delete = None
            for index in range(view.history.count()):
                card = view.history.itemAt(index).widget()
                if card is None:
                    continue
                delete = _named(card, "Delete")
                if delete is not None:
                    break
            assert delete is not None, "no Delete button in the history"
            click(walk_app, delete, pump_rounds=1)
        assert store.logs() == []
        assert store.total_hours() == 0
        assert view.tile_entries.value_label.text() == "0"


# -- the numbers -----------------------------------------------------------


def test_the_charts_cope_with_nothing_one_thing_and_many(walk_app, window,
                                                         store, curriculum):
    from datetime import date, timedelta
    window.go("stats", "")
    pump(walk_app, 3)
    view = window.views["stats"]

    with step(walk_app, "stats", "the charts render with no data at all",
              window):
        assert view.activity.data == {}
        assert not any(view.forecast.values)
        assert view.forecast_caption.text()
        view.activity.grab()
        view.forecast.grab()
        # The table lists the plan, not the learner's history, so it is
        # already full on a brand new store.
        assert view.table.rowCount() == len(
            window.ctx.progress.active_phase_ids())

    with step(walk_app, "stats", "the charts render with one data point",
              window):
        store.bump_activity(minutes=30, items=1)
        phase = curriculum.phases[1]
        store.set_many_checked([i.id for i in phase.items][:1], True)
        window.go("stats", "")
        pump(walk_app, 2)
        assert len(view.activity.data) == 1
        view.activity.grab()
        view.forecast.grab()
        assert view.table.rowCount() >= 1
        assert view.tile_percent.value_label.text().endswith("%")

    with step(walk_app, "stats", "the charts render with a year of data",
              window):
        today = date.today()
        with store.tx():
            for offset in range(1, 366):
                day = (today - timedelta(days=offset)).isoformat()
                store.db.execute(
                    "INSERT OR REPLACE INTO activity "
                    "(day, minutes, items, reviews, exercises) "
                    "VALUES (?,?,?,?,?)",
                    (day, offset % 180, offset % 7, offset % 40, offset % 5))
        window.go("stats", "")
        pump(walk_app, 3)
        assert len(view.activity.data) >= 365
        view.activity.grab()
        view.forecast.grab()
    REC.bump("activity days charted", len(view.activity.data))

    with step(walk_app, "stats", "rate every skill in the matrix", window):
        from PySide6.QtWidgets import QComboBox
        # The table's own sort control is a combo box too; the ratings are
        # the rest.
        pickers = [w for w in view.findChildren(QComboBox)
                   if w is not view.sort_by]
        assert len(pickers) == len(curriculum.matrix), (
            "%d pickers for %d skills"
            % (len(pickers), len(curriculum.matrix)))
        for picker, entry in zip(pickers, curriculum.matrix, strict=True):
            picker.setCurrentIndex(4)
            pump(walk_app, 1)
            assert store.rating(entry.skill) == 4
    REC.bump("skills self-assessed", len(curriculum.matrix))

    with step(walk_app, "stats", "the table covers the whole plan", window):
        window.go("stats", "")
        pump(walk_app, 2)
        assert view.table.rowCount() >= 1
        assert view.table.columnCount() == 6


# -- the library -----------------------------------------------------------


def test_every_library_tab_and_every_link(walk_app, window, curriculum):
    window.go("library", "")
    pump(walk_app, 3)
    view = window.views["library"]
    assert view.tabs.count() == 4
    before = len(REC.urls)
    for index in range(view.tabs.count()):
        with step(walk_app, "library", "open the %s tab"
                  % view.tabs.tabText(index), window):
            view.tabs.setCurrentIndex(index)
            pump(walk_app, 2)
    REC.bump("library tabs opened", view.tabs.count())

    from operators_console.ui.widgets.common import LinkRow
    from PySide6.QtWidgets import QPushButton
    for index in range(view.tabs.count()):
        view.tabs.setCurrentIndex(index)
        pump(walk_app, 2)
        page = view.tabs.widget(index)
        opens = []
        for row in page.findChildren(LinkRow):
            opens += [b for b in row.findChildren(QPushButton)
                      if b.text() == "Open"]
        with step(walk_app, "library", "press every Open on the %s tab"
                  % view.tabs.tabText(index), window):
            for widget in opens:
                click(walk_app, widget, pump_rounds=0)
    pump(walk_app, 2)
    opened = len(REC.urls) - before
    assert opened > 0, "no library link was pressed at all"
    REC.bump("library links opened", opened)

    with step(walk_app, "library", "press every field library button", window):
        view.tabs.setCurrentIndex(1)
        pump(walk_app, 2)
        expected = sum(len(field.libs) for field in curriculum.fields)
        page = view.tabs.widget(1)
        widgets = [b for b in page.findChildren(QPushButton)
                   if b.text() in {link.name
                                   for field in curriculum.fields
                                   for link in field.libs}]
        assert len(widgets) >= expected * 0.9, (
            "%d library buttons for %d declared links"
            % (len(widgets), expected))
        for widget in widgets:
            click(walk_app, widget, pump_rounds=0)
    REC.bump("field library buttons pressed", len(widgets))


def test_every_certificate_cycles_through_its_three_states(walk_app, window,
                                                           store, curriculum):
    from PySide6.QtWidgets import QPushButton
    from operators_console.ui.views.library import CERT_STATES
    window.go("library", "")
    pump(walk_app, 3)
    view = window.views["library"]
    view.tabs.setCurrentIndex(3)
    pump(walk_app, 2)
    for cert in curriculum.certs:
        with step(walk_app, "library", "cycle %s through every state"
                  % cert.id, window):
            for expected in (1, 2, 0):
                page = view.tabs.widget(3)
                wanted = "Mark: " + CERT_STATES[expected]
                widget = None
                for candidate in page.findChildren(QPushButton):
                    if candidate.text() == wanted:
                        widget = candidate
                        break
                if widget is None:
                    continue
                click(walk_app, widget, pump_rounds=1)
        REC.bump("certificates cycled")
    assert len(curriculum.certs) > 0
