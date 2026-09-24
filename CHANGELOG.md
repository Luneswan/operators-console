# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-09-24

### Added

- **14 specialization phases** (S1-S14), one per career pathway: data
  analysis and visualization, desktop and mobile apps, command-line tools,
  games and media, scientific computing, quantitative finance, computer
  vision, NLP, testing and quality engineering, network automation,
  embedded and IoT, security engineering, bots and integrations, and
  blockchain tooling. Each has a checklist, a gate, a reading list, an
  8-question quiz, 3 graded exercises and a project. The course is now
  35 phases, 34 quizzes (354 questions), 161 exercises and 36 projects.
- **21 goals and 16 tracks.** New tracks: desktop apps and tools, games,
  scientific computing, quantitative finance, test automation, network
  automation, embedded. Every track ends with architecture, beyond senior
  and the final-boss ladder.
- **Goal-driven plan.** Phase prerequisites are a dependency graph. The
  roadmap places each phase after what it needs, puts a chosen
  specialization right after its prerequisites, and adds any prerequisite
  your track lacks, with the reason shown.
- **Career ladder**: Starting out, Beginner, Junior, Mid-level, Senior,
  Senior+. Levels come from proven phases, not ticked lines. Shown on
  Today and Progress; a new level is announced once.
- **Profiles.** Several people can share the app, each with separate
  progress, settings, review deck and snapshots. File -> Switch profile and
  Settings -> Profiles create, switch, rename and remove them. Switching
  reopens the window in the same process. Removed profiles are moved to
  `removed-profiles/`, never deleted. The main profile keeps the existing
  data folder, so nothing moves on upgrade.
- **Report or request.** Settings and Help open a form for bugs, feature
  requests and course mistakes. It opens a prefilled GitHub issue for you
  to submit, or copies the text. The app sends nothing.

### Changed

- The update check, its downloads and the single-instance lock use the
  root data folder, shared by all profiles.
- "Not in your plan" on the roadmap is folded by default.

### Fixed

- `install.ps1` refused every install on Windows PowerShell 5.1 with "This
  release does not publish a SHA256SUMS file". GitHub serves the file as
  `application/octet-stream`, and 5.1 returns that as bytes, so no line
  matched. The script now decodes it. A checksum file without an entry for
  the download now gets its own error message. The script is fetched from
  `main`, so the fix applies without a new release.

## [1.1.3] - 2026-09-24

### Changed

- **Plain wording throughout.** About 200 strings in the app were rewritten to
  be direct: page text, dialogs, tooltips, status messages, onboarding,
  grader explanations and error explanations. Slogans and justifications are
  gone ("Watching is not learning", "a receipt for time spent", "The first one
  is the hardest"). Page kickers are plain labels (preferences, statistics,
  graded exercises). The same pass covers the phase aims and gate notes, field
  and certificate notes, track descriptions, project "why" lines, the 72 phase
  01 hints and six exercise prompts.
- Section headings are plain: Gate, Stretch goals, Rubric, Project idea.
- Ten checklist lines lost their flourishes ("never string-concatenate a path
  again", "the WHERE clause that saves you"). Their ids are unchanged, so no
  ticks move.
- README rewritten as a technical reference: contents, features with exact
  limits and defaults, install, updating, data, keyboard, development, code
  layout and content sources.
- Onboarding no longer says the update check runs every 30 minutes.

## [1.1.2] - 2026-09-23

### Quizzes

- **A countdown on every question**, sized to how much there is to read
  (25 to 55 seconds across the bank). It turns amber for the last ten seconds.
  An answer given after it runs out is still marked and explained but earns no
  mark, and a right-but-late answer is scheduled as Hard. Running out of time
  survives closing the app.
- **Every attempt is laid out anew**: the question order, the first question
  and the letter each right answer sits under are never the same as the last
  attempt. Choices are lettered A-D. Review cards follow the same rule, and a
  review session is shuffled too, with new cards still taking turns by kind.
- **Results that tell you what to study.** A score card (verdict, percentage,
  best before, right / wrong / skipped / late, answering time in plain words
  instead of "279 minutes 25 seconds"). Then *What to study*: the exact
  checklist lines that teach what you missed, grouped by phase and section in
  course order, each with an *Open this line* button, plus an unpassed exercise
  and the phase's first reading for each phase. Then *Question by question*:
  what you chose, the right answer, why yours is not it, the explanation, and
  a link to the line. *Practise the N you missed* reruns just those,
  reshuffled, without recording a score.
- All 242 questions now name the line that teaches them (121 were unmapped;
  `build_tools/quiz_teaches.json`, validated by the build).
- Code in questions and explanations is shown as code, not as backticks.
- Quizzes take the same keys as Review: A to D picks the answer drawn at that
  letter, Enter checks it and Enter again moves on.
- The status bar says the score when a quiz ends, instead of leaving "Time's
  up" from the last question on screen.

### Practice

- **Every exercise says how it is checked** and shows worked examples taken
  from its own checks (`greet('Ada') -> 'Hello, Ada!'`), so it is clear the
  checks call your function for you.
- **Errors raised while your file loads are explained in plain words** - a
  bare word without quotes, a parameter used outside its function, a capital
  letter, a missing colon or bracket - and a call you added at the bottom is
  named as the reason no check ran.
- **Hints are a ladder**, rendered with code formatting, ending in *the shape
  of an answer*: the solution's structure with every expression removed. The
  36 phase 01 exercises have rewritten beginner hints in plain words.

## [1.1.1] - 2026-09-23

### Changed

- **Main and optional are decided, not assumed.** Four checklist sections are
  stretch work rather than the phase itself: p05 *Challenge ladder*, p18
  *Leverage* and *Staying current after 2027*, and p99 *Portfolio target*.
  They fold behind an OPTIONAL pill, stay checkable, and no longer count
  toward progress, so a twelve-month portfolio target cannot hold the final
  phase back. Every other section, the week-by-week work included, is main.
  Decided at the source (`OPTIONAL_SECTIONS` in `build_tools/transform.py`);
  item ids are unchanged, so no one's ticks move.
- Better first picks in three reading lists: NeetCode for algorithms (grouped
  by the same techniques the phase teaches), CS50 week 4 for systems
  programming (the phase starts with C and memory), and Build your own X for
  the final ladder (free, and it covers the first three bosses).
- **New releases appear within minutes.** The app looks at every launch (not
  once a day), every five minutes while open, and when you switch back to it.
  It sends GitHub the last ETag, so an unchanged answer is a `304` that does
  not count against the rate limit.

### Fixed

- Checklist lines no longer shift when the mouse passes over them. The `...`
  handle, built on first hover, was taller than a line of text, so the row
  grew and its centred text dropped below the checkbox. The handle is now one
  line tall and the text sits level with its box.

## [1.1.0] - 2026-09-23

### Why 1.1.0

A minor release, not a major one, because nothing you already have has to
change: the progress database is still **schema version 1**, and a 1.1.0 install
opens a 1.0.x file as it is, with no conversion step. A minor release, not a
patch, because every page gained features and the update mechanism changed
shape.

One caveat. New columns were added inside schema version 1, so a 1.0.x build can
still open a database that 1.1.0 has used, and it will silently ignore what it
does not know about. Do not run the old version and the new one side by side on
the same data folder. From 1.1.0 the app refuses to: a second copy hands over to
the one already open.

### Updating from 1.0.x

- **In-app updates now work from an installed 1.0.x build on Windows.** Before,
  the 1.0.x updater ran the new installer from the executable it was trying to
  replace; the installer could not close it and gave up (exit code 5), and the
  old version reopened. Its own `update.log` shows exactly that. The 1.1.0
  installer closes whatever holds the program's files and reopens the new
  version itself. This was proven on real 1.0.x installs with
  `packaging/windows/check_old_build_update.py`. If the old version ever reopens
  after updating, close it and run `...-windows-setup.exe` once.
- **1.0.x portable Windows builds are told there is no download, on purpose.**
  Their updater damaged the folder it was running from. The 1.1.0 portable zip
  is named `...-windows-x64-portable.zip`, which those builds do not look for.
  Download it by hand, or run the one-line installer with `-Portable`.

### Added

- **Progress you have to prove.** A phase now counts as finished when its gate
  is ticked, its quiz is passed at 85% or better, at least 60% of its exercises
  pass, and a project is shipped where the phase has one. Ticked lines are shown
  as reading progress, separately. The "you are here" marker, Today's plan and
  the roadmap all follow the proven state, and each phase says in plain words
  what is still missing.
- **Gate checks as recall cards**, so the "do this from memory" lines at the end
  of each phase come back for review instead of being read once.
- **Quizzes that teach when you are wrong.** The question bank was rebalanced so
  the right answer is no longer usually in the same place, wrong choices carry
  their own explanation of why they are wrong, and new questions were added.
- **New graded exercises**, each with its reference solution checked by the
  build.
- **A reason for every failed check.** Instead of "Wrong result", the grader
  shows the value you returned, the value expected, and what differs: wrong
  type, wrong length, the index or key that differs, a case-only or
  whitespace-only difference, floats that are close but unequal. Errors keep
  their message and add a hint for the common ones.
- **Snapshots you can restore.** One is taken automatically each day, five
  seconds after launch, and before every reset, import or upgrade. Settings and
  the File menu list them with their date, reason and contents; restoring one
  takes a snapshot of the current state first, so a restore can be undone too.
- **Filters and search where lists got long.** Practice filters by text,
  difficulty and status, including "solved after reading". The Log filters by
  text and date range and pages through older entries. The Library has a filter
  and read marks. Search now covers your own notes, project notes, repository
  links and log entries, and ranks them above curriculum lines.
- **Practice:** stop a running exercise; the last passing code is kept and can be
  restored; Reset is one undoable edit; `Ctrl+/` comments or uncomments the
  selected lines.
- **Review:** keyboard keys for every action (Space or Enter, A to D, 1 to 4, S),
  bury a card and restore it, and undo the rating you just gave.
- **Log:** edit an entry, and delete one with undo.
- **Today:** a finished-curriculum state, "Not today" per row, and a line that
  says how much of today's goal is logged.
- **Updates found while the app is open.** The check runs shortly after launch
  and every 30 minutes, and the first-run setup asks before it is turned on.
- **Help > Keyboard shortcuts (`F1`)**, built from the live menus, plus
  `Ctrl+,` for Settings and `Ctrl+0` or `Ctrl+L` for the Library.
- The window remembers its size, position and maximised state.
- `CHANGELOG.md` (this file), and a `SHA256SUMS` manifest in every release.

### Changed

- **One copy of the app per data folder.** Starting it again brings the open
  window forward. Two copies started at the same moment, such as the installer
  and a 1.0.x updater both reopening the app after an update, settle it between
  them through a lock file: one opens, the other hands over.
- **The interface was redesigned**, in light and dark: a new colour system with
  measured contrast, a sidebar with icons and sections, a Today page with a
  progress ring, and a roadmap drawn as a timeline. Keyboard focus rings appear
  only when you use the keyboard.
- **Undo now covers everything one careless click can change:** ticked lines,
  project status, certificate status, self-assessment ratings, log entries you
  added, edited or deleted, a review rating, and a card you buried.
- Onboarding was rebuilt as four clear steps that keep your earlier answers when
  you run it again.
- An in-app update reopens the page you were on.
- Page switches, the Projects page and theme changes are much faster.
- Optional study resources show the single best one, with the rest folded under
  "N more to study".

### Fixed

- The installed build's in-app update could never succeed: the updater ran
  from the folder the installer had to overwrite. It now runs from a copy.
- A failed or refused update reopened the old version with no word; it now says
  why, once.
- A failed update no longer leaves its download in your data folder; old
  packages, unfinished downloads and their checksum files are cleared.
- Settings "not saved": two copies of the app were open on one database and the
  older one overwrote the newer one's settings.
- Stray blank windows flashing while pages opened.
- Quiz and Review counted a second press of Check.
- Practice hid the result and the hint straight after a run.
- Reset destroyed the learner's code with no way back.
- Redo was bound twice to `Ctrl+Y`, so neither key worked.
- A damaged database stayed locked after the app failed to open it.
- Several grader cases: correct code marked unreadable when something printed
  after the answer, a learner's own `json.py` breaking later runs, and a long
  traceback reported as an endless loop.

### Security

- Every download is checked against the release's `SHA256SUMS` before it is
  installed, by the in-app updater and by both one-line installers, which
  refuse a release that publishes no checksums. Redirects off HTTPS are refused.
- The release workflow refuses to publish when an expected file is missing,
  when the tag does not match `version.py`, or when a file carries a name that
  1.0.x portable builds would pick up.

## [1.0.2]

- Global undo and redo.

## [1.0.1]

- In-app updates, and the desktop shortcut is always created.

## [1.0.0]

- First release, with builds for Windows, macOS (Apple silicon and Intel) and
  Linux, and the one-line installers.

[1.1.0]: https://github.com/Luneswan/operators-console/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/Luneswan/operators-console/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Luneswan/operators-console/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Luneswan/operators-console/releases/tag/v1.0.0
