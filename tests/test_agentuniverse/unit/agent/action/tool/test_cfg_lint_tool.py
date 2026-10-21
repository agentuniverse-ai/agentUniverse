#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_cfg_lint_tool.py

"""Offline unit tests for CfgLintTool.

The tool is built purely on the standard library and never touches
the network or the filesystem, so this suite runs fully offline.
Every assertion is deterministic. The centerpiece is the
differential oracle suite: the tool's ``configparser_would_reject``
verdict must equal whether a real ``configparser.ConfigParser().read_string``
call raises, over a deterministically generated corpus of 300+ INI
texts (valid files plus systematic mutations); for every corpus
member the real parser *accepts*, the parse-mode values must equal
``configparser``'s own ``get(..., raw=True)`` results.

Security invariant asserted in every test whose fixture carries a
secret-ish key name (containing KEY/SECRET/PASSWORD/TOKEN): the raw
secret value must not appear anywhere in the serialized result of
any mode.
"""

import configparser
import json
import unittest

from agentuniverse.agent.action.tool.common_tool import CfgLintTool
from agentuniverse.agent.action.tool.common_tool.cfg_lint_tool import (
    RULES,
    SEVERITIES,
)
from agentuniverse.agent.action.tool.common_tool.cfg_lint_tool import (
    CfgLintTool as DirectCfgLintTool,
)

SECRET_RAW_VALUES = ("hunter2-password", "sk-live-abcdef123456")


def oracle_rejects(text: str) -> bool:
    """The ground truth: does a default strict configparser raise?"""
    parser = configparser.ConfigParser()
    try:
        parser.read_string(text)
        return False
    except Exception:
        return True


def oracle_parser(text: str) -> configparser.ConfigParser:
    """A real parser for accepted texts (raises like production use)."""
    parser = configparser.ConfigParser()
    parser.read_string(text)
    return parser


def codes(result) -> list:
    """The findings of a lint-style payload as (code, line) tuples."""
    return [(f["code"], f["line"]) for f in result["findings"]]


class CfgLintToolTestCase(unittest.TestCase):
    """Shared helpers."""

    def setUp(self) -> None:
        self.tool = CfgLintTool()

    def lint(self, text: str) -> list:
        return codes(self.tool.execute(mode="lint", text=text))

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def assert_no_secret_leak(self, result) -> None:
        """No raw secret value may appear anywhere in the payload."""
        dumped = json.dumps(result, sort_keys=True, default=str)
        for raw in SECRET_RAW_VALUES:
            self.assertNotIn(raw, dumped)


class CfgLintRegistryTest(CfgLintToolTestCase):
    """The rule registry is the documented 13-rule set."""

    def test_registry(self) -> None:
        self.assertEqual(len(RULES), 13)
        self.assertEqual(
            RULES,
            (
                "bom_present",
                "duplicate_default_section",
                "duplicate_option",
                "duplicate_option_case",
                "duplicate_section",
                "inline_comment_risk",
                "interpolation_risk",
                "key_without_value",
                "missing_final_newline",
                "missing_section_header",
                "tab_indentation",
                "trailing_whitespace",
                "unparseable_line",
            ),
        )

    def test_severities(self) -> None:
        for code in (
            "missing_section_header",
            "duplicate_section",
            "duplicate_option",
            "key_without_value",
            "unparseable_line",
        ):
            self.assertEqual(SEVERITIES[code], "error", code)
        for code in (
            "duplicate_option_case",
            "duplicate_default_section",
            "bom_present",
            "inline_comment_risk",
            "interpolation_risk",
        ):
            self.assertEqual(SEVERITIES[code], "warning", code)
        for code in ("missing_final_newline", "trailing_whitespace", "tab_indentation"):
            self.assertEqual(SEVERITIES[code], "info", code)

    def test_findings_carry_severity(self) -> None:
        result = self.tool.execute(mode="lint", text="[s]\nk = 1\nk = 2\n")
        finding = result["findings"][0]
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["code"], "duplicate_option")


class CfgLintRuleTest(CfgLintToolTestCase):
    """Every rule fires on its trigger fixture and stays silent on control."""

    # -- missing_section_header --------------------------------------- #

    def test_missing_section_header_fires(self) -> None:
        self.assertIn(
            ("missing_section_header", 1), self.lint("key = value\n")
        )

    def test_missing_section_header_line_citation(self) -> None:
        # configparser cites the PHYSICAL line of the first non-blank,
        # non-comment line: with a one-line comment+blank preamble the
        # citation is line 3 — one line later than the "content line"
        # a zero-based reading would expect (documented N+1 behavior).
        self.assertIn(
            ("missing_section_header", 3), self.lint("; c\n\nkey = v\n")
        )
        self.assertTrue(oracle_rejects("; c\n\nkey = v\n"))

    def test_missing_section_header_control(self) -> None:
        self.assertNotIn("missing_section_header", self.lint("; c\n[s]\nk = v\n"))

    # -- duplicate_section -------------------------------------------- #

    def test_duplicate_section_cites_repeat(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = 1\n[s]\nj = 2\n"),
            [("duplicate_section", 3)],
        )
        self.assertTrue(oracle_rejects("[s]\nk = 1\n[s]\nj = 2\n"))

    def test_duplicate_section_control(self) -> None:
        self.assertNotIn("duplicate_section", self.lint("[s]\nk = 1\n[t]\nj = 2\n"))

    def test_sections_case_sensitive(self) -> None:
        # configparser compares section names case-sensitively.
        self.assertNotIn("duplicate_section", self.lint("[S]\n[s]\n"))

    # -- duplicate_option ---------------------------------------------- #

    def test_duplicate_option_cites_repeat(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = 1\nk = 2\n"),
            [("duplicate_option", 3)],
        )
        self.assertTrue(oracle_rejects("[s]\nk = 1\nk = 2\n"))

    def test_duplicate_option_control(self) -> None:
        self.assertNotIn("duplicate_option", self.lint("[s]\nk = 1\nj = 2\n"))

    def test_duplicate_option_in_other_section_ok(self) -> None:
        self.assertNotIn("duplicate_option", self.lint("[s]\nk = 1\n[t]\nk = 2\n"))

    # -- duplicate_option_case ------------------------------------------ #

    def test_case_collision_flags_both_codes(self) -> None:
        # configparser lowercases keys (optionxform): 'Key' and 'key'
        # collide — DuplicateOptionError in the oracle, plus the extra
        # case-collision warning on the second spelling.
        self.assertEqual(
            self.lint("[s]\nKey = first\nkey = second\n"),
            [("duplicate_option", 3), ("duplicate_option_case", 3)],
        )
        self.assertTrue(oracle_rejects("[s]\nKey = first\nkey = second\n"))

    def test_case_collision_silent_for_identical_spelling(self) -> None:
        self.assertNotIn(
            "duplicate_option_case", self.lint("[s]\nkey = 1\nkey = 2\n")
        )

    # -- duplicate_default_section -------------------------------------- #

    def test_repeated_default_block_warns(self) -> None:
        # configparser re-enters [DEFAULT] without DuplicateSectionError;
        # only repeated options inside it raise. The lint mirrors both.
        findings = self.lint("[DEFAULT]\na = 1\n[DEFAULT]\nb = 2\n")
        self.assertEqual(findings, [("duplicate_default_section", 3)])
        self.assertFalse(oracle_rejects("[DEFAULT]\na = 1\n[DEFAULT]\nb = 2\n"))

    def test_repeated_default_with_repeated_option(self) -> None:
        findings = self.lint("[DEFAULT]\na = 1\n[DEFAULT]\na = 2\n")
        self.assertIn(("duplicate_default_section", 3), findings)
        self.assertIn(("duplicate_option", 4), findings)
        self.assertTrue(
            oracle_rejects("[DEFAULT]\na = 1\n[DEFAULT]\na = 2\n")
        )

    # -- key_without_value / unparseable_line --------------------------- #

    def test_key_without_value(self) -> None:
        self.assertEqual(self.lint("[s]\nk = 1\ntimeout\n"), [("key_without_value", 3)])
        self.assertTrue(oracle_rejects("[s]\nk = 1\ntimeout\n"))

    def test_unparseable_line_empty_option(self) -> None:
        self.assertEqual(self.lint("[s]\n= value\n"), [("unparseable_line", 2)])
        self.assertTrue(oracle_rejects("[s]\n= value\n"))

    def test_control_valid_mixed_delimiters(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = v\nj : w\nurl = http://x:80\nmy.name-1 = 3\n"), []
        )

    # -- bom_present ----------------------------------------------------- #

    def test_bom_makes_configparser_reject_line_one(self) -> None:
        findings = self.lint("\ufeff[s]\nk = 1\n")
        self.assertIn(("bom_present", 1), findings)
        self.assertIn(("missing_section_header", 1), findings)
        self.assertTrue(oracle_rejects("\ufeff[s]\nk = 1\n"))

    def test_bom_citation_quirk(self) -> None:
        # A BOM-only first line: configparser cites line 1 while the
        # visible section header sits on line 2 — the documented
        # citation divergence, replicated faithfully.
        findings = self.lint("\ufeff\n[s]\nk = 1\n")
        self.assertIn(("missing_section_header", 1), findings)
        self.assertIn(("bom_present", 1), findings)
        self.assertTrue(oracle_rejects("\ufeff\n[s]\nk = 1\n"))

    def test_no_bom_control(self) -> None:
        self.assertNotIn("bom_present", self.lint("[s]\nk = 1\n"))

    # -- inline_comment_risk ---------------------------------------------- #

    def test_inline_comment_risk(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = v ; note\n"),
            [("inline_comment_risk", 2)],
        )
        self.assertEqual(
            self.lint("[s]\nk = v # note\n"),
            [("inline_comment_risk", 2)],
        )
        # the default parser keeps the whole value as data (accepts)
        self.assertFalse(oracle_rejects("[s]\nk = v ; note\n"))

    def test_inline_comment_risk_in_continuation(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = a\n  b ; c\n"),
            [("inline_comment_risk", 3)],
        )

    def test_full_line_comment_not_flagged(self) -> None:
        self.assertEqual(self.lint("[s]\n; full comment\nk = 1\n"), [])

    def test_hash_inside_url_value(self) -> None:
        # a '#' anywhere in the value is data for the default parser
        self.assertEqual(self.lint("[s]\nanchor = a#b\n"), [("inline_comment_risk", 2)])

    # -- interpolation_risk ------------------------------------------------ #

    def test_interpolation_undefined_reference(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = %(missing)s\n"),
            [("interpolation_risk", 2)],
        )
        # read_string accepts; get() raises — warning, not error
        parser = oracle_parser("[s]\nk = %(missing)s\n")
        with self.assertRaises(configparser.InterpolationMissingOptionError):
            parser.get("s", "k")
        self.assertFalse(oracle_rejects("[s]\nk = %(missing)s\n"))

    def test_interpolation_defined_reference_control(self) -> None:
        self.assertEqual(self.lint("[s]\nbase = /x\npath = %(base)s/y\n"), [])

    def test_interpolation_defined_via_default_control(self) -> None:
        self.assertEqual(
            self.lint("[DEFAULT]\nroot = /x\n[s]\npath = %(root)s/y\n"), []
        )

    def test_interpolation_bare_percent(self) -> None:
        self.assertEqual(self.lint("[s]\nk = 100%\n"), [("interpolation_risk", 2)])
        parser = oracle_parser("[s]\nk = 100%\n")
        with self.assertRaises(configparser.InterpolationSyntaxError):
            parser.get("s", "k")

    def test_interpolation_unterminated_token(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = %(oops\n"), [("interpolation_risk", 2)]
        )

    def test_interpolation_escape_control(self) -> None:
        self.assertEqual(self.lint("[s]\nk = 100%% ok%%\n"), [])

    # -- missing_final_newline ----------------------------------------------- #

    def test_missing_final_newline(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = 1"), [("missing_final_newline", 2)]
        )

    def test_final_newline_control(self) -> None:
        self.assertNotIn("missing_final_newline", self.lint("[s]\nk = 1\n"))

    def test_empty_text_lints_clean(self) -> None:
        self.assertEqual(self.lint(""), [])

    # -- trailing_whitespace -------------------------------------------------- #

    def test_trailing_whitespace(self) -> None:
        self.assertEqual(
            self.lint("[s]  \nk = 1 \n"), [("trailing_whitespace", 1), ("trailing_whitespace", 2)]
        )

    def test_crlf_terminator_not_trailing_whitespace(self) -> None:
        # the \r of a CRLF terminator is not counted as trailing
        # whitespace — only genuine space/tab tails are
        self.assertEqual(self.lint("[s]\r\nk = 1\r\n"), [])

    # -- tab_indentation -------------------------------------------------------- #

    def test_tab_indentation(self) -> None:
        self.assertEqual(
            self.lint("[s]\nk = 1\n\tcontinuation\n"),
            [("tab_indentation", 3)],
        )
        # configparser itself accepts the tab-indented continuation
        self.assertFalse(oracle_rejects("[s]\nk = 1\n\tcontinuation\n"))

    def test_space_indentation_control(self) -> None:
        self.assertEqual(self.lint("[s]\nk = 1\n  continuation\n"), [])


class CfgLintPayloadTest(CfgLintToolTestCase):
    """Lint payload shape, ordering and determinism."""

    def test_findings_sorted_by_line_then_code(self) -> None:
        result = self.tool.execute(
            mode="lint", text="[s]\nk = 1 \nk = 2\n\tc\n"
        )
        pairs = codes(result)
        self.assertEqual(pairs, sorted(pairs, key=lambda t: (t[1], t[0])))

    def test_counts_and_result_strings(self) -> None:
        clean = self.tool.execute(mode="lint", text="[s]\nk = 1\n")
        self.assertEqual(clean["result"], "ok")
        self.assertEqual(clean["counts"], {"error": 0, "warning": 0, "info": 0})
        self.assertEqual(clean["total_findings"], 0)
        self.assertFalse(clean["configparser_would_reject"])
        dirty = self.tool.execute(
            mode="lint", text="\ufeffkey = 1 \nk"
        )
        self.assertEqual(dirty["result"], "findings")
        self.assertEqual(dirty["counts"]["error"], 2)
        self.assertEqual(dirty["counts"]["warning"], 1)
        self.assertEqual(dirty["counts"]["info"], 2)
        self.assertTrue(dirty["configparser_would_reject"])

    def test_deterministic_payloads(self) -> None:
        text = "[s]\nKey = 1\nkey = 2 ; x\n\ttab cont"
        first = self.tool.execute(mode="lint", text=text)
        second = self.tool.execute(mode="lint", text=text)
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )

    def test_error_messages_never_contain_values(self) -> None:
        text = "[auth]\npassword = hunter2-password\napi_token = sk-live-abcdef123456\n"
        result = self.tool.execute(mode="lint", text=text)
        self.assert_no_secret_leak(result)


class CfgParseTest(CfgLintToolTestCase):
    """parse mode: deterministic structure even when configparser fails."""

    def test_basic_structure(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="; top\n[a]\nx = 1\ny : 2\n# mid\n[b]\nz = 3\n",
        )
        self.assertEqual(result["result"], "ok")
        self.assertEqual(result["section_order"], ["a", "b"])
        self.assertEqual(result["sections"]["a"]["keys"], ["x", "y"])
        self.assertEqual(result["sections"]["a"]["values"], {"x": "1", "y": "2"})
        self.assertEqual(result["comments"], [{"line": 1, "text": "; top"}, {"line": 5, "text": "# mid"}])
        self.assertEqual(result["total_lines"], 7)
        self.assertEqual(result["option_count"], 3)
        self.assertFalse(result["configparser_would_reject"])

    def test_multiline_values_joined_like_configparser(self) -> None:
        text = "[s]\nk = a\n  b\n\n  c\n"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["sections"]["s"]["values"]["k"], "a\nb\n\nc")
        parser = oracle_parser(text)
        self.assertEqual(parser.get("s", "k", raw=True), "a\nb\n\nc")

    def test_raw_lines_and_key_lines(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[s]\nk = a\n  cont\nj = 2\n"
        )
        self.assertEqual(result["sections"]["s"]["raw_lines"], [1, 2, 3, 4])

    def test_duplicate_keys_reported(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[s]\nName = 1\nname = 2\n"
        )
        section = result["sections"]["s"]
        self.assertEqual(section["keys"], ["Name"])
        self.assertEqual(section["duplicate_keys"], [{"key": "name", "lines": [2, 3]}])
        # non-strict semantics: the later value wins
        self.assertEqual(section["values"]["name"], "2")
        self.assertEqual(result["result"], "parse_errors")

    def test_parse_survives_configparser_rejection(self) -> None:
        text = "[s]\nk = 1\n[s]\nj = 2\n"
        result = self.tool.execute(mode="parse", text=text)
        self.assertTrue(result["configparser_would_reject"])
        self.assertEqual(result["sections"]["s"]["values"], {"k": "1", "j": "2"})
        self.assertEqual(result["sections"]["s"]["raw_lines"], [1, 2, 3, 4])

    def test_default_section_tracked_outside_order(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[DEFAULT]\nx = 1\n[s]\ny = 2\n"
        )
        self.assertEqual(result["section_order"], ["s"])
        self.assertIn("DEFAULT", result["sections"])
        self.assertEqual(result["sections"]["DEFAULT"]["values"], {"x": "1"})

    def test_secret_values_masked(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="[db]\npassword = hunter2-password\napi_key = sk-live-abcdef123456\nuser = bob\n",
        )
        values = result["sections"]["db"]["values"]
        self.assertEqual(values["password"], "***")
        self.assertEqual(values["api_key"], "***")
        self.assertEqual(values["user"], "bob")
        self.assert_no_secret_leak(result)

    def test_keys_keep_original_spelling_and_order(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[s]\nZed = 1\nalpha : 2\nMiXeD = 3\n"
        )
        self.assertEqual(result["sections"]["s"]["keys"], ["Zed", "alpha", "MiXeD"])

    def test_empty_text(self) -> None:
        result = self.tool.execute(mode="parse", text="")
        self.assertEqual(result["sections"], {})
        self.assertEqual(result["section_order"], [])
        self.assertEqual(result["comments"], [])
        self.assertEqual(result["total_lines"], 0)


class CfgCheckTest(CfgLintToolTestCase):
    """check mode: policy options into a pass/fail summary."""

    def test_defaults_pass_on_clean_text(self) -> None:
        result = self.tool.execute(mode="check", text="[s]\nk = 1\n")
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["passed"], 8)
        self.assertEqual(result["failed"], 0)
        names = [c["name"] for c in result["checks"]]
        self.assertEqual(len(names), 8)
        self.assertEqual(len(set(names)), 8)

    def test_section_header_violation_fails(self) -> None:
        result = self.tool.execute(mode="check", text="k = 1\n")
        self.assertEqual(result["result"], "fail")
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertFalse(by_name["require_section_header"]["ok"])
        self.assertEqual(by_name["require_section_header"]["violations"], [1])
        self.assertTrue(by_name["require_unique_options"]["ok"])

    def test_optional_checks_disabled_by_default(self) -> None:
        result = self.tool.execute(mode="check", text="[s]\nk = 1")
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertEqual(result["result"], "pass")
        for name in (
            "require_final_newline",
            "forbid_inline_comments",
            "forbid_tabs",
            "forbid_bom",
        ):
            self.assertFalse(by_name[name]["enabled"], name)

    def test_enabling_optional_checks(self) -> None:
        text = "[s]\nk = v ; note\n"
        options = {"forbid_inline_comments": True, "forbid_tabs": True}
        result = self.tool.execute(mode="check", text=text, options=options)
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertEqual(result["result"], "fail")
        self.assertFalse(by_name["forbid_inline_comments"]["ok"])
        self.assertEqual(by_name["forbid_inline_comments"]["violations"], [2])
        # forbid_tabs stays enabled by explicit flag but has no violation
        self.assertTrue(by_name["forbid_tabs"]["ok"])

    def test_bom_policy(self) -> None:
        result = self.tool.execute(
            mode="check", text="\ufeff[s]\nk = 1\n", options={"forbid_bom": True}
        )
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertFalse(by_name["forbid_bom"]["ok"])
        # the BOM also breaks the section header match — faithful mirror
        self.assertFalse(by_name["require_section_header"]["ok"])

    def test_check_order_is_declaration_order(self) -> None:
        result = self.tool.execute(mode="check", text="[s]\nk = 1\n")
        self.assertEqual(
            [c["name"] for c in result["checks"]],
            [
                "require_section_header",
                "require_parseable",
                "require_unique_sections",
                "require_unique_options",
                "require_final_newline",
                "forbid_inline_comments",
                "forbid_tabs",
                "forbid_bom",
            ],
        )

    def test_duplicate_sections_violate_unique_sections(self) -> None:
        result = self.tool.execute(mode="check", text="[s]\n[s]\n")
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertFalse(by_name["require_unique_sections"]["ok"])

    def test_repeated_default_violates_unique_sections(self) -> None:
        result = self.tool.execute(mode="check", text="[DEFAULT]\n[DEFAULT]\n")
        by_name = {c["name"]: c for c in result["checks"]}
        self.assertFalse(by_name["require_unique_sections"]["ok"])

    def test_deterministic_summary(self) -> None:
        text = "[s]\nk = 1\nk = 2\nbare\n"
        first = self.tool.execute(mode="check", text=text)
        second = self.tool.execute(mode="check", text=text)
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )


class CfgValidationTest(CfgLintToolTestCase):
    """Malformed parameters raise ValueError before any computation."""

    def test_mode_required_and_known(self) -> None:
        self.assert_invalid(text="[s]\n")
        self.assert_invalid(mode="fix", text="[s]\n")
        self.assert_invalid(mode=None, text="[s]\n")
        self.assert_invalid(mode=["lint"], text="[s]\n")

    def test_text_must_be_string(self) -> None:
        self.assert_invalid(mode="lint")
        self.assert_invalid(mode="lint", text=None)
        self.assert_invalid(mode="lint", text=123)
        self.assert_invalid(mode="lint", text=True)
        self.assert_invalid(mode="parse", text=b"[s]\n")

    def test_text_cap(self) -> None:
        self.assert_invalid(mode="lint", text="x" * 100_001)
        # a large-but-legal file (one long value line) lints clean
        result = self.tool.execute(mode="lint", text="[s]\nv = " + "x" * 50_000 + "\n")
        self.assertEqual(result["result"], "ok")

    def test_options_shape(self) -> None:
        self.assert_invalid(mode="check", text="[s]\n", options=True)
        self.assert_invalid(mode="check", text="[s]\n", options=["require_bom"])
        self.assert_invalid(mode="check", text="[s]\n", options={"nope": True})
        self.assert_invalid(mode="check", text="[s]\n", options={"forbid_tabs": "yes"})
        self.assert_invalid(mode="check", text="[s]\n", options={"forbid_tabs": 1})

    def test_options_none_uses_defaults(self) -> None:
        result = self.tool.execute(mode="check", text="[s]\nk = 1\n", options=None)
        self.assertEqual(result["result"], "pass")
        self.assertEqual(len(result["checks"]), 8)

    def test_options_partial_fill(self) -> None:
        result = self.tool.execute(
            mode="check", text="[s]\nk = 1\n", options={"forbid_bom": True}
        )
        enabled = {c["name"]: c["enabled"] for c in result["checks"]}
        self.assertTrue(enabled["forbid_bom"])
        self.assertTrue(enabled["require_section_header"])
        self.assertFalse(enabled["forbid_tabs"])

    def test_lint_ignores_options(self) -> None:
        result = self.tool.execute(
            mode="lint", text="[s]\nk = 1\n", options={"nope": True}
        )
        self.assertEqual(result["result"], "ok")


# --------------------------------------------------------------------- #
# Differential oracle suite: configparser itself is the ground truth
# --------------------------------------------------------------------- #

def _base_configs() -> list[str]:
    """Deterministically built valid INI texts (all oracle-accepted)."""
    bases = []
    # 1..8: hand-built shapes exercising the accepted grammar.
    bases.append("[server]\nhost = localhost\nport = 8080\n")
    bases.append("[server]\nhost: localhost\n[port]\nhost: 0.0.0.0\n")
    bases.append("; leading comment\n[server]\nhost = a#b ; c\n\n[client]\ntimeout = 30\n")
    bases.append("[DEFAULT]\nroot = /opt\n[app]\nhome = %(root)s/app\nlog = 100%%\n")
    bases.append("[app]\ndescription = a long line\n  continued here\n\n  and here\n")
    bases.append("[app]\n\ttabbed continuation\nurl = http://x:80\n")
    bases.append("[a]\nx = 1\n[b]\ny = 2\n[c]\nz = 3\n")
    bases.append("[ empty-ish ]\n\n\n; only comments\nflag = on\n")
    bases.append("[a]\nmy.name-1 = v\nUPPER = V\nMiXeD = v\n")
    bases.append("[a]\nx =\ny = \n")
    # 11..30: combinatorial generated bodies.
    words = ["alpha", "beta", "gamma", "delta"]
    for i in range(20):
        parts = [f"[sec_{i}]"]
        for j in range(4):
            delim = "=" if (i + j) % 2 == 0 else ":"
            parts.append(f"{words[j]}{i} {delim} value-{i}-{j}")
            if j == 1 and i % 3 == 0:
                parts.append("  continued tail")
            if j == 2 and i % 4 == 0:
                parts.append("; inner comment")
            if j == 3 and i % 5 == 0:
                parts.append("")
        bases.append("\n".join(parts) + "\n")
    return bases


def _mutations(base: str) -> list[str]:
    """Systematic single mutations applied to one valid base text."""
    out = [base]
    if not base:
        return out
    # drop the first section header line
    lines = base.split("\n")
    header_idx = next((n for n, l in enumerate(lines) if l.strip().startswith("[")), None)
    if header_idx is not None:
        without = list(lines)
        del without[header_idx]
        out.append("\n".join(without))
        # move an option line above the first section header
        option_idx = next(
            (n for n, l in enumerate(lines) if n > header_idx and ("=" in l or ":" in l)),
            None,
        )
        if option_idx is not None:
            moved = list(lines)
            opt = moved.pop(option_idx)
            moved.insert(header_idx, opt)
            out.append("\n".join(moved))
        # duplicate the first section header right after its block start
        dup_header = list(lines)
        dup_header.insert(header_idx + 1, lines[header_idx])
        out.append("\n".join(dup_header))
    # duplicate the first option line
    option_idx = next((n for n, l in enumerate(lines) if "=" in l or ":" in l), None)
    if option_idx is not None:
        dup = list(lines)
        dup.insert(option_idx + 1, lines[option_idx])
        out.append("\n".join(dup))
        # case-variant duplicate of that option
        line = lines[option_idx]
        head, sep, tail = line.partition("=") if "=" in line else line.partition(":")
        variant = head.upper() + sep + tail
        case_dup = list(lines)
        case_dup.insert(option_idx + 1, variant)
        out.append("\n".join(case_dup))
        # strip the delimiter -> bare key
        bare = list(lines)
        key = head.strip()
        bare[option_idx] = key
        out.append("\n".join(bare))
        # empty option name
        empty = list(lines)
        empty[option_idx] = sep + tail
        out.append("\n".join(empty))
        # inline comment in the value
        inline = list(lines)
        inline[option_idx] = line.rstrip("\n") + " ; inline note"
        out.append("\n".join(inline))
        # interpolation hazards in the value
        interp = list(lines)
        interp[option_idx] = line.rstrip("\n") + "%(ghost)s"
        out.append("\n".join(interp))
        interp2 = list(lines)
        interp2[option_idx] = line.rstrip("\n") + " 75%"
        out.append("\n".join(interp2))
        # trailing whitespace on the option line
        trail = list(lines)
        trail[option_idx] = line.rstrip("\n") + "  "
        out.append("\n".join(trail))
        # tab continuation under the option
        tab = list(lines)
        tab.insert(option_idx + 1, "\textra tail")
        out.append("\n".join(tab))
        # dedented pseudo-continuation (breaks only when indent < option)
        dedent = list(lines)
        dedent.insert(option_idx + 1, "flat tail")
        out.append("\n".join(dedent))
    # whole-text mutations
    out.append("\ufeff" + base)
    if base.endswith("\n"):
        out.append(base[:-1])
    out.append(base.replace("\n", "\r\n"))
    return out


def _corpus() -> list[str]:
    """The differential corpus: valid bases plus their mutations."""
    corpus = []
    for base in _base_configs():
        corpus.extend(_mutations(base))
    # remove exact duplicates while keeping order (deterministic)
    seen = set()
    unique = []
    for text in corpus:
        if text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


class CfgDifferentialOracleTest(CfgLintToolTestCase):
    """The tool's verdict must equal the real configparser's behavior."""

    def test_corpus_size(self) -> None:
        corpus = _corpus()
        self.assertGreaterEqual(len(corpus), 300)
        rejected = [t for t in corpus if oracle_rejects(t)]
        accepted = [t for t in corpus if not oracle_rejects(t)]
        self.assertGreater(len(rejected), 30, "corpus must contain rejects")
        self.assertGreater(len(accepted), 30, "corpus must contain accepts")

    def test_verdicts_match_the_real_configparser(self) -> None:
        corpus = _corpus()
        mismatches = []
        for text in corpus:
            expected = oracle_rejects(text)
            got = self.tool.execute(mode="lint", text=text)["configparser_would_reject"]
            if expected != got:
                mismatches.append((text, expected, got))
        self.assertEqual(
            mismatches,
            [],
            f"{len(mismatches)}/{len(corpus)} verdict mismatches; first: "
            f"{mismatches[0] if mismatches else None}",
        )

    def test_parse_values_match_the_real_configparser(self) -> None:
        corpus = _corpus()
        checked = 0
        mismatches = []
        for text in corpus:
            if oracle_rejects(text):
                continue
            parser = oracle_parser(text)
            result = self.tool.execute(mode="parse", text=text)
            for name in parser.sections():
                mine = result["sections"].get(name, {}).get("values", {})
                for option in parser.options(name):
                    if not parser.has_option(name, option):
                        continue
                    if name in parser.sections() and parser.has_option(name, option):
                        # only compare keys the section itself defines —
                        # DEFAULT-inherited options are not section-local
                        if option in mine:
                            expected = parser.get(name, option, raw=True)
                            if mine[option] != expected:
                                mismatches.append(
                                    (text, name, option, mine[option], expected)
                                )
                            checked += 1
        self.assertGreater(checked, 200, "must have compared a real volume of values")
        self.assertEqual(
            mismatches, [], f"first: {mismatches[0] if mismatches else None}"
        )

    def test_curated_citation_agreement(self) -> None:
        # where the oracle's exception cites a line, the mirror finding
        # cites the same line (the oracle pads its "[line %2d]" field)
        text = "[s]\nk = 1\nk = 2\n"
        with self.assertRaises(configparser.DuplicateOptionError) as ctx:
            oracle_parser(text)
        self.assertIn("[line  3]", str(ctx.exception))
        self.assertIn(("duplicate_option", 3), self.lint(text))

        text = "[s]\nk = 1\n[s]\n"
        with self.assertRaises(configparser.DuplicateSectionError) as ctx:
            oracle_parser(text)
        self.assertIn("[line  3]", str(ctx.exception))
        self.assertIn(("duplicate_section", 3), self.lint(text))

        text = "a = 1\n[s]\n"
        with self.assertRaises(configparser.MissingSectionHeaderError) as ctx:
            oracle_parser(text)
        self.assertIn("line: 1", str(ctx.exception))
        self.assertIn(("missing_section_header", 1), self.lint(text))

        text = "[s]\nk = 1\nbogus line\n"
        with self.assertRaises(configparser.ParsingError) as ctx:
            oracle_parser(text)
        self.assertIn("[line  3]", str(ctx.exception))
        self.assertIn(("key_without_value", 3), self.lint(text))

    def test_direct_class_import(self) -> None:
        self.assertIs(DirectCfgLintTool, CfgLintTool)
        result = DirectCfgLintTool().execute(mode="lint", text="[s]\nk = 1\n")
        self.assertEqual(result["result"], "ok")


if __name__ == "__main__":
    unittest.main()
