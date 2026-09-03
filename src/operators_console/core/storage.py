"""Everything the learner creates, in one SQLite file.

Design notes:

* Every mutation commits immediately. There is no Save button anywhere in the
  app and no unsaved state to lose on a crash or a power cut.
* WAL mode keeps reads fast while a write is in flight.
* The schema is versioned; the store migrates forward on open and takes a
  timestamped backup before it does.
* Timestamps are UTC ISO-8601. Days are local YYYY-MM-DD, because a study
  streak is a human-calendar idea rather than a UTC one.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from . import paths
from .srs import Memory, State

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Roadmap items, gate items and project requirements all live here.
CREATE TABLE IF NOT EXISTS checks (
    item_id TEXT PRIMARY KEY,
    done_at TEXT NOT NULL
);

-- Self-assessed confidence per skill-matrix row, 0..4.
CREATE TABLE IF NOT EXISTS ratings (
    topic TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    scope      TEXT PRIMARY KEY,
    body       TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    day        TEXT NOT NULL,
    focus      TEXT NOT NULL DEFAULT '',
    hours      REAL NOT NULL DEFAULT 0,
    built      TEXT NOT NULL DEFAULT '',
    stuck      TEXT NOT NULL DEFAULT '',
    next_up    TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS logs_day ON logs(day);

-- One row per reviewable card. kind is 'quiz' or 'concept'.
CREATE TABLE IF NOT EXISTS srs (
    card_id     TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    phase       TEXT NOT NULL DEFAULT '',
    stability   REAL,
    difficulty  REAL,
    state       INTEGER NOT NULL DEFAULT 0,
    step        INTEGER NOT NULL DEFAULT 0,
    due         TEXT,
    last_review TEXT,
    reps        INTEGER NOT NULL DEFAULT 0,
    lapses      INTEGER NOT NULL DEFAULT 0,
    suspended   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS srs_due ON srs(due);
CREATE INDEX IF NOT EXISTS srs_phase ON srs(phase);

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id     TEXT NOT NULL,
    rating      INTEGER NOT NULL,
    reviewed_at TEXT NOT NULL,
    day         TEXT NOT NULL,
    correct     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS reviews_day ON reviews(day);
CREATE INDEX IF NOT EXISTS reviews_card ON reviews(card_id);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id     TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    day         TEXT NOT NULL,
    score       INTEGER NOT NULL,
    total       INTEGER NOT NULL,
    seconds     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS quiz_attempts_quiz ON quiz_attempts(quiz_id);

CREATE TABLE IF NOT EXISTS exercise_state (
    exercise_id TEXT PRIMARY KEY,
    code        TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'new',
    attempts    INTEGER NOT NULL DEFAULT 0,
    passed_at   TEXT,
    updated_at  TEXT NOT NULL,
    revealed    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS project_state (
    project_id  TEXT PRIMARY KEY,
    status      TEXT NOT NULL DEFAULT 'not-started',
    repo_url    TEXT NOT NULL DEFAULT '',
    notes       TEXT NOT NULL DEFAULT '',
    started_at  TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS cert_state (
    cert_id    TEXT PRIMARY KEY,
    status     INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

-- Aggregated per local day, so charts and streaks need no table scans.
CREATE TABLE IF NOT EXISTS activity (
    day       TEXT PRIMARY KEY,
    minutes   INTEGER NOT NULL DEFAULT 0,
    items     INTEGER NOT NULL DEFAULT 0,
    reviews   INTEGER NOT NULL DEFAULT 0,
    exercises INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

DEFAULT_SETTINGS: dict[str, Any] = {
    "onboarded": False,
    "learner_name": "",
    "track": "generalist",
    "goals": [],
    "hours_per_day": 3.0,
    "days_per_week": 5,
    "experience": "none",
    "theme": "system",
    "desired_retention": 0.90,
    "new_cards_per_day": 15,
    "max_reviews_per_day": 120,
    "started_on": "",
    "font_scale": 1.0,
    "exercise_timeout": 10,
    "check_for_updates": True,
    "last_update_check": "",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _today() -> str:
    return date.today().isoformat()


def _parse_dt(value):
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


class Store:
    """Thin, synchronous data-access layer over the progress database."""

    def __init__(self, db_file: Path | None = None) -> None:
        self.path = Path(db_file) if db_file else paths.db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fresh = not self.path.exists()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self._migrate(fresh)

    # -- lifecycle -------------------------------------------------------

    def _migrate(self, fresh: bool) -> None:
        with self.tx():
            self.db.executescript(SCHEMA)
        current = int(self.get_meta("schema_version", "0") or 0)
        if fresh or current == 0:
            self.set_meta("schema_version", str(SCHEMA_VERSION))
            self.set_meta("created_at", _now())
        elif current < SCHEMA_VERSION:
            self.backup(tag="pre-migration-v%d" % current)
            # Future migrations are appended here, each guarded by version.
            self.set_meta("schema_version", str(SCHEMA_VERSION))
        elif current > SCHEMA_VERSION:
            raise RuntimeError(
                "This database was written by a newer version of the app "
                "(schema %d, this build understands %d). Update the "
                "application to open it." % (current, SCHEMA_VERSION))

    def close(self) -> None:
        try:
            self.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:
            pass
        self.db.close()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        """One atomic unit of work; rolls back on any exception."""
        try:
            yield self.db
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def backup(self, tag: str = "") -> Path:
        """Copy the database to the backups folder, keeping the last 12."""
        self.db.commit()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = "progress-%s%s.db" % (stamp, ("-" + tag) if tag else "")
        target = paths.backups_dir() / name
        dest = sqlite3.connect(target)
        with dest:
            self.db.backup(dest)
        dest.close()
        existing = sorted(paths.backups_dir().glob("progress-*.db"))
        for old in existing[:-12]:
            try:
                old.unlink()
            except OSError:
                pass
        return target

    # -- meta and settings -----------------------------------------------

    def get_meta(self, key: str, default: str = "") -> str:
        row = self.db.execute(
            "SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_meta(self, key: str, value: str) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value))

    def setting(self, key: str, default: Any = None) -> Any:
        row = self.db.execute(
            "SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if row is None:
            return DEFAULT_SETTINGS.get(key, default)
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            return row["value"]

    def set_setting(self, key: str, value: Any) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, json.dumps(value)))

    def all_settings(self) -> dict:
        out = dict(DEFAULT_SETTINGS)
        for row in self.db.execute("SELECT key,value FROM settings"):
            try:
                out[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                out[row["key"]] = row["value"]
        return out

    # -- checkboxes ------------------------------------------------------

    def is_checked(self, item_id: str) -> bool:
        return self.db.execute(
            "SELECT 1 FROM checks WHERE item_id=?", (item_id,)).fetchone() is not None

    def checked_ids(self) -> set:
        return {r["item_id"] for r in self.db.execute("SELECT item_id FROM checks")}

    def set_checked(self, item_id: str, done: bool) -> None:
        with self.tx():
            if done:
                self.db.execute(
                    "INSERT OR IGNORE INTO checks(item_id,done_at) VALUES(?,?)",
                    (item_id, _now()))
            else:
                self.db.execute("DELETE FROM checks WHERE item_id=?", (item_id,))
        if done:
            self.bump_activity(items=1)

    def set_many_checked(self, item_ids: Iterable, done: bool) -> int:
        ids = list(item_ids)
        if not ids:
            return 0
        with self.tx():
            if done:
                now = _now()
                self.db.executemany(
                    "INSERT OR IGNORE INTO checks(item_id,done_at) VALUES(?,?)",
                    [(i, now) for i in ids])
            else:
                self.db.executemany(
                    "DELETE FROM checks WHERE item_id=?", [(i,) for i in ids])
        return len(ids)

    # -- ratings, notes, logs --------------------------------------------

    def rating(self, topic: str) -> int:
        row = self.db.execute(
            "SELECT value FROM ratings WHERE topic=?", (topic,)).fetchone()
        return row["value"] if row else 0

    def set_rating(self, topic: str, value: int) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO ratings(topic,value) VALUES(?,?) "
                "ON CONFLICT(topic) DO UPDATE SET value=excluded.value",
                (topic, max(0, min(4, int(value)))))

    def all_ratings(self) -> dict:
        return {r["topic"]: r["value"]
                for r in self.db.execute("SELECT topic,value FROM ratings")}

    def note(self, scope: str) -> str:
        row = self.db.execute(
            "SELECT body FROM notes WHERE scope=?", (scope,)).fetchone()
        return row["body"] if row else ""

    def set_note(self, scope: str, body: str) -> None:
        with self.tx():
            if body.strip():
                self.db.execute(
                    "INSERT INTO notes(scope,body,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(scope) DO UPDATE SET body=excluded.body, "
                    "updated_at=excluded.updated_at",
                    (scope, body, _now()))
            else:
                self.db.execute("DELETE FROM notes WHERE scope=?", (scope,))

    def all_notes(self) -> dict:
        return {r["scope"]: r["body"]
                for r in self.db.execute("SELECT scope,body FROM notes")}

    def add_log(self, day: str, focus: str, hours: float, built: str,
                stuck: str, next_up: str) -> int:
        with self.tx():
            cur = self.db.execute(
                "INSERT INTO logs(day,focus,hours,built,stuck,next_up,created_at)"
                " VALUES(?,?,?,?,?,?,?)",
                (day, focus, float(hours), built, stuck, next_up, _now()))
        self.bump_activity(minutes=int(float(hours) * 60), day=day)
        return int(cur.lastrowid or 0)

    def logs(self, limit: int = 500) -> list:
        return list(self.db.execute(
            "SELECT * FROM logs ORDER BY day DESC, id DESC LIMIT ?", (limit,)))

    def delete_log(self, log_id: int) -> None:
        with self.tx():
            self.db.execute("DELETE FROM logs WHERE id=?", (log_id,))

    def total_hours(self) -> float:
        row = self.db.execute(
            "SELECT COALESCE(SUM(hours),0) AS h FROM logs").fetchone()
        return float(row["h"])

    # -- spaced repetition ------------------------------------------------

    def memory(self, card_id: str) -> Memory:
        row = self.db.execute(
            "SELECT * FROM srs WHERE card_id=?", (card_id,)).fetchone()
        if row is None:
            return Memory()
        return Memory(
            stability=row["stability"],
            difficulty=row["difficulty"],
            state=State(row["state"]),
            step=row["step"],
            due=_parse_dt(row["due"]),
            last_review=_parse_dt(row["last_review"]),
            reps=row["reps"],
            lapses=row["lapses"],
        )

    def save_memory(self, card_id: str, kind: str, phase: str,
                    memory: Memory) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO srs(card_id,kind,phase,stability,difficulty,state,"
                "step,due,last_review,reps,lapses) VALUES(?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(card_id) DO UPDATE SET "
                "kind=excluded.kind, phase=excluded.phase, "
                "stability=excluded.stability, difficulty=excluded.difficulty, "
                "state=excluded.state, step=excluded.step, due=excluded.due, "
                "last_review=excluded.last_review, reps=excluded.reps, "
                "lapses=excluded.lapses",
                (card_id, kind, phase, memory.stability, memory.difficulty,
                 int(memory.state), memory.step,
                 memory.due.isoformat() if memory.due else None,
                 memory.last_review.isoformat() if memory.last_review else None,
                 memory.reps, memory.lapses))

    def log_review(self, card_id: str, rating: int, correct: bool) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO reviews(card_id,rating,reviewed_at,day,correct)"
                " VALUES(?,?,?,?,?)",
                (card_id, int(rating), _now(), _today(), int(bool(correct))))
        self.bump_activity(reviews=1)

    def due_cards(self, now=None, limit=None) -> list:
        now = now or datetime.now(timezone.utc)
        sql = ("SELECT card_id FROM srs WHERE suspended=0 AND due IS NOT NULL "
               "AND due<=? ORDER BY due ASC")
        args: list = [now.isoformat()]
        if limit:
            sql += " LIMIT ?"
            args.append(limit)
        return [r["card_id"] for r in self.db.execute(sql, args)]

    def seen_cards(self) -> set:
        return {r["card_id"] for r in self.db.execute("SELECT card_id FROM srs")}

    def suspend_card(self, card_id: str, suspended: bool = True) -> None:
        with self.tx():
            self.db.execute("UPDATE srs SET suspended=? WHERE card_id=?",
                            (int(suspended), card_id))

    def card_counts(self, now=None) -> dict:
        stamp = (now or datetime.now(timezone.utc)).isoformat()
        row = self.db.execute(
            "SELECT COUNT(*) AS total,"
            " SUM(CASE WHEN due<=? AND suspended=0 THEN 1 ELSE 0 END) AS due,"
            " SUM(CASE WHEN state IN (1,3) THEN 1 ELSE 0 END) AS learning,"
            " SUM(CASE WHEN state=2 THEN 1 ELSE 0 END) AS mature "
            "FROM srs", (stamp,)).fetchone()
        return {k: int(row[k] or 0)
                for k in ("total", "due", "learning", "mature")}

    def review_accuracy(self, days: int = 30):
        since = (date.today() - timedelta(days=days)).isoformat()
        row = self.db.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS c "
            "FROM reviews WHERE day>=?", (since,)).fetchone()
        return int(row["c"]), int(row["n"])

    def reviews_by_day(self, days: int = 90) -> dict:
        since = (date.today() - timedelta(days=days)).isoformat()
        return {r["day"]: r["n"] for r in self.db.execute(
            "SELECT day, COUNT(*) AS n FROM reviews WHERE day>=? GROUP BY day",
            (since,))}

    def forecast(self, days: int = 30) -> list:
        """How many cards fall due on each of the next N days."""
        out = [0] * days
        today = date.today()
        for row in self.db.execute(
                "SELECT substr(due,1,10) AS d, COUNT(*) AS n FROM srs "
                "WHERE suspended=0 AND due IS NOT NULL GROUP BY d"):
            try:
                delta = (date.fromisoformat(row["d"]) - today).days
            except (ValueError, TypeError):
                continue
            if delta < 0:
                out[0] += row["n"]
            elif delta < days:
                out[delta] += row["n"]
        return out

    # -- quizzes ----------------------------------------------------------

    def record_quiz(self, quiz_id: str, score: int, total: int,
                    seconds: int) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO quiz_attempts(quiz_id,finished_at,day,score,total,"
                "seconds) VALUES(?,?,?,?,?,?)",
                (quiz_id, _now(), _today(), score, total, seconds))

    def best_quiz_score(self, quiz_id: str):
        row = self.db.execute(
            "SELECT score,total FROM quiz_attempts WHERE quiz_id=? AND total>0 "
            "ORDER BY (CAST(score AS REAL)/total) DESC, finished_at DESC LIMIT 1",
            (quiz_id,)).fetchone()
        return (row["score"], row["total"]) if row else None

    def quiz_attempts(self, quiz_id=None, limit: int = 200) -> list:
        if quiz_id:
            return list(self.db.execute(
                "SELECT * FROM quiz_attempts WHERE quiz_id=? "
                "ORDER BY finished_at DESC LIMIT ?", (quiz_id, limit)))
        return list(self.db.execute(
            "SELECT * FROM quiz_attempts ORDER BY finished_at DESC LIMIT ?",
            (limit,)))

    # -- exercises --------------------------------------------------------

    def exercise(self, exercise_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM exercise_state WHERE exercise_id=?",
            (exercise_id,)).fetchone()
        if row is None:
            return {"exercise_id": exercise_id, "code": "", "status": "new",
                    "attempts": 0, "passed_at": None, "revealed": 0}
        return dict(row)

    def save_exercise_code(self, exercise_id: str, code: str) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO exercise_state(exercise_id,code,updated_at) "
                "VALUES(?,?,?) ON CONFLICT(exercise_id) DO UPDATE SET "
                "code=excluded.code, updated_at=excluded.updated_at",
                (exercise_id, code, _now()))

    def record_exercise_run(self, exercise_id: str, code: str,
                            passed: bool) -> None:
        already = self.exercise(exercise_id)["status"] == "passed"
        with self.tx():
            self.db.execute(
                "INSERT INTO exercise_state(exercise_id,code,status,attempts,"
                "passed_at,updated_at) VALUES(?,?,?,1,?,?) "
                "ON CONFLICT(exercise_id) DO UPDATE SET "
                "code=excluded.code, "
                "status=CASE WHEN exercise_state.status='passed' THEN 'passed' "
                "            ELSE excluded.status END, "
                "attempts=exercise_state.attempts+1, "
                "passed_at=COALESCE(exercise_state.passed_at,excluded.passed_at),"
                "updated_at=excluded.updated_at",
                (exercise_id, code, "passed" if passed else "attempted",
                 _now() if passed else None, _now()))
        if passed and not already:
            self.bump_activity(exercises=1)

    def reveal_solution(self, exercise_id: str) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO exercise_state(exercise_id,revealed,updated_at) "
                "VALUES(?,1,?) ON CONFLICT(exercise_id) DO UPDATE SET "
                "revealed=1, updated_at=excluded.updated_at",
                (exercise_id, _now()))

    def exercise_statuses(self) -> dict:
        return {r["exercise_id"]: r["status"] for r in self.db.execute(
            "SELECT exercise_id,status FROM exercise_state")}

    def passed_exercise_ids(self) -> set:
        return {r["exercise_id"] for r in self.db.execute(
            "SELECT exercise_id FROM exercise_state WHERE status='passed'")}

    # -- projects and certificates ----------------------------------------

    def project(self, project_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM project_state WHERE project_id=?",
            (project_id,)).fetchone()
        if row is None:
            return {"project_id": project_id, "status": "not-started",
                    "repo_url": "", "notes": "", "started_at": None,
                    "finished_at": None}
        return dict(row)

    def set_project(self, project_id: str, status=None, repo_url=None,
                    notes=None) -> None:
        cur = self.project(project_id)
        status = cur["status"] if status is None else status
        repo_url = cur["repo_url"] if repo_url is None else repo_url
        notes = cur["notes"] if notes is None else notes
        started = cur["started_at"]
        finished = cur["finished_at"]
        if status in ("in-progress", "shipped") and not started:
            started = _now()
        if status == "shipped" and not finished:
            finished = _now()
        if status == "not-started":
            started = finished = None
        if status == "in-progress":
            finished = None
        with self.tx():
            self.db.execute(
                "INSERT INTO project_state(project_id,status,repo_url,notes,"
                "started_at,finished_at) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(project_id) DO UPDATE SET status=excluded.status,"
                "repo_url=excluded.repo_url, notes=excluded.notes, "
                "started_at=excluded.started_at, finished_at=excluded.finished_at",
                (project_id, status, repo_url, notes, started, finished))

    def project_statuses(self) -> dict:
        return {r["project_id"]: r["status"] for r in self.db.execute(
            "SELECT project_id,status FROM project_state")}

    def cert_status(self, cert_id: str) -> int:
        row = self.db.execute(
            "SELECT status FROM cert_state WHERE cert_id=?",
            (cert_id,)).fetchone()
        return int(row["status"]) if row else 0

    def set_cert_status(self, cert_id: str, status: int) -> None:
        with self.tx():
            self.db.execute(
                "INSERT INTO cert_state(cert_id,status,updated_at) VALUES(?,?,?)"
                " ON CONFLICT(cert_id) DO UPDATE SET status=excluded.status, "
                "updated_at=excluded.updated_at",
                (cert_id, int(status) % 3, _now()))

    def cert_statuses(self) -> dict:
        return {r["cert_id"]: r["status"] for r in self.db.execute(
            "SELECT cert_id,status FROM cert_state")}

    # -- activity and streaks ----------------------------------------------

    def bump_activity(self, minutes: int = 0, items: int = 0, reviews: int = 0,
                      exercises: int = 0, day=None) -> None:
        day = day or _today()
        with self.tx():
            self.db.execute(
                "INSERT INTO activity(day,minutes,items,reviews,exercises) "
                "VALUES(?,?,?,?,?) ON CONFLICT(day) DO UPDATE SET "
                "minutes=activity.minutes+excluded.minutes, "
                "items=activity.items+excluded.items, "
                "reviews=activity.reviews+excluded.reviews, "
                "exercises=activity.exercises+excluded.exercises",
                (day, minutes, items, reviews, exercises))

    def activity(self, days: int = 365) -> dict:
        since = (date.today() - timedelta(days=days)).isoformat()
        return {r["day"]: dict(r) for r in self.db.execute(
            "SELECT * FROM activity WHERE day>=? ORDER BY day", (since,))}

    def active_days(self) -> list:
        return [r["day"] for r in self.db.execute(
            "SELECT day FROM activity WHERE minutes>0 OR items>0 OR reviews>0 "
            "OR exercises>0 ORDER BY day")]

    def streak(self):
        """(current, longest) run of consecutive active days."""
        days = self.active_days()
        if not days:
            return 0, 0
        seen = set()
        for d in days:
            try:
                seen.add(date.fromisoformat(d))
            except ValueError:
                continue
        if not seen:
            return 0, 0
        longest = run = 0
        prev = None
        for d in sorted(seen):
            run = run + 1 if prev is not None and (d - prev).days == 1 else 1
            longest = max(longest, run)
            prev = d
        today = date.today()
        anchor = today if today in seen else today - timedelta(days=1)
        if anchor not in seen:
            return 0, longest
        current = 0
        while anchor in seen:
            current += 1
            anchor -= timedelta(days=1)
        return current, longest

    # -- bulk export and import --------------------------------------------

    TABLES = ("checks", "ratings", "notes", "logs", "srs", "reviews",
              "quiz_attempts", "exercise_state", "project_state", "cert_state",
              "activity", "settings", "meta")

    def dump(self) -> dict:
        out = {
            "app": "operators-console",
            "schema": SCHEMA_VERSION,
            "exported_at": _now(),
            "tables": {},
        }
        for table in self.TABLES:
            out["tables"][table] = [
                dict(r) for r in self.db.execute("SELECT * FROM " + table)]
        return out

    def restore(self, payload: dict) -> None:
        """Replace all learner data with a previous dump()."""
        if payload.get("app") != "operators-console":
            raise ValueError(
                "That file was not exported by this application.")
        schema = int(payload.get("schema", 0))
        if schema > SCHEMA_VERSION:
            raise ValueError(
                "Backup schema %d is newer than this build (%d)."
                % (schema, SCHEMA_VERSION))
        tables = payload.get("tables") or {}
        self.backup(tag="pre-restore")
        with self.tx():
            for table in self.TABLES:
                self.db.execute("DELETE FROM " + table)
            for table in self.TABLES:
                rows = tables.get(table) or []
                if not rows:
                    continue
                cols = [c[1] for c in self.db.execute(
                    "PRAGMA table_info(%s)" % table)]
                usable = [c for c in cols if c in rows[0]]
                if not usable:
                    continue
                placeholders = ",".join("?" for _ in usable)
                self.db.executemany(
                    "INSERT OR REPLACE INTO %s (%s) VALUES (%s)"
                    % (table, ",".join(usable), placeholders),
                    [tuple(r.get(c) for c in usable) for r in rows])
        self.set_meta("schema_version", str(SCHEMA_VERSION))

    def reset_progress(self) -> None:
        """Wipe learner data but keep settings. Always backs up first."""
        self.backup(tag="pre-reset")
        with self.tx():
            for table in ("checks", "ratings", "notes", "logs", "srs",
                          "reviews", "quiz_attempts", "exercise_state",
                          "project_state", "cert_state", "activity"):
                self.db.execute("DELETE FROM " + table)
