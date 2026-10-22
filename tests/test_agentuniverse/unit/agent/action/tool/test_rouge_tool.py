#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_rouge_tool.py

"""Offline unit tests for RougeTool.

The tool is built purely on the standard library (no network, no
third-party evaluation package), so this suite runs fully offline.
Every assertion is a pinned literal hand-computed from the standard
ROUGE definitions (Lin 2004):

* n-gram overlap — an n-gram type overlaps ``min(candidate count,
  reference count)`` times; precision divides by the candidate n-gram
  total, recall by the reference n-gram total;
* ROUGE-L — the Longest Common Subsequence length over the token
  sequences (unit-weighted whole-sequence LCS per pair);
* F — ``((1 + beta^2) * P * R) / (R + beta^2 * P)``, beta = 1 (F1)
  unless stated; every zero denominator yields 0.0.

Worked example used throughout (per-token arithmetic pinned):

    candidate "the cat was found under the bed"   (7 tokens)
    reference "the cat was under the bed"          (6 tokens)

    ROUGE-1: overlap 6 (the x2, cat, was, under, bed; "found" absent)
             P = 6/7 = 0.8571  R = 6/6 = 1.0  F = 12/13 = 0.9231
    ROUGE-2: candidate bigrams 6, reference bigrams 5, overlap 4
             ((the,cat), (cat,was), (under,the), (the,bed))
             P = 4/6 = 0.6667  R = 4/5 = 0.8  F = 8/11 = 0.7273
    ROUGE-L: LCS = "the cat was under the bed", length 6
             P = 6/7 = 0.8571  R = 1.0  F = 12/13 = 0.9231

The multi-reference example (candidate "the cat sat on the mat"
against three references) is worked per reference in
``SummaryModeTest``; the LCS ambiguity cases pin the documented
deterministic backtrack (candidate-side preference on ties).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import RougeTool
from agentuniverse.agent.action.tool.common_tool.rouge_tool import (
    RougeTool as DirectRougeTool,
)

CANDIDATE = "the cat was found under the bed"
REFERENCE = "the cat was under the bed"


class ScoreSingleReferenceTest(unittest.TestCase):
    """score mode against one reference — hand-computed ground truths."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_classic_example_all_metrics(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="score", candidate=CANDIDATE, reference=REFERENCE)[
                "scores"
            ],
            {
                "rouge1": {"precision": 0.8571, "recall": 1.0, "f1": 0.9231},
                "rouge2": {"precision": 0.6667, "recall": 0.8, "f1": 0.7273},
                "rougeL": {"precision": 0.8571, "recall": 1.0, "f1": 0.9231},
            },
        )

    def test_score_result_context(self) -> None:
        result = self.tool.execute(
            mode="score", candidate=CANDIDATE, reference=REFERENCE
        )
        self.assertEqual(result["mode"], "score")
        self.assertEqual(result["candidate"], CANDIDATE)
        self.assertEqual(result["references"], [REFERENCE])
        self.assertEqual(result["reference_count"], 1)
        self.assertEqual(result["metrics"], ["rouge1", "rouge2", "rougeL"])
        self.assertEqual(result["beta"], 1.0)
        self.assertFalse(result["stemming"])

    def test_perfect_match_scores_one(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate=CANDIDATE, reference=CANDIDATE
        )["scores"]
        for metric in ("rouge1", "rouge2", "rougeL"):
            self.assertEqual(
                scores[metric],
                {"precision": 1.0, "recall": 1.0, "f1": 1.0},
            )

    def test_disjoint_scores_zero(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="alpha beta gamma", reference="delta epsilon zeta"
        )["scores"]
        for metric in ("rouge1", "rouge2", "rougeL"):
            self.assertEqual(
                scores[metric],
                {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            )

    def test_precision_recall_asymmetry_short_candidate(self) -> None:
        # candidate "a b" (2 tokens) vs reference "a b c d" (4 tokens):
        # overlap 2 -> P = 1.0, R = 0.5, F = 2/3.
        scores = self.tool.execute(
            mode="score", candidate="a b", reference="a b c d"
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 1.0, "recall": 0.5, "f1": 0.6667}
        )
        self.assertEqual(
            scores["rougeL"], {"precision": 1.0, "recall": 0.5, "f1": 0.6667}
        )

    def test_precision_recall_asymmetry_long_candidate(self) -> None:
        # Swapping the pair flips P and R (overlap 2 -> P = 0.5, R = 1.0).
        scores = self.tool.execute(
            mode="score", candidate="a b c d", reference="a b"
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 0.5, "recall": 1.0, "f1": 0.6667}
        )
        self.assertEqual(
            scores["rougeL"], {"precision": 0.5, "recall": 1.0, "f1": 0.6667}
        )

    def test_rouge1_dominates_rouge2(self) -> None:
        # Every matched bigram implies a matched unigram pair but not
        # vice versa ("was found" breaks two candidate bigrams).
        scores = self.tool.execute(
            mode="score", candidate=CANDIDATE, reference=REFERENCE
        )["scores"]
        self.assertGreater(scores["rouge1"]["f1"], scores["rouge2"]["f1"])
        self.assertEqual(scores["rouge1"]["f1"], 0.9231)
        self.assertEqual(scores["rouge2"]["f1"], 0.7273)

    def test_repeated_words_are_clamped(self) -> None:
        # candidate "buffalo buffalo buffalo" vs reference "buffalo
        # buffalo": unigram overlap min(3, 2) = 2 -> P = 2/3, R = 1.0;
        # bigram overlap min(2, 1) = 1 -> P = 1/2, R = 1.0.
        scores = self.tool.execute(
            mode="score",
            candidate="buffalo buffalo buffalo",
            reference="buffalo buffalo",
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 0.6667, "recall": 1.0, "f1": 0.8}
        )
        self.assertEqual(
            scores["rouge2"], {"precision": 0.5, "recall": 1.0, "f1": 0.6667}
        )

    def test_metrics_subset_and_order(self) -> None:
        result = self.tool.execute(
            mode="score",
            candidate=CANDIDATE,
            reference=REFERENCE,
            metrics=["rouge2"],
        )
        self.assertEqual(result["metrics"], ["rouge2"])
        self.assertEqual(list(result["scores"]), ["rouge2"])
        self.assertEqual(result["scores"]["rouge2"]["f1"], 0.7273)
        other = self.tool.execute(
            mode="score",
            candidate=CANDIDATE,
            reference=REFERENCE,
            metrics=["rougeL", "rouge1"],
        )
        self.assertEqual(other["metrics"], ["rougeL", "rouge1"])

    def test_beta_greater_than_one_favors_recall(self) -> None:
        # P = 1.0, R = 0.5 (recall the smaller side): beta = 2 ->
        # F = (1 + 4) * 1.0 * 0.5 / (0.5 + 4 * 1.0) = 2.5 / 4.5 =
        # 0.5556 — pulled down toward R, below the F1 0.6667.
        scores = self.tool.execute(
            mode="score", candidate="a b", reference="a b c d", beta=2
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 0.5556)
        # Pair swapped (P = 0.5, R = 1.0, precision the smaller side):
        # beta = 2 pulls F up toward R: F = 5 * 0.5 / (1.0 + 2.0) =
        # 2.5 / 3 = 0.8333.
        swapped = self.tool.execute(
            mode="score", candidate="a b c d", reference="a b", beta=2
        )["scores"]
        self.assertEqual(swapped["rouge1"]["f1"], 0.8333)

    def test_beta_less_than_one_favors_precision(self) -> None:
        # P = 1.0, R = 0.5, beta = 0.5: F = 1.25 * 0.5 / (0.5 + 0.25)
        # = 0.625 / 0.75 = 0.8333 — pulled up toward P, above the F1
        # 0.6667 (as beta -> 0 the F converges on the precision).
        scores = self.tool.execute(
            mode="score", candidate="a b", reference="a b c d", beta=0.5
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 0.8333)

    def test_beta_reported_in_context(self) -> None:
        result = self.tool.execute(
            mode="score", candidate="a b", reference="a b c d", beta=2
        )
        self.assertEqual(result["beta"], 2.0)

    def test_empty_candidate_scores_zero(self) -> None:
        scores = self.tool.execute(mode="score", candidate="", reference="a b")[
            "scores"
        ]
        for metric in ("rouge1", "rouge2", "rougeL"):
            self.assertEqual(
                scores[metric],
                {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            )

    def test_empty_reference_scores_zero(self) -> None:
        scores = self.tool.execute(mode="score", candidate="a b", reference="")[
            "scores"
        ]
        for metric in ("rouge1", "rouge2", "rougeL"):
            self.assertEqual(
                scores[metric],
                {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            )

    def test_both_empty_scores_zero(self) -> None:
        # Documented convention: any zero denominator scores 0.0 —
        # unlike a similarity ratio, empty-equals-empty is NOT 1.0.
        scores = self.tool.execute(mode="score", candidate="", reference="")[
            "scores"
        ]
        for metric in ("rouge1", "rouge2", "rougeL"):
            self.assertEqual(scores[metric]["f1"], 0.0)

    def test_single_token_has_no_bigrams(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="hello", reference="hello"
        )["scores"]
        self.assertEqual(scores["rouge1"], {"precision": 1.0, "recall": 1.0, "f1": 1.0})
        self.assertEqual(scores["rouge2"], {"precision": 0.0, "recall": 0.0, "f1": 0.0})
        self.assertEqual(scores["rougeL"], {"precision": 1.0, "recall": 1.0, "f1": 1.0})

    def test_case_sensitive_by_default(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="The Cat", reference="the cat"
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 0.0)

    def test_cjk_unigram_scoring(self) -> None:
        # CJK text tokenizes per ideograph: candidate "上海人工智能"
        # = [上, 海, 人, 工, 智, 能] (6) vs reference "上海" = [上, 海]
        # (2): overlap 2 -> P = 2/6, R = 1.0, F = 0.5.
        scores = self.tool.execute(
            mode="score", candidate="上海人工智能", reference="上海"
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 0.3333, "recall": 1.0, "f1": 0.5}
        )

    def test_cjk_bigram_and_lcs_scoring(self) -> None:
        # candidate [机, 器, 学, 习, 很, 有, 趣] vs reference
        # [学, 习, 机, 器]: unigram overlap 4 -> P = 4/7, R = 1.0;
        # bigrams: candidate 6, reference 3, overlap 2 ((机,器) and
        # (学,习)) -> P = 2/6, R = 2/3; LCS = [机, 器] -> P = 2/7.
        scores = self.tool.execute(
            mode="score", candidate="机器学习很有趣", reference="学习机器"
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 0.5714, "recall": 1.0, "f1": 0.7273}
        )
        self.assertEqual(
            scores["rouge2"], {"precision": 0.3333, "recall": 0.6667, "f1": 0.4444}
        )
        self.assertEqual(
            scores["rougeL"], {"precision": 0.2857, "recall": 0.5, "f1": 0.3636}
        )


class TokenizationTest(unittest.TestCase):
    """The established family tokenization rule, exercised via scores."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_contractions_and_punctuation(self) -> None:
        # "it's" and "don't" stay single tokens; punctuation dropped.
        scores = self.tool.execute(
            mode="score",
            candidate="it's fine, don't worry.",
            reference="it's fine don't worry",
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 1.0)

    def test_hyphens_split_words(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="state-of-the-art", reference="state of the art"
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 1.0)

    def test_quotation_apostrophes_trimmed(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="'quoted'", reference="quoted"
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 1.0)

    def test_alphanumeric_and_digits(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="GPT-4 has 2 variants", reference="GPT 4 has 2 variants"
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 1.0)

    def test_mixed_cjk_latin(self) -> None:
        # "AI是人工智能" -> [AI, 是, 人, 工, 智, 能] (6 tokens) vs
        # "人工智能" -> [人, 工, 智, 能] (4): overlap 4 -> P = 2/3,
        # R = 1.0, F = 0.8.
        scores = self.tool.execute(
            mode="score", candidate="AI是人工智能", reference="人工智能"
        )["scores"]
        self.assertEqual(
            scores["rouge1"], {"precision": 0.6667, "recall": 1.0, "f1": 0.8}
        )

    def test_whitespace_only_is_empty(self) -> None:
        scores = self.tool.execute(
            mode="score", candidate="   ", reference="a"
        )["scores"]
        self.assertEqual(scores["rouge1"]["f1"], 0.0)


class ScoreMultiReferenceTest(unittest.TestCase):
    """score mode with a reference list — per-component averaging."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_two_reference_average(self) -> None:
        # candidate [a, b, c, d]:
        #   vs [a, b]:    R1 P 0.5  R 1.0  F 2/3     R2 P 1/3  R 1.0  F 0.5
        #   vs [a, b, c]: R1 P 0.75 R 1.0  F 6/7     R2 P 2/3  R 1.0  F 0.8
        # averages (unrounded components, rounded once):
        #   R1 P 0.625  R 1.0  F 16/21 = 0.7619
        #   R2 P 0.5    R 1.0  F 0.65
        result = self.tool.execute(
            mode="score", candidate="a b c d", references=["a b", "a b c"]
        )
        self.assertEqual(result["reference_count"], 2)
        self.assertEqual(
            result["scores"]["rouge1"],
            {"precision": 0.625, "recall": 1.0, "f1": 0.7619},
        )
        self.assertEqual(
            result["scores"]["rouge2"],
            {"precision": 0.5, "recall": 1.0, "f1": 0.65},
        )

    def test_rouge_l_average(self) -> None:
        # LCS 2 vs 3 of 4 candidate tokens: P (0.5 + 0.75) / 2 = 0.625,
        # R 1.0, F (2/3 + 6/7) / 2 = 16/21 = 0.7619.
        result = self.tool.execute(
            mode="score", candidate="a b c d", references=["a b", "a b c"]
        )
        self.assertEqual(
            result["scores"]["rougeL"],
            {"precision": 0.625, "recall": 1.0, "f1": 0.7619},
        )

    def test_single_element_list_equals_single_reference(self) -> None:
        one = self.tool.execute(
            mode="score", candidate=CANDIDATE, reference=REFERENCE
        )
        many = self.tool.execute(
            mode="score", candidate=CANDIDATE, references=[REFERENCE]
        )
        self.assertEqual(one["scores"], many["scores"])

    def test_average_matches_summary_average(self) -> None:
        references = ["the cat is on the mat", "the cat sat", "the cat sat on the floor"]
        scored = self.tool.execute(
            mode="score", candidate="the cat sat on the mat", references=references
        )
        report = self.tool.execute(
            mode="summary", candidate="the cat sat on the mat", references=references
        )
        self.assertEqual(scored["scores"], report["average"])


class LcsDetailTest(unittest.TestCase):
    """lcs_detail mode — the subsequence itself and its positions."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_classic_example(self) -> None:
        result = self.tool.execute(
            mode="lcs_detail", candidate=CANDIDATE, reference=REFERENCE
        )
        self.assertEqual(result["candidate_token_count"], 7)
        self.assertEqual(result["reference_token_count"], 6)
        self.assertEqual(result["lcs_length"], 6)
        self.assertEqual(
            result["lcs_tokens"], ["the", "cat", "was", "under", "the", "bed"]
        )
        self.assertEqual(
            result["spans"],
            [
                {"token": "the", "candidate_index": 0, "reference_index": 0},
                {"token": "cat", "candidate_index": 1, "reference_index": 1},
                {"token": "was", "candidate_index": 2, "reference_index": 2},
                {"token": "under", "candidate_index": 4, "reference_index": 3},
                {"token": "the", "candidate_index": 5, "reference_index": 4},
                {"token": "bed", "candidate_index": 6, "reference_index": 5},
            ],
        )

    def test_interleaved_matches(self) -> None:
        # candidate [x, a, y, b, z, c] vs reference [a, b, c]: the LCS
        # skips the interleaved x / y / z.
        result = self.tool.execute(
            mode="lcs_detail", candidate="x a y b z c", reference="a b c"
        )
        self.assertEqual(result["lcs_tokens"], ["a", "b", "c"])
        self.assertEqual(
            [(span["candidate_index"], span["reference_index"]) for span in result["spans"]],
            [(1, 0), (3, 1), (5, 2)],
        )

    def test_ambiguous_lcs_is_deterministic(self) -> None:
        # candidate [a, b] vs reference [b, a]: both [a] and [b] are
        # maximal; the backtrack prefers the candidate side on ties,
        # landing on [a] at candidate 0 / reference 1.
        result = self.tool.execute(mode="lcs_detail", candidate="a b", reference="b a")
        self.assertEqual(result["lcs_tokens"], ["a"])
        self.assertEqual(
            result["spans"],
            [{"token": "a", "candidate_index": 0, "reference_index": 1}],
        )
        again = self.tool.execute(mode="lcs_detail", candidate="a b", reference="b a")
        self.assertEqual(result["spans"], again["spans"])

    def test_word_order_matters(self) -> None:
        # candidate "the cat sat" vs reference "cat sat on the":
        # LCS = [cat, sat] — "the" appears only after "sat" in the
        # reference, so it cannot join the common subsequence.
        result = self.tool.execute(
            mode="lcs_detail", candidate="the cat sat", reference="cat sat on the"
        )
        self.assertEqual(result["lcs_tokens"], ["cat", "sat"])
        self.assertEqual(result["lcs_length"], 2)
        self.assertEqual(
            [(span["candidate_index"], span["reference_index"]) for span in result["spans"]],
            [(1, 0), (2, 1)],
        )

    def test_cjk_ambiguous_lcs_backtrack(self) -> None:
        # candidate [机, 器, 学, 习, 很, 有, 趣] vs reference
        # [学, 习, 机, 器]: [机, 器] and [学, 习] are both maximal.  The
        # tie-preferring-candidate backtrack walks i down until the
        # trailing 器 match, yielding [机, 器] (candidate 0-1 against
        # reference 2-3).
        result = self.tool.execute(
            mode="lcs_detail", candidate="机器学习很有趣", reference="学习机器"
        )
        self.assertEqual(result["lcs_tokens"], ["机", "器"])
        self.assertEqual(result["lcs_length"], 2)
        self.assertEqual(
            result["spans"],
            [
                {"token": "机", "candidate_index": 0, "reference_index": 2},
                {"token": "器", "candidate_index": 1, "reference_index": 3},
            ],
        )

    def test_empty_inputs(self) -> None:
        result = self.tool.execute(mode="lcs_detail", candidate="", reference="a b")
        self.assertEqual(result["lcs_length"], 0)
        self.assertEqual(result["lcs_tokens"], [])
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["candidate_tokens"], [])
        self.assertEqual(result["reference_tokens"], ["a", "b"])

    def test_token_lists_exposed(self) -> None:
        result = self.tool.execute(
            mode="lcs_detail", candidate="GPT-4 rocks", reference="GPT 4"
        )
        self.assertEqual(result["candidate_tokens"], ["GPT", "4", "rocks"])
        self.assertEqual(result["reference_tokens"], ["GPT", "4"])

    def test_stemming_applies_to_detail(self) -> None:
        result = self.tool.execute(
            mode="lcs_detail",
            candidate="the cats",
            reference="the cat",
            stemming=True,
        )
        self.assertEqual(result["candidate_tokens"], ["the", "cat"])
        self.assertEqual(result["lcs_tokens"], ["the", "cat"])
        self.assertTrue(result["stemming"])


class SummaryModeTest(unittest.TestCase):
    """summary mode — per-reference, average and best (oracle)."""

    def setUp(self) -> None:
        self.tool = RougeTool()
        self.candidate = "the cat sat on the mat"
        self.references = [
            "the cat is on the mat",
            "the cat sat",
            "the cat sat on the floor",
        ]
        # Per reference, hand-computed:
        #   ref0: R1 5/6 (P = R = F = 0.8333), R2 0.6,      RL 5/6
        #   ref1: R1 P 0.5 / R 1.0 / F 2/3,    R2 P 0.4 / R 1.0
        #         / F 4/7 = 0.5714,             RL P 0.5 / R 1.0 / F 2/3
        #   ref2: R1 5/6,                       R2 0.8,      RL 5/6
        self.report = self.tool.execute(
            mode="summary", candidate=self.candidate, references=self.references
        )

    def test_context(self) -> None:
        self.assertEqual(self.report["mode"], "summary")
        self.assertEqual(self.report["reference_count"], 3)
        self.assertEqual(self.report["references"], self.references)

    def test_per_reference_scores(self) -> None:
        per = self.report["per_reference"]
        self.assertEqual([entry["index"] for entry in per], [0, 1, 2])
        self.assertEqual(per[0]["reference"], self.references[0])
        self.assertEqual(
            per[0]["scores"]["rouge1"],
            {"precision": 0.8333, "recall": 0.8333, "f1": 0.8333},
        )
        self.assertEqual(
            per[1]["scores"]["rouge1"],
            {"precision": 0.5, "recall": 1.0, "f1": 0.6667},
        )
        self.assertEqual(
            per[1]["scores"]["rouge2"],
            {"precision": 0.4, "recall": 1.0, "f1": 0.5714},
        )
        self.assertEqual(per[2]["scores"]["rouge2"]["f1"], 0.8)

    def test_average_scores(self) -> None:
        # R1: P (5/6 + 3/6 + 5/6) / 3 = 13/18, R 8/9, F 7/9.
        self.assertEqual(
            self.report["average"]["rouge1"],
            {"precision": 0.7222, "recall": 0.8889, "f1": 0.7778},
        )
        # R2: P (0.6 + 0.4 + 0.8) / 3 = 0.6, R (0.6 + 1.0 + 0.8) / 3
        # = 0.8, F (0.6 + 4/7 + 0.8) / 3 = 23/35 = 0.6571.
        self.assertEqual(
            self.report["average"]["rouge2"],
            {"precision": 0.6, "recall": 0.8, "f1": 0.6571},
        )
        # RL: identical per-reference f1 pattern to R1 -> 7/9.
        self.assertEqual(self.report["average"]["rougeL"]["f1"], 0.7778)

    def test_best_is_oracle_per_metric(self) -> None:
        best = self.report["best"]
        # rouge1: ref0 and ref2 tie at f1 5/6 -> lowest index wins.
        self.assertEqual(best["rouge1"]["reference_index"], 0)
        self.assertEqual(best["rouge1"]["f1"], 0.8333)
        self.assertEqual(best["rouge1"]["precision"], 0.8333)
        self.assertEqual(best["rouge1"]["recall"], 0.8333)
        # rouge2: ref2 alone reaches 0.8.
        self.assertEqual(best["rouge2"]["reference_index"], 2)
        self.assertEqual(
            best["rouge2"], {"reference_index": 2, "precision": 0.8, "recall": 0.8, "f1": 0.8}
        )
        # rougeL: tie again -> ref0.
        self.assertEqual(best["rougeL"]["reference_index"], 0)
        self.assertEqual(best["rougeL"]["f1"], 0.8333)

    def test_single_reference_summary(self) -> None:
        # candidate [x, y] vs reference [x, y, z]: overlap 2 ->
        # P = 2/2 = 1.0, R = 2/3, F = 0.8.
        report = self.tool.execute(
            mode="summary", candidate="x y", references=["x y z"]
        )
        self.assertEqual(report["reference_count"], 1)
        self.assertEqual(
            report["average"]["rouge1"],
            {"precision": 1.0, "recall": 0.6667, "f1": 0.8},
        )
        self.assertEqual(report["best"]["rouge1"]["reference_index"], 0)
        self.assertEqual(report["best"]["rouge1"]["f1"], 0.8)

    def test_metrics_subset(self) -> None:
        report = self.tool.execute(
            mode="summary",
            candidate=self.candidate,
            references=self.references,
            metrics=["rouge2"],
        )
        self.assertEqual(list(report["per_reference"][0]["scores"]), ["rouge2"])
        self.assertEqual(list(report["average"]), ["rouge2"])
        self.assertEqual(list(report["best"]), ["rouge2"])
        self.assertEqual(report["best"]["rouge2"]["reference_index"], 2)


class StemmingTest(unittest.TestCase):
    """The stemming option — light Porter rules from LightStemmerTool."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_off_by_default(self) -> None:
        result = self.tool.execute(
            mode="score", candidate="the cats", reference="the cat"
        )
        self.assertFalse(result["stemming"])
        self.assertEqual(result["scores"]["rouge1"]["f1"], 0.5)

    def test_stemming_merges_inflections(self) -> None:
        # Raw ("the cats" vs "the cat"): only "the" overlaps -> F 0.5
        # (pinned in test_off_by_default). With stemming "cats" ->
        # "cat" (step 1a), both token lists become [the, cat] -> 1.0.
        result = self.tool.execute(
            mode="score", candidate="the cats", reference="the cat", stemming=True
        )
        self.assertEqual(
            result["scores"]["rouge1"],
            {"precision": 1.0, "recall": 1.0, "f1": 1.0},
        )

    def test_stemming_partial_example(self) -> None:
        # candidate [the, cats, were, running] -> stems [the, cat, wer,
        # runn]; reference [the, cat, was, run] -> [the, cat, wa, run].
        # Overlap 2 ("the", "cat"): the light stemmer keeps "runn" /
        # "run" apart (no step-1b cleanup) — a documented divergence
        # from full Porter, pinned here.
        result = self.tool.execute(
            mode="score",
            candidate="the cats were running",
            reference="the cat was run",
        )
        self.assertEqual(result["scores"]["rouge1"]["f1"], 0.25)
        stemmed = self.tool.execute(
            mode="score",
            candidate="the cats were running",
            reference="the cat was run",
            stemming=True,
        )
        self.assertEqual(
            stemmed["scores"]["rouge1"],
            {"precision": 0.5, "recall": 0.5, "f1": 0.5},
        )

    def test_stemming_lowercases(self) -> None:
        result = self.tool.execute(
            mode="score", candidate="The Cat", reference="the cat", stemming=True
        )
        self.assertEqual(result["scores"]["rouge1"]["f1"], 1.0)

    def test_stemmer_rule_examples(self) -> None:
        # The documented LightStemmerTool examples, via lcs_detail
        # token lists (single "token" candidate per rule).
        for raw, stem in (
            ("cats", "cat"),
            ("ponies", "poni"),
            ("running", "runn"),
            ("happy", "happi"),
            ("sky", "sky"),
            ("relational", "relate"),
            ("goodness", "good"),
            ("agreed", "agree"),
            ("feed", "feed"),
        ):
            result = self.tool.execute(
                mode="lcs_detail", candidate=raw, reference=raw, stemming=True
            )
            self.assertEqual(result["candidate_tokens"], [stem], raw)

    def test_cjk_tokens_pass_through(self) -> None:
        result = self.tool.execute(
            mode="lcs_detail", candidate="猫猫", reference="猫猫", stemming=True
        )
        self.assertEqual(result["candidate_tokens"], ["猫", "猫"])


class DeterminismTest(unittest.TestCase):
    """Repeated calls return identical results."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def test_score_repeatable(self) -> None:
        first = self.tool.execute(mode="score", candidate=CANDIDATE, reference=REFERENCE)
        second = self.tool.execute(mode="score", candidate=CANDIDATE, reference=REFERENCE)
        self.assertEqual(first, second)

    def test_summary_repeatable(self) -> None:
        references = ["the cat is on the mat", "the cat sat", "the cat sat on the floor"]
        first = self.tool.execute(
            mode="summary", candidate="the cat sat on the mat", references=references
        )
        second = self.tool.execute(
            mode="summary", candidate="the cat sat on the mat", references=references
        )
        self.assertEqual(first, second)


class ValidationTest(unittest.TestCase):
    """The strict validation matrix — errors raised before computation."""

    def setUp(self) -> None:
        self.tool = RougeTool()

    def assert_invalid(self, message_part: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(**kwargs)
        self.assertIn("rouge_tool:", str(caught.exception))
        self.assertIn(message_part, str(caught.exception))

    def test_unknown_mode(self) -> None:
        self.assert_invalid(
            "mode must be one of", mode="f1", candidate="a", reference="a"
        )

    def test_missing_mode(self) -> None:
        self.assert_invalid("mode must be one of", mode=None)

    # ---- candidate -------------------------------------------------- #

    def test_candidate_missing(self) -> None:
        self.assert_invalid(
            "candidate must be a string", mode="score", reference="a"
        )

    def test_candidate_not_a_string(self) -> None:
        self.assert_invalid(
            "candidate must be a string", mode="score", candidate=7, reference="a"
        )

    def test_candidate_boolean_rejected(self) -> None:
        self.assert_invalid(
            "candidate must be a string", mode="score", candidate=True, reference="a"
        )

    def test_candidate_over_cap(self) -> None:
        self.assert_invalid(
            "candidate exceeds the 20,000-character limit",
            mode="score",
            candidate="x" * 20_001,
            reference="a",
        )

    # ---- reference / references shape -------------------------------- #

    def test_score_requires_a_reference(self) -> None:
        self.assert_invalid(
            "score mode requires a reference or references", mode="score", candidate="a"
        )

    def test_score_rejects_both_forms(self) -> None:
        self.assert_invalid(
            "provide either reference or references, not both",
            mode="score",
            candidate="a",
            reference="b",
            references=["c"],
        )

    def test_score_reference_not_a_string(self) -> None:
        self.assert_invalid(
            "reference must be a string", mode="score", candidate="a", reference=5
        )

    def test_empty_reference_list_rejected(self) -> None:
        self.assert_invalid(
            "references must be a non-empty list",
            mode="score",
            candidate="a",
            references=[],
        )

    def test_reference_list_not_a_list(self) -> None:
        self.assert_invalid(
            "references must be a non-empty list",
            mode="score",
            candidate="a",
            references="a b",
        )

    def test_reference_list_member_not_a_string(self) -> None:
        self.assert_invalid(
            "references[1] must be a string",
            mode="score",
            candidate="a",
            references=["a b", 3],
        )

    def test_reference_list_over_cap(self) -> None:
        self.assert_invalid(
            "references exceeds the 10-item limit",
            mode="score",
            candidate="a",
            references=["r"] * 11,
        )

    def test_reference_over_cap(self) -> None:
        self.assert_invalid(
            "references[0] exceeds the 20,000-character limit",
            mode="score",
            candidate="a",
            references=["y" * 20_001],
        )

    def test_lcs_detail_requires_single_reference(self) -> None:
        self.assert_invalid(
            "lcs_detail mode requires a reference string",
            mode="lcs_detail",
            candidate="a",
        )

    def test_lcs_detail_rejects_reference_list(self) -> None:
        self.assert_invalid(
            "lcs_detail mode takes a single reference, not a references list",
            mode="lcs_detail",
            candidate="a",
            references=["b"],
        )

    def test_summary_requires_reference_list(self) -> None:
        self.assert_invalid(
            "summary mode takes a references list, not a single reference",
            mode="summary",
            candidate="a",
            reference="b",
        )

    def test_summary_requires_references(self) -> None:
        self.assert_invalid(
            "references must be a non-empty list", mode="summary", candidate="a"
        )

    # ---- metrics ------------------------------------------------------ #

    def test_metrics_empty(self) -> None:
        self.assert_invalid(
            "metrics must be a non-empty list",
            mode="score",
            candidate="a",
            reference="a",
            metrics=[],
        )

    def test_metrics_not_a_list(self) -> None:
        self.assert_invalid(
            "metrics must be a non-empty list",
            mode="score",
            candidate="a",
            reference="a",
            metrics="rouge1",
        )

    def test_metrics_unknown_name(self) -> None:
        self.assert_invalid(
            "metrics must be a non-empty list",
            mode="score",
            candidate="a",
            reference="a",
            metrics=["rouge1", "rouge3"],
        )

    def test_metrics_duplicates(self) -> None:
        self.assert_invalid(
            "metrics must not contain duplicates",
            mode="score",
            candidate="a",
            reference="a",
            metrics=["rouge1", "rouge1"],
        )

    # ---- beta / stemming ---------------------------------------------- #

    def test_beta_zero(self) -> None:
        self.assert_invalid(
            "beta must be a positive number",
            mode="score",
            candidate="a",
            reference="a",
            beta=0,
        )

    def test_beta_negative(self) -> None:
        self.assert_invalid(
            "beta must be a positive number",
            mode="score",
            candidate="a",
            reference="a",
            beta=-1.5,
        )

    def test_beta_not_a_number(self) -> None:
        self.assert_invalid(
            "beta must be a positive number",
            mode="score",
            candidate="a",
            reference="a",
            beta="high",
        )

    def test_beta_boolean_rejected(self) -> None:
        self.assert_invalid(
            "beta must be a positive number",
            mode="score",
            candidate="a",
            reference="a",
            beta=True,
        )

    def test_beta_infinite_rejected(self) -> None:
        self.assert_invalid(
            "beta must be a positive number",
            mode="score",
            candidate="a",
            reference="a",
            beta=float("inf"),
        )

    def test_stemming_not_a_boolean(self) -> None:
        self.assert_invalid(
            "stemming must be a boolean",
            mode="score",
            candidate="a",
            reference="a",
            stemming="yes",
        )


class ModuleSurfaceTest(unittest.TestCase):
    """Import surface — package export and direct module import agree."""

    def test_exported_class_identity(self) -> None:
        self.assertIs(RougeTool, DirectRougeTool)

    def test_tool_name(self) -> None:
        self.assertEqual(RougeTool().name, "rouge_tool")


if __name__ == "__main__":
    unittest.main()
