# Interface changes: the flash, the fold, and the finish

Three things were wrong. Small windows opened and closed whenever you moved
between pages. Every phase opened with a wall of links where one would do.
And the palette had text nobody with ordinary eyes could read comfortably.

---

## 1. The flashing windows

### What you saw

Opening a page, or coming back to one, made a handful of small empty windows
appear at the corner of the screen and vanish again. It looked like the app
was shelling out to something.

### The root cause

It was not a subprocess. `core/runner.py` and `core/updates.py` already pass
`CREATE_NO_WINDOW`, and the grader child never touches Qt. The flash came
from the interface itself.

Every page tore itself down and rebuilt on each visit. The teardown looked
like this, duplicated eleven times across the views:

```python
while layout.count():
    item = layout.takeAt(0)
    widget = item.widget()
    if widget is not None:
        widget.setParent(None)      # <- here
        widget.deleteLater()
```

`setParent(None)` on a widget that is *currently laid out inside a shown
window* does not quietly detach it. Qt promotes it to a top-level
`Qt::Window`. Because the widget was already marked created and not hidden,
Qt gives it a real native window handle and shows it. It disappears only when
the deferred delete finally runs — one or more event-loop turns later.

Rebuilding a page orphans dozens of live widgets at once. That is the flicker.

### The evidence

An application-wide event filter counted every widget that received a `Show`
event while `isWindow()` was true, and every `WinIdChange` on a parentless
widget. Walking the eleven pages once and then switching phase twice, on the
real `windows` platform plugin with the main window kept off-screen:

```
STAGE go:today               clean
...
STAGE phase p02   [('WINID','QPushButton','Quiz'), ('SHOW','QPushButton','Quiz'),
                   ('WINID','QPushButton','Projects  1'), ('SHOW',...),
                   ('WINID','Card'), ('SHOW','Card'), ...]  count=16
```

Sixteen native windows created and shown for *one* phase switch. Across a full
session: 35 `Show`-as-window events, 35 parentless widgets given a native
handle, and 111 top-level widgets alive after four phase visits.

The same instrument on the `offscreen` platform reproduces it exactly, which
is what made it testable:

```
BEFORE: Show-as-window events: ['QPushButton','QPushButton','Card', ... ]  (35)
        visible stray top-levels: 35
AFTER : Show-as-window events: []
        visible stray top-levels: 0
```

### The fix

One shared teardown in `ui/widgets/common.py`, replacing all eleven copies:

```python
def discard(widget):
    widget.hide()          # sets WA_WState_Hidden + ExplicitShowHide
    widget.setParent(None) # ... so the detach that follows is silent
    widget.deleteLater()
```

Hiding first is what makes the promotion silent. Alongside it:

* `clear_layout()` — the single recursive teardown, used everywhere.
* `frozen(widget)` — a context manager that suspends painting while a subtree
  is rebuilt, so intermediate states never reach the screen.
* `Scroller.rebuilding()` — clear and refill a column with one repaint.
* `LibraryView` now builds its shelf, fields and channels **once** instead of
  on every visit, removing several hundred widget teardowns per trip.

The regression is locked down by `tests/test_ui_round2.py`, which walks every
page, the search popup, an exercise run and the onboarding wizard, and asserts
the visible top-level set is exactly `{main window}` (plus the search popup
while it is open). Putting the `hide()` back out makes four of those tests
fail immediately.

---

## 2. Optional resources: the best one, then the rest

Phase 00 opened with five links, four of them about GitHub. A learner starting
out does not need to choose between five things; they need the one that gets
them moving.

`src/operators_console/data/*.json` are generated, so the flags are produced
by the pipeline, not hand-edited into the bundle. Which resource leads is an
editorial judgement rather than something derivable from the data, so it is
hand-authored in **`build_tools/resource_picks.json`** — a group id to
resource name map — and applied by `build_tools/transform.py`. The generator
fails the build, loudly and specifically, on any of:

* a foldable group (two or more resources) with no pick;
* a pick naming a resource that does not exist, or that matches twice;
* a pick for a group too small to fold;
* a pick for a group that no longer exists.

`curriculum.json` was regenerated with the pipeline, and is byte-identical to
the previous bundle apart from the new flags and the `generated` date stamp.

The curriculum now carries two flags:

* `primary: true` on exactly one resource per group — the single thing to open
  first. Chosen by rule: interactive or course beats video; official docs are
  the primary only where nothing hands-on exists.
* `optional: true` (`resources_optional` / `libs_optional`) on the groups that
  may be folded: a phase's "Start here" list, the shelf, the channels, and a
  field's library list.

**Gates, exercises, projects and study steps carry neither flag and are never
folded.** A test asserts this.

The `Disclosure` widget shows the primary row in full and puts the rest behind
a quiet line: *"4 more to study"* with a chevron. It opens with a 180 ms
ease-out height reveal (interruptible — a second press finishes in proportion
to what is left), the chevron turns 90°, and the open state is remembered per
group so opening it once is enough. Enter and Space toggle it. Rows that are
folded away have their focus policy cleared, so Tab cannot reach an Open
button you cannot see. Under reduced motion the reveal is instant and the end
state identical.

---

## 3. The finish

Contrast was measured, not guessed. `#Muted` text failed 4.5:1 in *both*
themes; the light theme's `warn` fill failed against its own label. Tokens
were solved numerically and the results are asserted in tests.

---

## Before / After

| Before | After | Why |
| --- | --- | --- |
| `setParent(None)` on live widgets in 11 duplicated teardown helpers | one `discard()` that hides before detaching, plus `clear_layout()` | `setParent(None)` promotes a shown widget to a native top-level window — this was the flash |
| 35 stray windows shown per session; 111 top-levels after four phase visits | 0 stray windows; the main window and the search popup only | the user's "small windows open and close" |
| Every page rebuilt from scratch on every visit, painting each widget as it landed | `frozen()` / `Scroller.rebuilding()` suspend painting; Library builds its static tabs once | flicker you could see even without stray windows |
| Phase 00 "Start here": five links, four about GitHub | one primary row + "4 more to study ▾" | the one thing to do is obvious; the rest is one press away |
| No way to say a resource is optional | `primary` per resource, `optional` per group, validated in tests | gates, exercises, projects and steps are provably never folded |
| Folded content unreachable but still tab-focusable | focus policy cleared while collapsed, restored on open | a control you cannot see should not take focus |
| `#Muted` 11 px at 3.59:1 (light) / 4.09:1 (dark) | 12 px at 5.33:1 / 4.54:1 | body text you can actually read |
| Light `warn` fill 4.26:1 against its label | 4.52:1 | a label on a filled control needs 4.5:1 |
| Light primary hover `#C9714F` at 3.21:1 | `#BE4720` at 4.65:1 | the hover state was less readable than the resting one |
| One `rule` token used for both decoration and control borders (1.5:1) | `rule_strong` added at 3.56:1 / 3.07:1 for anything you can operate | WCAG 1.4.11 applies to control boundaries, not to decorative card edges |
| No pressed state on primary, good or bad buttons | `accent_press` token, pressed rules for every kind | press feedback on every pressable |
| Hover and focus rules dropped `border-radius`, squaring corners mid-interaction | radius repeated in every state rule, asserted by a test | no geometry change on press, no corner popping |
| Open buttons drifted left and right with the width of the kind pill | fixed 150 px trailing block, pill right-aligned | the buttons line up; a test asserts one x position |
| Update offer: a bare status-bar button opening a modal dialog | a sidebar button that becomes its own meter — "Downloading 24 MB… 62%", "Verifying…", "Restarting…" | nothing is blocked; the dialog is kept only for long release notes |
| A failed update left a dialog to dismiss | the button returns to the offer; the reason sits beneath it in words | a control that fails should not become a dead control |
| Empty pages rendered as blank rectangles | `empty_state()` says what would fill them | a blank page reads as a bug |
| No reduced-motion path | `reduced_motion()` honours `SPI_GETCLIENTAREAANIMATION` and an env override; every animation has an instant path to the same end state | motion is a preference, not a requirement |
| Shared Qt fixtures duplicated in the test module | `qt_app`, `window`, `pump`, `wait_for` in `conftest.py` | two UI test modules, one setup |
| A startup `QTimer.singleShot(2500, ...)` reached into the store after the window closed it | the timer is held on the window and stopped in `closeEvent`; `Store.is_open` guards the late call | closing the app in its first few seconds raised `Cannot operate on a closed database` |
| Spacing values of 5, 6, 7, 9, 10, 13, 14, 17, 18 px scattered across 13 files | normalised to a 4/8 px scale | one rhythm instead of thirteen |

---

## Files changed

* `core/models.py` — `primary` on `Resource`/`Link`/`ChannelItem`; `optional`
  on `Group`/`ChannelGroup`; `resources_optional` on `Phase`; `libs_optional`
  on `Field`; `primary_of()` and `split_optional()`.
* `core/curriculum.py` — reads the new fields, defaulting to off.
* `core/storage.py` — `disclosure_open()` / `set_disclosure_open()`.
* `build_tools/resource_picks.json` (new) — the editorial picks.
* `build_tools/transform.py` — emits `primary` / `optional` /
  `resources_optional` / `libs_optional`, and refuses to build on a bad pick.
* `data/curriculum.json` — regenerated by the pipeline.
* `ui/theme.py` — `rule_strong` and `accent_press` tokens, measured colour
  fixes, `reduced_motion()`, and a rewritten stylesheet.
* `ui/widgets/common.py` — `discard()`, `clear_layout()`, `frozen()`,
  `repolish()`, `empty_state()`, `Disclosure`, `_Chevron`, `_ToggleRow`, and a
  rewritten `LinkRow`.
* `ui/updater.py` — `UpdateButton`; the core engine is reached only through
  `updates.available()` / `download()` / `apply_and_restart()`, with the
  current names accepted as a fallback.
* `ui/main_window.py` — the update button moved into the sidebar.
* `ui/views/*.py` — eleven duplicated teardown helpers deleted; phase and
  library wired to `Disclosure`.
* `tests/conftest.py`, `tests/test_ui.py`, `tests/test_ui_round2.py`.
