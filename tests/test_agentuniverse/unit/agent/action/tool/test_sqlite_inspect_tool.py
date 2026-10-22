# All SQL in this file is fixed fixture DDL or whitelisted PRAGMA text; nothing is
# built from untrusted input.
# ruff: noqa: S608

import hashlib
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool import sqlite_inspect_tool as inspect_module
from agentuniverse.agent.action.tool.common_tool.sqlite_inspect_tool import SqliteInspectTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(inspect_module.__file__), "sqlite_inspect_tool.yaml")

WITHOUT_ROWID = re.compile(r"\bWITHOUT\s+ROWID\b", re.IGNORECASE)
TIMING = re.compile(r"\b(BEFORE|AFTER|INSTEAD\s+OF)\b", re.IGNORECASE)
EVENT = re.compile(r"\b(INSERT|UPDATE|DELETE)\b", re.IGNORECASE)


def build_database(path, script, journal_mode=None, application_id=None, user_version=None):
    """Create a real SQLite database from CREATE/INSERT statements."""
    conn = sqlite3.connect(path)
    try:
        if journal_mode:
            conn.execute(f"PRAGMA journal_mode={journal_mode}")
        if application_id is not None:
            conn.execute(f"PRAGMA application_id={application_id}")
        if user_version is not None:
            conn.execute(f"PRAGMA user_version={user_version}")
        conn.executescript(script)
        conn.commit()
    finally:
        conn.close()


def direct_columns(conn, table):
    """Oracle column inventory: raw PRAGMA table_info rows."""
    return [
        {"name": r[1], "type": r[2], "notnull": bool(r[3]), "default": r[4], "pk_index": int(r[5])}
        for r in conn.execute(f'PRAGMA table_info("{table}")')
    ]


def direct_indexes(conn):
    """Oracle index inventory: raw PRAGMA index_list/index_xinfo rows for every table."""
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    result = []
    for table in tables:
        for r in conn.execute(f'PRAGMA index_list("{table}")'):
            columns = [
                (str(x[2]) if x[2] is not None else "(expression)")
                for x in conn.execute(f'PRAGMA index_xinfo("{r[1]}")')
                if int(x[5]) == 1
            ]
            result.append(
                {
                    "table": table,
                    "name": str(r[1]),
                    "unique": bool(r[2]),
                    "origin": str(r[3]),
                    "partial": bool(r[4]),
                    "columns": columns,
                }
            )
    return result


def direct_trigger_shape(sql):
    timing_match = TIMING.search(sql)
    after = timing_match.end() if timing_match else 0
    event_match = EVENT.search(sql, after)
    timing = re.sub(r"\s+", " ", timing_match.group(1)).upper() if timing_match else ""
    event = event_match.group(1).upper() if event_match else ""
    return timing, event


def snapshot(path):
    """Content hash plus mtime for the read-only guarantee checks."""
    with open(path, "rb") as stream:
        data = stream.read()
    return hashlib.sha256(data).hexdigest(), os.stat(path).st_mtime_ns, len(data)


RICH_SCRIPT = """
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT);
CREATE TABLE codes (code TEXT PRIMARY KEY, label TEXT);
CREATE TABLE pairs (a TEXT, b TEXT, PRIMARY KEY (a, b)) WITHOUT ROWID;
CREATE TABLE events (id INTEGER, kind TEXT, note TEXT);
CREATE TABLE accounts (username TEXT UNIQUE, region TEXT);
CREATE INDEX idx_events_kind ON events (kind);
CREATE INDEX idx_events_partial ON events (id) WHERE kind = 'login';
CREATE UNIQUE INDEX idx_accounts_username ON accounts (username);
CREATE VIEW active_users AS SELECT id, name FROM users WHERE id > 0;
CREATE VIEW schema_qualified AS SELECT main.users.id FROM main.users;
CREATE TRIGGER trg_log_insert AFTER INSERT ON users
BEGIN INSERT INTO events (id, kind, note) VALUES (new.id, 'insert', 'user'); END;
CREATE TRIGGER trg_users_touch AFTER UPDATE ON users
BEGIN UPDATE users SET email = email WHERE id = old.id; END;
"""


class SqliteInspectToolTest(unittest.TestCase):
    """Unit tests for SqliteInspectTool schema/audit/integrity/compact modes."""

    def setUp(self):
        """Create a temp directory and a tool scoped to it."""
        self.directory = tempfile.TemporaryDirectory()
        self.tool = SqliteInspectTool(base_dir=self.directory.name)
        self.rich = self.make("rich.db", RICH_SCRIPT)

    def tearDown(self):
        """Remove the temporary working directory."""
        self.directory.cleanup()

    def make(self, name, script, **kwargs):
        """Build a database inside the temp directory from real SQL."""
        path = os.path.join(self.directory.name, name)
        build_database(path, script, **kwargs)
        return path

    # ------------------------------------------------------------------ schema

    def test_schema_mode_inventory(self):
        """Verify schema mode returns tables, views, indexes, and triggers with full detail."""
        result = self.tool.execute(mode="schema", db_path="rich.db")
        self.assertEqual(result["status"], "success")
        tables = {t["name"]: t for t in result["tables"]}
        self.assertTrue(tables["users"]["rowid"])
        self.assertTrue(tables["codes"]["rowid"])
        self.assertFalse(tables["pairs"]["rowid"])
        self.assertEqual(
            tables["users"]["columns"],
            [
                {"name": "id", "type": "INTEGER", "notnull": False, "default": None, "pk_index": 1},
                {"name": "name", "type": "TEXT", "notnull": True, "default": None, "pk_index": 0},
                {"name": "email", "type": "TEXT", "notnull": False, "default": None, "pk_index": 0},
            ],
        )
        self.assertEqual(tables["pairs"]["columns"][0]["pk_index"], 1)
        self.assertEqual(tables["pairs"]["columns"][1]["pk_index"], 2)
        self.assertEqual([v["name"] for v in result["views"]], ["active_users", "schema_qualified"])
        indexes = {i["name"]: i for i in result["indexes"]}
        self.assertEqual(indexes["idx_events_kind"]["origin"], "c")
        self.assertEqual(indexes["idx_events_kind"]["origin_description"], "create_index")
        self.assertEqual(indexes["idx_events_kind"]["columns"], ["kind"])
        self.assertFalse(indexes["idx_events_kind"]["partial"])
        self.assertTrue(indexes["idx_events_partial"]["partial"])
        self.assertEqual(indexes["sqlite_autoindex_accounts_1"]["origin"], "u")
        self.assertEqual(indexes["sqlite_autoindex_pairs_1"]["origin"], "pk")
        self.assertEqual(indexes["sqlite_autoindex_pairs_1"]["columns"], ["a", "b"])
        self.assertIsNone(indexes["sqlite_autoindex_pairs_1"]["sql"])
        triggers = {t["name"]: t for t in result["triggers"]}
        self.assertEqual(triggers["trg_log_insert"]["table"], "users")
        self.assertEqual(triggers["trg_log_insert"]["timing"], "AFTER")
        self.assertEqual(triggers["trg_log_insert"]["event"], "INSERT")
        self.assertEqual(triggers["trg_users_touch"]["event"], "UPDATE")
        self.assertEqual(
            result["total_object_count"],
            result["table_count"] + result["view_count"] + result["index_count"] + result["trigger_count"],
        )
        self.assertFalse(result["tables_truncated"])
        self.assertEqual(result["table_count"], 5)
        # WITHOUT ROWID primary-key btrees show up in the index listing but
        # are not separate sqlite_master objects, hence the +1 here.
        self.assertEqual(len(result["indexes"]), result["index_count"] + 1)

    def test_schema_matches_direct_pragma_on_rich_database(self):
        """Verify every schema field equals the raw PRAGMA answers on the rich fixture."""
        result = self.tool.execute(mode="schema", db_path="rich.db")
        conn = sqlite3.connect(self.rich)
        try:
            rows = conn.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY name").fetchall()
            expected_tables = [
                {
                    "name": r[1],
                    "rowid": WITHOUT_ROWID.search(r[3] or "") is None,
                    "columns": direct_columns(conn, r[1]),
                    "sql": r[3],
                }
                for r in sorted(rows, key=lambda r: r[1])
                if r[0] == "table"
            ]
            self.assertEqual(result["tables"], expected_tables)
            self.assertEqual(result["views"], [{"name": r[1], "sql": r[3]} for r in sorted(rows, key=lambda r: r[1]) if r[0] == "view"])
            expected_indexes = direct_indexes(conn)
            sql_by_name = {r[1]: r[3] for r in rows if r[0] == "index"}
            expected_indexes.sort(key=lambda i: (i["table"], i["name"]))
            actual = sorted(result["indexes"], key=lambda i: (i["table"], i["name"]))
            for got, want in zip(actual, expected_indexes, strict=False):
                self.assertEqual({k: got[k] for k in want}, want)
                self.assertEqual(got["sql"], sql_by_name.get(got["name"]))
            expected_triggers = [
                dict(
                    zip(
                        ("name", "table", "timing", "event", "sql"),
                        (r[1], r[2], *direct_trigger_shape(r[3] or ""), r[3]),
                        strict=False,
                    )
                )
                for r in sorted(rows, key=lambda r: r[1])
                if r[0] == "trigger"
            ]
            self.assertEqual(result["triggers"], expected_triggers)
        finally:
            conn.close()

    # ------------------------------------------------------------------ audit

    def test_audit_mode_findings(self):
        """Verify audit mode reports the expected structural findings and no false positives."""
        result = self.tool.execute(mode="audit", db_path="rich.db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["policy"], "structure-only")
        self.assertFalse(result["data_sampled"])
        codes = {}
        for finding in result["findings"]:
            codes.setdefault(finding["code"], []).append(finding)
        self.assertEqual(
            {f["table"] for f in codes["table_without_primary_key"]}, {"accounts", "events"}
        )
        nullable = {f["table"]: f["columns"] for f in codes["nullable_primary_key_column"]}
        self.assertEqual(nullable, {"codes": ["code"]})
        duplicates = [f for f in codes["duplicate_index"] if f["table"] == "accounts"]
        self.assertEqual(
            sorted(duplicates[0]["indexes"]), ["idx_accounts_username", "sqlite_autoindex_accounts_1"]
        )
        cross = codes["cross_table_trigger_mutation"][0]
        self.assertEqual(cross["object"], "trg_log_insert")
        self.assertEqual(cross["writes_to"], ["events"])
        attached = {f["object"] for f in codes["attached_database_reference"]}
        self.assertIn("schema_qualified", attached)
        self.assertNotIn("trg_users_touch", [f["object"] for f in codes["cross_table_trigger_mutation"]])

    def test_audit_reports_foreign_keys_default_off(self):
        """Verify the foreign-key default-off note appears when constraints are declared."""
        self.make(
            "fk.db",
            "CREATE TABLE parent (id INTEGER PRIMARY KEY);"
            "CREATE TABLE child (pid INTEGER REFERENCES parent(id));",
        )
        result = self.tool.execute(mode="audit", db_path="fk.db")
        self.assertEqual(result["foreign_key_count"], 1)
        finding = next(f for f in result["findings"] if f["code"] == "foreign_keys_enforcement_off_by_default")
        self.assertEqual(finding["foreign_keys_pragma_state"], 0)

    def test_audit_without_rowid_and_integer_pk_not_flagged(self):
        """Verify WITHOUT ROWID tables and exact INTEGER PRIMARY KEY tables raise no nullable-PK finding."""
        self.make(
            "clean.db",
            "CREATE TABLE wr (a TEXT PRIMARY KEY) WITHOUT ROWID;"
            "CREATE TABLE plain (id INTEGER PRIMARY KEY, v TEXT);",
        )
        result = self.tool.execute(mode="audit", db_path="clean.db")
        self.assertNotIn("nullable_primary_key_column", [f["code"] for f in result["findings"]])
        self.assertNotIn("table_without_primary_key", [f["code"] for f in result["findings"]])

    def test_audit_flags_int_primary_key_nullable_footgun(self):
        """Verify INT (not INTEGER) single-column PRIMARY KEY is reported as nullable."""
        self.make("intpk.db", "CREATE TABLE t (a INT PRIMARY KEY);")
        result = self.tool.execute(mode="audit", db_path="intpk.db")
        finding = result["findings"][0]
        self.assertEqual(finding["code"], "nullable_primary_key_column")
        self.assertEqual(finding["columns"], ["a"])

    # ------------------------------------------------------------------ integrity

    def test_integrity_mode_healthy_database(self):
        """Verify integrity verdicts and header pragmas on a healthy database."""
        self.make(
            "meta.db",
            "CREATE TABLE t (a INTEGER PRIMARY KEY); INSERT INTO t VALUES (1),(2);",
            application_id=1094861636,
            user_version=42,
        )
        result = self.tool.execute(mode="integrity", db_path="meta.db")
        self.assertEqual(result["integrity_check"], "ok")
        self.assertEqual(result["quick_check"], "ok")
        self.assertEqual(result["integrity_errors"], [])
        self.assertEqual(result["foreign_key_violations"], [])
        self.assertEqual(result["journal_mode"], "delete")
        self.assertEqual(result["user_version"], 42)
        self.assertEqual(result["application_id"], 1094861636)
        self.assertGreater(result["page_count"], 0)

    def test_integrity_reads_wal_database_read_only(self):
        """Verify a cleanly closed WAL database is inspected read-only and reports WAL mode."""
        self.make("wal.db", "CREATE TABLE t (a); INSERT INTO t VALUES (1);", journal_mode="wal")
        result = self.tool.execute(mode="integrity", db_path="wal.db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["journal_mode"], "wal")
        self.assertEqual(result["integrity_check"], "ok")

    def test_integrity_vacuum_candidate_and_parity(self):
        """Verify freelist accounting matches direct PRAGMA answers and flags reclaimable pages."""
        path = self.make(
            "churn.db",
            "CREATE TABLE t (a INTEGER PRIMARY KEY, b TEXT);"
            + "".join(f"INSERT INTO t (b) VALUES ('{'x' * 200}{i:06d}');" for i in range(6000))
            + "DELETE FROM t WHERE a BETWEEN 500 AND 5500;",
        )
        result = self.tool.execute(mode="integrity", db_path="churn.db")
        conn = sqlite3.connect(path)
        try:
            freelist = conn.execute("PRAGMA freelist_count").fetchone()[0]
            pages = conn.execute("PRAGMA page_count").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(result["freelist_count"], freelist)
        self.assertEqual(result["page_count"], pages)
        self.assertGreater(freelist, 0)
        self.assertTrue(result["vacuum_candidate"])
        self.assertEqual(result["freelist_bytes"], freelist * result["page_size"])

    def test_integrity_fk_violations_bounded(self):
        """Verify foreign_key_check violations are mapped and bounded."""
        script = (
            "CREATE TABLE parent (id INTEGER PRIMARY KEY);"
            "CREATE TABLE child (pid INTEGER REFERENCES parent(id));"
            + "".join(f"INSERT INTO child VALUES ({i});" for i in range(1, 41))
        )
        self.make("fkv.db", script)
        result = self.tool.execute(mode="integrity", db_path="fkv.db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["foreign_key_violations"]), 30)
        self.assertTrue(result["foreign_key_violations_truncated"])
        first = result["foreign_key_violations"][0]
        self.assertEqual(first["table"], "child")
        self.assertEqual(first["parent_table"], "parent")
        self.assertEqual(
            first["fk_definition"], {"parent_table": "parent", "from_column": "pid", "to_column": "id"}
        )
        self.assertEqual(first["rowid"], 1)

    # ------------------------------------------------------------------ compact

    def test_compact_mode(self):
        """Verify compact mode reports file/page math and excludes row estimates."""
        path = self.make(
            "c.db", "CREATE TABLE t (a INTEGER PRIMARY KEY, b TEXT, c REAL); INSERT INTO t VALUES (1,'x',2);"
        )
        result = self.tool.execute(mode="compact", db_path="c.db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file_size"], os.path.getsize(path))
        self.assertEqual(result["tables"], [{"name": "t", "column_count": 3}])
        self.assertEqual(result["used_bytes_estimate"], (result["page_count"] - result["freelist_count"]) * result["page_size"])
        self.assertIn("excluded", result["row_estimates"])

    # ------------------------------------------------------------------ read-only guarantee

    def test_read_only_guarantee_across_hundred_runs(self):
        """Verify file content and mtime never change across 100 executions of every mode."""
        self.make("data.db", RICH_SCRIPT + "INSERT INTO users (name) VALUES ('a');")
        self.make("waldata.db", RICH_SCRIPT, journal_mode="wal")
        before = (snapshot(os.path.join(self.directory.name, "data.db")),
                  snapshot(os.path.join(self.directory.name, "waldata.db")))
        modes = ("schema", "audit", "integrity", "compact")
        for i in range(100):
            name = "data.db" if i % 2 == 0 else "waldata.db"
            result = self.tool.execute(mode=modes[i % 4], db_path=name)
            self.assertEqual(result["status"], "success", result)
        after = (snapshot(os.path.join(self.directory.name, "data.db")),
                 snapshot(os.path.join(self.directory.name, "waldata.db")))
        self.assertEqual(before, after)

    # ------------------------------------------------------------------ error mapping

    def test_error_missing_file(self):
        """Verify a missing database path is a structured validation error."""
        result = self.tool.execute(mode="schema", db_path="ghost.db")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("does not exist", result["error"])

    def test_error_garbage_file(self):
        """Verify a non-SQLite file is reported as an invalid database."""
        with open(os.path.join(self.directory.name, "garbage.db"), "wb") as stream:
            stream.write(b"this is definitely not a sqlite database" * 8)
        result = self.tool.execute(mode="schema", db_path="garbage.db")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "invalid_database")
        self.assertIn("file is not a database", result["error"])

    def test_error_locked_database(self):
        """Verify a database locked by another process is reported as a structured lock error."""
        path = self.make("locked.db", "CREATE TABLE t(a); INSERT INTO t VALUES (1);")
        script = (
            "import sqlite3, time\n"
            f"conn = sqlite3.connect({path!r})\n"
            "conn.execute('BEGIN EXCLUSIVE')\n"
            "print('ready', flush=True)\n"
            "time.sleep(20)\n"
        )
        proc = subprocess.Popen(  # noqa: S603 - fixed interpreter and script, no untrusted input
            [sys.executable, "-c", script], stdout=subprocess.PIPE
        )
        try:
            self.assertEqual(proc.stdout.readline().decode().strip(), "ready")
            tool = SqliteInspectTool(base_dir=self.directory.name, lock_timeout=0.5)
            result = tool.execute(mode="schema", db_path="locked.db")
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error_type"], "database_locked")
        finally:
            proc.stdout.close()
            proc.kill()
            proc.wait()

    def test_empty_file_is_valid_empty_database(self):
        """Verify a zero-byte file is pinned as a valid empty database."""
        open(os.path.join(self.directory.name, "empty.db"), "wb").close()
        schema = self.tool.execute(mode="schema", db_path="empty.db")
        self.assertEqual(schema["status"], "success")
        self.assertEqual(schema["tables"], [])
        self.assertEqual(schema["total_object_count"], 0)
        integrity = self.tool.execute(mode="integrity", db_path="empty.db")
        self.assertEqual(integrity["integrity_check"], "ok")
        self.assertEqual(integrity["page_count"], 0)
        compact = self.tool.execute(mode="compact", db_path="empty.db")
        self.assertEqual(compact["status"], "success")
        self.assertEqual(compact["file_size"], 0)

    def test_validation_errors(self):
        """Verify mode, path, and tunable validation produce structured errors."""
        self.assertEqual(self.tool.execute(mode="query", db_path="rich.db")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="schema", db_path="")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="schema", db_path=5)["error_type"], "validation_error")
        self.assertIn(
            "escapes the allowed directory",
            self.tool.execute(mode="schema", db_path="../outside.db")["error"],
        )
        small = SqliteInspectTool(base_dir=self.directory.name, max_read_bytes=16)
        self.assertEqual(small.execute(mode="schema", db_path="rich.db")["error_type"], "validation_error")
        broken = SqliteInspectTool(base_dir=self.directory.name, max_objects=0)
        self.assertEqual(broken.execute(mode="schema", db_path="rich.db")["error_type"], "validation_error")

    # ------------------------------------------------------------------ caps and pathological input

    def test_schema_listing_cap(self):
        """Verify schema mode bounds listing size while reporting exact totals."""
        script = "".join(f"CREATE TABLE bulk{i:05d} (a INTEGER, b TEXT);" for i in range(2501))
        self.make("bulk.db", script)
        result = self.tool.execute(mode="schema", db_path="bulk.db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["tables"]), 2000)
        self.assertEqual(result["table_count"], 2501)
        self.assertTrue(result["tables_truncated"])
        self.assertEqual(result["total_object_count"], 2501)

    def test_audit_findings_cap(self):
        """Verify audit mode bounds finding count and reports truncation."""
        script = "".join(f"CREATE TABLE nopk{i:04d} (a TEXT);" for i in range(150))
        self.make("nopk.db", script)
        result = self.tool.execute(mode="audit", db_path="nopk.db")
        self.assertEqual(result["finding_count"], 100)
        self.assertTrue(result["findings_truncated"])
        self.assertEqual({f["code"] for f in result["findings"]}, {"table_without_primary_key"})

    def test_sql_text_bounded_on_one_megabyte_statement(self):
        """Verify a 1MB CREATE statement is truncated, not returned in full."""
        big = "CREATE VIEW huge AS SELECT " + " " * (1024 * 1024) + "1"
        self.make("huge.db", big + "; CREATE TABLE t (a);")
        result = self.tool.execute(mode="schema", db_path="huge.db")
        self.assertEqual(result["status"], "success")
        view = next(v for v in result["views"] if v["name"] == "huge")
        self.assertEqual(len(view["sql"]), 16384)
        self.assertEqual(result["truncated_sql_objects"], ["huge"])
        audit = self.tool.execute(mode="audit", db_path="huge.db")
        self.assertEqual(audit["status"], "success")
        for finding in audit["findings"]:
            self.assertLess(len(str(finding)), 4096)

    def test_pathological_ten_thousand_tables(self):
        """Verify a 10k-table database is bounded in output and completes quickly."""
        script = "".join(f"CREATE TABLE many{i:05d} (a INTEGER);" for i in range(10000))
        self.make("many.db", script)
        schema = self.tool.execute(mode="schema", db_path="many.db")
        self.assertEqual(schema["status"], "success")
        self.assertTrue(schema["tables_truncated"])
        self.assertEqual(schema["table_count"], 10000)
        self.assertEqual(schema["total_object_count"], 10000)
        audit = self.tool.execute(mode="audit", db_path="many.db")
        self.assertEqual(audit["status"], "success")
        self.assertLessEqual(audit["finding_count"], 100)
        self.assertEqual(audit["table_count"], 10000)

    def test_repeated_calls_are_deterministic(self):
        """Verify repeated identical calls return deep-equal results."""
        for mode in ("schema", "audit", "integrity", "compact"):
            first = self.tool.execute(mode=mode, db_path="rich.db")
            second = self.tool.execute(mode=mode, db_path="rich.db")
            self.assertEqual(first, second)


class SqliteInspectOracleTest(unittest.TestCase):
    """Oracle battery: 200 seeded databases checked field-by-field against raw PRAGMA answers."""

    def setUp(self):
        """Create a temp directory and a tool scoped to it."""
        self.directory = tempfile.TemporaryDirectory()
        self.tool = SqliteInspectTool(base_dir=self.directory.name)

    def tearDown(self):
        """Remove the temporary working directory."""
        self.directory.cleanup()

    BIT_FEATURES = (
        (
            1,
            "CREATE TABLE intpk (id INTEGER PRIMARY KEY, v TEXT); INSERT INTO intpk (v) VALUES ('x');",
        ),
        (
            2,
            "CREATE TABLE footgun (code TEXT PRIMARY KEY, v TEXT); INSERT INTO footgun VALUES ('k', 'v');",
        ),
        (
            4,
            "CREATE TABLE wr (a TEXT, b INT, PRIMARY KEY (a, b)) WITHOUT ROWID; INSERT INTO wr VALUES ('a', 1);",
        ),
        (8, "CREATE TABLE nopk (a TEXT); INSERT INTO nopk VALUES ('z');"),
        (
            16,
            "CREATE TABLE ix (a INT, b TEXT); INSERT INTO ix VALUES (1, 'p'), (2, 'q'); "
            "CREATE INDEX ix_a ON ix (a); CREATE INDEX ix_part ON ix (b) WHERE b = 'p';",
        ),
        (
            32,
            "CREATE TABLE uniq (u TEXT UNIQUE, v INT); "
            "CREATE UNIQUE INDEX uniq_dup ON uniq (u); INSERT INTO uniq VALUES ('u1', 1);",
        ),
        (
            64,
            "CREATE TABLE t_a (id INTEGER PRIMARY KEY); CREATE TABLE t_b (note TEXT); INSERT INTO t_a VALUES (1); "
            "CREATE TRIGGER t_a_log AFTER INSERT ON t_a BEGIN INSERT INTO t_b VALUES ('x'); END;",
        ),
        (
            128,
            "CREATE TABLE self (id INTEGER PRIMARY KEY, hits INT DEFAULT 0); CREATE TRIGGER self_touch "
            "AFTER UPDATE ON self BEGIN UPDATE self SET hits = hits + 1 WHERE id = old.id; END;",
        ),
    )

    EXTRA_FEATURES = (
        (
            lambda index: index % 7 == 0,
            "CREATE TABLE fk_p (id INTEGER PRIMARY KEY); CREATE TABLE fk_c (pid INT REFERENCES fk_p(id)); "
            "INSERT INTO fk_p VALUES (1); INSERT INTO fk_c VALUES (1), (999);",
        ),
        (
            lambda index: index % 13 == 0,
            "CREATE TABLE always (id INTEGER PRIMARY KEY); "
            "CREATE VIEW aux_view AS SELECT main.always.id FROM main.always;",
        ),
        (
            lambda index: index % 11 == 0,
            "CREATE TABLE late (a TEXT, b TEXT, PRIMARY KEY (a, b)) WITHOUT ROWID;",
        ),
    )

    @classmethod
    def script_for(cls, index):
        """Deterministically compose a CREATE/INSERT script exercising a feature subset."""
        parts = [sql for mask, sql in cls.BIT_FEATURES if index & mask]
        parts.extend(sql for predicate, sql in cls.EXTRA_FEATURES if predicate(index))
        return " ".join(parts)

    def build(self, index):
        """Build one seeded database file and return its path."""
        path = os.path.join(self.directory.name, f"seed{index:03d}.db")
        build_database(
            path,
            self.script_for(index),
            journal_mode="wal" if index % 25 == 0 else None,
            user_version=index,
        )
        return path

    def assert_schema_parity(self, path):
        """Assert every schema-mode field equals the direct PRAGMA answers."""
        result = self.tool.execute(mode="schema", db_path=os.path.basename(path))
        self.assertEqual(result["status"], "success", result)
        conn = sqlite3.connect(path)
        try:
            rows = sorted(
                conn.execute("SELECT type, name, tbl_name, sql FROM sqlite_master").fetchall(),
                key=lambda r: r[1],
            )
            expected_tables = [
                {
                    "name": r[1],
                    "rowid": WITHOUT_ROWID.search(r[3] or "") is None,
                    "columns": direct_columns(conn, r[1]),
                    "sql": r[3],
                }
                for r in rows
                if r[0] == "table"
            ]
            self.assertEqual(result["tables"], expected_tables)
            self.assertEqual(
                result["views"], [{"name": r[1], "sql": r[3]} for r in rows if r[0] == "view"]
            )
            sql_by_name = {r[1]: r[3] for r in rows if r[0] == "index"}
            expected_indexes = sorted(direct_indexes(conn), key=lambda i: (i["table"], i["name"]))
            actual = sorted(result["indexes"], key=lambda i: (i["table"], i["name"]))
            self.assertEqual(len(actual), len(expected_indexes))
            for got, want in zip(actual, expected_indexes, strict=False):
                self.assertEqual({k: got[k] for k in want}, want)
                self.assertEqual(got["sql"], sql_by_name.get(got["name"]))
            expected_triggers = [
                {
                    "name": r[1],
                    "table": r[2],
                    "timing": direct_trigger_shape(r[3] or "")[0],
                    "event": direct_trigger_shape(r[3] or "")[1],
                    "sql": r[3],
                }
                for r in rows
                if r[0] == "trigger"
            ]
            self.assertEqual(result["triggers"], expected_triggers)
            self.assertEqual(result["total_object_count"], len(rows))
        finally:
            conn.close()
        return result

    def assert_integrity_parity(self, path):
        """Assert integrity-mode verdicts and violation lists equal the direct PRAGMA answers."""
        result = self.tool.execute(mode="integrity", db_path=os.path.basename(path))
        self.assertEqual(result["status"], "success", result)
        conn = sqlite3.connect(path)
        try:
            integrity = [str(r[0]) for r in conn.execute("PRAGMA integrity_check") if str(r[0]) != "ok"]
            quick = [str(r[0]) for r in conn.execute("PRAGMA quick_check") if str(r[0]) != "ok"]
            violations = conn.execute("PRAGMA foreign_key_check").fetchall()
            self.assertEqual(result["integrity_check"], integrity[0] if integrity else "ok")
            self.assertEqual(result["integrity_errors"], integrity[:20])
            self.assertEqual(result["quick_check"], quick[0] if quick else "ok")
            self.assertEqual(result["quick_check_errors"], quick[:20])
            self.assertEqual(result["journal_mode"], str(conn.execute("PRAGMA journal_mode").fetchone()[0]))
            self.assertEqual(result["page_count"], conn.execute("PRAGMA page_count").fetchone()[0])
            self.assertEqual(result["freelist_count"], conn.execute("PRAGMA freelist_count").fetchone()[0])
            self.assertEqual(result["page_size"], conn.execute("PRAGMA page_size").fetchone()[0])
            self.assertEqual(len(result["foreign_key_violations"]), min(len(violations), 30))
            self.assertEqual(result["foreign_key_violations_truncated"], len(violations) > 30)
            definitions = {}
            for row in violations[:30]:
                table, fkid = str(row[0]), int(row[3])
                if table not in definitions:
                    definitions[table] = conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
                match = next(d for d in definitions[table] if int(d[0]) == fkid)
                self.assertEqual(
                    {
                        "table": str(row[0]),
                        "rowid": row[1],
                        "parent_table": str(row[2]),
                        "fk_definition": {
                            "parent_table": str(match[2]),
                            "from_column": str(match[3]),
                            "to_column": None if match[4] is None else str(match[4]),
                        },
                    },
                    next(v for v in result["foreign_key_violations"] if v["table"] == table and v["rowid"] == row[1]),
                )
            self.assertEqual(result["user_version"], int(re.sub(r"\D", "", os.path.basename(path))))
        finally:
            conn.close()
        return result

    def test_two_hundred_seeded_databases_schema_and_integrity_parity(self):
        """Verify 200 real seeded databases match the engine's own answers field by field."""
        for index in range(200):
            with self.subTest(index=index):
                path = self.build(index)
                schema = self.assert_schema_parity(path)
                conn = sqlite3.connect(path)
                try:
                    counts = {
                        t: conn.execute("SELECT count(*) FROM sqlite_master WHERE type=?", (t,)).fetchone()[0]
                        for t in ("table", "view", "index", "trigger")
                    }
                finally:
                    conn.close()
                self.assertEqual(schema["table_count"], counts["table"])
                self.assertEqual(schema["view_count"], counts["view"])
                self.assertEqual(schema["index_count"], counts["index"])
                self.assertEqual(schema["trigger_count"], counts["trigger"])
                self.assertEqual(
                    schema["total_object_count"], sum(counts.values())
                )
                self.assert_integrity_parity(path)
                audit = self.tool.execute(mode="audit", db_path=os.path.basename(path))
                self.assertEqual(audit["status"], "success")
                self.assertFalse(audit["data_sampled"])
                codes = {f["code"] for f in audit["findings"]}
                expected_no_pk = bool(index & 8 or index & 16 or index & 32 or index & 64 or index % 7 == 0)
                self.assertEqual("table_without_primary_key" in codes, expected_no_pk)
                self.assertEqual("nullable_primary_key_column" in codes, bool(index & 2))
                self.assertEqual("foreign_keys_enforcement_off_by_default" in codes, index % 7 == 0)
                self.assertEqual("cross_table_trigger_mutation" in codes, bool(index & 64))
                self.assertEqual("duplicate_index" in codes, bool(index & 32))
                self.assertEqual("attached_database_reference" in codes, index % 13 == 0)
                os.remove(path)

    def test_foreign_key_check_parity_thirty_databases(self):
        """Verify foreign_key_check parity on 30 databases with deliberate violations."""
        for index in range(30):
            with self.subTest(index=index):
                kind = index % 3
                if kind == 0:
                    script = (
                        "CREATE TABLE p (id INTEGER PRIMARY KEY);"
                        "CREATE TABLE c (pid INT REFERENCES p(id));"
                        "INSERT INTO p VALUES (1); INSERT INTO c VALUES (1), (50), (51);"
                    )
                elif kind == 1:
                    script = (
                        "CREATE TABLE p (a INT, b INT, PRIMARY KEY (a, b));"
                        "CREATE TABLE c (x INT, y INT, FOREIGN KEY (x, y) REFERENCES p (a, b));"
                        "INSERT INTO p VALUES (1, 1); INSERT INTO c VALUES (1, 1), (7, 8);"
                    )
                else:
                    script = (
                        "CREATE TABLE p (id INTEGER PRIMARY KEY);"
                        "CREATE TABLE c (pid INT REFERENCES p(id), note TEXT, PRIMARY KEY (pid, note)) WITHOUT ROWID;"
                        "INSERT INTO p VALUES (2); INSERT INTO c VALUES (2, 'ok'), (404, 'bad');"
                    )
                path = os.path.join(self.directory.name, f"fk{index:02d}.db")
                build_database(path, script)
                result = self.tool.execute(mode="integrity", db_path=os.path.basename(path))
                conn = sqlite3.connect(path)
                try:
                    direct = conn.execute("PRAGMA foreign_key_check").fetchall()
                    fk_rows = conn.execute('PRAGMA foreign_key_list("c")').fetchall()
                finally:
                    conn.close()
                self.assertEqual(len(result["foreign_key_violations"]), len(direct))
                for got, want in zip(result["foreign_key_violations"], direct, strict=False):
                    match = next(d for d in fk_rows if int(d[0]) == int(want[3]))
                    self.assertEqual(
                        got,
                        {
                            "table": str(want[0]),
                            "rowid": want[1],
                            "parent_table": str(want[2]),
                            "fk_definition": {
                                "parent_table": str(match[2]),
                                "from_column": str(match[3]),
                                "to_column": None if match[4] is None else str(match[4]),
                            },
                        },
                    )
                self.assertEqual(result["integrity_check"], "ok")
                os.remove(path)

    def test_corrupted_database_parity(self):
        """Verify byte-flipped databases surface integrity problems identical to direct PRAGMA output."""
        path = os.path.join(self.directory.name, "corrupt-base.db")
        build_database(
            path,
            "CREATE TABLE t1 (a INTEGER PRIMARY KEY, b TEXT);"
            "CREATE TABLE t2 (c TEXT, d REAL);"
            "CREATE INDEX i2 ON t2 (c);"
            + "".join(f"INSERT INTO t1 (b) VALUES ('row{i:05d}');" for i in range(400))
            + "".join(f"INSERT INTO t2 VALUES ('k{i:05d}', {i}.5);" for i in range(400)),
        )
        with open(path, "rb") as stream:
            original = stream.read()
        surfaced = 0
        try:
            for offset in (len(original) // 2, len(original) * 3 // 4, 105, 4096 + 21):
                if offset >= len(original):
                    continue
                corrupted = bytearray(original)
                corrupted[offset] ^= 0xFF
                corrupted_path = os.path.join(self.directory.name, "corrupt.db")
                with open(corrupted_path, "wb") as stream:
                    stream.write(bytes(corrupted))
                result = self.tool.execute(mode="integrity", db_path="corrupt.db")
                try:
                    conn = sqlite3.connect(f"file:{corrupted_path}?mode=ro", uri=True)
                    try:
                        direct = [str(r[0]) for r in conn.execute("PRAGMA integrity_check") if str(r[0]) != "ok"]
                    finally:
                        conn.close()
                except sqlite3.DatabaseError as exc:
                    direct = None
                    direct_message = str(exc)
                if direct is None:
                    self.assertEqual(result["status"], "error", offset)
                    self.assertEqual(result["error"], direct_message)
                else:
                    self.assertEqual(result["status"], "success", offset)
                    self.assertEqual(result["integrity_check"], direct[0] if direct else "ok")
                    self.assertEqual(result["integrity_errors"], direct[:20])
                    if direct:
                        surfaced += 1
        finally:
            os.remove(path)
        self.assertGreater(surfaced, 0, "at least one flipped byte must surface an integrity problem")


class SqliteInspectHostileReviewRegressionTest(unittest.TestCase):
    """Regressions found by a fresh hostile probe battery (independent seeds and oracles)."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = SqliteInspectTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def make(self, name, script, **kwargs):
        path = os.path.join(self.directory.name, name)
        build_database(path, script, **kwargs)
        return path

    def test_column_level_integer_pk_desc_is_flagged_nullable(self):
        """Column-level 'INTEGER PRIMARY KEY DESC' is not a rowid alias; the engine stores NULLs, so audit must flag it."""
        path = self.make("desc.db", "CREATE TABLE t (a INTEGER PRIMARY KEY DESC, v TEXT);")
        # Prove the footgun is real: two rows with NULL in the PRIMARY KEY column.
        conn = sqlite3.connect(path)
        conn.execute("INSERT INTO t (v) VALUES ('x'), ('y')")
        stored = conn.execute("SELECT a FROM t").fetchall()
        conn.commit()
        conn.close()
        self.assertEqual(stored, [(None,), (None,)])
        result = self.tool.execute(mode="audit", db_path="desc.db")
        finding = next(f for f in result["findings"] if f["code"] == "nullable_primary_key_column")
        self.assertEqual(finding["table"], "t")
        self.assertEqual(finding["columns"], ["a"])

    def test_rowid_alias_variants_still_not_flagged(self):
        """ASC / AUTOINCREMENT / table-level PRIMARY KEY(a DESC) all alias the rowid and stay clean."""
        self.make(
            "alias.db",
            "CREATE TABLE a1 (a INTEGER PRIMARY KEY ASC, v TEXT);"
            "CREATE TABLE a2 (a INTEGER PRIMARY KEY AUTOINCREMENT, v TEXT);"
            "CREATE TABLE a3 (a INTEGER, v TEXT, PRIMARY KEY (a DESC));"
            "CREATE TABLE a4 (a INTEGER, v TEXT, PRIMARY KEY (a));",
        )
        result = self.tool.execute(mode="audit", db_path="alias.db")
        self.assertNotIn("nullable_primary_key_column", [f["code"] for f in result["findings"]])


class SqliteInspectRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped sqlite_inspect_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the SqliteInspectTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "SqliteInspectTool")

    def test_manager(self):
        """Verify the SqliteInspectTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, SqliteInspectTool)
        self.assertEqual(tool.input_keys, ["mode", "db_path"])
        self.assertEqual(tool.max_objects, 2000)
        self.assertEqual(tool.max_sql_chars, 16384)
        self.assertEqual(tool.lock_timeout, 2.0)
        self.assertEqual(tool.freelist_vacuum_threshold, 64)


if __name__ == "__main__":
    unittest.main()
