#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_yaml_lint_tool.py

"""Offline unit tests for YamlLintTool.

The tool is built on the standard library plus the framework's
existing PyYAML and never touches the filesystem or the network, so
this suite runs fully offline. Assertions are exact ground truths:
every lint rule is checked in its triggering shape and in a
non-triggering control shape; the syntax-error rule is verified
against PyYAML's own problem marks over a 30-document malformed
corpus, and the tab-indentation rule against the verified mapping
that PyYAML rejects every unprotected tab-indent line; duplicate-key
detection is cross-checked against plain yaml.safe_load (which keeps
the last value — the behaviour the rule defends against); anchors,
aliases, multi-document streams and CJK keys are covered; profile
arithmetic is verified by hand; fix_hints asserts the exact edit
list, the exact fixed text, a re-lint-clean round-trip, idempotence
and the parse-failure path; and the option error matrix includes
per-mode option gating.
"""

import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import YamlLintTool
from agentuniverse.agent.action.tool.common_tool.yaml_lint_tool import (
    YamlLintTool as DirectYamlLintTool,
)


def _codes(result: dict) -> list:
    return [finding["code"] for finding in result["findings"]]


def _findings(result: dict, code: str) -> list:
    return [f for f in result["findings"] if f["code"] == code]


def _finding(result: dict, code: str) -> dict:
    matches = _findings(result, code)
    assert matches, f"{code} not in {_codes(result)}"
    return matches[0]


def _clean(text: str) -> str:
    """The canonical control document — no rule fires."""
    result = YamlLintTool().execute(mode="lint", yaml_text=text)
    assert result["finding_count"] == 0, result["findings"]
    return text


class YamlLintToolBasicsTest(unittest.TestCase):
    """Export surface, determinism, ok semantics, sorting, caps."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(YamlLintTool, DirectYamlLintTool)

    def test_name_modes_and_rule_codes(self) -> None:
        self.assertEqual(self.tool.name, "yaml_lint_tool")
        self.assertEqual(
            YamlLintTool.MODES, ("lint", "profile", "fix_hints")
        )
        self.assertEqual(len(YamlLintTool.RULE_CODES), 13)

    def test_control_document_is_clean(self) -> None:
        result = self.tool.execute(
            mode="lint",
            yaml_text="name: agent\nparams:\n  model: gpt\n  temp: 0.2\n"
                      "tags:\n  - a\n  - b\nenabled: true\n",
        )
        self.assertEqual(result["finding_count"], 0)
        self.assertTrue(result["ok"])
        self.assertTrue(result["parsed"])
        self.assertEqual(result["document_count"], 1)

    def test_deterministic_repeat(self) -> None:
        text = "a: 1\na: 2\nb: yes\n"
        first = self.tool.execute(mode="lint", yaml_text=text)
        second = self.tool.execute(mode="lint", yaml_text=text)
        self.assertEqual(first, second)

    def test_info_only_is_ok(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: yes\n")
        self.assertEqual(_codes(result), ["YML007"])
        self.assertTrue(result["ok"])

    def test_warning_breaks_ok(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a:\n")
        self.assertFalse(result["ok"])
        self.assertIn("YML008", _codes(result))

    def test_findings_sorted_by_line_col_code(self) -> None:
        text = "a: 1\nb: 2\na: 3\nc:\nd: 010\n"
        result = self.tool.execute(mode="lint", yaml_text=text)
        keys = [(f["line"], f["col"], f["code"]) for f in result["findings"]]
        self.assertEqual(keys, sorted(keys))

    def test_findings_cap_and_truncation_flag(self) -> None:
        text = "".join(f"key{i}: {i}   \n" for i in range(250))
        result = self.tool.execute(mode="lint", yaml_text=text)
        self.assertEqual(result["finding_count"], 250)
        self.assertEqual(len(result["findings"]), 200)
        self.assertTrue(result["findings_truncated"])

    def test_empty_string_is_a_contentless_document(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="")
        self.assertEqual(_codes(result), ["YML012"])
        self.assertFalse(result["ok"])
        self.assertEqual(_finding(result, "YML012")["line"], 1)


class YamlLintToolSyntaxMatrixTest(unittest.TestCase):
    """YML001 line/col against PyYAML's own marks, 30 documents.

    The expected positions were derived from PyYAML 6.x problem and
    context marks; the tab entries double as the verification that
    every un-protected tab-indent line is a real parse failure.
    """

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    CORPUS: tuple = (
        # (text, expected YML001 line, expected col) — None col means
        # only the line is asserted.
        ("\tkey: v\n", 1, 1),                                  # 1
        ("a:\n\tb: c\n", 2, 1),                                # 2
        ("a:\n  \tb: c\n", 2, 3),                              # 3
        ("a:\n- \tb\n", 2, 3),                                 # 4
        ("key:\tvalue\n", 1, 5),                               # 5
        ("data: |\n\ttabbed\n", 2, 1),                         # 6
        ("a: b: c\n", 1, 5),                                   # 7
        ('a: "unclosed\n', 2, 1),                              # 8
        ("a: 'unclosed\n", 2, 1),                              # 9
        ("a: [1, 2\n", 2, 1),                                  # 10
        ("a: {b: 1\n", 2, 1),                                  # 11
        ("a: ]\n", 1, 4),                                      # 12
        ("a: }\n", 1, 4),                                      # 13
        ("*undefined\n", 1, 1),                                # 14
        ("a: *missing\n", 1, 4),                               # 15
        ("- a\nb: 1\n", 2, 1),                                 # 16
        ("a:\n b: 1\n  c: 2\n", 3, 4),                         # 17
        ("a: 1\n b: 2\n", 2, 3),                               # 18
        ("@invalid\n", 1, 1),                                  # 19
        ("`backtick\n", 1, 1),                                 # 20
        ("a: !!\n", 1, 6),                                     # 21
        ("a: - b\n", 1, 4),                                    # 22
        ("a: |\n  b\n c\n", 3, 2),                             # 23
        ("? a\n: b\n: c\n", 3, 1),                             # 24
        ("a:\n- b\n\t- c\n", 3, 1),                            # 25
        ("{\n", 2, 1),                                         # 26
        ("[\n", 2, 1),                                         # 27
        ("a: >-\n b\n\tc\n", 3, 1),                            # 28
        ("---\na: 1\n---\tb: 2\n", 3, 4),                      # 29
        ("a: 'x\ny: 1", 2, 5),                                 # 30
    )

    def test_corpus_size(self) -> None:
        self.assertEqual(len(self.CORPUS), 30)

    def test_syntax_finding_matches_expected_marks(self) -> None:
        for text, line, col in self.CORPUS:
            with self.subTest(text=text):
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertIn(
                    "YML001", _codes(result),
                    f"expected a syntax error for {text!r}",
                )
                finding = _finding(result, "YML001")
                self.assertEqual(
                    finding["line"], line,
                    f"{text!r}: expected line {line}, got "
                    f"{finding['line']} ({finding['message']})",
                )
                if col is not None:
                    self.assertEqual(finding["col"], col, text)

    def test_marks_match_pyyaml_problem_marks(self) -> None:
        """The finding position equals PyYAML's own problem mark."""
        for text, _line, _col in self.CORPUS:
            with self.subTest(text=text):
                try:
                    list(yaml.compose_all(text, Loader=yaml.SafeLoader))
                    self.fail(f"{text!r} unexpectedly parsed")
                except (yaml.YAMLError, RecursionError) as error:
                    if isinstance(error, RecursionError):
                        continue
                    mark = error.problem_mark or error.context_mark
                    result = self.tool.execute(
                        mode="lint", yaml_text=text
                    )
                    finding = _finding(result, "YML001")
                    self.assertEqual(finding["line"], mark.line + 1)
                    self.assertEqual(finding["col"], mark.column + 1)

    def test_syntax_error_skips_structural_rules(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: 1\na: 2\n\tbad\n"
        )
        self.assertFalse(result["parsed"])
        self.assertIsNone(result["document_count"])
        # Raw-line rules still run; value-level rules do not.
        self.assertIn("YML001", _codes(result))
        self.assertIn("YML003", _codes(result))
        self.assertNotIn("YML005", _codes(result))
        self.assertNotIn("YML008", _codes(result))

    def test_recursion_depth_is_a_finding_not_a_crash(self) -> None:
        text = "[" * 3000 + "]" * 3000
        result = self.tool.execute(mode="lint", yaml_text=text)
        self.assertFalse(result["parsed"])
        self.assertIn("YML001", _codes(result))
        self.assertIn("recursion", _finding(result, "YML001")["message"])

    def test_unhashable_key_is_a_finding(self) -> None:
        # Compose succeeds; only the construct pass fails.
        result = self.tool.execute(mode="lint", yaml_text="[1, 2]: x\n")
        self.assertTrue(result["parsed"])
        self.assertIn("YML001", _codes(result))
        self.assertIn("unhashable", _finding(result, "YML001")["message"])

    def test_syntax_message_carries_context(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text='a: "abc\n')
        message = _finding(result, "YML001")["message"]
        self.assertIn("quoted scalar", message)
        self.assertIn("ScannerError", message)

    def test_parser_mark_preferred_over_late_scanner_mark(self) -> None:
        # A stray closing bracket survives the scanner and only breaks
        # it later, on whatever follows; the compose pass reports the
        # real mistake — the bracket itself — like safe_load does.
        text = "root:\n  s:\n    - [[1, 2]]]\n    - {a: 1}\n"
        with self.assertRaises(yaml.YAMLError) as raised:
            yaml.safe_load(text)
        mark = (raised.exception.problem_mark
                or raised.exception.context_mark)
        result = self.tool.execute(mode="lint", yaml_text=text)
        finding = _finding(result, "YML001")
        self.assertEqual(finding["line"], mark.line + 1)
        self.assertEqual(finding["col"], mark.column + 1)
        self.assertEqual(finding["line"], 3)

    def test_earlier_construct_error_beats_later_parse_error(self) -> None:
        # safe_load constructs document by document, so the unknown
        # tag in document 1 surfaces before the mapping-value error in
        # document 2; the reported mark must match safe_load's.
        text = "!--\na: 1\n---\n\n: 2\n"
        with self.assertRaises(yaml.YAMLError) as raised:
            list(yaml.safe_load_all(text))
        mark = (raised.exception.problem_mark
                or raised.exception.context_mark)
        result = self.tool.execute(mode="lint", yaml_text=text)
        finding = _finding(result, "YML001")
        self.assertEqual((finding["line"], finding["col"]),
                         (mark.line + 1, mark.column + 1))
        self.assertEqual(finding["line"], 1)


class YamlLintToolRawRulesTest(unittest.TestCase):
    """YML002 / YML003 / YML004 with block-scalar protection."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_bom_reported_at_line_1(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="\ufeffa: 1\n"
        )
        finding = _finding(result, "YML002")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertTrue(result["ok"])  # info only

    def test_tab_indentation_flagged_with_first_tab_column(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a:\n  \tb: 1\n")
        finding = _finding(result, "YML003")
        self.assertEqual((finding["line"], finding["col"]), (2, 3))
        self.assertEqual(finding["severity"], "error")

    def test_tab_indentation_always_pairs_with_parse_failure(self) -> None:
        for text in ("\tkey: v\n", "a:\n\tb: 1\n", "a:\n  \tb: 1\n"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertIn("YML003", _codes(result))
                self.assertIn("YML001", _codes(result))
                self.assertFalse(result["parsed"])

    def test_tab_after_block_indent_is_content_not_indentation(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="data: |\n  \tstuff\n"
        )
        self.assertNotIn("YML003", _codes(result))
        self.assertNotIn("YML004", _codes(result))
        self.assertTrue(result["parsed"])

    def test_tab_on_quoted_continuation_line_is_legal(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text='a: "p\n\tq"\n'
        )
        self.assertNotIn("YML003", _codes(result))
        self.assertTrue(result["parsed"])

    def test_trailing_spaces_reported_at_first_space(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: 1  \nb: 2\n")
        finding = _finding(result, "YML004")
        self.assertEqual((finding["line"], finding["col"]), (1, 5))

    def test_trailing_tabs_count_as_trailing_whitespace(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: 1\t\n")
        finding = _finding(result, "YML004")
        self.assertEqual((finding["line"], finding["col"]), (1, 5))

    def test_whitespace_only_line_is_trailing_not_tab_indent(self) -> None:
        # A tab-only line is a parse failure for PyYAML (YML001) and
        # trailing whitespace (YML004) — but never tab indentation.
        result = self.tool.execute(mode="lint", yaml_text="a: 1\n\t\n")
        self.assertEqual(set(_codes(result)), {"YML001", "YML004"})
        self.assertNotIn("YML003", _codes(result))
        self.assertEqual(_finding(result, "YML004")["line"], 2)

    def test_trailing_spaces_inside_block_scalar_protected(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="data: |\n  line with trailing   \n"
        )
        self.assertNotIn("YML004", _codes(result))

    def test_trailing_spaces_inside_quoted_multiline_are_folded(self) -> None:
        # Quoted scalars fold trailing whitespace at line breaks, so
        # flagging it is correct (documented behaviour).
        result = self.tool.execute(
            mode="lint", yaml_text='a: "x   \n  y"\n'
        )
        self.assertEqual(_codes(result), ["YML004"])
        self.assertEqual(_finding(result, "YML004")["line"], 1)

    def test_crlf_lines_tolerated(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: 1\r\nb: 2\r\n")
        self.assertEqual(result["finding_count"], 0)

    def test_scanned_regions_still_protected_after_later_error(self) -> None:
        # The scanner reads the block scalar (recording its range)
        # before it dies on the unterminated quote; the legal tab and
        # trailing spaces inside the block content must not become
        # findings just because the stream is broken further down.
        result = self.tool.execute(
            mode="lint",
            yaml_text='b: |\n  \tx   \nlater: "unterminated\n',
        )
        self.assertFalse(result["parsed"])
        self.assertIn("YML001", _codes(result))
        self.assertNotIn("YML003", _codes(result))
        self.assertNotIn("YML004", _codes(result))


class YamlLintToolDuplicateKeysTest(unittest.TestCase):
    """YML005 via the duplicate-key-safe loader subclass."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_basic_duplicate_at_second_occurrence(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: 1\nb: 2\na: 3\n"
        )
        finding = _finding(result, "YML005")
        self.assertEqual((finding["line"], finding["col"]), (3, 1))
        self.assertEqual(finding["severity"], "error")
        self.assertIn("first defined at line 1", finding["message"])

    def test_pyyaml_silently_keeps_the_last_value(self) -> None:
        # The behaviour the rule defends against, pinned down.
        self.assertEqual(
            yaml.safe_load("a: 1\nb: 2\na: 3\n"), {"a": 3, "b": 2}
        )

    def test_three_occurrences_two_findings(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: 1\na: 2\na: 3\n"
        )
        lines = [f["line"] for f in _findings(result, "YML005")]
        self.assertEqual(lines, [2, 3])

    def test_quoted_and_plain_strings_are_equal_keys(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: 1\n'a': 2\n"
        )
        self.assertIn("YML005", _codes(result))

    def test_boolean_key_case_variants_are_equal(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="true: 1\nTrue: 2\n"
        )
        self.assertIn("YML005", _codes(result))

    def test_int_key_spellings_are_equal(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="0x10: a\n16: b\n"
        )
        self.assertIn("YML005", _codes(result))

    def test_int_vs_float_equality_is_a_documented_edge(self) -> None:
        # python dicts equate 1 and 1.0 and keep the last value, so
        # the numeric bucket compares them by constructed value and
        # the duplicate fires.
        result = self.tool.execute(
            mode="lint", yaml_text="1: a\n1.0: b\n"
        )
        self.assertIn("YML005", _codes(result))

    def test_bool_word_keys_collide_with_true_false(self) -> None:
        # on / yes and true all construct to True, so the dict PyYAML
        # builds keeps one key — the rule must see the collision.
        for text in ("on: 1\ntrue: 2\n", "yes: 1\nTrue: 2\n",
                     "off: 1\nFalse: 2\n"):
            with self.subTest(text=text):
                self.assertEqual(
                    yaml.safe_load(text),
                    {True: 2} if "true" in text.lower() else {False: 2},
                )
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertIn("YML005", _codes(result))

    def test_bool_keys_collide_with_equal_ints(self) -> None:
        # hash(True) == hash(1): the built dict collapses them.
        for text in ("1: a\ntrue: b\n", "0: a\nfalse: b\n",
                     "1: a\non: b\n"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertIn("YML005", _codes(result))

    def test_quoted_number_never_collides_with_numeric(self) -> None:
        # '1' constructs to the string "1" — a different dict key.
        result = self.tool.execute(
            mode="lint", yaml_text="1: a\n'1': b\n"
        )
        self.assertNotIn("YML005", _codes(result))

    def test_nan_keys_never_collide(self) -> None:
        # Each .nan constructs a distinct float; NaN != NaN, so even
        # the built dict holds two keys.
        result = self.tool.execute(
            mode="lint", yaml_text="a: {.nan: x, .NaN: y}\n"
        )
        self.assertNotIn("YML005", _codes(result))

    def test_single_letter_y_n_are_string_keys(self) -> None:
        # PyYAML 6 does not resolve y / n to booleans.
        result = self.tool.execute(mode="lint", yaml_text="y: 1\nn: 2\n")
        self.assertNotIn("YML005", _codes(result))
        self.assertEqual(
            yaml.safe_load("y: 1\nn: 2\n"), {"y": 1, "n": 2}
        )

    def test_merge_keys_are_exempt(self) -> None:
        result = self.tool.execute(
            mode="lint",
            yaml_text="defaults: &d\n  x: 1\n<<: *d\n<<: *d\n",
        )
        self.assertNotIn("YML005", _codes(result))

    def test_duplicates_in_nested_mappings(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="outer:\n  k: 1\n  k: 2\n"
        )
        finding = _finding(result, "YML005")
        self.assertEqual((finding["line"], finding["col"]), (3, 3))

    def test_duplicates_across_documents_not_conflated(self) -> None:
        result = self.tool.execute(
            mode="lint",
            yaml_text="a: 1\n---\na: 2\n",
            allow_multiple_documents=True,
        )
        self.assertNotIn("YML005", _codes(result))

    def test_anchored_mapping_reported_once(self) -> None:
        # The anchor site defines the mapping once; alias uses share
        # the object, so the duplicate fires at its single source.
        result = self.tool.execute(
            mode="lint",
            yaml_text="tpl: &t\n  k: 1\n  k: 2\nuse1: *t\nuse2: *t\n",
        )
        duplicates = _findings(result, "YML005")
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["line"], 3)

    def test_billion_laughs_is_safe_and_fast(self) -> None:
        text = (
            "a: &a [lol, lol, lol, lol, lol, lol, lol, lol, lol]\n"
            "b: &b [*a, *a, *a, *a, *a, *a, *a, *a, *a]\n"
            "c: &c [*b, *b, *b, *b, *b, *b, *b, *b, *b]\n"
            "d: [*c, *c, *c, *c, *c, *c, *c, *c, *c]\n"
        )
        result = self.tool.execute(mode="lint", yaml_text=text)
        self.assertTrue(result["parsed"])
        self.assertEqual(result["finding_count"], 0)


class YamlLintToolScalarRulesTest(unittest.TestCase):
    """YML006 / YML007 / YML008 / YML010 / YML011."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_implicit_octal_flagged_with_parsed_value(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: 010\n")
        finding = _finding(result, "YML006")
        self.assertEqual((finding["line"], finding["col"]), (1, 4))
        self.assertIn("base-8 to 8", finding["message"])
        self.assertTrue(result["ok"])  # info

    def test_octal_variants(self) -> None:
        for text, note in (
            ("a: 00\n", "double zero"),
            ("a: 0_1\n", "underscore octal"),
            ("a: +010\n", "signed"),
        ):
            with self.subTest(note=note):
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertIn("YML006", _codes(result))

    def test_octal_controls_not_flagged(self) -> None:
        for text, note in (
            ("a: 0\n", "bare zero"),
            ("a: 0o10\n", "yaml 1.2 octal stays a string"),
            ("a: 0x10\n", "hex is explicit"),
            ("a: '010'\n", "quoted"),
            ("a: 08\n", "8 is not an octal digit"),
            ("a: 10\n", "plain decimal"),
        ):
            with self.subTest(note=note):
                result = self.tool.execute(mode="lint", yaml_text=text)
                self.assertNotIn("YML006", _codes(result))

    def test_bool_words_flagged_with_suggestion(self) -> None:
        for word in ("yes", "Yes", "YES", "no", "No", "on", "On", "off"):
            with self.subTest(word=word):
                result = self.tool.execute(
                    mode="lint", yaml_text=f"a: {word}\n"
                )
                finding = _finding(result, "YML007")
                self.assertEqual(finding["severity"], "info")
                self.assertIn("quote it", finding["hint"])

    def test_true_false_never_flagged(self) -> None:
        for word in ("true", "True", "false", "FALSE"):
            with self.subTest(word=word):
                result = self.tool.execute(
                    mode="lint", yaml_text=f"a: {word}\n"
                )
                self.assertEqual(result["finding_count"], 0)

    def test_quoted_bool_words_not_flagged(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a: 'yes'\n")
        self.assertEqual(result["finding_count"], 0)

    def test_bool_word_in_flow_and_list(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: [yes, no]\nb:\n  - on\n"
        )
        positions = {(f["line"], f["col"]) for f in
                     _findings(result, "YML007")}
        self.assertEqual(
            positions, {(1, 5), (1, 10), (3, 5)}
        )

    def test_bool_word_as_key_also_flagged_as_scalar(self) -> None:
        # 'on:' is an implicit bool key: YML010 fires on the key and
        # YML007 fires on the key scalar.
        result = self.tool.execute(mode="lint", yaml_text="on: 1\n")
        self.assertIn("YML010", _codes(result))
        self.assertIn("YML007", _codes(result))

    def test_empty_value_key_flagged(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="a:\nb: 1\n")
        finding = _finding(result, "YML008")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertEqual(finding["severity"], "warning")

    def test_explicit_nulls_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: null\nb: ~\nc:\n  d:\n"
        )
        # Only the trailing "d:" is implicit.
        self.assertEqual(
            [f["line"] for f in _findings(result, "YML008")], [4]
        )

    def test_flow_empty_value_flagged(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="{a: , b: 1}\n")
        self.assertIn("YML008", _codes(result))

    def test_non_string_keys_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="1: a\n1.5: b\nnull: c\n?\n  - x\n: d\n"
        )
        lines = [f["line"] for f in _findings(result, "YML010")]
        self.assertEqual(lines, [1, 2, 3, 5])

    def test_string_keys_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="'1': a\ns: b\n"
        )
        self.assertNotIn("YML010", _codes(result))

    def test_multiline_plain_scalar_flagged_with_span(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: one\n  two\nb: 2\n"
        )
        finding = _finding(result, "YML011")
        self.assertEqual((finding["line"], finding["col"]), (1, 4))
        self.assertIn("spans 2 lines", finding["message"])

    def test_block_and_quoted_scalars_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint",
            yaml_text="a: |\n  one\n  two\nb: \"x\"\nc:\n  - plain\n",
        )
        self.assertNotIn("YML011", _codes(result))

    def test_multiline_plain_scalar_folds(self) -> None:
        # The underlying parser behaviour, pinned down.
        self.assertEqual(yaml.safe_load("a: one\n  two\n"), {"a": "one two"})


class YamlLintToolStructureRulesTest(unittest.TestCase):
    """YML009 / YML012 / YML013."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    @staticmethod
    def _nested(depth: int) -> str:
        """A mapping nested ``depth`` collections deep, one per line."""
        lines = [
            "  " * level + f"k{level}:" for level in range(depth - 1)
        ]
        lines.append("  " * (depth - 1) + f"k{depth - 1}: 1")
        return "\n".join(lines) + "\n"

    def test_depth_twelve_is_clean(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text=self._nested(12)
        )
        self.assertEqual(result["finding_count"], 0)

    def test_depth_thirteen_flagged_once_with_depth_and_path(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text=self._nested(13)
        )
        findings = _findings(result, "YML009")
        self.assertEqual(len(findings), 1)
        self.assertIn("depth 13", findings[0]["message"])
        self.assertIn("k0.k1.k2", findings[0]["message"])
        self.assertEqual(findings[0]["line"], 13)

    def test_lists_nest_too(self) -> None:
        text = "a:\n" + "".join(
            f"{'  ' * (i + 1)}-\n" for i in range(13)
        )
        result = self.tool.execute(mode="lint", yaml_text=text)
        self.assertIn("YML009", _codes(result))

    def test_deep_nesting_reported_once_per_document(self) -> None:
        # Two documents that each exceed the limit get one finding
        # each, at their own first offending collection.
        doc = "a:\n" + "".join(
            f"{'  ' * (i + 1)}n{i}:\n" for i in range(13)
        )
        result = self.tool.execute(
            mode="lint", yaml_text=doc + "---\n" + doc,
            allow_multiple_documents=True,
        )
        findings = _findings(result, "YML009")
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0]["line"], 13)
        self.assertEqual(findings[1]["line"], 28)

    def test_max_depth_option_tightens_and_validates(self) -> None:
        text = self._nested(5)
        tight = self.tool.execute(
            mode="lint", yaml_text=text, max_depth=3
        )
        self.assertIn("YML009", _codes(tight))
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text=text, max_depth=0)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text=text, max_depth=129)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text=text, max_depth="12")

    def test_comment_only_stream_is_contentless(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="# only a comment\n\n"
        )
        finding = _finding(result, "YML012")
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertEqual(result["document_count"], 0)

    def test_explicit_empty_documents_at_their_markers(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="---\n---\n"
        )
        lines = [f["line"] for f in _findings(result, "YML012")]
        self.assertEqual(lines, [1, 2])

    def test_trailing_empty_document_after_content(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="x: 1\n---\n"
        )
        empties = [f for f in _findings(result, "YML012")]
        self.assertEqual(len(empties), 1)
        self.assertEqual(empties[0]["line"], 2)

    def test_explicit_null_document_is_content(self) -> None:
        result = self.tool.execute(mode="lint", yaml_text="--- null\n")
        self.assertNotIn("YML012", _codes(result))

    def test_multiple_documents_flagged_at_second_marker(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: 1\n---\nb: 2\n---\nc: 3\n"
        )
        findings = _findings(result, "YML013")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["line"], 2)
        self.assertIn("3 documents", findings[0]["message"])
        self.assertEqual(result["document_count"], 3)
        self.assertTrue(result["ok"])  # info only

    def test_allow_multiple_documents_suppresses(self) -> None:
        result = self.tool.execute(
            mode="lint",
            yaml_text="a: 1\n---\nb: 2\n",
            allow_multiple_documents=True,
        )
        self.assertNotIn("YML013", _codes(result))
        self.assertEqual(result["document_count"], 2)

    def test_marker_with_inline_content(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="--- a\n--- b\n"
        )
        finding = _finding(result, "YML013")
        self.assertEqual(finding["line"], 2)


class YamlLintToolRulesOptionTest(unittest.TestCase):
    """The per-rule disable map."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()
        self.text = "a: 1   \na: 2\n"

    def test_disable_single_rule(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text=self.text, rules={"YML004": False}
        )
        self.assertNotIn("YML004", _codes(result))
        self.assertIn("YML005", _codes(result))

    def test_disable_syntax_rule_still_reports_others(self) -> None:
        result = self.tool.execute(
            mode="lint", yaml_text="a: [\n", rules={"YML001": False}
        )
        self.assertEqual(result["finding_count"], 0)

    def test_unknown_code_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", yaml_text="a: 1\n", rules={"YML999": False}
            )

    def test_non_boolean_value_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", yaml_text="a: 1\n", rules={"YML004": "no"}
            )

    def test_non_dict_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", yaml_text="a: 1\n", rules=["YML004"]
            )


class YamlLintToolProfileTest(unittest.TestCase):
    """Profile topology statistics, verified by hand."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    PROFILE_TEXT: str = (
        "name: demo\n"                # flat key
        "max_tokens: 10\n"            # snake
        "retry-count: 2\n"            # kebab
        "useCaching: true\n"          # camel -> mixed naming
        "limits:\n"
        "  min: 0.5\n"
        "  labels:\n"
        "    - alpha\n"
        "    - beta\n"
        "    - gamma\n"
        "template: &tpl\n"
        "  id: 7\n"
        "derived: *tpl\n"
        "stamp: 2026-10-21\n"
        "missing:\n"
    )

    def test_profile_arithmetic(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text=self.PROFILE_TEXT
        )
        # Documents and collections: root, limits, template (the
        # derived alias shares the template object).
        self.assertEqual(result["document_count"], 1)
        self.assertEqual(result["mapping_count"], 3)
        # Keys: 9 root + min/labels + id.
        self.assertEqual(result["key_count"], 12)
        # Depth: root=1, limits=2, labels list=3.
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(result["deepest_path"], "limits.labels")
        # Lists.
        self.assertEqual(result["list_count"], 1)
        self.assertEqual(result["list_item_count"], 3)
        self.assertEqual(
            result["longest_list"], {"length": 3, "path": "limits.labels"}
        )
        # Scalars: 12 keys + values (demo, 10, 2, true, 0.5, 7,
        # 2026-10-21, empty) + 3 list items = 23.
        self.assertEqual(result["scalar_count"], 23)
        self.assertEqual(
            result["scalar_types"],
            # str: 12 keys + demo + alpha/beta/gamma = 16
            {"str": 16, "int": 3, "float": 1, "bool": 1, "null": 1,
             "timestamp": 1, "other": 0},
        )

    def test_profile_anchors_and_aliases(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text=self.PROFILE_TEXT
        )
        self.assertEqual(
            result["anchors"],
            {"definitions": 1, "uses": 1, "names": ["tpl"],
             "recursive": False},
        )

    def test_profile_recursive_anchor_detected(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text="a: &x\n- *x\n"
        )
        self.assertTrue(result["anchors"]["recursive"])

    def test_profile_naming_styles(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text=self.PROFILE_TEXT
        )
        naming = result["naming"]
        self.assertEqual(
            naming["styles"],
            {"snake": 1, "kebab": 1, "camel": 1, "flat": 9, "other": 0},
        )
        self.assertTrue(naming["mixed"])
        self.assertEqual(
            result["notes"],
            ["key naming styles are mixed (snake=1, kebab=1, camel=1) "
             "— pick one convention"],
        )

    def test_profile_consistent_naming_has_no_note(self) -> None:
        result = self.tool.execute(
            mode="profile",
            yaml_text="first_key: 1\nsecond_key: 2\nplain: 3\n",
        )
        self.assertFalse(result["naming"]["mixed"])
        self.assertEqual(result["naming"]["dominant"], "snake")
        self.assertEqual(result["notes"], [])

    def test_profile_flat_keys_are_neutral(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text="name: a\nport: 1\n"
        )
        self.assertFalse(result["naming"]["mixed"])
        self.assertEqual(
            result["naming"]["styles"],
            {"snake": 0, "kebab": 0, "camel": 0, "flat": 2, "other": 0},
        )

    def test_profile_cjk_keys_classified_other(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text="名字: agent\nmax_tokens: 1\n"
        )
        self.assertEqual(result["naming"]["styles"]["other"], 1)
        self.assertEqual(result["naming"]["styles"]["snake"], 1)
        self.assertFalse(result["naming"]["mixed"])
        # The CJK key survives linting untouched.
        lint = self.tool.execute(
            mode="lint", yaml_text="名字: agent\n"
        )
        self.assertEqual(lint["finding_count"], 0)

    def test_profile_scalar_only_document(self) -> None:
        result = self.tool.execute(mode="profile", yaml_text="hello\n")
        self.assertEqual(result["max_depth"], 0)
        self.assertIsNone(result["deepest_path"])
        self.assertEqual(result["mapping_count"], 0)
        self.assertEqual(result["scalar_types"]["str"], 1)

    def test_profile_multi_document_counts_all(self) -> None:
        result = self.tool.execute(
            mode="profile", yaml_text="a: 1\n---\nb: 2\n"
        )
        self.assertEqual(result["document_count"], 2)
        self.assertEqual(result["key_count"], 2)

    def test_profile_unparseable_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="profile", yaml_text="a: [\n")

    def test_profile_scanner_error_also_raises_value_error(self) -> None:
        # Scanner failures surface as ValueError, never as a leaked
        # yaml.YAMLError.
        for text in ('a: "unclosed\n', "a: 'x\ny: 1", "\tkey: v\n"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="profile", yaml_text=text)

    def test_profile_longest_list_paths_and_cjk_key_paths(self) -> None:
        result = self.tool.execute(
            mode="profile",
            yaml_text="outer:\n  - 1\n  - 2\n  - inner:\n      - x\n",
        )
        self.assertEqual(
            result["longest_list"], {"length": 3, "path": "outer"}
        )
        self.assertEqual(result["max_depth"], 4)


class YamlLintToolFixHintsTest(unittest.TestCase):
    """fix_hints: exact edits, exact fixed text, round-trips."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_exact_edits_and_fixed_text(self) -> None:
        result = self.tool.execute(
            mode="fix_hints",
            yaml_text="\ufeffa: 1\nb: yes  \nc: on\n",
        )
        self.assertEqual(
            result["edits"],
            [
                {"action": "remove_bom", "line": 1, "col": 1,
                 "original": "\ufeff", "replacement": ""},
                {"action": "quote_bool_word", "line": 2, "col": 4,
                 "original": "yes", "replacement": "'yes'"},
                {"action": "strip_trailing_spaces", "line": 2, "col": 7,
                 "original": "  ", "replacement": ""},
                {"action": "quote_bool_word", "line": 3, "col": 4,
                 "original": "on", "replacement": "'on'"},
            ],
        )
        self.assertEqual(
            result["fixed_text"], "a: 1\nb: 'yes'\nc: 'on'\n"
        )
        self.assertEqual(
            result["applied"],
            [
                {"action": "remove_bom", "count": 1},
                {"action": "strip_trailing_spaces", "count": 1},
                {"action": "quote_bool_word", "count": 2},
            ],
        )
        self.assertFalse(result["parse_failed"])

    def test_re_lint_round_trip_is_clean(self) -> None:
        text = "\ufeffa: 1\nb: yes  \nc: on\nd: 010   \n"
        result = self.tool.execute(mode="fix_hints", yaml_text=text)
        self.assertEqual(result["remaining_count"], 1)
        remaining_codes = [f["code"] for f in result["remaining"]]
        # Only the octal info (a semantic choice) survives.
        self.assertEqual(remaining_codes, ["YML006"])
        relint = self.tool.execute(
            mode="lint", yaml_text=result["fixed_text"]
        )
        self.assertEqual(_codes(relint), ["YML006"])
        # Semantics preserved.
        self.assertEqual(
            yaml.safe_load(result["fixed_text"]),
            {"a": 1, "b": "yes", "c": "on", "d": 8},
        )

    def test_fix_hints_never_restructures(self) -> None:
        text = "a: 1\na: 2\nouter:\n  k: 1\n  k: 2\n"
        result = self.tool.execute(mode="fix_hints", yaml_text=text)
        self.assertEqual(result["edits"], [])
        self.assertEqual(result["fixed_text"], text)
        self.assertEqual(result["remaining_count"], 2)
        self.assertEqual(
            [f["code"] for f in result["remaining"]],
            ["YML005", "YML005"],
        )

    def test_fix_hints_idempotent(self) -> None:
        text = "\ufeffa: yes   \n"
        once = self.tool.execute(mode="fix_hints", yaml_text=text)
        twice = self.tool.execute(
            mode="fix_hints", yaml_text=once["fixed_text"]
        )
        self.assertEqual(twice["edits"], [])
        self.assertEqual(twice["fixed_text"], once["fixed_text"])

    def test_block_scalar_content_never_touched(self) -> None:
        text = "data: |\n  keep trailing   \n  \tand tabs\n"
        result = self.tool.execute(mode="fix_hints", yaml_text=text)
        self.assertEqual(result["edits"], [])
        self.assertEqual(result["fixed_text"], text)
        self.assertEqual(
            yaml.safe_load(result["fixed_text"])["data"],
            "keep trailing   \n\tand tabs\n",
        )

    def test_parse_failure_still_offers_textual_edits(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", yaml_text="a: 1   \n\tbad: [\n"
        )
        self.assertTrue(result["parse_failed"])
        actions = [edit["action"] for edit in result["edits"]]
        self.assertEqual(actions, ["strip_trailing_spaces"])
        self.assertNotIn("quote_bool_word", actions)
        self.assertEqual(result["fixed_text"], "a: 1\n\tbad: [\n")

    def test_option_toggles(self) -> None:
        text = "\ufeffa: yes \n"
        result = self.tool.execute(
            mode="fix_hints", yaml_text=text, remove_bom=False,
            strip_trailing_spaces=False,
        )
        self.assertEqual(
            result["edits"],
            [{"action": "quote_bool_word", "line": 1, "col": 4,
              "original": "yes", "replacement": "'yes'"}],
        )
        # BOM kept when remove_bom is disabled.
        self.assertTrue(result["fixed_text"].startswith("\ufeff"))
        result = self.tool.execute(
            mode="fix_hints", yaml_text=text, quote_bool_words=False
        )
        actions = [edit["action"] for edit in result["edits"]]
        self.assertEqual(
            actions, ["remove_bom", "strip_trailing_spaces"]
        )

    def test_crlf_preserved_by_edits(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", yaml_text="a: yes \r\nb: 2\r\n"
        )
        self.assertEqual(
            result["fixed_text"], "a: 'yes'\r\nb: 2\r\n"
        )


class YamlLintToolErrorMatrixTest(unittest.TestCase):
    """Strict validation and per-mode option gating."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_unknown_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="validate", yaml_text="a: 1\n")

    def test_missing_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(yaml_text="a: 1\n")

    def test_non_string_text_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text={"a": 1})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text=None)

    def test_oversized_text_rejected(self) -> None:
        text = "a: 1\n" + "#" * 1_000_000
        self.assertGreater(len(text), 1_000_000)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", yaml_text=text)

    def test_input_at_cap_accepted(self) -> None:
        text = "a: 1\n" + "#" * (1_000_000 - 5)
        self.assertEqual(len(text), 1_000_000)
        result = self.tool.execute(mode="lint", yaml_text=text)
        self.assertEqual(result["finding_count"], 0)

    def test_option_gating_per_mode(self) -> None:
        for mode, option in (
            ("profile", "rules"),
            ("profile", "max_depth"),
            ("profile", "allow_multiple_documents"),
            ("profile", "remove_bom"),
            ("fix_hints", "rules"),
            ("fix_hints", "max_depth"),
            ("fix_hints", "allow_multiple_documents"),
            ("lint", "remove_bom"),
            ("lint", "strip_trailing_spaces"),
            ("lint", "quote_bool_words"),
        ):
            with self.subTest(mode=mode, option=option):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode=mode, yaml_text="a: 1\n", **{option: True}
                    )

    def test_bool_options_must_be_bool(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", yaml_text="a: 1\n",
                allow_multiple_documents="yes",
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="fix_hints", yaml_text="a: 1\n", remove_bom=1
            )

    def test_max_depth_must_be_int(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", yaml_text="a: 1\n", max_depth=True
            )

    def test_profile_accepts_no_extra_options(self) -> None:
        result = self.tool.execute(mode="profile", yaml_text="a: 1\n")
        self.assertEqual(result["mode"], "profile")


class YamlLintToolIntegrationTest(unittest.TestCase):
    """Realistic agent-configuration documents."""

    def setUp(self) -> None:
        self.tool = YamlLintTool()

    def test_agent_config_with_classic_hazards(self) -> None:
        text = (
            "info:\n"
            "  name: demo\n"
            "  description: demo agent\n"
            "plan:\n"
            "  retry: yes\n"           # bool word
            "  seed: 010\n"            # octal look
            "  seed: 7\n"              # plain duplicate repeat
            "metadata:\n"
            "  on: true\n"             # bool KEY
            "input_keys:\n"
            "  - query\n"
        )
        result = self.tool.execute(mode="lint", yaml_text=text)
        codes = _codes(result)
        self.assertIn("YML005", codes)
        self.assertIn("YML006", codes)
        self.assertIn("YML007", codes)
        self.assertIn("YML010", codes)
        self.assertFalse(result["ok"])

    def test_yaml_round_trip_survives_fixes(self) -> None:
        text = "flag: on\nname: 'on'\n"
        result = self.tool.execute(mode="fix_hints", yaml_text=text)
        fixed = yaml.safe_load(result["fixed_text"])
        # The plain 'on' became an explicit string; the quoted one
        # stayed a string.
        self.assertEqual(fixed, {"flag": "on", "name": "on"})


if __name__ == "__main__":
    unittest.main()
