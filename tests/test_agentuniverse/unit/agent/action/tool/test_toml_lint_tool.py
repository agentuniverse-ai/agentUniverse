#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_toml_lint_tool.py

"""Offline unit tests for TomlLintTool.

The tool is built purely on the standard library and never touches
the filesystem or the network, so this suite runs fully offline.
Assertions are exact ground truths: every lint rule is checked in
its triggering shape and in a non-triggering control shape; the
tomllib error mapping is verified differentially against real
tomllib over 30 malformed documents (the tool's line/col must equal
the position tomllib embeds in its own message, including the
"(at end of document)" mapping); masking (strings and comments never
trigger raw-text rules), mixed-type arrays, offset/naive datetimes,
BOM behavior, profile arithmetic verified by hand, fix_hints with a
re-lint round trip and idempotence, and the full option error matrix
including per-mode option gating are all covered.
"""

import re
import tomllib
import unittest

from agentuniverse.agent.action.tool.common_tool import TomlLintTool
from agentuniverse.agent.action.tool.common_tool.toml_lint_tool import (
    TomlLintTool as DirectTomlLintTool,
)

_TOML_POSITION = re.compile(r"\(at line (\d+), column (\d+)\)\s*\Z")


def _codes(result: dict) -> list:
    return [finding["code"] for finding in result["findings"]]


def _finding(result: dict, code: str) -> dict:
    matches = [f for f in result["findings"] if f["code"] == code]
    assert matches, f"{code} not in {[f['code'] for f in result['findings']]}"
    return matches[0]


def _remaining_codes(result: dict) -> list:
    return [finding["code"] for finding in result["remaining"]]


class TomlLintToolBasicsTest(unittest.TestCase):
    """Export surface, vocabulary, determinism and ok semantics."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(TomlLintTool, DirectTomlLintTool)

    def test_name_modes_and_rule_codes(self) -> None:
        self.assertEqual(self.tool.name, "toml_lint_tool")
        self.assertEqual(TomlLintTool.MODES,
                         ("lint", "profile", "fix_hints"))
        self.assertEqual(len(TomlLintTool.RULE_CODES), 10)
        self.assertEqual(TomlLintTool.RULE_CODES,
                         tuple(f"TOML{i:03d}" for i in range(1, 11)))

    def test_deterministic_repeat(self) -> None:
        text = 'a = 1  \nb = "x"\n[t]\nc = [1, "y"]\n'
        first = self.tool.execute(mode="lint", toml_text=text)
        second = self.tool.execute(mode="lint", toml_text=text)
        self.assertEqual(first, second)

    def test_ok_semantics(self) -> None:
        info_only = self.tool.execute(
            mode="lint", toml_text='a = [1, "x"]  \n')
        self.assertTrue(info_only["ok"])
        self.assertTrue(info_only["valid"])
        with_warning = self.tool.execute(mode="lint", toml_text="[t]\n")
        self.assertFalse(with_warning["ok"])
        self.assertTrue(with_warning["valid"])
        with_error = self.tool.execute(mode="lint", toml_text="a = True\n")
        self.assertFalse(with_error["ok"])
        self.assertFalse(with_error["valid"])

    def test_findings_sorted_by_line_col_code(self) -> None:
        text = (
            "a = [1, 'x']  \n"        # line 1: TOML003 + TOML005
            "b = 2\n"
            "c = 3  \n"               # line 3: TOML005
        )
        result = self.tool.execute(mode="lint", toml_text=text)
        keys = [(f["line"], f["col"] if f["col"] is not None else 0,
                 f["code"]) for f in result["findings"]]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(set(_codes(result)), {"TOML003", "TOML005"})

    def test_findings_cap_and_true_count(self) -> None:
        lines = [f"k{i} = [1, 'x']  " for i in range(250)]
        result = self.tool.execute(mode="lint",
                                   toml_text="\n".join(lines) + "\n")
        # 250 TOML003 findings (one per mixed array) plus the single
        # once-per-file TOML005 summary -> 251 findings, capped at 200.
        self.assertEqual(result["finding_count"], 251)
        self.assertTrue(result["findings_truncated"])
        self.assertEqual(len(result["findings"]), TomlLintTool.MAX_FINDINGS)


class TomlLintSyntaxMappingTest(unittest.TestCase):
    """TOML002: differential mapping against real tomllib over 30
    malformed documents — the tool must report exactly the position
    tomllib itself embeds in its message."""

    MALFORMED = [
        ("unterminated_string", 'a = "abc\n'),
        ("no_equal", '[x]\nfoo\n'),
        ("bad_number", "a = 1.2.3\n"),
        ("bad_date", "a = 1979-05-99\n"),
        ("bad_time", "a = 25:00:00\n"),
        ("unclosed_array", "a = [1, 2\n"),
        ("unclosed_table", "[x\n"),
        ("bad_table_name", "[x y]\na=1\n"),
        ("dup_inline_key", "a = {b=1, b=2}\n"),
        ("bare_nl_basic_string", 'a = "x\ny"\n'),
        ("bad_escape", 'a = "x\\qy"\n'),
        ("control_char_in_string", 'a = "x\x01y"\n'),
        ("underscore_double", "a = 1__000\n"),
        ("underscore_trailing", "a = 1000_\n"),
        ("bad_hex_digit", "a = 0x1G\n"),
        ("float_no_fraction", "a = 1.\n"),
        ("leading_zero_int", "a = 007\n"),
        ("plus_leading_zero", "a = +007\n"),
        ("bool_mixed_case", "a = tRue\n"),
        ("bool_capitalized", "a = True\n"),
        ("bool_upper", "a = TRUE\n"),
        ("inf_capitalized", "a = Inf\n"),
        ("nan_capitalized", "a = NaN\n"),
        ("array_missing_comma", "a = [1 2]\n"),
        ("overwrite_table_with_kv", "[a.b]\nx=1\n[a]\nb=1\n"),
        ("dup_table_header", "[a]\n[a]\n"),
        ("dup_table_with_keys", "[x]\na=1\n[x]\nb=2\n"),
        ("dup_key_in_table", "a = 1\na = 2\n"),
        ("dup_dotted_key", "a.b = 1\na.b = 2\n"),
        ("aot_then_plain_table", "[[a]]\n[a]\n"),
    ]

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    def test_every_malformed_doc_maps_tomllib_position(self) -> None:
        for name, text in self.MALFORMED:
            with self.subTest(doc=name):
                with self.assertRaises(tomllib.TOMLDecodeError) as caught:
                    tomllib.loads(text)
                result = self.tool.execute(mode="lint", toml_text=text)
                self.assertFalse(result["valid"])
                self.assertFalse(result["ok"])
                finding = _finding(result, "TOML002")
                self.assertEqual(finding["severity"], "error")
                message = str(caught.exception)
                match = _TOML_POSITION.search(message)
                if match is not None:
                    self.assertEqual(finding["line"], int(match.group(1)))
                    self.assertEqual(finding["col"], int(match.group(2)))
                elif "(at end of document)" in message:
                    # end-of-document errors: final physical line (the
                    # empty line when the text ends with a newline),
                    # no column
                    self.assertEqual(finding["line"], len(text.split("\n")))
                    self.assertIsNone(finding["col"])
                # message carries tomllib's wording minus the position
                core = re.sub(
                    r"\s*\(at (?:line \d+, column \d+"
                    r"|end of document)\)\s*\Z", "", message)
                self.assertIn(core, finding["message"])

    def test_malformed_doc_still_runs_line_rules(self) -> None:
        # Text-level rules still fire while the parse rule is present.
        result = self.tool.execute(
            mode="lint", toml_text="a = True  \nb = 1_0\nc = 100000\n")
        codes = set(_codes(result))
        self.assertIn("TOML002", codes)
        self.assertIn("TOML005", codes)
        self.assertIn("TOML007", codes)
        # parse-dependent rules are skipped for invalid documents
        self.assertNotIn("TOML003", codes)
        self.assertNotIn("TOML008", codes)
        self.assertNotIn("TOML009", codes)
        self.assertNotIn("TOML010", codes)

    def test_parse_dependent_rules_silent_on_syntax_error(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = [1, 'x']\nb = True\n")
        codes = set(_codes(result))
        self.assertIn("TOML002", codes)
        self.assertNotIn("TOML003", codes)

    def test_recursion_guard(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(
                mode="lint",
                toml_text="a = " + "[" * 3000 + "]" * 3000 + "\n")
        self.assertIn("recursion limit", str(caught.exception))


class TomlLintRuleTableTest(unittest.TestCase):
    """Every rule: triggering shape plus a non-triggering control."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    # --- TOML001 bom ---------------------------------------------------

    def test_bom_reported_and_stripped(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text="﻿a = 1\n")
        finding = _finding(result, "TOML001")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertFalse(result["ok"])
        # stripping happens before parsing: doc is otherwise valid
        self.assertTrue(
            all(f["code"] != "TOML002" for f in result["findings"]))

    def test_no_bom_no_finding(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="a = 1\n")
        self.assertNotIn("TOML001", _codes(result))

    def test_bom_byte_inside_string_is_not_a_bom(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text='a = "﻿"\n')
        self.assertNotIn("TOML001", _codes(result))

    # --- TOML003 mixed_array_types --------------------------------------

    def test_mixed_scalar_types_fires(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text="a = [1, \"two\", 3.5]\n")
        finding = _finding(result, "TOML003")
        self.assertEqual(finding["severity"], "info")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertIn("number", finding["message"])
        self.assertIn("string", finding["message"])
        self.assertTrue(result["ok"])  # info only

    def test_homogeneous_arrays_do_not_fire(self) -> None:
        for text in ("a = [1, 2, 3]\n",
                     "a = [1, 2.5]\n",
                     "a = [\"x\", 'y']\n",
                     "a = [true, false]\n",
                     "a = []\n"):
            result = self.tool.execute(mode="lint", toml_text=text)
            self.assertNotIn("TOML003", _codes(result), text)

    def test_int_and_float_are_one_number_class(self) -> None:
        # ints and floats are deliberately one class — [1, 2.5] is
        # ordinary numeric data, not a type mix.
        result = self.tool.execute(mode="lint",
                                   toml_text="a = [1, 2.5]\n")
        self.assertNotIn("TOML003", _codes(result))

    def test_bool_and_number_are_distinct(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text="a = [1, true]\n")
        self.assertIn("TOML003", _codes(result))

    def test_nested_containers_do_not_participate(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = [1, [\"x\"], {b = 2}]\n")
        self.assertNotIn("TOML003", _codes(result))

    def test_multiline_array_across_lines(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = [\n  1,\n  \"two\",  # comment\n]\n")
        finding = _finding(result, "TOML003")
        self.assertEqual(finding["line"], 1)

    def test_trailing_comma_and_datetimes(self) -> None:
        # datetime + date are distinct classes -> mixed
        result = self.tool.execute(
            mode="lint",
            toml_text="a = [1979-05-27, 1979-05-27T07:32:00Z]\n")
        self.assertIn("TOML003", _codes(result))
        # homogeneous datetimes (with a trailing comma) are not mixed
        result = self.tool.execute(
            mode="lint",
            toml_text="a = [1979-05-27T07:32:00Z, 1979-05-27T10:00:00,]\n")
        self.assertNotIn("TOML003", _codes(result))

    def test_string_elements_with_brackets_do_not_confuse(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text='a = ["[x, y]", 1]\n')
        self.assertIn("TOML003", _codes(result))
        result = self.tool.execute(
            mode="lint", toml_text='a = ["[x, y]", "z"]\n')
        self.assertNotIn("TOML003", _codes(result))

    def test_inline_table_commas_do_not_split_elements(self) -> None:
        # Commas inside an inline-table element never split the array;
        # containers do not participate in the type mix, so a single
        # scalar class alongside containers stays clean.
        result = self.tool.execute(
            mode="lint", toml_text="a = [{b = 1, c = 2}, 1]\n")
        self.assertNotIn("TOML003", _codes(result))
        # ...but two scalar classes among container elements still fire
        result = self.tool.execute(
            mode="lint", toml_text="a = [{b = 1, c = 2}, 1, \"x\"]\n")
        self.assertIn("TOML003", _codes(result))

    # --- TOML004 datetime_mixed_offsets ----------------------------------

    def test_offset_naive_mix_fires(self) -> None:
        result = self.tool.execute(
            mode="lint",
            toml_text="a = [1979-05-27T07:32:00Z, 1979-05-27T07:32:00]\n")
        finding = _finding(result, "TOML004")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertIn("1 aware", finding["message"])
        self.assertIn("1 naive", finding["message"])

    def test_both_offset_variants_do_not_fire(self) -> None:
        result = self.tool.execute(
            mode="lint",
            toml_text=("a = [1979-05-27T07:32:00Z, "
                       "1979-05-27T07:32:00+01:00]\n"))
        self.assertNotIn("TOML004", _codes(result))

    def test_both_naive_do_not_fire(self) -> None:
        result = self.tool.execute(
            mode="lint",
            toml_text="a = [1979-05-27T07:32:00, 1979-05-27T10:00:00]\n")
        self.assertNotIn("TOML004", _codes(result))

    def test_no_datetime_array_no_finding(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="a = [1, \"x\"]\n")
        self.assertNotIn("TOML004", _codes(result))

    # --- TOML005 trailing_spaces ------------------------------------------

    def test_trailing_spaces_first_line_and_count(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = 1  \nb = 2\nc = 3\t\n")
        finding = _finding(result, "TOML005")
        self.assertEqual((finding["line"], finding["col"]), (1, 6))
        self.assertIn("2 line(s)", finding["message"])
        self.assertIn("first at line 1", finding["message"])

    def test_multiline_string_trailing_whitespace_preserved(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text='a = """\nkeep   \n"""\nb = 1\n')
        self.assertNotIn("TOML005", _codes(result))

    def test_comment_text_is_masked_not_trailing(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = 1  # comment with tail\n")
        self.assertNotIn("TOML005", _codes(result))

    def test_blank_line_counts(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="a = 1\n   \n")
        finding = _finding(result, "TOML005")
        self.assertEqual((finding["line"], finding["col"]), (2, 1))

    # --- TOML006 mixed_indent_styles --------------------------------------

    def test_tab_space_mix_fires_on_clash_line(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[t]\n\ta = 1\n  b = 2\n")
        finding = _finding(result, "TOML006")
        self.assertEqual(finding["line"], 3)
        self.assertIn("1 tab-led", finding["message"])
        self.assertIn("1 space-led", finding["message"])

    def test_single_style_does_not_fire(self) -> None:
        for text in ("[t]\n\ta = 1\n\tb = 2\n", "[t]\n  a = 1\n  b = 2\n"):
            result = self.tool.execute(mode="lint", toml_text=text)
            self.assertNotIn("TOML006", _codes(result), text)

    def test_tab_only_document_is_legal_and_clean(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text="[t]\n\ta = 1\n")
        self.assertEqual(_codes(result), [])

    def test_mixed_run_line_is_its_own_class(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[t]\n \ta = 1\n\t b = 2\n")
        # both lines are "mixed" runs — a single class, no clash
        self.assertNotIn("TOML006", _codes(result))

    def test_multiline_string_indent_ignored(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = \"\"\"\n\ttab line\n\"\"\"\n[t]\n  b = 1\n")
        self.assertNotIn("TOML006", _codes(result))

    # --- TOML007 number_underscores_style ---------------------------------

    def test_grouped_and_plain_long_mixed(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = 1_000\nb = 100000\n")
        finding = _finding(result, "TOML007")
        self.assertEqual((finding["line"], finding["col"]), (1, 5))
        self.assertIn("1 digit-grouped", finding["message"])
        self.assertIn("1 plain long", finding["message"])

    def test_all_grouped_or_all_plain_do_not_fire(self) -> None:
        for text in ("a = 1_000\nb = 20_000\n",
                     "a = 100000\nb = 200000\n",
                     "a = 1000\nb = 1_000\n"):  # plain < 5 digits
            result = self.tool.execute(mode="lint", toml_text=text)
            self.assertNotIn("TOML007", _codes(result), text)

    def test_numbers_inside_strings_and_comments_ignored(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text='a = "1_000 and 100000"\n# 2_000 300000\n')
        self.assertNotIn("TOML007", _codes(result))

    def test_hex_and_binary_grouping(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = 0xdead_beef\nb = 0xdeadbeef\n")
        self.assertIn("TOML007", _codes(result))

    def test_underscored_float_and_date_do_not_confuse(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a = 1979-05-27\nd = 1_000.500\n")
        self.assertNotIn("TOML007", _codes(result))

    # --- TOML008 empty_table ----------------------------------------------

    def test_empty_header_table_fires(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[t]\nk = 1\n[empty]\n")
        finding = _finding(result, "TOML008")
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual((finding["line"], finding["col"]), (3, 1))
        self.assertIn("[empty]", finding["message"])
        self.assertFalse(result["ok"])

    def test_populated_table_does_not_fire(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="[t]\nk = 1\n")
        self.assertNotIn("TOML008", _codes(result))

    def test_table_with_subtable_is_not_empty(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[t]\n[t.sub]\nk = 1\n")
        self.assertNotIn("TOML008", _codes(result))

    def test_inline_empty_table_value_not_flagged(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="x = {}\n")
        self.assertNotIn("TOML008", _codes(result))

    def test_empty_aot_entry_flagged_at_own_header(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[[x]]\na = 1\n[[x]]\n[[x]]\nb = 2\n")
        finding = _finding(result, "TOML008")
        self.assertEqual(finding["line"], 3)

    def test_comment_only_section_is_empty(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[t]\n# nothing here\n")
        self.assertIn("TOML008", _codes(result))

    # --- TOML009 deeply_nested --------------------------------------------

    def test_thirteen_levels_fire_with_default_threshold(self) -> None:
        deep = ".".join(f"k{i}" for i in range(13))
        result = self.tool.execute(mode="lint",
                                   toml_text=f"{deep} = 1\n")
        finding = _finding(result, "TOML009")
        self.assertIn(deep, finding["message"])
        self.assertIn("13 levels", finding["message"])
        self.assertEqual((finding["line"], finding["col"]), (1, 1))

    def test_twelve_levels_are_clean(self) -> None:
        deep = ".".join(f"k{i}" for i in range(12))
        result = self.tool.execute(mode="lint",
                                   toml_text=f"{deep} = 1\n")
        self.assertNotIn("TOML009", _codes(result))

    def test_nested_headers_count_too(self) -> None:
        text = "".join(f"[{'.'.join(f'h{i}' for i in range(n))}]\n"
                       for n in range(1, 13)) + "k = 1\n"
        result = self.tool.execute(mode="lint", toml_text=text)
        finding = _finding(result, "TOML009")
        self.assertIn("13 levels", finding["message"])

    def test_max_depth_option_raises_and_lowers_threshold(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="a.b.c = 1\n",
                                   max_depth=2)
        self.assertIn("TOML009", _codes(result))
        result = self.tool.execute(mode="lint", toml_text="a.b.c = 1\n",
                                   max_depth=3)
        self.assertNotIn("TOML009", _codes(result))

    # --- TOML010 table_style_mixed ----------------------------------------

    def test_dotted_and_header_styles_fire_at_dotted_key(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="a.b = 1\n[z]\nc = 2\n")
        finding = _finding(result, "TOML010")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertIn("1 dotted-key", finding["message"])
        self.assertIn("1 header-defined", finding["message"])

    def test_dotted_only_does_not_fire(self) -> None:
        result = self.tool.execute(mode="lint",
                                   toml_text="a.b = 1\nc.d = 2\n")
        self.assertNotIn("TOML010", _codes(result))

    def test_header_only_does_not_fire(self) -> None:
        result = self.tool.execute(
            mode="lint", toml_text="[a]\nb = 1\n[z]\nc = 2\n")
        self.assertNotIn("TOML010", _codes(result))

    def test_header_without_direct_keys_is_not_header_style(self) -> None:
        # [outer] has no direct keys — only the sub-table does
        result = self.tool.execute(
            mode="lint", toml_text="a.b = 1\n[outer]\n[outer.sub]\nc = 2\n")
        # [outer.sub] has direct key c -> header style present -> fires
        self.assertIn("TOML010", _codes(result))
        result = self.tool.execute(
            mode="lint", toml_text="a.b = 1\n[outer.sub.deep]\nc = 2\n")
        self.assertIn("TOML010", _codes(result))

    def test_hard_clash_is_a_syntax_error_instead(self) -> None:
        # Same table both ways: tomllib rejects — lands in TOML002.
        result = self.tool.execute(
            mode="lint", toml_text="a.b = 1\n[a]\nc = 2\n")
        self.assertIn("TOML002", _codes(result))
        self.assertNotIn("TOML010", _codes(result))

    def test_quoted_key_with_dot_still_defines_the_parent(self) -> None:
        # a."b.c" = 1 has two key segments — it defines table a just
        # like a dotted key, so the style rule counts it.
        result = self.tool.execute(
            mode="lint", toml_text='a."b.c" = 1\n[z]\nc = 2\n')
        self.assertIn("TOML010", _codes(result))


class TomlLintMaskingTest(unittest.TestCase):
    """Strings and comments never trigger raw-text rules."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    def test_literal_multiline_string_content_fully_masked(self) -> None:
        text = "a = '''\n[not a header]\nx = [1, 'mix']\n1_000 100000\n'''\n"
        result = self.tool.execute(mode="lint", toml_text=text)
        self.assertEqual(_codes(result), [])

    def test_escaped_quotes_do_not_break_masking(self) -> None:
        text = 'a = "he said \\"hi\\" [1, 2]"\nb = 2\n'
        result = self.tool.execute(mode="lint", toml_text=text)
        self.assertEqual(_codes(result), [])

    def test_comment_hash_inside_string_is_not_comment(self) -> None:
        text = 'a = "value # not comment"\nb = "#hash"\n'
        result = self.tool.execute(mode="lint", toml_text=text)
        self.assertTrue(result["valid"])
        self.assertEqual(_codes(result), [])

    def test_multiline_basic_with_escaped_triple_quote(self) -> None:
        text = 'a = """start \\""" end"""\nb = 1\n'
        result = self.tool.execute(mode="lint", toml_text=text)
        self.assertEqual(_codes(result), [])

    def test_array_of_strings_with_commas_and_hashes(self) -> None:
        text = 'a = ["x, y", "z # w", "#"]\n'
        result = self.tool.execute(mode="lint", toml_text=text)
        self.assertNotIn("TOML003", _codes(result))


class TomlLintProfileTest(unittest.TestCase):
    """Profile arithmetic verified by hand."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    PROFILE_DOC = (
        "title = \"demo\"\n"                       # string
        "version = 2\n"                            # integer
        "ratio = 0.5\n"                            # float
        "enabled = true\n"                         # boolean
        "released = 1979-05-27\n"                  # date
        "written = 1979-05-27T07:32:00Z\n"         # datetime
        "edited = 1979-05-27T07:32:00\n"           # datetime (naive)
        "at = 07:32:00\n"                          # time
        "tags = [\"a\", \"b\"]\n"                  # array<string>
        "mixed = [1, \"x\"]\n"                     # array<mixed>
        "empty = []\n"                             # array<empty>
        "inline = {a = 1}\n"                       # table + integer
        "[server]\n"
        "host = \"h\"\n"                           # string
        "port = 80\n"                              # integer
        "[server.auth]\n"
        "user = \"u\"\n"                           # string
        "[[items]]\n"
        "name = \"one\"\n"
        "[[items]]\n"
        "name = \"two\"\n"
        "flag = false\n"
    )

    def test_profile_ground_truth(self) -> None:
        result = self.tool.execute(mode="profile",
                                   toml_text=self.PROFILE_DOC)
        # tables: inline, server, server.auth, items[0], items[1] = 5
        self.assertEqual(result["tables"], 5)
        self.assertEqual(result["arrays_of_tables"], 1)
        # keys: root: title version ratio enabled released written
        #       edited at tags mixed empty = 11; inline.a = 1;
        #       server: host port = 2; server.auth: user = 1;
        #       items[0]: name = 1; items[1]: name flag = 2 -> 18
        self.assertEqual(result["keys"], 18)
        self.assertEqual(result["scalar_type_histogram"], {
            "integer": 3,          # version, inline.a, port
            "string": 5,           # title, host, user, items[*].name x2
            "float": 1,            # ratio
            "boolean": 2,          # enabled, items[1].flag
            "datetime": 2,         # written (aware), edited (naive)
            "date": 1,             # released
            "time": 1,             # at
            "array<string>": 1,    # tags
            "array<mixed>": 1,     # mixed
            "array<empty>": 1,     # empty
        })
        # deepest path: server.auth.user (3) vs items[1].name (2)
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(result["deepest_path"], "server.auth.user")

    def test_profile_empty_document(self) -> None:
        result = self.tool.execute(mode="profile", toml_text="# only\n")
        self.assertEqual(result["tables"], 0)
        self.assertEqual(result["arrays_of_tables"], 0)
        self.assertEqual(result["keys"], 0)
        self.assertEqual(result["scalar_type_histogram"], {})
        self.assertEqual(result["max_depth"], 0)
        self.assertIsNone(result["deepest_path"])

    def test_profile_bom_is_stripped(self) -> None:
        result = self.tool.execute(mode="profile",
                                   toml_text="﻿a = 1\n")
        self.assertEqual(result["keys"], 1)

    def test_profile_invalid_toml_raises(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(mode="profile", toml_text="a = True\n")
        self.assertIn("valid TOML", str(caught.exception))
        self.assertIn("Invalid value", str(caught.exception))

    def test_profile_is_deterministic(self) -> None:
        first = self.tool.execute(mode="profile",
                                  toml_text=self.PROFILE_DOC)
        second = self.tool.execute(mode="profile",
                                   toml_text=self.PROFILE_DOC)
        self.assertEqual(first, second)

    def test_profile_aot_depth_counts_entries(self) -> None:
        result = self.tool.execute(
            mode="profile",
            toml_text="[[a]]\n[[a]]\nb = 1\n")
        # two [[a]] entries -> 2 tables; b lives at a.b (depth 2)
        self.assertEqual(result["tables"], 2)
        self.assertEqual(result["keys"], 1)
        self.assertEqual(result["max_depth"], 2)
        self.assertEqual(result["deepest_path"], "a.b")


class TomlLintFixHintsTest(unittest.TestCase):
    """fix_hints: safe textual repairs, re-lint, idempotence."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    def test_bom_and_trailing_spaces_fixed(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", toml_text="﻿a = 1   \nb = 2\n")
        self.assertEqual(result["fixed_text"], "a = 1\nb = 2\n")
        self.assertEqual(result["applied"], [
            {"repair": "bom_strip", "count": 1},
            {"repair": "trailing_space_strip", "count": 1},
        ])
        self.assertEqual(_remaining_codes(result), [])

    def test_crlf_terminators_preserved(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", toml_text="a = 1  \r\nb = 2\r\n")
        self.assertEqual(result["fixed_text"], "a = 1\r\nb = 2\r\n")

    def test_multiline_string_whitespace_untouched(self) -> None:
        text = 'a = """\nkeep me   \n"""\nb = 1  \n'
        result = self.tool.execute(mode="fix_hints", toml_text=text)
        self.assertEqual(result["fixed_text"],
                         'a = """\nkeep me   \n"""\nb = 1\n')
        self.assertEqual(result["applied"],
                         [{"repair": "trailing_space_strip", "count": 1}])

    def test_idempotent(self) -> None:
        dirty = "﻿a = [1, \"x\"]   \nb = 1_0  \n"
        once = self.tool.execute(mode="fix_hints", toml_text=dirty)
        twice = self.tool.execute(mode="fix_hints",
                                  toml_text=once["fixed_text"])
        self.assertEqual(twice["fixed_text"], once["fixed_text"])
        self.assertEqual(twice["applied"], [])

    def test_remaining_keeps_structural_findings(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", toml_text="﻿a = [1, \"x\"]   \n[t]\n")
        self.assertEqual(_remaining_codes(result), ["TOML003", "TOML008"])

    def test_broken_document_fixed_textually_not_structurally(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", toml_text="[x\na = True   \n")
        self.assertEqual(result["fixed_text"], "[x\na = True\n")
        self.assertEqual(_remaining_codes(result), ["TOML002"])

    def test_clean_input_is_unchanged(self) -> None:
        text = "a = 1\n[t]\nb = 2\n"
        result = self.tool.execute(mode="fix_hints", toml_text=text)
        self.assertEqual(result["fixed_text"], text)
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["remaining_count"], 0)

    def test_comment_and_values_never_restructured(self) -> None:
        text = 'a = 1   # keep   \nb = "  spaced  "\n'
        result = self.tool.execute(mode="fix_hints", toml_text=text)
        self.assertEqual(result["fixed_text"],
                         'a = 1   # keep\nb = "  spaced  "\n')


class TomlLintErrorMatrixTest(unittest.TestCase):
    """Strict argument validation and per-mode option gating."""

    def setUp(self) -> None:
        self.tool = TomlLintTool()

    def test_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="repair", toml_text="a = 1\n")

    def test_toml_text_type_and_emptiness(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text=42)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text="")

    def test_oversized_input(self) -> None:
        limit = self.tool.max_input_chars
        self.assertEqual(limit, 1_048_576)
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(mode="lint", toml_text="a" * (limit + 1))
        self.assertIn("1,048,576", str(caught.exception))
        # exactly at the limit is accepted (and fails as TOML, not as
        # an argument error)
        result = self.tool.execute(mode="lint", toml_text="a" * limit)
        self.assertFalse(result["valid"])

    def test_mode_option_gating(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="profile", toml_text="a = 1\n",
                              rules={"TOML005": False})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix_hints", toml_text="a = 1\n",
                              max_depth=3)

    def test_rules_map_validation(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text="a = 1\n",
                              rules={"TOML999": False})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text="a = 1\n",
                              rules={"TOML005": "no"})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", toml_text="a = 1\n",
                              rules=["TOML005"])

    def test_rules_disable_single_rule(self) -> None:
        text = "a = [1, \"x\"]  \n"
        full = self.tool.execute(mode="lint", toml_text=text)
        self.assertEqual(set(_codes(full)), {"TOML003", "TOML005"})
        trimmed = self.tool.execute(mode="lint", toml_text=text,
                                    rules={"TOML005": False})
        self.assertEqual(_codes(trimmed), ["TOML003"])
        # disabling a rule keeps true-enabled semantics
        kept = self.tool.execute(mode="lint", toml_text=text,
                                 rules={"TOML003": True})
        self.assertEqual(set(_codes(kept)), {"TOML003", "TOML005"})

    def test_syntax_rule_disable_still_reports_valid_false(self) -> None:
        result = self.tool.execute(mode="lint", toml_text="a = True\n",
                                   rules={"TOML002": False})
        self.assertFalse(result["valid"])
        self.assertEqual(_codes(result), [])

    def test_max_depth_validation(self) -> None:
        for bad in (0, 129, -1, "3", 2.5, True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.tool.execute(mode="lint", toml_text="a = 1\n",
                                  max_depth=bad)
        # boundaries accepted
        for good in (1, 128):
            self.tool.execute(mode="lint", toml_text="a = 1\n",
                              max_depth=good)

    def test_all_modes_accept_any_valid_document(self) -> None:
        text = "[t]\na = 1\n"
        for mode in TomlLintTool.MODES:
            result = self.tool.execute(mode=mode, toml_text=text)
            self.assertEqual(result["mode"], mode)


if __name__ == "__main__":
    unittest.main()
