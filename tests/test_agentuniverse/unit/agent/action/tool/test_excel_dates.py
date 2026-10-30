#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for JSON output from Excel date and time cells."""

import asyncio
import json
import tempfile
import unittest
from datetime import date, datetime, time
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

from agentuniverse.agent.action.tool.common_tool.excel_tool import ExcelTool


class TestExcelDates(unittest.TestCase):
    """Exercise the public tool with real Excel workbooks."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = str(Path(self.directory.name) / "dates.xlsx")
        self.tool = ExcelTool()

    def write_workbook(self, values, iso_dates=True):
        """Write a row without substituting the Excel reader or serializer."""
        workbook = Workbook()
        workbook.iso_dates = iso_dates
        workbook.active.append(values)
        workbook.save(self.path)
        workbook.close()

    def test_read_serializes_date_and_time_cells(self):
        cases = [
            (datetime(2026, 10, 18, 9, 30, 15), "2026-10-18T09:30:15"),
            (date(2026, 10, 18), "2026-10-18"),
            (time(9, 30, 15), "09:30:15"),
        ]
        for value, expected in cases:
            with self.subTest(cell_type=type(value).__name__):
                self.write_workbook([value])

                # The reader's native values remain available to Python callers.
                native = self.tool._read_excel(self.path)
                self.assertEqual(native["data"], [[value]])
                self.assertIsInstance(native["data"][0][0], type(value))

                result = json.loads(self.tool.execute(self.path, "read"))
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["data"], [[expected]])
                self.assertEqual(result["rows_read"], 1)
                self.assertEqual(result["columns"], 1)

    def test_read_preserves_serial_dates_and_other_cell_values(self):
        self.write_workbook(
            [date(2026, 10, 18), 42, 1.5, True, None, "plain text"],
            iso_dates=False,
        )
        result = json.loads(self.tool.execute(self.path, "read"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["data"],
            [["2026-10-18T00:00:00", 42, 1.5, True, None, "plain text"]],
        )

    def test_async_read_serializes_time_cells(self):
        self.write_workbook([time(9, 30, 15)])
        result = json.loads(asyncio.run(self.tool.async_execute(self.path, "read")))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], [["09:30:15"]])

    def test_read_does_not_stringify_unsupported_objects(self):
        with patch.object(ExcelTool, "_read_excel", return_value={"data": [[object()]]}):
            result = json.loads(self.tool.execute(self.path, "read"))
        self.assertEqual(result["status"], "error")
        self.assertIn("not JSON serializable", result["error"])


if __name__ == "__main__":
    unittest.main()
