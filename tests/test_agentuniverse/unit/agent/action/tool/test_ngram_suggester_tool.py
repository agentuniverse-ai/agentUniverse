#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_ngram_suggester_tool.py

"""Offline unit tests for NgramSuggesterTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic and checked against hand-computed ground truths: the
n-gram tables (including the ``<START>`` / ``<END>`` sentence markers)
are enumerated by hand for tiny corpora, per-context probabilities are
property-checked to sum to 1, next-mode hits and misses are pinned,
character n-grams are counted by hand for both cross-word settings, and
the Laplace-smoothed negative-log-probability arithmetic is verified
term by term with literal logarithm expressions.
"""

import json
import math
import unittest

from agentuniverse.agent.action.tool.common_tool import NgramSuggesterTool
from agentuniverse.agent.action.tool.common_tool.ngram_suggester_tool import (
    NgramSuggesterTool as DirectNgramSuggesterTool,
)

# --------------------------------------------------------------------- #
# Hand-computed corpora and ground truths
# --------------------------------------------------------------------- #
#
# Corpus A: "The cat sat. The cat ran. The dog sat." (n=2, lowercased)
#
# Sentences (lowercased): [the cat sat] [the cat ran] [the dog sat]
# Each padded for n=2: [<START>, t1, t2, t3, <END>]; windows of two:
#   (<START>, the) x3   (the, cat) x2   (the, dog) x1
#   (cat, sat) x1       (cat, ran) x1   (dog, sat) x1
#   (sat, <END>) x2     (ran, <END>) x1
CORPUS_A = "The cat sat. The cat ran. The dog sat."
TABLE_A = {
    "<START>": [["the", 3, 1.0]],
    "cat": [["ran", 1, 0.5], ["sat", 1, 0.5]],
    "dog": [["sat", 1, 1.0]],
    "ran": [["<END>", 1, 1.0]],
    "sat": [["<END>", 2, 1.0]],
    "the": [["cat", 2, 2 / 3], ["dog", 1, 1 / 3]],
}

# Corpus B: "A b a. A c." (n=1, lowercased) — every token is a
# continuation of the empty context; <END> closes each sentence.
CORPUS_B = "A b a. A c."
TABLE_B = {
    "": [["a", 3, 3 / 7], ["<END>", 2, 2 / 7], ["b", 1, 1 / 7], ["c", 1, 1 / 7]]
}

# Corpus C: "a b c d. a b c e." (n=3) — sentences are padded with two
# <START> symbols: [<START>, <START>, a, b, c, d, <END>].
CORPUS_C = "a b c d. a b c e."
TABLE_C = {
    "<START> <START>": [["a", 2, 1.0]],
    "<START> a": [["b", 2, 1.0]],
    "a b": [["c", 2, 1.0]],
    "b c": [["d", 1, 0.5], ["e", 1, 0.5]],
    "c d": [["<END>", 1, 1.0]],
    "c e": [["<END>", 1, 1.0]],
}

# Perplexity-lite model: "the cat sat. the cat ran." (n=2, lowercased).
# Contexts: <START>->the x2; the->cat x2; cat->{ran,sat}; sat-><END>;
# ran-><END>. Vocabulary V = {the, cat, sat, ran, <END>} = 5.
PERPLEXITY_MODEL_TEXT = "the cat sat. the cat ran."


class NgramSuggesterToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib NgramSuggesterTool."""

    def setUp(self) -> None:
        self.tool = NgramSuggesterTool()

    # ------------------------------------------------------------------ #
    # model mode
    # ------------------------------------------------------------------ #

    def test_model_bigram_hand_computed_table(self) -> None:
        result = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        self.assertEqual(result["mode"], "model")
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["lowercase"], True)
        self.assertEqual(result["min_token_length"], 1)
        self.assertEqual(result["top_k"], 10)
        self.assertEqual(result["total_contexts"], 6)
        self.assertEqual(result["total_continuations"], 12)
        self.assertEqual(result["vocabulary_size"], 6)
        self.assertEqual(result["truncated_contexts"], 0)
        self.assertEqual(result["table"], TABLE_A)

    def test_model_probabilities_sum_to_one_per_context(self) -> None:
        # Property: with top_k large enough to retain every row, the
        # probabilities of each context sum to exactly 1.
        result = self.tool.execute(
            mode="model", text=CORPUS_A, n=2, lowercase=True, top_k=1000
        )
        self.assertTrue(result["table"])
        for context, rows in result["table"].items():
            self.assertAlmostEqual(
                sum(row[2] for row in rows), 1.0, places=12,
                msg=f"context {context!r} probabilities do not sum to 1",
            )
        # ... and the same property holds for the unigram and trigram
        # tables of their respective corpora.
        for n, corpus in ((1, CORPUS_B), (3, CORPUS_C)):
            model = self.tool.execute(mode="model", text=corpus, n=n)
            for context, rows in model["table"].items():
                self.assertAlmostEqual(
                    sum(row[2] for row in rows), 1.0, places=12
                )

    def test_model_unigram_empty_context(self) -> None:
        result = self.tool.execute(mode="model", text=CORPUS_B, n=1, lowercase=True)
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["total_contexts"], 1)
        self.assertEqual(result["total_continuations"], 7)
        self.assertEqual(result["vocabulary_size"], 4)
        self.assertEqual(result["table"], TABLE_B)

    def test_model_trigram_double_start_padding(self) -> None:
        result = self.tool.execute(mode="model", text=CORPUS_C, n=3)
        self.assertEqual(result["total_contexts"], 6)
        self.assertEqual(result["total_continuations"], 10)
        self.assertEqual(result["vocabulary_size"], 6)
        self.assertEqual(result["table"], TABLE_C)

    def test_model_no_lowercase_by_default(self) -> None:
        result = self.tool.execute(mode="model", text="The the THE", n=1)
        self.assertEqual(result["lowercase"], False)
        # ASCII order of the tie-broken rows: "<END>" < "THE" < "The" < "the".
        self.assertEqual(
            result["table"],
            {
                "": [
                    ["<END>", 1, 0.25],
                    ["THE", 1, 0.25],
                    ["The", 1, 0.25],
                    ["the", 1, 0.25],
                ]
            },
        )

    def test_model_min_token_length_filter(self) -> None:
        # "on" (2 chars) and "a" (1 char) are dropped before modeling:
        # surviving token stream is [the, cat, sat, mat].
        result = self.tool.execute(
            mode="model",
            text="the cat sat on a mat",
            n=2,
            min_token_length=3,
        )
        self.assertEqual(result["min_token_length"], 3)
        self.assertEqual(result["total_continuations"], 5)
        self.assertEqual(result["vocabulary_size"], 5)
        self.assertEqual(result["table"]["<START>"], [["the", 1, 1.0]])
        self.assertEqual(result["table"]["sat"], [["mat", 1, 1.0]])
        self.assertEqual(result["table"]["mat"], [["<END>", 1, 1.0]])
        self.assertNotIn("on", result["table"])
        self.assertNotIn("a", result["table"])

    def test_model_filter_removing_every_token_yields_empty_table(self) -> None:
        result = self.tool.execute(
            mode="model", text="a bb", n=2, min_token_length=5
        )
        self.assertEqual(result["table"], {})
        self.assertEqual(result["total_contexts"], 0)
        self.assertEqual(result["total_continuations"], 0)
        self.assertEqual(result["vocabulary_size"], 0)

    def test_model_cjk_sentence_separators(self) -> None:
        # "。" and "！" end sentences; whitespace splitting keeps each
        # unspaced CJK run as one token.
        result = self.tool.execute(mode="model", text="你好世界。你好！", n=1)
        self.assertEqual(
            result["table"],
            {
                "": [
                    ["<END>", 2, 0.5],
                    ["你好", 1, 0.25],
                    ["你好世界", 1, 0.25],
                ]
            },
        )
        self.assertEqual(result["total_continuations"], 4)
        self.assertEqual(result["vocabulary_size"], 3)

    def test_model_top_k_truncates_and_reports_it(self) -> None:
        # Five sentences "c a." ... "c f.": context "c" has 5 distinct
        # continuations (a, b, d, e, f), so top_k=2 truncates exactly
        # that one context; <START> -> c keeps a single row.
        corpus = "c a. c b. c d. c e. c f."
        result = self.tool.execute(mode="model", text=corpus, n=2, top_k=2)
        self.assertEqual(result["truncated_contexts"], 1)
        self.assertEqual(result["table"]["<START>"], [["c", 5, 1.0]])
        # Ties break alphabetically: the retained rows are a and b.
        self.assertEqual(
            result["table"]["c"], [["a", 1, 0.2], ["b", 1, 0.2]]
        )
        # Every context still observes its full continuation mass:
        # 3 observations per sentence x 5 sentences.
        self.assertEqual(result["total_continuations"], 15)

    def test_model_deterministic(self) -> None:
        first = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        second = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # next mode
    # ------------------------------------------------------------------ #

    def test_next_hit_for_frequent_context(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        result = self.tool.execute(mode="next", model=model, context="the")
        self.assertEqual(result["mode"], "next")
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["context"], "the")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], [["cat", 2, 2 / 3], ["dog", 1, 1 / 3]])
        self.assertEqual(result["total_count"], 3)

    def test_next_hit_tie_broken_alphabetically(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        result = self.tool.execute(mode="next", model=model, context="cat")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], [["ran", 1, 0.5], ["sat", 1, 0.5]])
        self.assertEqual(result["total_count"], 2)

    def test_next_normalizes_whitespace_and_case(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        result = self.tool.execute(mode="next", model=model, context="  The  ")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["context"], "the")
        self.assertEqual(result["total_count"], 3)

    def test_next_unigram_empty_context(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_B, n=1, lowercase=True)
        result = self.tool.execute(mode="next", model=model, context="")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], TABLE_B[""])
        self.assertEqual(result["total_count"], 7)

    def test_next_trigram_start_context(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_C, n=3)
        result = self.tool.execute(mode="next", model=model, context="<START> a")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], [["b", 2, 1.0]])
        branching = self.tool.execute(mode="next", model=model, context="b c")
        self.assertEqual(branching["candidates"], [["d", 1, 0.5], ["e", 1, 0.5]])

    def test_next_unseen_context_structured_note(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        result = self.tool.execute(mode="next", model=model, context="zebra")
        self.assertEqual(result["mode"], "next")
        self.assertFalse(result["context_seen"])
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["total_count"], 0)
        self.assertEqual(result["note"]["type"], "unseen_context")
        self.assertIn("zebra", result["note"]["message"])

    def test_next_accepts_model_as_json_string(self) -> None:
        model = self.tool.execute(mode="model", text=CORPUS_A, n=2, lowercase=True)
        as_string = json.dumps(model)
        result = self.tool.execute(mode="next", model=as_string, context="the")
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], [["cat", 2, 2 / 3], ["dog", 1, 1 / 3]])
        # A JSON string of the model round-trips to the same candidates
        # as the dict form.
        dict_result = self.tool.execute(mode="next", model=model, context="the")
        self.assertEqual(result["candidates"], dict_result["candidates"])

    # ------------------------------------------------------------------ #
    # char_ngrams mode
    # ------------------------------------------------------------------ #

    def test_char_ngrams_within_words(self) -> None:
        result = self.tool.execute(mode="char_ngrams", text="aba ab", n=2)
        self.assertEqual(result["mode"], "char_ngrams")
        self.assertEqual(result["n"], 2)
        self.assertFalse(result["cross_word"])
        self.assertEqual(result["total_ngrams"], 3)
        self.assertEqual(result["distinct_ngrams"], 2)
        self.assertEqual(result["table"], [["ab", 2, 2 / 3], ["ba", 1, 1 / 3]])

    def test_char_ngrams_cross_word_includes_spaces(self) -> None:
        result = self.tool.execute(
            mode="char_ngrams", text="aba ab", n=2, cross_word=True
        )
        self.assertTrue(result["cross_word"])
        self.assertEqual(result["total_ngrams"], 5)
        self.assertEqual(result["distinct_ngrams"], 4)
        # "aba ab" -> ab, ba, "a ", " a", ab; ASCII order breaks the
        # count-1 tie: " a" < "a " < "ba".
        self.assertEqual(
            result["table"],
            [["ab", 2, 0.4], [" a", 1, 0.2], ["a ", 1, 0.2], ["ba", 1, 0.2]],
        )

    def test_char_ngrams_cross_word_normalizes_whitespace_runs(self) -> None:
        result = self.tool.execute(
            mode="char_ngrams", text="ab  cd", n=2, cross_word=True
        )
        # Normalized to "ab cd": ab, "b ", " c", cd.
        self.assertEqual(result["total_ngrams"], 4)
        self.assertEqual(result["distinct_ngrams"], 4)

    def test_char_ngrams_words_shorter_than_n_contribute_nothing(self) -> None:
        result = self.tool.execute(mode="char_ngrams", text="a bb", n=3)
        self.assertEqual(result["total_ngrams"], 0)
        self.assertEqual(result["distinct_ngrams"], 0)
        self.assertEqual(result["table"], [])

    def test_char_ngrams_top_k_truncates_but_keeps_full_totals(self) -> None:
        result = self.tool.execute(mode="char_ngrams", text="abcabc", n=2, top_k=2)
        # abcabc -> ab, bc, ca, ab, bc (5 n-grams, 3 distinct); the top-2
        # table keeps count-desc then alpha order but the totals count
        # every n-gram observed.
        self.assertEqual(result["total_ngrams"], 5)
        self.assertEqual(result["distinct_ngrams"], 3)
        self.assertEqual(result["table"], [["ab", 2, 0.4], ["bc", 2, 0.4]])

    # ------------------------------------------------------------------ #
    # perplexity-lite mode (Laplace-smoothed NLL, hand-verified)
    # ------------------------------------------------------------------ #

    def _perplexity_model(self) -> dict:
        return self.tool.execute(
            mode="model", text=PERPLEXITY_MODEL_TEXT, n=2, lowercase=True
        )

    def test_perplexity_lite_all_seen_continuations(self) -> None:
        # "the cat sat" under the hand-built model:
        #   (<START>, the) p=1    (the, cat) p=1
        #   (cat, sat)    p=0.5   (sat, <END>) p=1
        # average NLL = -ln(0.5)/4 = ln(2)/4.
        result = self.tool.execute(
            mode="perplexity-lite",
            text="the cat sat",
            model=self._perplexity_model(),
        )
        self.assertEqual(result["mode"], "perplexity-lite")
        self.assertEqual(result["num_continuations"], 4)
        self.assertEqual(result["num_seen"], 4)
        self.assertEqual(result["num_unseen"], 0)
        self.assertEqual(result["vocabulary_size"], 5)
        self.assertAlmostEqual(
            result["average_neg_log_prob"], math.log(2) / 4, places=12
        )
        self.assertEqual(result["note"]["type"], "laplace_smoothed_nll")

    def test_perplexity_lite_laplace_arithmetic_hand_verified(self) -> None:
        # Two sentences, 8 continuation events, 3 of them unseen:
        #   S1 "the dog barked":
        #     (<START>, the) p=1                      (seen)
        #     (the, dog)     1/(2+5+1)=1/8 (seen ctx C=2, unseen word)
        #     (dog, barked)  1/(5+1)=1/6   (unseen context)
        #     (barked, END)  1/(5+1)=1/6   (unseen context)
        #   S2 "the cat sat":
        #     (<START>, the) p=1, (the, cat) p=1, (cat, sat) p=0.5,
        #     (sat, END) p=1                              (all seen)
        # average NLL = (ln2 + ln8 + ln6 + ln6) / 8.
        expected = (math.log(2) + math.log(8) + 2 * math.log(6)) / 8
        result = self.tool.execute(
            mode="perplexity-lite",
            text="the dog barked. the cat sat",
            model=self._perplexity_model(),
        )
        self.assertEqual(result["num_continuations"], 8)
        self.assertEqual(result["num_seen"], 5)
        self.assertEqual(result["num_unseen"], 3)
        self.assertAlmostEqual(
            result["average_neg_log_prob"], expected, places=12
        )

    def test_perplexity_lite_single_laplace_terms(self) -> None:
        # "the dog": (<START>, the) p=1 (seen);
        # (the, dog) p=1/(2+5+1)=1/8; (dog, <END>) p=1/(5+1)=1/6.
        expected = (math.log(8) + math.log(6)) / 3
        result = self.tool.execute(
            mode="perplexity-lite",
            text="the dog",
            model=self._perplexity_model(),
        )
        self.assertEqual(result["num_continuations"], 3)
        self.assertEqual(result["num_seen"], 1)
        self.assertEqual(result["num_unseen"], 2)
        self.assertAlmostEqual(
            result["average_neg_log_prob"], expected, places=12
        )

    def test_perplexity_lite_unigram_model(self) -> None:
        # Unigram model of "A b a. A c." lowercased (V=4: a, b, c,
        # <END>); the text "a b" is one sentence, so its events are
        # ("", a) p=3/7, ("", b) p=1/7 and the sentence-closing
        # ("", <END>) p=2/7 — all seen.
        model = self.tool.execute(mode="model", text=CORPUS_B, n=1, lowercase=True)
        result = self.tool.execute(mode="perplexity-lite", text="a b", model=model)
        self.assertEqual(result["num_continuations"], 3)
        self.assertEqual(result["num_seen"], 3)
        self.assertEqual(result["num_unseen"], 0)
        self.assertAlmostEqual(
            result["average_neg_log_prob"],
            (math.log(7 / 3) + math.log(7) + math.log(7 / 2)) / 3,
            places=12,
        )

    def test_perplexity_lite_derives_vocabulary_when_absent(self) -> None:
        # A minimal hand-written model without vocabulary_size: V is
        # derived from the retained rows (cat, dog -> V=2).
        model = {
            "n": 2,
            "lowercase": True,
            "table": {"the": [["cat", 1, 0.5], ["dog", 1, 0.5]]},
        }
        # "the cat" produces three continuations:
        #   (<START>, the) unseen context   -> 1/(V+1) = 1/3
        #   (the, cat)     seen             -> p = 0.5
        #   (cat, <END>)  unseen context    -> 1/(V+1) = 1/3
        result = self.tool.execute(
            mode="perplexity-lite", text="the cat", model=model
        )
        self.assertEqual(result["vocabulary_size"], 2)
        self.assertEqual(result["num_seen"], 1)
        self.assertEqual(result["num_unseen"], 2)
        self.assertAlmostEqual(
            result["average_neg_log_prob"],
            (2 * math.log(3) + math.log(2)) / 3,
            places=12,
        )

    def test_perplexity_lite_accepts_model_as_json_string(self) -> None:
        model = json.dumps(self._perplexity_model())
        result = self.tool.execute(
            mode="perplexity-lite", text="the cat sat", model=model
        )
        self.assertAlmostEqual(
            result["average_neg_log_prob"], math.log(2) / 4, places=12
        )

    def test_perplexity_lite_lowercases_with_model_settings(self) -> None:
        # The model lowercases, so "THE CAT SAT" scores identically to
        # "the cat sat".
        lowered = self.tool.execute(
            mode="perplexity-lite",
            text="the cat sat",
            model=self._perplexity_model(),
        )
        upper = self.tool.execute(
            mode="perplexity-lite",
            text="THE CAT SAT",
            model=self._perplexity_model(),
        )
        self.assertEqual(
            upper["average_neg_log_prob"], lowered["average_neg_log_prob"]
        )

    # ------------------------------------------------------------------ #
    # Model-shape validation (structured content-level errors)
    # ------------------------------------------------------------------ #

    def assert_invalid_model(self, model, fragment: str) -> None:
        for mode, extra in (
            ("next", {"context": "the"}),
            ("perplexity-lite", {"text": "the cat"}),
        ):
            result = self.tool.execute(mode=mode, model=model, **extra)
            self.assertEqual(result["error"]["type"], "invalid_model", msg=mode)
            self.assertIn(fragment, result["error"]["message"], msg=mode)

    def test_next_invalid_json_string_error(self) -> None:
        result = self.tool.execute(mode="next", model="{not json", context="the")
        self.assertEqual(result["error"]["type"], "invalid_model_json")
        self.assertIn("not valid JSON", result["error"]["message"])

    def test_next_json_array_is_invalid_model(self) -> None:
        result = self.tool.execute(mode="next", model="[1, 2]", context="the")
        self.assertEqual(result["error"]["type"], "invalid_model")
        self.assertIn("JSON object", result["error"]["message"])

    def test_model_shape_error_matrix(self) -> None:
        self.assert_invalid_model({"table": {}}, "missing required key")
        self.assert_invalid_model('{"n": "2", "table": {}}', "model['n']")
        self.assert_invalid_model('{"n": 6, "table": {}}', "between 1 and 5")
        self.assert_invalid_model('{"n": 2, "table": []}', "model['table']")
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": "cat"}}', "model['table'][\'the\']"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [["cat"]]}}', "3-item"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [["cat", 0, 1.0]]}}', ">= 1"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [["cat", 1.5, 1.0]]}}', "integers"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [["cat", 1, 1.5]]}}', "(0, 1]"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [[true, 1, 1.0]]}}', "non-empty strings"
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {"the": [["cat", 1, 0.5]]}, "lowercase": "yes"}',
            "model['lowercase']",
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {}, "min_token_length": 0}',
            "model['min_token_length']",
        )
        self.assert_invalid_model(
            '{"n": 2, "table": {}, "vocabulary_size": -1}',
            "model['vocabulary_size']",
        )

    def test_valid_minimal_model_shape_is_accepted(self) -> None:
        result = self.tool.execute(
            mode="next",
            model={"n": 2, "table": {"the": [["cat", 1, 1.0]]}},
            context="the",
        )
        self.assertTrue(result["context_seen"])
        self.assertEqual(result["candidates"], [["cat", 1, 1.0]])

    # ------------------------------------------------------------------ #
    # Parameter validation (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def assert_value_error(self, message_fragment: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as raised:
            self.tool.execute(**kwargs)
        self.assertIn(message_fragment, str(raised.exception))

    def test_unknown_mode_raises(self) -> None:
        self.assert_value_error(
            "mode must be one of", mode="train", text="a", n=2
        )

    def test_model_mode_n_validation(self) -> None:
        for bad_n in (None, 0, 6, True, "2", 2.0):
            self.assert_value_error(
                "n must be an integer", mode="model", text="a b", n=bad_n
            )

    def test_char_ngrams_n_validation(self) -> None:
        for bad_n in (1, 6, None, "3"):
            self.assert_value_error(
                "n must be an integer between 2 and 5",
                mode="char_ngrams",
                text="abc",
                n=bad_n,
            )

    def test_text_validation(self) -> None:
        for bad_text in (None, "", 42, b"bytes", True):
            self.assert_value_error(
                "text must be a non-empty string",
                mode="model",
                text=bad_text,
                n=2,
            )
        self.assert_value_error(
            "exceeds the 100,000-character limit",
            mode="model",
            text="a" * 100_001,
            n=2,
        )

    def test_boolean_flag_validation(self) -> None:
        self.assert_value_error(
            "lowercase must be a boolean",
            mode="model",
            text="a b",
            n=2,
            lowercase="yes",
        )
        self.assert_value_error(
            "cross_word must be a boolean",
            mode="char_ngrams",
            text="abc",
            n=2,
            cross_word=1,
        )

    def test_int_option_validation(self) -> None:
        for bad_len in (0, 51, True, "3", 2.5):
            self.assert_value_error(
                "min_token_length must be an integer",
                mode="model",
                text="a b",
                n=2,
                min_token_length=bad_len,
            )
        for bad_k in (0, 1001, False, "10"):
            self.assert_value_error(
                "top_k must be an integer",
                mode="model",
                text="a b",
                n=2,
                top_k=bad_k,
            )

    def test_next_mode_model_param_validation(self) -> None:
        for bad_model in (None, 42, "", ["n"], True):
            self.assert_value_error(
                "model", mode="next", model=bad_model, context="the"
            )

    def test_next_mode_context_word_count_validation(self) -> None:
        model = {"n": 2, "table": {}}
        self.assert_value_error(
            "context must contain exactly 1 word(s)",
            mode="next",
            model=model,
            context="the cat sat",
        )
        self.assert_value_error(
            "context must contain exactly 1 word(s)",
            mode="next",
            model=model,
            context="",
        )
        self.assert_value_error(
            "context must be a string",
            mode="next",
            model=model,
            context=42,
        )

    def test_perplexity_lite_required_params(self) -> None:
        self.assert_value_error(
            "text must be a non-empty string", mode="perplexity-lite", model={"n": 1, "table": {}}
        )
        self.assert_value_error(
            "model is required", mode="perplexity-lite", text="a b"
        )

    # ------------------------------------------------------------------ #
    # Packaging
    # ------------------------------------------------------------------ #

    def test_importable_from_package_and_module(self) -> None:
        self.assertIs(DirectNgramSuggesterTool, NgramSuggesterTool)

    def test_tool_identity(self) -> None:
        self.assertEqual(self.tool.name, "ngram_suggester_tool")
        self.assertIn("model", self.tool.description)


if __name__ == "__main__":
    unittest.main()
