# Walkthrough of Operator's Console

A single learner's pass through every page, every control and every piece of content, driven through the real widgets with QTest and watched by a net of sensors.

- Generated: 2026-09-24 14:09
- Platform: Windows-11-10.0.26200-SP0, Python 3.14.5, Qt offscreen
- Runtime: 8 min 43 s
- Steps recorded: 2098
- Findings: 8
- Unhandled exceptions seen: 0
- Qt warnings and criticals: 1
- Dialogs answered: 35
- URLs intercepted (none opened): 1019
- pytest exit status: 0

## Findings

| id | severity | view | what happened | how to reproduce |
| --- | --- | --- | --- | --- |
| W-01 | major | roadmap | step blocks for 3250 ms: open every phase outside the plan | Open roadmap and open every phase outside the plan; the interface is frozen for 3.2 s. |
| W-02 | major | navigation | step blocks for 5528 ms: switch pages 200 times as fast as the event loop allows | Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 5.5 s. |
| W-03 | major | phase | step blocks for 5760 ms: walk Next through all 35 phases | Open phase and walk Next through all 35 phases; the interface is frozen for 5.8 s. |
| W-04 | major | phase | step blocks for 5592 ms: walk Previous back to the first phase | Open phase and walk Previous back to the first phase; the interface is frozen for 5.6 s. |
| W-05 | major | phase | step blocks for 3917 ms: choose every phase from the picker | Open phase and choose every phase from the picker; the interface is frozen for 3.9 s. |
| W-06 | major | phase | step blocks for 4850 ms: type a note in each phase and leave at once | Open phase and type a note in each phase and leave at once; the interface is frozen for 4.8 s. |
| W-08 | minor | settings | unexpected dialog during: the report buttons open the form | Open settings and the report buttons open the form. |
| W-07 | polish | journal | a second entry for the same day is added, not merged | Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions. |

### W-01 - step blocks for 3250 ms: open every phase outside the plan

- **Severity**: major
- **View**: roadmap
- **Repro**: Open roadmap and open every phase outside the plan; the interface is frozen for 3.2 s.

### W-02 - step blocks for 5528 ms: switch pages 200 times as fast as the event loop allows

- **Severity**: major
- **View**: navigation
- **Repro**: Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 5.5 s.

### W-03 - step blocks for 5760 ms: walk Next through all 35 phases

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Next through all 35 phases; the interface is frozen for 5.8 s.

### W-04 - step blocks for 5592 ms: walk Previous back to the first phase

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Previous back to the first phase; the interface is frozen for 5.6 s.

### W-05 - step blocks for 3917 ms: choose every phase from the picker

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and choose every phase from the picker; the interface is frozen for 3.9 s.

### W-06 - step blocks for 4850 ms: type a note in each phase and leave at once

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and type a note in each phase and leave at once; the interface is frozen for 4.8 s.

### W-08 - unexpected dialog during: the report buttons open the form

- **Severity**: minor
- **View**: settings
- **Repro**: Open settings and the report buttons open the form.

```
[('dialog', 'FeedbackDialog', 'Report a problem or request a feature'), ('dialog', 'FeedbackDialog', 'Report a problem or request a feature'), ('dialog', 'FeedbackDialog', 'Report a problem or request a feature')]
```

### W-07 - a second entry for the same day is added, not merged

- **Severity**: polish
- **View**: journal
- **Repro**: Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions.

```
2 rows for today, total hours now 12.5
```

## Coverage of the interface

Every `button(...)`, `QPushButton(...)`, `QAction(...)` and `setShortcut(...)` under `src/` is counted. A control counts as hit when the walk activated the widget built by that exact source line.

- Controls declared: **133**
- Activated by the walk: **116** (87%)

| kind | declared | hit | % |
| --- | --- | --- | --- |
| action | 16 | 13 | 81% |
| button | 106 | 93 | 88% |
| shortcut | 11 | 10 | 91% |

<details><summary>Every control, hit or not</summary>

| file | line | kind | label | hit |
| --- | --- | --- | --- | --- |
| operators_console/ui/feedback.py | 73 | button | Copy text | yes |
| operators_console/ui/feedback.py | 77 | button | Cancel | yes |
| operators_console/ui/feedback.py | 80 | button | Open on GitHub | yes |
| operators_console/ui/main_window.py | 149 | button | Close | yes |
| operators_console/ui/main_window.py | 361 | button | Undo | yes |
| operators_console/ui/main_window.py | 367 | button | Redo | yes |
| operators_console/ui/main_window.py | 407 | action | Quit | yes |
| operators_console/ui/main_window.py | 408 | shortcut | StandardKey.Quit | yes |
| operators_console/ui/main_window.py | 429 | action | Undo | yes |
| operators_console/ui/main_window.py | 430 | shortcut | StandardKey.Undo | yes |
| operators_console/ui/main_window.py | 433 | action | Redo | yes |
| operators_console/ui/main_window.py | 434 | shortcut | <_redo_keys()> | yes |
| operators_console/ui/main_window.py | 439 | action | Find | yes |
| operators_console/ui/main_window.py | 440 | shortcut | Ctrl+K | yes |
| operators_console/ui/main_window.py | 445 | action | Start or stop studying | yes |
| operators_console/ui/main_window.py | 446 | shortcut | Ctrl+T | yes |
| operators_console/ui/main_window.py | 449 | action | Pause or resume studying | yes |
| operators_console/ui/main_window.py | 450 | shortcut | Ctrl+Shift+T | yes |
| operators_console/ui/main_window.py | 455 | action | How this app works | yes |
| operators_console/ui/main_window.py | 458 | action | Keyboard shortcuts | yes |
| operators_console/ui/main_window.py | 459 | shortcut | F1 | yes |
| operators_console/ui/main_window.py | 462 | action | Report a problem or request a feature... | yes |
| operators_console/ui/main_window.py | 465 | action | Check for updates | yes |
| operators_console/ui/main_window.py | 468 | action | About | yes |
| operators_console/ui/main_window.py | 568 | action | New profile... | NO |
| operators_console/ui/main_window.py | 571 | action | Manage profiles... | NO |
| operators_console/ui/main_window.py | 289 | button | <text> | yes |
| operators_console/ui/main_window.py | 401 | action | <text> | yes |
| operators_console/ui/main_window.py | 415 | action | <text> | yes |
| operators_console/ui/main_window.py | 560 | action | <name> | NO |
| operators_console/ui/main_window.py | 404 | shortcut | <QKeySequence()> | NO |
| operators_console/ui/main_window.py | 417 | shortcut | Ctrl+%d | yes |
| operators_console/ui/main_window.py | 421 | shortcut | Ctrl+0 | yes |
| operators_console/ui/main_window.py | 424 | shortcut | Ctrl+, | yes |
| operators_console/ui/onboarding.py | 162 | button | Skip for now | yes |
| operators_console/ui/onboarding.py | 167 | button | Back | yes |
| operators_console/ui/onboarding.py | 171 | button | Continue | yes |
| operators_console/ui/session_dialog.py | 134 | button | Discard | yes |
| operators_console/ui/session_dialog.py | 138 | button | Keep going | yes |
| operators_console/ui/session_dialog.py | 141 | button | Save to log | yes |
| operators_console/ui/shortcuts.py | 90 | button | Close | yes |
| operators_console/ui/snapshots.py | 72 | button | Open the backups folder | yes |
| operators_console/ui/snapshots.py | 77 | button | Cancel | yes |
| operators_console/ui/snapshots.py | 80 | button | Restore this snapshot | yes |
| operators_console/ui/updater.py | 220 | button | Open the releases page | yes |
| operators_console/ui/updater.py | 224 | button | Not now | yes |
| operators_console/ui/updater.py | 227 | button | Update and restart | yes |
| operators_console/ui/views/dashboard.py | 235 | button | <computed> | yes |
| operators_console/ui/views/dashboard.py | 244 | button | Not today | yes |
| operators_console/ui/views/dashboard.py | 260 | button | Start | yes |
| operators_console/ui/views/dashboard.py | 329 | button | Open this phase | yes |
| operators_console/ui/views/dashboard.py | 381 | button | Export report | yes |
| operators_console/ui/views/dashboard.py | 384 | button | Keep reviewing | yes |
| operators_console/ui/views/dashboard.py | 388 | button | Change track | yes |
| operators_console/ui/views/journal.py | 144 | button | Cancel | yes |
| operators_console/ui/views/journal.py | 148 | button | Log today | yes |
| operators_console/ui/views/journal.py | 175 | button | Show older | yes |
| operators_console/ui/views/journal.py | 349 | button | Edit | yes |
| operators_console/ui/views/journal.py | 353 | button | Delete | yes |
| operators_console/ui/views/journal.py | 422 | button | Open | yes |
| operators_console/ui/views/library.py | 533 | button | <computed> | yes |
| operators_console/ui/views/library.py | 439 | button | <name> | yes |
| operators_console/ui/views/library.py | 538 | button | Open | NO |
| operators_console/ui/views/library.py | 456 | button | <name> | yes |
| operators_console/ui/views/phase.py | 43 | button | Previous | yes |
| operators_console/ui/views/phase.py | 44 | button | Next | yes |
| operators_console/ui/views/phase.py | 262 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 268 | button | Quiz | yes |
| operators_console/ui/views/phase.py | 274 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 319 | button | <dynamic> | yes |
| operators_console/ui/views/phase.py | 372 | button | Copy | yes |
| operators_console/ui/views/practice.py | 222 | button | Run checks | yes |
| operators_console/ui/views/practice.py | 227 | button | Stop | yes |
| operators_console/ui/views/practice.py | 232 | button | Hint | yes |
| operators_console/ui/views/practice.py | 235 | button | Reset | yes |
| operators_console/ui/views/practice.py | 238 | button | Show solution | yes |
| operators_console/ui/views/practice.py | 242 | button | Next | yes |
| operators_console/ui/views/practice.py | 253 | button | Restore my passing version | yes |
| operators_console/ui/views/practice.py | 258 | button | Try this one again from scratch | yes |
| operators_console/ui/views/practice.py | 776 | button | Where this is taught | yes |
| operators_console/ui/views/projects.py | 108 | button | Open | yes |
| operators_console/ui/views/projects.py | 141 | button | <computed> | yes |
| operators_console/ui/views/projects.py | 135 | button | <text> | yes |
| operators_console/ui/views/projects.py | 444 | button | Show every project | yes |
| operators_console/ui/views/quiz.py | 241 | button | Start | yes |
| operators_console/ui/views/quiz.py | 268 | button | Resume | yes |
| operators_console/ui/views/quiz.py | 271 | button | Start over | yes |
| operators_console/ui/views/quiz.py | 492 | button | Skip (counts as wrong) | yes |
| operators_console/ui/views/quiz.py | 497 | button | Leave this quiz | yes |
| operators_console/ui/views/quiz.py | 501 | button | Check answer | yes |
| operators_console/ui/views/quiz.py | 634 | button | <dynamic> | yes |
| operators_console/ui/views/quiz.py | 744 | button | Retake the whole quiz | yes |
| operators_console/ui/views/quiz.py | 749 | button | Back to the phase | yes |
| operators_console/ui/views/quiz.py | 753 | button | Review due cards | NO |
| operators_console/ui/views/quiz.py | 756 | button | Other quizzes | yes |
| operators_console/ui/views/quiz.py | 738 | button | <computed> | NO |
| operators_console/ui/views/quiz.py | 684 | button | <dynamic> | NO |
| operators_console/ui/views/quiz.py | 832 | button | Open this line | NO |
| operators_console/ui/views/quiz.py | 843 | button | Open the phase | NO |
| operators_console/ui/views/quiz.py | 915 | button | Open | NO |
| operators_console/ui/views/quiz.py | 857 | button | <computed> | NO |
| operators_console/ui/views/quiz.py | 866 | button | <computed> | NO |
| operators_console/ui/views/review.py | 196 | button | Restore | yes |
| operators_console/ui/views/review.py | 316 | button | Skip for now  (S) | yes |
| operators_console/ui/views/review.py | 415 | button | Where this is taught | yes |
| operators_console/ui/views/review.py | 421 | button | Next card  (Space) | yes |
| operators_console/ui/views/review.py | 477 | button | Bury this card | yes |
| operators_console/ui/views/review.py | 596 | button | Check for more | yes |
| operators_console/ui/views/review.py | 662 | button | <dynamic> | NO |
| operators_console/ui/views/review.py | 273 | button | Undo that answer | yes |
| operators_console/ui/views/review.py | 298 | button | Check  (Space) | yes |
| operators_console/ui/views/review.py | 310 | button | Reveal  (Space) | yes |
| operators_console/ui/views/review.py | 467 | button | <computed> | yes |
| operators_console/ui/views/roadmap.py | 267 | button | Open | yes |
| operators_console/ui/views/roadmap.py | 347 | button | Open | yes |
| operators_console/ui/views/settings.py | 129 | button | Run setup again | yes |
| operators_console/ui/views/settings.py | 148 | button | New profile... | yes |
| operators_console/ui/views/settings.py | 255 | button | Check now | yes |
| operators_console/ui/views/settings.py | 291 | button | Choose folder... | yes |
| operators_console/ui/views/settings.py | 294 | button | Copy now | yes |
| operators_console/ui/views/settings.py | 308 | button | Snapshot now | yes |
| operators_console/ui/views/settings.py | 311 | button | Restore a snapshot... | yes |
| operators_console/ui/views/settings.py | 323 | button | Reset all progress | yes |
| operators_console/ui/views/settings.py | 273 | button | <text> | yes |
| operators_console/ui/views/settings.py | 342 | button | <text> | yes |
| operators_console/ui/views/settings.py | 385 | button | Rename | NO |
| operators_console/ui/views/settings.py | 381 | button | Switch | NO |
| operators_console/ui/views/settings.py | 390 | button | Remove | NO |
| operators_console/ui/widgets/common.py | 469 | button | ... | yes |
| operators_console/ui/widgets/common.py | 652 | button | Open | yes |
| operators_console/ui/widgets/study_timer.py | 20 | button | Start studying | yes |
| operators_console/ui/widgets/study_timer.py | 31 | button | Pause | yes |
| operators_console/ui/widgets/study_timer.py | 35 | button | Stop | yes |

</details>

Recorded activations with no matching declaration (Qt's own controls, e.g. dialog buttons): 2

## What the walk could not reach

- **the "N more" resource disclosure** - PhaseView._fill_body draws one LinkRow per resource with no collapse, so no disclosure control exists in this revision of src/operators_console/ui/views/phase.py
- **undo across a restart** - History lives in memory (ui/context.py -> core/history.py) and is not written to the store, so nothing can be undone after a relaunch. That is a design choice, not a defect, but it means the walk cannot test undo across a save and reload.
- **the page you were on when you quit** - MainWindow always opens on Today (go('today') in __init__) and nothing writes the current page to the store, so 'position survives a relaunch' means progress, not the page. Recorded rather than asserted.
- **the real folder chooser** - QFileDialog.getExistingDirectory is a static that builds and execs its dialog in C++, so the walk's dialog answerer - which patches QDialog.exec in Python - cannot reach it. It is stubbed here the way getSaveFileName is stubbed in the harness.
- **the 'Update and restart' button** - Pressing it downloads a release package over the network and relaunches the program. The walk drives the dialog up to that button and stops; the download path itself is covered by tests/test_updates.py and tests/test_updates_security.py.
- **operators_console/ui/main_window.py:568 (action New profile...)** - never activated by the walk
- **operators_console/ui/main_window.py:571 (action Manage profiles...)** - never activated by the walk
- **operators_console/ui/main_window.py:560 (action <name>)** - never activated by the walk
- **operators_console/ui/main_window.py:404 (shortcut <QKeySequence()>)** - never activated by the walk
- **operators_console/ui/views/library.py:538 (button Open)** - never activated by the walk
- **operators_console/ui/views/quiz.py:753 (button Review due cards)** - never activated by the walk
- **operators_console/ui/views/quiz.py:738 (button <computed>)** - never activated by the walk
- **operators_console/ui/views/quiz.py:684 (button <dynamic>)** - never activated by the walk
- **operators_console/ui/views/quiz.py:832 (button Open this line)** - never activated by the walk
- **operators_console/ui/views/quiz.py:843 (button Open the phase)** - never activated by the walk
- **operators_console/ui/views/quiz.py:915 (button Open)** - never activated by the walk
- **operators_console/ui/views/quiz.py:857 (button <computed>)** - never activated by the walk
- **operators_console/ui/views/quiz.py:866 (button <computed>)** - never activated by the walk
- **operators_console/ui/views/review.py:662 (button <dynamic>)** - never activated by the walk
- **operators_console/ui/views/settings.py:385 (button Rename)** - never activated by the walk
- **operators_console/ui/views/settings.py:381 (button Switch)** - never activated by the walk
- **operators_console/ui/views/settings.py:390 (button Remove)** - never activated by the walk

## Content covered

| measure | count |
| --- | --- |
| Today plan actions offered | 5 |
| activity days charted | 366 |
| cards allowed by a ceiling of five | 5 |
| cards buried | 1 |
| cards planned for the first session | 15 |
| cards skipped out of the day | 1 |
| certificates cycled | 24 |
| clean shutdowns with a run in flight | 1 |
| clicks on disabled controls | 166 |
| concept cards revealed | 1 |
| controls declared in the source | 133 |
| controls reached by Tab on practice | 24 |
| controls reached by Tab on today | 22 |
| controls the walk activated | 116 |
| copies of the backups off this disk | 1 |
| curriculum completions reached | 1 |
| dead controls that now say so | 1 |
| distinct tracks reachable from goals | 15 |
| duplicate days warned about | 1 |
| endless loops timed out | 1 |
| exercises fully exercised | 161 |
| exercises re-armed from scratch | 1 |
| failing checks that explained themselves | 3 |
| field library buttons pressed | 118 |
| filters kept across a theme change | 3 |
| first run hints shown | 1 |
| gate checks recalled | 1 |
| gates cleared and reopened | 34 |
| goal combinations previewed | 745 |
| goals toggled in settings | 42 |
| graded submissions | 483 |
| guide links followed | 633 |
| hint ladders read to the end | 1 |
| library buttons pressed | 37 |
| library cards opened from search | 2 |
| library filters typed | 2 |
| library links opened | 71 |
| library rows marked as read | 3 |
| library shortcuts pressed | 2 |
| library tab counts read | 4 |
| library tabs opened | 4 |
| lines sent to the deck from the keyboard | 1 |
| lines taken out of the deck | 1 |
| log entries corrected | 1 |
| log entries deleted and restored | 1 |
| log entries found by search | 1 |
| log entries paged into view | 130 |
| log entries written | 5 |
| log promises surfaced | 1 |
| log ranges tried | 3 |
| menu actions triggered | 12 |
| milliseconds for 200 page switches | 2119 |
| milliseconds for a typical project status press | 25 |
| milliseconds to open review with 1000 cards | 46 |
| notes found by search | 1 |
| notes gathered onto the log | 7 |
| notes opened from the log | 7 |
| onboarding experience levels | 4 |
| onboarding steps walked | 4 |
| page and size combinations checked | 33 |
| pages opened against empty content | 5 |
| passing versions restored | 2 |
| phase check rows drawn | 790 |
| phase jump buttons used | 98 |
| phase notes written | 1 |
| phases opened | 35 |
| phases proven in the walk | 1 |
| phases reachable from the picker | 35 |
| plan actions dismissed | 2 |
| plan notes read | 1 |
| practice difficulty filters used | 5 |
| practice phase filters used | 31 |
| progress reports written | 1 |
| progress rows opened | 1 |
| project requirements drawn | 209 |
| project requirements ticked | 209 |
| project status changes | 108 |
| projects filters pressed | 3 |
| projects listed | 36 |
| projects outside the plan | 13 |
| questions answered by position | 18 |
| questions answered correctly | 354 |
| questions answered wrongly | 354 |
| questions read without an attempt | 1 |
| quiz folds opened | 1 |
| quiz options picked by letter | 1 |
| quiz searches typed | 1 |
| quiz status filters chosen | 3 |
| quiz trends shown | 1 |
| quizzes listed | 34 |
| quizzes scored full marks | 34 |
| quizzes started from the picker | 2 |
| rapid page switches | 400 |
| rating keys pressed | 4 |
| resource links opened | 167 |
| result rows walked with the keyboard | 4 |
| review answers taken back | 1 |
| review cards answered | 15 |
| review cards answered from the keyboard | 1 |
| review cards seeded | 1000 |
| roadmap Open buttons pressed | 13 |
| roadmap extras opened | 21 |
| roadmap tracks rendered | 16 |
| runs started from the keyboard | 1 |
| runs stopped by hand | 1 |
| screenshot notes written | 1 |
| screenshots kept | 23 |
| search result kinds seen | 8 |
| searches run | 5 |
| settings controls exercised | 16 |
| shelf hits opened | 1 |
| sidebar pages opened | 33 |
| skills self-assessed | 16 |
| snapshots restored | 1 |
| snippets copied | 5 |
| sort choices tried | 6 |
| study guides opened | 633 |
| study sessions saved | 1 |
| study steps ticked and unticked | 633 |
| themes exercised | 3 |
| tracks chosen in settings | 16 |
| undoable change kinds covered | 4 |
| update dialogs opened | 1 |
| ways back into the setup wizard | 1 |
| ways out of a quiz | 2 |
| where-taught presses | 1 |
| worst theme switch in milliseconds | 581 |
| wrong answers explained down to the character | 1 |
| wrong answers scheduled for review | 354 |
| wrong answers traced to their phase | 1 |

## URLs the app asked to open

Recorded and swallowed; nothing reached a browser.

- `https://github.com/skills/introduction-to-git`
- `https://www.youtube.com/watch?v=mAFoROnOfHs`
- `https://github.com/skills/introduction-to-github`
- `https://git-scm.com/doc`
- `https://docs.astral.sh/uv/`
- `https://cs50.harvard.edu/python/`
- `https://docs.python.org/3/tutorial/`
- `https://docs.python.org/3/library/`
- `https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU`
- `https://realpython.com/`
- `https://www.fluentpython.com/`
- `https://docs.python.org/3/howto/`
- `https://docs.python.org/3/reference/`
- `https://www.youtube.com/watch?v=ZDa-Z5JzLYM`
- `https://packaging.python.org/en/latest/`
- `https://docs.pytest.org/en/stable/`
- `https://docs.astral.sh/ruff/`
- `https://docs.astral.sh/`
- `https://mypy.readthedocs.io/en/stable/`
- `https://hypothesis.readthedocs.io/en/latest/`
- `https://cs50.harvard.edu/x/`
- `https://cs50.harvard.edu/x/weeks/3/`
- `https://cs50.harvard.edu/x/weeks/5/`
- `https://visualgo.net/en`
- `https://neetcode.io/`
- `https://www.youtube.com/watch?v=pkYVOmU3MgA`
- `https://cp-algorithms.com/`
- `https://exercism.org/tracks/python`
- `https://adventofcode.com/`
- `https://www.codewars.com/`
- `https://missing.csail.mit.edu/`
- `https://linuxjourney.com/`
- `https://overthewire.org/wargames/bandit/`
- `https://docs.python.org/3/library/subprocess.html`
- `https://developer.mozilla.org/en-US/docs/Web/HTTP`
- `https://docs.python.org/3/library/socket.html`
- `https://www.python-httpx.org/`
- `https://www.postgresql.org/docs/current/tutorial.html`
- `https://www.postgresql.org/docs/current/`
- `https://docs.sqlalchemy.org/en/20/`
- `https://fastapi.tiangolo.com/tutorial/`
- `https://docs.pydantic.dev/latest/`
- `https://owasp.org/www-project-top-ten/`
- `https://automatetheboringstuff.com/`
- `https://www.crummy.com/software/BeautifulSoup/bs4/doc/`
- `https://playwright.dev/python/`
- `https://docs.scrapy.org/en/latest/`
- `https://textual.textualize.io/`
- `https://docs.python.org/3/library/asyncio.html`
- `https://docs.python.org/3/library/concurrent.futures.html`
- `https://docs.python.org/3/library/profile.html`
- `https://locust.io/`
- `https://docs.docker.com/guides/python/`
- `https://docs.github.com/en/actions`
- `https://packaging.python.org/en/latest/guides/`
- `https://owasp.org/www-project-web-security-testing-guide/`
- `https://cheatsheetseries.owasp.org/`
- `https://docs.python.org/3/library/secrets.html`
- `https://karpathy.ai/zero-to-hero.html`
- `https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ`
- `https://docs.pytorch.org/tutorials/beginner/basics/`
- `https://scikit-learn.org/stable/`
- `https://numpy.org/doc/stable/`
- `https://pandas.pydata.org/docs/`
- `https://course.fast.ai/`
- `https://dataintensive.net/`
- `https://redis.io/docs/latest/`
- `https://docs.celeryq.dev/en/stable/`
- `https://docs.temporal.io/`
- `https://docs.langchain.com/oss/python/langgraph/`
- `https://opentelemetry.io/docs/`
- `https://cs50.harvard.edu/x/weeks/4/`
- `https://docs.python.org/3/extending/index.html`
- `https://github.com/python/cpython`
- `https://docs.python.org/3/library/dis.html`
- `https://github.com/DataTalksClub/data-engineering-zoomcamp`
- `https://airflow.apache.org/docs/`
- `https://docs.prefect.io/`
- `https://docs.getdbt.com/`
- `https://docs.pola.rs/`
- ... and 608 more

## Appendix: raw sensor output

Everything the sensors saw, including anything that landed between recorded steps.

### Qt warnings and criticals

- **warning**: `QFontDatabase: Cannot find font directory C:/Users/anasa/AppData/Roaming/Python/Python314/site-packages/PySide6/lib/fonts.
Note that Qt no longer ships fonts. Deploy some (from https://dejavu-fonts.github.io/ for example) or switch to fontconfig.`

### Unhandled exceptions

None.

### Dialogs the auto answerer handled

| kind | title | text |
| --- | --- | --- |
| save file | Export your progress | C:\Users\anasa\operators-console-backup.json |
| save file | Export a progress report | C:\Users\anasa\python-progress.md |
| dialog | SnapshotDialog | Restore a snapshot |
| notice | How this app works | Today: what to do next.  Roadmap: your plan, in teaching order. No phase is locked.  Practice: write code, and real checks grade it.  Quizzes: one per phase. Wrong answers go to Review.  Review: spaced repetition of earl |
| dialog | ShortcutsDialog | Keyboard shortcuts |
| dialog | FeedbackDialog | Report a problem or request a feature |
| notice | About Python Operator's Console | Python Operator's Console 1.3.0  35 phases, 161 graded exercises, 354 review questions, 36 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2964\test_the_help_ |
| messagebox | Show the solution? | You have not passed this one.  If you read the answer, it is marked as read, not solved. Try another hint first? |
| open file | Import a backup | C:\Users\anasa |
| question | Replace everything? | Importing replaces all current progress.  A backup of the current state is saved first. Continue? |
| question | Reset all progress? | This clears all checkboxes, exercises, reviews, projects and log entries.  A snapshot is taken first. Use Restore a snapshot in Settings to undo. Settings are kept. |
| dialog | UpdateDialog | Update available |
| dialog | QuestionDialog | Question |
| dialog | Onboarding | Set up your plan |
| question | Leave this quiz? | Answered questions are already scored.  The rest of this attempt is discarded, and the quiz starts over next time. Leave? |
| notice | About Python Operator's Console | Python Operator's Console 1.3.0  35 phases, 161 graded exercises, 354 review questions, 36 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2964\test_the_remai |

## Every step

| # | view | action | result | ms |
| --- | --- | --- | --- | --- |
| 1 | onboarding | open the wizard on first run | ok | 37 |
| 2 | onboarding | continue from step 1 | ok | 6 |
| 3 | onboarding | continue from step 2 | ok | 0 |
| 4 | onboarding | continue from step 3 | ok | 0 |
| 5 | onboarding | back from step 4 | ok | 0 |
| 6 | onboarding | back from step 3 | ok | 0 |
| 7 | onboarding | back from step 2 | ok | 0 |
| 8 | onboarding | experience: Never written code before | ok | 40 |
| 9 | onboarding | experience: Some Python, but it does not stick | ok | 36 |
| 10 | onboarding | experience: Confident in another language | ok | 56 |
| 11 | onboarding | experience: I write Python at work already | ok | 33 |
| 12 | onboarding | tick 745 goal combinations | ok | 799 |
| 13 | onboarding | finish with goal: Websites and APIs | ok | 64 |
| 14 | onboarding | finish with goal: Data analysis and engineering | ok | 47 |
| 15 | onboarding | finish with goal: Machine learning and AI | ok | 50 |
| 16 | onboarding | finish with goal: Computer vision | ok | 46 |
| 17 | onboarding | finish with goal: Language and text (NLP) | ok | 49 |
| 18 | onboarding | finish with goal: Automation and scraping | ok | 41 |
| 19 | onboarding | finish with goal: Bots and integrations | ok | 34 |
| 20 | onboarding | finish with goal: Desktop and mobile apps | ok | 29 |
| 21 | onboarding | finish with goal: Command-line tools | ok | 34 |
| 22 | onboarding | finish with goal: Games, graphics and media | ok | 29 |
| 23 | onboarding | finish with goal: Science and optimization | ok | 46 |
| 24 | onboarding | finish with goal: Finance and trading | ok | 28 |
| 25 | onboarding | finish with goal: Infrastructure and deployment | ok | 34 |
| 26 | onboarding | finish with goal: Network automation | ok | 37 |
| 27 | onboarding | finish with goal: Security | ok | 34 |
| 28 | onboarding | finish with goal: Testing and QA | ok | 31 |
| 29 | onboarding | finish with goal: Hardware, IoT and robotics | ok | 32 |
| 30 | onboarding | finish with goal: Blockchain | ok | 36 |
| 31 | onboarding | finish with goal: Pass a technical interview | ok | 28 |
| 32 | onboarding | finish with goal: How computers work | ok | 32 |
| 33 | onboarding | finish with goal: Compilers and language tools | ok | 35 |
| 34 | onboarding | pace 0.5 h x 1 days | ok | 36 |
| 35 | onboarding | pace 16.0 h x 7 days | ok | 32 |
| 36 | onboarding | skip the wizard | ok | 5 |
| 37 | today | land on Today after skipping | ok | 40 |
| 38 | today | read the four headline tiles | ok | 0 |
| 39 | today | press Start on plan row 1 | ok | 159 |
| 40 | today | press Start on plan row 2 | ok | 219 |
| 41 | today | press Start on plan row 3 | ok | 1202 |
| 42 | today | press Start on plan row 4 | ok | 204 |
| 43 | today | press Start on plan row 5 | ok | 27 |
| 44 | today | open the current phase from Where you are | ok | 156 |
| 45 | settings | switch the theme to light | ok | 4 |
| 46 | today | click the Today sidebar button (light theme) | ok | 37 |
| 47 | roadmap | click the Roadmap sidebar button (light theme) | ok | 166 |
| 48 | phase | click the Phase sidebar button (light theme) | ok | 152 |
| 49 | practice | click the Practice sidebar button (light theme) | ok | 77 |
| 50 | quiz | click the Quizzes sidebar button (light theme) | ok | 136 |
| 51 | review | click the Review sidebar button (light theme) | ok | 25 |
| 52 | projects | click the Projects sidebar button (light theme) | ok | 1137 |
| 53 | journal | click the Log sidebar button (light theme) | ok | 35 |
| 54 | stats | click the Progress sidebar button (light theme) | ok | 137 |
| 55 | library | click the Library sidebar button (light theme) | ok | 867 |
| 56 | settings | click the Settings sidebar button (light theme) | ok | 117 |
| 57 | settings | switch the theme to dark | ok | 275 |
| 58 | today | click the Today sidebar button (dark theme) | ok | 60 |
| 59 | roadmap | click the Roadmap sidebar button (dark theme) | ok | 146 |
| 60 | phase | click the Phase sidebar button (dark theme) | ok | 169 |
| 61 | practice | click the Practice sidebar button (dark theme) | ok | 60 |
| 62 | quiz | click the Quizzes sidebar button (dark theme) | ok | 114 |
| 63 | review | click the Review sidebar button (dark theme) | ok | 7 |
| 64 | projects | click the Projects sidebar button (dark theme) | ok | 1028 |
| 65 | journal | click the Log sidebar button (dark theme) | ok | 34 |
| 66 | stats | click the Progress sidebar button (dark theme) | ok | 118 |
| 67 | library | click the Library sidebar button (dark theme) | ok | 843 |
| 68 | settings | click the Settings sidebar button (dark theme) | ok | 59 |
| 69 | settings | switch the theme to system | ok | 262 |
| 70 | today | click the Today sidebar button (system theme) | ok | 58 |
| 71 | roadmap | click the Roadmap sidebar button (system theme) | ok | 146 |
| 72 | phase | click the Phase sidebar button (system theme) | ok | 156 |
| 73 | practice | click the Practice sidebar button (system theme) | ok | 62 |
| 74 | quiz | click the Quizzes sidebar button (system theme) | ok | 111 |
| 75 | review | click the Review sidebar button (system theme) | ok | 9 |
| 76 | projects | click the Projects sidebar button (system theme) | ok | 1036 |
| 77 | journal | click the Log sidebar button (system theme) | ok | 36 |
| 78 | stats | click the Progress sidebar button (system theme) | ok | 119 |
| 79 | library | click the Library sidebar button (system theme) | ok | 820 |
| 80 | settings | click the Settings sidebar button (system theme) | ok | 59 |
| 81 | today | check no control escapes the Today page | ok | 0 |
| 82 | roadmap | check no control escapes the Roadmap page | ok | 0 |
| 83 | phase | check no control escapes the Phase page | ok | 0 |
| 84 | practice | check no control escapes the Practice page | ok | 0 |
| 85 | quiz | check no control escapes the Quizzes page | ok | 0 |
| 86 | review | check no control escapes the Review page | ok | 0 |
| 87 | projects | check no control escapes the Projects page | ok | 3 |
| 88 | journal | check no control escapes the Log page | ok | 0 |
| 89 | stats | check no control escapes the Progress page | ok | 0 |
| 90 | library | check no control escapes the Library page | ok | 1 |
| 91 | settings | check no control escapes the Settings page | ok | 0 |
| 92 | menu | Go > Today | ok | 34 |
| 93 | menu | Go > Roadmap | ok | 134 |
| 94 | menu | Go > Phase | ok | 132 |
| 95 | menu | Go > Practice | ok | 42 |
| 96 | menu | Go > Quizzes | ok | 111 |
| 97 | menu | Go > Review | ok | 21 |
| 98 | menu | Go > Projects | ok | 980 |
| 99 | menu | Go > Log | ok | 31 |
| 100 | menu | Go > Progress | ok | 105 |
| 101 | menu | Go > Library | ok | 823 |
| 102 | menu | Go > Settings | ok | 95 |
| 103 | menu | Go > Find | ok | 8 |
| 104 | today | press Ctrl+1 for Today | ok | 35 |
| 105 | roadmap | press Ctrl+2 for Roadmap | ok | 153 |
| 106 | phase | press Ctrl+3 for Phase | ok | 159 |
| 107 | practice | press Ctrl+4 for Practice | ok | 48 |
| 108 | quiz | press Ctrl+5 for Quizzes | ok | 132 |
| 109 | review | press Ctrl+6 for Review | ok | 35 |
| 110 | projects | press Ctrl+7 for Projects | ok | 1276 |
| 111 | journal | press Ctrl+8 for Log | ok | 36 |
| 112 | stats | press Ctrl+9 for Progress | ok | 125 |
| 113 | menu | &File > Switch profile | ok | 0 |
| 114 | menu | &File > Export backup... | ok | 134 |
| 115 | menu | &File > Export progress report... | ok | 16 |
| 116 | menu | &File > Take a snapshot | ok | 9 |
| 117 | menu | &File > Restore a snapshot... | ok | 32 |
| 118 | menu | &Help > How this app works | ok | 0 |
| 119 | menu | &Help > Keyboard shortcuts | ok | 8 |
| 120 | menu | &Help > Report a problem or request a feature... | ok | 69 |
| 121 | menu | &Help > Check for updates | ok | 0 |
| 122 | menu | &Help > About | ok | 0 |
| 123 | roadmap | switch to the Well-rounded software engineer track | ok | 188 |
| 124 | roadmap | switch to the Learn Python properly (no career pressure) track | ok | 149 |
| 125 | roadmap | switch to the Backend & API engineer track | ok | 226 |
| 126 | roadmap | switch to the Data analysis & data engineering track | ok | 146 |
| 127 | roadmap | switch to the AI & machine learning engineer track | ok | 189 |
| 128 | roadmap | switch to the Automation, scripting & scraping track | ok | 144 |
| 129 | roadmap | switch to the DevOps & platform engineering track | ok | 155 |
| 130 | roadmap | switch to the Application security track | ok | 171 |
| 131 | roadmap | switch to the Job-ready, fastest route track | ok | 155 |
| 132 | roadmap | switch to the Desktop apps & developer tools track | ok | 166 |
| 133 | roadmap | switch to the Games & graphics track | ok | 158 |
| 134 | roadmap | switch to the Scientific computing & research track | ok | 158 |
| 135 | roadmap | switch to the Quantitative finance track | ok | 145 |
| 136 | roadmap | switch to the Test automation & quality engineering track | ok | 173 |
| 137 | roadmap | switch to the Network automation track | ok | 192 |
| 138 | roadmap | switch to the Embedded & IoT track | ok | 164 |
| 139 | roadmap | open every phase card from the roadmap | ok | 1985 |
| 140 | roadmap | open every phase outside the plan | slow (3250 ms) | 3250 |
| 141 | navigation | switch pages 200 times as fast as the event loop allows | slow (5528 ms) | 5528 |
| 142 | phase | walk Next through all 35 phases | slow (5760 ms) | 5760 |
| 143 | phase | walk Previous back to the first phase | slow (5592 ms) | 5592 |
| 144 | phase | choose every phase from the picker | slow (3917 ms) | 3917 |
| 145 | phase | open phase OS Operating rules | ok | 208 |
| 146 | phase | open phase 00 Environment & Git | ok | 160 |
| 147 | phase | open phase 01 Python foundations | ok | 180 |
| 148 | phase | open phase 02 Python engineering | ok | 149 |
| 149 | phase | open phase 03 Packaging & tooling | ok | 126 |
| 150 | phase | open phase 04 Computer science core | ok | 188 |
| 151 | phase | open phase 05 Algorithms & problem solving | ok | 148 |
| 152 | phase | open phase 06 Linux & systems | ok | 191 |
| 153 | phase | open phase 07 Networking | ok | 92 |
| 154 | phase | open phase 08 SQL & PostgreSQL | ok | 151 |
| 155 | phase | open phase 09 Backend engineering | ok | 129 |
| 156 | phase | open phase 10 Automation & web | ok | 137 |
| 157 | phase | open phase 11 Async, concurrency & performance | ok | 155 |
| 158 | phase | open phase 12 Docker, CI/CD & deployment | ok | 130 |
| 159 | phase | open phase 13 Application security | ok | 166 |
| 160 | phase | open phase 14 AI engineering | ok | 227 |
| 161 | phase | open phase 15 Architecture & orchestration | ok | 129 |
| 162 | phase | open phase 16 Systems programming & internals | ok | 149 |
| 163 | phase | open phase 17 Data engineering | ok | 110 |
| 164 | phase | open phase S1 Data analysis & visualization | ok | 154 |
| 165 | phase | open phase S2 Desktop & mobile apps | ok | 179 |
| 166 | phase | open phase S3 Command-line tools | ok | 158 |
| 167 | phase | open phase S4 Games, graphics & media | ok | 153 |
| 168 | phase | open phase S5 Scientific computing & optimization | ok | 155 |
| 169 | phase | open phase S6 Quantitative finance | ok | 101 |
| 170 | phase | open phase S7 Computer vision | ok | 202 |
| 171 | phase | open phase S8 Natural language processing | ok | 137 |
| 172 | phase | open phase S9 Testing & quality engineering | ok | 158 |
| 173 | phase | open phase S10 Network automation | ok | 156 |
| 174 | phase | open phase S11 Embedded, IoT & hardware | ok | 157 |
| 175 | phase | open phase S12 Security engineering | ok | 103 |
| 176 | phase | open phase S13 Bots & integrations | ok | 123 |
| 177 | phase | open phase S14 Blockchain tooling | ok | 104 |
| 178 | phase | open phase 18 Beyond senior | ok | 175 |
| 179 | phase | open phase 99 Final-boss ladder | ok | 155 |
| 180 | phase | tick every study step in OS | ok | 278 |
| 181 | phase | untick every study step in OS | ok | 176 |
| 182 | phase | tick every study step in 00 | ok | 167 |
| 183 | phase | untick every study step in 00 | ok | 164 |
| 184 | phase | tick every study step in 01 | ok | 338 |
| 185 | phase | untick every study step in 01 | ok | 331 |
| 186 | phase | tick every study step in 02 | ok | 166 |
| 187 | phase | untick every study step in 02 | ok | 188 |
| 188 | phase | tick every study step in 03 | ok | 188 |
| 189 | phase | untick every study step in 03 | ok | 154 |
| 190 | phase | tick every study step in 04 | ok | 212 |
| 191 | phase | untick every study step in 04 | ok | 172 |
| 192 | phase | tick every study step in 05 | ok | 227 |
| 193 | phase | untick every study step in 05 | ok | 170 |
| 194 | phase | tick every study step in 06 | ok | 171 |
| 195 | phase | untick every study step in 06 | ok | 145 |
| 196 | phase | tick every study step in 07 | ok | 183 |
| 197 | phase | untick every study step in 07 | ok | 181 |
| 198 | phase | tick every study step in 08 | ok | 174 |
| 199 | phase | untick every study step in 08 | ok | 131 |
| 200 | phase | tick every study step in 09 | ok | 227 |
| 201 | phase | untick every study step in 09 | ok | 165 |
| 202 | phase | tick every study step in 10 | ok | 222 |
| 203 | phase | untick every study step in 10 | ok | 193 |
| 204 | phase | tick every study step in 11 | ok | 193 |
| 205 | phase | untick every study step in 11 | ok | 172 |
| 206 | phase | tick every study step in 12 | ok | 200 |
| 207 | phase | untick every study step in 12 | ok | 182 |
| 208 | phase | tick every study step in 13 | ok | 239 |
| 209 | phase | untick every study step in 13 | ok | 196 |
| 210 | phase | tick every study step in 14 | ok | 271 |
| 211 | phase | untick every study step in 14 | ok | 226 |
| 212 | phase | tick every study step in 15 | ok | 242 |
| 213 | phase | untick every study step in 15 | ok | 174 |
| 214 | phase | tick every study step in 16 | ok | 212 |
| 215 | phase | untick every study step in 16 | ok | 155 |
| 216 | phase | tick every study step in 17 | ok | 214 |
| 217 | phase | untick every study step in 17 | ok | 189 |
| 218 | phase | tick every study step in S1 | ok | 195 |
| 219 | phase | untick every study step in S1 | ok | 166 |
| 220 | phase | tick every study step in S2 | ok | 139 |
| 221 | phase | untick every study step in S2 | ok | 151 |
| 222 | phase | tick every study step in S3 | ok | 157 |
| 223 | phase | untick every study step in S3 | ok | 112 |
| 224 | phase | tick every study step in S4 | ok | 141 |
| 225 | phase | untick every study step in S4 | ok | 123 |
| 226 | phase | tick every study step in S5 | ok | 211 |
| 227 | phase | untick every study step in S5 | ok | 125 |
| 228 | phase | tick every study step in S6 | ok | 151 |
| 229 | phase | untick every study step in S6 | ok | 106 |
| 230 | phase | tick every study step in S7 | ok | 148 |
| 231 | phase | untick every study step in S7 | ok | 185 |
| 232 | phase | tick every study step in S8 | ok | 128 |
| 233 | phase | untick every study step in S8 | ok | 108 |
| 234 | phase | tick every study step in S9 | ok | 149 |
| 235 | phase | untick every study step in S9 | ok | 142 |
| 236 | phase | tick every study step in S10 | ok | 131 |
| 237 | phase | untick every study step in S10 | ok | 125 |
| 238 | phase | tick every study step in S11 | ok | 153 |
| 239 | phase | untick every study step in S11 | ok | 116 |
| 240 | phase | tick every study step in S12 | ok | 142 |
| 241 | phase | untick every study step in S12 | ok | 143 |
| 242 | phase | tick every study step in S13 | ok | 146 |
| 243 | phase | untick every study step in S13 | ok | 107 |
| 244 | phase | tick every study step in S14 | ok | 126 |
| 245 | phase | untick every study step in S14 | ok | 115 |
| 246 | phase | tick every study step in 18 | ok | 308 |
| 247 | phase | untick every study step in 18 | ok | 304 |
| 248 | phase | tick every study step in 99 | ok | 222 |
| 249 | phase | untick every study step in 99 | ok | 225 |
| 250 | phase | clear the gate on 00 | ok | 76 |
| 251 | phase | reopen the gate on 00 | ok | 65 |
| 252 | phase | clear the gate on 01 | ok | 74 |
| 253 | phase | reopen the gate on 01 | ok | 61 |
| 254 | phase | clear the gate on 02 | ok | 108 |
| 255 | phase | reopen the gate on 02 | ok | 51 |
| 256 | phase | clear the gate on 03 | ok | 68 |
| 257 | phase | reopen the gate on 03 | ok | 63 |
| 258 | phase | clear the gate on 04 | ok | 92 |
| 259 | phase | reopen the gate on 04 | ok | 56 |
| 260 | phase | clear the gate on 05 | ok | 68 |
| 261 | phase | reopen the gate on 05 | ok | 55 |
| 262 | phase | clear the gate on 06 | ok | 62 |
| 263 | phase | reopen the gate on 06 | ok | 71 |
| 264 | phase | clear the gate on 07 | ok | 56 |
| 265 | phase | reopen the gate on 07 | ok | 47 |
| 266 | phase | clear the gate on 08 | ok | 61 |
| 267 | phase | reopen the gate on 08 | ok | 67 |
| 268 | phase | clear the gate on 09 | ok | 88 |
| 269 | phase | reopen the gate on 09 | ok | 54 |
| 270 | phase | clear the gate on 10 | ok | 86 |
| 271 | phase | reopen the gate on 10 | ok | 51 |
| 272 | phase | clear the gate on 11 | ok | 109 |
| 273 | phase | reopen the gate on 11 | ok | 59 |
| 274 | phase | clear the gate on 12 | ok | 64 |
| 275 | phase | reopen the gate on 12 | ok | 43 |
| 276 | phase | clear the gate on 13 | ok | 57 |
| 277 | phase | reopen the gate on 13 | ok | 49 |
| 278 | phase | clear the gate on 14 | ok | 73 |
| 279 | phase | reopen the gate on 14 | ok | 62 |
| 280 | phase | clear the gate on 15 | ok | 90 |
| 281 | phase | reopen the gate on 15 | ok | 46 |
| 282 | phase | clear the gate on 16 | ok | 80 |
| 283 | phase | reopen the gate on 16 | ok | 60 |
| 284 | phase | clear the gate on 17 | ok | 84 |
| 285 | phase | reopen the gate on 17 | ok | 47 |
| 286 | phase | clear the gate on S1 | ok | 85 |
| 287 | phase | reopen the gate on S1 | ok | 62 |
| 288 | phase | clear the gate on S2 | ok | 57 |
| 289 | phase | reopen the gate on S2 | ok | 63 |
| 290 | phase | clear the gate on S3 | ok | 51 |
| 291 | phase | reopen the gate on S3 | ok | 35 |
| 292 | phase | clear the gate on S4 | ok | 70 |
| 293 | phase | reopen the gate on S4 | ok | 46 |
| 294 | phase | clear the gate on S5 | ok | 58 |
| 295 | phase | reopen the gate on S5 | ok | 40 |
| 296 | phase | clear the gate on S6 | ok | 74 |
| 297 | phase | reopen the gate on S6 | ok | 63 |
| 298 | phase | clear the gate on S7 | ok | 67 |
| 299 | phase | reopen the gate on S7 | ok | 38 |
| 300 | phase | clear the gate on S8 | ok | 53 |
| 301 | phase | reopen the gate on S8 | ok | 66 |
| 302 | phase | clear the gate on S9 | ok | 54 |
| 303 | phase | reopen the gate on S9 | ok | 67 |
| 304 | phase | clear the gate on S10 | ok | 52 |
| 305 | phase | reopen the gate on S10 | ok | 35 |
| 306 | phase | clear the gate on S11 | ok | 48 |
| 307 | phase | reopen the gate on S11 | ok | 44 |
| 308 | phase | clear the gate on S12 | ok | 87 |
| 309 | phase | reopen the gate on S12 | ok | 41 |
| 310 | phase | clear the gate on S13 | ok | 43 |
| 311 | phase | reopen the gate on S13 | ok | 42 |
| 312 | phase | clear the gate on S14 | ok | 71 |
| 313 | phase | reopen the gate on S14 | ok | 37 |
| 314 | phase | clear the gate on 18 | ok | 83 |
| 315 | phase | reopen the gate on 18 | ok | 65 |
| 316 | phase | clear the gate on 99 | ok | 73 |
| 317 | phase | reopen the gate on 99 | ok | 41 |
| 318 | phase | open every resource in 00 | ok | 19 |
| 319 | phase | open every resource in 01 | ok | 30 |
| 320 | phase | open every resource in 02 | ok | 29 |
| 321 | phase | open every resource in 03 | ok | 38 |
| 322 | phase | open every resource in 04 | ok | 27 |
| 323 | phase | open every resource in 05 | ok | 38 |
| 324 | phase | open every resource in 06 | ok | 39 |
| 325 | phase | open every resource in 07 | ok | 35 |
| 326 | phase | open every resource in 08 | ok | 25 |
| 327 | phase | open every resource in 09 | ok | 41 |
| 328 | phase | open every resource in 10 | ok | 33 |
| 329 | phase | open every resource in 11 | ok | 37 |
| 330 | phase | open every resource in 12 | ok | 34 |
| 331 | phase | open every resource in 13 | ok | 26 |
| 332 | phase | open every resource in 14 | ok | 29 |
| 333 | phase | open every resource in 15 | ok | 43 |
| 334 | phase | open every resource in 16 | ok | 39 |
| 335 | phase | open every resource in 17 | ok | 59 |
| 336 | phase | open every resource in S1 | ok | 32 |
| 337 | phase | open every resource in S2 | ok | 34 |
| 338 | phase | open every resource in S3 | ok | 36 |
| 339 | phase | open every resource in S4 | ok | 34 |
| 340 | phase | open every resource in S5 | ok | 42 |
| 341 | phase | open every resource in S6 | ok | 26 |
| 342 | phase | open every resource in S7 | ok | 34 |
| 343 | phase | open every resource in S8 | ok | 26 |
| 344 | phase | open every resource in S9 | ok | 42 |
| 345 | phase | open every resource in S10 | ok | 37 |
| 346 | phase | open every resource in S11 | ok | 63 |
| 347 | phase | open every resource in S12 | ok | 37 |
| 348 | phase | open every resource in S13 | ok | 26 |
| 349 | phase | open every resource in S14 | ok | 31 |
| 350 | phase | open every resource in 18 | ok | 23 |
| 351 | phase | open every resource in 99 | ok | 33 |
| 352 | phase | use the jump row and snippet on OS | ok | 0 |
| 353 | phase | use the jump row and snippet on 00 | ok | 1525 |
| 354 | phase | use the jump row and snippet on 01 | ok | 443 |
| 355 | phase | use the jump row and snippet on 02 | ok | 507 |
| 356 | phase | use the jump row and snippet on 03 | ok | 477 |
| 357 | phase | use the jump row and snippet on 04 | ok | 526 |
| 358 | phase | use the jump row and snippet on 05 | ok | 490 |
| 359 | phase | use the jump row and snippet on 06 | ok | 451 |
| 360 | phase | use the jump row and snippet on 07 | ok | 389 |
| 361 | phase | use the jump row and snippet on 08 | ok | 394 |
| 362 | phase | use the jump row and snippet on 09 | ok | 446 |
| 363 | phase | use the jump row and snippet on 10 | ok | 495 |
| 364 | phase | use the jump row and snippet on 11 | ok | 514 |
| 365 | phase | use the jump row and snippet on 12 | ok | 453 |
| 366 | phase | use the jump row and snippet on 13 | ok | 492 |
| 367 | phase | use the jump row and snippet on 14 | ok | 616 |
| 368 | phase | use the jump row and snippet on 15 | ok | 527 |
| 369 | phase | use the jump row and snippet on 16 | ok | 405 |
| 370 | phase | use the jump row and snippet on 17 | ok | 511 |
| 371 | phase | use the jump row and snippet on S1 | ok | 753 |
| 372 | phase | use the jump row and snippet on S2 | ok | 513 |
| 373 | phase | use the jump row and snippet on S3 | ok | 409 |
| 374 | phase | use the jump row and snippet on S4 | ok | 387 |
| 375 | phase | use the jump row and snippet on S5 | ok | 493 |
| 376 | phase | use the jump row and snippet on S6 | ok | 415 |
| 377 | phase | use the jump row and snippet on S7 | ok | 434 |
| 378 | phase | use the jump row and snippet on S8 | ok | 533 |
| 379 | phase | use the jump row and snippet on S9 | ok | 451 |
| 380 | phase | use the jump row and snippet on S10 | ok | 479 |
| 381 | phase | use the jump row and snippet on S11 | ok | 412 |
| 382 | phase | use the jump row and snippet on S12 | ok | 445 |
| 383 | phase | use the jump row and snippet on S13 | ok | 364 |
| 384 | phase | use the jump row and snippet on S14 | ok | 420 |
| 385 | phase | use the jump row and snippet on 18 | ok | 182 |
| 386 | phase | use the jump row and snippet on 99 | ok | 243 |
| 387 | phase | send a line to the review deck from the right click menu | ok | 260 |
| 388 | phase | type a note in each phase and leave at once | slow (4850 ms) | 4850 |
| 389 | phase | the pending note is committed on quit | ok | 283 |
| 390 | practice | filter the list by every phase | ok | 500 |
| 391 | practice | switch the status filter three ways | ok | 38 |
| 392 | practice | walk the list with Next exercise | ok | 56 |
| 393 | practice | run an endless loop and wait it out | ok | 3482 |
| 394 | practice | ask for the solution before passing | ok | 2 |
| 395 | practice | insist on the solution | ok | 17 |
| 396 | practice | type, then press Reset | ok | 6 |
| 397 | practice | p01.001: read the brief | ok | 0 |
| 398 | practice | p01.001: reveal every hint | ok | 58 |
| 399 | practice | p01.001: run an empty editor | ok | 264 |
| 400 | practice | p01.001: run the untouched starter | ok | 259 |
| 401 | practice | p01.001: run the reference solution | ok | 215 |
| 402 | practice | p01.001: read the solution once passed | ok | 19 |
| 403 | practice | p01.002: read the brief | ok | 0 |
| 404 | practice | p01.002: reveal every hint | ok | 38 |
| 405 | practice | p01.002: run an empty editor | ok | 216 |
| 406 | practice | p01.002: run the untouched starter | ok | 297 |
| 407 | practice | p01.002: run the reference solution | ok | 345 |
| 408 | practice | p01.002: read the solution once passed | ok | 36 |
| 409 | practice | p01.003: read the brief | ok | 0 |
| 410 | practice | p01.003: reveal every hint | ok | 57 |
| 411 | practice | p01.003: run an empty editor | ok | 283 |
| 412 | practice | p01.003: run the untouched starter | ok | 258 |
| 413 | practice | p01.003: run the reference solution | ok | 261 |
| 414 | practice | p01.003: read the solution once passed | ok | 28 |
| 415 | practice | p01.004: read the brief | ok | 0 |
| 416 | practice | p01.004: reveal every hint | ok | 41 |
| 417 | practice | p01.004: run an empty editor | ok | 250 |
| 418 | practice | p01.004: run the untouched starter | ok | 264 |
| 419 | practice | p01.004: run the reference solution | ok | 223 |
| 420 | practice | p01.004: read the solution once passed | ok | 16 |
| 421 | practice | p01.005: read the brief | ok | 0 |
| 422 | practice | p01.005: reveal every hint | ok | 28 |
| 423 | practice | p01.005: run an empty editor | ok | 318 |
| 424 | practice | p01.005: run the untouched starter | ok | 217 |
| 425 | practice | p01.005: run the reference solution | ok | 241 |
| 426 | practice | p01.005: read the solution once passed | ok | 18 |
| 427 | practice | p01.006: read the brief | ok | 0 |
| 428 | practice | p01.006: reveal every hint | ok | 50 |
| 429 | practice | p01.006: run an empty editor | ok | 210 |
| 430 | practice | p01.006: run the untouched starter | ok | 211 |
| 431 | practice | p01.006: run the reference solution | ok | 322 |
| 432 | practice | p01.006: read the solution once passed | ok | 27 |
| 433 | practice | p01.007: read the brief | ok | 0 |
| 434 | practice | p01.007: reveal every hint | ok | 35 |
| 435 | practice | p01.007: run an empty editor | ok | 262 |
| 436 | practice | p01.007: run the untouched starter | ok | 250 |
| 437 | practice | p01.007: run the reference solution | ok | 244 |
| 438 | practice | p01.007: read the solution once passed | ok | 23 |
| 439 | practice | p01.008: read the brief | ok | 0 |
| 440 | practice | p01.008: reveal every hint | ok | 41 |
| 441 | practice | p01.008: run an empty editor | ok | 211 |
| 442 | practice | p01.008: run the untouched starter | ok | 219 |
| 443 | practice | p01.008: run the reference solution | ok | 223 |
| 444 | practice | p01.008: read the solution once passed | ok | 19 |
| 445 | practice | p01.009: read the brief | ok | 0 |
| 446 | practice | p01.009: reveal every hint | ok | 42 |
| 447 | practice | p01.009: run an empty editor | ok | 197 |
| 448 | practice | p01.009: run the untouched starter | ok | 268 |
| 449 | practice | p01.009: run the reference solution | ok | 256 |
| 450 | practice | p01.009: read the solution once passed | ok | 22 |
| 451 | practice | p01.010: read the brief | ok | 0 |
| 452 | practice | p01.010: reveal every hint | ok | 50 |
| 453 | practice | p01.010: run an empty editor | ok | 219 |
| 454 | practice | p01.010: run the untouched starter | ok | 221 |
| 455 | practice | p01.010: run the reference solution | ok | 219 |
| 456 | practice | p01.010: read the solution once passed | ok | 24 |
| 457 | practice | p01.011: read the brief | ok | 0 |
| 458 | practice | p01.011: reveal every hint | ok | 35 |
| 459 | practice | p01.011: run an empty editor | ok | 277 |
| 460 | practice | p01.011: run the untouched starter | ok | 248 |
| 461 | practice | p01.011: run the reference solution | ok | 187 |
| 462 | practice | p01.011: read the solution once passed | ok | 29 |
| 463 | practice | p01.012: read the brief | ok | 0 |
| 464 | practice | p01.012: reveal every hint | ok | 39 |
| 465 | practice | p01.012: run an empty editor | ok | 239 |
| 466 | practice | p01.012: run the untouched starter | ok | 218 |
| 467 | practice | p01.012: run the reference solution | ok | 244 |
| 468 | practice | p01.012: read the solution once passed | ok | 22 |
| 469 | practice | p01.013: read the brief | ok | 0 |
| 470 | practice | p01.013: reveal every hint | ok | 30 |
| 471 | practice | p01.013: run an empty editor | ok | 282 |
| 472 | practice | p01.013: run the untouched starter | ok | 310 |
| 473 | practice | p01.013: run the reference solution | ok | 230 |
| 474 | practice | p01.013: read the solution once passed | ok | 32 |
| 475 | practice | p01.014: read the brief | ok | 0 |
| 476 | practice | p01.014: reveal every hint | ok | 54 |
| 477 | practice | p01.014: run an empty editor | ok | 199 |
| 478 | practice | p01.014: run the untouched starter | ok | 306 |
| 479 | practice | p01.014: run the reference solution | ok | 210 |
| 480 | practice | p01.014: read the solution once passed | ok | 19 |
| 481 | practice | p01.015: read the brief | ok | 0 |
| 482 | practice | p01.015: reveal every hint | ok | 31 |
| 483 | practice | p01.015: run an empty editor | ok | 183 |
| 484 | practice | p01.015: run the untouched starter | ok | 231 |
| 485 | practice | p01.015: run the reference solution | ok | 256 |
| 486 | practice | p01.015: read the solution once passed | ok | 47 |
| 487 | practice | p01.016: read the brief | ok | 0 |
| 488 | practice | p01.016: reveal every hint | ok | 41 |
| 489 | practice | p01.016: run an empty editor | ok | 234 |
| 490 | practice | p01.016: run the untouched starter | ok | 257 |
| 491 | practice | p01.016: run the reference solution | ok | 194 |
| 492 | practice | p01.016: read the solution once passed | ok | 31 |
| 493 | practice | p01.017: read the brief | ok | 0 |
| 494 | practice | p01.017: reveal every hint | ok | 27 |
| 495 | practice | p01.017: run an empty editor | ok | 205 |
| 496 | practice | p01.017: run the untouched starter | ok | 288 |
| 497 | practice | p01.017: run the reference solution | ok | 261 |
| 498 | practice | p01.017: read the solution once passed | ok | 19 |
| 499 | practice | p01.018: read the brief | ok | 0 |
| 500 | practice | p01.018: reveal every hint | ok | 55 |
| 501 | practice | p01.018: run an empty editor | ok | 308 |
| 502 | practice | p01.018: run the untouched starter | ok | 274 |
| 503 | practice | p01.018: run the reference solution | ok | 253 |
| 504 | practice | p01.018: read the solution once passed | ok | 27 |
| 505 | practice | p01.019: read the brief | ok | 0 |
| 506 | practice | p01.019: reveal every hint | ok | 40 |
| 507 | practice | p01.019: run an empty editor | ok | 254 |
| 508 | practice | p01.019: run the untouched starter | ok | 252 |
| 509 | practice | p01.019: run the reference solution | ok | 236 |
| 510 | practice | p01.019: read the solution once passed | ok | 46 |
| 511 | practice | p01.020: read the brief | ok | 0 |
| 512 | practice | p01.020: reveal every hint | ok | 41 |
| 513 | practice | p01.020: run an empty editor | ok | 248 |
| 514 | practice | p01.020: run the untouched starter | ok | 281 |
| 515 | practice | p01.020: run the reference solution | ok | 306 |
| 516 | practice | p01.020: read the solution once passed | ok | 20 |
| 517 | practice | p01.021: read the brief | ok | 0 |
| 518 | practice | p01.021: reveal every hint | ok | 32 |
| 519 | practice | p01.021: run an empty editor | ok | 249 |
| 520 | practice | p01.021: run the untouched starter | ok | 244 |
| 521 | practice | p01.021: run the reference solution | ok | 265 |
| 522 | practice | p01.021: read the solution once passed | ok | 26 |
| 523 | practice | p01.022: read the brief | ok | 0 |
| 524 | practice | p01.022: reveal every hint | ok | 29 |
| 525 | practice | p01.022: run an empty editor | ok | 270 |
| 526 | practice | p01.022: run the untouched starter | ok | 296 |
| 527 | practice | p01.022: run the reference solution | ok | 258 |
| 528 | practice | p01.022: read the solution once passed | ok | 23 |
| 529 | practice | p01.023: read the brief | ok | 0 |
| 530 | practice | p01.023: reveal every hint | ok | 64 |
| 531 | practice | p01.023: run an empty editor | ok | 267 |
| 532 | practice | p01.023: run the untouched starter | ok | 281 |
| 533 | practice | p01.023: run the reference solution | ok | 268 |
| 534 | practice | p01.023: read the solution once passed | ok | 32 |
| 535 | practice | p01.024: read the brief | ok | 0 |
| 536 | practice | p01.024: reveal every hint | ok | 30 |
| 537 | practice | p01.024: run an empty editor | ok | 226 |
| 538 | practice | p01.024: run the untouched starter | ok | 264 |
| 539 | practice | p01.024: run the reference solution | ok | 335 |
| 540 | practice | p01.024: read the solution once passed | ok | 26 |
| 541 | practice | p01.025: read the brief | ok | 0 |
| 542 | practice | p01.025: reveal every hint | ok | 38 |
| 543 | practice | p01.025: run an empty editor | ok | 218 |
| 544 | practice | p01.025: run the untouched starter | ok | 290 |
| 545 | practice | p01.025: run the reference solution | ok | 266 |
| 546 | practice | p01.025: read the solution once passed | ok | 45 |
| 547 | practice | p01.026: read the brief | ok | 0 |
| 548 | practice | p01.026: reveal every hint | ok | 34 |
| 549 | practice | p01.026: run an empty editor | ok | 266 |
| 550 | practice | p01.026: run the untouched starter | ok | 291 |
| 551 | practice | p01.026: run the reference solution | ok | 279 |
| 552 | practice | p01.026: read the solution once passed | ok | 18 |
| 553 | practice | p01.027: read the brief | ok | 0 |
| 554 | practice | p01.027: reveal every hint | ok | 33 |
| 555 | practice | p01.027: run an empty editor | ok | 245 |
| 556 | practice | p01.027: run the untouched starter | ok | 313 |
| 557 | practice | p01.027: run the reference solution | ok | 260 |
| 558 | practice | p01.027: read the solution once passed | ok | 26 |
| 559 | practice | p01.028: read the brief | ok | 0 |
| 560 | practice | p01.028: reveal every hint | ok | 54 |
| 561 | practice | p01.028: run an empty editor | ok | 213 |
| 562 | practice | p01.028: run the untouched starter | ok | 289 |
| 563 | practice | p01.028: run the reference solution | ok | 262 |
| 564 | practice | p01.028: read the solution once passed | ok | 26 |
| 565 | practice | p01.029: read the brief | ok | 0 |
| 566 | practice | p01.029: reveal every hint | ok | 41 |
| 567 | practice | p01.029: run an empty editor | ok | 219 |
| 568 | practice | p01.029: run the untouched starter | ok | 295 |
| 569 | practice | p01.029: run the reference solution | ok | 270 |
| 570 | practice | p01.029: read the solution once passed | ok | 34 |
| 571 | practice | p01.030: read the brief | ok | 0 |
| 572 | practice | p01.030: reveal every hint | ok | 43 |
| 573 | practice | p01.030: run an empty editor | ok | 216 |
| 574 | practice | p01.030: run the untouched starter | ok | 266 |
| 575 | practice | p01.030: run the reference solution | ok | 277 |
| 576 | practice | p01.030: read the solution once passed | ok | 23 |
| 577 | practice | p01.031: read the brief | ok | 0 |
| 578 | practice | p01.031: reveal every hint | ok | 39 |
| 579 | practice | p01.031: run an empty editor | ok | 215 |
| 580 | practice | p01.031: run the untouched starter | ok | 289 |
| 581 | practice | p01.031: run the reference solution | ok | 252 |
| 582 | practice | p01.031: read the solution once passed | ok | 57 |
| 583 | practice | p01.032: read the brief | ok | 0 |
| 584 | practice | p01.032: reveal every hint | ok | 43 |
| 585 | practice | p01.032: run an empty editor | ok | 291 |
| 586 | practice | p01.032: run the untouched starter | ok | 293 |
| 587 | practice | p01.032: run the reference solution | ok | 245 |
| 588 | practice | p01.032: read the solution once passed | ok | 21 |
| 589 | practice | p01.033: read the brief | ok | 0 |
| 590 | practice | p01.033: reveal every hint | ok | 19 |
| 591 | practice | p01.033: run an empty editor | ok | 232 |
| 592 | practice | p01.033: run the untouched starter | ok | 306 |
| 593 | practice | p01.033: run the reference solution | ok | 268 |
| 594 | practice | p01.033: read the solution once passed | ok | 33 |
| 595 | practice | p01.034: read the brief | ok | 0 |
| 596 | practice | p01.034: reveal every hint | ok | 31 |
| 597 | practice | p01.034: run an empty editor | ok | 230 |
| 598 | practice | p01.034: run the untouched starter | ok | 244 |
| 599 | practice | p01.034: run the reference solution | ok | 247 |
| 600 | practice | p01.034: read the solution once passed | ok | 21 |
| 601 | practice | p01.035: read the brief | ok | 0 |
| 602 | practice | p01.035: reveal every hint | ok | 41 |
| 603 | practice | p01.035: run an empty editor | ok | 209 |
| 604 | practice | p01.035: run the untouched starter | ok | 263 |
| 605 | practice | p01.035: run the reference solution | ok | 211 |
| 606 | practice | p01.035: read the solution once passed | ok | 19 |
| 607 | practice | p01.036: read the brief | ok | 0 |
| 608 | practice | p01.036: reveal every hint | ok | 51 |
| 609 | practice | p01.036: run an empty editor | ok | 288 |
| 610 | practice | p01.036: run the untouched starter | ok | 250 |
| 611 | practice | p01.036: run the reference solution | ok | 229 |
| 612 | practice | p01.036: read the solution once passed | ok | 24 |
| 613 | practice | p02.001: read the brief | ok | 0 |
| 614 | practice | p02.001: reveal every hint | ok | 36 |
| 615 | practice | p02.001: run an empty editor | ok | 237 |
| 616 | practice | p02.001: run the untouched starter | ok | 231 |
| 617 | practice | p02.001: run the reference solution | ok | 257 |
| 618 | practice | p02.001: read the solution once passed | ok | 18 |
| 619 | practice | p02.002: read the brief | ok | 0 |
| 620 | practice | p02.002: reveal every hint | ok | 20 |
| 621 | practice | p02.002: run an empty editor | ok | 251 |
| 622 | practice | p02.002: run the untouched starter | ok | 322 |
| 623 | practice | p02.002: run the reference solution | ok | 260 |
| 624 | practice | p02.002: read the solution once passed | ok | 18 |
| 625 | practice | p02.003: read the brief | ok | 0 |
| 626 | practice | p02.003: reveal every hint | ok | 24 |
| 627 | practice | p02.003: run an empty editor | ok | 181 |
| 628 | practice | p02.003: run the untouched starter | ok | 248 |
| 629 | practice | p02.003: run the reference solution | ok | 221 |
| 630 | practice | p02.003: read the solution once passed | ok | 16 |
| 631 | practice | p02.004: read the brief | ok | 0 |
| 632 | practice | p02.004: reveal every hint | ok | 41 |
| 633 | practice | p02.004: run an empty editor | ok | 264 |
| 634 | practice | p02.004: run the untouched starter | ok | 242 |
| 635 | practice | p02.004: run the reference solution | ok | 247 |
| 636 | practice | p02.004: read the solution once passed | ok | 22 |
| 637 | practice | p02.005: read the brief | ok | 0 |
| 638 | practice | p02.005: reveal every hint | ok | 28 |
| 639 | practice | p02.005: run an empty editor | ok | 273 |
| 640 | practice | p02.005: run the untouched starter | ok | 217 |
| 641 | practice | p02.005: run the reference solution | ok | 324 |
| 642 | practice | p02.005: read the solution once passed | ok | 20 |
| 643 | practice | p02.006: read the brief | ok | 0 |
| 644 | practice | p02.006: reveal every hint | ok | 37 |
| 645 | practice | p02.006: run an empty editor | ok | 277 |
| 646 | practice | p02.006: run the untouched starter | ok | 261 |
| 647 | practice | p02.006: run the reference solution | ok | 235 |
| 648 | practice | p02.006: read the solution once passed | ok | 22 |
| 649 | practice | p02.007: read the brief | ok | 0 |
| 650 | practice | p02.007: reveal every hint | ok | 24 |
| 651 | practice | p02.007: run an empty editor | ok | 232 |
| 652 | practice | p02.007: run the untouched starter | ok | 239 |
| 653 | practice | p02.007: run the reference solution | ok | 221 |
| 654 | practice | p02.007: read the solution once passed | ok | 22 |
| 655 | practice | p02.008: read the brief | ok | 0 |
| 656 | practice | p02.008: reveal every hint | ok | 29 |
| 657 | practice | p02.008: run an empty editor | ok | 230 |
| 658 | practice | p02.008: run the untouched starter | ok | 294 |
| 659 | practice | p02.008: run the reference solution | ok | 267 |
| 660 | practice | p02.008: read the solution once passed | ok | 19 |
| 661 | practice | p02.009: read the brief | ok | 0 |
| 662 | practice | p02.009: reveal every hint | ok | 38 |
| 663 | practice | p02.009: run an empty editor | ok | 239 |
| 664 | practice | p02.009: run the untouched starter | ok | 293 |
| 665 | practice | p02.009: run the reference solution | ok | 233 |
| 666 | practice | p02.009: read the solution once passed | ok | 17 |
| 667 | practice | p02.010: read the brief | ok | 0 |
| 668 | practice | p02.010: reveal every hint | ok | 32 |
| 669 | practice | p02.010: run an empty editor | ok | 280 |
| 670 | practice | p02.010: run the untouched starter | ok | 266 |
| 671 | practice | p02.010: run the reference solution | ok | 319 |
| 672 | practice | p02.010: read the solution once passed | ok | 33 |
| 673 | practice | p02.011: read the brief | ok | 0 |
| 674 | practice | p02.011: reveal every hint | ok | 44 |
| 675 | practice | p02.011: run an empty editor | ok | 267 |
| 676 | practice | p02.011: run the untouched starter | ok | 295 |
| 677 | practice | p02.011: run the reference solution | ok | 234 |
| 678 | practice | p02.011: read the solution once passed | ok | 51 |
| 679 | practice | p02.012: read the brief | ok | 0 |
| 680 | practice | p02.012: reveal every hint | ok | 30 |
| 681 | practice | p02.012: run an empty editor | ok | 220 |
| 682 | practice | p02.012: run the untouched starter | ok | 269 |
| 683 | practice | p02.012: run the reference solution | ok | 246 |
| 684 | practice | p02.012: read the solution once passed | ok | 24 |
| 685 | practice | p02.013: read the brief | ok | 0 |
| 686 | practice | p02.013: reveal every hint | ok | 37 |
| 687 | practice | p02.013: run an empty editor | ok | 241 |
| 688 | practice | p02.013: run the untouched starter | ok | 292 |
| 689 | practice | p02.013: run the reference solution | ok | 298 |
| 690 | practice | p02.013: read the solution once passed | ok | 27 |
| 691 | practice | p02.014: read the brief | ok | 0 |
| 692 | practice | p02.014: reveal every hint | ok | 25 |
| 693 | practice | p02.014: run an empty editor | ok | 231 |
| 694 | practice | p02.014: run the untouched starter | ok | 236 |
| 695 | practice | p02.014: run the reference solution | ok | 323 |
| 696 | practice | p02.014: read the solution once passed | ok | 28 |
| 697 | practice | p02.015: read the brief | ok | 0 |
| 698 | practice | p02.015: reveal every hint | ok | 48 |
| 699 | practice | p02.015: run an empty editor | ok | 230 |
| 700 | practice | p02.015: run the untouched starter | ok | 288 |
| 701 | practice | p02.015: run the reference solution | ok | 249 |
| 702 | practice | p02.015: read the solution once passed | ok | 19 |
| 703 | practice | p02.016: read the brief | ok | 0 |
| 704 | practice | p02.016: reveal every hint | ok | 26 |
| 705 | practice | p02.016: run an empty editor | ok | 264 |
| 706 | practice | p02.016: run the untouched starter | ok | 268 |
| 707 | practice | p02.016: run the reference solution | ok | 278 |
| 708 | practice | p02.016: read the solution once passed | ok | 22 |
| 709 | practice | p04.011: read the brief | ok | 0 |
| 710 | practice | p04.011: reveal every hint | ok | 42 |
| 711 | practice | p04.011: run an empty editor | ok | 296 |
| 712 | practice | p04.011: run the untouched starter | ok | 241 |
| 713 | practice | p04.011: run the reference solution | ok | 287 |
| 714 | practice | p04.011: read the solution once passed | ok | 24 |
| 715 | practice | p04.012: read the brief | ok | 0 |
| 716 | practice | p04.012: reveal every hint | ok | 45 |
| 717 | practice | p04.012: run an empty editor | ok | 303 |
| 718 | practice | p04.012: run the untouched starter | ok | 288 |
| 719 | practice | p04.012: run the reference solution | ok | 263 |
| 720 | practice | p04.012: read the solution once passed | ok | 19 |
| 721 | practice | p04.013: read the brief | ok | 0 |
| 722 | practice | p04.013: reveal every hint | ok | 50 |
| 723 | practice | p04.013: run an empty editor | ok | 284 |
| 724 | practice | p04.013: run the untouched starter | ok | 291 |
| 725 | practice | p04.013: run the reference solution | ok | 257 |
| 726 | practice | p04.013: read the solution once passed | ok | 19 |
| 727 | practice | p04.001: read the brief | ok | 0 |
| 728 | practice | p04.001: reveal every hint | ok | 37 |
| 729 | practice | p04.001: run an empty editor | ok | 251 |
| 730 | practice | p04.001: run the untouched starter | ok | 301 |
| 731 | practice | p04.001: run the reference solution | ok | 235 |
| 732 | practice | p04.001: read the solution once passed | ok | 29 |
| 733 | practice | p04.002: read the brief | ok | 0 |
| 734 | practice | p04.002: reveal every hint | ok | 28 |
| 735 | practice | p04.002: run an empty editor | ok | 181 |
| 736 | practice | p04.002: run the untouched starter | ok | 230 |
| 737 | practice | p04.002: run the reference solution | ok | 231 |
| 738 | practice | p04.002: read the solution once passed | ok | 22 |
| 739 | practice | p04.003: read the brief | ok | 0 |
| 740 | practice | p04.003: reveal every hint | ok | 40 |
| 741 | practice | p04.003: run an empty editor | ok | 251 |
| 742 | practice | p04.003: run the untouched starter | ok | 293 |
| 743 | practice | p04.003: run the reference solution | ok | 270 |
| 744 | practice | p04.003: read the solution once passed | ok | 26 |
| 745 | practice | p04.004: read the brief | ok | 0 |
| 746 | practice | p04.004: reveal every hint | ok | 39 |
| 747 | practice | p04.004: run an empty editor | ok | 255 |
| 748 | practice | p04.004: run the untouched starter | ok | 226 |
| 749 | practice | p04.004: run the reference solution | ok | 253 |
| 750 | practice | p04.004: read the solution once passed | ok | 34 |
| 751 | practice | p04.005: read the brief | ok | 0 |
| 752 | practice | p04.005: reveal every hint | ok | 53 |
| 753 | practice | p04.005: run an empty editor | ok | 236 |
| 754 | practice | p04.005: run the untouched starter | ok | 287 |
| 755 | practice | p04.005: run the reference solution | ok | 267 |
| 756 | practice | p04.005: read the solution once passed | ok | 31 |
| 757 | practice | p04.006: read the brief | ok | 0 |
| 758 | practice | p04.006: reveal every hint | ok | 41 |
| 759 | practice | p04.006: run an empty editor | ok | 257 |
| 760 | practice | p04.006: run the untouched starter | ok | 277 |
| 761 | practice | p04.006: run the reference solution | ok | 295 |
| 762 | practice | p04.006: read the solution once passed | ok | 21 |
| 763 | practice | p04.007: read the brief | ok | 0 |
| 764 | practice | p04.007: reveal every hint | ok | 58 |
| 765 | practice | p04.007: run an empty editor | ok | 197 |
| 766 | practice | p04.007: run the untouched starter | ok | 300 |
| 767 | practice | p04.007: run the reference solution | ok | 274 |
| 768 | practice | p04.007: read the solution once passed | ok | 18 |
| 769 | practice | p04.008: read the brief | ok | 0 |
| 770 | practice | p04.008: reveal every hint | ok | 50 |
| 771 | practice | p04.008: run an empty editor | ok | 251 |
| 772 | practice | p04.008: run the untouched starter | ok | 350 |
| 773 | practice | p04.008: run the reference solution | ok | 254 |
| 774 | practice | p04.008: read the solution once passed | ok | 24 |
| 775 | practice | p04.009: read the brief | ok | 0 |
| 776 | practice | p04.009: reveal every hint | ok | 52 |
| 777 | practice | p04.009: run an empty editor | ok | 242 |
| 778 | practice | p04.009: run the untouched starter | ok | 284 |
| 779 | practice | p04.009: run the reference solution | ok | 234 |
| 780 | practice | p04.009: read the solution once passed | ok | 31 |
| 781 | practice | p04.010: read the brief | ok | 0 |
| 782 | practice | p04.010: reveal every hint | ok | 26 |
| 783 | practice | p04.010: run an empty editor | ok | 283 |
| 784 | practice | p04.010: run the untouched starter | ok | 224 |
| 785 | practice | p04.010: run the reference solution | ok | 240 |
| 786 | practice | p04.010: read the solution once passed | ok | 18 |
| 787 | practice | p05.001: read the brief | ok | 0 |
| 788 | practice | p05.001: reveal every hint | ok | 34 |
| 789 | practice | p05.001: run an empty editor | ok | 294 |
| 790 | practice | p05.001: run the untouched starter | ok | 266 |
| 791 | practice | p05.001: run the reference solution | ok | 255 |
| 792 | practice | p05.001: read the solution once passed | ok | 21 |
| 793 | practice | p05.002: read the brief | ok | 0 |
| 794 | practice | p05.002: reveal every hint | ok | 48 |
| 795 | practice | p05.002: run an empty editor | ok | 257 |
| 796 | practice | p05.002: run the untouched starter | ok | 264 |
| 797 | practice | p05.002: run the reference solution | ok | 218 |
| 798 | practice | p05.002: read the solution once passed | ok | 22 |
| 799 | practice | p05.003: read the brief | ok | 0 |
| 800 | practice | p05.003: reveal every hint | ok | 32 |
| 801 | practice | p05.003: run an empty editor | ok | 247 |
| 802 | practice | p05.003: run the untouched starter | ok | 229 |
| 803 | practice | p05.003: run the reference solution | ok | 229 |
| 804 | practice | p05.003: read the solution once passed | ok | 15 |
| 805 | practice | p05.004: read the brief | ok | 0 |
| 806 | practice | p05.004: reveal every hint | ok | 39 |
| 807 | practice | p05.004: run an empty editor | ok | 265 |
| 808 | practice | p05.004: run the untouched starter | ok | 271 |
| 809 | practice | p05.004: run the reference solution | ok | 263 |
| 810 | practice | p05.004: read the solution once passed | ok | 21 |
| 811 | practice | p05.005: read the brief | ok | 0 |
| 812 | practice | p05.005: reveal every hint | ok | 30 |
| 813 | practice | p05.005: run an empty editor | ok | 227 |
| 814 | practice | p05.005: run the untouched starter | ok | 282 |
| 815 | practice | p05.005: run the reference solution | ok | 211 |
| 816 | practice | p05.005: read the solution once passed | ok | 17 |
| 817 | practice | p05.006: read the brief | ok | 0 |
| 818 | practice | p05.006: reveal every hint | ok | 25 |
| 819 | practice | p05.006: run an empty editor | ok | 218 |
| 820 | practice | p05.006: run the untouched starter | ok | 220 |
| 821 | practice | p05.006: run the reference solution | ok | 248 |
| 822 | practice | p05.006: read the solution once passed | ok | 25 |
| 823 | practice | p05.007: read the brief | ok | 0 |
| 824 | practice | p05.007: reveal every hint | ok | 32 |
| 825 | practice | p05.007: run an empty editor | ok | 205 |
| 826 | practice | p05.007: run the untouched starter | ok | 341 |
| 827 | practice | p05.007: run the reference solution | ok | 234 |
| 828 | practice | p05.007: read the solution once passed | ok | 19 |
| 829 | practice | p05.008: read the brief | ok | 0 |
| 830 | practice | p05.008: reveal every hint | ok | 38 |
| 831 | practice | p05.008: run an empty editor | ok | 252 |
| 832 | practice | p05.008: run the untouched starter | ok | 235 |
| 833 | practice | p05.008: run the reference solution | ok | 252 |
| 834 | practice | p05.008: read the solution once passed | ok | 18 |
| 835 | practice | p05.009: read the brief | ok | 0 |
| 836 | practice | p05.009: reveal every hint | ok | 25 |
| 837 | practice | p05.009: run an empty editor | ok | 266 |
| 838 | practice | p05.009: run the untouched starter | ok | 255 |
| 839 | practice | p05.009: run the reference solution | ok | 255 |
| 840 | practice | p05.009: read the solution once passed | ok | 28 |
| 841 | practice | p05.010: read the brief | ok | 0 |
| 842 | practice | p05.010: reveal every hint | ok | 25 |
| 843 | practice | p05.010: run an empty editor | ok | 274 |
| 844 | practice | p05.010: run the untouched starter | ok | 294 |
| 845 | practice | p05.010: run the reference solution | ok | 359 |
| 846 | practice | p05.010: read the solution once passed | ok | 19 |
| 847 | practice | p03.001: read the brief | ok | 0 |
| 848 | practice | p03.001: reveal every hint | ok | 21 |
| 849 | practice | p03.001: run an empty editor | ok | 204 |
| 850 | practice | p03.001: run the untouched starter | ok | 276 |
| 851 | practice | p03.001: run the reference solution | ok | 261 |
| 852 | practice | p03.001: read the solution once passed | ok | 33 |
| 853 | practice | p03.002: read the brief | ok | 0 |
| 854 | practice | p03.002: reveal every hint | ok | 28 |
| 855 | practice | p03.002: run an empty editor | ok | 273 |
| 856 | practice | p03.002: run the untouched starter | ok | 304 |
| 857 | practice | p03.002: run the reference solution | ok | 276 |
| 858 | practice | p03.002: read the solution once passed | ok | 34 |
| 859 | practice | p03.003: read the brief | ok | 0 |
| 860 | practice | p03.003: reveal every hint | ok | 28 |
| 861 | practice | p03.003: run an empty editor | ok | 246 |
| 862 | practice | p03.003: run the untouched starter | ok | 328 |
| 863 | practice | p03.003: run the reference solution | ok | 256 |
| 864 | practice | p03.003: read the solution once passed | ok | 35 |
| 865 | practice | p03.004: read the brief | ok | 0 |
| 866 | practice | p03.004: reveal every hint | ok | 26 |
| 867 | practice | p03.004: run an empty editor | ok | 278 |
| 868 | practice | p03.004: run the untouched starter | ok | 275 |
| 869 | practice | p03.004: run the reference solution | ok | 253 |
| 870 | practice | p03.004: read the solution once passed | ok | 17 |
| 871 | practice | p08.001: read the brief | ok | 0 |
| 872 | practice | p08.001: reveal every hint | ok | 39 |
| 873 | practice | p08.001: run an empty editor | ok | 269 |
| 874 | practice | p08.001: run the untouched starter | ok | 290 |
| 875 | practice | p08.001: run the reference solution | ok | 287 |
| 876 | practice | p08.001: read the solution once passed | ok | 21 |
| 877 | practice | p08.002: read the brief | ok | 0 |
| 878 | practice | p08.002: reveal every hint | ok | 34 |
| 879 | practice | p08.002: run an empty editor | ok | 264 |
| 880 | practice | p08.002: run the untouched starter | ok | 332 |
| 881 | practice | p08.002: run the reference solution | ok | 260 |
| 882 | practice | p08.002: read the solution once passed | ok | 23 |
| 883 | practice | p08.003: read the brief | ok | 0 |
| 884 | practice | p08.003: reveal every hint | ok | 53 |
| 885 | practice | p08.003: run an empty editor | ok | 255 |
| 886 | practice | p08.003: run the untouched starter | ok | 272 |
| 887 | practice | p08.003: run the reference solution | ok | 242 |
| 888 | practice | p08.003: read the solution once passed | ok | 20 |
| 889 | practice | p08.004: read the brief | ok | 0 |
| 890 | practice | p08.004: reveal every hint | ok | 23 |
| 891 | practice | p08.004: run an empty editor | ok | 254 |
| 892 | practice | p08.004: run the untouched starter | ok | 263 |
| 893 | practice | p08.004: run the reference solution | ok | 266 |
| 894 | practice | p08.004: read the solution once passed | ok | 17 |
| 895 | practice | p09.001: read the brief | ok | 0 |
| 896 | practice | p09.001: reveal every hint | ok | 47 |
| 897 | practice | p09.001: run an empty editor | ok | 195 |
| 898 | practice | p09.001: run the untouched starter | ok | 296 |
| 899 | practice | p09.001: run the reference solution | ok | 195 |
| 900 | practice | p09.001: read the solution once passed | ok | 18 |
| 901 | practice | p09.002: read the brief | ok | 0 |
| 902 | practice | p09.002: reveal every hint | ok | 51 |
| 903 | practice | p09.002: run an empty editor | ok | 230 |
| 904 | practice | p09.002: run the untouched starter | ok | 305 |
| 905 | practice | p09.002: run the reference solution | ok | 206 |
| 906 | practice | p09.002: read the solution once passed | ok | 20 |
| 907 | practice | p09.003: read the brief | ok | 0 |
| 908 | practice | p09.003: reveal every hint | ok | 34 |
| 909 | practice | p09.003: run an empty editor | ok | 255 |
| 910 | practice | p09.003: run the untouched starter | ok | 239 |
| 911 | practice | p09.003: run the reference solution | ok | 313 |
| 912 | practice | p09.003: read the solution once passed | ok | 24 |
| 913 | practice | p10.001: read the brief | ok | 0 |
| 914 | practice | p10.001: reveal every hint | ok | 39 |
| 915 | practice | p10.001: run an empty editor | ok | 244 |
| 916 | practice | p10.001: run the untouched starter | ok | 274 |
| 917 | practice | p10.001: run the reference solution | ok | 264 |
| 918 | practice | p10.001: read the solution once passed | ok | 26 |
| 919 | practice | p10.002: read the brief | ok | 0 |
| 920 | practice | p10.002: reveal every hint | ok | 50 |
| 921 | practice | p10.002: run an empty editor | ok | 270 |
| 922 | practice | p10.002: run the untouched starter | ok | 230 |
| 923 | practice | p10.002: run the reference solution | ok | 251 |
| 924 | practice | p10.002: read the solution once passed | ok | 16 |
| 925 | practice | p10.003: read the brief | ok | 0 |
| 926 | practice | p10.003: reveal every hint | ok | 32 |
| 927 | practice | p10.003: run an empty editor | ok | 252 |
| 928 | practice | p10.003: run the untouched starter | ok | 301 |
| 929 | practice | p10.003: run the reference solution | ok | 265 |
| 930 | practice | p10.003: read the solution once passed | ok | 18 |
| 931 | practice | p11.001: read the brief | ok | 0 |
| 932 | practice | p11.001: reveal every hint | ok | 30 |
| 933 | practice | p11.001: run an empty editor | ok | 422 |
| 934 | practice | p11.001: run the untouched starter | ok | 481 |
| 935 | practice | p11.001: run the reference solution | ok | 555 |
| 936 | practice | p11.001: read the solution once passed | ok | 17 |
| 937 | practice | p11.002: read the brief | ok | 0 |
| 938 | practice | p11.002: reveal every hint | ok | 21 |
| 939 | practice | p11.002: run an empty editor | ok | 458 |
| 940 | practice | p11.002: run the untouched starter | ok | 415 |
| 941 | practice | p11.002: run the reference solution | ok | 991 |
| 942 | practice | p11.002: read the solution once passed | ok | 20 |
| 943 | practice | p11.003: read the brief | ok | 0 |
| 944 | practice | p11.003: reveal every hint | ok | 20 |
| 945 | practice | p11.003: run an empty editor | ok | 382 |
| 946 | practice | p11.003: run the untouched starter | ok | 426 |
| 947 | practice | p11.003: run the reference solution | ok | 540 |
| 948 | practice | p11.003: read the solution once passed | ok | 19 |
| 949 | practice | p13.001: read the brief | ok | 0 |
| 950 | practice | p13.001: reveal every hint | ok | 28 |
| 951 | practice | p13.001: run an empty editor | ok | 217 |
| 952 | practice | p13.001: run the untouched starter | ok | 235 |
| 953 | practice | p13.001: run the reference solution | ok | 943 |
| 954 | practice | p13.001: read the solution once passed | ok | 21 |
| 955 | practice | p13.002: read the brief | ok | 0 |
| 956 | practice | p13.002: reveal every hint | ok | 21 |
| 957 | practice | p13.002: run an empty editor | ok | 262 |
| 958 | practice | p13.002: run the untouched starter | ok | 261 |
| 959 | practice | p13.002: run the reference solution | ok | 187 |
| 960 | practice | p13.002: read the solution once passed | ok | 16 |
| 961 | practice | p13.003: read the brief | ok | 0 |
| 962 | practice | p13.003: reveal every hint | ok | 27 |
| 963 | practice | p13.003: run an empty editor | ok | 255 |
| 964 | practice | p13.003: run the untouched starter | ok | 259 |
| 965 | practice | p13.003: run the reference solution | ok | 247 |
| 966 | practice | p13.003: read the solution once passed | ok | 33 |
| 967 | practice | p14.001: read the brief | ok | 0 |
| 968 | practice | p14.001: reveal every hint | ok | 30 |
| 969 | practice | p14.001: run an empty editor | ok | 236 |
| 970 | practice | p14.001: run the untouched starter | ok | 287 |
| 971 | practice | p14.001: run the reference solution | ok | 295 |
| 972 | practice | p14.001: read the solution once passed | ok | 32 |
| 973 | practice | p14.002: read the brief | ok | 0 |
| 974 | practice | p14.002: reveal every hint | ok | 42 |
| 975 | practice | p14.002: run an empty editor | ok | 259 |
| 976 | practice | p14.002: run the untouched starter | ok | 244 |
| 977 | practice | p14.002: run the reference solution | ok | 213 |
| 978 | practice | p14.002: read the solution once passed | ok | 26 |
| 979 | practice | p14.003: read the brief | ok | 0 |
| 980 | practice | p14.003: reveal every hint | ok | 35 |
| 981 | practice | p14.003: run an empty editor | ok | 283 |
| 982 | practice | p14.003: run the untouched starter | ok | 275 |
| 983 | practice | p14.003: run the reference solution | ok | 270 |
| 984 | practice | p14.003: read the solution once passed | ok | 23 |
| 985 | practice | p14.004: read the brief | ok | 0 |
| 986 | practice | p14.004: reveal every hint | ok | 26 |
| 987 | practice | p14.004: run an empty editor | ok | 220 |
| 988 | practice | p14.004: run the untouched starter | ok | 251 |
| 989 | practice | p14.004: run the reference solution | ok | 193 |
| 990 | practice | p14.004: read the solution once passed | ok | 29 |
| 991 | practice | p06.001: read the brief | ok | 0 |
| 992 | practice | p06.001: reveal every hint | ok | 46 |
| 993 | practice | p06.001: run an empty editor | ok | 242 |
| 994 | practice | p06.001: run the untouched starter | ok | 274 |
| 995 | practice | p06.001: run the reference solution | ok | 219 |
| 996 | practice | p06.001: read the solution once passed | ok | 17 |
| 997 | practice | p06.002: read the brief | ok | 0 |
| 998 | practice | p06.002: reveal every hint | ok | 32 |
| 999 | practice | p06.002: run an empty editor | ok | 220 |
| 1000 | practice | p06.002: run the untouched starter | ok | 244 |
| 1001 | practice | p06.002: run the reference solution | ok | 206 |
| 1002 | practice | p06.002: read the solution once passed | ok | 21 |
| 1003 | practice | p06.003: read the brief | ok | 0 |
| 1004 | practice | p06.003: reveal every hint | ok | 34 |
| 1005 | practice | p06.003: run an empty editor | ok | 173 |
| 1006 | practice | p06.003: run the untouched starter | ok | 227 |
| 1007 | practice | p06.003: run the reference solution | ok | 230 |
| 1008 | practice | p06.003: read the solution once passed | ok | 16 |
| 1009 | practice | p06.004: read the brief | ok | 0 |
| 1010 | practice | p06.004: reveal every hint | ok | 37 |
| 1011 | practice | p06.004: run an empty editor | ok | 199 |
| 1012 | practice | p06.004: run the untouched starter | ok | 261 |
| 1013 | practice | p06.004: run the reference solution | ok | 280 |
| 1014 | practice | p06.004: read the solution once passed | ok | 28 |
| 1015 | practice | p07.001: read the brief | ok | 0 |
| 1016 | practice | p07.001: reveal every hint | ok | 36 |
| 1017 | practice | p07.001: run an empty editor | ok | 206 |
| 1018 | practice | p07.001: run the untouched starter | ok | 336 |
| 1019 | practice | p07.001: run the reference solution | ok | 214 |
| 1020 | practice | p07.001: read the solution once passed | ok | 22 |
| 1021 | practice | p07.002: read the brief | ok | 0 |
| 1022 | practice | p07.002: reveal every hint | ok | 54 |
| 1023 | practice | p07.002: run an empty editor | ok | 212 |
| 1024 | practice | p07.002: run the untouched starter | ok | 281 |
| 1025 | practice | p07.002: run the reference solution | ok | 260 |
| 1026 | practice | p07.002: read the solution once passed | ok | 33 |
| 1027 | practice | p07.003: read the brief | ok | 0 |
| 1028 | practice | p07.003: reveal every hint | ok | 36 |
| 1029 | practice | p07.003: run an empty editor | ok | 217 |
| 1030 | practice | p07.003: run the untouched starter | ok | 247 |
| 1031 | practice | p07.003: run the reference solution | ok | 219 |
| 1032 | practice | p07.003: read the solution once passed | ok | 20 |
| 1033 | practice | p07.004: read the brief | ok | 0 |
| 1034 | practice | p07.004: reveal every hint | ok | 37 |
| 1035 | practice | p07.004: run an empty editor | ok | 205 |
| 1036 | practice | p07.004: run the untouched starter | ok | 279 |
| 1037 | practice | p07.004: run the reference solution | ok | 266 |
| 1038 | practice | p07.004: read the solution once passed | ok | 21 |
| 1039 | practice | p12.001: read the brief | ok | 0 |
| 1040 | practice | p12.001: reveal every hint | ok | 27 |
| 1041 | practice | p12.001: run an empty editor | ok | 231 |
| 1042 | practice | p12.001: run the untouched starter | ok | 238 |
| 1043 | practice | p12.001: run the reference solution | ok | 224 |
| 1044 | practice | p12.001: read the solution once passed | ok | 20 |
| 1045 | practice | p12.002: read the brief | ok | 0 |
| 1046 | practice | p12.002: reveal every hint | ok | 64 |
| 1047 | practice | p12.002: run an empty editor | ok | 200 |
| 1048 | practice | p12.002: run the untouched starter | ok | 229 |
| 1049 | practice | p12.002: run the reference solution | ok | 211 |
| 1050 | practice | p12.002: read the solution once passed | ok | 29 |
| 1051 | practice | p12.003: read the brief | ok | 0 |
| 1052 | practice | p12.003: reveal every hint | ok | 44 |
| 1053 | practice | p12.003: run an empty editor | ok | 192 |
| 1054 | practice | p12.003: run the untouched starter | ok | 232 |
| 1055 | practice | p12.003: run the reference solution | ok | 221 |
| 1056 | practice | p12.003: read the solution once passed | ok | 34 |
| 1057 | practice | p15.001: read the brief | ok | 0 |
| 1058 | practice | p15.001: reveal every hint | ok | 40 |
| 1059 | practice | p15.001: run an empty editor | ok | 213 |
| 1060 | practice | p15.001: run the untouched starter | ok | 243 |
| 1061 | practice | p15.001: run the reference solution | ok | 228 |
| 1062 | practice | p15.001: read the solution once passed | ok | 19 |
| 1063 | practice | p15.002: read the brief | ok | 0 |
| 1064 | practice | p15.002: reveal every hint | ok | 44 |
| 1065 | practice | p15.002: run an empty editor | ok | 237 |
| 1066 | practice | p15.002: run the untouched starter | ok | 228 |
| 1067 | practice | p15.002: run the reference solution | ok | 196 |
| 1068 | practice | p15.002: read the solution once passed | ok | 21 |
| 1069 | practice | p15.003: read the brief | ok | 0 |
| 1070 | practice | p15.003: reveal every hint | ok | 70 |
| 1071 | practice | p15.003: run an empty editor | ok | 209 |
| 1072 | practice | p15.003: run the untouched starter | ok | 265 |
| 1073 | practice | p15.003: run the reference solution | ok | 238 |
| 1074 | practice | p15.003: read the solution once passed | ok | 21 |
| 1075 | practice | p16.001: read the brief | ok | 0 |
| 1076 | practice | p16.001: reveal every hint | ok | 34 |
| 1077 | practice | p16.001: run an empty editor | ok | 182 |
| 1078 | practice | p16.001: run the untouched starter | ok | 268 |
| 1079 | practice | p16.001: run the reference solution | ok | 219 |
| 1080 | practice | p16.001: read the solution once passed | ok | 35 |
| 1081 | practice | p16.002: read the brief | ok | 0 |
| 1082 | practice | p16.002: reveal every hint | ok | 30 |
| 1083 | practice | p16.002: run an empty editor | ok | 198 |
| 1084 | practice | p16.002: run the untouched starter | ok | 237 |
| 1085 | practice | p16.002: run the reference solution | ok | 210 |
| 1086 | practice | p16.002: read the solution once passed | ok | 24 |
| 1087 | practice | p16.003: read the brief | ok | 0 |
| 1088 | practice | p16.003: reveal every hint | ok | 40 |
| 1089 | practice | p16.003: run an empty editor | ok | 220 |
| 1090 | practice | p16.003: run the untouched starter | ok | 233 |
| 1091 | practice | p16.003: run the reference solution | ok | 287 |
| 1092 | practice | p16.003: read the solution once passed | ok | 26 |
| 1093 | practice | p17.001: read the brief | ok | 0 |
| 1094 | practice | p17.001: reveal every hint | ok | 46 |
| 1095 | practice | p17.001: run an empty editor | ok | 262 |
| 1096 | practice | p17.001: run the untouched starter | ok | 276 |
| 1097 | practice | p17.001: run the reference solution | ok | 211 |
| 1098 | practice | p17.001: read the solution once passed | ok | 21 |
| 1099 | practice | p17.002: read the brief | ok | 0 |
| 1100 | practice | p17.002: reveal every hint | ok | 47 |
| 1101 | practice | p17.002: run an empty editor | ok | 258 |
| 1102 | practice | p17.002: run the untouched starter | ok | 264 |
| 1103 | practice | p17.002: run the reference solution | ok | 292 |
| 1104 | practice | p17.002: read the solution once passed | ok | 49 |
| 1105 | practice | p17.003: read the brief | ok | 0 |
| 1106 | practice | p17.003: reveal every hint | ok | 35 |
| 1107 | practice | p17.003: run an empty editor | ok | 249 |
| 1108 | practice | p17.003: run the untouched starter | ok | 278 |
| 1109 | practice | p17.003: run the reference solution | ok | 192 |
| 1110 | practice | p17.003: read the solution once passed | ok | 17 |
| 1111 | practice | s01.001: read the brief | ok | 0 |
| 1112 | practice | s01.001: reveal every hint | ok | 30 |
| 1113 | practice | s01.001: run an empty editor | ok | 213 |
| 1114 | practice | s01.001: run the untouched starter | ok | 236 |
| 1115 | practice | s01.001: run the reference solution | ok | 204 |
| 1116 | practice | s01.001: read the solution once passed | ok | 16 |
| 1117 | practice | s01.002: read the brief | ok | 0 |
| 1118 | practice | s01.002: reveal every hint | ok | 26 |
| 1119 | practice | s01.002: run an empty editor | ok | 185 |
| 1120 | practice | s01.002: run the untouched starter | ok | 210 |
| 1121 | practice | s01.002: run the reference solution | ok | 240 |
| 1122 | practice | s01.002: read the solution once passed | ok | 34 |
| 1123 | practice | s01.003: read the brief | ok | 0 |
| 1124 | practice | s01.003: reveal every hint | ok | 33 |
| 1125 | practice | s01.003: run an empty editor | ok | 286 |
| 1126 | practice | s01.003: run the untouched starter | ok | 218 |
| 1127 | practice | s01.003: run the reference solution | ok | 235 |
| 1128 | practice | s01.003: read the solution once passed | ok | 21 |
| 1129 | practice | s02.001: read the brief | ok | 0 |
| 1130 | practice | s02.001: reveal every hint | ok | 33 |
| 1131 | practice | s02.001: run an empty editor | ok | 292 |
| 1132 | practice | s02.001: run the untouched starter | ok | 254 |
| 1133 | practice | s02.001: run the reference solution | ok | 253 |
| 1134 | practice | s02.001: read the solution once passed | ok | 36 |
| 1135 | practice | s02.002: read the brief | ok | 0 |
| 1136 | practice | s02.002: reveal every hint | ok | 30 |
| 1137 | practice | s02.002: run an empty editor | ok | 247 |
| 1138 | practice | s02.002: run the untouched starter | ok | 246 |
| 1139 | practice | s02.002: run the reference solution | ok | 229 |
| 1140 | practice | s02.002: read the solution once passed | ok | 17 |
| 1141 | practice | s02.003: read the brief | ok | 0 |
| 1142 | practice | s02.003: reveal every hint | ok | 34 |
| 1143 | practice | s02.003: run an empty editor | ok | 234 |
| 1144 | practice | s02.003: run the untouched starter | ok | 251 |
| 1145 | practice | s02.003: run the reference solution | ok | 286 |
| 1146 | practice | s02.003: read the solution once passed | ok | 44 |
| 1147 | practice | s03.001: read the brief | ok | 0 |
| 1148 | practice | s03.001: reveal every hint | ok | 42 |
| 1149 | practice | s03.001: run an empty editor | ok | 283 |
| 1150 | practice | s03.001: run the untouched starter | ok | 231 |
| 1151 | practice | s03.001: run the reference solution | ok | 251 |
| 1152 | practice | s03.001: read the solution once passed | ok | 22 |
| 1153 | practice | s03.002: read the brief | ok | 0 |
| 1154 | practice | s03.002: reveal every hint | ok | 41 |
| 1155 | practice | s03.002: run an empty editor | ok | 292 |
| 1156 | practice | s03.002: run the untouched starter | ok | 270 |
| 1157 | practice | s03.002: run the reference solution | ok | 234 |
| 1158 | practice | s03.002: read the solution once passed | ok | 37 |
| 1159 | practice | s03.003: read the brief | ok | 0 |
| 1160 | practice | s03.003: reveal every hint | ok | 64 |
| 1161 | practice | s03.003: run an empty editor | ok | 261 |
| 1162 | practice | s03.003: run the untouched starter | ok | 255 |
| 1163 | practice | s03.003: run the reference solution | ok | 247 |
| 1164 | practice | s03.003: read the solution once passed | ok | 19 |
| 1165 | practice | s04.001: read the brief | ok | 0 |
| 1166 | practice | s04.001: reveal every hint | ok | 29 |
| 1167 | practice | s04.001: run an empty editor | ok | 193 |
| 1168 | practice | s04.001: run the untouched starter | ok | 302 |
| 1169 | practice | s04.001: run the reference solution | ok | 202 |
| 1170 | practice | s04.001: read the solution once passed | ok | 24 |
| 1171 | practice | s04.002: read the brief | ok | 0 |
| 1172 | practice | s04.002: reveal every hint | ok | 23 |
| 1173 | practice | s04.002: run an empty editor | ok | 221 |
| 1174 | practice | s04.002: run the untouched starter | ok | 252 |
| 1175 | practice | s04.002: run the reference solution | ok | 233 |
| 1176 | practice | s04.002: read the solution once passed | ok | 16 |
| 1177 | practice | s04.003: read the brief | ok | 0 |
| 1178 | practice | s04.003: reveal every hint | ok | 31 |
| 1179 | practice | s04.003: run an empty editor | ok | 198 |
| 1180 | practice | s04.003: run the untouched starter | ok | 209 |
| 1181 | practice | s04.003: run the reference solution | ok | 238 |
| 1182 | practice | s04.003: read the solution once passed | ok | 22 |
| 1183 | practice | s05.001: read the brief | ok | 0 |
| 1184 | practice | s05.001: reveal every hint | ok | 24 |
| 1185 | practice | s05.001: run an empty editor | ok | 196 |
| 1186 | practice | s05.001: run the untouched starter | ok | 249 |
| 1187 | practice | s05.001: run the reference solution | ok | 276 |
| 1188 | practice | s05.001: read the solution once passed | ok | 26 |
| 1189 | practice | s05.002: read the brief | ok | 0 |
| 1190 | practice | s05.002: reveal every hint | ok | 33 |
| 1191 | practice | s05.002: run an empty editor | ok | 244 |
| 1192 | practice | s05.002: run the untouched starter | ok | 228 |
| 1193 | practice | s05.002: run the reference solution | ok | 215 |
| 1194 | practice | s05.002: read the solution once passed | ok | 24 |
| 1195 | practice | s05.003: read the brief | ok | 0 |
| 1196 | practice | s05.003: reveal every hint | ok | 29 |
| 1197 | practice | s05.003: run an empty editor | ok | 191 |
| 1198 | practice | s05.003: run the untouched starter | ok | 207 |
| 1199 | practice | s05.003: run the reference solution | ok | 192 |
| 1200 | practice | s05.003: read the solution once passed | ok | 19 |
| 1201 | practice | s06.001: read the brief | ok | 0 |
| 1202 | practice | s06.001: reveal every hint | ok | 27 |
| 1203 | practice | s06.001: run an empty editor | ok | 256 |
| 1204 | practice | s06.001: run the untouched starter | ok | 239 |
| 1205 | practice | s06.001: run the reference solution | ok | 185 |
| 1206 | practice | s06.001: read the solution once passed | ok | 17 |
| 1207 | practice | s06.002: read the brief | ok | 0 |
| 1208 | practice | s06.002: reveal every hint | ok | 26 |
| 1209 | practice | s06.002: run an empty editor | ok | 202 |
| 1210 | practice | s06.002: run the untouched starter | ok | 262 |
| 1211 | practice | s06.002: run the reference solution | ok | 285 |
| 1212 | practice | s06.002: read the solution once passed | ok | 20 |
| 1213 | practice | s06.003: read the brief | ok | 0 |
| 1214 | practice | s06.003: reveal every hint | ok | 49 |
| 1215 | practice | s06.003: run an empty editor | ok | 204 |
| 1216 | practice | s06.003: run the untouched starter | ok | 201 |
| 1217 | practice | s06.003: run the reference solution | ok | 261 |
| 1218 | practice | s06.003: read the solution once passed | ok | 23 |
| 1219 | practice | s07.001: read the brief | ok | 0 |
| 1220 | practice | s07.001: reveal every hint | ok | 27 |
| 1221 | practice | s07.001: run an empty editor | ok | 213 |
| 1222 | practice | s07.001: run the untouched starter | ok | 305 |
| 1223 | practice | s07.001: run the reference solution | ok | 223 |
| 1224 | practice | s07.001: read the solution once passed | ok | 23 |
| 1225 | practice | s07.002: read the brief | ok | 0 |
| 1226 | practice | s07.002: reveal every hint | ok | 33 |
| 1227 | practice | s07.002: run an empty editor | ok | 270 |
| 1228 | practice | s07.002: run the untouched starter | ok | 210 |
| 1229 | practice | s07.002: run the reference solution | ok | 197 |
| 1230 | practice | s07.002: read the solution once passed | ok | 23 |
| 1231 | practice | s07.003: read the brief | ok | 0 |
| 1232 | practice | s07.003: reveal every hint | ok | 23 |
| 1233 | practice | s07.003: run an empty editor | ok | 211 |
| 1234 | practice | s07.003: run the untouched starter | ok | 226 |
| 1235 | practice | s07.003: run the reference solution | ok | 240 |
| 1236 | practice | s07.003: read the solution once passed | ok | 18 |
| 1237 | practice | s08.001: read the brief | ok | 0 |
| 1238 | practice | s08.001: reveal every hint | ok | 32 |
| 1239 | practice | s08.001: run an empty editor | ok | 246 |
| 1240 | practice | s08.001: run the untouched starter | ok | 236 |
| 1241 | practice | s08.001: run the reference solution | ok | 217 |
| 1242 | practice | s08.001: read the solution once passed | ok | 19 |
| 1243 | practice | s08.002: read the brief | ok | 0 |
| 1244 | practice | s08.002: reveal every hint | ok | 43 |
| 1245 | practice | s08.002: run an empty editor | ok | 224 |
| 1246 | practice | s08.002: run the untouched starter | ok | 221 |
| 1247 | practice | s08.002: run the reference solution | ok | 259 |
| 1248 | practice | s08.002: read the solution once passed | ok | 17 |
| 1249 | practice | s08.003: read the brief | ok | 0 |
| 1250 | practice | s08.003: reveal every hint | ok | 30 |
| 1251 | practice | s08.003: run an empty editor | ok | 250 |
| 1252 | practice | s08.003: run the untouched starter | ok | 255 |
| 1253 | practice | s08.003: run the reference solution | ok | 201 |
| 1254 | practice | s08.003: read the solution once passed | ok | 22 |
| 1255 | practice | s09.001: read the brief | ok | 0 |
| 1256 | practice | s09.001: reveal every hint | ok | 22 |
| 1257 | practice | s09.001: run an empty editor | ok | 246 |
| 1258 | practice | s09.001: run the untouched starter | ok | 228 |
| 1259 | practice | s09.001: run the reference solution | ok | 235 |
| 1260 | practice | s09.001: read the solution once passed | ok | 36 |
| 1261 | practice | s09.002: read the brief | ok | 0 |
| 1262 | practice | s09.002: reveal every hint | ok | 34 |
| 1263 | practice | s09.002: run an empty editor | ok | 204 |
| 1264 | practice | s09.002: run the untouched starter | ok | 289 |
| 1265 | practice | s09.002: run the reference solution | ok | 211 |
| 1266 | practice | s09.002: read the solution once passed | ok | 21 |
| 1267 | practice | s09.003: read the brief | ok | 0 |
| 1268 | practice | s09.003: reveal every hint | ok | 41 |
| 1269 | practice | s09.003: run an empty editor | ok | 206 |
| 1270 | practice | s09.003: run the untouched starter | ok | 223 |
| 1271 | practice | s09.003: run the reference solution | ok | 225 |
| 1272 | practice | s09.003: read the solution once passed | ok | 21 |
| 1273 | practice | s10.001: read the brief | ok | 0 |
| 1274 | practice | s10.001: reveal every hint | ok | 29 |
| 1275 | practice | s10.001: run an empty editor | ok | 208 |
| 1276 | practice | s10.001: run the untouched starter | ok | 243 |
| 1277 | practice | s10.001: run the reference solution | ok | 238 |
| 1278 | practice | s10.001: read the solution once passed | ok | 16 |
| 1279 | practice | s10.002: read the brief | ok | 0 |
| 1280 | practice | s10.002: reveal every hint | ok | 24 |
| 1281 | practice | s10.002: run an empty editor | ok | 185 |
| 1282 | practice | s10.002: run the untouched starter | ok | 234 |
| 1283 | practice | s10.002: run the reference solution | ok | 195 |
| 1284 | practice | s10.002: read the solution once passed | ok | 15 |
| 1285 | practice | s10.003: read the brief | ok | 0 |
| 1286 | practice | s10.003: reveal every hint | ok | 31 |
| 1287 | practice | s10.003: run an empty editor | ok | 211 |
| 1288 | practice | s10.003: run the untouched starter | ok | 240 |
| 1289 | practice | s10.003: run the reference solution | ok | 169 |
| 1290 | practice | s10.003: read the solution once passed | ok | 21 |
| 1291 | practice | s11.001: read the brief | ok | 0 |
| 1292 | practice | s11.001: reveal every hint | ok | 36 |
| 1293 | practice | s11.001: run an empty editor | ok | 217 |
| 1294 | practice | s11.001: run the untouched starter | ok | 252 |
| 1295 | practice | s11.001: run the reference solution | ok | 228 |
| 1296 | practice | s11.001: read the solution once passed | ok | 23 |
| 1297 | practice | s11.002: read the brief | ok | 0 |
| 1298 | practice | s11.002: reveal every hint | ok | 29 |
| 1299 | practice | s11.002: run an empty editor | ok | 236 |
| 1300 | practice | s11.002: run the untouched starter | ok | 277 |
| 1301 | practice | s11.002: run the reference solution | ok | 203 |
| 1302 | practice | s11.002: read the solution once passed | ok | 15 |
| 1303 | practice | s11.003: read the brief | ok | 0 |
| 1304 | practice | s11.003: reveal every hint | ok | 44 |
| 1305 | practice | s11.003: run an empty editor | ok | 261 |
| 1306 | practice | s11.003: run the untouched starter | ok | 205 |
| 1307 | practice | s11.003: run the reference solution | ok | 215 |
| 1308 | practice | s11.003: read the solution once passed | ok | 17 |
| 1309 | practice | s12.001: read the brief | ok | 0 |
| 1310 | practice | s12.001: reveal every hint | ok | 39 |
| 1311 | practice | s12.001: run an empty editor | ok | 248 |
| 1312 | practice | s12.001: run the untouched starter | ok | 216 |
| 1313 | practice | s12.001: run the reference solution | ok | 262 |
| 1314 | practice | s12.001: read the solution once passed | ok | 26 |
| 1315 | practice | s12.002: read the brief | ok | 0 |
| 1316 | practice | s12.002: reveal every hint | ok | 36 |
| 1317 | practice | s12.002: run an empty editor | ok | 211 |
| 1318 | practice | s12.002: run the untouched starter | ok | 304 |
| 1319 | practice | s12.002: run the reference solution | ok | 245 |
| 1320 | practice | s12.002: read the solution once passed | ok | 15 |
| 1321 | practice | s12.003: read the brief | ok | 0 |
| 1322 | practice | s12.003: reveal every hint | ok | 25 |
| 1323 | practice | s12.003: run an empty editor | ok | 250 |
| 1324 | practice | s12.003: run the untouched starter | ok | 243 |
| 1325 | practice | s12.003: run the reference solution | ok | 240 |
| 1326 | practice | s12.003: read the solution once passed | ok | 25 |
| 1327 | practice | s13.001: read the brief | ok | 0 |
| 1328 | practice | s13.001: reveal every hint | ok | 30 |
| 1329 | practice | s13.001: run an empty editor | ok | 206 |
| 1330 | practice | s13.001: run the untouched starter | ok | 314 |
| 1331 | practice | s13.001: run the reference solution | ok | 236 |
| 1332 | practice | s13.001: read the solution once passed | ok | 27 |
| 1333 | practice | s13.002: read the brief | ok | 0 |
| 1334 | practice | s13.002: reveal every hint | ok | 35 |
| 1335 | practice | s13.002: run an empty editor | ok | 217 |
| 1336 | practice | s13.002: run the untouched starter | ok | 265 |
| 1337 | practice | s13.002: run the reference solution | ok | 256 |
| 1338 | practice | s13.002: read the solution once passed | ok | 17 |
| 1339 | practice | s13.003: read the brief | ok | 0 |
| 1340 | practice | s13.003: reveal every hint | ok | 32 |
| 1341 | practice | s13.003: run an empty editor | ok | 214 |
| 1342 | practice | s13.003: run the untouched starter | ok | 264 |
| 1343 | practice | s13.003: run the reference solution | ok | 250 |
| 1344 | practice | s13.003: read the solution once passed | ok | 19 |
| 1345 | practice | s14.001: read the brief | ok | 0 |
| 1346 | practice | s14.001: reveal every hint | ok | 45 |
| 1347 | practice | s14.001: run an empty editor | ok | 273 |
| 1348 | practice | s14.001: run the untouched starter | ok | 262 |
| 1349 | practice | s14.001: run the reference solution | ok | 234 |
| 1350 | practice | s14.001: read the solution once passed | ok | 35 |
| 1351 | practice | s14.002: read the brief | ok | 0 |
| 1352 | practice | s14.002: reveal every hint | ok | 30 |
| 1353 | practice | s14.002: run an empty editor | ok | 234 |
| 1354 | practice | s14.002: run the untouched starter | ok | 202 |
| 1355 | practice | s14.002: run the reference solution | ok | 258 |
| 1356 | practice | s14.002: read the solution once passed | ok | 19 |
| 1357 | practice | s14.003: read the brief | ok | 0 |
| 1358 | practice | s14.003: reveal every hint | ok | 35 |
| 1359 | practice | s14.003: run an empty editor | ok | 233 |
| 1360 | practice | s14.003: run the untouched starter | ok | 279 |
| 1361 | practice | s14.003: run the reference solution | ok | 210 |
| 1362 | practice | s14.003: read the solution once passed | ok | 21 |
| 1363 | practice | the counter agrees with the store | ok | 0 |
| 1364 | practice | press Run checks and read the result | ok | 208 |
| 1365 | practice | close the window while a run is in flight | ok | 12064 |
| 1366 | quiz | read the quiz picker | ok | 0 |
| 1367 | quiz | answer all 8 questions in q00 correctly | ok | 301 |
| 1368 | quiz | answer all 18 questions in q01 correctly | ok | 552 |
| 1369 | quiz | answer all 11 questions in q02 correctly | ok | 332 |
| 1370 | quiz | answer all 8 questions in q03 correctly | ok | 222 |
| 1371 | quiz | answer all 18 questions in q04 correctly | ok | 571 |
| 1372 | quiz | answer all 12 questions in q05 correctly | ok | 438 |
| 1373 | quiz | answer all 12 questions in q06 correctly | ok | 436 |
| 1374 | quiz | answer all 13 questions in q07 correctly | ok | 594 |
| 1375 | quiz | answer all 14 questions in q08 correctly | ok | 440 |
| 1376 | quiz | answer all 13 questions in q09 correctly | ok | 564 |
| 1377 | quiz | answer all 12 questions in q10 correctly | ok | 443 |
| 1378 | quiz | answer all 10 questions in q11 correctly | ok | 329 |
| 1379 | quiz | answer all 8 questions in q12 correctly | ok | 306 |
| 1380 | quiz | answer all 9 questions in q13 correctly | ok | 290 |
| 1381 | quiz | answer all 10 questions in q14 correctly | ok | 334 |
| 1382 | quiz | answer all 18 questions in q15 correctly | ok | 577 |
| 1383 | quiz | answer all 18 questions in q16 correctly | ok | 644 |
| 1384 | quiz | answer all 14 questions in q17 correctly | ok | 559 |
| 1385 | quiz | answer all 8 questions in q18 correctly | ok | 273 |
| 1386 | quiz | answer all 8 questions in q99 correctly | ok | 208 |
| 1387 | quiz | answer all 8 questions in q20 correctly | ok | 225 |
| 1388 | quiz | answer all 8 questions in q21 correctly | ok | 193 |
| 1389 | quiz | answer all 8 questions in q22 correctly | ok | 262 |
| 1390 | quiz | answer all 8 questions in q23 correctly | ok | 202 |
| 1391 | quiz | answer all 8 questions in q24 correctly | ok | 232 |
| 1392 | quiz | answer all 8 questions in q25 correctly | ok | 230 |
| 1393 | quiz | answer all 8 questions in q26 correctly | ok | 275 |
| 1394 | quiz | answer all 8 questions in q27 correctly | ok | 236 |
| 1395 | quiz | answer all 8 questions in q28 correctly | ok | 229 |
| 1396 | quiz | answer all 8 questions in q29 correctly | ok | 235 |
| 1397 | quiz | answer all 8 questions in q30 correctly | ok | 245 |
| 1398 | quiz | answer all 8 questions in q31 correctly | ok | 271 |
| 1399 | quiz | answer all 8 questions in q32 correctly | ok | 233 |
| 1400 | quiz | answer all 8 questions in q33 correctly | ok | 257 |
| 1401 | quiz | get every question in q00 wrong | ok | 327 |
| 1402 | quiz | read the wrap-up for q00 | ok | 0 |
| 1403 | quiz | get every question in q01 wrong | ok | 716 |
| 1404 | quiz | read the wrap-up for q01 | ok | 0 |
| 1405 | quiz | get every question in q02 wrong | ok | 508 |
| 1406 | quiz | read the wrap-up for q02 | ok | 1 |
| 1407 | quiz | get every question in q03 wrong | ok | 389 |
| 1408 | quiz | read the wrap-up for q03 | ok | 0 |
| 1409 | quiz | get every question in q04 wrong | ok | 907 |
| 1410 | quiz | read the wrap-up for q04 | ok | 0 |
| 1411 | quiz | get every question in q05 wrong | ok | 683 |
| 1412 | quiz | read the wrap-up for q05 | ok | 0 |
| 1413 | quiz | get every question in q06 wrong | ok | 693 |
| 1414 | quiz | read the wrap-up for q06 | ok | 1 |
| 1415 | quiz | get every question in q07 wrong | ok | 689 |
| 1416 | quiz | read the wrap-up for q07 | ok | 0 |
| 1417 | quiz | get every question in q08 wrong | ok | 633 |
| 1418 | quiz | read the wrap-up for q08 | ok | 0 |
| 1419 | quiz | get every question in q09 wrong | ok | 633 |
| 1420 | quiz | read the wrap-up for q09 | ok | 0 |
| 1421 | quiz | get every question in q10 wrong | ok | 583 |
| 1422 | quiz | read the wrap-up for q10 | ok | 0 |
| 1423 | quiz | get every question in q11 wrong | ok | 565 |
| 1424 | quiz | read the wrap-up for q11 | ok | 0 |
| 1425 | quiz | get every question in q12 wrong | ok | 316 |
| 1426 | quiz | read the wrap-up for q12 | ok | 0 |
| 1427 | quiz | get every question in q13 wrong | ok | 437 |
| 1428 | quiz | read the wrap-up for q13 | ok | 0 |
| 1429 | quiz | get every question in q14 wrong | ok | 450 |
| 1430 | quiz | read the wrap-up for q14 | ok | 0 |
| 1431 | quiz | get every question in q15 wrong | ok | 815 |
| 1432 | quiz | read the wrap-up for q15 | ok | 0 |
| 1433 | quiz | get every question in q16 wrong | ok | 931 |
| 1434 | quiz | read the wrap-up for q16 | ok | 0 |
| 1435 | quiz | get every question in q17 wrong | ok | 685 |
| 1436 | quiz | read the wrap-up for q17 | ok | 0 |
| 1437 | quiz | get every question in q18 wrong | ok | 378 |
| 1438 | quiz | read the wrap-up for q18 | ok | 0 |
| 1439 | quiz | get every question in q99 wrong | ok | 388 |
| 1440 | quiz | read the wrap-up for q99 | ok | 0 |
| 1441 | quiz | get every question in q20 wrong | ok | 287 |
| 1442 | quiz | read the wrap-up for q20 | ok | 0 |
| 1443 | quiz | get every question in q21 wrong | ok | 326 |
| 1444 | quiz | read the wrap-up for q21 | ok | 0 |
| 1445 | quiz | get every question in q22 wrong | ok | 316 |
| 1446 | quiz | read the wrap-up for q22 | ok | 0 |
| 1447 | quiz | get every question in q23 wrong | ok | 339 |
| 1448 | quiz | read the wrap-up for q23 | ok | 0 |
| 1449 | quiz | get every question in q24 wrong | ok | 338 |
| 1450 | quiz | read the wrap-up for q24 | ok | 0 |
| 1451 | quiz | get every question in q25 wrong | ok | 407 |
| 1452 | quiz | read the wrap-up for q25 | ok | 0 |
| 1453 | quiz | get every question in q26 wrong | ok | 366 |
| 1454 | quiz | read the wrap-up for q26 | ok | 0 |
| 1455 | quiz | get every question in q27 wrong | ok | 310 |
| 1456 | quiz | read the wrap-up for q27 | ok | 0 |
| 1457 | quiz | get every question in q28 wrong | ok | 347 |
| 1458 | quiz | read the wrap-up for q28 | ok | 0 |
| 1459 | quiz | get every question in q29 wrong | ok | 294 |
| 1460 | quiz | read the wrap-up for q29 | ok | 0 |
| 1461 | quiz | get every question in q30 wrong | ok | 316 |
| 1462 | quiz | read the wrap-up for q30 | ok | 0 |
| 1463 | quiz | get every question in q31 wrong | ok | 256 |
| 1464 | quiz | read the wrap-up for q31 | ok | 1 |
| 1465 | quiz | get every question in q32 wrong | ok | 325 |
| 1466 | quiz | read the wrap-up for q32 | ok | 0 |
| 1467 | quiz | get every question in q33 wrong | ok | 397 |
| 1468 | quiz | read the wrap-up for q33 | ok | 0 |
| 1469 | review | the wrong answers are waiting in review | ok | 4 |
| 1470 | quiz | skip every question without answering | ok | 335 |
| 1471 | quiz | retake it | ok | 40 |
| 1472 | quiz | go back to the picker | ok | 173 |
| 1473 | review | open Review with nothing started | ok | 0 |
| 1474 | review | answer card 1 of 15 | ok | 45 |
| 1475 | review | answer card 2 of 15 | ok | 39 |
| 1476 | review | answer card 3 of 15 | ok | 41 |
| 1477 | review | answer card 4 of 15 | ok | 59 |
| 1478 | review | answer card 5 of 15 | ok | 32 |
| 1479 | review | answer card 6 of 15 | ok | 48 |
| 1480 | review | answer card 7 of 15 | ok | 41 |
| 1481 | review | answer card 8 of 15 | ok | 56 |
| 1482 | review | answer card 9 of 15 | ok | 50 |
| 1483 | review | answer card 10 of 15 | ok | 55 |
| 1484 | review | answer card 11 of 15 | ok | 40 |
| 1485 | review | answer card 12 of 15 | ok | 38 |
| 1486 | review | answer card 13 of 15 | ok | 39 |
| 1487 | review | answer card 14 of 15 | ok | 56 |
| 1488 | review | answer card 15 of 15 | ok | 61 |
| 1489 | review | the session ends with a clear queue | ok | 0 |
| 1490 | review | skip the card in front of you | ok | 12 |
| 1491 | review | work to the daily limit | ok | 165 |
| 1492 | review | the idle screen explains the limit | ok | 0 |
| 1493 | review | open Review with a thousand cards due | ok | 45 |
| 1494 | projects | read all 36 project cards | ok | 2 |
| 1495 | projects | meet every requirement of pj.p00.1 | ok | 62 |
| 1496 | projects | meet every requirement of pj.p01.1 | ok | 57 |
| 1497 | projects | meet every requirement of pj.p01.2 | ok | 57 |
| 1498 | projects | meet every requirement of pj.p02.1 | ok | 73 |
| 1499 | projects | meet every requirement of pj.p02.2 | ok | 70 |
| 1500 | projects | meet every requirement of pj.p03.1 | ok | 80 |
| 1501 | projects | meet every requirement of pj.p04.1 | ok | 51 |
| 1502 | projects | meet every requirement of pj.p05.1 | ok | 71 |
| 1503 | projects | meet every requirement of pj.p06.1 | ok | 57 |
| 1504 | projects | meet every requirement of pj.p07.1 | ok | 85 |
| 1505 | projects | meet every requirement of pj.p08.1 | ok | 54 |
| 1506 | projects | meet every requirement of pj.p09.1 | ok | 95 |
| 1507 | projects | meet every requirement of pj.p10.1 | ok | 80 |
| 1508 | projects | meet every requirement of pj.p11.1 | ok | 77 |
| 1509 | projects | meet every requirement of pj.p12.1 | ok | 79 |
| 1510 | projects | meet every requirement of pj.p13.1 | ok | 74 |
| 1511 | projects | meet every requirement of pj.p14.1 | ok | 92 |
| 1512 | projects | meet every requirement of pj.p14.2 | ok | 108 |
| 1513 | projects | meet every requirement of pj.p15.1 | ok | 91 |
| 1514 | projects | meet every requirement of pj.p16.1 | ok | 64 |
| 1515 | projects | meet every requirement of pj.p17.1 | ok | 71 |
| 1516 | projects | meet every requirement of pj.p99.1 | ok | 98 |
| 1517 | projects | meet every requirement of pj.s01.1 | ok | 74 |
| 1518 | projects | meet every requirement of pj.s02.1 | ok | 95 |
| 1519 | projects | meet every requirement of pj.s03.1 | ok | 65 |
| 1520 | projects | meet every requirement of pj.s04.1 | ok | 88 |
| 1521 | projects | meet every requirement of pj.s05.1 | ok | 78 |
| 1522 | projects | meet every requirement of pj.s06.1 | ok | 53 |
| 1523 | projects | meet every requirement of pj.s07.1 | ok | 58 |
| 1524 | projects | meet every requirement of pj.s08.1 | ok | 64 |
| 1525 | projects | meet every requirement of pj.s09.1 | ok | 44 |
| 1526 | projects | meet every requirement of pj.s10.1 | ok | 65 |
| 1527 | projects | meet every requirement of pj.s11.1 | ok | 60 |
| 1528 | projects | meet every requirement of pj.s12.1 | ok | 78 |
| 1529 | projects | meet every requirement of pj.s13.1 | ok | 99 |
| 1530 | projects | meet every requirement of pj.s14.1 | ok | 110 |
| 1531 | projects | the meters agree once everything is met | ok | 7 |
| 1532 | projects | untick pj.p00.1 again | ok | 56 |
| 1533 | projects | untick pj.p01.1 again | ok | 141 |
| 1534 | projects | untick pj.p01.2 again | ok | 131 |
| 1535 | projects | untick pj.p02.1 again | ok | 92 |
| 1536 | projects | untick pj.p02.2 again | ok | 97 |
| 1537 | projects | untick pj.p03.1 again | ok | 72 |
| 1538 | projects | untick pj.p04.1 again | ok | 66 |
| 1539 | projects | untick pj.p05.1 again | ok | 73 |
| 1540 | projects | untick pj.p06.1 again | ok | 108 |
| 1541 | projects | untick pj.p07.1 again | ok | 129 |
| 1542 | projects | untick pj.p08.1 again | ok | 73 |
| 1543 | projects | untick pj.p09.1 again | ok | 123 |
| 1544 | projects | untick pj.p10.1 again | ok | 81 |
| 1545 | projects | untick pj.p11.1 again | ok | 100 |
| 1546 | projects | untick pj.p12.1 again | ok | 90 |
| 1547 | projects | untick pj.p13.1 again | ok | 88 |
| 1548 | projects | untick pj.p14.1 again | ok | 62 |
| 1549 | projects | untick pj.p14.2 again | ok | 106 |
| 1550 | projects | untick pj.p15.1 again | ok | 76 |
| 1551 | projects | untick pj.p16.1 again | ok | 79 |
| 1552 | projects | untick pj.p17.1 again | ok | 111 |
| 1553 | projects | untick pj.p99.1 again | ok | 58 |
| 1554 | projects | untick pj.s01.1 again | ok | 85 |
| 1555 | projects | untick pj.s02.1 again | ok | 50 |
| 1556 | projects | untick pj.s03.1 again | ok | 56 |
| 1557 | projects | untick pj.s04.1 again | ok | 54 |
| 1558 | projects | untick pj.s05.1 again | ok | 42 |
| 1559 | projects | untick pj.s06.1 again | ok | 48 |
| 1560 | projects | untick pj.s07.1 again | ok | 35 |
| 1561 | projects | untick pj.s08.1 again | ok | 29 |
| 1562 | projects | untick pj.s09.1 again | ok | 36 |
| 1563 | projects | untick pj.s10.1 again | ok | 58 |
| 1564 | projects | untick pj.s11.1 again | ok | 38 |
| 1565 | projects | untick pj.s12.1 again | ok | 29 |
| 1566 | projects | untick pj.s13.1 again | ok | 35 |
| 1567 | projects | untick pj.s14.1 again | ok | 34 |
| 1568 | projects | mark pj.p00.1 as Not started | ok | 54 |
| 1569 | projects | mark pj.p00.1 as In progress | ok | 14 |
| 1570 | projects | mark pj.p00.1 as Shipped | ok | 27 |
| 1571 | projects | mark pj.p01.1 as Not started | ok | 16 |
| 1572 | projects | mark pj.p01.1 as In progress | ok | 20 |
| 1573 | projects | mark pj.p01.1 as Shipped | ok | 22 |
| 1574 | projects | mark pj.p01.2 as Not started | ok | 18 |
| 1575 | projects | mark pj.p01.2 as In progress | ok | 19 |
| 1576 | projects | mark pj.p01.2 as Shipped | ok | 23 |
| 1577 | projects | mark pj.p02.1 as Not started | ok | 15 |
| 1578 | projects | mark pj.p02.1 as In progress | ok | 16 |
| 1579 | projects | mark pj.p02.1 as Shipped | ok | 19 |
| 1580 | projects | mark pj.p02.2 as Not started | ok | 20 |
| 1581 | projects | mark pj.p02.2 as In progress | ok | 20 |
| 1582 | projects | mark pj.p02.2 as Shipped | ok | 21 |
| 1583 | projects | mark pj.p03.1 as Not started | ok | 18 |
| 1584 | projects | mark pj.p03.1 as In progress | ok | 20 |
| 1585 | projects | mark pj.p03.1 as Shipped | ok | 26 |
| 1586 | projects | mark pj.p04.1 as Not started | ok | 16 |
| 1587 | projects | mark pj.p04.1 as In progress | ok | 18 |
| 1588 | projects | mark pj.p04.1 as Shipped | ok | 15 |
| 1589 | projects | mark pj.p05.1 as Not started | ok | 17 |
| 1590 | projects | mark pj.p05.1 as In progress | ok | 17 |
| 1591 | projects | mark pj.p05.1 as Shipped | ok | 38 |
| 1592 | projects | mark pj.p06.1 as Not started | ok | 27 |
| 1593 | projects | mark pj.p06.1 as In progress | ok | 15 |
| 1594 | projects | mark pj.p06.1 as Shipped | ok | 15 |
| 1595 | projects | mark pj.p07.1 as Not started | ok | 22 |
| 1596 | projects | mark pj.p07.1 as In progress | ok | 39 |
| 1597 | projects | mark pj.p07.1 as Shipped | ok | 18 |
| 1598 | projects | mark pj.p08.1 as Not started | ok | 12 |
| 1599 | projects | mark pj.p08.1 as In progress | ok | 13 |
| 1600 | projects | mark pj.p08.1 as Shipped | ok | 17 |
| 1601 | projects | mark pj.p09.1 as Not started | ok | 30 |
| 1602 | projects | mark pj.p09.1 as In progress | ok | 25 |
| 1603 | projects | mark pj.p09.1 as Shipped | ok | 20 |
| 1604 | projects | mark pj.p10.1 as Not started | ok | 15 |
| 1605 | projects | mark pj.p10.1 as In progress | ok | 14 |
| 1606 | projects | mark pj.p10.1 as Shipped | ok | 27 |
| 1607 | projects | mark pj.p11.1 as Not started | ok | 17 |
| 1608 | projects | mark pj.p11.1 as In progress | ok | 13 |
| 1609 | projects | mark pj.p11.1 as Shipped | ok | 16 |
| 1610 | projects | mark pj.p12.1 as Not started | ok | 25 |
| 1611 | projects | mark pj.p12.1 as In progress | ok | 24 |
| 1612 | projects | mark pj.p12.1 as Shipped | ok | 23 |
| 1613 | projects | mark pj.p13.1 as Not started | ok | 19 |
| 1614 | projects | mark pj.p13.1 as In progress | ok | 19 |
| 1615 | projects | mark pj.p13.1 as Shipped | ok | 28 |
| 1616 | projects | mark pj.p14.1 as Not started | ok | 19 |
| 1617 | projects | mark pj.p14.1 as In progress | ok | 23 |
| 1618 | projects | mark pj.p14.1 as Shipped | ok | 16 |
| 1619 | projects | mark pj.p14.2 as Not started | ok | 15 |
| 1620 | projects | mark pj.p14.2 as In progress | ok | 19 |
| 1621 | projects | mark pj.p14.2 as Shipped | ok | 28 |
| 1622 | projects | mark pj.p15.1 as Not started | ok | 35 |
| 1623 | projects | mark pj.p15.1 as In progress | ok | 17 |
| 1624 | projects | mark pj.p15.1 as Shipped | ok | 20 |
| 1625 | projects | mark pj.p16.1 as Not started | ok | 19 |
| 1626 | projects | mark pj.p16.1 as In progress | ok | 24 |
| 1627 | projects | mark pj.p16.1 as Shipped | ok | 36 |
| 1628 | projects | mark pj.p17.1 as Not started | ok | 22 |
| 1629 | projects | mark pj.p17.1 as In progress | ok | 18 |
| 1630 | projects | mark pj.p17.1 as Shipped | ok | 21 |
| 1631 | projects | mark pj.p99.1 as Not started | ok | 14 |
| 1632 | projects | mark pj.p99.1 as In progress | ok | 16 |
| 1633 | projects | mark pj.p99.1 as Shipped | ok | 19 |
| 1634 | projects | mark pj.s01.1 as Not started | ok | 15 |
| 1635 | projects | mark pj.s01.1 as In progress | ok | 14 |
| 1636 | projects | mark pj.s01.1 as Shipped | ok | 13 |
| 1637 | projects | mark pj.s02.1 as Not started | ok | 14 |
| 1638 | projects | mark pj.s02.1 as In progress | ok | 12 |
| 1639 | projects | mark pj.s02.1 as Shipped | ok | 14 |
| 1640 | projects | mark pj.s03.1 as Not started | ok | 15 |
| 1641 | projects | mark pj.s03.1 as In progress | ok | 17 |
| 1642 | projects | mark pj.s03.1 as Shipped | ok | 19 |
| 1643 | projects | mark pj.s04.1 as Not started | ok | 12 |
| 1644 | projects | mark pj.s04.1 as In progress | ok | 14 |
| 1645 | projects | mark pj.s04.1 as Shipped | ok | 17 |
| 1646 | projects | mark pj.s05.1 as Not started | ok | 14 |
| 1647 | projects | mark pj.s05.1 as In progress | ok | 15 |
| 1648 | projects | mark pj.s05.1 as Shipped | ok | 19 |
| 1649 | projects | mark pj.s06.1 as Not started | ok | 14 |
| 1650 | projects | mark pj.s06.1 as In progress | ok | 12 |
| 1651 | projects | mark pj.s06.1 as Shipped | ok | 12 |
| 1652 | projects | mark pj.s07.1 as Not started | ok | 11 |
| 1653 | projects | mark pj.s07.1 as In progress | ok | 11 |
| 1654 | projects | mark pj.s07.1 as Shipped | ok | 12 |
| 1655 | projects | mark pj.s08.1 as Not started | ok | 14 |
| 1656 | projects | mark pj.s08.1 as In progress | ok | 15 |
| 1657 | projects | mark pj.s08.1 as Shipped | ok | 28 |
| 1658 | projects | mark pj.s09.1 as Not started | ok | 43 |
| 1659 | projects | mark pj.s09.1 as In progress | ok | 27 |
| 1660 | projects | mark pj.s09.1 as Shipped | ok | 14 |
| 1661 | projects | mark pj.s10.1 as Not started | ok | 13 |
| 1662 | projects | mark pj.s10.1 as In progress | ok | 16 |
| 1663 | projects | mark pj.s10.1 as Shipped | ok | 16 |
| 1664 | projects | mark pj.s11.1 as Not started | ok | 20 |
| 1665 | projects | mark pj.s11.1 as In progress | ok | 26 |
| 1666 | projects | mark pj.s11.1 as Shipped | ok | 35 |
| 1667 | projects | mark pj.s12.1 as Not started | ok | 36 |
| 1668 | projects | mark pj.s12.1 as In progress | ok | 18 |
| 1669 | projects | mark pj.s12.1 as Shipped | ok | 15 |
| 1670 | projects | mark pj.s13.1 as Not started | ok | 22 |
| 1671 | projects | mark pj.s13.1 as In progress | ok | 14 |
| 1672 | projects | mark pj.s13.1 as Shipped | ok | 28 |
| 1673 | projects | mark pj.s14.1 as Not started | ok | 16 |
| 1674 | projects | mark pj.s14.1 as In progress | ok | 19 |
| 1675 | projects | mark pj.s14.1 as Shipped | ok | 17 |
| 1676 | projects | try each filter | ok | 247 |
| 1677 | projects | record a repo and some notes | ok | 493 |
| 1678 | projects | press Open next to the repo | ok | 2 |
| 1679 | projects | jump to the project's phase | ok | 286 |
| 1680 | projects | ship all 36 projects | ok | 357 |
| 1681 | today | Today agrees | ok | 55 |
| 1682 | projects | press a status button | 25 ms | 25 |
| 1683 | journal | write today's entry | ok | 25 |
| 1684 | journal | add three more days | ok | 115 |
| 1685 | journal | an entry is edited by writing it again | ok | 46 |
| 1686 | journal | delete every entry from the history | ok | 137 |
| 1687 | stats | the charts render with no data at all | ok | 3 |
| 1688 | stats | the charts render with one data point | ok | 123 |
| 1689 | stats | the charts render with a year of data | ok | 145 |
| 1690 | stats | rate every skill in the matrix | ok | 14 |
| 1691 | stats | the table covers the whole plan | ok | 106 |
| 1692 | library | open the Shelf tab | ok | 36 |
| 1693 | library | open the Fields of work tab | ok | 75 |
| 1694 | library | open the Video tab | ok | 51 |
| 1695 | library | open the Certificates tab | ok | 50 |
| 1696 | library | press every Open on the Shelf tab | ok | 7 |
| 1697 | library | press every Open on the Fields of work tab | ok | 0 |
| 1698 | library | press every Open on the Video tab | ok | 3 |
| 1699 | library | press every Open on the Certificates tab | ok | 0 |
| 1700 | library | press every field library button | ok | 65 |
| 1701 | library | cycle c-cs50p through every state | ok | 600 |
| 1702 | library | cycle c-helsinki through every state | ok | 573 |
| 1703 | library | cycle c-fcc-sci through every state | ok | 602 |
| 1704 | library | cycle c-netacad1 through every state | ok | 651 |
| 1705 | library | cycle c-netacad2 through every state | ok | 763 |
| 1706 | library | cycle c-pcep through every state | ok | 680 |
| 1707 | library | cycle c-pcap through every state | ok | 701 |
| 1708 | library | cycle c-hackerrank through every state | ok | 565 |
| 1709 | library | cycle c-kaggle through every state | ok | 614 |
| 1710 | library | cycle c-fcc-data through every state | ok | 584 |
| 1711 | library | cycle c-fcc-ml through every state | ok | 641 |
| 1712 | library | cycle c-hf-agents through every state | ok | 669 |
| 1713 | library | cycle c-hf-llm through every state | ok | 672 |
| 1714 | library | cycle c-hf-mcp through every state | ok | 651 |
| 1715 | library | cycle c-anthropic through every state | ok | 568 |
| 1716 | library | cycle c-google-ml through every state | ok | 569 |
| 1717 | library | cycle c-mit191 through every state | ok | 559 |
| 1718 | library | cycle c-cs50ai through every state | ok | 585 |
| 1719 | library | cycle c-cs50w through every state | ok | 664 |
| 1720 | library | cycle c-google-auto through every state | ok | 626 |
| 1721 | library | cycle c-py4e through every state | ok | 811 |
| 1722 | library | cycle c-mlzoom through every state | ok | 694 |
| 1723 | library | cycle c-dezoom through every state | ok | 554 |
| 1724 | library | cycle c-mit6001 through every state | ok | 632 |
| 1725 | settings | change your name | ok | 6 |
| 1726 | settings | try every track | ok | 129 |
| 1727 | settings | try every experience level | ok | 13 |
| 1728 | settings | tick and untick every goal | ok | 263 |
| 1729 | settings | push every number to both ends | ok | 50 |
| 1730 | settings | turn the update check off and on | ok | 8 |
| 1731 | settings | put every setting back | ok | 20 |
| 1732 | settings | switch the theme to Dark | ok | 579 |
| 1733 | settings | switch the theme to Light | ok | 433 |
| 1734 | settings | switch the theme to Match the system | ok | 7 |
| 1735 | settings | press Open folder | ok | 1 |
| 1736 | settings | export a backup | ok | 5 |
| 1737 | settings | export a progress report | ok | 8 |
| 1738 | settings | take a snapshot | ok | 11 |
| 1739 | settings | cancel an import | ok | 0 |
| 1740 | settings | import the backup back | ok | 0 |
| 1741 | settings | decline a reset | ok | 1 |
| 1742 | settings | accept a reset | ok | 0 |
| 1743 | settings | press Check now | ok | 0 |
| 1744 | search | open search with Ctrl+K | ok | 1 |
| 1745 | search | search for 'nothing' | ok | 0 |
| 1746 | search | search for 'd' | ok | 0 |
| 1747 | search | search for 'Python engineering' | ok | 11 |
| 1748 | search | search for 'Say hello' | ok | 6 |
| 1749 | search | search for 'zzzqqqxx nothing at all' | ok | 2 |
| 1750 | search | press Escape | ok | 11 |
| 1751 | search | press Enter on the first result | ok | 70 |
| 1752 | search | open a result of every kind | ok | 946 |
| 1753 | history | nothing to undo on a fresh store | ok | 0 |
| 1754 | history | tick a line, then undo and redo it | ok | 452 |
| 1755 | history | change a project status, then undo it | ok | 1371 |
| 1756 | history | rate a skill, then undo it | ok | 283 |
| 1757 | history | cycle a certificate, then undo it | ok | 1404 |
| 1758 | history | undo and redo from the keyboard | ok | 1300 |
| 1759 | history | a new change drops the redo branch | ok | 293 |
| 1760 | history | reopen the app and look for the undo | ok | 0 |
| 1761 | history | the tick survived, the undo did not | ok | 0 |
| 1762 | updates | the button is hidden until there is one | ok | 0 |
| 1763 | updates | a release makes the button appear | ok | 1 |
| 1764 | updates | press it for a release with no changelog | ok | 1 |
| 1765 | updates | press it for a release with a changelog | ok | 5 |
| 1766 | updates | a release with nothing for this platform | ok | 2 |
| 1767 | updates | Help > Check for updates | ok | 2 |
| 1768 | restart | reopen the app on the same store | ok | 0 |
| 1769 | restart | the position is remembered | ok | 0 |
| 1770 | restart | quit inside the autosave window | ok | 3008 |
| 1771 | history | Ctrl+Z undoes a tick | ok | 246 |
| 1772 | history | the advertised redo keys | ok | 198 |
| 1773 | history | the Redo button still works | ok | 0 |
| 1774 | today | Today at 800x600 | ok | 0 |
| 1775 | roadmap | Roadmap at 800x600 | ok | 0 |
| 1776 | phase | Phase at 800x600 | ok | 0 |
| 1777 | practice | Practice at 800x600 | ok | 0 |
| 1778 | quiz | Quizzes at 800x600 | ok | 0 |
| 1779 | review | Review at 800x600 | ok | 0 |
| 1780 | projects | Projects at 800x600 | ok | 4 |
| 1781 | journal | Log at 800x600 | ok | 0 |
| 1782 | stats | Progress at 800x600 | ok | 0 |
| 1783 | library | Library at 800x600 | ok | 2 |
| 1784 | settings | Settings at 800x600 | ok | 0 |
| 1785 | today | Today at 1280x900 | ok | 0 |
| 1786 | roadmap | Roadmap at 1280x900 | ok | 0 |
| 1787 | phase | Phase at 1280x900 | ok | 0 |
| 1788 | practice | Practice at 1280x900 | ok | 0 |
| 1789 | quiz | Quizzes at 1280x900 | ok | 0 |
| 1790 | review | Review at 1280x900 | ok | 0 |
| 1791 | projects | Projects at 1280x900 | ok | 4 |
| 1792 | journal | Log at 1280x900 | ok | 0 |
| 1793 | stats | Progress at 1280x900 | ok | 0 |
| 1794 | library | Library at 1280x900 | ok | 2 |
| 1795 | settings | Settings at 1280x900 | ok | 0 |
| 1796 | today | Today at 2560x1440 | ok | 0 |
| 1797 | roadmap | Roadmap at 2560x1440 | ok | 0 |
| 1798 | phase | Phase at 2560x1440 | ok | 0 |
| 1799 | practice | Practice at 2560x1440 | ok | 0 |
| 1800 | quiz | Quizzes at 2560x1440 | ok | 0 |
| 1801 | review | Review at 2560x1440 | ok | 0 |
| 1802 | projects | Projects at 2560x1440 | ok | 4 |
| 1803 | journal | Log at 2560x1440 | ok | 0 |
| 1804 | stats | Progress at 2560x1440 | ok | 0 |
| 1805 | library | Library at 2560x1440 | ok | 2 |
| 1806 | settings | Settings at 2560x1440 | ok | 0 |
| 1807 | layout | the window refuses to go below its minimum | ok | 0 |
| 1808 | layout | the sidebar keeps every page button | ok | 0 |
| 1809 | today | tab through the today page | ok | 46 |
| 1810 | today | the focused control is the one you can see | ok | 0 |
| 1811 | practice | tab through the practice page | ok | 78 |
| 1812 | practice | the focused control is the one you can see | ok | 0 |
| 1813 | phase | tick a line with the space bar | ok | 32 |
| 1814 | practice | Ctrl+Enter in the editor runs the code | ok | 201 |
| 1815 | settings | type 2,5 hours in a German locale | ok | 9 |
| 1816 | settings | type it by hand as 3,5 | ok | 6 |
| 1817 | today | the pace line still reads sensibly | ok | 43 |
| 1818 | library | open library with nothing to show | ok | 12 |
| 1819 | stats | open stats with nothing to show | ok | 54 |
| 1820 | projects | open projects with nothing to show | ok | 14 |
| 1821 | today | open today with nothing to show | ok | 36 |
| 1822 | roadmap | open roadmap with nothing to show | ok | 164 |
| 1823 | navigation | switch pages 200 times | ok | 2098 |
| 1824 | today | reopen the Today page | 1 ms | 1 |
| 1825 | roadmap | reopen the Roadmap page | 14 ms | 14 |
| 1826 | phase | reopen the Phase page | 12 ms | 12 |
| 1827 | practice | reopen the Practice page | 18 ms | 18 |
| 1828 | quiz | reopen the Quizzes page | 8 ms | 8 |
| 1829 | review | reopen the Review page | 6 ms | 6 |
| 1830 | projects | reopen the Projects page | 20 ms | 20 |
| 1831 | journal | reopen the Log page | 8 ms | 8 |
| 1832 | stats | reopen the Progress page | 10 ms | 10 |
| 1833 | library | reopen the Library page | 16 ms | 16 |
| 1834 | settings | reopen the Settings page | 14 ms | 14 |
| 1835 | screenshots | grab every page on both themes | ok | 11386 |
| 1836 | screenshots | practice page after a passing run | results panel hidden: False; rows rendered into it: 4; hint label hidden: True;  | 0 |
| 1837 | help | press F1 and close the shortcut list | ok | 19 |
| 1838 | menu | press Ctrl+, for Settings | ok | 75 |
| 1839 | settings | open the snapshot list and cancel | ok | 26 |
| 1840 | settings | restore the snapshot just taken | ok | 61 |
| 1841 | onboarding | Continue, Continue, Back | ok | 23 |
| 1842 | update | press Update and restart while offline | ok | 7 |
| 1843 | quiz | finish a quiz and go back to its phase | ok | 464 |
| 1844 | quiz | finish a quiz and pick another | ok | 557 |
| 1845 | review | skip to a concept card, reveal, rate | ok | 63 |
| 1846 | practice | press Next | ok | 9 |
| 1847 | phase | open the first resource | ok | 18 |
| 1848 | library | press every button on tab 0 | ok | 400 |
| 1849 | library | press every button on tab 1 | ok | 439 |
| 1850 | library | press every button on tab 2 | ok | 495 |
| 1851 | library | press every button on tab 3 | ok | 205 |
| 1852 | projects | open the repo link | ok | 56 |
| 1853 | projects | press every status button | ok | 260 |
| 1854 | journal | the history opens on the newest sixty | ok | 0 |
| 1855 | journal | press Show older for the next sixty | ok | 258 |
| 1856 | journal | press Show older for the last ten | ok | 60 |
| 1857 | journal | find one entry among a hundred | ok | 140 |
| 1858 | journal | a filter that matches nothing says so | ok | 239 |
| 1859 | journal | narrow the range, then widen it again | ok | 735 |
| 1860 | journal | load an old entry back into the form | ok | 15 |
| 1861 | journal | save the correction | ok | 29 |
| 1862 | journal | take the correction back with Ctrl+Z | ok | 20 |
| 1863 | journal | and put it back with Ctrl+Y | ok | 18 |
| 1864 | journal | start an edit and cancel out of it | ok | 40 |
| 1865 | journal | delete an entry by mistake | ok | 17 |
| 1866 | journal | Ctrl+Z brings the whole entry back | ok | 17 |
| 1867 | journal | Ctrl+Y deletes it again | ok | 14 |
| 1868 | journal | log today for the first time | ok | 22 |
| 1869 | journal | the form warns before the day stacks | ok | 0 |
| 1870 | journal | log today again anyway | ok | 19 |
| 1871 | journal | every note written is listed here | ok | 0 |
| 1872 | journal | the filter searches the notes too | ok | 41 |
| 1873 | journal | open note 0 from the log | ok | 144 |
| 1874 | journal | open note 1 from the log | ok | 159 |
| 1875 | journal | open note 2 from the log | ok | 147 |
| 1876 | journal | open note 3 from the log | ok | 162 |
| 1877 | journal | open note 4 from the log | ok | 1072 |
| 1878 | journal | open note 5 from the log | ok | 37 |
| 1879 | journal | open note 6 from the log | ok | 57 |
| 1880 | journal | the notes section with nothing in it | ok | 0 |
| 1881 | practice | submit an empty editor and read the reasons | ok | 199 |
| 1882 | practice | put the real answer back | ok | 187 |
| 1883 | practice | forget the exclamation mark and run | ok | 200 |
| 1884 | practice | get one character wrong instead | ok | 216 |
| 1885 | practice | get only the capital wrong | ok | 198 |
| 1886 | practice | start an endless run and press Stop | ok | 369 |
| 1887 | practice | read every hint, then press once more | ok | 42 |
| 1888 | practice | search for one exercise by its title | ok | 10 |
| 1889 | practice | search for something that is not there | ok | 10 |
| 1890 | practice | clear the search | ok | 15 |
| 1891 | practice | filter by every difficulty | ok | 91 |
| 1892 | practice | show only the revealed ones | ok | 42 |
| 1893 | practice | walk to the last exercise and press Next again | ok | 44 |
| 1894 | practice | pass the exercise | ok | 227 |
| 1895 | practice | carry on experimenting and break it | ok | 15 |
| 1896 | practice | press Restore my passing version | ok | 8 |
| 1897 | practice | press Reset, then restore once more | ok | 90 |
| 1898 | practice | read the answer | ok | 18 |
| 1899 | practice | check the list says so too | ok | 0 |
| 1900 | practice | press Try this one again from scratch | ok | 15 |
| 1901 | review | press Space to reveal the saved line | ok | 9 |
| 1902 | review | press 3 to rate it Good | ok | 17 |
| 1903 | review | pick a multiple choice option by letter | ok | 1 |
| 1904 | review | press Enter to check it | ok | 11 |
| 1905 | review | press 4 for Easy | ok | 19 |
| 1906 | review | answer with the Again key | ok | 30 |
| 1907 | review | answer with the Hard key | ok | 24 |
| 1908 | review | answer with the Good key | ok | 23 |
| 1909 | review | answer with the Easy key | ok | 23 |
| 1910 | review | type in the search box with a card open | ok | 1 |
| 1911 | review | bury the card in front of you | ok | 31 |
| 1912 | review | the summary offers the buried card back | ok | 49 |
| 1913 | review | answer one card, then take it back | ok | 53 |
| 1914 | review | Ctrl+Z takes the next one back too | ok | 48 |
| 1915 | review | skip the same card twice | ok | 31 |
| 1916 | phase | open a line's menu with the ... button | ok | 24 |
| 1917 | phase | open the same menu with Shift+F10 | ok | 9 |
| 1918 | phase | the Menu key offers to take it out again | ok | 5 |
| 1919 | search | open the box with Ctrl+K | ok | 3 |
| 1920 | search | find a phase note written minutes ago | ok | 219 |
| 1921 | search | find your own project note | ok | 70 |
| 1922 | search | find a project by its repository url | ok | 3 |
| 1923 | search | find a log entry and open the log | ok | 12 |
| 1924 | search | type a query | ok | 35 |
| 1925 | search | walk down and back up the results | ok | 4 |
| 1926 | search | page down and page up the results | ok | 4 |
| 1927 | search | open the selected hit with Enter | ok | 187 |
| 1928 | search | close the results with Escape | ok | 8 |
| 1929 | library | open the field f-web from search | ok | 61 |
| 1930 | library | open the cert c-cs50p from search | ok | 94 |
| 1931 | search | open a question from search | ok | 7 |
| 1932 | search | read the question and close it | ok | 18 |
| 1933 | library | filter the library to nothing | ok | 28 |
| 1934 | library | filter the library to one shelf entry | ok | 117 |
| 1935 | library | mark a row on tab 0 as read | ok | 13 |
| 1936 | library | take the mark on tab 0 back | ok | 5 |
| 1937 | library | mark a row on tab 1 as read | ok | 106 |
| 1938 | library | take the mark on tab 1 back | ok | 12 |
| 1939 | library | mark a row on tab 2 as read | ok | 73 |
| 1940 | library | take the mark on tab 2 back | ok | 6 |
| 1941 | library | undo the last read mark | ok | 155 |
| 1942 | navigation | press Ctrl+0 | ok | 40 |
| 1943 | navigation | press Ctrl+L | ok | 31 |
| 1944 | navigation | open the library from the Go menu | ok | 41 |
| 1945 | first run | read the status bar on a first launch | ok | 0 |
| 1946 | onboarding | type a name and continue | ok | 12 |
| 1947 | onboarding | choose an experience card | ok | 15 |
| 1948 | onboarding | tick two goals | ok | 17 |
| 1949 | onboarding | go back a step and forward again | ok | 15 |
| 1950 | onboarding | set a pace and build the plan | ok | 60 |
| 1951 | onboarding | skip the whole thing | ok | 8 |
| 1952 | settings | press Run setup again | ok | 56 |
| 1953 | quiz | start one and skip a question | ok | 61 |
| 1954 | quiz | move on to the next question | ok | 14 |
| 1955 | quiz | think better of leaving | ok | 0 |
| 1956 | quiz | leave the quiz | ok | 110 |
| 1957 | quiz | close the app in the middle of one | ok | 182 |
| 1958 | quiz | resume where it was left | ok | 34 |
| 1959 | quiz | start it over instead | ok | 167 |
| 1960 | settings | nothing has left this machine yet | ok | 0 |
| 1961 | settings | choose a second copy folder | ok | 11 |
| 1962 | settings | copy everything there now | ok | 23 |
| 1963 | settings | import a backup and read the summary | ok | 75 |
| 1964 | projects | press Open with nothing to open | ok | 1 |
| 1965 | projects | type a repo address | ok | 2 |
| 1966 | projects | replace it with a note to self | ok | 1 |
| 1967 | today | read the note above the list | ok | 69 |
| 1968 | today | push the first item off until tomorrow | ok | 55 |
| 1969 | today | push a second one off from a compact row | ok | 38 |
| 1970 | today | find the way back to what was hidden | ok | 50 |
| 1971 | today | yesterday's 'first thing tomorrow' returns | ok | 64 |
| 1972 | today | push everything off for a quiet evening | ok | 28 |
| 1973 | today | finish the entire curriculum | ok | 284 |
| 1974 | today | read what the finished plan says | ok | 0 |
| 1975 | today | keep reviewing from the hero | ok | 36 |
| 1976 | today | change track from the hero | ok | 99 |
| 1977 | today | export the report from the hero | ok | 38 |
| 1978 | roadmap | the marker is there while work remains | ok | 0 |
| 1979 | roadmap | and is gone once there is nowhere to go | ok | 1 |
| 1980 | stats | click a phase row | ok | 305 |
| 1981 | stats | select a row and press Enter | ok | 151 |
| 1982 | stats | hover the quiz column for the trend | ok | 0 |
| 1983 | phase | the way into the review deck is announced | ok | 0 |
| 1984 | phase | write a long note into the box | ok | 16 |
| 1985 | phase | and it shrinks back for a short one | ok | 11 |
| 1986 | search | type a word that is nowhere | ok | 24 |
| 1987 | search | Escape, then Ctrl+K again | ok | 13 |
| 1988 | search | open a shelf book from Ctrl+K | ok | 107 |
| 1989 | library | filter for a channel on the Shelf tab | ok | 68 |
| 1990 | library | follow the count to the Video tab | ok | 5 |
| 1991 | library | clear the filter | ok | 238 |
| 1992 | projects | SHOW Shipped with nothing shipped | ok | 23 |
| 1993 | projects | press Show every project | ok | 267 |
| 1994 | projects | type in FIND | ok | 294 |
| 1995 | stats | click the Checks heading | ok | 2 |
| 1996 | stats | pick every SORT choice | ok | 6 |
| 1997 | practice | fail a run, then Where this is taught | ok | 333 |
| 1998 | settings | set filters, then change the theme | ok | 4209 |
| 1999 | settings | come back to each page | ok | 6675 |
| 2000 | quiz | read the picker and its counter | ok | 0 |
| 2001 | quiz | open the quizzes outside the track | ok | 14 |
| 2002 | quiz | type into FIND | ok | 143 |
| 2003 | quiz | a search that matches nothing | ok | 130 |
| 2004 | quiz | SHOW each status in turn | ok | 414 |
| 2005 | quiz | start a quiz from the filtered list | ok | 177 |
| 2006 | quiz | press the second choice every time | ok | 759 |
| 2007 | review | pick a wrong option by its letter | ok | 25 |
| 2008 | review | press Where this is taught | ok | 182 |
| 2009 | review | press Next card | ok | 25 |
| 2010 | review | a second wrong answer, left with Space | ok | 46 |
| 2011 | review | reveal a gate check | ok | 13 |
| 2012 | review | rate it Good | ok | 24 |
| 2013 | phase | a phase read to the end | ok | 211 |
| 2014 | roadmap | the roadmap says read, not proven | ok | 168 |
| 2015 | phase | the same phase, proven | ok | 144 |
| 2016 | today | an earlier phase is mixed into today | ok | 107 |
| 2017 | study | start the timer from the top bar | ok | 57 |
| 2018 | study | pause and resume | ok | 9 |
| 2019 | study | pause and resume by shortcut | ok | 125 |
| 2020 | study | Today shows the session so far | ok | 24 |
| 2021 | study | Keep going leaves the timer running | ok | 8 |
| 2022 | study | save the session to the log | ok | 13 |
| 2023 | study | start from the Study menu | ok | 52 |
| 2024 | study | Ctrl+T under a minute saves nothing | ok | 89 |
| 2025 | study | discard a session | ok | 71 |
| 2026 | study | Stop from the top bar | ok | 122 |
| 2027 | phase | open every guide in OS | ok | 242 |
| 2028 | phase | open every guide in 00 | ok | 166 |
| 2029 | phase | open every guide in 01 | ok | 316 |
| 2030 | phase | open every guide in 02 | ok | 196 |
| 2031 | phase | open every guide in 03 | ok | 176 |
| 2032 | phase | open every guide in 04 | ok | 222 |
| 2033 | phase | open every guide in 05 | ok | 208 |
| 2034 | phase | open every guide in 06 | ok | 193 |
| 2035 | phase | open every guide in 07 | ok | 128 |
| 2036 | phase | open every guide in 08 | ok | 202 |
| 2037 | phase | open every guide in 09 | ok | 279 |
| 2038 | phase | open every guide in 10 | ok | 203 |
| 2039 | phase | open every guide in 11 | ok | 274 |
| 2040 | phase | open every guide in 12 | ok | 258 |
| 2041 | phase | open every guide in 13 | ok | 252 |
| 2042 | phase | open every guide in 14 | ok | 406 |
| 2043 | phase | open every guide in 15 | ok | 313 |
| 2044 | phase | open every guide in 16 | ok | 176 |
| 2045 | phase | open every guide in 17 | ok | 302 |
| 2046 | phase | open every guide in S1 | ok | 209 |
| 2047 | phase | open every guide in S2 | ok | 163 |
| 2048 | phase | open every guide in S3 | ok | 167 |
| 2049 | phase | open every guide in S4 | ok | 170 |
| 2050 | phase | open every guide in S5 | ok | 190 |
| 2051 | phase | open every guide in S6 | ok | 155 |
| 2052 | phase | open every guide in S7 | ok | 189 |
| 2053 | phase | open every guide in S8 | ok | 144 |
| 2054 | phase | open every guide in S9 | ok | 207 |
| 2055 | phase | open every guide in S10 | ok | 212 |
| 2056 | phase | open every guide in S11 | ok | 142 |
| 2057 | phase | open every guide in S12 | ok | 157 |
| 2058 | phase | open every guide in S13 | ok | 129 |
| 2059 | phase | open every guide in S14 | ok | 124 |
| 2060 | phase | open every guide in 18 | ok | 250 |
| 2061 | phase | open every guide in 99 | ok | 243 |
| 2062 | phase | Show all guides, then hide them | ok | 670 |
| 2063 | settings | the report buttons open the form | dialog: FeedbackDialog | 32 |
| 2064 | settings | fill in and send a report | ok | 22 |
| 2065 | settings | New profile asks for a name | ok | 0 |
| 2066 | quiz | start a quiz from the picker | ok | 37 |
| 2067 | quiz | leave and start a different one | ok | 197 |
| 2068 | review | press Check for more | ok | 9 |
| 2069 | updates | open the update dialog and decline | ok | 7 |
| 2070 | updates | open the releases page instead | ok | 4 |
| 2071 | menu | File > Quit | ok | 10 |
| 2072 | menu | File > Switch profile | ok | 0 |
| 2073 | menu | File > Export backup... | ok | 139 |
| 2074 | menu | File > Export progress report... | ok | 24 |
| 2075 | menu | File > Take a snapshot | ok | 12 |
| 2076 | menu | File > Restore a snapshot... | ok | 28 |
| 2077 | menu | Go > Today | ok | 81 |
| 2078 | menu | Go > Roadmap | ok | 176 |
| 2079 | menu | Go > Phase | ok | 184 |
| 2080 | menu | Go > Practice | ok | 49 |
| 2081 | menu | Go > Quizzes | ok | 128 |
| 2082 | menu | Go > Review | ok | 23 |
| 2083 | menu | Go > Projects | ok | 1513 |
| 2084 | menu | Go > Log | ok | 37 |
| 2085 | menu | Go > Progress | ok | 176 |
| 2086 | menu | Go > Library | ok | 969 |
| 2087 | menu | Go > Settings | ok | 39 |
| 2088 | menu | Go > Find | ok | 10 |
| 2089 | menu | Edit > Undo | ok | 0 |
| 2090 | menu | Edit > Redo | ok | 0 |
| 2091 | menu | Study > Start or stop studying | ok | 10 |
| 2092 | menu | Study > Pause or resume studying | ok | 6 |
| 2093 | menu | Help > How this app works | ok | 0 |
| 2094 | menu | Help > Keyboard shortcuts | ok | 7 |
| 2095 | menu | Help > Report a problem or request a feature... | ok | 8 |
| 2096 | menu | Help > Check for updates | ok | 2 |
| 2097 | menu | Help > About | ok | 1 |
| 2098 | menu | every navigation shortcut | ok | 778 |
