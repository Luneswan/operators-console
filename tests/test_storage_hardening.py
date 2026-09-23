"""The store under conditions it will actually meet.

A learner's progress is the only thing in this application that cannot be
regenerated. These tests are about the ways it could be lost: a second copy
of the app writing at the same moment, a truncated backup, a store written by
an older build, and a long random sequence of edits followed by a reopen.
"""
from __future__ import annotations

import json
import random
import sqlite3
import threading

import pytest

from operators_console.core import paths
from operators_console.core.storage import SCHEMA_VERSION, Store


# ---------------------------------------------------------------------------
# durability
# ---------------------------------------------------------------------------

def test_the_connection_is_configured_for_survival(store):
    """WAL for concurrency, FULL for power cuts, a long wait for the lock."""
    assert store.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    # 2 is FULL: every commit reaches the disk, so the module's promise that
    # there is nothing to lose on a crash is actually true.
    assert store.db.execute("PRAGMA synchronous").fetchone()[0] == 2
    assert store.db.execute("PRAGMA busy_timeout").fetchone()[0] >= 30_000


def test_a_commit_is_visible_to_a_second_connection_immediately(store):
    store.set_checked("p01.s0.0", True)
    other = Store()
    try:
        assert other.is_checked("p01.s0.0")
    finally:
        other.close()


# ---------------------------------------------------------------------------
# two copies of the app
# ---------------------------------------------------------------------------

def test_a_write_waits_out_another_instance_instead_of_failing(store):
    """Two windows open at once must not cost the learner a click.

    Before the retry, the second instance raised OperationalError out of
    whatever the learner had just ticked, and the tick was simply lost.

    The busy timeout is shortened here so the lock can be held past it in a
    test that still finishes in a second. That is what isolates the retry:
    with a single attempt the write fails the moment the timeout expires,
    however long the timeout happens to be in production.
    """
    other = Store()
    other.db.execute("PRAGMA busy_timeout=120")
    released = threading.Event()
    taken = threading.Event()

    def hold_the_lock():
        store.db.execute("BEGIN IMMEDIATE")
        store.db.execute(
            "INSERT OR REPLACE INTO checks(item_id,done_at) VALUES('a','t')")
        taken.set()
        released.wait(1.0)
        store.db.commit()

    holder = threading.Thread(target=hold_the_lock)
    holder.start()
    try:
        assert taken.wait(5.0)
        # Hold it well past the shortened timeout, then let go while the
        # retries are still running.
        threading.Timer(0.45, released.set).start()
        other.set_checked("p01.s0.0", True)
        assert other.is_checked("p01.s0.0")
    finally:
        released.set()
        holder.join(5)
        other.close()


def test_the_retry_gives_up_eventually_rather_than_hanging(store):
    """Waiting forever would be its own bug; the attempts are bounded."""
    from operators_console.core.storage import WRITE_ATTEMPTS
    assert 1 < WRITE_ATTEMPTS <= 10


def test_two_instances_interleaving_writes_keep_both_sets(store):
    other = Store()
    try:
        for i in range(25):
            store.set_checked("a-%d" % i, True)
            other.set_checked("b-%d" % i, True)
        seen = other.checked_ids()
        assert len([x for x in seen if x.startswith("a-")]) == 25
        assert len([x for x in seen if x.startswith("b-")]) == 25
    finally:
        other.close()


# ---------------------------------------------------------------------------
# migration
# ---------------------------------------------------------------------------

def _write_unversioned_store(path):
    """A store shaped like the one 1.0.0 shipped: no schema_version row."""
    raw = sqlite3.connect(path)
    raw.executescript("""
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE checks (item_id TEXT PRIMARY KEY, done_at TEXT NOT NULL);
        INSERT INTO checks VALUES('p01.s0.0','2025-01-01T00:00:00+00:00');
    """)
    raw.commit()
    raw.close()


def test_an_unversioned_store_is_backed_up_before_it_is_migrated(isolated_home):
    """The store most likely to be damaged by a migration gets the backup.

    An existing database with no schema_version row is not a new one - it was
    written before versioning existed. Treating it as new skipped exactly the
    safety net the docstring promises.
    """
    db = paths.db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    _write_unversioned_store(db)

    store = Store()
    try:
        assert store.is_checked("p01.s0.0")
        assert store.get_meta("schema_version") == str(SCHEMA_VERSION)
        backups = list(paths.backups_dir().glob("*pre-migration-unversioned*"))
        assert backups, "an unversioned store was migrated with no backup"
        # The backup is a real database holding the pre-migration rows.
        saved = sqlite3.connect(backups[0])
        rows = saved.execute("SELECT item_id FROM checks").fetchall()
        saved.close()
        assert rows == [("p01.s0.0",)]
    finally:
        store.close()


def test_a_fresh_store_is_not_backed_up(isolated_home):
    store = Store()
    try:
        assert not list(paths.backups_dir().glob("*pre-migration*"))
    finally:
        store.close()


def test_a_store_from_a_newer_build_is_refused_not_downgraded(store, tmp_path):
    store.set_meta("schema_version", "99")
    store.close()
    with pytest.raises(RuntimeError, match="newer version"):
        Store()


# ---------------------------------------------------------------------------
# restore
# ---------------------------------------------------------------------------

def test_a_full_round_trip_restores_everything(store):
    store.set_checked("p01.s0.0", True)
    store.set_rating("loops", 3)
    store.add_log("2026-01-01", "Generators", 2.0, "b", "s", "n")
    payload = store.dump()
    store.reset_progress()
    assert not store.checked_ids()
    store.restore(payload)
    assert store.is_checked("p01.s0.0")
    assert store.rating("loops") == 3
    assert store.total_hours() == 2.0


def test_a_backup_missing_a_table_is_refused_rather_than_obeyed(store):
    """A truncated backup used to wipe the tables it did not mention.

    restore() deleted every table first and then inserted whatever the
    payload happened to contain, so a hand-edited or half-written export
    destroyed the learner's checks and reported success.
    """
    store.set_checked("p01.s0.0", True)
    payload = store.dump()
    del payload["tables"]["checks"]

    with pytest.raises(ValueError, match="incomplete"):
        store.restore(payload)
    assert store.is_checked("p01.s0.0"), "a refused restore still wiped data"


def test_a_backup_with_a_damaged_section_is_refused(store):
    store.set_checked("p01.s0.0", True)
    payload = store.dump()
    payload["tables"]["checks"] = "not a list of rows"
    with pytest.raises(ValueError, match="damaged"):
        store.restore(payload)
    assert store.is_checked("p01.s0.0")


def test_a_backup_with_no_tables_at_all_is_refused(store):
    store.set_checked("p01.s0.0", True)
    with pytest.raises(ValueError, match="no tables"):
        store.restore({"app": "operators-console", "schema": SCHEMA_VERSION,
                       "tables": {}})
    assert store.is_checked("p01.s0.0")


def test_a_backup_naming_a_table_that_does_not_exist_is_refused(store):
    payload = store.dump()
    payload["tables"]["sqlite_master"] = [{"name": "x"}]
    with pytest.raises(ValueError, match="unknown table"):
        store.restore(payload)


def test_an_unstorable_value_leaves_the_store_untouched(store):
    store.set_checked("p01.s0.0", True)
    payload = store.dump()
    payload["tables"]["checks"] = [{"item_id": {"not": "a string"},
                                    "done_at": "x"}]
    with pytest.raises(ValueError):       # a sentence the Import page can show
        store.restore(payload)
    assert store.is_checked("p01.s0.0")


def test_a_dump_survives_json(store):
    """Exports go through a file, so every value has to be JSON-clean."""
    store.set_checked("p01.s0.0", True)
    store.set_setting("goals", ["web", "data"])
    store.add_log("2026-01-01", "Generators — 你好", 1.5,
                  "b", "s", "n")
    round_tripped = json.loads(json.dumps(store.dump()))
    store.reset_progress()
    store.restore(round_tripped)
    assert store.is_checked("p01.s0.0")
    assert store.logs()[0]["focus"] == "Generators — 你好"


# ---------------------------------------------------------------------------
# generation counter, which the undo stack keys on
# ---------------------------------------------------------------------------

def test_wholesale_replacements_move_the_generation(store):
    before = store.generation
    store.set_checked("p01.s0.0", True)
    assert store.generation == before, "an ordinary edit is not a replacement"
    store.reset_progress()
    assert store.generation == before + 1
    store.restore(store.dump())
    assert store.generation == before + 2


# ---------------------------------------------------------------------------
# fuzz
# ---------------------------------------------------------------------------

OPERATIONS = (
    lambda s, r: s.set_checked("item-%d" % r.randrange(40), r.random() < 0.7),
    lambda s, r: s.set_rating("topic-%d" % r.randrange(10), r.randrange(-3, 9)),
    lambda s, r: s.set_note("scope-%d" % r.randrange(8),
                            r.choice(["", " ", "body 你好", "x" * 500])),
    lambda s, r: s.add_log("2026-01-%02d" % (r.randrange(28) + 1), "focus",
                           r.choice([0, 0.5, 8.25]), "b", "s", "n"),
    lambda s, r: s.record_quiz("quiz-%d" % r.randrange(5), r.randrange(6),
                               r.choice([0, 5]), r.randrange(600)),
    lambda s, r: s.record_exercise_run("ex-%d" % r.randrange(12),
                                       "code = %d" % r.randrange(99),
                                       r.random() < 0.5),
    lambda s, r: s.save_exercise_code("ex-%d" % r.randrange(12), "draft"),
    lambda s, r: s.set_project("proj-%d" % r.randrange(6),
                               status=r.choice(["not-started", "in-progress",
                                                "shipped"])),
    lambda s, r: s.set_cert_status("cert-%d" % r.randrange(4), r.randrange(5)),
    lambda s, r: s.bump_activity(minutes=r.randrange(90), reviews=r.randrange(4)),
    lambda s, r: s.set_setting("learner_name", r.choice(["", "Ada", "你"])),
    lambda s, r: s.suspend_card("card-%d" % r.randrange(5), r.random() < 0.5),
    lambda s, r: s.reveal_solution("ex-%d" % r.randrange(12)),
)


@pytest.mark.parametrize("seed", [1, 7, 13, 101])
def test_a_random_edit_sequence_survives_a_reopen(seed, isolated_home):
    """Fuzz the store, close it, open it again, and compare every table.

    Nothing here checks a specific value. The property under test is that
    whatever the learner did, reopening the file shows exactly what closing
    it showed - no half-written row, no lost commit, no schema surprise.
    """
    rng = random.Random(seed)
    store = Store()
    try:
        for step in range(120):
            OPERATIONS[rng.randrange(len(OPERATIONS))](store, rng)
            if step % 30 == 29:
                # Reopen mid-sequence: a crash could happen at any point, and
                # the next launch has to cope with whatever is on disk.
                snapshot = store.dump()
                store.close()
                store = Store()
                assert store.dump()["tables"] == snapshot["tables"]
        final = store.dump()
    finally:
        store.close()

    reopened = Store()
    try:
        assert reopened.dump()["tables"] == final["tables"]
        # And the reopened store is still usable, not just readable.
        reopened.set_checked("after-the-fuzz", True)
        assert reopened.is_checked("after-the-fuzz")
        current, longest = reopened.streak()
        assert current >= 0 and longest >= current or longest >= 0
    finally:
        reopened.close()


@pytest.mark.parametrize("seed", [3, 29])
def test_a_fuzzed_store_round_trips_through_export_and_import(seed,
                                                              isolated_home):
    rng = random.Random(seed)
    store = Store()
    try:
        for _ in range(80):
            OPERATIONS[rng.randrange(len(OPERATIONS))](store, rng)
        payload = json.loads(json.dumps(store.dump()))
        store.restore(payload)
        after = store.dump()
        for table in Store.TABLES:
            if table == "meta":
                continue    # schema_version is re-stamped by restore()
            assert after["tables"][table] == payload["tables"][table], table
    finally:
        store.close()


def test_a_damaged_database_is_released_when_opening_it_fails(tmp_path):
    """The error dialog tells the learner to move the file aside.

    On Windows that is impossible while this process still holds it open,
    which it did: the connection outlived the failed constructor.
    """
    damaged = tmp_path / "progress.db"
    damaged.write_bytes(b"this was never a database" * 200)
    with pytest.raises(sqlite3.DatabaseError):
        Store(damaged)
    damaged.rename(tmp_path / "progress-damaged.db")     # would fail if locked
    assert (tmp_path / "progress-damaged.db").exists()
