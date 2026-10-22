#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_collocation_tool.py

"""Offline unit tests for CollocationTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic and checked against hand-computed ground truths: bigram
counts (including CJK single-character tokens and sentence-internal
pairing) are enumerated by hand for tiny corpora, and the PMI / Dice /
t-score arithmetic is verified term by term with literal ``math.log2``
expressions (F(xy), F(x), F(y) and N all spelled out), plus pinned
decimal constants. Tie ordering, the min_count filter against the
low-frequency PMI explosion, pair_lookup in both orders, empty-input
behavior and the full error matrix are each pinned separately.
"""

import json
import math
import unittest

from agentuniverse.agent.action.tool.common_tool import CollocationTool
from agentuniverse.agent.action.tool.common_tool.collocation_tool import (
    CollocationTool as DirectCollocationTool,
)

# --------------------------------------------------------------------- #
# Hand-computed corpora and ground truths
# --------------------------------------------------------------------- #
#
# Corpus A: "The cat sat. The cat ran. The dog sat." (casefold=True)
#
# Sentences (folded): [the cat sat] [the cat ran] [the dog sat]
# N = 9 tokens. Unigrams: the:3 cat:2 sat:2 ran:1 dog:1.
# Sentence-internal pairs: (the,cat)x2 (cat,sat)x1 (cat,ran)x1
# (the,dog)x1 (dog,sat)x1 — total 6, distinct 5. No cross-sentence
# pair (sat,the) exists.
CORPUS_A = "The cat sat. The cat ran. The dog sat."
BIGRAMS_A = [
    {"pair": "the cat", "count": 2},
    {"pair": "cat ran", "count": 1},
    {"pair": "cat sat", "count": 1},
    {"pair": "dog sat", "count": 1},
    {"pair": "the dog", "count": 1},
]
# Scored (min_count=1). Ground truth arithmetic, term by term:
#   the cat: Fxy=2 Fx=3 Fy=2 N=9 -> pmi=log2(2*9/(3*2))=log2(3)
#            dice=2*2/(3+2)=0.8   t=(2-3*2/9)/sqrt(2)=4/3/sqrt(2)
#   cat ran: Fxy=1 Fx=2 Fy=1     -> pmi=log2(9/2)  dice=2/3  t=1-2/9=7/9
#   dog sat: Fxy=1 Fx=1 Fy=2     -> pmi=log2(9/2)  dice=2/3  t=7/9
#   the dog: Fxy=1 Fx=3 Fy=1     -> pmi=log2(3)    dice=0.5  t=1-1/3=2/3
#   cat sat: Fxy=1 Fx=2 Fy=2     -> pmi=log2(9/4)  dice=0.5  t=1-4/9=5/9
# Order: pmi desc (cat ran and dog sat tie at log2(9/2), tie-broken
# count-desc then pair-asc; the cat and the dog tie at log2(3),
# tie-broken count-desc), then cat sat at log2(9/4).
SCORED_A_MIN1 = [
    {
        "pair": "cat ran",
        "count": 1,
        "pmi": round(math.log2(9 / 2), 3),
        "dice": round(2 / 3, 6),
        "t_score": round(7 / 9, 3),
    },
    {
        "pair": "dog sat",
        "count": 1,
        "pmi": round(math.log2(9 / 2), 3),
        "dice": round(2 / 3, 6),
        "t_score": round(7 / 9, 3),
    },
    {
        "pair": "the cat",
        "count": 2,
        "pmi": round(math.log2(3), 3),
        "dice": round(0.8, 6),
        "t_score": round(4 / 3 / math.sqrt(2), 3),
    },
    {
        "pair": "the dog",
        "count": 1,
        "pmi": round(math.log2(3), 3),
        "dice": 0.5,
        "t_score": round(2 / 3, 3),
    },
    {
        "pair": "cat sat",
        "count": 1,
        "pmi": round(math.log2(9 / 4), 3),
        "dice": 0.5,
        "t_score": round(5 / 9, 3),
    },
]
# Pinned decimal constants (computed by hand from the expressions
# above; if these ever disagree the rounding contract has changed).
PINNED_A = {
    "cat ran": (2.17, 0.666667, 0.778),
    "dog sat": (2.17, 0.666667, 0.778),
    "the cat": (1.585, 0.8, 0.943),
    "the dog": (1.585, 0.5, 0.667),
    "cat sat": (1.17, 0.5, 0.556),
}

# Corpus B: "big data rocks. big data rules. big data rocks.
# big data rocks." — 4 sentences, N=12 tokens; unigrams big:4 data:4
# rocks:3 rules:1; pairs (big,data)x4 (data,rocks)x3 (data,rules)x1.
CORPUS_B = (
    "big data rocks. big data rules. big data rocks. big data rocks."
)
SCORED_B_DEFAULT = [
    {
        "pair": "big data",
        "count": 4,
        "pmi": round(math.log2(4 * 12 / (4 * 4)), 3),
        "dice": round(2 * 4 / (4 + 4), 6),
        "t_score": round((4 - 4 * 4 / 12) / math.sqrt(4), 3),
    },
    {
        "pair": "data rocks",
        "count": 3,
        "pmi": round(math.log2(3 * 12 / (4 * 3)), 3),
        "dice": round(2 * 3 / (4 + 3), 6),
        "t_score": round((3 - 4 * 3 / 12) / math.sqrt(3), 3),
    },
]

# Corpus C (CJK): "我爱北京。我爱上海。我爱北京。" — the tokenizer
# emits one token per Han character, so the sentences are
# [我 爱 北 京] [我 爱 上 海] [我 爱 北 京]; N=12; pairs (我,爱)x3
# (爱,北)x2 (北,京)x2 (爱,上)x1 (上,海)x1. Tie order follows Unicode
# code points: 北 U+5317 < 爱 U+7231 and 上 U+4E0A < 爱 U+7231.
CORPUS_C = "我爱北京。我爱上海。我爱北京。"
BIGRAMS_C = [
    {"pair": "我 爱", "count": 3},
    {"pair": "北 京", "count": 2},
    {"pair": "爱 北", "count": 2},
    {"pair": "上 海", "count": 1},
    {"pair": "爱 上", "count": 1},
]
# Scored (min_count=1) with hand-computed measures:
#   上 海: Fxy=1 Fx=1 Fy=1 N=12 -> pmi=log2(12)     dice=1.0 t=11/12
#   北 京: Fxy=2 Fx=2 Fy=2     -> pmi=log2(6)      dice=1.0 t=5/3/sqrt(2)
#   我 爱: Fxy=3 Fx=3 Fy=3     -> pmi=log2(4)      dice=1.0 t=2.25/sqrt(3)
#   爱 北: Fxy=2 Fx=3 Fy=2     -> pmi=log2(24/6)   dice=0.8 t=1.5/sqrt(2)
#   爱 上: Fxy=1 Fx=3 Fy=1     -> pmi=log2(12/3)   dice=0.5 t=1-3/12
SCORED_C_MIN1 = [
    {
        "pair": "上 海",
        "count": 1,
        "pmi": round(math.log2(12), 3),
        "dice": 1.0,
        "t_score": round(11 / 12, 3),
    },
    {
        "pair": "北 京",
        "count": 2,
        "pmi": round(math.log2(6), 3),
        "dice": 1.0,
        "t_score": round(5 / 3 / math.sqrt(2), 3),
    },
    {
        "pair": "我 爱",
        "count": 3,
        "pmi": round(math.log2(4), 3),
        "dice": 1.0,
        "t_score": round(2.25 / math.sqrt(3), 3),
    },
    {
        "pair": "爱 北",
        "count": 2,
        "pmi": round(math.log2(4), 3),
        "dice": round(0.8, 6),
        "t_score": round(1.5 / math.sqrt(2), 3),
    },
    {
        "pair": "爱 上",
        "count": 1,
        "pmi": round(math.log2(4), 3),
        "dice": 0.5,
        "t_score": round(1 - 3 / 12, 3),
    },
]

# Corpus D (mixed CJK/ASCII): "使用python开发。" — the tokenizer splits
# at the CJK boundary into 使 用 python 开 发, so pairs bridge the two
# scripts ("用 python", "python 开"). Sorted by code point, "python 开"
# (starts with ASCII 'p') precedes every CJK-initial pair.
CORPUS_D = "使用python开发。"
BIGRAMS_D = [
    {"pair": "python 开", "count": 1},
    {"pair": "使 用", "count": 1},
    {"pair": "开 发", "count": 1},
    {"pair": "用 python", "count": 1},
]

# Corpus E (casefold): "New York new york. NEW YORK."
CORPUS_E = "New York new york. NEW YORK."

# Corpus F (contraction): "don't stop. don't stop." — the tokenizer
# keeps "don't" as one token; N=4, (don't,stop)x2.
CORPUS_F = "don't stop. don't stop."

# PMI-explosion corpus: "zebra quark. zebra quark. zebra quark.
# elephant giraffe." — N=8; (zebra,quark)x3 with Fx=Fy=3 -> pmi=
# log2(3*8/9)=log2(8/3)~1.415, while (elephant,giraffe)x1 with
# Fx=Fy=1 -> pmi=log2(8/1)=3.0 — the once-seen pair OUTSCORES the
# thrice-seen one, which is exactly the low-frequency PMI explosion
# the min_count filter (default 3) exists to mitigate.
CORPUS_PMI = "zebra quark. zebra quark. zebra quark. elephant giraffe."


class CollocationToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib CollocationTool."""

    def setUp(self) -> None:
        self.tool = CollocationTool()

    # ------------------------------------------------------------------ #
    # bigrams mode
    # ------------------------------------------------------------------ #

    def test_bigrams_hand_computed_table(self) -> None:
        result = self.tool.execute(mode="bigrams", text=CORPUS_A, casefold=True)
        self.assertEqual(result["mode"], "bigrams")
        self.assertEqual(result["casefold"], True)
        self.assertEqual(result["top_n"], 50)
        self.assertEqual(result["total_bigrams"], 6)
        self.assertEqual(result["distinct_pairs"], 5)
        self.assertEqual(result["bigrams"], BIGRAMS_A)

    def test_bigrams_no_cross_sentence_pairs(self) -> None:
        # "... ran. The ..." must NOT produce (ran, the): the count-1
        # rows are exactly the four within-sentence pairs.
        pairs = {
            row["pair"] for row in self.tool.execute(
                mode="bigrams", text=CORPUS_A, casefold=True
            )["bigrams"]
        }
        self.assertNotIn("ran the", pairs)
        self.assertNotIn("sat the", pairs)
        self.assertEqual(len(pairs), 5)

    def test_bigrams_top_n_truncation_keeps_totals(self) -> None:
        result = self.tool.execute(
            mode="bigrams", text=CORPUS_A, casefold=True, top_n=1
        )
        self.assertEqual(result["top_n"], 1)
        # Totals describe the whole corpus, not the truncated table.
        self.assertEqual(result["total_bigrams"], 6)
        self.assertEqual(result["distinct_pairs"], 5)
        self.assertEqual(result["bigrams"], [{"pair": "the cat", "count": 2}])

    def test_bigrams_cjk_single_char_tokens(self) -> None:
        result = self.tool.execute(mode="bigrams", text=CORPUS_C)
        self.assertEqual(result["total_bigrams"], 9)
        self.assertEqual(result["distinct_pairs"], 5)
        self.assertEqual(result["bigrams"], BIGRAMS_C)

    def test_bigrams_cjk_ascii_boundary(self) -> None:
        result = self.tool.execute(mode="bigrams", text=CORPUS_D)
        self.assertEqual(result["bigrams"], BIGRAMS_D)

    def test_bigrams_casefold_merges_variants(self) -> None:
        folded = self.tool.execute(mode="bigrams", text=CORPUS_E, casefold=True)
        self.assertEqual(folded["distinct_pairs"], 2)
        self.assertEqual(folded["total_bigrams"], 4)
        self.assertEqual(
            folded["bigrams"],
            [{"pair": "new york", "count": 3}, {"pair": "york new", "count": 1}],
        )
        raw = self.tool.execute(mode="bigrams", text=CORPUS_E)
        self.assertEqual(raw["distinct_pairs"], 4)
        self.assertEqual(raw["total_bigrams"], 4)

    def test_bigrams_default_no_casefold(self) -> None:
        result = self.tool.execute(mode="bigrams", text=CORPUS_A)
        # Without casefold the token is capital-T "The" (always
        # sentence-initial here), so the pair is ("The", "cat") and
        # the folded form "the cat" does not exist at all.
        self.assertEqual(result["casefold"], False)
        self.assertEqual(result["total_bigrams"], 6)
        self.assertEqual(result["distinct_pairs"], 5)
        self.assertEqual(result["bigrams"][0], {"pair": "The cat", "count": 2})
        self.assertNotIn(
            "the cat", {row["pair"] for row in result["bigrams"]}
        )

    # ------------------------------------------------------------------ #
    # scored mode
    # ------------------------------------------------------------------ #

    def test_scored_hand_computed_measures(self) -> None:
        result = self.tool.execute(
            mode="scored", text=CORPUS_A, casefold=True, min_count=1
        )
        self.assertEqual(result["mode"], "scored")
        self.assertEqual(result["min_count"], 1)
        self.assertEqual(result["top_n"], 50)
        self.assertEqual(result["total_tokens"], 9)
        self.assertEqual(result["distinct_pairs"], 5)
        self.assertEqual(result["qualifying_pairs"], 5)
        self.assertEqual(result["collocations"], SCORED_A_MIN1)

    def test_scored_pinned_decimal_constants(self) -> None:
        rows = self.tool.execute(
            mode="scored", text=CORPUS_A, casefold=True, min_count=1
        )["collocations"]
        by_pair = {row["pair"]: row for row in rows}
        for pair, (pmi, dice, t_score) in PINNED_A.items():
            self.assertEqual(by_pair[pair]["pmi"], pmi, msg=pair)
            self.assertEqual(by_pair[pair]["dice"], dice, msg=pair)
            self.assertEqual(by_pair[pair]["t_score"], t_score, msg=pair)

    def test_scored_sorted_by_pmi_desc_with_deterministic_ties(self) -> None:
        # pmi ties (log2(9/2) and log2(3) occur twice) fall back to
        # count desc then pair asc — asserted by the exact SCORED_A
        # order above; here the ordering invariant is re-checked.
        rows = self.tool.execute(
            mode="scored", text=CORPUS_A, casefold=True, min_count=1
        )["collocations"]
        keys = [(-row["pmi"], -row["count"], row["pair"]) for row in rows]
        self.assertEqual(keys, sorted(keys))

    def test_scored_default_min_count_filters_and_explains(self) -> None:
        result = self.tool.execute(
            mode="scored", text=CORPUS_B
        )
        self.assertEqual(result["min_count"], 3)
        self.assertEqual(result["casefold"], False)
        self.assertEqual(result["total_tokens"], 12)
        self.assertEqual(result["distinct_pairs"], 3)
        # (data, rules) has count 1 < 3 and is filtered out.
        self.assertEqual(result["qualifying_pairs"], 2)
        self.assertEqual(result["collocations"], SCORED_B_DEFAULT)
        # The pmi-tie (both log2(3)) is broken by count desc: the
        # count-4 pair precedes the count-3 pair.
        self.assertEqual(
            [row["pair"] for row in result["collocations"]],
            ["big data", "data rocks"],
        )
        self.assertEqual(result["note"]["type"], "low_frequency_pmi")

    def test_scored_min_count_filter_blocks_pmi_explosion(self) -> None:
        everything = self.tool.execute(
            mode="scored", text=CORPUS_PMI, min_count=1
        )
        by_pair = {row["pair"]: row for row in everything["collocations"]}
        # The explosion: the once-seen pair outscores the thrice-seen.
        self.assertEqual(
            by_pair["elephant giraffe"]["pmi"], round(math.log2(8), 3)
        )
        self.assertEqual(
            by_pair["zebra quark"]["pmi"], round(math.log2(8 / 3), 3)
        )
        self.assertGreater(
            by_pair["elephant giraffe"]["pmi"], by_pair["zebra quark"]["pmi"]
        )
        # The default filter removes exactly the exploding pair.
        filtered = self.tool.execute(mode="scored", text=CORPUS_PMI)
        self.assertEqual(filtered["qualifying_pairs"], 1)
        self.assertEqual(
            filtered["collocations"][0]["pair"], "zebra quark"
        )

    def test_scored_cjk_measures(self) -> None:
        result = self.tool.execute(mode="scored", text=CORPUS_C, min_count=1)
        self.assertEqual(result["total_tokens"], 12)
        self.assertEqual(result["collocations"], SCORED_C_MIN1)

    def test_scored_contraction_token_integrity(self) -> None:
        result = self.tool.execute(mode="scored", text=CORPUS_F, min_count=2)
        self.assertEqual(result["total_tokens"], 4)
        self.assertEqual(
            result["collocations"],
            [
                {
                    "pair": "don't stop",
                    "count": 2,
                    "pmi": round(math.log2(2 * 4 / (2 * 2)), 3),
                    "dice": round(2 * 2 / (2 + 2), 6),
                    "t_score": round((2 - 2 * 2 / 4) / math.sqrt(2), 3),
                }
            ],
        )

    def test_scored_top_n_truncation_keeps_qualifying_count(self) -> None:
        result = self.tool.execute(
            mode="scored", text=CORPUS_A, casefold=True, min_count=1, top_n=2
        )
        self.assertEqual(result["top_n"], 2)
        self.assertEqual(result["qualifying_pairs"], 5)
        self.assertEqual(len(result["collocations"]), 2)
        self.assertEqual(
            [row["pair"] for row in result["collocations"]], ["cat ran", "dog sat"]
        )

    def test_scored_default_min_count_on_small_corpus_is_empty(self) -> None:
        result = self.tool.execute(mode="scored", text=CORPUS_A, casefold=True)
        self.assertEqual(result["min_count"], 3)
        self.assertEqual(result["qualifying_pairs"], 0)
        self.assertEqual(result["collocations"], [])
        self.assertEqual(result["total_tokens"], 9)

    # ------------------------------------------------------------------ #
    # pair_lookup mode
    # ------------------------------------------------------------------ #

    def test_pair_lookup_both_orders(self) -> None:
        result = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="cat", casefold=True
        )
        self.assertEqual(result["mode"], "pair_lookup")
        self.assertEqual(result["word"], "cat")
        self.assertEqual(result["casefold"], True)
        self.assertEqual(result["top_n"], 50)
        self.assertEqual(result["total_pairs_with_word"], 3)
        self.assertEqual(
            result["collocates"],
            [
                {"pair": "the cat", "count": 2, "position": "second"},
                {"pair": "cat ran", "count": 1, "position": "first"},
                {"pair": "cat sat", "count": 1, "position": "first"},
            ],
        )

    def test_pair_lookup_word_second_only(self) -> None:
        # "dog" is the second element of (the, dog) and the first
        # element of (dog, sat) — both orders are returned, tie-broken
        # by pair asc ("dog sat" < "the dog").
        result = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="dog", casefold=True
        )
        self.assertEqual(result["total_pairs_with_word"], 2)
        self.assertEqual(
            result["collocates"],
            [
                {"pair": "dog sat", "count": 1, "position": "first"},
                {"pair": "the dog", "count": 1, "position": "second"},
            ],
        )

    def test_pair_lookup_tie_order_and_position_second(self) -> None:
        result = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="sat", casefold=True
        )
        self.assertEqual(
            result["collocates"],
            [
                {"pair": "cat sat", "count": 1, "position": "second"},
                {"pair": "dog sat", "count": 1, "position": "second"},
            ],
        )

    def test_pair_lookup_casefold_applies_to_word(self) -> None:
        folded = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="CAT", casefold=True
        )
        self.assertEqual(folded["word"], "cat")
        self.assertEqual(folded["total_pairs_with_word"], 3)
        raw = self.tool.execute(mode="pair_lookup", text=CORPUS_A, word="CAT")
        # Without casefold the corpus holds "cat" but never "CAT".
        self.assertEqual(raw["word"], "CAT")
        self.assertEqual(raw["total_pairs_with_word"], 0)
        self.assertEqual(raw["collocates"], [])

    def test_pair_lookup_cjk(self) -> None:
        result = self.tool.execute(mode="pair_lookup", text=CORPUS_C, word="爱")
        self.assertEqual(result["total_pairs_with_word"], 3)
        self.assertEqual(
            result["collocates"],
            [
                {"pair": "我 爱", "count": 3, "position": "second"},
                {"pair": "爱 北", "count": 2, "position": "first"},
                {"pair": "爱 上", "count": 1, "position": "first"},
            ],
        )

    def test_pair_lookup_position_both(self) -> None:
        result = self.tool.execute(mode="pair_lookup", text="ha ha. ha ha.", word="ha")
        self.assertEqual(
            result["collocates"],
            [{"pair": "ha ha", "count": 2, "position": "both"}],
        )

    def test_pair_lookup_unknown_word_is_empty_not_error(self) -> None:
        result = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="zebra", casefold=True
        )
        self.assertEqual(result["total_pairs_with_word"], 0)
        self.assertEqual(result["collocates"], [])

    def test_pair_lookup_top_n_truncation(self) -> None:
        result = self.tool.execute(
            mode="pair_lookup", text=CORPUS_A, word="cat", casefold=True, top_n=1
        )
        self.assertEqual(result["total_pairs_with_word"], 3)
        self.assertEqual(
            result["collocates"],
            [{"pair": "the cat", "count": 2, "position": "second"}],
        )

    # ------------------------------------------------------------------ #
    # Empty inputs (valid, not errors)
    # ------------------------------------------------------------------ #

    def test_single_word_text_yields_empty_tables(self) -> None:
        for mode in ("bigrams", "scored"):
            result = self.tool.execute(
                mode=mode, text="hello.", min_count=1
            )
            self.assertEqual(result["total_bigrams" if mode == "bigrams" else "qualifying_pairs"], 0)
            rows = result["bigrams"] if mode == "bigrams" else result["collocations"]
            self.assertEqual(rows, [])
        lookup = self.tool.execute(mode="pair_lookup", text="hello.", word="hello")
        self.assertEqual(lookup["total_pairs_with_word"], 0)
        scored = self.tool.execute(mode="scored", text="hello.", min_count=1)
        self.assertEqual(scored["total_tokens"], 1)
        self.assertEqual(scored["distinct_pairs"], 0)

    # ------------------------------------------------------------------ #
    # Determinism / serializability
    # ------------------------------------------------------------------ #

    def test_results_deterministic_and_json_serializable(self) -> None:
        for kwargs in (
            {"mode": "bigrams", "text": CORPUS_A, "casefold": True},
            {"mode": "scored", "text": CORPUS_B},
            {"mode": "pair_lookup", "text": CORPUS_C, "word": "爱"},
        ):
            first = self.tool.execute(**kwargs)
            second = self.tool.execute(**kwargs)
            self.assertEqual(first, second, msg=str(kwargs))
            json.dumps(first)  # must not raise

    def test_package_and_direct_imports_expose_same_class(self) -> None:
        self.assertIs(CollocationTool, DirectCollocationTool)

    # ------------------------------------------------------------------ #
    # Error matrix (strict validation, raised before any computation)
    # ------------------------------------------------------------------ #

    def assert_value_error(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode_rejected(self) -> None:
        self.assert_value_error(mode="collocate", text=CORPUS_A)
        self.assert_value_error(mode=None, text=CORPUS_A)

    def test_text_rejected_when_missing_empty_wrong_type_or_oversized(self) -> None:
        self.assert_value_error(mode="bigrams")
        self.assert_value_error(mode="bigrams", text=None)
        self.assert_value_error(mode="bigrams", text="")
        self.assert_value_error(mode="bigrams", text=123)
        self.assert_value_error(mode="bigrams", text=True)
        self.assert_value_error(mode="scored", text=["words"])
        self.assert_value_error(mode="bigrams", text="a" * 100_001)

    def test_top_n_and_min_count_bounds(self) -> None:
        for bad in (0, -1, 1001, "10", 2.5, True):
            self.assert_value_error(mode="bigrams", text=CORPUS_A, top_n=bad)
        # None is allowed and means the default.
        self.assertEqual(
            self.tool.execute(mode="bigrams", text=CORPUS_A, top_n=None)["top_n"], 50
        )
        for bad in (0, -3, "3", 1.5, True):
            self.assert_value_error(mode="scored", text=CORPUS_A, min_count=bad)
        self.assert_value_error(
            mode="scored", text=CORPUS_A, min_count=1_000_001
        )

    def test_casefold_type_rejected(self) -> None:
        for bad in ("yes", 1, 0, [True]):
            self.assert_value_error(mode="bigrams", text=CORPUS_A, casefold=bad)

    def test_pair_lookup_word_validation(self) -> None:
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A)
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word=None)
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word="")
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word="   ")
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word="new york")
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word=" leading")
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word=7)
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word=True)
        self.assert_value_error(mode="pair_lookup", text=CORPUS_A, word="x" * 1_001)

    def test_error_messages_are_prefixed_and_specific(self) -> None:
        with self.assertRaisesRegex(ValueError, "collocation_tool: mode must be one of"):
            self.tool.execute(mode="nope", text=CORPUS_A)
        with self.assertRaisesRegex(ValueError, "text must be a non-empty string"):
            self.tool.execute(mode="bigrams", text="")
        with self.assertRaisesRegex(ValueError, r"word must be a single word without whitespace"):
            self.tool.execute(mode="pair_lookup", text=CORPUS_A, word="two words")
        with self.assertRaisesRegex(ValueError, "top_n must be an integer between 1 and 1000"):
            self.tool.execute(mode="bigrams", text=CORPUS_A, top_n=0)
        with self.assertRaisesRegex(ValueError, "min_count must be an integer between 1 and"):
            self.tool.execute(mode="scored", text=CORPUS_A, min_count=0)
        with self.assertRaisesRegex(ValueError, "text exceeds the"):
            self.tool.execute(mode="bigrams", text="a" * 100_001)


if __name__ == "__main__":
    unittest.main()
