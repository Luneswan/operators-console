"""The gaps the Log page left in the learner's own record.

Five of them, each one only visible after weeks of use: the history stopped
dead at sixty entries, an entry could be deleted but never corrected, the
delete was one unconfirmed click with nothing behind it, a second entry for
a day stacked silently onto the first, and the notes written on phase and
project pages could only ever be re-read one page at a time.
"""
from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLabel, QPushButton

from conftest import pump


# -- helpers ---------------------------------------------------------------


def _open(qt_app, window):
    window.go("journal", "")
    pump(qt_app)
    return window.views["journal"]


def _cards(layout) -> list:
    out = []
    for index in range(layout.count()):
        widget = layout.itemAt(index).widget()
        if widget is not None:
            out.append(widget)
    return out


def _button(root, text):
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def _texts(root) -> str:
    return "\n".join(w.text() for w in root.findChildren(QLabel))


def _day(offset: int) -> str:
    return (date.today() - timedelta(days=offset)).isoformat()


def _fill(store, count: int) -> None:
    for index in range(count):
        store.add_log(_day(index), "day %d" % index, 1.0, "", "", "")


# -- 1. the history no longer stops at sixty -------------------------------


def test_the_history_pages_past_sixty_entries(qt_app, window, store):
    _fill(store, 130)
    view = _open(qt_app, window)
    assert len(_cards(view.history)) == 60
    assert view.counter.text() == "130 entries, 60 shown"
    assert view.more.isEnabled()

    view.more.click()
    pump(qt_app)
    assert len(_cards(view.history)) == 120
    assert view.counter.text() == "130 entries, 120 shown"

    view.more.click()
    pump(qt_app)
    assert len(_cards(view.history)) == 130
    assert view.counter.text() == "130 entries, 130 shown"
    assert not view.more.isEnabled()


def test_the_counter_reads_naturally_for_a_single_entry(qt_app, window, store):
    store.add_log(_day(0), "generators", 1.0, "", "", "")
    view = _open(qt_app, window)
    assert view.counter.text() == "1 entry, 1 shown"
    assert not view.more.isEnabled()


def test_the_text_filter_searches_every_field_the_learner_wrote(
        qt_app, window, store):
    store.add_log(_day(0), "generators", 1.0, "", "", "")
    store.add_log(_day(1), "sockets", 1.0, "a parser for zebra logs", "", "")
    store.add_log(_day(2), "asyncio", 1.0, "", "closing over the loop", "")
    store.add_log(_day(3), "sqlite", 1.0, "", "", "read itertools properly")
    view = _open(qt_app, window)
    assert len(_cards(view.history)) == 4

    for needle, expected in (("GENERATORS", "generators"),
                             ("zebra", "sockets"),
                             ("loop", "asyncio"),
                             ("itertools", "sqlite")):
        view.filter.setText(needle)
        pump(qt_app)
        shown = _cards(view.history)
        assert len(shown) == 1, needle
        assert expected in _texts(shown[0])

    view.filter.setText("nothing was ever written about this")
    pump(qt_app)
    assert view.counter.text() == "0 of 4 entries match, 0 shown"
    assert "No entry matches that filter" in _texts(view)


def test_the_range_choice_hides_what_is_older(qt_app, window, store):
    store.add_log(_day(0), "this month", 1.0, "", "", "")
    store.add_log(_day(45), "six weeks back", 1.0, "", "", "")
    store.add_log(_day(200), "most of a year back", 1.0, "", "", "")
    view = _open(qt_app, window)
    assert len(_cards(view.history)) == 3          # "All" is the default

    view.range.setCurrentIndex(1)                  # Last 3 months
    pump(qt_app)
    assert len(_cards(view.history)) == 2
    assert "most of a year back" not in _texts(view)

    view.range.setCurrentIndex(0)                  # This month
    pump(qt_app)
    assert len(_cards(view.history)) == 1
    assert "six weeks back" not in _texts(view)

    view.range.setCurrentIndex(2)                  # All, again
    pump(qt_app)
    assert len(_cards(view.history)) == 3


def test_a_filter_starts_again_at_the_newest_entry(qt_app, window, store):
    _fill(store, 130)
    view = _open(qt_app, window)
    view.more.click()
    pump(qt_app)
    assert len(_cards(view.history)) == 120
    view.filter.setText("day")                     # still matches all of them
    pump(qt_app)
    assert len(_cards(view.history)) == 60


# -- 2. an entry can be corrected ------------------------------------------


def test_editing_loads_every_field_and_saves_as_one_undoable_step(
        qt_app, window, store):
    store.add_log(_day(2), "generators", 2.5, "a streaming pipeline",
                  "the loop variable", "read itertools")
    view = _open(qt_app, window)
    first_id = store.logs()[0]["id"]

    edit = _button(_cards(view.history)[0], "Edit")
    assert edit is not None, "no Edit button on a history card"
    edit.click()
    pump(qt_app)
    assert view.date.date().toString("yyyy-MM-dd") == _day(2)
    assert view.hours.value() == 2.5
    assert view.focus.text() == "generators"
    assert view.built.toPlainText() == "a streaming pipeline"
    assert view.stuck.toPlainText() == "the loop variable"
    assert view.next_up.text() == "read itertools"
    assert view.save.text() == "Save changes"
    assert view.cancel.isVisibleTo(view)

    view.focus.setText("generators, properly")
    view.hours.setValue(4.0)
    view.save.click()
    pump(qt_app)
    rows = store.logs()
    assert len(rows) == 1, "the edit added a row instead of replacing one"
    assert rows[0]["focus"] == "generators, properly"
    assert rows[0]["hours"] == 4.0
    assert rows[0]["built"] == "a streaming pipeline"
    assert rows[0]["id"] != first_id
    assert store.total_hours() == 4.0
    assert view.save.text() == "Log today"
    assert not view.cancel.isVisibleTo(view)

    # One step, not two: a single undo has to put the whole entry back.
    assert window.ctx.undo() == "edited entry"
    pump(qt_app)
    rows = store.logs()
    assert len(rows) == 1
    assert rows[0]["focus"] == "generators"
    assert rows[0]["hours"] == 2.5
    assert not window.ctx.history.can_undo

    window.ctx.redo()
    pump(qt_app)
    rows = store.logs()
    assert len(rows) == 1
    assert rows[0]["focus"] == "generators, properly"
    assert store.total_hours() == 4.0


def test_cancelling_an_edit_returns_the_form_to_logging(qt_app, window, store):
    store.add_log(_day(3), "generators", 2.5, "built it", "stuck on it",
                  "next thing")
    view = _open(qt_app, window)
    _button(_cards(view.history)[0], "Edit").click()
    pump(qt_app)
    assert view.save.text() == "Save changes"

    view.cancel.click()
    pump(qt_app)
    assert view.save.text() == "Log today"
    assert not view.cancel.isVisibleTo(view)
    assert view.focus.text() == ""
    assert view.built.toPlainText() == ""
    assert view.stuck.toPlainText() == ""
    assert view.next_up.text() == ""
    assert view.date.date() == QDate.currentDate()
    rows = store.logs()
    assert len(rows) == 1 and rows[0]["focus"] == "generators"


def test_a_plain_new_entry_is_undoable_too(qt_app, window, store):
    view = _open(qt_app, window)
    view.focus.setText("generators")
    view.hours.setValue(2.0)
    view.save.click()
    pump(qt_app)
    assert len(store.logs()) == 1
    window.ctx.undo()
    pump(qt_app)
    assert store.logs() == []
    assert store.total_hours() == 0
    window.ctx.redo()
    pump(qt_app)
    assert len(store.logs()) == 1
    assert store.total_hours() == 2.0


# -- 3. the delete can be taken back ---------------------------------------


def test_deleting_an_entry_is_undoable_and_says_so(qt_app, window, store):
    store.add_log(_day(1), "generators", 2.5, "built it", "stuck on it",
                  "next thing")
    view = _open(qt_app, window)
    said = []
    window.ctx.toast.connect(said.append)

    _button(_cards(view.history)[0], "Delete").click()
    pump(qt_app)
    assert store.logs() == []
    assert said[-1] == ("Deleted the entry for %s. Ctrl+Z brings it back."
                        % _day(1))

    window.ctx.undo()
    pump(qt_app)
    rows = store.logs()
    assert len(rows) == 1
    row = rows[0]
    assert (row["day"], row["focus"], row["hours"]) == (_day(1),
                                                        "generators", 2.5)
    assert (row["built"], row["stuck"], row["next_up"]) == (
        "built it", "stuck on it", "next thing")
    assert store.total_hours() == 2.5
    assert store.activity()[_day(1)]["minutes"] == 150

    window.ctx.redo()
    pump(qt_app)
    assert store.logs() == []
    assert store.total_hours() == 0


def test_deleting_the_entry_being_edited_drops_the_edit(qt_app, window, store):
    store.add_log(_day(0), "generators", 2.5, "", "", "")
    view = _open(qt_app, window)
    _button(_cards(view.history)[0], "Edit").click()
    pump(qt_app)
    assert view.save.text() == "Save changes"
    _button(_cards(view.history)[0], "Delete").click()
    pump(qt_app)
    assert store.logs() == []
    assert view.save.text() == "Log today"
    assert not view.cancel.isVisibleTo(view)


# -- 4. a second entry for one day is no longer a surprise -----------------


def test_a_second_entry_for_the_same_day_is_flagged_first(qt_app, window,
                                                          store):
    view = _open(qt_app, window)
    assert not view.dup.isVisibleTo(view)

    store.add_log(date.today().isoformat(), "generators", 2.5, "", "", "")
    window.go("today", "")
    window.go("journal", "")
    pump(qt_app)
    assert view.dup.isVisibleTo(view)
    assert view.dup_text.text() == (
        "You already logged 2.5 h today - this adds to it")

    # Editing that entry replaces it, so the warning stands down.
    _button(_cards(view.history)[0], "Edit").click()
    pump(qt_app)
    assert not view.dup.isVisibleTo(view)
    view.cancel.click()
    pump(qt_app)
    assert view.dup.isVisibleTo(view)


def test_the_warning_names_the_day_when_an_old_one_is_backfilled(
        qt_app, window, store):
    store.add_log(_day(4), "generators", 1.5, "", "", "")
    view = _open(qt_app, window)
    assert not view.dup.isVisibleTo(view)
    view.date.setDate(QDate.currentDate().addDays(-4))
    pump(qt_app)
    assert view.dup_text.text() == (
        "You already logged 1.5 h on %s - this adds to it" % _day(4))


# -- 5. the notes are readable in one place --------------------------------


def test_the_notes_section_lists_phase_and_project_notes(qt_app, window,
                                                         store, curriculum):
    phase = curriculum.phases[1]
    project = curriculum.projects[0]
    store.set_note("phase:" + phase.id, "Iterators finally clicked.")
    store.set_note("phase:no-such-phase", "orphaned")
    store.set_note("something:else", "not a phase note")
    store.set_project(project.id, notes="The parser needs a real tokeniser.")

    view = _open(qt_app, window)
    cards = _cards(view.notes)
    assert len(cards) == 2, "expected exactly the phase and the project note"
    written = _texts(view)
    assert phase.name in written and project.title in written
    assert "Iterators finally clicked." in written
    assert "The parser needs a real tokeniser." in written
    assert "not a phase note" not in written

    seen = []
    window.ctx.navigate.connect(lambda k, t: seen.append((k, t)))
    for widget in [_button(card, "Open") for card in cards]:
        assert widget is not None, "a note with no way back to its page"
        widget.click()
        pump(qt_app)
    assert ("phase", phase.id) in seen
    assert ("projects", project.id) in seen


def test_the_notes_section_says_what_would_fill_it(qt_app, window):
    view = _open(qt_app, window)
    assert len(_cards(view.notes)) == 1
    assert ("Notes you write on phase and project pages collect here."
            in _texts(view))


def test_the_filter_searches_the_notes_as_well(qt_app, window, store,
                                               curriculum):
    phase = curriculum.phases[1]
    project = curriculum.projects[0]
    store.set_note("phase:" + phase.id, "Iterators finally clicked.")
    store.set_project(project.id, notes="The parser needs a real tokeniser.")
    view = _open(qt_app, window)

    view.filter.setText("tokeniser")
    pump(qt_app)
    cards = _cards(view.notes)
    assert len(cards) == 1
    assert project.title in _texts(cards[0])

    view.filter.setText(phase.name)
    pump(qt_app)
    assert len(_cards(view.notes)) == 1

    view.filter.setText("zzzz")
    pump(qt_app)
    assert "No note matches that filter." in _texts(view)


def test_a_long_note_is_clipped_rather_than_filling_the_page(
        qt_app, window, store, curriculum):
    phase = curriculum.phases[1]
    store.set_note("phase:" + phase.id, "word " * 400)
    view = _open(qt_app, window)
    bodies = [w.text() for w in _cards(view.notes)[0].findChildren(QLabel)]
    assert any(text.endswith("...") and len(text) <= 250 for text in bodies)


# -- the redraw key --------------------------------------------------------


def test_a_revisit_redraws_only_when_something_it_shows_moved(qt_app, window,
                                                              store):
    store.add_log(_day(0), "generators", 1.0, "", "", "")
    view = _open(qt_app, window)
    first = _cards(view.history)[0]
    window.go("today", "")
    window.go("journal", "")
    pump(qt_app)
    assert _cards(view.history)[0] is first     # nothing moved: no rebuild

    view.filter.setText("gen")                  # the filter is part of the key
    pump(qt_app)
    second = _cards(view.history)[0]
    assert second is not first

    view.range.setCurrentIndex(0)               # so is the range
    pump(qt_app)
    assert _cards(view.history)[0] is not second
