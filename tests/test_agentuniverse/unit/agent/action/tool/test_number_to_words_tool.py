#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_number_to_words_tool.py

"""Offline unit tests for NumberToWordsTool.

The tool is built purely on the standard library (re + arithmetic) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: the word renderings are checked against
literal expected strings written out independently (not produced by
the tool under test), the parsers against exact values, and both
directions against exhaustive and sampled round trips. The only
property-style checks — round trips over a bounded value set with a
fixed random seed — are also fully deterministic.
"""

import random
import unittest

from agentuniverse.agent.action.tool.common_tool import NumberToWordsTool
from agentuniverse.agent.action.tool.common_tool.number_to_words_tool import (
    NumberToWordsTool as DirectNumberToWordsTool,
)

# --------------------------------------------------------------------- #
# Literal ground-truth pairs (hand-written, independent of the tool)
# --------------------------------------------------------------------- #
EN_CASES = [
    (0, "zero"),
    (7, "seven"),
    (10, "ten"),
    (13, "thirteen"),
    (18, "eighteen"),
    (20, "twenty"),
    (21, "twenty-one"),
    (42, "forty-two"),
    (99, "ninety-nine"),
    (100, "one hundred"),
    (101, "one hundred one"),
    (105, "one hundred five"),
    (110, "one hundred ten"),
    (123, "one hundred twenty-three"),
    (999, "nine hundred ninety-nine"),
    (1000, "one thousand"),
    (1001, "one thousand one"),
    (1010, "one thousand ten"),
    (1100, "one thousand one hundred"),
    (1234, "one thousand two hundred thirty-four"),
    (2000, "two thousand"),
    (10000, "ten thousand"),
    (10001, "ten thousand one"),
    (100000, "one hundred thousand"),
    (100001, "one hundred thousand one"),
    (123456, "one hundred twenty-three thousand four hundred fifty-six"),
    (1000000, "one million"),
    (10000000, "ten million"),
    (100000000, "one hundred million"),
    (100000001, "one hundred million one"),
    (
        123456789,
        "one hundred twenty-three million four hundred fifty-six "
        "thousand seven hundred eighty-nine",
    ),
    (1000000000, "one billion"),
    (
        9876543210,
        "nine billion eight hundred seventy-six million five hundred "
        "forty-three thousand two hundred ten",
    ),
    (
        999999999999,
        "nine hundred ninety-nine billion nine hundred ninety-nine "
        "million nine hundred ninety-nine thousand nine hundred "
        "ninety-nine",
    ),
    (-42, "minus forty-two"),
]

ZH_CASES = [
    (0, "零"),
    (7, "七"),
    (10, "十"),
    (13, "十三"),
    (15, "十五"),
    (20, "二十"),
    (21, "二十一"),
    (42, "四十二"),
    (99, "九十九"),
    (100, "一百"),
    (101, "一百零一"),
    (105, "一百零五"),
    (110, "一百一十"),
    (123, "一百二十三"),
    (999, "九百九十九"),
    (1000, "一千"),
    (1001, "一千零一"),
    (1010, "一千零一十"),
    (1100, "一千一百"),
    (1234, "一千二百三十四"),
    (2000, "二千"),
    (10000, "一万"),
    (10001, "一万零一"),
    (100000, "十万"),
    (100001, "十万零一"),
    (123456, "十二万三千四百五十六"),
    (1000000, "一百万"),
    (10000000, "一千万"),
    (100000000, "一亿"),
    (100000001, "一亿零一"),
    (123456789, "一亿二千三百四十五万六千七百八十九"),
    (1000000000, "十亿"),
    (9876543210, "九十八亿七千六百五十四万三千二百一十"),
    (
        999999999999,
        "九千九百九十九亿九千九百九十九万九千九百九十九",
    ),
    (200010, "二十万零一十"),
    (-42, "负四十二"),
]


class NumberToWordsToolEnglishTest(unittest.TestCase):
    """English rendering and parsing cases."""

    def setUp(self) -> None:
        self.tool = NumberToWordsTool()

    def test_number_to_words_ground_truths(self) -> None:
        for number, expected in EN_CASES:
            result = self.tool.execute(
                mode="number_to_words", number=number, lang="en"
            )
            self.assertEqual(result["result"], expected, msg=str(number))
            self.assertEqual(result["mode"], "number_to_words")
            self.assertEqual(result["lang"], "en")
            self.assertEqual(result["number"], str(number))

    def test_decimal_ground_truths(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="number_to_words", number="3.14", lang="en"
            )["result"],
            "three point one four",
        )
        self.assertEqual(
            self.tool.execute(
                mode="number_to_words", number="0.5", lang="en"
            )["result"],
            "zero point five",
        )
        self.assertEqual(
            self.tool.execute(
                mode="number_to_words", number="-0.25", lang="en"
            )["result"],
            "minus zero point two five",
        )

    def test_words_to_number_ground_truths(self) -> None:
        cases = {
            "zero": 0,
            "nineteen": 19,
            "twenty-one": 21,
            "twenty one": 21,
            "one hundred five": 105,
            "two thousand five": 2005,
            "one thousand two hundred thirty-four": 1234,
            "one million two hundred thirty-four thousand five hundred "
            "sixty-seven": 1234567,
            "nine hundred ninety-nine billion nine hundred ninety-nine "
            "million nine hundred ninety-nine thousand nine hundred "
            "ninety-nine": 999999999999,
            "minus five": -5,
            "negative one hundred": -100,
        }
        for words, expected in cases.items():
            result = self.tool.execute(mode="words_to_number", words=words)
            self.assertEqual(result["result"], expected, msg=words)
            self.assertEqual(result["mode"], "words_to_number")
            self.assertEqual(result["lang"], "en")

    def test_words_to_number_decimal_ground_truths(self) -> None:
        cases = {
            "three point one four": "3.14",
            "zero point five": "0.5",
            "minus zero point two five": "-0.25",
            "zero point zero zero one": "0.001",
        }
        for words, expected in cases.items():
            result = self.tool.execute(mode="words_to_number", words=words)
            self.assertEqual(result["result"], expected, msg=words)


class NumberToWordsToolChineseTest(unittest.TestCase):
    """Chinese rendering and parsing cases."""

    def setUp(self) -> None:
        self.tool = NumberToWordsTool()

    def test_number_to_words_ground_truths(self) -> None:
        for number, expected in ZH_CASES:
            result = self.tool.execute(
                mode="number_to_words", number=number, lang="zh"
            )
            self.assertEqual(result["result"], expected, msg=str(number))
            self.assertEqual(result["lang"], "zh")

    def test_decimal_ground_truths(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="number_to_words", number="3.14", lang="zh"
            )["result"],
            "三点一四",
        )
        self.assertEqual(
            self.tool.execute(
                mode="number_to_words", number="-0.25", lang="zh"
            )["result"],
            "负零点二五",
        )

    def test_words_to_number_ground_truths(self) -> None:
        cases = {
            "零": 0,
            "十": 10,
            "十五": 15,
            "二十": 20,
            "一百零五": 105,
            "一千二百三十四": 1234,
            "一万零一": 10001,
            "十万": 100000,
            "十万零一": 100001,
            "一亿零一": 100000001,
            "一千二百三十四万五千六百七十八": 12345678,
            "九千九百九十九亿九千九百九十九万九千九百九十九": 999999999999,
            "负四十二": -42,
            "两": 2,
            "两千三百": 2300,
            "一千〇一": 1001,
        }
        for words, expected in cases.items():
            result = self.tool.execute(
                mode="words_to_number", words=words, lang="zh"
            )
            self.assertEqual(result["result"], expected, msg=words)

    def test_words_to_number_decimal_ground_truths(self) -> None:
        cases = {
            "三点一四": "3.14",
            "零点五": "0.5",
            "负零点二五": "-0.25",
            "两点五": "2.5",
        }
        for words, expected in cases.items():
            result = self.tool.execute(
                mode="words_to_number", words=words, lang="zh"
            )
            self.assertEqual(result["result"], expected, msg=words)


class NumberToWordsToolRoundTripTest(unittest.TestCase):
    """Exact round trips across the full supported range."""

    def setUp(self) -> None:
        self.tool = NumberToWordsTool()

    def test_round_trip_exhaustive_small(self) -> None:
        for n in range(0, 20001):
            for lang in ("en", "zh"):
                words = self.tool.execute(
                    mode="number_to_words", number=n, lang=lang
                )["result"]
                back = self.tool.execute(
                    mode="words_to_number", words=words, lang=lang
                )["result"]
                self.assertEqual(back, n)

    def test_round_trip_sampled_large(self) -> None:
        rng = random.Random(20261019)
        values = (
            [rng.randint(1, 999999999999) for _ in range(500)]
            + [999999999999, 1, 100000000001, 300000050, 500000600007]
        )
        for n in values:
            for lang in ("en", "zh"):
                words = self.tool.execute(
                    mode="number_to_words", number=n, lang=lang
                )["result"]
                back = self.tool.execute(
                    mode="words_to_number", words=words, lang=lang
                )["result"]
                self.assertEqual(back, n)

    def test_round_trip_decimals(self) -> None:
        for text in ("0.5", "3.14", "-0.25", "0.001", "123.456"):
            for lang in ("en", "zh"):
                words = self.tool.execute(
                    mode="number_to_words", number=text, lang=lang
                )["result"]
                back = self.tool.execute(
                    mode="words_to_number", words=words, lang=lang
                )["result"]
                self.assertEqual(back, text)


class NumberToWordsToolValidationTest(unittest.TestCase):
    """Parameter-level errors raise ValueError (before any computation)."""

    def setUp(self) -> None:
        self.tool = NumberToWordsTool()

    def test_invalid_mode(self) -> None:
        for mode in ("spell", "", None, 1):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, number=1)

    def test_invalid_lang(self) -> None:
        for lang in ("fr", "", 1, True):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="number_to_words", number=1, lang=lang
                )

    def test_invalid_number_type(self) -> None:
        for number in (None, True, False, [1], {"a": 1}, 1.5):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="number_to_words", number=number)

    def test_invalid_number_string(self) -> None:
        for number in (
            "abc", "1,000", "+5", "007", "1.", ".5", "1.2.3", "",
            "  ", "-0", "-0.0", "0x10", "1e3", "1000000000000",
            "0.1234567890123",
        ):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="number_to_words", number=number)

    def test_number_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="number_to_words", number=10 ** 12)

    def test_invalid_words_parameter(self) -> None:
        for words in (None, True, 5, "", "   ", "x" * 10001):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="words_to_number", words=words)

    def test_string_number_whitespace_stripped(self) -> None:
        result = self.tool.execute(
            mode="number_to_words", number="  42 ", lang="en"
        )
        self.assertEqual(result["result"], "forty-two")
        self.assertEqual(result["number"], "42")


class NumberToWordsToolErrorPayloadTest(unittest.TestCase):
    """Content-level failures return structured error payloads."""

    def setUp(self) -> None:
        self.tool = NumberToWordsTool()

    def assert_invalid_words(self, words: str, lang: str) -> None:
        result = self.tool.execute(
            mode="words_to_number", words=words, lang=lang
        )
        self.assertEqual(result["mode"], "words_to_number")
        self.assertEqual(result["lang"], lang)
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["type"], "invalid_words")
        self.assertTrue(result["error"]["message"])

    def test_english_invalid_words(self) -> None:
        for words in (
            "hello world",
            "banana",
            "twenty twelve",
            "thousand",
            "hundred five",
            "ten hundred",
            "point five",
            "five point",
            "five point six seven ten",
            "one thousand thousand",
            "one thousand million",
            "nine billion nine billion",
            "zero five",
            "five zero",
            "minus",
            "minus minus five",
            "minus zero",
            "one hundred and five",
            "one trillion",
        ):
            self.assert_invalid_words(words, lang="en")

    def test_chinese_invalid_words(self) -> None:
        for words in (
            "万",
            "一百零",
            "一二三",
            "一零五",
            "一百零零五",
            "点五",
            "五点",
            "三点点四",
            "负",
            "负零",
            "二千三千",
            "十百",
            "English",
            "五 万",
            "一百X",
            "一万二",
            "一亿亿",
            "一亿一亿",
            "一亿零亿",
            "一千亿亿",
            "一亿二亿",
        ):
            self.assert_invalid_words(words, lang="zh")

    def test_chinese_repeated_yi_is_rejected(self) -> None:
        # A second '亿' would describe at least 10^16 — beyond the
        # supported 12-digit range — and must never compose additively
        # (previously '一亿一亿' silently parsed as 200,000,000).
        for words in ("一亿亿", "一亿一亿", "一亿零亿", "一千亿亿", "一亿二亿"):
            with self.subTest(words=words):
                result = self.tool.execute(
                    mode="words_to_number", words=words, lang="zh"
                )
                self.assertEqual(
                    result["error"]["type"], "invalid_words", msg=words
                )
                self.assertIn("亿", result["error"]["message"])
                self.assertNotIn("result", result)

    def test_chinese_wan_after_yi_still_parses(self) -> None:
        # The repeated-'亿' guard must not reject legitimate follow-up
        # 万 sections after a single 亿.
        cases = {
            "一亿一万": 100010000,
            "一亿零一万": 100010000,
            "一亿二千万": 120000000,
            "九千九百九十九亿九千九百九十九万九千九百九十九": 999999999999,
        }
        for words, expected in cases.items():
            with self.subTest(words=words):
                result = self.tool.execute(
                    mode="words_to_number", words=words, lang="zh"
                )
                self.assertEqual(result["result"], expected, msg=words)

    def test_english_out_of_range_words(self) -> None:
        # "trillion" is beyond the supported short-scale vocabulary — the
        # English parser tops out at billion, so no word sequence can
        # describe more than 999,999,999,999.
        result = self.tool.execute(
            mode="words_to_number", words="one trillion"
        )
        self.assertEqual(result["error"]["type"], "invalid_words")

    def test_chinese_out_of_range_words(self) -> None:
        # 一万亿 == 10^12 — one past the supported maximum.
        result = self.tool.execute(
            mode="words_to_number", words="一万亿", lang="zh"
        )
        self.assertEqual(result["error"]["type"], "out_of_range")


class NumberToWordsToolImportTest(unittest.TestCase):
    """The package-level export matches the direct module import."""

    def test_package_export(self) -> None:
        self.assertIs(NumberToWordsTool, DirectNumberToWordsTool)


if __name__ == "__main__":
    unittest.main()
