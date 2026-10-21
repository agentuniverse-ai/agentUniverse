#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_version_constraint_tool.py

"""Offline unit tests for VersionConstraintTool.

The tool resolves npm-style dependency *constraint sets* purely on
the standard library and never touches the network, so this suite
runs fully offline. Every assertion is deterministic against
hand-computed ground truths: the ``resolve`` vectors intersect
caret / comparison constraints over a fixed available-version
fixture (including the binding-constraint attribution and the
unsatisfiable case with the conflicting pair identified), the
``conflicts`` vectors check pairwise-empty detection (``^1.0.0``
vs ``^2.0.0``, the 0.x caret special cases) and the tightest
ranking, the ``explain_set`` vectors assert the npm comparator
expansions side-by-side plus the folded intersection bounds, the
prerelease vectors pin the npm same-triple gating rule (and its
propagation through a constraint set), and the error matrix covers
both the parameter-level ``ValueError`` inputs and the
content-level structured ``error`` payloads with the 0-based
character position of the offending range fragment.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import (
    VersionConstraintTool,
)
from agentuniverse.agent.action.tool.common_tool.version_constraint_tool import (  # noqa: E501
    VersionConstraintTool as DirectVersionConstraintTool,
)

# Fixed fixture: the versions of the imaginary package "fixture-pkg".
FIXTURE = [
    "0.9.0", "1.0.0", "1.1.0", "1.2.0", "1.2.5", "1.3.0",
    "1.4.2", "1.4.9", "1.5.0", "2.0.0",
]


def run_resolve(constraints, available_versions):
    return VersionConstraintTool().execute(
        mode="resolve",
        constraints=constraints,
        available_versions=available_versions,
    )


def run_conflicts(constraints):
    return VersionConstraintTool().execute(
        mode="conflicts", constraints=constraints
    )


def run_explain_set(constraints):
    return VersionConstraintTool().execute(
        mode="explain_set", constraints=constraints
    )


class ResolveGroundTruths(unittest.TestCase):
    """``resolve`` — intersection, best pick, binding constraint."""

    def test_task_vector_caret_and_comparisons(self):
        """^1.0.0 + >=1.2.0 + <1.5.0 → the 1.2.0..1.4.x window."""
        result = run_resolve(
            ["^1.0.0", ">=1.2.0", "<1.5.0"], FIXTURE
        )
        self.assertNotIn("error", result)
        self.assertTrue(result["satisfiable"])
        self.assertEqual(
            result["candidates"],
            ["1.2.0", "1.2.5", "1.3.0", "1.4.2", "1.4.9"],
        )
        self.assertEqual(result["best"], "1.4.9")
        self.assertEqual(result["available_count"], len(FIXTURE))
        # ^1.0.0 admits the 1.x series (8 of 10, incl. 1.5.0);
        # >=1.2.0 admits 7 (excludes 0.9.0/1.0.0/1.1.0) — the most
        # exclusive range, hence the binding constraint.
        self.assertEqual(result["binding_constraint"]["index"], 1)
        self.assertEqual(result["binding_constraint"]["constraint"],
                         ">=1.2.0")
        self.assertEqual(result["binding_constraint"]["matched_count"], 7)
        self.assertEqual(result["binding_constraint"]["excluded_count"], 3)
        per = result["per_constraint"]
        self.assertEqual(len(per), 3)
        self.assertEqual(per[0]["matched_count"], 8)
        self.assertEqual(per[0]["excluded_count"], 2)
        self.assertEqual(per[1]["matched_count"], 7)
        self.assertEqual(per[1]["excluded_count"], 3)
        self.assertEqual(per[2]["matched_count"], 8)
        self.assertEqual(per[2]["excluded_count"], 2)
        self.assertEqual(
            result["normalized"],
            [">=1.0.0 <2.0.0", ">=1.2.0", "<1.5.0"],
        )

    def test_binding_tie_resolves_to_lowest_index(self):
        """^1.0.0 and <2.0.0 both admit the same 8 versions → index 0."""
        result = run_resolve(["^1.0.0", "<2.0.0"], FIXTURE)
        self.assertEqual(result["binding_constraint"]["index"], 0)
        self.assertEqual(
            result["binding_constraint"]["excluded_count"], 2
        )

    def test_unsatisfiable_with_binding_and_conflict(self):
        """>=2.0.0 + <1.5.0 excludes every fixture version."""
        result = run_resolve([">=2.0.0", "<1.5.0"], FIXTURE)
        self.assertFalse(result["satisfiable"])
        self.assertEqual(result["candidates"], [])
        self.assertIsNone(result["best"])
        # ">=2.0.0" keeps only 2.0.0 (excludes 9); "<1.5.0" keeps
        # 0.9.0..1.4.9 (excludes 2) — the binding constraint is 0.
        self.assertEqual(result["binding_constraint"]["index"], 0)
        self.assertEqual(
            result["binding_constraint"]["excluded_count"], 9
        )
        # The pairwise-empty pair that explains the failure.
        self.assertEqual(
            result["unsatisfiable_because"],
            [{"indexes": [0, 1], "constraints": [">=2.0.0", "<1.5.0"]}],
        )

    def test_union_intersected(self):
        """A || union intersected with a comparator window."""
        result = run_resolve(
            ["^1.0.0 || ^2.0.0", ">=1.2.0 <1.5.0"], FIXTURE
        )
        self.assertTrue(result["satisfiable"])
        self.assertEqual(
            result["candidates"],
            ["1.2.0", "1.2.5", "1.3.0", "1.4.2", "1.4.9"],
        )
        self.assertEqual(result["best"], "1.4.9")

    def test_union_second_branch_used(self):
        """Only the second || branch survives the intersection."""
        result = run_resolve(
            ["^3.0.0 || ~1.2", "1.2.x"], FIXTURE
        )
        self.assertEqual(result["candidates"], ["1.2.0", "1.2.5"])
        self.assertEqual(result["best"], "1.2.5")

    def test_exact_pin_set(self):
        """An exact pin against a compatible series."""
        result = run_resolve(["1.2.5", "~1.2.0"], FIXTURE)
        self.assertTrue(result["satisfiable"])
        self.assertEqual(result["candidates"], ["1.2.5"])
        self.assertEqual(result["best"], "1.2.5")
        # The pin excludes every other fixture version.
        self.assertEqual(result["binding_constraint"]["index"], 0)
        self.assertEqual(
            result["binding_constraint"]["excluded_count"], 9
        )

    def test_caret_zero_special_cases(self):
        """^0.2.3 excludes 0.3.0; ^0.0.3 excludes 0.0.4 (npm rule)."""
        available = ["0.2.3", "0.2.9", "0.3.0"]
        result = run_resolve(["^0.2.3"], available)
        self.assertEqual(result["candidates"], ["0.2.3", "0.2.9"])
        self.assertEqual(result["best"], "0.2.9")
        available = ["0.0.3", "0.0.4"]
        result = run_resolve(["^0.0.3"], available)
        self.assertEqual(result["candidates"], ["0.0.3"])
        # ^0.2.3 vs ^0.3.0 is unsatisfiable over any pool.
        result = run_resolve(["^0.2.3", "^0.3.0"], available + ["0.3.1"])
        self.assertFalse(result["satisfiable"])
        self.assertEqual(
            result["unsatisfiable_because"],
            [{"indexes": [0, 1], "constraints": ["^0.2.3", "^0.3.0"]}],
        )

    def test_hyphen_and_xrange_constraints(self):
        """Hyphen partial upper bounds and x-ranges inside a set."""
        result = run_resolve(
            ["1.2.3 - 2.3", "<2.0.0"],
            ["1.2.2", "1.2.3", "1.9.9", "2.0.0", "2.3.0"],
        )
        # 1.2.3 - 2.3 desugars to >=1.2.3 <2.4.0; <2.0.0 tightens it.
        self.assertEqual(result["candidates"], ["1.2.3", "1.9.9"])
        result = run_resolve(
            ["1.2.x", ">=1.2.5"],
            ["1.2.0", "1.2.5", "1.2.9", "1.3.0"],
        )
        self.assertEqual(result["candidates"], ["1.2.5", "1.2.9"])

    def test_candidates_sorted_semver_not_lexical(self):
        """1.10.0 sorts above 1.9.0 (numeric, not string order)."""
        result = run_resolve(
            ["^1.0.0"], ["1.9.0", "1.10.0", "1.2.0"]
        )
        self.assertEqual(
            result["candidates"], ["1.2.0", "1.9.0", "1.10.0"]
        )
        self.assertEqual(result["best"], "1.10.0")

    def test_star_and_empty_constraints_admit_everything(self):
        result = run_resolve(["*"], FIXTURE)
        self.assertTrue(result["satisfiable"])
        self.assertEqual(result["candidates"], sorted(
            FIXTURE,
            key=lambda v: [
                int(p) for p in v.split(".")
            ],
        ))
        self.assertEqual(result["best"], "2.0.0")
        # '*' excludes nothing; binding falls to index 0 by rule.
        self.assertEqual(result["binding_constraint"]["index"], 0)
        self.assertEqual(
            result["binding_constraint"]["excluded_count"], 0
        )

    def test_invalid_available_entries_reported(self):
        """Junk pool entries are reported, not fatal."""
        result = run_resolve(
            ["^1.0.0"],
            ["1.2.0", "banana", "1.2", "01.2.3", "1.4.0"],
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["available_count"], 2)
        self.assertEqual(result["invalid_count"], 3)
        reasons = {item["version"]: item for item in result["invalid"]}
        self.assertIn("banana", reasons)
        self.assertEqual(reasons["1.2"]["index"], 2)
        self.assertIn("dot-separated", reasons["1.2"]["reason"])
        self.assertIn("leading zeroes", reasons["01.2.3"]["reason"])
        self.assertEqual(result["candidates"], ["1.2.0", "1.4.0"])

    def test_build_metadata_ignored(self):
        result = run_resolve(
            ["^1.0.0"], ["1.2.0+build.7", "1.2.0"]
        )
        self.assertEqual(result["candidates"], ["1.2.0+build.7", "1.2.0"])
        self.assertEqual(result["best"], "1.2.0")

    def test_empty_pool_means_unsatisfiable(self):
        """All pool entries invalid → unsatisfiable, not an error."""
        result = run_resolve(["^1.0.0"], ["nope", "1.2"])
        self.assertFalse(result["satisfiable"])
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["invalid_count"], 2)


class ResolvePrereleasePropagation(unittest.TestCase):
    """The npm same-triple gating rule through a constraint set."""

    def test_prerelease_excluded_by_plain_lower_bound(self):
        """>=1.2.3 does NOT admit 1.2.4-alpha (no gated triple)."""
        result = run_resolve(
            [">=1.2.3"],
            ["1.2.3-beta", "1.2.4", "1.2.4-alpha", "1.3.0"],
        )
        self.assertEqual(
            result["candidates"], ["1.2.4", "1.3.0"]
        )
        self.assertEqual(result["best"], "1.3.0")

    def test_prerelease_admitted_on_same_triple_only(self):
        """^1.2.3-beta admits 1.2.3-* but NOT 1.2.4-alpha."""
        result = run_resolve(
            ["^1.2.3-beta"],
            ["1.2.3-beta", "1.2.4-alpha", "1.2.4", "1.3.0"],
        )
        self.assertEqual(
            result["candidates"],
            ["1.2.3-beta", "1.2.4", "1.3.0"],
        )
        self.assertEqual(result["best"], "1.3.0")

    def test_gating_propagates_through_intersection(self):
        """A gated prerelease survives only if EVERY constraint gates
        its triple — here <1.3.0-rc.1 re-gates (1,2,3) but >=1.2.4
        does not, so 1.2.3-rc.2 still drops out and only 1.2.4 stays."""
        result = run_resolve(
            ["^1.2.3-alpha", ">=1.2.4"],
            ["1.2.3-rc.2", "1.2.4"],
        )
        self.assertEqual(result["candidates"], ["1.2.4"])

    def test_prerelease_conflict_detection(self):
        """>=1.2.3 vs =1.2.3-alpha is a genuine empty pair."""
        result = run_conflicts([">=1.2.3", "1.2.3-alpha"])
        self.assertFalse(result["conflict_free"])
        self.assertEqual(len(result["conflicts"]), 1)
        self.assertEqual(result["conflicts"][0]["indexes"], [0, 1])

    def test_same_triple_prereleases_intersect(self):
        """Two prerelease bounds on one triple do intersect."""
        result = run_conflicts(["^1.2.3-alpha", "^1.2.3-beta"])
        self.assertTrue(result["conflict_free"])


class ConflictsGroundTruths(unittest.TestCase):
    """``conflicts`` — pairwise emptiness and the tightest range."""

    def test_disjoint_carets_conflict(self):
        result = run_conflicts(["^1.0.0", "^2.0.0"])
        self.assertFalse(result["conflict_free"])
        self.assertEqual(
            result["conflicts"],
            [{
                "indexes": [0, 1],
                "constraints": ["^1.0.0", "^2.0.0"],
                "reason": (
                    "the two ranges share no version at all "
                    "(empty intersection over every union branch pair)"
                ),
            }],
        )
        self.assertEqual(result["pairs_checked"], 1)

    def test_compatible_set_is_conflict_free_with_tightest(self):
        result = run_conflicts(["^1.0.0", ">=1.2.0 <1.5.0", "~1.4.2"])
        self.assertTrue(result["conflict_free"])
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(result["pairs_checked"], 3)
        # ~1.4.2 spans [1.4.2, 1.5.0) — narrower than the 1.2..1.5
        # window and far narrower than ^1.0.0.
        self.assertEqual(result["tightest"]["index"], 2)
        self.assertEqual(result["tightest"]["constraint"], "~1.4.2")
        self.assertFalse(result["tightest"]["exact"])
        self.assertEqual(
            result["tightest"]["span"],
            {"lower_triple": [1, 4, 2], "upper_triple": [1, 5, 0]},
        )

    def test_exact_pin_is_tightest(self):
        result = run_conflicts(["^1.0.0", "1.4.2", "<1.5.0"])
        self.assertTrue(result["conflict_free"])
        self.assertEqual(result["tightest"]["index"], 1)
        self.assertTrue(result["tightest"]["exact"])
        self.assertEqual(
            result["tightest"]["span"],
            {"lower_triple": [1, 4, 2], "upper_triple": [1, 4, 2]},
        )

    def test_star_never_tightest(self):
        result = run_conflicts(["*", "^1.0.0"])
        self.assertTrue(result["conflict_free"])
        self.assertEqual(result["tightest"]["index"], 1)
        self.assertEqual(result["tightest"]["constraint"], "^1.0.0")

    def test_adjacent_tildes_conflict(self):
        """~1.2.3 (the 1.2.x series) and ~1.3.0 share nothing."""
        result = run_conflicts(["~1.2.3", "~1.3.0"])
        self.assertFalse(result["conflict_free"])

    def test_half_open_bounds_conflict(self):
        """>=1.2.0 <1.3.0 vs >=1.3.0 <1.4.0 — touching, not overlapping."""
        result = run_conflicts(
            [">=1.2.0 <1.3.0", ">=1.3.0 <1.4.0"]
        )
        self.assertFalse(result["conflict_free"])
        self.assertEqual(result["conflicts"][0]["indexes"], [0, 1])

    def test_union_rescues_pair(self):
        """A || branch on each side keeps the pair alive."""
        result = run_conflicts(["^1.0.0 || ^2.0.0", ">=1.5.0"])
        self.assertTrue(result["conflict_free"])
        result = run_conflicts(["^1.0.0 || ^2.0.0", "^3.0.0"])
        self.assertFalse(result["conflict_free"])

    def test_exact_pins_conflict(self):
        result = run_conflicts(["1.2.3", "1.2.4"])
        self.assertFalse(result["conflict_free"])
        # 1.2.3 pins tighter than nothing else here — index 0 wins
        # the equal-width tie by the lowest-index rule.
        self.assertEqual(result["tightest"]["index"], 0)
        self.assertTrue(result["tightest"]["exact"])

    def test_three_constraints_two_conflicts(self):
        result = run_conflicts(["^1.0.0", "^2.0.0", "^3.0.0"])
        self.assertFalse(result["conflict_free"])
        self.assertEqual(result["pairs_checked"], 3)
        pairs = [tuple(c["indexes"]) for c in result["conflicts"]]
        self.assertEqual(pairs, [(0, 1), (0, 2), (1, 2)])

    def test_single_constraint_no_pairs(self):
        result = run_conflicts(["^1.0.0"])
        self.assertTrue(result["conflict_free"])
        self.assertEqual(result["pairs_checked"], 0)
        self.assertEqual(result["tightest"]["index"], 0)


class ExplainSetGroundTruths(unittest.TestCase):
    """``explain_set`` — expansions side-by-side + folded bounds."""

    def test_task_vector_simple_intersection(self):
        result = run_explain_set(["^1.0.0", ">=1.2.0", "<1.5.0"])
        self.assertNotIn("error", result)
        rows = result["constraints"]
        self.assertEqual(
            [row["constraint"] for row in rows],
            ["^1.0.0", ">=1.2.0", "<1.5.0"],
        )
        self.assertEqual(rows[0]["branches"], [[">=1.0.0", "<2.0.0"]])
        self.assertEqual(rows[1]["branches"], [[">=1.2.0"]])
        self.assertEqual(rows[2]["branches"], [["<1.5.0"]])
        self.assertEqual(rows[0]["normalized"], ">=1.0.0 <2.0.0")
        intersection = result["intersection"]
        self.assertTrue(intersection["simple"])
        self.assertFalse(intersection["empty"])
        self.assertEqual(
            intersection["expression"], ">=1.2.0 <1.5.0"
        )
        self.assertEqual(intersection["lower"], ">=1.2.0")
        self.assertEqual(intersection["upper"], "<1.5.0")
        self.assertEqual(
            intersection["window"],
            {"lower_triple": [1, 2, 0], "upper_triple": [1, 5, 0]},
        )

    def test_tilde_and_xrange_fold(self):
        result = run_explain_set(["~1.2.3", "1.2.x"])
        rows = result["constraints"]
        self.assertEqual(rows[0]["branches"], [[">=1.2.3", "<1.3.0"]])
        self.assertEqual(rows[1]["branches"], [[">=1.2.0", "<1.3.0"]])
        intersection = result["intersection"]
        self.assertEqual(
            intersection["expression"], ">=1.2.3 <1.3.0"
        )

    def test_hyphen_fold(self):
        """1.2.3 - 2.3 → >=1.2.3 <2.4.0; <2.0.0 tightens the top."""
        result = run_explain_set(["1.2.3 - 2.3", "<2.0.0"])
        rows = result["constraints"]
        self.assertEqual(rows[0]["branches"], [[">=1.2.3", "<2.4.0"]])
        intersection = result["intersection"]
        self.assertEqual(
            intersection["expression"], ">=1.2.3 <2.0.0"
        )

    def test_exact_pin_fold(self):
        result = run_explain_set(["1.2.3", "^1.0.0"])
        intersection = result["intersection"]
        self.assertFalse(intersection["empty"])
        self.assertEqual(intersection["expression"], "=1.2.3")
        self.assertEqual(
            intersection["window"],
            {"lower_triple": [1, 2, 3], "upper_triple": [1, 2, 3]},
        )

    def test_empty_fold(self):
        result = run_explain_set([">=2.0.0", "<1.5.0"])
        intersection = result["intersection"]
        self.assertTrue(intersection["simple"])
        self.assertTrue(intersection["empty"])
        self.assertIsNone(intersection["expression"])
        self.assertIsNone(intersection["window"])

    def test_star_fold_is_any(self):
        result = run_explain_set(["*", "^1.0.0"])
        intersection = result["intersection"]
        self.assertFalse(intersection["empty"])
        self.assertEqual(intersection["expression"], ">=1.0.0 <2.0.0")

    def test_union_set_not_simple_combinations(self):
        result = run_explain_set(["^1.0.0 || ^2.0.0", ">=2.5.0"])
        intersection = result["intersection"]
        self.assertFalse(intersection["simple"])
        self.assertFalse(intersection["empty"])
        combos = intersection["combinations"]
        self.assertEqual(
            [c["branch_indexes"] for c in combos], [[0, 0], [1, 0]]
        )
        by_indexes = {tuple(c["branch_indexes"]): c for c in combos}
        # The ^1.0.0 branch (upper bound <2.0.0) dies against >=2.5.0;
        # the ^2.0.0 branch carries the intersection.
        self.assertTrue(by_indexes[(0, 0)]["empty"])
        self.assertIsNone(by_indexes[(0, 0)]["expression"])
        self.assertFalse(by_indexes[(1, 0)]["empty"])
        self.assertEqual(
            by_indexes[(1, 0)]["expression"], ">=2.5.0 <3.0.0"
        )

    def test_union_set_all_empty(self):
        result = run_explain_set(["^1.0.0 || ^2.0.0", "^3.0.0"])
        intersection = result["intersection"]
        self.assertFalse(intersection["simple"])
        self.assertTrue(intersection["empty"])
        self.assertTrue(
            all(c["empty"] for c in intersection["combinations"])
        )

    def test_prerelease_bound_in_fold(self):
        """^1.2.3-alpha vs >=1.2.3: the release lower bound wins."""
        result = run_explain_set(["^1.2.3-alpha", ">=1.2.3"])
        intersection = result["intersection"]
        self.assertFalse(intersection["empty"])
        self.assertEqual(intersection["lower"], ">=1.2.3")
        self.assertEqual(intersection["upper"], "<2.0.0")

    def test_partial_comparator_expansion(self):
        """>1.2 → >=1.3.0 and <=1.2 → <1.3.0 (npm desugaring)."""
        result = run_explain_set([">1.2", "<=1.2"])
        rows = result["constraints"]
        self.assertEqual(rows[0]["branches"], [[">=1.3.0"]])
        self.assertEqual(rows[1]["branches"], [["<1.3.0"]])
        intersection = result["intersection"]
        # No release sits above >=1.3.0 and below <1.3.0 — empty.
        self.assertTrue(intersection["empty"])


class ContentErrorMatrix(unittest.TestCase):
    """Structured ``error`` payloads for malformed content."""

    def test_invalid_range_cites_position_and_index(self):
        result = run_conflicts(["^1.2.3", ">=1..2"])
        self.assertIn("error", result)
        error = result["error"]
        self.assertEqual(error["type"], "invalid_range")
        self.assertEqual(error["constraint_index"], 1)
        self.assertEqual(error["fragment"], ">=1..2")
        self.assertEqual(error["position"], 0)
        self.assertIn("must not be empty", error["message"])

    def test_position_of_second_union_branch(self):
        """'^1.0.0 || foo!!' fails inside branch 1 at offset 10."""
        result = run_resolve(
            ["^1.0.0 || foo!!"], ["1.0.0"]
        )
        self.assertIn("error", result)
        error = result["error"]
        self.assertEqual(error["branch"], 1)
        self.assertEqual(error["position"], 10)
        self.assertEqual(error["fragment"], "foo!!")

    def test_incomplete_comparator(self):
        result = run_explain_set([">= "])
        self.assertIn("error", result)
        self.assertEqual(result["error"]["type"], "invalid_range")
        self.assertIn("incomplete", result["error"]["message"])

    def test_operator_sigil_combination_rejected(self):
        result = run_explain_set([">=^1.2.3"])
        self.assertIn("error", result)
        self.assertIn("cannot be combined",
                      result["error"]["message"])

    def test_too_many_components(self):
        result = run_explain_set(["1.2.3.4"])
        self.assertIn("error", result)
        self.assertIn("1 to 3 dot-separated",
                      result["error"]["message"])

    def test_double_hyphen_rejected(self):
        result = run_explain_set(["1.2.3 - 2.0.0 - 3.0.0"])
        self.assertIn("error", result)
        self.assertIn("exactly one ' - '", result["error"]["message"])

    def test_prerelease_needs_full_core(self):
        result = run_explain_set(["^1.2-alpha"])
        self.assertIn("error", result)
        self.assertIn("full X.Y.Z version core",
                      result["error"]["message"])

    def test_error_mode_visible_in_all_modes(self):
        for runner in (run_resolve, lambda c: run_conflicts(c),
                       run_explain_set):
            if runner is run_resolve:
                result = runner(["bogus!!"], ["1.0.0"])
            else:
                result = runner(["bogus!!"])
            self.assertIn("error", result)
            self.assertEqual(result["error"]["type"], "invalid_range")


class ParameterErrorMatrix(unittest.TestCase):
    """Parameter-level ``ValueError`` inputs (raised, not returned)."""

    def setUp(self):
        self.tool = VersionConstraintTool()

    def assert_invalid(self, **kwargs):
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_mode_required_and_bounded(self):
        self.assert_invalid(mode=None, constraints=["^1.0.0"])
        self.assert_invalid(mode="bogus", constraints=["^1.0.0"])
        self.assert_invalid(mode="resolve")

    def test_constraints_must_be_non_empty_string_list(self):
        for bad in (None, "^1.0.0", 7, [], ["^1.0.0", 42],
                    ["^1.0.0", ""], ["^1.0.0", None]):
            self.assert_invalid(
                mode="conflicts", constraints=bad
            )

    def test_constraints_entry_too_long(self):
        self.assert_invalid(
            mode="conflicts", constraints=["^1.0.0" + " " * 1_000]
        )

    def test_constraints_list_too_long(self):
        self.assert_invalid(
            mode="conflicts", constraints=["^1.0.0"] * 101
        )

    def test_available_versions_required_for_resolve(self):
        self.assert_invalid(
            mode="resolve", constraints=["^1.0.0"],
            available_versions=None,
        )
        # An empty available list is a parameter error (mirror of the
        # candidate-list rule of the other common tools).
        self.assert_invalid(
            mode="resolve", constraints=["^1.0.0"],
            available_versions=[],
        )

    def test_available_versions_entries_must_be_strings(self):
        for bad in ("1.0.0", 42, ["1.0.0", 42], ["1.0.0", ""],
                    ["1.0.0", None]):
            self.assert_invalid(
                mode="resolve", constraints=["^1.0.0"],
                available_versions=bad,
            )

    def test_available_versions_too_long(self):
        self.assert_invalid(
            mode="resolve", constraints=["^1.0.0"],
            available_versions=["1.0.0"] * 1_001,
        )

    def test_available_versions_entry_too_long(self):
        self.assert_invalid(
            mode="resolve", constraints=["^1.0.0"],
            available_versions=["1.0.0" + "0" * 1_000],
        )


class Integration(unittest.TestCase):
    """Package-level wiring (the common_tool export path)."""

    def test_exported_from_package(self):
        self.assertIs(VersionConstraintTool, DirectVersionConstraintTool)

    def test_tool_identity(self):
        tool = VersionConstraintTool()
        self.assertEqual(tool.name, "version_constraint_tool")
        self.assertIn("resolve", tool.description)
        self.assertIn("conflicts", tool.description)
        self.assertIn("explain_set", tool.description)

    def test_determinism(self):
        """Same inputs → byte-identical results (dict equality)."""
        first = run_resolve(
            ["^1.0.0", ">=1.2.0", "<1.5.0"], FIXTURE
        )
        second = run_resolve(
            ["^1.0.0", ">=1.2.0", "<1.5.0"], FIXTURE
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
