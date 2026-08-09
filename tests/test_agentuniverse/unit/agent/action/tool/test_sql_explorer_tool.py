#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for SQLExplorerTool.

Covers query validation (read-only enforcement, forbidden keywords),
row/cell/total bounding, LIMIT injection, and error handling. Uses a
mock SQLDBWrapper so no real database is required.
"""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.tool.common_tool.sql_explorer_tool import \
    SQLExplorerTool


def _mock_db(rows=None):
    db = MagicMock()
    db.run.return_value = rows or []
    return db


class TestSQLExplorerValidation(unittest.TestCase):

    def _tool(self, **kwargs):
        defaults = dict(db_wrapper_name="w", read_only=True, allow_write=False)
        defaults.update(kwargs)
        tool = SQLExplorerTool(**defaults)
        return tool

    def test_empty_query_rejected(self):
        tool = self._tool()
        result = tool.execute("")
        self.assertEqual(result["status"], "error")

    def test_select_allowed_in_read_only(self):
        tool = self._tool()
        tool._validate_query("SELECT * FROM users")  # no raise

    def test_with_allowed(self):
        tool = self._tool()
        tool._validate_query("WITH t AS (SELECT 1) SELECT * FROM t")

    def test_insert_rejected_in_read_only(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool._validate_query("INSERT INTO users VALUES (1)")

    def test_delete_rejected_in_read_only(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool._validate_query("DELETE FROM users")

    def test_drop_rejected_even_as_subquery(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool._validate_query("SELECT * FROM users; DROP TABLE users")

    def test_update_rejected(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool._validate_query("UPDATE users SET name = 'x'")

    def test_write_allowed_when_allow_write(self):
        tool = self._tool(read_only=False, allow_write=True)
        tool._validate_query("INSERT INTO users VALUES (1)")  # no raise

    def test_explain_allowed(self):
        tool = self._tool()
        tool._validate_query("EXPLAIN SELECT * FROM users")


class TestSQLExplorerBounding(unittest.TestCase):

    def setUp(self):
        self.tool = SQLExplorerTool(
            db_wrapper_name="w", max_rows=3, max_cell_chars=5,
            max_result_chars=50)

    def _patch_db(self, rows):
        return patch.object(self.tool, "_get_db", return_value=_mock_db(rows))

    def test_rows_capped_at_max_rows(self):
        rows = [{"id": i} for i in range(10)]
        with self._patch_db(rows):
            result = self.tool.execute("SELECT * FROM t")
        self.assertEqual(result["row_count"], 3)
        self.assertTrue(result["truncated"])

    def test_cell_truncated_at_max_cell_chars(self):
        rows = [{"text": "abcdefghij"}]
        with self._patch_db(rows):
            result = self.tool.execute("SELECT * FROM t")
        self.assertLessEqual(len(result["rows"][0]["text"]), 5)

    def test_total_result_truncated(self):
        rows = [{"c": "1234567890"}] * 10
        with self._patch_db(rows):
            result = self.tool.execute("SELECT * FROM t")
        self.assertTrue(result["truncated"])

    def test_limit_injected_when_missing(self):
        tool = SQLExplorerTool(db_wrapper_name="w", max_rows=42)
        db = _mock_db([])
        tool._run_query(db, "SELECT * FROM t")
        sql_called = db.run.call_args.args[0]
        self.assertIn("LIMIT 42", sql_called)

    def test_user_limit_clamped_to_max(self):
        tool = SQLExplorerTool(db_wrapper_name="w", max_rows=10)
        db = _mock_db([])
        tool._run_query(db, "SELECT * FROM t LIMIT 999")
        sql_called = db.run.call_args.args[0]
        self.assertIn("LIMIT 10", sql_called)
        self.assertNotIn("999", sql_called)


class TestSQLExplorerErrors(unittest.TestCase):

    def test_unregistered_wrapper_raises_validation_error(self):
        tool = SQLExplorerTool(db_wrapper_name="nonexistent")
        with patch("agentuniverse.database.sqldb_wrapper_manager."
                   "SQLDBWrapperManager") as mgr:
            mgr.return_value.get_instance_obj.return_value = None
            result = tool.execute("SELECT 1")
        self.assertEqual(result["status"], "error")
        self.assertIn("not registered", result["error"])

    def test_db_exception_returns_structured_error(self):
        tool = SQLExplorerTool(db_wrapper_name="w")
        db = MagicMock()
        db.run.side_effect = RuntimeError("connection lost")
        with patch.object(tool, "_get_db", return_value=db):
            result = tool.execute("SELECT 1")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "query_error")


class TestSQLExplorerConfig(unittest.TestCase):

    def test_missing_db_wrapper_rejected(self):
        with self.assertRaises(ValueError):
            SQLExplorerTool(db_wrapper_name="")._validate_config()

    def test_zero_max_rows_rejected(self):
        with self.assertRaises(ValueError):
            SQLExplorerTool(db_wrapper_name="w", max_rows=0)._validate_config()


if __name__ == "__main__":
    unittest.main(verbosity=2)
