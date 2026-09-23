# Walkthrough of Operator's Console

A single learner's pass through every page, every control and every piece of content, driven through the real widgets with QTest and watched by a net of sensors.

- Generated: 2026-09-23 17:48
- Platform: Windows-11-10.0.26200-SP0, Python 3.14.5, Qt offscreen
- Runtime: 5 min 56 s
- Steps recorded: 1561
- Findings: 2
- Unhandled exceptions seen: 0
- Qt warnings and criticals: 1
- Dialogs answered: 30
- URLs intercepted (none opened): 312
- pytest exit status: 0

## Findings

| id | severity | view | what happened | how to reproduce |
| --- | --- | --- | --- | --- |
| W-01 | major | navigation | step blocks for 5864 ms: switch pages 200 times as fast as the event loop allows | Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 5.9 s. |
| W-02 | polish | journal | a second entry for the same day is added, not merged | Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions. |

### W-01 - step blocks for 5864 ms: switch pages 200 times as fast as the event loop allows

- **Severity**: major
- **View**: navigation
- **Repro**: Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 5.9 s.

### W-02 - a second entry for the same day is added, not merged

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
| operators_console/ui/updater.py | 220 | button | Open the releases page | yes |
| operators_console/ui/updater.py | 224 | button | Not now | yes |
| operators_console/ui/updater.py | 227 | button | Update and restart | yes |
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
| operators_console/ui/views/phase.py | 324 | button | Copy | yes |
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
| milliseconds for 200 page switches | 1997 |
| milliseconds for a typical project status press | 14 |
| milliseconds to open review with 1000 cards | 45 |
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
| worst theme switch in milliseconds | 423 |
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
| notice | About Python Operator's Console | Python Operator's Console 1.1.0  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2849\test_the_help_ |
| messagebox | Show the solution? | You have not passed this one yet.  Reading the answer now costs you the exercise. Try one more hint first? |
| open file | Import a backup | C:\Users\anasa |
| question | Replace everything? | Importing replaces all of your current progress.  A backup of the current state is taken first, into the backups folder. Continue? |
| question | Reset all progress? | This clears every checkbox, exercise, review, project and log entry.  A snapshot is taken first, so Restore a snapshot (here in Settings) can bring it all back. Your settings are kept. |
| dialog | UpdateDialog | Update available |
| dialog | QuestionDialog | Question |
| dialog | Onboarding | Set up your plan |
| question | Leave this quiz? | What you have answered is already scored and scheduled for review.  The rest of this attempt is dropped, and the quiz starts from the beginning next time. Leave it? |
| notice | About Python Operator's Console | Python Operator's Console 1.1.0  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2849\test_the_remai |

## Every step

| # | view | action | result | ms |
| --- | --- | --- | --- | --- |
| 1 | onboarding | open the wizard on first run | ok | 47 |
| 2 | onboarding | continue from step 1 | ok | 7 |
| 3 | onboarding | continue from step 2 | ok | 0 |
| 4 | onboarding | continue from step 3 | ok | 0 |
| 5 | onboarding | back from step 4 | ok | 0 |
| 6 | onboarding | back from step 3 | ok | 0 |
| 7 | onboarding | back from step 2 | ok | 0 |
| 8 | onboarding | experience: Never written code before | ok | 44 |
| 9 | onboarding | experience: Some Python, but it does not stick | ok | 40 |
| 10 | onboarding | experience: Confident in another language | ok | 41 |
| 11 | onboarding | experience: I write Python at work already | ok | 41 |
| 12 | onboarding | tick all 512 goal combinations | ok | 344 |
| 13 | onboarding | finish with goal: Build websites and APIs | ok | 57 |
| 14 | onboarding | finish with goal: Work with data | ok | 51 |
| 15 | onboarding | finish with goal: Machine learning and AI | ok | 72 |
| 16 | onboarding | finish with goal: Automate boring work | ok | 88 |
| 17 | onboarding | finish with goal: Games and graphics | ok | 101 |
| 18 | onboarding | finish with goal: Infrastructure and deployment | ok | 46 |
| 19 | onboarding | finish with goal: Security and hacking | ok | 51 |
| 20 | onboarding | finish with goal: Pass a technical interview | ok | 42 |
| 21 | onboarding | finish with goal: Understand how computers work | ok | 48 |
| 22 | onboarding | pace 0.5 h x 1 days | ok | 33 |
| 23 | onboarding | pace 16.0 h x 7 days | ok | 35 |
| 24 | onboarding | skip the wizard | ok | 3 |
| 25 | today | land on Today after skipping | ok | 54 |
| 26 | today | read the four headline tiles | ok | 0 |
| 27 | today | press Start on plan row 1 | ok | 74 |
| 28 | today | press Start on plan row 2 | ok | 139 |
| 29 | today | press Start on plan row 3 | ok | 878 |
| 30 | today | press Start on plan row 4 | ok | 165 |
| 31 | today | press Start on plan row 5 | ok | 36 |
| 32 | today | open the current phase from Where you are | ok | 129 |
| 33 | settings | switch the theme to light | ok | 4 |
| 34 | today | click the Today sidebar button (light theme) | ok | 58 |
| 35 | roadmap | click the Roadmap sidebar button (light theme) | ok | 175 |
| 36 | phase | click the Phase sidebar button (light theme) | ok | 170 |
| 37 | practice | click the Practice sidebar button (light theme) | ok | 84 |
| 38 | quiz | click the Quizzes sidebar button (light theme) | ok | 92 |
| 39 | review | click the Review sidebar button (light theme) | ok | 27 |
| 40 | projects | click the Projects sidebar button (light theme) | ok | 1036 |
| 41 | journal | click the Log sidebar button (light theme) | ok | 68 |
| 42 | stats | click the Progress sidebar button (light theme) | ok | 151 |
| 43 | library | click the Library sidebar button (light theme) | ok | 1165 |
| 44 | settings | click the Settings sidebar button (light theme) | ok | 173 |
| 45 | settings | switch the theme to dark | ok | 370 |
| 46 | today | click the Today sidebar button (dark theme) | ok | 70 |
| 47 | roadmap | click the Roadmap sidebar button (dark theme) | ok | 184 |
| 48 | phase | click the Phase sidebar button (dark theme) | ok | 154 |
| 49 | practice | click the Practice sidebar button (dark theme) | ok | 88 |
| 50 | quiz | click the Quizzes sidebar button (dark theme) | ok | 104 |
| 51 | review | click the Review sidebar button (dark theme) | ok | 14 |
| 52 | projects | click the Projects sidebar button (dark theme) | ok | 1036 |
| 53 | journal | click the Log sidebar button (dark theme) | ok | 49 |
| 54 | stats | click the Progress sidebar button (dark theme) | ok | 139 |
| 55 | library | click the Library sidebar button (dark theme) | ok | 1325 |
| 56 | settings | click the Settings sidebar button (dark theme) | ok | 75 |
| 57 | settings | switch the theme to system | ok | 344 |
| 58 | today | click the Today sidebar button (system theme) | ok | 68 |
| 59 | roadmap | click the Roadmap sidebar button (system theme) | ok | 187 |
| 60 | phase | click the Phase sidebar button (system theme) | ok | 146 |
| 61 | practice | click the Practice sidebar button (system theme) | ok | 66 |
| 62 | quiz | click the Quizzes sidebar button (system theme) | ok | 190 |
| 63 | review | click the Review sidebar button (system theme) | ok | 27 |
| 64 | projects | click the Projects sidebar button (system theme) | ok | 2377 |
| 65 | journal | click the Log sidebar button (system theme) | ok | 77 |
| 66 | stats | click the Progress sidebar button (system theme) | ok | 199 |
| 67 | library | click the Library sidebar button (system theme) | ok | 2931 |
| 68 | settings | click the Settings sidebar button (system theme) | ok | 166 |
| 69 | today | check no control escapes the Today page | ok | 0 |
| 70 | roadmap | check no control escapes the Roadmap page | ok | 0 |
| 71 | phase | check no control escapes the Phase page | ok | 0 |
| 72 | practice | check no control escapes the Practice page | ok | 0 |
| 73 | quiz | check no control escapes the Quizzes page | ok | 0 |
| 74 | review | check no control escapes the Review page | ok | 0 |
| 75 | projects | check no control escapes the Projects page | ok | 6 |
| 76 | journal | check no control escapes the Log page | ok | 0 |
| 77 | stats | check no control escapes the Progress page | ok | 0 |
| 78 | library | check no control escapes the Library page | ok | 2 |
| 79 | settings | check no control escapes the Settings page | ok | 0 |
| 80 | menu | Go > Today | ok | 54 |
| 81 | menu | Go > Roadmap | ok | 187 |
| 82 | menu | Go > Phase | ok | 154 |
| 83 | menu | Go > Practice | ok | 61 |
| 84 | menu | Go > Quizzes | ok | 96 |
| 85 | menu | Go > Review | ok | 21 |
| 86 | menu | Go > Projects | ok | 892 |
| 87 | menu | Go > Log | ok | 44 |
| 88 | menu | Go > Progress | ok | 151 |
| 89 | menu | Go > Library | ok | 1342 |
| 90 | menu | Go > Settings | ok | 126 |
| 91 | menu | Go > Find | ok | 6 |
| 92 | today | press Ctrl+1 for Today | ok | 60 |
| 93 | roadmap | press Ctrl+2 for Roadmap | ok | 193 |
| 94 | phase | press Ctrl+3 for Phase | ok | 151 |
| 95 | practice | press Ctrl+4 for Practice | ok | 60 |
| 96 | quiz | press Ctrl+5 for Quizzes | ok | 92 |
| 97 | review | press Ctrl+6 for Review | ok | 22 |
| 98 | projects | press Ctrl+7 for Projects | ok | 1045 |
| 99 | journal | press Ctrl+8 for Log | ok | 49 |
| 100 | stats | press Ctrl+9 for Progress | ok | 151 |
| 101 | menu | &File > Export backup... | ok | 100 |
| 102 | menu | &File > Export progress report... | ok | 17 |
| 103 | menu | &File > Take a snapshot | ok | 9 |
| 104 | menu | &File > Restore a snapshot... | ok | 89 |
| 105 | menu | &Help > How this app works | ok | 0 |
| 106 | menu | &Help > Keyboard shortcuts | ok | 14 |
| 107 | menu | &Help > Check for updates | ok | 1 |
| 108 | menu | &Help > About | ok | 0 |
| 109 | roadmap | switch to the Well-rounded software engineer track | ok | 263 |
| 110 | roadmap | switch to the Learn Python properly (no career pressure) track | ok | 191 |
| 111 | roadmap | switch to the Backend & API engineer track | ok | 203 |
| 112 | roadmap | switch to the Data analysis & data engineering track | ok | 167 |
| 113 | roadmap | switch to the AI & machine learning engineer track | ok | 162 |
| 114 | roadmap | switch to the Automation, scripting & scraping track | ok | 165 |
| 115 | roadmap | switch to the DevOps & platform engineering track | ok | 224 |
| 116 | roadmap | switch to the Application security track | ok | 216 |
| 117 | roadmap | switch to the Job-ready in the shortest honest time track | ok | 179 |
| 118 | roadmap | open every phase card from the roadmap | ok | 2044 |
| 119 | roadmap | open every phase outside the plan | ok | 879 |
| 120 | navigation | switch pages 200 times as fast as the event loop allows | slow (5864 ms) | 5864 |
| 121 | phase | walk Next through all 21 phases | ok | 2642 |
| 122 | phase | walk Previous back to the first phase | ok | 2775 |
| 123 | phase | choose every phase from the picker | ok | 2174 |
| 124 | phase | open phase OS Operating rules | ok | 125 |
| 125 | phase | open phase 00 Environment & Git | ok | 131 |
| 126 | phase | open phase 01 Python foundations | ok | 145 |
| 127 | phase | open phase 02 Python engineering | ok | 156 |
| 128 | phase | open phase 03 Packaging & tooling | ok | 95 |
| 129 | phase | open phase 04 Computer science core | ok | 100 |
| 130 | phase | open phase 05 Algorithms & problem solving | ok | 91 |
| 131 | phase | open phase 06 Linux & systems | ok | 116 |
| 132 | phase | open phase 07 Networking | ok | 81 |
| 133 | phase | open phase 08 SQL & PostgreSQL | ok | 105 |
| 134 | phase | open phase 09 Backend engineering | ok | 115 |
| 135 | phase | open phase 10 Automation & web | ok | 164 |
| 136 | phase | open phase 11 Async, concurrency & performance | ok | 92 |
| 137 | phase | open phase 12 Docker, CI/CD & deployment | ok | 90 |
| 138 | phase | open phase 13 Application security | ok | 124 |
| 139 | phase | open phase 14 AI engineering | ok | 190 |
| 140 | phase | open phase 15 Architecture & orchestration | ok | 121 |
| 141 | phase | open phase 16 Systems programming & internals | ok | 110 |
| 142 | phase | open phase 17 Data engineering | ok | 108 |
| 143 | phase | open phase 18 Beyond senior | ok | 117 |
| 144 | phase | open phase 99 Final-boss ladder | ok | 91 |
| 145 | phase | tick every study step in OS | ok | 205 |
| 146 | phase | untick every study step in OS | ok | 195 |
| 147 | phase | tick every study step in 00 | ok | 126 |
| 148 | phase | untick every study step in 00 | ok | 108 |
| 149 | phase | tick every study step in 01 | ok | 260 |
| 150 | phase | untick every study step in 01 | ok | 199 |
| 151 | phase | tick every study step in 02 | ok | 170 |
| 152 | phase | untick every study step in 02 | ok | 152 |
| 153 | phase | tick every study step in 03 | ok | 144 |
| 154 | phase | untick every study step in 03 | ok | 101 |
| 155 | phase | tick every study step in 04 | ok | 179 |
| 156 | phase | untick every study step in 04 | ok | 142 |
| 157 | phase | tick every study step in 05 | ok | 177 |
| 158 | phase | untick every study step in 05 | ok | 171 |
| 159 | phase | tick every study step in 06 | ok | 148 |
| 160 | phase | untick every study step in 06 | ok | 121 |
| 161 | phase | tick every study step in 07 | ok | 104 |
| 162 | phase | untick every study step in 07 | ok | 134 |
| 163 | phase | tick every study step in 08 | ok | 184 |
| 164 | phase | untick every study step in 08 | ok | 117 |
| 165 | phase | tick every study step in 09 | ok | 174 |
| 166 | phase | untick every study step in 09 | ok | 146 |
| 167 | phase | tick every study step in 10 | ok | 108 |
| 168 | phase | untick every study step in 10 | ok | 96 |
| 169 | phase | tick every study step in 11 | ok | 179 |
| 170 | phase | untick every study step in 11 | ok | 175 |
| 171 | phase | tick every study step in 12 | ok | 154 |
| 172 | phase | untick every study step in 12 | ok | 185 |
| 173 | phase | tick every study step in 13 | ok | 138 |
| 174 | phase | untick every study step in 13 | ok | 120 |
| 175 | phase | tick every study step in 14 | ok | 191 |
| 176 | phase | untick every study step in 14 | ok | 169 |
| 177 | phase | tick every study step in 15 | ok | 240 |
| 178 | phase | untick every study step in 15 | ok | 137 |
| 179 | phase | tick every study step in 16 | ok | 146 |
| 180 | phase | untick every study step in 16 | ok | 93 |
| 181 | phase | tick every study step in 17 | ok | 131 |
| 182 | phase | untick every study step in 17 | ok | 122 |
| 183 | phase | tick every study step in 18 | ok | 171 |
| 184 | phase | untick every study step in 18 | ok | 137 |
| 185 | phase | tick every study step in 99 | ok | 176 |
| 186 | phase | untick every study step in 99 | ok | 126 |
| 187 | phase | clear the gate on 00 | ok | 56 |
| 188 | phase | reopen the gate on 00 | ok | 37 |
| 189 | phase | clear the gate on 01 | ok | 82 |
| 190 | phase | reopen the gate on 01 | ok | 41 |
| 191 | phase | clear the gate on 02 | ok | 43 |
| 192 | phase | reopen the gate on 02 | ok | 33 |
| 193 | phase | clear the gate on 03 | ok | 76 |
| 194 | phase | reopen the gate on 03 | ok | 48 |
| 195 | phase | clear the gate on 04 | ok | 57 |
| 196 | phase | reopen the gate on 04 | ok | 36 |
| 197 | phase | clear the gate on 05 | ok | 45 |
| 198 | phase | reopen the gate on 05 | ok | 33 |
| 199 | phase | clear the gate on 06 | ok | 64 |
| 200 | phase | reopen the gate on 06 | ok | 49 |
| 201 | phase | clear the gate on 07 | ok | 53 |
| 202 | phase | reopen the gate on 07 | ok | 50 |
| 203 | phase | clear the gate on 08 | ok | 57 |
| 204 | phase | reopen the gate on 08 | ok | 50 |
| 205 | phase | clear the gate on 09 | ok | 49 |
| 206 | phase | reopen the gate on 09 | ok | 36 |
| 207 | phase | clear the gate on 10 | ok | 47 |
| 208 | phase | reopen the gate on 10 | ok | 44 |
| 209 | phase | clear the gate on 11 | ok | 58 |
| 210 | phase | reopen the gate on 11 | ok | 49 |
| 211 | phase | clear the gate on 12 | ok | 62 |
| 212 | phase | reopen the gate on 12 | ok | 42 |
| 213 | phase | clear the gate on 13 | ok | 61 |
| 214 | phase | reopen the gate on 13 | ok | 51 |
| 215 | phase | clear the gate on 14 | ok | 68 |
| 216 | phase | reopen the gate on 14 | ok | 51 |
| 217 | phase | clear the gate on 15 | ok | 53 |
| 218 | phase | reopen the gate on 15 | ok | 42 |
| 219 | phase | clear the gate on 16 | ok | 45 |
| 220 | phase | reopen the gate on 16 | ok | 36 |
| 221 | phase | clear the gate on 17 | ok | 53 |
| 222 | phase | reopen the gate on 17 | ok | 41 |
| 223 | phase | clear the gate on 18 | ok | 48 |
| 224 | phase | reopen the gate on 18 | ok | 35 |
| 225 | phase | clear the gate on 99 | ok | 45 |
| 226 | phase | reopen the gate on 99 | ok | 42 |
| 227 | phase | open every resource in 00 | ok | 16 |
| 228 | phase | open every resource in 01 | ok | 26 |
| 229 | phase | open every resource in 02 | ok | 22 |
| 230 | phase | open every resource in 03 | ok | 17 |
| 231 | phase | open every resource in 04 | ok | 19 |
| 232 | phase | open every resource in 05 | ok | 16 |
| 233 | phase | open every resource in 06 | ok | 20 |
| 234 | phase | open every resource in 07 | ok | 15 |
| 235 | phase | open every resource in 08 | ok | 23 |
| 236 | phase | open every resource in 09 | ok | 16 |
| 237 | phase | open every resource in 10 | ok | 25 |
| 238 | phase | open every resource in 11 | ok | 27 |
| 239 | phase | open every resource in 12 | ok | 22 |
| 240 | phase | open every resource in 13 | ok | 28 |
| 241 | phase | open every resource in 14 | ok | 28 |
| 242 | phase | open every resource in 15 | ok | 26 |
| 243 | phase | open every resource in 16 | ok | 17 |
| 244 | phase | open every resource in 17 | ok | 27 |
| 245 | phase | open every resource in 18 | ok | 19 |
| 246 | phase | open every resource in 99 | ok | 21 |
| 247 | phase | use the jump row and snippet on OS | ok | 0 |
| 248 | phase | use the jump row and snippet on 00 | ok | 1303 |
| 249 | phase | use the jump row and snippet on 01 | ok | 229 |
| 250 | phase | use the jump row and snippet on 02 | ok | 227 |
| 251 | phase | use the jump row and snippet on 03 | ok | 269 |
| 252 | phase | use the jump row and snippet on 04 | ok | 194 |
| 253 | phase | use the jump row and snippet on 05 | ok | 210 |
| 254 | phase | use the jump row and snippet on 06 | ok | 240 |
| 255 | phase | use the jump row and snippet on 07 | ok | 196 |
| 256 | phase | use the jump row and snippet on 08 | ok | 209 |
| 257 | phase | use the jump row and snippet on 09 | ok | 256 |
| 258 | phase | use the jump row and snippet on 10 | ok | 250 |
| 259 | phase | use the jump row and snippet on 11 | ok | 250 |
| 260 | phase | use the jump row and snippet on 12 | ok | 208 |
| 261 | phase | use the jump row and snippet on 13 | ok | 263 |
| 262 | phase | use the jump row and snippet on 14 | ok | 260 |
| 263 | phase | use the jump row and snippet on 15 | ok | 225 |
| 264 | phase | use the jump row and snippet on 16 | ok | 266 |
| 265 | phase | use the jump row and snippet on 17 | ok | 321 |
| 266 | phase | use the jump row and snippet on 18 | ok | 47 |
| 267 | phase | use the jump row and snippet on 99 | ok | 81 |
| 268 | phase | send a line to the review deck from the right click menu | ok | 170 |
| 269 | phase | type a note in each phase and leave at once | ok | 2385 |
| 270 | phase | the pending note is committed on quit | ok | 185 |
| 271 | practice | filter the list by every phase | ok | 172 |
| 272 | practice | switch the status filter three ways | ok | 37 |
| 273 | practice | walk the list with Next exercise | ok | 47 |
| 274 | practice | run an endless loop and wait it out | ok | 3308 |
| 275 | practice | ask for the solution before passing | ok | 7 |
| 276 | practice | insist on the solution | ok | 13 |
| 277 | practice | type, then press Reset | ok | 6 |
| 278 | practice | p01.001: read the brief | ok | 0 |
| 279 | practice | p01.001: reveal every hint | ok | 20 |
| 280 | practice | p01.001: run an empty editor | ok | 304 |
| 281 | practice | p01.001: run the untouched starter | ok | 281 |
| 282 | practice | p01.001: run the reference solution | ok | 217 |
| 283 | practice | p01.001: read the solution once passed | ok | 20 |
| 284 | practice | p01.002: read the brief | ok | 0 |
| 285 | practice | p01.002: reveal every hint | ok | 8 |
| 286 | practice | p01.002: run an empty editor | ok | 226 |
| 287 | practice | p01.002: run the untouched starter | ok | 232 |
| 288 | practice | p01.002: run the reference solution | ok | 209 |
| 289 | practice | p01.002: read the solution once passed | ok | 17 |
| 290 | practice | p01.003: read the brief | ok | 0 |
| 291 | practice | p01.003: reveal every hint | ok | 9 |
| 292 | practice | p01.003: run an empty editor | ok | 176 |
| 293 | practice | p01.003: run the untouched starter | ok | 215 |
| 294 | practice | p01.003: run the reference solution | ok | 207 |
| 295 | practice | p01.003: read the solution once passed | ok | 24 |
| 296 | practice | p01.004: read the brief | ok | 0 |
| 297 | practice | p01.004: reveal every hint | ok | 11 |
| 298 | practice | p01.004: run an empty editor | ok | 179 |
| 299 | practice | p01.004: run the untouched starter | ok | 212 |
| 300 | practice | p01.004: run the reference solution | ok | 185 |
| 301 | practice | p01.004: read the solution once passed | ok | 19 |
| 302 | practice | p01.005: read the brief | ok | 0 |
| 303 | practice | p01.005: reveal every hint | ok | 13 |
| 304 | practice | p01.005: run an empty editor | ok | 171 |
| 305 | practice | p01.005: run the untouched starter | ok | 190 |
| 306 | practice | p01.005: run the reference solution | ok | 178 |
| 307 | practice | p01.005: read the solution once passed | ok | 25 |
| 308 | practice | p01.006: read the brief | ok | 0 |
| 309 | practice | p01.006: reveal every hint | ok | 9 |
| 310 | practice | p01.006: run an empty editor | ok | 180 |
| 311 | practice | p01.006: run the untouched starter | ok | 205 |
| 312 | practice | p01.006: run the reference solution | ok | 206 |
| 313 | practice | p01.006: read the solution once passed | ok | 20 |
| 314 | practice | p01.007: read the brief | ok | 0 |
| 315 | practice | p01.007: reveal every hint | ok | 9 |
| 316 | practice | p01.007: run an empty editor | ok | 177 |
| 317 | practice | p01.007: run the untouched starter | ok | 219 |
| 318 | practice | p01.007: run the reference solution | ok | 182 |
| 319 | practice | p01.007: read the solution once passed | ok | 24 |
| 320 | practice | p01.008: read the brief | ok | 0 |
| 321 | practice | p01.008: reveal every hint | ok | 9 |
| 322 | practice | p01.008: run an empty editor | ok | 165 |
| 323 | practice | p01.008: run the untouched starter | ok | 200 |
| 324 | practice | p01.008: run the reference solution | ok | 181 |
| 325 | practice | p01.008: read the solution once passed | ok | 18 |
| 326 | practice | p01.009: read the brief | ok | 0 |
| 327 | practice | p01.009: reveal every hint | ok | 9 |
| 328 | practice | p01.009: run an empty editor | ok | 168 |
| 329 | practice | p01.009: run the untouched starter | ok | 201 |
| 330 | practice | p01.009: run the reference solution | ok | 215 |
| 331 | practice | p01.009: read the solution once passed | ok | 28 |
| 332 | practice | p01.010: read the brief | ok | 0 |
| 333 | practice | p01.010: reveal every hint | ok | 13 |
| 334 | practice | p01.010: run an empty editor | ok | 174 |
| 335 | practice | p01.010: run the untouched starter | ok | 222 |
| 336 | practice | p01.010: run the reference solution | ok | 181 |
| 337 | practice | p01.010: read the solution once passed | ok | 25 |
| 338 | practice | p01.011: read the brief | ok | 0 |
| 339 | practice | p01.011: reveal every hint | ok | 11 |
| 340 | practice | p01.011: run an empty editor | ok | 166 |
| 341 | practice | p01.011: run the untouched starter | ok | 181 |
| 342 | practice | p01.011: run the reference solution | ok | 179 |
| 343 | practice | p01.011: read the solution once passed | ok | 16 |
| 344 | practice | p01.012: read the brief | ok | 0 |
| 345 | practice | p01.012: reveal every hint | ok | 7 |
| 346 | practice | p01.012: run an empty editor | ok | 162 |
| 347 | practice | p01.012: run the untouched starter | ok | 201 |
| 348 | practice | p01.012: run the reference solution | ok | 186 |
| 349 | practice | p01.012: read the solution once passed | ok | 16 |
| 350 | practice | p01.013: read the brief | ok | 0 |
| 351 | practice | p01.013: reveal every hint | ok | 9 |
| 352 | practice | p01.013: run an empty editor | ok | 175 |
| 353 | practice | p01.013: run the untouched starter | ok | 195 |
| 354 | practice | p01.013: run the reference solution | ok | 200 |
| 355 | practice | p01.013: read the solution once passed | ok | 29 |
| 356 | practice | p01.014: read the brief | ok | 0 |
| 357 | practice | p01.014: reveal every hint | ok | 13 |
| 358 | practice | p01.014: run an empty editor | ok | 176 |
| 359 | practice | p01.014: run the untouched starter | ok | 208 |
| 360 | practice | p01.014: run the reference solution | ok | 184 |
| 361 | practice | p01.014: read the solution once passed | ok | 21 |
| 362 | practice | p01.015: read the brief | ok | 0 |
| 363 | practice | p01.015: reveal every hint | ok | 12 |
| 364 | practice | p01.015: run an empty editor | ok | 179 |
| 365 | practice | p01.015: run the untouched starter | ok | 217 |
| 366 | practice | p01.015: run the reference solution | ok | 197 |
| 367 | practice | p01.015: read the solution once passed | ok | 19 |
| 368 | practice | p01.016: read the brief | ok | 0 |
| 369 | practice | p01.016: reveal every hint | ok | 10 |
| 370 | practice | p01.016: run an empty editor | ok | 169 |
| 371 | practice | p01.016: run the untouched starter | ok | 217 |
| 372 | practice | p01.016: run the reference solution | ok | 192 |
| 373 | practice | p01.016: read the solution once passed | ok | 37 |
| 374 | practice | p01.017: read the brief | ok | 0 |
| 375 | practice | p01.017: reveal every hint | ok | 10 |
| 376 | practice | p01.017: run an empty editor | ok | 163 |
| 377 | practice | p01.017: run the untouched starter | ok | 201 |
| 378 | practice | p01.017: run the reference solution | ok | 178 |
| 379 | practice | p01.017: read the solution once passed | ok | 25 |
| 380 | practice | p01.018: read the brief | ok | 0 |
| 381 | practice | p01.018: reveal every hint | ok | 9 |
| 382 | practice | p01.018: run an empty editor | ok | 155 |
| 383 | practice | p01.018: run the untouched starter | ok | 196 |
| 384 | practice | p01.018: run the reference solution | ok | 187 |
| 385 | practice | p01.018: read the solution once passed | ok | 15 |
| 386 | practice | p01.019: read the brief | ok | 0 |
| 387 | practice | p01.019: reveal every hint | ok | 7 |
| 388 | practice | p01.019: run an empty editor | ok | 168 |
| 389 | practice | p01.019: run the untouched starter | ok | 190 |
| 390 | practice | p01.019: run the reference solution | ok | 169 |
| 391 | practice | p01.019: read the solution once passed | ok | 18 |
| 392 | practice | p01.020: read the brief | ok | 0 |
| 393 | practice | p01.020: reveal every hint | ok | 8 |
| 394 | practice | p01.020: run an empty editor | ok | 164 |
| 395 | practice | p01.020: run the untouched starter | ok | 211 |
| 396 | practice | p01.020: run the reference solution | ok | 175 |
| 397 | practice | p01.020: read the solution once passed | ok | 19 |
| 398 | practice | p01.021: read the brief | ok | 0 |
| 399 | practice | p01.021: reveal every hint | ok | 9 |
| 400 | practice | p01.021: run an empty editor | ok | 156 |
| 401 | practice | p01.021: run the untouched starter | ok | 217 |
| 402 | practice | p01.021: run the reference solution | ok | 172 |
| 403 | practice | p01.021: read the solution once passed | ok | 18 |
| 404 | practice | p01.022: read the brief | ok | 0 |
| 405 | practice | p01.022: reveal every hint | ok | 11 |
| 406 | practice | p01.022: run an empty editor | ok | 164 |
| 407 | practice | p01.022: run the untouched starter | ok | 196 |
| 408 | practice | p01.022: run the reference solution | ok | 176 |
| 409 | practice | p01.022: read the solution once passed | ok | 17 |
| 410 | practice | p01.023: read the brief | ok | 0 |
| 411 | practice | p01.023: reveal every hint | ok | 9 |
| 412 | practice | p01.023: run an empty editor | ok | 176 |
| 413 | practice | p01.023: run the untouched starter | ok | 188 |
| 414 | practice | p01.023: run the reference solution | ok | 185 |
| 415 | practice | p01.023: read the solution once passed | ok | 27 |
| 416 | practice | p01.024: read the brief | ok | 0 |
| 417 | practice | p01.024: reveal every hint | ok | 13 |
| 418 | practice | p01.024: run an empty editor | ok | 159 |
| 419 | practice | p01.024: run the untouched starter | ok | 200 |
| 420 | practice | p01.024: run the reference solution | ok | 213 |
| 421 | practice | p01.024: read the solution once passed | ok | 27 |
| 422 | practice | p01.025: read the brief | ok | 0 |
| 423 | practice | p01.025: reveal every hint | ok | 12 |
| 424 | practice | p01.025: run an empty editor | ok | 168 |
| 425 | practice | p01.025: run the untouched starter | ok | 202 |
| 426 | practice | p01.025: run the reference solution | ok | 172 |
| 427 | practice | p01.025: read the solution once passed | ok | 14 |
| 428 | practice | p01.026: read the brief | ok | 0 |
| 429 | practice | p01.026: reveal every hint | ok | 10 |
| 430 | practice | p01.026: run an empty editor | ok | 150 |
| 431 | practice | p01.026: run the untouched starter | ok | 221 |
| 432 | practice | p01.026: run the reference solution | ok | 200 |
| 433 | practice | p01.026: read the solution once passed | ok | 23 |
| 434 | practice | p01.027: read the brief | ok | 0 |
| 435 | practice | p01.027: reveal every hint | ok | 7 |
| 436 | practice | p01.027: run an empty editor | ok | 168 |
| 437 | practice | p01.027: run the untouched starter | ok | 231 |
| 438 | practice | p01.027: run the reference solution | ok | 178 |
| 439 | practice | p01.027: read the solution once passed | ok | 16 |
| 440 | practice | p01.028: read the brief | ok | 0 |
| 441 | practice | p01.028: reveal every hint | ok | 10 |
| 442 | practice | p01.028: run an empty editor | ok | 167 |
| 443 | practice | p01.028: run the untouched starter | ok | 188 |
| 444 | practice | p01.028: run the reference solution | ok | 171 |
| 445 | practice | p01.028: read the solution once passed | ok | 27 |
| 446 | practice | p01.029: read the brief | ok | 0 |
| 447 | practice | p01.029: reveal every hint | ok | 12 |
| 448 | practice | p01.029: run an empty editor | ok | 167 |
| 449 | practice | p01.029: run the untouched starter | ok | 197 |
| 450 | practice | p01.029: run the reference solution | ok | 196 |
| 451 | practice | p01.029: read the solution once passed | ok | 21 |
| 452 | practice | p01.030: read the brief | ok | 0 |
| 453 | practice | p01.030: reveal every hint | ok | 11 |
| 454 | practice | p01.030: run an empty editor | ok | 157 |
| 455 | practice | p01.030: run the untouched starter | ok | 216 |
| 456 | practice | p01.030: run the reference solution | ok | 202 |
| 457 | practice | p01.030: read the solution once passed | ok | 27 |
| 458 | practice | p01.031: read the brief | ok | 0 |
| 459 | practice | p01.031: reveal every hint | ok | 10 |
| 460 | practice | p01.031: run an empty editor | ok | 177 |
| 461 | practice | p01.031: run the untouched starter | ok | 208 |
| 462 | practice | p01.031: run the reference solution | ok | 172 |
| 463 | practice | p01.031: read the solution once passed | ok | 20 |
| 464 | practice | p01.032: read the brief | ok | 0 |
| 465 | practice | p01.032: reveal every hint | ok | 6 |
| 466 | practice | p01.032: run an empty editor | ok | 166 |
| 467 | practice | p01.032: run the untouched starter | ok | 203 |
| 468 | practice | p01.032: run the reference solution | ok | 181 |
| 469 | practice | p01.032: read the solution once passed | ok | 24 |
| 470 | practice | p01.033: read the brief | ok | 0 |
| 471 | practice | p01.033: reveal every hint | ok | 12 |
| 472 | practice | p01.033: run an empty editor | ok | 170 |
| 473 | practice | p01.033: run the untouched starter | ok | 196 |
| 474 | practice | p01.033: run the reference solution | ok | 176 |
| 475 | practice | p01.033: read the solution once passed | ok | 19 |
| 476 | practice | p01.034: read the brief | ok | 0 |
| 477 | practice | p01.034: reveal every hint | ok | 9 |
| 478 | practice | p01.034: run an empty editor | ok | 169 |
| 479 | practice | p01.034: run the untouched starter | ok | 187 |
| 480 | practice | p01.034: run the reference solution | ok | 181 |
| 481 | practice | p01.034: read the solution once passed | ok | 15 |
| 482 | practice | p01.035: read the brief | ok | 0 |
| 483 | practice | p01.035: reveal every hint | ok | 9 |
| 484 | practice | p01.035: run an empty editor | ok | 167 |
| 485 | practice | p01.035: run the untouched starter | ok | 199 |
| 486 | practice | p01.035: run the reference solution | ok | 201 |
| 487 | practice | p01.035: read the solution once passed | ok | 20 |
| 488 | practice | p01.036: read the brief | ok | 0 |
| 489 | practice | p01.036: reveal every hint | ok | 8 |
| 490 | practice | p01.036: run an empty editor | ok | 184 |
| 491 | practice | p01.036: run the untouched starter | ok | 206 |
| 492 | practice | p01.036: run the reference solution | ok | 195 |
| 493 | practice | p01.036: read the solution once passed | ok | 13 |
| 494 | practice | p02.001: read the brief | ok | 0 |
| 495 | practice | p02.001: reveal every hint | ok | 8 |
| 496 | practice | p02.001: run an empty editor | ok | 159 |
| 497 | practice | p02.001: run the untouched starter | ok | 193 |
| 498 | practice | p02.001: run the reference solution | ok | 190 |
| 499 | practice | p02.001: read the solution once passed | ok | 18 |
| 500 | practice | p02.002: read the brief | ok | 0 |
| 501 | practice | p02.002: reveal every hint | ok | 12 |
| 502 | practice | p02.002: run an empty editor | ok | 185 |
| 503 | practice | p02.002: run the untouched starter | ok | 221 |
| 504 | practice | p02.002: run the reference solution | ok | 167 |
| 505 | practice | p02.002: read the solution once passed | ok | 14 |
| 506 | practice | p02.003: read the brief | ok | 0 |
| 507 | practice | p02.003: reveal every hint | ok | 7 |
| 508 | practice | p02.003: run an empty editor | ok | 191 |
| 509 | practice | p02.003: run the untouched starter | ok | 199 |
| 510 | practice | p02.003: run the reference solution | ok | 181 |
| 511 | practice | p02.003: read the solution once passed | ok | 17 |
| 512 | practice | p02.004: read the brief | ok | 0 |
| 513 | practice | p02.004: reveal every hint | ok | 10 |
| 514 | practice | p02.004: run an empty editor | ok | 164 |
| 515 | practice | p02.004: run the untouched starter | ok | 171 |
| 516 | practice | p02.004: run the reference solution | ok | 171 |
| 517 | practice | p02.004: read the solution once passed | ok | 16 |
| 518 | practice | p02.005: read the brief | ok | 0 |
| 519 | practice | p02.005: reveal every hint | ok | 8 |
| 520 | practice | p02.005: run an empty editor | ok | 216 |
| 521 | practice | p02.005: run the untouched starter | ok | 180 |
| 522 | practice | p02.005: run the reference solution | ok | 195 |
| 523 | practice | p02.005: read the solution once passed | ok | 25 |
| 524 | practice | p02.006: read the brief | ok | 0 |
| 525 | practice | p02.006: reveal every hint | ok | 13 |
| 526 | practice | p02.006: run an empty editor | ok | 158 |
| 527 | practice | p02.006: run the untouched starter | ok | 163 |
| 528 | practice | p02.006: run the reference solution | ok | 172 |
| 529 | practice | p02.006: read the solution once passed | ok | 14 |
| 530 | practice | p02.007: read the brief | ok | 0 |
| 531 | practice | p02.007: reveal every hint | ok | 8 |
| 532 | practice | p02.007: run an empty editor | ok | 163 |
| 533 | practice | p02.007: run the untouched starter | ok | 189 |
| 534 | practice | p02.007: run the reference solution | ok | 190 |
| 535 | practice | p02.007: read the solution once passed | ok | 14 |
| 536 | practice | p02.008: read the brief | ok | 0 |
| 537 | practice | p02.008: reveal every hint | ok | 10 |
| 538 | practice | p02.008: run an empty editor | ok | 181 |
| 539 | practice | p02.008: run the untouched starter | ok | 200 |
| 540 | practice | p02.008: run the reference solution | ok | 182 |
| 541 | practice | p02.008: read the solution once passed | ok | 18 |
| 542 | practice | p02.009: read the brief | ok | 0 |
| 543 | practice | p02.009: reveal every hint | ok | 11 |
| 544 | practice | p02.009: run an empty editor | ok | 167 |
| 545 | practice | p02.009: run the untouched starter | ok | 185 |
| 546 | practice | p02.009: run the reference solution | ok | 178 |
| 547 | practice | p02.009: read the solution once passed | ok | 17 |
| 548 | practice | p02.010: read the brief | ok | 0 |
| 549 | practice | p02.010: reveal every hint | ok | 18 |
| 550 | practice | p02.010: run an empty editor | ok | 185 |
| 551 | practice | p02.010: run the untouched starter | ok | 188 |
| 552 | practice | p02.010: run the reference solution | ok | 186 |
| 553 | practice | p02.010: read the solution once passed | ok | 15 |
| 554 | practice | p02.011: read the brief | ok | 0 |
| 555 | practice | p02.011: reveal every hint | ok | 7 |
| 556 | practice | p02.011: run an empty editor | ok | 153 |
| 557 | practice | p02.011: run the untouched starter | ok | 191 |
| 558 | practice | p02.011: run the reference solution | ok | 177 |
| 559 | practice | p02.011: read the solution once passed | ok | 17 |
| 560 | practice | p02.012: read the brief | ok | 0 |
| 561 | practice | p02.012: reveal every hint | ok | 7 |
| 562 | practice | p02.012: run an empty editor | ok | 154 |
| 563 | practice | p02.012: run the untouched starter | ok | 231 |
| 564 | practice | p02.012: run the reference solution | ok | 171 |
| 565 | practice | p02.012: read the solution once passed | ok | 31 |
| 566 | practice | p02.013: read the brief | ok | 0 |
| 567 | practice | p02.013: reveal every hint | ok | 12 |
| 568 | practice | p02.013: run an empty editor | ok | 175 |
| 569 | practice | p02.013: run the untouched starter | ok | 199 |
| 570 | practice | p02.013: run the reference solution | ok | 210 |
| 571 | practice | p02.013: read the solution once passed | ok | 26 |
| 572 | practice | p02.014: read the brief | ok | 0 |
| 573 | practice | p02.014: reveal every hint | ok | 13 |
| 574 | practice | p02.014: run an empty editor | ok | 176 |
| 575 | practice | p02.014: run the untouched starter | ok | 202 |
| 576 | practice | p02.014: run the reference solution | ok | 193 |
| 577 | practice | p02.014: read the solution once passed | ok | 20 |
| 578 | practice | p02.015: read the brief | ok | 0 |
| 579 | practice | p02.015: reveal every hint | ok | 8 |
| 580 | practice | p02.015: run an empty editor | ok | 177 |
| 581 | practice | p02.015: run the untouched starter | ok | 200 |
| 582 | practice | p02.015: run the reference solution | ok | 194 |
| 583 | practice | p02.015: read the solution once passed | ok | 36 |
| 584 | practice | p02.016: read the brief | ok | 0 |
| 585 | practice | p02.016: reveal every hint | ok | 13 |
| 586 | practice | p02.016: run an empty editor | ok | 187 |
| 587 | practice | p02.016: run the untouched starter | ok | 254 |
| 588 | practice | p02.016: run the reference solution | ok | 233 |
| 589 | practice | p02.016: read the solution once passed | ok | 39 |
| 590 | practice | p04.011: read the brief | ok | 0 |
| 591 | practice | p04.011: reveal every hint | ok | 25 |
| 592 | practice | p04.011: run an empty editor | ok | 184 |
| 593 | practice | p04.011: run the untouched starter | ok | 205 |
| 594 | practice | p04.011: run the reference solution | ok | 190 |
| 595 | practice | p04.011: read the solution once passed | ok | 25 |
| 596 | practice | p04.012: read the brief | ok | 0 |
| 597 | practice | p04.012: reveal every hint | ok | 32 |
| 598 | practice | p04.012: run an empty editor | ok | 175 |
| 599 | practice | p04.012: run the untouched starter | ok | 221 |
| 600 | practice | p04.012: run the reference solution | ok | 205 |
| 601 | practice | p04.012: read the solution once passed | ok | 28 |
| 602 | practice | p04.013: read the brief | ok | 0 |
| 603 | practice | p04.013: reveal every hint | ok | 14 |
| 604 | practice | p04.013: run an empty editor | ok | 187 |
| 605 | practice | p04.013: run the untouched starter | ok | 194 |
| 606 | practice | p04.013: run the reference solution | ok | 191 |
| 607 | practice | p04.013: read the solution once passed | ok | 26 |
| 608 | practice | p04.001: read the brief | ok | 0 |
| 609 | practice | p04.001: reveal every hint | ok | 10 |
| 610 | practice | p04.001: run an empty editor | ok | 176 |
| 611 | practice | p04.001: run the untouched starter | ok | 231 |
| 612 | practice | p04.001: run the reference solution | ok | 228 |
| 613 | practice | p04.001: read the solution once passed | ok | 34 |
| 614 | practice | p04.002: read the brief | ok | 0 |
| 615 | practice | p04.002: reveal every hint | ok | 13 |
| 616 | practice | p04.002: run an empty editor | ok | 171 |
| 617 | practice | p04.002: run the untouched starter | ok | 175 |
| 618 | practice | p04.002: run the reference solution | ok | 177 |
| 619 | practice | p04.002: read the solution once passed | ok | 17 |
| 620 | practice | p04.003: read the brief | ok | 0 |
| 621 | practice | p04.003: reveal every hint | ok | 8 |
| 622 | practice | p04.003: run an empty editor | ok | 177 |
| 623 | practice | p04.003: run the untouched starter | ok | 204 |
| 624 | practice | p04.003: run the reference solution | ok | 177 |
| 625 | practice | p04.003: read the solution once passed | ok | 20 |
| 626 | practice | p04.004: read the brief | ok | 0 |
| 627 | practice | p04.004: reveal every hint | ok | 9 |
| 628 | practice | p04.004: run an empty editor | ok | 192 |
| 629 | practice | p04.004: run the untouched starter | ok | 186 |
| 630 | practice | p04.004: run the reference solution | ok | 195 |
| 631 | practice | p04.004: read the solution once passed | ok | 18 |
| 632 | practice | p04.005: read the brief | ok | 0 |
| 633 | practice | p04.005: reveal every hint | ok | 8 |
| 634 | practice | p04.005: run an empty editor | ok | 176 |
| 635 | practice | p04.005: run the untouched starter | ok | 198 |
| 636 | practice | p04.005: run the reference solution | ok | 186 |
| 637 | practice | p04.005: read the solution once passed | ok | 24 |
| 638 | practice | p04.006: read the brief | ok | 0 |
| 639 | practice | p04.006: reveal every hint | ok | 8 |
| 640 | practice | p04.006: run an empty editor | ok | 170 |
| 641 | practice | p04.006: run the untouched starter | ok | 230 |
| 642 | practice | p04.006: run the reference solution | ok | 200 |
| 643 | practice | p04.006: read the solution once passed | ok | 21 |
| 644 | practice | p04.007: read the brief | ok | 0 |
| 645 | practice | p04.007: reveal every hint | ok | 12 |
| 646 | practice | p04.007: run an empty editor | ok | 170 |
| 647 | practice | p04.007: run the untouched starter | ok | 209 |
| 648 | practice | p04.007: run the reference solution | ok | 174 |
| 649 | practice | p04.007: read the solution once passed | ok | 15 |
| 650 | practice | p04.008: read the brief | ok | 0 |
| 651 | practice | p04.008: reveal every hint | ok | 8 |
| 652 | practice | p04.008: run an empty editor | ok | 171 |
| 653 | practice | p04.008: run the untouched starter | ok | 186 |
| 654 | practice | p04.008: run the reference solution | ok | 182 |
| 655 | practice | p04.008: read the solution once passed | ok | 22 |
| 656 | practice | p04.009: read the brief | ok | 0 |
| 657 | practice | p04.009: reveal every hint | ok | 7 |
| 658 | practice | p04.009: run an empty editor | ok | 171 |
| 659 | practice | p04.009: run the untouched starter | ok | 200 |
| 660 | practice | p04.009: run the reference solution | ok | 186 |
| 661 | practice | p04.009: read the solution once passed | ok | 15 |
| 662 | practice | p04.010: read the brief | ok | 0 |
| 663 | practice | p04.010: reveal every hint | ok | 10 |
| 664 | practice | p04.010: run an empty editor | ok | 162 |
| 665 | practice | p04.010: run the untouched starter | ok | 193 |
| 666 | practice | p04.010: run the reference solution | ok | 214 |
| 667 | practice | p04.010: read the solution once passed | ok | 19 |
| 668 | practice | p05.001: read the brief | ok | 0 |
| 669 | practice | p05.001: reveal every hint | ok | 7 |
| 670 | practice | p05.001: run an empty editor | ok | 159 |
| 671 | practice | p05.001: run the untouched starter | ok | 224 |
| 672 | practice | p05.001: run the reference solution | ok | 198 |
| 673 | practice | p05.001: read the solution once passed | ok | 19 |
| 674 | practice | p05.002: read the brief | ok | 0 |
| 675 | practice | p05.002: reveal every hint | ok | 12 |
| 676 | practice | p05.002: run an empty editor | ok | 174 |
| 677 | practice | p05.002: run the untouched starter | ok | 197 |
| 678 | practice | p05.002: run the reference solution | ok | 189 |
| 679 | practice | p05.002: read the solution once passed | ok | 24 |
| 680 | practice | p05.003: read the brief | ok | 0 |
| 681 | practice | p05.003: reveal every hint | ok | 12 |
| 682 | practice | p05.003: run an empty editor | ok | 184 |
| 683 | practice | p05.003: run the untouched starter | ok | 187 |
| 684 | practice | p05.003: run the reference solution | ok | 179 |
| 685 | practice | p05.003: read the solution once passed | ok | 24 |
| 686 | practice | p05.004: read the brief | ok | 0 |
| 687 | practice | p05.004: reveal every hint | ok | 10 |
| 688 | practice | p05.004: run an empty editor | ok | 190 |
| 689 | practice | p05.004: run the untouched starter | ok | 213 |
| 690 | practice | p05.004: run the reference solution | ok | 202 |
| 691 | practice | p05.004: read the solution once passed | ok | 27 |
| 692 | practice | p05.005: read the brief | ok | 0 |
| 693 | practice | p05.005: reveal every hint | ok | 7 |
| 694 | practice | p05.005: run an empty editor | ok | 181 |
| 695 | practice | p05.005: run the untouched starter | ok | 215 |
| 696 | practice | p05.005: run the reference solution | ok | 221 |
| 697 | practice | p05.005: read the solution once passed | ok | 13 |
| 698 | practice | p05.006: read the brief | ok | 0 |
| 699 | practice | p05.006: reveal every hint | ok | 7 |
| 700 | practice | p05.006: run an empty editor | ok | 172 |
| 701 | practice | p05.006: run the untouched starter | ok | 189 |
| 702 | practice | p05.006: run the reference solution | ok | 185 |
| 703 | practice | p05.006: read the solution once passed | ok | 13 |
| 704 | practice | p05.007: read the brief | ok | 0 |
| 705 | practice | p05.007: reveal every hint | ok | 10 |
| 706 | practice | p05.007: run an empty editor | ok | 166 |
| 707 | practice | p05.007: run the untouched starter | ok | 205 |
| 708 | practice | p05.007: run the reference solution | ok | 228 |
| 709 | practice | p05.007: read the solution once passed | ok | 20 |
| 710 | practice | p05.008: read the brief | ok | 0 |
| 711 | practice | p05.008: reveal every hint | ok | 10 |
| 712 | practice | p05.008: run an empty editor | ok | 165 |
| 713 | practice | p05.008: run the untouched starter | ok | 195 |
| 714 | practice | p05.008: run the reference solution | ok | 173 |
| 715 | practice | p05.008: read the solution once passed | ok | 21 |
| 716 | practice | p05.009: read the brief | ok | 0 |
| 717 | practice | p05.009: reveal every hint | ok | 10 |
| 718 | practice | p05.009: run an empty editor | ok | 185 |
| 719 | practice | p05.009: run the untouched starter | ok | 206 |
| 720 | practice | p05.009: run the reference solution | ok | 188 |
| 721 | practice | p05.009: read the solution once passed | ok | 15 |
| 722 | practice | p05.010: read the brief | ok | 0 |
| 723 | practice | p05.010: reveal every hint | ok | 7 |
| 724 | practice | p05.010: run an empty editor | ok | 175 |
| 725 | practice | p05.010: run the untouched starter | ok | 224 |
| 726 | practice | p05.010: run the reference solution | ok | 236 |
| 727 | practice | p05.010: read the solution once passed | ok | 29 |
| 728 | practice | p03.001: read the brief | ok | 0 |
| 729 | practice | p03.001: reveal every hint | ok | 8 |
| 730 | practice | p03.001: run an empty editor | ok | 159 |
| 731 | practice | p03.001: run the untouched starter | ok | 183 |
| 732 | practice | p03.001: run the reference solution | ok | 177 |
| 733 | practice | p03.001: read the solution once passed | ok | 16 |
| 734 | practice | p03.002: read the brief | ok | 0 |
| 735 | practice | p03.002: reveal every hint | ok | 13 |
| 736 | practice | p03.002: run an empty editor | ok | 199 |
| 737 | practice | p03.002: run the untouched starter | ok | 183 |
| 738 | practice | p03.002: run the reference solution | ok | 204 |
| 739 | practice | p03.002: read the solution once passed | ok | 21 |
| 740 | practice | p03.003: read the brief | ok | 0 |
| 741 | practice | p03.003: reveal every hint | ok | 15 |
| 742 | practice | p03.003: run an empty editor | ok | 169 |
| 743 | practice | p03.003: run the untouched starter | ok | 201 |
| 744 | practice | p03.003: run the reference solution | ok | 198 |
| 745 | practice | p03.003: read the solution once passed | ok | 21 |
| 746 | practice | p03.004: read the brief | ok | 0 |
| 747 | practice | p03.004: reveal every hint | ok | 11 |
| 748 | practice | p03.004: run an empty editor | ok | 179 |
| 749 | practice | p03.004: run the untouched starter | ok | 200 |
| 750 | practice | p03.004: run the reference solution | ok | 213 |
| 751 | practice | p03.004: read the solution once passed | ok | 22 |
| 752 | practice | p08.001: read the brief | ok | 0 |
| 753 | practice | p08.001: reveal every hint | ok | 10 |
| 754 | practice | p08.001: run an empty editor | ok | 182 |
| 755 | practice | p08.001: run the untouched starter | ok | 199 |
| 756 | practice | p08.001: run the reference solution | ok | 180 |
| 757 | practice | p08.001: read the solution once passed | ok | 15 |
| 758 | practice | p08.002: read the brief | ok | 0 |
| 759 | practice | p08.002: reveal every hint | ok | 10 |
| 760 | practice | p08.002: run an empty editor | ok | 172 |
| 761 | practice | p08.002: run the untouched starter | ok | 235 |
| 762 | practice | p08.002: run the reference solution | ok | 200 |
| 763 | practice | p08.002: read the solution once passed | ok | 21 |
| 764 | practice | p08.003: read the brief | ok | 0 |
| 765 | practice | p08.003: reveal every hint | ok | 11 |
| 766 | practice | p08.003: run an empty editor | ok | 183 |
| 767 | practice | p08.003: run the untouched starter | ok | 209 |
| 768 | practice | p08.003: run the reference solution | ok | 194 |
| 769 | practice | p08.003: read the solution once passed | ok | 18 |
| 770 | practice | p08.004: read the brief | ok | 0 |
| 771 | practice | p08.004: reveal every hint | ok | 10 |
| 772 | practice | p08.004: run an empty editor | ok | 167 |
| 773 | practice | p08.004: run the untouched starter | ok | 190 |
| 774 | practice | p08.004: run the reference solution | ok | 182 |
| 775 | practice | p08.004: read the solution once passed | ok | 14 |
| 776 | practice | p09.001: read the brief | ok | 0 |
| 777 | practice | p09.001: reveal every hint | ok | 9 |
| 778 | practice | p09.001: run an empty editor | ok | 159 |
| 779 | practice | p09.001: run the untouched starter | ok | 201 |
| 780 | practice | p09.001: run the reference solution | ok | 185 |
| 781 | practice | p09.001: read the solution once passed | ok | 13 |
| 782 | practice | p09.002: read the brief | ok | 0 |
| 783 | practice | p09.002: reveal every hint | ok | 11 |
| 784 | practice | p09.002: run an empty editor | ok | 169 |
| 785 | practice | p09.002: run the untouched starter | ok | 228 |
| 786 | practice | p09.002: run the reference solution | ok | 186 |
| 787 | practice | p09.002: read the solution once passed | ok | 22 |
| 788 | practice | p09.003: read the brief | ok | 0 |
| 789 | practice | p09.003: reveal every hint | ok | 12 |
| 790 | practice | p09.003: run an empty editor | ok | 165 |
| 791 | practice | p09.003: run the untouched starter | ok | 191 |
| 792 | practice | p09.003: run the reference solution | ok | 224 |
| 793 | practice | p09.003: read the solution once passed | ok | 20 |
| 794 | practice | p10.001: read the brief | ok | 0 |
| 795 | practice | p10.001: reveal every hint | ok | 10 |
| 796 | practice | p10.001: run an empty editor | ok | 177 |
| 797 | practice | p10.001: run the untouched starter | ok | 216 |
| 798 | practice | p10.001: run the reference solution | ok | 182 |
| 799 | practice | p10.001: read the solution once passed | ok | 24 |
| 800 | practice | p10.002: read the brief | ok | 0 |
| 801 | practice | p10.002: reveal every hint | ok | 13 |
| 802 | practice | p10.002: run an empty editor | ok | 177 |
| 803 | practice | p10.002: run the untouched starter | ok | 202 |
| 804 | practice | p10.002: run the reference solution | ok | 207 |
| 805 | practice | p10.002: read the solution once passed | ok | 27 |
| 806 | practice | p10.003: read the brief | ok | 0 |
| 807 | practice | p10.003: reveal every hint | ok | 10 |
| 808 | practice | p10.003: run an empty editor | ok | 182 |
| 809 | practice | p10.003: run the untouched starter | ok | 213 |
| 810 | practice | p10.003: run the reference solution | ok | 195 |
| 811 | practice | p10.003: read the solution once passed | ok | 26 |
| 812 | practice | p11.001: read the brief | ok | 0 |
| 813 | practice | p11.001: reveal every hint | ok | 17 |
| 814 | practice | p11.001: run an empty editor | ok | 339 |
| 815 | practice | p11.001: run the untouched starter | ok | 388 |
| 816 | practice | p11.001: run the reference solution | ok | 484 |
| 817 | practice | p11.001: read the solution once passed | ok | 19 |
| 818 | practice | p11.002: read the brief | ok | 0 |
| 819 | practice | p11.002: reveal every hint | ok | 14 |
| 820 | practice | p11.002: run an empty editor | ok | 350 |
| 821 | practice | p11.002: run the untouched starter | ok | 385 |
| 822 | practice | p11.002: run the reference solution | ok | 863 |
| 823 | practice | p11.002: read the solution once passed | ok | 25 |
| 824 | practice | p11.003: read the brief | ok | 0 |
| 825 | practice | p11.003: reveal every hint | ok | 19 |
| 826 | practice | p11.003: run an empty editor | ok | 350 |
| 827 | practice | p11.003: run the untouched starter | ok | 404 |
| 828 | practice | p11.003: run the reference solution | ok | 532 |
| 829 | practice | p11.003: read the solution once passed | ok | 16 |
| 830 | practice | p13.001: read the brief | ok | 0 |
| 831 | practice | p13.001: reveal every hint | ok | 10 |
| 832 | practice | p13.001: run an empty editor | ok | 195 |
| 833 | practice | p13.001: run the untouched starter | ok | 203 |
| 834 | practice | p13.001: run the reference solution | ok | 683 |
| 835 | practice | p13.001: read the solution once passed | ok | 22 |
| 836 | practice | p13.002: read the brief | ok | 0 |
| 837 | practice | p13.002: reveal every hint | ok | 9 |
| 838 | practice | p13.002: run an empty editor | ok | 175 |
| 839 | practice | p13.002: run the untouched starter | ok | 192 |
| 840 | practice | p13.002: run the reference solution | ok | 213 |
| 841 | practice | p13.002: read the solution once passed | ok | 13 |
| 842 | practice | p13.003: read the brief | ok | 0 |
| 843 | practice | p13.003: reveal every hint | ok | 8 |
| 844 | practice | p13.003: run an empty editor | ok | 165 |
| 845 | practice | p13.003: run the untouched starter | ok | 218 |
| 846 | practice | p13.003: run the reference solution | ok | 204 |
| 847 | practice | p13.003: read the solution once passed | ok | 21 |
| 848 | practice | p14.001: read the brief | ok | 0 |
| 849 | practice | p14.001: reveal every hint | ok | 8 |
| 850 | practice | p14.001: run an empty editor | ok | 186 |
| 851 | practice | p14.001: run the untouched starter | ok | 218 |
| 852 | practice | p14.001: run the reference solution | ok | 209 |
| 853 | practice | p14.001: read the solution once passed | ok | 28 |
| 854 | practice | p14.002: read the brief | ok | 0 |
| 855 | practice | p14.002: reveal every hint | ok | 13 |
| 856 | practice | p14.002: run an empty editor | ok | 198 |
| 857 | practice | p14.002: run the untouched starter | ok | 210 |
| 858 | practice | p14.002: run the reference solution | ok | 204 |
| 859 | practice | p14.002: read the solution once passed | ok | 20 |
| 860 | practice | p14.003: read the brief | ok | 0 |
| 861 | practice | p14.003: reveal every hint | ok | 9 |
| 862 | practice | p14.003: run an empty editor | ok | 227 |
| 863 | practice | p14.003: run the untouched starter | ok | 231 |
| 864 | practice | p14.003: run the reference solution | ok | 190 |
| 865 | practice | p14.003: read the solution once passed | ok | 20 |
| 866 | practice | p14.004: read the brief | ok | 0 |
| 867 | practice | p14.004: reveal every hint | ok | 11 |
| 868 | practice | p14.004: run an empty editor | ok | 155 |
| 869 | practice | p14.004: run the untouched starter | ok | 231 |
| 870 | practice | p14.004: run the reference solution | ok | 172 |
| 871 | practice | p14.004: read the solution once passed | ok | 26 |
| 872 | practice | p06.001: read the brief | ok | 0 |
| 873 | practice | p06.001: reveal every hint | ok | 19 |
| 874 | practice | p06.001: run an empty editor | ok | 183 |
| 875 | practice | p06.001: run the untouched starter | ok | 213 |
| 876 | practice | p06.001: run the reference solution | ok | 188 |
| 877 | practice | p06.001: read the solution once passed | ok | 23 |
| 878 | practice | p06.002: read the brief | ok | 0 |
| 879 | practice | p06.002: reveal every hint | ok | 11 |
| 880 | practice | p06.002: run an empty editor | ok | 206 |
| 881 | practice | p06.002: run the untouched starter | ok | 204 |
| 882 | practice | p06.002: run the reference solution | ok | 242 |
| 883 | practice | p06.002: read the solution once passed | ok | 20 |
| 884 | practice | p06.003: read the brief | ok | 0 |
| 885 | practice | p06.003: reveal every hint | ok | 11 |
| 886 | practice | p06.003: run an empty editor | ok | 188 |
| 887 | practice | p06.003: run the untouched starter | ok | 201 |
| 888 | practice | p06.003: run the reference solution | ok | 256 |
| 889 | practice | p06.003: read the solution once passed | ok | 23 |
| 890 | practice | p06.004: read the brief | ok | 0 |
| 891 | practice | p06.004: reveal every hint | ok | 12 |
| 892 | practice | p06.004: run an empty editor | ok | 170 |
| 893 | practice | p06.004: run the untouched starter | ok | 210 |
| 894 | practice | p06.004: run the reference solution | ok | 199 |
| 895 | practice | p06.004: read the solution once passed | ok | 19 |
| 896 | practice | p07.001: read the brief | ok | 0 |
| 897 | practice | p07.001: reveal every hint | ok | 9 |
| 898 | practice | p07.001: run an empty editor | ok | 195 |
| 899 | practice | p07.001: run the untouched starter | ok | 210 |
| 900 | practice | p07.001: run the reference solution | ok | 208 |
| 901 | practice | p07.001: read the solution once passed | ok | 20 |
| 902 | practice | p07.002: read the brief | ok | 0 |
| 903 | practice | p07.002: reveal every hint | ok | 14 |
| 904 | practice | p07.002: run an empty editor | ok | 180 |
| 905 | practice | p07.002: run the untouched starter | ok | 225 |
| 906 | practice | p07.002: run the reference solution | ok | 197 |
| 907 | practice | p07.002: read the solution once passed | ok | 25 |
| 908 | practice | p07.003: read the brief | ok | 0 |
| 909 | practice | p07.003: reveal every hint | ok | 24 |
| 910 | practice | p07.003: run an empty editor | ok | 177 |
| 911 | practice | p07.003: run the untouched starter | ok | 208 |
| 912 | practice | p07.003: run the reference solution | ok | 188 |
| 913 | practice | p07.003: read the solution once passed | ok | 23 |
| 914 | practice | p07.004: read the brief | ok | 0 |
| 915 | practice | p07.004: reveal every hint | ok | 22 |
| 916 | practice | p07.004: run an empty editor | ok | 168 |
| 917 | practice | p07.004: run the untouched starter | ok | 203 |
| 918 | practice | p07.004: run the reference solution | ok | 186 |
| 919 | practice | p07.004: read the solution once passed | ok | 32 |
| 920 | practice | p12.001: read the brief | ok | 0 |
| 921 | practice | p12.001: reveal every hint | ok | 11 |
| 922 | practice | p12.001: run an empty editor | ok | 173 |
| 923 | practice | p12.001: run the untouched starter | ok | 174 |
| 924 | practice | p12.001: run the reference solution | ok | 176 |
| 925 | practice | p12.001: read the solution once passed | ok | 25 |
| 926 | practice | p12.002: read the brief | ok | 0 |
| 927 | practice | p12.002: reveal every hint | ok | 19 |
| 928 | practice | p12.002: run an empty editor | ok | 172 |
| 929 | practice | p12.002: run the untouched starter | ok | 224 |
| 930 | practice | p12.002: run the reference solution | ok | 210 |
| 931 | practice | p12.002: read the solution once passed | ok | 28 |
| 932 | practice | p12.003: read the brief | ok | 0 |
| 933 | practice | p12.003: reveal every hint | ok | 30 |
| 934 | practice | p12.003: run an empty editor | ok | 181 |
| 935 | practice | p12.003: run the untouched starter | ok | 231 |
| 936 | practice | p12.003: run the reference solution | ok | 228 |
| 937 | practice | p12.003: read the solution once passed | ok | 22 |
| 938 | practice | p15.001: read the brief | ok | 0 |
| 939 | practice | p15.001: reveal every hint | ok | 26 |
| 940 | practice | p15.001: run an empty editor | ok | 182 |
| 941 | practice | p15.001: run the untouched starter | ok | 204 |
| 942 | practice | p15.001: run the reference solution | ok | 183 |
| 943 | practice | p15.001: read the solution once passed | ok | 25 |
| 944 | practice | p15.002: read the brief | ok | 0 |
| 945 | practice | p15.002: reveal every hint | ok | 12 |
| 946 | practice | p15.002: run an empty editor | ok | 164 |
| 947 | practice | p15.002: run the untouched starter | ok | 218 |
| 948 | practice | p15.002: run the reference solution | ok | 184 |
| 949 | practice | p15.002: read the solution once passed | ok | 22 |
| 950 | practice | p15.003: read the brief | ok | 0 |
| 951 | practice | p15.003: reveal every hint | ok | 31 |
| 952 | practice | p15.003: run an empty editor | ok | 181 |
| 953 | practice | p15.003: run the untouched starter | ok | 224 |
| 954 | practice | p15.003: run the reference solution | ok | 216 |
| 955 | practice | p15.003: read the solution once passed | ok | 33 |
| 956 | practice | p16.001: read the brief | ok | 0 |
| 957 | practice | p16.001: reveal every hint | ok | 23 |
| 958 | practice | p16.001: run an empty editor | ok | 186 |
| 959 | practice | p16.001: run the untouched starter | ok | 216 |
| 960 | practice | p16.001: run the reference solution | ok | 190 |
| 961 | practice | p16.001: read the solution once passed | ok | 15 |
| 962 | practice | p16.002: read the brief | ok | 0 |
| 963 | practice | p16.002: reveal every hint | ok | 8 |
| 964 | practice | p16.002: run an empty editor | ok | 166 |
| 965 | practice | p16.002: run the untouched starter | ok | 214 |
| 966 | practice | p16.002: run the reference solution | ok | 199 |
| 967 | practice | p16.002: read the solution once passed | ok | 17 |
| 968 | practice | p16.003: read the brief | ok | 0 |
| 969 | practice | p16.003: reveal every hint | ok | 32 |
| 970 | practice | p16.003: run an empty editor | ok | 187 |
| 971 | practice | p16.003: run the untouched starter | ok | 212 |
| 972 | practice | p16.003: run the reference solution | ok | 203 |
| 973 | practice | p16.003: read the solution once passed | ok | 21 |
| 974 | practice | p17.001: read the brief | ok | 0 |
| 975 | practice | p17.001: reveal every hint | ok | 22 |
| 976 | practice | p17.001: run an empty editor | ok | 174 |
| 977 | practice | p17.001: run the untouched starter | ok | 200 |
| 978 | practice | p17.001: run the reference solution | ok | 182 |
| 979 | practice | p17.001: read the solution once passed | ok | 18 |
| 980 | practice | p17.002: read the brief | ok | 0 |
| 981 | practice | p17.002: reveal every hint | ok | 16 |
| 982 | practice | p17.002: run an empty editor | ok | 163 |
| 983 | practice | p17.002: run the untouched starter | ok | 182 |
| 984 | practice | p17.002: run the reference solution | ok | 184 |
| 985 | practice | p17.002: read the solution once passed | ok | 21 |
| 986 | practice | p17.003: read the brief | ok | 0 |
| 987 | practice | p17.003: reveal every hint | ok | 16 |
| 988 | practice | p17.003: run an empty editor | ok | 166 |
| 989 | practice | p17.003: run the untouched starter | ok | 203 |
| 990 | practice | p17.003: run the reference solution | ok | 196 |
| 991 | practice | p17.003: read the solution once passed | ok | 18 |
| 992 | practice | the counter agrees with the store | ok | 0 |
| 993 | practice | press Run checks and read the result | ok | 157 |
| 994 | practice | close the window while a run is in flight | ok | 12067 |
| 995 | quiz | read the quiz picker | ok | 0 |
| 996 | quiz | answer all 8 questions in q00 correctly | ok | 273 |
| 997 | quiz | answer all 18 questions in q01 correctly | ok | 421 |
| 998 | quiz | answer all 11 questions in q02 correctly | ok | 268 |
| 999 | quiz | answer all 8 questions in q03 correctly | ok | 189 |
| 1000 | quiz | answer all 18 questions in q04 correctly | ok | 447 |
| 1001 | quiz | answer all 12 questions in q05 correctly | ok | 333 |
| 1002 | quiz | answer all 12 questions in q06 correctly | ok | 289 |
| 1003 | quiz | answer all 13 questions in q07 correctly | ok | 312 |
| 1004 | quiz | answer all 14 questions in q08 correctly | ok | 321 |
| 1005 | quiz | answer all 13 questions in q09 correctly | ok | 334 |
| 1006 | quiz | answer all 12 questions in q10 correctly | ok | 381 |
| 1007 | quiz | answer all 10 questions in q11 correctly | ok | 367 |
| 1008 | quiz | answer all 8 questions in q12 correctly | ok | 336 |
| 1009 | quiz | answer all 9 questions in q13 correctly | ok | 300 |
| 1010 | quiz | answer all 10 questions in q14 correctly | ok | 396 |
| 1011 | quiz | answer all 18 questions in q15 correctly | ok | 579 |
| 1012 | quiz | answer all 18 questions in q16 correctly | ok | 590 |
| 1013 | quiz | answer all 14 questions in q17 correctly | ok | 521 |
| 1014 | quiz | answer all 8 questions in q18 correctly | ok | 230 |
| 1015 | quiz | answer all 8 questions in q99 correctly | ok | 215 |
| 1016 | quiz | get every question in q00 wrong | ok | 244 |
| 1017 | quiz | read the wrap-up for q00 | ok | 0 |
| 1018 | quiz | get every question in q01 wrong | ok | 446 |
| 1019 | quiz | read the wrap-up for q01 | ok | 0 |
| 1020 | quiz | get every question in q02 wrong | ok | 280 |
| 1021 | quiz | read the wrap-up for q02 | ok | 0 |
| 1022 | quiz | get every question in q03 wrong | ok | 214 |
| 1023 | quiz | read the wrap-up for q03 | ok | 0 |
| 1024 | quiz | get every question in q04 wrong | ok | 435 |
| 1025 | quiz | read the wrap-up for q04 | ok | 0 |
| 1026 | quiz | get every question in q05 wrong | ok | 289 |
| 1027 | quiz | read the wrap-up for q05 | ok | 0 |
| 1028 | quiz | get every question in q06 wrong | ok | 275 |
| 1029 | quiz | read the wrap-up for q06 | ok | 0 |
| 1030 | quiz | get every question in q07 wrong | ok | 306 |
| 1031 | quiz | read the wrap-up for q07 | ok | 0 |
| 1032 | quiz | get every question in q08 wrong | ok | 374 |
| 1033 | quiz | read the wrap-up for q08 | ok | 0 |
| 1034 | quiz | get every question in q09 wrong | ok | 397 |
| 1035 | quiz | read the wrap-up for q09 | ok | 0 |
| 1036 | quiz | get every question in q10 wrong | ok | 414 |
| 1037 | quiz | read the wrap-up for q10 | ok | 0 |
| 1038 | quiz | get every question in q11 wrong | ok | 270 |
| 1039 | quiz | read the wrap-up for q11 | ok | 0 |
| 1040 | quiz | get every question in q12 wrong | ok | 233 |
| 1041 | quiz | read the wrap-up for q12 | ok | 0 |
| 1042 | quiz | get every question in q13 wrong | ok | 240 |
| 1043 | quiz | read the wrap-up for q13 | ok | 0 |
| 1044 | quiz | get every question in q14 wrong | ok | 276 |
| 1045 | quiz | read the wrap-up for q14 | ok | 0 |
| 1046 | quiz | get every question in q15 wrong | ok | 582 |
| 1047 | quiz | read the wrap-up for q15 | ok | 0 |
| 1048 | quiz | get every question in q16 wrong | ok | 430 |
| 1049 | quiz | read the wrap-up for q16 | ok | 0 |
| 1050 | quiz | get every question in q17 wrong | ok | 386 |
| 1051 | quiz | read the wrap-up for q17 | ok | 0 |
| 1052 | quiz | get every question in q18 wrong | ok | 205 |
| 1053 | quiz | read the wrap-up for q18 | ok | 0 |
| 1054 | quiz | get every question in q99 wrong | ok | 265 |
| 1055 | quiz | read the wrap-up for q99 | ok | 0 |
| 1056 | review | the wrong answers are waiting in review | ok | 4 |
| 1057 | quiz | skip every question without answering | ok | 225 |
| 1058 | quiz | retake it | ok | 12 |
| 1059 | quiz | go back to the picker | ok | 53 |
| 1060 | review | open Review with nothing started | ok | 0 |
| 1061 | review | answer card 1 of 15 | ok | 48 |
| 1062 | review | answer card 2 of 15 | ok | 48 |
| 1063 | review | answer card 3 of 15 | ok | 47 |
| 1064 | review | answer card 4 of 15 | ok | 36 |
| 1065 | review | answer card 5 of 15 | ok | 55 |
| 1066 | review | answer card 6 of 15 | ok | 38 |
| 1067 | review | answer card 7 of 15 | ok | 29 |
| 1068 | review | answer card 8 of 15 | ok | 34 |
| 1069 | review | answer card 9 of 15 | ok | 35 |
| 1070 | review | answer card 10 of 15 | ok | 32 |
| 1071 | review | answer card 11 of 15 | ok | 39 |
| 1072 | review | answer card 12 of 15 | ok | 50 |
| 1073 | review | answer card 13 of 15 | ok | 40 |
| 1074 | review | answer card 14 of 15 | ok | 37 |
| 1075 | review | answer card 15 of 15 | ok | 41 |
| 1076 | review | the session ends with a clear queue | ok | 0 |
| 1077 | review | skip the card in front of you | ok | 9 |
| 1078 | review | work to the daily limit | ok | 149 |
| 1079 | review | the idle screen explains the limit | ok | 0 |
| 1080 | review | open Review with a thousand cards due | ok | 44 |
| 1081 | projects | read all 22 project cards | ok | 1 |
| 1082 | projects | meet every requirement of pj.p00.1 | ok | 68 |
| 1083 | projects | meet every requirement of pj.p01.1 | ok | 49 |
| 1084 | projects | meet every requirement of pj.p01.2 | ok | 47 |
| 1085 | projects | meet every requirement of pj.p02.1 | ok | 55 |
| 1086 | projects | meet every requirement of pj.p02.2 | ok | 48 |
| 1087 | projects | meet every requirement of pj.p03.1 | ok | 50 |
| 1088 | projects | meet every requirement of pj.p04.1 | ok | 55 |
| 1089 | projects | meet every requirement of pj.p05.1 | ok | 48 |
| 1090 | projects | meet every requirement of pj.p06.1 | ok | 56 |
| 1091 | projects | meet every requirement of pj.p07.1 | ok | 61 |
| 1092 | projects | meet every requirement of pj.p08.1 | ok | 55 |
| 1093 | projects | meet every requirement of pj.p09.1 | ok | 78 |
| 1094 | projects | meet every requirement of pj.p10.1 | ok | 78 |
| 1095 | projects | meet every requirement of pj.p11.1 | ok | 60 |
| 1096 | projects | meet every requirement of pj.p12.1 | ok | 81 |
| 1097 | projects | meet every requirement of pj.p13.1 | ok | 61 |
| 1098 | projects | meet every requirement of pj.p14.1 | ok | 57 |
| 1099 | projects | meet every requirement of pj.p14.2 | ok | 59 |
| 1100 | projects | meet every requirement of pj.p15.1 | ok | 63 |
| 1101 | projects | meet every requirement of pj.p16.1 | ok | 52 |
| 1102 | projects | meet every requirement of pj.p17.1 | ok | 83 |
| 1103 | projects | meet every requirement of pj.p99.1 | ok | 85 |
| 1104 | projects | the meters agree once everything is met | ok | 26 |
| 1105 | projects | untick pj.p00.1 again | ok | 68 |
| 1106 | projects | untick pj.p01.1 again | ok | 82 |
| 1107 | projects | untick pj.p01.2 again | ok | 106 |
| 1108 | projects | untick pj.p02.1 again | ok | 97 |
| 1109 | projects | untick pj.p02.2 again | ok | 52 |
| 1110 | projects | untick pj.p03.1 again | ok | 75 |
| 1111 | projects | untick pj.p04.1 again | ok | 77 |
| 1112 | projects | untick pj.p05.1 again | ok | 130 |
| 1113 | projects | untick pj.p06.1 again | ok | 86 |
| 1114 | projects | untick pj.p07.1 again | ok | 95 |
| 1115 | projects | untick pj.p08.1 again | ok | 74 |
| 1116 | projects | untick pj.p09.1 again | ok | 74 |
| 1117 | projects | untick pj.p10.1 again | ok | 65 |
| 1118 | projects | untick pj.p11.1 again | ok | 64 |
| 1119 | projects | untick pj.p12.1 again | ok | 93 |
| 1120 | projects | untick pj.p13.1 again | ok | 57 |
| 1121 | projects | untick pj.p14.1 again | ok | 56 |
| 1122 | projects | untick pj.p14.2 again | ok | 51 |
| 1123 | projects | untick pj.p15.1 again | ok | 57 |
| 1124 | projects | untick pj.p16.1 again | ok | 47 |
| 1125 | projects | untick pj.p17.1 again | ok | 53 |
| 1126 | projects | untick pj.p99.1 again | ok | 77 |
| 1127 | projects | mark pj.p00.1 as Not started | ok | 36 |
| 1128 | projects | mark pj.p00.1 as In progress | ok | 5 |
| 1129 | projects | mark pj.p00.1 as Shipped | ok | 13 |
| 1130 | projects | mark pj.p01.1 as Not started | ok | 7 |
| 1131 | projects | mark pj.p01.1 as In progress | ok | 6 |
| 1132 | projects | mark pj.p01.1 as Shipped | ok | 8 |
| 1133 | projects | mark pj.p01.2 as Not started | ok | 8 |
| 1134 | projects | mark pj.p01.2 as In progress | ok | 5 |
| 1135 | projects | mark pj.p01.2 as Shipped | ok | 7 |
| 1136 | projects | mark pj.p02.1 as Not started | ok | 6 |
| 1137 | projects | mark pj.p02.1 as In progress | ok | 5 |
| 1138 | projects | mark pj.p02.1 as Shipped | ok | 15 |
| 1139 | projects | mark pj.p02.2 as Not started | ok | 7 |
| 1140 | projects | mark pj.p02.2 as In progress | ok | 6 |
| 1141 | projects | mark pj.p02.2 as Shipped | ok | 10 |
| 1142 | projects | mark pj.p03.1 as Not started | ok | 6 |
| 1143 | projects | mark pj.p03.1 as In progress | ok | 10 |
| 1144 | projects | mark pj.p03.1 as Shipped | ok | 8 |
| 1145 | projects | mark pj.p04.1 as Not started | ok | 4 |
| 1146 | projects | mark pj.p04.1 as In progress | ok | 6 |
| 1147 | projects | mark pj.p04.1 as Shipped | ok | 7 |
| 1148 | projects | mark pj.p05.1 as Not started | ok | 5 |
| 1149 | projects | mark pj.p05.1 as In progress | ok | 9 |
| 1150 | projects | mark pj.p05.1 as Shipped | ok | 9 |
| 1151 | projects | mark pj.p06.1 as Not started | ok | 7 |
| 1152 | projects | mark pj.p06.1 as In progress | ok | 7 |
| 1153 | projects | mark pj.p06.1 as Shipped | ok | 8 |
| 1154 | projects | mark pj.p07.1 as Not started | ok | 10 |
| 1155 | projects | mark pj.p07.1 as In progress | ok | 6 |
| 1156 | projects | mark pj.p07.1 as Shipped | ok | 7 |
| 1157 | projects | mark pj.p08.1 as Not started | ok | 7 |
| 1158 | projects | mark pj.p08.1 as In progress | ok | 7 |
| 1159 | projects | mark pj.p08.1 as Shipped | ok | 9 |
| 1160 | projects | mark pj.p09.1 as Not started | ok | 6 |
| 1161 | projects | mark pj.p09.1 as In progress | ok | 8 |
| 1162 | projects | mark pj.p09.1 as Shipped | ok | 7 |
| 1163 | projects | mark pj.p10.1 as Not started | ok | 6 |
| 1164 | projects | mark pj.p10.1 as In progress | ok | 6 |
| 1165 | projects | mark pj.p10.1 as Shipped | ok | 8 |
| 1166 | projects | mark pj.p11.1 as Not started | ok | 6 |
| 1167 | projects | mark pj.p11.1 as In progress | ok | 6 |
| 1168 | projects | mark pj.p11.1 as Shipped | ok | 7 |
| 1169 | projects | mark pj.p12.1 as Not started | ok | 10 |
| 1170 | projects | mark pj.p12.1 as In progress | ok | 8 |
| 1171 | projects | mark pj.p12.1 as Shipped | ok | 10 |
| 1172 | projects | mark pj.p13.1 as Not started | ok | 7 |
| 1173 | projects | mark pj.p13.1 as In progress | ok | 6 |
| 1174 | projects | mark pj.p13.1 as Shipped | ok | 7 |
| 1175 | projects | mark pj.p14.1 as Not started | ok | 6 |
| 1176 | projects | mark pj.p14.1 as In progress | ok | 6 |
| 1177 | projects | mark pj.p14.1 as Shipped | ok | 10 |
| 1178 | projects | mark pj.p14.2 as Not started | ok | 8 |
| 1179 | projects | mark pj.p14.2 as In progress | ok | 8 |
| 1180 | projects | mark pj.p14.2 as Shipped | ok | 15 |
| 1181 | projects | mark pj.p15.1 as Not started | ok | 6 |
| 1182 | projects | mark pj.p15.1 as In progress | ok | 6 |
| 1183 | projects | mark pj.p15.1 as Shipped | ok | 9 |
| 1184 | projects | mark pj.p16.1 as Not started | ok | 5 |
| 1185 | projects | mark pj.p16.1 as In progress | ok | 6 |
| 1186 | projects | mark pj.p16.1 as Shipped | ok | 8 |
| 1187 | projects | mark pj.p17.1 as Not started | ok | 11 |
| 1188 | projects | mark pj.p17.1 as In progress | ok | 10 |
| 1189 | projects | mark pj.p17.1 as Shipped | ok | 10 |
| 1190 | projects | mark pj.p99.1 as Not started | ok | 9 |
| 1191 | projects | mark pj.p99.1 as In progress | ok | 12 |
| 1192 | projects | mark pj.p99.1 as Shipped | ok | 12 |
| 1193 | projects | try each filter | ok | 310 |
| 1194 | projects | record a repo and some notes | ok | 503 |
| 1195 | projects | press Open next to the repo | ok | 1 |
| 1196 | projects | jump to the project's phase | ok | 141 |
| 1197 | projects | ship all 22 projects | ok | 247 |
| 1198 | today | Today agrees | ok | 39 |
| 1199 | projects | press a status button | 14 ms | 14 |
| 1200 | journal | write today's entry | ok | 29 |
| 1201 | journal | add three more days | ok | 103 |
| 1202 | journal | an entry is edited by writing it again | ok | 39 |
| 1203 | journal | delete every entry from the history | ok | 132 |
| 1204 | stats | the charts render with no data at all | ok | 4 |
| 1205 | stats | the charts render with one data point | ok | 89 |
| 1206 | stats | the charts render with a year of data | ok | 148 |
| 1207 | stats | rate every skill in the matrix | ok | 23 |
| 1208 | stats | the table covers the whole plan | ok | 151 |
| 1209 | library | open the Shelf tab | ok | 32 |
| 1210 | library | open the Fields of work tab | ok | 86 |
| 1211 | library | open the Video tab | ok | 64 |
| 1212 | library | open the Certificates tab | ok | 54 |
| 1213 | library | press every Open on the Shelf tab | ok | 6 |
| 1214 | library | press every Open on the Fields of work tab | ok | 0 |
| 1215 | library | press every Open on the Video tab | ok | 7 |
| 1216 | library | press every Open on the Certificates tab | ok | 0 |
| 1217 | library | press every field library button | ok | 57 |
| 1218 | library | cycle c-cs50p through every state | ok | 716 |
| 1219 | library | cycle c-helsinki through every state | ok | 517 |
| 1220 | library | cycle c-fcc-sci through every state | ok | 656 |
| 1221 | library | cycle c-netacad1 through every state | ok | 567 |
| 1222 | library | cycle c-netacad2 through every state | ok | 519 |
| 1223 | library | cycle c-pcep through every state | ok | 496 |
| 1224 | library | cycle c-pcap through every state | ok | 596 |
| 1225 | library | cycle c-hackerrank through every state | ok | 618 |
| 1226 | library | cycle c-kaggle through every state | ok | 696 |
| 1227 | library | cycle c-fcc-data through every state | ok | 606 |
| 1228 | library | cycle c-fcc-ml through every state | ok | 782 |
| 1229 | library | cycle c-hf-agents through every state | ok | 776 |
| 1230 | library | cycle c-hf-llm through every state | ok | 541 |
| 1231 | library | cycle c-hf-mcp through every state | ok | 723 |
| 1232 | library | cycle c-anthropic through every state | ok | 763 |
| 1233 | library | cycle c-google-ml through every state | ok | 543 |
| 1234 | library | cycle c-mit191 through every state | ok | 562 |
| 1235 | library | cycle c-cs50ai through every state | ok | 653 |
| 1236 | library | cycle c-cs50w through every state | ok | 799 |
| 1237 | library | cycle c-google-auto through every state | ok | 670 |
| 1238 | library | cycle c-py4e through every state | ok | 768 |
| 1239 | library | cycle c-mlzoom through every state | ok | 813 |
| 1240 | library | cycle c-dezoom through every state | ok | 679 |
| 1241 | library | cycle c-mit6001 through every state | ok | 577 |
| 1242 | settings | change your name | ok | 2 |
| 1243 | settings | try every track | ok | 50 |
| 1244 | settings | try every experience level | ok | 12 |
| 1245 | settings | tick and untick every goal | ok | 72 |
| 1246 | settings | push every number to both ends | ok | 70 |
| 1247 | settings | turn the update check off and on | ok | 8 |
| 1248 | settings | put every setting back | ok | 21 |
| 1249 | settings | switch the theme to Dark | ok | 421 |
| 1250 | settings | switch the theme to Light | ok | 346 |
| 1251 | settings | switch the theme to Match the system | ok | 3 |
| 1252 | settings | press Open folder | ok | 2 |
| 1253 | settings | export a backup | ok | 5 |
| 1254 | settings | export a progress report | ok | 6 |
| 1255 | settings | take a snapshot | ok | 8 |
| 1256 | settings | cancel an import | ok | 0 |
| 1257 | settings | import the backup back | ok | 0 |
| 1258 | settings | decline a reset | ok | 1 |
| 1259 | settings | accept a reset | ok | 0 |
| 1260 | settings | press Check now | ok | 0 |
| 1261 | search | open search with Ctrl+K | ok | 1 |
| 1262 | search | search for 'nothing' | ok | 0 |
| 1263 | search | search for 'd' | ok | 0 |
| 1264 | search | search for 'Python engineering' | ok | 9 |
| 1265 | search | search for 'Say hello' | ok | 5 |
| 1266 | search | search for 'zzzqqqxx nothing at all' | ok | 2 |
| 1267 | search | press Escape | ok | 7 |
| 1268 | search | press Enter on the first result | ok | 54 |
| 1269 | search | open a result of every kind | ok | 467 |
| 1270 | history | nothing to undo on a fresh store | ok | 0 |
| 1271 | history | tick a line, then undo and redo it | ok | 256 |
| 1272 | history | change a project status, then undo it | ok | 903 |
| 1273 | history | rate a skill, then undo it | ok | 206 |
| 1274 | history | cycle a certificate, then undo it | ok | 1239 |
| 1275 | history | undo and redo from the keyboard | ok | 831 |
| 1276 | history | a new change drops the redo branch | ok | 232 |
| 1277 | history | reopen the app and look for the undo | ok | 0 |
| 1278 | history | the tick survived, the undo did not | ok | 0 |
| 1279 | updates | the button is hidden until there is one | ok | 0 |
| 1280 | updates | a release makes the button appear | ok | 1 |
| 1281 | updates | press it for a release with no changelog | ok | 2 |
| 1282 | updates | press it for a release with a changelog | ok | 7 |
| 1283 | updates | a release with nothing for this platform | ok | 2 |
| 1284 | updates | Help > Check for updates | ok | 2 |
| 1285 | restart | reopen the app on the same store | ok | 0 |
| 1286 | restart | the position is remembered | ok | 0 |
| 1287 | restart | quit inside the autosave window | ok | 3015 |
| 1288 | history | Ctrl+Z undoes a tick | ok | 176 |
| 1289 | history | the advertised redo keys | ok | 136 |
| 1290 | history | the Redo button still works | ok | 0 |
| 1291 | today | Today at 800x600 | ok | 0 |
| 1292 | roadmap | Roadmap at 800x600 | ok | 0 |
| 1293 | phase | Phase at 800x600 | ok | 0 |
| 1294 | practice | Practice at 800x600 | ok | 0 |
| 1295 | quiz | Quizzes at 800x600 | ok | 0 |
| 1296 | review | Review at 800x600 | ok | 0 |
| 1297 | projects | Projects at 800x600 | ok | 4 |
| 1298 | journal | Log at 800x600 | ok | 0 |
| 1299 | stats | Progress at 800x600 | ok | 0 |
| 1300 | library | Library at 800x600 | ok | 3 |
| 1301 | settings | Settings at 800x600 | ok | 0 |
| 1302 | today | Today at 1280x900 | ok | 0 |
| 1303 | roadmap | Roadmap at 1280x900 | ok | 0 |
| 1304 | phase | Phase at 1280x900 | ok | 0 |
| 1305 | practice | Practice at 1280x900 | ok | 0 |
| 1306 | quiz | Quizzes at 1280x900 | ok | 0 |
| 1307 | review | Review at 1280x900 | ok | 0 |
| 1308 | projects | Projects at 1280x900 | ok | 3 |
| 1309 | journal | Log at 1280x900 | ok | 0 |
| 1310 | stats | Progress at 1280x900 | ok | 0 |
| 1311 | library | Library at 1280x900 | ok | 1 |
| 1312 | settings | Settings at 1280x900 | ok | 0 |
| 1313 | today | Today at 2560x1440 | ok | 0 |
| 1314 | roadmap | Roadmap at 2560x1440 | ok | 0 |
| 1315 | phase | Phase at 2560x1440 | ok | 0 |
| 1316 | practice | Practice at 2560x1440 | ok | 0 |
| 1317 | quiz | Quizzes at 2560x1440 | ok | 0 |
| 1318 | review | Review at 2560x1440 | ok | 0 |
| 1319 | projects | Projects at 2560x1440 | ok | 4 |
| 1320 | journal | Log at 2560x1440 | ok | 0 |
| 1321 | stats | Progress at 2560x1440 | ok | 0 |
| 1322 | library | Library at 2560x1440 | ok | 2 |
| 1323 | settings | Settings at 2560x1440 | ok | 0 |
| 1324 | layout | the window refuses to go below its minimum | ok | 0 |
| 1325 | layout | the sidebar keeps every page button | ok | 0 |
| 1326 | today | tab through the today page | ok | 61 |
| 1327 | today | the focused control is the one you can see | ok | 0 |
| 1328 | practice | tab through the practice page | ok | 94 |
| 1329 | practice | the focused control is the one you can see | ok | 0 |
| 1330 | phase | tick a line with the space bar | ok | 16 |
| 1331 | practice | Ctrl+Enter in the editor runs the code | ok | 172 |
| 1332 | settings | type 2,5 hours in a German locale | ok | 5 |
| 1333 | settings | type it by hand as 3,5 | ok | 3 |
| 1334 | today | the pace line still reads sensibly | ok | 35 |
| 1335 | library | open library with nothing to show | ok | 20 |
| 1336 | stats | open stats with nothing to show | ok | 41 |
| 1337 | projects | open projects with nothing to show | ok | 12 |
| 1338 | today | open today with nothing to show | ok | 42 |
| 1339 | roadmap | open roadmap with nothing to show | ok | 170 |
| 1340 | navigation | switch pages 200 times | ok | 1985 |
| 1341 | today | reopen the Today page | 1 ms | 1 |
| 1342 | roadmap | reopen the Roadmap page | 13 ms | 13 |
| 1343 | phase | reopen the Phase page | 10 ms | 10 |
| 1344 | practice | reopen the Practice page | 15 ms | 15 |
| 1345 | quiz | reopen the Quizzes page | 9 ms | 9 |
| 1346 | review | reopen the Review page | 9 ms | 9 |
| 1347 | projects | reopen the Projects page | 15 ms | 15 |
| 1348 | journal | reopen the Log page | 8 ms | 8 |
| 1349 | stats | reopen the Progress page | 9 ms | 9 |
| 1350 | library | reopen the Library page | 18 ms | 18 |
| 1351 | settings | reopen the Settings page | 14 ms | 14 |
| 1352 | screenshots | grab every page on both themes | ok | 9557 |
| 1353 | screenshots | practice page after a passing run | results panel hidden: False; rows rendered into it: 4; hint label hidden: True;  | 0 |
| 1354 | help | press F1 and close the shortcut list | ok | 23 |
| 1355 | menu | press Ctrl+, for Settings | ok | 57 |
| 1356 | settings | open the snapshot list and cancel | ok | 16 |
| 1357 | settings | restore the snapshot just taken | ok | 43 |
| 1358 | onboarding | Continue, Continue, Back | ok | 16 |
| 1359 | update | press Update and restart while offline | ok | 7 |
| 1360 | quiz | finish a quiz and go back to its phase | ok | 338 |
| 1361 | quiz | finish a quiz and pick another | ok | 298 |
| 1362 | review | skip to a concept card, reveal, rate | ok | 51 |
| 1363 | practice | press Next | ok | 12 |
| 1364 | phase | open the first resource | ok | 17 |
| 1365 | library | press every button on tab 0 | ok | 560 |
| 1366 | library | press every button on tab 1 | ok | 607 |
| 1367 | library | press every button on tab 2 | ok | 516 |
| 1368 | library | press every button on tab 3 | ok | 284 |
| 1369 | projects | open the repo link | ok | 92 |
| 1370 | projects | press every status button | ok | 290 |
| 1371 | journal | the history opens on the newest sixty | ok | 0 |
| 1372 | journal | press Show older for the next sixty | ok | 408 |
| 1373 | journal | press Show older for the last ten | ok | 98 |
| 1374 | journal | find one entry among a hundred | ok | 222 |
| 1375 | journal | a filter that matches nothing says so | ok | 426 |
| 1376 | journal | narrow the range, then widen it again | ok | 1090 |
| 1377 | journal | load an old entry back into the form | ok | 31 |
| 1378 | journal | save the correction | ok | 47 |
| 1379 | journal | take the correction back with Ctrl+Z | ok | 30 |
| 1380 | journal | and put it back with Ctrl+Y | ok | 30 |
| 1381 | journal | start an edit and cancel out of it | ok | 54 |
| 1382 | journal | delete an entry by mistake | ok | 16 |
| 1383 | journal | Ctrl+Z brings the whole entry back | ok | 22 |
| 1384 | journal | Ctrl+Y deletes it again | ok | 19 |
| 1385 | journal | log today for the first time | ok | 22 |
| 1386 | journal | the form warns before the day stacks | ok | 0 |
| 1387 | journal | log today again anyway | ok | 26 |
| 1388 | journal | every note written is listed here | ok | 0 |
| 1389 | journal | the filter searches the notes too | ok | 44 |
| 1390 | journal | open note 0 from the log | ok | 128 |
| 1391 | journal | open note 1 from the log | ok | 157 |
| 1392 | journal | open note 2 from the log | ok | 140 |
| 1393 | journal | open note 3 from the log | ok | 121 |
| 1394 | journal | open note 4 from the log | ok | 976 |
| 1395 | journal | open note 5 from the log | ok | 62 |
| 1396 | journal | open note 6 from the log | ok | 51 |
| 1397 | journal | the notes section with nothing in it | ok | 0 |
| 1398 | practice | submit an empty editor and read the reasons | ok | 237 |
| 1399 | practice | put the real answer back | ok | 211 |
| 1400 | practice | forget the exclamation mark and run | ok | 184 |
| 1401 | practice | get one character wrong instead | ok | 215 |
| 1402 | practice | get only the capital wrong | ok | 244 |
| 1403 | practice | start an endless run and press Stop | ok | 338 |
| 1404 | practice | read every hint, then press once more | ok | 15 |
| 1405 | practice | search for one exercise by its title | ok | 12 |
| 1406 | practice | search for something that is not there | ok | 11 |
| 1407 | practice | clear the search | ok | 18 |
| 1408 | practice | filter by every difficulty | ok | 61 |
| 1409 | practice | show only the revealed ones | ok | 24 |
| 1410 | practice | walk to the last exercise and press Next again | ok | 33 |
| 1411 | practice | pass the exercise | ok | 191 |
| 1412 | practice | carry on experimenting and break it | ok | 10 |
| 1413 | practice | press Restore my passing version | ok | 6 |
| 1414 | practice | press Reset, then restore once more | ok | 46 |
| 1415 | practice | read the answer | ok | 16 |
| 1416 | practice | check the list says so too | ok | 0 |
| 1417 | practice | press Try this one again from scratch | ok | 12 |
| 1418 | review | press Space to reveal the saved line | ok | 19 |
| 1419 | review | press 3 to rate it Good | ok | 22 |
| 1420 | review | pick a multiple choice option by letter | ok | 1 |
| 1421 | review | press Enter to check it | ok | 20 |
| 1422 | review | press 4 for Easy | ok | 20 |
| 1423 | review | answer with the Again key | ok | 32 |
| 1424 | review | answer with the Hard key | ok | 37 |
| 1425 | review | answer with the Good key | ok | 45 |
| 1426 | review | answer with the Easy key | ok | 34 |
| 1427 | review | type in the search box with a card open | ok | 2 |
| 1428 | review | bury the card in front of you | ok | 41 |
| 1429 | review | the summary offers the buried card back | ok | 69 |
| 1430 | review | answer one card, then take it back | ok | 60 |
| 1431 | review | Ctrl+Z takes the next one back too | ok | 46 |
| 1432 | review | skip the same card twice | ok | 44 |
| 1433 | phase | open a line's menu with the ... button | ok | 17 |
| 1434 | phase | open the same menu with Shift+F10 | ok | 7 |
| 1435 | phase | the Menu key offers to take it out again | ok | 4 |
| 1436 | search | open the box with Ctrl+K | ok | 3 |
| 1437 | search | find a phase note written minutes ago | ok | 107 |
| 1438 | search | find your own project note | ok | 66 |
| 1439 | search | find a project by its repository url | ok | 2 |
| 1440 | search | find a log entry and open the log | ok | 12 |
| 1441 | search | type a query | ok | 27 |
| 1442 | search | walk down and back up the results | ok | 5 |
| 1443 | search | page down and page up the results | ok | 5 |
| 1444 | search | open the selected hit with Enter | ok | 120 |
| 1445 | search | close the results with Escape | ok | 7 |
| 1446 | library | open the field f-web from search | ok | 59 |
| 1447 | library | open the cert c-cs50p from search | ok | 90 |
| 1448 | search | open a question from search | ok | 5 |
| 1449 | search | read the question and close it | ok | 13 |
| 1450 | library | filter the library to nothing | ok | 35 |
| 1451 | library | filter the library to one shelf entry | ok | 124 |
| 1452 | library | mark a row on tab 0 as read | ok | 8 |
| 1453 | library | take the mark on tab 0 back | ok | 6 |
| 1454 | library | mark a row on tab 1 as read | ok | 123 |
| 1455 | library | take the mark on tab 1 back | ok | 5 |
| 1456 | library | mark a row on tab 2 as read | ok | 92 |
| 1457 | library | take the mark on tab 2 back | ok | 11 |
| 1458 | library | undo the last read mark | ok | 230 |
| 1459 | navigation | press Ctrl+0 | ok | 43 |
| 1460 | navigation | press Ctrl+L | ok | 46 |
| 1461 | navigation | open the library from the Go menu | ok | 45 |
| 1462 | first run | read the status bar on a first launch | ok | 0 |
| 1463 | onboarding | type a name and continue | ok | 9 |
| 1464 | onboarding | choose an experience card | ok | 8 |
| 1465 | onboarding | tick two goals | ok | 11 |
| 1466 | onboarding | go back a step and forward again | ok | 11 |
| 1467 | onboarding | set a pace and build the plan | ok | 55 |
| 1468 | onboarding | skip the whole thing | ok | 7 |
| 1469 | settings | press Run setup again | ok | 56 |
| 1470 | quiz | start one and skip a question | ok | 41 |
| 1471 | quiz | move on to the next question | ok | 13 |
| 1472 | quiz | think better of leaving | ok | 0 |
| 1473 | quiz | leave the quiz | ok | 68 |
| 1474 | quiz | close the app in the middle of one | ok | 84 |
| 1475 | quiz | resume where it was left | ok | 18 |
| 1476 | quiz | start it over instead | ok | 77 |
| 1477 | settings | nothing has left this machine yet | ok | 0 |
| 1478 | settings | choose a second copy folder | ok | 6 |
| 1479 | settings | copy everything there now | ok | 14 |
| 1480 | settings | import a backup and read the summary | ok | 64 |
| 1481 | projects | press Open with nothing to open | ok | 0 |
| 1482 | projects | type a repo address | ok | 1 |
| 1483 | projects | replace it with a note to self | ok | 1 |
| 1484 | today | read the note above the list | ok | 34 |
| 1485 | today | push the first item off until tomorrow | ok | 41 |
| 1486 | today | push a second one off from a compact row | ok | 42 |
| 1487 | today | find the way back to what was hidden | ok | 85 |
| 1488 | today | yesterday's 'first thing tomorrow' returns | ok | 54 |
| 1489 | today | push everything off for a quiet evening | ok | 60 |
| 1490 | today | finish the entire curriculum | ok | 340 |
| 1491 | today | read what the finished plan says | ok | 0 |
| 1492 | today | keep reviewing from the hero | ok | 48 |
| 1493 | today | change track from the hero | ok | 67 |
| 1494 | today | export the report from the hero | ok | 67 |
| 1495 | roadmap | the marker is there while work remains | ok | 0 |
| 1496 | roadmap | and is gone once there is nowhere to go | ok | 0 |
| 1497 | stats | click a phase row | ok | 204 |
| 1498 | stats | select a row and press Enter | ok | 111 |
| 1499 | stats | hover the quiz column for the trend | ok | 0 |
| 1500 | phase | the way into the review deck is announced | ok | 0 |
| 1501 | phase | write a long note into the box | ok | 12 |
| 1502 | phase | and it shrinks back for a short one | ok | 8 |
| 1503 | search | type a word that is nowhere | ok | 22 |
| 1504 | search | Escape, then Ctrl+K again | ok | 16 |
| 1505 | search | open a shelf book from Ctrl+K | ok | 110 |
| 1506 | library | filter for a channel on the Shelf tab | ok | 48 |
| 1507 | library | follow the count to the Video tab | ok | 5 |
| 1508 | library | clear the filter | ok | 198 |
| 1509 | projects | SHOW Shipped with nothing shipped | ok | 10 |
| 1510 | projects | press Show every project | ok | 283 |
| 1511 | projects | type in FIND | ok | 313 |
| 1512 | stats | click the Checks heading | ok | 3 |
| 1513 | stats | pick every SORT choice | ok | 11 |
| 1514 | practice | fail a run, then Where this is taught | ok | 280 |
| 1515 | settings | set filters, then change the theme | ok | 3806 |
| 1516 | settings | come back to each page | ok | 5917 |
| 1517 | quiz | read the picker and its counter | ok | 0 |
| 1518 | quiz | type into FIND | ok | 76 |
| 1519 | quiz | a search that matches nothing | ok | 125 |
| 1520 | quiz | SHOW each status in turn | ok | 334 |
| 1521 | quiz | start a quiz from the filtered list | ok | 78 |
| 1522 | quiz | press the second choice every time | ok | 735 |
| 1523 | review | pick a wrong option by its letter | ok | 25 |
| 1524 | review | press Where this is taught | ok | 149 |
| 1525 | review | press Next card | ok | 16 |
| 1526 | review | a second wrong answer, left with Space | ok | 45 |
| 1527 | review | reveal a gate check | ok | 16 |
| 1528 | review | rate it Good | ok | 24 |
| 1529 | phase | a phase read to the end | ok | 155 |
| 1530 | roadmap | the roadmap says read, not proven | ok | 196 |
| 1531 | phase | the same phase, proven | ok | 143 |
| 1532 | today | an earlier phase is mixed into today | ok | 90 |
| 1533 | quiz | start a quiz from the picker | ok | 28 |
| 1534 | quiz | leave and start a different one | ok | 93 |
| 1535 | review | press Check for more | ok | 16 |
| 1536 | updates | open the update dialog and decline | ok | 6 |
| 1537 | updates | open the releases page instead | ok | 5 |
| 1538 | menu | File > Quit | ok | 6 |
| 1539 | menu | File > Export backup... | ok | 65 |
| 1540 | menu | File > Export progress report... | ok | 10 |
| 1541 | menu | File > Take a snapshot | ok | 8 |
| 1542 | menu | File > Restore a snapshot... | ok | 12 |
| 1543 | menu | Go > Today | ok | 46 |
| 1544 | menu | Go > Roadmap | ok | 159 |
| 1545 | menu | Go > Phase | ok | 154 |
| 1546 | menu | Go > Practice | ok | 40 |
| 1547 | menu | Go > Quizzes | ok | 57 |
| 1548 | menu | Go > Review | ok | 19 |
| 1549 | menu | Go > Projects | ok | 749 |
| 1550 | menu | Go > Log | ok | 34 |
| 1551 | menu | Go > Progress | ok | 100 |
| 1552 | menu | Go > Library | ok | 1197 |
| 1553 | menu | Go > Settings | ok | 70 |
| 1554 | menu | Go > Find | ok | 7 |
| 1555 | menu | Edit > Undo | ok | 0 |
| 1556 | menu | Edit > Redo | ok | 0 |
| 1557 | menu | Help > How this app works | ok | 0 |
| 1558 | menu | Help > Keyboard shortcuts | ok | 12 |
| 1559 | menu | Help > Check for updates | ok | 1 |
| 1560 | menu | Help > About | ok | 1 |
| 1561 | menu | every navigation shortcut | ok | 769 |
