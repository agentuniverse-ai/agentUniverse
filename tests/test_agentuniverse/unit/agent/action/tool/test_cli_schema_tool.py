#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_cli_schema_tool.py

"""Offline unit tests for CliSchemaTool.

The tool is built purely on the standard library and never touches the
network or the filesystem, so this suite runs fully offline. Every
assertion is deterministic: ``check`` verdicts (parsed values,
missing/unknown/type-mismatch reporting, defaults, ``--`` terminator,
negative-number edge, repeated and multiple flags) are pinned against
literal ground truths, ``usage`` output against exact strings, and
``suggested_schema`` against pinned inferred schemas — plus the
round-trip property that every input sample passes ``check`` against
its own suggestion, over a battery of tricky invocations. The full
input-validation error matrix is exercised with ``assertRaises``.
"""

import os
import sys
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import CliSchemaTool
from agentuniverse.agent.action.tool.common_tool.cli_schema_tool import (
    CliSchemaTool as DirectCliSchemaTool,
)

# --------------------------------------------------------------------- #
# Shared fixtures
# --------------------------------------------------------------------- #

# The grep-like schema used across the check/usage tests.
SCHEMA_MAIN = {
    "program": "grep",
    "arguments": [
        {
            "name": "color", "kind": "flag", "type": "string",
            "choices": ["auto", "always", "never"], "default": "auto",
        },
        {"name": "ignore-case", "kind": "flag", "alias": "i", "has_value": False},
        {
            "name": "count", "kind": "flag", "alias": "c", "type": "int",
            "multiple": True,
        },
        {"name": "pattern", "kind": "positional", "type": "string"},
        {
            "name": "file", "kind": "positional", "type": "path",
            "required": False, "multiple": True,
        },
    ],
}

# One flag per type plus a path positional, for the type battery.
SCHEMA_TYPES = {
    "program": "app",
    "arguments": [
        {"name": "n", "kind": "flag", "type": "int"},
        {"name": "f", "kind": "flag", "type": "float"},
        {"name": "b", "kind": "flag", "type": "bool"},
        {"name": "s", "kind": "flag", "type": "string"},
        {"name": "src", "kind": "positional", "type": "path"},
    ],
}


def _clean(result):
    """Drop the mode echo for terser ground-truth comparisons."""
    return {k: v for k, v in result.items() if k != "mode"}


class TestCheckBasics(unittest.TestCase):
    """check mode: forms, parsing, switches, aliases, missing."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def test_full_passing_invocation(self) -> None:
        result = self.tool.execute(
            mode="check",
            argv=[
                "grep", "--color=always", "-i", "-c", "1", "-c", "2",
                "pat", "a.txt", "b.txt", "--", "--weird",
            ],
            schema=SCHEMA_MAIN,
        )
        self.assertEqual(result, {
            "mode": "check",
            "passed": True,
            "parsed": {
                "color": "always",
                "ignore-case": True,
                "count": [1, 2],
                "pattern": "pat",
                "file": ["a.txt", "b.txt", "--weird"],
            },
            "missing": [],
            "unknown": [],
            "type_mismatches": [],
            "defaults_applied": [],
            "separator_seen": True,
        })

    def test_minimal_invocation_with_defaults(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["/usr/bin/grep", "pat"], schema=SCHEMA_MAIN
        )
        self.assertEqual(_clean(result), {
            "passed": True,
            "parsed": {
                "color": "auto",
                "ignore-case": False,
                "count": [],
                "pattern": "pat",
            },
            "missing": [],
            "unknown": [],
            "type_mismatches": [],
            "defaults_applied": ["color"],
            "separator_seen": False,
        })

    def test_space_and_equals_forms_agree(self) -> None:
        via_space = self.tool.execute(
            mode="check", argv=["grep", "--color", "always", "p"],
            schema=SCHEMA_MAIN,
        )
        via_eq = self.tool.execute(
            mode="check", argv=["grep", "--color=always", "p"],
            schema=SCHEMA_MAIN,
        )
        self.assertEqual(via_space["parsed"]["color"], "always")
        self.assertEqual(via_eq["parsed"]["color"], "always")
        self.assertTrue(via_space["passed"] and via_eq["passed"])

    def test_alias_space_and_equals_forms(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["grep", "-c=7", "p"], schema=SCHEMA_MAIN
        )
        self.assertEqual(result["parsed"]["count"], [7])
        result = self.tool.execute(
            mode="check", argv=["grep", "-c", "7", "p"], schema=SCHEMA_MAIN
        )
        self.assertEqual(result["parsed"]["count"], [7])

    def test_absent_switch_parses_false(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["grep", "p"], schema=SCHEMA_MAIN
        )
        self.assertIs(result["parsed"]["ignore-case"], False)
        self.assertEqual(result["defaults_applied"], ["color"])

    def test_missing_required_flag_and_positional(self) -> None:
        schema = {
            "program": "app",
            "arguments": [
                {"name": "out", "kind": "flag", "type": "string", "required": True},
                {"name": "src", "kind": "positional", "type": "string"},
            ],
        }
        result = self.tool.execute(
            mode="check", argv=["app"], schema=schema
        )
        self.assertEqual(result["missing"], ["out", "src"])
        self.assertFalse(result["passed"])

    def test_required_flag_with_bad_value_is_not_missing(self) -> None:
        schema = {
            "program": "app",
            "arguments": [
                {"name": "n", "kind": "flag", "type": "int", "required": True},
            ],
        }
        result = self.tool.execute(
            mode="check", argv=["app", "--n", "xyz"], schema=schema
        )
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["type_mismatches"], [
            {"name": "n", "expected": "int", "got": "xyz"},
        ])
        self.assertFalse(result["passed"])

    def test_valueless_flag_at_end_is_missing(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "color", "kind": "flag", "type": "string"},
            {"name": "pattern", "kind": "positional", "type": "string"},
        ]}
        # The space form consumes the next value-ish token — so the
        # single 'p' becomes the flag value and the positional is left
        # missing.
        result = self.tool.execute(
            mode="check", argv=["app", "--color", "p"], schema=schema
        )
        self.assertEqual(_clean(result), {
            "passed": False,
            "parsed": {"color": "p"},
            "missing": ["pattern"], "unknown": [], "type_mismatches": [],
            "defaults_applied": [], "separator_seen": False,
        })
        # A value flag with no value at all.
        schema = {"program": "app", "arguments": [
            {"name": "lim", "kind": "flag", "type": "int"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--lim"], schema=schema
        )
        self.assertEqual(result["missing"], ["lim"])
        self.assertFalse(result["passed"])

    def test_valueless_flag_falls_back_to_default(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "lim", "kind": "flag", "type": "int", "default": 10},
            {"name": "x", "kind": "flag", "has_value": False},
        ]}
        # At the end of argv.
        result = self.tool.execute(
            mode="check", argv=["app", "--lim"], schema=schema
        )
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["parsed"]["lim"], 10)
        self.assertEqual(result["defaults_applied"], ["lim"])
        self.assertTrue(result["passed"])
        # Before a flag-like token.
        result = self.tool.execute(
            mode="check", argv=["app", "--lim", "--x"], schema=schema
        )
        self.assertEqual(result["parsed"]["lim"], 10)
        self.assertTrue(result["passed"])
        # Before the -- terminator.
        result = self.tool.execute(
            mode="check", argv=["app", "--lim", "--"], schema=schema
        )
        self.assertEqual(result["parsed"]["lim"], 10)
        self.assertTrue(result["passed"])
        # A collected value beats the default fallback.
        result = self.tool.execute(
            mode="check", argv=["app", "--lim", "3"], schema=schema
        )
        self.assertEqual(result["parsed"]["lim"], 3)
        self.assertEqual(result["defaults_applied"], [])

    def test_switch_with_equals_value_is_unknown(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "v", "kind": "flag", "has_value": False},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--v=1"], schema=schema
        )
        self.assertEqual(result["unknown"], ["--v=1"])
        self.assertFalse(result["passed"])

    def test_repeated_flag_last_wins_and_multiple_collects(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "one", "kind": "flag", "type": "int"},
            {"name": "many", "kind": "flag", "type": "int", "multiple": True},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--one", "1", "--one", "2"], schema=schema
        )
        self.assertEqual(result["parsed"]["one"], 2)
        result = self.tool.execute(
            mode="check",
            argv=["app", "--many", "1", "--many", "2", "--many", "3"],
            schema=schema,
        )
        self.assertEqual(result["parsed"]["many"], [1, 2, 3])
        # A bad occurrence is reported but does not poison the list.
        result = self.tool.execute(
            mode="check", argv=["app", "--many", "1", "--many", "x"],
            schema=schema,
        )
        self.assertEqual(result["parsed"]["many"], [1])
        self.assertEqual(result["type_mismatches"], [
            {"name": "many", "expected": "int", "got": "x"},
        ])

    def test_repeated_switch_multiple_collects_trues(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "v", "kind": "flag", "has_value": False, "multiple": True},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--v", "--v"], schema=schema
        )
        self.assertEqual(result["parsed"]["v"], [True, True])
        result = self.tool.execute(mode="check", argv=["app"], schema=schema)
        self.assertEqual(result["parsed"]["v"], [])


class TestCheckTypesAndChoices(unittest.TestCase):
    """check mode: family type coercion and choices membership."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def test_int_accepts_and_rejects(self) -> None:
        ok = self.tool.execute(
            mode="check", argv=["app", "--n", "42", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(ok["parsed"]["n"], 42)
        ok = self.tool.execute(
            mode="check", argv=["app", "--n=+7", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(ok["parsed"]["n"], 7)
        bad = self.tool.execute(
            mode="check", argv=["app", "--n", "3.5", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "n", "expected": "int", "got": "3.5"},
        ])
        bad = self.tool.execute(
            mode="check", argv=["app", "--n", "", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "n", "expected": "int", "got": ""},
        ])

    def test_float_accepts_scientific_and_negative(self) -> None:
        ok = self.tool.execute(
            mode="check", argv=["app", "--f=-2.5e3", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(ok["parsed"]["f"], -2500.0)
        ok = self.tool.execute(
            mode="check", argv=["app", "--f", ".5", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(ok["parsed"]["f"], 0.5)
        bad = self.tool.execute(
            mode="check", argv=["app", "--f", "1,5", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "f", "expected": "float", "got": "1,5"},
        ])

    def test_bool_words_case_insensitive(self) -> None:
        for token, expected in [
            ("yes", True), ("FALSE", False), ("1", True), ("0", False),
            ("True", True), ("no", False),
        ]:
            result = self.tool.execute(
                mode="check", argv=["app", "--b", token, "-"],
                schema=SCHEMA_TYPES,
            )
            self.assertEqual(result["parsed"]["b"], expected)
        bad = self.tool.execute(
            mode="check", argv=["app", "--b", "maybe", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "b", "expected": "bool", "got": "maybe"},
        ])

    def test_string_accepts_anything_including_empty(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["app", "--s=", "-"], schema=SCHEMA_TYPES
        )
        self.assertEqual(result["parsed"]["s"], "")
        self.assertTrue(result["passed"])

    def test_path_requires_content_without_controls(self) -> None:
        bad = self.tool.execute(
            mode="check", argv=["app", "--s", "x", ""], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "src", "expected": "path", "got": ""},
        ])
        bad = self.tool.execute(
            mode="check", argv=["app", "--s", "x", "a\nb"], schema=SCHEMA_TYPES
        )
        self.assertEqual(bad["type_mismatches"], [
            {"name": "src", "expected": "path", "got": "a\nb"},
        ])
        ok = self.tool.execute(
            mode="check", argv=["app", "--s", "x", "/tmp/ok file.txt"],
            schema=SCHEMA_TYPES,
        )
        self.assertEqual(ok["parsed"]["src"], "/tmp/ok file.txt")

    def test_flag_choices_violation(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["grep", "--color", "maybe", "p"],
            schema=SCHEMA_MAIN,
        )
        self.assertEqual(result["type_mismatches"], [{
            "name": "color",
            "expected": "one of: auto, always, never",
            "got": "maybe",
        }])
        self.assertFalse(result["passed"])

    def test_positional_choices_violation(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "fmt", "kind": "positional", "type": "string",
             "choices": ["json", "yaml"]},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "xml"], schema=schema
        )
        self.assertEqual(result["type_mismatches"], [{
            "name": "fmt", "expected": "one of: json, yaml", "got": "xml",
        }])

    def test_choices_checked_on_raw_token_before_coercion(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "n", "kind": "flag", "type": "int",
             "choices": ["1", "2", "3"]},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--n", "1"], schema=schema
        )
        self.assertEqual(result["parsed"]["n"], 1)
        result = self.tool.execute(
            mode="check", argv=["app", "--n", "4"], schema=schema
        )
        self.assertEqual(result["type_mismatches"], [{
            "name": "n", "expected": "one of: 1, 2, 3", "got": "4"},
        ])


class TestCheckEdgeCases(unittest.TestCase):
    """check mode: --, negative numbers, bundles, program matching."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def test_separator_overflow_goes_to_args(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "src", "kind": "positional", "type": "string"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "src", "--", "-x", "y"], schema=schema
        )
        self.assertEqual(_clean(result), {
            "passed": True,
            "parsed": {"src": "src", "_args": ["-x", "y"]},
            "missing": [], "unknown": [], "type_mismatches": [],
            "defaults_applied": [], "separator_seen": True,
        })

    def test_second_separator_is_data(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "src", "kind": "positional", "type": "string"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "src", "--", "--"], schema=schema
        )
        self.assertEqual(result["parsed"]["_args"], ["--"])
        self.assertTrue(result["passed"])

    def test_separator_without_rest_has_no_args_key(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "src", "kind": "positional", "type": "string"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "src", "--"], schema=schema
        )
        self.assertNotIn("_args", result["parsed"])
        self.assertTrue(result["separator_seen"])
        self.assertTrue(result["passed"])

    def test_pre_separator_overflow_is_unknown(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "src", "kind": "positional", "type": "string"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "src", "extra"], schema=schema
        )
        self.assertEqual(result["unknown"], ["extra"])
        self.assertFalse(result["passed"])

    def test_multiple_positional_consumes_rest_including_after_separator(
        self,
    ) -> None:
        result = self.tool.execute(
            mode="check",
            argv=["grep", "pat", "a", "b", "--", "-c"],
            schema=SCHEMA_MAIN,
        )
        self.assertEqual(result["parsed"]["file"], ["a", "b", "-c"])
        self.assertNotIn("_args", result["parsed"])

    def test_negative_numbers_are_positional(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "off", "kind": "flag", "type": "int"},
            {"name": "num", "kind": "positional", "type": "float"},
        ]}
        for token, value in [("-5", -5.0), ("-3.14", -3.14), ("-.5", -0.5),
                              ("-1e-3", -0.001)]:
            result = self.tool.execute(
                mode="check", argv=["app", token], schema=schema
            )
            self.assertEqual(result["parsed"]["num"], value, token)
        # The lone dash (stdin marker) is positional too (a string slot
        # accepts it; a float slot reports a mismatch, never 'unknown').
        string_schema = {"program": "app", "arguments": [
            {"name": "text", "kind": "positional", "type": "string"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "-"], schema=string_schema
        )
        self.assertEqual(result["unknown"], [])
        self.assertEqual(result["parsed"]["text"], "-")
        result = self.tool.execute(
            mode="check", argv=["app", "-"], schema=schema
        )
        self.assertEqual(result["unknown"], [])
        self.assertEqual(result["type_mismatches"], [
            {"name": "num", "expected": "float", "got": "-"},
        ])

    def test_negative_number_consumed_as_flag_value(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "off", "kind": "flag", "type": "int"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "--off", "-5"], schema=schema
        )
        self.assertEqual(result["parsed"]["off"], -5)
        result = self.tool.execute(
            mode="check", argv=["app", "--off=-5"], schema=schema
        )
        self.assertEqual(result["parsed"]["off"], -5)

    def test_bundle_not_expanded(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "a", "kind": "flag", "alias": "a", "has_value": False},
            {"name": "b", "kind": "flag", "alias": "b", "has_value": False},
            {"name": "c", "kind": "flag", "alias": "c", "has_value": False},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "-abc"], schema=schema
        )
        self.assertEqual(result["unknown"], ["-abc"])
        self.assertFalse(result["passed"])

    def test_multi_character_alias_matches(self) -> None:
        schema = {"program": "ls", "arguments": [
            {"name": "la", "kind": "flag", "alias": "la", "has_value": False},
        ]}
        result = self.tool.execute(
            mode="check", argv=["ls", "-la"], schema=schema
        )
        self.assertIs(result["parsed"]["la"], True)
        self.assertTrue(result["passed"])

    def test_alias_equals_name_matches_both_forms(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "v", "kind": "flag", "alias": "v", "has_value": False},
        ]}
        for token in ("-v", "--v"):
            result = self.tool.execute(
                mode="check", argv=["app", token], schema=schema
            )
            self.assertIs(result["parsed"]["v"], True)

    def test_glued_short_value_is_unknown(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "r", "kind": "flag", "alias": "r", "type": "float"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "-r5"], schema=schema
        )
        self.assertEqual(result["unknown"], ["-r5"])

    def test_program_exact_and_basename_match(self) -> None:
        for program_token in ("grep", "/usr/bin/grep", "./grep"):
            result = self.tool.execute(
                mode="check", argv=[program_token, "p"], schema=SCHEMA_MAIN
            )
            self.assertTrue(result["passed"], program_token)

    def test_program_mismatch_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="check", argv=["ls", "p"], schema=SCHEMA_MAIN
        )
        self.assertEqual(result["mode"], "check")
        self.assertFalse(result["passed"])
        self.assertEqual(result["error"]["type"], "program_mismatch")
        self.assertEqual(result["error"]["expected"], "grep")
        self.assertEqual(result["error"]["got"], "ls")
        self.assertIn("message", result["error"])

    def test_switch_default_true_injected(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "quiet", "kind": "flag", "has_value": False,
             "default": True},
            {"name": "loud", "kind": "flag", "has_value": False},
        ]}
        result = self.tool.execute(mode="check", argv=["app"], schema=schema)
        self.assertEqual(_clean(result), {
            "passed": True,
            "parsed": {"quiet": True, "loud": False},
            "missing": [], "unknown": [], "type_mismatches": [],
            "defaults_applied": ["quiet"], "separator_seen": False,
        })

    def test_positional_optional_with_default(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "src", "kind": "positional", "type": "string"},
            {"name": "dst", "kind": "positional", "type": "string",
             "required": False, "default": "out.txt"},
        ]}
        result = self.tool.execute(
            mode="check", argv=["app", "in.txt"], schema=schema
        )
        self.assertEqual(result["parsed"], {"src": "in.txt", "dst": "out.txt"})
        self.assertEqual(result["defaults_applied"], ["dst"])

    def test_flag_interleaved_with_positionals(self) -> None:
        result = self.tool.execute(
            mode="check",
            argv=["grep", "pat", "--ignore-case", "a.txt"],
            schema=SCHEMA_MAIN,
        )
        self.assertEqual(result["parsed"]["pattern"], "pat")
        self.assertEqual(result["parsed"]["file"], ["a.txt"])
        self.assertIs(result["parsed"]["ignore-case"], True)


class TestUsageMode(unittest.TestCase):
    """usage mode: exact usage line and help text rendering."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def test_usage_line_and_help_text_main(self) -> None:
        result = self.tool.execute(mode="usage", schema=SCHEMA_MAIN)
        self.assertEqual(result["mode"], "usage")
        self.assertEqual(
            result["usage"],
            "grep [--color VALUE] [--ignore-case] [--count VALUE ...] "
            "PATTERN [FILE ...]",
        )
        self.assertEqual(
            result["help_text"],
            "grep [--color VALUE] [--ignore-case] [--count VALUE ...] "
            "PATTERN [FILE ...]\n"
            "\n"
            "arguments:\n"
            "  --color VALUE      (type: string, choices: auto|always|never,"
            " default: auto)\n"
            "  --ignore-case, -i  (type: bool)\n"
            "  --count VALUE, -c  (type: int, multiple)\n"
            "  PATTERN            (type: string, required)\n"
            "  FILE ...           (type: path, multiple)",
        )

    def test_required_flag_rendered_unbracketed(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "out", "kind": "flag", "type": "string",
             "required": True},
            {"name": "force", "kind": "flag", "has_value": False,
             "required": True},
        ]}
        result = self.tool.execute(mode="usage", schema=schema)
        self.assertEqual(result["usage"], "app --out VALUE --force")

    def test_dashed_positional_uppercased_with_dash_kept(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "output-file", "kind": "positional", "type": "path"},
        ]}
        result = self.tool.execute(mode="usage", schema=schema)
        self.assertEqual(result["usage"], "app OUTPUT-FILE")

    def test_help_text_epilog_and_help_lines(self) -> None:
        schema = {
            "program": "convert",
            "arguments": [
                {"name": "input", "kind": "positional", "type": "path",
                 "help": "source file"},
                {"name": "output", "kind": "positional", "type": "path",
                 "required": False, "default": "out.png",
                 "help": "destination file"},
                {"name": "quality", "kind": "flag", "alias": "q",
                 "type": "int", "default": 92, "help": "JPEG quality"},
                {"name": "verbose", "kind": "flag", "alias": "v",
                 "has_value": False},
            ],
            "epilog": "Run 'convert --help' for all options.",
        }
        result = self.tool.execute(mode="usage", schema=schema)
        self.assertEqual(
            result["usage"],
            "convert [--quality VALUE] [--verbose] INPUT [OUTPUT]",
        )
        self.assertEqual(
            result["help_text"],
            "convert [--quality VALUE] [--verbose] INPUT [OUTPUT]\n"
            "\n"
            "arguments:\n"
            "  INPUT                source file (type: path, required)\n"
            "  OUTPUT               destination file (type: path,"
            " default: out.png)\n"
            "  --quality VALUE, -q  JPEG quality (type: int, default: 92)\n"
            "  --verbose, -v        (type: bool)\n"
            "\n"
            "Run 'convert --help' for all options.",
        )

    def test_default_rendering_scalars_and_lists(self) -> None:
        schema = {"program": "app", "arguments": [
            {"name": "i", "kind": "flag", "type": "int", "default": 3},
            {"name": "f", "kind": "flag", "type": "float", "default": 1.5},
            {"name": "b", "kind": "flag", "type": "bool", "default": True},
            {"name": "m", "kind": "flag", "type": "string", "multiple": True,
             "default": ["a", "b"]},
            {"name": "sw", "kind": "flag", "has_value": False,
             "default": False},
        ]}
        result = self.tool.execute(mode="usage", schema=schema)
        self.assertIn("default: 3", result["help_text"])
        self.assertIn("default: 1.5", result["help_text"])
        self.assertIn("default: true", result["help_text"])
        self.assertIn("default: [a, b]", result["help_text"])
        # A False switch default is the implicit behavior — not rendered.
        self.assertNotIn("default: false", result["help_text"])

    def test_no_arguments_schema(self) -> None:
        schema = {"program": "date"}
        result = self.tool.execute(mode="usage", schema=schema)
        self.assertEqual(result["usage"], "date")
        self.assertEqual(result["help_text"], "date")

    def test_arguments_key_optional_and_empty(self) -> None:
        result = self.tool.execute(
            mode="usage", schema={"program": "date", "arguments": []}
        )
        self.assertEqual(result["usage"], "date")
        self.assertEqual(result["help_text"], "date")


class TestSuggestedSchema(unittest.TestCase):
    """suggested_schema mode: merge heuristics and round-trip safety."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def test_merge_across_samples(self) -> None:
        samples = [
            ["grep", "--color", "auto", "-i", "pat", "a.txt"],
            ["grep", "--color=always", "--count", "3", "pat"],
            ["grep", "-c", "1", "-c", "2", "--", "--dash-file"],
            ["/usr/bin/grep", "-i", "pat", "x", "y", "z"],
        ]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        self.assertEqual(result["program"], "grep")
        self.assertEqual(result["notes"], [])
        self.assertEqual(result["schema"], {
            "program": "grep",
            "arguments": [
                {"name": "color", "kind": "flag", "type": "string",
                 "required": False, "has_value": True,
                 "choices": ["auto", "always"]},
                {"name": "i", "kind": "flag", "type": "string",
                 "required": False, "has_value": True, "alias": "i"},
                {"name": "count", "kind": "flag", "type": "int",
                 "required": False, "has_value": True},
                {"name": "c", "kind": "flag", "type": "int",
                 "required": False, "has_value": True, "alias": "c",
                 "multiple": True},
                {"name": "arg1", "kind": "positional", "type": "string",
                 "required": True},
                {"name": "arg2", "kind": "positional", "type": "string",
                 "required": False},
                {"name": "arg3", "kind": "positional", "type": "string",
                 "required": False, "multiple": True},
            ],
        })

    def test_round_trip_battery(self) -> None:
        samples = [
            ["app", "--mode", "fast", "-v", "in.txt"],
            ["app", "--mode=slow", "--tag", "a", "--tag", "b", "x", "y"],
            ["app", "-5", "-"],
            ["app", "src", "--", "--flag", "-n", "val"],
            ["app", "--empty=", "f"],
            ["app", "--off", "-1e-3", "src"],
            ["app", "-la", "file"],
            ["app", "--on", "yes", "--off2", "0"],
            ["/usr/local/bin/app", "only-positional"],
            ["app"],
        ]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        for sample in samples:
            verdict = self.tool.execute(
                mode="check", argv=sample, schema=result["schema"]
            )
            self.assertTrue(
                verdict["passed"],
                f"{sample} failed against {result['schema']}: {verdict}",
            )

    def test_mixed_without_equals_infers_switch(self) -> None:
        samples = [["app", "-v", "file1"], ["app", "-v"]]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        self.assertEqual(result["schema"]["arguments"], [
            {"name": "v", "kind": "flag", "type": "bool", "required": True,
             "has_value": False, "alias": "v"},
            {"name": "arg1", "kind": "positional", "type": "string",
             "required": False},
        ])
        self.assertEqual(len(result["notes"]), 1)
        self.assertIn("--v", result["notes"][0])
        for sample in samples:
            self.assertTrue(self.tool.execute(
                mode="check", argv=sample, schema=result["schema"]
            )["passed"])

    def test_mixed_with_equals_infers_default(self) -> None:
        samples = [["app", "--mode=x", "file"], ["app", "--mode"]]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        self.assertEqual(result["schema"]["arguments"], [
            {"name": "mode", "kind": "flag", "type": "string",
             "required": False, "has_value": True, "default": "x"},
            {"name": "arg1", "kind": "positional", "type": "string",
             "required": False},
        ])
        self.assertEqual(len(result["notes"]), 1)
        for sample in samples:
            self.assertTrue(self.tool.execute(
                mode="check", argv=sample, schema=result["schema"]
            )["passed"])

    def test_rescue_default_is_coerced_to_inferred_type(self) -> None:
        samples = [["app", "--n=5"], ["app", "--n"]]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        mode_arg = result["schema"]["arguments"][0]
        self.assertEqual(mode_arg["type"], "int")
        self.assertEqual(mode_arg["default"], 5)
        for sample in samples:
            self.assertTrue(self.tool.execute(
                mode="check", argv=sample, schema=result["schema"]
            )["passed"])

    def test_type_inference_matrix(self) -> None:
        cases = [
            (["t", "--a", "1", "--a", "2"], "int"),
            (["t", "--a", "1", "--a", "2.5"], "float"),
            (["t", "--a", ".5", "--a", "1e3"], "float"),
            (["t", "--a", "yes", "--a", "0"], "bool"),
            (["t", "--a", "x", "--a", "y"], "string"),
            (["t", "--a", "1", "--a", "b"], "string"),
        ]
        for samples, expected in cases:
            result = self.tool.execute(mode="suggested_schema", samples=[samples])
            self.assertEqual(
                result["schema"]["arguments"][0]["type"], expected, samples
            )

    def test_choices_inference_two_and_three_distinct(self) -> None:
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--c", "auto"], ["t", "--c", "always"],
        ])
        self.assertEqual(
            result["schema"]["arguments"][0]["choices"], ["auto", "always"]
        )
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--c", "a"], ["t", "--c", "b"], ["t", "--c", "c"],
        ])
        self.assertEqual(
            result["schema"]["arguments"][0]["choices"], ["a", "b", "c"]
        )

    def test_no_choices_for_four_distinct_or_non_string(self) -> None:
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--c", "a"], ["t", "--c", "b"], ["t", "--c", "c"],
            ["t", "--c", "d"],
        ])
        self.assertNotIn("choices", result["schema"]["arguments"][0])
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--c", "1"], ["t", "--c", "2"],
        ])
        self.assertNotIn("choices", result["schema"]["arguments"][0])

    def test_required_and_multiple_inference(self) -> None:
        samples = [
            ["t", "--always", "1", "--dup", "a", "--dup", "b", "s1"],
            ["t", "--always", "2", "--dup", "c", "s2"],
        ]
        result = self.tool.execute(mode="suggested_schema", samples=samples)
        # dup appears in EVERY sample (required) and repeats within the
        # first one (multiple); its 3 distinct string values give choices.
        self.assertEqual(result["schema"]["arguments"], [
            {"name": "always", "kind": "flag", "type": "int",
             "required": True, "has_value": True},
            {"name": "dup", "kind": "flag", "type": "string",
             "required": True, "has_value": True, "multiple": True,
             "choices": ["a", "b", "c"]},
            {"name": "arg1", "kind": "positional", "type": "string",
             "required": True, "choices": ["s1", "s2"]},
        ])
        # An argument missing from one sample is not required.
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--sometimes", "1", "x"], ["t", "x"],
        ])
        args = {arg["name"]: arg for arg in result["schema"]["arguments"]}
        self.assertFalse(args["sometimes"]["required"])

    def test_short_only_tokens_become_aliased_names(self) -> None:
        # Short-only tokens that never carry a value become switches
        # whose name IS the alias (so -la and -v both keep matching).
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["ls", "-la"], ["ls", "-v"],
        ])
        self.assertEqual(result["schema"]["arguments"], [
            {"name": "la", "kind": "flag", "type": "bool",
             "required": False, "has_value": False, "alias": "la"},
            {"name": "v", "kind": "flag", "type": "bool",
             "required": False, "has_value": False, "alias": "v"},
        ])
        # A short token followed by a bare value infers a value flag.
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["ls", "-la", "dir"],
        ])
        self.assertEqual(result["schema"]["arguments"][0], {
            "name": "la", "kind": "flag", "type": "string",
            "required": True, "has_value": True, "alias": "la",
        })
        self.assertTrue(self.tool.execute(
            mode="check", argv=["ls", "-la", "dir"],
            schema=result["schema"],
        )["passed"])

    def test_program_taken_from_basename_and_disagreement_rejected(self) -> None:
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["/usr/bin/grep", "p"], ["grep", "q"],
        ])
        self.assertEqual(result["program"], "grep")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="suggested_schema", samples=[
                ["grep", "p"], ["find", "q"],
            ])

    def test_program_only_sample(self) -> None:
        result = self.tool.execute(
            mode="suggested_schema", samples=[["app"]]
        )
        self.assertEqual(
            result["schema"], {"program": "app", "arguments": []}
        )
        self.assertTrue(self.tool.execute(
            mode="check", argv=["app"], schema=result["schema"]
        )["passed"])

    def test_positional_type_inference(self) -> None:
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "1", "x"], ["t", "2", "y"],
        ])
        args = result["schema"]["arguments"]
        self.assertEqual(args[0]["type"], "int")
        self.assertEqual(args[1]["type"], "string")
        self.assertTrue(args[0]["required"])
        self.assertTrue(args[1]["required"])

    def test_flag_name_collision_with_positional_slot(self) -> None:
        # A long flag literally named --arg1 forces the first inferred
        # positional slot to rename itself.
        result = self.tool.execute(mode="suggested_schema", samples=[
            ["t", "--arg1", "v", "pos1"], ["t", "pos1"],
        ])
        names = [arg["name"] for arg in result["schema"]["arguments"]]
        self.assertEqual(len(names), len(set(names)))
        verdict = self.tool.execute(
            mode="check", argv=["t", "--arg1", "v", "pos1"],
            schema=result["schema"],
        )
        self.assertTrue(verdict["passed"])


class TestInputValidation(unittest.TestCase):
    """The strict ValueError matrix (raised before any computation)."""

    def setUp(self) -> None:
        self.tool = CliSchemaTool()

    def _check(self, **kwargs) -> None:
        self.tool.execute(mode=kwargs.pop("mode", "check"), **kwargs)

    def test_unknown_mode(self) -> None:
        for mode in (None, "parse", "validate", 1):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, argv=["a"], schema={"program": "a"})

    def test_mode_parameter_presence_matrix(self) -> None:
        schema = {"program": "app"}
        with self.assertRaises(ValueError):
            self._check(argv=["app"], schema=None)
        with self.assertRaises(ValueError):
            self._check(argv=None, schema=schema)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="suggested_schema", samples=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema=schema, argv=["app"])
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema=schema, samples=[["app"]])
        with self.assertRaises(ValueError):
            self._check(argv=["app"], schema=schema, samples=[["app"]])
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="suggested_schema", samples=[["app"]], argv=["app"]
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="suggested_schema", samples=[["app"]], schema=schema
            )

    def test_argv_malformed(self) -> None:
        schema = {"program": "app"}
        for argv in (None, "app", 5, True, [], [""], [1], [True],
                     ["app", "a\x00b"], ["app", 3]):
            with self.assertRaises(ValueError, msg=repr(argv)):
                self._check(argv=argv, schema=schema)

    def test_samples_malformed(self) -> None:
        for samples in (None, "x", 5, [], [[]], ["app"], [["app"], []],
                        [["app", 1]], "app"):
            with self.assertRaises(ValueError, msg=repr(samples)):
                self.tool.execute(
                    mode="suggested_schema", samples=samples
                )

    def test_samples_over_limit(self) -> None:
        samples = [["app"]] * 201
        with self.assertRaises(ValueError):
            self.tool.execute(mode="suggested_schema", samples=samples)

    def test_schema_malformed(self) -> None:
        for schema in (None, [], "x", 5, True):
            with self.assertRaises(ValueError, msg=repr(schema)):
                self.tool.execute(mode="usage", schema=schema)

    def test_unknown_schema_key(self) -> None:
        with self.assertRaises(ValueError):
            self._check(
                argv=["app"], schema={"program": "app", "foo": 1}
            )

    def test_program_malformed(self) -> None:
        for program in (None, 5, True, "", "a b", "a\tb", "a\nb", "a\x1fb",
                        "x" * 201):
            with self.assertRaises(ValueError, msg=repr(program)):
                self.tool.execute(
                    mode="usage", schema={"program": program}
                )

    def test_epilog_malformed(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="usage", schema={"program": "app", "epilog": 5}
            )

    def test_arguments_malformed(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="usage", schema={"program": "app", "arguments": "flags"}
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="usage", schema={"program": "app", "arguments": ["x"]}
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="usage",
                schema={"program": "app",
                        "arguments": [{"name": f"a{i}", "kind": "flag"}
                                      for i in range(101)]},
            )

    def test_argument_name_and_kind_malformed(self) -> None:
        base = {"program": "app", "arguments": [{}]}
        for name in (None, 5, True, "", "1abc", "-x", "_args", "a b",
                     "x" * 65):
            with self.assertRaises(ValueError, msg=repr(name)):
                self.tool.execute(
                    mode="usage",
                    schema={"program": "app",
                            "arguments": [{"name": name, "kind": "flag"}]},
                )
        with self.assertRaises(ValueError):
            self.tool.execute(mode=base["mode"] if "mode" in base else "usage",
                              schema={"program": "app",
                                      "arguments": [{"name": "a"}]})
        for kind in (None, "option", "opt", 5):
            with self.assertRaises(ValueError, msg=repr(kind)):
                self.tool.execute(
                    mode="usage",
                    schema={"program": "app",
                            "arguments": [{"name": "a", "kind": kind}]},
                )

    def test_duplicate_names_and_aliases(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [
                    {"name": "a", "kind": "flag"},
                    {"name": "a", "kind": "flag"},
                ]})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [
                    {"name": "x", "kind": "flag", "alias": "v"},
                    {"name": "y", "kind": "flag", "alias": "v"},
                ]})
        # An alias colliding with ANOTHER argument's name is rejected;
        # alias == own name is allowed (short-only flags).
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [
                    {"name": "v", "kind": "flag"},
                    {"name": "y", "kind": "flag", "alias": "v"},
                ]})

    def test_alias_malformed(self) -> None:
        for alias in (5, True, "", "1a", "-x", "a b", "x" * 65):
            with self.assertRaises(ValueError, msg=repr(alias)):
                self.tool.execute(mode="usage", schema={"program": "app",
                    "arguments": [{"name": "a", "kind": "flag",
                                   "alias": alias}]})

    def test_positional_cannot_have_flag_fields(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "p", "kind": "positional",
                               "alias": "p"}]})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "p", "kind": "positional",
                               "has_value": False}]})

    def test_type_and_switch_constraints(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag", "type": "num"}]})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag",
                               "has_value": False, "type": "int"}]})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag",
                               "has_value": False, "choices": ["x"]}]})

    def test_boolean_fields_malformed(self) -> None:
        for field in ("required", "multiple", "has_value"):
            with self.assertRaises(ValueError, msg=field):
                self.tool.execute(mode="usage", schema={"program": "app",
                    "arguments": [{"name": "a", "kind": "flag",
                                   field: "yes"}]})

    def test_choices_malformed(self) -> None:
        for choices in ("x", 5, [], [1], [True], ["a", "a"], list(range(51)),
                        [["a"]]):
            with self.assertRaises(ValueError, msg=repr(choices)):
                self.tool.execute(mode="usage", schema={"program": "app",
                    "arguments": [{"name": "a", "kind": "flag",
                                   "choices": choices}]})

    def test_default_type_mismatch_matrix(self) -> None:
        cases = [
            ({"name": "a", "kind": "flag", "type": "string", "default": 3}),
            ({"name": "a", "kind": "flag", "type": "string", "default": True}),
            ({"name": "a", "kind": "flag", "type": "int", "default": "3"}),
            ({"name": "a", "kind": "flag", "type": "int", "default": True}),
            ({"name": "a", "kind": "flag", "type": "int", "default": 1.5}),
            ({"name": "a", "kind": "flag", "type": "float", "default": "x"}),
            ({"name": "a", "kind": "flag", "type": "bool", "default": "true"}),
            ({"name": "a", "kind": "flag", "type": "bool", "default": 1}),
            ({"name": "p", "kind": "positional", "type": "path",
             "required": False, "default": ""}),
            ({"name": "p", "kind": "positional", "type": "path",
             "required": False, "default": "a\nb"}),
            ({"name": "p", "kind": "positional", "type": "path",
             "required": False, "default": 5}),
        ]
        for arg in cases:
            with self.assertRaises(ValueError, msg=repr(arg)):
                self.tool.execute(mode="usage",
                                  schema={"program": "app",
                                          "arguments": [arg]})

    def test_default_not_in_choices(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag",
                               "choices": ["x", "y"], "default": "z"}]})

    def test_required_with_default_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag", "required": True,
                               "default": "x"}]})
        # Positionals are required by default, so this too is rejected.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "p", "kind": "positional",
                               "default": "x"}]})

    def test_multiple_default_must_be_list(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag", "multiple": True,
                               "default": "x"}]})
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag", "multiple": True,
                               "default": [1]}]})

    def test_multiple_positional_must_be_last(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [
                    {"name": "p1", "kind": "positional", "multiple": True},
                    {"name": "p2", "kind": "positional"},
                ]})
        # Last position is fine.
        result = self.tool.execute(mode="usage", schema={"program": "app",
            "arguments": [
                {"name": "p1", "kind": "positional"},
                {"name": "p2", "kind": "positional", "required": False,
                 "multiple": True},
            ]})
        self.assertEqual(result["usage"], "app P1 [P2 ...]")

    def test_help_malformed(self) -> None:
        for help_text in (5, True, "a\nb", "x" * 201):
            with self.assertRaises(ValueError, msg=repr(help_text)):
                self.tool.execute(mode="usage", schema={"program": "app",
                    "arguments": [{"name": "a", "kind": "flag",
                                   "help": help_text}]})

    def test_unknown_argument_key(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="usage", schema={"program": "app",
                "arguments": [{"name": "a", "kind": "flag", "metavar": "X"}]})

    def test_argv_caps(self) -> None:
        schema = {"program": "app"}
        with self.assertRaises(ValueError):
            self._check(argv=["app"] + ["x"] * 10_000, schema=schema)
        with self.assertRaises(ValueError):
            self._check(argv=["app", "y" * 100_001], schema=schema)


class TestConfiguration(unittest.TestCase):
    """The packaged yaml configuration matches the module."""

    def test_yaml_config(self) -> None:
        module_dir = os.path.dirname(os.path.abspath(sys.modules[
            CliSchemaTool.__module__
        ].__file__))
        path = os.path.join(module_dir, "cli_schema_tool.yaml")
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "cli_schema_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["metadata"]["class"], "CliSchemaTool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.cli_schema_tool",
        )
        self.assertEqual(config["input_keys"], ["mode"])

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(DirectCliSchemaTool, CliSchemaTool)

    def test_tool_metadata(self) -> None:
        tool = CliSchemaTool()
        self.assertEqual(tool.name, "cli_schema_tool")
        self.assertIn("check", tool.description)
        self.assertIn("usage", tool.description)
        self.assertIn("suggested_schema", tool.description)


if __name__ == "__main__":
    unittest.main()
