#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for NotionReader database pagination and row_id guard.

1. The previous code consumed only the first page of
   ``client.databases.query`` (≤100 rows), silently dropping every row
   beyond that. Now follows ``has_more`` / ``next_cursor``.
2. A database row without an ``id`` used to pass ``None`` into
   ``_export_page`` → Notion API 400 → the entire database read aborted.
   Now skips the row.
3. The pagination loop is bounded by MAX_DATABASE_PAGES so a hostile
   database cannot exhaust memory / quota.
"""

import unittest
from unittest.mock import MagicMock, patch


def _query_page(results, has_more=False, next_cursor=None):
    return {"results": results, "has_more": has_more, "next_cursor": next_cursor}


def _row(row_id):
    return {"id": row_id}


class TestNotionReaderPagination(unittest.TestCase):

    def _reader(self):
        from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader \
            import NotionReader
        return NotionReader()

    def test_database_read_follows_pagination(self):
        reader = self._reader()
        client = MagicMock()
        # Two pages of results: page 1 has rows [r1, r2] with has_more=True,
        # page 2 has [r3] with has_more=False.
        client.databases.query.side_effect = [
            _query_page([_row("r1"), _row("r2")], has_more=True, next_cursor="c1"),
            _query_page([_row("r3")], has_more=False),
        ]
        # _export_page returns one text block per page id.
        with patch.object(reader, "_export_page", side_effect=lambda c, pid: [f"text-{pid}"]):
            blocks = reader._export_database(client, "db1")
        # All three rows exported; previously only r1, r2 were (first page).
        self.assertEqual(blocks, ["text-r1", "text-r2", "text-r3"])
        self.assertEqual(client.databases.query.call_count, 2)
        # Second call used the next_cursor from the first.
        second_call = client.databases.query.call_args_list[1]
        self.assertEqual(second_call.kwargs.get("start_cursor"), "c1")

    def test_database_read_single_page_when_no_more(self):
        reader = self._reader()
        client = MagicMock()
        client.databases.query.return_value = _query_page(
            [_row("r1")], has_more=False)
        with patch.object(reader, "_export_page", side_effect=lambda c, pid: [f"t-{pid}"]):
            blocks = reader._export_database(client, "db1")
        self.assertEqual(blocks, ["t-r1"])
        self.assertEqual(client.databases.query.call_count, 1)

    def test_database_read_skips_row_without_id(self):
        reader = self._reader()
        client = MagicMock()
        client.databases.query.return_value = _query_page(
            [_row("r1"), {"no_id_field": True}, _row("r3")], has_more=False)
        exported = []
        with patch.object(reader, "_export_page",
                          side_effect=lambda c, pid: exported.append(pid) or [pid]):
            reader._export_database(client, "db1")
        # The id-less row was skipped, not passed to _export_page.
        self.assertEqual(exported, ["r1", "r3"])

    def test_database_read_caps_at_max_pages(self):
        from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader \
            import NotionReader
        reader = self._reader()
        client = MagicMock()
        # Every page says has_more=True with a cursor; the loop must stop at
        # MAX_DATABASE_PAGES rather than following forever.
        client.databases.query.return_value = _query_page(
            [_row("r")], has_more=True, next_cursor="c")
        with patch.object(NotionReader, "MAX_DATABASE_PAGES", 3):
            with patch.object(reader, "_export_page", return_value=["t"]):
                reader._export_database(client, "db1")
        self.assertEqual(client.databases.query.call_count, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
