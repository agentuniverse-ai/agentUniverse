#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_random_pick_tool.py

"""Offline unit tests for RandomPickTool.

The tool is built purely on the standard library ``random`` module and
never touches the network, so this suite runs fully offline. Every
seeded assertion is deterministic: the expected vectors are produced
with plain ``random.Random(seed)`` calls, so the tests simultaneously
pin the tool to the stdlib's exact draw semantics. Unseeded calls use
``random.SystemRandom`` and are asserted structurally (valid indices,
distinctness, payload shape) instead of by value.

The weighted statistical sanity checks aggregate many fixed seeds, so
they are as deterministic as the vector tests — the assertion bounds
are dozens of standard deviations away from the expected counts.
"""

import json
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import RandomPickTool
from agentuniverse.agent.action.tool.common_tool.random_pick_tool import (
    RandomPickTool as DirectRandomPickTool,
)

ITEMS_10 = ["alpha", "beta", "gamma", "delta", "epsilon",
            "zeta", "eta", "theta", "iota", "kappa"]


def expected_weighted(seed, weights, k):
    """Reference implementation of the renormalized successive draw.

    Mirrors the documented semantics of the weighted mode: a pool of
    positive-weight items, one proportional draw at a time, the drawn
    item removed and the remaining weights renormalized implicitly.
    """
    rng = random.Random(seed)
    pool = [(index, weight) for index, weight in enumerate(weights)
            if weight > 0]
    drawn = []
    for _ in range(k):
        total = sum(weight for _, weight in pool)
        threshold = rng.random() * total
        cumulative = 0.0
        chosen = len(pool) - 1
        for slot, (_, weight) in enumerate(pool):
            cumulative += weight
            if threshold < cumulative:
                chosen = slot
                break
        drawn.append(pool.pop(chosen)[0])
    return drawn


class RandomPickToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib RandomPickTool."""

    def setUp(self) -> None:
        self.tool = RandomPickTool()

    # ------------------------------------------------------------------ #
    # Exact stdlib-conformance vectors (seeded)
    # ------------------------------------------------------------------ #

    def test_pick_without_replacement_known_vector(self) -> None:
        result = self.tool.execute(mode="pick", items=ITEMS_10, k=3, seed=42)
        indices = random.Random(42).sample(range(10), 3)
        self.assertEqual(
            result,
            {
                "mode": "pick",
                "k": 3,
                "with_replacement": False,
                "seed_used": 42,
                "picked": [ITEMS_10[i] for i in indices],
                "indices": indices,
            },
        )

    def test_pick_with_replacement_known_vector(self) -> None:
        result = self.tool.execute(
            mode="pick", items=["x", "y", "z"], k=5, seed=7,
            with_replacement=True,
        )
        rng = random.Random(7)
        indices = [rng.randrange(3) for _ in range(5)]
        self.assertEqual(result["mode"], "pick")
        self.assertEqual(result["with_replacement"], True)
        self.assertEqual(result["indices"], indices)
        self.assertEqual(
            result["picked"], [["x", "y", "z"][i] for i in indices]
        )

    def test_weighted_known_vector_with_zero_weight(self) -> None:
        items = ["a", "b", "c", "d"]
        weights = [4, 0, 1, 2]
        result = self.tool.execute(
            mode="weighted", items=items, weights=weights, k=3, seed=11
        )
        drawn = expected_weighted(11, weights, 3)
        self.assertEqual(
            result,
            {
                "mode": "weighted",
                "k": 3,
                "eligible_items": 3,
                "with_replacement": False,
                "seed_used": 11,
                "picked": [items[i] for i in drawn],
                "indices": drawn,
            },
        )

    def test_shuffle_known_vector(self) -> None:
        items = ["one", "two", "three", "four", "five"]
        result = self.tool.execute(mode="shuffle", items=items, seed=99)
        order = list(range(5))
        random.Random(99).shuffle(order)
        self.assertEqual(
            result,
            {
                "mode": "shuffle",
                "k": 5,
                "with_replacement": False,
                "seed_used": 99,
                "picked": [items[i] for i in order],
                "indices": order,
            },
        )

    def test_sample_indices_known_vector(self) -> None:
        result = self.tool.execute(mode="sample_indices", n=20, k=6, seed=5)
        indices = random.Random(5).sample(range(20), 6)
        self.assertEqual(
            result,
            {
                "mode": "sample_indices",
                "n": 20,
                "k": 6,
                "with_replacement": False,
                "seed_used": 5,
                "indices": indices,
                "picked": indices,
            },
        )

    # ------------------------------------------------------------------ #
    # Seeding semantics
    # ------------------------------------------------------------------ #

    def test_same_seed_same_result_every_mode(self) -> None:
        calls = [
            lambda: self.tool.execute(mode="pick", items=ITEMS_10, k=4, seed=1),
            lambda: self.tool.execute(
                mode="pick", items=ITEMS_10, k=4, seed=1, with_replacement=True
            ),
            lambda: self.tool.execute(
                mode="weighted", items=ITEMS_10,
                weights=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], k=4, seed=1,
            ),
            lambda: self.tool.execute(mode="shuffle", items=ITEMS_10, seed=1),
            lambda: self.tool.execute(mode="sample_indices", n=50, k=8, seed=1),
        ]
        for call in calls:
            with self.subTest(call=call):
                first = call()
                self.assertEqual(first, call())
                self.assertEqual(first, call())
                self.assertEqual(first["seed_used"], 1)

    def test_seed_independent_of_call_history(self) -> None:
        # A fresh random.Random(seed) is built per call, so prior calls
        # (seeded or not) must never shift a seeded result.
        first = self.tool.execute(mode="shuffle", items=ITEMS_10, seed=123)
        for _ in range(5):
            self.tool.execute(mode="shuffle", items=ITEMS_10)
            self.tool.execute(mode="shuffle", items=ITEMS_10, seed=777)
        again = self.tool.execute(mode="shuffle", items=ITEMS_10, seed=123)
        self.assertEqual(first, again)

    def test_different_seeds_vary(self) -> None:
        for call in (
            lambda s: self.tool.execute(mode="pick", items=ITEMS_10, k=5, seed=s),
            lambda s: self.tool.execute(mode="shuffle", items=ITEMS_10, seed=s),
            lambda s: self.tool.execute(mode="sample_indices", n=30, k=9, seed=s),
        ):
            with self.subTest(call=call):
                outputs = {
                    json.dumps(call(seed), sort_keys=True)
                    for seed in range(1, 21)
                }
                self.assertGreater(len(outputs), 1)

    def test_string_seed_is_deterministic(self) -> None:
        first = self.tool.execute(mode="pick", items=ITEMS_10, k=3, seed="au-42")
        second = self.tool.execute(mode="pick", items=ITEMS_10, k=3, seed="au-42")
        self.assertEqual(first, second)
        self.assertEqual(first["seed_used"], "au-42")
        self.assertEqual(
            first["indices"],
            random.Random("au-42").sample(range(10), 3),
        )

    def test_unseeded_uses_system_random_and_reports_null(self) -> None:
        result = self.tool.execute(mode="pick", items=ITEMS_10, k=5)
        self.assertIsNone(result["seed_used"])
        self.assertEqual(len(result["indices"]), 5)
        self.assertEqual(len(set(result["indices"])), 5)
        for index in result["indices"]:
            self.assertIn(index, range(10))
        self.assertIsNone(
            self.tool.execute(mode="shuffle", items=ITEMS_10)["seed_used"]
        )
        self.assertIsNone(
            self.tool.execute(mode="sample_indices", n=10, k=3)["seed_used"]
        )
        self.assertIsNone(
            self.tool.execute(
                mode="weighted", items=ITEMS_10,
                weights=[1] * 8 + [2, 0], k=3,
            )["seed_used"]
        )

    # ------------------------------------------------------------------ #
    # Selection properties
    # ------------------------------------------------------------------ #

    def test_pick_without_replacement_uniqueness(self) -> None:
        full = self.tool.execute(mode="pick", items=ITEMS_10, k=10, seed=3)
        self.assertEqual(sorted(full["picked"]), sorted(ITEMS_10))
        self.assertEqual(sorted(full["indices"]), list(range(10)))
        partial = self.tool.execute(mode="pick", items=ITEMS_10, k=4, seed=4)
        self.assertEqual(len(set(partial["indices"])), 4)
        self.assertEqual(
            partial["picked"],
            [ITEMS_10[i] for i in partial["indices"]],
        )

    def test_pick_with_replacement_allows_k_beyond_length(self) -> None:
        result = self.tool.execute(
            mode="pick", items=["heads", "tails"], k=7, seed=8,
            with_replacement=True,
        )
        self.assertEqual(len(result["picked"]), 7)
        self.assertEqual(result["with_replacement"], True)
        for index in result["indices"]:
            self.assertIn(index, (0, 1))
        self.assertEqual(
            result["picked"],
            [["heads", "tails"][i] for i in result["indices"]],
        )

    def test_shuffle_is_permutation_with_original_indices(self) -> None:
        items = ["p", "q", "r", "s", "t", "u"]
        result = self.tool.execute(mode="shuffle", items=items, seed=13)
        self.assertEqual(sorted(result["picked"]), sorted(items))
        self.assertEqual(sorted(result["indices"]), list(range(6)))
        for position, original in enumerate(result["indices"]):
            self.assertEqual(result["picked"][position], items[original])

    def test_sample_indices_properties(self) -> None:
        result = self.tool.execute(mode="sample_indices", n=100, k=12, seed=21)
        self.assertEqual(len(result["indices"]), 12)
        self.assertEqual(len(set(result["indices"])), 12)
        self.assertEqual(result["picked"], result["indices"])
        for index in result["indices"]:
            self.assertIn(index, range(100))
        self.assertEqual(
            result["indices"], random.Random(21).sample(range(100), 12)
        )

    def test_duplicate_items_disambiguated_by_indices(self) -> None:
        items = ["same", "same", "same", "other"]
        result = self.tool.execute(mode="pick", items=items, k=4, seed=6)
        self.assertEqual(sorted(result["picked"]), sorted(items))
        self.assertEqual(sorted(result["indices"]), [0, 1, 2, 3])
        for position, index in enumerate(result["indices"]):
            self.assertEqual(result["picked"][position], items[index])

    def test_pick_accepts_arbitrary_json_values(self) -> None:
        items = [1, 2.5, "three", {"four": 4}, [5], True, None]
        result = self.tool.execute(mode="pick", items=items, k=7, seed=2)
        self.assertEqual(sorted(result["picked"], key=repr), sorted(items, key=repr))
        json.dumps(result["picked"])

    # ------------------------------------------------------------------ #
    # Weighted semantics
    # ------------------------------------------------------------------ #

    def test_zero_weight_items_never_picked(self) -> None:
        items = ["a", "b", "c"]
        weights = [0, 5, 0]
        for seed in range(100):
            result = self.tool.execute(
                mode="weighted", items=items, weights=weights, k=1, seed=seed
            )
            self.assertEqual(result["picked"], ["b"])
            self.assertEqual(result["indices"], [1])
            self.assertEqual(result["eligible_items"], 1)
        # k beyond the positive-weight pool must be rejected.
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="weighted", items=items, weights=weights, k=2, seed=1
            )

    def test_heavy_weight_wins_aggregate_over_fixed_seeds(self) -> None:
        items = ["light", "heavy"]
        weights = [1, 9]
        heavy = 0
        trials = 200
        for seed in range(trials):
            result = self.tool.execute(
                mode="weighted", items=items, weights=weights, k=1, seed=seed
            )
            self.assertEqual(len(result["picked"]), 1)
            heavy += result["picked"][0] == "heavy"
        # Expected 180 of 200 (sd ~ 4.2); 150 is far below any plausible run.
        self.assertGreaterEqual(heavy, 150)

    def test_weighted_without_replacement_distinct_indices(self) -> None:
        items = ["a", "b", "c", "d", "e"]
        weights = [10, 0.5, 3, 0, 1.5]
        for seed in range(25):
            result = self.tool.execute(
                mode="weighted", items=items, weights=weights, k=3, seed=seed
            )
            self.assertEqual(len(set(result["indices"])), 3)
            self.assertEqual(result["eligible_items"], 4)
            self.assertNotIn(3, result["indices"])  # zero weight excluded

    def test_weighted_equal_weights_both_sides_occur(self) -> None:
        items = ["left", "right"]
        outcomes = set()
        for seed in range(100):
            result = self.tool.execute(
                mode="weighted", items=items, weights=[1, 1], k=1, seed=seed
            )
            outcomes.add(result["picked"][0])
        self.assertEqual(outcomes, {"left", "right"})

    def test_weighted_mixed_int_float_weights(self) -> None:
        result = self.tool.execute(
            mode="weighted", items=["a", "b", "c"],
            weights=[2, 1.5, 0.5], k=3, seed=17,
        )
        self.assertEqual(
            result["indices"], expected_weighted(17, [2, 1.5, 0.5], 3)
        )

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="roulette", items=ITEMS_10, k=1)
        self.assert_invalid(mode=None, items=ITEMS_10, k=1)
        self.assert_invalid(mode=123, items=ITEMS_10, k=1)

    def test_invalid_items(self) -> None:
        for bad in (None, "abc", {"a": 1}, ("a", "b"), 42):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="pick", items=bad, k=1)
                self.assert_invalid(mode="shuffle", items=bad)
        self.assert_invalid(mode="pick", items=[], k=1)
        self.assert_invalid(mode="shuffle", items=[])
        self.assert_invalid(mode="pick", items=list(range(10_001)), k=1)
        ok = self.tool.execute(mode="pick", items=list(range(10_000)), k=1, seed=1)
        self.assertEqual(len(ok["picked"]), 1)

    def test_invalid_k(self) -> None:
        cases = [
            dict(mode="pick", items=ITEMS_10, k=0),
            dict(mode="pick", items=ITEMS_10, k=-2),
            dict(mode="pick", items=ITEMS_10, k=11),          # k > len
            dict(mode="pick", items=ITEMS_10, k=True),        # bool trap
            dict(mode="pick", items=ITEMS_10, k=2.5),
            dict(mode="pick", items=ITEMS_10, k="3"),
            dict(mode="pick", items=ITEMS_10),                # missing
            dict(mode="pick", items=["a", "b"], k=10_001, with_replacement=True),
            dict(mode="weighted", items=ITEMS_10,
                 weights=[1] * 10, k=11),                     # k > eligible
            dict(mode="weighted", items=ITEMS_10, weights=[1] * 10, k=0),
            dict(mode="sample_indices", n=25, k=26),          # k > n
            dict(mode="sample_indices", n=25, k=0),
        ]
        for case in cases:
            with self.subTest(case=case):
                self.assert_invalid(**case)
        # k == len(items) is valid without replacement.
        ok = self.tool.execute(mode="pick", items=["a", "b"], k=2, seed=9)
        self.assertEqual(sorted(ok["picked"]), ["a", "b"])
        # k at the with-replacement cap is valid.
        ok = self.tool.execute(
            mode="pick", items=["a", "b"], k=10_000,
            with_replacement=True, seed=10,
        )
        self.assertEqual(len(ok["picked"]), 10_000)

    def test_invalid_weights(self) -> None:
        base = dict(mode="weighted", items=["a", "b", "c"], k=1)
        for bad in (
            [1, 2],              # length mismatch
            [1, 2, 3, 4],        # length mismatch
            [-1, 2, 3],          # negative
            [0, 0, 0],           # all zero
            [0, 0, 0.0],         # all zero, float flavor
            [1, "2", 3],         # non-numeric
            [1, True, 3],        # bool trap
            [1, float("nan"), 3],
            [1, float("inf"), 3],
            [1, float("-inf"), 3],
            "123",               # not a list
            None,                # missing
        ):
            with self.subTest(bad=bad):
                self.assert_invalid(**base, weights=bad)
        # Boundary-valid weights.
        ok = self.tool.execute(
            **base, weights=[0, 0.0, 0.001], seed=3
        )
        self.assertEqual(ok["picked"], ["c"])

    def test_invalid_n(self) -> None:
        for bad in (0, -1, True, 2.0, "10", 10_001, None):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="sample_indices", n=bad, k=1)
        ok = self.tool.execute(mode="sample_indices", n=10_000, k=1, seed=1)
        self.assertIn(ok["indices"][0], range(10_000))

    def test_invalid_seed(self) -> None:
        for bad in (True, False, "", 1.5, [1], {"seed": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="pick", items=ITEMS_10, k=1, seed=bad)
        # Negative integer seeds are perfectly valid Random seeds.
        ok = self.tool.execute(mode="pick", items=ITEMS_10, k=1, seed=-5)
        self.assertEqual(ok["seed_used"], -5)

    def test_invalid_with_replacement(self) -> None:
        for bad in ("true", 1, 0, [], "yes"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="pick", items=ITEMS_10, k=1, with_replacement=bad
                )
        # None means the documented default (False).
        ok = self.tool.execute(
            mode="pick", items=ITEMS_10, k=1, with_replacement=None, seed=1
        )
        self.assertEqual(ok["with_replacement"], False)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectRandomPickTool, RandomPickTool)
        self.assertEqual(self.tool.name, "random_pick_tool")
        for word in ("pick", "weighted", "shuffle", "sample_indices", "seed"):
            self.assertIn(word, self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("RandomPickTool", __all__)


if __name__ == "__main__":
    unittest.main()
