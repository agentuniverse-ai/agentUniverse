#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_distance_tool.py

"""Offline unit tests for TextDistanceTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: distances are checked against literal published vectors
(written independently of the tool under test), the normalized scores
against exact arithmetic, and both kernels are cross-checked against
independent reference implementations — a breadth-first search over
single edits for Levenshtein and a textbook full-matrix recurrence for
the optimal-string-alignment distance — plus metric properties
(identity, symmetry, bounds, ordering, triangle inequality) over a
fixed pool and seeded random pairs.
"""

import random
import unittest
from collections import deque

from agentuniverse.agent.action.tool.common_tool import TextDistanceTool
from agentuniverse.agent.action.tool.common_tool.text_distance_tool import (
    TextDistanceTool as DirectTextDistanceTool,
)

# --------------------------------------------------------------------- #
# Independent reference implementations
# --------------------------------------------------------------------- #


def bfs_levenshtein(source: str, target: str) -> int:
    """Reference Levenshtein: BFS over single-character edits."""
    if source == target:
        return 0
    alphabet = sorted(set(source + target))
    seen = {source}
    queue = deque([(source, 0)])
    while queue:
        text, steps = queue.popleft()
        if text == target:
            return steps
        neighbors = set()
        for i in range(len(text)):  # deletions
            neighbors.add(text[:i] + text[i + 1 :])
        for i in range(len(text)):  # substitutions
            for char in alphabet:
                if char != text[i]:
                    neighbors.add(text[:i] + char + text[i + 1 :])
        if len(text) < len(target):  # insertions never need to overshoot
            for i in range(len(text) + 1):
                for char in alphabet:
                    neighbors.add(text[:i] + char + text[i:])
        for neighbor in neighbors:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, steps + 1))
    raise AssertionError(f"BFS exhausted without reaching {target!r}")


def osa_reference(a: str, b: str) -> int:
    """Reference optimal-string-alignment distance (full matrix)."""
    n, m = len(a), len(b)
    table = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        table[i][0] = i
    for j in range(m + 1):
        table[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                table[i][j] = min(table[i][j], table[i - 2][j - 2] + 1)
    return table[n][m]


# Fixed string pool for metric-property checks (deterministic).
POOL = [
    "",
    "a",
    "ab",
    "abc",
    "abab",
    "xyz",
    "hello",
    "world",
    "kitten",
    "sitting",
    "café",
    "世界",
    "the quick",
    "teh quick",
]


class TextDistanceToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextDistanceTool."""

    def setUp(self) -> None:
        self.tool = TextDistanceTool()

    def lev(self, a: str, b: str) -> int:
        return self.tool.execute(mode="levenshtein", text_a=a, text_b=b)["result"]

    def osa(self, a: str, b: str) -> int:
        return self.tool.execute(mode="damerau_levenshtein", text_a=a, text_b=b)["result"]

    # ------------------------------------------------------------------ #
    # Levenshtein known vectors
    # ------------------------------------------------------------------ #

    def test_levenshtein_known_vectors(self) -> None:
        cases = [
            ("", "", 0),
            ("", "abc", 3),
            ("abc", "", 3),
            ("a", "b", 1),
            ("abc", "abc", 0),
            ("book", "back", 2),
            ("gumbo", "gambol", 2),
            ("flaw", "lawn", 2),
            ("kitten", "sitting", 3),
            ("saturday", "sunday", 3),
            ("ab", "ba", 2),
            ("teh", "the", 2),
            ("café", "cafe", 1),
            ("世界", "世间", 1),
            ("naïve", "naive", 1),
            ("a" * 100, "b" * 100, 100),
        ]
        for a, b, expected in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(self.lev(a, b), expected)

    def test_damerau_known_vectors(self) -> None:
        cases = [
            ("", "", 0),
            ("", "abc", 3),
            ("a", "b", 1),
            ("abc", "abc", 0),
            ("flaw", "lawn", 2),
            ("kitten", "sitting", 3),
            ("saturday", "sunday", 3),
            # adjacent transpositions cost 1, not 2
            ("ab", "ba", 1),
            ("teh", "the", 1),
            ("abc", "acb", 1),
            ("world", "wrold", 1),
            ("café", "cafe", 1),
            ("世界", "世间", 1),
        ]
        for a, b, expected in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(self.osa(a, b), expected)

    def test_damerau_is_optimal_string_alignment(self) -> None:
        # OSA counts "ca" -> "abc" as 3 (no substring re-edited); the
        # unrestricted Damerau variant would reach 2.
        self.assertEqual(self.osa("ca", "abc"), 3)
        self.assertEqual(self.lev("ca", "abc"), 3)

    # ------------------------------------------------------------------ #
    # similarity mode
    # ------------------------------------------------------------------ #

    def test_similarity_known_values(self) -> None:
        result = self.tool.execute(mode="similarity", text_a="kitten", text_b="sitting")
        self.assertEqual(result["metric"], "levenshtein")
        self.assertEqual(result["distance"], 3)
        self.assertEqual(result["result"], 1 - 3 / 7)

        self.assertEqual(
            self.tool.execute(mode="similarity", text_a="flaw", text_b="lawn")["result"],
            0.5,
        )

    def test_similarity_boundaries(self) -> None:
        empty = self.tool.execute(mode="similarity", text_a="", text_b="")
        self.assertEqual(empty["result"], 1.0)
        self.assertEqual(empty["distance"], 0)

        one_empty = self.tool.execute(mode="similarity", text_a="", text_b="abc")
        self.assertEqual(one_empty["result"], 0.0)
        self.assertEqual(one_empty["distance"], 3)

        identical = self.tool.execute(mode="similarity", text_a="abc", text_b="abc")
        self.assertEqual(identical["result"], 1.0)
        self.assertEqual(identical["distance"], 0)

        disjoint = self.tool.execute(mode="similarity", text_a="aaaa", text_b="bbbb")
        self.assertEqual(disjoint["result"], 0.0)

    def test_similarity_metric_option(self) -> None:
        # Default metric is levenshtein: "ab" -> "ba" costs 2.
        default = self.tool.execute(mode="similarity", text_a="ab", text_b="ba")
        self.assertEqual(default["metric"], "levenshtein")
        self.assertEqual(default["distance"], 2)
        self.assertEqual(default["result"], 0.0)

        # Damerau metric: the transposition costs 1.
        damerau = self.tool.execute(
            mode="similarity",
            text_a="ab",
            text_b="ba",
            metric="damerau_levenshtein",
        )
        self.assertEqual(damerau["metric"], "damerau_levenshtein")
        self.assertEqual(damerau["distance"], 1)
        self.assertEqual(damerau["result"], 0.5)

    # ------------------------------------------------------------------ #
    # case sensitivity
    # ------------------------------------------------------------------ #

    def test_case_sensitive_default_is_exact(self) -> None:
        result = self.tool.execute(mode="levenshtein", text_a="HELLO", text_b="hello")
        self.assertEqual(result["case_sensitive"], True)
        self.assertEqual(result["result"], 5)

    def test_case_insensitive_comparison(self) -> None:
        result = self.tool.execute(
            mode="levenshtein",
            text_a="Kitten",
            text_b="SiTTING",
            case_sensitive=False,
        )
        self.assertEqual(result["case_sensitive"], False)
        self.assertEqual(result["result"], 3)

        folded = self.tool.execute(
            mode="damerau_levenshtein",
            text_a="HELLO",
            text_b="hello",
            case_sensitive=False,
        )
        self.assertEqual(folded["result"], 0)

    def test_case_insensitive_uses_casefold(self) -> None:
        # casefold() maps "ß" to "ss", lower() does not.
        result = self.tool.execute(
            mode="levenshtein",
            text_a="Straße",
            text_b="STRASSE",
            case_sensitive=False,
        )
        self.assertEqual(result["result"], 0)

    # ------------------------------------------------------------------ #
    # Metric properties (deterministic pools / seeded pairs)
    # ------------------------------------------------------------------ #

    def test_identity_property(self) -> None:
        for text in POOL:
            with self.subTest(text=text):
                self.assertEqual(self.lev(text, text), 0)
                self.assertEqual(self.osa(text, text), 0)

    def test_symmetry_property(self) -> None:
        for a in POOL:
            for b in POOL:
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.lev(a, b), self.lev(b, a))
                    self.assertEqual(self.osa(a, b), self.osa(b, a))

    def test_bounds_and_ordering_property(self) -> None:
        for a in POOL:
            for b in POOL:
                with self.subTest(a=a, b=b):
                    lower = abs(len(a) - len(b))
                    upper = max(len(a), len(b))
                    for distance in (self.lev(a, b), self.osa(a, b)):
                        self.assertGreaterEqual(distance, lower)
                        self.assertLessEqual(distance, upper)
                    # transpositions can only help, never hurt
                    self.assertLessEqual(self.osa(a, b), self.lev(a, b))

    def test_triangle_inequality_property(self) -> None:
        subset = ["", "ab", "abab", "xyz", "kitten", "世界"]
        for a in subset:
            for b in subset:
                for c in subset:
                    with self.subTest(a=a, b=b, c=c):
                        self.assertLessEqual(self.lev(a, c), self.lev(a, b) + self.lev(b, c))
                        self.assertLessEqual(self.osa(a, c), self.osa(a, b) + self.osa(b, c))

    def test_seeded_random_pairs_properties(self) -> None:
        rng = random.Random(42)
        alphabet = "abcxyz "
        for _ in range(200):
            a = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 40)))
            b = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 40)))
            lev = self.lev(a, b)
            osa = self.osa(a, b)
            self.assertLessEqual(osa, lev)
            self.assertLessEqual(lev, max(len(a), len(b)))
            self.assertGreaterEqual(osa, abs(len(a) - len(b)))
            self.assertEqual(
                self.tool.execute(mode="levenshtein", text_a=b, text_b=a)["result"],
                lev,
            )

    # ------------------------------------------------------------------ #
    # Cross-checks against independent reference implementations
    # ------------------------------------------------------------------ #

    def test_levenshtein_matches_bfs_reference(self) -> None:
        strings = [
            "",
            "a",
            "b",
            "ab",
            "ba",
            "aa",
            "aba",
            "bab",
            "abab",
            "aabb",
            "abba",
        ]
        for a in strings:
            for b in strings:
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.lev(a, b), bfs_levenshtein(a, b))

    def test_osa_matches_full_matrix_reference(self) -> None:
        strings = [*POOL, "ab", "ba", "ca", "abc", "acb", "abab", "abcd"]
        for a in strings:
            for b in strings:
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.osa(a, b), osa_reference(a, b))
                    if a == b:
                        self.assertEqual(self.lev(a, b), osa_reference(a, b))

    # ------------------------------------------------------------------ #
    # Result payload shape
    # ------------------------------------------------------------------ #

    def test_distance_payload_shape(self) -> None:
        result = self.tool.execute(mode="levenshtein", text_a="flaw", text_b="lawn")
        self.assertEqual(
            result,
            {
                "mode": "levenshtein",
                "length_a": 4,
                "length_b": 4,
                "case_sensitive": True,
                "result": 2,
            },
        )

    def test_similarity_payload_shape(self) -> None:
        result = self.tool.execute(
            mode="similarity",
            text_a="kitten",
            text_b="sitting",
            metric="damerau_levenshtein",
        )
        self.assertEqual(result["mode"], "similarity")
        self.assertEqual(result["metric"], "damerau_levenshtein")
        self.assertEqual(result["length_a"], 6)
        self.assertEqual(result["length_b"], 7)
        self.assertEqual(result["case_sensitive"], True)
        self.assertEqual(result["distance"], 3)
        self.assertEqual(result["result"], 1 - 3 / 7)

    def test_large_inputs_within_bounds(self) -> None:
        # Exactly at the per-text and matrix-cell limits.
        result = self.tool.execute(mode="levenshtein", text_a="a" * 10_000, text_b="b")
        self.assertEqual(result["result"], 10_000)

        boundary = self.tool.execute(mode="levenshtein", text_a="a" * 2000, text_b="a" * 1999 + "b")
        self.assertEqual(boundary["result"], 1)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="jaro", text_a="a", text_b="b")
        self.assert_invalid(mode=None, text_a="a", text_b="b")
        self.assert_invalid(mode=123, text_a="a", text_b="b")
        self.assert_invalid(mode="LEVENSHTEIN", text_a="a", text_b="b")

    def test_invalid_text_types(self) -> None:
        for bad in (None, 123, True, b"ab", ["a"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="levenshtein", text_a=bad, text_b="b")
                self.assert_invalid(mode="levenshtein", text_a="a", text_b=bad)
                self.assert_invalid(mode="similarity", text_a=bad, text_b=bad)

    def test_empty_strings_are_valid(self) -> None:
        result = self.tool.execute(mode="levenshtein", text_a="", text_b="")
        self.assertEqual(result["result"], 0)
        self.assertEqual(result["length_a"], 0)
        self.assertEqual(result["length_b"], 0)

    def test_text_length_limit(self) -> None:
        self.assert_invalid(mode="levenshtein", text_a="a" * 10_001, text_b="b")
        self.assert_invalid(mode="similarity", text_a="a", text_b="b" * 10_001)

    def test_matrix_cell_limit(self) -> None:
        # 2001 x 2001 = 4,004,001 cells exceeds the 4,000,000 bound.
        self.assert_invalid(mode="levenshtein", text_a="a" * 2001, text_b="b" * 2001)
        # 2000 x 2000 = 4,000,000 cells is exactly at the bound.
        result = self.tool.execute(mode="levenshtein", text_a="a" * 2000, text_b="b" * 2000)
        self.assertEqual(result["result"], 2000)

    def test_matrix_cell_limit_applies_after_casefold(self) -> None:
        # casefold() expands "ß" to "ss" and "ﬃ" (U+FB03) to "ffi", so the
        # DP-cell bound must be measured on the case-folded texts the
        # dynamic program actually runs on, not on the raw inputs.
        # Raw product 1,000 x 1,000 = 1,000,000 passes, but the folded
        # product is 2,000 x 2,000 = 4,000,000 — exactly at the bound.
        at_bound = self.tool.execute(
            mode="levenshtein", text_a="ß" * 1_000, text_b="ß" * 1_000, case_sensitive=False
        )
        self.assertEqual(at_bound["result"], 0)

        # Raw product 1,001 x 1,000 = 1,001,000 passes, but the folded
        # product is 2,002 x 2,000 = 4,004,000 — past the bound.
        self.assert_invalid(
            mode="levenshtein", text_a="ß" * 1_001, text_b="ß" * 1_000, case_sensitive=False
        )

        # Ligature expansion (1 -> 3): raw 1,200 x 1,200 = 1,440,000 passes,
        # folded 3,600 x 3,600 = 12,960,000 must be rejected.
        self.assert_invalid(
            mode="levenshtein",
            text_a="ﬃ" * 1_200,
            text_b="ﬃ" * 1_200,
            case_sensitive=False,
        )

        # The same inputs are fine case-sensitively (no folding, no excess).
        literal = self.tool.execute(
            mode="levenshtein", text_a="ß" * 1_001, text_b="ß" * 1_000
        )
        self.assertEqual(literal["result"], 1)

    def test_limits_are_instance_configurable(self) -> None:
        # max_chars / max_matrix_cells are documented attributes; lowering
        # them on an instance must tighten validation, not be ignored.
        tool = TextDistanceTool()
        tool.max_chars = 8
        with self.assertRaises(ValueError):
            tool.execute(mode="levenshtein", text_a="a" * 9, text_b="b")
        self.assertEqual(
            tool.execute(mode="levenshtein", text_a="a" * 8, text_b="b")["result"], 8
        )

        tool = TextDistanceTool()
        tool.max_matrix_cells = 99
        with self.assertRaises(ValueError):
            tool.execute(mode="levenshtein", text_a="a" * 10, text_b="b" * 10)
        self.assertEqual(
            tool.execute(mode="levenshtein", text_a="a" * 9, text_b="b" * 10)["result"], 10
        )

    def test_invalid_case_sensitive(self) -> None:
        for bad in ("yes", 1, 0, "true"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="levenshtein", text_a="a", text_b="b", case_sensitive=bad)

    def test_case_sensitive_none_defaults_to_true(self) -> None:
        result = self.tool.execute(mode="levenshtein", text_a="a", text_b="b", case_sensitive=None)
        self.assertEqual(result["case_sensitive"], True)

    def test_invalid_metric(self) -> None:
        for bad in ("jaro", "Levenshtein", "Damerau", 42, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="similarity", text_a="a", text_b="b", metric=bad)

    def test_metric_ignored_by_distance_modes(self) -> None:
        result = self.tool.execute(mode="levenshtein", text_a="ab", text_b="ba", metric="jaro")
        self.assertEqual(result["result"], 2)
        result = self.tool.execute(mode="damerau_levenshtein", text_a="ab", text_b="ba", metric="jaro")
        self.assertEqual(result["result"], 1)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextDistanceTool, TextDistanceTool)
        self.assertEqual(self.tool.name, "text_distance_tool")
        self.assertIn("levenshtein", self.tool.description)
        self.assertIn("damerau_levenshtein", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextDistanceTool", __all__)


if __name__ == "__main__":
    unittest.main()
