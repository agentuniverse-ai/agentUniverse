#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_csv_lint_tool.py

"""Offline unit tests for CsvLintTool.

The tool is built purely on the standard library and never touches
the filesystem, the network or a database, so this suite runs fully
offline. Assertions are exact ground truths: every lint rule is
checked in its triggering shape and in a non-triggering control
shape; delimiter sniffing (including the quoted-candidate rule and
tie-breaks), mixed CRLF/LF/CR terminator detection with hand-derived
first-differing records, quoted commas / escaped quotes / multi-line
cells, BOM handling, secret-column masking, profile arithmetic
verified by hand, fix-mode exact outputs with a re-lint-clean
round-trip and idempotence, and the full option error matrix
including per-mode option gating.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import CsvLintTool
from agentuniverse.agent.action.tool.common_tool.csv_lint_tool import (
    CsvLintTool as DirectCsvLintTool,
)


def _codes(result: dict) -> list:
    return [finding["code"] for finding in result["findings"]]


def _remaining_codes(result: dict) -> list:
    return [finding["code"] for finding in result["remaining"]]


def _finding(result: dict, code: str) -> dict:
    matches = [f for f in result["findings"] if f["code"] == code]
    assert matches, f"{code} not in {[f['code'] for f in result['findings']]}"
    return matches[0]


class CsvLintToolBasicsTest(unittest.TestCase):
    """Export surface, determinism and ok semantics."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(CsvLintTool, DirectCsvLintTool)

    def test_name_modes_and_rule_codes(self) -> None:
        self.assertEqual(self.tool.name, "csv_lint_tool")
        self.assertEqual(SqlModes(), ("lint", "profile", "fix"))
        self.assertEqual(len(CsvLintTool.RULE_CODES), 14)

    def test_deterministic_repeat(self) -> None:
        text = "a,b\nc\r\n\nd,e,f\n"
        first = self.tool.execute(mode="lint", csv_text=text)
        second = self.tool.execute(mode="lint", csv_text=text)
        self.assertEqual(first, second)

    def test_info_only_is_ok(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="\ufeffa,b\n1,2\n")
        self.assertEqual(_codes(result), ["CSV001"])
        self.assertTrue(result["ok"])

    def test_warning_breaks_ok(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\nc\n")
        self.assertFalse(result["ok"])
        self.assertIn("CSV003", _codes(result))

    def test_findings_sorted_by_row_col_code(self) -> None:
        # Row 1 col 2 whitespace header cell, row 3 ragged row.
        result = self.tool.execute(mode="lint", csv_text="a, b\n1,2\n3\n")
        keys = [
            (f["row"], f["col"] or 0, f["code"]) for f in result["findings"]
        ]
        self.assertEqual(keys, sorted(keys))

    def test_value_preview_cap(self) -> None:
        # Whitespace around a 100-character body triggers CSV008 and
        # the 102-character escaped cell is capped to 40.
        result = self.tool.execute(
            mode="lint", csv_text="a\n" + " " + "x" * 100 + " " + "\n"
        )
        finding = _finding(result, "CSV008")
        self.assertEqual(len(finding["value_preview"]), 40)
        self.assertTrue(finding["value_preview"].endswith("..."))
        self.assertEqual(finding["value_preview"], " " + "x" * 36 + "...")

    def test_value_preview_escapes_control_characters(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text='a\n"x\ny\tz "\n'
        )
        finding = _finding(result, "CSV008")
        self.assertEqual(finding["value_preview"], 'x\\ny\\tz ')


class CsvLintToolSniffingTest(unittest.TestCase):
    """Delimiter auto-sniffing, explicit override and validation."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    def test_sniff_semicolon(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a;b\nc;d\n")
        self.assertEqual(result["delimiter"], ";")
        self.assertTrue(result["delimiter_sniffed"])

    def test_sniff_tab(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a\tb\tc\n")
        self.assertEqual(result["delimiter"], "\t")

    def test_sniff_pipe(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="p|q\nr|s\n")
        self.assertEqual(result["delimiter"], "|")

    def test_sniff_tie_prefers_comma(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b;c,d\n")
        self.assertEqual(result["delimiter"], ",")

    def test_sniff_no_candidate_defaults_to_comma(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="abc\ndef\n")
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(result["column_count"], 1)

    def test_sniff_ignores_quoted_candidates(self) -> None:
        # The comma sits inside quotes; only the semicolon counts.
        result = self.tool.execute(mode="lint", csv_text='"x,y";z\n')
        self.assertEqual(result["delimiter"], ";")

    def test_explicit_delimiter_overrides_sniffing(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b\nc,d\n", delimiter="|"
        )
        self.assertEqual(result["delimiter"], "|")
        self.assertFalse(result["delimiter_sniffed"])
        self.assertEqual(result["column_count"], 1)

    def test_invalid_delimiter_raises(self) -> None:
        for bad in (":", "ab", 5):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lint", csv_text="a,b\n", delimiter=bad)


class CsvLintToolRuleTest(unittest.TestCase):
    """Every rule: triggering shape plus non-triggering control."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    # -- CSV001 bom -------------------------------------------------------

    def test_csv001_bom(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="\ufeffa,b\n1,2\n"
        )
        self.assertEqual(_codes(result), ["CSV001"])
        finding = _finding(result, "CSV001")
        self.assertEqual(finding["severity"], "info")
        self.assertEqual((finding["row"], finding["col"]), (1, 1))
        # The BOM is stripped: the table itself is clean.
        self.assertEqual((result["row_count"], result["column_count"]), (1, 2))

    def test_csv001_control_no_bom(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n1,2\n")
        self.assertEqual(result["findings"], [])

    # -- CSV002 mixed_line_terminators ------------------------------------

    def test_csv002_crlf_and_lf(self) -> None:
        # crlf ends record 1, lf ends record 2: counts tie 1-1, the
        # tie-break makes crlf dominant, so the lf ends the first
        # differing record -> row 2.
        result = self.tool.execute(mode="lint", csv_text="a,b\r\nc,d\ne,f")
        finding = _finding(result, "CSV002")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual(finding["row"], 2)
        self.assertIn("1 CRLF", finding["message"])
        self.assertIn("1 LF", finding["message"])
        self.assertFalse(result["ok"])

    def test_csv002_control_pure_crlf(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\r\nc,d\r\n")
        self.assertNotIn("CSV002", _codes(result))

    def test_csv002_control_cr_only(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\rc,d\r")
        self.assertNotIn("CSV002", _codes(result))

    def test_csv002_control_quoted_newline_not_counted(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text='a,b\n"x\ny",2\n'
        )
        self.assertNotIn("CSV002", _codes(result))

    # -- CSV003 / CSV004 ragged rows --------------------------------------

    def test_csv003_ragged_short(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,c\n1,2\n")
        self.assertEqual(_codes(result), ["CSV003", "CSV005"])
        finding = _finding(result, "CSV003")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual(finding["row"], 2)
        self.assertEqual(finding["col"], None)
        self.assertIn("2 field(s), expected 3", finding["message"])

    def test_csv003_control_full_width(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,c\n1,2,3\n")
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["ok"])

    def test_csv004_ragged_long(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,c\n1,2,3,4\n")
        self.assertEqual(_codes(result), ["CSV004", "CSV005"])
        finding = _finding(result, "CSV004")
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["row"], 2)
        self.assertIn("4 field(s), expected 3", finding["message"])

    def test_ragged_headerless_uses_modal_width(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="1,2\n3\n4,5\n", has_header=False
        )
        self.assertEqual(result["column_count"], 2)
        self.assertEqual(_codes(result), ["CSV003", "CSV005"])
        self.assertEqual(_finding(result, "CSV003")["row"], 2)

    def test_ragged_headerless_modal_tie_prefers_smaller(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="1,2\n3,4,5\n", has_header=False
        )
        self.assertEqual(result["column_count"], 2)
        self.assertEqual(_codes(result), ["CSV004", "CSV005"])
        self.assertEqual(_finding(result, "CSV004")["row"], 2)

    # -- CSV005 inconsistent_column_count ---------------------------------

    def test_csv005_breakdown_message(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b,c\n1,2,3\n4,5\n6,7,8\n"
        )
        finding = _finding(result, "CSV005")
        self.assertEqual(finding["row"], 3)
        # The header counts toward the width breakdown.
        self.assertIn("3 row(s) with 3 field(s)", finding["message"])
        self.assertIn("1 row(s) with 2 field(s)", finding["message"])
        self.assertIn("expected 3 from the header", finding["message"])

    def test_csv005_control_uniform_widths(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b\n1,2\n3,4\n"
        )
        self.assertNotIn("CSV005", _codes(result))

    # -- CSV006 empty_header_cell -----------------------------------------

    def test_csv006_empty_header_cell(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,,c\n1,2,3\n")
        finding = _finding(result, "CSV006")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual((finding["row"], finding["col"]), (1, 2))
        self.assertEqual(finding["value_preview"], "")

    def test_csv006_whitespace_header_cell_also_flags_whitespace(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a, ,c\n1,2,3\n")
        self.assertEqual(_codes(result), ["CSV006", "CSV008"])
        self.assertEqual(_finding(result, "CSV006")["col"], 2)
        self.assertEqual(_finding(result, "CSV008")["value_preview"], " ")

    # -- CSV007 duplicate_headers -----------------------------------------

    def test_csv007_duplicate_headers(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,a\n1,2,3\n")
        finding = _finding(result, "CSV007")
        self.assertEqual(finding["severity"], "error")
        self.assertEqual((finding["row"], finding["col"]), (1, 3))
        self.assertIn("first seen at column 1", finding["message"])

    def test_csv007_control_case_sensitive(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,A\n1,2,3\n")
        self.assertEqual(result["findings"], [])

    def test_csv007_triple_reports_each_later_duplicate(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,a,a\n1,2,3\n")
        duplicates = [f for f in result["findings"] if f["code"] == "CSV007"]
        self.assertEqual([f["col"] for f in duplicates], [2, 3])

    # -- CSV008 cell_whitespace -------------------------------------------

    def test_csv008_data_cell(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n 1 ,2\n")
        finding = _finding(result, "CSV008")
        self.assertEqual(finding["severity"], "info")
        self.assertEqual((finding["row"], finding["col"]), (2, 1))
        self.assertEqual(finding["value_preview"], " 1 ")
        self.assertIn("2 character(s)", finding["message"])
        self.assertTrue(result["ok"])

    def test_csv008_quoted_intentional_spaces_still_flagged(self) -> None:
        result = self.tool.execute(mode="lint", csv_text='a,b\n" x ",y\n')
        self.assertEqual(_codes(result), ["CSV008"])
        self.assertEqual(_finding(result, "CSV008")["value_preview"], " x ")

    def test_csv008_control_clean_cells(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n1,2\n")
        self.assertEqual(result["findings"], [])

    # -- CSV009 empty_rows -------------------------------------------------

    def test_csv009_single_summary_with_count(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n\n1,2\n \n3,4\n")
        finding = _finding(result, "CSV009")
        self.assertEqual(finding["severity"], "info")
        self.assertEqual(finding["row"], 2)
        self.assertIn("2 empty row(s) at record(s) 2, 4", finding["message"])
        # Empty rows are excluded from the table.
        self.assertEqual(result["row_count"], 2)
        self.assertTrue(result["ok"])

    def test_csv009_row_list_capped_at_five(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b\n\n\n\n\n\n\n\n1,2\n"
        )
        finding = _finding(result, "CSV009")
        self.assertIn("7 empty row(s) at record(s) 2, 3, 4, 5, 6 ...",
                      finding["message"])

    def test_csv009_control_no_empty_rows(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n1,2\n")
        self.assertNotIn("CSV009", _codes(result))

    # -- CSV010 header_only -------------------------------------------------

    def test_csv010_header_only(self) -> None:
        for text in ("a,b\n", "a,b"):
            result = self.tool.execute(mode="lint", csv_text=text)
            finding = _finding(result, "CSV010")
            self.assertEqual(finding["severity"], "warning")
            self.assertEqual(finding["row"], 1)
            self.assertEqual(result["row_count"], 0)
            self.assertFalse(result["ok"])

    def test_csv010_control_with_data(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b\n1,2\n")
        self.assertNotIn("CSV010", _codes(result))

    def test_csv010_control_headerless_single_row(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="1,2\n", has_header=False
        )
        self.assertNotIn("CSV010", _codes(result))
        self.assertEqual(result["row_count"], 1)

    # -- CSV011 unclosed_quote ----------------------------------------------

    def test_csv011_unterminated_quote(self) -> None:
        result = self.tool.execute(mode="lint", csv_text='a,b\n1,"2\n')
        self.assertEqual(_codes(result), ["CSV010", "CSV011"])
        finding = _finding(result, "CSV011")
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["row"], 2)
        self.assertIn("unexpected end of data", finding["message"])
        self.assertFalse(result["ok"])

    def test_csv011_partial_table_still_linted(self) -> None:
        result = self.tool.execute(mode="lint", csv_text='a,b\n1,2\n3,"x\n')
        self.assertEqual(_codes(result), ["CSV011"])
        self.assertEqual(_finding(result, "CSV011")["row"], 3)
        self.assertEqual(result["row_count"], 1)

    def test_csv011_stray_quote_in_first_record(self) -> None:
        result = self.tool.execute(mode="lint", csv_text='a,"b"c,d\n')
        self.assertEqual(_codes(result), ["CSV011"])
        finding = _finding(result, "CSV011")
        self.assertEqual(finding["row"], 1)
        self.assertIn("expected", finding["message"])
        self.assertEqual(result["row_count"], 0)

    # -- CSV012 numeric_column_mixed_locale ----------------------------------

    def test_csv012_dot_and_comma_numbers(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a;b\n1.5;2\n1,234;3\n"
        )
        finding = _finding(result, "CSV012")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual((finding["row"], finding["col"]), (3, 1))
        self.assertIn('column "a"', finding["message"])

    def test_csv012_control_single_style(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a;b\n1.5;2.25\n")
        self.assertNotIn("CSV012", _codes(result))

    def test_csv012_control_requires_numeric_majority(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a;b\nhello;1\nworld;2\n1.5;3\n1,234;4\n"
        )
        self.assertNotIn("CSV012", _codes(result))

    def test_csv012_quoted_comma_number_with_comma_delimiter(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text='a,b\n1.5,x\n"1,234",y\n'
        )
        self.assertEqual(_codes(result), ["CSV012"])
        self.assertEqual(_finding(result, "CSV012")["col"], 1)

    # -- CSV013 field_over_max_len --------------------------------------------

    def test_csv013_over_limit(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b\nabcdef,2\n", max_field_len=5
        )
        finding = _finding(result, "CSV013")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual((finding["row"], finding["col"]), (2, 1))
        self.assertIn("field length 6 exceeds max_field_len 5",
                      finding["message"])

    def test_csv013_control_at_limit(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b\nabcde,2\n", max_field_len=5
        )
        self.assertNotIn("CSV013", _codes(result))

    def test_csv013_off_by_default(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a\n" + "x" * 99 + "\n")
        self.assertNotIn("CSV013", _codes(result))

    # -- CSV014 over_max_columns -----------------------------------------------

    def test_csv014_over_limit(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a,b,c\n1,2,3\n", max_columns=2
        )
        finding = _finding(result, "CSV014")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual(finding["row"], 1)
        self.assertIn("table width 3 exceeds max_columns 2",
                      finding["message"])

    def test_csv014_off_by_default(self) -> None:
        result = self.tool.execute(mode="lint", csv_text="a,b,c\n1,2,3\n")
        self.assertNotIn("CSV014", _codes(result))

    # -- rules disable map -------------------------------------------------------

    def test_rules_disable_single_rule(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a, b\n1,2\n", rules={"CSV008": False}
        )
        self.assertEqual(result["findings"], [])

    def test_rules_disable_keeps_others(self) -> None:
        result = self.tool.execute(
            mode="lint", csv_text="a, b\n1\n", rules={"CSV008": False}
        )
        self.assertEqual(_codes(result), ["CSV003", "CSV005"])

    def test_rules_unknown_code_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", csv_text="a,b\n", rules={"CSV999": False}
            )

    def test_rules_non_boolean_value_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", csv_text="a,b\n", rules={"CSV008": 0}
            )

    def test_rules_non_dict_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="a,b\n", rules=["CSV008"])


class CsvLintToolStructureTest(unittest.TestCase):
    """RFC 4180 quoting shapes parse without false findings."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    def test_quoted_commas_escaped_quotes_multiline_cells(self) -> None:
        text = (
            'name,note\n'
            '"Doe, John","line1\nline2"\n'
            '"say ""hi""",x\n'
        )
        result = self.tool.execute(mode="lint", csv_text=text)
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["ok"])
        self.assertEqual((result["row_count"], result["column_count"]), (2, 2))
        self.assertEqual(result["delimiter"], ",")

    def test_lf_terminators_with_crlf_inside_quoted_cell(self) -> None:
        # The only CRLF sits inside quotes: one style outside -> clean.
        result = self.tool.execute(
            mode="lint", csv_text='a,b\n"x\r\ny",2\n'
        )
        self.assertEqual(result["findings"], [])

    def test_row_numbers_count_blank_records(self) -> None:
        # Record 1 header, 2 blank, 3 short: the ragged row is 3.
        result = self.tool.execute(mode="lint", csv_text="a,b\n\n1\n")
        self.assertEqual(_finding(result, "CSV003")["row"], 3)


class CsvLintToolProfileTest(unittest.TestCase):
    """Profile mode: hand-verified per-column arithmetic."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    @staticmethod
    def _sample() -> str:
        return (
            "id,amount,active,day,token,note\n"
            "1,1.5,true,2026-01-02,abc,hello\n"
            "2,2.5,false,2026-01-03T10:30:00,abc,world\n"
            "3,,,2026-01-04,abc,\n"
        )

    def test_profile_full_table(self) -> None:
        result = self.tool.execute(mode="profile", csv_text=self._sample())
        self.assertEqual(result["mode"], "profile")
        self.assertEqual(result["delimiter"], ",")
        self.assertTrue(result["delimiter_sniffed"])
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(result["column_count"], 6)
        columns = result["columns"]
        self.assertEqual([c["name"] for c in columns],
                         ["id", "amount", "active", "day", "token", "note"])

        id_col, amount_col, active_col, day_col, token_col, note_col = columns

        self.assertEqual(id_col["type"], "int")
        self.assertFalse(id_col["nullable"])
        self.assertEqual(id_col["fill_rate"], 1.0)
        self.assertEqual(id_col["distinct_count"], 3)
        self.assertEqual(id_col["top_values"],
                         [{"value": "1", "count": 1},
                          {"value": "2", "count": 1},
                          {"value": "3", "count": 1}])
        self.assertEqual((id_col["min"], id_col["max"]), (1, 3))

        self.assertEqual(amount_col["type"], "float")
        self.assertTrue(amount_col["nullable"])
        self.assertEqual(amount_col["fill_rate"], 0.6667)
        self.assertEqual(amount_col["distinct_count"], 2)
        self.assertEqual((amount_col["min"], amount_col["max"]), (1.5, 2.5))

        self.assertEqual(active_col["type"], "bool")
        self.assertTrue(active_col["nullable"])
        self.assertEqual(active_col["fill_rate"], 0.6667)
        # Ties sort by value: "false" before "true".
        self.assertEqual(active_col["top_values"],
                         [{"value": "false", "count": 1},
                          {"value": "true", "count": 1}])
        self.assertIsNone(active_col["min"])
        self.assertIsNone(active_col["max"])

        self.assertEqual(day_col["type"], "date")
        self.assertEqual(day_col["fill_rate"], 1.0)
        self.assertEqual(day_col["distinct_count"], 3)

        # Secret-named column: counts kept, values masked.
        self.assertEqual(token_col["type"], "string")
        self.assertEqual(token_col["distinct_count"], 1)
        self.assertEqual(token_col["top_values"], [{"value": "***", "count": 3}])

        self.assertEqual(note_col["type"], "string")
        self.assertTrue(note_col["nullable"])
        self.assertEqual(note_col["fill_rate"], 0.6667)

    def test_profile_datetime_type(self) -> None:
        result = self.tool.execute(
            mode="profile", csv_text="t\n2026-01-02T10:30:00\n2026-01-03 09:15\n"
        )
        column = result["columns"][0]
        self.assertEqual(column["type"], "datetime")
        self.assertEqual(column["distinct_count"], 2)

    def test_profile_type_tie_prefers_int(self) -> None:
        result = self.tool.execute(mode="profile", csv_text="mix\n1\nhello\n")
        self.assertEqual(result["columns"][0]["type"], "int")

    def test_profile_leading_zero_stays_string(self) -> None:
        result = self.tool.execute(mode="profile", csv_text="z\n007\n")
        column = result["columns"][0]
        self.assertEqual(column["type"], "string")
        self.assertEqual(column["distinct_count"], 1)

    def test_profile_headerless_names_and_stats(self) -> None:
        result = self.tool.execute(
            mode="profile", csv_text="1,a\n2,b\n", has_header=False
        )
        self.assertEqual(result["has_header"], False)
        self.assertEqual([c["name"] for c in result["columns"]],
                         ["col_1", "col_2"])
        first, second = result["columns"]
        self.assertEqual(first["type"], "int")
        self.assertEqual((first["min"], first["max"]), (1, 2))
        self.assertEqual(second["type"], "string")
        self.assertEqual(second["top_values"],
                         [{"value": "a", "count": 1},
                          {"value": "b", "count": 1}])

    def test_profile_ragged_long_row_contributes_extra_cells(self) -> None:
        result = self.tool.execute(mode="profile", csv_text="a,b\n1,2,3\n")
        self.assertEqual(result["column_count"], 3)
        self.assertEqual([c["name"] for c in result["columns"]],
                         ["a", "b", "col_3"])
        self.assertEqual(result["columns"][2]["top_values"],
                         [{"value": "3", "count": 1}])

    def test_profile_header_only_columns_are_empty(self) -> None:
        result = self.tool.execute(mode="profile", csv_text="a,b\n")
        self.assertEqual(result["row_count"], 0)
        for column in result["columns"]:
            self.assertEqual(column["type"], "empty")
            self.assertEqual(column["fill_rate"], 0.0)
            self.assertEqual(column["distinct_count"], 0)
            self.assertEqual(column["top_values"], [])
            self.assertIsNone(column["min"])

    def test_profile_top_values_capped_at_five(self) -> None:
        result = self.tool.execute(
            mode="profile", csv_text="v\nb\nb\nc\nc\nd\ne\nf\ng\n"
        )
        top = result["columns"][0]["top_values"]
        self.assertEqual(len(top), 5)
        self.assertEqual([entry["value"] for entry in top],
                         ["b", "c", "d", "e", "f"])
        self.assertEqual([entry["count"] for entry in top], [2, 2, 1, 1, 1])

    def test_profile_parse_error_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="profile", csv_text='a,b\n1,"2\n')


class CsvLintToolFixTest(unittest.TestCase):
    """Fix mode: exact outputs, re-lint round-trip and idempotence."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    def test_fix_kitchen_sink_round_trip(self) -> None:
        text = "\ufeffname, qty \r\n Alice , 7 \r\n\r\nBob,9\n"
        result = self.tool.execute(mode="fix", csv_text=text)
        self.assertEqual(result["fixed_text"], "name,qty\nAlice,7\nBob,9\n")
        self.assertEqual(result["applied"], [
            {"action": "strip_bom"},
            {"action": "normalize_terminator", "to": "lf"},
            {"action": "drop_empty_rows", "count": 1},
            {"action": "strip_cell_whitespace", "count": 3},
        ])
        self.assertEqual(result["remaining"], [])
        self.assertEqual(result["remaining_count"], 0)
        self.assertEqual((result["row_count"], result["column_count"]), (2, 2))
        # Re-lint of the fixed text is clean.
        relint = self.tool.execute(mode="lint", csv_text=result["fixed_text"])
        self.assertEqual(relint["findings"], [])
        self.assertTrue(relint["ok"])

    def test_fix_pads_short_rows(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="a,b,c\n1,2\n2,3,4\n"
        )
        self.assertEqual(result["fixed_text"], "a,b,c\n1,2,\n2,3,4\n")
        self.assertEqual(result["applied"],
                         [{"action": "pad_short_rows", "count": 1}])
        self.assertEqual(result["remaining"], [])

    def test_fix_pad_short_rows_disabled_keeps_finding(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="a,b,c\n1,2\n2,3,4\n", pad_short_rows=False
        )
        self.assertEqual(result["applied"], [])
        self.assertEqual(_remaining_codes(result), ["CSV003", "CSV005"])
        self.assertEqual(result["fixed_text"], "a,b,c\n1,2\n2,3,4\n")

    def test_fix_strip_whitespace_disabled(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="a, b\n1,2\n", strip_whitespace=False
        )
        self.assertEqual(result["applied"], [])
        self.assertEqual(_remaining_codes(result), ["CSV008"])
        self.assertEqual(result["fixed_text"], "a, b\n1,2\n")

    def test_fix_drop_empty_rows_disabled(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="a,b\n\n1,2\n", drop_empty_rows=False
        )
        self.assertEqual(result["applied"], [])
        self.assertEqual(_remaining_codes(result), ["CSV009"])
        self.assertEqual(result["fixed_text"], "a,b\n\n1,2\n")

    def test_fix_crlf_terminator(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="a,b\n1,2\n", terminator="crlf"
        )
        self.assertEqual(result["fixed_text"], "a,b\r\n1,2\r\n")
        self.assertEqual(result["applied"],
                         [{"action": "normalize_terminator", "to": "crlf"}])
        self.assertEqual(result["remaining"], [])

    def test_fix_crlf_source_normalized_to_lf(self) -> None:
        result = self.tool.execute(mode="fix", csv_text="a,b\r\n1,2\r\n")
        self.assertEqual(result["fixed_text"], "a,b\n1,2\n")
        self.assertEqual(
            result["applied"], [{"action": "normalize_terminator", "to": "lf"}]
        )

    def test_fix_ragged_long_row_not_repaired(self) -> None:
        result = self.tool.execute(mode="fix", csv_text="a,b\n1,2,3\n")
        self.assertEqual(result["applied"], [])
        self.assertEqual(_remaining_codes(result), ["CSV004", "CSV005"])
        self.assertEqual(result["fixed_text"], "a,b\n1,2,3\n")

    def test_fix_duplicate_headers_not_repaired(self) -> None:
        result = self.tool.execute(mode="fix", csv_text="a,a\n1,2\n")
        self.assertEqual(_remaining_codes(result), ["CSV007"])
        self.assertEqual(result["applied"], [])

    def test_fix_drops_unnecessary_quotes_preserving_values(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text='"a","b"\n"1",2\n'
        )
        self.assertEqual(result["fixed_text"], "a,b\n1,2\n")
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["remaining"], [])

    def test_fix_preserves_quoted_multiline_cell(self) -> None:
        text = 'a,b\n"x\ny",2\n'
        result = self.tool.execute(mode="fix", csv_text=text)
        self.assertEqual(result["fixed_text"], text)
        self.assertIn("x\ny", result["fixed_text"])
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["remaining"], [])

    def test_fix_is_idempotent(self) -> None:
        text = "\ufeffa, b\r\n 1 ,2\r\n\r\n3,4\n"
        first = self.tool.execute(mode="fix", csv_text=text)
        second = self.tool.execute(mode="fix", csv_text=first["fixed_text"])
        self.assertEqual(second["fixed_text"], first["fixed_text"])
        self.assertEqual(second["applied"], [])
        self.assertEqual(second["remaining"], [])

    def test_fix_headerless_pads_to_modal_width(self) -> None:
        result = self.tool.execute(
            mode="fix", csv_text="1,2\n3\n4,5\n", has_header=False
        )
        self.assertEqual(result["fixed_text"], "1,2\n3,\n4,5\n")
        self.assertEqual(result["applied"],
                         [{"action": "pad_short_rows", "count": 1}])
        self.assertEqual(result["remaining"], [])

    def test_fix_headerless_modal_tie_keeps_smaller_width(self) -> None:
        # Widths 2 and 1 tie: the expected width is the smaller one,
        # so the wide row stays ragged_long and is never truncated.
        result = self.tool.execute(
            mode="fix", csv_text="1,2\n3\n", has_header=False
        )
        self.assertEqual(result["column_count"], 1)
        self.assertEqual(result["fixed_text"], "1,2\n3\n")
        self.assertEqual(_remaining_codes(result), ["CSV004", "CSV005"])

    def test_fix_parse_error_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix", csv_text='a,b\n1,"2\n')

    def test_fix_nothing_remaining_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix", csv_text="\n\n")


class CsvLintToolErrorMatrixTest(unittest.TestCase):
    """Every strict-validation branch of the option surface."""

    def setUp(self) -> None:
        self.tool = CsvLintTool()

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="check", csv_text="a,b\n")

    def test_non_string_csv_text_raises(self) -> None:
        for bad in (None, 123, ["a,b"], b"a,b"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lint", csv_text=bad)

    def test_empty_csv_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="")

    def test_oversized_csv_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="a\n" * 60_000)

    def test_too_many_records_raises(self) -> None:
        text = "\n".join(f"r{i}" for i in range(10_001))
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text=text)

    def test_too_wide_row_raises(self) -> None:
        text = ",".join(f"c{j}" for j in range(1_001)) + "\n"
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text=text)

    def test_no_non_empty_record_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="\n\n\n")

    def test_bom_only_raises_value_error_in_every_mode(self) -> None:
        for mode in ("lint", "profile", "fix"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, csv_text="\ufeff")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="\ufeff", delimiter=";")

    def test_non_boolean_has_header_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", csv_text="a,b\n", has_header="yes")

    def test_max_field_len_bounds(self) -> None:
        for bad in (0, -1, 1_000_001, True, 2.5, "5"):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="lint", csv_text="a,b\n", max_field_len=bad
                )

    def test_max_columns_bounds(self) -> None:
        for bad in (0, 1_001, False):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="lint", csv_text="a,b\n", max_columns=bad
                )

    def test_mode_option_gating(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="profile", csv_text="a,b\n", rules={}
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="fix", csv_text="a,b\n", max_field_len=5
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", csv_text="a,b\n", terminator="lf"
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="profile", csv_text="a,b\n", strip_whitespace=True
            )

    def test_fix_option_validation(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="fix", csv_text="a,b\n", strip_whitespace="yes"
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="fix", csv_text="a,b\n", terminator="cr"
            )

    def test_findings_capped_with_true_count(self) -> None:
        # 210 whitespace cells -> 210 findings, list capped at 200.
        text = "a\n" + "\n".join([" x"] * 210) + "\n"
        result = self.tool.execute(mode="lint", csv_text=text)
        self.assertEqual(result["finding_count"], 210)
        self.assertTrue(result["findings_truncated"])
        self.assertEqual(len(result["findings"]), 200)

    def test_ok_false_when_warning_sits_beyond_findings_cap(self) -> None:
        text = "a,b\n" + "\n".join([" x,y"] * 210) + "\nz\n"
        result = self.tool.execute(mode="lint", csv_text=text)
        self.assertEqual(result["finding_count"], 212)
        self.assertTrue(result["findings_truncated"])
        self.assertEqual(len(result["findings"]), 200)
        self.assertFalse(any(
            finding["severity"] in ("error", "warning")
            for finding in result["findings"]
        ))
        self.assertFalse(result["ok"])


def SqlModes() -> tuple:
    """Indirection keeps the import surface of the test obvious."""
    return CsvLintTool.MODES


if __name__ == "__main__":
    unittest.main()
