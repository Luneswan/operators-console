# Walkthrough of Operator's Console

A single learner's pass through every page, every control and every piece of content, driven through the real widgets with QTest and watched by a net of sensors.

- Generated: 2026-09-24 05:39
- Platform: Windows-11-10.0.26200-SP0, Python 3.14.5, Qt offscreen
- Runtime: 14 min 34 s
- Steps recorded: 2047
- Findings: 16
- Unhandled exceptions seen: 0
- Qt warnings and criticals: 1
- Dialogs answered: 32
- URLs intercepted (none opened): 387
- pytest exit status: 0

## Findings

| id | severity | view | what happened | how to reproduce |
| --- | --- | --- | --- | --- |
| W-01 | major | today | step blocks for 5215 ms: press Start on plan row 3 | Open today and press Start on plan row 3; the interface is frozen for 5.2 s. |
| W-02 | major | projects | step blocks for 3196 ms: click the Projects sidebar button (light theme) | Open projects and click the Projects sidebar button (light theme); the interface is frozen for 3.2 s. |
| W-03 | major | projects | step blocks for 3198 ms: click the Projects sidebar button (dark theme) | Open projects and click the Projects sidebar button (dark theme); the interface is frozen for 3.2 s. |
| W-04 | major | projects | step blocks for 3839 ms: click the Projects sidebar button (system theme) | Open projects and click the Projects sidebar button (system theme); the interface is frozen for 3.8 s. |
| W-05 | major | menu | step blocks for 3620 ms: Go > Projects | Open menu and Go > Projects; the interface is frozen for 3.6 s. |
| W-06 | major | projects | step blocks for 3697 ms: press Ctrl+7 for Projects | Open projects and press Ctrl+7 for Projects; the interface is frozen for 3.7 s. |
| W-07 | major | roadmap | step blocks for 3033 ms: open every phase card from the roadmap | Open roadmap and open every phase card from the roadmap; the interface is frozen for 3.0 s. |
| W-08 | major | roadmap | step blocks for 4238 ms: open every phase outside the plan | Open roadmap and open every phase outside the plan; the interface is frozen for 4.2 s. |
| W-09 | major | navigation | step blocks for 10647 ms: switch pages 200 times as fast as the event loop allows | Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 10.6 s. |
| W-10 | major | phase | step blocks for 6853 ms: walk Next through all 35 phases | Open phase and walk Next through all 35 phases; the interface is frozen for 6.9 s. |
| W-11 | major | phase | step blocks for 6741 ms: walk Previous back to the first phase | Open phase and walk Previous back to the first phase; the interface is frozen for 6.7 s. |
| W-12 | major | phase | step blocks for 5721 ms: choose every phase from the picker | Open phase and choose every phase from the picker; the interface is frozen for 5.7 s. |
| W-13 | major | phase | step blocks for 3214 ms: use the jump row and snippet on 00 | Open phase and use the jump row and snippet on 00; the interface is frozen for 3.2 s. |
| W-14 | major | phase | step blocks for 6655 ms: type a note in each phase and leave at once | Open phase and type a note in each phase and leave at once; the interface is frozen for 6.7 s. |
| W-16 | major | settings | changing the theme freezes the window for 1.1 seconds | Visit every page once, then open Settings > Appearance and change the theme. The window stops responding for about 1.1 s each time. |
| W-15 | polish | journal | a second entry for the same day is added, not merged | Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions. |

### W-01 - step blocks for 5215 ms: press Start on plan row 3

- **Severity**: major
- **View**: today
- **Repro**: Open today and press Start on plan row 3; the interface is frozen for 5.2 s.

### W-02 - step blocks for 3196 ms: click the Projects sidebar button (light theme)

- **Severity**: major
- **View**: projects
- **Repro**: Open projects and click the Projects sidebar button (light theme); the interface is frozen for 3.2 s.

### W-03 - step blocks for 3198 ms: click the Projects sidebar button (dark theme)

- **Severity**: major
- **View**: projects
- **Repro**: Open projects and click the Projects sidebar button (dark theme); the interface is frozen for 3.2 s.

### W-04 - step blocks for 3839 ms: click the Projects sidebar button (system theme)

- **Severity**: major
- **View**: projects
- **Repro**: Open projects and click the Projects sidebar button (system theme); the interface is frozen for 3.8 s.

### W-05 - step blocks for 3620 ms: Go > Projects

- **Severity**: major
- **View**: menu
- **Repro**: Open menu and Go > Projects; the interface is frozen for 3.6 s.

### W-06 - step blocks for 3697 ms: press Ctrl+7 for Projects

- **Severity**: major
- **View**: projects
- **Repro**: Open projects and press Ctrl+7 for Projects; the interface is frozen for 3.7 s.

### W-07 - step blocks for 3033 ms: open every phase card from the roadmap

- **Severity**: major
- **View**: roadmap
- **Repro**: Open roadmap and open every phase card from the roadmap; the interface is frozen for 3.0 s.

### W-08 - step blocks for 4238 ms: open every phase outside the plan

- **Severity**: major
- **View**: roadmap
- **Repro**: Open roadmap and open every phase outside the plan; the interface is frozen for 4.2 s.

### W-09 - step blocks for 10647 ms: switch pages 200 times as fast as the event loop allows

- **Severity**: major
- **View**: navigation
- **Repro**: Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 10.6 s.

### W-10 - step blocks for 6853 ms: walk Next through all 35 phases

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Next through all 35 phases; the interface is frozen for 6.9 s.

### W-11 - step blocks for 6741 ms: walk Previous back to the first phase

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Previous back to the first phase; the interface is frozen for 6.7 s.

### W-12 - step blocks for 5721 ms: choose every phase from the picker

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and choose every phase from the picker; the interface is frozen for 5.7 s.

### W-13 - step blocks for 3214 ms: use the jump row and snippet on 00

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and use the jump row and snippet on 00; the interface is frozen for 3.2 s.

### W-14 - step blocks for 6655 ms: type a note in each phase and leave at once

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and type a note in each phase and leave at once; the interface is frozen for 6.7 s.

### W-16 - changing the theme freezes the window for 1.1 seconds

- **Severity**: major
- **View**: settings
- **Repro**: Visit every page once, then open Settings > Appearance and change the theme. The window stops responding for about 1.1 s each time.

```
MainWindow.apply_theme calls app.setStyleSheet() with an 11 KB sheet, which repolishes every widget in the process. With only Today built (184 widgets) the switch costs about 80 ms; with all eleven pages built (316 widgets) it costs 1140 ms. The text-size spin box on the same page goes through the same path on every step.
```

### W-15 - a second entry for the same day is added, not merged

- **Severity**: polish
- **View**: journal
- **Repro**: Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions.

```
2 rows for today, total hours now 12.5
```

## Coverage of the interface

Every `button(...)`, `QPushButton(...)`, `QAction(...)` and `setShortcut(...)` under `src/` is counted. A control counts as hit when the walk activated the widget built by that exact source line.

- Controls declared: **122**
- Activated by the walk: **100** (82%)

| kind | declared | hit | % |
| --- | --- | --- | --- |
| action | 14 | 11 | 79% |
| button | 99 | 81 | 82% |
| shortcut | 9 | 8 | 89% |

<details><summary>Every control, hit or not</summary>

| file | line | kind | label | hit |
| --- | --- | --- | --- | --- |
| operators_console/ui/feedback.py | 73 | button | Copy text | NO |
| operators_console/ui/feedback.py | 77 | button | Cancel | NO |
| operators_console/ui/feedback.py | 80 | button | Open on GitHub | NO |
| operators_console/ui/main_window.py | 148 | button | Close | yes |
| operators_console/ui/main_window.py | 355 | button | Undo | yes |
| operators_console/ui/main_window.py | 361 | button | Redo | yes |
| operators_console/ui/main_window.py | 401 | action | Quit | yes |
| operators_console/ui/main_window.py | 402 | shortcut | StandardKey.Quit | yes |
| operators_console/ui/main_window.py | 423 | action | Undo | yes |
| operators_console/ui/main_window.py | 424 | shortcut | StandardKey.Undo | yes |
| operators_console/ui/main_window.py | 427 | action | Redo | yes |
| operators_console/ui/main_window.py | 428 | shortcut | <_redo_keys()> | yes |
| operators_console/ui/main_window.py | 433 | action | Find | yes |
| operators_console/ui/main_window.py | 434 | shortcut | Ctrl+K | yes |
| operators_console/ui/main_window.py | 439 | action | How this app works | yes |
| operators_console/ui/main_window.py | 442 | action | Keyboard shortcuts | yes |
| operators_console/ui/main_window.py | 443 | shortcut | F1 | yes |
| operators_console/ui/main_window.py | 446 | action | Report a problem or request a feature... | yes |
| operators_console/ui/main_window.py | 449 | action | Check for updates | yes |
| operators_console/ui/main_window.py | 452 | action | About | yes |
| operators_console/ui/main_window.py | 552 | action | New profile... | NO |
| operators_console/ui/main_window.py | 555 | action | Manage profiles... | NO |
| operators_console/ui/main_window.py | 288 | button | <text> | yes |
| operators_console/ui/main_window.py | 395 | action | <text> | yes |
| operators_console/ui/main_window.py | 409 | action | <text> | yes |
| operators_console/ui/main_window.py | 544 | action | <name> | NO |
| operators_console/ui/main_window.py | 398 | shortcut | <QKeySequence()> | NO |
| operators_console/ui/main_window.py | 411 | shortcut | Ctrl+%d | yes |
| operators_console/ui/main_window.py | 415 | shortcut | Ctrl+0 | yes |
| operators_console/ui/main_window.py | 418 | shortcut | Ctrl+, | yes |
| operators_console/ui/onboarding.py | 162 | button | Skip for now | yes |
| operators_console/ui/onboarding.py | 167 | button | Back | yes |
| operators_console/ui/onboarding.py | 171 | button | Continue | yes |
| operators_console/ui/shortcuts.py | 90 | button | Close | yes |
| operators_console/ui/snapshots.py | 72 | button | Open the backups folder | yes |
| operators_console/ui/snapshots.py | 77 | button | Cancel | yes |
| operators_console/ui/snapshots.py | 80 | button | Restore this snapshot | yes |
| operators_console/ui/updater.py | 220 | button | Open the releases page | yes |
| operators_console/ui/updater.py | 224 | button | Not now | yes |
| operators_console/ui/updater.py | 227 | button | Update and restart | yes |
| operators_console/ui/views/dashboard.py | 230 | button | <computed> | yes |
| operators_console/ui/views/dashboard.py | 239 | button | Not today | yes |
| operators_console/ui/views/dashboard.py | 255 | button | Start | yes |
| operators_console/ui/views/dashboard.py | 324 | button | Open this phase | yes |
| operators_console/ui/views/dashboard.py | 376 | button | Export report | yes |
| operators_console/ui/views/dashboard.py | 379 | button | Keep reviewing | yes |
| operators_console/ui/views/dashboard.py | 383 | button | Change track | yes |
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
| operators_console/ui/views/phase.py | 41 | button | Previous | yes |
| operators_console/ui/views/phase.py | 42 | button | Next | yes |
| operators_console/ui/views/phase.py | 241 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 247 | button | Quiz | yes |
| operators_console/ui/views/phase.py | 253 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 324 | button | Copy | yes |
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
| operators_console/ui/views/roadmap.py | 212 | button | Open | yes |
| operators_console/ui/views/roadmap.py | 262 | button | Open | yes |
| operators_console/ui/views/settings.py | 129 | button | Run setup again | yes |
| operators_console/ui/views/settings.py | 148 | button | New profile... | NO |
| operators_console/ui/views/settings.py | 255 | button | Check now | yes |
| operators_console/ui/views/settings.py | 291 | button | Choose folder... | yes |
| operators_console/ui/views/settings.py | 294 | button | Copy now | yes |
| operators_console/ui/views/settings.py | 308 | button | Snapshot now | yes |
| operators_console/ui/views/settings.py | 311 | button | Restore a snapshot... | yes |
| operators_console/ui/views/settings.py | 323 | button | Reset all progress | yes |
| operators_console/ui/views/settings.py | 273 | button | <text> | yes |
| operators_console/ui/views/settings.py | 342 | button | <text> | NO |
| operators_console/ui/views/settings.py | 385 | button | Rename | NO |
| operators_console/ui/views/settings.py | 381 | button | Switch | NO |
| operators_console/ui/views/settings.py | 390 | button | Remove | NO |
| operators_console/ui/widgets/common.py | 467 | button | ... | yes |
| operators_console/ui/widgets/common.py | 648 | button | Open | yes |

</details>

Recorded activations with no matching declaration (Qt's own controls, e.g. dialog buttons): 2

## What the walk could not reach

- **the "N more" resource disclosure** - PhaseView._fill_body draws one LinkRow per resource with no collapse, so no disclosure control exists in this revision of src/operators_console/ui/views/phase.py
- **undo across a restart** - History lives in memory (ui/context.py -> core/history.py) and is not written to the store, so nothing can be undone after a relaunch. That is a design choice, not a defect, but it means the walk cannot test undo across a save and reload.
- **the page you were on when you quit** - MainWindow always opens on Today (go('today') in __init__) and nothing writes the current page to the store, so 'position survives a relaunch' means progress, not the page. Recorded rather than asserted.
- **the real folder chooser** - QFileDialog.getExistingDirectory is a static that builds and execs its dialog in C++, so the walk's dialog answerer - which patches QDialog.exec in Python - cannot reach it. It is stubbed here the way getSaveFileName is stubbed in the harness.
- **the 'Update and restart' button** - Pressing it downloads a release package over the network and relaunches the program. The walk drives the dialog up to that button and stops; the download path itself is covered by tests/test_updates.py and tests/test_updates_security.py.
- **operators_console/ui/feedback.py:73 (button Copy text)** - never activated by the walk
- **operators_console/ui/feedback.py:77 (button Cancel)** - never activated by the walk
- **operators_console/ui/feedback.py:80 (button Open on GitHub)** - never activated by the walk
- **operators_console/ui/main_window.py:552 (action New profile...)** - never activated by the walk
- **operators_console/ui/main_window.py:555 (action Manage profiles...)** - never activated by the walk
- **operators_console/ui/main_window.py:544 (action <name>)** - never activated by the walk
- **operators_console/ui/main_window.py:398 (shortcut <QKeySequence()>)** - never activated by the walk
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
- **operators_console/ui/views/settings.py:148 (button New profile...)** - never activated by the walk
- **operators_console/ui/views/settings.py:342 (button <text>)** - never activated by the walk
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
| controls declared in the source | 122 |
| controls reached by Tab on practice | 23 |
| controls reached by Tab on today | 21 |
| controls the walk activated | 100 |
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
| milliseconds for 200 page switches | 4674 |
| milliseconds for a typical project status press | 46 |
| milliseconds to open review with 1000 cards | 82 |
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
| study steps ticked and unticked | 633 |
| themes exercised | 3 |
| tracks chosen in settings | 16 |
| undoable change kinds covered | 4 |
| update dialogs opened | 1 |
| ways back into the setup wizard | 1 |
| ways out of a quiz | 2 |
| where-taught presses | 1 |
| worst theme switch in milliseconds | 1140 |
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
- ... and 171 more

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
| notice | About Python Operator's Console | Python Operator's Console 1.1.3  35 phases, 161 graded exercises, 354 review questions, 36 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2942\test_the_help_ |
| messagebox | Show the solution? | You have not passed this one.  If you read the answer, it is marked as read, not solved. Try another hint first? |
| open file | Import a backup | C:\Users\anasa |
| question | Replace everything? | Importing replaces all current progress.  A backup of the current state is saved first. Continue? |
| question | Reset all progress? | This clears all checkboxes, exercises, reviews, projects and log entries.  A snapshot is taken first. Use Restore a snapshot in Settings to undo. Settings are kept. |
| dialog | UpdateDialog | Update available |
| dialog | QuestionDialog | Question |
| dialog | Onboarding | Set up your plan |
| question | Leave this quiz? | Answered questions are already scored.  The rest of this attempt is discarded, and the quiz starts over next time. Leave? |
| notice | About Python Operator's Console | Python Operator's Console 1.1.3  35 phases, 161 graded exercises, 354 review questions, 36 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2942\test_the_remai |

## Every step

| # | view | action | result | ms |
| --- | --- | --- | --- | --- |
| 1 | onboarding | open the wizard on first run | ok | 217 |
| 2 | onboarding | continue from step 1 | ok | 45 |
| 3 | onboarding | continue from step 2 | ok | 3 |
| 4 | onboarding | continue from step 3 | ok | 0 |
| 5 | onboarding | back from step 4 | ok | 3 |
| 6 | onboarding | back from step 3 | ok | 0 |
| 7 | onboarding | back from step 2 | ok | 0 |
| 8 | onboarding | experience: Never written code before | ok | 147 |
| 9 | onboarding | experience: Some Python, but it does not stick | ok | 142 |
| 10 | onboarding | experience: Confident in another language | ok | 178 |
| 11 | onboarding | experience: I write Python at work already | ok | 134 |
| 12 | onboarding | tick 745 goal combinations | ok | 2667 |
| 13 | onboarding | finish with goal: Websites and APIs | ok | 223 |
| 14 | onboarding | finish with goal: Data analysis and engineering | ok | 125 |
| 15 | onboarding | finish with goal: Machine learning and AI | ok | 71 |
| 16 | onboarding | finish with goal: Computer vision | ok | 103 |
| 17 | onboarding | finish with goal: Language and text (NLP) | ok | 100 |
| 18 | onboarding | finish with goal: Automation and scraping | ok | 412 |
| 19 | onboarding | finish with goal: Bots and integrations | ok | 192 |
| 20 | onboarding | finish with goal: Desktop and mobile apps | ok | 366 |
| 21 | onboarding | finish with goal: Command-line tools | ok | 457 |
| 22 | onboarding | finish with goal: Games, graphics and media | ok | 232 |
| 23 | onboarding | finish with goal: Science and optimization | ok | 216 |
| 24 | onboarding | finish with goal: Finance and trading | ok | 122 |
| 25 | onboarding | finish with goal: Infrastructure and deployment | ok | 106 |
| 26 | onboarding | finish with goal: Network automation | ok | 89 |
| 27 | onboarding | finish with goal: Security | ok | 99 |
| 28 | onboarding | finish with goal: Testing and QA | ok | 114 |
| 29 | onboarding | finish with goal: Hardware, IoT and robotics | ok | 148 |
| 30 | onboarding | finish with goal: Blockchain | ok | 228 |
| 31 | onboarding | finish with goal: Pass a technical interview | ok | 193 |
| 32 | onboarding | finish with goal: How computers work | ok | 165 |
| 33 | onboarding | finish with goal: Compilers and language tools | ok | 205 |
| 34 | onboarding | pace 0.5 h x 1 days | ok | 117 |
| 35 | onboarding | pace 16.0 h x 7 days | ok | 356 |
| 36 | onboarding | skip the wizard | ok | 9 |
| 37 | today | land on Today after skipping | ok | 133 |
| 38 | today | read the four headline tiles | ok | 0 |
| 39 | today | press Start on plan row 1 | ok | 523 |
| 40 | today | press Start on plan row 2 | ok | 526 |
| 41 | today | press Start on plan row 3 | slow (5215 ms) | 5215 |
| 42 | today | press Start on plan row 4 | ok | 571 |
| 43 | today | press Start on plan row 5 | ok | 161 |
| 44 | today | open the current phase from Where you are | ok | 237 |
| 45 | settings | switch the theme to light | ok | 12 |
| 46 | today | click the Today sidebar button (light theme) | ok | 137 |
| 47 | roadmap | click the Roadmap sidebar button (light theme) | ok | 461 |
| 48 | phase | click the Phase sidebar button (light theme) | ok | 283 |
| 49 | practice | click the Practice sidebar button (light theme) | ok | 238 |
| 50 | quiz | click the Quizzes sidebar button (light theme) | ok | 367 |
| 51 | review | click the Review sidebar button (light theme) | ok | 72 |
| 52 | projects | click the Projects sidebar button (light theme) | slow (3196 ms) | 3196 |
| 53 | journal | click the Log sidebar button (light theme) | ok | 117 |
| 54 | stats | click the Progress sidebar button (light theme) | ok | 320 |
| 55 | library | click the Library sidebar button (light theme) | ok | 2547 |
| 56 | settings | click the Settings sidebar button (light theme) | ok | 417 |
| 57 | settings | switch the theme to dark | ok | 942 |
| 58 | today | click the Today sidebar button (dark theme) | ok | 298 |
| 59 | roadmap | click the Roadmap sidebar button (dark theme) | ok | 428 |
| 60 | phase | click the Phase sidebar button (dark theme) | ok | 536 |
| 61 | practice | click the Practice sidebar button (dark theme) | ok | 260 |
| 62 | quiz | click the Quizzes sidebar button (dark theme) | ok | 605 |
| 63 | review | click the Review sidebar button (dark theme) | ok | 49 |
| 64 | projects | click the Projects sidebar button (dark theme) | slow (3198 ms) | 3198 |
| 65 | journal | click the Log sidebar button (dark theme) | ok | 98 |
| 66 | stats | click the Progress sidebar button (dark theme) | ok | 278 |
| 67 | library | click the Library sidebar button (dark theme) | ok | 2595 |
| 68 | settings | click the Settings sidebar button (dark theme) | ok | 164 |
| 69 | settings | switch the theme to system | ok | 1140 |
| 70 | today | click the Today sidebar button (system theme) | ok | 271 |
| 71 | roadmap | click the Roadmap sidebar button (system theme) | ok | 582 |
| 72 | phase | click the Phase sidebar button (system theme) | ok | 301 |
| 73 | practice | click the Practice sidebar button (system theme) | ok | 229 |
| 74 | quiz | click the Quizzes sidebar button (system theme) | ok | 468 |
| 75 | review | click the Review sidebar button (system theme) | ok | 29 |
| 76 | projects | click the Projects sidebar button (system theme) | slow (3839 ms) | 3839 |
| 77 | journal | click the Log sidebar button (system theme) | ok | 116 |
| 78 | stats | click the Progress sidebar button (system theme) | ok | 330 |
| 79 | library | click the Library sidebar button (system theme) | ok | 2682 |
| 80 | settings | click the Settings sidebar button (system theme) | ok | 205 |
| 81 | today | check no control escapes the Today page | ok | 5 |
| 82 | roadmap | check no control escapes the Roadmap page | ok | 0 |
| 83 | phase | check no control escapes the Phase page | ok | 1 |
| 84 | practice | check no control escapes the Practice page | ok | 1 |
| 85 | quiz | check no control escapes the Quizzes page | ok | 0 |
| 86 | review | check no control escapes the Review page | ok | 0 |
| 87 | projects | check no control escapes the Projects page | ok | 10 |
| 88 | journal | check no control escapes the Log page | ok | 0 |
| 89 | stats | check no control escapes the Progress page | ok | 0 |
| 90 | library | check no control escapes the Library page | ok | 3 |
| 91 | settings | check no control escapes the Settings page | ok | 0 |
| 92 | menu | Go > Today | ok | 90 |
| 93 | menu | Go > Roadmap | ok | 380 |
| 94 | menu | Go > Phase | ok | 315 |
| 95 | menu | Go > Practice | ok | 309 |
| 96 | menu | Go > Quizzes | ok | 362 |
| 97 | menu | Go > Review | ok | 57 |
| 98 | menu | Go > Projects | slow (3620 ms) | 3620 |
| 99 | menu | Go > Log | ok | 110 |
| 100 | menu | Go > Progress | ok | 258 |
| 101 | menu | Go > Library | ok | 2590 |
| 102 | menu | Go > Settings | ok | 259 |
| 103 | menu | Go > Find | ok | 20 |
| 104 | today | press Ctrl+1 for Today | ok | 101 |
| 105 | roadmap | press Ctrl+2 for Roadmap | ok | 489 |
| 106 | phase | press Ctrl+3 for Phase | ok | 389 |
| 107 | practice | press Ctrl+4 for Practice | ok | 227 |
| 108 | quiz | press Ctrl+5 for Quizzes | ok | 553 |
| 109 | review | press Ctrl+6 for Review | ok | 86 |
| 110 | projects | press Ctrl+7 for Projects | slow (3697 ms) | 3697 |
| 111 | journal | press Ctrl+8 for Log | ok | 111 |
| 112 | stats | press Ctrl+9 for Progress | ok | 447 |
| 113 | menu | &File > Switch profile | ok | 1 |
| 114 | menu | &File > Export backup... | ok | 226 |
| 115 | menu | &File > Export progress report... | ok | 55 |
| 116 | menu | &File > Take a snapshot | ok | 22 |
| 117 | menu | &File > Restore a snapshot... | ok | 240 |
| 118 | menu | &Help > How this app works | ok | 0 |
| 119 | menu | &Help > Keyboard shortcuts | ok | 45 |
| 120 | menu | &Help > Report a problem or request a feature... | ok | 159 |
| 121 | menu | &Help > Check for updates | ok | 1 |
| 122 | menu | &Help > About | ok | 3 |
| 123 | roadmap | switch to the Well-rounded software engineer track | ok | 554 |
| 124 | roadmap | switch to the Learn Python properly (no career pressure) track | ok | 533 |
| 125 | roadmap | switch to the Backend & API engineer track | ok | 354 |
| 126 | roadmap | switch to the Data analysis & data engineering track | ok | 324 |
| 127 | roadmap | switch to the AI & machine learning engineer track | ok | 450 |
| 128 | roadmap | switch to the Automation, scripting & scraping track | ok | 305 |
| 129 | roadmap | switch to the DevOps & platform engineering track | ok | 515 |
| 130 | roadmap | switch to the Application security track | ok | 581 |
| 131 | roadmap | switch to the Job-ready, fastest route track | ok | 437 |
| 132 | roadmap | switch to the Desktop apps & developer tools track | ok | 531 |
| 133 | roadmap | switch to the Games & graphics track | ok | 440 |
| 134 | roadmap | switch to the Scientific computing & research track | ok | 426 |
| 135 | roadmap | switch to the Quantitative finance track | ok | 399 |
| 136 | roadmap | switch to the Test automation & quality engineering track | ok | 323 |
| 137 | roadmap | switch to the Network automation track | ok | 300 |
| 138 | roadmap | switch to the Embedded & IoT track | ok | 452 |
| 139 | roadmap | open every phase card from the roadmap | slow (3033 ms) | 3033 |
| 140 | roadmap | open every phase outside the plan | slow (4238 ms) | 4238 |
| 141 | navigation | switch pages 200 times as fast as the event loop allows | slow (10647 ms) | 10647 |
| 142 | phase | walk Next through all 35 phases | slow (6853 ms) | 6853 |
| 143 | phase | walk Previous back to the first phase | slow (6741 ms) | 6741 |
| 144 | phase | choose every phase from the picker | slow (5721 ms) | 5721 |
| 145 | phase | open phase OS Operating rules | ok | 261 |
| 146 | phase | open phase 00 Environment & Git | ok | 217 |
| 147 | phase | open phase 01 Python foundations | ok | 253 |
| 148 | phase | open phase 02 Python engineering | ok | 219 |
| 149 | phase | open phase 03 Packaging & tooling | ok | 180 |
| 150 | phase | open phase 04 Computer science core | ok | 232 |
| 151 | phase | open phase 05 Algorithms & problem solving | ok | 191 |
| 152 | phase | open phase 06 Linux & systems | ok | 195 |
| 153 | phase | open phase 07 Networking | ok | 146 |
| 154 | phase | open phase 08 SQL & PostgreSQL | ok | 223 |
| 155 | phase | open phase 09 Backend engineering | ok | 214 |
| 156 | phase | open phase 10 Automation & web | ok | 223 |
| 157 | phase | open phase 11 Async, concurrency & performance | ok | 186 |
| 158 | phase | open phase 12 Docker, CI/CD & deployment | ok | 185 |
| 159 | phase | open phase 13 Application security | ok | 170 |
| 160 | phase | open phase 14 AI engineering | ok | 256 |
| 161 | phase | open phase 15 Architecture & orchestration | ok | 219 |
| 162 | phase | open phase 16 Systems programming & internals | ok | 183 |
| 163 | phase | open phase 17 Data engineering | ok | 219 |
| 164 | phase | open phase S1 Data analysis & visualization | ok | 192 |
| 165 | phase | open phase S2 Desktop & mobile apps | ok | 159 |
| 166 | phase | open phase S3 Command-line tools | ok | 187 |
| 167 | phase | open phase S4 Games, graphics & media | ok | 159 |
| 168 | phase | open phase S5 Scientific computing & optimization | ok | 220 |
| 169 | phase | open phase S6 Quantitative finance | ok | 143 |
| 170 | phase | open phase S7 Computer vision | ok | 186 |
| 171 | phase | open phase S8 Natural language processing | ok | 167 |
| 172 | phase | open phase S9 Testing & quality engineering | ok | 300 |
| 173 | phase | open phase S10 Network automation | ok | 601 |
| 174 | phase | open phase S11 Embedded, IoT & hardware | ok | 336 |
| 175 | phase | open phase S12 Security engineering | ok | 186 |
| 176 | phase | open phase S13 Bots & integrations | ok | 183 |
| 177 | phase | open phase S14 Blockchain tooling | ok | 151 |
| 178 | phase | open phase 18 Beyond senior | ok | 249 |
| 179 | phase | open phase 99 Final-boss ladder | ok | 204 |
| 180 | phase | tick every study step in OS | ok | 415 |
| 181 | phase | untick every study step in OS | ok | 337 |
| 182 | phase | tick every study step in 00 | ok | 299 |
| 183 | phase | untick every study step in 00 | ok | 251 |
| 184 | phase | tick every study step in 01 | ok | 603 |
| 185 | phase | untick every study step in 01 | ok | 499 |
| 186 | phase | tick every study step in 02 | ok | 286 |
| 187 | phase | untick every study step in 02 | ok | 219 |
| 188 | phase | tick every study step in 03 | ok | 214 |
| 189 | phase | untick every study step in 03 | ok | 186 |
| 190 | phase | tick every study step in 04 | ok | 335 |
| 191 | phase | untick every study step in 04 | ok | 269 |
| 192 | phase | tick every study step in 05 | ok | 326 |
| 193 | phase | untick every study step in 05 | ok | 276 |
| 194 | phase | tick every study step in 06 | ok | 254 |
| 195 | phase | untick every study step in 06 | ok | 195 |
| 196 | phase | tick every study step in 07 | ok | 215 |
| 197 | phase | untick every study step in 07 | ok | 179 |
| 198 | phase | tick every study step in 08 | ok | 270 |
| 199 | phase | untick every study step in 08 | ok | 217 |
| 200 | phase | tick every study step in 09 | ok | 322 |
| 201 | phase | untick every study step in 09 | ok | 499 |
| 202 | phase | tick every study step in 10 | ok | 270 |
| 203 | phase | untick every study step in 10 | ok | 231 |
| 204 | phase | tick every study step in 11 | ok | 323 |
| 205 | phase | untick every study step in 11 | ok | 376 |
| 206 | phase | tick every study step in 12 | ok | 300 |
| 207 | phase | untick every study step in 12 | ok | 216 |
| 208 | phase | tick every study step in 13 | ok | 304 |
| 209 | phase | untick every study step in 13 | ok | 262 |
| 210 | phase | tick every study step in 14 | ok | 395 |
| 211 | phase | untick every study step in 14 | ok | 403 |
| 212 | phase | tick every study step in 15 | ok | 364 |
| 213 | phase | untick every study step in 15 | ok | 325 |
| 214 | phase | tick every study step in 16 | ok | 239 |
| 215 | phase | untick every study step in 16 | ok | 216 |
| 216 | phase | tick every study step in 17 | ok | 306 |
| 217 | phase | untick every study step in 17 | ok | 264 |
| 218 | phase | tick every study step in S1 | ok | 231 |
| 219 | phase | untick every study step in S1 | ok | 182 |
| 220 | phase | tick every study step in S2 | ok | 246 |
| 221 | phase | untick every study step in S2 | ok | 187 |
| 222 | phase | tick every study step in S3 | ok | 223 |
| 223 | phase | untick every study step in S3 | ok | 241 |
| 224 | phase | tick every study step in S4 | ok | 226 |
| 225 | phase | untick every study step in S4 | ok | 198 |
| 226 | phase | tick every study step in S5 | ok | 232 |
| 227 | phase | untick every study step in S5 | ok | 194 |
| 228 | phase | tick every study step in S6 | ok | 234 |
| 229 | phase | untick every study step in S6 | ok | 218 |
| 230 | phase | tick every study step in S7 | ok | 229 |
| 231 | phase | untick every study step in S7 | ok | 204 |
| 232 | phase | tick every study step in S8 | ok | 213 |
| 233 | phase | untick every study step in S8 | ok | 169 |
| 234 | phase | tick every study step in S9 | ok | 222 |
| 235 | phase | untick every study step in S9 | ok | 197 |
| 236 | phase | tick every study step in S10 | ok | 208 |
| 237 | phase | untick every study step in S10 | ok | 221 |
| 238 | phase | tick every study step in S11 | ok | 213 |
| 239 | phase | untick every study step in S11 | ok | 172 |
| 240 | phase | tick every study step in S12 | ok | 266 |
| 241 | phase | untick every study step in S12 | ok | 215 |
| 242 | phase | tick every study step in S13 | ok | 251 |
| 243 | phase | untick every study step in S13 | ok | 180 |
| 244 | phase | tick every study step in S14 | ok | 192 |
| 245 | phase | untick every study step in S14 | ok | 173 |
| 246 | phase | tick every study step in 18 | ok | 363 |
| 247 | phase | untick every study step in 18 | ok | 307 |
| 248 | phase | tick every study step in 99 | ok | 325 |
| 249 | phase | untick every study step in 99 | ok | 286 |
| 250 | phase | clear the gate on 00 | ok | 106 |
| 251 | phase | reopen the gate on 00 | ok | 91 |
| 252 | phase | clear the gate on 01 | ok | 109 |
| 253 | phase | reopen the gate on 01 | ok | 83 |
| 254 | phase | clear the gate on 02 | ok | 88 |
| 255 | phase | reopen the gate on 02 | ok | 78 |
| 256 | phase | clear the gate on 03 | ok | 94 |
| 257 | phase | reopen the gate on 03 | ok | 76 |
| 258 | phase | clear the gate on 04 | ok | 95 |
| 259 | phase | reopen the gate on 04 | ok | 71 |
| 260 | phase | clear the gate on 05 | ok | 91 |
| 261 | phase | reopen the gate on 05 | ok | 81 |
| 262 | phase | clear the gate on 06 | ok | 97 |
| 263 | phase | reopen the gate on 06 | ok | 79 |
| 264 | phase | clear the gate on 07 | ok | 94 |
| 265 | phase | reopen the gate on 07 | ok | 79 |
| 266 | phase | clear the gate on 08 | ok | 105 |
| 267 | phase | reopen the gate on 08 | ok | 108 |
| 268 | phase | clear the gate on 09 | ok | 132 |
| 269 | phase | reopen the gate on 09 | ok | 103 |
| 270 | phase | clear the gate on 10 | ok | 109 |
| 271 | phase | reopen the gate on 10 | ok | 92 |
| 272 | phase | clear the gate on 11 | ok | 100 |
| 273 | phase | reopen the gate on 11 | ok | 85 |
| 274 | phase | clear the gate on 12 | ok | 112 |
| 275 | phase | reopen the gate on 12 | ok | 83 |
| 276 | phase | clear the gate on 13 | ok | 100 |
| 277 | phase | reopen the gate on 13 | ok | 89 |
| 278 | phase | clear the gate on 14 | ok | 137 |
| 279 | phase | reopen the gate on 14 | ok | 90 |
| 280 | phase | clear the gate on 15 | ok | 97 |
| 281 | phase | reopen the gate on 15 | ok | 98 |
| 282 | phase | clear the gate on 16 | ok | 90 |
| 283 | phase | reopen the gate on 16 | ok | 58 |
| 284 | phase | clear the gate on 17 | ok | 112 |
| 285 | phase | reopen the gate on 17 | ok | 121 |
| 286 | phase | clear the gate on S1 | ok | 81 |
| 287 | phase | reopen the gate on S1 | ok | 71 |
| 288 | phase | clear the gate on S2 | ok | 81 |
| 289 | phase | reopen the gate on S2 | ok | 72 |
| 290 | phase | clear the gate on S3 | ok | 84 |
| 291 | phase | reopen the gate on S3 | ok | 67 |
| 292 | phase | clear the gate on S4 | ok | 77 |
| 293 | phase | reopen the gate on S4 | ok | 63 |
| 294 | phase | clear the gate on S5 | ok | 85 |
| 295 | phase | reopen the gate on S5 | ok | 62 |
| 296 | phase | clear the gate on S6 | ok | 90 |
| 297 | phase | reopen the gate on S6 | ok | 67 |
| 298 | phase | clear the gate on S7 | ok | 81 |
| 299 | phase | reopen the gate on S7 | ok | 71 |
| 300 | phase | clear the gate on S8 | ok | 83 |
| 301 | phase | reopen the gate on S8 | ok | 68 |
| 302 | phase | clear the gate on S9 | ok | 81 |
| 303 | phase | reopen the gate on S9 | ok | 68 |
| 304 | phase | clear the gate on S10 | ok | 84 |
| 305 | phase | reopen the gate on S10 | ok | 54 |
| 306 | phase | clear the gate on S11 | ok | 84 |
| 307 | phase | reopen the gate on S11 | ok | 55 |
| 308 | phase | clear the gate on S12 | ok | 96 |
| 309 | phase | reopen the gate on S12 | ok | 76 |
| 310 | phase | clear the gate on S13 | ok | 102 |
| 311 | phase | reopen the gate on S13 | ok | 70 |
| 312 | phase | clear the gate on S14 | ok | 79 |
| 313 | phase | reopen the gate on S14 | ok | 63 |
| 314 | phase | clear the gate on 18 | ok | 97 |
| 315 | phase | reopen the gate on 18 | ok | 86 |
| 316 | phase | clear the gate on 99 | ok | 91 |
| 317 | phase | reopen the gate on 99 | ok | 58 |
| 318 | phase | open every resource in 00 | ok | 29 |
| 319 | phase | open every resource in 01 | ok | 39 |
| 320 | phase | open every resource in 02 | ok | 30 |
| 321 | phase | open every resource in 03 | ok | 26 |
| 322 | phase | open every resource in 04 | ok | 33 |
| 323 | phase | open every resource in 05 | ok | 25 |
| 324 | phase | open every resource in 06 | ok | 29 |
| 325 | phase | open every resource in 07 | ok | 56 |
| 326 | phase | open every resource in 08 | ok | 39 |
| 327 | phase | open every resource in 09 | ok | 36 |
| 328 | phase | open every resource in 10 | ok | 29 |
| 329 | phase | open every resource in 11 | ok | 38 |
| 330 | phase | open every resource in 12 | ok | 27 |
| 331 | phase | open every resource in 13 | ok | 36 |
| 332 | phase | open every resource in 14 | ok | 37 |
| 333 | phase | open every resource in 15 | ok | 39 |
| 334 | phase | open every resource in 16 | ok | 28 |
| 335 | phase | open every resource in 17 | ok | 34 |
| 336 | phase | open every resource in S1 | ok | 29 |
| 337 | phase | open every resource in S2 | ok | 26 |
| 338 | phase | open every resource in S3 | ok | 21 |
| 339 | phase | open every resource in S4 | ok | 26 |
| 340 | phase | open every resource in S5 | ok | 33 |
| 341 | phase | open every resource in S6 | ok | 31 |
| 342 | phase | open every resource in S7 | ok | 46 |
| 343 | phase | open every resource in S8 | ok | 39 |
| 344 | phase | open every resource in S9 | ok | 28 |
| 345 | phase | open every resource in S10 | ok | 26 |
| 346 | phase | open every resource in S11 | ok | 27 |
| 347 | phase | open every resource in S12 | ok | 75 |
| 348 | phase | open every resource in S13 | ok | 28 |
| 349 | phase | open every resource in S14 | ok | 27 |
| 350 | phase | open every resource in 18 | ok | 28 |
| 351 | phase | open every resource in 99 | ok | 31 |
| 352 | phase | use the jump row and snippet on OS | ok | 0 |
| 353 | phase | use the jump row and snippet on 00 | slow (3214 ms) | 3214 |
| 354 | phase | use the jump row and snippet on 01 | ok | 752 |
| 355 | phase | use the jump row and snippet on 02 | ok | 1082 |
| 356 | phase | use the jump row and snippet on 03 | ok | 644 |
| 357 | phase | use the jump row and snippet on 04 | ok | 654 |
| 358 | phase | use the jump row and snippet on 05 | ok | 687 |
| 359 | phase | use the jump row and snippet on 06 | ok | 586 |
| 360 | phase | use the jump row and snippet on 07 | ok | 567 |
| 361 | phase | use the jump row and snippet on 08 | ok | 659 |
| 362 | phase | use the jump row and snippet on 09 | ok | 696 |
| 363 | phase | use the jump row and snippet on 10 | ok | 678 |
| 364 | phase | use the jump row and snippet on 11 | ok | 712 |
| 365 | phase | use the jump row and snippet on 12 | ok | 611 |
| 366 | phase | use the jump row and snippet on 13 | ok | 676 |
| 367 | phase | use the jump row and snippet on 14 | ok | 1051 |
| 368 | phase | use the jump row and snippet on 15 | ok | 764 |
| 369 | phase | use the jump row and snippet on 16 | ok | 590 |
| 370 | phase | use the jump row and snippet on 17 | ok | 795 |
| 371 | phase | use the jump row and snippet on S1 | ok | 1241 |
| 372 | phase | use the jump row and snippet on S2 | ok | 728 |
| 373 | phase | use the jump row and snippet on S3 | ok | 603 |
| 374 | phase | use the jump row and snippet on S4 | ok | 606 |
| 375 | phase | use the jump row and snippet on S5 | ok | 764 |
| 376 | phase | use the jump row and snippet on S6 | ok | 738 |
| 377 | phase | use the jump row and snippet on S7 | ok | 571 |
| 378 | phase | use the jump row and snippet on S8 | ok | 573 |
| 379 | phase | use the jump row and snippet on S9 | ok | 587 |
| 380 | phase | use the jump row and snippet on S10 | ok | 570 |
| 381 | phase | use the jump row and snippet on S11 | ok | 661 |
| 382 | phase | use the jump row and snippet on S12 | ok | 714 |
| 383 | phase | use the jump row and snippet on S13 | ok | 635 |
| 384 | phase | use the jump row and snippet on S14 | ok | 620 |
| 385 | phase | use the jump row and snippet on 18 | ok | 359 |
| 386 | phase | use the jump row and snippet on 99 | ok | 398 |
| 387 | phase | send a line to the review deck from the right click menu | ok | 302 |
| 388 | phase | type a note in each phase and leave at once | slow (6655 ms) | 6655 |
| 389 | phase | the pending note is committed on quit | ok | 345 |
| 390 | practice | filter the list by every phase | ok | 823 |
| 391 | practice | switch the status filter three ways | ok | 72 |
| 392 | practice | walk the list with Next exercise | ok | 104 |
| 393 | practice | run an endless loop and wait it out | ok | 3419 |
| 394 | practice | ask for the solution before passing | ok | 10 |
| 395 | practice | insist on the solution | ok | 35 |
| 396 | practice | type, then press Reset | ok | 14 |
| 397 | practice | p01.001: read the brief | ok | 0 |
| 398 | practice | p01.001: reveal every hint | ok | 84 |
| 399 | practice | p01.001: run an empty editor | ok | 255 |
| 400 | practice | p01.001: run the untouched starter | ok | 332 |
| 401 | practice | p01.001: run the reference solution | ok | 274 |
| 402 | practice | p01.001: read the solution once passed | ok | 49 |
| 403 | practice | p01.002: read the brief | ok | 0 |
| 404 | practice | p01.002: reveal every hint | ok | 69 |
| 405 | practice | p01.002: run an empty editor | ok | 319 |
| 406 | practice | p01.002: run the untouched starter | ok | 313 |
| 407 | practice | p01.002: run the reference solution | ok | 285 |
| 408 | practice | p01.002: read the solution once passed | ok | 45 |
| 409 | practice | p01.003: read the brief | ok | 0 |
| 410 | practice | p01.003: reveal every hint | ok | 72 |
| 411 | practice | p01.003: run an empty editor | ok | 269 |
| 412 | practice | p01.003: run the untouched starter | ok | 262 |
| 413 | practice | p01.003: run the reference solution | ok | 282 |
| 414 | practice | p01.003: read the solution once passed | ok | 47 |
| 415 | practice | p01.004: read the brief | ok | 0 |
| 416 | practice | p01.004: reveal every hint | ok | 67 |
| 417 | practice | p01.004: run an empty editor | ok | 246 |
| 418 | practice | p01.004: run the untouched starter | ok | 272 |
| 419 | practice | p01.004: run the reference solution | ok | 330 |
| 420 | practice | p01.004: read the solution once passed | ok | 46 |
| 421 | practice | p01.005: read the brief | ok | 0 |
| 422 | practice | p01.005: reveal every hint | ok | 67 |
| 423 | practice | p01.005: run an empty editor | ok | 337 |
| 424 | practice | p01.005: run the untouched starter | ok | 350 |
| 425 | practice | p01.005: run the reference solution | ok | 302 |
| 426 | practice | p01.005: read the solution once passed | ok | 49 |
| 427 | practice | p01.006: read the brief | ok | 0 |
| 428 | practice | p01.006: reveal every hint | ok | 75 |
| 429 | practice | p01.006: run an empty editor | ok | 278 |
| 430 | practice | p01.006: run the untouched starter | ok | 340 |
| 431 | practice | p01.006: run the reference solution | ok | 340 |
| 432 | practice | p01.006: read the solution once passed | ok | 46 |
| 433 | practice | p01.007: read the brief | ok | 0 |
| 434 | practice | p01.007: reveal every hint | ok | 39 |
| 435 | practice | p01.007: run an empty editor | ok | 275 |
| 436 | practice | p01.007: run the untouched starter | ok | 356 |
| 437 | practice | p01.007: run the reference solution | ok | 253 |
| 438 | practice | p01.007: read the solution once passed | ok | 46 |
| 439 | practice | p01.008: read the brief | ok | 0 |
| 440 | practice | p01.008: reveal every hint | ok | 68 |
| 441 | practice | p01.008: run an empty editor | ok | 276 |
| 442 | practice | p01.008: run the untouched starter | ok | 276 |
| 443 | practice | p01.008: run the reference solution | ok | 295 |
| 444 | practice | p01.008: read the solution once passed | ok | 48 |
| 445 | practice | p01.009: read the brief | ok | 0 |
| 446 | practice | p01.009: reveal every hint | ok | 80 |
| 447 | practice | p01.009: run an empty editor | ok | 274 |
| 448 | practice | p01.009: run the untouched starter | ok | 300 |
| 449 | practice | p01.009: run the reference solution | ok | 361 |
| 450 | practice | p01.009: read the solution once passed | ok | 54 |
| 451 | practice | p01.010: read the brief | ok | 0 |
| 452 | practice | p01.010: reveal every hint | ok | 85 |
| 453 | practice | p01.010: run an empty editor | ok | 309 |
| 454 | practice | p01.010: run the untouched starter | ok | 326 |
| 455 | practice | p01.010: run the reference solution | ok | 330 |
| 456 | practice | p01.010: read the solution once passed | ok | 46 |
| 457 | practice | p01.011: read the brief | ok | 0 |
| 458 | practice | p01.011: reveal every hint | ok | 61 |
| 459 | practice | p01.011: run an empty editor | ok | 246 |
| 460 | practice | p01.011: run the untouched starter | ok | 317 |
| 461 | practice | p01.011: run the reference solution | ok | 279 |
| 462 | practice | p01.011: read the solution once passed | ok | 45 |
| 463 | practice | p01.012: read the brief | ok | 0 |
| 464 | practice | p01.012: reveal every hint | ok | 79 |
| 465 | practice | p01.012: run an empty editor | ok | 302 |
| 466 | practice | p01.012: run the untouched starter | ok | 328 |
| 467 | practice | p01.012: run the reference solution | ok | 245 |
| 468 | practice | p01.012: read the solution once passed | ok | 43 |
| 469 | practice | p01.013: read the brief | ok | 0 |
| 470 | practice | p01.013: reveal every hint | ok | 75 |
| 471 | practice | p01.013: run an empty editor | ok | 310 |
| 472 | practice | p01.013: run the untouched starter | ok | 302 |
| 473 | practice | p01.013: run the reference solution | ok | 283 |
| 474 | practice | p01.013: read the solution once passed | ok | 58 |
| 475 | practice | p01.014: read the brief | ok | 0 |
| 476 | practice | p01.014: reveal every hint | ok | 60 |
| 477 | practice | p01.014: run an empty editor | ok | 268 |
| 478 | practice | p01.014: run the untouched starter | ok | 314 |
| 479 | practice | p01.014: run the reference solution | ok | 299 |
| 480 | practice | p01.014: read the solution once passed | ok | 44 |
| 481 | practice | p01.015: read the brief | ok | 0 |
| 482 | practice | p01.015: reveal every hint | ok | 91 |
| 483 | practice | p01.015: run an empty editor | ok | 262 |
| 484 | practice | p01.015: run the untouched starter | ok | 286 |
| 485 | practice | p01.015: run the reference solution | ok | 304 |
| 486 | practice | p01.015: read the solution once passed | ok | 43 |
| 487 | practice | p01.016: read the brief | ok | 0 |
| 488 | practice | p01.016: reveal every hint | ok | 70 |
| 489 | practice | p01.016: run an empty editor | ok | 282 |
| 490 | practice | p01.016: run the untouched starter | ok | 354 |
| 491 | practice | p01.016: run the reference solution | ok | 327 |
| 492 | practice | p01.016: read the solution once passed | ok | 45 |
| 493 | practice | p01.017: read the brief | ok | 0 |
| 494 | practice | p01.017: reveal every hint | ok | 67 |
| 495 | practice | p01.017: run an empty editor | ok | 271 |
| 496 | practice | p01.017: run the untouched starter | ok | 283 |
| 497 | practice | p01.017: run the reference solution | ok | 283 |
| 498 | practice | p01.017: read the solution once passed | ok | 44 |
| 499 | practice | p01.018: read the brief | ok | 0 |
| 500 | practice | p01.018: reveal every hint | ok | 68 |
| 501 | practice | p01.018: run an empty editor | ok | 302 |
| 502 | practice | p01.018: run the untouched starter | ok | 354 |
| 503 | practice | p01.018: run the reference solution | ok | 237 |
| 504 | practice | p01.018: read the solution once passed | ok | 56 |
| 505 | practice | p01.019: read the brief | ok | 0 |
| 506 | practice | p01.019: reveal every hint | ok | 104 |
| 507 | practice | p01.019: run an empty editor | ok | 225 |
| 508 | practice | p01.019: run the untouched starter | ok | 465 |
| 509 | practice | p01.019: run the reference solution | ok | 776 |
| 510 | practice | p01.019: read the solution once passed | ok | 450 |
| 511 | practice | p01.020: read the brief | ok | 0 |
| 512 | practice | p01.020: reveal every hint | ok | 61 |
| 513 | practice | p01.020: run an empty editor | ok | 258 |
| 514 | practice | p01.020: run the untouched starter | ok | 310 |
| 515 | practice | p01.020: run the reference solution | ok | 273 |
| 516 | practice | p01.020: read the solution once passed | ok | 44 |
| 517 | practice | p01.021: read the brief | ok | 0 |
| 518 | practice | p01.021: reveal every hint | ok | 68 |
| 519 | practice | p01.021: run an empty editor | ok | 292 |
| 520 | practice | p01.021: run the untouched starter | ok | 350 |
| 521 | practice | p01.021: run the reference solution | ok | 313 |
| 522 | practice | p01.021: read the solution once passed | ok | 44 |
| 523 | practice | p01.022: read the brief | ok | 0 |
| 524 | practice | p01.022: reveal every hint | ok | 60 |
| 525 | practice | p01.022: run an empty editor | ok | 296 |
| 526 | practice | p01.022: run the untouched starter | ok | 311 |
| 527 | practice | p01.022: run the reference solution | ok | 319 |
| 528 | practice | p01.022: read the solution once passed | ok | 44 |
| 529 | practice | p01.023: read the brief | ok | 0 |
| 530 | practice | p01.023: reveal every hint | ok | 69 |
| 531 | practice | p01.023: run an empty editor | ok | 245 |
| 532 | practice | p01.023: run the untouched starter | ok | 288 |
| 533 | practice | p01.023: run the reference solution | ok | 257 |
| 534 | practice | p01.023: read the solution once passed | ok | 75 |
| 535 | practice | p01.024: read the brief | ok | 0 |
| 536 | practice | p01.024: reveal every hint | ok | 94 |
| 537 | practice | p01.024: run an empty editor | ok | 359 |
| 538 | practice | p01.024: run the untouched starter | ok | 396 |
| 539 | practice | p01.024: run the reference solution | ok | 246 |
| 540 | practice | p01.024: read the solution once passed | ok | 48 |
| 541 | practice | p01.025: read the brief | ok | 0 |
| 542 | practice | p01.025: reveal every hint | ok | 47 |
| 543 | practice | p01.025: run an empty editor | ok | 249 |
| 544 | practice | p01.025: run the untouched starter | ok | 316 |
| 545 | practice | p01.025: run the reference solution | ok | 270 |
| 546 | practice | p01.025: read the solution once passed | ok | 46 |
| 547 | practice | p01.026: read the brief | ok | 0 |
| 548 | practice | p01.026: reveal every hint | ok | 63 |
| 549 | practice | p01.026: run an empty editor | ok | 336 |
| 550 | practice | p01.026: run the untouched starter | ok | 264 |
| 551 | practice | p01.026: run the reference solution | ok | 338 |
| 552 | practice | p01.026: read the solution once passed | ok | 46 |
| 553 | practice | p01.027: read the brief | ok | 0 |
| 554 | practice | p01.027: reveal every hint | ok | 69 |
| 555 | practice | p01.027: run an empty editor | ok | 300 |
| 556 | practice | p01.027: run the untouched starter | ok | 374 |
| 557 | practice | p01.027: run the reference solution | ok | 306 |
| 558 | practice | p01.027: read the solution once passed | ok | 55 |
| 559 | practice | p01.028: read the brief | ok | 0 |
| 560 | practice | p01.028: reveal every hint | ok | 65 |
| 561 | practice | p01.028: run an empty editor | ok | 310 |
| 562 | practice | p01.028: run the untouched starter | ok | 297 |
| 563 | practice | p01.028: run the reference solution | ok | 324 |
| 564 | practice | p01.028: read the solution once passed | ok | 54 |
| 565 | practice | p01.029: read the brief | ok | 0 |
| 566 | practice | p01.029: reveal every hint | ok | 59 |
| 567 | practice | p01.029: run an empty editor | ok | 323 |
| 568 | practice | p01.029: run the untouched starter | ok | 316 |
| 569 | practice | p01.029: run the reference solution | ok | 280 |
| 570 | practice | p01.029: read the solution once passed | ok | 51 |
| 571 | practice | p01.030: read the brief | ok | 0 |
| 572 | practice | p01.030: reveal every hint | ok | 62 |
| 573 | practice | p01.030: run an empty editor | ok | 337 |
| 574 | practice | p01.030: run the untouched starter | ok | 348 |
| 575 | practice | p01.030: run the reference solution | ok | 518 |
| 576 | practice | p01.030: read the solution once passed | ok | 52 |
| 577 | practice | p01.031: read the brief | ok | 0 |
| 578 | practice | p01.031: reveal every hint | ok | 80 |
| 579 | practice | p01.031: run an empty editor | ok | 305 |
| 580 | practice | p01.031: run the untouched starter | ok | 392 |
| 581 | practice | p01.031: run the reference solution | ok | 272 |
| 582 | practice | p01.031: read the solution once passed | ok | 48 |
| 583 | practice | p01.032: read the brief | ok | 0 |
| 584 | practice | p01.032: reveal every hint | ok | 58 |
| 585 | practice | p01.032: run an empty editor | ok | 317 |
| 586 | practice | p01.032: run the untouched starter | ok | 298 |
| 587 | practice | p01.032: run the reference solution | ok | 297 |
| 588 | practice | p01.032: read the solution once passed | ok | 63 |
| 589 | practice | p01.033: read the brief | ok | 0 |
| 590 | practice | p01.033: reveal every hint | ok | 81 |
| 591 | practice | p01.033: run an empty editor | ok | 236 |
| 592 | practice | p01.033: run the untouched starter | ok | 313 |
| 593 | practice | p01.033: run the reference solution | ok | 382 |
| 594 | practice | p01.033: read the solution once passed | ok | 62 |
| 595 | practice | p01.034: read the brief | ok | 0 |
| 596 | practice | p01.034: reveal every hint | ok | 42 |
| 597 | practice | p01.034: run an empty editor | ok | 325 |
| 598 | practice | p01.034: run the untouched starter | ok | 291 |
| 599 | practice | p01.034: run the reference solution | ok | 277 |
| 600 | practice | p01.034: read the solution once passed | ok | 45 |
| 601 | practice | p01.035: read the brief | ok | 0 |
| 602 | practice | p01.035: reveal every hint | ok | 80 |
| 603 | practice | p01.035: run an empty editor | ok | 294 |
| 604 | practice | p01.035: run the untouched starter | ok | 372 |
| 605 | practice | p01.035: run the reference solution | ok | 278 |
| 606 | practice | p01.035: read the solution once passed | ok | 55 |
| 607 | practice | p01.036: read the brief | ok | 0 |
| 608 | practice | p01.036: reveal every hint | ok | 92 |
| 609 | practice | p01.036: run an empty editor | ok | 276 |
| 610 | practice | p01.036: run the untouched starter | ok | 280 |
| 611 | practice | p01.036: run the reference solution | ok | 291 |
| 612 | practice | p01.036: read the solution once passed | ok | 36 |
| 613 | practice | p02.001: read the brief | ok | 0 |
| 614 | practice | p02.001: reveal every hint | ok | 57 |
| 615 | practice | p02.001: run an empty editor | ok | 252 |
| 616 | practice | p02.001: run the untouched starter | ok | 282 |
| 617 | practice | p02.001: run the reference solution | ok | 270 |
| 618 | practice | p02.001: read the solution once passed | ok | 40 |
| 619 | practice | p02.002: read the brief | ok | 0 |
| 620 | practice | p02.002: reveal every hint | ok | 43 |
| 621 | practice | p02.002: run an empty editor | ok | 273 |
| 622 | practice | p02.002: run the untouched starter | ok | 267 |
| 623 | practice | p02.002: run the reference solution | ok | 298 |
| 624 | practice | p02.002: read the solution once passed | ok | 53 |
| 625 | practice | p02.003: read the brief | ok | 0 |
| 626 | practice | p02.003: reveal every hint | ok | 48 |
| 627 | practice | p02.003: run an empty editor | ok | 236 |
| 628 | practice | p02.003: run the untouched starter | ok | 254 |
| 629 | practice | p02.003: run the reference solution | ok | 310 |
| 630 | practice | p02.003: read the solution once passed | ok | 31 |
| 631 | practice | p02.004: read the brief | ok | 0 |
| 632 | practice | p02.004: reveal every hint | ok | 47 |
| 633 | practice | p02.004: run an empty editor | ok | 300 |
| 634 | practice | p02.004: run the untouched starter | ok | 267 |
| 635 | practice | p02.004: run the reference solution | ok | 259 |
| 636 | practice | p02.004: read the solution once passed | ok | 47 |
| 637 | practice | p02.005: read the brief | ok | 0 |
| 638 | practice | p02.005: reveal every hint | ok | 42 |
| 639 | practice | p02.005: run an empty editor | ok | 254 |
| 640 | practice | p02.005: run the untouched starter | ok | 345 |
| 641 | practice | p02.005: run the reference solution | ok | 284 |
| 642 | practice | p02.005: read the solution once passed | ok | 38 |
| 643 | practice | p02.006: read the brief | ok | 0 |
| 644 | practice | p02.006: reveal every hint | ok | 55 |
| 645 | practice | p02.006: run an empty editor | ok | 295 |
| 646 | practice | p02.006: run the untouched starter | ok | 262 |
| 647 | practice | p02.006: run the reference solution | ok | 342 |
| 648 | practice | p02.006: read the solution once passed | ok | 39 |
| 649 | practice | p02.007: read the brief | ok | 0 |
| 650 | practice | p02.007: reveal every hint | ok | 55 |
| 651 | practice | p02.007: run an empty editor | ok | 228 |
| 652 | practice | p02.007: run the untouched starter | ok | 300 |
| 653 | practice | p02.007: run the reference solution | ok | 264 |
| 654 | practice | p02.007: read the solution once passed | ok | 38 |
| 655 | practice | p02.008: read the brief | ok | 0 |
| 656 | practice | p02.008: reveal every hint | ok | 61 |
| 657 | practice | p02.008: run an empty editor | ok | 341 |
| 658 | practice | p02.008: run the untouched starter | ok | 350 |
| 659 | practice | p02.008: run the reference solution | ok | 370 |
| 660 | practice | p02.008: read the solution once passed | ok | 53 |
| 661 | practice | p02.009: read the brief | ok | 0 |
| 662 | practice | p02.009: reveal every hint | ok | 50 |
| 663 | practice | p02.009: run an empty editor | ok | 285 |
| 664 | practice | p02.009: run the untouched starter | ok | 298 |
| 665 | practice | p02.009: run the reference solution | ok | 289 |
| 666 | practice | p02.009: read the solution once passed | ok | 42 |
| 667 | practice | p02.010: read the brief | ok | 0 |
| 668 | practice | p02.010: reveal every hint | ok | 55 |
| 669 | practice | p02.010: run an empty editor | ok | 310 |
| 670 | practice | p02.010: run the untouched starter | ok | 349 |
| 671 | practice | p02.010: run the reference solution | ok | 343 |
| 672 | practice | p02.010: read the solution once passed | ok | 47 |
| 673 | practice | p02.011: read the brief | ok | 0 |
| 674 | practice | p02.011: reveal every hint | ok | 65 |
| 675 | practice | p02.011: run an empty editor | ok | 269 |
| 676 | practice | p02.011: run the untouched starter | ok | 310 |
| 677 | practice | p02.011: run the reference solution | ok | 295 |
| 678 | practice | p02.011: read the solution once passed | ok | 42 |
| 679 | practice | p02.012: read the brief | ok | 0 |
| 680 | practice | p02.012: reveal every hint | ok | 49 |
| 681 | practice | p02.012: run an empty editor | ok | 312 |
| 682 | practice | p02.012: run the untouched starter | ok | 352 |
| 683 | practice | p02.012: run the reference solution | ok | 294 |
| 684 | practice | p02.012: read the solution once passed | ok | 46 |
| 685 | practice | p02.013: read the brief | ok | 0 |
| 686 | practice | p02.013: reveal every hint | ok | 91 |
| 687 | practice | p02.013: run an empty editor | ok | 310 |
| 688 | practice | p02.013: run the untouched starter | ok | 389 |
| 689 | practice | p02.013: run the reference solution | ok | 328 |
| 690 | practice | p02.013: read the solution once passed | ok | 41 |
| 691 | practice | p02.014: read the brief | ok | 0 |
| 692 | practice | p02.014: reveal every hint | ok | 52 |
| 693 | practice | p02.014: run an empty editor | ok | 219 |
| 694 | practice | p02.014: run the untouched starter | ok | 282 |
| 695 | practice | p02.014: run the reference solution | ok | 291 |
| 696 | practice | p02.014: read the solution once passed | ok | 43 |
| 697 | practice | p02.015: read the brief | ok | 0 |
| 698 | practice | p02.015: reveal every hint | ok | 74 |
| 699 | practice | p02.015: run an empty editor | ok | 264 |
| 700 | practice | p02.015: run the untouched starter | ok | 270 |
| 701 | practice | p02.015: run the reference solution | ok | 336 |
| 702 | practice | p02.015: read the solution once passed | ok | 44 |
| 703 | practice | p02.016: read the brief | ok | 0 |
| 704 | practice | p02.016: reveal every hint | ok | 41 |
| 705 | practice | p02.016: run an empty editor | ok | 257 |
| 706 | practice | p02.016: run the untouched starter | ok | 302 |
| 707 | practice | p02.016: run the reference solution | ok | 347 |
| 708 | practice | p02.016: read the solution once passed | ok | 42 |
| 709 | practice | p04.011: read the brief | ok | 0 |
| 710 | practice | p04.011: reveal every hint | ok | 66 |
| 711 | practice | p04.011: run an empty editor | ok | 249 |
| 712 | practice | p04.011: run the untouched starter | ok | 381 |
| 713 | practice | p04.011: run the reference solution | ok | 312 |
| 714 | practice | p04.011: read the solution once passed | ok | 46 |
| 715 | practice | p04.012: read the brief | ok | 0 |
| 716 | practice | p04.012: reveal every hint | ok | 71 |
| 717 | practice | p04.012: run an empty editor | ok | 318 |
| 718 | practice | p04.012: run the untouched starter | ok | 300 |
| 719 | practice | p04.012: run the reference solution | ok | 320 |
| 720 | practice | p04.012: read the solution once passed | ok | 91 |
| 721 | practice | p04.013: read the brief | ok | 0 |
| 722 | practice | p04.013: reveal every hint | ok | 69 |
| 723 | practice | p04.013: run an empty editor | ok | 259 |
| 724 | practice | p04.013: run the untouched starter | ok | 288 |
| 725 | practice | p04.013: run the reference solution | ok | 284 |
| 726 | practice | p04.013: read the solution once passed | ok | 42 |
| 727 | practice | p04.001: read the brief | ok | 0 |
| 728 | practice | p04.001: reveal every hint | ok | 51 |
| 729 | practice | p04.001: run an empty editor | ok | 229 |
| 730 | practice | p04.001: run the untouched starter | ok | 410 |
| 731 | practice | p04.001: run the reference solution | ok | 349 |
| 732 | practice | p04.001: read the solution once passed | ok | 51 |
| 733 | practice | p04.002: read the brief | ok | 0 |
| 734 | practice | p04.002: reveal every hint | ok | 53 |
| 735 | practice | p04.002: run an empty editor | ok | 244 |
| 736 | practice | p04.002: run the untouched starter | ok | 268 |
| 737 | practice | p04.002: run the reference solution | ok | 268 |
| 738 | practice | p04.002: read the solution once passed | ok | 46 |
| 739 | practice | p04.003: read the brief | ok | 0 |
| 740 | practice | p04.003: reveal every hint | ok | 76 |
| 741 | practice | p04.003: run an empty editor | ok | 305 |
| 742 | practice | p04.003: run the untouched starter | ok | 331 |
| 743 | practice | p04.003: run the reference solution | ok | 395 |
| 744 | practice | p04.003: read the solution once passed | ok | 52 |
| 745 | practice | p04.004: read the brief | ok | 0 |
| 746 | practice | p04.004: reveal every hint | ok | 68 |
| 747 | practice | p04.004: run an empty editor | ok | 274 |
| 748 | practice | p04.004: run the untouched starter | ok | 296 |
| 749 | practice | p04.004: run the reference solution | ok | 308 |
| 750 | practice | p04.004: read the solution once passed | ok | 55 |
| 751 | practice | p04.005: read the brief | ok | 0 |
| 752 | practice | p04.005: reveal every hint | ok | 76 |
| 753 | practice | p04.005: run an empty editor | ok | 326 |
| 754 | practice | p04.005: run the untouched starter | ok | 291 |
| 755 | practice | p04.005: run the reference solution | ok | 301 |
| 756 | practice | p04.005: read the solution once passed | ok | 39 |
| 757 | practice | p04.006: read the brief | ok | 0 |
| 758 | practice | p04.006: reveal every hint | ok | 70 |
| 759 | practice | p04.006: run an empty editor | ok | 315 |
| 760 | practice | p04.006: run the untouched starter | ok | 289 |
| 761 | practice | p04.006: run the reference solution | ok | 354 |
| 762 | practice | p04.006: read the solution once passed | ok | 40 |
| 763 | practice | p04.007: read the brief | ok | 0 |
| 764 | practice | p04.007: reveal every hint | ok | 50 |
| 765 | practice | p04.007: run an empty editor | ok | 270 |
| 766 | practice | p04.007: run the untouched starter | ok | 306 |
| 767 | practice | p04.007: run the reference solution | ok | 263 |
| 768 | practice | p04.007: read the solution once passed | ok | 88 |
| 769 | practice | p04.008: read the brief | ok | 0 |
| 770 | practice | p04.008: reveal every hint | ok | 47 |
| 771 | practice | p04.008: run an empty editor | ok | 279 |
| 772 | practice | p04.008: run the untouched starter | ok | 297 |
| 773 | practice | p04.008: run the reference solution | ok | 361 |
| 774 | practice | p04.008: read the solution once passed | ok | 38 |
| 775 | practice | p04.009: read the brief | ok | 0 |
| 776 | practice | p04.009: reveal every hint | ok | 61 |
| 777 | practice | p04.009: run an empty editor | ok | 362 |
| 778 | practice | p04.009: run the untouched starter | ok | 305 |
| 779 | practice | p04.009: run the reference solution | ok | 286 |
| 780 | practice | p04.009: read the solution once passed | ok | 41 |
| 781 | practice | p04.010: read the brief | ok | 0 |
| 782 | practice | p04.010: reveal every hint | ok | 60 |
| 783 | practice | p04.010: run an empty editor | ok | 245 |
| 784 | practice | p04.010: run the untouched starter | ok | 266 |
| 785 | practice | p04.010: run the reference solution | ok | 253 |
| 786 | practice | p04.010: read the solution once passed | ok | 41 |
| 787 | practice | p05.001: read the brief | ok | 0 |
| 788 | practice | p05.001: reveal every hint | ok | 64 |
| 789 | practice | p05.001: run an empty editor | ok | 235 |
| 790 | practice | p05.001: run the untouched starter | ok | 279 |
| 791 | practice | p05.001: run the reference solution | ok | 285 |
| 792 | practice | p05.001: read the solution once passed | ok | 37 |
| 793 | practice | p05.002: read the brief | ok | 0 |
| 794 | practice | p05.002: reveal every hint | ok | 45 |
| 795 | practice | p05.002: run an empty editor | ok | 287 |
| 796 | practice | p05.002: run the untouched starter | ok | 311 |
| 797 | practice | p05.002: run the reference solution | ok | 309 |
| 798 | practice | p05.002: read the solution once passed | ok | 47 |
| 799 | practice | p05.003: read the brief | ok | 0 |
| 800 | practice | p05.003: reveal every hint | ok | 110 |
| 801 | practice | p05.003: run an empty editor | ok | 234 |
| 802 | practice | p05.003: run the untouched starter | ok | 342 |
| 803 | practice | p05.003: run the reference solution | ok | 290 |
| 804 | practice | p05.003: read the solution once passed | ok | 34 |
| 805 | practice | p05.004: read the brief | ok | 0 |
| 806 | practice | p05.004: reveal every hint | ok | 61 |
| 807 | practice | p05.004: run an empty editor | ok | 277 |
| 808 | practice | p05.004: run the untouched starter | ok | 306 |
| 809 | practice | p05.004: run the reference solution | ok | 313 |
| 810 | practice | p05.004: read the solution once passed | ok | 43 |
| 811 | practice | p05.005: read the brief | ok | 0 |
| 812 | practice | p05.005: reveal every hint | ok | 58 |
| 813 | practice | p05.005: run an empty editor | ok | 274 |
| 814 | practice | p05.005: run the untouched starter | ok | 311 |
| 815 | practice | p05.005: run the reference solution | ok | 303 |
| 816 | practice | p05.005: read the solution once passed | ok | 36 |
| 817 | practice | p05.006: read the brief | ok | 0 |
| 818 | practice | p05.006: reveal every hint | ok | 61 |
| 819 | practice | p05.006: run an empty editor | ok | 303 |
| 820 | practice | p05.006: run the untouched starter | ok | 288 |
| 821 | practice | p05.006: run the reference solution | ok | 264 |
| 822 | practice | p05.006: read the solution once passed | ok | 36 |
| 823 | practice | p05.007: read the brief | ok | 0 |
| 824 | practice | p05.007: reveal every hint | ok | 78 |
| 825 | practice | p05.007: run an empty editor | ok | 365 |
| 826 | practice | p05.007: run the untouched starter | ok | 274 |
| 827 | practice | p05.007: run the reference solution | ok | 372 |
| 828 | practice | p05.007: read the solution once passed | ok | 35 |
| 829 | practice | p05.008: read the brief | ok | 0 |
| 830 | practice | p05.008: reveal every hint | ok | 56 |
| 831 | practice | p05.008: run an empty editor | ok | 260 |
| 832 | practice | p05.008: run the untouched starter | ok | 393 |
| 833 | practice | p05.008: run the reference solution | ok | 294 |
| 834 | practice | p05.008: read the solution once passed | ok | 40 |
| 835 | practice | p05.009: read the brief | ok | 0 |
| 836 | practice | p05.009: reveal every hint | ok | 53 |
| 837 | practice | p05.009: run an empty editor | ok | 227 |
| 838 | practice | p05.009: run the untouched starter | ok | 308 |
| 839 | practice | p05.009: run the reference solution | ok | 323 |
| 840 | practice | p05.009: read the solution once passed | ok | 37 |
| 841 | practice | p05.010: read the brief | ok | 0 |
| 842 | practice | p05.010: reveal every hint | ok | 54 |
| 843 | practice | p05.010: run an empty editor | ok | 313 |
| 844 | practice | p05.010: run the untouched starter | ok | 325 |
| 845 | practice | p05.010: run the reference solution | ok | 380 |
| 846 | practice | p05.010: read the solution once passed | ok | 40 |
| 847 | practice | p03.001: read the brief | ok | 0 |
| 848 | practice | p03.001: reveal every hint | ok | 39 |
| 849 | practice | p03.001: run an empty editor | ok | 301 |
| 850 | practice | p03.001: run the untouched starter | ok | 281 |
| 851 | practice | p03.001: run the reference solution | ok | 327 |
| 852 | practice | p03.001: read the solution once passed | ok | 37 |
| 853 | practice | p03.002: read the brief | ok | 0 |
| 854 | practice | p03.002: reveal every hint | ok | 51 |
| 855 | practice | p03.002: run an empty editor | ok | 322 |
| 856 | practice | p03.002: run the untouched starter | ok | 364 |
| 857 | practice | p03.002: run the reference solution | ok | 362 |
| 858 | practice | p03.002: read the solution once passed | ok | 38 |
| 859 | practice | p03.003: read the brief | ok | 0 |
| 860 | practice | p03.003: reveal every hint | ok | 39 |
| 861 | practice | p03.003: run an empty editor | ok | 250 |
| 862 | practice | p03.003: run the untouched starter | ok | 289 |
| 863 | practice | p03.003: run the reference solution | ok | 273 |
| 864 | practice | p03.003: read the solution once passed | ok | 39 |
| 865 | practice | p03.004: read the brief | ok | 0 |
| 866 | practice | p03.004: reveal every hint | ok | 46 |
| 867 | practice | p03.004: run an empty editor | ok | 309 |
| 868 | practice | p03.004: run the untouched starter | ok | 326 |
| 869 | practice | p03.004: run the reference solution | ok | 307 |
| 870 | practice | p03.004: read the solution once passed | ok | 37 |
| 871 | practice | p08.001: read the brief | ok | 0 |
| 872 | practice | p08.001: reveal every hint | ok | 80 |
| 873 | practice | p08.001: run an empty editor | ok | 260 |
| 874 | practice | p08.001: run the untouched starter | ok | 310 |
| 875 | practice | p08.001: run the reference solution | ok | 267 |
| 876 | practice | p08.001: read the solution once passed | ok | 32 |
| 877 | practice | p08.002: read the brief | ok | 0 |
| 878 | practice | p08.002: reveal every hint | ok | 53 |
| 879 | practice | p08.002: run an empty editor | ok | 339 |
| 880 | practice | p08.002: run the untouched starter | ok | 325 |
| 881 | practice | p08.002: run the reference solution | ok | 246 |
| 882 | practice | p08.002: read the solution once passed | ok | 43 |
| 883 | practice | p08.003: read the brief | ok | 0 |
| 884 | practice | p08.003: reveal every hint | ok | 54 |
| 885 | practice | p08.003: run an empty editor | ok | 294 |
| 886 | practice | p08.003: run the untouched starter | ok | 336 |
| 887 | practice | p08.003: run the reference solution | ok | 289 |
| 888 | practice | p08.003: read the solution once passed | ok | 33 |
| 889 | practice | p08.004: read the brief | ok | 0 |
| 890 | practice | p08.004: reveal every hint | ok | 44 |
| 891 | practice | p08.004: run an empty editor | ok | 223 |
| 892 | practice | p08.004: run the untouched starter | ok | 322 |
| 893 | practice | p08.004: run the reference solution | ok | 267 |
| 894 | practice | p08.004: read the solution once passed | ok | 39 |
| 895 | practice | p09.001: read the brief | ok | 0 |
| 896 | practice | p09.001: reveal every hint | ok | 64 |
| 897 | practice | p09.001: run an empty editor | ok | 260 |
| 898 | practice | p09.001: run the untouched starter | ok | 319 |
| 899 | practice | p09.001: run the reference solution | ok | 255 |
| 900 | practice | p09.001: read the solution once passed | ok | 43 |
| 901 | practice | p09.002: read the brief | ok | 0 |
| 902 | practice | p09.002: reveal every hint | ok | 76 |
| 903 | practice | p09.002: run an empty editor | ok | 289 |
| 904 | practice | p09.002: run the untouched starter | ok | 267 |
| 905 | practice | p09.002: run the reference solution | ok | 279 |
| 906 | practice | p09.002: read the solution once passed | ok | 37 |
| 907 | practice | p09.003: read the brief | ok | 0 |
| 908 | practice | p09.003: reveal every hint | ok | 49 |
| 909 | practice | p09.003: run an empty editor | ok | 282 |
| 910 | practice | p09.003: run the untouched starter | ok | 319 |
| 911 | practice | p09.003: run the reference solution | ok | 286 |
| 912 | practice | p09.003: read the solution once passed | ok | 29 |
| 913 | practice | p10.001: read the brief | ok | 0 |
| 914 | practice | p10.001: reveal every hint | ok | 55 |
| 915 | practice | p10.001: run an empty editor | ok | 266 |
| 916 | practice | p10.001: run the untouched starter | ok | 307 |
| 917 | practice | p10.001: run the reference solution | ok | 282 |
| 918 | practice | p10.001: read the solution once passed | ok | 34 |
| 919 | practice | p10.002: read the brief | ok | 0 |
| 920 | practice | p10.002: reveal every hint | ok | 49 |
| 921 | practice | p10.002: run an empty editor | ok | 318 |
| 922 | practice | p10.002: run the untouched starter | ok | 311 |
| 923 | practice | p10.002: run the reference solution | ok | 296 |
| 924 | practice | p10.002: read the solution once passed | ok | 44 |
| 925 | practice | p10.003: read the brief | ok | 0 |
| 926 | practice | p10.003: reveal every hint | ok | 56 |
| 927 | practice | p10.003: run an empty editor | ok | 314 |
| 928 | practice | p10.003: run the untouched starter | ok | 387 |
| 929 | practice | p10.003: run the reference solution | ok | 284 |
| 930 | practice | p10.003: read the solution once passed | ok | 37 |
| 931 | practice | p11.001: read the brief | ok | 0 |
| 932 | practice | p11.001: reveal every hint | ok | 65 |
| 933 | practice | p11.001: run an empty editor | ok | 389 |
| 934 | practice | p11.001: run the untouched starter | ok | 495 |
| 935 | practice | p11.001: run the reference solution | ok | 635 |
| 936 | practice | p11.001: read the solution once passed | ok | 38 |
| 937 | practice | p11.002: read the brief | ok | 0 |
| 938 | practice | p11.002: reveal every hint | ok | 47 |
| 939 | practice | p11.002: run an empty editor | ok | 407 |
| 940 | practice | p11.002: run the untouched starter | ok | 598 |
| 941 | practice | p11.002: run the reference solution | ok | 920 |
| 942 | practice | p11.002: read the solution once passed | ok | 40 |
| 943 | practice | p11.003: read the brief | ok | 0 |
| 944 | practice | p11.003: reveal every hint | ok | 41 |
| 945 | practice | p11.003: run an empty editor | ok | 403 |
| 946 | practice | p11.003: run the untouched starter | ok | 532 |
| 947 | practice | p11.003: run the reference solution | ok | 592 |
| 948 | practice | p11.003: read the solution once passed | ok | 40 |
| 949 | practice | p13.001: read the brief | ok | 0 |
| 950 | practice | p13.001: reveal every hint | ok | 54 |
| 951 | practice | p13.001: run an empty editor | ok | 312 |
| 952 | practice | p13.001: run the untouched starter | ok | 344 |
| 953 | practice | p13.001: run the reference solution | ok | 825 |
| 954 | practice | p13.001: read the solution once passed | ok | 46 |
| 955 | practice | p13.002: read the brief | ok | 0 |
| 956 | practice | p13.002: reveal every hint | ok | 51 |
| 957 | practice | p13.002: run an empty editor | ok | 279 |
| 958 | practice | p13.002: run the untouched starter | ok | 329 |
| 959 | practice | p13.002: run the reference solution | ok | 387 |
| 960 | practice | p13.002: read the solution once passed | ok | 35 |
| 961 | practice | p13.003: read the brief | ok | 0 |
| 962 | practice | p13.003: reveal every hint | ok | 41 |
| 963 | practice | p13.003: run an empty editor | ok | 299 |
| 964 | practice | p13.003: run the untouched starter | ok | 352 |
| 965 | practice | p13.003: run the reference solution | ok | 273 |
| 966 | practice | p13.003: read the solution once passed | ok | 34 |
| 967 | practice | p14.001: read the brief | ok | 0 |
| 968 | practice | p14.001: reveal every hint | ok | 65 |
| 969 | practice | p14.001: run an empty editor | ok | 238 |
| 970 | practice | p14.001: run the untouched starter | ok | 327 |
| 971 | practice | p14.001: run the reference solution | ok | 272 |
| 972 | practice | p14.001: read the solution once passed | ok | 37 |
| 973 | practice | p14.002: read the brief | ok | 0 |
| 974 | practice | p14.002: reveal every hint | ok | 43 |
| 975 | practice | p14.002: run an empty editor | ok | 303 |
| 976 | practice | p14.002: run the untouched starter | ok | 292 |
| 977 | practice | p14.002: run the reference solution | ok | 298 |
| 978 | practice | p14.002: read the solution once passed | ok | 37 |
| 979 | practice | p14.003: read the brief | ok | 0 |
| 980 | practice | p14.003: reveal every hint | ok | 43 |
| 981 | practice | p14.003: run an empty editor | ok | 240 |
| 982 | practice | p14.003: run the untouched starter | ok | 322 |
| 983 | practice | p14.003: run the reference solution | ok | 296 |
| 984 | practice | p14.003: read the solution once passed | ok | 38 |
| 985 | practice | p14.004: read the brief | ok | 0 |
| 986 | practice | p14.004: reveal every hint | ok | 43 |
| 987 | practice | p14.004: run an empty editor | ok | 297 |
| 988 | practice | p14.004: run the untouched starter | ok | 283 |
| 989 | practice | p14.004: run the reference solution | ok | 273 |
| 990 | practice | p14.004: read the solution once passed | ok | 47 |
| 991 | practice | p06.001: read the brief | ok | 0 |
| 992 | practice | p06.001: reveal every hint | ok | 89 |
| 993 | practice | p06.001: run an empty editor | ok | 276 |
| 994 | practice | p06.001: run the untouched starter | ok | 295 |
| 995 | practice | p06.001: run the reference solution | ok | 239 |
| 996 | practice | p06.001: read the solution once passed | ok | 40 |
| 997 | practice | p06.002: read the brief | ok | 0 |
| 998 | practice | p06.002: reveal every hint | ok | 55 |
| 999 | practice | p06.002: run an empty editor | ok | 329 |
| 1000 | practice | p06.002: run the untouched starter | ok | 326 |
| 1001 | practice | p06.002: run the reference solution | ok | 313 |
| 1002 | practice | p06.002: read the solution once passed | ok | 37 |
| 1003 | practice | p06.003: read the brief | ok | 0 |
| 1004 | practice | p06.003: reveal every hint | ok | 64 |
| 1005 | practice | p06.003: run an empty editor | ok | 257 |
| 1006 | practice | p06.003: run the untouched starter | ok | 353 |
| 1007 | practice | p06.003: run the reference solution | ok | 289 |
| 1008 | practice | p06.003: read the solution once passed | ok | 37 |
| 1009 | practice | p06.004: read the brief | ok | 0 |
| 1010 | practice | p06.004: reveal every hint | ok | 65 |
| 1011 | practice | p06.004: run an empty editor | ok | 252 |
| 1012 | practice | p06.004: run the untouched starter | ok | 319 |
| 1013 | practice | p06.004: run the reference solution | ok | 352 |
| 1014 | practice | p06.004: read the solution once passed | ok | 40 |
| 1015 | practice | p07.001: read the brief | ok | 0 |
| 1016 | practice | p07.001: reveal every hint | ok | 53 |
| 1017 | practice | p07.001: run an empty editor | ok | 222 |
| 1018 | practice | p07.001: run the untouched starter | ok | 280 |
| 1019 | practice | p07.001: run the reference solution | ok | 337 |
| 1020 | practice | p07.001: read the solution once passed | ok | 36 |
| 1021 | practice | p07.002: read the brief | ok | 0 |
| 1022 | practice | p07.002: reveal every hint | ok | 62 |
| 1023 | practice | p07.002: run an empty editor | ok | 294 |
| 1024 | practice | p07.002: run the untouched starter | ok | 340 |
| 1025 | practice | p07.002: run the reference solution | ok | 296 |
| 1026 | practice | p07.002: read the solution once passed | ok | 50 |
| 1027 | practice | p07.003: read the brief | ok | 0 |
| 1028 | practice | p07.003: reveal every hint | ok | 63 |
| 1029 | practice | p07.003: run an empty editor | ok | 267 |
| 1030 | practice | p07.003: run the untouched starter | ok | 301 |
| 1031 | practice | p07.003: run the reference solution | ok | 306 |
| 1032 | practice | p07.003: read the solution once passed | ok | 38 |
| 1033 | practice | p07.004: read the brief | ok | 0 |
| 1034 | practice | p07.004: reveal every hint | ok | 69 |
| 1035 | practice | p07.004: run an empty editor | ok | 263 |
| 1036 | practice | p07.004: run the untouched starter | ok | 257 |
| 1037 | practice | p07.004: run the reference solution | ok | 284 |
| 1038 | practice | p07.004: read the solution once passed | ok | 38 |
| 1039 | practice | p12.001: read the brief | ok | 0 |
| 1040 | practice | p12.001: reveal every hint | ok | 57 |
| 1041 | practice | p12.001: run an empty editor | ok | 326 |
| 1042 | practice | p12.001: run the untouched starter | ok | 334 |
| 1043 | practice | p12.001: run the reference solution | ok | 330 |
| 1044 | practice | p12.001: read the solution once passed | ok | 47 |
| 1045 | practice | p12.002: read the brief | ok | 0 |
| 1046 | practice | p12.002: reveal every hint | ok | 69 |
| 1047 | practice | p12.002: run an empty editor | ok | 318 |
| 1048 | practice | p12.002: run the untouched starter | ok | 284 |
| 1049 | practice | p12.002: run the reference solution | ok | 325 |
| 1050 | practice | p12.002: read the solution once passed | ok | 41 |
| 1051 | practice | p12.003: read the brief | ok | 0 |
| 1052 | practice | p12.003: reveal every hint | ok | 90 |
| 1053 | practice | p12.003: run an empty editor | ok | 285 |
| 1054 | practice | p12.003: run the untouched starter | ok | 349 |
| 1055 | practice | p12.003: run the reference solution | ok | 261 |
| 1056 | practice | p12.003: read the solution once passed | ok | 43 |
| 1057 | practice | p15.001: read the brief | ok | 0 |
| 1058 | practice | p15.001: reveal every hint | ok | 103 |
| 1059 | practice | p15.001: run an empty editor | ok | 282 |
| 1060 | practice | p15.001: run the untouched starter | ok | 318 |
| 1061 | practice | p15.001: run the reference solution | ok | 261 |
| 1062 | practice | p15.001: read the solution once passed | ok | 37 |
| 1063 | practice | p15.002: read the brief | ok | 0 |
| 1064 | practice | p15.002: reveal every hint | ok | 65 |
| 1065 | practice | p15.002: run an empty editor | ok | 248 |
| 1066 | practice | p15.002: run the untouched starter | ok | 288 |
| 1067 | practice | p15.002: run the reference solution | ok | 305 |
| 1068 | practice | p15.002: read the solution once passed | ok | 40 |
| 1069 | practice | p15.003: read the brief | ok | 0 |
| 1070 | practice | p15.003: reveal every hint | ok | 79 |
| 1071 | practice | p15.003: run an empty editor | ok | 316 |
| 1072 | practice | p15.003: run the untouched starter | ok | 289 |
| 1073 | practice | p15.003: run the reference solution | ok | 348 |
| 1074 | practice | p15.003: read the solution once passed | ok | 39 |
| 1075 | practice | p16.001: read the brief | ok | 0 |
| 1076 | practice | p16.001: reveal every hint | ok | 59 |
| 1077 | practice | p16.001: run an empty editor | ok | 269 |
| 1078 | practice | p16.001: run the untouched starter | ok | 307 |
| 1079 | practice | p16.001: run the reference solution | ok | 261 |
| 1080 | practice | p16.001: read the solution once passed | ok | 38 |
| 1081 | practice | p16.002: read the brief | ok | 0 |
| 1082 | practice | p16.002: reveal every hint | ok | 54 |
| 1083 | practice | p16.002: run an empty editor | ok | 291 |
| 1084 | practice | p16.002: run the untouched starter | ok | 297 |
| 1085 | practice | p16.002: run the reference solution | ok | 388 |
| 1086 | practice | p16.002: read the solution once passed | ok | 39 |
| 1087 | practice | p16.003: read the brief | ok | 0 |
| 1088 | practice | p16.003: reveal every hint | ok | 83 |
| 1089 | practice | p16.003: run an empty editor | ok | 339 |
| 1090 | practice | p16.003: run the untouched starter | ok | 346 |
| 1091 | practice | p16.003: run the reference solution | ok | 244 |
| 1092 | practice | p16.003: read the solution once passed | ok | 46 |
| 1093 | practice | p17.001: read the brief | ok | 0 |
| 1094 | practice | p17.001: reveal every hint | ok | 72 |
| 1095 | practice | p17.001: run an empty editor | ok | 270 |
| 1096 | practice | p17.001: run the untouched starter | ok | 359 |
| 1097 | practice | p17.001: run the reference solution | ok | 250 |
| 1098 | practice | p17.001: read the solution once passed | ok | 50 |
| 1099 | practice | p17.002: read the brief | ok | 0 |
| 1100 | practice | p17.002: reveal every hint | ok | 67 |
| 1101 | practice | p17.002: run an empty editor | ok | 354 |
| 1102 | practice | p17.002: run the untouched starter | ok | 318 |
| 1103 | practice | p17.002: run the reference solution | ok | 300 |
| 1104 | practice | p17.002: read the solution once passed | ok | 37 |
| 1105 | practice | p17.003: read the brief | ok | 0 |
| 1106 | practice | p17.003: reveal every hint | ok | 69 |
| 1107 | practice | p17.003: run an empty editor | ok | 360 |
| 1108 | practice | p17.003: run the untouched starter | ok | 290 |
| 1109 | practice | p17.003: run the reference solution | ok | 387 |
| 1110 | practice | p17.003: read the solution once passed | ok | 41 |
| 1111 | practice | s01.001: read the brief | ok | 0 |
| 1112 | practice | s01.001: reveal every hint | ok | 55 |
| 1113 | practice | s01.001: run an empty editor | ok | 286 |
| 1114 | practice | s01.001: run the untouched starter | ok | 324 |
| 1115 | practice | s01.001: run the reference solution | ok | 289 |
| 1116 | practice | s01.001: read the solution once passed | ok | 50 |
| 1117 | practice | s01.002: read the brief | ok | 0 |
| 1118 | practice | s01.002: reveal every hint | ok | 52 |
| 1119 | practice | s01.002: run an empty editor | ok | 335 |
| 1120 | practice | s01.002: run the untouched starter | ok | 280 |
| 1121 | practice | s01.002: run the reference solution | ok | 353 |
| 1122 | practice | s01.002: read the solution once passed | ok | 35 |
| 1123 | practice | s01.003: read the brief | ok | 0 |
| 1124 | practice | s01.003: reveal every hint | ok | 67 |
| 1125 | practice | s01.003: run an empty editor | ok | 334 |
| 1126 | practice | s01.003: run the untouched starter | ok | 326 |
| 1127 | practice | s01.003: run the reference solution | ok | 281 |
| 1128 | practice | s01.003: read the solution once passed | ok | 34 |
| 1129 | practice | s02.001: read the brief | ok | 0 |
| 1130 | practice | s02.001: reveal every hint | ok | 56 |
| 1131 | practice | s02.001: run an empty editor | ok | 236 |
| 1132 | practice | s02.001: run the untouched starter | ok | 308 |
| 1133 | practice | s02.001: run the reference solution | ok | 244 |
| 1134 | practice | s02.001: read the solution once passed | ok | 36 |
| 1135 | practice | s02.002: read the brief | ok | 0 |
| 1136 | practice | s02.002: reveal every hint | ok | 53 |
| 1137 | practice | s02.002: run an empty editor | ok | 259 |
| 1138 | practice | s02.002: run the untouched starter | ok | 292 |
| 1139 | practice | s02.002: run the reference solution | ok | 277 |
| 1140 | practice | s02.002: read the solution once passed | ok | 37 |
| 1141 | practice | s02.003: read the brief | ok | 0 |
| 1142 | practice | s02.003: reveal every hint | ok | 72 |
| 1143 | practice | s02.003: run an empty editor | ok | 266 |
| 1144 | practice | s02.003: run the untouched starter | ok | 282 |
| 1145 | practice | s02.003: run the reference solution | ok | 296 |
| 1146 | practice | s02.003: read the solution once passed | ok | 40 |
| 1147 | practice | s03.001: read the brief | ok | 0 |
| 1148 | practice | s03.001: reveal every hint | ok | 52 |
| 1149 | practice | s03.001: run an empty editor | ok | 267 |
| 1150 | practice | s03.001: run the untouched starter | ok | 296 |
| 1151 | practice | s03.001: run the reference solution | ok | 322 |
| 1152 | practice | s03.001: read the solution once passed | ok | 43 |
| 1153 | practice | s03.002: read the brief | ok | 0 |
| 1154 | practice | s03.002: reveal every hint | ok | 53 |
| 1155 | practice | s03.002: run an empty editor | ok | 320 |
| 1156 | practice | s03.002: run the untouched starter | ok | 260 |
| 1157 | practice | s03.002: run the reference solution | ok | 337 |
| 1158 | practice | s03.002: read the solution once passed | ok | 38 |
| 1159 | practice | s03.003: read the brief | ok | 0 |
| 1160 | practice | s03.003: reveal every hint | ok | 46 |
| 1161 | practice | s03.003: run an empty editor | ok | 235 |
| 1162 | practice | s03.003: run the untouched starter | ok | 342 |
| 1163 | practice | s03.003: run the reference solution | ok | 298 |
| 1164 | practice | s03.003: read the solution once passed | ok | 39 |
| 1165 | practice | s04.001: read the brief | ok | 0 |
| 1166 | practice | s04.001: reveal every hint | ok | 52 |
| 1167 | practice | s04.001: run an empty editor | ok | 291 |
| 1168 | practice | s04.001: run the untouched starter | ok | 280 |
| 1169 | practice | s04.001: run the reference solution | ok | 307 |
| 1170 | practice | s04.001: read the solution once passed | ok | 38 |
| 1171 | practice | s04.002: read the brief | ok | 0 |
| 1172 | practice | s04.002: reveal every hint | ok | 56 |
| 1173 | practice | s04.002: run an empty editor | ok | 308 |
| 1174 | practice | s04.002: run the untouched starter | ok | 268 |
| 1175 | practice | s04.002: run the reference solution | ok | 299 |
| 1176 | practice | s04.002: read the solution once passed | ok | 42 |
| 1177 | practice | s04.003: read the brief | ok | 0 |
| 1178 | practice | s04.003: reveal every hint | ok | 97 |
| 1179 | practice | s04.003: run an empty editor | ok | 298 |
| 1180 | practice | s04.003: run the untouched starter | ok | 271 |
| 1181 | practice | s04.003: run the reference solution | ok | 368 |
| 1182 | practice | s04.003: read the solution once passed | ok | 37 |
| 1183 | practice | s05.001: read the brief | ok | 0 |
| 1184 | practice | s05.001: reveal every hint | ok | 53 |
| 1185 | practice | s05.001: run an empty editor | ok | 252 |
| 1186 | practice | s05.001: run the untouched starter | ok | 366 |
| 1187 | practice | s05.001: run the reference solution | ok | 275 |
| 1188 | practice | s05.001: read the solution once passed | ok | 37 |
| 1189 | practice | s05.002: read the brief | ok | 0 |
| 1190 | practice | s05.002: reveal every hint | ok | 59 |
| 1191 | practice | s05.002: run an empty editor | ok | 298 |
| 1192 | practice | s05.002: run the untouched starter | ok | 305 |
| 1193 | practice | s05.002: run the reference solution | ok | 268 |
| 1194 | practice | s05.002: read the solution once passed | ok | 72 |
| 1195 | practice | s05.003: read the brief | ok | 0 |
| 1196 | practice | s05.003: reveal every hint | ok | 124 |
| 1197 | practice | s05.003: run an empty editor | ok | 208 |
| 1198 | practice | s05.003: run the untouched starter | ok | 295 |
| 1199 | practice | s05.003: run the reference solution | ok | 238 |
| 1200 | practice | s05.003: read the solution once passed | ok | 36 |
| 1201 | practice | s06.001: read the brief | ok | 0 |
| 1202 | practice | s06.001: reveal every hint | ok | 53 |
| 1203 | practice | s06.001: run an empty editor | ok | 223 |
| 1204 | practice | s06.001: run the untouched starter | ok | 255 |
| 1205 | practice | s06.001: run the reference solution | ok | 317 |
| 1206 | practice | s06.001: read the solution once passed | ok | 45 |
| 1207 | practice | s06.002: read the brief | ok | 0 |
| 1208 | practice | s06.002: reveal every hint | ok | 63 |
| 1209 | practice | s06.002: run an empty editor | ok | 267 |
| 1210 | practice | s06.002: run the untouched starter | ok | 246 |
| 1211 | practice | s06.002: run the reference solution | ok | 265 |
| 1212 | practice | s06.002: read the solution once passed | ok | 31 |
| 1213 | practice | s06.003: read the brief | ok | 0 |
| 1214 | practice | s06.003: reveal every hint | ok | 54 |
| 1215 | practice | s06.003: run an empty editor | ok | 234 |
| 1216 | practice | s06.003: run the untouched starter | ok | 243 |
| 1217 | practice | s06.003: run the reference solution | ok | 220 |
| 1218 | practice | s06.003: read the solution once passed | ok | 36 |
| 1219 | practice | s07.001: read the brief | ok | 0 |
| 1220 | practice | s07.001: reveal every hint | ok | 56 |
| 1221 | practice | s07.001: run an empty editor | ok | 307 |
| 1222 | practice | s07.001: run the untouched starter | ok | 319 |
| 1223 | practice | s07.001: run the reference solution | ok | 337 |
| 1224 | practice | s07.001: read the solution once passed | ok | 39 |
| 1225 | practice | s07.002: read the brief | ok | 0 |
| 1226 | practice | s07.002: reveal every hint | ok | 64 |
| 1227 | practice | s07.002: run an empty editor | ok | 280 |
| 1228 | practice | s07.002: run the untouched starter | ok | 265 |
| 1229 | practice | s07.002: run the reference solution | ok | 265 |
| 1230 | practice | s07.002: read the solution once passed | ok | 38 |
| 1231 | practice | s07.003: read the brief | ok | 0 |
| 1232 | practice | s07.003: reveal every hint | ok | 51 |
| 1233 | practice | s07.003: run an empty editor | ok | 255 |
| 1234 | practice | s07.003: run the untouched starter | ok | 278 |
| 1235 | practice | s07.003: run the reference solution | ok | 355 |
| 1236 | practice | s07.003: read the solution once passed | ok | 67 |
| 1237 | practice | s08.001: read the brief | ok | 0 |
| 1238 | practice | s08.001: reveal every hint | ok | 94 |
| 1239 | practice | s08.001: run an empty editor | ok | 339 |
| 1240 | practice | s08.001: run the untouched starter | ok | 423 |
| 1241 | practice | s08.001: run the reference solution | ok | 302 |
| 1242 | practice | s08.001: read the solution once passed | ok | 36 |
| 1243 | practice | s08.002: read the brief | ok | 0 |
| 1244 | practice | s08.002: reveal every hint | ok | 53 |
| 1245 | practice | s08.002: run an empty editor | ok | 281 |
| 1246 | practice | s08.002: run the untouched starter | ok | 319 |
| 1247 | practice | s08.002: run the reference solution | ok | 293 |
| 1248 | practice | s08.002: read the solution once passed | ok | 34 |
| 1249 | practice | s08.003: read the brief | ok | 0 |
| 1250 | practice | s08.003: reveal every hint | ok | 57 |
| 1251 | practice | s08.003: run an empty editor | ok | 306 |
| 1252 | practice | s08.003: run the untouched starter | ok | 299 |
| 1253 | practice | s08.003: run the reference solution | ok | 295 |
| 1254 | practice | s08.003: read the solution once passed | ok | 48 |
| 1255 | practice | s09.001: read the brief | ok | 0 |
| 1256 | practice | s09.001: reveal every hint | ok | 63 |
| 1257 | practice | s09.001: run an empty editor | ok | 305 |
| 1258 | practice | s09.001: run the untouched starter | ok | 358 |
| 1259 | practice | s09.001: run the reference solution | ok | 279 |
| 1260 | practice | s09.001: read the solution once passed | ok | 43 |
| 1261 | practice | s09.002: read the brief | ok | 0 |
| 1262 | practice | s09.002: reveal every hint | ok | 58 |
| 1263 | practice | s09.002: run an empty editor | ok | 294 |
| 1264 | practice | s09.002: run the untouched starter | ok | 296 |
| 1265 | practice | s09.002: run the reference solution | ok | 264 |
| 1266 | practice | s09.002: read the solution once passed | ok | 50 |
| 1267 | practice | s09.003: read the brief | ok | 0 |
| 1268 | practice | s09.003: reveal every hint | ok | 70 |
| 1269 | practice | s09.003: run an empty editor | ok | 366 |
| 1270 | practice | s09.003: run the untouched starter | ok | 477 |
| 1271 | practice | s09.003: run the reference solution | ok | 327 |
| 1272 | practice | s09.003: read the solution once passed | ok | 40 |
| 1273 | practice | s10.001: read the brief | ok | 0 |
| 1274 | practice | s10.001: reveal every hint | ok | 60 |
| 1275 | practice | s10.001: run an empty editor | ok | 263 |
| 1276 | practice | s10.001: run the untouched starter | ok | 276 |
| 1277 | practice | s10.001: run the reference solution | ok | 343 |
| 1278 | practice | s10.001: read the solution once passed | ok | 47 |
| 1279 | practice | s10.002: read the brief | ok | 0 |
| 1280 | practice | s10.002: reveal every hint | ok | 61 |
| 1281 | practice | s10.002: run an empty editor | ok | 259 |
| 1282 | practice | s10.002: run the untouched starter | ok | 296 |
| 1283 | practice | s10.002: run the reference solution | ok | 256 |
| 1284 | practice | s10.002: read the solution once passed | ok | 38 |
| 1285 | practice | s10.003: read the brief | ok | 0 |
| 1286 | practice | s10.003: reveal every hint | ok | 60 |
| 1287 | practice | s10.003: run an empty editor | ok | 299 |
| 1288 | practice | s10.003: run the untouched starter | ok | 305 |
| 1289 | practice | s10.003: run the reference solution | ok | 297 |
| 1290 | practice | s10.003: read the solution once passed | ok | 48 |
| 1291 | practice | s11.001: read the brief | ok | 0 |
| 1292 | practice | s11.001: reveal every hint | ok | 71 |
| 1293 | practice | s11.001: run an empty editor | ok | 279 |
| 1294 | practice | s11.001: run the untouched starter | ok | 241 |
| 1295 | practice | s11.001: run the reference solution | ok | 279 |
| 1296 | practice | s11.001: read the solution once passed | ok | 37 |
| 1297 | practice | s11.002: read the brief | ok | 0 |
| 1298 | practice | s11.002: reveal every hint | ok | 53 |
| 1299 | practice | s11.002: run an empty editor | ok | 255 |
| 1300 | practice | s11.002: run the untouched starter | ok | 262 |
| 1301 | practice | s11.002: run the reference solution | ok | 264 |
| 1302 | practice | s11.002: read the solution once passed | ok | 38 |
| 1303 | practice | s11.003: read the brief | ok | 0 |
| 1304 | practice | s11.003: reveal every hint | ok | 68 |
| 1305 | practice | s11.003: run an empty editor | ok | 264 |
| 1306 | practice | s11.003: run the untouched starter | ok | 243 |
| 1307 | practice | s11.003: run the reference solution | ok | 247 |
| 1308 | practice | s11.003: read the solution once passed | ok | 38 |
| 1309 | practice | s12.001: read the brief | ok | 0 |
| 1310 | practice | s12.001: reveal every hint | ok | 58 |
| 1311 | practice | s12.001: run an empty editor | ok | 234 |
| 1312 | practice | s12.001: run the untouched starter | ok | 270 |
| 1313 | practice | s12.001: run the reference solution | ok | 372 |
| 1314 | practice | s12.001: read the solution once passed | ok | 44 |
| 1315 | practice | s12.002: read the brief | ok | 0 |
| 1316 | practice | s12.002: reveal every hint | ok | 65 |
| 1317 | practice | s12.002: run an empty editor | ok | 309 |
| 1318 | practice | s12.002: run the untouched starter | ok | 347 |
| 1319 | practice | s12.002: run the reference solution | ok | 253 |
| 1320 | practice | s12.002: read the solution once passed | ok | 39 |
| 1321 | practice | s12.003: read the brief | ok | 0 |
| 1322 | practice | s12.003: reveal every hint | ok | 51 |
| 1323 | practice | s12.003: run an empty editor | ok | 222 |
| 1324 | practice | s12.003: run the untouched starter | ok | 328 |
| 1325 | practice | s12.003: run the reference solution | ok | 289 |
| 1326 | practice | s12.003: read the solution once passed | ok | 41 |
| 1327 | practice | s13.001: read the brief | ok | 0 |
| 1328 | practice | s13.001: reveal every hint | ok | 52 |
| 1329 | practice | s13.001: run an empty editor | ok | 279 |
| 1330 | practice | s13.001: run the untouched starter | ok | 303 |
| 1331 | practice | s13.001: run the reference solution | ok | 232 |
| 1332 | practice | s13.001: read the solution once passed | ok | 42 |
| 1333 | practice | s13.002: read the brief | ok | 0 |
| 1334 | practice | s13.002: reveal every hint | ok | 91 |
| 1335 | practice | s13.002: run an empty editor | ok | 297 |
| 1336 | practice | s13.002: run the untouched starter | ok | 328 |
| 1337 | practice | s13.002: run the reference solution | ok | 285 |
| 1338 | practice | s13.002: read the solution once passed | ok | 37 |
| 1339 | practice | s13.003: read the brief | ok | 0 |
| 1340 | practice | s13.003: reveal every hint | ok | 56 |
| 1341 | practice | s13.003: run an empty editor | ok | 274 |
| 1342 | practice | s13.003: run the untouched starter | ok | 274 |
| 1343 | practice | s13.003: run the reference solution | ok | 240 |
| 1344 | practice | s13.003: read the solution once passed | ok | 38 |
| 1345 | practice | s14.001: read the brief | ok | 0 |
| 1346 | practice | s14.001: reveal every hint | ok | 77 |
| 1347 | practice | s14.001: run an empty editor | ok | 235 |
| 1348 | practice | s14.001: run the untouched starter | ok | 292 |
| 1349 | practice | s14.001: run the reference solution | ok | 329 |
| 1350 | practice | s14.001: read the solution once passed | ok | 38 |
| 1351 | practice | s14.002: read the brief | ok | 0 |
| 1352 | practice | s14.002: reveal every hint | ok | 60 |
| 1353 | practice | s14.002: run an empty editor | ok | 250 |
| 1354 | practice | s14.002: run the untouched starter | ok | 360 |
| 1355 | practice | s14.002: run the reference solution | ok | 249 |
| 1356 | practice | s14.002: read the solution once passed | ok | 40 |
| 1357 | practice | s14.003: read the brief | ok | 0 |
| 1358 | practice | s14.003: reveal every hint | ok | 77 |
| 1359 | practice | s14.003: run an empty editor | ok | 293 |
| 1360 | practice | s14.003: run the untouched starter | ok | 327 |
| 1361 | practice | s14.003: run the reference solution | ok | 377 |
| 1362 | practice | s14.003: read the solution once passed | ok | 58 |
| 1363 | practice | the counter agrees with the store | ok | 0 |
| 1364 | practice | press Run checks and read the result | ok | 258 |
| 1365 | practice | close the window while a run is in flight | ok | 12103 |
| 1366 | quiz | read the quiz picker | ok | 0 |
| 1367 | quiz | answer all 8 questions in q00 correctly | ok | 529 |
| 1368 | quiz | answer all 18 questions in q01 correctly | ok | 1303 |
| 1369 | quiz | answer all 11 questions in q02 correctly | ok | 781 |
| 1370 | quiz | answer all 8 questions in q03 correctly | ok | 584 |
| 1371 | quiz | answer all 18 questions in q04 correctly | ok | 1346 |
| 1372 | quiz | answer all 12 questions in q05 correctly | ok | 861 |
| 1373 | quiz | answer all 12 questions in q06 correctly | ok | 903 |
| 1374 | quiz | answer all 13 questions in q07 correctly | ok | 850 |
| 1375 | quiz | answer all 14 questions in q08 correctly | ok | 940 |
| 1376 | quiz | answer all 13 questions in q09 correctly | ok | 908 |
| 1377 | quiz | answer all 12 questions in q10 correctly | ok | 879 |
| 1378 | quiz | answer all 10 questions in q11 correctly | ok | 685 |
| 1379 | quiz | answer all 8 questions in q12 correctly | ok | 539 |
| 1380 | quiz | answer all 9 questions in q13 correctly | ok | 610 |
| 1381 | quiz | answer all 10 questions in q14 correctly | ok | 698 |
| 1382 | quiz | answer all 18 questions in q15 correctly | ok | 1358 |
| 1383 | quiz | answer all 18 questions in q16 correctly | ok | 1455 |
| 1384 | quiz | answer all 14 questions in q17 correctly | ok | 1017 |
| 1385 | quiz | answer all 8 questions in q18 correctly | ok | 579 |
| 1386 | quiz | answer all 8 questions in q99 correctly | ok | 580 |
| 1387 | quiz | answer all 8 questions in q20 correctly | ok | 541 |
| 1388 | quiz | answer all 8 questions in q21 correctly | ok | 540 |
| 1389 | quiz | answer all 8 questions in q22 correctly | ok | 580 |
| 1390 | quiz | answer all 8 questions in q23 correctly | ok | 529 |
| 1391 | quiz | answer all 8 questions in q24 correctly | ok | 502 |
| 1392 | quiz | answer all 8 questions in q25 correctly | ok | 511 |
| 1393 | quiz | answer all 8 questions in q26 correctly | ok | 551 |
| 1394 | quiz | answer all 8 questions in q27 correctly | ok | 677 |
| 1395 | quiz | answer all 8 questions in q28 correctly | ok | 545 |
| 1396 | quiz | answer all 8 questions in q29 correctly | ok | 579 |
| 1397 | quiz | answer all 8 questions in q30 correctly | ok | 529 |
| 1398 | quiz | answer all 8 questions in q31 correctly | ok | 569 |
| 1399 | quiz | answer all 8 questions in q32 correctly | ok | 561 |
| 1400 | quiz | answer all 8 questions in q33 correctly | ok | 555 |
| 1401 | quiz | get every question in q00 wrong | ok | 860 |
| 1402 | quiz | read the wrap-up for q00 | ok | 1 |
| 1403 | quiz | get every question in q01 wrong | ok | 2205 |
| 1404 | quiz | read the wrap-up for q01 | ok | 1 |
| 1405 | quiz | get every question in q02 wrong | ok | 1075 |
| 1406 | quiz | read the wrap-up for q02 | ok | 1 |
| 1407 | quiz | get every question in q03 wrong | ok | 763 |
| 1408 | quiz | read the wrap-up for q03 | ok | 1 |
| 1409 | quiz | get every question in q04 wrong | ok | 1581 |
| 1410 | quiz | read the wrap-up for q04 | ok | 1 |
| 1411 | quiz | get every question in q05 wrong | ok | 1083 |
| 1412 | quiz | read the wrap-up for q05 | ok | 1 |
| 1413 | quiz | get every question in q06 wrong | ok | 1074 |
| 1414 | quiz | read the wrap-up for q06 | ok | 1 |
| 1415 | quiz | get every question in q07 wrong | ok | 1152 |
| 1416 | quiz | read the wrap-up for q07 | ok | 1 |
| 1417 | quiz | get every question in q08 wrong | ok | 1293 |
| 1418 | quiz | read the wrap-up for q08 | ok | 1 |
| 1419 | quiz | get every question in q09 wrong | ok | 1175 |
| 1420 | quiz | read the wrap-up for q09 | ok | 1 |
| 1421 | quiz | get every question in q10 wrong | ok | 1066 |
| 1422 | quiz | read the wrap-up for q10 | ok | 3 |
| 1423 | quiz | get every question in q11 wrong | ok | 939 |
| 1424 | quiz | read the wrap-up for q11 | ok | 1 |
| 1425 | quiz | get every question in q12 wrong | ok | 700 |
| 1426 | quiz | read the wrap-up for q12 | ok | 0 |
| 1427 | quiz | get every question in q13 wrong | ok | 819 |
| 1428 | quiz | read the wrap-up for q13 | ok | 1 |
| 1429 | quiz | get every question in q14 wrong | ok | 849 |
| 1430 | quiz | read the wrap-up for q14 | ok | 0 |
| 1431 | quiz | get every question in q15 wrong | ok | 1568 |
| 1432 | quiz | read the wrap-up for q15 | ok | 1 |
| 1433 | quiz | get every question in q16 wrong | ok | 1570 |
| 1434 | quiz | read the wrap-up for q16 | ok | 1 |
| 1435 | quiz | get every question in q17 wrong | ok | 1367 |
| 1436 | quiz | read the wrap-up for q17 | ok | 1 |
| 1437 | quiz | get every question in q18 wrong | ok | 700 |
| 1438 | quiz | read the wrap-up for q18 | ok | 0 |
| 1439 | quiz | get every question in q99 wrong | ok | 747 |
| 1440 | quiz | read the wrap-up for q99 | ok | 1 |
| 1441 | quiz | get every question in q20 wrong | ok | 659 |
| 1442 | quiz | read the wrap-up for q20 | ok | 0 |
| 1443 | quiz | get every question in q21 wrong | ok | 640 |
| 1444 | quiz | read the wrap-up for q21 | ok | 1 |
| 1445 | quiz | get every question in q22 wrong | ok | 627 |
| 1446 | quiz | read the wrap-up for q22 | ok | 1 |
| 1447 | quiz | get every question in q23 wrong | ok | 748 |
| 1448 | quiz | read the wrap-up for q23 | ok | 0 |
| 1449 | quiz | get every question in q24 wrong | ok | 688 |
| 1450 | quiz | read the wrap-up for q24 | ok | 0 |
| 1451 | quiz | get every question in q25 wrong | ok | 659 |
| 1452 | quiz | read the wrap-up for q25 | ok | 1 |
| 1453 | quiz | get every question in q26 wrong | ok | 679 |
| 1454 | quiz | read the wrap-up for q26 | ok | 1 |
| 1455 | quiz | get every question in q27 wrong | ok | 707 |
| 1456 | quiz | read the wrap-up for q27 | ok | 1 |
| 1457 | quiz | get every question in q28 wrong | ok | 724 |
| 1458 | quiz | read the wrap-up for q28 | ok | 0 |
| 1459 | quiz | get every question in q29 wrong | ok | 703 |
| 1460 | quiz | read the wrap-up for q29 | ok | 0 |
| 1461 | quiz | get every question in q30 wrong | ok | 725 |
| 1462 | quiz | read the wrap-up for q30 | ok | 0 |
| 1463 | quiz | get every question in q31 wrong | ok | 767 |
| 1464 | quiz | read the wrap-up for q31 | ok | 0 |
| 1465 | quiz | get every question in q32 wrong | ok | 653 |
| 1466 | quiz | read the wrap-up for q32 | ok | 1 |
| 1467 | quiz | get every question in q33 wrong | ok | 625 |
| 1468 | quiz | read the wrap-up for q33 | ok | 0 |
| 1469 | review | the wrong answers are waiting in review | ok | 14 |
| 1470 | quiz | skip every question without answering | ok | 640 |
| 1471 | quiz | retake it | ok | 71 |
| 1472 | quiz | go back to the picker | ok | 290 |
| 1473 | review | open Review with nothing started | ok | 0 |
| 1474 | review | answer card 1 of 15 | ok | 76 |
| 1475 | review | answer card 2 of 15 | ok | 139 |
| 1476 | review | answer card 3 of 15 | ok | 104 |
| 1477 | review | answer card 4 of 15 | ok | 89 |
| 1478 | review | answer card 5 of 15 | ok | 84 |
| 1479 | review | answer card 6 of 15 | ok | 79 |
| 1480 | review | answer card 7 of 15 | ok | 120 |
| 1481 | review | answer card 8 of 15 | ok | 159 |
| 1482 | review | answer card 9 of 15 | ok | 75 |
| 1483 | review | answer card 10 of 15 | ok | 106 |
| 1484 | review | answer card 11 of 15 | ok | 86 |
| 1485 | review | answer card 12 of 15 | ok | 80 |
| 1486 | review | answer card 13 of 15 | ok | 68 |
| 1487 | review | answer card 14 of 15 | ok | 77 |
| 1488 | review | answer card 15 of 15 | ok | 76 |
| 1489 | review | the session ends with a clear queue | ok | 0 |
| 1490 | review | skip the card in front of you | ok | 24 |
| 1491 | review | work to the daily limit | ok | 222 |
| 1492 | review | the idle screen explains the limit | ok | 0 |
| 1493 | review | open Review with a thousand cards due | ok | 80 |
| 1494 | projects | read all 36 project cards | ok | 4 |
| 1495 | projects | meet every requirement of pj.p00.1 | ok | 174 |
| 1496 | projects | meet every requirement of pj.p01.1 | ok | 119 |
| 1497 | projects | meet every requirement of pj.p01.2 | ok | 102 |
| 1498 | projects | meet every requirement of pj.p02.1 | ok | 120 |
| 1499 | projects | meet every requirement of pj.p02.2 | ok | 125 |
| 1500 | projects | meet every requirement of pj.p03.1 | ok | 125 |
| 1501 | projects | meet every requirement of pj.p04.1 | ok | 106 |
| 1502 | projects | meet every requirement of pj.p05.1 | ok | 130 |
| 1503 | projects | meet every requirement of pj.p06.1 | ok | 161 |
| 1504 | projects | meet every requirement of pj.p07.1 | ok | 140 |
| 1505 | projects | meet every requirement of pj.p08.1 | ok | 125 |
| 1506 | projects | meet every requirement of pj.p09.1 | ok | 147 |
| 1507 | projects | meet every requirement of pj.p10.1 | ok | 158 |
| 1508 | projects | meet every requirement of pj.p11.1 | ok | 142 |
| 1509 | projects | meet every requirement of pj.p12.1 | ok | 159 |
| 1510 | projects | meet every requirement of pj.p13.1 | ok | 137 |
| 1511 | projects | meet every requirement of pj.p14.1 | ok | 141 |
| 1512 | projects | meet every requirement of pj.p14.2 | ok | 122 |
| 1513 | projects | meet every requirement of pj.p15.1 | ok | 148 |
| 1514 | projects | meet every requirement of pj.p16.1 | ok | 134 |
| 1515 | projects | meet every requirement of pj.p17.1 | ok | 134 |
| 1516 | projects | meet every requirement of pj.p99.1 | ok | 136 |
| 1517 | projects | meet every requirement of pj.s01.1 | ok | 128 |
| 1518 | projects | meet every requirement of pj.s02.1 | ok | 109 |
| 1519 | projects | meet every requirement of pj.s03.1 | ok | 93 |
| 1520 | projects | meet every requirement of pj.s04.1 | ok | 96 |
| 1521 | projects | meet every requirement of pj.s05.1 | ok | 89 |
| 1522 | projects | meet every requirement of pj.s06.1 | ok | 106 |
| 1523 | projects | meet every requirement of pj.s07.1 | ok | 85 |
| 1524 | projects | meet every requirement of pj.s08.1 | ok | 86 |
| 1525 | projects | meet every requirement of pj.s09.1 | ok | 96 |
| 1526 | projects | meet every requirement of pj.s10.1 | ok | 155 |
| 1527 | projects | meet every requirement of pj.s11.1 | ok | 109 |
| 1528 | projects | meet every requirement of pj.s12.1 | ok | 108 |
| 1529 | projects | meet every requirement of pj.s13.1 | ok | 114 |
| 1530 | projects | meet every requirement of pj.s14.1 | ok | 110 |
| 1531 | projects | the meters agree once everything is met | ok | 16 |
| 1532 | projects | untick pj.p00.1 again | ok | 119 |
| 1533 | projects | untick pj.p01.1 again | ok | 142 |
| 1534 | projects | untick pj.p01.2 again | ok | 131 |
| 1535 | projects | untick pj.p02.1 again | ok | 158 |
| 1536 | projects | untick pj.p02.2 again | ok | 122 |
| 1537 | projects | untick pj.p03.1 again | ok | 142 |
| 1538 | projects | untick pj.p04.1 again | ok | 129 |
| 1539 | projects | untick pj.p05.1 again | ok | 129 |
| 1540 | projects | untick pj.p06.1 again | ok | 143 |
| 1541 | projects | untick pj.p07.1 again | ok | 137 |
| 1542 | projects | untick pj.p08.1 again | ok | 138 |
| 1543 | projects | untick pj.p09.1 again | ok | 182 |
| 1544 | projects | untick pj.p10.1 again | ok | 149 |
| 1545 | projects | untick pj.p11.1 again | ok | 140 |
| 1546 | projects | untick pj.p12.1 again | ok | 153 |
| 1547 | projects | untick pj.p13.1 again | ok | 137 |
| 1548 | projects | untick pj.p14.1 again | ok | 141 |
| 1549 | projects | untick pj.p14.2 again | ok | 135 |
| 1550 | projects | untick pj.p15.1 again | ok | 164 |
| 1551 | projects | untick pj.p16.1 again | ok | 123 |
| 1552 | projects | untick pj.p17.1 again | ok | 134 |
| 1553 | projects | untick pj.p99.1 again | ok | 125 |
| 1554 | projects | untick pj.s01.1 again | ok | 115 |
| 1555 | projects | untick pj.s02.1 again | ok | 79 |
| 1556 | projects | untick pj.s03.1 again | ok | 90 |
| 1557 | projects | untick pj.s04.1 again | ok | 88 |
| 1558 | projects | untick pj.s05.1 again | ok | 64 |
| 1559 | projects | untick pj.s06.1 again | ok | 101 |
| 1560 | projects | untick pj.s07.1 again | ok | 60 |
| 1561 | projects | untick pj.s08.1 again | ok | 66 |
| 1562 | projects | untick pj.s09.1 again | ok | 66 |
| 1563 | projects | untick pj.s10.1 again | ok | 108 |
| 1564 | projects | untick pj.s11.1 again | ok | 55 |
| 1565 | projects | untick pj.s12.1 again | ok | 63 |
| 1566 | projects | untick pj.s13.1 again | ok | 67 |
| 1567 | projects | untick pj.s14.1 again | ok | 65 |
| 1568 | projects | mark pj.p00.1 as Not started | ok | 79 |
| 1569 | projects | mark pj.p00.1 as In progress | ok | 25 |
| 1570 | projects | mark pj.p00.1 as Shipped | ok | 39 |
| 1571 | projects | mark pj.p01.1 as Not started | ok | 32 |
| 1572 | projects | mark pj.p01.1 as In progress | ok | 38 |
| 1573 | projects | mark pj.p01.1 as Shipped | ok | 34 |
| 1574 | projects | mark pj.p01.2 as Not started | ok | 24 |
| 1575 | projects | mark pj.p01.2 as In progress | ok | 33 |
| 1576 | projects | mark pj.p01.2 as Shipped | ok | 32 |
| 1577 | projects | mark pj.p02.1 as Not started | ok | 38 |
| 1578 | projects | mark pj.p02.1 as In progress | ok | 25 |
| 1579 | projects | mark pj.p02.1 as Shipped | ok | 30 |
| 1580 | projects | mark pj.p02.2 as Not started | ok | 25 |
| 1581 | projects | mark pj.p02.2 as In progress | ok | 30 |
| 1582 | projects | mark pj.p02.2 as Shipped | ok | 31 |
| 1583 | projects | mark pj.p03.1 as Not started | ok | 28 |
| 1584 | projects | mark pj.p03.1 as In progress | ok | 28 |
| 1585 | projects | mark pj.p03.1 as Shipped | ok | 33 |
| 1586 | projects | mark pj.p04.1 as Not started | ok | 22 |
| 1587 | projects | mark pj.p04.1 as In progress | ok | 25 |
| 1588 | projects | mark pj.p04.1 as Shipped | ok | 30 |
| 1589 | projects | mark pj.p05.1 as Not started | ok | 22 |
| 1590 | projects | mark pj.p05.1 as In progress | ok | 25 |
| 1591 | projects | mark pj.p05.1 as Shipped | ok | 28 |
| 1592 | projects | mark pj.p06.1 as Not started | ok | 29 |
| 1593 | projects | mark pj.p06.1 as In progress | ok | 26 |
| 1594 | projects | mark pj.p06.1 as Shipped | ok | 32 |
| 1595 | projects | mark pj.p07.1 as Not started | ok | 25 |
| 1596 | projects | mark pj.p07.1 as In progress | ok | 27 |
| 1597 | projects | mark pj.p07.1 as Shipped | ok | 29 |
| 1598 | projects | mark pj.p08.1 as Not started | ok | 24 |
| 1599 | projects | mark pj.p08.1 as In progress | ok | 25 |
| 1600 | projects | mark pj.p08.1 as Shipped | ok | 31 |
| 1601 | projects | mark pj.p09.1 as Not started | ok | 24 |
| 1602 | projects | mark pj.p09.1 as In progress | ok | 27 |
| 1603 | projects | mark pj.p09.1 as Shipped | ok | 29 |
| 1604 | projects | mark pj.p10.1 as Not started | ok | 25 |
| 1605 | projects | mark pj.p10.1 as In progress | ok | 26 |
| 1606 | projects | mark pj.p10.1 as Shipped | ok | 30 |
| 1607 | projects | mark pj.p11.1 as Not started | ok | 25 |
| 1608 | projects | mark pj.p11.1 as In progress | ok | 26 |
| 1609 | projects | mark pj.p11.1 as Shipped | ok | 29 |
| 1610 | projects | mark pj.p12.1 as Not started | ok | 25 |
| 1611 | projects | mark pj.p12.1 as In progress | ok | 26 |
| 1612 | projects | mark pj.p12.1 as Shipped | ok | 30 |
| 1613 | projects | mark pj.p13.1 as Not started | ok | 27 |
| 1614 | projects | mark pj.p13.1 as In progress | ok | 27 |
| 1615 | projects | mark pj.p13.1 as Shipped | ok | 33 |
| 1616 | projects | mark pj.p14.1 as Not started | ok | 28 |
| 1617 | projects | mark pj.p14.1 as In progress | ok | 36 |
| 1618 | projects | mark pj.p14.1 as Shipped | ok | 32 |
| 1619 | projects | mark pj.p14.2 as Not started | ok | 26 |
| 1620 | projects | mark pj.p14.2 as In progress | ok | 30 |
| 1621 | projects | mark pj.p14.2 as Shipped | ok | 28 |
| 1622 | projects | mark pj.p15.1 as Not started | ok | 28 |
| 1623 | projects | mark pj.p15.1 as In progress | ok | 27 |
| 1624 | projects | mark pj.p15.1 as Shipped | ok | 30 |
| 1625 | projects | mark pj.p16.1 as Not started | ok | 25 |
| 1626 | projects | mark pj.p16.1 as In progress | ok | 28 |
| 1627 | projects | mark pj.p16.1 as Shipped | ok | 29 |
| 1628 | projects | mark pj.p17.1 as Not started | ok | 23 |
| 1629 | projects | mark pj.p17.1 as In progress | ok | 28 |
| 1630 | projects | mark pj.p17.1 as Shipped | ok | 29 |
| 1631 | projects | mark pj.p99.1 as Not started | ok | 24 |
| 1632 | projects | mark pj.p99.1 as In progress | ok | 26 |
| 1633 | projects | mark pj.p99.1 as Shipped | ok | 32 |
| 1634 | projects | mark pj.s01.1 as Not started | ok | 29 |
| 1635 | projects | mark pj.s01.1 as In progress | ok | 26 |
| 1636 | projects | mark pj.s01.1 as Shipped | ok | 25 |
| 1637 | projects | mark pj.s02.1 as Not started | ok | 25 |
| 1638 | projects | mark pj.s02.1 as In progress | ok | 26 |
| 1639 | projects | mark pj.s02.1 as Shipped | ok | 28 |
| 1640 | projects | mark pj.s03.1 as Not started | ok | 25 |
| 1641 | projects | mark pj.s03.1 as In progress | ok | 27 |
| 1642 | projects | mark pj.s03.1 as Shipped | ok | 25 |
| 1643 | projects | mark pj.s04.1 as Not started | ok | 25 |
| 1644 | projects | mark pj.s04.1 as In progress | ok | 26 |
| 1645 | projects | mark pj.s04.1 as Shipped | ok | 27 |
| 1646 | projects | mark pj.s05.1 as Not started | ok | 35 |
| 1647 | projects | mark pj.s05.1 as In progress | ok | 26 |
| 1648 | projects | mark pj.s05.1 as Shipped | ok | 29 |
| 1649 | projects | mark pj.s06.1 as Not started | ok | 26 |
| 1650 | projects | mark pj.s06.1 as In progress | ok | 26 |
| 1651 | projects | mark pj.s06.1 as Shipped | ok | 30 |
| 1652 | projects | mark pj.s07.1 as Not started | ok | 23 |
| 1653 | projects | mark pj.s07.1 as In progress | ok | 26 |
| 1654 | projects | mark pj.s07.1 as Shipped | ok | 26 |
| 1655 | projects | mark pj.s08.1 as Not started | ok | 27 |
| 1656 | projects | mark pj.s08.1 as In progress | ok | 29 |
| 1657 | projects | mark pj.s08.1 as Shipped | ok | 25 |
| 1658 | projects | mark pj.s09.1 as Not started | ok | 29 |
| 1659 | projects | mark pj.s09.1 as In progress | ok | 27 |
| 1660 | projects | mark pj.s09.1 as Shipped | ok | 33 |
| 1661 | projects | mark pj.s10.1 as Not started | ok | 25 |
| 1662 | projects | mark pj.s10.1 as In progress | ok | 27 |
| 1663 | projects | mark pj.s10.1 as Shipped | ok | 26 |
| 1664 | projects | mark pj.s11.1 as Not started | ok | 26 |
| 1665 | projects | mark pj.s11.1 as In progress | ok | 26 |
| 1666 | projects | mark pj.s11.1 as Shipped | ok | 28 |
| 1667 | projects | mark pj.s12.1 as Not started | ok | 25 |
| 1668 | projects | mark pj.s12.1 as In progress | ok | 25 |
| 1669 | projects | mark pj.s12.1 as Shipped | ok | 29 |
| 1670 | projects | mark pj.s13.1 as Not started | ok | 25 |
| 1671 | projects | mark pj.s13.1 as In progress | ok | 25 |
| 1672 | projects | mark pj.s13.1 as Shipped | ok | 27 |
| 1673 | projects | mark pj.s14.1 as Not started | ok | 26 |
| 1674 | projects | mark pj.s14.1 as In progress | ok | 28 |
| 1675 | projects | mark pj.s14.1 as Shipped | ok | 26 |
| 1676 | projects | try each filter | ok | 545 |
| 1677 | projects | record a repo and some notes | ok | 523 |
| 1678 | projects | press Open next to the repo | ok | 3 |
| 1679 | projects | jump to the project's phase | ok | 255 |
| 1680 | projects | ship all 36 projects | ok | 710 |
| 1681 | today | Today agrees | ok | 99 |
| 1682 | projects | press a status button | 46 ms | 46 |
| 1683 | journal | write today's entry | ok | 50 |
| 1684 | journal | add three more days | ok | 250 |
| 1685 | journal | an entry is edited by writing it again | ok | 89 |
| 1686 | journal | delete every entry from the history | ok | 323 |
| 1687 | stats | the charts render with no data at all | ok | 10 |
| 1688 | stats | the charts render with one data point | ok | 244 |
| 1689 | stats | the charts render with a year of data | ok | 239 |
| 1690 | stats | rate every skill in the matrix | ok | 25 |
| 1691 | stats | the table covers the whole plan | ok | 246 |
| 1692 | library | open the Shelf tab | ok | 73 |
| 1693 | library | open the Fields of work tab | ok | 173 |
| 1694 | library | open the Video tab | ok | 119 |
| 1695 | library | open the Certificates tab | ok | 111 |
| 1696 | library | press every Open on the Shelf tab | ok | 16 |
| 1697 | library | press every Open on the Fields of work tab | ok | 0 |
| 1698 | library | press every Open on the Video tab | ok | 11 |
| 1699 | library | press every Open on the Certificates tab | ok | 0 |
| 1700 | library | press every field library button | ok | 105 |
| 1701 | library | cycle c-cs50p through every state | ok | 1748 |
| 1702 | library | cycle c-helsinki through every state | ok | 1252 |
| 1703 | library | cycle c-fcc-sci through every state | ok | 1304 |
| 1704 | library | cycle c-netacad1 through every state | ok | 1319 |
| 1705 | library | cycle c-netacad2 through every state | ok | 1369 |
| 1706 | library | cycle c-pcep through every state | ok | 1316 |
| 1707 | library | cycle c-pcap through every state | ok | 1256 |
| 1708 | library | cycle c-hackerrank through every state | ok | 1373 |
| 1709 | library | cycle c-kaggle through every state | ok | 1397 |
| 1710 | library | cycle c-fcc-data through every state | ok | 1346 |
| 1711 | library | cycle c-fcc-ml through every state | ok | 1248 |
| 1712 | library | cycle c-hf-agents through every state | ok | 1384 |
| 1713 | library | cycle c-hf-llm through every state | ok | 1326 |
| 1714 | library | cycle c-hf-mcp through every state | ok | 1333 |
| 1715 | library | cycle c-anthropic through every state | ok | 1312 |
| 1716 | library | cycle c-google-ml through every state | ok | 1356 |
| 1717 | library | cycle c-mit191 through every state | ok | 1258 |
| 1718 | library | cycle c-cs50ai through every state | ok | 1223 |
| 1719 | library | cycle c-cs50w through every state | ok | 1320 |
| 1720 | library | cycle c-google-auto through every state | ok | 1373 |
| 1721 | library | cycle c-py4e through every state | ok | 1319 |
| 1722 | library | cycle c-mlzoom through every state | ok | 1335 |
| 1723 | library | cycle c-dezoom through every state | ok | 1258 |
| 1724 | library | cycle c-mit6001 through every state | ok | 1503 |
| 1725 | settings | change your name | ok | 15 |
| 1726 | settings | try every track | ok | 210 |
| 1727 | settings | try every experience level | ok | 29 |
| 1728 | settings | tick and untick every goal | ok | 519 |
| 1729 | settings | push every number to both ends | ok | 92 |
| 1730 | settings | turn the update check off and on | ok | 18 |
| 1731 | settings | put every setting back | ok | 49 |
| 1732 | settings | switch the theme to Dark | ok | 1137 |
| 1733 | settings | switch the theme to Light | ok | 982 |
| 1734 | settings | switch the theme to Match the system | ok | 10 |
| 1735 | settings | press Open folder | ok | 5 |
| 1736 | settings | export a backup | ok | 7 |
| 1737 | settings | export a progress report | ok | 29 |
| 1738 | settings | take a snapshot | ok | 18 |
| 1739 | settings | cancel an import | ok | 0 |
| 1740 | settings | import the backup back | ok | 0 |
| 1741 | settings | decline a reset | ok | 1 |
| 1742 | settings | accept a reset | ok | 0 |
| 1743 | settings | press Check now | ok | 3 |
| 1744 | search | open search with Ctrl+K | ok | 2 |
| 1745 | search | search for 'nothing' | ok | 0 |
| 1746 | search | search for 'd' | ok | 1 |
| 1747 | search | search for 'Python engineering' | ok | 17 |
| 1748 | search | search for 'Say hello' | ok | 7 |
| 1749 | search | search for 'zzzqqqxx nothing at all' | ok | 4 |
| 1750 | search | press Escape | ok | 13 |
| 1751 | search | press Enter on the first result | ok | 144 |
| 1752 | search | open a result of every kind | ok | 1223 |
| 1753 | history | nothing to undo on a fresh store | ok | 0 |
| 1754 | history | tick a line, then undo and redo it | ok | 823 |
| 1755 | history | change a project status, then undo it | ok | 2802 |
| 1756 | history | rate a skill, then undo it | ok | 494 |
| 1757 | history | cycle a certificate, then undo it | ok | 2673 |
| 1758 | history | undo and redo from the keyboard | ok | 1393 |
| 1759 | history | a new change drops the redo branch | ok | 389 |
| 1760 | history | reopen the app and look for the undo | ok | 0 |
| 1761 | history | the tick survived, the undo did not | ok | 0 |
| 1762 | updates | the button is hidden until there is one | ok | 0 |
| 1763 | updates | a release makes the button appear | ok | 3 |
| 1764 | updates | press it for a release with no changelog | ok | 1 |
| 1765 | updates | press it for a release with a changelog | ok | 20 |
| 1766 | updates | a release with nothing for this platform | ok | 5 |
| 1767 | updates | Help > Check for updates | ok | 3 |
| 1768 | restart | reopen the app on the same store | ok | 0 |
| 1769 | restart | the position is remembered | ok | 0 |
| 1770 | restart | quit inside the autosave window | ok | 3022 |
| 1771 | history | Ctrl+Z undoes a tick | ok | 342 |
| 1772 | history | the advertised redo keys | ok | 302 |
| 1773 | history | the Redo button still works | ok | 0 |
| 1774 | today | Today at 800x600 | ok | 0 |
| 1775 | roadmap | Roadmap at 800x600 | ok | 0 |
| 1776 | phase | Phase at 800x600 | ok | 1 |
| 1777 | practice | Practice at 800x600 | ok | 0 |
| 1778 | quiz | Quizzes at 800x600 | ok | 1 |
| 1779 | review | Review at 800x600 | ok | 0 |
| 1780 | projects | Projects at 800x600 | ok | 9 |
| 1781 | journal | Log at 800x600 | ok | 1 |
| 1782 | stats | Progress at 800x600 | ok | 1 |
| 1783 | library | Library at 800x600 | ok | 3 |
| 1784 | settings | Settings at 800x600 | ok | 1 |
| 1785 | today | Today at 1280x900 | ok | 0 |
| 1786 | roadmap | Roadmap at 1280x900 | ok | 0 |
| 1787 | phase | Phase at 1280x900 | ok | 1 |
| 1788 | practice | Practice at 1280x900 | ok | 0 |
| 1789 | quiz | Quizzes at 1280x900 | ok | 0 |
| 1790 | review | Review at 1280x900 | ok | 0 |
| 1791 | projects | Projects at 1280x900 | ok | 9 |
| 1792 | journal | Log at 1280x900 | ok | 0 |
| 1793 | stats | Progress at 1280x900 | ok | 1 |
| 1794 | library | Library at 1280x900 | ok | 3 |
| 1795 | settings | Settings at 1280x900 | ok | 0 |
| 1796 | today | Today at 2560x1440 | ok | 0 |
| 1797 | roadmap | Roadmap at 2560x1440 | ok | 0 |
| 1798 | phase | Phase at 2560x1440 | ok | 1 |
| 1799 | practice | Practice at 2560x1440 | ok | 0 |
| 1800 | quiz | Quizzes at 2560x1440 | ok | 0 |
| 1801 | review | Review at 2560x1440 | ok | 0 |
| 1802 | projects | Projects at 2560x1440 | ok | 9 |
| 1803 | journal | Log at 2560x1440 | ok | 0 |
| 1804 | stats | Progress at 2560x1440 | ok | 1 |
| 1805 | library | Library at 2560x1440 | ok | 2 |
| 1806 | settings | Settings at 2560x1440 | ok | 1 |
| 1807 | layout | the window refuses to go below its minimum | ok | 0 |
| 1808 | layout | the sidebar keeps every page button | ok | 0 |
| 1809 | today | tab through the today page | ok | 193 |
| 1810 | today | the focused control is the one you can see | ok | 0 |
| 1811 | practice | tab through the practice page | ok | 500 |
| 1812 | practice | the focused control is the one you can see | ok | 0 |
| 1813 | phase | tick a line with the space bar | ok | 36 |
| 1814 | practice | Ctrl+Enter in the editor runs the code | ok | 306 |
| 1815 | settings | type 2,5 hours in a German locale | ok | 12 |
| 1816 | settings | type it by hand as 3,5 | ok | 10 |
| 1817 | today | the pace line still reads sensibly | ok | 92 |
| 1818 | library | open library with nothing to show | ok | 30 |
| 1819 | stats | open stats with nothing to show | ok | 94 |
| 1820 | projects | open projects with nothing to show | ok | 26 |
| 1821 | today | open today with nothing to show | ok | 81 |
| 1822 | roadmap | open roadmap with nothing to show | ok | 375 |
| 1823 | navigation | switch pages 200 times | ok | 4633 |
| 1824 | today | reopen the Today page | 2 ms | 2 |
| 1825 | roadmap | reopen the Roadmap page | 33 ms | 33 |
| 1826 | phase | reopen the Phase page | 20 ms | 20 |
| 1827 | practice | reopen the Practice page | 44 ms | 44 |
| 1828 | quiz | reopen the Quizzes page | 18 ms | 18 |
| 1829 | review | reopen the Review page | 14 ms | 14 |
| 1830 | projects | reopen the Projects page | 43 ms | 43 |
| 1831 | journal | reopen the Log page | 17 ms | 17 |
| 1832 | stats | reopen the Progress page | 23 ms | 23 |
| 1833 | library | reopen the Library page | 34 ms | 34 |
| 1834 | settings | reopen the Settings page | 29 ms | 29 |
| 1835 | screenshots | grab every page on both themes | ok | 12796 |
| 1836 | screenshots | practice page after a passing run | results panel hidden: False; rows rendered into it: 4; hint label hidden: True;  | 0 |
| 1837 | help | press F1 and close the shortcut list | ok | 50 |
| 1838 | menu | press Ctrl+, for Settings | ok | 187 |
| 1839 | settings | open the snapshot list and cancel | ok | 46 |
| 1840 | settings | restore the snapshot just taken | ok | 124 |
| 1841 | onboarding | Continue, Continue, Back | ok | 41 |
| 1842 | update | press Update and restart while offline | ok | 18 |
| 1843 | quiz | finish a quiz and go back to its phase | ok | 1085 |
| 1844 | quiz | finish a quiz and pick another | ok | 975 |
| 1845 | review | skip to a concept card, reveal, rate | ok | 124 |
| 1846 | practice | press Next | ok | 21 |
| 1847 | phase | open the first resource | ok | 28 |
| 1848 | library | press every button on tab 0 | ok | 974 |
| 1849 | library | press every button on tab 1 | ok | 920 |
| 1850 | library | press every button on tab 2 | ok | 746 |
| 1851 | library | press every button on tab 3 | ok | 516 |
| 1852 | projects | open the repo link | ok | 133 |
| 1853 | projects | press every status button | ok | 486 |
| 1854 | journal | the history opens on the newest sixty | ok | 0 |
| 1855 | journal | press Show older for the next sixty | ok | 825 |
| 1856 | journal | press Show older for the last ten | ok | 177 |
| 1857 | journal | find one entry among a hundred | ok | 386 |
| 1858 | journal | a filter that matches nothing says so | ok | 646 |
| 1859 | journal | narrow the range, then widen it again | ok | 1912 |
| 1860 | journal | load an old entry back into the form | ok | 42 |
| 1861 | journal | save the correction | ok | 70 |
| 1862 | journal | take the correction back with Ctrl+Z | ok | 45 |
| 1863 | journal | and put it back with Ctrl+Y | ok | 47 |
| 1864 | journal | start an edit and cancel out of it | ok | 74 |
| 1865 | journal | delete an entry by mistake | ok | 35 |
| 1866 | journal | Ctrl+Z brings the whole entry back | ok | 46 |
| 1867 | journal | Ctrl+Y deletes it again | ok | 33 |
| 1868 | journal | log today for the first time | ok | 48 |
| 1869 | journal | the form warns before the day stacks | ok | 0 |
| 1870 | journal | log today again anyway | ok | 47 |
| 1871 | journal | every note written is listed here | ok | 0 |
| 1872 | journal | the filter searches the notes too | ok | 183 |
| 1873 | journal | open note 0 from the log | ok | 223 |
| 1874 | journal | open note 1 from the log | ok | 263 |
| 1875 | journal | open note 2 from the log | ok | 211 |
| 1876 | journal | open note 3 from the log | ok | 200 |
| 1877 | journal | open note 4 from the log | ok | 2545 |
| 1878 | journal | open note 5 from the log | ok | 84 |
| 1879 | journal | open note 6 from the log | ok | 82 |
| 1880 | journal | the notes section with nothing in it | ok | 0 |
| 1881 | practice | submit an empty editor and read the reasons | ok | 306 |
| 1882 | practice | put the real answer back | ok | 340 |
| 1883 | practice | forget the exclamation mark and run | ok | 327 |
| 1884 | practice | get one character wrong instead | ok | 385 |
| 1885 | practice | get only the capital wrong | ok | 356 |
| 1886 | practice | start an endless run and press Stop | ok | 354 |
| 1887 | practice | read every hint, then press once more | ok | 86 |
| 1888 | practice | search for one exercise by its title | ok | 20 |
| 1889 | practice | search for something that is not there | ok | 19 |
| 1890 | practice | clear the search | ok | 39 |
| 1891 | practice | filter by every difficulty | ok | 150 |
| 1892 | practice | show only the revealed ones | ok | 50 |
| 1893 | practice | walk to the last exercise and press Next again | ok | 50 |
| 1894 | practice | pass the exercise | ok | 252 |
| 1895 | practice | carry on experimenting and break it | ok | 22 |
| 1896 | practice | press Restore my passing version | ok | 9 |
| 1897 | practice | press Reset, then restore once more | ok | 100 |
| 1898 | practice | read the answer | ok | 39 |
| 1899 | practice | check the list says so too | ok | 0 |
| 1900 | practice | press Try this one again from scratch | ok | 29 |
| 1901 | review | press Space to reveal the saved line | ok | 35 |
| 1902 | review | press 3 to rate it Good | ok | 35 |
| 1903 | review | pick a multiple choice option by letter | ok | 2 |
| 1904 | review | press Enter to check it | ok | 29 |
| 1905 | review | press 4 for Easy | ok | 40 |
| 1906 | review | answer with the Again key | ok | 62 |
| 1907 | review | answer with the Hard key | ok | 57 |
| 1908 | review | answer with the Good key | ok | 59 |
| 1909 | review | answer with the Easy key | ok | 56 |
| 1910 | review | type in the search box with a card open | ok | 3 |
| 1911 | review | bury the card in front of you | ok | 78 |
| 1912 | review | the summary offers the buried card back | ok | 135 |
| 1913 | review | answer one card, then take it back | ok | 126 |
| 1914 | review | Ctrl+Z takes the next one back too | ok | 118 |
| 1915 | review | skip the same card twice | ok | 74 |
| 1916 | phase | open a line's menu with the ... button | ok | 34 |
| 1917 | phase | open the same menu with Shift+F10 | ok | 9 |
| 1918 | phase | the Menu key offers to take it out again | ok | 19 |
| 1919 | search | open the box with Ctrl+K | ok | 12 |
| 1920 | search | find a phase note written minutes ago | ok | 271 |
| 1921 | search | find your own project note | ok | 167 |
| 1922 | search | find a project by its repository url | ok | 6 |
| 1923 | search | find a log entry and open the log | ok | 28 |
| 1924 | search | type a query | ok | 65 |
| 1925 | search | walk down and back up the results | ok | 11 |
| 1926 | search | page down and page up the results | ok | 9 |
| 1927 | search | open the selected hit with Enter | ok | 347 |
| 1928 | search | close the results with Escape | ok | 17 |
| 1929 | library | open the field f-web from search | ok | 148 |
| 1930 | library | open the cert c-cs50p from search | ok | 201 |
| 1931 | search | open a question from search | ok | 13 |
| 1932 | search | read the question and close it | ok | 30 |
| 1933 | library | filter the library to nothing | ok | 68 |
| 1934 | library | filter the library to one shelf entry | ok | 270 |
| 1935 | library | mark a row on tab 0 as read | ok | 29 |
| 1936 | library | take the mark on tab 0 back | ok | 15 |
| 1937 | library | mark a row on tab 1 as read | ok | 236 |
| 1938 | library | take the mark on tab 1 back | ok | 16 |
| 1939 | library | mark a row on tab 2 as read | ok | 190 |
| 1940 | library | take the mark on tab 2 back | ok | 20 |
| 1941 | library | undo the last read mark | ok | 425 |
| 1942 | navigation | press Ctrl+0 | ok | 86 |
| 1943 | navigation | press Ctrl+L | ok | 73 |
| 1944 | navigation | open the library from the Go menu | ok | 89 |
| 1945 | first run | read the status bar on a first launch | ok | 0 |
| 1946 | onboarding | type a name and continue | ok | 17 |
| 1947 | onboarding | choose an experience card | ok | 22 |
| 1948 | onboarding | tick two goals | ok | 26 |
| 1949 | onboarding | go back a step and forward again | ok | 20 |
| 1950 | onboarding | set a pace and build the plan | ok | 119 |
| 1951 | onboarding | skip the whole thing | ok | 10 |
| 1952 | settings | press Run setup again | ok | 104 |
| 1953 | quiz | start one and skip a question | ok | 112 |
| 1954 | quiz | move on to the next question | ok | 36 |
| 1955 | quiz | think better of leaving | ok | 2 |
| 1956 | quiz | leave the quiz | ok | 252 |
| 1957 | quiz | close the app in the middle of one | ok | 366 |
| 1958 | quiz | resume where it was left | ok | 75 |
| 1959 | quiz | start it over instead | ok | 346 |
| 1960 | settings | nothing has left this machine yet | ok | 0 |
| 1961 | settings | choose a second copy folder | ok | 10 |
| 1962 | settings | copy everything there now | ok | 29 |
| 1963 | settings | import a backup and read the summary | ok | 72 |
| 1964 | projects | press Open with nothing to open | ok | 2 |
| 1965 | projects | type a repo address | ok | 3 |
| 1966 | projects | replace it with a note to self | ok | 2 |
| 1967 | today | read the note above the list | ok | 83 |
| 1968 | today | push the first item off until tomorrow | ok | 92 |
| 1969 | today | push a second one off from a compact row | ok | 64 |
| 1970 | today | find the way back to what was hidden | ok | 78 |
| 1971 | today | yesterday's 'first thing tomorrow' returns | ok | 115 |
| 1972 | today | push everything off for a quiet evening | ok | 65 |
| 1973 | today | finish the entire curriculum | ok | 415 |
| 1974 | today | read what the finished plan says | ok | 0 |
| 1975 | today | keep reviewing from the hero | ok | 105 |
| 1976 | today | change track from the hero | ok | 186 |
| 1977 | today | export the report from the hero | ok | 80 |
| 1978 | roadmap | the marker is there while work remains | ok | 0 |
| 1979 | roadmap | and is gone once there is nowhere to go | ok | 0 |
| 1980 | stats | click a phase row | ok | 402 |
| 1981 | stats | select a row and press Enter | ok | 237 |
| 1982 | stats | hover the quiz column for the trend | ok | 0 |
| 1983 | phase | the way into the review deck is announced | ok | 0 |
| 1984 | phase | write a long note into the box | ok | 24 |
| 1985 | phase | and it shrinks back for a short one | ok | 11 |
| 1986 | search | type a word that is nowhere | ok | 45 |
| 1987 | search | Escape, then Ctrl+K again | ok | 27 |
| 1988 | search | open a shelf book from Ctrl+K | ok | 206 |
| 1989 | library | filter for a channel on the Shelf tab | ok | 119 |
| 1990 | library | follow the count to the Video tab | ok | 10 |
| 1991 | library | clear the filter | ok | 365 |
| 1992 | projects | SHOW Shipped with nothing shipped | ok | 30 |
| 1993 | projects | press Show every project | ok | 469 |
| 1994 | projects | type in FIND | ok | 647 |
| 1995 | stats | click the Checks heading | ok | 7 |
| 1996 | stats | pick every SORT choice | ok | 22 |
| 1997 | practice | fail a run, then Where this is taught | ok | 538 |
| 1998 | settings | set filters, then change the theme | ok | 8316 |
| 1999 | settings | come back to each page | ok | 16028 |
| 2000 | quiz | read the picker and its counter | ok | 0 |
| 2001 | quiz | open the quizzes outside the track | ok | 25 |
| 2002 | quiz | type into FIND | ok | 274 |
| 2003 | quiz | a search that matches nothing | ok | 295 |
| 2004 | quiz | SHOW each status in turn | ok | 872 |
| 2005 | quiz | start a quiz from the filtered list | ok | 416 |
| 2006 | quiz | press the second choice every time | ok | 1796 |
| 2007 | review | pick a wrong option by its letter | ok | 40 |
| 2008 | review | press Where this is taught | ok | 229 |
| 2009 | review | press Next card | ok | 33 |
| 2010 | review | a second wrong answer, left with Space | ok | 55 |
| 2011 | review | reveal a gate check | ok | 25 |
| 2012 | review | rate it Good | ok | 39 |
| 2013 | phase | a phase read to the end | ok | 297 |
| 2014 | roadmap | the roadmap says read, not proven | ok | 324 |
| 2015 | phase | the same phase, proven | ok | 255 |
| 2016 | today | an earlier phase is mixed into today | ok | 126 |
| 2017 | quiz | start a quiz from the picker | ok | 77 |
| 2018 | quiz | leave and start a different one | ok | 335 |
| 2019 | review | press Check for more | ok | 33 |
| 2020 | updates | open the update dialog and decline | ok | 23 |
| 2021 | updates | open the releases page instead | ok | 15 |
| 2022 | menu | File > Quit | ok | 10 |
| 2023 | menu | File > Switch profile | ok | 0 |
| 2024 | menu | File > Export backup... | ok | 193 |
| 2025 | menu | File > Export progress report... | ok | 30 |
| 2026 | menu | File > Take a snapshot | ok | 14 |
| 2027 | menu | File > Restore a snapshot... | ok | 39 |
| 2028 | menu | Go > Today | ok | 82 |
| 2029 | menu | Go > Roadmap | ok | 336 |
| 2030 | menu | Go > Phase | ok | 228 |
| 2031 | menu | Go > Practice | ok | 125 |
| 2032 | menu | Go > Quizzes | ok | 279 |
| 2033 | menu | Go > Review | ok | 47 |
| 2034 | menu | Go > Projects | ok | 2418 |
| 2035 | menu | Go > Log | ok | 80 |
| 2036 | menu | Go > Progress | ok | 232 |
| 2037 | menu | Go > Library | ok | 2277 |
| 2038 | menu | Go > Settings | ok | 87 |
| 2039 | menu | Go > Find | ok | 15 |
| 2040 | menu | Edit > Undo | ok | 0 |
| 2041 | menu | Edit > Redo | ok | 0 |
| 2042 | menu | Help > How this app works | ok | 0 |
| 2043 | menu | Help > Keyboard shortcuts | ok | 19 |
| 2044 | menu | Help > Report a problem or request a feature... | ok | 24 |
| 2045 | menu | Help > Check for updates | ok | 1 |
| 2046 | menu | Help > About | ok | 1 |
| 2047 | menu | every navigation shortcut | ok | 1547 |
