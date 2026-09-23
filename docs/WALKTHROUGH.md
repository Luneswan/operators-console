# Walkthrough of Operator's Console

A single learner's pass through every page, every control and every piece of content, driven through the real widgets with QTest and watched by a net of sensors.

- Generated: 2026-09-23 13:02
- Platform: Windows-11-10.0.26200-SP0, Python 3.14.5, Qt offscreen
- Runtime: 9 min 48 s
- Steps recorded: 1561
- Findings: 8
- Unhandled exceptions seen: 0
- Qt warnings and criticals: 1
- Dialogs answered: 30
- URLs intercepted (none opened): 312
- pytest exit status: 0

## Findings

| id | severity | view | what happened | how to reproduce |
| --- | --- | --- | --- | --- |
| W-01 | major | roadmap | step blocks for 3260 ms: open every phase card from the roadmap | Open roadmap and open every phase card from the roadmap; the interface is frozen for 3.3 s. |
| W-02 | major | navigation | step blocks for 9726 ms: switch pages 200 times as fast as the event loop allows | Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 9.7 s. |
| W-03 | major | phase | step blocks for 4664 ms: walk Next through all 21 phases | Open phase and walk Next through all 21 phases; the interface is frozen for 4.7 s. |
| W-04 | major | phase | step blocks for 4207 ms: walk Previous back to the first phase | Open phase and walk Previous back to the first phase; the interface is frozen for 4.2 s. |
| W-05 | major | phase | step blocks for 3658 ms: choose every phase from the picker | Open phase and choose every phase from the picker; the interface is frozen for 3.7 s. |
| W-06 | major | phase | step blocks for 4059 ms: type a note in each phase and leave at once | Open phase and type a note in each phase and leave at once; the interface is frozen for 4.1 s. |
| W-08 | major | settings | changing the theme freezes the window for 1.0 seconds | Visit every page once, then open Settings > Appearance and change the theme. The window stops responding for about 1.0 s each time. |
| W-07 | polish | journal | a second entry for the same day is added, not merged | Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions. |

### W-01 - step blocks for 3260 ms: open every phase card from the roadmap

- **Severity**: major
- **View**: roadmap
- **Repro**: Open roadmap and open every phase card from the roadmap; the interface is frozen for 3.3 s.

### W-02 - step blocks for 9726 ms: switch pages 200 times as fast as the event loop allows

- **Severity**: major
- **View**: navigation
- **Repro**: Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 9.7 s.

### W-03 - step blocks for 4664 ms: walk Next through all 21 phases

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Next through all 21 phases; the interface is frozen for 4.7 s.

### W-04 - step blocks for 4207 ms: walk Previous back to the first phase

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and walk Previous back to the first phase; the interface is frozen for 4.2 s.

### W-05 - step blocks for 3658 ms: choose every phase from the picker

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and choose every phase from the picker; the interface is frozen for 3.7 s.

### W-06 - step blocks for 4059 ms: type a note in each phase and leave at once

- **Severity**: major
- **View**: phase
- **Repro**: Open phase and type a note in each phase and leave at once; the interface is frozen for 4.1 s.

### W-08 - changing the theme freezes the window for 1.0 seconds

- **Severity**: major
- **View**: settings
- **Repro**: Visit every page once, then open Settings > Appearance and change the theme. The window stops responding for about 1.0 s each time.

```
MainWindow.apply_theme calls app.setStyleSheet() with an 11 KB sheet, which repolishes every widget in the process. With only Today built (184 widgets) the switch costs about 80 ms; with all eleven pages built (290 widgets) it costs 1014 ms. The text-size spin box on the same page goes through the same path on every step.
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

- Controls declared: **102**
- Activated by the walk: **99** (97%)

| kind | declared | hit | % |
| --- | --- | --- | --- |
| action | 10 | 10 | 100% |
| button | 83 | 81 | 98% |
| shortcut | 9 | 8 | 89% |

<details><summary>Every control, hit or not</summary>

| file | line | kind | label | hit |
| --- | --- | --- | --- | --- |
| operators_console/ui/main_window.py | 149 | button | Close | yes |
| operators_console/ui/main_window.py | 356 | button | Undo | yes |
| operators_console/ui/main_window.py | 362 | button | Redo | yes |
| operators_console/ui/main_window.py | 399 | action | Quit | yes |
| operators_console/ui/main_window.py | 400 | shortcut | StandardKey.Quit | yes |
| operators_console/ui/main_window.py | 421 | action | Undo | yes |
| operators_console/ui/main_window.py | 422 | shortcut | StandardKey.Undo | yes |
| operators_console/ui/main_window.py | 425 | action | Redo | yes |
| operators_console/ui/main_window.py | 426 | shortcut | <_redo_keys()> | yes |
| operators_console/ui/main_window.py | 431 | action | Find | yes |
| operators_console/ui/main_window.py | 432 | shortcut | Ctrl+K | yes |
| operators_console/ui/main_window.py | 437 | action | How this app works | yes |
| operators_console/ui/main_window.py | 440 | action | Keyboard shortcuts | yes |
| operators_console/ui/main_window.py | 441 | shortcut | F1 | yes |
| operators_console/ui/main_window.py | 444 | action | Check for updates | yes |
| operators_console/ui/main_window.py | 447 | action | About | yes |
| operators_console/ui/main_window.py | 289 | button | <text> | yes |
| operators_console/ui/main_window.py | 393 | action | <text> | yes |
| operators_console/ui/main_window.py | 407 | action | <text> | yes |
| operators_console/ui/main_window.py | 396 | shortcut | <QKeySequence()> | NO |
| operators_console/ui/main_window.py | 409 | shortcut | Ctrl+%d | yes |
| operators_console/ui/main_window.py | 413 | shortcut | Ctrl+0 | yes |
| operators_console/ui/main_window.py | 416 | shortcut | Ctrl+, | yes |
| operators_console/ui/onboarding.py | 150 | button | Skip - I will decide later | yes |
| operators_console/ui/onboarding.py | 155 | button | Back | yes |
| operators_console/ui/onboarding.py | 159 | button | Continue | yes |
| operators_console/ui/shortcuts.py | 90 | button | Close | yes |
| operators_console/ui/snapshots.py | 72 | button | Open the backups folder | yes |
| operators_console/ui/snapshots.py | 77 | button | Cancel | yes |
| operators_console/ui/snapshots.py | 80 | button | Restore this snapshot | yes |
| operators_console/ui/updater.py | 199 | button | Open the releases page | yes |
| operators_console/ui/updater.py | 203 | button | Not now | yes |
| operators_console/ui/updater.py | 206 | button | Update and restart | yes |
| operators_console/ui/views/dashboard.py | 226 | button | <computed> | yes |
| operators_console/ui/views/dashboard.py | 235 | button | Not today | yes |
| operators_console/ui/views/dashboard.py | 251 | button | Start | yes |
| operators_console/ui/views/dashboard.py | 320 | button | Open this phase | yes |
| operators_console/ui/views/dashboard.py | 372 | button | Export report | yes |
| operators_console/ui/views/dashboard.py | 375 | button | Keep reviewing | yes |
| operators_console/ui/views/dashboard.py | 379 | button | Change track | yes |
| operators_console/ui/views/journal.py | 145 | button | Cancel | yes |
| operators_console/ui/views/journal.py | 149 | button | Log today | yes |
| operators_console/ui/views/journal.py | 176 | button | Show older | yes |
| operators_console/ui/views/journal.py | 350 | button | Edit | yes |
| operators_console/ui/views/journal.py | 354 | button | Delete | yes |
| operators_console/ui/views/journal.py | 423 | button | Open | yes |
| operators_console/ui/views/library.py | 535 | button | <computed> | yes |
| operators_console/ui/views/library.py | 440 | button | <name> | yes |
| operators_console/ui/views/library.py | 540 | button | Open | NO |
| operators_console/ui/views/library.py | 457 | button | <name> | yes |
| operators_console/ui/views/phase.py | 41 | button | Previous | yes |
| operators_console/ui/views/phase.py | 42 | button | Next | yes |
| operators_console/ui/views/phase.py | 241 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 247 | button | Quiz | yes |
| operators_console/ui/views/phase.py | 253 | button | <computed> | yes |
| operators_console/ui/views/phase.py | 310 | button | Copy | yes |
| operators_console/ui/views/practice.py | 213 | button | Run checks | yes |
| operators_console/ui/views/practice.py | 218 | button | Stop | yes |
| operators_console/ui/views/practice.py | 223 | button | Hint | yes |
| operators_console/ui/views/practice.py | 226 | button | Reset | yes |
| operators_console/ui/views/practice.py | 229 | button | Show solution | yes |
| operators_console/ui/views/practice.py | 233 | button | Next | yes |
| operators_console/ui/views/practice.py | 244 | button | Restore my passing version | yes |
| operators_console/ui/views/practice.py | 249 | button | Try this one again from scratch | yes |
| operators_console/ui/views/practice.py | 755 | button | Where this is taught | yes |
| operators_console/ui/views/projects.py | 108 | button | Open | yes |
| operators_console/ui/views/projects.py | 141 | button | <computed> | yes |
| operators_console/ui/views/projects.py | 135 | button | <text> | yes |
| operators_console/ui/views/projects.py | 444 | button | Show every project | yes |
| operators_console/ui/views/quiz.py | 215 | button | Start | yes |
| operators_console/ui/views/quiz.py | 242 | button | Resume | yes |
| operators_console/ui/views/quiz.py | 245 | button | Start over | yes |
| operators_console/ui/views/quiz.py | 401 | button | Skip (counts as wrong) | yes |
| operators_console/ui/views/quiz.py | 406 | button | Leave this quiz | yes |
| operators_console/ui/views/quiz.py | 410 | button | Check answer | yes |
| operators_console/ui/views/quiz.py | 464 | button | <dynamic> | yes |
| operators_console/ui/views/quiz.py | 523 | button | Retake | yes |
| operators_console/ui/views/quiz.py | 526 | button | Back to the phase | yes |
| operators_console/ui/views/quiz.py | 531 | button | Other quizzes | yes |
| operators_console/ui/views/review.py | 200 | button | Restore | yes |
| operators_console/ui/views/review.py | 321 | button | Skip for now  (S) | yes |
| operators_console/ui/views/review.py | 402 | button | Where this is taught | yes |
| operators_console/ui/views/review.py | 408 | button | Next card  (Space) | yes |
| operators_console/ui/views/review.py | 464 | button | Bury this card | yes |
| operators_console/ui/views/review.py | 584 | button | Check for more | yes |
| operators_console/ui/views/review.py | 650 | button | <dynamic> | NO |
| operators_console/ui/views/review.py | 277 | button | Undo that answer | yes |
| operators_console/ui/views/review.py | 302 | button | Check  (Space) | yes |
| operators_console/ui/views/review.py | 315 | button | Reveal  (Space) | yes |
| operators_console/ui/views/review.py | 454 | button | <computed> | yes |
| operators_console/ui/views/roadmap.py | 208 | button | Open | yes |
| operators_console/ui/views/roadmap.py | 258 | button | Open | yes |
| operators_console/ui/views/settings.py | 130 | button | Run setup again | yes |
| operators_console/ui/views/settings.py | 240 | button | Check now | yes |
| operators_console/ui/views/settings.py | 277 | button | Choose folder... | yes |
| operators_console/ui/views/settings.py | 280 | button | Copy now | yes |
| operators_console/ui/views/settings.py | 295 | button | Snapshot now | yes |
| operators_console/ui/views/settings.py | 298 | button | Restore a snapshot... | yes |
| operators_console/ui/views/settings.py | 310 | button | Reset all progress | yes |
| operators_console/ui/views/settings.py | 258 | button | <text> | yes |
| operators_console/ui/widgets/common.py | 463 | button | ... | yes |
| operators_console/ui/widgets/common.py | 635 | button | Open | yes |

</details>

Recorded activations with no matching declaration (Qt's own controls, e.g. dialog buttons): 2

## What the walk could not reach

- **the "N more" resource disclosure** - PhaseView._fill_body draws one LinkRow per resource with no collapse, so no disclosure control exists in this revision of src/operators_console/ui/views/phase.py
- **undo across a restart** - History lives in memory (ui/context.py -> core/history.py) and is not written to the store, so nothing can be undone after a relaunch. That is a design choice, not a defect, but it means the walk cannot test undo across a save and reload.
- **the page you were on when you quit** - MainWindow always opens on Today (go('today') in __init__) and nothing writes the current page to the store, so 'position survives a relaunch' means progress, not the page. Recorded rather than asserted.
- **the real folder chooser** - QFileDialog.getExistingDirectory is a static that builds and execs its dialog in C++, so the walk's dialog answerer - which patches QDialog.exec in Python - cannot reach it. It is stubbed here the way getSaveFileName is stubbed in the harness.
- **the 'Update and restart' button** - Pressing it downloads a release package over the network and relaunches the program. The walk drives the dialog up to that button and stops; the download path itself is covered by tests/test_updates.py and tests/test_updates_security.py.
- **operators_console/ui/main_window.py:396 (shortcut <QKeySequence()>)** - never activated by the walk
- **operators_console/ui/views/library.py:540 (button Open)** - never activated by the walk
- **operators_console/ui/views/review.py:650 (button <dynamic>)** - never activated by the walk

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
| clicks on disabled controls | 124 |
| concept cards revealed | 1 |
| controls declared in the source | 102 |
| controls reached by Tab on practice | 23 |
| controls reached by Tab on today | 21 |
| controls the walk activated | 99 |
| copies of the backups off this disk | 1 |
| curriculum completions reached | 1 |
| dead controls that now say so | 1 |
| distinct tracks reachable from goals | 9 |
| duplicate days warned about | 1 |
| endless loops timed out | 1 |
| exercises fully exercised | 119 |
| exercises re-armed from scratch | 1 |
| failing checks that explained themselves | 3 |
| field library buttons pressed | 118 |
| filters kept across a theme change | 3 |
| first run hints shown | 1 |
| gate checks recalled | 1 |
| gates cleared and reopened | 20 |
| goal combinations previewed | 512 |
| goals toggled in settings | 18 |
| graded submissions | 357 |
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
| milliseconds for 200 page switches | 4068 |
| milliseconds for a typical project status press | 25 |
| milliseconds to open review with 1000 cards | 91 |
| notes found by search | 1 |
| notes gathered onto the log | 7 |
| notes opened from the log | 7 |
| onboarding experience levels | 4 |
| onboarding steps walked | 4 |
| page and size combinations checked | 33 |
| pages opened against empty content | 5 |
| passing versions restored | 2 |
| phase check rows drawn | 536 |
| phase jump buttons used | 56 |
| phase notes written | 1 |
| phases opened | 21 |
| phases proven in the walk | 1 |
| phases reachable from the picker | 21 |
| plan actions dismissed | 2 |
| plan notes read | 1 |
| practice difficulty filters used | 5 |
| practice phase filters used | 17 |
| progress reports written | 1 |
| progress rows opened | 1 |
| project requirements drawn | 130 |
| project requirements ticked | 130 |
| project status changes | 66 |
| projects filters pressed | 3 |
| projects listed | 22 |
| projects outside the plan | 0 |
| questions answered by position | 18 |
| questions answered correctly | 242 |
| questions answered wrongly | 242 |
| questions read without an attempt | 1 |
| quiz options picked by letter | 1 |
| quiz searches typed | 1 |
| quiz status filters chosen | 3 |
| quiz trends shown | 1 |
| quizzes listed | 20 |
| quizzes scored full marks | 20 |
| quizzes started from the picker | 2 |
| rapid page switches | 400 |
| rating keys pressed | 4 |
| resource links opened | 92 |
| result rows walked with the keyboard | 4 |
| review answers taken back | 1 |
| review cards answered | 15 |
| review cards answered from the keyboard | 1 |
| review cards seeded | 1000 |
| roadmap Open buttons pressed | 14 |
| roadmap extras opened | 6 |
| roadmap tracks rendered | 9 |
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
| study steps ticked and unticked | 435 |
| themes exercised | 3 |
| tracks chosen in settings | 9 |
| undoable change kinds covered | 4 |
| update dialogs opened | 1 |
| ways back into the setup wizard | 1 |
| ways out of a quiz | 2 |
| where-taught presses | 1 |
| worst theme switch in milliseconds | 1014 |
| wrong answers explained down to the character | 1 |
| wrong answers scheduled for review | 242 |
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
- `https://exercism.org/tracks/python`
- `https://www.youtube.com/watch?v=pkYVOmU3MgA`
- `https://cp-algorithms.com/`
- `https://neetcode.io/`
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
- `https://docs.python.org/3/extending/index.html`
- `https://cs50.harvard.edu/x/weeks/4/`
- `https://github.com/python/cpython`
- `https://docs.python.org/3/library/dis.html`
- `https://github.com/DataTalksClub/data-engineering-zoomcamp`
- `https://airflow.apache.org/docs/`
- `https://docs.prefect.io/`
- `https://docs.getdbt.com/`
- `https://docs.pola.rs/`
- ... and 110 more

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
| notice | How this app works | Today tells you what to do next. Follow it and you can ignore everything else.  Roadmap is the plan, ordered so nothing depends on something you have not been taught. Phases are never locked.  Practice runs your code aga |
| dialog | ShortcutsDialog | Keyboard shortcuts |
| notice | About Python Operator's Console | Python Operator's Console 1.1.0  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2841\test_the_help_ |
| messagebox | Show the solution? | You have not passed this one yet.  Reading the answer now costs you the exercise. Try one more hint first? |
| open file | Import a backup | C:\Users\anasa |
| question | Replace everything? | Importing replaces all of your current progress.  A backup of the current state is taken first, into the backups folder. Continue? |
| question | Reset all progress? | This clears every checkbox, exercise, review, project and log entry.  A snapshot is taken first, so Restore a snapshot (here in Settings) can bring it all back. Your settings are kept. |
| dialog | UpdateDialog | Update available |
| dialog | QuestionDialog | Question |
| dialog | Onboarding | Set up your plan |
| question | Leave this quiz? | What you have answered is already scored and scheduled for review.  The rest of this attempt is dropped, and the quiz starts from the beginning next time. Leave it? |
| notice | About Python Operator's Console | Python Operator's Console 1.1.0  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2841\test_the_remai |

## Every step

| # | view | action | result | ms |
| --- | --- | --- | --- | --- |
| 1 | onboarding | open the wizard on first run | ok | 20 |
| 2 | onboarding | continue from step 1 | ok | 6 |
| 3 | onboarding | continue from step 2 | ok | 0 |
| 4 | onboarding | continue from step 3 | ok | 0 |
| 5 | onboarding | back from step 4 | ok | 0 |
| 6 | onboarding | back from step 3 | ok | 0 |
| 7 | onboarding | back from step 2 | ok | 0 |
| 8 | onboarding | experience: Never written code before | ok | 31 |
| 9 | onboarding | experience: Some Python, but it does not stick | ok | 27 |
| 10 | onboarding | experience: Confident in another language | ok | 30 |
| 11 | onboarding | experience: I write Python at work already | ok | 31 |
| 12 | onboarding | tick all 512 goal combinations | ok | 92 |
| 13 | onboarding | finish with goal: Build websites and APIs | ok | 33 |
| 14 | onboarding | finish with goal: Work with data | ok | 29 |
| 15 | onboarding | finish with goal: Machine learning and AI | ok | 27 |
| 16 | onboarding | finish with goal: Automate boring work | ok | 69 |
| 17 | onboarding | finish with goal: Games and graphics | ok | 85 |
| 18 | onboarding | finish with goal: Infrastructure and deployment | ok | 71 |
| 19 | onboarding | finish with goal: Security and hacking | ok | 95 |
| 20 | onboarding | finish with goal: Pass a technical interview | ok | 50 |
| 21 | onboarding | finish with goal: Understand how computers work | ok | 75 |
| 22 | onboarding | pace 0.5 h x 1 days | ok | 65 |
| 23 | onboarding | pace 16.0 h x 7 days | ok | 66 |
| 24 | onboarding | skip the wizard | ok | 8 |
| 25 | today | land on Today after skipping | ok | 112 |
| 26 | today | read the four headline tiles | ok | 0 |
| 27 | today | press Start on plan row 1 | ok | 145 |
| 28 | today | press Start on plan row 2 | ok | 285 |
| 29 | today | press Start on plan row 3 | ok | 1750 |
| 30 | today | press Start on plan row 4 | ok | 300 |
| 31 | today | press Start on plan row 5 | ok | 75 |
| 32 | today | open the current phase from Where you are | ok | 197 |
| 33 | settings | switch the theme to light | ok | 10 |
| 34 | today | click the Today sidebar button (light theme) | ok | 105 |
| 35 | roadmap | click the Roadmap sidebar button (light theme) | ok | 345 |
| 36 | phase | click the Phase sidebar button (light theme) | ok | 278 |
| 37 | practice | click the Practice sidebar button (light theme) | ok | 137 |
| 38 | quiz | click the Quizzes sidebar button (light theme) | ok | 180 |
| 39 | review | click the Review sidebar button (light theme) | ok | 56 |
| 40 | projects | click the Projects sidebar button (light theme) | ok | 1729 |
| 41 | journal | click the Log sidebar button (light theme) | ok | 117 |
| 42 | stats | click the Progress sidebar button (light theme) | ok | 243 |
| 43 | library | click the Library sidebar button (light theme) | ok | 2275 |
| 44 | settings | click the Settings sidebar button (light theme) | ok | 266 |
| 45 | settings | switch the theme to dark | ok | 593 |
| 46 | today | click the Today sidebar button (dark theme) | ok | 127 |
| 47 | roadmap | click the Roadmap sidebar button (dark theme) | ok | 364 |
| 48 | phase | click the Phase sidebar button (dark theme) | ok | 279 |
| 49 | practice | click the Practice sidebar button (dark theme) | ok | 144 |
| 50 | quiz | click the Quizzes sidebar button (dark theme) | ok | 179 |
| 51 | review | click the Review sidebar button (dark theme) | ok | 31 |
| 52 | projects | click the Projects sidebar button (dark theme) | ok | 1819 |
| 53 | journal | click the Log sidebar button (dark theme) | ok | 89 |
| 54 | stats | click the Progress sidebar button (dark theme) | ok | 249 |
| 55 | library | click the Library sidebar button (dark theme) | ok | 2321 |
| 56 | settings | click the Settings sidebar button (dark theme) | ok | 148 |
| 57 | settings | switch the theme to system | ok | 598 |
| 58 | today | click the Today sidebar button (system theme) | ok | 141 |
| 59 | roadmap | click the Roadmap sidebar button (system theme) | ok | 366 |
| 60 | phase | click the Phase sidebar button (system theme) | ok | 310 |
| 61 | practice | click the Practice sidebar button (system theme) | ok | 121 |
| 62 | quiz | click the Quizzes sidebar button (system theme) | ok | 162 |
| 63 | review | click the Review sidebar button (system theme) | ok | 22 |
| 64 | projects | click the Projects sidebar button (system theme) | ok | 1845 |
| 65 | journal | click the Log sidebar button (system theme) | ok | 84 |
| 66 | stats | click the Progress sidebar button (system theme) | ok | 217 |
| 67 | library | click the Library sidebar button (system theme) | ok | 2107 |
| 68 | settings | click the Settings sidebar button (system theme) | ok | 129 |
| 69 | today | check no control escapes the Today page | ok | 0 |
| 70 | roadmap | check no control escapes the Roadmap page | ok | 0 |
| 71 | phase | check no control escapes the Phase page | ok | 1 |
| 72 | practice | check no control escapes the Practice page | ok | 0 |
| 73 | quiz | check no control escapes the Quizzes page | ok | 0 |
| 74 | review | check no control escapes the Review page | ok | 0 |
| 75 | projects | check no control escapes the Projects page | ok | 5 |
| 76 | journal | check no control escapes the Log page | ok | 0 |
| 77 | stats | check no control escapes the Progress page | ok | 1 |
| 78 | library | check no control escapes the Library page | ok | 2 |
| 79 | settings | check no control escapes the Settings page | ok | 0 |
| 80 | menu | Go > Today | ok | 95 |
| 81 | menu | Go > Roadmap | ok | 345 |
| 82 | menu | Go > Phase | ok | 253 |
| 83 | menu | Go > Practice | ok | 134 |
| 84 | menu | Go > Quizzes | ok | 153 |
| 85 | menu | Go > Review | ok | 49 |
| 86 | menu | Go > Projects | ok | 1617 |
| 87 | menu | Go > Log | ok | 87 |
| 88 | menu | Go > Progress | ok | 251 |
| 89 | menu | Go > Library | ok | 2204 |
| 90 | menu | Go > Settings | ok | 240 |
| 91 | menu | Go > Find | ok | 16 |
| 92 | today | press Ctrl+1 for Today | ok | 114 |
| 93 | roadmap | press Ctrl+2 for Roadmap | ok | 322 |
| 94 | phase | press Ctrl+3 for Phase | ok | 259 |
| 95 | practice | press Ctrl+4 for Practice | ok | 124 |
| 96 | quiz | press Ctrl+5 for Quizzes | ok | 140 |
| 97 | review | press Ctrl+6 for Review | ok | 53 |
| 98 | projects | press Ctrl+7 for Projects | ok | 1813 |
| 99 | journal | press Ctrl+8 for Log | ok | 106 |
| 100 | stats | press Ctrl+9 for Progress | ok | 265 |
| 101 | menu | &File > Export backup... | ok | 143 |
| 102 | menu | &File > Export progress report... | ok | 23 |
| 103 | menu | &File > Take a snapshot | ok | 18 |
| 104 | menu | &File > Restore a snapshot... | ok | 51 |
| 105 | menu | &Help > How this app works | ok | 0 |
| 106 | menu | &Help > Keyboard shortcuts | ok | 21 |
| 107 | menu | &Help > Check for updates | ok | 2 |
| 108 | menu | &Help > About | ok | 1 |
| 109 | roadmap | switch to the Well-rounded software engineer track | ok | 370 |
| 110 | roadmap | switch to the Learn Python properly (no career pressure) track | ok | 291 |
| 111 | roadmap | switch to the Backend & API engineer track | ok | 362 |
| 112 | roadmap | switch to the Data analysis & data engineering track | ok | 311 |
| 113 | roadmap | switch to the AI & machine learning engineer track | ok | 332 |
| 114 | roadmap | switch to the Automation, scripting & scraping track | ok | 261 |
| 115 | roadmap | switch to the DevOps & platform engineering track | ok | 333 |
| 116 | roadmap | switch to the Application security track | ok | 342 |
| 117 | roadmap | switch to the Job-ready in the shortest honest time track | ok | 313 |
| 118 | roadmap | open every phase card from the roadmap | slow (3260 ms) | 3260 |
| 119 | roadmap | open every phase outside the plan | ok | 1539 |
| 120 | navigation | switch pages 200 times as fast as the event loop allows | slow (9726 ms) | 9726 |
| 121 | phase | walk Next through all 21 phases | slow (4664 ms) | 4664 |
| 122 | phase | walk Previous back to the first phase | slow (4207 ms) | 4207 |
| 123 | phase | choose every phase from the picker | slow (3658 ms) | 3658 |
| 124 | phase | open phase OS Operating rules | ok | 291 |
| 125 | phase | open phase 00 Environment & Git | ok | 283 |
| 126 | phase | open phase 01 Python foundations | ok | 273 |
| 127 | phase | open phase 02 Python engineering | ok | 266 |
| 128 | phase | open phase 03 Packaging & tooling | ok | 184 |
| 129 | phase | open phase 04 Computer science core | ok | 225 |
| 130 | phase | open phase 05 Algorithms & problem solving | ok | 214 |
| 131 | phase | open phase 06 Linux & systems | ok | 211 |
| 132 | phase | open phase 07 Networking | ok | 164 |
| 133 | phase | open phase 08 SQL & PostgreSQL | ok | 185 |
| 134 | phase | open phase 09 Backend engineering | ok | 166 |
| 135 | phase | open phase 10 Automation & web | ok | 215 |
| 136 | phase | open phase 11 Async, concurrency & performance | ok | 198 |
| 137 | phase | open phase 12 Docker, CI/CD & deployment | ok | 168 |
| 138 | phase | open phase 13 Application security | ok | 167 |
| 139 | phase | open phase 14 AI engineering | ok | 264 |
| 140 | phase | open phase 15 Architecture & orchestration | ok | 217 |
| 141 | phase | open phase 16 Systems programming & internals | ok | 223 |
| 142 | phase | open phase 17 Data engineering | ok | 195 |
| 143 | phase | open phase 18 Beyond senior | ok | 239 |
| 144 | phase | open phase 99 Final-boss ladder | ok | 176 |
| 145 | phase | tick every study step in OS | ok | 228 |
| 146 | phase | untick every study step in OS | ok | 239 |
| 147 | phase | tick every study step in 00 | ok | 244 |
| 148 | phase | untick every study step in 00 | ok | 158 |
| 149 | phase | tick every study step in 01 | ok | 470 |
| 150 | phase | untick every study step in 01 | ok | 400 |
| 151 | phase | tick every study step in 02 | ok | 298 |
| 152 | phase | untick every study step in 02 | ok | 234 |
| 153 | phase | tick every study step in 03 | ok | 208 |
| 154 | phase | untick every study step in 03 | ok | 141 |
| 155 | phase | tick every study step in 04 | ok | 269 |
| 156 | phase | untick every study step in 04 | ok | 214 |
| 157 | phase | tick every study step in 05 | ok | 307 |
| 158 | phase | untick every study step in 05 | ok | 312 |
| 159 | phase | tick every study step in 06 | ok | 247 |
| 160 | phase | untick every study step in 06 | ok | 138 |
| 161 | phase | tick every study step in 07 | ok | 144 |
| 162 | phase | untick every study step in 07 | ok | 113 |
| 163 | phase | tick every study step in 08 | ok | 308 |
| 164 | phase | untick every study step in 08 | ok | 239 |
| 165 | phase | tick every study step in 09 | ok | 191 |
| 166 | phase | untick every study step in 09 | ok | 227 |
| 167 | phase | tick every study step in 10 | ok | 198 |
| 168 | phase | untick every study step in 10 | ok | 227 |
| 169 | phase | tick every study step in 11 | ok | 378 |
| 170 | phase | untick every study step in 11 | ok | 250 |
| 171 | phase | tick every study step in 12 | ok | 243 |
| 172 | phase | untick every study step in 12 | ok | 195 |
| 173 | phase | tick every study step in 13 | ok | 300 |
| 174 | phase | untick every study step in 13 | ok | 281 |
| 175 | phase | tick every study step in 14 | ok | 408 |
| 176 | phase | untick every study step in 14 | ok | 389 |
| 177 | phase | tick every study step in 15 | ok | 346 |
| 178 | phase | untick every study step in 15 | ok | 318 |
| 179 | phase | tick every study step in 16 | ok | 221 |
| 180 | phase | untick every study step in 16 | ok | 139 |
| 181 | phase | tick every study step in 17 | ok | 298 |
| 182 | phase | untick every study step in 17 | ok | 232 |
| 183 | phase | tick every study step in 18 | ok | 327 |
| 184 | phase | untick every study step in 18 | ok | 276 |
| 185 | phase | tick every study step in 99 | ok | 318 |
| 186 | phase | untick every study step in 99 | ok | 258 |
| 187 | phase | clear the gate on 00 | ok | 99 |
| 188 | phase | reopen the gate on 00 | ok | 67 |
| 189 | phase | clear the gate on 01 | ok | 81 |
| 190 | phase | reopen the gate on 01 | ok | 57 |
| 191 | phase | clear the gate on 02 | ok | 102 |
| 192 | phase | reopen the gate on 02 | ok | 67 |
| 193 | phase | clear the gate on 03 | ok | 80 |
| 194 | phase | reopen the gate on 03 | ok | 59 |
| 195 | phase | clear the gate on 04 | ok | 75 |
| 196 | phase | reopen the gate on 04 | ok | 56 |
| 197 | phase | clear the gate on 05 | ok | 94 |
| 198 | phase | reopen the gate on 05 | ok | 68 |
| 199 | phase | clear the gate on 06 | ok | 103 |
| 200 | phase | reopen the gate on 06 | ok | 66 |
| 201 | phase | clear the gate on 07 | ok | 84 |
| 202 | phase | reopen the gate on 07 | ok | 64 |
| 203 | phase | clear the gate on 08 | ok | 104 |
| 204 | phase | reopen the gate on 08 | ok | 91 |
| 205 | phase | clear the gate on 09 | ok | 92 |
| 206 | phase | reopen the gate on 09 | ok | 89 |
| 207 | phase | clear the gate on 10 | ok | 78 |
| 208 | phase | reopen the gate on 10 | ok | 69 |
| 209 | phase | clear the gate on 11 | ok | 85 |
| 210 | phase | reopen the gate on 11 | ok | 81 |
| 211 | phase | clear the gate on 12 | ok | 106 |
| 212 | phase | reopen the gate on 12 | ok | 76 |
| 213 | phase | clear the gate on 13 | ok | 95 |
| 214 | phase | reopen the gate on 13 | ok | 79 |
| 215 | phase | clear the gate on 14 | ok | 139 |
| 216 | phase | reopen the gate on 14 | ok | 70 |
| 217 | phase | clear the gate on 15 | ok | 107 |
| 218 | phase | reopen the gate on 15 | ok | 74 |
| 219 | phase | clear the gate on 16 | ok | 81 |
| 220 | phase | reopen the gate on 16 | ok | 63 |
| 221 | phase | clear the gate on 17 | ok | 109 |
| 222 | phase | reopen the gate on 17 | ok | 62 |
| 223 | phase | clear the gate on 18 | ok | 77 |
| 224 | phase | reopen the gate on 18 | ok | 74 |
| 225 | phase | clear the gate on 99 | ok | 79 |
| 226 | phase | reopen the gate on 99 | ok | 54 |
| 227 | phase | open every resource in 00 | ok | 28 |
| 228 | phase | open every resource in 01 | ok | 45 |
| 229 | phase | open every resource in 02 | ok | 37 |
| 230 | phase | open every resource in 03 | ok | 36 |
| 231 | phase | open every resource in 04 | ok | 33 |
| 232 | phase | open every resource in 05 | ok | 42 |
| 233 | phase | open every resource in 06 | ok | 26 |
| 234 | phase | open every resource in 07 | ok | 39 |
| 235 | phase | open every resource in 08 | ok | 33 |
| 236 | phase | open every resource in 09 | ok | 41 |
| 237 | phase | open every resource in 10 | ok | 36 |
| 238 | phase | open every resource in 11 | ok | 36 |
| 239 | phase | open every resource in 12 | ok | 30 |
| 240 | phase | open every resource in 13 | ok | 39 |
| 241 | phase | open every resource in 14 | ok | 38 |
| 242 | phase | open every resource in 15 | ok | 41 |
| 243 | phase | open every resource in 16 | ok | 30 |
| 244 | phase | open every resource in 17 | ok | 66 |
| 245 | phase | open every resource in 18 | ok | 45 |
| 246 | phase | open every resource in 99 | ok | 28 |
| 247 | phase | use the jump row and snippet on OS | ok | 0 |
| 248 | phase | use the jump row and snippet on 00 | ok | 1884 |
| 249 | phase | use the jump row and snippet on 01 | ok | 420 |
| 250 | phase | use the jump row and snippet on 02 | ok | 412 |
| 251 | phase | use the jump row and snippet on 03 | ok | 435 |
| 252 | phase | use the jump row and snippet on 04 | ok | 403 |
| 253 | phase | use the jump row and snippet on 05 | ok | 360 |
| 254 | phase | use the jump row and snippet on 06 | ok | 387 |
| 255 | phase | use the jump row and snippet on 07 | ok | 395 |
| 256 | phase | use the jump row and snippet on 08 | ok | 362 |
| 257 | phase | use the jump row and snippet on 09 | ok | 415 |
| 258 | phase | use the jump row and snippet on 10 | ok | 397 |
| 259 | phase | use the jump row and snippet on 11 | ok | 408 |
| 260 | phase | use the jump row and snippet on 12 | ok | 399 |
| 261 | phase | use the jump row and snippet on 13 | ok | 438 |
| 262 | phase | use the jump row and snippet on 14 | ok | 541 |
| 263 | phase | use the jump row and snippet on 15 | ok | 438 |
| 264 | phase | use the jump row and snippet on 16 | ok | 380 |
| 265 | phase | use the jump row and snippet on 17 | ok | 446 |
| 266 | phase | use the jump row and snippet on 18 | ok | 267 |
| 267 | phase | use the jump row and snippet on 99 | ok | 138 |
| 268 | phase | send a line to the review deck from the right click menu | ok | 281 |
| 269 | phase | type a note in each phase and leave at once | slow (4059 ms) | 4059 |
| 270 | phase | the pending note is committed on quit | ok | 337 |
| 271 | practice | filter the list by every phase | ok | 358 |
| 272 | practice | switch the status filter three ways | ok | 70 |
| 273 | practice | walk the list with Next exercise | ok | 65 |
| 274 | practice | run an endless loop and wait it out | ok | 3363 |
| 275 | practice | ask for the solution before passing | ok | 6 |
| 276 | practice | insist on the solution | ok | 30 |
| 277 | practice | type, then press Reset | ok | 14 |
| 278 | practice | p01.001: read the brief | ok | 0 |
| 279 | practice | p01.001: reveal every hint | ok | 24 |
| 280 | practice | p01.001: run an empty editor | ok | 216 |
| 281 | practice | p01.001: run the untouched starter | ok | 239 |
| 282 | practice | p01.001: run the reference solution | ok | 265 |
| 283 | practice | p01.001: read the solution once passed | ok | 26 |
| 284 | practice | p01.002: read the brief | ok | 0 |
| 285 | practice | p01.002: reveal every hint | ok | 21 |
| 286 | practice | p01.002: run an empty editor | ok | 250 |
| 287 | practice | p01.002: run the untouched starter | ok | 274 |
| 288 | practice | p01.002: run the reference solution | ok | 300 |
| 289 | practice | p01.002: read the solution once passed | ok | 40 |
| 290 | practice | p01.003: read the brief | ok | 0 |
| 291 | practice | p01.003: reveal every hint | ok | 10 |
| 292 | practice | p01.003: run an empty editor | ok | 234 |
| 293 | practice | p01.003: run the untouched starter | ok | 278 |
| 294 | practice | p01.003: run the reference solution | ok | 296 |
| 295 | practice | p01.003: read the solution once passed | ok | 49 |
| 296 | practice | p01.004: read the brief | ok | 0 |
| 297 | practice | p01.004: reveal every hint | ok | 12 |
| 298 | practice | p01.004: run an empty editor | ok | 252 |
| 299 | practice | p01.004: run the untouched starter | ok | 277 |
| 300 | practice | p01.004: run the reference solution | ok | 275 |
| 301 | practice | p01.004: read the solution once passed | ok | 45 |
| 302 | practice | p01.005: read the brief | ok | 0 |
| 303 | practice | p01.005: reveal every hint | ok | 19 |
| 304 | practice | p01.005: run an empty editor | ok | 210 |
| 305 | practice | p01.005: run the untouched starter | ok | 244 |
| 306 | practice | p01.005: run the reference solution | ok | 268 |
| 307 | practice | p01.005: read the solution once passed | ok | 37 |
| 308 | practice | p01.006: read the brief | ok | 0 |
| 309 | practice | p01.006: reveal every hint | ok | 16 |
| 310 | practice | p01.006: run an empty editor | ok | 219 |
| 311 | practice | p01.006: run the untouched starter | ok | 263 |
| 312 | practice | p01.006: run the reference solution | ok | 265 |
| 313 | practice | p01.006: read the solution once passed | ok | 49 |
| 314 | practice | p01.007: read the brief | ok | 0 |
| 315 | practice | p01.007: reveal every hint | ok | 21 |
| 316 | practice | p01.007: run an empty editor | ok | 219 |
| 317 | practice | p01.007: run the untouched starter | ok | 233 |
| 318 | practice | p01.007: run the reference solution | ok | 276 |
| 319 | practice | p01.007: read the solution once passed | ok | 32 |
| 320 | practice | p01.008: read the brief | ok | 0 |
| 321 | practice | p01.008: reveal every hint | ok | 14 |
| 322 | practice | p01.008: run an empty editor | ok | 232 |
| 323 | practice | p01.008: run the untouched starter | ok | 307 |
| 324 | practice | p01.008: run the reference solution | ok | 312 |
| 325 | practice | p01.008: read the solution once passed | ok | 41 |
| 326 | practice | p01.009: read the brief | ok | 0 |
| 327 | practice | p01.009: reveal every hint | ok | 25 |
| 328 | practice | p01.009: run an empty editor | ok | 265 |
| 329 | practice | p01.009: run the untouched starter | ok | 258 |
| 330 | practice | p01.009: run the reference solution | ok | 261 |
| 331 | practice | p01.009: read the solution once passed | ok | 42 |
| 332 | practice | p01.010: read the brief | ok | 0 |
| 333 | practice | p01.010: reveal every hint | ok | 20 |
| 334 | practice | p01.010: run an empty editor | ok | 296 |
| 335 | practice | p01.010: run the untouched starter | ok | 233 |
| 336 | practice | p01.010: run the reference solution | ok | 239 |
| 337 | practice | p01.010: read the solution once passed | ok | 41 |
| 338 | practice | p01.011: read the brief | ok | 0 |
| 339 | practice | p01.011: reveal every hint | ok | 20 |
| 340 | practice | p01.011: run an empty editor | ok | 206 |
| 341 | practice | p01.011: run the untouched starter | ok | 261 |
| 342 | practice | p01.011: run the reference solution | ok | 230 |
| 343 | practice | p01.011: read the solution once passed | ok | 42 |
| 344 | practice | p01.012: read the brief | ok | 0 |
| 345 | practice | p01.012: reveal every hint | ok | 17 |
| 346 | practice | p01.012: run an empty editor | ok | 212 |
| 347 | practice | p01.012: run the untouched starter | ok | 269 |
| 348 | practice | p01.012: run the reference solution | ok | 269 |
| 349 | practice | p01.012: read the solution once passed | ok | 36 |
| 350 | practice | p01.013: read the brief | ok | 0 |
| 351 | practice | p01.013: reveal every hint | ok | 15 |
| 352 | practice | p01.013: run an empty editor | ok | 216 |
| 353 | practice | p01.013: run the untouched starter | ok | 247 |
| 354 | practice | p01.013: run the reference solution | ok | 256 |
| 355 | practice | p01.013: read the solution once passed | ok | 29 |
| 356 | practice | p01.014: read the brief | ok | 0 |
| 357 | practice | p01.014: reveal every hint | ok | 21 |
| 358 | practice | p01.014: run an empty editor | ok | 240 |
| 359 | practice | p01.014: run the untouched starter | ok | 337 |
| 360 | practice | p01.014: run the reference solution | ok | 284 |
| 361 | practice | p01.014: read the solution once passed | ok | 51 |
| 362 | practice | p01.015: read the brief | ok | 0 |
| 363 | practice | p01.015: reveal every hint | ok | 17 |
| 364 | practice | p01.015: run an empty editor | ok | 202 |
| 365 | practice | p01.015: run the untouched starter | ok | 231 |
| 366 | practice | p01.015: run the reference solution | ok | 236 |
| 367 | practice | p01.015: read the solution once passed | ok | 49 |
| 368 | practice | p01.016: read the brief | ok | 0 |
| 369 | practice | p01.016: reveal every hint | ok | 17 |
| 370 | practice | p01.016: run an empty editor | ok | 227 |
| 371 | practice | p01.016: run the untouched starter | ok | 240 |
| 372 | practice | p01.016: run the reference solution | ok | 264 |
| 373 | practice | p01.016: read the solution once passed | ok | 62 |
| 374 | practice | p01.017: read the brief | ok | 0 |
| 375 | practice | p01.017: reveal every hint | ok | 15 |
| 376 | practice | p01.017: run an empty editor | ok | 190 |
| 377 | practice | p01.017: run the untouched starter | ok | 293 |
| 378 | practice | p01.017: run the reference solution | ok | 280 |
| 379 | practice | p01.017: read the solution once passed | ok | 52 |
| 380 | practice | p01.018: read the brief | ok | 0 |
| 381 | practice | p01.018: reveal every hint | ok | 18 |
| 382 | practice | p01.018: run an empty editor | ok | 215 |
| 383 | practice | p01.018: run the untouched starter | ok | 281 |
| 384 | practice | p01.018: run the reference solution | ok | 259 |
| 385 | practice | p01.018: read the solution once passed | ok | 40 |
| 386 | practice | p01.019: read the brief | ok | 0 |
| 387 | practice | p01.019: reveal every hint | ok | 15 |
| 388 | practice | p01.019: run an empty editor | ok | 198 |
| 389 | practice | p01.019: run the untouched starter | ok | 248 |
| 390 | practice | p01.019: run the reference solution | ok | 291 |
| 391 | practice | p01.019: read the solution once passed | ok | 40 |
| 392 | practice | p01.020: read the brief | ok | 0 |
| 393 | practice | p01.020: reveal every hint | ok | 21 |
| 394 | practice | p01.020: run an empty editor | ok | 248 |
| 395 | practice | p01.020: run the untouched starter | ok | 338 |
| 396 | practice | p01.020: run the reference solution | ok | 262 |
| 397 | practice | p01.020: read the solution once passed | ok | 37 |
| 398 | practice | p01.021: read the brief | ok | 0 |
| 399 | practice | p01.021: reveal every hint | ok | 17 |
| 400 | practice | p01.021: run an empty editor | ok | 293 |
| 401 | practice | p01.021: run the untouched starter | ok | 330 |
| 402 | practice | p01.021: run the reference solution | ok | 274 |
| 403 | practice | p01.021: read the solution once passed | ok | 39 |
| 404 | practice | p01.022: read the brief | ok | 0 |
| 405 | practice | p01.022: reveal every hint | ok | 18 |
| 406 | practice | p01.022: run an empty editor | ok | 231 |
| 407 | practice | p01.022: run the untouched starter | ok | 307 |
| 408 | practice | p01.022: run the reference solution | ok | 237 |
| 409 | practice | p01.022: read the solution once passed | ok | 31 |
| 410 | practice | p01.023: read the brief | ok | 0 |
| 411 | practice | p01.023: reveal every hint | ok | 19 |
| 412 | practice | p01.023: run an empty editor | ok | 208 |
| 413 | practice | p01.023: run the untouched starter | ok | 269 |
| 414 | practice | p01.023: run the reference solution | ok | 276 |
| 415 | practice | p01.023: read the solution once passed | ok | 39 |
| 416 | practice | p01.024: read the brief | ok | 0 |
| 417 | practice | p01.024: reveal every hint | ok | 21 |
| 418 | practice | p01.024: run an empty editor | ok | 295 |
| 419 | practice | p01.024: run the untouched starter | ok | 287 |
| 420 | practice | p01.024: run the reference solution | ok | 289 |
| 421 | practice | p01.024: read the solution once passed | ok | 40 |
| 422 | practice | p01.025: read the brief | ok | 0 |
| 423 | practice | p01.025: reveal every hint | ok | 16 |
| 424 | practice | p01.025: run an empty editor | ok | 205 |
| 425 | practice | p01.025: run the untouched starter | ok | 261 |
| 426 | practice | p01.025: run the reference solution | ok | 293 |
| 427 | practice | p01.025: read the solution once passed | ok | 53 |
| 428 | practice | p01.026: read the brief | ok | 0 |
| 429 | practice | p01.026: reveal every hint | ok | 20 |
| 430 | practice | p01.026: run an empty editor | ok | 229 |
| 431 | practice | p01.026: run the untouched starter | ok | 284 |
| 432 | practice | p01.026: run the reference solution | ok | 242 |
| 433 | practice | p01.026: read the solution once passed | ok | 44 |
| 434 | practice | p01.027: read the brief | ok | 0 |
| 435 | practice | p01.027: reveal every hint | ok | 18 |
| 436 | practice | p01.027: run an empty editor | ok | 220 |
| 437 | practice | p01.027: run the untouched starter | ok | 249 |
| 438 | practice | p01.027: run the reference solution | ok | 252 |
| 439 | practice | p01.027: read the solution once passed | ok | 38 |
| 440 | practice | p01.028: read the brief | ok | 0 |
| 441 | practice | p01.028: reveal every hint | ok | 15 |
| 442 | practice | p01.028: run an empty editor | ok | 221 |
| 443 | practice | p01.028: run the untouched starter | ok | 341 |
| 444 | practice | p01.028: run the reference solution | ok | 268 |
| 445 | practice | p01.028: read the solution once passed | ok | 41 |
| 446 | practice | p01.029: read the brief | ok | 0 |
| 447 | practice | p01.029: reveal every hint | ok | 17 |
| 448 | practice | p01.029: run an empty editor | ok | 255 |
| 449 | practice | p01.029: run the untouched starter | ok | 286 |
| 450 | practice | p01.029: run the reference solution | ok | 259 |
| 451 | practice | p01.029: read the solution once passed | ok | 40 |
| 452 | practice | p01.030: read the brief | ok | 0 |
| 453 | practice | p01.030: reveal every hint | ok | 12 |
| 454 | practice | p01.030: run an empty editor | ok | 283 |
| 455 | practice | p01.030: run the untouched starter | ok | 285 |
| 456 | practice | p01.030: run the reference solution | ok | 296 |
| 457 | practice | p01.030: read the solution once passed | ok | 35 |
| 458 | practice | p01.031: read the brief | ok | 0 |
| 459 | practice | p01.031: reveal every hint | ok | 29 |
| 460 | practice | p01.031: run an empty editor | ok | 226 |
| 461 | practice | p01.031: run the untouched starter | ok | 326 |
| 462 | practice | p01.031: run the reference solution | ok | 279 |
| 463 | practice | p01.031: read the solution once passed | ok | 44 |
| 464 | practice | p01.032: read the brief | ok | 0 |
| 465 | practice | p01.032: reveal every hint | ok | 17 |
| 466 | practice | p01.032: run an empty editor | ok | 201 |
| 467 | practice | p01.032: run the untouched starter | ok | 305 |
| 468 | practice | p01.032: run the reference solution | ok | 295 |
| 469 | practice | p01.032: read the solution once passed | ok | 39 |
| 470 | practice | p01.033: read the brief | ok | 0 |
| 471 | practice | p01.033: reveal every hint | ok | 16 |
| 472 | practice | p01.033: run an empty editor | ok | 253 |
| 473 | practice | p01.033: run the untouched starter | ok | 268 |
| 474 | practice | p01.033: run the reference solution | ok | 266 |
| 475 | practice | p01.033: read the solution once passed | ok | 32 |
| 476 | practice | p01.034: read the brief | ok | 0 |
| 477 | practice | p01.034: reveal every hint | ok | 17 |
| 478 | practice | p01.034: run an empty editor | ok | 249 |
| 479 | practice | p01.034: run the untouched starter | ok | 281 |
| 480 | practice | p01.034: run the reference solution | ok | 293 |
| 481 | practice | p01.034: read the solution once passed | ok | 48 |
| 482 | practice | p01.035: read the brief | ok | 0 |
| 483 | practice | p01.035: reveal every hint | ok | 18 |
| 484 | practice | p01.035: run an empty editor | ok | 213 |
| 485 | practice | p01.035: run the untouched starter | ok | 244 |
| 486 | practice | p01.035: run the reference solution | ok | 236 |
| 487 | practice | p01.035: read the solution once passed | ok | 51 |
| 488 | practice | p01.036: read the brief | ok | 0 |
| 489 | practice | p01.036: reveal every hint | ok | 15 |
| 490 | practice | p01.036: run an empty editor | ok | 231 |
| 491 | practice | p01.036: run the untouched starter | ok | 269 |
| 492 | practice | p01.036: run the reference solution | ok | 251 |
| 493 | practice | p01.036: read the solution once passed | ok | 38 |
| 494 | practice | p02.001: read the brief | ok | 0 |
| 495 | practice | p02.001: reveal every hint | ok | 19 |
| 496 | practice | p02.001: run an empty editor | ok | 197 |
| 497 | practice | p02.001: run the untouched starter | ok | 295 |
| 498 | practice | p02.001: run the reference solution | ok | 292 |
| 499 | practice | p02.001: read the solution once passed | ok | 45 |
| 500 | practice | p02.002: read the brief | ok | 0 |
| 501 | practice | p02.002: reveal every hint | ok | 20 |
| 502 | practice | p02.002: run an empty editor | ok | 240 |
| 503 | practice | p02.002: run the untouched starter | ok | 314 |
| 504 | practice | p02.002: run the reference solution | ok | 280 |
| 505 | practice | p02.002: read the solution once passed | ok | 40 |
| 506 | practice | p02.003: read the brief | ok | 0 |
| 507 | practice | p02.003: reveal every hint | ok | 17 |
| 508 | practice | p02.003: run an empty editor | ok | 204 |
| 509 | practice | p02.003: run the untouched starter | ok | 280 |
| 510 | practice | p02.003: run the reference solution | ok | 258 |
| 511 | practice | p02.003: read the solution once passed | ok | 35 |
| 512 | practice | p02.004: read the brief | ok | 0 |
| 513 | practice | p02.004: reveal every hint | ok | 19 |
| 514 | practice | p02.004: run an empty editor | ok | 228 |
| 515 | practice | p02.004: run the untouched starter | ok | 290 |
| 516 | practice | p02.004: run the reference solution | ok | 279 |
| 517 | practice | p02.004: read the solution once passed | ok | 35 |
| 518 | practice | p02.005: read the brief | ok | 0 |
| 519 | practice | p02.005: reveal every hint | ok | 17 |
| 520 | practice | p02.005: run an empty editor | ok | 226 |
| 521 | practice | p02.005: run the untouched starter | ok | 256 |
| 522 | practice | p02.005: run the reference solution | ok | 240 |
| 523 | practice | p02.005: read the solution once passed | ok | 36 |
| 524 | practice | p02.006: read the brief | ok | 0 |
| 525 | practice | p02.006: reveal every hint | ok | 37 |
| 526 | practice | p02.006: run an empty editor | ok | 231 |
| 527 | practice | p02.006: run the untouched starter | ok | 290 |
| 528 | practice | p02.006: run the reference solution | ok | 298 |
| 529 | practice | p02.006: read the solution once passed | ok | 33 |
| 530 | practice | p02.007: read the brief | ok | 0 |
| 531 | practice | p02.007: reveal every hint | ok | 26 |
| 532 | practice | p02.007: run an empty editor | ok | 215 |
| 533 | practice | p02.007: run the untouched starter | ok | 228 |
| 534 | practice | p02.007: run the reference solution | ok | 282 |
| 535 | practice | p02.007: read the solution once passed | ok | 38 |
| 536 | practice | p02.008: read the brief | ok | 0 |
| 537 | practice | p02.008: reveal every hint | ok | 20 |
| 538 | practice | p02.008: run an empty editor | ok | 252 |
| 539 | practice | p02.008: run the untouched starter | ok | 258 |
| 540 | practice | p02.008: run the reference solution | ok | 321 |
| 541 | practice | p02.008: read the solution once passed | ok | 50 |
| 542 | practice | p02.009: read the brief | ok | 0 |
| 543 | practice | p02.009: reveal every hint | ok | 18 |
| 544 | practice | p02.009: run an empty editor | ok | 248 |
| 545 | practice | p02.009: run the untouched starter | ok | 273 |
| 546 | practice | p02.009: run the reference solution | ok | 302 |
| 547 | practice | p02.009: read the solution once passed | ok | 63 |
| 548 | practice | p02.010: read the brief | ok | 0 |
| 549 | practice | p02.010: reveal every hint | ok | 21 |
| 550 | practice | p02.010: run an empty editor | ok | 224 |
| 551 | practice | p02.010: run the untouched starter | ok | 254 |
| 552 | practice | p02.010: run the reference solution | ok | 243 |
| 553 | practice | p02.010: read the solution once passed | ok | 50 |
| 554 | practice | p02.011: read the brief | ok | 0 |
| 555 | practice | p02.011: reveal every hint | ok | 21 |
| 556 | practice | p02.011: run an empty editor | ok | 224 |
| 557 | practice | p02.011: run the untouched starter | ok | 280 |
| 558 | practice | p02.011: run the reference solution | ok | 274 |
| 559 | practice | p02.011: read the solution once passed | ok | 52 |
| 560 | practice | p02.012: read the brief | ok | 0 |
| 561 | practice | p02.012: reveal every hint | ok | 19 |
| 562 | practice | p02.012: run an empty editor | ok | 226 |
| 563 | practice | p02.012: run the untouched starter | ok | 209 |
| 564 | practice | p02.012: run the reference solution | ok | 250 |
| 565 | practice | p02.012: read the solution once passed | ok | 42 |
| 566 | practice | p02.013: read the brief | ok | 0 |
| 567 | practice | p02.013: reveal every hint | ok | 26 |
| 568 | practice | p02.013: run an empty editor | ok | 240 |
| 569 | practice | p02.013: run the untouched starter | ok | 252 |
| 570 | practice | p02.013: run the reference solution | ok | 268 |
| 571 | practice | p02.013: read the solution once passed | ok | 37 |
| 572 | practice | p02.014: read the brief | ok | 0 |
| 573 | practice | p02.014: reveal every hint | ok | 19 |
| 574 | practice | p02.014: run an empty editor | ok | 291 |
| 575 | practice | p02.014: run the untouched starter | ok | 280 |
| 576 | practice | p02.014: run the reference solution | ok | 302 |
| 577 | practice | p02.014: read the solution once passed | ok | 40 |
| 578 | practice | p02.015: read the brief | ok | 0 |
| 579 | practice | p02.015: reveal every hint | ok | 19 |
| 580 | practice | p02.015: run an empty editor | ok | 247 |
| 581 | practice | p02.015: run the untouched starter | ok | 306 |
| 582 | practice | p02.015: run the reference solution | ok | 274 |
| 583 | practice | p02.015: read the solution once passed | ok | 52 |
| 584 | practice | p02.016: read the brief | ok | 0 |
| 585 | practice | p02.016: reveal every hint | ok | 17 |
| 586 | practice | p02.016: run an empty editor | ok | 239 |
| 587 | practice | p02.016: run the untouched starter | ok | 301 |
| 588 | practice | p02.016: run the reference solution | ok | 264 |
| 589 | practice | p02.016: read the solution once passed | ok | 38 |
| 590 | practice | p04.011: read the brief | ok | 0 |
| 591 | practice | p04.011: reveal every hint | ok | 28 |
| 592 | practice | p04.011: run an empty editor | ok | 240 |
| 593 | practice | p04.011: run the untouched starter | ok | 243 |
| 594 | practice | p04.011: run the reference solution | ok | 298 |
| 595 | practice | p04.011: read the solution once passed | ok | 40 |
| 596 | practice | p04.012: read the brief | ok | 0 |
| 597 | practice | p04.012: reveal every hint | ok | 47 |
| 598 | practice | p04.012: run an empty editor | ok | 231 |
| 599 | practice | p04.012: run the untouched starter | ok | 248 |
| 600 | practice | p04.012: run the reference solution | ok | 244 |
| 601 | practice | p04.012: read the solution once passed | ok | 45 |
| 602 | practice | p04.013: read the brief | ok | 0 |
| 603 | practice | p04.013: reveal every hint | ok | 21 |
| 604 | practice | p04.013: run an empty editor | ok | 224 |
| 605 | practice | p04.013: run the untouched starter | ok | 286 |
| 606 | practice | p04.013: run the reference solution | ok | 216 |
| 607 | practice | p04.013: read the solution once passed | ok | 48 |
| 608 | practice | p04.001: read the brief | ok | 0 |
| 609 | practice | p04.001: reveal every hint | ok | 11 |
| 610 | practice | p04.001: run an empty editor | ok | 201 |
| 611 | practice | p04.001: run the untouched starter | ok | 257 |
| 612 | practice | p04.001: run the reference solution | ok | 265 |
| 613 | practice | p04.001: read the solution once passed | ok | 42 |
| 614 | practice | p04.002: read the brief | ok | 0 |
| 615 | practice | p04.002: reveal every hint | ok | 23 |
| 616 | practice | p04.002: run an empty editor | ok | 227 |
| 617 | practice | p04.002: run the untouched starter | ok | 300 |
| 618 | practice | p04.002: run the reference solution | ok | 287 |
| 619 | practice | p04.002: read the solution once passed | ok | 39 |
| 620 | practice | p04.003: read the brief | ok | 0 |
| 621 | practice | p04.003: reveal every hint | ok | 23 |
| 622 | practice | p04.003: run an empty editor | ok | 258 |
| 623 | practice | p04.003: run the untouched starter | ok | 266 |
| 624 | practice | p04.003: run the reference solution | ok | 247 |
| 625 | practice | p04.003: read the solution once passed | ok | 49 |
| 626 | practice | p04.004: read the brief | ok | 0 |
| 627 | practice | p04.004: reveal every hint | ok | 17 |
| 628 | practice | p04.004: run an empty editor | ok | 301 |
| 629 | practice | p04.004: run the untouched starter | ok | 244 |
| 630 | practice | p04.004: run the reference solution | ok | 285 |
| 631 | practice | p04.004: read the solution once passed | ok | 43 |
| 632 | practice | p04.005: read the brief | ok | 0 |
| 633 | practice | p04.005: reveal every hint | ok | 16 |
| 634 | practice | p04.005: run an empty editor | ok | 265 |
| 635 | practice | p04.005: run the untouched starter | ok | 242 |
| 636 | practice | p04.005: run the reference solution | ok | 282 |
| 637 | practice | p04.005: read the solution once passed | ok | 46 |
| 638 | practice | p04.006: read the brief | ok | 0 |
| 639 | practice | p04.006: reveal every hint | ok | 20 |
| 640 | practice | p04.006: run an empty editor | ok | 246 |
| 641 | practice | p04.006: run the untouched starter | ok | 237 |
| 642 | practice | p04.006: run the reference solution | ok | 260 |
| 643 | practice | p04.006: read the solution once passed | ok | 38 |
| 644 | practice | p04.007: read the brief | ok | 0 |
| 645 | practice | p04.007: reveal every hint | ok | 21 |
| 646 | practice | p04.007: run an empty editor | ok | 229 |
| 647 | practice | p04.007: run the untouched starter | ok | 269 |
| 648 | practice | p04.007: run the reference solution | ok | 318 |
| 649 | practice | p04.007: read the solution once passed | ok | 35 |
| 650 | practice | p04.008: read the brief | ok | 0 |
| 651 | practice | p04.008: reveal every hint | ok | 19 |
| 652 | practice | p04.008: run an empty editor | ok | 225 |
| 653 | practice | p04.008: run the untouched starter | ok | 407 |
| 654 | practice | p04.008: run the reference solution | ok | 234 |
| 655 | practice | p04.008: read the solution once passed | ok | 49 |
| 656 | practice | p04.009: read the brief | ok | 0 |
| 657 | practice | p04.009: reveal every hint | ok | 20 |
| 658 | practice | p04.009: run an empty editor | ok | 219 |
| 659 | practice | p04.009: run the untouched starter | ok | 289 |
| 660 | practice | p04.009: run the reference solution | ok | 266 |
| 661 | practice | p04.009: read the solution once passed | ok | 38 |
| 662 | practice | p04.010: read the brief | ok | 0 |
| 663 | practice | p04.010: reveal every hint | ok | 15 |
| 664 | practice | p04.010: run an empty editor | ok | 206 |
| 665 | practice | p04.010: run the untouched starter | ok | 234 |
| 666 | practice | p04.010: run the reference solution | ok | 290 |
| 667 | practice | p04.010: read the solution once passed | ok | 55 |
| 668 | practice | p05.001: read the brief | ok | 0 |
| 669 | practice | p05.001: reveal every hint | ok | 16 |
| 670 | practice | p05.001: run an empty editor | ok | 252 |
| 671 | practice | p05.001: run the untouched starter | ok | 349 |
| 672 | practice | p05.001: run the reference solution | ok | 257 |
| 673 | practice | p05.001: read the solution once passed | ok | 22 |
| 674 | practice | p05.002: read the brief | ok | 0 |
| 675 | practice | p05.002: reveal every hint | ok | 22 |
| 676 | practice | p05.002: run an empty editor | ok | 269 |
| 677 | practice | p05.002: run the untouched starter | ok | 266 |
| 678 | practice | p05.002: run the reference solution | ok | 266 |
| 679 | practice | p05.002: read the solution once passed | ok | 40 |
| 680 | practice | p05.003: read the brief | ok | 0 |
| 681 | practice | p05.003: reveal every hint | ok | 21 |
| 682 | practice | p05.003: run an empty editor | ok | 219 |
| 683 | practice | p05.003: run the untouched starter | ok | 259 |
| 684 | practice | p05.003: run the reference solution | ok | 277 |
| 685 | practice | p05.003: read the solution once passed | ok | 30 |
| 686 | practice | p05.004: read the brief | ok | 0 |
| 687 | practice | p05.004: reveal every hint | ok | 20 |
| 688 | practice | p05.004: run an empty editor | ok | 231 |
| 689 | practice | p05.004: run the untouched starter | ok | 287 |
| 690 | practice | p05.004: run the reference solution | ok | 272 |
| 691 | practice | p05.004: read the solution once passed | ok | 37 |
| 692 | practice | p05.005: read the brief | ok | 0 |
| 693 | practice | p05.005: reveal every hint | ok | 8 |
| 694 | practice | p05.005: run an empty editor | ok | 225 |
| 695 | practice | p05.005: run the untouched starter | ok | 323 |
| 696 | practice | p05.005: run the reference solution | ok | 239 |
| 697 | practice | p05.005: read the solution once passed | ok | 27 |
| 698 | practice | p05.006: read the brief | ok | 0 |
| 699 | practice | p05.006: reveal every hint | ok | 12 |
| 700 | practice | p05.006: run an empty editor | ok | 225 |
| 701 | practice | p05.006: run the untouched starter | ok | 264 |
| 702 | practice | p05.006: run the reference solution | ok | 230 |
| 703 | practice | p05.006: read the solution once passed | ok | 41 |
| 704 | practice | p05.007: read the brief | ok | 0 |
| 705 | practice | p05.007: reveal every hint | ok | 16 |
| 706 | practice | p05.007: run an empty editor | ok | 277 |
| 707 | practice | p05.007: run the untouched starter | ok | 228 |
| 708 | practice | p05.007: run the reference solution | ok | 276 |
| 709 | practice | p05.007: read the solution once passed | ok | 46 |
| 710 | practice | p05.008: read the brief | ok | 0 |
| 711 | practice | p05.008: reveal every hint | ok | 36 |
| 712 | practice | p05.008: run an empty editor | ok | 363 |
| 713 | practice | p05.008: run the untouched starter | ok | 264 |
| 714 | practice | p05.008: run the reference solution | ok | 248 |
| 715 | practice | p05.008: read the solution once passed | ok | 45 |
| 716 | practice | p05.009: read the brief | ok | 0 |
| 717 | practice | p05.009: reveal every hint | ok | 20 |
| 718 | practice | p05.009: run an empty editor | ok | 204 |
| 719 | practice | p05.009: run the untouched starter | ok | 273 |
| 720 | practice | p05.009: run the reference solution | ok | 259 |
| 721 | practice | p05.009: read the solution once passed | ok | 36 |
| 722 | practice | p05.010: read the brief | ok | 0 |
| 723 | practice | p05.010: reveal every hint | ok | 24 |
| 724 | practice | p05.010: run an empty editor | ok | 222 |
| 725 | practice | p05.010: run the untouched starter | ok | 296 |
| 726 | practice | p05.010: run the reference solution | ok | 321 |
| 727 | practice | p05.010: read the solution once passed | ok | 37 |
| 728 | practice | p03.001: read the brief | ok | 0 |
| 729 | practice | p03.001: reveal every hint | ok | 21 |
| 730 | practice | p03.001: run an empty editor | ok | 273 |
| 731 | practice | p03.001: run the untouched starter | ok | 323 |
| 732 | practice | p03.001: run the reference solution | ok | 241 |
| 733 | practice | p03.001: read the solution once passed | ok | 36 |
| 734 | practice | p03.002: read the brief | ok | 0 |
| 735 | practice | p03.002: reveal every hint | ok | 16 |
| 736 | practice | p03.002: run an empty editor | ok | 279 |
| 737 | practice | p03.002: run the untouched starter | ok | 273 |
| 738 | practice | p03.002: run the reference solution | ok | 268 |
| 739 | practice | p03.002: read the solution once passed | ok | 27 |
| 740 | practice | p03.003: read the brief | ok | 0 |
| 741 | practice | p03.003: reveal every hint | ok | 24 |
| 742 | practice | p03.003: run an empty editor | ok | 282 |
| 743 | practice | p03.003: run the untouched starter | ok | 306 |
| 744 | practice | p03.003: run the reference solution | ok | 247 |
| 745 | practice | p03.003: read the solution once passed | ok | 40 |
| 746 | practice | p03.004: read the brief | ok | 0 |
| 747 | practice | p03.004: reveal every hint | ok | 21 |
| 748 | practice | p03.004: run an empty editor | ok | 254 |
| 749 | practice | p03.004: run the untouched starter | ok | 275 |
| 750 | practice | p03.004: run the reference solution | ok | 254 |
| 751 | practice | p03.004: read the solution once passed | ok | 32 |
| 752 | practice | p08.001: read the brief | ok | 0 |
| 753 | practice | p08.001: reveal every hint | ok | 22 |
| 754 | practice | p08.001: run an empty editor | ok | 291 |
| 755 | practice | p08.001: run the untouched starter | ok | 255 |
| 756 | practice | p08.001: run the reference solution | ok | 359 |
| 757 | practice | p08.001: read the solution once passed | ok | 37 |
| 758 | practice | p08.002: read the brief | ok | 0 |
| 759 | practice | p08.002: reveal every hint | ok | 22 |
| 760 | practice | p08.002: run an empty editor | ok | 229 |
| 761 | practice | p08.002: run the untouched starter | ok | 301 |
| 762 | practice | p08.002: run the reference solution | ok | 271 |
| 763 | practice | p08.002: read the solution once passed | ok | 35 |
| 764 | practice | p08.003: read the brief | ok | 0 |
| 765 | practice | p08.003: reveal every hint | ok | 18 |
| 766 | practice | p08.003: run an empty editor | ok | 262 |
| 767 | practice | p08.003: run the untouched starter | ok | 231 |
| 768 | practice | p08.003: run the reference solution | ok | 239 |
| 769 | practice | p08.003: read the solution once passed | ok | 40 |
| 770 | practice | p08.004: read the brief | ok | 0 |
| 771 | practice | p08.004: reveal every hint | ok | 18 |
| 772 | practice | p08.004: run an empty editor | ok | 216 |
| 773 | practice | p08.004: run the untouched starter | ok | 280 |
| 774 | practice | p08.004: run the reference solution | ok | 269 |
| 775 | practice | p08.004: read the solution once passed | ok | 37 |
| 776 | practice | p09.001: read the brief | ok | 0 |
| 777 | practice | p09.001: reveal every hint | ok | 20 |
| 778 | practice | p09.001: run an empty editor | ok | 241 |
| 779 | practice | p09.001: run the untouched starter | ok | 241 |
| 780 | practice | p09.001: run the reference solution | ok | 241 |
| 781 | practice | p09.001: read the solution once passed | ok | 39 |
| 782 | practice | p09.002: read the brief | ok | 0 |
| 783 | practice | p09.002: reveal every hint | ok | 18 |
| 784 | practice | p09.002: run an empty editor | ok | 229 |
| 785 | practice | p09.002: run the untouched starter | ok | 276 |
| 786 | practice | p09.002: run the reference solution | ok | 261 |
| 787 | practice | p09.002: read the solution once passed | ok | 38 |
| 788 | practice | p09.003: read the brief | ok | 0 |
| 789 | practice | p09.003: reveal every hint | ok | 19 |
| 790 | practice | p09.003: run an empty editor | ok | 239 |
| 791 | practice | p09.003: run the untouched starter | ok | 306 |
| 792 | practice | p09.003: run the reference solution | ok | 266 |
| 793 | practice | p09.003: read the solution once passed | ok | 37 |
| 794 | practice | p10.001: read the brief | ok | 0 |
| 795 | practice | p10.001: reveal every hint | ok | 24 |
| 796 | practice | p10.001: run an empty editor | ok | 225 |
| 797 | practice | p10.001: run the untouched starter | ok | 282 |
| 798 | practice | p10.001: run the reference solution | ok | 275 |
| 799 | practice | p10.001: read the solution once passed | ok | 32 |
| 800 | practice | p10.002: read the brief | ok | 0 |
| 801 | practice | p10.002: reveal every hint | ok | 16 |
| 802 | practice | p10.002: run an empty editor | ok | 263 |
| 803 | practice | p10.002: run the untouched starter | ok | 400 |
| 804 | practice | p10.002: run the reference solution | ok | 250 |
| 805 | practice | p10.002: read the solution once passed | ok | 39 |
| 806 | practice | p10.003: read the brief | ok | 0 |
| 807 | practice | p10.003: reveal every hint | ok | 21 |
| 808 | practice | p10.003: run an empty editor | ok | 243 |
| 809 | practice | p10.003: run the untouched starter | ok | 285 |
| 810 | practice | p10.003: run the reference solution | ok | 269 |
| 811 | practice | p10.003: read the solution once passed | ok | 36 |
| 812 | practice | p11.001: read the brief | ok | 0 |
| 813 | practice | p11.001: reveal every hint | ok | 12 |
| 814 | practice | p11.001: run an empty editor | ok | 417 |
| 815 | practice | p11.001: run the untouched starter | ok | 408 |
| 816 | practice | p11.001: run the reference solution | ok | 520 |
| 817 | practice | p11.001: read the solution once passed | ok | 29 |
| 818 | practice | p11.002: read the brief | ok | 0 |
| 819 | practice | p11.002: reveal every hint | ok | 17 |
| 820 | practice | p11.002: run an empty editor | ok | 417 |
| 821 | practice | p11.002: run the untouched starter | ok | 446 |
| 822 | practice | p11.002: run the reference solution | ok | 841 |
| 823 | practice | p11.002: read the solution once passed | ok | 42 |
| 824 | practice | p11.003: read the brief | ok | 0 |
| 825 | practice | p11.003: reveal every hint | ok | 20 |
| 826 | practice | p11.003: run an empty editor | ok | 400 |
| 827 | practice | p11.003: run the untouched starter | ok | 422 |
| 828 | practice | p11.003: run the reference solution | ok | 520 |
| 829 | practice | p11.003: read the solution once passed | ok | 29 |
| 830 | practice | p13.001: read the brief | ok | 0 |
| 831 | practice | p13.001: reveal every hint | ok | 16 |
| 832 | practice | p13.001: run an empty editor | ok | 258 |
| 833 | practice | p13.001: run the untouched starter | ok | 275 |
| 834 | practice | p13.001: run the reference solution | ok | 806 |
| 835 | practice | p13.001: read the solution once passed | ok | 43 |
| 836 | practice | p13.002: read the brief | ok | 0 |
| 837 | practice | p13.002: reveal every hint | ok | 18 |
| 838 | practice | p13.002: run an empty editor | ok | 249 |
| 839 | practice | p13.002: run the untouched starter | ok | 271 |
| 840 | practice | p13.002: run the reference solution | ok | 277 |
| 841 | practice | p13.002: read the solution once passed | ok | 45 |
| 842 | practice | p13.003: read the brief | ok | 0 |
| 843 | practice | p13.003: reveal every hint | ok | 25 |
| 844 | practice | p13.003: run an empty editor | ok | 264 |
| 845 | practice | p13.003: run the untouched starter | ok | 266 |
| 846 | practice | p13.003: run the reference solution | ok | 248 |
| 847 | practice | p13.003: read the solution once passed | ok | 32 |
| 848 | practice | p14.001: read the brief | ok | 0 |
| 849 | practice | p14.001: reveal every hint | ok | 19 |
| 850 | practice | p14.001: run an empty editor | ok | 212 |
| 851 | practice | p14.001: run the untouched starter | ok | 288 |
| 852 | practice | p14.001: run the reference solution | ok | 300 |
| 853 | practice | p14.001: read the solution once passed | ok | 26 |
| 854 | practice | p14.002: read the brief | ok | 0 |
| 855 | practice | p14.002: reveal every hint | ok | 20 |
| 856 | practice | p14.002: run an empty editor | ok | 233 |
| 857 | practice | p14.002: run the untouched starter | ok | 281 |
| 858 | practice | p14.002: run the reference solution | ok | 232 |
| 859 | practice | p14.002: read the solution once passed | ok | 20 |
| 860 | practice | p14.003: read the brief | ok | 0 |
| 861 | practice | p14.003: reveal every hint | ok | 18 |
| 862 | practice | p14.003: run an empty editor | ok | 252 |
| 863 | practice | p14.003: run the untouched starter | ok | 276 |
| 864 | practice | p14.003: run the reference solution | ok | 297 |
| 865 | practice | p14.003: read the solution once passed | ok | 34 |
| 866 | practice | p14.004: read the brief | ok | 0 |
| 867 | practice | p14.004: reveal every hint | ok | 16 |
| 868 | practice | p14.004: run an empty editor | ok | 260 |
| 869 | practice | p14.004: run the untouched starter | ok | 284 |
| 870 | practice | p14.004: run the reference solution | ok | 268 |
| 871 | practice | p14.004: read the solution once passed | ok | 47 |
| 872 | practice | p06.001: read the brief | ok | 0 |
| 873 | practice | p06.001: reveal every hint | ok | 18 |
| 874 | practice | p06.001: run an empty editor | ok | 204 |
| 875 | practice | p06.001: run the untouched starter | ok | 236 |
| 876 | practice | p06.001: run the reference solution | ok | 269 |
| 877 | practice | p06.001: read the solution once passed | ok | 42 |
| 878 | practice | p06.002: read the brief | ok | 0 |
| 879 | practice | p06.002: reveal every hint | ok | 19 |
| 880 | practice | p06.002: run an empty editor | ok | 206 |
| 881 | practice | p06.002: run the untouched starter | ok | 342 |
| 882 | practice | p06.002: run the reference solution | ok | 244 |
| 883 | practice | p06.002: read the solution once passed | ok | 37 |
| 884 | practice | p06.003: read the brief | ok | 0 |
| 885 | practice | p06.003: reveal every hint | ok | 18 |
| 886 | practice | p06.003: run an empty editor | ok | 223 |
| 887 | practice | p06.003: run the untouched starter | ok | 260 |
| 888 | practice | p06.003: run the reference solution | ok | 250 |
| 889 | practice | p06.003: read the solution once passed | ok | 37 |
| 890 | practice | p06.004: read the brief | ok | 0 |
| 891 | practice | p06.004: reveal every hint | ok | 18 |
| 892 | practice | p06.004: run an empty editor | ok | 244 |
| 893 | practice | p06.004: run the untouched starter | ok | 321 |
| 894 | practice | p06.004: run the reference solution | ok | 264 |
| 895 | practice | p06.004: read the solution once passed | ok | 51 |
| 896 | practice | p07.001: read the brief | ok | 0 |
| 897 | practice | p07.001: reveal every hint | ok | 22 |
| 898 | practice | p07.001: run an empty editor | ok | 224 |
| 899 | practice | p07.001: run the untouched starter | ok | 220 |
| 900 | practice | p07.001: run the reference solution | ok | 264 |
| 901 | practice | p07.001: read the solution once passed | ok | 48 |
| 902 | practice | p07.002: read the brief | ok | 0 |
| 903 | practice | p07.002: reveal every hint | ok | 20 |
| 904 | practice | p07.002: run an empty editor | ok | 244 |
| 905 | practice | p07.002: run the untouched starter | ok | 257 |
| 906 | practice | p07.002: run the reference solution | ok | 251 |
| 907 | practice | p07.002: read the solution once passed | ok | 39 |
| 908 | practice | p07.003: read the brief | ok | 0 |
| 909 | practice | p07.003: reveal every hint | ok | 46 |
| 910 | practice | p07.003: run an empty editor | ok | 218 |
| 911 | practice | p07.003: run the untouched starter | ok | 246 |
| 912 | practice | p07.003: run the reference solution | ok | 274 |
| 913 | practice | p07.003: read the solution once passed | ok | 47 |
| 914 | practice | p07.004: read the brief | ok | 0 |
| 915 | practice | p07.004: reveal every hint | ok | 31 |
| 916 | practice | p07.004: run an empty editor | ok | 252 |
| 917 | practice | p07.004: run the untouched starter | ok | 300 |
| 918 | practice | p07.004: run the reference solution | ok | 302 |
| 919 | practice | p07.004: read the solution once passed | ok | 44 |
| 920 | practice | p12.001: read the brief | ok | 0 |
| 921 | practice | p12.001: reveal every hint | ok | 20 |
| 922 | practice | p12.001: run an empty editor | ok | 307 |
| 923 | practice | p12.001: run the untouched starter | ok | 263 |
| 924 | practice | p12.001: run the reference solution | ok | 281 |
| 925 | practice | p12.001: read the solution once passed | ok | 37 |
| 926 | practice | p12.002: read the brief | ok | 0 |
| 927 | practice | p12.002: reveal every hint | ok | 42 |
| 928 | practice | p12.002: run an empty editor | ok | 271 |
| 929 | practice | p12.002: run the untouched starter | ok | 246 |
| 930 | practice | p12.002: run the reference solution | ok | 239 |
| 931 | practice | p12.002: read the solution once passed | ok | 46 |
| 932 | practice | p12.003: read the brief | ok | 0 |
| 933 | practice | p12.003: reveal every hint | ok | 43 |
| 934 | practice | p12.003: run an empty editor | ok | 258 |
| 935 | practice | p12.003: run the untouched starter | ok | 298 |
| 936 | practice | p12.003: run the reference solution | ok | 248 |
| 937 | practice | p12.003: read the solution once passed | ok | 64 |
| 938 | practice | p15.001: read the brief | ok | 0 |
| 939 | practice | p15.001: reveal every hint | ok | 41 |
| 940 | practice | p15.001: run an empty editor | ok | 224 |
| 941 | practice | p15.001: run the untouched starter | ok | 300 |
| 942 | practice | p15.001: run the reference solution | ok | 286 |
| 943 | practice | p15.001: read the solution once passed | ok | 41 |
| 944 | practice | p15.002: read the brief | ok | 0 |
| 945 | practice | p15.002: reveal every hint | ok | 19 |
| 946 | practice | p15.002: run an empty editor | ok | 229 |
| 947 | practice | p15.002: run the untouched starter | ok | 209 |
| 948 | practice | p15.002: run the reference solution | ok | 270 |
| 949 | practice | p15.002: read the solution once passed | ok | 45 |
| 950 | practice | p15.003: read the brief | ok | 0 |
| 951 | practice | p15.003: reveal every hint | ok | 50 |
| 952 | practice | p15.003: run an empty editor | ok | 219 |
| 953 | practice | p15.003: run the untouched starter | ok | 284 |
| 954 | practice | p15.003: run the reference solution | ok | 312 |
| 955 | practice | p15.003: read the solution once passed | ok | 48 |
| 956 | practice | p16.001: read the brief | ok | 0 |
| 957 | practice | p16.001: reveal every hint | ok | 46 |
| 958 | practice | p16.001: run an empty editor | ok | 250 |
| 959 | practice | p16.001: run the untouched starter | ok | 309 |
| 960 | practice | p16.001: run the reference solution | ok | 267 |
| 961 | practice | p16.001: read the solution once passed | ok | 48 |
| 962 | practice | p16.002: read the brief | ok | 0 |
| 963 | practice | p16.002: reveal every hint | ok | 18 |
| 964 | practice | p16.002: run an empty editor | ok | 212 |
| 965 | practice | p16.002: run the untouched starter | ok | 300 |
| 966 | practice | p16.002: run the reference solution | ok | 287 |
| 967 | practice | p16.002: read the solution once passed | ok | 47 |
| 968 | practice | p16.003: read the brief | ok | 0 |
| 969 | practice | p16.003: reveal every hint | ok | 83 |
| 970 | practice | p16.003: run an empty editor | ok | 254 |
| 971 | practice | p16.003: run the untouched starter | ok | 261 |
| 972 | practice | p16.003: run the reference solution | ok | 270 |
| 973 | practice | p16.003: read the solution once passed | ok | 32 |
| 974 | practice | p17.001: read the brief | ok | 0 |
| 975 | practice | p17.001: reveal every hint | ok | 47 |
| 976 | practice | p17.001: run an empty editor | ok | 251 |
| 977 | practice | p17.001: run the untouched starter | ok | 318 |
| 978 | practice | p17.001: run the reference solution | ok | 298 |
| 979 | practice | p17.001: read the solution once passed | ok | 45 |
| 980 | practice | p17.002: read the brief | ok | 0 |
| 981 | practice | p17.002: reveal every hint | ok | 35 |
| 982 | practice | p17.002: run an empty editor | ok | 224 |
| 983 | practice | p17.002: run the untouched starter | ok | 265 |
| 984 | practice | p17.002: run the reference solution | ok | 258 |
| 985 | practice | p17.002: read the solution once passed | ok | 44 |
| 986 | practice | p17.003: read the brief | ok | 0 |
| 987 | practice | p17.003: reveal every hint | ok | 49 |
| 988 | practice | p17.003: run an empty editor | ok | 234 |
| 989 | practice | p17.003: run the untouched starter | ok | 293 |
| 990 | practice | p17.003: run the reference solution | ok | 237 |
| 991 | practice | p17.003: read the solution once passed | ok | 50 |
| 992 | practice | the counter agrees with the store | ok | 0 |
| 993 | practice | press Run checks and read the result | ok | 224 |
| 994 | practice | close the window while a run is in flight | ok | 12057 |
| 995 | quiz | read the quiz picker | ok | 0 |
| 996 | quiz | answer all 8 questions in q00 correctly | ok | 442 |
| 997 | quiz | answer all 18 questions in q01 correctly | ok | 909 |
| 998 | quiz | answer all 11 questions in q02 correctly | ok | 552 |
| 999 | quiz | answer all 8 questions in q03 correctly | ok | 395 |
| 1000 | quiz | answer all 18 questions in q04 correctly | ok | 956 |
| 1001 | quiz | answer all 12 questions in q05 correctly | ok | 604 |
| 1002 | quiz | answer all 12 questions in q06 correctly | ok | 727 |
| 1003 | quiz | answer all 13 questions in q07 correctly | ok | 733 |
| 1004 | quiz | answer all 14 questions in q08 correctly | ok | 889 |
| 1005 | quiz | answer all 13 questions in q09 correctly | ok | 761 |
| 1006 | quiz | answer all 12 questions in q10 correctly | ok | 632 |
| 1007 | quiz | answer all 10 questions in q11 correctly | ok | 539 |
| 1008 | quiz | answer all 8 questions in q12 correctly | ok | 393 |
| 1009 | quiz | answer all 9 questions in q13 correctly | ok | 494 |
| 1010 | quiz | answer all 10 questions in q14 correctly | ok | 570 |
| 1011 | quiz | answer all 18 questions in q15 correctly | ok | 1034 |
| 1012 | quiz | answer all 18 questions in q16 correctly | ok | 1058 |
| 1013 | quiz | answer all 14 questions in q17 correctly | ok | 829 |
| 1014 | quiz | answer all 8 questions in q18 correctly | ok | 411 |
| 1015 | quiz | answer all 8 questions in q99 correctly | ok | 487 |
| 1016 | quiz | get every question in q00 wrong | ok | 519 |
| 1017 | quiz | read the wrap-up for q00 | ok | 0 |
| 1018 | quiz | get every question in q01 wrong | ok | 1113 |
| 1019 | quiz | read the wrap-up for q01 | ok | 0 |
| 1020 | quiz | get every question in q02 wrong | ok | 644 |
| 1021 | quiz | read the wrap-up for q02 | ok | 0 |
| 1022 | quiz | get every question in q03 wrong | ok | 499 |
| 1023 | quiz | read the wrap-up for q03 | ok | 0 |
| 1024 | quiz | get every question in q04 wrong | ok | 1050 |
| 1025 | quiz | read the wrap-up for q04 | ok | 0 |
| 1026 | quiz | get every question in q05 wrong | ok | 681 |
| 1027 | quiz | read the wrap-up for q05 | ok | 0 |
| 1028 | quiz | get every question in q06 wrong | ok | 674 |
| 1029 | quiz | read the wrap-up for q06 | ok | 0 |
| 1030 | quiz | get every question in q07 wrong | ok | 731 |
| 1031 | quiz | read the wrap-up for q07 | ok | 0 |
| 1032 | quiz | get every question in q08 wrong | ok | 773 |
| 1033 | quiz | read the wrap-up for q08 | ok | 0 |
| 1034 | quiz | get every question in q09 wrong | ok | 757 |
| 1035 | quiz | read the wrap-up for q09 | ok | 0 |
| 1036 | quiz | get every question in q10 wrong | ok | 692 |
| 1037 | quiz | read the wrap-up for q10 | ok | 0 |
| 1038 | quiz | get every question in q11 wrong | ok | 603 |
| 1039 | quiz | read the wrap-up for q11 | ok | 0 |
| 1040 | quiz | get every question in q12 wrong | ok | 588 |
| 1041 | quiz | read the wrap-up for q12 | ok | 0 |
| 1042 | quiz | get every question in q13 wrong | ok | 579 |
| 1043 | quiz | read the wrap-up for q13 | ok | 0 |
| 1044 | quiz | get every question in q14 wrong | ok | 621 |
| 1045 | quiz | read the wrap-up for q14 | ok | 0 |
| 1046 | quiz | get every question in q15 wrong | ok | 1248 |
| 1047 | quiz | read the wrap-up for q15 | ok | 0 |
| 1048 | quiz | get every question in q16 wrong | ok | 1189 |
| 1049 | quiz | read the wrap-up for q16 | ok | 0 |
| 1050 | quiz | get every question in q17 wrong | ok | 893 |
| 1051 | quiz | read the wrap-up for q17 | ok | 0 |
| 1052 | quiz | get every question in q18 wrong | ok | 478 |
| 1053 | quiz | read the wrap-up for q18 | ok | 0 |
| 1054 | quiz | get every question in q99 wrong | ok | 451 |
| 1055 | quiz | read the wrap-up for q99 | ok | 0 |
| 1056 | review | the wrong answers are waiting in review | ok | 9 |
| 1057 | quiz | skip every question without answering | ok | 424 |
| 1058 | quiz | retake it | ok | 27 |
| 1059 | quiz | go back to the picker | ok | 135 |
| 1060 | review | open Review with nothing started | ok | 0 |
| 1061 | review | answer card 1 of 15 | ok | 70 |
| 1062 | review | answer card 2 of 15 | ok | 71 |
| 1063 | review | answer card 3 of 15 | ok | 57 |
| 1064 | review | answer card 4 of 15 | ok | 68 |
| 1065 | review | answer card 5 of 15 | ok | 71 |
| 1066 | review | answer card 6 of 15 | ok | 50 |
| 1067 | review | answer card 7 of 15 | ok | 47 |
| 1068 | review | answer card 8 of 15 | ok | 43 |
| 1069 | review | answer card 9 of 15 | ok | 68 |
| 1070 | review | answer card 10 of 15 | ok | 47 |
| 1071 | review | answer card 11 of 15 | ok | 82 |
| 1072 | review | answer card 12 of 15 | ok | 78 |
| 1073 | review | answer card 13 of 15 | ok | 72 |
| 1074 | review | answer card 14 of 15 | ok | 64 |
| 1075 | review | answer card 15 of 15 | ok | 65 |
| 1076 | review | the session ends with a clear queue | ok | 0 |
| 1077 | review | skip the card in front of you | ok | 29 |
| 1078 | review | work to the daily limit | ok | 268 |
| 1079 | review | the idle screen explains the limit | ok | 0 |
| 1080 | review | open Review with a thousand cards due | ok | 89 |
| 1081 | projects | read all 22 project cards | ok | 2 |
| 1082 | projects | meet every requirement of pj.p00.1 | ok | 137 |
| 1083 | projects | meet every requirement of pj.p01.1 | ok | 78 |
| 1084 | projects | meet every requirement of pj.p01.2 | ok | 93 |
| 1085 | projects | meet every requirement of pj.p02.1 | ok | 78 |
| 1086 | projects | meet every requirement of pj.p02.2 | ok | 106 |
| 1087 | projects | meet every requirement of pj.p03.1 | ok | 116 |
| 1088 | projects | meet every requirement of pj.p04.1 | ok | 90 |
| 1089 | projects | meet every requirement of pj.p05.1 | ok | 93 |
| 1090 | projects | meet every requirement of pj.p06.1 | ok | 116 |
| 1091 | projects | meet every requirement of pj.p07.1 | ok | 116 |
| 1092 | projects | meet every requirement of pj.p08.1 | ok | 109 |
| 1093 | projects | meet every requirement of pj.p09.1 | ok | 145 |
| 1094 | projects | meet every requirement of pj.p10.1 | ok | 158 |
| 1095 | projects | meet every requirement of pj.p11.1 | ok | 101 |
| 1096 | projects | meet every requirement of pj.p12.1 | ok | 97 |
| 1097 | projects | meet every requirement of pj.p13.1 | ok | 121 |
| 1098 | projects | meet every requirement of pj.p14.1 | ok | 84 |
| 1099 | projects | meet every requirement of pj.p14.2 | ok | 139 |
| 1100 | projects | meet every requirement of pj.p15.1 | ok | 176 |
| 1101 | projects | meet every requirement of pj.p16.1 | ok | 155 |
| 1102 | projects | meet every requirement of pj.p17.1 | ok | 142 |
| 1103 | projects | meet every requirement of pj.p99.1 | ok | 141 |
| 1104 | projects | the meters agree once everything is met | ok | 45 |
| 1105 | projects | untick pj.p00.1 again | ok | 117 |
| 1106 | projects | untick pj.p01.1 again | ok | 158 |
| 1107 | projects | untick pj.p01.2 again | ok | 141 |
| 1108 | projects | untick pj.p02.1 again | ok | 125 |
| 1109 | projects | untick pj.p02.2 again | ok | 125 |
| 1110 | projects | untick pj.p03.1 again | ok | 128 |
| 1111 | projects | untick pj.p04.1 again | ok | 127 |
| 1112 | projects | untick pj.p05.1 again | ok | 97 |
| 1113 | projects | untick pj.p06.1 again | ok | 147 |
| 1114 | projects | untick pj.p07.1 again | ok | 145 |
| 1115 | projects | untick pj.p08.1 again | ok | 112 |
| 1116 | projects | untick pj.p09.1 again | ok | 119 |
| 1117 | projects | untick pj.p10.1 again | ok | 134 |
| 1118 | projects | untick pj.p11.1 again | ok | 123 |
| 1119 | projects | untick pj.p12.1 again | ok | 116 |
| 1120 | projects | untick pj.p13.1 again | ok | 133 |
| 1121 | projects | untick pj.p14.1 again | ok | 114 |
| 1122 | projects | untick pj.p14.2 again | ok | 93 |
| 1123 | projects | untick pj.p15.1 again | ok | 122 |
| 1124 | projects | untick pj.p16.1 again | ok | 86 |
| 1125 | projects | untick pj.p17.1 again | ok | 125 |
| 1126 | projects | untick pj.p99.1 again | ok | 95 |
| 1127 | projects | mark pj.p00.1 as Not started | ok | 70 |
| 1128 | projects | mark pj.p00.1 as In progress | ok | 9 |
| 1129 | projects | mark pj.p00.1 as Shipped | ok | 27 |
| 1130 | projects | mark pj.p01.1 as Not started | ok | 15 |
| 1131 | projects | mark pj.p01.1 as In progress | ok | 17 |
| 1132 | projects | mark pj.p01.1 as Shipped | ok | 19 |
| 1133 | projects | mark pj.p01.2 as Not started | ok | 8 |
| 1134 | projects | mark pj.p01.2 as In progress | ok | 11 |
| 1135 | projects | mark pj.p01.2 as Shipped | ok | 20 |
| 1136 | projects | mark pj.p02.1 as Not started | ok | 14 |
| 1137 | projects | mark pj.p02.1 as In progress | ok | 15 |
| 1138 | projects | mark pj.p02.1 as Shipped | ok | 11 |
| 1139 | projects | mark pj.p02.2 as Not started | ok | 10 |
| 1140 | projects | mark pj.p02.2 as In progress | ok | 15 |
| 1141 | projects | mark pj.p02.2 as Shipped | ok | 14 |
| 1142 | projects | mark pj.p03.1 as Not started | ok | 7 |
| 1143 | projects | mark pj.p03.1 as In progress | ok | 8 |
| 1144 | projects | mark pj.p03.1 as Shipped | ok | 15 |
| 1145 | projects | mark pj.p04.1 as Not started | ok | 10 |
| 1146 | projects | mark pj.p04.1 as In progress | ok | 11 |
| 1147 | projects | mark pj.p04.1 as Shipped | ok | 19 |
| 1148 | projects | mark pj.p05.1 as Not started | ok | 8 |
| 1149 | projects | mark pj.p05.1 as In progress | ok | 18 |
| 1150 | projects | mark pj.p05.1 as Shipped | ok | 19 |
| 1151 | projects | mark pj.p06.1 as Not started | ok | 16 |
| 1152 | projects | mark pj.p06.1 as In progress | ok | 19 |
| 1153 | projects | mark pj.p06.1 as Shipped | ok | 20 |
| 1154 | projects | mark pj.p07.1 as Not started | ok | 12 |
| 1155 | projects | mark pj.p07.1 as In progress | ok | 13 |
| 1156 | projects | mark pj.p07.1 as Shipped | ok | 20 |
| 1157 | projects | mark pj.p08.1 as Not started | ok | 14 |
| 1158 | projects | mark pj.p08.1 as In progress | ok | 13 |
| 1159 | projects | mark pj.p08.1 as Shipped | ok | 18 |
| 1160 | projects | mark pj.p09.1 as Not started | ok | 14 |
| 1161 | projects | mark pj.p09.1 as In progress | ok | 13 |
| 1162 | projects | mark pj.p09.1 as Shipped | ok | 16 |
| 1163 | projects | mark pj.p10.1 as Not started | ok | 13 |
| 1164 | projects | mark pj.p10.1 as In progress | ok | 16 |
| 1165 | projects | mark pj.p10.1 as Shipped | ok | 17 |
| 1166 | projects | mark pj.p11.1 as Not started | ok | 12 |
| 1167 | projects | mark pj.p11.1 as In progress | ok | 13 |
| 1168 | projects | mark pj.p11.1 as Shipped | ok | 11 |
| 1169 | projects | mark pj.p12.1 as Not started | ok | 13 |
| 1170 | projects | mark pj.p12.1 as In progress | ok | 13 |
| 1171 | projects | mark pj.p12.1 as Shipped | ok | 21 |
| 1172 | projects | mark pj.p13.1 as Not started | ok | 15 |
| 1173 | projects | mark pj.p13.1 as In progress | ok | 18 |
| 1174 | projects | mark pj.p13.1 as Shipped | ok | 24 |
| 1175 | projects | mark pj.p14.1 as Not started | ok | 21 |
| 1176 | projects | mark pj.p14.1 as In progress | ok | 10 |
| 1177 | projects | mark pj.p14.1 as Shipped | ok | 15 |
| 1178 | projects | mark pj.p14.2 as Not started | ok | 12 |
| 1179 | projects | mark pj.p14.2 as In progress | ok | 20 |
| 1180 | projects | mark pj.p14.2 as Shipped | ok | 21 |
| 1181 | projects | mark pj.p15.1 as Not started | ok | 16 |
| 1182 | projects | mark pj.p15.1 as In progress | ok | 15 |
| 1183 | projects | mark pj.p15.1 as Shipped | ok | 20 |
| 1184 | projects | mark pj.p16.1 as Not started | ok | 10 |
| 1185 | projects | mark pj.p16.1 as In progress | ok | 10 |
| 1186 | projects | mark pj.p16.1 as Shipped | ok | 21 |
| 1187 | projects | mark pj.p17.1 as Not started | ok | 22 |
| 1188 | projects | mark pj.p17.1 as In progress | ok | 18 |
| 1189 | projects | mark pj.p17.1 as Shipped | ok | 23 |
| 1190 | projects | mark pj.p99.1 as Not started | ok | 19 |
| 1191 | projects | mark pj.p99.1 as In progress | ok | 20 |
| 1192 | projects | mark pj.p99.1 as Shipped | ok | 14 |
| 1193 | projects | try each filter | ok | 554 |
| 1194 | projects | record a repo and some notes | ok | 516 |
| 1195 | projects | press Open next to the repo | ok | 2 |
| 1196 | projects | jump to the project's phase | ok | 217 |
| 1197 | projects | ship all 22 projects | ok | 514 |
| 1198 | today | Today agrees | ok | 114 |
| 1199 | projects | press a status button | 25 ms | 25 |
| 1200 | journal | write today's entry | ok | 58 |
| 1201 | journal | add three more days | ok | 212 |
| 1202 | journal | an entry is edited by writing it again | ok | 68 |
| 1203 | journal | delete every entry from the history | ok | 269 |
| 1204 | stats | the charts render with no data at all | ok | 9 |
| 1205 | stats | the charts render with one data point | ok | 219 |
| 1206 | stats | the charts render with a year of data | ok | 286 |
| 1207 | stats | rate every skill in the matrix | ok | 30 |
| 1208 | stats | the table covers the whole plan | ok | 222 |
| 1209 | library | open the Shelf tab | ok | 67 |
| 1210 | library | open the Fields of work tab | ok | 185 |
| 1211 | library | open the Video tab | ok | 135 |
| 1212 | library | open the Certificates tab | ok | 142 |
| 1213 | library | press every Open on the Shelf tab | ok | 17 |
| 1214 | library | press every Open on the Fields of work tab | ok | 0 |
| 1215 | library | press every Open on the Video tab | ok | 20 |
| 1216 | library | press every Open on the Certificates tab | ok | 0 |
| 1217 | library | press every field library button | ok | 140 |
| 1218 | library | cycle c-cs50p through every state | ok | 1272 |
| 1219 | library | cycle c-helsinki through every state | ok | 1352 |
| 1220 | library | cycle c-fcc-sci through every state | ok | 1272 |
| 1221 | library | cycle c-netacad1 through every state | ok | 1271 |
| 1222 | library | cycle c-netacad2 through every state | ok | 1305 |
| 1223 | library | cycle c-pcep through every state | ok | 1393 |
| 1224 | library | cycle c-pcap through every state | ok | 1253 |
| 1225 | library | cycle c-hackerrank through every state | ok | 1268 |
| 1226 | library | cycle c-kaggle through every state | ok | 1302 |
| 1227 | library | cycle c-fcc-data through every state | ok | 1418 |
| 1228 | library | cycle c-fcc-ml through every state | ok | 1319 |
| 1229 | library | cycle c-hf-agents through every state | ok | 1461 |
| 1230 | library | cycle c-hf-llm through every state | ok | 1423 |
| 1231 | library | cycle c-hf-mcp through every state | ok | 1353 |
| 1232 | library | cycle c-anthropic through every state | ok | 1294 |
| 1233 | library | cycle c-google-ml through every state | ok | 1314 |
| 1234 | library | cycle c-mit191 through every state | ok | 1367 |
| 1235 | library | cycle c-cs50ai through every state | ok | 1362 |
| 1236 | library | cycle c-cs50w through every state | ok | 1321 |
| 1237 | library | cycle c-google-auto through every state | ok | 1499 |
| 1238 | library | cycle c-py4e through every state | ok | 1416 |
| 1239 | library | cycle c-mlzoom through every state | ok | 1360 |
| 1240 | library | cycle c-dezoom through every state | ok | 1405 |
| 1241 | library | cycle c-mit6001 through every state | ok | 1230 |
| 1242 | settings | change your name | ok | 8 |
| 1243 | settings | try every track | ok | 129 |
| 1244 | settings | try every experience level | ok | 28 |
| 1245 | settings | tick and untick every goal | ok | 134 |
| 1246 | settings | push every number to both ends | ok | 83 |
| 1247 | settings | turn the update check off and on | ok | 13 |
| 1248 | settings | put every setting back | ok | 33 |
| 1249 | settings | switch the theme to Dark | ok | 1010 |
| 1250 | settings | switch the theme to Light | ok | 915 |
| 1251 | settings | switch the theme to Match the system | ok | 10 |
| 1252 | settings | press Open folder | ok | 2 |
| 1253 | settings | export a backup | ok | 12 |
| 1254 | settings | export a progress report | ok | 13 |
| 1255 | settings | take a snapshot | ok | 15 |
| 1256 | settings | cancel an import | ok | 0 |
| 1257 | settings | import the backup back | ok | 0 |
| 1258 | settings | decline a reset | ok | 2 |
| 1259 | settings | accept a reset | ok | 0 |
| 1260 | settings | press Check now | ok | 3 |
| 1261 | search | open search with Ctrl+K | ok | 2 |
| 1262 | search | search for 'nothing' | ok | 0 |
| 1263 | search | search for 'd' | ok | 1 |
| 1264 | search | search for 'Python engineering' | ok | 17 |
| 1265 | search | search for 'Say hello' | ok | 7 |
| 1266 | search | search for 'zzzqqqxx nothing at all' | ok | 3 |
| 1267 | search | press Escape | ok | 12 |
| 1268 | search | press Enter on the first result | ok | 114 |
| 1269 | search | open a result of every kind | ok | 1217 |
| 1270 | history | nothing to undo on a fresh store | ok | 0 |
| 1271 | history | tick a line, then undo and redo it | ok | 815 |
| 1272 | history | change a project status, then undo it | ok | 1928 |
| 1273 | history | rate a skill, then undo it | ok | 487 |
| 1274 | history | cycle a certificate, then undo it | ok | 2835 |
| 1275 | history | undo and redo from the keyboard | ok | 1357 |
| 1276 | history | a new change drops the redo branch | ok | 388 |
| 1277 | history | reopen the app and look for the undo | ok | 0 |
| 1278 | history | the tick survived, the undo did not | ok | 0 |
| 1279 | updates | the button is hidden until there is one | ok | 0 |
| 1280 | updates | a release makes the button appear | ok | 2 |
| 1281 | updates | press it for a release with no changelog | ok | 1 |
| 1282 | updates | press it for a release with a changelog | ok | 9 |
| 1283 | updates | a release with nothing for this platform | ok | 5 |
| 1284 | updates | Help > Check for updates | ok | 3 |
| 1285 | restart | reopen the app on the same store | ok | 0 |
| 1286 | restart | the position is remembered | ok | 0 |
| 1287 | restart | quit inside the autosave window | ok | 3023 |
| 1288 | history | Ctrl+Z undoes a tick | ok | 320 |
| 1289 | history | the advertised redo keys | ok | 269 |
| 1290 | history | the Redo button still works | ok | 0 |
| 1291 | today | Today at 800x600 | ok | 0 |
| 1292 | roadmap | Roadmap at 800x600 | ok | 0 |
| 1293 | phase | Phase at 800x600 | ok | 1 |
| 1294 | practice | Practice at 800x600 | ok | 0 |
| 1295 | quiz | Quizzes at 800x600 | ok | 0 |
| 1296 | review | Review at 800x600 | ok | 0 |
| 1297 | projects | Projects at 800x600 | ok | 7 |
| 1298 | journal | Log at 800x600 | ok | 0 |
| 1299 | stats | Progress at 800x600 | ok | 1 |
| 1300 | library | Library at 800x600 | ok | 3 |
| 1301 | settings | Settings at 800x600 | ok | 0 |
| 1302 | today | Today at 1280x900 | ok | 0 |
| 1303 | roadmap | Roadmap at 1280x900 | ok | 0 |
| 1304 | phase | Phase at 1280x900 | ok | 1 |
| 1305 | practice | Practice at 1280x900 | ok | 0 |
| 1306 | quiz | Quizzes at 1280x900 | ok | 0 |
| 1307 | review | Review at 1280x900 | ok | 0 |
| 1308 | projects | Projects at 1280x900 | ok | 10 |
| 1309 | journal | Log at 1280x900 | ok | 0 |
| 1310 | stats | Progress at 1280x900 | ok | 1 |
| 1311 | library | Library at 1280x900 | ok | 3 |
| 1312 | settings | Settings at 1280x900 | ok | 1 |
| 1313 | today | Today at 2560x1440 | ok | 0 |
| 1314 | roadmap | Roadmap at 2560x1440 | ok | 0 |
| 1315 | phase | Phase at 2560x1440 | ok | 0 |
| 1316 | practice | Practice at 2560x1440 | ok | 0 |
| 1317 | quiz | Quizzes at 2560x1440 | ok | 0 |
| 1318 | review | Review at 2560x1440 | ok | 0 |
| 1319 | projects | Projects at 2560x1440 | ok | 8 |
| 1320 | journal | Log at 2560x1440 | ok | 0 |
| 1321 | stats | Progress at 2560x1440 | ok | 1 |
| 1322 | library | Library at 2560x1440 | ok | 2 |
| 1323 | settings | Settings at 2560x1440 | ok | 0 |
| 1324 | layout | the window refuses to go below its minimum | ok | 0 |
| 1325 | layout | the sidebar keeps every page button | ok | 0 |
| 1326 | today | tab through the today page | ok | 115 |
| 1327 | today | the focused control is the one you can see | ok | 0 |
| 1328 | practice | tab through the practice page | ok | 179 |
| 1329 | practice | the focused control is the one you can see | ok | 0 |
| 1330 | phase | tick a line with the space bar | ok | 30 |
| 1331 | practice | Ctrl+Enter in the editor runs the code | ok | 231 |
| 1332 | settings | type 2,5 hours in a German locale | ok | 15 |
| 1333 | settings | type it by hand as 3,5 | ok | 11 |
| 1334 | today | the pace line still reads sensibly | ok | 100 |
| 1335 | library | open library with nothing to show | ok | 38 |
| 1336 | stats | open stats with nothing to show | ok | 74 |
| 1337 | projects | open projects with nothing to show | ok | 26 |
| 1338 | today | open today with nothing to show | ok | 78 |
| 1339 | roadmap | open roadmap with nothing to show | ok | 321 |
| 1340 | navigation | switch pages 200 times | ok | 4037 |
| 1341 | today | reopen the Today page | 3 ms | 3 |
| 1342 | roadmap | reopen the Roadmap page | 35 ms | 35 |
| 1343 | phase | reopen the Phase page | 22 ms | 22 |
| 1344 | practice | reopen the Practice page | 42 ms | 42 |
| 1345 | quiz | reopen the Quizzes page | 19 ms | 19 |
| 1346 | review | reopen the Review page | 18 ms | 18 |
| 1347 | projects | reopen the Projects page | 30 ms | 30 |
| 1348 | journal | reopen the Log page | 17 ms | 17 |
| 1349 | stats | reopen the Progress page | 20 ms | 20 |
| 1350 | library | reopen the Library page | 39 ms | 39 |
| 1351 | settings | reopen the Settings page | 26 ms | 26 |
| 1352 | screenshots | grab every page on both themes | ok | 10130 |
| 1353 | screenshots | practice page after a passing run | results panel hidden: False; rows rendered into it: 4; hint label hidden: True;  | 0 |
| 1354 | help | press F1 and close the shortcut list | ok | 39 |
| 1355 | menu | press Ctrl+, for Settings | ok | 162 |
| 1356 | settings | open the snapshot list and cancel | ok | 38 |
| 1357 | settings | restore the snapshot just taken | ok | 115 |
| 1358 | onboarding | Continue, Continue, Back | ok | 36 |
| 1359 | update | press Update and restart while offline | ok | 17 |
| 1360 | quiz | finish a quiz and go back to its phase | ok | 720 |
| 1361 | quiz | finish a quiz and pick another | ok | 579 |
| 1362 | review | skip to a concept card, reveal, rate | ok | 107 |
| 1363 | practice | press Next | ok | 14 |
| 1364 | phase | open the first resource | ok | 20 |
| 1365 | library | press every button on tab 0 | ok | 800 |
| 1366 | library | press every button on tab 1 | ok | 837 |
| 1367 | library | press every button on tab 2 | ok | 741 |
| 1368 | library | press every button on tab 3 | ok | 565 |
| 1369 | projects | open the repo link | ok | 125 |
| 1370 | projects | press every status button | ok | 475 |
| 1371 | journal | the history opens on the newest sixty | ok | 0 |
| 1372 | journal | press Show older for the next sixty | ok | 711 |
| 1373 | journal | press Show older for the last ten | ok | 161 |
| 1374 | journal | find one entry among a hundred | ok | 365 |
| 1375 | journal | a filter that matches nothing says so | ok | 735 |
| 1376 | journal | narrow the range, then widen it again | ok | 1816 |
| 1377 | journal | load an old entry back into the form | ok | 37 |
| 1378 | journal | save the correction | ok | 60 |
| 1379 | journal | take the correction back with Ctrl+Z | ok | 45 |
| 1380 | journal | and put it back with Ctrl+Y | ok | 41 |
| 1381 | journal | start an edit and cancel out of it | ok | 101 |
| 1382 | journal | delete an entry by mistake | ok | 42 |
| 1383 | journal | Ctrl+Z brings the whole entry back | ok | 58 |
| 1384 | journal | Ctrl+Y deletes it again | ok | 32 |
| 1385 | journal | log today for the first time | ok | 49 |
| 1386 | journal | the form warns before the day stacks | ok | 0 |
| 1387 | journal | log today again anyway | ok | 31 |
| 1388 | journal | every note written is listed here | ok | 0 |
| 1389 | journal | the filter searches the notes too | ok | 104 |
| 1390 | journal | open note 0 from the log | ok | 281 |
| 1391 | journal | open note 1 from the log | ok | 285 |
| 1392 | journal | open note 2 from the log | ok | 308 |
| 1393 | journal | open note 3 from the log | ok | 230 |
| 1394 | journal | open note 4 from the log | ok | 1735 |
| 1395 | journal | open note 5 from the log | ok | 54 |
| 1396 | journal | open note 6 from the log | ok | 56 |
| 1397 | journal | the notes section with nothing in it | ok | 0 |
| 1398 | practice | submit an empty editor and read the reasons | ok | 310 |
| 1399 | practice | put the real answer back | ok | 258 |
| 1400 | practice | forget the exclamation mark and run | ok | 293 |
| 1401 | practice | get one character wrong instead | ok | 283 |
| 1402 | practice | get only the capital wrong | ok | 316 |
| 1403 | practice | start an endless run and press Stop | ok | 366 |
| 1404 | practice | read every hint, then press once more | ok | 32 |
| 1405 | practice | search for one exercise by its title | ok | 24 |
| 1406 | practice | search for something that is not there | ok | 17 |
| 1407 | practice | clear the search | ok | 36 |
| 1408 | practice | filter by every difficulty | ok | 131 |
| 1409 | practice | show only the revealed ones | ok | 45 |
| 1410 | practice | walk to the last exercise and press Next again | ok | 54 |
| 1411 | practice | pass the exercise | ok | 305 |
| 1412 | practice | carry on experimenting and break it | ok | 20 |
| 1413 | practice | press Restore my passing version | ok | 15 |
| 1414 | practice | press Reset, then restore once more | ok | 76 |
| 1415 | practice | read the answer | ok | 39 |
| 1416 | practice | check the list says so too | ok | 0 |
| 1417 | practice | press Try this one again from scratch | ok | 31 |
| 1418 | review | press Space to reveal the saved line | ok | 32 |
| 1419 | review | press 3 to rate it Good | ok | 34 |
| 1420 | review | pick a multiple choice option by letter | ok | 2 |
| 1421 | review | press Enter to check it | ok | 34 |
| 1422 | review | press 4 for Easy | ok | 44 |
| 1423 | review | answer with the Again key | ok | 70 |
| 1424 | review | answer with the Hard key | ok | 66 |
| 1425 | review | answer with the Good key | ok | 60 |
| 1426 | review | answer with the Easy key | ok | 69 |
| 1427 | review | type in the search box with a card open | ok | 4 |
| 1428 | review | bury the card in front of you | ok | 71 |
| 1429 | review | the summary offers the buried card back | ok | 102 |
| 1430 | review | answer one card, then take it back | ok | 126 |
| 1431 | review | Ctrl+Z takes the next one back too | ok | 107 |
| 1432 | review | skip the same card twice | ok | 68 |
| 1433 | phase | open a line's menu with the ... button | ok | 54 |
| 1434 | phase | open the same menu with Shift+F10 | ok | 14 |
| 1435 | phase | the Menu key offers to take it out again | ok | 9 |
| 1436 | search | open the box with Ctrl+K | ok | 6 |
| 1437 | search | find a phase note written minutes ago | ok | 329 |
| 1438 | search | find your own project note | ok | 143 |
| 1439 | search | find a project by its repository url | ok | 6 |
| 1440 | search | find a log entry and open the log | ok | 27 |
| 1441 | search | type a query | ok | 54 |
| 1442 | search | walk down and back up the results | ok | 16 |
| 1443 | search | page down and page up the results | ok | 13 |
| 1444 | search | open the selected hit with Enter | ok | 316 |
| 1445 | search | close the results with Escape | ok | 15 |
| 1446 | library | open the field f-web from search | ok | 169 |
| 1447 | library | open the cert c-cs50p from search | ok | 199 |
| 1448 | search | open a question from search | ok | 21 |
| 1449 | search | read the question and close it | ok | 41 |
| 1450 | library | filter the library to nothing | ok | 71 |
| 1451 | library | filter the library to one shelf entry | ok | 336 |
| 1452 | library | mark a row on tab 0 as read | ok | 14 |
| 1453 | library | take the mark on tab 0 back | ok | 7 |
| 1454 | library | mark a row on tab 1 as read | ok | 228 |
| 1455 | library | take the mark on tab 1 back | ok | 12 |
| 1456 | library | mark a row on tab 2 as read | ok | 173 |
| 1457 | library | take the mark on tab 2 back | ok | 14 |
| 1458 | library | undo the last read mark | ok | 380 |
| 1459 | navigation | press Ctrl+0 | ok | 124 |
| 1460 | navigation | press Ctrl+L | ok | 84 |
| 1461 | navigation | open the library from the Go menu | ok | 135 |
| 1462 | first run | read the status bar on a first launch | ok | 0 |
| 1463 | onboarding | type a name and continue | ok | 18 |
| 1464 | onboarding | choose an experience card | ok | 21 |
| 1465 | onboarding | tick two goals | ok | 28 |
| 1466 | onboarding | go back a step and forward again | ok | 20 |
| 1467 | onboarding | set a pace and build the plan | ok | 132 |
| 1468 | onboarding | skip the whole thing | ok | 12 |
| 1469 | settings | press Run setup again | ok | 68 |
| 1470 | quiz | start one and skip a question | ok | 69 |
| 1471 | quiz | move on to the next question | ok | 32 |
| 1472 | quiz | think better of leaving | ok | 2 |
| 1473 | quiz | leave the quiz | ok | 167 |
| 1474 | quiz | close the app in the middle of one | ok | 220 |
| 1475 | quiz | resume where it was left | ok | 43 |
| 1476 | quiz | start it over instead | ok | 204 |
| 1477 | settings | nothing has left this machine yet | ok | 0 |
| 1478 | settings | choose a second copy folder | ok | 11 |
| 1479 | settings | copy everything there now | ok | 29 |
| 1480 | settings | import a backup and read the summary | ok | 68 |
| 1481 | projects | press Open with nothing to open | ok | 1 |
| 1482 | projects | type a repo address | ok | 2 |
| 1483 | projects | replace it with a note to self | ok | 1 |
| 1484 | today | read the note above the list | ok | 68 |
| 1485 | today | push the first item off until tomorrow | ok | 76 |
| 1486 | today | push a second one off from a compact row | ok | 75 |
| 1487 | today | find the way back to what was hidden | ok | 99 |
| 1488 | today | yesterday's 'first thing tomorrow' returns | ok | 83 |
| 1489 | today | push everything off for a quiet evening | ok | 76 |
| 1490 | today | finish the entire curriculum | ok | 416 |
| 1491 | today | read what the finished plan says | ok | 0 |
| 1492 | today | keep reviewing from the hero | ok | 112 |
| 1493 | today | change track from the hero | ok | 188 |
| 1494 | today | export the report from the hero | ok | 112 |
| 1495 | roadmap | the marker is there while work remains | ok | 0 |
| 1496 | roadmap | and is gone once there is nowhere to go | ok | 0 |
| 1497 | stats | click a phase row | ok | 400 |
| 1498 | stats | select a row and press Enter | ok | 236 |
| 1499 | stats | hover the quiz column for the trend | ok | 0 |
| 1500 | phase | the way into the review deck is announced | ok | 0 |
| 1501 | phase | write a long note into the box | ok | 29 |
| 1502 | phase | and it shrinks back for a short one | ok | 14 |
| 1503 | search | type a word that is nowhere | ok | 46 |
| 1504 | search | Escape, then Ctrl+K again | ok | 28 |
| 1505 | search | open a shelf book from Ctrl+K | ok | 194 |
| 1506 | library | filter for a channel on the Shelf tab | ok | 157 |
| 1507 | library | follow the count to the Video tab | ok | 14 |
| 1508 | library | clear the filter | ok | 491 |
| 1509 | projects | SHOW Shipped with nothing shipped | ok | 26 |
| 1510 | projects | press Show every project | ok | 516 |
| 1511 | projects | type in FIND | ok | 558 |
| 1512 | stats | click the Checks heading | ok | 7 |
| 1513 | stats | pick every SORT choice | ok | 22 |
| 1514 | practice | fail a run, then Where this is taught | ok | 481 |
| 1515 | settings | set filters, then change the theme | ok | 6828 |
| 1516 | settings | come back to each page | ok | 11228 |
| 1517 | quiz | read the picker and its counter | ok | 0 |
| 1518 | quiz | type into FIND | ok | 127 |
| 1519 | quiz | a search that matches nothing | ok | 143 |
| 1520 | quiz | SHOW each status in turn | ok | 408 |
| 1521 | quiz | start a quiz from the filtered list | ok | 193 |
| 1522 | quiz | press the second choice every time | ok | 1139 |
| 1523 | review | pick a wrong option by its letter | ok | 32 |
| 1524 | review | press Where this is taught | ok | 280 |
| 1525 | review | press Next card | ok | 39 |
| 1526 | review | a second wrong answer, left with Space | ok | 72 |
| 1527 | review | reveal a gate check | ok | 36 |
| 1528 | review | rate it Good | ok | 32 |
| 1529 | phase | a phase read to the end | ok | 262 |
| 1530 | roadmap | the roadmap says read, not proven | ok | 291 |
| 1531 | phase | the same phase, proven | ok | 251 |
| 1532 | today | an earlier phase is mixed into today | ok | 163 |
| 1533 | quiz | start a quiz from the picker | ok | 41 |
| 1534 | quiz | leave and start a different one | ok | 193 |
| 1535 | review | press Check for more | ok | 37 |
| 1536 | updates | open the update dialog and decline | ok | 16 |
| 1537 | updates | open the releases page instead | ok | 11 |
| 1538 | menu | File > Quit | ok | 12 |
| 1539 | menu | File > Export backup... | ok | 142 |
| 1540 | menu | File > Export progress report... | ok | 21 |
| 1541 | menu | File > Take a snapshot | ok | 20 |
| 1542 | menu | File > Restore a snapshot... | ok | 25 |
| 1543 | menu | Go > Today | ok | 96 |
| 1544 | menu | Go > Roadmap | ok | 298 |
| 1545 | menu | Go > Phase | ok | 240 |
| 1546 | menu | Go > Practice | ok | 90 |
| 1547 | menu | Go > Quizzes | ok | 165 |
| 1548 | menu | Go > Review | ok | 42 |
| 1549 | menu | Go > Projects | ok | 1662 |
| 1550 | menu | Go > Log | ok | 83 |
| 1551 | menu | Go > Progress | ok | 277 |
| 1552 | menu | Go > Library | ok | 2375 |
| 1553 | menu | Go > Settings | ok | 95 |
| 1554 | menu | Go > Find | ok | 18 |
| 1555 | menu | Edit > Undo | ok | 0 |
| 1556 | menu | Edit > Redo | ok | 0 |
| 1557 | menu | Help > How this app works | ok | 0 |
| 1558 | menu | Help > Keyboard shortcuts | ok | 24 |
| 1559 | menu | Help > Check for updates | ok | 2 |
| 1560 | menu | Help > About | ok | 1 |
| 1561 | menu | every navigation shortcut | ok | 1290 |
