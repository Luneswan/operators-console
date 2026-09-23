# Walkthrough of Operator's Console

A single learner's pass through every page, every control and every piece of content, driven through the real widgets with QTest and watched by a net of sensors.

- Generated: 2026-09-24 02:14
- Platform: Windows-11-10.0.26200-SP0, Python 3.14.5, Qt offscreen
- Runtime: 6 min 31 s
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
| W-01 | major | navigation | step blocks for 4659 ms: switch pages 200 times as fast as the event loop allows | Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 4.7 s. |
| W-02 | polish | journal | a second entry for the same day is added, not merged | Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions. |

### W-01 - step blocks for 4659 ms: switch pages 200 times as fast as the event loop allows

- **Severity**: major
- **View**: navigation
- **Repro**: Open navigation and switch pages 200 times as fast as the event loop allows; the interface is frozen for 4.7 s.

### W-02 - a second entry for the same day is added, not merged

- **Severity**: polish
- **View**: journal
- **Repro**: Log 2.5 hours today, then log 1 hour today again. The form says so before you do ('You already logged 2.5 h today - this adds to it') and the rows stay separate: two sessions in one day are two sessions.

```
2 rows for today, total hours now 12.5
```

## Coverage of the interface

Every `button(...)`, `QPushButton(...)`, `QAction(...)` and `setShortcut(...)` under `src/` is counted. A control counts as hit when the walk activated the widget built by that exact source line.

- Controls declared: **110**
- Activated by the walk: **99** (90%)

| kind | declared | hit | % |
| --- | --- | --- | --- |
| action | 10 | 10 | 100% |
| button | 91 | 81 | 89% |
| shortcut | 9 | 8 | 89% |

<details><summary>Every control, hit or not</summary>

| file | line | kind | label | hit |
| --- | --- | --- | --- | --- |
| operators_console/ui/main_window.py | 148 | button | Close | yes |
| operators_console/ui/main_window.py | 355 | button | Undo | yes |
| operators_console/ui/main_window.py | 361 | button | Redo | yes |
| operators_console/ui/main_window.py | 398 | action | Quit | yes |
| operators_console/ui/main_window.py | 399 | shortcut | StandardKey.Quit | yes |
| operators_console/ui/main_window.py | 420 | action | Undo | yes |
| operators_console/ui/main_window.py | 421 | shortcut | StandardKey.Undo | yes |
| operators_console/ui/main_window.py | 424 | action | Redo | yes |
| operators_console/ui/main_window.py | 425 | shortcut | <_redo_keys()> | yes |
| operators_console/ui/main_window.py | 430 | action | Find | yes |
| operators_console/ui/main_window.py | 431 | shortcut | Ctrl+K | yes |
| operators_console/ui/main_window.py | 436 | action | How this app works | yes |
| operators_console/ui/main_window.py | 439 | action | Keyboard shortcuts | yes |
| operators_console/ui/main_window.py | 440 | shortcut | F1 | yes |
| operators_console/ui/main_window.py | 443 | action | Check for updates | yes |
| operators_console/ui/main_window.py | 446 | action | About | yes |
| operators_console/ui/main_window.py | 288 | button | <text> | yes |
| operators_console/ui/main_window.py | 392 | action | <text> | yes |
| operators_console/ui/main_window.py | 406 | action | <text> | yes |
| operators_console/ui/main_window.py | 395 | shortcut | <QKeySequence()> | NO |
| operators_console/ui/main_window.py | 408 | shortcut | Ctrl+%d | yes |
| operators_console/ui/main_window.py | 412 | shortcut | Ctrl+0 | yes |
| operators_console/ui/main_window.py | 415 | shortcut | Ctrl+, | yes |
| operators_console/ui/onboarding.py | 150 | button | Skip for now | yes |
| operators_console/ui/onboarding.py | 155 | button | Back | yes |
| operators_console/ui/onboarding.py | 159 | button | Continue | yes |
| operators_console/ui/shortcuts.py | 90 | button | Close | yes |
| operators_console/ui/snapshots.py | 72 | button | Open the backups folder | yes |
| operators_console/ui/snapshots.py | 77 | button | Cancel | yes |
| operators_console/ui/snapshots.py | 80 | button | Restore this snapshot | yes |
| operators_console/ui/updater.py | 220 | button | Open the releases page | yes |
| operators_console/ui/updater.py | 224 | button | Not now | yes |
| operators_console/ui/updater.py | 227 | button | Update and restart | yes |
| operators_console/ui/views/dashboard.py | 224 | button | <computed> | yes |
| operators_console/ui/views/dashboard.py | 233 | button | Not today | yes |
| operators_console/ui/views/dashboard.py | 249 | button | Start | yes |
| operators_console/ui/views/dashboard.py | 318 | button | Open this phase | yes |
| operators_console/ui/views/dashboard.py | 370 | button | Export report | yes |
| operators_console/ui/views/dashboard.py | 373 | button | Keep reviewing | yes |
| operators_console/ui/views/dashboard.py | 377 | button | Change track | yes |
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
| operators_console/ui/views/roadmap.py | 205 | button | Open | yes |
| operators_console/ui/views/roadmap.py | 255 | button | Open | yes |
| operators_console/ui/views/settings.py | 129 | button | Run setup again | yes |
| operators_console/ui/views/settings.py | 237 | button | Check now | yes |
| operators_console/ui/views/settings.py | 273 | button | Choose folder... | yes |
| operators_console/ui/views/settings.py | 276 | button | Copy now | yes |
| operators_console/ui/views/settings.py | 290 | button | Snapshot now | yes |
| operators_console/ui/views/settings.py | 293 | button | Restore a snapshot... | yes |
| operators_console/ui/views/settings.py | 305 | button | Reset all progress | yes |
| operators_console/ui/views/settings.py | 255 | button | <text> | yes |
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
- **operators_console/ui/main_window.py:395 (shortcut <QKeySequence()>)** - never activated by the walk
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
| controls declared in the source | 110 |
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
| milliseconds for 200 page switches | 1903 |
| milliseconds for a typical project status press | 11 |
| milliseconds to open review with 1000 cards | 34 |
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
| worst theme switch in milliseconds | 439 |
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
| notice | How this app works | Today: what to do next.  Roadmap: your plan, in teaching order. No phase is locked.  Practice: write code, and real checks grade it.  Quizzes: one per phase. Wrong answers go to Review.  Review: spaced repetition of earl |
| dialog | ShortcutsDialog | Keyboard shortcuts |
| notice | About Python Operator's Console | Python Operator's Console 1.1.3  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2905\test_the_help_ |
| messagebox | Show the solution? | You have not passed this one.  If you read the answer, it is marked as read, not solved. Try another hint first? |
| open file | Import a backup | C:\Users\anasa |
| question | Replace everything? | Importing replaces all current progress.  A backup of the current state is saved first. Continue? |
| question | Reset all progress? | This clears all checkboxes, exercises, reviews, projects and log entries.  A snapshot is taken first. Use Restore a snapshot in Settings to undo. Settings are kept. |
| dialog | UpdateDialog | Update available |
| dialog | QuestionDialog | Question |
| dialog | Onboarding | Set up your plan |
| question | Leave this quiz? | Answered questions are already scored.  The rest of this attempt is discarded, and the quiz starts over next time. Leave? |
| notice | About Python Operator's Console | Python Operator's Console 1.1.3  21 phases, 119 graded exercises, 242 review questions, 22 projects.  Scheduling by FSRS-6. Your data lives in: C:\Users\anasa\AppData\Local\Temp\pytest-of-anasa\pytest-2905\test_the_remai |

## Every step

| # | view | action | result | ms |
| --- | --- | --- | --- | --- |
| 1 | onboarding | open the wizard on first run | ok | 30 |
| 2 | onboarding | continue from step 1 | ok | 7 |
| 3 | onboarding | continue from step 2 | ok | 0 |
| 4 | onboarding | continue from step 3 | ok | 0 |
| 5 | onboarding | back from step 4 | ok | 0 |
| 6 | onboarding | back from step 3 | ok | 0 |
| 7 | onboarding | back from step 2 | ok | 0 |
| 8 | onboarding | experience: Never written code before | ok | 40 |
| 9 | onboarding | experience: Some Python, but it does not stick | ok | 29 |
| 10 | onboarding | experience: Confident in another language | ok | 36 |
| 11 | onboarding | experience: I write Python at work already | ok | 32 |
| 12 | onboarding | tick all 512 goal combinations | ok | 111 |
| 13 | onboarding | finish with goal: Build websites and APIs | ok | 41 |
| 14 | onboarding | finish with goal: Work with data | ok | 35 |
| 15 | onboarding | finish with goal: Machine learning and AI | ok | 30 |
| 16 | onboarding | finish with goal: Automate boring work | ok | 37 |
| 17 | onboarding | finish with goal: Games and graphics | ok | 36 |
| 18 | onboarding | finish with goal: Infrastructure and deployment | ok | 32 |
| 19 | onboarding | finish with goal: Security and hacking | ok | 34 |
| 20 | onboarding | finish with goal: Pass a technical interview | ok | 34 |
| 21 | onboarding | finish with goal: Understand how computers work | ok | 30 |
| 22 | onboarding | pace 0.5 h x 1 days | ok | 27 |
| 23 | onboarding | pace 16.0 h x 7 days | ok | 30 |
| 24 | onboarding | skip the wizard | ok | 4 |
| 25 | today | land on Today after skipping | ok | 52 |
| 26 | today | read the four headline tiles | ok | 0 |
| 27 | today | press Start on plan row 1 | ok | 77 |
| 28 | today | press Start on plan row 2 | ok | 125 |
| 29 | today | press Start on plan row 3 | ok | 902 |
| 30 | today | press Start on plan row 4 | ok | 176 |
| 31 | today | press Start on plan row 5 | ok | 64 |
| 32 | today | open the current phase from Where you are | ok | 160 |
| 33 | settings | switch the theme to light | ok | 5 |
| 34 | today | click the Today sidebar button (light theme) | ok | 89 |
| 35 | roadmap | click the Roadmap sidebar button (light theme) | ok | 226 |
| 36 | phase | click the Phase sidebar button (light theme) | ok | 192 |
| 37 | practice | click the Practice sidebar button (light theme) | ok | 146 |
| 38 | quiz | click the Quizzes sidebar button (light theme) | ok | 110 |
| 39 | review | click the Review sidebar button (light theme) | ok | 38 |
| 40 | projects | click the Projects sidebar button (light theme) | ok | 1273 |
| 41 | journal | click the Log sidebar button (light theme) | ok | 57 |
| 42 | stats | click the Progress sidebar button (light theme) | ok | 227 |
| 43 | library | click the Library sidebar button (light theme) | ok | 1657 |
| 44 | settings | click the Settings sidebar button (light theme) | ok | 204 |
| 45 | settings | switch the theme to dark | ok | 448 |
| 46 | today | click the Today sidebar button (dark theme) | ok | 97 |
| 47 | roadmap | click the Roadmap sidebar button (dark theme) | ok | 248 |
| 48 | phase | click the Phase sidebar button (dark theme) | ok | 200 |
| 49 | practice | click the Practice sidebar button (dark theme) | ok | 88 |
| 50 | quiz | click the Quizzes sidebar button (dark theme) | ok | 115 |
| 51 | review | click the Review sidebar button (dark theme) | ok | 16 |
| 52 | projects | click the Projects sidebar button (dark theme) | ok | 1312 |
| 53 | journal | click the Log sidebar button (dark theme) | ok | 57 |
| 54 | stats | click the Progress sidebar button (dark theme) | ok | 196 |
| 55 | library | click the Library sidebar button (dark theme) | ok | 1189 |
| 56 | settings | click the Settings sidebar button (dark theme) | ok | 64 |
| 57 | settings | switch the theme to system | ok | 285 |
| 58 | today | click the Today sidebar button (system theme) | ok | 72 |
| 59 | roadmap | click the Roadmap sidebar button (system theme) | ok | 181 |
| 60 | phase | click the Phase sidebar button (system theme) | ok | 126 |
| 61 | practice | click the Practice sidebar button (system theme) | ok | 61 |
| 62 | quiz | click the Quizzes sidebar button (system theme) | ok | 80 |
| 63 | review | click the Review sidebar button (system theme) | ok | 10 |
| 64 | projects | click the Projects sidebar button (system theme) | ok | 882 |
| 65 | journal | click the Log sidebar button (system theme) | ok | 46 |
| 66 | stats | click the Progress sidebar button (system theme) | ok | 99 |
| 67 | library | click the Library sidebar button (system theme) | ok | 955 |
| 68 | settings | click the Settings sidebar button (system theme) | ok | 63 |
| 69 | today | check no control escapes the Today page | ok | 1 |
| 70 | roadmap | check no control escapes the Roadmap page | ok | 0 |
| 71 | phase | check no control escapes the Phase page | ok | 0 |
| 72 | practice | check no control escapes the Practice page | ok | 0 |
| 73 | quiz | check no control escapes the Quizzes page | ok | 0 |
| 74 | review | check no control escapes the Review page | ok | 0 |
| 75 | projects | check no control escapes the Projects page | ok | 2 |
| 76 | journal | check no control escapes the Log page | ok | 0 |
| 77 | stats | check no control escapes the Progress page | ok | 0 |
| 78 | library | check no control escapes the Library page | ok | 1 |
| 79 | settings | check no control escapes the Settings page | ok | 0 |
| 80 | menu | Go > Today | ok | 43 |
| 81 | menu | Go > Roadmap | ok | 146 |
| 82 | menu | Go > Phase | ok | 114 |
| 83 | menu | Go > Practice | ok | 44 |
| 84 | menu | Go > Quizzes | ok | 75 |
| 85 | menu | Go > Review | ok | 28 |
| 86 | menu | Go > Projects | ok | 800 |
| 87 | menu | Go > Log | ok | 46 |
| 88 | menu | Go > Progress | ok | 164 |
| 89 | menu | Go > Library | ok | 1256 |
| 90 | menu | Go > Settings | ok | 101 |
| 91 | menu | Go > Find | ok | 7 |
| 92 | today | press Ctrl+1 for Today | ok | 43 |
| 93 | roadmap | press Ctrl+2 for Roadmap | ok | 176 |
| 94 | phase | press Ctrl+3 for Phase | ok | 121 |
| 95 | practice | press Ctrl+4 for Practice | ok | 53 |
| 96 | quiz | press Ctrl+5 for Quizzes | ok | 80 |
| 97 | review | press Ctrl+6 for Review | ok | 33 |
| 98 | projects | press Ctrl+7 for Projects | ok | 776 |
| 99 | journal | press Ctrl+8 for Log | ok | 46 |
| 100 | stats | press Ctrl+9 for Progress | ok | 122 |
| 101 | menu | &File > Export backup... | ok | 69 |
| 102 | menu | &File > Export progress report... | ok | 10 |
| 103 | menu | &File > Take a snapshot | ok | 10 |
| 104 | menu | &File > Restore a snapshot... | ok | 84 |
| 105 | menu | &Help > How this app works | ok | 0 |
| 106 | menu | &Help > Keyboard shortcuts | ok | 8 |
| 107 | menu | &Help > Check for updates | ok | 0 |
| 108 | menu | &Help > About | ok | 0 |
| 109 | roadmap | switch to the Well-rounded software engineer track | ok | 181 |
| 110 | roadmap | switch to the Learn Python properly (no career pressure) track | ok | 126 |
| 111 | roadmap | switch to the Backend & API engineer track | ok | 133 |
| 112 | roadmap | switch to the Data analysis & data engineering track | ok | 132 |
| 113 | roadmap | switch to the AI & machine learning engineer track | ok | 127 |
| 114 | roadmap | switch to the Automation, scripting & scraping track | ok | 118 |
| 115 | roadmap | switch to the DevOps & platform engineering track | ok | 135 |
| 116 | roadmap | switch to the Application security track | ok | 134 |
| 117 | roadmap | switch to the Job-ready, fastest route track | ok | 183 |
| 118 | roadmap | open every phase card from the roadmap | ok | 1538 |
| 119 | roadmap | open every phase outside the plan | ok | 605 |
| 120 | navigation | switch pages 200 times as fast as the event loop allows | slow (4659 ms) | 4659 |
| 121 | phase | walk Next through all 21 phases | ok | 2328 |
| 122 | phase | walk Previous back to the first phase | ok | 2355 |
| 123 | phase | choose every phase from the picker | ok | 1928 |
| 124 | phase | open phase OS Operating rules | ok | 131 |
| 125 | phase | open phase 00 Environment & Git | ok | 117 |
| 126 | phase | open phase 01 Python foundations | ok | 119 |
| 127 | phase | open phase 02 Python engineering | ok | 118 |
| 128 | phase | open phase 03 Packaging & tooling | ok | 101 |
| 129 | phase | open phase 04 Computer science core | ok | 115 |
| 130 | phase | open phase 05 Algorithms & problem solving | ok | 107 |
| 131 | phase | open phase 06 Linux & systems | ok | 107 |
| 132 | phase | open phase 07 Networking | ok | 77 |
| 133 | phase | open phase 08 SQL & PostgreSQL | ok | 105 |
| 134 | phase | open phase 09 Backend engineering | ok | 90 |
| 135 | phase | open phase 10 Automation & web | ok | 115 |
| 136 | phase | open phase 11 Async, concurrency & performance | ok | 90 |
| 137 | phase | open phase 12 Docker, CI/CD & deployment | ok | 81 |
| 138 | phase | open phase 13 Application security | ok | 78 |
| 139 | phase | open phase 14 AI engineering | ok | 129 |
| 140 | phase | open phase 15 Architecture & orchestration | ok | 106 |
| 141 | phase | open phase 16 Systems programming & internals | ok | 96 |
| 142 | phase | open phase 17 Data engineering | ok | 80 |
| 143 | phase | open phase 18 Beyond senior | ok | 129 |
| 144 | phase | open phase 99 Final-boss ladder | ok | 80 |
| 145 | phase | tick every study step in OS | ok | 165 |
| 146 | phase | untick every study step in OS | ok | 136 |
| 147 | phase | tick every study step in 00 | ok | 117 |
| 148 | phase | untick every study step in 00 | ok | 111 |
| 149 | phase | tick every study step in 01 | ok | 244 |
| 150 | phase | untick every study step in 01 | ok | 260 |
| 151 | phase | tick every study step in 02 | ok | 121 |
| 152 | phase | untick every study step in 02 | ok | 105 |
| 153 | phase | tick every study step in 03 | ok | 103 |
| 154 | phase | untick every study step in 03 | ok | 93 |
| 155 | phase | tick every study step in 04 | ok | 162 |
| 156 | phase | untick every study step in 04 | ok | 123 |
| 157 | phase | tick every study step in 05 | ok | 198 |
| 158 | phase | untick every study step in 05 | ok | 150 |
| 159 | phase | tick every study step in 06 | ok | 127 |
| 160 | phase | untick every study step in 06 | ok | 117 |
| 161 | phase | tick every study step in 07 | ok | 129 |
| 162 | phase | untick every study step in 07 | ok | 99 |
| 163 | phase | tick every study step in 08 | ok | 143 |
| 164 | phase | untick every study step in 08 | ok | 122 |
| 165 | phase | tick every study step in 09 | ok | 189 |
| 166 | phase | untick every study step in 09 | ok | 139 |
| 167 | phase | tick every study step in 10 | ok | 128 |
| 168 | phase | untick every study step in 10 | ok | 123 |
| 169 | phase | tick every study step in 11 | ok | 159 |
| 170 | phase | untick every study step in 11 | ok | 119 |
| 171 | phase | tick every study step in 12 | ok | 133 |
| 172 | phase | untick every study step in 12 | ok | 104 |
| 173 | phase | tick every study step in 13 | ok | 143 |
| 174 | phase | untick every study step in 13 | ok | 123 |
| 175 | phase | tick every study step in 14 | ok | 213 |
| 176 | phase | untick every study step in 14 | ok | 181 |
| 177 | phase | tick every study step in 15 | ok | 163 |
| 178 | phase | untick every study step in 15 | ok | 137 |
| 179 | phase | tick every study step in 16 | ok | 108 |
| 180 | phase | untick every study step in 16 | ok | 95 |
| 181 | phase | tick every study step in 17 | ok | 139 |
| 182 | phase | untick every study step in 17 | ok | 119 |
| 183 | phase | tick every study step in 18 | ok | 161 |
| 184 | phase | untick every study step in 18 | ok | 140 |
| 185 | phase | tick every study step in 99 | ok | 154 |
| 186 | phase | untick every study step in 99 | ok | 135 |
| 187 | phase | clear the gate on 00 | ok | 54 |
| 188 | phase | reopen the gate on 00 | ok | 45 |
| 189 | phase | clear the gate on 01 | ok | 48 |
| 190 | phase | reopen the gate on 01 | ok | 39 |
| 191 | phase | clear the gate on 02 | ok | 49 |
| 192 | phase | reopen the gate on 02 | ok | 35 |
| 193 | phase | clear the gate on 03 | ok | 40 |
| 194 | phase | reopen the gate on 03 | ok | 33 |
| 195 | phase | clear the gate on 04 | ok | 43 |
| 196 | phase | reopen the gate on 04 | ok | 37 |
| 197 | phase | clear the gate on 05 | ok | 43 |
| 198 | phase | reopen the gate on 05 | ok | 29 |
| 199 | phase | clear the gate on 06 | ok | 56 |
| 200 | phase | reopen the gate on 06 | ok | 41 |
| 201 | phase | clear the gate on 07 | ok | 51 |
| 202 | phase | reopen the gate on 07 | ok | 39 |
| 203 | phase | clear the gate on 08 | ok | 50 |
| 204 | phase | reopen the gate on 08 | ok | 40 |
| 205 | phase | clear the gate on 09 | ok | 45 |
| 206 | phase | reopen the gate on 09 | ok | 34 |
| 207 | phase | clear the gate on 10 | ok | 42 |
| 208 | phase | reopen the gate on 10 | ok | 32 |
| 209 | phase | clear the gate on 11 | ok | 44 |
| 210 | phase | reopen the gate on 11 | ok | 30 |
| 211 | phase | clear the gate on 12 | ok | 43 |
| 212 | phase | reopen the gate on 12 | ok | 34 |
| 213 | phase | clear the gate on 13 | ok | 43 |
| 214 | phase | reopen the gate on 13 | ok | 38 |
| 215 | phase | clear the gate on 14 | ok | 54 |
| 216 | phase | reopen the gate on 14 | ok | 34 |
| 217 | phase | clear the gate on 15 | ok | 41 |
| 218 | phase | reopen the gate on 15 | ok | 37 |
| 219 | phase | clear the gate on 16 | ok | 37 |
| 220 | phase | reopen the gate on 16 | ok | 25 |
| 221 | phase | clear the gate on 17 | ok | 47 |
| 222 | phase | reopen the gate on 17 | ok | 36 |
| 223 | phase | clear the gate on 18 | ok | 42 |
| 224 | phase | reopen the gate on 18 | ok | 36 |
| 225 | phase | clear the gate on 99 | ok | 27 |
| 226 | phase | reopen the gate on 99 | ok | 26 |
| 227 | phase | open every resource in 00 | ok | 16 |
| 228 | phase | open every resource in 01 | ok | 21 |
| 229 | phase | open every resource in 02 | ok | 18 |
| 230 | phase | open every resource in 03 | ok | 14 |
| 231 | phase | open every resource in 04 | ok | 20 |
| 232 | phase | open every resource in 05 | ok | 15 |
| 233 | phase | open every resource in 06 | ok | 14 |
| 234 | phase | open every resource in 07 | ok | 18 |
| 235 | phase | open every resource in 08 | ok | 17 |
| 236 | phase | open every resource in 09 | ok | 16 |
| 237 | phase | open every resource in 10 | ok | 16 |
| 238 | phase | open every resource in 11 | ok | 20 |
| 239 | phase | open every resource in 12 | ok | 14 |
| 240 | phase | open every resource in 13 | ok | 22 |
| 241 | phase | open every resource in 14 | ok | 19 |
| 242 | phase | open every resource in 15 | ok | 24 |
| 243 | phase | open every resource in 16 | ok | 16 |
| 244 | phase | open every resource in 17 | ok | 21 |
| 245 | phase | open every resource in 18 | ok | 19 |
| 246 | phase | open every resource in 99 | ok | 15 |
| 247 | phase | use the jump row and snippet on OS | ok | 0 |
| 248 | phase | use the jump row and snippet on 00 | ok | 976 |
| 249 | phase | use the jump row and snippet on 01 | ok | 335 |
| 250 | phase | use the jump row and snippet on 02 | ok | 315 |
| 251 | phase | use the jump row and snippet on 03 | ok | 333 |
| 252 | phase | use the jump row and snippet on 04 | ok | 372 |
| 253 | phase | use the jump row and snippet on 05 | ok | 312 |
| 254 | phase | use the jump row and snippet on 06 | ok | 268 |
| 255 | phase | use the jump row and snippet on 07 | ok | 256 |
| 256 | phase | use the jump row and snippet on 08 | ok | 277 |
| 257 | phase | use the jump row and snippet on 09 | ok | 299 |
| 258 | phase | use the jump row and snippet on 10 | ok | 275 |
| 259 | phase | use the jump row and snippet on 11 | ok | 306 |
| 260 | phase | use the jump row and snippet on 12 | ok | 307 |
| 261 | phase | use the jump row and snippet on 13 | ok | 325 |
| 262 | phase | use the jump row and snippet on 14 | ok | 408 |
| 263 | phase | use the jump row and snippet on 15 | ok | 370 |
| 264 | phase | use the jump row and snippet on 16 | ok | 302 |
| 265 | phase | use the jump row and snippet on 17 | ok | 353 |
| 266 | phase | use the jump row and snippet on 18 | ok | 144 |
| 267 | phase | use the jump row and snippet on 99 | ok | 178 |
| 268 | phase | send a line to the review deck from the right click menu | ok | 165 |
| 269 | phase | type a note in each phase and leave at once | ok | 1942 |
| 270 | phase | the pending note is committed on quit | ok | 164 |
| 271 | practice | filter the list by every phase | ok | 261 |
| 272 | practice | switch the status filter three ways | ok | 35 |
| 273 | practice | walk the list with Next exercise | ok | 57 |
| 274 | practice | run an endless loop and wait it out | ok | 3718 |
| 275 | practice | ask for the solution before passing | ok | 6 |
| 276 | practice | insist on the solution | ok | 20 |
| 277 | practice | type, then press Reset | ok | 9 |
| 278 | practice | p01.001: read the brief | ok | 0 |
| 279 | practice | p01.001: reveal every hint | ok | 45 |
| 280 | practice | p01.001: run an empty editor | ok | 479 |
| 281 | practice | p01.001: run the untouched starter | ok | 693 |
| 282 | practice | p01.001: run the reference solution | ok | 910 |
| 283 | practice | p01.001: read the solution once passed | ok | 19 |
| 284 | practice | p01.002: read the brief | ok | 0 |
| 285 | practice | p01.002: reveal every hint | ok | 36 |
| 286 | practice | p01.002: run an empty editor | ok | 1559 |
| 287 | practice | p01.002: run the untouched starter | ok | 764 |
| 288 | practice | p01.002: run the reference solution | ok | 295 |
| 289 | practice | p01.002: read the solution once passed | ok | 25 |
| 290 | practice | p01.003: read the brief | ok | 0 |
| 291 | practice | p01.003: reveal every hint | ok | 35 |
| 292 | practice | p01.003: run an empty editor | ok | 616 |
| 293 | practice | p01.003: run the untouched starter | ok | 286 |
| 294 | practice | p01.003: run the reference solution | ok | 227 |
| 295 | practice | p01.003: read the solution once passed | ok | 26 |
| 296 | practice | p01.004: read the brief | ok | 0 |
| 297 | practice | p01.004: reveal every hint | ok | 40 |
| 298 | practice | p01.004: run an empty editor | ok | 194 |
| 299 | practice | p01.004: run the untouched starter | ok | 246 |
| 300 | practice | p01.004: run the reference solution | ok | 211 |
| 301 | practice | p01.004: read the solution once passed | ok | 17 |
| 302 | practice | p01.005: read the brief | ok | 0 |
| 303 | practice | p01.005: reveal every hint | ok | 36 |
| 304 | practice | p01.005: run an empty editor | ok | 200 |
| 305 | practice | p01.005: run the untouched starter | ok | 255 |
| 306 | practice | p01.005: run the reference solution | ok | 186 |
| 307 | practice | p01.005: read the solution once passed | ok | 18 |
| 308 | practice | p01.006: read the brief | ok | 0 |
| 309 | practice | p01.006: reveal every hint | ok | 33 |
| 310 | practice | p01.006: run an empty editor | ok | 224 |
| 311 | practice | p01.006: run the untouched starter | ok | 224 |
| 312 | practice | p01.006: run the reference solution | ok | 207 |
| 313 | practice | p01.006: read the solution once passed | ok | 21 |
| 314 | practice | p01.007: read the brief | ok | 0 |
| 315 | practice | p01.007: reveal every hint | ok | 20 |
| 316 | practice | p01.007: run an empty editor | ok | 209 |
| 317 | practice | p01.007: run the untouched starter | ok | 232 |
| 318 | practice | p01.007: run the reference solution | ok | 363 |
| 319 | practice | p01.007: read the solution once passed | ok | 22 |
| 320 | practice | p01.008: read the brief | ok | 0 |
| 321 | practice | p01.008: reveal every hint | ok | 34 |
| 322 | practice | p01.008: run an empty editor | ok | 602 |
| 323 | practice | p01.008: run the untouched starter | ok | 327 |
| 324 | practice | p01.008: run the reference solution | ok | 223 |
| 325 | practice | p01.008: read the solution once passed | ok | 20 |
| 326 | practice | p01.009: read the brief | ok | 0 |
| 327 | practice | p01.009: reveal every hint | ok | 40 |
| 328 | practice | p01.009: run an empty editor | ok | 200 |
| 329 | practice | p01.009: run the untouched starter | ok | 236 |
| 330 | practice | p01.009: run the reference solution | ok | 373 |
| 331 | practice | p01.009: read the solution once passed | ok | 20 |
| 332 | practice | p01.010: read the brief | ok | 0 |
| 333 | practice | p01.010: reveal every hint | ok | 38 |
| 334 | practice | p01.010: run an empty editor | ok | 309 |
| 335 | practice | p01.010: run the untouched starter | ok | 235 |
| 336 | practice | p01.010: run the reference solution | ok | 285 |
| 337 | practice | p01.010: read the solution once passed | ok | 20 |
| 338 | practice | p01.011: read the brief | ok | 0 |
| 339 | practice | p01.011: reveal every hint | ok | 38 |
| 340 | practice | p01.011: run an empty editor | ok | 249 |
| 341 | practice | p01.011: run the untouched starter | ok | 672 |
| 342 | practice | p01.011: run the reference solution | ok | 215 |
| 343 | practice | p01.011: read the solution once passed | ok | 21 |
| 344 | practice | p01.012: read the brief | ok | 0 |
| 345 | practice | p01.012: reveal every hint | ok | 37 |
| 346 | practice | p01.012: run an empty editor | ok | 206 |
| 347 | practice | p01.012: run the untouched starter | ok | 227 |
| 348 | practice | p01.012: run the reference solution | ok | 212 |
| 349 | practice | p01.012: read the solution once passed | ok | 22 |
| 350 | practice | p01.013: read the brief | ok | 0 |
| 351 | practice | p01.013: reveal every hint | ok | 39 |
| 352 | practice | p01.013: run an empty editor | ok | 241 |
| 353 | practice | p01.013: run the untouched starter | ok | 238 |
| 354 | practice | p01.013: run the reference solution | ok | 222 |
| 355 | practice | p01.013: read the solution once passed | ok | 18 |
| 356 | practice | p01.014: read the brief | ok | 0 |
| 357 | practice | p01.014: reveal every hint | ok | 35 |
| 358 | practice | p01.014: run an empty editor | ok | 948 |
| 359 | practice | p01.014: run the untouched starter | ok | 239 |
| 360 | practice | p01.014: run the reference solution | ok | 263 |
| 361 | practice | p01.014: read the solution once passed | ok | 21 |
| 362 | practice | p01.015: read the brief | ok | 0 |
| 363 | practice | p01.015: reveal every hint | ok | 37 |
| 364 | practice | p01.015: run an empty editor | ok | 285 |
| 365 | practice | p01.015: run the untouched starter | ok | 256 |
| 366 | practice | p01.015: run the reference solution | ok | 319 |
| 367 | practice | p01.015: read the solution once passed | ok | 21 |
| 368 | practice | p01.016: read the brief | ok | 0 |
| 369 | practice | p01.016: reveal every hint | ok | 41 |
| 370 | practice | p01.016: run an empty editor | ok | 307 |
| 371 | practice | p01.016: run the untouched starter | ok | 517 |
| 372 | practice | p01.016: run the reference solution | ok | 237 |
| 373 | practice | p01.016: read the solution once passed | ok | 27 |
| 374 | practice | p01.017: read the brief | ok | 0 |
| 375 | practice | p01.017: reveal every hint | ok | 38 |
| 376 | practice | p01.017: run an empty editor | ok | 252 |
| 377 | practice | p01.017: run the untouched starter | ok | 241 |
| 378 | practice | p01.017: run the reference solution | ok | 204 |
| 379 | practice | p01.017: read the solution once passed | ok | 23 |
| 380 | practice | p01.018: read the brief | ok | 0 |
| 381 | practice | p01.018: reveal every hint | ok | 40 |
| 382 | practice | p01.018: run an empty editor | ok | 189 |
| 383 | practice | p01.018: run the untouched starter | ok | 224 |
| 384 | practice | p01.018: run the reference solution | ok | 244 |
| 385 | practice | p01.018: read the solution once passed | ok | 18 |
| 386 | practice | p01.019: read the brief | ok | 0 |
| 387 | practice | p01.019: reveal every hint | ok | 34 |
| 388 | practice | p01.019: run an empty editor | ok | 217 |
| 389 | practice | p01.019: run the untouched starter | ok | 281 |
| 390 | practice | p01.019: run the reference solution | ok | 215 |
| 391 | practice | p01.019: read the solution once passed | ok | 21 |
| 392 | practice | p01.020: read the brief | ok | 0 |
| 393 | practice | p01.020: reveal every hint | ok | 35 |
| 394 | practice | p01.020: run an empty editor | ok | 212 |
| 395 | practice | p01.020: run the untouched starter | ok | 266 |
| 396 | practice | p01.020: run the reference solution | ok | 220 |
| 397 | practice | p01.020: read the solution once passed | ok | 21 |
| 398 | practice | p01.021: read the brief | ok | 0 |
| 399 | practice | p01.021: reveal every hint | ok | 34 |
| 400 | practice | p01.021: run an empty editor | ok | 214 |
| 401 | practice | p01.021: run the untouched starter | ok | 305 |
| 402 | practice | p01.021: run the reference solution | ok | 243 |
| 403 | practice | p01.021: read the solution once passed | ok | 21 |
| 404 | practice | p01.022: read the brief | ok | 0 |
| 405 | practice | p01.022: reveal every hint | ok | 39 |
| 406 | practice | p01.022: run an empty editor | ok | 633 |
| 407 | practice | p01.022: run the untouched starter | ok | 221 |
| 408 | practice | p01.022: run the reference solution | ok | 219 |
| 409 | practice | p01.022: read the solution once passed | ok | 26 |
| 410 | practice | p01.023: read the brief | ok | 0 |
| 411 | practice | p01.023: reveal every hint | ok | 40 |
| 412 | practice | p01.023: run an empty editor | ok | 219 |
| 413 | practice | p01.023: run the untouched starter | ok | 384 |
| 414 | practice | p01.023: run the reference solution | ok | 244 |
| 415 | practice | p01.023: read the solution once passed | ok | 22 |
| 416 | practice | p01.024: read the brief | ok | 0 |
| 417 | practice | p01.024: reveal every hint | ok | 36 |
| 418 | practice | p01.024: run an empty editor | ok | 191 |
| 419 | practice | p01.024: run the untouched starter | ok | 258 |
| 420 | practice | p01.024: run the reference solution | ok | 203 |
| 421 | practice | p01.024: read the solution once passed | ok | 22 |
| 422 | practice | p01.025: read the brief | ok | 0 |
| 423 | practice | p01.025: reveal every hint | ok | 24 |
| 424 | practice | p01.025: run an empty editor | ok | 204 |
| 425 | practice | p01.025: run the untouched starter | ok | 237 |
| 426 | practice | p01.025: run the reference solution | ok | 217 |
| 427 | practice | p01.025: read the solution once passed | ok | 20 |
| 428 | practice | p01.026: read the brief | ok | 0 |
| 429 | practice | p01.026: reveal every hint | ok | 36 |
| 430 | practice | p01.026: run an empty editor | ok | 243 |
| 431 | practice | p01.026: run the untouched starter | ok | 262 |
| 432 | practice | p01.026: run the reference solution | ok | 267 |
| 433 | practice | p01.026: read the solution once passed | ok | 21 |
| 434 | practice | p01.027: read the brief | ok | 0 |
| 435 | practice | p01.027: reveal every hint | ok | 39 |
| 436 | practice | p01.027: run an empty editor | ok | 209 |
| 437 | practice | p01.027: run the untouched starter | ok | 232 |
| 438 | practice | p01.027: run the reference solution | ok | 211 |
| 439 | practice | p01.027: read the solution once passed | ok | 26 |
| 440 | practice | p01.028: read the brief | ok | 0 |
| 441 | practice | p01.028: reveal every hint | ok | 36 |
| 442 | practice | p01.028: run an empty editor | ok | 210 |
| 443 | practice | p01.028: run the untouched starter | ok | 237 |
| 444 | practice | p01.028: run the reference solution | ok | 228 |
| 445 | practice | p01.028: read the solution once passed | ok | 23 |
| 446 | practice | p01.029: read the brief | ok | 0 |
| 447 | practice | p01.029: reveal every hint | ok | 31 |
| 448 | practice | p01.029: run an empty editor | ok | 177 |
| 449 | practice | p01.029: run the untouched starter | ok | 235 |
| 450 | practice | p01.029: run the reference solution | ok | 217 |
| 451 | practice | p01.029: read the solution once passed | ok | 20 |
| 452 | practice | p01.030: read the brief | ok | 0 |
| 453 | practice | p01.030: reveal every hint | ok | 26 |
| 454 | practice | p01.030: run an empty editor | ok | 190 |
| 455 | practice | p01.030: run the untouched starter | ok | 215 |
| 456 | practice | p01.030: run the reference solution | ok | 224 |
| 457 | practice | p01.030: read the solution once passed | ok | 21 |
| 458 | practice | p01.031: read the brief | ok | 0 |
| 459 | practice | p01.031: reveal every hint | ok | 37 |
| 460 | practice | p01.031: run an empty editor | ok | 218 |
| 461 | practice | p01.031: run the untouched starter | ok | 222 |
| 462 | practice | p01.031: run the reference solution | ok | 211 |
| 463 | practice | p01.031: read the solution once passed | ok | 24 |
| 464 | practice | p01.032: read the brief | ok | 0 |
| 465 | practice | p01.032: reveal every hint | ok | 35 |
| 466 | practice | p01.032: run an empty editor | ok | 188 |
| 467 | practice | p01.032: run the untouched starter | ok | 221 |
| 468 | practice | p01.032: run the reference solution | ok | 201 |
| 469 | practice | p01.032: read the solution once passed | ok | 21 |
| 470 | practice | p01.033: read the brief | ok | 0 |
| 471 | practice | p01.033: reveal every hint | ok | 23 |
| 472 | practice | p01.033: run an empty editor | ok | 189 |
| 473 | practice | p01.033: run the untouched starter | ok | 233 |
| 474 | practice | p01.033: run the reference solution | ok | 207 |
| 475 | practice | p01.033: read the solution once passed | ok | 22 |
| 476 | practice | p01.034: read the brief | ok | 0 |
| 477 | practice | p01.034: reveal every hint | ok | 24 |
| 478 | practice | p01.034: run an empty editor | ok | 186 |
| 479 | practice | p01.034: run the untouched starter | ok | 224 |
| 480 | practice | p01.034: run the reference solution | ok | 206 |
| 481 | practice | p01.034: read the solution once passed | ok | 24 |
| 482 | practice | p01.035: read the brief | ok | 0 |
| 483 | practice | p01.035: reveal every hint | ok | 38 |
| 484 | practice | p01.035: run an empty editor | ok | 218 |
| 485 | practice | p01.035: run the untouched starter | ok | 224 |
| 486 | practice | p01.035: run the reference solution | ok | 223 |
| 487 | practice | p01.035: read the solution once passed | ok | 19 |
| 488 | practice | p01.036: read the brief | ok | 0 |
| 489 | practice | p01.036: reveal every hint | ok | 40 |
| 490 | practice | p01.036: run an empty editor | ok | 204 |
| 491 | practice | p01.036: run the untouched starter | ok | 236 |
| 492 | practice | p01.036: run the reference solution | ok | 208 |
| 493 | practice | p01.036: read the solution once passed | ok | 21 |
| 494 | practice | p02.001: read the brief | ok | 0 |
| 495 | practice | p02.001: reveal every hint | ok | 25 |
| 496 | practice | p02.001: run an empty editor | ok | 188 |
| 497 | practice | p02.001: run the untouched starter | ok | 202 |
| 498 | practice | p02.001: run the reference solution | ok | 211 |
| 499 | practice | p02.001: read the solution once passed | ok | 22 |
| 500 | practice | p02.002: read the brief | ok | 0 |
| 501 | practice | p02.002: reveal every hint | ok | 21 |
| 502 | practice | p02.002: run an empty editor | ok | 199 |
| 503 | practice | p02.002: run the untouched starter | ok | 211 |
| 504 | practice | p02.002: run the reference solution | ok | 198 |
| 505 | practice | p02.002: read the solution once passed | ok | 20 |
| 506 | practice | p02.003: read the brief | ok | 0 |
| 507 | practice | p02.003: reveal every hint | ok | 24 |
| 508 | practice | p02.003: run an empty editor | ok | 195 |
| 509 | practice | p02.003: run the untouched starter | ok | 199 |
| 510 | practice | p02.003: run the reference solution | ok | 210 |
| 511 | practice | p02.003: read the solution once passed | ok | 20 |
| 512 | practice | p02.004: read the brief | ok | 0 |
| 513 | practice | p02.004: reveal every hint | ok | 28 |
| 514 | practice | p02.004: run an empty editor | ok | 185 |
| 515 | practice | p02.004: run the untouched starter | ok | 187 |
| 516 | practice | p02.004: run the reference solution | ok | 197 |
| 517 | practice | p02.004: read the solution once passed | ok | 22 |
| 518 | practice | p02.005: read the brief | ok | 0 |
| 519 | practice | p02.005: reveal every hint | ok | 23 |
| 520 | practice | p02.005: run an empty editor | ok | 190 |
| 521 | practice | p02.005: run the untouched starter | ok | 251 |
| 522 | practice | p02.005: run the reference solution | ok | 244 |
| 523 | practice | p02.005: read the solution once passed | ok | 21 |
| 524 | practice | p02.006: read the brief | ok | 0 |
| 525 | practice | p02.006: reveal every hint | ok | 25 |
| 526 | practice | p02.006: run an empty editor | ok | 415 |
| 527 | practice | p02.006: run the untouched starter | ok | 230 |
| 528 | practice | p02.006: run the reference solution | ok | 300 |
| 529 | practice | p02.006: read the solution once passed | ok | 17 |
| 530 | practice | p02.007: read the brief | ok | 0 |
| 531 | practice | p02.007: reveal every hint | ok | 32 |
| 532 | practice | p02.007: run an empty editor | ok | 555 |
| 533 | practice | p02.007: run the untouched starter | ok | 218 |
| 534 | practice | p02.007: run the reference solution | ok | 244 |
| 535 | practice | p02.007: read the solution once passed | ok | 20 |
| 536 | practice | p02.008: read the brief | ok | 0 |
| 537 | practice | p02.008: reveal every hint | ok | 30 |
| 538 | practice | p02.008: run an empty editor | ok | 202 |
| 539 | practice | p02.008: run the untouched starter | ok | 235 |
| 540 | practice | p02.008: run the reference solution | ok | 330 |
| 541 | practice | p02.008: read the solution once passed | ok | 22 |
| 542 | practice | p02.009: read the brief | ok | 0 |
| 543 | practice | p02.009: reveal every hint | ok | 25 |
| 544 | practice | p02.009: run an empty editor | ok | 202 |
| 545 | practice | p02.009: run the untouched starter | ok | 213 |
| 546 | practice | p02.009: run the reference solution | ok | 226 |
| 547 | practice | p02.009: read the solution once passed | ok | 17 |
| 548 | practice | p02.010: read the brief | ok | 0 |
| 549 | practice | p02.010: reveal every hint | ok | 27 |
| 550 | practice | p02.010: run an empty editor | ok | 207 |
| 551 | practice | p02.010: run the untouched starter | ok | 224 |
| 552 | practice | p02.010: run the reference solution | ok | 237 |
| 553 | practice | p02.010: read the solution once passed | ok | 23 |
| 554 | practice | p02.011: read the brief | ok | 0 |
| 555 | practice | p02.011: reveal every hint | ok | 28 |
| 556 | practice | p02.011: run an empty editor | ok | 210 |
| 557 | practice | p02.011: run the untouched starter | ok | 237 |
| 558 | practice | p02.011: run the reference solution | ok | 209 |
| 559 | practice | p02.011: read the solution once passed | ok | 20 |
| 560 | practice | p02.012: read the brief | ok | 0 |
| 561 | practice | p02.012: reveal every hint | ok | 22 |
| 562 | practice | p02.012: run an empty editor | ok | 202 |
| 563 | practice | p02.012: run the untouched starter | ok | 231 |
| 564 | practice | p02.012: run the reference solution | ok | 195 |
| 565 | practice | p02.012: read the solution once passed | ok | 19 |
| 566 | practice | p02.013: read the brief | ok | 0 |
| 567 | practice | p02.013: reveal every hint | ok | 28 |
| 568 | practice | p02.013: run an empty editor | ok | 235 |
| 569 | practice | p02.013: run the untouched starter | ok | 442 |
| 570 | practice | p02.013: run the reference solution | ok | 219 |
| 571 | practice | p02.013: read the solution once passed | ok | 18 |
| 572 | practice | p02.014: read the brief | ok | 0 |
| 573 | practice | p02.014: reveal every hint | ok | 25 |
| 574 | practice | p02.014: run an empty editor | ok | 213 |
| 575 | practice | p02.014: run the untouched starter | ok | 272 |
| 576 | practice | p02.014: run the reference solution | ok | 210 |
| 577 | practice | p02.014: read the solution once passed | ok | 19 |
| 578 | practice | p02.015: read the brief | ok | 0 |
| 579 | practice | p02.015: reveal every hint | ok | 34 |
| 580 | practice | p02.015: run an empty editor | ok | 202 |
| 581 | practice | p02.015: run the untouched starter | ok | 234 |
| 582 | practice | p02.015: run the reference solution | ok | 209 |
| 583 | practice | p02.015: read the solution once passed | ok | 18 |
| 584 | practice | p02.016: read the brief | ok | 0 |
| 585 | practice | p02.016: reveal every hint | ok | 20 |
| 586 | practice | p02.016: run an empty editor | ok | 197 |
| 587 | practice | p02.016: run the untouched starter | ok | 244 |
| 588 | practice | p02.016: run the reference solution | ok | 204 |
| 589 | practice | p02.016: read the solution once passed | ok | 21 |
| 590 | practice | p04.011: read the brief | ok | 0 |
| 591 | practice | p04.011: reveal every hint | ok | 34 |
| 592 | practice | p04.011: run an empty editor | ok | 762 |
| 593 | practice | p04.011: run the untouched starter | ok | 497 |
| 594 | practice | p04.011: run the reference solution | ok | 436 |
| 595 | practice | p04.011: read the solution once passed | ok | 21 |
| 596 | practice | p04.012: read the brief | ok | 0 |
| 597 | practice | p04.012: reveal every hint | ok | 33 |
| 598 | practice | p04.012: run an empty editor | ok | 210 |
| 599 | practice | p04.012: run the untouched starter | ok | 229 |
| 600 | practice | p04.012: run the reference solution | ok | 206 |
| 601 | practice | p04.012: read the solution once passed | ok | 18 |
| 602 | practice | p04.013: read the brief | ok | 0 |
| 603 | practice | p04.013: reveal every hint | ok | 30 |
| 604 | practice | p04.013: run an empty editor | ok | 207 |
| 605 | practice | p04.013: run the untouched starter | ok | 252 |
| 606 | practice | p04.013: run the reference solution | ok | 218 |
| 607 | practice | p04.013: read the solution once passed | ok | 16 |
| 608 | practice | p04.001: read the brief | ok | 0 |
| 609 | practice | p04.001: reveal every hint | ok | 28 |
| 610 | practice | p04.001: run an empty editor | ok | 215 |
| 611 | practice | p04.001: run the untouched starter | ok | 224 |
| 612 | practice | p04.001: run the reference solution | ok | 210 |
| 613 | practice | p04.001: read the solution once passed | ok | 18 |
| 614 | practice | p04.002: read the brief | ok | 0 |
| 615 | practice | p04.002: reveal every hint | ok | 25 |
| 616 | practice | p04.002: run an empty editor | ok | 189 |
| 617 | practice | p04.002: run the untouched starter | ok | 213 |
| 618 | practice | p04.002: run the reference solution | ok | 214 |
| 619 | practice | p04.002: read the solution once passed | ok | 18 |
| 620 | practice | p04.003: read the brief | ok | 0 |
| 621 | practice | p04.003: reveal every hint | ok | 38 |
| 622 | practice | p04.003: run an empty editor | ok | 194 |
| 623 | practice | p04.003: run the untouched starter | ok | 241 |
| 624 | practice | p04.003: run the reference solution | ok | 209 |
| 625 | practice | p04.003: read the solution once passed | ok | 18 |
| 626 | practice | p04.004: read the brief | ok | 0 |
| 627 | practice | p04.004: reveal every hint | ok | 30 |
| 628 | practice | p04.004: run an empty editor | ok | 193 |
| 629 | practice | p04.004: run the untouched starter | ok | 200 |
| 630 | practice | p04.004: run the reference solution | ok | 208 |
| 631 | practice | p04.004: read the solution once passed | ok | 19 |
| 632 | practice | p04.005: read the brief | ok | 0 |
| 633 | practice | p04.005: reveal every hint | ok | 34 |
| 634 | practice | p04.005: run an empty editor | ok | 211 |
| 635 | practice | p04.005: run the untouched starter | ok | 357 |
| 636 | practice | p04.005: run the reference solution | ok | 225 |
| 637 | practice | p04.005: read the solution once passed | ok | 18 |
| 638 | practice | p04.006: read the brief | ok | 0 |
| 639 | practice | p04.006: reveal every hint | ok | 34 |
| 640 | practice | p04.006: run an empty editor | ok | 328 |
| 641 | practice | p04.006: run the untouched starter | ok | 231 |
| 642 | practice | p04.006: run the reference solution | ok | 400 |
| 643 | practice | p04.006: read the solution once passed | ok | 19 |
| 644 | practice | p04.007: read the brief | ok | 0 |
| 645 | practice | p04.007: reveal every hint | ok | 28 |
| 646 | practice | p04.007: run an empty editor | ok | 191 |
| 647 | practice | p04.007: run the untouched starter | ok | 234 |
| 648 | practice | p04.007: run the reference solution | ok | 193 |
| 649 | practice | p04.007: read the solution once passed | ok | 22 |
| 650 | practice | p04.008: read the brief | ok | 0 |
| 651 | practice | p04.008: reveal every hint | ok | 28 |
| 652 | practice | p04.008: run an empty editor | ok | 247 |
| 653 | practice | p04.008: run the untouched starter | ok | 489 |
| 654 | practice | p04.008: run the reference solution | ok | 274 |
| 655 | practice | p04.008: read the solution once passed | ok | 20 |
| 656 | practice | p04.009: read the brief | ok | 0 |
| 657 | practice | p04.009: reveal every hint | ok | 30 |
| 658 | practice | p04.009: run an empty editor | ok | 204 |
| 659 | practice | p04.009: run the untouched starter | ok | 240 |
| 660 | practice | p04.009: run the reference solution | ok | 219 |
| 661 | practice | p04.009: read the solution once passed | ok | 24 |
| 662 | practice | p04.010: read the brief | ok | 0 |
| 663 | practice | p04.010: reveal every hint | ok | 28 |
| 664 | practice | p04.010: run an empty editor | ok | 202 |
| 665 | practice | p04.010: run the untouched starter | ok | 214 |
| 666 | practice | p04.010: run the reference solution | ok | 220 |
| 667 | practice | p04.010: read the solution once passed | ok | 19 |
| 668 | practice | p05.001: read the brief | ok | 0 |
| 669 | practice | p05.001: reveal every hint | ok | 30 |
| 670 | practice | p05.001: run an empty editor | ok | 208 |
| 671 | practice | p05.001: run the untouched starter | ok | 220 |
| 672 | practice | p05.001: run the reference solution | ok | 210 |
| 673 | practice | p05.001: read the solution once passed | ok | 19 |
| 674 | practice | p05.002: read the brief | ok | 0 |
| 675 | practice | p05.002: reveal every hint | ok | 30 |
| 676 | practice | p05.002: run an empty editor | ok | 205 |
| 677 | practice | p05.002: run the untouched starter | ok | 229 |
| 678 | practice | p05.002: run the reference solution | ok | 210 |
| 679 | practice | p05.002: read the solution once passed | ok | 19 |
| 680 | practice | p05.003: read the brief | ok | 0 |
| 681 | practice | p05.003: reveal every hint | ok | 29 |
| 682 | practice | p05.003: run an empty editor | ok | 200 |
| 683 | practice | p05.003: run the untouched starter | ok | 219 |
| 684 | practice | p05.003: run the reference solution | ok | 219 |
| 685 | practice | p05.003: read the solution once passed | ok | 18 |
| 686 | practice | p05.004: read the brief | ok | 0 |
| 687 | practice | p05.004: reveal every hint | ok | 35 |
| 688 | practice | p05.004: run an empty editor | ok | 207 |
| 689 | practice | p05.004: run the untouched starter | ok | 239 |
| 690 | practice | p05.004: run the reference solution | ok | 1054 |
| 691 | practice | p05.004: read the solution once passed | ok | 19 |
| 692 | practice | p05.005: read the brief | ok | 0 |
| 693 | practice | p05.005: reveal every hint | ok | 34 |
| 694 | practice | p05.005: run an empty editor | ok | 528 |
| 695 | practice | p05.005: run the untouched starter | ok | 240 |
| 696 | practice | p05.005: run the reference solution | ok | 219 |
| 697 | practice | p05.005: read the solution once passed | ok | 19 |
| 698 | practice | p05.006: read the brief | ok | 0 |
| 699 | practice | p05.006: reveal every hint | ok | 30 |
| 700 | practice | p05.006: run an empty editor | ok | 217 |
| 701 | practice | p05.006: run the untouched starter | ok | 228 |
| 702 | practice | p05.006: run the reference solution | ok | 293 |
| 703 | practice | p05.006: read the solution once passed | ok | 20 |
| 704 | practice | p05.007: read the brief | ok | 0 |
| 705 | practice | p05.007: reveal every hint | ok | 30 |
| 706 | practice | p05.007: run an empty editor | ok | 403 |
| 707 | practice | p05.007: run the untouched starter | ok | 697 |
| 708 | practice | p05.007: run the reference solution | ok | 321 |
| 709 | practice | p05.007: read the solution once passed | ok | 19 |
| 710 | practice | p05.008: read the brief | ok | 0 |
| 711 | practice | p05.008: reveal every hint | ok | 34 |
| 712 | practice | p05.008: run an empty editor | ok | 1249 |
| 713 | practice | p05.008: run the untouched starter | ok | 1351 |
| 714 | practice | p05.008: run the reference solution | ok | 691 |
| 715 | practice | p05.008: read the solution once passed | ok | 26 |
| 716 | practice | p05.009: read the brief | ok | 0 |
| 717 | practice | p05.009: reveal every hint | ok | 55 |
| 718 | practice | p05.009: run an empty editor | ok | 1070 |
| 719 | practice | p05.009: run the untouched starter | ok | 678 |
| 720 | practice | p05.009: run the reference solution | ok | 497 |
| 721 | practice | p05.009: read the solution once passed | ok | 21 |
| 722 | practice | p05.010: read the brief | ok | 0 |
| 723 | practice | p05.010: reveal every hint | ok | 38 |
| 724 | practice | p05.010: run an empty editor | ok | 309 |
| 725 | practice | p05.010: run the untouched starter | ok | 431 |
| 726 | practice | p05.010: run the reference solution | ok | 340 |
| 727 | practice | p05.010: read the solution once passed | ok | 19 |
| 728 | practice | p03.001: read the brief | ok | 0 |
| 729 | practice | p03.001: reveal every hint | ok | 24 |
| 730 | practice | p03.001: run an empty editor | ok | 319 |
| 731 | practice | p03.001: run the untouched starter | ok | 385 |
| 732 | practice | p03.001: run the reference solution | ok | 363 |
| 733 | practice | p03.001: read the solution once passed | ok | 21 |
| 734 | practice | p03.002: read the brief | ok | 0 |
| 735 | practice | p03.002: reveal every hint | ok | 22 |
| 736 | practice | p03.002: run an empty editor | ok | 298 |
| 737 | practice | p03.002: run the untouched starter | ok | 308 |
| 738 | practice | p03.002: run the reference solution | ok | 427 |
| 739 | practice | p03.002: read the solution once passed | ok | 23 |
| 740 | practice | p03.003: read the brief | ok | 0 |
| 741 | practice | p03.003: reveal every hint | ok | 25 |
| 742 | practice | p03.003: run an empty editor | ok | 307 |
| 743 | practice | p03.003: run the untouched starter | ok | 304 |
| 744 | practice | p03.003: run the reference solution | ok | 360 |
| 745 | practice | p03.003: read the solution once passed | ok | 26 |
| 746 | practice | p03.004: read the brief | ok | 0 |
| 747 | practice | p03.004: reveal every hint | ok | 41 |
| 748 | practice | p03.004: run an empty editor | ok | 661 |
| 749 | practice | p03.004: run the untouched starter | ok | 415 |
| 750 | practice | p03.004: run the reference solution | ok | 410 |
| 751 | practice | p03.004: read the solution once passed | ok | 17 |
| 752 | practice | p08.001: read the brief | ok | 0 |
| 753 | practice | p08.001: reveal every hint | ok | 34 |
| 754 | practice | p08.001: run an empty editor | ok | 357 |
| 755 | practice | p08.001: run the untouched starter | ok | 254 |
| 756 | practice | p08.001: run the reference solution | ok | 269 |
| 757 | practice | p08.001: read the solution once passed | ok | 21 |
| 758 | practice | p08.002: read the brief | ok | 0 |
| 759 | practice | p08.002: reveal every hint | ok | 31 |
| 760 | practice | p08.002: run an empty editor | ok | 217 |
| 761 | practice | p08.002: run the untouched starter | ok | 445 |
| 762 | practice | p08.002: run the reference solution | ok | 512 |
| 763 | practice | p08.002: read the solution once passed | ok | 18 |
| 764 | practice | p08.003: read the brief | ok | 0 |
| 765 | practice | p08.003: reveal every hint | ok | 31 |
| 766 | practice | p08.003: run an empty editor | ok | 281 |
| 767 | practice | p08.003: run the untouched starter | ok | 237 |
| 768 | practice | p08.003: run the reference solution | ok | 228 |
| 769 | practice | p08.003: read the solution once passed | ok | 18 |
| 770 | practice | p08.004: read the brief | ok | 0 |
| 771 | practice | p08.004: reveal every hint | ok | 26 |
| 772 | practice | p08.004: run an empty editor | ok | 312 |
| 773 | practice | p08.004: run the untouched starter | ok | 291 |
| 774 | practice | p08.004: run the reference solution | ok | 418 |
| 775 | practice | p08.004: read the solution once passed | ok | 19 |
| 776 | practice | p09.001: read the brief | ok | 0 |
| 777 | practice | p09.001: reveal every hint | ok | 32 |
| 778 | practice | p09.001: run an empty editor | ok | 251 |
| 779 | practice | p09.001: run the untouched starter | ok | 345 |
| 780 | practice | p09.001: run the reference solution | ok | 243 |
| 781 | practice | p09.001: read the solution once passed | ok | 20 |
| 782 | practice | p09.002: read the brief | ok | 0 |
| 783 | practice | p09.002: reveal every hint | ok | 38 |
| 784 | practice | p09.002: run an empty editor | ok | 378 |
| 785 | practice | p09.002: run the untouched starter | ok | 444 |
| 786 | practice | p09.002: run the reference solution | ok | 334 |
| 787 | practice | p09.002: read the solution once passed | ok | 29 |
| 788 | practice | p09.003: read the brief | ok | 0 |
| 789 | practice | p09.003: reveal every hint | ok | 27 |
| 790 | practice | p09.003: run an empty editor | ok | 302 |
| 791 | practice | p09.003: run the untouched starter | ok | 712 |
| 792 | practice | p09.003: run the reference solution | ok | 1735 |
| 793 | practice | p09.003: read the solution once passed | ok | 24 |
| 794 | practice | p10.001: read the brief | ok | 0 |
| 795 | practice | p10.001: reveal every hint | ok | 31 |
| 796 | practice | p10.001: run an empty editor | ok | 549 |
| 797 | practice | p10.001: run the untouched starter | ok | 461 |
| 798 | practice | p10.001: run the reference solution | ok | 934 |
| 799 | practice | p10.001: read the solution once passed | ok | 17 |
| 800 | practice | p10.002: read the brief | ok | 0 |
| 801 | practice | p10.002: reveal every hint | ok | 36 |
| 802 | practice | p10.002: run an empty editor | ok | 355 |
| 803 | practice | p10.002: run the untouched starter | ok | 354 |
| 804 | practice | p10.002: run the reference solution | ok | 303 |
| 805 | practice | p10.002: read the solution once passed | ok | 16 |
| 806 | practice | p10.003: read the brief | ok | 0 |
| 807 | practice | p10.003: reveal every hint | ok | 28 |
| 808 | practice | p10.003: run an empty editor | ok | 346 |
| 809 | practice | p10.003: run the untouched starter | ok | 325 |
| 810 | practice | p10.003: run the reference solution | ok | 1650 |
| 811 | practice | p10.003: read the solution once passed | ok | 25 |
| 812 | practice | p11.001: read the brief | ok | 0 |
| 813 | practice | p11.001: reveal every hint | ok | 40 |
| 814 | practice | p11.001: run an empty editor | ok | 1138 |
| 815 | practice | p11.001: run the untouched starter | ok | 978 |
| 816 | practice | p11.001: run the reference solution | ok | 1317 |
| 817 | practice | p11.001: read the solution once passed | ok | 22 |
| 818 | practice | p11.002: read the brief | ok | 0 |
| 819 | practice | p11.002: reveal every hint | ok | 25 |
| 820 | practice | p11.002: run an empty editor | ok | 417 |
| 821 | practice | p11.002: run the untouched starter | ok | 819 |
| 822 | practice | p11.002: run the reference solution | ok | 890 |
| 823 | practice | p11.002: read the solution once passed | ok | 18 |
| 824 | practice | p11.003: read the brief | ok | 0 |
| 825 | practice | p11.003: reveal every hint | ok | 21 |
| 826 | practice | p11.003: run an empty editor | ok | 455 |
| 827 | practice | p11.003: run the untouched starter | ok | 505 |
| 828 | practice | p11.003: run the reference solution | ok | 570 |
| 829 | practice | p11.003: read the solution once passed | ok | 19 |
| 830 | practice | p13.001: read the brief | ok | 0 |
| 831 | practice | p13.001: reveal every hint | ok | 30 |
| 832 | practice | p13.001: run an empty editor | ok | 316 |
| 833 | practice | p13.001: run the untouched starter | ok | 295 |
| 834 | practice | p13.001: run the reference solution | ok | 823 |
| 835 | practice | p13.001: read the solution once passed | ok | 18 |
| 836 | practice | p13.002: read the brief | ok | 0 |
| 837 | practice | p13.002: reveal every hint | ok | 22 |
| 838 | practice | p13.002: run an empty editor | ok | 211 |
| 839 | practice | p13.002: run the untouched starter | ok | 232 |
| 840 | practice | p13.002: run the reference solution | ok | 296 |
| 841 | practice | p13.002: read the solution once passed | ok | 18 |
| 842 | practice | p13.003: read the brief | ok | 0 |
| 843 | practice | p13.003: reveal every hint | ok | 22 |
| 844 | practice | p13.003: run an empty editor | ok | 532 |
| 845 | practice | p13.003: run the untouched starter | ok | 440 |
| 846 | practice | p13.003: run the reference solution | ok | 243 |
| 847 | practice | p13.003: read the solution once passed | ok | 20 |
| 848 | practice | p14.001: read the brief | ok | 0 |
| 849 | practice | p14.001: reveal every hint | ok | 31 |
| 850 | practice | p14.001: run an empty editor | ok | 266 |
| 851 | practice | p14.001: run the untouched starter | ok | 246 |
| 852 | practice | p14.001: run the reference solution | ok | 221 |
| 853 | practice | p14.001: read the solution once passed | ok | 19 |
| 854 | practice | p14.002: read the brief | ok | 0 |
| 855 | practice | p14.002: reveal every hint | ok | 26 |
| 856 | practice | p14.002: run an empty editor | ok | 200 |
| 857 | practice | p14.002: run the untouched starter | ok | 231 |
| 858 | practice | p14.002: run the reference solution | ok | 234 |
| 859 | practice | p14.002: read the solution once passed | ok | 22 |
| 860 | practice | p14.003: read the brief | ok | 0 |
| 861 | practice | p14.003: reveal every hint | ok | 25 |
| 862 | practice | p14.003: run an empty editor | ok | 230 |
| 863 | practice | p14.003: run the untouched starter | ok | 264 |
| 864 | practice | p14.003: run the reference solution | ok | 279 |
| 865 | practice | p14.003: read the solution once passed | ok | 25 |
| 866 | practice | p14.004: read the brief | ok | 0 |
| 867 | practice | p14.004: reveal every hint | ok | 30 |
| 868 | practice | p14.004: run an empty editor | ok | 224 |
| 869 | practice | p14.004: run the untouched starter | ok | 256 |
| 870 | practice | p14.004: run the reference solution | ok | 325 |
| 871 | practice | p14.004: read the solution once passed | ok | 22 |
| 872 | practice | p06.001: read the brief | ok | 0 |
| 873 | practice | p06.001: reveal every hint | ok | 44 |
| 874 | practice | p06.001: run an empty editor | ok | 248 |
| 875 | practice | p06.001: run the untouched starter | ok | 249 |
| 876 | practice | p06.001: run the reference solution | ok | 225 |
| 877 | practice | p06.001: read the solution once passed | ok | 19 |
| 878 | practice | p06.002: read the brief | ok | 0 |
| 879 | practice | p06.002: reveal every hint | ok | 30 |
| 880 | practice | p06.002: run an empty editor | ok | 214 |
| 881 | practice | p06.002: run the untouched starter | ok | 234 |
| 882 | practice | p06.002: run the reference solution | ok | 212 |
| 883 | practice | p06.002: read the solution once passed | ok | 17 |
| 884 | practice | p06.003: read the brief | ok | 0 |
| 885 | practice | p06.003: reveal every hint | ok | 31 |
| 886 | practice | p06.003: run an empty editor | ok | 218 |
| 887 | practice | p06.003: run the untouched starter | ok | 252 |
| 888 | practice | p06.003: run the reference solution | ok | 216 |
| 889 | practice | p06.003: read the solution once passed | ok | 18 |
| 890 | practice | p06.004: read the brief | ok | 0 |
| 891 | practice | p06.004: reveal every hint | ok | 36 |
| 892 | practice | p06.004: run an empty editor | ok | 225 |
| 893 | practice | p06.004: run the untouched starter | ok | 327 |
| 894 | practice | p06.004: run the reference solution | ok | 452 |
| 895 | practice | p06.004: read the solution once passed | ok | 23 |
| 896 | practice | p07.001: read the brief | ok | 0 |
| 897 | practice | p07.001: reveal every hint | ok | 33 |
| 898 | practice | p07.001: run an empty editor | ok | 263 |
| 899 | practice | p07.001: run the untouched starter | ok | 313 |
| 900 | practice | p07.001: run the reference solution | ok | 1118 |
| 901 | practice | p07.001: read the solution once passed | ok | 19 |
| 902 | practice | p07.002: read the brief | ok | 0 |
| 903 | practice | p07.002: reveal every hint | ok | 32 |
| 904 | practice | p07.002: run an empty editor | ok | 711 |
| 905 | practice | p07.002: run the untouched starter | ok | 363 |
| 906 | practice | p07.002: run the reference solution | ok | 207 |
| 907 | practice | p07.002: read the solution once passed | ok | 18 |
| 908 | practice | p07.003: read the brief | ok | 0 |
| 909 | practice | p07.003: reveal every hint | ok | 33 |
| 910 | practice | p07.003: run an empty editor | ok | 217 |
| 911 | practice | p07.003: run the untouched starter | ok | 242 |
| 912 | practice | p07.003: run the reference solution | ok | 242 |
| 913 | practice | p07.003: read the solution once passed | ok | 18 |
| 914 | practice | p07.004: read the brief | ok | 0 |
| 915 | practice | p07.004: reveal every hint | ok | 35 |
| 916 | practice | p07.004: run an empty editor | ok | 259 |
| 917 | practice | p07.004: run the untouched starter | ok | 226 |
| 918 | practice | p07.004: run the reference solution | ok | 244 |
| 919 | practice | p07.004: read the solution once passed | ok | 22 |
| 920 | practice | p12.001: read the brief | ok | 0 |
| 921 | practice | p12.001: reveal every hint | ok | 33 |
| 922 | practice | p12.001: run an empty editor | ok | 414 |
| 923 | practice | p12.001: run the untouched starter | ok | 234 |
| 924 | practice | p12.001: run the reference solution | ok | 212 |
| 925 | practice | p12.001: read the solution once passed | ok | 16 |
| 926 | practice | p12.002: read the brief | ok | 0 |
| 927 | practice | p12.002: reveal every hint | ok | 40 |
| 928 | practice | p12.002: run an empty editor | ok | 1220 |
| 929 | practice | p12.002: run the untouched starter | ok | 295 |
| 930 | practice | p12.002: run the reference solution | ok | 218 |
| 931 | practice | p12.002: read the solution once passed | ok | 19 |
| 932 | practice | p12.003: read the brief | ok | 0 |
| 933 | practice | p12.003: reveal every hint | ok | 47 |
| 934 | practice | p12.003: run an empty editor | ok | 216 |
| 935 | practice | p12.003: run the untouched starter | ok | 231 |
| 936 | practice | p12.003: run the reference solution | ok | 211 |
| 937 | practice | p12.003: read the solution once passed | ok | 19 |
| 938 | practice | p15.001: read the brief | ok | 0 |
| 939 | practice | p15.001: reveal every hint | ok | 37 |
| 940 | practice | p15.001: run an empty editor | ok | 204 |
| 941 | practice | p15.001: run the untouched starter | ok | 230 |
| 942 | practice | p15.001: run the reference solution | ok | 239 |
| 943 | practice | p15.001: read the solution once passed | ok | 24 |
| 944 | practice | p15.002: read the brief | ok | 0 |
| 945 | practice | p15.002: reveal every hint | ok | 34 |
| 946 | practice | p15.002: run an empty editor | ok | 262 |
| 947 | practice | p15.002: run the untouched starter | ok | 324 |
| 948 | practice | p15.002: run the reference solution | ok | 250 |
| 949 | practice | p15.002: read the solution once passed | ok | 19 |
| 950 | practice | p15.003: read the brief | ok | 0 |
| 951 | practice | p15.003: reveal every hint | ok | 41 |
| 952 | practice | p15.003: run an empty editor | ok | 235 |
| 953 | practice | p15.003: run the untouched starter | ok | 251 |
| 954 | practice | p15.003: run the reference solution | ok | 273 |
| 955 | practice | p15.003: read the solution once passed | ok | 25 |
| 956 | practice | p16.001: read the brief | ok | 0 |
| 957 | practice | p16.001: reveal every hint | ok | 36 |
| 958 | practice | p16.001: run an empty editor | ok | 231 |
| 959 | practice | p16.001: run the untouched starter | ok | 225 |
| 960 | practice | p16.001: run the reference solution | ok | 209 |
| 961 | practice | p16.001: read the solution once passed | ok | 18 |
| 962 | practice | p16.002: read the brief | ok | 0 |
| 963 | practice | p16.002: reveal every hint | ok | 30 |
| 964 | practice | p16.002: run an empty editor | ok | 199 |
| 965 | practice | p16.002: run the untouched starter | ok | 241 |
| 966 | practice | p16.002: run the reference solution | ok | 216 |
| 967 | practice | p16.002: read the solution once passed | ok | 19 |
| 968 | practice | p16.003: read the brief | ok | 0 |
| 969 | practice | p16.003: reveal every hint | ok | 37 |
| 970 | practice | p16.003: run an empty editor | ok | 232 |
| 971 | practice | p16.003: run the untouched starter | ok | 241 |
| 972 | practice | p16.003: run the reference solution | ok | 227 |
| 973 | practice | p16.003: read the solution once passed | ok | 22 |
| 974 | practice | p17.001: read the brief | ok | 0 |
| 975 | practice | p17.001: reveal every hint | ok | 40 |
| 976 | practice | p17.001: run an empty editor | ok | 233 |
| 977 | practice | p17.001: run the untouched starter | ok | 248 |
| 978 | practice | p17.001: run the reference solution | ok | 254 |
| 979 | practice | p17.001: read the solution once passed | ok | 24 |
| 980 | practice | p17.002: read the brief | ok | 0 |
| 981 | practice | p17.002: reveal every hint | ok | 39 |
| 982 | practice | p17.002: run an empty editor | ok | 253 |
| 983 | practice | p17.002: run the untouched starter | ok | 241 |
| 984 | practice | p17.002: run the reference solution | ok | 228 |
| 985 | practice | p17.002: read the solution once passed | ok | 19 |
| 986 | practice | p17.003: read the brief | ok | 0 |
| 987 | practice | p17.003: reveal every hint | ok | 38 |
| 988 | practice | p17.003: run an empty editor | ok | 215 |
| 989 | practice | p17.003: run the untouched starter | ok | 260 |
| 990 | practice | p17.003: run the reference solution | ok | 257 |
| 991 | practice | p17.003: read the solution once passed | ok | 24 |
| 992 | practice | the counter agrees with the store | ok | 0 |
| 993 | practice | press Run checks and read the result | ok | 205 |
| 994 | practice | close the window while a run is in flight | ok | 12064 |
| 995 | quiz | read the quiz picker | ok | 0 |
| 996 | quiz | answer all 8 questions in q00 correctly | ok | 285 |
| 997 | quiz | answer all 18 questions in q01 correctly | ok | 668 |
| 998 | quiz | answer all 11 questions in q02 correctly | ok | 394 |
| 999 | quiz | answer all 8 questions in q03 correctly | ok | 282 |
| 1000 | quiz | answer all 18 questions in q04 correctly | ok | 596 |
| 1001 | quiz | answer all 12 questions in q05 correctly | ok | 371 |
| 1002 | quiz | answer all 12 questions in q06 correctly | ok | 360 |
| 1003 | quiz | answer all 13 questions in q07 correctly | ok | 435 |
| 1004 | quiz | answer all 14 questions in q08 correctly | ok | 465 |
| 1005 | quiz | answer all 13 questions in q09 correctly | ok | 460 |
| 1006 | quiz | answer all 12 questions in q10 correctly | ok | 393 |
| 1007 | quiz | answer all 10 questions in q11 correctly | ok | 331 |
| 1008 | quiz | answer all 8 questions in q12 correctly | ok | 263 |
| 1009 | quiz | answer all 9 questions in q13 correctly | ok | 301 |
| 1010 | quiz | answer all 10 questions in q14 correctly | ok | 308 |
| 1011 | quiz | answer all 18 questions in q15 correctly | ok | 565 |
| 1012 | quiz | answer all 18 questions in q16 correctly | ok | 604 |
| 1013 | quiz | answer all 14 questions in q17 correctly | ok | 448 |
| 1014 | quiz | answer all 8 questions in q18 correctly | ok | 257 |
| 1015 | quiz | answer all 8 questions in q99 correctly | ok | 308 |
| 1016 | quiz | get every question in q00 wrong | ok | 413 |
| 1017 | quiz | read the wrap-up for q00 | ok | 0 |
| 1018 | quiz | get every question in q01 wrong | ok | 784 |
| 1019 | quiz | read the wrap-up for q01 | ok | 1 |
| 1020 | quiz | get every question in q02 wrong | ok | 500 |
| 1021 | quiz | read the wrap-up for q02 | ok | 0 |
| 1022 | quiz | get every question in q03 wrong | ok | 344 |
| 1023 | quiz | read the wrap-up for q03 | ok | 0 |
| 1024 | quiz | get every question in q04 wrong | ok | 707 |
| 1025 | quiz | read the wrap-up for q04 | ok | 0 |
| 1026 | quiz | get every question in q05 wrong | ok | 500 |
| 1027 | quiz | read the wrap-up for q05 | ok | 0 |
| 1028 | quiz | get every question in q06 wrong | ok | 492 |
| 1029 | quiz | read the wrap-up for q06 | ok | 0 |
| 1030 | quiz | get every question in q07 wrong | ok | 500 |
| 1031 | quiz | read the wrap-up for q07 | ok | 0 |
| 1032 | quiz | get every question in q08 wrong | ok | 593 |
| 1033 | quiz | read the wrap-up for q08 | ok | 0 |
| 1034 | quiz | get every question in q09 wrong | ok | 536 |
| 1035 | quiz | read the wrap-up for q09 | ok | 0 |
| 1036 | quiz | get every question in q10 wrong | ok | 502 |
| 1037 | quiz | read the wrap-up for q10 | ok | 0 |
| 1038 | quiz | get every question in q11 wrong | ok | 455 |
| 1039 | quiz | read the wrap-up for q11 | ok | 0 |
| 1040 | quiz | get every question in q12 wrong | ok | 350 |
| 1041 | quiz | read the wrap-up for q12 | ok | 0 |
| 1042 | quiz | get every question in q13 wrong | ok | 392 |
| 1043 | quiz | read the wrap-up for q13 | ok | 0 |
| 1044 | quiz | get every question in q14 wrong | ok | 421 |
| 1045 | quiz | read the wrap-up for q14 | ok | 0 |
| 1046 | quiz | get every question in q15 wrong | ok | 726 |
| 1047 | quiz | read the wrap-up for q15 | ok | 1 |
| 1048 | quiz | get every question in q16 wrong | ok | 731 |
| 1049 | quiz | read the wrap-up for q16 | ok | 0 |
| 1050 | quiz | get every question in q17 wrong | ok | 583 |
| 1051 | quiz | read the wrap-up for q17 | ok | 0 |
| 1052 | quiz | get every question in q18 wrong | ok | 313 |
| 1053 | quiz | read the wrap-up for q18 | ok | 0 |
| 1054 | quiz | get every question in q99 wrong | ok | 330 |
| 1055 | quiz | read the wrap-up for q99 | ok | 0 |
| 1056 | review | the wrong answers are waiting in review | ok | 3 |
| 1057 | quiz | skip every question without answering | ok | 324 |
| 1058 | quiz | retake it | ok | 32 |
| 1059 | quiz | go back to the picker | ok | 88 |
| 1060 | review | open Review with nothing started | ok | 0 |
| 1061 | review | answer card 1 of 15 | ok | 39 |
| 1062 | review | answer card 2 of 15 | ok | 37 |
| 1063 | review | answer card 3 of 15 | ok | 41 |
| 1064 | review | answer card 4 of 15 | ok | 39 |
| 1065 | review | answer card 5 of 15 | ok | 41 |
| 1066 | review | answer card 6 of 15 | ok | 43 |
| 1067 | review | answer card 7 of 15 | ok | 29 |
| 1068 | review | answer card 8 of 15 | ok | 39 |
| 1069 | review | answer card 9 of 15 | ok | 35 |
| 1070 | review | answer card 10 of 15 | ok | 33 |
| 1071 | review | answer card 11 of 15 | ok | 36 |
| 1072 | review | answer card 12 of 15 | ok | 31 |
| 1073 | review | answer card 13 of 15 | ok | 25 |
| 1074 | review | answer card 14 of 15 | ok | 37 |
| 1075 | review | answer card 15 of 15 | ok | 32 |
| 1076 | review | the session ends with a clear queue | ok | 0 |
| 1077 | review | skip the card in front of you | ok | 10 |
| 1078 | review | work to the daily limit | ok | 97 |
| 1079 | review | the idle screen explains the limit | ok | 0 |
| 1080 | review | open Review with a thousand cards due | ok | 33 |
| 1081 | projects | read all 22 project cards | ok | 1 |
| 1082 | projects | meet every requirement of pj.p00.1 | ok | 71 |
| 1083 | projects | meet every requirement of pj.p01.1 | ok | 60 |
| 1084 | projects | meet every requirement of pj.p01.2 | ok | 52 |
| 1085 | projects | meet every requirement of pj.p02.1 | ok | 53 |
| 1086 | projects | meet every requirement of pj.p02.2 | ok | 47 |
| 1087 | projects | meet every requirement of pj.p03.1 | ok | 52 |
| 1088 | projects | meet every requirement of pj.p04.1 | ok | 50 |
| 1089 | projects | meet every requirement of pj.p05.1 | ok | 54 |
| 1090 | projects | meet every requirement of pj.p06.1 | ok | 54 |
| 1091 | projects | meet every requirement of pj.p07.1 | ok | 59 |
| 1092 | projects | meet every requirement of pj.p08.1 | ok | 63 |
| 1093 | projects | meet every requirement of pj.p09.1 | ok | 66 |
| 1094 | projects | meet every requirement of pj.p10.1 | ok | 65 |
| 1095 | projects | meet every requirement of pj.p11.1 | ok | 63 |
| 1096 | projects | meet every requirement of pj.p12.1 | ok | 73 |
| 1097 | projects | meet every requirement of pj.p13.1 | ok | 66 |
| 1098 | projects | meet every requirement of pj.p14.1 | ok | 69 |
| 1099 | projects | meet every requirement of pj.p14.2 | ok | 60 |
| 1100 | projects | meet every requirement of pj.p15.1 | ok | 81 |
| 1101 | projects | meet every requirement of pj.p16.1 | ok | 63 |
| 1102 | projects | meet every requirement of pj.p17.1 | ok | 69 |
| 1103 | projects | meet every requirement of pj.p99.1 | ok | 79 |
| 1104 | projects | the meters agree once everything is met | ok | 22 |
| 1105 | projects | untick pj.p00.1 again | ok | 54 |
| 1106 | projects | untick pj.p01.1 again | ok | 69 |
| 1107 | projects | untick pj.p01.2 again | ok | 56 |
| 1108 | projects | untick pj.p02.1 again | ok | 71 |
| 1109 | projects | untick pj.p02.2 again | ok | 54 |
| 1110 | projects | untick pj.p03.1 again | ok | 60 |
| 1111 | projects | untick pj.p04.1 again | ok | 57 |
| 1112 | projects | untick pj.p05.1 again | ok | 69 |
| 1113 | projects | untick pj.p06.1 again | ok | 81 |
| 1114 | projects | untick pj.p07.1 again | ok | 63 |
| 1115 | projects | untick pj.p08.1 again | ok | 69 |
| 1116 | projects | untick pj.p09.1 again | ok | 70 |
| 1117 | projects | untick pj.p10.1 again | ok | 82 |
| 1118 | projects | untick pj.p11.1 again | ok | 83 |
| 1119 | projects | untick pj.p12.1 again | ok | 80 |
| 1120 | projects | untick pj.p13.1 again | ok | 64 |
| 1121 | projects | untick pj.p14.1 again | ok | 63 |
| 1122 | projects | untick pj.p14.2 again | ok | 53 |
| 1123 | projects | untick pj.p15.1 again | ok | 65 |
| 1124 | projects | untick pj.p16.1 again | ok | 58 |
| 1125 | projects | untick pj.p17.1 again | ok | 54 |
| 1126 | projects | untick pj.p99.1 again | ok | 51 |
| 1127 | projects | mark pj.p00.1 as Not started | ok | 37 |
| 1128 | projects | mark pj.p00.1 as In progress | ok | 6 |
| 1129 | projects | mark pj.p00.1 as Shipped | ok | 14 |
| 1130 | projects | mark pj.p01.1 as Not started | ok | 6 |
| 1131 | projects | mark pj.p01.1 as In progress | ok | 7 |
| 1132 | projects | mark pj.p01.1 as Shipped | ok | 11 |
| 1133 | projects | mark pj.p01.2 as Not started | ok | 6 |
| 1134 | projects | mark pj.p01.2 as In progress | ok | 7 |
| 1135 | projects | mark pj.p01.2 as Shipped | ok | 7 |
| 1136 | projects | mark pj.p02.1 as Not started | ok | 7 |
| 1137 | projects | mark pj.p02.1 as In progress | ok | 8 |
| 1138 | projects | mark pj.p02.1 as Shipped | ok | 8 |
| 1139 | projects | mark pj.p02.2 as Not started | ok | 7 |
| 1140 | projects | mark pj.p02.2 as In progress | ok | 7 |
| 1141 | projects | mark pj.p02.2 as Shipped | ok | 8 |
| 1142 | projects | mark pj.p03.1 as Not started | ok | 6 |
| 1143 | projects | mark pj.p03.1 as In progress | ok | 7 |
| 1144 | projects | mark pj.p03.1 as Shipped | ok | 10 |
| 1145 | projects | mark pj.p04.1 as Not started | ok | 7 |
| 1146 | projects | mark pj.p04.1 as In progress | ok | 7 |
| 1147 | projects | mark pj.p04.1 as Shipped | ok | 9 |
| 1148 | projects | mark pj.p05.1 as Not started | ok | 5 |
| 1149 | projects | mark pj.p05.1 as In progress | ok | 6 |
| 1150 | projects | mark pj.p05.1 as Shipped | ok | 8 |
| 1151 | projects | mark pj.p06.1 as Not started | ok | 5 |
| 1152 | projects | mark pj.p06.1 as In progress | ok | 7 |
| 1153 | projects | mark pj.p06.1 as Shipped | ok | 10 |
| 1154 | projects | mark pj.p07.1 as Not started | ok | 6 |
| 1155 | projects | mark pj.p07.1 as In progress | ok | 6 |
| 1156 | projects | mark pj.p07.1 as Shipped | ok | 8 |
| 1157 | projects | mark pj.p08.1 as Not started | ok | 6 |
| 1158 | projects | mark pj.p08.1 as In progress | ok | 6 |
| 1159 | projects | mark pj.p08.1 as Shipped | ok | 8 |
| 1160 | projects | mark pj.p09.1 as Not started | ok | 6 |
| 1161 | projects | mark pj.p09.1 as In progress | ok | 6 |
| 1162 | projects | mark pj.p09.1 as Shipped | ok | 7 |
| 1163 | projects | mark pj.p10.1 as Not started | ok | 5 |
| 1164 | projects | mark pj.p10.1 as In progress | ok | 6 |
| 1165 | projects | mark pj.p10.1 as Shipped | ok | 8 |
| 1166 | projects | mark pj.p11.1 as Not started | ok | 8 |
| 1167 | projects | mark pj.p11.1 as In progress | ok | 6 |
| 1168 | projects | mark pj.p11.1 as Shipped | ok | 7 |
| 1169 | projects | mark pj.p12.1 as Not started | ok | 6 |
| 1170 | projects | mark pj.p12.1 as In progress | ok | 6 |
| 1171 | projects | mark pj.p12.1 as Shipped | ok | 8 |
| 1172 | projects | mark pj.p13.1 as Not started | ok | 6 |
| 1173 | projects | mark pj.p13.1 as In progress | ok | 6 |
| 1174 | projects | mark pj.p13.1 as Shipped | ok | 9 |
| 1175 | projects | mark pj.p14.1 as Not started | ok | 6 |
| 1176 | projects | mark pj.p14.1 as In progress | ok | 6 |
| 1177 | projects | mark pj.p14.1 as Shipped | ok | 7 |
| 1178 | projects | mark pj.p14.2 as Not started | ok | 5 |
| 1179 | projects | mark pj.p14.2 as In progress | ok | 6 |
| 1180 | projects | mark pj.p14.2 as Shipped | ok | 9 |
| 1181 | projects | mark pj.p15.1 as Not started | ok | 5 |
| 1182 | projects | mark pj.p15.1 as In progress | ok | 5 |
| 1183 | projects | mark pj.p15.1 as Shipped | ok | 8 |
| 1184 | projects | mark pj.p16.1 as Not started | ok | 6 |
| 1185 | projects | mark pj.p16.1 as In progress | ok | 6 |
| 1186 | projects | mark pj.p16.1 as Shipped | ok | 7 |
| 1187 | projects | mark pj.p17.1 as Not started | ok | 6 |
| 1188 | projects | mark pj.p17.1 as In progress | ok | 6 |
| 1189 | projects | mark pj.p17.1 as Shipped | ok | 8 |
| 1190 | projects | mark pj.p99.1 as Not started | ok | 5 |
| 1191 | projects | mark pj.p99.1 as In progress | ok | 6 |
| 1192 | projects | mark pj.p99.1 as Shipped | ok | 7 |
| 1193 | projects | try each filter | ok | 259 |
| 1194 | projects | record a repo and some notes | ok | 505 |
| 1195 | projects | press Open next to the repo | ok | 1 |
| 1196 | projects | jump to the project's phase | ok | 132 |
| 1197 | projects | ship all 22 projects | ok | 203 |
| 1198 | today | Today agrees | ok | 50 |
| 1199 | projects | press a status button | 11 ms | 11 |
| 1200 | journal | write today's entry | ok | 23 |
| 1201 | journal | add three more days | ok | 90 |
| 1202 | journal | an entry is edited by writing it again | ok | 32 |
| 1203 | journal | delete every entry from the history | ok | 127 |
| 1204 | stats | the charts render with no data at all | ok | 4 |
| 1205 | stats | the charts render with one data point | ok | 128 |
| 1206 | stats | the charts render with a year of data | ok | 133 |
| 1207 | stats | rate every skill in the matrix | ok | 20 |
| 1208 | stats | the table covers the whole plan | ok | 119 |
| 1209 | library | open the Shelf tab | ok | 42 |
| 1210 | library | open the Fields of work tab | ok | 96 |
| 1211 | library | open the Video tab | ok | 70 |
| 1212 | library | open the Certificates tab | ok | 61 |
| 1213 | library | press every Open on the Shelf tab | ok | 8 |
| 1214 | library | press every Open on the Fields of work tab | ok | 0 |
| 1215 | library | press every Open on the Video tab | ok | 5 |
| 1216 | library | press every Open on the Certificates tab | ok | 0 |
| 1217 | library | press every field library button | ok | 58 |
| 1218 | library | cycle c-cs50p through every state | ok | 624 |
| 1219 | library | cycle c-helsinki through every state | ok | 634 |
| 1220 | library | cycle c-fcc-sci through every state | ok | 588 |
| 1221 | library | cycle c-netacad1 through every state | ok | 592 |
| 1222 | library | cycle c-netacad2 through every state | ok | 594 |
| 1223 | library | cycle c-pcep through every state | ok | 589 |
| 1224 | library | cycle c-pcap through every state | ok | 664 |
| 1225 | library | cycle c-hackerrank through every state | ok | 650 |
| 1226 | library | cycle c-kaggle through every state | ok | 596 |
| 1227 | library | cycle c-fcc-data through every state | ok | 561 |
| 1228 | library | cycle c-fcc-ml through every state | ok | 590 |
| 1229 | library | cycle c-hf-agents through every state | ok | 569 |
| 1230 | library | cycle c-hf-llm through every state | ok | 543 |
| 1231 | library | cycle c-hf-mcp through every state | ok | 581 |
| 1232 | library | cycle c-anthropic through every state | ok | 556 |
| 1233 | library | cycle c-google-ml through every state | ok | 580 |
| 1234 | library | cycle c-mit191 through every state | ok | 572 |
| 1235 | library | cycle c-cs50ai through every state | ok | 553 |
| 1236 | library | cycle c-cs50w through every state | ok | 609 |
| 1237 | library | cycle c-google-auto through every state | ok | 553 |
| 1238 | library | cycle c-py4e through every state | ok | 577 |
| 1239 | library | cycle c-mlzoom through every state | ok | 580 |
| 1240 | library | cycle c-dezoom through every state | ok | 559 |
| 1241 | library | cycle c-mit6001 through every state | ok | 563 |
| 1242 | settings | change your name | ok | 4 |
| 1243 | settings | try every track | ok | 47 |
| 1244 | settings | try every experience level | ok | 10 |
| 1245 | settings | tick and untick every goal | ok | 67 |
| 1246 | settings | push every number to both ends | ok | 38 |
| 1247 | settings | turn the update check off and on | ok | 6 |
| 1248 | settings | put every setting back | ok | 13 |
| 1249 | settings | switch the theme to Dark | ok | 437 |
| 1250 | settings | switch the theme to Light | ok | 386 |
| 1251 | settings | switch the theme to Match the system | ok | 3 |
| 1252 | settings | press Open folder | ok | 1 |
| 1253 | settings | export a backup | ok | 4 |
| 1254 | settings | export a progress report | ok | 16 |
| 1255 | settings | take a snapshot | ok | 9 |
| 1256 | settings | cancel an import | ok | 0 |
| 1257 | settings | import the backup back | ok | 0 |
| 1258 | settings | decline a reset | ok | 0 |
| 1259 | settings | accept a reset | ok | 0 |
| 1260 | settings | press Check now | ok | 1 |
| 1261 | search | open search with Ctrl+K | ok | 1 |
| 1262 | search | search for 'nothing' | ok | 0 |
| 1263 | search | search for 'd' | ok | 0 |
| 1264 | search | search for 'Python engineering' | ok | 9 |
| 1265 | search | search for 'Say hello' | ok | 4 |
| 1266 | search | search for 'zzzqqqxx nothing at all' | ok | 2 |
| 1267 | search | press Escape | ok | 6 |
| 1268 | search | press Enter on the first result | ok | 69 |
| 1269 | search | open a result of every kind | ok | 558 |
| 1270 | history | nothing to undo on a fresh store | ok | 0 |
| 1271 | history | tick a line, then undo and redo it | ok | 300 |
| 1272 | history | change a project status, then undo it | ok | 899 |
| 1273 | history | rate a skill, then undo it | ok | 234 |
| 1274 | history | cycle a certificate, then undo it | ok | 1232 |
| 1275 | history | undo and redo from the keyboard | ok | 706 |
| 1276 | history | a new change drops the redo branch | ok | 180 |
| 1277 | history | reopen the app and look for the undo | ok | 0 |
| 1278 | history | the tick survived, the undo did not | ok | 0 |
| 1279 | updates | the button is hidden until there is one | ok | 0 |
| 1280 | updates | a release makes the button appear | ok | 1 |
| 1281 | updates | press it for a release with no changelog | ok | 0 |
| 1282 | updates | press it for a release with a changelog | ok | 6 |
| 1283 | updates | a release with nothing for this platform | ok | 2 |
| 1284 | updates | Help > Check for updates | ok | 1 |
| 1285 | restart | reopen the app on the same store | ok | 0 |
| 1286 | restart | the position is remembered | ok | 0 |
| 1287 | restart | quit inside the autosave window | ok | 3022 |
| 1288 | history | Ctrl+Z undoes a tick | ok | 145 |
| 1289 | history | the advertised redo keys | ok | 125 |
| 1290 | history | the Redo button still works | ok | 0 |
| 1291 | today | Today at 800x600 | ok | 0 |
| 1292 | roadmap | Roadmap at 800x600 | ok | 0 |
| 1293 | phase | Phase at 800x600 | ok | 0 |
| 1294 | practice | Practice at 800x600 | ok | 0 |
| 1295 | quiz | Quizzes at 800x600 | ok | 0 |
| 1296 | review | Review at 800x600 | ok | 0 |
| 1297 | projects | Projects at 800x600 | ok | 3 |
| 1298 | journal | Log at 800x600 | ok | 0 |
| 1299 | stats | Progress at 800x600 | ok | 0 |
| 1300 | library | Library at 800x600 | ok | 1 |
| 1301 | settings | Settings at 800x600 | ok | 0 |
| 1302 | today | Today at 1280x900 | ok | 0 |
| 1303 | roadmap | Roadmap at 1280x900 | ok | 0 |
| 1304 | phase | Phase at 1280x900 | ok | 1 |
| 1305 | practice | Practice at 1280x900 | ok | 0 |
| 1306 | quiz | Quizzes at 1280x900 | ok | 0 |
| 1307 | review | Review at 1280x900 | ok | 0 |
| 1308 | projects | Projects at 1280x900 | ok | 4 |
| 1309 | journal | Log at 1280x900 | ok | 0 |
| 1310 | stats | Progress at 1280x900 | ok | 1 |
| 1311 | library | Library at 1280x900 | ok | 2 |
| 1312 | settings | Settings at 1280x900 | ok | 0 |
| 1313 | today | Today at 2560x1440 | ok | 0 |
| 1314 | roadmap | Roadmap at 2560x1440 | ok | 0 |
| 1315 | phase | Phase at 2560x1440 | ok | 0 |
| 1316 | practice | Practice at 2560x1440 | ok | 0 |
| 1317 | quiz | Quizzes at 2560x1440 | ok | 0 |
| 1318 | review | Review at 2560x1440 | ok | 0 |
| 1319 | projects | Projects at 2560x1440 | ok | 3 |
| 1320 | journal | Log at 2560x1440 | ok | 0 |
| 1321 | stats | Progress at 2560x1440 | ok | 0 |
| 1322 | library | Library at 2560x1440 | ok | 1 |
| 1323 | settings | Settings at 2560x1440 | ok | 0 |
| 1324 | layout | the window refuses to go below its minimum | ok | 0 |
| 1325 | layout | the sidebar keeps every page button | ok | 0 |
| 1326 | today | tab through the today page | ok | 49 |
| 1327 | today | the focused control is the one you can see | ok | 0 |
| 1328 | practice | tab through the practice page | ok | 72 |
| 1329 | practice | the focused control is the one you can see | ok | 0 |
| 1330 | phase | tick a line with the space bar | ok | 14 |
| 1331 | practice | Ctrl+Enter in the editor runs the code | ok | 164 |
| 1332 | settings | type 2,5 hours in a German locale | ok | 5 |
| 1333 | settings | type it by hand as 3,5 | ok | 3 |
| 1334 | today | the pace line still reads sensibly | ok | 37 |
| 1335 | library | open library with nothing to show | ok | 13 |
| 1336 | stats | open stats with nothing to show | ok | 36 |
| 1337 | projects | open projects with nothing to show | ok | 11 |
| 1338 | today | open today with nothing to show | ok | 33 |
| 1339 | roadmap | open roadmap with nothing to show | ok | 112 |
| 1340 | navigation | switch pages 200 times | ok | 1889 |
| 1341 | today | reopen the Today page | 1 ms | 1 |
| 1342 | roadmap | reopen the Roadmap page | 15 ms | 15 |
| 1343 | phase | reopen the Phase page | 10 ms | 10 |
| 1344 | practice | reopen the Practice page | 17 ms | 17 |
| 1345 | quiz | reopen the Quizzes page | 9 ms | 9 |
| 1346 | review | reopen the Review page | 7 ms | 7 |
| 1347 | projects | reopen the Projects page | 13 ms | 13 |
| 1348 | journal | reopen the Log page | 8 ms | 8 |
| 1349 | stats | reopen the Progress page | 9 ms | 9 |
| 1350 | library | reopen the Library page | 18 ms | 18 |
| 1351 | settings | reopen the Settings page | 11 ms | 11 |
| 1352 | screenshots | grab every page on both themes | ok | 10123 |
| 1353 | screenshots | practice page after a passing run | results panel hidden: False; rows rendered into it: 4; hint label hidden: True;  | 0 |
| 1354 | help | press F1 and close the shortcut list | ok | 19 |
| 1355 | menu | press Ctrl+, for Settings | ok | 66 |
| 1356 | settings | open the snapshot list and cancel | ok | 22 |
| 1357 | settings | restore the snapshot just taken | ok | 68 |
| 1358 | onboarding | Continue, Continue, Back | ok | 21 |
| 1359 | update | press Update and restart while offline | ok | 11 |
| 1360 | quiz | finish a quiz and go back to its phase | ok | 480 |
| 1361 | quiz | finish a quiz and pick another | ok | 415 |
| 1362 | review | skip to a concept card, reveal, rate | ok | 52 |
| 1363 | practice | press Next | ok | 16 |
| 1364 | phase | open the first resource | ok | 10 |
| 1365 | library | press every button on tab 0 | ok | 505 |
| 1366 | library | press every button on tab 1 | ok | 570 |
| 1367 | library | press every button on tab 2 | ok | 412 |
| 1368 | library | press every button on tab 3 | ok | 246 |
| 1369 | projects | open the repo link | ok | 53 |
| 1370 | projects | press every status button | ok | 203 |
| 1371 | journal | the history opens on the newest sixty | ok | 0 |
| 1372 | journal | press Show older for the next sixty | ok | 306 |
| 1373 | journal | press Show older for the last ten | ok | 62 |
| 1374 | journal | find one entry among a hundred | ok | 158 |
| 1375 | journal | a filter that matches nothing says so | ok | 279 |
| 1376 | journal | narrow the range, then widen it again | ok | 869 |
| 1377 | journal | load an old entry back into the form | ok | 23 |
| 1378 | journal | save the correction | ok | 37 |
| 1379 | journal | take the correction back with Ctrl+Z | ok | 20 |
| 1380 | journal | and put it back with Ctrl+Y | ok | 22 |
| 1381 | journal | start an edit and cancel out of it | ok | 36 |
| 1382 | journal | delete an entry by mistake | ok | 16 |
| 1383 | journal | Ctrl+Z brings the whole entry back | ok | 19 |
| 1384 | journal | Ctrl+Y deletes it again | ok | 13 |
| 1385 | journal | log today for the first time | ok | 20 |
| 1386 | journal | the form warns before the day stacks | ok | 0 |
| 1387 | journal | log today again anyway | ok | 17 |
| 1388 | journal | every note written is listed here | ok | 0 |
| 1389 | journal | the filter searches the notes too | ok | 38 |
| 1390 | journal | open note 0 from the log | ok | 156 |
| 1391 | journal | open note 1 from the log | ok | 183 |
| 1392 | journal | open note 2 from the log | ok | 148 |
| 1393 | journal | open note 3 from the log | ok | 122 |
| 1394 | journal | open note 4 from the log | ok | 963 |
| 1395 | journal | open note 5 from the log | ok | 40 |
| 1396 | journal | open note 6 from the log | ok | 42 |
| 1397 | journal | the notes section with nothing in it | ok | 0 |
| 1398 | practice | submit an empty editor and read the reasons | ok | 248 |
| 1399 | practice | put the real answer back | ok | 236 |
| 1400 | practice | forget the exclamation mark and run | ok | 262 |
| 1401 | practice | get one character wrong instead | ok | 214 |
| 1402 | practice | get only the capital wrong | ok | 293 |
| 1403 | practice | start an endless run and press Stop | ok | 355 |
| 1404 | practice | read every hint, then press once more | ok | 38 |
| 1405 | practice | search for one exercise by its title | ok | 10 |
| 1406 | practice | search for something that is not there | ok | 15 |
| 1407 | practice | clear the search | ok | 21 |
| 1408 | practice | filter by every difficulty | ok | 98 |
| 1409 | practice | show only the revealed ones | ok | 37 |
| 1410 | practice | walk to the last exercise and press Next again | ok | 48 |
| 1411 | practice | pass the exercise | ok | 246 |
| 1412 | practice | carry on experimenting and break it | ok | 13 |
| 1413 | practice | press Restore my passing version | ok | 8 |
| 1414 | practice | press Reset, then restore once more | ok | 54 |
| 1415 | practice | read the answer | ok | 14 |
| 1416 | practice | check the list says so too | ok | 0 |
| 1417 | practice | press Try this one again from scratch | ok | 15 |
| 1418 | review | press Space to reveal the saved line | ok | 16 |
| 1419 | review | press 3 to rate it Good | ok | 17 |
| 1420 | review | pick a multiple choice option by letter | ok | 1 |
| 1421 | review | press Enter to check it | ok | 10 |
| 1422 | review | press 4 for Easy | ok | 17 |
| 1423 | review | answer with the Again key | ok | 50 |
| 1424 | review | answer with the Hard key | ok | 30 |
| 1425 | review | answer with the Good key | ok | 33 |
| 1426 | review | answer with the Easy key | ok | 36 |
| 1427 | review | type in the search box with a card open | ok | 2 |
| 1428 | review | bury the card in front of you | ok | 27 |
| 1429 | review | the summary offers the buried card back | ok | 69 |
| 1430 | review | answer one card, then take it back | ok | 86 |
| 1431 | review | Ctrl+Z takes the next one back too | ok | 59 |
| 1432 | review | skip the same card twice | ok | 32 |
| 1433 | phase | open a line's menu with the ... button | ok | 14 |
| 1434 | phase | open the same menu with Shift+F10 | ok | 8 |
| 1435 | phase | the Menu key offers to take it out again | ok | 3 |
| 1436 | search | open the box with Ctrl+K | ok | 13 |
| 1437 | search | find a phase note written minutes ago | ok | 103 |
| 1438 | search | find your own project note | ok | 65 |
| 1439 | search | find a project by its repository url | ok | 5 |
| 1440 | search | find a log entry and open the log | ok | 28 |
| 1441 | search | type a query | ok | 32 |
| 1442 | search | walk down and back up the results | ok | 6 |
| 1443 | search | page down and page up the results | ok | 4 |
| 1444 | search | open the selected hit with Enter | ok | 134 |
| 1445 | search | close the results with Escape | ok | 8 |
| 1446 | library | open the field f-web from search | ok | 64 |
| 1447 | library | open the cert c-cs50p from search | ok | 110 |
| 1448 | search | open a question from search | ok | 5 |
| 1449 | search | read the question and close it | ok | 15 |
| 1450 | library | filter the library to nothing | ok | 30 |
| 1451 | library | filter the library to one shelf entry | ok | 117 |
| 1452 | library | mark a row on tab 0 as read | ok | 12 |
| 1453 | library | take the mark on tab 0 back | ok | 5 |
| 1454 | library | mark a row on tab 1 as read | ok | 97 |
| 1455 | library | take the mark on tab 1 back | ok | 5 |
| 1456 | library | mark a row on tab 2 as read | ok | 66 |
| 1457 | library | take the mark on tab 2 back | ok | 4 |
| 1458 | library | undo the last read mark | ok | 176 |
| 1459 | navigation | press Ctrl+0 | ok | 34 |
| 1460 | navigation | press Ctrl+L | ok | 30 |
| 1461 | navigation | open the library from the Go menu | ok | 46 |
| 1462 | first run | read the status bar on a first launch | ok | 0 |
| 1463 | onboarding | type a name and continue | ok | 13 |
| 1464 | onboarding | choose an experience card | ok | 11 |
| 1465 | onboarding | tick two goals | ok | 10 |
| 1466 | onboarding | go back a step and forward again | ok | 9 |
| 1467 | onboarding | set a pace and build the plan | ok | 46 |
| 1468 | onboarding | skip the whole thing | ok | 3 |
| 1469 | settings | press Run setup again | ok | 25 |
| 1470 | quiz | start one and skip a question | ok | 63 |
| 1471 | quiz | move on to the next question | ok | 18 |
| 1472 | quiz | think better of leaving | ok | 1 |
| 1473 | quiz | leave the quiz | ok | 108 |
| 1474 | quiz | close the app in the middle of one | ok | 113 |
| 1475 | quiz | resume where it was left | ok | 26 |
| 1476 | quiz | start it over instead | ok | 112 |
| 1477 | settings | nothing has left this machine yet | ok | 0 |
| 1478 | settings | choose a second copy folder | ok | 5 |
| 1479 | settings | copy everything there now | ok | 14 |
| 1480 | settings | import a backup and read the summary | ok | 31 |
| 1481 | projects | press Open with nothing to open | ok | 1 |
| 1482 | projects | type a repo address | ok | 1 |
| 1483 | projects | replace it with a note to self | ok | 1 |
| 1484 | today | read the note above the list | ok | 35 |
| 1485 | today | push the first item off until tomorrow | ok | 67 |
| 1486 | today | push a second one off from a compact row | ok | 31 |
| 1487 | today | find the way back to what was hidden | ok | 61 |
| 1488 | today | yesterday's 'first thing tomorrow' returns | ok | 93 |
| 1489 | today | push everything off for a quiet evening | ok | 37 |
| 1490 | today | finish the entire curriculum | ok | 265 |
| 1491 | today | read what the finished plan says | ok | 0 |
| 1492 | today | keep reviewing from the hero | ok | 76 |
| 1493 | today | change track from the hero | ok | 59 |
| 1494 | today | export the report from the hero | ok | 93 |
| 1495 | roadmap | the marker is there while work remains | ok | 0 |
| 1496 | roadmap | and is gone once there is nowhere to go | ok | 0 |
| 1497 | stats | click a phase row | ok | 205 |
| 1498 | stats | select a row and press Enter | ok | 94 |
| 1499 | stats | hover the quiz column for the trend | ok | 0 |
| 1500 | phase | the way into the review deck is announced | ok | 0 |
| 1501 | phase | write a long note into the box | ok | 11 |
| 1502 | phase | and it shrinks back for a short one | ok | 11 |
| 1503 | search | type a word that is nowhere | ok | 18 |
| 1504 | search | Escape, then Ctrl+K again | ok | 14 |
| 1505 | search | open a shelf book from Ctrl+K | ok | 127 |
| 1506 | library | filter for a channel on the Shelf tab | ok | 97 |
| 1507 | library | follow the count to the Video tab | ok | 11 |
| 1508 | library | clear the filter | ok | 259 |
| 1509 | projects | SHOW Shipped with nothing shipped | ok | 10 |
| 1510 | projects | press Show every project | ok | 256 |
| 1511 | projects | type in FIND | ok | 279 |
| 1512 | stats | click the Checks heading | ok | 2 |
| 1513 | stats | pick every SORT choice | ok | 9 |
| 1514 | practice | fail a run, then Where this is taught | ok | 253 |
| 1515 | settings | set filters, then change the theme | ok | 3532 |
| 1516 | settings | come back to each page | ok | 5897 |
| 1517 | quiz | read the picker and its counter | ok | 0 |
| 1518 | quiz | type into FIND | ok | 53 |
| 1519 | quiz | a search that matches nothing | ok | 110 |
| 1520 | quiz | SHOW each status in turn | ok | 285 |
| 1521 | quiz | start a quiz from the filtered list | ok | 121 |
| 1522 | quiz | press the second choice every time | ok | 912 |
| 1523 | review | pick a wrong option by its letter | ok | 30 |
| 1524 | review | press Where this is taught | ok | 149 |
| 1525 | review | press Next card | ok | 26 |
| 1526 | review | a second wrong answer, left with Space | ok | 33 |
| 1527 | review | reveal a gate check | ok | 15 |
| 1528 | review | rate it Good | ok | 26 |
| 1529 | phase | a phase read to the end | ok | 133 |
| 1530 | roadmap | the roadmap says read, not proven | ok | 176 |
| 1531 | phase | the same phase, proven | ok | 125 |
| 1532 | today | an earlier phase is mixed into today | ok | 87 |
| 1533 | quiz | start a quiz from the picker | ok | 25 |
| 1534 | quiz | leave and start a different one | ok | 124 |
| 1535 | review | press Check for more | ok | 11 |
| 1536 | updates | open the update dialog and decline | ok | 5 |
| 1537 | updates | open the releases page instead | ok | 5 |
| 1538 | menu | File > Quit | ok | 6 |
| 1539 | menu | File > Export backup... | ok | 78 |
| 1540 | menu | File > Export progress report... | ok | 9 |
| 1541 | menu | File > Take a snapshot | ok | 9 |
| 1542 | menu | File > Restore a snapshot... | ok | 14 |
| 1543 | menu | Go > Today | ok | 43 |
| 1544 | menu | Go > Roadmap | ok | 119 |
| 1545 | menu | Go > Phase | ok | 165 |
| 1546 | menu | Go > Practice | ok | 72 |
| 1547 | menu | Go > Quizzes | ok | 94 |
| 1548 | menu | Go > Review | ok | 27 |
| 1549 | menu | Go > Projects | ok | 891 |
| 1550 | menu | Go > Log | ok | 32 |
| 1551 | menu | Go > Progress | ok | 111 |
| 1552 | menu | Go > Library | ok | 1048 |
| 1553 | menu | Go > Settings | ok | 35 |
| 1554 | menu | Go > Find | ok | 7 |
| 1555 | menu | Edit > Undo | ok | 0 |
| 1556 | menu | Edit > Redo | ok | 0 |
| 1557 | menu | Help > How this app works | ok | 0 |
| 1558 | menu | Help > Keyboard shortcuts | ok | 7 |
| 1559 | menu | Help > Check for updates | ok | 0 |
| 1560 | menu | Help > About | ok | 0 |
| 1561 | menu | every navigation shortcut | ok | 674 |
