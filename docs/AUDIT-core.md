# Audit: core, updates, installers

An adversarial review of everything below the interface: the store, the
scheduler, the position marker and the daily plan, the exercise grader, the
in-app updater, the two one-line installers and the release workflow.

Every finding below was reproduced before it was fixed. "Evidence" is the
observed behaviour, not an argument about the code. Findings marked **left**
are real and deliberately not changed; the reason is given.

Line numbers refer to the code as it was at commit `7ad8750` ("Add global
undo and redo").

---

## Findings

| id | severity | where | evidence | fix / left |
|----|----------|-------|----------|------------|
| **U1** | critical | `core/updates.py:192` `download()` | The downloaded package was checked for length and nothing else. A 100-byte file of attacker bytes, served in place of a 100-byte installer, was accepted and then executed by `_apply_windows_installer`. Reproduced: `download()` returned a file containing `MZ\x00...` with no complaint. | **fixed** - every release now publishes `SHA256SUMS`; `fetch_latest` stamps each asset with its digest, `download()` writes to a `.part` and only moves it into place once the hash matches, and the helper checks it again before applying. |
| **U2** | critical | `core/updates.py:75` `_request()` | Asset URLs come from the release JSON and were passed to `urlopen` unchecked. A payload naming `http://attacker.example/evil-setup.exe` was parsed, selected by `pick_asset`, reported as newer, and would have been downloaded over plain HTTP and run. `file://` likewise. urllib also follows an https -> http redirect by default. | **fixed** - `secure_url()` refuses anything but `https` with a host, and `_HttpsOnlyRedirects` refuses a redirect that leaves HTTPS while still allowing GitHub's CDN hop. |
| **U3** | high | `core/updates.py:291` `apply_update()` | The application quits, then the helper starts and executes the staged package. Nothing re-checked the file in between - the exact window in which a staged installer could be swapped. | **fixed** - the digest travels with the handover (`--sha256`, plus a sidecar beside the package) and the helper verifies immediately before it acts. A mismatch deletes the package, restarts the old build and exits 2. |
| **U4** | high | `core/updates.py:367` `_apply_archive()` | The swap deleted each destination and then moved the new file in. An error part way through left the application half old and half new, with no way back; `_restart` would then launch whatever was left. | **fixed** - the old build is moved aside into `.opcon-previous`, the new one moved in, the result checked for completeness, and any failure restores every file that was moved. `_apply_appimage` and `_apply_macos_dmg` keep the previous build the same way. |
| **U5** | high | `.github/workflows/build.yml:122` | `softprops/action-gh-release` uploaded `artifacts/*` with no checksum file, so there was nothing for an installer to verify against. | **fixed** - a step runs `sha256sum -- *` over the merged artefact folder and publishes `SHA256SUMS` with the release. |
| **U6** | high | `install.ps1:60`, `install.sh:75,114` | `Invoke-WebRequest` / `curl -fL` fetched the asset and ran it (`Start-Process`, `chmod +x`) with no verification and no scheme pinning. `irm ... \| iex` executes whatever is on `main`. | **fixed** - both fetch `SHA256SUMS` from the same release *before* the asset, refuse a release that has none (unless `-SkipVerify` / `OPCON_SKIP_VERIFY=1`), refuse a mismatch with the same words the app uses, and pin HTTPS on the first request and on redirects (`--proto =https --proto-redir =https`, `Assert-Https`). The one-liner itself is discussed under *Trust root* below. |
| **U7** | high | `install.sh:108` vs `core/paths.py:30` | The Linux installer put the AppImage in `${XDG_DATA_HOME:-~/.local/share}/operators-console` - byte for byte the directory `paths.data_dir()` keeps `progress.db` in. The learner's only irreplaceable file sat beside the program being replaced. | **fixed** - the program moved to `~/.local/opt/operators-console` (override with `OPCON_APP_DIR`), the installer refuses to run if the two are nested, and it deletes the stale AppImage from the old location without touching anything else in that folder. `_apply_appimage` now also runs `_guard_user_data`. |
| **U8** | medium | `core/updates.py:377` | `zipfile`/`tarfile` `extractall` with no member check. Python 3.12+ sanitises both, so this was not exploitable on a supported interpreter, but the archive is remote input and the guard costs nothing. | **fixed** - `_safe_extract` refuses any member that resolves outside the unpack directory. |
| **U9** | medium | `install.ps1:68` | `Remove-Item $target -Recurse -Force` then `Expand-Archive -DestinationPath $target` - the live install was deleted before the new one was known to be good, and anything else in that folder went with it. | **fixed** - expansion goes to a staging folder; the swap is a rename with the previous build kept until it succeeds. |
| **U10** | medium | both installers | Re-running on a machine with the app open failed on locked files. | **fixed** - both ask the running copy to close (`CloseMainWindow`, `pkill -TERM`), wait, and only then force it. |
| **S1** | high | `core/storage.py:696` `restore()` | Every table was emptied first and the payload inserted after. A backup missing a section silently wiped it: restoring a dump with `tables["checks"]` deleted left `checked_ids() == set()` and reported success. A payload whose `tables` was `{"checks": "not a list"}` wiped **everything** and returned normally. | **fixed** - the whole payload is validated before a single row is deleted; a missing section, a damaged section or an unknown table raises and the store is untouched. |
| **S2** | medium | `core/storage.py:185` | Two app instances: the second write raised `sqlite3.OperationalError: database is locked` after 5.5 s, out of `Store.set_checked`, uncaught by anything in `core`. The learner's click was lost. | **fixed** - `busy_timeout` 30 s, and `tx()` takes `BEGIN IMMEDIATE` up front with four retries, so the wait happens where it can be retried. |
| **S3** | medium | `core/storage.py:189` | `PRAGMA synchronous=NORMAL` in WAL does not fsync on commit, so a power cut can lose recent commits - while the module docstring promises "no unsaved state to lose on a crash or a power cut". | **fixed** - `synchronous=FULL`. Measured cost: 1.3 ms per write against 0.1 ms, for writes that happen when a human clicks something. |
| **S4** | medium | `core/storage.py:198` | `if fresh or current == 0` treated an existing store with no `schema_version` row - i.e. one written before versioning existed - as brand new, skipping the backup the docstring promises. Reproduced: a 1.0.0-shaped database was migrated with `backups/` empty. | **fixed** - the stamp is read before `CREATE TABLE IF NOT EXISTS` invents a `meta` table, and an unversioned existing store gets a `pre-migration-unversioned` backup. |
| **H1** | high | `core/history.py` (whole module) | The undo stack holds closures over rows. Nothing cleared it when the store was replaced. Reproduced: tick an item, `reset_progress()`, then `undo(); redo()` - the wiped check came back. The same stack survives `restore()`, so a redo writes a fragment of the pre-restore world into the freshly restored database. | **fixed** - `Store.generation` moves on `reset_progress()` and `restore()`; `History(store=...)` stamps each action with the generation and drops both stacks when it changes. Wired in `ui/context.py` with a one-line change. |
| **H2** | medium | `core/history.py:78` | `undo()` popped the action and *then* ran the reversal. A reversal that raised left the action on neither stack - the change unreachable from both directions. | **fixed** - the action is only moved once the call returns. |
| **H3** | low | `core/history.py:50` | `del self._undo[:-self.limit]` deletes nothing when `limit` is 0, so `History(limit=0)` kept everything. | **fixed** - the zero case is handled before the slice. |
| **R1** | high | `core/runner.py:97` | `subprocess.run(..., timeout=)` kills the direct child only. A submission calling `subprocess.Popen` left a grandchild that both kept running and kept the inherited stdout pipe open, so `communicate()` blocked until the grandchild finished. Measured: `run_exercise(..., timeout=4)` **returned after 20.3 s**, and the grandchild ran to completion. A `while True: subprocess.Popen(...)` hangs grading indefinitely. | **fixed** - `Popen` + `communicate(timeout=)`, then a process-tree kill (`taskkill /F /T` on Windows, `killpg` elsewhere), then a bounded second read, then the pipes are dropped. Same case now returns in 4.5 s and the grandchild dies with the tree. |
| **P1** | medium | `core/progress.py:176` | `current_phase_id()` ended `self.c.phases[0].id`. With an empty phase list that is `IndexError`, and `TodayPlan.build()` calls it on every dashboard build - so a curriculum that failed to load crashed the first screen instead of showing an empty plan. | **fixed** - returns `""`, and `today.py` copes with an empty marker. |
| **P2** | medium | `core/progress.py:174` | `PhaseProgress.is_complete` is false whenever `total` is 0, so a phase with nothing in it could never be finished and held the position marker forever. | **fixed** - the marker skips phases with nothing to tick. |
| **P3** | medium | `core/today.py:50`, `core/progress.py:210` | `float(self.s.setting("hours_per_day"))` raised `ValueError` straight out of the dashboard for any non-numeric value. Settings are JSON and arrive from restored backups and other machines. | **fixed** - both coerce through a tolerant `_number()` with the documented default. |
| **F1** | medium | `core/srs.py:212` | Relearning + Hard returned the average of the first two steps at *every* step. The reference only does that on step 0 and otherwise repeats the current step. With three relearning steps, a card on step 1 was scheduled at 15 min instead of 20. | **fixed** - same shape as the learning branch. |
| **F2** | medium | `core/srs.py:185,207` | A card whose `step` had run past a shortened step list graduated to Review on **Again**. The reference guards that branch with the rating. A learner who had just failed a card was told to come back in days. | **fixed** - Again never graduates a card. |
| **F3** | low | `core/srs.py:128-131` | A REVIEW-state card with `last_review = None` - restorable from a partial backup - took the short-term path with elapsed 0, freezing its stability. The reference takes the long-term path with retrievability 0. | **fixed**. |
| **F4** | low | `core/srs.py:103` | Only the parameter *count* was checked. `w4 = 99.0` was accepted and produced plausible-looking, wrong intervals. | **fixed** - each weight is checked against the reference's published bounds. |
| **F5** | info | `core/srs.py:82` | The reference floors elapsed time to whole days (`.days`); this counts fractional days. At 10 d 12 h: reference `S = 25.108720`, here `S = 25.631204`. | **left** - the app records real timestamps and throwing half of one away is not an improvement. It is now pinned by a test so it stays a decision rather than a drift. |
| **F6** | info | `core/srs.py:34` | `maximum_interval` is 3650 days where the reference default is 36500. | **left** - ten years is past the end of any curriculum. Pinned by a test. |
| **F7** | info | `core/srs.py:80` | `retrievability()` returns 1.0 for a card never studied; the reference returns 0. | **left** - the number is also read by the interface, where "nothing is decaying yet" is the honest reading, and `review()` never asks before a stability exists. Documented in the docstring. |
| **X1** | info | `core/runner.py` | A submission can `import operators_console.core.storage`, open the learner's own database and write to it. Verified: a submission ticked `p01.s0.1` in the real store. | **left, documented** - see *Sandboxing* below. |

Everything in the FSRS core that is *not* listed above was checked against the
reference implementation and agrees: the 21 default weights, the
retrievability and interval formulas, initial and next difficulty (including
that the mean reversion target is `D0(Easy)`, unclamped), short-term stability
and which ratings clamp its increase, post-lapse stability with its
`min(long_term, short_term)` cap, recall stability with the hard penalty and
easy bonus, the clamping bounds, the fuzz ranges, and the use of the *old*
difficulty when computing the next stability. Both published py-fsrs vectors
reproduce exactly - `tests/test_srs_vectors.py` pins them.

---

## Updater and installer: the security verdict

**Before.** There was no integrity check anywhere in the chain. The release
published no checksums, the installers downloaded and executed whatever URL
the API answered with, the in-app updater did the same and then re-executed
the file after a gap in which nothing re-checked it, and a failed swap could
leave the application unusable. Anyone able to alter a response on the path -
or to serve one - could have run code on a learner's machine.

**After.** The chain is:

1. The release workflow hashes every artefact and publishes `SHA256SUMS`.
2. `fetch_latest()` downloads that manifest and stamps each asset with its
   digest. A release with no manifest is marked `verified = False`.
3. Every request is HTTPS-only, including redirects.
4. `download()` refuses to keep a file whose hash does not match, and refuses
   to download at all when there is no digest to match against.
5. `launch_helper()` carries the digest across the handover.
6. `apply_update()` checks it again, in the helper, immediately before the
   package is used - and refuses with exit 2 if it fails.
7. The swap keeps the old build until the new one is complete, and restores
   it on any failure.

The installers do the equivalent, in their own languages, with the same
refusal wording.

**Trust root - and it is the honest limit of all of this.** `irm ... | iex`
and `curl ... | sh` execute a script fetched from the `main` branch of the
repository. The checksum proves the bytes you downloaded are the bytes that
release published. It does not prove who published that release, and it does
not protect you if the repository or the account behind it is compromised: an
attacker with push access writes both the binary and the `SHA256SUMS` beside
it. What this buys is protection against everything between GitHub and the
learner - a hostile network, a proxy, a mirror, a corrupted CDN object, a
partial download - and a way to notice a swapped artefact after the fact.

Closing the remaining gap needs a signature over the manifest with a key that
does not live in the repository: code signing on Windows and macOS (which
also removes the Gatekeeper workaround in `install.sh`), or a detached
signature the installers check against a pinned public key. That is the next
step, and it is not one an audit can do on its own.

Two smaller things a maintainer should know:

* The one-liners fetch `install.ps1` / `install.sh` from `main`, not from a
  tag. Pinning them to a tag would mean the documented command changes every
  release; the trade-off was left as it is, and it is the same trust root
  either way.
* `-SkipVerify` / `OPCON_SKIP_VERIFY=1` exists so releases published before
  `SHA256SUMS` can still be installed. It is off by default, it warns loudly,
  and it should be removed once no supported release predates the manifest.

### The three calls the interface uses

```
updates.available(timeout=8)                -> offer or None
updates.download_update(offer, progress=cb, cancelled=cb) -> Path
updates.apply_and_restart(path, sha256="")  -> hands over; the caller quits
```

`available()` returns a `Release` that reads **both** ways, because the two
halves of the app reach for different shapes:

* as an object - `offer.label`, `offer.name`, `offer.notes`, `offer.url`,
  `offer.verified`, and `updates.pick_asset(offer)`;
* as a mapping - `offer["version"]`, `offer["notes"]`, `offer["size"]`,
  `offer["asset"]`, `offer["sha256"]`, `offer["verified"]`.

`offer["verified"]` is `False` when the release published no manifest. Show
that before offering to install, because `download_update` will refuse it.

`download_update` raises `updates.IntegrityError` (message in
`updates.MISMATCH_MESSAGE` or `updates.NO_SUMS_MESSAGE`) and
`InterruptedError` when `cancelled()` goes true. The older entry points -
`fetch_latest`, `pick_asset`, `download`, `launch_helper` - still work and are
verified the same way, since the digest now travels on the `Asset`.

---

## Sandboxing: what the grader does and does not do

The grader runs the learner's own code on the learner's own machine with the
learner's own permissions. It is not a sandbox and is not pretending to be
one: the code being graded is code the learner wrote and is about to run
anyway. What it does guarantee:

* the code runs in a **separate process**, so an endless loop, a segfault, a
  `sys.exit` or a runaway allocation cannot take the application with it;
* a **timeout** that kills the whole process tree, so nothing a submission
  starts can outlive the run or block the interface;
* the working directory is `paths.workspace_dir()`, a scratch folder that is
  *not* the folder holding `progress.db`;
* output is captured and truncated, so a print loop cannot fill memory in the
  interface process;
* on POSIX, best-effort `RLIMIT_AS` and `RLIMIT_CPU`. Windows has no
  equivalent and relies on the timeout.

What it does **not** do: a submission can read and write files anywhere the
learner can, open the network, and `import operators_console` and edit the
learner's own database. Do not paste code you do not understand into the
practice editor. The thing the app does protect unconditionally is the text in
the editor: grading never touches it, and a run that times out returns a
failure rather than losing the submission.

---

## Mutation check

Twelve-plus deliberate breakages were applied one at a time to a scratch copy
of the tree, each followed by the tests that cover that area. A mutation the
tests still pass is a **survivor** - the line it touched is not actually
asserted anywhere.

<!-- MUTATION-RESULTS -->

---

## What a maintainer should know

**The store is the only thing that cannot be regenerated.** Everything else in
this repository can be rebuilt from source. `progress.db` cannot. That is why
`restore()` now validates before it deletes, why the migration path backs up a
store it does not recognise, and why every installer and updater change above
is really a data-safety change wearing a security hat.

**Three directories must never be the same directory.** The program, the
scratch workspace and the store. They are distinct on all three platforms:

| | program | store |
|---|---|---|
| Windows | `%LOCALAPPDATA%\Programs\Operators Console` (or the Inno install dir) | `%APPDATA%\Operator's Console` |
| macOS | `~/Applications/Operator's Console.app` | `~/Library/Application Support/Operator's Console` |
| Linux | `~/.local/opt/operators-console` | `${XDG_DATA_HOME:-~/.local/share}/operators-console` |

On Linux they used to be the same folder (U7). `_guard_user_data()` is the
backstop for anyone who points `OPERATORS_CONSOLE_HOME` inside the app
directory, and `tests/test_installers.py` is the backstop for the layout.

**The undo stack is session-only and now epoch-aware.** It holds closures, not
data, so it is only valid against the database generation it was recorded on.
Any new operation that replaces the store wholesale must bump
`Store.generation`, or undo will start writing the old world into the new one.

**Scheduling is pinned to vectors, not to intuition.** `tests/test_srs_vectors.py`
holds numbers produced by the reference implementation. If a change to
`core/srs.py` makes one of them fail, the change altered every learner's
schedule - decide that deliberately and update the vector with a reason, or
revert. The two documented divergences (F5, F6) have their own tests so they
cannot drift into accidents.

**Two copies of the app is a supported state, not an error.** Someone will
leave a window open on a second desktop. Writes wait for each other and retry;
reads are current because every mutation commits immediately. What is *not*
handled is two instances holding stale in-memory view state - the interface
refreshes on its own actions, not on the other instance's.

**The grader's timeout is a tree kill, not a process kill.** If that ever gets
simplified back to `proc.kill()` or `subprocess.run(timeout=)`, the hang in R1
comes back, and it does not look like a hang in the runner - it looks like the
whole app freezing on a student's exercise.
