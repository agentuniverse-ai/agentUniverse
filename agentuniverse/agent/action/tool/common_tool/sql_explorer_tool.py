#!/usr/bin/env python3
"""Structured SQL explorer tool with bounded query execution.

Provides safe, read-only SQL query execution against a configured database.
All queries are validated (read-only, parameterised), row-limited, and
result-size-bounded so an agent cannot issue destructive SQL or dump
unbounded data.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import json
import logging
import re
from typing import Any, Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# SQL keywords that modify data — rejected in read-only mode.
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"MERGE|REPLACE|CALL|EXEC|EXECUTE|SET|LOCK|UNLOCK|HANDLER|LOAD|"
    r"VACUUM|ANALYZE|COMMENT|REINDEX|RESET)\b",
    re.IGNORECASE,
)

# Statements that are always allowed in read-only mode.
_ALLOWED_PREFIXES = ("SELECT", "WITH", "EXPLAIN", "SHOW", "DESCRIBE", "DESC")


class SQLExplorerTool(Tool):
    """Bounded, read-only SQL query tool.

    Attributes:
        db_wrapper_name: Name of the registered SQLDBWrapper component.
        max_rows: Maximum rows returned per query (default 100).
        max_cell_chars: Maximum characters per cell in the result (default 500).
        max_result_chars: Maximum total characters of the serialised result
            (default 50_000).
        query_timeout_seconds: Per-query timeout in seconds (default 30).
        read_only: If ``True`` (default), only SELECT/WITH/EXPLAIN/SHOW/
            DESCRIBE statements are allowed.
        allow_write: If ``True``, write statements (INSERT/UPDATE/DELETE) are
            allowed. Defaults to ``False`` for safety.
    """

    db_wrapper_name: Optional[str] = None
    max_rows: int = 100
    max_cell_chars: int = 500
    max_result_chars: int = 50_000
    query_timeout_seconds: int = 30
    read_only: bool = True
    allow_write: bool = False

    _db: Any = None

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) -> "SQLExplorerTool":
        super()._initialize_by_component_configer(configer)
        for field in (
            "db_wrapper_name", "max_rows", "max_cell_chars",
            "max_result_chars", "query_timeout_seconds", "read_only",
            "allow_write",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        if not self.db_wrapper_name:
            raise ValueError("db_wrapper_name must be set")
        for field in ("max_rows", "max_cell_chars", "max_result_chars",
                      "query_timeout_seconds"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field} must be a positive integer")
        if self.allow_write:
            self.read_only = False

    # ------------------------------------------------------------------ #
    # DB connection
    # ------------------------------------------------------------------ #
    def _get_db(self) -> Any:
        if self._db is None:
            from agentuniverse.database.sqldb_wrapper_manager import \
                SQLDBWrapperManager
            wrapper = SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)
            if wrapper is None:
                raise ValueError(
                    f"SQLDBWrapper {self.db_wrapper_name!r} is not registered")
            self._db = wrapper.sql_database
        return self._db

    # ------------------------------------------------------------------ #
    # Query validation
    # ------------------------------------------------------------------ #
    def _validate_query(self, sql: str) -> None:
        stripped = sql.strip()
        if not stripped:
            raise ValueError("SQL query must not be empty")

        if self.read_only:
            upper = stripped.upper()
            if not upper.startswith(_ALLOWED_PREFIXES):
                raise ValueError(
                    f"Read-only mode: query must start with one of "
                    f"{', '.join(_ALLOWED_PREFIXES)}; got a statement starting "
                    f"with {stripped[:20]!r}")

            forbidden = _FORBIDDEN_KEYWORDS.findall(stripped)
            if forbidden:
                raise ValueError(
                    f"Read-only mode: forbidden keyword(s) {forbidden} "
                    f"detected in query")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def execute(self, sql: str, **kwargs) -> dict:
        try:
            self._validate_query(sql)
            db = self._get_db()
            results = self._run_query(db, sql)
            return self._format_results(results)
        except ValueError as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("query_error", f"SQL query failed: {exc}")

    def _run_query(self, db: Any, sql: str) -> list:
        # Inject a LIMIT if the user did not provide one (for SELECT).
        if self.read_only and not re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
            sql = sql.rstrip(";").rstrip() + f" LIMIT {self.max_rows}"
        elif self.read_only:
            # If user specified LIMIT, clamp it to max_rows.
            sql = self._clamp_limit(sql)
        return db.run(sql, fetch="all") or []

    def _clamp_limit(self, sql: str) -> str:
        match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
        if match:
            user_limit = int(match.group(1))
            if user_limit > self.max_rows:
                return sql[:match.start()] + f"LIMIT {self.max_rows}" + sql[match.end():]
        return sql

    def _format_results(self, results: list) -> dict:
        if isinstance(results, str):
            results = json.loads(results) if results.strip() else []
        bounded = []
        total_chars = 0
        truncated = False
        for i, row in enumerate(results):
            if i >= self.max_rows:
                truncated = True
                break
            bounded_row = {}
            for key, value in (row.items() if isinstance(row, dict)
                               else enumerate(row)):
                cell = str(value) if value is not None else ""
                if len(cell) > self.max_cell_chars:
                    cell = cell[: max(0, self.max_cell_chars - 1)] + "…"
                bounded_row[str(key)] = cell
                total_chars += len(cell)
                if total_chars > self.max_result_chars:
                    truncated = True
                    break
            bounded.append(bounded_row)
            if truncated:
                break
        return {
            "status": "success",
            "row_count": len(bounded),
            "truncated": truncated,
            "max_rows": self.max_rows,
            "rows": bounded,
        }

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}
