#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_semver_tool.py

"""Offline unit tests for SemverTool.

The tool implements Semantic Versioning 2.0.0 purely on the standard
library and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: parsing is checked against
the valid/invalid example lists published on semver.org, precedence
against the spec §11 ordering list (1.0.0-alpha < 1.0.0-alpha.1 <
1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 <
1.0.0-rc.1 < 1.0.0), bumping against a fixed matrix including the
prerelease handling rules, and ranges against npm/node-semver tilde /
caret / comparator ground truths including prerelease gating.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SemverTool
from agentuniverse.agent.action.tool.common_tool.semver_tool import (
    SemverTool as DirectSemverTool,
)

# --------------------------------------------------------------------- #
# semver.org ground truths
# --------------------------------------------------------------------- #

# Valid examples from https://semver.org (FAQ "is this a valid
# semantic version" list) plus spec §9 grammar examples.
VALID_VERSIONS = [
    "0.0.4",
    "1.1.7",
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-alpha.beta",
    "1.0.0-beta.2",
    "1.0.0-beta.11",
    "1.0.0-rc.1",
    "1.0.0-alpha+001",
    "1.0.0+20130313144700",
    "1.0.0-beta+exp.sha.5114f85",
    "0.0.0",
    "10.20.30",
    "1.2.3-0.3.7",            # spec §9 example
    "1.2.3-x.7.z.92",         # spec §9 example
    "1.2.3-0",                # single numeric prerelease identifier
    "1.2.3-RC-1",             # uppercase + hyphen inside an identifier
    "1.2.3-00a1",             # alphanumeric ids may carry leading zeroes
    "1.2.3+007",              # numeric build ids may carry leading zeroes
    "1.2.3+build-1-a.1",      # hyphens inside build identifiers
]

# Invalid examples: (version, keyword expected in the error message).
# The first entries mirror the semver.org invalid list; every message
# cites the violated spec rule.
INVALID_VERSIONS = [
    ("1.2", "three dot-separated"),
    ("1", "three dot-separated"),
    ("1.2.3.4", "three dot-separated"),
    ("01.2.3", "major version MUST NOT contain leading zeroes"),
    ("1.02.3", "minor version MUST NOT contain leading zeroes"),
    ("1.2.03", "patch version MUST NOT contain leading zeroes"),
    ("1.2.3-0123", "leading zeroes"),
    ("1.2.3-0123.0123", "leading zeroes"),
    ("1.2.3-", "pre-release version MUST NOT be empty"),
    ("1.1.2+.123", "non-empty"),
    ("1.2.3+", "build metadata MUST NOT be empty"),
    ("1.2.3-a..b", "non-empty"),
    ("1.2.3-a.", "non-empty"),
    ("+invalid", "three dot-separated"),
    ("-invalid", "three dot-separated"),
    ("-invalid+invalid", "three dot-separated"),
    ("-invalid.01", "leading zeroes"),
    ("alpha", "three dot-separated"),
    ("alpha.1", "three dot-separated"),
    ("alpha.beta.1", "major version must be a non-negative integer"),
    ("v1.2.3", "major version must be a non-negative integer"),
    ("1.2.3-é", "ASCII"),
    ("1.2.3+a_1", "ASCII"),
    ("1.2.3+b+c", "build identifiers must comprise only ASCII"),
    (" 1.2.3", "whitespace"),
    ("1.2.3 ", "whitespace"),
    ("1.2.3 beta", "whitespace"),
]

# Spec §11 precedence ordering, lowest to highest.
SPEC_ORDER = [
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-alpha.beta",
    "1.0.0-beta",
    "1.0.0-beta.2",
    "1.0.0-beta.11",
    "1.0.0-rc.1",
    "1.0.0",
]

# (version, level, label, expected result)
BUMP_CASES = [
    # major
    ("1.2.3", "major", None, "2.0.0"),
    ("1.2.3-rc.1", "major", None, "2.0.0"),
    ("0.0.1", "major", None, "1.0.0"),
    ("9.9.9", "major", None, "10.0.0"),
    ("1.2.3+meta", "major", None, "2.0.0"),
    # minor
    ("1.2.3", "minor", None, "1.3.0"),
    ("1.2.3-rc.1", "minor", None, "1.3.0"),
    ("0.1.2", "minor", None, "0.2.0"),
    ("1.2.3+meta.1", "minor", None, "1.3.0"),
    # patch
    ("1.2.3", "patch", None, "1.2.4"),
    ("1.2.9", "patch", None, "1.2.10"),
    ("1.2.3-rc.1", "patch", None, "1.2.4"),
    ("1.2.3-rc.1+build", "patch", None, "1.2.4"),
    # prerelease: start the next patch series (default label rc)
    ("1.2.3", "prerelease", None, "1.2.4-rc.0"),
    ("1.2.3-rc.0", "prerelease", None, "1.2.3-rc.1"),
    ("1.2.3-rc.9", "prerelease", None, "1.2.3-rc.10"),
    ("1.2.3-rc", "prerelease", None, "1.2.3-rc.0"),
    ("1.2.3-rc.1.beta", "prerelease", None, "1.2.3-rc.2.beta"),
    # prerelease: custom labels / channel switching on the same core
    ("1.2.3", "prerelease", "alpha", "1.2.4-alpha.0"),
    ("1.2.3", "prerelease", "0", "1.2.4-0.0"),
    ("1.2.3-beta.2", "prerelease", "beta", "1.2.3-beta.3"),
    ("1.2.3-alpha.1", "prerelease", None, "1.2.3-rc.0"),
    ("1.2.3-0.3", "prerelease", None, "1.2.3-rc.0"),
    ("1.2.3-RC.1", "prerelease", "RC", "1.2.3-RC.2"),
    ("1.2.3-beta.1", "prerelease", "rc", "1.2.3-rc.0"),
    # release: strip the prerelease
    ("1.2.3-rc.1", "release", None, "1.2.3"),
    ("1.2.4-rc.0", "release", None, "1.2.4"),
    ("1.2.3-alpha.beta.1", "release", None, "1.2.3"),
    ("1.2.3-rc.1+build.1", "release", None, "1.2.3"),
]

# (range, version, expected satisfies)
RANGE_CASES = [
    # exact
    ("1.2.3", "1.2.3", True),
    ("1.2.3", "1.2.4", False),
    ("1.2.3", "1.2.3-rc.1", False),      # prerelease gating
    ("=1.2.3", "1.2.3", True),
    ("=1.2.3", "1.2.2", False),
    ("1.2.3+build.7", "1.2.3", True),    # build metadata ignored
    ("1.2.3-rc.1", "1.2.3-rc.1", True),
    ("1.2.3-rc.1", "1.2.3-rc.2", False),
    ("1.2.3-rc.1", "1.2.3", False),
    # comparators
    (">=1.2.3", "1.2.3", True),
    (">=1.2.3", "1.2.2", False),
    (">1.2.3", "1.2.3", False),
    (">1.2.3", "1.2.4", True),
    ("<2.0.0", "1.9.9", True),
    ("<2.0.0", "2.0.0", False),
    ("<2.0.0", "2.0.0-rc.1", False),     # prerelease gating
    ("<=2.0.0", "2.0.0", True),
    ("<=2.0.0", "2.0.1", False),
    (">0.0.0", "0.0.1", True),
    # conjunctions
    (">=1.2.3 <2.0.0", "1.2.3", True),
    (">=1.2.3 <2.0.0", "1.5.0", True),
    (">=1.2.3 <2.0.0", "1.2.2", False),
    (">=1.2.3 <2.0.0", "2.0.0", False),
    (">=1.2.0 <1.3.0", "1.2.99", True),
    (">=1.2.3-alpha <2.0.0", "1.2.3-beta", True),   # same core tuple
    (">=1.2.3-alpha <2.0.0", "1.2.4-alpha", False), # gated: other tuple
    (">=1.2.3-alpha <2.0.0", "1.2.4", True),
    (">=1.2.3-alpha <2.0.0", "1.2.2", False),
    # tilde
    ("~1.2.3", "1.2.3", True),
    ("~1.2.3", "1.2.4", True),
    ("~1.2.3", "1.2.99", True),
    ("~1.2.3", "1.2.2", False),
    ("~1.2.3", "1.3.0", False),
    ("~1.2.3", "1.2.4-beta", False),     # prerelease gating
    ("~1.2", "1.2.0", True),
    ("~1.2", "1.2.9", True),
    ("~1.2", "1.1.9", False),
    ("~1.2", "1.3.0", False),
    ("~1", "1.0.0", True),
    ("~1", "1.9.9", True),
    ("~1", "2.0.0", False),
    ("~1", "0.9.9", False),
    ("~0.2.3", "0.2.5", True),
    ("~0.2.3", "0.3.0", False),
    ("~1.2.3-beta.2", "1.2.3-beta.4", True),
    ("~1.2.3-beta.2", "1.2.3-beta.1", False),
    ("~1.2.3-beta.2", "1.2.3", True),
    ("~1.2.3-beta.2", "1.2.4-beta", False),
    # caret
    ("^1.2.3", "1.2.3", True),
    ("^1.2.3", "1.9.9", True),
    ("^1.2.3", "1.2.2", False),
    ("^1.2.3", "2.0.0", False),
    ("^0.2.3", "0.2.3", True),
    ("^0.2.3", "0.2.9", True),
    ("^0.2.3", "0.3.0", False),
    ("^0.0.3", "0.0.3", True),
    ("^0.0.3", "0.0.4", False),
    ("^0.0.0", "0.0.0", True),
    ("^0.0.0", "0.0.1", False),
    ("^1.2", "1.2.0", True),
    ("^1.2", "1.9.9", True),
    ("^1.2", "1.1.9", False),
    ("^1.2", "2.0.0", False),
    ("^0.2", "0.2.0", True),
    ("^0.2", "0.3.0", False),
    ("^0.0", "0.0.9", True),
    ("^0.0", "0.1.0", False),
    ("^1", "1.0.0", True),
    ("^1", "1.5.3", True),
    ("^1", "2.0.0", False),
    ("^0", "0.0.0", True),
    ("^0", "0.9.9", True),
    ("^0", "1.0.0", False),
    ("^1.2.3-beta.2", "1.2.3-beta.1", False),
    ("^1.2.3-beta.2", "1.2.3-rc.1", True),
    ("^1.2.3-beta.2", "1.5.0", True),
    ("^1.2.3-beta.2", "1.5.0-beta", False),  # prerelease gating
    ("^1.2.3+build", "1.2.4", True),        # build metadata ignored
]

# (range, expected desugared comparator set)
EXPANSION_CASES = [
    ("1.2.3", "1.2.3"),
    ("=1.2.3", "1.2.3"),
    (">=1.2.3", ">=1.2.3"),
    (">=1.2.3 <2.0.0", ">=1.2.3 <2.0.0"),
    ("~1.2.3", ">=1.2.3 <1.3.0"),
    ("~1.2", ">=1.2.0 <1.3.0"),
    ("~1", ">=1.0.0 <2.0.0"),
    ("~1.2.3-beta.2", ">=1.2.3-beta.2 <1.3.0"),
    ("^1.2.3", ">=1.2.3 <2.0.0"),
    ("^0.2.3", ">=0.2.3 <0.3.0"),
    ("^0.0.3", ">=0.0.3 <0.0.4"),
    ("^0.0.0", ">=0.0.0 <0.0.1"),
    ("^1.2", ">=1.2.0 <2.0.0"),
    ("^0.2", ">=0.2.0 <0.3.0"),
    ("^0.0", ">=0.0.0 <0.1.0"),
    ("^1", ">=1.0.0 <2.0.0"),
    ("^0", ">=0.0.0 <1.0.0"),
    ("^1.2.3+build", ">=1.2.3 <2.0.0"),
]

# (range, keyword expected in the invalid_range message)
UNSUPPORTED_RANGES = [
    ("1.2 - 2.3", "hyphen ranges"),
    ("1.2.3 - 2.3.4", "hyphen ranges"),
    (">=1.2 || <1.0.0", "unions"),
    ("1.2.x", "x-ranges"),
    ("1.x", "x-ranges"),
    ("*", "not a supported range"),
    ("latest", "dist-tags"),
    (">=abc", "full X.Y.Z version"),
    (">=1.2", "full X.Y.Z version"),
    ("<1", "full X.Y.Z version"),
    ("~1.2-beta", "pre-release requires a full X.Y.Z"),
    ("^1.2.3.4", "1 to 3 dot-separated"),
    ("~", "non-negative integers"),
    ("^", "non-negative integers"),
    (">", "full X.Y.Z version"),
    ("1.2.3-", "not a supported range"),
    ("~01.2", "non-negative integers"),
    (" ", "contains no comparators"),
]


class SemverToolParseTest(unittest.TestCase):
    """parse mode — strict semver.org validity verdicts."""

    def setUp(self) -> None:
        self.tool = SemverTool()

    def test_valid_semver_org_examples(self) -> None:
        for version in VALID_VERSIONS:
            with self.subTest(version=version):
                result = self.tool.execute(mode="parse", version=version)
                self.assertTrue(result["valid"])
                self.assertNotIn("error", result)
                self.assertEqual(result["mode"], "parse")
                self.assertEqual(result["version"], version)

    def test_parse_full_structure(self) -> None:
        result = self.tool.execute(mode="parse", version="1.2.3-rc.1+build.5")
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "version": "1.2.3-rc.1+build.5",
                "valid": True,
                "major": 1,
                "minor": 2,
                "patch": 3,
                "prerelease": "rc.1",
                "prerelease_identifiers": ["rc", "1"],
                "build": "build.5",
                "build_identifiers": ["build", "5"],
            },
        )

    def test_parse_release_structure(self) -> None:
        result = self.tool.execute(mode="parse", version="2.0.1")
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "version": "2.0.1",
                "valid": True,
                "major": 2,
                "minor": 0,
                "patch": 1,
                "prerelease": "",
                "prerelease_identifiers": [],
                "build": "",
                "build_identifiers": [],
            },
        )

    def test_parse_spec_grammar_example(self) -> None:
        # Spec §9 example identifiers.
        result = self.tool.execute(mode="parse", version="1.2.3-x.7.z.92")
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["prerelease_identifiers"], ["x", "7", "z", "92"]
        )
        self.assertEqual(result["prerelease"], "x.7.z.92")

    def test_invalid_matrix_with_rule_citations(self) -> None:
        for version, keyword in INVALID_VERSIONS:
            with self.subTest(version=version):
                result = self.tool.execute(mode="parse", version=version)
                self.assertFalse(result["valid"])
                self.assertEqual(
                    result["error"]["type"], "invalid_version"
                )
                self.assertIn(keyword, result["error"]["message"])
                # Precise rule citation: spec section number.
                self.assertIn("§", result["error"]["rule"])

    def test_leading_zero_rules_differ_between_prerelease_and_build(
        self,
    ) -> None:
        # Numeric prerelease identifiers: no leading zeroes (§9).
        self.assertFalse(
            self.tool.execute(mode="parse", version="1.2.3-0123")["valid"]
        )
        # Numeric build identifiers MAY carry leading zeroes (§9/§10).
        self.assertTrue(
            self.tool.execute(mode="parse", version="1.2.3+0123")["valid"]
        )
        # Alphanumeric prerelease identifiers may carry leading zeroes.
        self.assertTrue(
            self.tool.execute(mode="parse", version="1.2.3-0123a")["valid"]
        )


class SemverToolCompareTest(unittest.TestCase):
    """compare mode — spec §11 precedence."""

    def setUp(self) -> None:
        self.tool = SemverTool()

    def test_spec_ordering_all_pairs(self) -> None:
        for i, lower in enumerate(SPEC_ORDER):
            for j, higher in enumerate(SPEC_ORDER):
                with self.subTest(lower=lower, higher=higher):
                    result = self.tool.execute(
                        mode="compare", version_a=lower, version_b=higher
                    )
                    expected = -1 if i < j else (1 if i > j else 0)
                    self.assertEqual(result["result"], expected)
                    relation = {(-1): "lt", 0: "eq", 1: "gt"}[expected]
                    self.assertEqual(result["relation"], relation)

    def test_numeric_identifiers_compare_numerically(self) -> None:
        # 2 < 11 numerically (not lexically); contrast 1.0.0-2 < 1.0.0-11.
        result = self.tool.execute(
            mode="compare", version_a="1.0.0-2", version_b="1.0.0-11"
        )
        self.assertEqual(result["result"], -1)
        # Core fields also compare numerically.
        self.assertEqual(
            self.tool.execute(
                mode="compare", version_a="1.10.0", version_b="1.9.99"
            )["result"],
            1,
        )
        self.assertEqual(
            self.tool.execute(
                mode="compare", version_a="1.0.10", version_b="1.0.9"
            )["result"],
            1,
        )
        self.assertEqual(
            self.tool.execute(
                mode="compare",
                version_a="999999999.0.0",
                version_b="1000000000.0.0",
            )["result"],
            -1,
        )

    def test_numeric_identifier_below_alphanumeric(self) -> None:
        result = self.tool.execute(
            mode="compare", version_a="1.0.0-1", version_b="1.0.0-alpha"
        )
        self.assertEqual(result["result"], -1)

    def test_larger_prerelease_set_wins(self) -> None:
        result = self.tool.execute(
            mode="compare", version_a="1.0.0-rc", version_b="1.0.0-rc.0"
        )
        self.assertEqual(result["result"], -1)

    def test_build_metadata_ignored_for_precedence(self) -> None:
        result = self.tool.execute(
            mode="compare", version_a="1.0.0+build.1", version_b="1.0.0+x.2"
        )
        self.assertEqual(result["result"], 0)
        self.assertEqual(result["relation"], "eq")
        self.assertTrue(result["differs_only_in_build_metadata"])
        # Equal strings: no build-only difference to report.
        result = self.tool.execute(
            mode="compare", version_a="1.0.0", version_b="1.0.0"
        )
        self.assertEqual(result["result"], 0)
        self.assertFalse(result["differs_only_in_build_metadata"])
        # Different precedence: flag stays False.
        result = self.tool.execute(
            mode="compare", version_a="1.0.0-rc.1+001", version_b="1.0.0"
        )
        self.assertEqual(result["result"], -1)
        self.assertFalse(result["differs_only_in_build_metadata"])

    def test_compare_invalid_version_payloads(self) -> None:
        for bad_a, bad_b in (("1.2", "1.2.3"), ("1.2.3", "not-a-version")):
            with self.subTest(version_a=bad_a, version_b=bad_b):
                result = self.tool.execute(
                    mode="compare", version_a=bad_a, version_b=bad_b
                )
                self.assertEqual(
                    result["error"]["type"], "invalid_version"
                )
                self.assertIn(
                    result["error"]["which"], ("version_a", "version_b")
                )
                self.assertIn("§", result["error"]["rule"])


class SemverToolBumpTest(unittest.TestCase):
    """bump mode — level matrix and prerelease handling."""

    def setUp(self) -> None:
        self.tool = SemverTool()

    def test_bump_matrix(self) -> None:
        for version, level, label, expected in BUMP_CASES:
            with self.subTest(version=version, level=level, label=label):
                kwargs = {"mode": "bump", "version": version, "level": level}
                if label is not None:
                    kwargs["label"] = label
                result = self.tool.execute(**kwargs)
                self.assertNotIn("error", result)
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["from"], version)
                self.assertEqual(result["level"], level)

    def test_bump_strictly_increases_precedence(self) -> None:
        # Invariant: every successful bump yields a valid version that
        # strictly outranks the input (build metadata is dropped).
        for version, level, label, expected in BUMP_CASES:
            with self.subTest(version=version, level=level):
                parsed = self.tool.execute(mode="parse", version=expected)
                self.assertTrue(parsed["valid"])
                compared = self.tool.execute(
                    mode="compare", version_a=version, version_b=expected
                )
                self.assertEqual(compared["result"], -1)

    def test_prerelease_label_in_context(self) -> None:
        result = self.tool.execute(
            mode="bump", version="1.2.3", level="prerelease"
        )
        self.assertEqual(result["label"], "rc")
        result = self.tool.execute(
            mode="bump", version="1.2.3", level="prerelease", label="alpha"
        )
        self.assertEqual(result["label"], "alpha")
        result = self.tool.execute(
            mode="bump", version="1.2.3", level="patch"
        )
        self.assertNotIn("label", result)

    def test_release_without_prerelease_is_content_error(self) -> None:
        result = self.tool.execute(mode="bump", version="1.2.3", level="release")
        self.assertEqual(result["error"]["type"], "no_prerelease")
        self.assertIn("pre-release", result["error"]["message"])

    def test_bump_invalid_version_payload(self) -> None:
        for version in ("1.2", "01.2.3", "1.2.3-01", "v1.2.3"):
            with self.subTest(version=version):
                result = self.tool.execute(
                    mode="bump", version=version, level="patch"
                )
                self.assertEqual(
                    result["error"]["type"], "invalid_version"
                )


class SemverToolRangeTest(unittest.TestCase):
    """range mode — comparator, tilde and caret ground truths."""

    def setUp(self) -> None:
        self.tool = SemverTool()

    def test_range_matrix(self) -> None:
        for version_range, version, expected in RANGE_CASES:
            with self.subTest(range=version_range, version=version):
                result = self.tool.execute(
                    mode="range", version=version, version_range=version_range
                )
                self.assertNotIn("error", result)
                self.assertIs(result["result"], expected)

    def test_expansion(self) -> None:
        for version_range, expanded in EXPANSION_CASES:
            with self.subTest(range=version_range):
                result = self.tool.execute(
                    mode="range", version="1.2.3", version_range=version_range
                )
                self.assertEqual(result["expanded"], expanded)

    def test_unsupported_range_payloads(self) -> None:
        for version_range, keyword in UNSUPPORTED_RANGES:
            with self.subTest(range=version_range):
                result = self.tool.execute(
                    mode="range", version="1.2.3", version_range=version_range
                )
                self.assertEqual(result["error"]["type"], "invalid_range")
                self.assertIn(keyword, result["error"]["message"])

    def test_range_invalid_version_payload(self) -> None:
        result = self.tool.execute(
            mode="range", version="1.2", version_range="~1.2.3"
        )
        self.assertEqual(result["error"]["type"], "invalid_version")
        self.assertEqual(result["error"]["which"], "version")

    def test_conjunction_whitespace_runs(self) -> None:
        result = self.tool.execute(
            mode="range", version="1.5.0", version_range="  >=1.2.3    <2.0.0  "
        )
        self.assertTrue(result["result"])
        self.assertEqual(result["expanded"], ">=1.2.3 <2.0.0")


class SemverToolValidationTest(unittest.TestCase):
    """ValueError validation for malformed parameters."""

    def setUp(self) -> None:
        self.tool = SemverTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_bad_mode(self) -> None:
        self.assert_invalid(mode="roll", version="1.2.3")
        self.assert_invalid(mode=None, version="1.2.3")

    def test_bad_version_parameters(self) -> None:
        for mode in ("parse", "bump", "range"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, version=None)
                self.assert_invalid(mode=mode, version=123)
                self.assert_invalid(mode=mode, version="")
                self.assert_invalid(mode=mode, version=True)
                self.assert_invalid(mode=mode, version="1." + "0" * 2000)

    def test_bad_compare_parameters(self) -> None:
        self.assert_invalid(mode="compare", version_a="1.2.3")
        self.assert_invalid(mode="compare", version_b="1.2.3")
        self.assert_invalid(mode="compare", version_a=None, version_b="1.2.3")
        self.assert_invalid(mode="compare", version_a="1.2.3", version_b=5)

    def test_bad_bump_parameters(self) -> None:
        self.assert_invalid(mode="bump", version="1.2.3", level=None)
        self.assert_invalid(mode="bump", version="1.2.3", level="build")
        self.assert_invalid(mode="bump", version="1.2.3", level="MAJOR")
        # label is only valid with level='prerelease'.
        self.assert_invalid(
            mode="bump", version="1.2.3", level="patch", label="rc"
        )
        # Malformed labels.
        for label in ("", "rc!", "r c", 7, True, "01", "x" * 65, "rc.beta"):
            with self.subTest(label=label):
                self.assert_invalid(
                    mode="bump",
                    version="1.2.3",
                    level="prerelease",
                    label=label,
                )

    def test_bad_range_parameters(self) -> None:
        self.assert_invalid(mode="range", version="1.2.3", version_range=None)
        self.assert_invalid(mode="range", version="1.2.3", version_range="")
        self.assert_invalid(mode="range", version="1.2.3", version_range=123)
        self.assert_invalid(
            mode="range",
            version="1.2.3",
            version_range=">=1.0.0 " * 150,
        )


class SemverToolExportTest(unittest.TestCase):
    """Package exports and component metadata."""

    def test_export_from_common_tool(self) -> None:
        self.assertIs(SemverTool, DirectSemverTool)

    def test_component_metadata(self) -> None:
        tool = SemverTool()
        self.assertEqual(tool.name, "semver_tool")
        self.assertIn("Semantic versioning", tool.description)
        self.assertEqual(
            SemverTool.MODES, ("parse", "compare", "bump", "range")
        )
        self.assertEqual(
            SemverTool.LEVELS,
            ("major", "minor", "patch", "prerelease", "release"),
        )


if __name__ == "__main__":
    unittest.main()
