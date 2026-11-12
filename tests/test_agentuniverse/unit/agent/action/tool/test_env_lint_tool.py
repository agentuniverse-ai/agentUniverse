#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_env_lint_tool.py

"""Offline unit tests for EnvLintTool.

The tool is built purely on the standard library and never touches
the network or the filesystem, so this suite runs fully offline.
Every assertion is deterministic: each of the 17 lint rules is
exercised against a triggering fixture AND a control fixture that
must stay silent, whole-file findings are compared against literal
sorted (code, line) tuples, fix_hints against exact fixed texts
(plus re-lint resolution and idempotence), stats against literal
arithmetic ground truths, and the error matrix against strict
ValueError contracts.

Security invariant asserted in EVERY test whose fixture carries a
secret-ish variable name (containing KEY/SECRET/PASSWORD/TOKEN): the
raw secret value must not appear anywhere in the serialized result
of any mode.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import EnvLintTool
from agentuniverse.agent.action.tool.common_tool.env_lint_tool import (
    RULES,
    SEVERITIES,
)
from agentuniverse.agent.action.tool.common_tool.env_lint_tool import (
    EnvLintTool as DirectEnvLintTool,
)

SECRET_RAW_VALUES = ("sk-live-abcdef123456", "hunter2-secret")


def codes(result) -> list:
    """The findings of a lint-style payload as (code, line) tuples."""
    return [(f["code"], f["line"]) for f in result["findings"]]


class EnvLintToolTestCase(unittest.TestCase):
    """Shared helpers."""

    def setUp(self) -> None:
        self.tool = EnvLintTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def assert_no_secret_leak(self, result) -> None:
        """No raw secret value may appear anywhere in the payload."""
        dumped = json.dumps(result, sort_keys=True, default=str)
        for raw in SECRET_RAW_VALUES:
            self.assertNotIn(raw, dumped)


class EnvLintRegistryTest(EnvLintToolTestCase):
    """The rule registry is the documented 17-rule set."""

    def test_registry(self) -> None:
        self.assertEqual(len(RULES), 17)
        self.assertEqual(
            RULES,
            (
                "bom_present",
                "crlf_line_endings",
                "duplicate_keys",
                "empty_value_without_default_marker",
                "export_prefix_mixing",
                "inconsistent_key_case",
                "key_with_spaces",
                "line_without_assignment",
                "lowercase_key",
                "missing_final_newline",
                "order_grouping_breaks",
                "quote_style_mixing",
                "spacing_around_equals",
                "trailing_whitespace",
                "value_with_unquoted_hash",
                "value_with_unquoted_spaces",
                "very_long_line",
            ),
        )

    def test_severity_model(self) -> None:
        errors = sorted(code for code, sev in SEVERITIES.items() if sev == "error")
        warnings = sorted(code for code, sev in SEVERITIES.items() if sev == "warning")
        infos = sorted(code for code, sev in SEVERITIES.items() if sev == "info")
        self.assertEqual(
            errors,
            ["duplicate_keys", "key_with_spaces", "line_without_assignment"],
        )
        self.assertEqual(
            warnings,
            [
                "bom_present",
                "empty_value_without_default_marker",
                "export_prefix_mixing",
                "inconsistent_key_case",
                "quote_style_mixing",
                "spacing_around_equals",
                "value_with_unquoted_hash",
                "value_with_unquoted_spaces",
            ],
        )
        self.assertEqual(
            infos,
            [
                "crlf_line_endings",
                "lowercase_key",
                "missing_final_newline",
                "order_grouping_breaks",
                "trailing_whitespace",
                "very_long_line",
            ],
        )

    def test_findings_sorted_and_counted(self) -> None:
        result = self.tool.execute(mode="lint", text="B=2\nA=1\nA=3\n")
        pairs = [(f["line"], f["code"]) for f in result["findings"]]
        self.assertEqual(pairs, sorted(pairs))
        counts = result["counts"]
        self.assertEqual(
            counts["total"],
            counts["error"] + counts["warning"] + counts["info"],
        )
        self.assertEqual(counts["total"], len(result["findings"]))

    def test_deterministic(self) -> None:
        text = "FOO=1\nfoo=2\nBAR = spaced\nMSG=hello world\n"
        first = self.tool.execute(mode="lint", text=text)
        second = self.tool.execute(mode="lint", text=text)
        self.assertEqual(first, second)


class EnvLintCleanTest(EnvLintToolTestCase):
    """A tidy file lints clean; each rule's control stays silent."""

    TIDY = "\n".join(
        [
            "# service configuration",
            "",
            "API_HOST=localhost",
            "API_PORT=8080",
            "DEBUG=true",
            "TAGLINE=everything-is-fine",
            "",
            "# database",
            "DB_HOST=db.example.com",
            "DB_PORT=5432",
            "",
        ]
    )

    def test_tidy_file_is_clean(self) -> None:
        result = self.tool.execute(mode="lint", text=self.TIDY)
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["clean"])
        self.assertEqual(result["result"], "clean")
        self.assertEqual(result["counts"], {"error": 0, "warning": 0, "info": 0, "total": 0})

    def test_empty_text_is_clean(self) -> None:
        self.assertTrue(self.tool.execute(mode="lint", text="")["clean"])

    def test_all_quoted_is_clean(self) -> None:
        result = self.tool.execute(mode="lint", text='A="1"\nB="2"\n')
        self.assertEqual(result["findings"], [])

    def test_all_unquoted_is_clean(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2\n")
        self.assertEqual(result["findings"], [])

    def test_whitespace_only_lines_are_trailing_whitespace(self) -> None:
        result = self.tool.execute(mode="lint", text="# c\n\n   \n\t\nB=2\n")
        self.assertEqual(
            codes(result),
            [("trailing_whitespace", 3), ("trailing_whitespace", 4)],
        )


class EnvLintRuleMatrixTest(EnvLintToolTestCase):
    """One triggered + one control fixture per rule."""

    # -- error rules ---------------------------------------------------- #

    def test_duplicate_keys(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2\nA=3\nA=4\n")
        hits = [pair for pair in codes(result) if pair[0] == "duplicate_keys"]
        self.assertEqual(hits, [("duplicate_keys", 3), ("duplicate_keys", 4)])
        message = result["findings"][0]["message"]
        self.assertIn("first at line 1", message)
        self.assertEqual(SEVERITIES["duplicate_keys"], "error")

    def test_duplicate_keys_control(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2\nA3=3\n")
        self.assertNotIn("duplicate_keys", [c for c, _ in codes(result)])

    def test_key_with_spaces(self) -> None:
        result = self.tool.execute(mode="lint", text="MY KEY=1\nOK=2\n")
        self.assertEqual(codes(result), [("key_with_spaces", 1)])
        self.assertEqual(result["findings"][0]["preview"], "MY KEY=***")
        self.assertEqual(SEVERITIES["key_with_spaces"], "error")

    def test_key_with_spaces_control(self) -> None:
        # A space before '=' is a consistent spacing choice, not an
        # illegal key.
        result = self.tool.execute(mode="lint", text="A = 1\nB = 2\n")
        self.assertEqual(result["findings"], [])

    def test_line_without_assignment(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\njust text\nB=2\n")
        self.assertEqual(codes(result), [("line_without_assignment", 2)])
        self.assertEqual(result["findings"][0]["preview"], "just text")
        self.assertEqual(SEVERITIES["line_without_assignment"], "error")

    def test_line_without_assignment_control(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\n# comment\n\nB=2\n")
        self.assertEqual(result["findings"], [])

    # -- warning rules --------------------------------------------------- #

    def test_inconsistent_key_case(self) -> None:
        result = self.tool.execute(mode="lint", text="FOO=1\nfoo=2\n")
        self.assertEqual(
            codes(result),
            [("inconsistent_key_case", 2), ("lowercase_key", 2)],
        )
        message = next(f["message"] for f in result["findings"] if f["code"] == "inconsistent_key_case")
        self.assertIn("'FOO'", message)

    def test_inconsistent_key_case_control(self) -> None:
        result = self.tool.execute(mode="lint", text="FOO=1\nFOOBAR=2\n")
        self.assertNotIn("inconsistent_key_case", [c for c, _ in codes(result)])

    def test_quote_style_mixing(self) -> None:
        result = self.tool.execute(mode="lint", text='A="1"\nB=2\nC="3"\n')
        self.assertEqual(codes(result), [("quote_style_mixing", 2)])

    def test_quote_style_mixing_tie_silent(self) -> None:
        # 1 quoted vs 1 unquoted: no authoritative side -> silent.
        result = self.tool.execute(mode="lint", text='A="1"\nB=2\n')
        self.assertEqual(result["findings"], [])

    def test_quote_style_mixing_empty_has_no_style(self) -> None:
        # Empty unquoted values carry no quote style, so B= never
        # fabricates a mixing finding against the quoted majority.
        result = self.tool.execute(mode="lint", text='A="1"\nB=\nC="2"\n')
        self.assertEqual(codes(result), [("empty_value_without_default_marker", 2)])

    def test_export_prefix_mixing(self) -> None:
        result = self.tool.execute(mode="lint", text="export A=1\nexport B=2\nC=3\n")
        self.assertEqual(codes(result), [("export_prefix_mixing", 3)])

    def test_export_prefix_mixing_control(self) -> None:
        result = self.tool.execute(mode="lint", text="export A=1\n")
        self.assertEqual(result["findings"], [])

    def test_spacing_around_equals(self) -> None:
        result = self.tool.execute(mode="lint", text="A = 1\nB = 2\nC=3\n")
        self.assertEqual(codes(result), [("spacing_around_equals", 3)])

    def test_spacing_around_equals_control(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2\n")
        self.assertEqual(result["findings"], [])

    def test_empty_value_without_default_marker(self) -> None:
        result = self.tool.execute(mode="lint", text="A=\nB=2\n")
        self.assertEqual(codes(result), [("empty_value_without_default_marker", 1)])
        self.assertEqual(SEVERITIES["empty_value_without_default_marker"], "warning")

    def test_empty_value_default_marker_suppressed(self) -> None:
        for line in ("A= # optional", "A= # default: none", "A=  # DEFAULT"):
            with self.subTest(line=line):
                result = self.tool.execute(mode="lint", text=line + "\n")
                self.assertNotIn(
                    "empty_value_without_default_marker",
                    [c for c, _ in codes(result)],
                )

    def test_empty_quoted_value_not_flagged(self) -> None:
        result = self.tool.execute(mode="lint", text='A=""\n')
        self.assertEqual(result["findings"], [])

    def test_value_with_unquoted_spaces(self) -> None:
        result = self.tool.execute(mode="lint", text="MSG=hello world\n")
        self.assertEqual(codes(result), [("value_with_unquoted_spaces", 1)])

    def test_value_with_unquoted_spaces_control(self) -> None:
        # ALT < MSG keeps the block ascending; 1 quoted vs 1 unquoted
        # is a style tie, which stays silent.
        result = self.tool.execute(mode="lint", text='ALT=plain\nMSG="hello world"\n')
        self.assertEqual(result["findings"], [])

    def test_value_with_unquoted_hash(self) -> None:
        for text in ("COLOR=#fff\n", "A=v # note\n", "A= # note\n"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="lint", text=text)
                self.assertIn("value_with_unquoted_hash", [c for c, _ in codes(result)])

    def test_value_with_unquoted_hash_control(self) -> None:
        result = self.tool.execute(mode="lint", text='A="v"\nCOLOR="#fff"\n')
        self.assertEqual(result["findings"], [])

    # -- info rules ------------------------------------------------------ #

    def test_lowercase_key(self) -> None:
        result = self.tool.execute(mode="lint", text="abc=1\nDEF=2\n")
        self.assertEqual(codes(result), [("lowercase_key", 1)])

    def test_lowercase_key_control(self) -> None:
        result = self.tool.execute(mode="lint", text="FOO_BAR2=1\nX_Y=2\n")
        self.assertEqual(result["findings"], [])

    def test_trailing_whitespace(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1   \nB=2\t\n")
        self.assertEqual(
            codes(result),
            [("trailing_whitespace", 1), ("trailing_whitespace", 2)],
        )

    def test_trailing_whitespace_control(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB = 2\n")
        self.assertEqual(result["findings"], [])

    def test_missing_final_newline(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2")
        self.assertEqual(codes(result), [("missing_final_newline", 2)])

    def test_missing_final_newline_control(self) -> None:
        self.assertTrue(self.tool.execute(mode="lint", text="A=1\n")["clean"])

    def test_crlf_line_endings(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\r\nB=2\r\n")
        self.assertEqual(codes(result), [("crlf_line_endings", 1)])
        self.assertIn("2 of 2 lines", result["findings"][0]["message"])

    def test_crlf_line_endings_control(self) -> None:
        self.assertTrue(self.tool.execute(mode="lint", text="A=1\n")["clean"])

    def test_bom_present(self) -> None:
        result = self.tool.execute(mode="lint", text="\ufeffA=1\n")
        self.assertEqual(codes(result), [("bom_present", 1)])

    def test_bom_present_control(self) -> None:
        self.assertTrue(self.tool.execute(mode="lint", text="A=1\n")["clean"])

    def test_very_long_line(self) -> None:
        long_line = "A=" + "x" * 6000
        result = self.tool.execute(mode="lint", text=long_line + "\n")
        self.assertEqual(
            codes(result),
            [("very_long_line", 1)],
        )

    def test_very_long_line_boundary_control(self) -> None:
        # A line of exactly 5000 characters must stay silent.
        line = "A=" + "x" * 4998
        self.assertEqual(len(line), 5000)
        self.assertTrue(self.tool.execute(mode="lint", text=line + "\n")["clean"])

    def test_order_grouping_breaks(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nC=2\nB=3\n")
        self.assertEqual(codes(result), [("order_grouping_breaks", 3)])

    def test_order_grouping_separator_starts_new_block(self) -> None:
        result = self.tool.execute(mode="lint", text="Z=1\n\n# new group\nA=2\n")
        self.assertEqual(result["findings"], [])

    def test_order_grouping_sorted_control(self) -> None:
        result = self.tool.execute(mode="lint", text="A=1\nB=2\nC=3\n")
        self.assertEqual(result["findings"], [])


class EnvLintRealWorldSampleTest(EnvLintToolTestCase):
    """A realistic messy .env with CRLF, BOM, unicode and a secret."""

    MESSY = (
        "\ufeff# app configuration\r\n"
        "\r\n"
        "APP_NAME=my app\r\n"
        "API_KEY=sk-live-abcdef123456\r\n"
        "API_KEY=sk-live-abcdef123456  \r\n"
        "api_port=8080\r\n"
        "COLOR=#ff0000\r\n"
        "EMPTY=\r\n"
        "MULTI = word1 word2\r\n"
        "just a stray line\r\n"
        "GREETING=Grüße Welt\r\n"
    )

    def test_full_findings_ground_truth(self) -> None:
        result = self.tool.execute(mode="lint", text=self.MESSY)
        # "API_KEY" sorts *below* "APP_NAME" (I < P), so line 4 is an
        # order break inside the single leading block.
        self.assertEqual(
            codes(result),
            [
                ("bom_present", 1),
                ("crlf_line_endings", 1),
                ("value_with_unquoted_spaces", 3),
                ("order_grouping_breaks", 4),
                ("duplicate_keys", 5),
                ("trailing_whitespace", 5),
                ("lowercase_key", 6),
                ("value_with_unquoted_hash", 7),
                ("empty_value_without_default_marker", 8),
                ("spacing_around_equals", 9),
                ("value_with_unquoted_spaces", 9),
                ("line_without_assignment", 10),
                ("value_with_unquoted_spaces", 11),
            ],
        )
        self.assertEqual(
            result["counts"],
            {"error": 2, "warning": 7, "info": 4, "total": 13},
        )
        self.assertFalse(result["clean"])
        self.assertEqual(
            result["result"],
            "13 finding(s): 2 error(s), 7 warning(s), 4 info(s)",
        )
        self.assert_no_secret_leak(result)

    def test_stats_ground_truth(self) -> None:
        result = self.tool.execute(mode="stats", text=self.MESSY)
        self.assertEqual(result["total_lines"], 11)
        self.assertEqual(result["blank_lines"], 1)
        self.assertEqual(result["comment_lines"], 1)
        self.assertEqual(result["assignment_lines"], 8)
        # api_port is a distinct spelling (no API_PORT twin present).
        self.assertEqual(result["vars"], 7)
        self.assertEqual(result["exported_vars"], 0)
        self.assertEqual(result["quoted"], 0)
        # Style counts are per assignment line (API_KEY twice).
        self.assertEqual(result["unquoted"], 7)
        self.assertEqual(result["empty_values"], 1)
        self.assertEqual(result["quoted_ratio"], 0.0)
        self.assertEqual(
            result["grouping"],
            {"runs": 2, "order_breaks": 1, "assessment": "mostly_alphabetical"},
        )
        self.assertEqual(
            result["encoding"],
            {"bom": True, "line_ending": "crlf", "final_newline": True},
        )
        self.assertIn("7 variable(s), 0% quoted", result["result"])
        self.assert_no_secret_leak(result)


class EnvLintSecretMaskingTest(EnvLintToolTestCase):
    """Values of secret-ish names never appear in any payload."""

    LEAKY_TEXT = (
        "API_KEY=sk-live-abcdef123456   \n"
        "DB_PASSWORD=hunter2-secret\n"
        "SESSION_TOKEN=abc def\n"
        "PUBLIC_NAME=not a secret\n"
        "MY SECRET=leak attempt\n"
    )

    def test_lint_never_echoes_secrets(self) -> None:
        result = self.tool.execute(mode="lint", text=self.LEAKY_TEXT)
        self.assert_no_secret_leak(result)

    def test_fix_snapshots_mask_secret_values(self) -> None:
        result = self.tool.execute(mode="fix_hints", text=self.LEAKY_TEXT)
        self.assert_no_secret_leak(result)
        strip = next(f for f in result["fixes"] if f["fix"] == "strip_trailing_whitespace")
        self.assertEqual(strip["before"], "API_KEY=***   ")
        self.assertEqual(strip["after"], "API_KEY=***")
        quote = next(f for f in result["fixes"] if f["line"] == 3)
        self.assertEqual(quote["before"], "SESSION_TOKEN=***")
        self.assertEqual(quote["after"], 'SESSION_TOKEN="***"')
        # Line 5 is a spaced-key line — the fixer never touches it.
        self.assertNotIn(5, {f["line"] for f in result["fixes"]})
        # Its finding preview masks the value after the '='.
        preview = self.tool.execute(mode="lint", text="MY SECRET=leak attempt\n")["findings"][0]["preview"]
        self.assertEqual(preview, "MY SECRET=***")

    def test_fixed_text_masks_secret_values(self) -> None:
        result = self.tool.execute(mode="fix_hints", text=self.LEAKY_TEXT)
        self.assertIn("API_KEY=***", result["fixed_text"])
        self.assertIn("DB_PASSWORD=***", result["fixed_text"])
        self.assert_no_secret_leak(result)

    def test_bom_snapshots_mask_secret_values(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", text="\ufeffAPI_KEY=sk-live-abcdef123456\n"
        )
        self.assert_no_secret_leak(result)
        strip = next(f for f in result["fixes"] if f["fix"] == "strip_bom")
        self.assertEqual(strip["before"], "\ufeffAPI_KEY=***")
        self.assertEqual(strip["after"], "API_KEY=***")

    def test_bom_secret_masked_across_all_modes(self) -> None:
        text = "\ufeffDB_PASSWORD=hunter2-secret\r\nPLAIN=ok\r\n"
        for mode in ("lint", "fix_hints", "stats"):
            with self.subTest(mode=mode):
                self.assert_no_secret_leak(
                    self.tool.execute(mode=mode, text=text)
                )

    def test_non_secret_values_visible(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="MSG=hello world\n")
        quote = result["fixes"][0]
        self.assertEqual(quote["before"], "MSG=hello world")
        self.assertEqual(quote["after"], 'MSG="hello world"')
        self.assertEqual(result["fixed_text"], 'MSG="hello world"\n')


class EnvLintFixTest(EnvLintToolTestCase):
    """fix_hints: exact edits, re-lint resolution, idempotence."""

    def test_exact_fixed_text(self) -> None:
        text = "A=1   \n" "MSG=hello world\n" "COLOR=#fff\n" "PATH_LIKE=C:\\new dir\n" "B=2"
        result = self.tool.execute(mode="fix_hints", text=text)
        self.assertEqual(
            result["fixed_text"],
            "A=1\n" 'MSG="hello world"\n' 'COLOR="#fff"\n' 'PATH_LIKE="C:\\\\new dir"\n' "B=2\n",
        )

    def test_fixes_records(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="A=1  \nCOLOR=#fff")
        self.assertEqual(
            result["fixes"],
            [
                {
                    "line": 1,
                    "fix": "strip_trailing_whitespace",
                    "before": "A=1  ",
                    "after": "A=1",
                },
                {
                    "line": 2,
                    "fix": "quote_value",
                    "before": "COLOR=#fff",
                    "after": 'COLOR="#fff"',
                },
                {
                    "line": 2,
                    "fix": "add_final_newline",
                    "before": "<missing final newline>",
                    "after": "<final newline added>",
                },
            ],
        )
        self.assertEqual(
            result["fixes_by_type"],
            {
                "strip_trailing_whitespace": 1,
                "quote_value": 1,
                "add_final_newline": 1,
            },
        )

    def test_inline_comment_stays_outside_quotes(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="NOTE=see the docs # upstream issue\n")
        # Data "see the docs" has a space -> quoted; the comment stays.
        self.assertEqual(result["fixed_text"], 'NOTE="see the docs" # upstream issue\n')
        # Pure-comment data with no space/hash is left untouched.
        result = self.tool.execute(mode="fix_hints", text="A=val # note\n")
        self.assertEqual(result["fixed_text"], "A=val # note\n")

    def test_bom_crlf_fixes(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="\ufeffA=1\r\nB=2\r\n")
        self.assertEqual(result["fixed_text"], "A=1\nB=2\n")
        self.assertEqual([f["fix"] for f in result["fixes"]], ["strip_bom", "crlf_to_lf"])

    def test_target_codes_resolved(self) -> None:
        text = "A=1  \r\nCOLOR=#fff\r\nMSG=a b\r\nWIN=C:\\x y\r\nLAST=1"
        result = self.tool.execute(mode="fix_hints", text=text)
        for code in (
            "trailing_whitespace",
            "crlf_line_endings",
            "missing_final_newline",
            "value_with_unquoted_spaces",
            "value_with_unquoted_hash",
        ):
            self.assertIn(code, result["resolved_codes"])
            self.assertNotIn(code, result["remaining_codes"])
        # The embedded re-lint matches a fresh lint of the fixed text.
        fresh = self.tool.execute(mode="lint", text=result["fixed_text"])["findings"]
        self.assertEqual(result["remaining_findings"], fresh)

    def test_idempotence(self) -> None:
        text = "A=1  \r\nCOLOR=#fff\r\nMSG=a b # c\r\nWIN=C:\\x y\r\nZ=1"
        first = self.tool.execute(mode="fix_hints", text=text)
        second = self.tool.execute(mode="fix_hints", text=first["fixed_text"])
        self.assertEqual(second["fixes"], [])
        self.assertEqual(second["fixed_text"], first["fixed_text"])
        for code in (
            "trailing_whitespace",
            "crlf_line_endings",
            "missing_final_newline",
            "bom_present",
            "value_with_unquoted_spaces",
            "value_with_unquoted_hash",
        ):
            self.assertNotIn(code, second["remaining_codes"])

    def test_no_fixes_needed(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="A=1\nB=2\n")
        self.assertEqual(result["fixes"], [])
        self.assertEqual(result["fixed_text"], "A=1\nB=2\n")
        self.assertIn("no safe fixes needed", result["result"])

    def test_never_touches_unsafe_things(self) -> None:
        # Duplicate keys, case collisions, bare lines, spacing, export
        # prefixes, key case and ordering are human decisions.
        text = "A=1\nA=2\nfoo=1\nbare line\nB = 1\nexport C=3\n"
        result = self.tool.execute(mode="fix_hints", text=text)
        for fix in result["fixes"]:
            self.assertIn(
                fix["fix"],
                (
                    "strip_bom",
                    "crlf_to_lf",
                    "strip_trailing_whitespace",
                    "quote_value",
                    "add_final_newline",
                ),
            )
        self.assertIn("duplicate_keys", result["remaining_codes"])
        self.assertIn("line_without_assignment", result["remaining_codes"])
        self.assertIn("spacing_around_equals", result["remaining_codes"])
        self.assertIn("export_prefix_mixing", result["remaining_codes"])

    def test_quoting_preserves_parsed_value(self) -> None:
        # Escaping keeps the dotenv-parsed value identical.
        text = 'WIN=C:\\new dir\nQ=say "hi" now\n'
        result = self.tool.execute(mode="fix_hints", text=text)
        self.assertEqual(
            result["fixed_text"],
            'WIN="C:\\\\new dir"\nQ="say \\"hi\\" now"\n',
        )

    def test_empty_file_fix(self) -> None:
        result = self.tool.execute(mode="fix_hints", text="")
        self.assertEqual(result["fixes"], [])
        self.assertEqual(result["fixed_text"], "")


class EnvLintStatsTest(EnvLintToolTestCase):
    """stats arithmetic against literal ground truths."""

    TEXT = (
        "\n".join(
            [
                "# header comment",
                'export ALPHA="one"',
                "BETA=two",
                "# inline section",
                "export DELTA=three",
                'EPSILON=""',
                "",
                'ZETA=""',
            ]
        )
        + "\n"
    )

    def test_counts_ground_truth(self) -> None:
        result = self.tool.execute(mode="stats", text=self.TEXT)
        self.assertEqual(result["total_lines"], 8)
        self.assertEqual(result["blank_lines"], 1)
        self.assertEqual(result["comment_lines"], 2)
        self.assertEqual(result["assignment_lines"], 5)
        self.assertEqual(result["vars"], 5)
        self.assertEqual(result["exported_vars"], 2)
        # ALPHA / EPSILON / ZETA quoted vs BETA / DELTA unquoted.
        self.assertEqual(result["quoted"], 3)
        self.assertEqual(result["unquoted"], 2)
        # The quoted-empty EPSILON / ZETA count as empty values.
        self.assertEqual(result["empty_values"], 2)
        self.assertEqual(result["quoted_ratio"], round(3 / 5, 2))
        # Blocks: (ALPHA, BETA) | (DELTA, EPSILON) | (ZETA).
        self.assertEqual(
            result["grouping"],
            {"runs": 3, "order_breaks": 0, "assessment": "alphabetical"},
        )
        self.assertEqual(
            result["encoding"],
            {"bom": False, "line_ending": "lf", "final_newline": True},
        )

    def test_empty_file_stats(self) -> None:
        result = self.tool.execute(mode="stats", text="")
        self.assertEqual(result["vars"], 0)
        self.assertIsNone(result["quoted_ratio"])
        self.assertEqual(
            result["grouping"],
            {"runs": 0, "order_breaks": 0, "assessment": "no assignments"},
        )
        self.assertIn("n/a", result["result"])

    def test_assessment_boundaries(self) -> None:
        # 5 assignments, 1 break -> 1*4 <= 5 -> mostly_alphabetical.
        text = "A=1\nB=2\nA2=3\nC=4\nD=5\n"
        result = self.tool.execute(mode="stats", text=text)
        self.assertEqual(
            result["grouping"],
            {
                "runs": 1,
                "order_breaks": 1,
                "assessment": "mostly_alphabetical",
            },
        )
        # 5 assignments, 3 breaks -> 3*4 > 5 -> unsorted.
        text = "A=1\nZ=2\nB=3\nY=4\nC=5\n"
        result = self.tool.execute(mode="stats", text=text)
        self.assertEqual(result["grouping"]["assessment"], "unsorted")

    def test_mixed_line_endings(self) -> None:
        result = self.tool.execute(mode="stats", text="A=1\r\nB=2\n")
        self.assertEqual(result["encoding"]["line_ending"], "mixed")

    def test_unicode_values_counted(self) -> None:
        result = self.tool.execute(mode="stats", text="GREETING=Grüße\nLANG=de\n")
        self.assertEqual(result["vars"], 2)
        self.assertEqual(result["unquoted"], 2)


class EnvLintErrorMatrixTest(EnvLintToolTestCase):
    """Malformed parameters raise ValueError before any computation."""

    def test_unknown_mode(self) -> None:
        for mode in ("lintt", "", None, "LINT", 1):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text="A=1\n")

    def test_text_required_string(self) -> None:
        for bad in (None, 123, 1.5, True, ["A=1"], {"a": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="lint", text=bad)

    def test_text_size_limit(self) -> None:
        self.assert_invalid(mode="lint", text="x" * 100_001)
        # Exactly at the limit is accepted: a single 100k-character
        # line without '=' is a bare line, over-long and unterminated.
        ok = self.tool.execute(mode="lint", text="x" * 100_000)
        self.assertEqual(
            [f["code"] for f in ok["findings"]],
            [
                "line_without_assignment",
                "missing_final_newline",
                "very_long_line",
            ],
        )

    def test_max_text_chars_attribute_enforced(self) -> None:
        tool = EnvLintTool(max_text_chars=10)
        with self.assertRaises(ValueError):
            tool.execute(mode="lint", text="A=123456789")
        self.assertTrue(tool.execute(mode="lint", text="A=1234567\n")["clean"])

    def test_error_names_the_tool(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nope", text="A=1\n")
        self.assertIn("env_lint_tool", str(ctx.exception))
        self.assertIn("mode must be one of", str(ctx.exception))


class EnvLintToolRegistrationTest(EnvLintToolTestCase):
    """The tool is importable exactly like its family siblings."""

    def test_direct_import_identity(self) -> None:
        self.assertIs(DirectEnvLintTool, type(self.tool))

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "env_lint_tool")
        self.assertIn("17", self.tool.description)
        self.assertEqual(self.tool.MODES, ("lint", "fix_hints", "stats"))


if __name__ == "__main__":
    unittest.main()
