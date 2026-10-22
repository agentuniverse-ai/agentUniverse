#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_semver_range_tool.py

"""Offline unit tests for SemverRangeTool.

The tool implements the npm ``node-semver`` range grammar purely on
the standard library and never touches the network, so this suite
runs fully offline. Every assertion is deterministic: satisfaction
is checked against the ground-truth vectors of the npm ranges
documentation — including the notorious caret special cases
(``^0.2.3`` excludes ``0.3.0``, ``^0.0.3`` excludes ``0.0.4``) and
the npm prerelease gating rule (``1.2.3-alpha`` satisfies
``^1.2.3-alpha`` but NOT ``>=1.2.3``) — the ``explain`` expansions
against the desugaring tables npm documents, ``versions`` against a
fixed candidate list, ``intersect`` against hand-merged bounds, and
the error matrix covers both the parameter-level ``ValueError``
inputs and the content-level structured ``error`` payloads with the
0-based character position of the offending range fragment.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SemverRangeTool
from agentuniverse.agent.action.tool.common_tool.semver_range_tool import (
    SemverRangeTool as DirectSemverRangeTool,
)


def run_satisfies(version, version_range):
    return SemverRangeTool().execute(
        mode="satisfies", version=version, version_range=version_range
    )


def run_explain(version_range):
    return SemverRangeTool().execute(mode="explain",
                                     version_range=version_range)


def run_versions(version_range, versions):
    return SemverRangeTool().execute(
        mode="versions", version_range=version_range, versions=versions
    )


def run_intersect(version_range, version_range_b):
    return SemverRangeTool().execute(
        mode="intersect",
        version_range=version_range,
        version_range_b=version_range_b,
    )


# --------------------------------------------------------------------- #
# npm ground truths: (range, version, expected satisfies)
# --------------------------------------------------------------------- #

SATISFIES_VECTORS = [
    # --- caret ranges (npm docs table) ---------------------------- #
    ("^1.2.3", "1.2.3", True),
    ("^1.2.3", "1.9.9", True),
    ("^1.2.3", "2.0.0", False),
    ("^1.2.3", "1.2.2", False),
    # ^0.2.3 excludes 0.3.0 (leftmost-nonzero = minor)
    ("^0.2.3", "0.2.3", True),
    ("^0.2.3", "0.2.9", True),
    ("^0.2.3", "0.3.0", False),
    # ^0.0.3 excludes 0.0.4 (leftmost-nonzero = patch)
    ("^0.0.3", "0.0.3", True),
    ("^0.0.3", "0.0.4", False),
    ("^0.0.3", "0.0.2", False),
    # partial carets
    ("^1.2", "1.2.0", True),
    ("^1.2", "1.9.9", True),
    ("^1.2", "2.0.0", False),
    ("^0.0", "0.0.9", True),
    ("^0.0", "0.1.0", False),
    ("^1", "1.0.0", True),
    ("^1", "1.9.9", True),
    ("^1", "2.0.0", False),
    ("^0", "0.9.9", True),
    ("^0", "1.0.0", False),
    ("^1.x", "1.5.0", True),
    ("^1.x", "2.0.0", False),
    ("^0.x", "0.5.0", True),
    ("^0.x", "1.0.0", False),
    ("^1.2.x", "1.2.9", True),
    ("^1.2.x", "1.3.0", True),   # ^1.2.x -> >=1.2.0 <2.0.0
    ("^0.0.x", "0.0.9", True),
    ("^0.0.x", "0.1.0", False),
    # --- tilde ranges (npm docs table) ---------------------------- #
    ("~1.2.3", "1.2.3", True),
    ("~1.2.3", "1.2.9", True),
    ("~1.2.3", "1.3.0", False),
    ("~1.2.3", "1.2.2", False),
    ("~1.2", "1.2.0", True),
    ("~1.2", "1.2.9", True),
    ("~1.2", "1.3.0", False),
    ("~1", "1.0.0", True),
    ("~1", "1.9.9", True),
    ("~1", "2.0.0", False),
    ("~0.2.3", "0.2.3", True),
    ("~0.2.3", "0.2.9", True),
    ("~0.2.3", "0.3.0", False),
    ("~0.2", "0.2.5", True),
    ("~0.2", "0.3.0", False),
    ("~0", "0.9.9", True),
    ("~0", "1.0.0", False),
    # --- x-ranges -------------------------------------------------- #
    ("1.2.x", "1.2.0", True),
    ("1.2.x", "1.2.9", True),
    ("1.2.x", "1.3.0", False),
    ("1.2.x", "1.2.3-alpha", False),  # prerelease not gated
    ("1.2", "1.2.9", True),
    ("1.2", "1.3.0", False),
    ("1", "1.9.9", True),
    ("1", "2.0.0", False),
    ("1.x.x", "1.5.0", True),
    ("1.X", "1.0.0", True),
    ("*", "0.0.1", True),
    ("*", "99.99.99", True),
    ("x", "5.0.0", True),
    ("*", "1.2.3-alpha", False),  # even '*' rejects ungated prereleases
    ("", "1.2.3", None),  # placeholder: empty range param is rejected
    # --- exact versions -------------------------------------------- #
    ("1.2.3", "1.2.3", True),
    ("1.2.3", "1.2.4", False),
    ("=1.2.3", "1.2.3", True),
    ("=1.2.3", "1.2.3+build", True),  # build metadata ignored
    ("1.2.3", "1.2.3-alpha", False),
    ("v1.2.3", "1.2.3", True),  # leading v stripped in ranges too
    # --- comparison primitives (npm docs) -------------------------- #
    (">1.2.3", "1.2.3", False),
    (">1.2.3", "1.2.4", True),
    (">=1.2.3", "1.2.3", True),
    (">=1.2.3", "1.2.2", False),
    ("<2.0.0", "1.9.9", True),
    ("<2.0.0", "2.0.0", False),
    ("<=1.2.3", "1.2.3", True),
    ("<=1.2.3", "1.2.4", False),
    # primitives with partial right-hand sides (npm desugaring)
    (">1.2", "1.2.9", False),
    (">1.2", "1.3.0", True),   # >1.2 -> >=1.3.0
    (">1", "1.9.9", False),
    (">1", "2.0.0", True),     # >1 -> >=2.0.0
    ("<1.2", "1.1.9", True),
    ("<1.2", "1.2.0", False),  # <1.2 -> <1.2.0
    ("<1", "0.9.9", True),
    ("<1", "1.0.0", False),    # <1 -> <1.0.0
    (">=1.2", "1.2.0", True),  # >=1.2 -> >=1.2.0
    (">=1", "1.0.0", True),    # >=1 -> >=1.0.0
    ("<=1.2", "1.2.99", True),
    ("<=1.2", "1.3.0", False),  # <=1.2 -> <1.3.0
    ("<=1", "1.99.99", True),
    ("<=1", "2.0.0", False),    # <=1 -> <2.0.0
    ("=1.2", "1.2.9", True),   # =1.2 -> >=1.2.0 <1.3.0
    ("=1.2", "1.3.0", False),
    ("=1", "1.5.0", True),
    ("=1", "2.0.0", False),
    # '*'-bounds primitives
    (">*", "1.2.3", False),     # >* matches nothing (npm: <0.0.0-0)
    ("<x", "0.0.1", False),
    (">=*", "0.0.1", True),
    ("<=*", "99.0.0", True),
    # --- hyphen ranges (npm docs table) ---------------------------- #
    ("1.2.3 - 2.3.4", "1.2.3", True),
    ("1.2.3 - 2.3.4", "2.3.4", True),   # upper bound inclusive
    ("1.2.3 - 2.3.4", "2.3.5", False),
    ("1.2.3 - 2.3.4", "1.2.2", False),
    ("1.2 - 2.3.4", "1.2.0", True),     # partial lower zero-filled
    ("1.2 - 2.3.4", "1.1.9", False),
    ("1.2.3 - 2.3", "2.3.9", True),     # partial upper -> <2.4.0
    ("1.2.3 - 2.3", "2.4.0", False),
    ("1.2.3 - 2", "2.9.9", True),       # partial upper -> <3.0.0
    ("1.2.3 - 2", "3.0.0", False),
    ("1.2.3 - 2.3.4-beta", "2.3.4-beta", True),  # prerelease upper kept
    ("1.2.3 - 2.3.4-beta", "2.3.4", False),      # release above the bound
    ("1.2.3-alpha - 2.0.0", "1.2.3-beta", True),
    ("1.2.3-alpha - 2.0.0", "1.2.3-alpha", True),
    ("1.2.3  -  2.0.0", "1.5.0", True),  # extra spaces tolerated
    # --- whitespace AND conjunctions -------------------------------- #
    (">=1.2.3 <2.0.0", "1.5.0", True),
    (">=1.2.3 <2.0.0", "2.0.0", False),
    (">=1.2.3 <2.0.0", "1.2.2", False),
    # whitespace between an operator and its version is tolerated
    # (npm's comparator trim glues it back together)
    (">= 1.2.3 < 2.0.0", "1.5.0", True),
    (">= 1.2.3 < 2.0.0", "2.0.0", False),
    ("~ 1.2.3", "1.2.9", True),
    ("= 1.5.0", "1.5.0", True),
    ("^ 1.2.3", "1.5.0", True),
    (">=1.0.0 <2.0.0 >1.5.0", "1.6.0", True),
    (">=1.0.0 <2.0.0 >1.5.0", "1.5.0", False),
    ("1.2.3 1.3.0", "1.2.3", False),  # two exacts AND to nothing
    # --- || unions --------------------------------------------------- #
    ("^1.0.0 || ^2.0.0", "1.5.0", True),
    ("^1.0.0 || ^2.0.0", "2.5.0", True),
    ("^1.0.0 || ^2.0.0", "3.0.0", False),
    ("^1.0.0 || ^2.0.0", "0.9.0", False),
    ("~1.2.3 || ~1.3.0", "1.3.5", True),
    ("~1.2.3 || ~1.3.0", "1.4.0", False),
    ("1.2.3 || >2.0.0", "1.2.3", True),
    ("1.2.3 || >2.0.0", "2.1.0", True),
    ("1.2.3 || >2.0.0", "1.9.0", False),
    # --- the notorious npm prerelease rule --------------------------- #
    # a prerelease satisfies a range only when some comparator of the
    # matching branch carries a prerelease on the SAME triple
    ("^1.2.3-alpha", "1.2.3-alpha", True),
    ("^1.2.3-alpha", "1.2.3-beta", True),   # same triple, higher pre
    ("^1.2.3-alpha", "1.2.4-alpha", False),  # different triple!
    ("^1.2.3-alpha", "1.2.4-beta", False),
    ("^1.2.3-alpha", "1.2.4", True),         # releases are never gated
    (">=1.2.3", "1.2.3-alpha", False),       # the classic NOT case
    ("^1.2.3", "1.2.3-alpha", False),
    ("~1.2.3", "1.2.4-beta", False),
    ("~1.2.3-beta.2", "1.2.3-beta.4", True),  # same triple gated
    ("~1.2.3-beta.2", "1.2.4-beta.4", False),
    (">=1.2.3-alpha", "1.2.3-beta", True),
    ("<1.2.4-alpha", "1.2.3-beta", False),    # gate is on (1,2,4)
    ("<1.2.4-alpha", "1.2.4-beta", False),    # above the bound anyway
    (">=1.2.3-alpha <1.3.0", "1.2.3-rc.1", True),
    ("1.2.3-alpha", "1.2.3-alpha", True),     # exact prerelease gates
    ("1.2.3-alpha", "1.2.3-rc.1", False),     # exact comparison
    # build metadata never affects satisfaction
    ("^1.2.3", "1.5.0+build.9", True),
    ("^1.2.3-alpha", "1.2.3-alpha+001", True),
    # leading v on the version input is accepted
    ("^1.2.3", "v1.5.0", True),
]

# --------------------------------------------------------------------- #
# npm ground truths: range -> expanded union branches
# --------------------------------------------------------------------- #

EXPLAIN_VECTORS = [
    # caret
    ("^1.2.3", [[">=1.2.3", "<2.0.0"]]),
    ("^0.2.3", [[">=0.2.3", "<0.3.0"]]),
    ("^0.0.3", [[">=0.0.3", "<0.0.4"]]),
    ("^1.2.3-beta.2", [[">=1.2.3-beta.2", "<2.0.0"]]),
    ("^1.2", [[">=1.2.0", "<2.0.0"]]),
    ("^0.0", [[">=0.0.0", "<0.1.0"]]),
    ("^1", [[">=1.0.0", "<2.0.0"]]),
    ("^0", [[">=0.0.0", "<1.0.0"]]),
    ("^1.2.x", [[">=1.2.0", "<2.0.0"]]),
    ("^0.0.x", [[">=0.0.0", "<0.1.0"]]),
    ("^1.x", [[">=1.0.0", "<2.0.0"]]),
    ("^0.x", [[">=0.0.0", "<1.0.0"]]),
    ("^*", [["*"]]),
    # tilde
    ("~1.2.3", [[">=1.2.3", "<1.3.0"]]),
    ("~1.2", [[">=1.2.0", "<1.3.0"]]),
    ("~1", [[">=1.0.0", "<2.0.0"]]),
    ("~0.2.3", [[">=0.2.3", "<0.3.0"]]),
    ("~0.2", [[">=0.2.0", "<0.3.0"]]),
    ("~0", [[">=0.0.0", "<1.0.0"]]),
    ("~1.2.3-beta.2", [[">=1.2.3-beta.2", "<1.3.0"]]),
    ("~1.2.x", [[">=1.2.0", "<1.3.0"]]),
    ("~*", [["*"]]),
    # x-ranges and bare partials
    ("1.2.x", [[">=1.2.0", "<1.3.0"]]),
    ("1.2", [[">=1.2.0", "<1.3.0"]]),
    ("1.x.x", [[">=1.0.0", "<2.0.0"]]),
    ("1.x", [[">=1.0.0", "<2.0.0"]]),
    ("1", [[">=1.0.0", "<2.0.0"]]),
    ("1.2.X", [[">=1.2.0", "<1.3.0"]]),
    ("*", [["*"]]),
    ("x", [["*"]]),
    ("X", [["*"]]),
    ("1.x.3", [[">=1.0.0", "<2.0.0"]]),  # npm collapses after an x
    # exact and primitives
    ("1.2.3", [["=1.2.3"]]),
    ("=1.2.3", [["=1.2.3"]]),
    ("1.2.3-beta", [["=1.2.3-beta"]]),
    ("1.2.3+build", [["=1.2.3"]]),  # build metadata dropped
    (">1.2.3", [[">1.2.3"]]),
    (">=1.2.3", [[">=1.2.3"]]),
    ("<2.0.0", [["<2.0.0"]]),
    ("<=2.0.0", [["<=2.0.0"]]),
    (">1.2", [[">=1.3.0"]]),
    (">1", [[">=2.0.0"]]),
    ("<1.2", [["<1.2.0"]]),
    ("<1", [["<1.0.0"]]),
    (">=1.2", [[">=1.2.0"]]),
    (">=1", [[">=1.0.0"]]),
    ("<=1.2", [["<1.3.0"]]),
    ("<=1", [["<2.0.0"]]),
    ("=1.2", [[">=1.2.0", "<1.3.0"]]),
    ("=1", [[">=1.0.0", "<2.0.0"]]),
    (">=1.2.3-beta", [[">=1.2.3-beta"]]),
    (">*", [["<0.0.0-0"]]),  # npm: nothing is greater than *
    ("<x", [["<0.0.0-0"]]),
    (">=*", [["*"]]),
    ("<=*", [["*"]]),
    ("=x", [["*"]]),
    ("=v1.2.3", [["=1.2.3"]]),
    (">=v1.2.3", [[">=1.2.3"]]),
    # hyphen ranges
    ("1.2.3 - 2.3.4", [[">=1.2.3", "<=2.3.4"]]),
    ("1.2 - 2.3.4", [[">=1.2.0", "<=2.3.4"]]),
    ("1.2.3 - 2.3", [[">=1.2.3", "<2.4.0"]]),
    ("1.2.3 - 2", [[">=1.2.3", "<3.0.0"]]),
    ("1.2 - 2", [[">=1.2.0", "<3.0.0"]]),
    ("1.2.3 - 2.3.4-beta", [[">=1.2.3", "<=2.3.4-beta"]]),
    ("1.2.3-alpha - 2", [[">=1.2.3-alpha", "<3.0.0"]]),
    ("1.2.3 - x", [[">=1.2.3"]]),
    ("x - 2.0.0", [["<=2.0.0"]]),
    # AND conjunctions and unions
    (">=1.2.3 <2.0.0", [[">=1.2.3", "<2.0.0"]]),
    (">= 1.2.3 < 2.0.0 || 1.2.x",
     [[">=1.2.3", "<2.0.0"], [">=1.2.0", "<1.3.0"]]),  # glued operators
    # AND tokens are kept verbatim (npm does not reduce them either)
    ("~1.2.3 >=1.2.5", [[">=1.2.3", "<1.3.0", ">=1.2.5"]]),
    ("^1.0.0 || ^2.0.0",
     [[">=1.0.0", "<2.0.0"], [">=2.0.0", "<3.0.0"]]),
    ("1.2.3 || >2.0.0", [["=1.2.3"], [">2.0.0"]]),
    ("1.2.3 - 2.3.4 || >3", [[">=1.2.3", "<=2.3.4"], [">=4.0.0"]]),
    # an empty union branch means '*'
    ("1.2.3 ||", [["=1.2.3"], ["*"]]),
]

# --------------------------------------------------------------------- #
# satisfied mode
# --------------------------------------------------------------------- #


class TestSatisfies(unittest.TestCase):
    """satisfies mode against the npm ground-truth vectors."""

    def test_npm_vectors(self):
        for version_range, version, expected in SATISFIES_VECTORS:
            if expected is None:
                continue
            with self.subTest(range=version_range, version=version):
                result = run_satisfies(version, version_range)
                self.assertNotIn("error", result)
                self.assertEqual(result["satisfies"], expected)

    def test_matching_union_branch_reported(self):
        result = run_satisfies("2.5.0", "^1.0.0 || ^2.0.0")
        self.assertTrue(result["satisfies"])
        self.assertEqual(result["matched_branch"], 1)
        self.assertEqual(
            result["matched_comparators"], [">=2.0.0", "<3.0.0"]
        )

    def test_no_branch_reported_on_miss(self):
        result = run_satisfies("3.5.0", "^1.0.0 || ^2.0.0")
        self.assertFalse(result["satisfies"])
        self.assertIsNone(result["matched_branch"])
        self.assertIsNone(result["matched_comparators"])
        self.assertEqual(len(result["branches"]), 2)

    def test_version_fields_reported(self):
        result = run_satisfies("v1.2.3-alpha.7+build.1", "^1.2.3-alpha")
        self.assertTrue(result["satisfies"])
        self.assertEqual(result["major"], 1)
        self.assertEqual(result["minor"], 2)
        self.assertEqual(result["patch"], 3)
        self.assertEqual(result["prerelease"], "alpha.7")
        self.assertEqual(result["build"], "build.1")

    def test_normalized_range_round_trip(self):
        result = run_satisfies("1.2.4", ">=1.2.3  <2.0.0")
        self.assertEqual(result["normalized"], ">=1.2.3 <2.0.0")
        self.assertTrue(result["satisfies"])

    def test_union_normalized_with_star_branch(self):
        result = run_explain("1.2.3 ||")
        self.assertEqual(result["normalized"], "*")  # '*' absorbs it

    def test_invalid_version_is_structured_error(self):
        for bad in ("1.2", "banana", "1.2.3-", "01.2.3", "1.2.3.4",
                    "1.2.3-0123"):
            with self.subTest(bad=bad):
                result = run_satisfies(bad, "^1.2.3")
                self.assertIn("error", result)
                self.assertEqual(result["error"]["type"],
                                 "invalid_version")
                self.assertIn("message", result["error"])


# --------------------------------------------------------------------- #
# explain mode
# --------------------------------------------------------------------- #


class TestExplain(unittest.TestCase):
    """explain mode against the npm desugaring tables."""

    def test_npm_expansions(self):
        for version_range, expected in EXPLAIN_VECTORS:
            with self.subTest(range=version_range):
                result = run_explain(version_range)
                self.assertNotIn("error", result)
                self.assertEqual(result["comparators"], expected)
                self.assertEqual(result["branches"], len(expected))

    def test_normalized_forms(self):
        cases = [
            ("^1.2.3", ">=1.2.3 <2.0.0"),
            ("~1.2.3", ">=1.2.3 <1.3.0"),
            ("1.2.x", ">=1.2.0 <1.3.0"),
            ("1.2.3 - 2.3", ">=1.2.3 <2.4.0"),
            ("*", "*"),
            (">=1.2.3  <2.0.0", ">=1.2.3 <2.0.0"),
            ("^1.0.0 ||^2.0.0",
             ">=1.0.0 <2.0.0 || >=2.0.0 <3.0.0"),
        ]
        for version_range, expected in cases:
            with self.subTest(range=version_range):
                self.assertEqual(
                    run_explain(version_range)["normalized"], expected
                )

    def test_deterministic(self):
        self.assertEqual(run_explain("^1.2.3"), run_explain("^1.2.3"))


# --------------------------------------------------------------------- #
# versions mode
# --------------------------------------------------------------------- #


class TestVersions(unittest.TestCase):
    """versions mode: filtering, sorting, min/max, invalid entries."""

    CANDIDATES = [
        "1.4.2", "1.9.0", "2.0.0-rc.1", "1.2.3", "0.9.0",
        "1.5.0", "3.1.4", "2.0.0", "1.0.0", "2.1.5",
    ]

    def test_filter_and_sort(self):
        result = run_versions("^1.0.0", self.CANDIDATES)
        self.assertNotIn("error", result)
        self.assertEqual(
            result["matches"],
            ["1.0.0", "1.2.3", "1.4.2", "1.5.0", "1.9.0"],
        )
        self.assertEqual(result["matches_count"], 5)
        self.assertEqual(result["min_satisfying"], "1.0.0")
        self.assertEqual(result["max_satisfying"], "1.9.0")
        self.assertEqual(result["rejected_count"], 5)

    def test_prerelease_gating_in_versions(self):
        result = run_versions("^2.0.0", ["2.0.0-rc.1", "2.0.0", "2.5.0"])
        self.assertEqual(result["matches"], ["2.0.0", "2.5.0"])
        self.assertEqual(result["rejected_count"], 1)
        self.assertEqual(result["rejected_sample"], ["2.0.0-rc.1"])
        # the same prerelease satisfies the range that gates its triple
        gated = run_versions("^2.0.0-rc.0", ["2.0.0-rc.1", "2.0.0"])
        self.assertEqual(gated["matches"], ["2.0.0-rc.1", "2.0.0"])

    def test_union_branches(self):
        result = run_versions(
            "^1.0.0 || >=3.0.0 <4.0.0", self.CANDIDATES
        )
        self.assertEqual(
            result["matches"],
            ["1.0.0", "1.2.3", "1.4.2", "1.5.0", "1.9.0", "3.1.4"],
        )

    def test_invalid_entries_reported_with_index(self):
        result = run_versions(
            "^1.0.0", ["1.0.0", "not-a-version", "1.2", "1.5.0"]
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["invalid_count"], 2)
        self.assertEqual(
            [entry["index"] for entry in result["invalid"]], [1, 2]
        )
        self.assertEqual(result["matches"], ["1.0.0", "1.5.0"])

    def test_build_metadata_entries_keep_their_strings(self):
        result = run_versions("^1.0.0", ["1.5.0+a", "1.5.0+b"])
        self.assertEqual(result["matches"], ["1.5.0+a", "1.5.0+b"])


# --------------------------------------------------------------------- #
# intersect mode
# --------------------------------------------------------------------- #


class TestIntersect(unittest.TestCase):
    """intersect mode: simplified bounds or the empty verdict."""

    def test_simple_overlap(self):
        result = run_intersect(">=1.0.0 <2.0.0", ">=1.5.0 <3.0.0")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=1.5.0 <2.0.0")

    def test_caret_tilde_overlap(self):
        result = run_intersect("^1.2.3", "~1.2.3")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=1.2.3 <1.3.0")

    def test_disjoint_carets_empty(self):
        result = run_intersect("^1.0.0", "^2.0.0")
        self.assertTrue(result["empty"])
        self.assertIsNone(result["intersection"])
        self.assertEqual(result["branches"], [])

    def test_adjacent_carets_empty(self):
        # ^0.2.3 is >=0.2.3 <0.3.0 and ^0.2.4 is >=0.2.4 <0.3.0:
        # the strongest bounds are >=0.2.4 and <0.3.0 — non-empty.
        result = run_intersect("^0.2.3", "^0.2.4")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=0.2.4 <0.3.0")
        # but ^0.0.3 and ^0.0.4 share no patch version
        result = run_intersect("^0.0.3", "^0.0.4")
        self.assertTrue(result["empty"])

    def test_exact_pin(self):
        result = run_intersect("1.2.3", "^1.0.0")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], "=1.2.3")

    def test_conflicting_exacts_empty(self):
        result = run_intersect("1.2.3", "1.2.4")
        self.assertTrue(result["empty"])

    def test_star_absorbs(self):
        result = run_intersect("*", ">=1.2.0")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=1.2.0")

    def test_open_bounds_gap_is_empty(self):
        # >1.2.3 AND <1.2.4 admits no release and gates no prerelease
        result = run_intersect(">1.2.3", "<1.2.4")
        self.assertTrue(result["empty"])

    def test_prerelease_bounds_keep_releases(self):
        result = run_intersect(">1.2.3-alpha", "<1.2.4-beta")
        self.assertFalse(result["empty"])
        self.assertEqual(
            result["intersection"], ">1.2.3-alpha <1.2.4-beta"
        )

    def test_prerelease_intersection_same_triple(self):
        result = run_intersect("~1.2.3-alpha", "~1.2.3-beta")
        self.assertFalse(result["empty"])
        self.assertEqual(
            result["intersection"], ">=1.2.3-beta <1.3.0"
        )

    def test_prerelease_version_needs_both_gates(self):
        # the release window says non-empty either way (1.2.3 and up);
        # the merged expression documents the same bounds
        result = run_intersect("~1.2.3-alpha", ">=1.2.3")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=1.2.3 <1.3.0")

    def test_unions_intersect_pairwise(self):
        result = run_intersect("^1.0.0 || ^2.0.0", ">=1.5.0 <3.0.0")
        self.assertFalse(result["empty"])
        self.assertEqual(
            result["intersection"], ">=1.5.0 <2.0.0 || >=2.0.0 <3.0.0"
        )

    def test_never_range_empty(self):
        result = run_intersect(">*", "*")
        self.assertTrue(result["empty"])

    def test_hyphen_intersect(self):
        result = run_intersect("1.2.3 - 2.3", ">=2.0.0")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], ">=2.0.0 <2.4.0")

    def test_best_effort_note_present(self):
        self.assertIn(
            "best-effort", run_intersect("*", "*")["note"]
        )

    def test_star_intersect_star(self):
        result = run_intersect("*", "x")
        self.assertFalse(result["empty"])
        self.assertEqual(result["intersection"], "*")


# --------------------------------------------------------------------- #
# parameter-level validation (ValueError) and malformed ranges
# --------------------------------------------------------------------- #


class TestValidationAndErrors(unittest.TestCase):
    """strict input validation and structured range errors."""

    def setUp(self):
        self.tool = SemverRangeTool()

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="bump")

    def test_missing_mode_raises(self):
        with self.assertRaises(ValueError):
            self.tool.execute(version="1.2.3", version_range="^1.2.3")

    def test_missing_required_params_raise(self):
        cases = [
            dict(mode="satisfies", version_range="^1.2.3"),
            dict(mode="satisfies", version="1.2.3"),
            dict(mode="explain"),
            dict(mode="versions", version_range="^1.2.3"),
            dict(mode="versions", versions=["1.2.3"]),
            dict(mode="intersect", version_range="^1.2.3"),
            dict(mode="intersect", version_range_b="^1.2.3"),
        ]
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    self.tool.execute(**kwargs)

    def test_wrong_types_raise(self):
        cases = [
            dict(mode="satisfies", version=123, version_range="^1.2.3"),
            dict(mode="satisfies", version=True, version_range="^1.2.3"),
            dict(mode="satisfies", version=None, version_range="^1.2.3"),
            dict(mode="satisfies", version="1.2.3", version_range=7),
            dict(mode="explain", version_range=["^1.2.3"]),
            dict(mode="versions", version_range="^1.2.3", versions="1.2.3"),
            dict(mode="versions", version_range="^1.2.3", versions=[42]),
            dict(mode="intersect", version_range="^1.2.3",
                 version_range_b=None),
        ]
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    self.tool.execute(**kwargs)

    def test_empty_and_oversized_strings_raise(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="explain", version_range="")
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="satisfies", version="1.2.3", version_range="^1.2.3 "
                * 200  # 1200 characters
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="versions",
                version_range="^1.2.3",
                versions=["1.2.3"] * 1001,
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="versions", version_range="^1.2.3", versions=[]
            )

    def test_malformed_ranges_are_structured_errors(self):
        bad_ranges = [
            "josh",
            ">=abc",
            ">=1.2.3.4",
            "1.2.3.4",
            "~1.2-beta",       # prerelease on a partial core
            ">=01.2.3",        # leading zero
            "1.2.3 - 2.3.4 - 3.0.0",  # two hyphen separators
            ">=1.2.3 <",       # dangling operator
            ">=",
            "~",
            "^",
            "1.2.3-",          # empty prerelease
            "1.2.3-a..b",      # empty prerelease identifier
            "1.2.3-b.02",      # numeric prerelease leading zero
            ">=1.2.3 >~1.4",   # operator + tilde combination
            "~^1.2.3",         # both sigils at once
            "1.2.3 -",         # dangling hyphen
            "- 2.0.0",         # dangling hyphen
            "1.2 +3.0",        # build on a partial
        ]
        for bad in bad_ranges:
            with self.subTest(bad=bad):
                result = run_explain(bad)
                self.assertIn("error", result, bad)
                self.assertEqual(result["error"]["type"], "invalid_range")
                self.assertIn("position", result["error"])
                self.assertIn("fragment", result["error"])
                self.assertIn("branch", result["error"])

    def test_error_position_points_at_fragment(self):
        result = run_explain("1.2.3 || josh")
        self.assertEqual(result["error"]["type"], "invalid_range")
        self.assertEqual(result["error"]["branch"], 1)
        self.assertEqual(result["error"]["position"], 9)
        self.assertEqual(result["error"]["fragment"], "josh")

    def test_error_position_within_token(self):
        result = run_explain(">=1.2.3 <josh")
        self.assertEqual(result["error"]["position"], 8)
        self.assertEqual(result["error"]["fragment"], "<josh")

    def test_second_range_error_reports_which(self):
        result = run_intersect("^1.2.3", "banana")
        self.assertIn("error", result)
        self.assertEqual(result["error"]["type"], "invalid_range")

    def test_whitespace_only_union_branch_is_star(self):
        result = run_explain("  ^1.2.3   ||   ")
        self.assertEqual(result["comparators"], [[">=1.2.3", "<2.0.0"],
                                                 ["*"]])

    def test_satisfies_invalid_range_is_error_not_false(self):
        result = run_satisfies("1.2.3", "not a range!")
        self.assertIn("error", result)


# --------------------------------------------------------------------- #
# packaging
# --------------------------------------------------------------------- #


class TestPackaging(unittest.TestCase):
    """the tool is importable and registered like the other tools."""

    def test_package_export_matches_direct_class(self):
        self.assertIs(SemverRangeTool, DirectSemverRangeTool)

    def test_tool_metadata(self):
        tool = SemverRangeTool()
        self.assertEqual(tool.name, "semver_range_tool")
        self.assertIn("satisfies", tool.description)

    def test_modes_constant(self):
        self.assertEqual(
            SemverRangeTool.MODES,
            ("satisfies", "explain", "versions", "intersect"),
        )


if __name__ == "__main__":
    unittest.main()
