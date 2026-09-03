"""Drive the real widgets headlessly.

No pytest-qt: a single QApplication for the session is enough, and it keeps the
dependency list short enough to package without surprises.
"""
from __future__ import annotations

import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="session")
def qt_app():
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    yield app


@pytest.fixture
def window(qt_app, store, curriculum):
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow
    store.set_setting("onboarded", True)
    ctx = AppContext(store=store, curriculum=curriculum)
    main = MainWindow(ctx)
    main.show()
    qt_app.processEvents()
    yield main
    main.close()


def pump(app, rounds=3):
    for _ in range(rounds):
        app.processEvents()


def wait_for(app, predicate, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return True
        time.sleep(0.02)
    return False


def test_every_page_opens(qt_app, window):
    from operators_console.ui.main_window import NAV
    for key, _text, _factory in NAV:
        window.go(key, "")
        pump(qt_app)
        assert window.stack.currentWidget() is window.views[key]


def test_the_sidebar_marks_the_current_page(qt_app, window):
    window.go("roadmap", "")
    pump(qt_app)
    assert window.nav_buttons["roadmap"].property("active") is True
    assert window.nav_buttons["today"].property("active") is False


def test_ticking_a_line_is_saved_and_shown_again(qt_app, window, store):
    from operators_console.ui.widgets.common import CheckRow
    window.go("phase", "p01")
    pump(qt_app)
    rows = [r for r in window.views["phase"].findChildren(CheckRow)
            if r.item_id.startswith("p01.")]
    assert len(rows) > 10
    rows[0].box.setChecked(True)
    pump(qt_app)
    assert store.is_checked(rows[0].item_id)

    window.go("today", "")
    window.go("phase", "p01")
    pump(qt_app)
    again = [r for r in window.views["phase"].findChildren(CheckRow)
             if r.item_id == rows[0].item_id]
    assert again and again[0].box.isChecked()


def test_a_correct_submission_is_graded_in_the_interface(qt_app, window, store):
    window.go("practice", "p01.001")
    pump(qt_app)
    view = window.views["practice"]
    assert view.current.id == "p01.001"
    view.editor.set_code("def greet(name):\n    return f'Hello, {name}!'\n")
    view._run()
    assert wait_for(qt_app, lambda: view.run_button.isEnabled())
    assert store.exercise("p01.001")["status"] == "passed"
    # The results panel is populated even though the offscreen
    # platform reports every widget as hidden.
    assert view.results.box.count() > 0


def test_a_hanging_submission_does_not_freeze_the_interface(qt_app, window,
                                                            store):
    store.set_setting("exercise_timeout", 3)
    window.go("practice", "p01.008")
    pump(qt_app)
    view = window.views["practice"]
    view.editor.set_code("while True:\n    pass\n")
    view._run()
    assert wait_for(qt_app, lambda: view.run_button.isEnabled(), seconds=25)


def test_a_full_quiz_run_records_a_score(qt_app, window, store, curriculum):
    window.go("quiz", "q00")
    pump(qt_app)
    view = window.views["quiz"]
    total = len(view.order)
    for _ in range(total):
        question = view.quiz.questions[view.order[view.position]]
        view._answer(question.correct)
        pump(qt_app)
        view._advance()
        pump(qt_app)
    assert store.best_quiz_score("q00") == (total, total)


def test_review_presents_and_schedules_a_card(qt_app, window, store,
                                              curriculum):
    from operators_console.core.srs import Rating
    phase = curriculum.phase("p00")
    store.set_many_checked([i.id for i in phase.items][:3], True)
    window.go("review", "")
    pump(qt_app)
    view = window.views["review"]
    assert view.card is not None
    card_id = view.card.id
    view._apply(Rating.GOOD)
    pump(qt_app)
    assert store.memory(card_id).reps == 1


def test_search_finds_and_opens_a_result(qt_app, window):
    window.search.setText("decorator")
    pump(qt_app)
    assert window.results.count() > 0
    window._open_first_result()
    pump(qt_app)
    assert window.search.text() == ""


def test_switching_theme_restyles_without_error(qt_app, window, store):
    for theme in ("dark", "light", "system"):
        store.set_setting("theme", theme)
        window.ctx.refresh_palette()
        pump(qt_app)
    assert qt_app.styleSheet()


def test_changing_the_track_reshapes_the_roadmap(qt_app, window, store):
    window.go("settings", "")
    pump(qt_app)
    view = window.views["settings"]
    view.track.setCurrentIndex(view.track.findData("data"))
    pump(qt_app)
    assert store.setting("track") == "data"
    plan = window.ctx.progress.active_phase_ids()
    assert "p17" in plan and "p16" not in plan


def test_shipping_a_project_updates_the_store(qt_app, window, store):
    window.go("projects", "pj.p00.1")
    pump(qt_app)
    window.views["projects"]._set_status("pj.p00.1", "shipped")
    pump(qt_app)
    assert store.project("pj.p00.1")["status"] == "shipped"


def test_a_log_entry_updates_the_hours_and_the_streak(qt_app, window, store):
    window.go("journal", "")
    pump(qt_app)
    view = window.views["journal"]
    view.focus.setText("Generators")
    view.hours.setValue(2.5)
    view._save()
    pump(qt_app)
    assert store.total_hours() == 2.5
    assert store.streak()[0] >= 1


def test_the_onboarding_wizard_writes_a_plan(qt_app, window, store):
    from operators_console.ui.onboarding import Onboarding
    store.set_setting("onboarded", False)
    wizard = Onboarding(window.ctx, window)
    wizard.name.setText("Sam")
    wizard.goal_boxes["ai"].setChecked(True)
    wizard.hours.setValue(4.0)
    wizard.days.setValue(6)
    wizard._finish()
    pump(qt_app)
    assert store.setting("onboarded") is True
    assert store.setting("learner_name") == "Sam"
    assert store.setting("track") == "ai"
    assert store.setting("hours_per_day") == 4.0


def test_skipping_onboarding_still_leaves_a_usable_app(qt_app, window, store):
    from operators_console.ui.onboarding import Onboarding
    store.set_setting("onboarded", False)
    wizard = Onboarding(window.ctx, window)
    wizard._skip()
    pump(qt_app)
    assert store.setting("onboarded") is True
    window.go("today", "")
    pump(qt_app)
    assert window.ctx.today.build()


def test_rating_a_card_advances_by_exactly_one(qt_app, window, store,
                                               curriculum):
    """A card must never be consumed without being shown.

    Refreshing the page used to rebuild the queue mid-session, which quietly
    dropped whichever card was next.
    """
    from operators_console.core.srs import Rating

    phase = curriculum.phase("p00")
    store.set_many_checked([i.id for i in phase.items][:3], True)
    window.go("review", "")
    pump(qt_app)
    view = window.views["review"]

    planned = [card.id for card in window.ctx.review.session()]
    assert len(planned) >= 6

    shown = []
    for _ in range(5):
        assert view.card is not None
        shown.append(view.card.id)
        view._apply(Rating.GOOD)
        pump(qt_app)

    assert shown == planned[:len(shown)], (shown, planned)
    reviewed = {row["card_id"] for row in store.db.execute(
        "SELECT DISTINCT card_id FROM reviews")}
    assert reviewed == set(shown)


def test_returning_to_review_does_not_restart_the_session(qt_app, window,
                                                          store, curriculum):
    from operators_console.core.srs import Rating

    phase = curriculum.phase("p00")
    store.set_many_checked([i.id for i in phase.items][:3], True)
    window.go("review", "")
    pump(qt_app)
    view = window.views["review"]
    view._apply(Rating.GOOD)
    pump(qt_app)
    in_progress = view.card.id

    window.go("today", "")
    window.go("review", "")
    pump(qt_app)
    assert view.card.id == in_progress


def test_a_note_is_kept_when_you_switch_phase_immediately(qt_app, window,
                                                          store):
    window.go("phase", "p01")
    pump(qt_app)
    view = window.views["phase"]
    view.notes.setPlainText("Generators finally clicked.")
    # No waiting: switch straight away, as an impatient user would.
    window.go("phase", "p02")
    pump(qt_app)
    assert store.note("phase:p01") == "Generators finally clicked."
    assert store.note("phase:p02") == ""


def test_closing_the_window_commits_a_pending_note(qt_app, window):
    """Closing the window also closes the store, so read it back fresh."""
    from operators_console.core.storage import Store

    window.go("phase", "p03")
    pump(qt_app)
    window.views["phase"].notes.setPlainText("Packaging notes.")
    window.close()
    pump(qt_app)

    reopened = Store()
    try:
        assert reopened.note("phase:p03") == "Packaging notes."
    finally:
        reopened.close()
