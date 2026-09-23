"""The log: what you did, what broke, what is next.

The history used to stop dead at sixty entries with no way past it, an entry
could only ever be deleted - instantly, unrecoverably - and the notes written
on twenty-one phase pages and twenty-two project pages could only be re-read
one page at a time. This page now carries the whole record: a filter and a
range over the history, an editable entry, an undoable delete, a warning
before a second entry stacks onto a day, and every note in one list.
"""
from __future__ import annotations


from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QVBoxLayout,
)

from ...core.textmatch import matches as _text_matches
from ..widgets.common import (
    Card, StatTile, button, clear_layout, divider, heading, label, muted,
    pill,
)
from .base import View

#: Entries drawn before "Show older" has to be pressed, and per press after.
PAGE = 60

#: Enough rows that no learner reaches the end of the record.
ALL = 20000

#: The range choices, in the order they are offered.
RANGES = ("This month", "Last 3 months", "All")


def _fields(row) -> tuple:
    """The six values `Store.add_log` takes, in its own order."""
    return (row["day"], row["focus"] or "", float(row["hours"] or 0.0),
            row["built"] or "", row["stuck"] or "", row["next_up"] or "")


def _matches(row, query: str) -> bool:
    """Does every word of the query appear somewhere in this entry?

    Through core.textmatch, like every other box in the app: case, accents,
    dashes and extra spaces never decide it, and word order does not matter.
    """
    return _text_matches(query, row["focus"], row["built"], row["stuck"],
                         row["next_up"])


def _clip(text: str, limit: int = 240) -> str:
    """A note's opening, on one line, so the list stays scannable."""
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit].rstrip() + "..."


class JournalView(View):
    title = "Log"

    #: Set again by `build`; here so a callback that outlives the widgets -
    #: an undo arriving after a teardown - still finds them.
    _window = PAGE
    _editing = None

    def build(self) -> None:
        self.header("Log", "daily log",
                    "Hours logged here set the pace estimate on Today.")

        self._window = PAGE
        self._editing = None

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.tile_hours = StatTile("0", "Hours logged")
        self.tile_entries = StatTile("0", "Entries")
        self.tile_streak = StatTile("0", "Day streak")
        self.tile_best = StatTile("0", "Longest streak")
        for tile in (self.tile_hours, self.tile_entries, self.tile_streak,
                     self.tile_best):
            stats_row.addWidget(tile)
        self.scroller.add_layout(stats_row)

        form = Card()
        self.form_title = heading("Add an entry")
        form.add(self.form_title)

        # A second entry for the same day is added, not merged, and the hours
        # add up. That is sometimes what the learner wants; it should never be
        # a surprise, so the page says so before the entry is written.
        self.dup = Card(flat=True, padding=10, spacing=6)
        dup_row = QHBoxLayout()
        dup_row.setSpacing(8)
        dup_row.addWidget(pill("HEADS UP", "warn"))
        self.dup_text = label("", "Soft", wrap=True)
        dup_row.addWidget(self.dup_text, 1)
        self.dup.box.addLayout(dup_row)
        self.dup.setVisible(False)
        form.add(self.dup)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 72)
        # The slack goes to a spare column, so date and hours sit together
        # on the left instead of the hours being pushed to the far edge.
        grid.setColumnStretch(4, 1)
        self._default_day = QDate.currentDate()
        self.date = QDateEdit(self._default_day)
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setAccessibleName("Date of the entry")
        grid.addWidget(muted("DATE"), 0, 0)
        grid.addWidget(self.date, 0, 1)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.0, 24.0)
        self.hours.setSingleStep(0.5)
        self.hours.setValue(float(self.ctx.store.setting("hours_per_day", 3.0)))
        self.hours.setSuffix(" h")
        self.hours.setAccessibleName("Hours worked")
        grid.addWidget(muted("HOURS"), 0, 2)
        grid.addWidget(self.hours, 0, 3)
        self.focus = QLineEdit()
        self.focus.setPlaceholderText("What was today about?")
        self.focus.setAccessibleName("Focus")
        grid.addWidget(muted("FOCUS"), 1, 0)
        grid.addWidget(self.focus, 1, 1, 1, 4)
        form.box.addLayout(grid)

        self.built = QPlainTextEdit()
        self.built.setPlaceholderText("What did you build or fix?")
        self.built.setFixedHeight(60)
        self.built.setAccessibleName("What you built")
        form.add(self.built)
        self.stuck = QPlainTextEdit()
        self.stuck.setPlaceholderText("Where did you get stuck, and why?")
        self.stuck.setFixedHeight(60)
        self.stuck.setAccessibleName("Where you got stuck")
        form.add(self.stuck)
        self.next_up = QLineEdit()
        self.next_up.setPlaceholderText("First thing tomorrow")
        self.next_up.setAccessibleName("First thing tomorrow")
        form.add(self.next_up)

        self.cancel = button("Cancel", "quiet")
        self.cancel.setToolTip("Leave the entry as it was")
        self.cancel.clicked.connect(self._cancel_edit)
        self.cancel.setVisible(False)
        self.save = button("Log today", "primary")
        self.save.clicked.connect(self._save)
        form.add_row(None, self.cancel, self.save)
        self.scroller.add(form)

        self.scroller.add(divider())
        self.scroller.add(heading("History"))

        find_row = QHBoxLayout()
        find_row.setSpacing(8)
        find_row.addWidget(muted("FIND"))
        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            "Search focus, built, stuck and next")
        self.filter.setClearButtonEnabled(True)
        self.filter.setAccessibleName("Filter the log and the notes")
        find_row.addWidget(self.filter, 1)
        find_row.addWidget(muted("SHOW"))
        self.range = QComboBox()
        self.range.addItems(RANGES)
        self.range.setCurrentIndex(len(RANGES) - 1)     # nothing hidden by default
        self.range.setAccessibleName("How far back to show")
        find_row.addWidget(self.range)
        self.scroller.add_layout(find_row)

        more_row = QHBoxLayout()
        more_row.setSpacing(8)
        self.more = button("Show older", "quiet")
        self.more.setToolTip("Another %d entries" % PAGE)
        self.more.clicked.connect(self._show_older)
        more_row.addWidget(self.more)
        self.counter = muted("")
        more_row.addWidget(self.counter, 1)
        self.scroller.add_layout(more_row)

        self.history = QVBoxLayout()
        self.history.setSpacing(8)
        self.scroller.add_layout(self.history)

        self.scroller.add(divider())
        self.scroller.add(heading("Your notes"))
        self.scroller.add(muted(
            "Notes from phase and project pages. The filter above searches "
            "these too."))
        self.notes = QVBoxLayout()
        self.notes.setSpacing(8)
        self.scroller.add_layout(self.notes)
        self.scroller.add_stretch()

        # Connected last, so no handler can fire against a half-built page.
        self.filter.textChanged.connect(lambda *_: self._filter_changed())
        self.range.currentIndexChanged.connect(lambda *_: self._filter_changed())
        self.date.dateChanged.connect(lambda *_: self._sync_form_hint())

    # -- lifecycle ---------------------------------------------------------

    def refresh(self) -> None:
        # Left open past midnight, the form still offered yesterday and the
        # next entry was filed there. Follow the calendar - unless the learner
        # picked another date on purpose.
        today = QDate.currentDate()
        if self._default_day != today:
            if self.date.date() == self._default_day:
                self.date.setDate(today)
            self._default_day = today
        key = self._draw_key(today)
        if self.store_unchanged(*key):
            return
        grew = self._only_opened_wider(key)
        store = self.ctx.store
        logs = store.logs(ALL)
        if grew:
            # Nothing changed but how far the window is open, so the cards
            # already on screen still stand: draw the new page and stop.
            # Rebuilding all of them cost a tenth of a second a press and
            # threw away the scroll position with it.
            self._extend_history(logs)
            self.mark_drawn(*key)
            return
        current, longest = store.streak()
        self.tile_hours.set_value("%.0f" % store.total_hours())
        self.tile_entries.set_value(str(len(logs)))
        self.tile_streak.set_value(str(current))
        self.tile_best.set_value(str(longest))
        self._sync_form_hint(logs)
        self._fill_history(logs)
        self._fill_notes()
        self.mark_drawn(*key)

    def save_state(self):
        return {"filter": self.filter.text(),
                "range": self.range.currentIndex()}

    def restore_state(self, state) -> None:
        index = int(state.get("range", len(RANGES) - 1))
        if 0 <= index < self.range.count():
            self.range.setCurrentIndex(index)
        self.filter.setText(state.get("filter", ""))

    def _only_opened_wider(self, key: tuple) -> bool:
        """True when the sole change since the last draw is a wider window."""
        previous = self._drawn_key
        if previous is None:
            return False
        whole = self._key(key)
        if previous[:3] != whole[:3]:
            return False                    # the store moved underneath us
        before, now = previous[3], whole[3]
        return (before[:3] == now[:3] and before[4] == now[4]
                and now[3] > before[3])

    def _draw_key(self, today: QDate) -> tuple:
        """What the page drew from, beyond the store itself.

        The filter, the range, how far the window has been opened and which
        entry is being edited all change what is on screen without touching
        the store, so each has to be part of the key that decides whether a
        revisit can skip its redraw.
        """
        return (today.toJulianDay(), " ".join(self.filter.text().split()),
                self.range.currentIndex(), self._window, self._editing)

    # -- the history -------------------------------------------------------

    def _cutoff(self, today: QDate) -> str:
        """The earliest day the chosen range shows, or "" for all of them."""
        index = self.range.currentIndex()
        if index == 0:
            return today.toString("yyyy-MM-01")
        if index == 1:
            return today.addMonths(-3).toString("yyyy-MM-dd")
        return ""

    def _kept(self, logs) -> list:
        needle = self.filter.text()
        cutoff = self._cutoff(QDate.currentDate())
        return [row for row in logs
                if _matches(row, needle)
                and (not cutoff or (row["day"] or "") >= cutoff)]

    def _sync_counter(self, logged: int, total: int, shown: int) -> None:
        """How big the log is, how much of it matches, and how much is drawn.

        While a filter or a range is on, the size of the whole log is said
        too: "2 of 20 entries match, 2 shown". Without it the learner had no
        idea how much record the filter was hiding.
        """
        noun = "entry" if logged == 1 else "entries"
        if self._narrowed():
            self.counter.setText("%d of %d %s match, %d shown"
                                 % (total, logged, noun, shown))
        else:
            self.counter.setText("%d %s, %d shown" % (total, noun, shown))
        hidden = total - shown
        self.more.setEnabled(hidden > 0)
        if hidden:
            self.more.setToolTip("Another %d of the %d still hidden"
                                 % (min(PAGE, hidden), hidden))
        else:
            self.more.setToolTip("Every entry is already shown")

    def _extend_history(self, logs) -> None:
        """Add the page just asked for; the rest is already on screen."""
        kept = self._kept(logs)
        for row in kept[self.history.count():self._window]:
            self.history.addWidget(self._entry_card(row))
        self._sync_counter(len(logs), len(kept),
                           min(self._window, len(kept)))

    def _narrowed(self) -> bool:
        """True while the text box or the range hides any part of the log."""
        return bool(self.filter.text().split()) or bool(
            self._cutoff(QDate.currentDate()))

    def _fill_history(self, logs) -> None:
        clear_layout(self.history)
        kept = self._kept(logs)
        shown = kept[:self._window]
        self._sync_counter(len(logs), len(kept), len(shown))
        if not shown:
            card = Card()
            if logs:
                card.add(muted("No entry matches that filter. Widen the range "
                               "or clear the box above."))
            else:
                card.add(muted("No entries yet."))
            self.history.addWidget(card)
            return
        for row in shown:
            self.history.addWidget(self._entry_card(row))

    def _entry_card(self, row) -> Card:
        card = Card(padding=12, spacing=5)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(pill(row["day"]))
        top.addWidget(label(row["focus"] or "(no focus recorded)", "RowTitle"),
                      1)
        if row["id"] == self._editing:
            top.addWidget(pill("EDITING", "accent"))
        top.addWidget(muted("%.1f h" % row["hours"]))
        edit = button("Edit", "quiet")
        edit.setToolTip("Load this entry back into the form above")
        edit.clicked.connect(lambda _=False, i=row["id"]: self._edit(i))
        top.addWidget(edit)
        delete = button("Delete", "quiet")
        delete.setToolTip("Remove it. Ctrl+Z brings it back.")
        delete.clicked.connect(lambda _=False, i=row["id"]: self._delete(i))
        top.addWidget(delete)
        card.box.addLayout(top)
        if row["built"]:
            card.add(label("Built: " + row["built"], "Soft"))
        if row["stuck"]:
            card.add(label("Stuck: " + row["stuck"], "Soft"))
        if row["next_up"]:
            card.add(muted("Next: " + row["next_up"]))
        return card

    def _filter_changed(self) -> None:
        self._window = PAGE         # a new question starts at the newest entry
        self.refresh()

    def _show_older(self) -> None:
        self._window += PAGE
        self.refresh()

    # -- the notes ---------------------------------------------------------

    def _note_entries(self) -> list:
        """Every note the learner has written: (name, body, view, target)."""
        store = self.ctx.store
        out = []
        written = store.all_notes()
        for scope in sorted(written):
            if not scope.startswith("phase:"):
                continue
            body = (written[scope] or "").strip()
            phase = self.ctx.curriculum.phase(scope.split(":", 1)[1])
            if not body or phase is None:
                continue
            out.append((phase.name, body, "phase", phase.id))
        for project in self.ctx.curriculum.projects:
            body = (store.project(project.id)["notes"] or "").strip()
            if body:
                out.append((project.title, body, "projects", project.id))
        return out

    def _fill_notes(self) -> None:
        clear_layout(self.notes)
        needle = self.filter.text()
        written = self._note_entries()
        kept = [entry for entry in written
                if _text_matches(needle, entry[0], entry[1])]
        if not kept:
            card = Card()
            if written:
                card.add(muted("No note matches that filter."))
            else:
                card.add(muted("Notes you write on phase and project pages "
                               "collect here."))
            self.notes.addWidget(card)
            return
        for name, body, view_key, target in kept:
            self.notes.addWidget(self._note_card(name, body, view_key, target))

    def _note_card(self, name: str, body: str, view_key: str,
                   target: str) -> Card:
        card = Card(padding=12, spacing=5)
        top = QHBoxLayout()
        top.setSpacing(8)
        is_phase = view_key == "phase"
        top.addWidget(pill("PHASE" if is_phase else "PROJECT",
                           "accent" if is_phase else "done"))
        top.addWidget(label(name, "RowTitle"), 1)
        open_it = button("Open", "quiet")
        open_it.setToolTip("Go to %s" % name)
        open_it.clicked.connect(
            lambda _=False, k=view_key, t=target: self.ctx.navigate.emit(k, t))
        top.addWidget(open_it)
        card.box.addLayout(top)
        card.add(label(_clip(body), "Soft"))
        return card

    # -- the form ----------------------------------------------------------

    def _sync_form_hint(self, logs=None) -> None:
        """Say so when this day already has hours on it."""
        if logs is None:
            logs = self.ctx.store.logs(ALL)
        day = self.date.date().toString("yyyy-MM-dd")
        hours = sum(float(row["hours"] or 0.0) for row in logs
                    if row["day"] == day and row["id"] != self._editing)
        if hours <= 0:
            self.dup.setVisible(False)
            self.dup_text.setText("")
            return
        when = ("today" if day == QDate.currentDate().toString("yyyy-MM-dd")
                else "on " + day)
        self.dup_text.setText(
            "You already logged %.1f h %s - this adds to it" % (hours, when))
        self.dup.setVisible(True)

    def _set_mode(self) -> None:
        """The one submit button says which of the two things it will do."""
        editing = self._editing is not None
        self.form_title.setText("Edit an entry" if editing else "Add an entry")
        self.save.setText("Save changes" if editing else "Log today")
        self.cancel.setVisible(editing)

    def _clear_form(self) -> None:
        self.focus.clear()
        self.built.clear()
        self.stuck.clear()
        self.next_up.clear()

    def _form_values(self) -> tuple:
        return (self.date.date().toString("yyyy-MM-dd"),
                self.focus.text().strip(), self.hours.value(),
                self.built.toPlainText().strip(),
                self.stuck.toPlainText().strip(), self.next_up.text().strip())

    def _edit(self, log_id: int) -> None:
        row = self._row(log_id)
        if row is None:
            return
        self._editing = log_id
        day, focus, hours, built, stuck, next_up = _fields(row)
        picked = QDate.fromString(day, "yyyy-MM-dd")
        if picked.isValid():
            self.date.setDate(picked)
        self.hours.setValue(hours)
        self.focus.setText(focus)
        self.built.setPlainText(built)
        self.stuck.setPlainText(stuck)
        self.next_up.setText(next_up)
        self._set_mode()
        self.focus.setFocus()
        self.ctx.announce("Editing the entry for %s." % day)
        self.refresh()

    def _cancel_edit(self) -> None:
        self._editing = None
        self._clear_form()
        self.date.setDate(QDate.currentDate())
        self._set_mode()
        self.refresh()

    # -- writing, and taking it back ---------------------------------------

    def _row(self, log_id: int):
        for row in self.ctx.store.logs(ALL):
            if row["id"] == log_id:
                return row
        return None

    def _add_back(self, state: dict, data: tuple) -> None:
        """Write the row again. It gets a new id, which the pair remembers."""
        state["id"] = self.ctx.store.add_log(*data)
        self.ctx.changed()
        self._redraw()

    def _drop(self, state: dict) -> None:
        self.ctx.store.delete_log(state["id"])
        self.ctx.changed()
        self._redraw()

    def _swap(self, state: dict, data: tuple) -> None:
        """An edit is a delete and an add - as one step, either way round."""
        store = self.ctx.store
        store.delete_log(state["id"])
        state["id"] = store.add_log(*data)
        self.ctx.changed()
        self._redraw()

    def _redraw(self) -> None:
        """Undo can arrive long after the page was torn down."""
        if self._built:
            self.refresh()

    def _save(self) -> None:
        data = self._form_values()
        editing = self._editing
        old = self._row(editing) if editing is not None else None
        before = _fields(old) if old is not None else None
        if before is None:
            editing = self._editing = None      # the row went while we held it
        if editing is None:
            state = {"id": self.ctx.store.add_log(*data)}
            self.ctx.record("log entry",
                            lambda: self._drop(state),
                            lambda: self._add_back(state, data))
            message = "Logged."
        else:
            state = {"id": editing}
            self._swap(state, data)
            self.ctx.record("edited entry",
                            lambda: self._swap(state, before),
                            lambda: self._swap(state, data))
            self._editing = None
            self._set_mode()
            message = "Saved the changes. Ctrl+Z puts them back."
        self._clear_form()
        self.ctx.changed()
        self.ctx.announce(message)
        self.refresh()

    def _delete(self, log_id: int) -> None:
        row = self._row(log_id)
        if row is None:
            return
        data = _fields(row)
        state = {"id": log_id}
        self.ctx.store.delete_log(log_id)
        if self._editing == log_id:
            self._editing = None
            self._set_mode()
        self.ctx.record("deleted entry",
                        lambda: self._add_back(state, data),
                        lambda: self._drop(state))
        self.ctx.changed()
        self.ctx.announce("Deleted the entry for %s. Ctrl+Z brings it back."
                          % data[0])
        self.refresh()
