"""Exercise prompts render their emphasis, and leave code alone."""
from operators_console.ui.views.practice import _markup


def test_single_asterisks_become_italics():
    assert "<i>distinct</i>" in _markup("the second largest *distinct* value")
    assert "*" not in _markup("the second largest *distinct* value")


def test_code_and_arithmetic_keep_their_asterisks():
    out = _markup("not `a*b*c` and not 2 * 3 * 4")
    assert "<code>a*b*c</code>" in out
    assert "2 * 3 * 4" in out


def test_no_shipped_prompt_shows_a_literal_emphasis_marker(curriculum):
    import re
    for exercise in curriculum.exercises:
        plain = re.sub(r"<code>.*?</code>", "", _markup(exercise.prompt))
        assert not re.search(r"(?<![\w*])\*[^*\s][^*]*?\*(?![\w*])", plain), \
            exercise.id


def test_a_failed_check_shows_its_code_as_code(qt_app, window, curriculum):
    from PySide6.QtWidgets import QLabel

    from conftest import pump
    from operators_console.core.runner import CaseResult, RunResult

    exercise = curriculum.exercises[0]
    window.go("practice", exercise.id)
    pump(qt_app)
    view = window.views["practice"]
    fields = RunResult.__dataclass_fields__
    result = RunResult(**{
        name: value for name, value in {
            "ok": False, "cases": (CaseResult(
                "plain case", False,
                "Your function returned None - is a `return` missing?"),),
            "stdout": "", "error": "", "duration_ms": 5,
        }.items() if name in fields})
    view._render_result(result) if hasattr(view, "_render_result") else None
    pump(qt_app)
    texts = [w.text() for w in view.results.findChildren(QLabel)]
    assert any("<code>return</code>" in t for t in texts), texts
    assert not any("`return`" in t for t in texts)
