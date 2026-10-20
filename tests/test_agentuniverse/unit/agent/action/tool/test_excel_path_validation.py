#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.action.tool.common_tool.excel_tool import ExcelTool


class ExcelPathValidationTest(unittest.TestCase):
    def test_windows_system_path_is_blocked_case_insensitively(self):
        result = ExcelTool()._validate_path("c:\\windows\\temp\\data.xlsx")

        self.assertFalse(result["valid"])
        self.assertIn("Access denied", result["error"])

    def test_windows_style_traversal_is_blocked_on_all_platforms(self):
        result = ExcelTool()._validate_path("..\\secret\\data.xlsx")

        self.assertFalse(result["valid"])
        self.assertIn("Path traversal", result["error"])


if __name__ == "__main__":
    unittest.main()
