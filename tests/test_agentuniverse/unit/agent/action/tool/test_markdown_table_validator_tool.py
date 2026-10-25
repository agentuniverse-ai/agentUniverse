#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_markdown_table_validator_tool.py

"""Offline unit tests for MarkdownTableValidatorTool.

The tool is built purely on the standard library (re) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: each finding kind is triggered against a hand-built
document and checked against ground-truth type / severity / row / line
/ count values, every fix mode is checked against the exact repaired
markdown string, and the stats mode is checked against hand-computed
arithmetic.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import MarkdownTableValidatorTool
from agentuniverse.agent.action.tool.common_tool.markdown_table_validator_tool import (
    MarkdownTableValidatorTool as DirectMarkdownTableValidatorTool,
)

CLEAN_TABLE = (
    "| Name | Age |\n"
    "| --- | --- |\n"
    "| Alice | 30 |\n"
    "| Bob | 25 |\n"
)


class MarkdownTableValidatorToolTest(unittest.TestCase):
    """Ground-truth tests for the three tool modes."""

    def setUp(self) -> None:
        self.tool = MarkdownTableValidatorTool()

    # ------------------------------------------------------------------ #
    # validate mode — clean tables
    # ------------------------------------------------------------------ #

    def test_clean_table_has_no_findings(self) -> None:
        report = self.tool.execute(mode="validate", markdown=CLEAN_TABLE)
        self.assertEqual(report["mode"], "validate")
        self.assertEqual(report["table_count"], 1)
        table = report["tables"][0]
        self.assertEqual(table["verdict"], "valid")
        self.assertEqual(table["findings"], [])
        self.assertEqual(table["row_count"], 4)
        self.assertEqual(table["column_count"], 2)
        self.assertEqual(table["line_start"], 1)
        self.assertEqual(table["line_end"], 4)
        self.assertEqual(
            report["summary"], {"valid": 1, "warnings": 0, "errors": 0}
        )

    def test_alignment_variants_are_all_valid(self) -> None:
        markdown = (
            "| l | c | r |\n"
            "| :--- | :---: | ---: |\n"
            "| a | b | c |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(report["tables"][0]["verdict"], "valid")
        self.assertEqual(report["tables"][0]["findings"], [])

    def test_escaped_pipes_count_as_content_not_separators(self) -> None:
        markdown = (
            "| a \\| b | c |\n"
            "| --- | --- |\n"
            "| x \\| y | z |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(report["table_count"], 1)
        table = report["tables"][0]
        self.assertEqual(table["column_count"], 2)
        self.assertEqual(table["verdict"], "valid")
        self.assertEqual(table["findings"], [])

    def test_default_mode_is_validate(self) -> None:
        report = self.tool.execute(markdown=CLEAN_TABLE)
        self.assertEqual(report["mode"], "validate")
        self.assertEqual(report["table_count"], 1)

    # ------------------------------------------------------------------ #
    # validate mode — each error finding kind
    # ------------------------------------------------------------------ #

    def test_column_count_mismatch_reports_row_and_both_counts(self) -> None:
        markdown = (
            "| H1 | H2 | H3 |\n"
            "| --- | --- | --- |\n"
            "| a | b |\n"
            "| c | d | e | f |\n"
            "| g | h | i |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        mismatches = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] == "column_count_mismatch"
        ]
        self.assertEqual(len(mismatches), 2)
        first, second = mismatches
        # Row 3 (document line 3) has 2 cells, the header has 3.
        self.assertEqual(first["row"], 3)
        self.assertEqual(first["line"], 3)
        self.assertEqual(first["expected"], 3)
        self.assertEqual(first["actual"], 2)
        self.assertEqual(first["severity"], "error")
        # Row 4 (document line 4) has 4 cells, the header has 3.
        self.assertEqual(second["row"], 4)
        self.assertEqual(second["line"], 4)
        self.assertEqual(second["expected"], 3)
        self.assertEqual(second["actual"], 4)
        self.assertEqual(report["tables"][0]["verdict"], "errors")

    def test_missing_alignment_row(self) -> None:
        markdown = "| H1 | H2 |\n| a | b |\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        findings = report["tables"][0]["findings"]
        missing = [
            finding
            for finding in findings
            if finding["type"] == "missing_alignment_row"
        ]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["severity"], "error")
        self.assertEqual(missing[0]["line"], 1)
        self.assertEqual(report["tables"][0]["verdict"], "errors")
        # "| a | b |" is a plain body row, not a botched delimiter row.
        self.assertEqual(
            [f["type"] for f in findings if f["type"] == "invalid_alignment_row"],
            [],
        )

    def test_header_only_table_is_missing_alignment(self) -> None:
        markdown = "| H1 | H2 |\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        findings = report["tables"][0]["findings"]
        self.assertEqual(
            [f["type"] for f in findings], ["missing_alignment_row"]
        )
        self.assertEqual(report["tables"][0]["row_count"], 1)

    def test_invalid_alignment_row_bad_cell_syntax(self) -> None:
        # Cells with spaces inside the dash run or without any dash are
        # delimiter-row syntax errors, not content rows.
        markdown = "| H1 | H2 |\n| - - | : : |\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        invalid = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] == "invalid_alignment_row"
        ]
        self.assertEqual(len(invalid), 2)
        self.assertEqual(invalid[0]["cell"], 1)
        self.assertEqual(invalid[1]["cell"], 2)
        self.assertEqual(invalid[0]["severity"], "error")
        self.assertEqual(report["tables"][0]["verdict"], "errors")

    def test_ragged_alignment_reports_both_counts(self) -> None:
        markdown = "| H1 | H2 |\n| --- | --- | --- |\n| a | b |\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        ragged = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] == "ragged_alignment"
        ]
        self.assertEqual(len(ragged), 1)
        self.assertEqual(ragged[0]["row"], 2)
        self.assertEqual(ragged[0]["line"], 2)
        self.assertEqual(ragged[0]["expected"], 2)
        self.assertEqual(ragged[0]["actual"], 3)
        self.assertEqual(ragged[0]["severity"], "error")

    # ------------------------------------------------------------------ #
    # validate mode — info finding kinds
    # ------------------------------------------------------------------ #

    def test_unclosed_edge_leading_and_trailing(self) -> None:
        markdown = "H1 | H2\n| --- | --- |\n| a | b\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        edges = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] == "unclosed_edge"
        ]
        # Row 1 misses both pipes, row 3 misses its trailing pipe.
        self.assertEqual(
            [(f["row"], f["edge"]) for f in edges],
            [(1, "leading"), (1, "trailing"), (3, "trailing")],
        )
        self.assertTrue(all(f["severity"] == "info" for f in edges))
        # Info findings alone yield the "warnings" verdict.
        self.assertEqual(report["tables"][0]["verdict"], "warnings")
        self.assertEqual(
            report["summary"], {"valid": 0, "warnings": 1, "errors": 0}
        )

    def test_empty_header_and_body_cells(self) -> None:
        markdown = "| H1 |  |\n| --- | --- |\n| a |  |\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        empties = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] in ("empty_header_cell", "empty_body_cell")
        ]
        self.assertEqual(
            [(f["type"], f["row"], f["cell"]) for f in empties],
            [("empty_header_cell", 1, 2), ("empty_body_cell", 3, 2)],
        )
        self.assertTrue(all(f["severity"] == "info" for f in empties))
        self.assertEqual(report["tables"][0]["verdict"], "warnings")

    # ------------------------------------------------------------------ #
    # validate mode — table detection
    # ------------------------------------------------------------------ #

    def test_multiple_tables_separated_by_blank_lines(self) -> None:
        markdown = (
            "| a | b |\n"
            "| --- | --- |\n"
            "\n"
            "paragraph text\n"
            "\n"
            "| c |\n"
            "| --- |\n"
            "| d |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(report["table_count"], 2)
        first, second = report["tables"]
        self.assertEqual((first["line_start"], first["line_end"]), (1, 2))
        self.assertEqual((second["line_start"], second["line_end"]), (6, 8))
        self.assertEqual(first["verdict"], "valid")
        self.assertEqual(second["verdict"], "valid")

    def test_pipe_less_line_inside_group_is_a_single_cell_row(self) -> None:
        markdown = "| a | b |\n| --- | --- |\nno pipes here\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        mismatches = [
            finding
            for finding in report["tables"][0]["findings"]
            if finding["type"] == "column_count_mismatch"
        ]
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["row"], 3)
        self.assertEqual(mismatches[0]["actual"], 1)
        self.assertEqual(mismatches[0]["expected"], 2)

    def test_fenced_code_blocks_are_immune(self) -> None:
        markdown = (
            "| a | b |\n"
            "| --- | --- |\n"
            "\n"
            "```text\n"
            "| broken | \n"
            "| no | delimiter | here |\n"
            "```\n"
            "\n"
            "~~~\n"
            "| also | ignored |\n"
            "~~~\n"
            "\n"
            "| c |\n"
            "| --- |\n"
            "| d |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(report["table_count"], 2)
        self.assertTrue(
            all(table["verdict"] == "valid" for table in report["tables"])
        )

    def test_document_without_tables(self) -> None:
        markdown = "# Heading\n\nJust a paragraph.\n"
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(report["table_count"], 0)
        self.assertEqual(report["tables"], [])
        self.assertEqual(
            report["summary"], {"valid": 0, "warnings": 0, "errors": 0}
        )

    def test_verdict_matrix_across_tables(self) -> None:
        markdown = (
            "| ok | fine |\n"
            "| --- | --- |\n"
            "\n"
            "| h |  |\n"
            "| --- | --- |\n"
            "\n"
            "| h1 | h2 |\n"
            "| a |\n"
        )
        report = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(
            [table["verdict"] for table in report["tables"]],
            ["valid", "warnings", "errors"],
        )
        self.assertEqual(
            report["summary"], {"valid": 1, "warnings": 1, "errors": 1}
        )

    # ------------------------------------------------------------------ #
    # fix mode — each fix mode with exact repaired output
    # ------------------------------------------------------------------ #

    def test_fix_pad_short_rows_exact_output(self) -> None:
        markdown = (
            "| H1 | H2 |\n"
            "| --- | --- |\n"
            "| short |\n"
            "| ok | yes |\n"
        )
        fixed = self.tool.execute(
            mode="fix", markdown=markdown, fix_modes=["pad_short_rows"]
        )
        self.assertEqual(
            fixed["result"],
            "| H1 | H2 |\n| --- | --- |\n| short |  |\n| ok | yes |\n",
        )
        self.assertEqual(
            [(f["fix"], f["line"]) for f in fixed["fixes_applied"]],
            [("pad_short_rows", 3)],
        )

    def test_fix_pad_short_rows_survives_revalidation(self) -> None:
        # A row without edge pipes still needs its padding to be
        # visible: the fix must add the trailing pipe.
        markdown = "| H1 | H2 |\n| --- | --- |\nbare\n"
        fixed = self.tool.execute(
            mode="fix", markdown=markdown, fix_modes=["pad_short_rows"]
        )
        self.assertEqual(
            fixed["result"], "| H1 | H2 |\n| --- | --- |\nbare |  |\n"
        )
        revalidated = self.tool.execute(
            mode="validate", markdown=fixed["result"]
        )
        self.assertEqual(
            [
                finding
                for finding in revalidated["tables"][0]["findings"]
                if finding["severity"] == "error"
            ],
            [],
        )

    def test_fix_drop_mismatched_rows_preserves_other_rows(self) -> None:
        markdown = (
            "| H1 | H2 |\n"
            "| --- | --- |\n"
            "| one |\n"
            "| ok | yes |\n"
            "| a | b | c |\n"
        )
        fixed = self.tool.execute(
            mode="fix", markdown=markdown, fix_modes=["drop_mismatched_rows"]
        )
        self.assertEqual(
            fixed["result"],
            "| H1 | H2 |\n| --- | --- |\n| ok | yes |\n",
        )
        self.assertEqual(
            [(f["fix"], f["line"]) for f in fixed["fixes_applied"]],
            [("drop_mismatched_rows", 3), ("drop_mismatched_rows", 5)],
        )

    def test_fix_add_missing_alignment_row(self) -> None:
        markdown = "| H1 | H2 |\n| r1 | r2 |\n"
        fixed = self.tool.execute(
            mode="fix", markdown=markdown, fix_modes=["add_missing_alignment_row"]
        )
        self.assertEqual(
            fixed["result"],
            "| H1 | H2 |\n| :--- | :--- |\n| r1 | r2 |\n",
        )
        self.assertEqual(
            [(f["fix"], f["line"], f["detail"]) for f in fixed["fixes_applied"]],
            [("add_missing_alignment_row", 1, "inserted a 2-cell alignment row")],
        )

    def test_fix_default_selects_all_modes(self) -> None:
        markdown = (
            "| H1 | H2 |\n"
            "| short |\n"
            "| a | b | c |\n"
            "\n"
            "| H3 |\n"
            "| x |\n"
        )
        fixed = self.tool.execute(mode="fix", markdown=markdown)
        self.assertEqual(fixed["fix_modes"], [
            "pad_short_rows",
            "drop_mismatched_rows",
            "add_missing_alignment_row",
        ])
        # Both tables lack an alignment row, so both get one inserted;
        # the short row is padded, the over-long row is dropped.
        self.assertEqual(
            fixed["result"],
            "| H1 | H2 |\n"
            "| :--- | :--- |\n"
            "| short |  |\n"
            "\n"
            "| H3 |\n"
            "| :--- |\n"
            "| x |\n",
        )
        self.assertEqual(
            [f["fix"] for f in fixed["fixes_applied"]],
            [
                "add_missing_alignment_row",
                "pad_short_rows",
                "drop_mismatched_rows",
                "add_missing_alignment_row",
            ],
        )
        # Repaired document passes validation with no error findings.
        revalidated = self.tool.execute(mode="validate", markdown=fixed["result"])
        self.assertEqual(revalidated["summary"]["errors"], 0)

    def test_fix_canonical_mode_order_regardless_of_input_order(self) -> None:
        markdown = "| H1 | H2 |\n| a | b | c |\n| s |\n"
        fixed = self.tool.execute(
            mode="fix",
            markdown=markdown,
            fix_modes=["drop_mismatched_rows", "pad_short_rows"],
        )
        # The short row is padded (padding runs first), the over-long
        # row is dropped.
        self.assertEqual(
            fixed["result"], "| H1 | H2 |\n| s |  |\n"
        )
        self.assertEqual(
            [f["fix"] for f in fixed["fixes_applied"]],
            ["pad_short_rows", "drop_mismatched_rows"],
        )

    def test_fix_reports_unfixable_issues(self) -> None:
        # Nothing selected can repair an invalid alignment row or an
        # over-long body row when only padding is enabled.
        markdown = "| H1 | H2 |\n| - - | --- |\n| a | b | c |\n"
        fixed = self.tool.execute(
            mode="fix", markdown=markdown, fix_modes=["pad_short_rows"]
        )
        self.assertEqual(fixed["result"], markdown)
        remaining_types = sorted(
            issue["type"] for issue in fixed["unfixable_issues"]
        )
        self.assertEqual(
            remaining_types,
            ["column_count_mismatch", "invalid_alignment_row"],
        )

    def test_fix_passes_non_table_content_through_unchanged(self) -> None:
        markdown = (
            "# Title\n"
            "\n"
            "```python\n"
            "x = 1 | 2\n"
            "```\n"
            "\n"
            "| H1 |\n"
            "| --- |\n"
            "| a |\n"
            "\n"
            "trailing prose\n"
        )
        fixed = self.tool.execute(mode="fix", markdown=markdown)
        self.assertEqual(fixed["result"], markdown)
        self.assertEqual(fixed["fixes_applied"], [])
        self.assertEqual(fixed["unfixable_issues"], [])

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def test_stats_arithmetic(self) -> None:
        markdown = (
            "| a | b | c |\n"
            "| --- | --- | --- |\n"
            "| 1 | 2 | 3 |\n"
            "\n"
            "one | two\n"
        )
        stats = self.tool.execute(mode="stats", markdown=markdown)
        self.assertEqual(stats["mode"], "stats")
        self.assertEqual(stats["table_count"], 2)
        self.assertEqual(stats["shapes"], ["3x3", "1x2"])
        self.assertEqual(stats["max_cols"], 3)
        # 3+3+3 cells in the first table, 2 in the second.
        self.assertEqual(stats["total_cells"], 11)

    def test_stats_counts_actual_cells_of_ragged_tables(self) -> None:
        markdown = "| a | b |\n| --- |\n| 1 | 2 | 3 |\n"
        stats = self.tool.execute(mode="stats", markdown=markdown)
        self.assertEqual(stats["table_count"], 1)
        self.assertEqual(stats["shapes"], ["3x2"])
        self.assertEqual(stats["max_cols"], 2)
        # 2 + 1 + 3 actual pipe-separated cells.
        self.assertEqual(stats["total_cells"], 6)

    def test_stats_without_tables(self) -> None:
        stats = self.tool.execute(mode="stats", markdown="plain text only")
        self.assertEqual(stats["table_count"], 0)
        self.assertEqual(stats["shapes"], [])
        self.assertEqual(stats["max_cols"], 0)
        self.assertEqual(stats["total_cells"], 0)

    def test_stats_ignores_fenced_content(self) -> None:
        markdown = "```\n| a | b |\n| --- | --- |\n```\n"
        stats = self.tool.execute(mode="stats", markdown=markdown)
        self.assertEqual(stats["table_count"], 0)
        self.assertEqual(stats["total_cells"], 0)

    # ------------------------------------------------------------------ #
    # Determinism and the public run() entry point
    # ------------------------------------------------------------------ #

    def test_deterministic_output(self) -> None:
        markdown = "| a |\n| x | y |\n"
        first = self.tool.execute(mode="validate", markdown=markdown)
        second = self.tool.execute(mode="validate", markdown=markdown)
        self.assertEqual(first, second)
        fixed_first = self.tool.execute(mode="fix", markdown=markdown)
        fixed_second = self.tool.execute(mode="fix", markdown=markdown)
        self.assertEqual(fixed_first, fixed_second)

    # ------------------------------------------------------------------ #
    # Input validation error matrix
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="render", markdown=CLEAN_TABLE)
        self.assertIn("mode must be one of", str(ctx.exception))
        self.assertIn("render", str(ctx.exception))

    def test_invalid_markdown_type(self) -> None:
        for bad in (None, 123, True, ["| a |"]):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(mode="validate", markdown=bad)
            self.assertIn("markdown must be a non-empty string", str(ctx.exception))

    def test_blank_markdown_rejected(self) -> None:
        for bad in ("", "   \n  \n"):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(mode="validate", markdown=bad)
            self.assertIn("non-empty string", str(ctx.exception))

    def test_markdown_length_limit(self) -> None:
        oversized = "| a |\n" + ("x" * 100_000)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="validate", markdown=oversized)
        self.assertIn("100,000-character limit", str(ctx.exception))

    def test_invalid_fix_modes_type(self) -> None:
        for bad in ("pad_short_rows", 42, True, {"pad_short_rows": True}):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(mode="fix", markdown="| a |", fix_modes=bad)
            self.assertIn("fix_modes must be a list drawn from", str(ctx.exception))

    def test_invalid_fix_modes_entries(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="fix", markdown="| a |", fix_modes=["uppercase_headers"]
            )
        self.assertIn("fix_modes entries must come from", str(ctx.exception))
        self.assertIn("uppercase_headers", str(ctx.exception))

    def test_empty_fix_modes_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="fix", markdown="| a |", fix_modes=[])
        self.assertIn("non-empty list", str(ctx.exception))

    def test_duplicate_fix_modes_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="fix",
                markdown="| a |",
                fix_modes=["pad_short_rows", "pad_short_rows"],
            )
        self.assertIn("duplicate entry", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # Class surface
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertEqual(self.tool.name, "markdown_table_validator_tool")
        self.assertEqual(
            MarkdownTableValidatorTool, DirectMarkdownTableValidatorTool
        )
        self.assertIn("pad_short_rows", MarkdownTableValidatorTool.FIX_MODES)
        self.assertIn("validate", MarkdownTableValidatorTool.MODES)


if __name__ == "__main__":
    unittest.main()
