#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_tokenizer_tool.py

"""Offline unit tests for TokenizerTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic and checked against hand-computed ground truths: the
seven strategies are enumerated by hand for tiny inputs (exact token
strings AND character offsets), the sentence strategy's abbreviation
guards are pinned case by case (Dr. / e.g. / U.S. / initials /
decimals / domains / dot runs / newlines / CJK terminators / bare
punctuation), the lowercase and stopword options are verified to
rewrite token strings and filter tokens without ever moving a span,
the error matrix is exercised parameter by parameter, and the offset
invariant ``text[start:end] == token`` is asserted via span_check over
500 seeded random texts containing CJK, emoji, combining marks and
joiners — zero violations required.
"""

import json
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import TokenizerTool
from agentuniverse.agent.action.tool.common_tool.tokenizer_tool import (
    TokenizerTool as DirectTokenizerTool,
)

ALL_STRATEGIES = (
    "whitespace",
    "word",
    "word_punct",
    "char",
    "char_no_space",
    "sentence",
    "cjk",
)


def rows(tokens):
    """Reduce a token list to comparable (token, start, end) triples."""
    return [(t["token"], t["start"], t["end"]) for t in tokens]


class TokenizerToolGroundTruthTest(unittest.TestCase):
    """Hand-computed ground truths for every strategy."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_package_and_direct_import(self):
        self.assertIs(TokenizerTool, DirectTokenizerTool)
        self.assertEqual(self.tool.name, "tokenizer_tool")
        self.assertEqual(TokenizerTool.MODES, ("tokenize", "span_check", "count"))
        self.assertEqual(TokenizerTool.STRATEGIES, ALL_STRATEGIES)

    def test_whitespace_strategy(self):
        # "The  cat\t sat\n"
        # T0 h1 e2 ' '3 ' '4 c5 a6 t7 \t8 ' '9 s10 a11 t12 \n13
        result = self.tool.execute(
            mode="tokenize", text="The  cat\t sat\n", strategy="whitespace"
        )
        self.assertEqual(
            rows(result["tokens"]),
            [("The", 0, 3), ("cat", 5, 8), ("sat", 10, 13)],
        )
        self.assertEqual(result["token_count"], 3)
        self.assertEqual(result["dropped_stopword_count"], 0)

    def test_word_strategy(self):
        # "Don't panic, it's 42!"
        # D0o1n2'3t4 ' '5 p6..10 ,11 ' '12 i13t14'15s16 ' '17 4(18)2(19) !(20)
        result = self.tool.execute(
            mode="tokenize", text="Don't panic, it's 42!", strategy="word"
        )
        self.assertEqual(
            rows(result["tokens"]),
            [("Don't", 0, 5), ("panic", 6, 11), ("it's", 13, 17), ("42", 18, 20)],
        )

    def test_word_strategy_apostrophe_trimming(self):
        # "'tis 'rock' ''"
        # '0 t1i2s3 '4 '5 r6..9 '10 '11 '12 '13
        # Internal apostrophes stay in the span; leading/trailing ones
        # are excluded, so the all-apostrophe run yields no token.
        result = self.tool.execute(
            mode="tokenize", text="'tis 'rock' ''", strategy="word"
        )
        self.assertEqual(rows(result["tokens"]), [("tis", 1, 4), ("rock", 6, 10)])

    def test_word_strategy_han_run_stays_whole(self):
        # isalnum() covers Han ideographs and no dictionary split is
        # attempted under the plain word rule (use cjk for that).
        result = self.tool.execute(
            mode="tokenize", text="中国abc", strategy="word"
        )
        self.assertEqual(rows(result["tokens"]), [("中国abc", 0, 5)])

    def test_word_punct_strategy(self):
        # "Hello, world! x_1?" — \w keeps underscore inside the run;
        # punctuation is kept as runs of its own.
        # H0..4 ,5 ' '6 w7..11 !12 ' '13 x14 _15 1(16) ?17
        result = self.tool.execute(
            mode="tokenize", text="Hello, world! x_1?", strategy="word_punct"
        )
        self.assertEqual(
            rows(result["tokens"]),
            [
                ("Hello", 0, 5),
                (",", 5, 6),
                ("world", 7, 12),
                ("!", 12, 13),
                ("x_1", 14, 17),
                ("?", 17, 18),
            ],
        )

    def test_word_punct_punctuation_run(self):
        # "What--?!" is one punctuation run (wordpunct semantics).
        result = self.tool.execute(
            mode="tokenize", text="What--?!", strategy="word_punct"
        )
        self.assertEqual(
            rows(result["tokens"]), [("What", 0, 4), ("--?!", 4, 8)]
        )

    def test_char_strategy(self):
        # "a 😀" — the emoji is one code point (astral-plane safe):
        # a0 ' '1 😀2
        result = self.tool.execute(mode="tokenize", text="a 😀", strategy="char")
        self.assertEqual(
            rows(result["tokens"]), [("a", 0, 1), (" ", 1, 2), ("😀", 2, 3)]
        )

    def test_char_no_space_strategy(self):
        result = self.tool.execute(
            mode="tokenize", text="a 😀 b", strategy="char_no_space"
        )
        self.assertEqual(
            rows(result["tokens"]), [("a", 0, 1), ("😀", 2, 3), ("b", 4, 5)]
        )

    def test_char_combining_mark_is_its_own_code_point(self):
        # "e" + U+0301 COMBINING ACUTE ACCENT: two code points, two
        # tokens (grapheme clusters are not fused — documented).
        text = "é"
        self.assertEqual(len(text), 2)
        result = self.tool.execute(mode="tokenize", text=text, strategy="char")
        self.assertEqual(
            rows(result["tokens"]), [("e", 0, 1), ("́", 1, 2)]
        )

    def test_cjk_strategy(self):
        # a0b1c2 中3 d4e5f6 中7 国8
        result = self.tool.execute(
            mode="tokenize", text="abc中def中国", strategy="cjk"
        )
        self.assertEqual(
            rows(result["tokens"]),
            [
                ("abc", 0, 3),
                ("中", 3, 4),
                ("def", 4, 7),
                ("中", 7, 8),
                ("国", 8, 9),
            ],
        )

    def test_cjk_strategy_keeps_contractions(self):
        # d0..3 '4 t5 中6 — the apostrophe is internal, kept in the run.
        result = self.tool.execute(
            mode="tokenize", text="don't中", strategy="cjk"
        )
        self.assertEqual(rows(result["tokens"]), [("don't", 0, 5), ("中", 5, 6)])


class TokenizerToolSentenceTest(unittest.TestCase):
    """The family's conservative segmentation with abbreviation guards."""

    def setUp(self):
        self.tool = TokenizerTool()

    def sentence_rows(self, text):
        result = self.tool.execute(mode="tokenize", text=text, strategy="sentence")
        return rows(result["tokens"])

    def test_plain_sentences(self):
        # "He said. Then left."
        # H0e1 ' '2 s3a4i5d6 .7 ' '8 T9..12 ' '13 l14..17 .18
        self.assertEqual(
            self.sentence_rows("He said. Then left."),
            [("He said.", 0, 8), ("Then left.", 9, 19)],
        )

    def test_abbreviation_doctor(self):
        self.assertEqual(
            self.sentence_rows("Dr. Smith arrived. He ran."),
            [("Dr. Smith arrived.", 0, 18), ("He ran.", 19, 26)],
        )

    def test_abbreviation_eg_etc_keeps_one_sentence(self):
        # Both "e.g." and "etc." are guarded, so the text closes only
        # at the final period: exactly one sentence (0, 34).
        text = "e.g. apples, pears, etc. Next one."
        self.assertEqual(len(text), 34)
        self.assertEqual(self.sentence_rows(text), [(text, 0, 34)])

    def test_initials(self):
        # J. R. R. Tolkien — single letters are guarded.
        text = "J. R. R. Tolkien wrote books."
        self.assertEqual(len(text), 29)
        self.assertEqual(self.sentence_rows(text), [(text, 0, 29)])

    def test_us_abbreviation_and_dot_run(self):
        # "U.S. stocks fell... Then we ate."
        # U0 .1 S2 .3 ' '4 stocks 5..10 ' '11 fell 12..15 .16 .17 .18 ' '19
        # "Then we ate." ends at .31 → span (20, 32).
        self.assertEqual(
            self.sentence_rows("U.S. stocks fell... Then we ate."),
            [("U.S. stocks fell...", 0, 19), ("Then we ate.", 20, 32)],
        )

    def test_decimal_and_domain_internal_dots_guarded(self):
        # "3.14 and example.com work."
        # Both dots are internal (followed by an alphanumeric char):
        # the decimal and the domain stay in one sentence that closes
        # only at the final period after "work".
        text = "3.14 and example.com work."
        self.assertEqual(len(text), 26)
        self.assertEqual(self.sentence_rows(text), [(text, 0, 26)])

    def test_domain_final_period_is_a_boundary(self):
        # "Visit example.com. Then go."
        # The period after "com" is followed by a space and "com" is
        # no abbreviation, so it ends the sentence.
        # V0..4 ' '5 example 6..12 .13 com 14..16 .17 ' '18 Then 19..22
        # ' '23 go 24..25 .26
        self.assertEqual(
            self.sentence_rows("Visit example.com. Then go."),
            [("Visit example.com.", 0, 18), ("Then go.", 19, 27)],
        )

    def test_all_digit_token_before_period_is_guarded(self):
        # The family guard treats an all-digit word run before a
        # period (an enumeration such as "3.") as non-terminal.
        text = "Items: 3. four five."
        self.assertEqual(self.sentence_rows(text), [(text, 0, len(text))])

    def test_newline_flushes(self):
        self.assertEqual(
            self.sentence_rows("One line\nAnother line"),
            [("One line", 0, 8), ("Another line", 9, 21)],
        )

    def test_cjk_terminators(self):
        # 你0 好1 。2 世3 界4 ！5
        self.assertEqual(
            self.sentence_rows("你好。世界！"),
            [("你好。", 0, 3), ("世界！", 3, 6)],
        )

    def test_ellipsis_run_boundary(self):
        # w0a1i2t3 .4.5.6 ' '7 what? 8..12
        self.assertEqual(
            self.sentence_rows("wait... what?"),
            [("wait...", 0, 7), ("what?", 8, 13)],
        )

    def test_no_trailing_terminator(self):
        self.assertEqual(
            self.sentence_rows("  End without period  "),
            [("End without period", 2, 20)],
        )

    def test_bare_punctuation_dropped(self):
        self.assertEqual(self.sentence_rows("!!!"), [])
        self.assertEqual(self.sentence_rows("。。。"), [])
        self.assertEqual(self.sentence_rows("...!?!"), [])


class TokenizerToolOptionsTest(unittest.TestCase):
    """lowercase / drop_stopwords interplay — spans never move."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_lowercase_rewrites_token_not_span(self):
        text = "Don't PANIC"
        plain = self.tool.execute(
            mode="tokenize", text=text, strategy="word"
        )
        lowered = self.tool.execute(
            mode="tokenize", text=text, strategy="word", lowercase=True
        )
        self.assertEqual(
            rows(plain["tokens"]),
            [("Don't", 0, 5), ("PANIC", 6, 11)],
        )
        self.assertEqual(
            rows(lowered["tokens"]),
            [("don't", 0, 5), ("panic", 6, 11)],
        )
        self.assertTrue(lowered["lowercase"])
        # The offset invariant under lowercase: the span still slices
        # the original text and lowercases to the token.
        for entry in lowered["tokens"]:
            self.assertEqual(text[entry["start"] : entry["end"]].lower(), entry["token"])

    def test_stopwords_case_sensitive_without_lowercase(self):
        # EN list is lowercase: "The" survives, "and"/"the" drop.
        result = self.tool.execute(
            mode="tokenize",
            text="The cat and the dog",
            strategy="word",
            drop_stopwords=True,
        )
        self.assertEqual(
            rows(result["tokens"]),
            [("The", 0, 3), ("cat", 4, 7), ("dog", 16, 19)],
        )
        self.assertEqual(result["dropped_stopword_count"], 2)

    def test_stopwords_lowercased_with_lowercase(self):
        # "The CAT and the dog" + lowercase + drop → cat, dog remain
        # with lowercased token fields and original spans.
        result = self.tool.execute(
            mode="tokenize",
            text="The CAT and the dog",
            strategy="word",
            lowercase=True,
            drop_stopwords=True,
        )
        self.assertEqual(
            rows(result["tokens"]), [("cat", 4, 7), ("dog", 16, 19)]
        )
        self.assertEqual(result["dropped_stopword_count"], 3)

    def test_chinese_stopwords_single_characters(self):
        # 我0 是1 中2 国3 人4 — the ZH list is single-character,
        # matching the cjk strategy's per-ideograph tokens; 我/是/中
        # are stopwords, 国/人 survive.
        result = self.tool.execute(
            mode="tokenize", text="我是中国人", strategy="cjk", drop_stopwords=True
        )
        self.assertEqual(
            rows(result["tokens"]), [("国", 3, 4), ("人", 4, 5)]
        )
        self.assertEqual(result["dropped_stopword_count"], 3)

    def test_stopword_drop_on_char_strategy(self):
        # "a b" char-by-char: "a" is a stopword, the space is not.
        result = self.tool.execute(
            mode="tokenize", text="a b", strategy="char", drop_stopwords=True
        )
        self.assertEqual(
            rows(result["tokens"]), [(" ", 1, 2), ("b", 2, 3)]
        )
        self.assertEqual(result["dropped_stopword_count"], 1)

    def test_strategy_without_tokens_returns_empty_not_error(self):
        for strategy, expected in (
            ("whitespace", 0),
            ("word", 0),
            ("word_punct", 0),
            ("char", 3),
            ("char_no_space", 0),
            ("sentence", 0),
            ("cjk", 0),
        ):
            result = self.tool.execute(
                mode="tokenize", text="   ", strategy=strategy
            )
            self.assertEqual(result["token_count"], expected)
            self.assertEqual(len(result["tokens"]), expected)
            self.assertEqual(result["dropped_stopword_count"], 0)

    def test_result_context_fields(self):
        result = self.tool.execute(
            mode="tokenize",
            text="Hello",
            strategy="whitespace",
            lowercase=False,
            drop_stopwords=False,
        )
        self.assertEqual(result["mode"], "tokenize")
        self.assertEqual(result["strategy"], "whitespace")
        self.assertFalse(result["lowercase"])
        self.assertFalse(result["drop_stopwords"])


class TokenizerToolCountTest(unittest.TestCase):
    """count mode — totals, type folding, per-strategy comparison."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_token_and_type_counts(self):
        result = self.tool.execute(
            mode="count", text="The cat cat CAT", strategy="word"
        )
        self.assertEqual(result["token_count"], 4)
        self.assertEqual(result["type_count"], 3)  # The, cat, CAT

    def test_lowercase_folds_types(self):
        result = self.tool.execute(
            mode="count", text="The cat cat CAT", strategy="word", lowercase=True
        )
        self.assertEqual(result["token_count"], 4)
        self.assertEqual(result["type_count"], 2)  # the, cat

    def test_stopwords_affect_counts(self):
        result = self.tool.execute(
            mode="count",
            text="The cat and the dog",
            strategy="word",
            lowercase=True,
            drop_stopwords=True,
        )
        self.assertEqual(result["token_count"], 2)
        self.assertEqual(result["type_count"], 2)

    def test_default_strategy_is_word(self):
        result = self.tool.execute(mode="count", text="one two two")
        self.assertEqual(result["strategy"], "word")
        self.assertEqual(result["token_count"], 3)
        self.assertEqual(result["type_count"], 2)

    def test_compare_strategies_table(self):
        text = "The cat sat."
        result = self.tool.execute(
            mode="count", text=text, strategy="word", compare_strategies=True
        )
        self.assertEqual(
            sorted(result["compare"].keys()), sorted(ALL_STRATEGIES)
        )
        # char counts every code point, char_no_space drops the two
        # spaces, sentence yields exactly one sentence.
        self.assertEqual(result["compare"]["char"]["token_count"], len(text))
        self.assertEqual(
            result["compare"]["char_no_space"]["token_count"], len(text) - 2
        )
        self.assertEqual(result["compare"]["sentence"]["token_count"], 1)
        self.assertEqual(result["compare"]["word"]["token_count"], 3)

    def test_compare_absent_without_flag(self):
        result = self.tool.execute(mode="count", text="hello world")
        self.assertNotIn("compare", result)
        self.assertEqual(result["token_count"], 2)

    def test_count_on_tokenless_text(self):
        result = self.tool.execute(
            mode="count", text="   ", strategy="char_no_space"
        )
        self.assertEqual(result["token_count"], 0)
        self.assertEqual(result["type_count"], 0)


class TokenizerToolSpanCheckTest(unittest.TestCase):
    """span_check — the invariant helper."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_all_strategies_by_default(self):
        result = self.tool.execute(mode="span_check", text="Hello 世界 😀!")
        self.assertEqual(result["mode"], "span_check")
        self.assertEqual(result["strategy"], "all")
        self.assertEqual(result["text_length"], 11)
        self.assertEqual(result["strategies_checked"], list(ALL_STRATEGIES))
        self.assertTrue(result["ok"])
        self.assertEqual(result["violation_count"], 0)
        self.assertEqual(result["violations"], [])
        self.assertGreater(result["tokens_checked"], 0)

    def test_single_strategy(self):
        result = self.tool.execute(
            mode="span_check", text="abc中def", strategy="cjk"
        )
        self.assertEqual(result["strategies_checked"], ["cjk"])
        self.assertEqual(result["tokens_checked"], 3)
        self.assertTrue(result["ok"])

    def test_seeded_random_texts_zero_violations(self):
        alphabet = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
            " \t\n"
            ".!?,;:'\"-_"
            "中国日本"
            "。！？…"
            "😀🎉"
            "é́"  # e + COMBINING ACUTE ACCENT
            "‍"  # ZERO WIDTH JOINER
            "#$%"
            "’"  # curly apostrophe (a separator here)
        )
        rng = random.Random(20261021)
        for _ in range(500):
            text = "".join(rng.choice(alphabet) for _ in range(80))
            result = self.tool.execute(mode="span_check", text=text)
            self.assertTrue(result["ok"], text)
            self.assertEqual(result["violation_count"], 0, text)
            self.assertEqual(result["violations"], [], text)
            # Independent invariant re-check on the raw word and
            # sentence streams (not just trusting span_check itself).
            for strategy in ("word", "sentence", "cjk", "word_punct"):
                previous_end = 0
                for entry in self.tool.execute(
                    mode="tokenize", text=text, strategy=strategy
                )["tokens"]:
                    self.assertGreater(entry["end"], entry["start"])
                    self.assertGreaterEqual(entry["start"], previous_end)
                    self.assertEqual(
                        text[entry["start"] : entry["end"]], entry["token"]
                    )
                    previous_end = entry["end"]

    def test_seeded_random_texts_count_works(self):
        rng = random.Random(20261022)
        alphabet = "ab 中。😀.'!\n"
        for _ in range(50):
            text = "".join(rng.choice(alphabet) for _ in range(40))
            result = self.tool.execute(
                mode="count",
                text=text,
                strategy="char",
                compare_strategies=True,
            )
            self.assertEqual(
                sorted(result["compare"].keys()), sorted(ALL_STRATEGIES)
            )
            self.assertEqual(
                result["compare"]["char"]["token_count"], len(text)
            )


class TokenizerToolErrorTest(unittest.TestCase):
    """Strict validation matrix — ValueError before any computation."""

    def setUp(self):
        self.tool = TokenizerTool()

    def assert_invalid(self, **kwargs):
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(**kwargs)
        self.assertIn("tokenizer_tool:", str(caught.exception))
        return caught.exception

    def test_unknown_mode(self):
        self.assert_invalid(mode="tokens", text="hi", strategy="word")
        self.assert_invalid(mode=None, text="hi", strategy="word")
        self.assert_invalid(mode=123, text="hi", strategy="word")

    def test_text_required_validated(self):
        for bad in (None, "", 123, True, ["words"], {"k": 1}):
            self.assert_invalid(mode="tokenize", text=bad, strategy="word")
            self.assert_invalid(mode="span_check", text=bad)
            self.assert_invalid(mode="count", text=bad)

    def test_text_too_long(self):
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(
                mode="tokenize", text="x" * 100_001, strategy="word"
            )
        self.assertIn("100,000-character limit", str(caught.exception))

    def test_strategy_required_for_tokenize(self):
        self.assert_invalid(mode="tokenize", text="hi", strategy=None)

    def test_unknown_or_mistyped_strategy(self):
        for bad in ("words", "CHAR", "nltk", 123, True):
            self.assert_invalid(mode="tokenize", text="hi", strategy=bad)
            self.assert_invalid(mode="span_check", text="hi", strategy=bad)
            self.assert_invalid(mode="count", text="hi", strategy=bad)

    def test_boolean_flags(self):
        for bad in ("yes", 1, 0, [True]):
            self.assert_invalid(
                mode="tokenize", text="hi", strategy="word", lowercase=bad
            )
            self.assert_invalid(
                mode="tokenize", text="hi", strategy="word", drop_stopwords=bad
            )
            self.assert_invalid(
                mode="count", text="hi", compare_strategies=bad
            )

    def test_none_flags_mean_defaults(self):
        result = self.tool.execute(
            mode="tokenize",
            text="hi",
            strategy="word",
            lowercase=None,
            drop_stopwords=None,
        )
        self.assertFalse(result["lowercase"])
        self.assertFalse(result["drop_stopwords"])


class TokenizerToolDeterminismTest(unittest.TestCase):
    """Identical calls return identical results."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_tokenize_stable(self):
        text = "Don't panic. It's 42%! 中国 😀"
        first = self.tool.execute(
            mode="tokenize", text=text, strategy="word", drop_stopwords=True
        )
        second = self.tool.execute(
            mode="tokenize", text=text, strategy="word", drop_stopwords=True
        )
        self.assertEqual(json.dumps(first, ensure_ascii=False), json.dumps(second, ensure_ascii=False))

    def test_count_compare_stable(self):
        text = "The cat sat on the mat. The dog sat!"
        first = self.tool.execute(
            mode="count",
            text=text,
            strategy="sentence",
            lowercase=True,
            drop_stopwords=True,
            compare_strategies=True,
        )
        second = self.tool.execute(
            mode="count",
            text=text,
            strategy="sentence",
            lowercase=True,
            drop_stopwords=True,
            compare_strategies=True,
        )
        self.assertEqual(
            json.dumps(first, ensure_ascii=False),
            json.dumps(second, ensure_ascii=False),
        )


class TokenizerToolAstralPlaneTest(unittest.TestCase):
    """Emoji / joined sequences — astral-plane safe."""

    def setUp(self):
        self.tool = TokenizerTool()

    def test_single_emoji_is_a_single_token(self):
        for strategy in ("char", "char_no_space", "word_punct"):
            result = self.tool.execute(
                mode="tokenize", text="😀", strategy=strategy
            )
            self.assertEqual(rows(result["tokens"]), [("😀", 0, 1)])

    def test_emoji_dropped_by_word_strategy(self):
        # Emoji are not alphanumeric — separators under the word rule.
        result = self.tool.execute(mode="tokenize", text="a😀b", strategy="word")
        self.assertEqual(rows(result["tokens"]), [("a", 0, 1), ("b", 2, 3)])

    def test_zwj_family_is_one_word_punct_run(self):
        # MAN ZWJ WOMAN ZWJ GIRL: five code points; ZWJ is neither
        # \w nor \s, so word_punct keeps the whole run as one token.
        text = "👨‍👩‍👧"
        self.assertEqual(len(text), 5)
        result = self.tool.execute(
            mode="tokenize", text=text, strategy="word_punct"
        )
        self.assertEqual(rows(result["tokens"]), [(text, 0, 5)])

    def test_zwj_family_char_strategy_is_five_tokens(self):
        text = "👨‍👩‍👧"
        result = self.tool.execute(mode="tokenize", text=text, strategy="char")
        self.assertEqual(len(result["tokens"]), 5)
        self.assertEqual(
            [(t["start"], t["end"]) for t in result["tokens"]],
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        )


class TokenizerToolAdversarialTest(unittest.TestCase):
    """Pinned adversarial edge cases (all span-consistent by design)."""

    def setUp(self):
        self.tool = TokenizerTool()

    def tokenize(self, text, strategy, **options):
        return rows(
            self.tool.execute(
                mode="tokenize", text=text, strategy=strategy, **options
            )["tokens"]
        )

    def test_rock_n_roll_is_one_token(self):
        self.assertEqual(
            self.tokenize("rock'n'roll", "word"), [("rock'n'roll", 0, 11)]
        )
        self.assertEqual(
            self.tokenize("y'all'd've", "word"), [("y'all'd've", 0, 10)]
        )

    def test_curly_apostrophe_is_a_separator(self):
        text = "don’t"
        self.assertEqual(
            self.tokenize(text, "word"), [("don", 0, 3), ("t", 4, 5)]
        )

    def test_underscore_separator_only_in_word_strategy(self):
        self.assertEqual(
            self.tokenize("snake_case_x", "word"),
            [("snake", 0, 5), ("case", 6, 10), ("x", 11, 12)],
        )
        self.assertEqual(
            self.tokenize("snake_case_x", "word_punct"),
            [("snake_case_x", 0, 12)],
        )

    def test_fullwidth_digits_are_word_characters(self):
        text = "共１２３个。Next"
        self.assertEqual(
            self.tokenize("１２３ＡＢ", "word"), [("１２３ＡＢ", 0, 5)]
        )
        self.assertEqual(
            self.tokenize(text, "sentence"),
            [("共１２３个。", 0, 6), ("Next", 6, 10)],
        )
        self.assertEqual(
            self.tokenize("第１２３。Then go.", "sentence"),
            [("第１２３。", 0, 5), ("Then go.", 5, 13)],
        )

    def test_fullwidth_digits_not_guarded_before_latin_period(self):
        self.assertEqual(
            self.tokenize("共１２３. Then go.", "sentence"),
            [("共１２３.", 0, 5), ("Then go.", 6, 14)],
        )
        self.assertEqual(
            self.tokenize("共1２3. Then go.", "sentence"),
            [("共1２3. Then go.", 0, 14)],
        )

    def test_skin_tone_modifier_stays_in_word_punct_run(self):
        text = "👍🏽"
        self.assertEqual(len(text), 2)
        self.assertEqual(self.tokenize(text, "word_punct"), [(text, 0, 2)])
        self.assertEqual(
            self.tokenize(text, "char"), [("👍", 0, 1), ("🏽", 1, 2)]
        )

    def test_rtl_with_embedded_ltr(self):
        text = "قال hello‎ 世界"
        for strategy in ALL_STRATEGIES:
            result = self.tool.execute(
                mode="tokenize", text=text, strategy=strategy
            )
            for entry in result["tokens"]:
                self.assertEqual(
                    text[entry["start"] : entry["end"]], entry["token"]
                )
        check = self.tool.execute(mode="span_check", text=text)
        self.assertTrue(check["ok"])
        self.assertEqual(
            self.tokenize(text, "word"),
            [("قال", 0, 3), ("hello", 4, 9), ("世界", 11, 13)],
        )

    def test_unicode_spaces_separate_runs(self):
        for space in ("\xa0", "\u3000", "\u202f"):
            text = "a" + space + "b"
            self.assertEqual(self.tokenize(text, "whitespace"), [("a", 0, 1), ("b", 2, 3)])
            self.assertEqual(self.tokenize(text, "word"), [("a", 0, 1), ("b", 2, 3)])
            self.assertEqual(self.tokenize(text, "char_no_space"), [("a", 0, 1), ("b", 2, 3)])
            self.assertTrue(
                self.tool.execute(mode="span_check", text=text)["ok"]
            )

    def test_whitespace_tokens_match_str_split(self):
        text = "The  cat\t sat\n on  the mat"
        tokens = self.tokenize(text, "whitespace")
        self.assertEqual([t[0] for t in tokens], text.split())
        for token, start, end in tokens:
            self.assertEqual(text[start:end], token)

    def test_text_length_limit_boundary(self):
        result = self.tool.execute(
            mode="count", text="x" * 100_000, strategy="word"
        )
        self.assertEqual(result["token_count"], 1)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="count", text="x" * 100_001, strategy="word"
            )

    def test_terminal_run_extra_marks_dropped_by_sentence(self):
        self.assertEqual(
            self.tokenize("真的吗？！", "sentence"), [("真的吗？", 0, 4)]
        )
        self.assertEqual(
            self.tokenize("Wow!!! Great.", "sentence"),
            [("Wow!", 0, 4), ("Great.", 7, 13)],
        )

    def test_stopword_order_is_drop_on_comparison_form(self):
        text = "The AND the"
        self.assertEqual(
            self.tokenize(text, "word", drop_stopwords=True),
            [("The", 0, 3), ("AND", 4, 7)],
        )
        self.assertEqual(
            self.tokenize(
                text, "word", lowercase=True, drop_stopwords=True
            ),
            [],
        )

    def test_cjk_mixed_with_latin_and_digits(self):
        self.assertEqual(
            self.tokenize("abc123中文456def", "word"),
            [("abc123中文456def", 0, 14)],
        )
        self.assertEqual(
            self.tokenize("abc123中文456def", "cjk"),
            [
                ("abc123", 0, 6),
                ("中", 6, 7),
                ("文", 7, 8),
                ("456def", 8, 14),
            ],
        )


if __name__ == "__main__":
    unittest.main()
