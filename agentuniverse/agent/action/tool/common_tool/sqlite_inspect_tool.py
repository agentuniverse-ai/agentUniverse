#!/usr/bin/env python3
"""Read-only SQLite database introspection for agents.

The tool inspects an existing local SQLite database file through a fixed set
of whitelisted metadata queries (the ``sqlite_master`` catalog and PRAGMA
statements). It never executes caller-supplied SQL. The database is always
opened with a ``file:...?mode=ro`` URI, so the engine itself rejects any
write attempt on the handle; the file is never opened read-write and never
created or upgraded by this tool.

Structural analysis is deliberately sample-free: no row values are ever read,
so results stay deterministic and no database content leaks into tool output.
Cardinality- or statistics-based checks are therefore out of scope (they
would require scanning data, which read-only structural inspection refuses).
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import os
import re
import sqlite3
from pathlib import Path
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool


class SqliteInspectTool(Tool):
    """Inventory schemas, audit structure, and judge integrity of a SQLite file read-only."""

    base_dir: str = "."
    max_read_bytes: int = 512 * 1024 * 1024
    max_objects: int = 2000
    max_scan_objects: int = 10000
    max_sql_chars: int = 16384
    max_integrity_findings: int = 20
    max_fk_violations: int = 30
    max_audit_findings: int = 100
    freelist_vacuum_threshold: int = 64
    lock_timeout: float = 2.0

    _MODES: ClassVar[tuple[str, ...]] = ("schema", "audit", "integrity", "compact")
    _ORIGINS: ClassVar[dict[str, str]] = {
        "c": "create_index",
        "pk": "primary_key",
        "u": "unique_constraint",
    }
    _WITHOUT_ROWID: ClassVar[re.Pattern[str]] = re.compile(r"\bWITHOUT\s+ROWID\b", re.IGNORECASE)
    _TIMING: ClassVar[re.Pattern[str]] = re.compile(r"\b(BEFORE|AFTER|INSTEAD\s+OF)\b", re.IGNORECASE)
    _EVENT: ClassVar[re.Pattern[str]] = re.compile(r"\b(INSERT|UPDATE|DELETE)\b", re.IGNORECASE)
    _ATTACH: ClassVar[re.Pattern[str]] = re.compile(r"\bATTACH\b", re.IGNORECASE)
    _QUALIFIED: ClassVar[re.Pattern[str]] = re.compile(
        r"\b[A-Za-z_][A-Za-z0-9_$]*\s*\.\s*[A-Za-z_][A-Za-z0-9_$]*\s*\.\s*[A-Za-z_][A-Za-z0-9_$]*"
    )
    _IDENT = r"(?:\"([^\"]+)\"|`([^`]+)`|\[([^\]]+)\]|([A-Za-z_][A-Za-z0-9_$]*))"
    _WRITES: ClassVar[tuple[re.Pattern[str], ...]] = (
        re.compile(r"\bINSERT\s+INTO\s+" + _IDENT, re.IGNORECASE),
        re.compile(r"\bUPDATE\s+" + _IDENT + r"\s+SET", re.IGNORECASE),
        re.compile(r"\bDELETE\s+FROM\s+" + _IDENT, re.IGNORECASE),
    )

    def execute(self, mode: str, db_path: str) -> dict[str, Any]:
        """Inspect ``db_path`` with one of the four modes and return a structured result."""
        try:
            self._validate_config()
            operation = self._validate_mode(mode)
            path = self._database_path(db_path)
            self._check_file(path)
            if operation == "schema":
                return self._connect(path, self._schema)
            if operation == "audit":
                return self._connect(path, self._audit)
            if operation == "integrity":
                return self._connect(path, self._integrity)
            return self._connect(path, self._compact)
        except (TypeError, ValueError) as exc:
            return self._error(db_path, "validation_error", str(exc))
        except sqlite3.DatabaseError as exc:
            return self._error(db_path, self._database_error_type(exc), str(exc))
        except Exception as exc:
            return self._error(db_path, "operation_error", f"Database inspection failed: {exc}")

    # ------------------------------------------------------------------ plumbing

    @staticmethod
    def _error(path: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "db_path": path}

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_objects",
            "max_scan_objects",
            "max_sql_chars",
            "max_integrity_findings",
            "max_fk_violations",
            "max_audit_findings",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        value = self.freelist_vacuum_threshold
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("freelist_vacuum_threshold must be a non-negative integer")
        if isinstance(self.lock_timeout, bool) or not isinstance(self.lock_timeout, (int, float)):
            raise TypeError("lock_timeout must be a number")
        if self.lock_timeout <= 0:
            raise ValueError("lock_timeout must be positive")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _validate_mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in SqliteInspectTool._MODES:
            raise ValueError("mode must be schema, audit, integrity, or compact")
        return mode

    def _database_path(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("db_path must be a non-empty string")
        return str(resolve_safe_path(value, self.base_dir))

    def _check_file(self, path: str) -> None:
        if not os.path.isfile(path):
            raise ValueError(f"db_path does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"database exceeds max_read_bytes ({self.max_read_bytes})")

    def _connect(self, path: str, inspect: Any) -> dict[str, Any]:
        # mode=ro in the URI is the read-only guarantee: the engine refuses to
        # open the file for writing on this handle and never creates it.
        uri = Path(path).as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=self.lock_timeout)
        try:
            return inspect(conn, path)
        finally:
            conn.close()

    @staticmethod
    def _database_error_type(exc: sqlite3.DatabaseError) -> str:
        text = str(exc).lower()
        if "locked" in text or "busy" in text:
            return "database_locked"
        if "unable to open database file" in text:
            return "unable_to_open"
        if "not a database" in text or "encrypted" in text or "malformed" in text:
            return "invalid_database"
        return "database_error"

    # ------------------------------------------------------------------ catalog helpers

    @staticmethod
    def _catalog(conn: sqlite3.Connection) -> list[tuple[str, str, str, str | None]]:
        rows = conn.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY name").fetchall()
        return [(str(r[0]), str(r[1]), str(r[2]), r[3]) for r in rows]

    @staticmethod
    def _quoted(name: str) -> str:
        if "\x00" in name:
            raise ValueError(f"unusable object name in catalog: {name!r}")
        return '"' + name.replace('"', '""') + '"'

    def _pragma(self, conn: sqlite3.Connection, statement: str) -> list[tuple]:
        return conn.execute(statement).fetchall()

    def _table_info(self, conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
        rows = self._pragma(conn, f"PRAGMA table_info({self._quoted(table)})")
        return [
            {"name": str(r[1]), "type": str(r[2]), "notnull": bool(r[3]), "default": r[4], "pk_index": int(r[5])}
            for r in rows
        ]

    def _index_rows(self, conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
        rows = self._pragma(conn, f"PRAGMA index_list({self._quoted(table)})")
        result: list[dict[str, Any]] = []
        for r in rows:
            name = str(r[1])
            columns = []
            for row in self._pragma(conn, f"PRAGMA index_xinfo({self._quoted(name)})"):
                if int(row[5]) == 1:
                    columns.append(str(row[2]) if row[2] is not None else "(expression)")
            result.append(
                {
                    "table": table,
                    "name": name,
                    "unique": bool(r[2]),
                    "origin": str(r[3]),
                    "partial": bool(r[4]),
                    "columns": columns,
                }
            )
        return result

    def _sql_of(self, sql: str | None) -> tuple[str | None, str | None]:
        if sql is None:
            return None, None
        if len(sql) <= self.max_sql_chars:
            return sql, None
        return sql[: self.max_sql_chars], "truncated"

    def _rowid_table(self, sql: str | None) -> bool:
        # WITHOUT ROWID is only knowable from the stored CREATE text; sql=None
        # (internal objects) is treated as an ordinary rowid table.
        if sql is None:
            return True
        return self._WITHOUT_ROWID.search(sql) is None

    # ------------------------------------------------------------------ schema mode

    def _schema(self, conn: sqlite3.Connection, path: str) -> dict[str, Any]:
        rows = self._catalog(conn)
        tables = [r for r in rows if r[0] == "table"]
        views = [r for r in rows if r[0] == "view"]
        indexes = [r for r in rows if r[0] == "index"]
        triggers = [r for r in rows if r[0] == "trigger"]
        sql_by_index = {r[1]: r[3] for r in indexes}
        truncated_sql: list[str] = []

        table_out: list[dict[str, Any]] = []
        for row in tables[: self.max_objects]:
            columns = self._table_info(conn, row[1])
            sql, marker = self._sql_of(row[3])
            if marker:
                truncated_sql.append(row[1])
            table_out.append({"name": row[1], "rowid": self._rowid_table(row[3]), "columns": columns, "sql": sql})

        view_out: list[dict[str, Any]] = []
        for row in views[: self.max_objects]:
            sql, marker = self._sql_of(row[3])
            if marker:
                truncated_sql.append(row[1])
            view_out.append({"name": row[1], "sql": sql})

        index_out: list[dict[str, Any]] = []
        for row in tables[: self.max_objects]:
            for entry in self._index_rows(conn, row[1]):
                sql, marker = self._sql_of(sql_by_index.get(entry["name"]))
                if marker:
                    truncated_sql.append(entry["name"])
                entry["origin_description"] = self._ORIGINS.get(entry["origin"], entry["origin"])
                entry["sql"] = sql
                index_out.append(entry)

        trigger_out: list[dict[str, Any]] = []
        for row in triggers[: self.max_objects]:
            sql, marker = self._sql_of(row[3])
            if marker:
                truncated_sql.append(row[1])
            timing, event = self._trigger_shape(row[3] or "")
            trigger_out.append({"name": row[1], "table": row[2], "timing": timing, "event": event, "sql": sql})

        return {
            "status": "success",
            "mode": "schema",
            "db_path": path,
            "tables": table_out,
            "views": view_out,
            "indexes": index_out,
            "triggers": trigger_out,
            "total_object_count": len(rows),
            "table_count": len(tables),
            "view_count": len(views),
            "index_count": len(indexes),
            "trigger_count": len(triggers),
            "tables_truncated": len(tables) > len(table_out),
            "indexes_truncated": len(indexes) > len(index_out),
            "triggers_truncated": len(triggers) > len(trigger_out),
            "views_truncated": len(views) > len(view_out),
            "truncated_sql_objects": sorted(truncated_sql),
        }

    def _trigger_shape(self, sql: str) -> tuple[str, str]:
        timing_match = self._TIMING.search(sql)
        after = timing_match.end() if timing_match else 0
        event_match = self._EVENT.search(sql, after)
        timing = re.sub(r"\s+", " ", timing_match.group(1)).upper() if timing_match else ""
        event = event_match.group(1).upper() if event_match else ""
        return timing, event

    # ------------------------------------------------------------------ audit mode

    def _audit(self, conn: sqlite3.Connection, path: str) -> dict[str, Any]:
        rows = self._catalog(conn)
        tables = [r for r in rows if r[0] == "table"][: self.max_scan_objects]
        objects = ([r for r in rows if r[0] == "trigger"] + [r for r in rows if r[0] == "view"])[: self.max_objects]
        findings: list[dict[str, Any]] = []
        truncated = False
        fk_total = 0
        for row in tables:
            fk_total += len(self._pragma(conn, f"PRAGMA foreign_key_list({self._quoted(row[1])})"))
            for finding in self._table_findings(conn, row):
                if len(findings) >= self.max_audit_findings:
                    truncated = True
                    break
                findings.append(finding)
        if fk_total:
            state = self._pragma(conn, "PRAGMA foreign_keys")
            findings.append(
                {
                    "code": "foreign_keys_enforcement_off_by_default",
                    "severity": "info",
                    "foreign_keys_pragma_state": int(state[0][0]) if state else 0,
                    "detail": (
                        "Foreign keys are declared but PRAGMA foreign_keys reports the default value 0 on a "
                        "fresh connection (it is a per-connection setting); unless the application enables "
                        "it, these constraints are not enforced at runtime."
                    ),
                }
            )
        for row in objects:
            for finding in self._object_findings(row):
                if len(findings) >= self.max_audit_findings:
                    truncated = True
                    break
                findings.append(finding)
        return {
            "status": "success",
            "mode": "audit",
            "db_path": path,
            "findings": findings[: self.max_audit_findings],
            "finding_count": len(findings[: self.max_audit_findings]),
            "findings_truncated": truncated,
            "scanned_table_count": len(tables),
            "table_count": sum(1 for r in rows if r[0] == "table"),
            "view_count": sum(1 for r in rows if r[0] == "view"),
            "trigger_count": sum(1 for r in rows if r[0] == "trigger"),
            "foreign_key_count": fk_total,
            "data_sampled": False,
            "policy": "structure-only",
        }

    def _table_findings(self, conn: sqlite3.Connection, row: tuple[str, str, str, str | None]) -> list[dict[str, Any]]:
        """Structural findings for one table: missing/nullable primary key and duplicate indexes."""
        name, sql = row[1], row[3]
        columns = self._table_info(conn, name)
        pk_cols = [c for c in columns if c["pk_index"] > 0]
        findings: list[dict[str, Any]] = []
        if not pk_cols:
            findings.append(
                {
                    "code": "table_without_primary_key",
                    "severity": "warning",
                    "table": name,
                    "detail": "No PRIMARY KEY: rows in this rowid table cannot be deduplicated by key.",
                }
            )
        else:
            nullable = [c["name"] for c in self._nullable_pk_columns(columns, sql)]
            if nullable:
                findings.append(
                    {
                        "code": "nullable_primary_key_column",
                        "severity": "warning",
                        "table": name,
                        "columns": nullable,
                        "detail": (
                            "PRIMARY KEY column(s) without NOT NULL: SQLite permits NULL in non-INTEGER "
                            "PRIMARY KEY columns of rowid tables, so duplicates of NULL can be stored."
                        ),
                    }
                )
        return findings + self._index_findings(conn, name)

    def _object_findings(self, row: tuple[str, str, str, str | None]) -> list[dict[str, Any]]:
        """Text-scan findings for one trigger or view: attached-db references and cross-table writes."""
        sql = row[3] or ""
        findings: list[dict[str, Any]] = []
        if self._ATTACH.search(sql) or self._QUALIFIED.search(sql):
            findings.append(
                {
                    "code": "attached_database_reference",
                    "severity": "info",
                    "object": row[1],
                    "detail": (
                        "Trigger/view SQL mentions ATTACH or a three-part schema.table.column name; "
                        "it may depend on a database attached at runtime (shallow text scan)."
                    ),
                }
            )
        if row[0] == "trigger":
            targets = self._cross_table_write_targets(sql, row[2])
            if targets:
                findings.append(
                    {
                        "code": "cross_table_trigger_mutation",
                        "severity": "info",
                        "object": row[1],
                        "table": row[2],
                        "writes_to": targets,
                        "detail": "Trigger body writes to other tables (shallow parse of INSERT/UPDATE/DELETE targets).",
                    }
                )
        return findings

    def _nullable_pk_columns(self, columns: list[dict[str, Any]], sql: str | None) -> list[dict[str, Any]]:
        nullable = [c for c in columns if c["pk_index"] > 0 and not c["notnull"]]
        if not nullable:
            return []
        # An exactly-INTEGER single PRIMARY KEY on a rowid table aliases the
        # rowid, which the engine itself keeps non-null even though table_info
        # reports notnull=0; that case is not a footgun.
        if self._rowid_table(sql) and len(nullable) == 1 and nullable[0]["type"].strip().upper() == "INTEGER":
            return []
        return nullable

    def _index_findings(self, conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
        groups: dict[tuple, list[str]] = {}
        for entry in self._index_rows(conn, table):
            signature = (table, tuple(entry["columns"]), entry["unique"], entry["partial"])
            if "(expression)" in signature[1]:
                # Expression indexes cannot be compared structurally by column name.
                continue
            groups.setdefault(signature, []).append(entry["name"])
        findings = []
        for names in groups.values():
            if len(names) > 1:
                findings.append(
                    {
                        "code": "duplicate_index",
                        "severity": "warning",
                        "table": table,
                        "indexes": sorted(names),
                        "detail": "Multiple indexes cover the same column set (and uniqueness/partiality); redundant.",
                    }
                )
        return findings

    def _cross_table_write_targets(self, sql: str, own_table: str) -> list[str]:
        targets: set[str] = set()
        for pattern in self._WRITES:
            for match in pattern.finditer(sql):
                groups = match.groups()
                target = next(g for g in groups if g is not None)
                if target != own_table:
                    targets.add(target)
        return sorted(targets)

    # ------------------------------------------------------------------ integrity mode

    def _integrity(self, conn: sqlite3.Connection, path: str) -> dict[str, Any]:
        # A healthy database yields a single literal "ok" row; only real
        # problems are reported in the bounded error lists.
        integrity_rows = [str(r[0]) for r in self._pragma(conn, "PRAGMA integrity_check") if str(r[0]) != "ok"]
        quick_rows = [str(r[0]) for r in self._pragma(conn, "PRAGMA quick_check") if str(r[0]) != "ok"]
        violations, fk_truncated = self._fk_violations(conn)
        page_size = self._scalar(conn, "PRAGMA page_size")
        page_count = self._scalar(conn, "PRAGMA page_count")
        freelist = self._scalar(conn, "PRAGMA freelist_count")
        return {
            "status": "success",
            "mode": "integrity",
            "db_path": path,
            "integrity_check": integrity_rows[0] if integrity_rows else "ok",
            "integrity_errors": integrity_rows[: self.max_integrity_findings],
            "integrity_errors_truncated": len(integrity_rows) > self.max_integrity_findings,
            "quick_check": quick_rows[0] if quick_rows else "ok",
            "quick_check_errors": quick_rows[: self.max_integrity_findings],
            "quick_check_errors_truncated": len(quick_rows) > self.max_integrity_findings,
            "foreign_key_violations": violations[: self.max_fk_violations],
            "foreign_key_violations_truncated": fk_truncated or len(violations) > self.max_fk_violations,
            "page_size": page_size,
            "page_count": page_count,
            "freelist_count": freelist,
            "freelist_bytes": freelist * page_size,
            "vacuum_candidate": freelist >= self.freelist_vacuum_threshold,
            "journal_mode": self._scalar(conn, "PRAGMA journal_mode"),
            "user_version": self._scalar(conn, "PRAGMA user_version"),
            "application_id": self._scalar(conn, "PRAGMA application_id"),
        }

    def _fk_violations(self, conn: sqlite3.Connection) -> tuple[list[dict[str, Any]], bool]:
        cursor = conn.execute("PRAGMA foreign_key_check")
        definitions: dict[str, list[Any]] = {}
        violations: list[dict[str, Any]] = []
        truncated = False
        for row in cursor:
            if len(violations) > self.max_fk_violations:
                truncated = True
                break
            table, rowid, parent, fkid = str(row[0]), row[1], str(row[2]), int(row[3])
            if table not in definitions:
                definitions[table] = self._pragma(conn, f"PRAGMA foreign_key_list({self._quoted(table)})")
            matches = [d for d in definitions[table] if int(d[0]) == fkid]
            definition = None
            if matches:
                d = matches[0]
                definition = {
                    "parent_table": str(d[2]),
                    "from_column": str(d[3]),
                    "to_column": None if d[4] is None else str(d[4]),
                }
            violations.append({"table": table, "rowid": rowid, "parent_table": parent, "fk_definition": definition})
        return violations, truncated

    @staticmethod
    def _scalar(conn: sqlite3.Connection, statement: str) -> int | str:
        row = conn.execute(statement).fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------ compact mode

    def _compact(self, conn: sqlite3.Connection, path: str) -> dict[str, Any]:
        rows = self._catalog(conn)
        tables = [r for r in rows if r[0] == "table"]
        page_size = self._scalar(conn, "PRAGMA page_size")
        page_count = self._scalar(conn, "PRAGMA page_count")
        freelist = self._scalar(conn, "PRAGMA freelist_count")
        columns = [
            {"name": row[1], "column_count": len(self._table_info(conn, row[1]))} for row in tables[: self.max_objects]
        ]
        return {
            "status": "success",
            "mode": "compact",
            "db_path": path,
            "file_size": os.path.getsize(path),
            "page_size": page_size,
            "page_count": page_count,
            "freelist_count": freelist,
            "freelist_bytes": freelist * page_size,
            "used_bytes_estimate": max(0, page_count - freelist) * page_size,
            "freelist_ratio": round(freelist / page_count, 6) if page_count else 0.0,
            "tables": columns,
            "table_count": len(tables),
            "view_count": sum(1 for r in rows if r[0] == "view"),
            "index_count": sum(1 for r in rows if r[0] == "index"),
            "trigger_count": sum(1 for r in rows if r[0] == "trigger"),
            "row_estimates": "excluded (would require scanning or sampling rows)",
        }
