#!/usr/bin/env python3

# @Time    : 2026/10/20
# @FileName: test_reading_time_tool.py

"""Tests for ReadingTimeTool.

All arithmetic is deterministic and exact (fractions.Fraction
internally). Ground truths below were computed by hand from the
documented rules:

* words: family tokenizer (Latin runs with inner -/', digit runs,
  ONE word per Han/kana/Hangul character);
* durations: ceil(words * 60 / wpm) seconds, humanized with zero
  components skipped, "< 1 s" below one second;
* deck rule: 30-60 s per slide or bullet, midpoint 45 s per unit;
* plan budgets: exact budget +/-10% (floor / ceil).
"""

import os
import unittest
from fractions import Fraction

from agentuniverse.agent.action.tool.common_tool import (
    reading_time_tool as module,
)
from agentuniverse.agent.action.tool.common_tool.reading_time_tool import (
    ReadingTimeTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(module.__file__), "reading_time_tool.yaml")

FOX = "The quick brown fox jumps over the lazy dog."


def words_text(n: int) -> str:
    return " ".join(["word"] * n)


class ReadingTimeHumanizeTest(unittest.TestCase):
    """Documented humanization matrix, incl. sub-second and >60 min."""

    def test_matrix(self):
        # (input seconds, humanized)
        cases = [
            (0, "0 s"),
            (Fraction(1, 2), "< 1 s"),
            (Fraction(59, 60), "< 1 s"),
            (1, "1 s"),
            (45, "45 s"),
            (59, "59 s"),
            (60, "1 min"),
            (72, "1 min 12 s"),
            (192, "3 min 12 s"),
            (3599, "59 min 59 s"),
            (3600, "1 h"),
            (3605, "1 h 5 s"),
            (3660, "1 h 1 min"),
            (3903, "1 h 5 min 3 s"),
        ]
        for raw, expected in cases:
            self.assertEqual(module._humanize(Fraction(raw)), expected,
                             msg=str(raw))

    def test_ceil_seconds(self):
        self.assertEqual(module._ceil_seconds(Fraction(0)), 0)
        self.assertEqual(module._ceil_seconds(Fraction(59, 60)), 1)
        self.assertEqual(module._ceil_seconds(Fraction(192, 1)), 192)
        self.assertEqual(
            module._ceil_seconds(Fraction(900000, 238)), 3782)


class ReadingTimeEstimateTest(unittest.TestCase):
    """mode=estimate: speeds, CJK counting, override, humanization."""

    def setUp(self):
        self.tool = ReadingTimeTool()

    def test_nine_word_english_sentence(self):
        # 9 words: slow 540/150=3.6->4 s, average 540/238=2.268->3 s,
        # fast 540/350=1.543->2 s.
        result = self.tool.execute(mode="estimate", text=FOX)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["words"], 9)
        self.assertEqual(result["latin_words"], 9)
        self.assertEqual(result["cjk_chars"], 0)
        speeds = result["speeds"]
        self.assertEqual(
            [(s["speed"], s["wpm"], s["seconds"], s["humanized"])
             for s in speeds],
            [("slow", 150, 4, "4 s"),
             ("average", 238, 3, "3 s"),
             ("fast", 350, 2, "2 s")])
        self.assertIn("Brysbaert (2019)", result["reference"])

    def test_cjk_each_character_is_one_word(self):
        # 4 Han characters = 4 words; fast 240/350=0.686 s -> ceil 1,
        # humanized "< 1 s".
        result = self.tool.execute(mode="estimate", text="你好世界")
        self.assertEqual(result["words"], 4)
        self.assertEqual(result["cjk_chars"], 4)
        self.assertEqual(result["latin_words"], 0)
        speeds = result["speeds"]
        self.assertEqual(
            [(s["seconds"], s["humanized"]) for s in speeds],
            [(2, "2 s"), (2, "2 s"), (1, "< 1 s")])

    def test_mixed_document(self):
        result = self.tool.execute(
            mode="estimate", text="Hello 你世界 world")
        self.assertEqual(result["words"], 5)
        self.assertEqual(result["latin_words"], 2)
        self.assertEqual(result["cjk_chars"], 3)

    def test_family_tokenizer_rules(self):
        for text, expected in (
            ("don't stop 42 times", 4),
            ("state-of-the-art AI", 2),
            ("e.g., 3.14 and 2,000 items", 8),
            ("こんにちは", 5),
            ("안녕하세요", 5),
            ("word—dash", 2),
        ):
            result = self.tool.execute(mode="estimate", text=text)
            self.assertEqual(result["words"], expected, msg=text)

    def test_punctuation_only_text_is_zero_words_zero_seconds(self):
        result = self.tool.execute(mode="estimate", text="...")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["words"], 0)
        for speed in result["speeds"]:
            self.assertEqual(speed["seconds"], 0)
            self.assertEqual(speed["humanized"], "0 s")

    def test_reading_wpm_override_three_min_twelve_seconds(self):
        # 320 words at 100 wpm = 19200/100 = 192 s = 3 min 12 s.
        result = self.tool.execute(
            mode="estimate", text=words_text(320), reading_wpm=100)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["reading_wpm"], 100)
        self.assertEqual(len(result["speeds"]), 1)
        entry = result["speeds"][0]
        self.assertEqual(
            (entry["speed"], entry["wpm"], entry["seconds"],
             entry["humanized"]),
            ("custom", 100, 192, "3 min 12 s"))

    def test_hour_plus_duration(self):
        # 15000 words: slow 900000/150=6000 s, average -> 3782 s,
        # fast 900000/350=2571.43 -> 2572 s.
        result = self.tool.execute(mode="estimate", text=words_text(15000))
        by_speed = {s["speed"]: s for s in result["speeds"]}
        self.assertEqual(by_speed["slow"]["seconds"], 6000)
        self.assertEqual(by_speed["slow"]["humanized"], "1 h 40 min")
        self.assertEqual(by_speed["average"]["seconds"], 3782)
        self.assertEqual(
            by_speed["average"]["humanized"], "1 h 3 min 2 s")
        self.assertEqual(by_speed["fast"]["seconds"], 2572)
        self.assertEqual(by_speed["fast"]["humanized"], "42 min 52 s")

    def test_wpm_bounds_inclusive(self):
        # 9 words at 50 wpm = 10.8 -> 11 s; at 1000 wpm = 0.54 s ->
        # ceil 1, "< 1 s".
        low = self.tool.execute(
            mode="estimate", text=FOX, reading_wpm=50)
        self.assertEqual(low["speeds"][0]["seconds"], 11)
        high = self.tool.execute(
            mode="estimate", text=FOX, reading_wpm=1000)
        self.assertEqual(high["speeds"][0]["seconds"], 1)
        self.assertEqual(high["speeds"][0]["humanized"], "< 1 s")


class ReadingTimeSpeakingTest(unittest.TestCase):
    """mode=speaking: word tiers and the slide/bullet deck rule."""

    def setUp(self):
        self.tool = ReadingTimeTool()

    def test_word_tiers(self):
        # 480 words: 140 -> 28800/140=205.71 -> 206 s; 160 -> 180 s
        # exactly; 180 -> 160 s.
        result = self.tool.execute(mode="speaking", text=words_text(480))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["words"], 480)
        self.assertEqual(
            [(t["tier"], t["wpm"], t["seconds"], t["humanized"])
             for t in result["tiers"]],
            [("slow", 140, 206, "3 min 26 s"),
             ("average", 160, 180, "3 min"),
             ("fast", 180, 160, "2 min 40 s")])

    def test_cjk_speaking(self):
        result = self.tool.execute(mode="speaking", text="你好世界")
        self.assertEqual(result["words"], 4)
        self.assertEqual(
            [t["seconds"] for t in result["tiers"]], [2, 2, 2])

    def test_slide_rule(self):
        # 10 slides x (30, 60) s = 300..600 s, midpoint 450 s.
        result = self.tool.execute(mode="speaking", deck_count=10)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["deck_unit"], "slides")
        self.assertEqual(result["deck_count"], 10)
        self.assertEqual(result["seconds_per_unit"], [30, 60])
        self.assertEqual(result["min_seconds"], 300)
        self.assertEqual(result["min_humanized"], "5 min")
        self.assertEqual(result["max_seconds"], 600)
        self.assertEqual(result["max_humanized"], "10 min")
        self.assertEqual(result["mid_seconds"], 450)
        self.assertEqual(result["mid_humanized"], "7 min 30 s")

    def test_bullet_rule_and_unit_normalisation(self):
        # 25 bullets x (30, 60) s = 750..1500 s, midpoint 1125 s.
        result = self.tool.execute(
            mode="speaking", deck_count=25, deck_unit=" Bullets ")
        self.assertEqual(result["deck_unit"], "bullets")
        self.assertEqual(result["min_seconds"], 750)
        self.assertEqual(result["min_humanized"], "12 min 30 s")
        self.assertEqual(result["max_seconds"], 1500)
        self.assertEqual(result["max_humanized"], "25 min")
        self.assertEqual(result["mid_seconds"], 1125)
        self.assertEqual(result["mid_humanized"], "18 min 45 s")

    def test_single_slide_range(self):
        result = self.tool.execute(mode="speaking", deck_count=1)
        self.assertEqual(result["min_seconds"], 30)
        self.assertEqual(result["max_seconds"], 60)
        self.assertEqual(result["mid_seconds"], 45)


class ReadingTimeCustomTest(unittest.TestCase):
    """mode=custom: wpm basis and seconds_per_char basis."""

    def setUp(self):
        self.tool = ReadingTimeTool()

    def test_custom_wpm_exact_seconds(self):
        # 100 words at 200 wpm = 6000/200 = 30 s exactly.
        result = self.tool.execute(
            mode="custom", text=words_text(100), wpm=200)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["basis"], "words")
        self.assertEqual(result["wpm"], 200)
        self.assertEqual(result["words"], 100)
        self.assertEqual(result["seconds"], 30)
        self.assertEqual(result["humanized"], "30 s")

    def test_custom_default_wpm_is_238(self):
        # 238 words at the 238 wpm default = exactly 60 s.
        result = self.tool.execute(mode="custom", text=words_text(238))
        self.assertEqual(result["wpm"], 238)
        self.assertEqual(result["seconds"], 60)
        self.assertEqual(result["humanized"], "1 min")

    def test_subtitle_standard_seventeen_chars_per_second(self):
        # 340 chars at 1/17 s per char = 340/17 = 20 s exactly.
        result = self.tool.execute(
            mode="custom", text="a" * 340, seconds_per_char=1 / 17)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["basis"], "chars")
        self.assertEqual(result["chars"], 340)
        self.assertEqual(result["seconds"], 20)
        self.assertEqual(result["humanized"], "20 s")
        self.assertIn("17", result["note"])

    def test_char_basis_counts_internal_whitespace(self):
        # "ab cd" (trimmed) = 5 chars at 0.25 s = 1.25 -> ceil 2 s.
        result = self.tool.execute(
            mode="custom", text="  ab cd  ", seconds_per_char=0.25)
        self.assertEqual(result["chars"], 5)
        self.assertEqual(result["seconds"], 2)
        self.assertEqual(result["humanized"], "2 s")

    def test_binary_exact_char_rate(self):
        # 80 chars at 0.5 s = 40 s.
        result = self.tool.execute(
            mode="custom", text="b" * 80, seconds_per_char=0.5)
        self.assertEqual(result["seconds"], 40)
        self.assertEqual(result["humanized"], "40 s")

    def test_char_rate_upper_bound_allowed(self):
        result = self.tool.execute(
            mode="custom", text="xyz", seconds_per_char=10)
        self.assertEqual(result["seconds"], 30)


class ReadingTimePlanTest(unittest.TestCase):
    """mode=plan: inverse word budgets at +/-10%."""

    def setUp(self):
        self.tool = ReadingTimeTool()

    def test_ten_minutes_at_238_wpm(self):
        result = self.tool.execute(
            mode="plan", target_minutes=10, wpm=238)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["budget_words"], 2380)
        self.assertEqual(result["min_words"], 2142)
        self.assertEqual(result["max_words"], 2618)
        self.assertEqual(result["slot_seconds"], 600)
        self.assertEqual(result["slot_humanized"], "10 min")
        self.assertEqual(result["tolerance"], "+/-10%")

    def test_fractional_minutes_exact_budget(self):
        # 7.5 min at 160 wpm = 1200 words, window 1080..1320.
        result = self.tool.execute(
            mode="plan", target_minutes=7.5, wpm=160)
        self.assertEqual(result["budget_words"], 1200)
        self.assertEqual(result["min_words"], 1080)
        self.assertEqual(result["max_words"], 1320)
        self.assertEqual(result["slot_seconds"], 450)
        self.assertEqual(result["slot_humanized"], "7 min 30 s")

    def test_fractional_budget_floors_and_ceils(self):
        # 5.5 min at 201 wpm = 1105.5 words exactly; 994.95 floors to
        # 994 and 1216.05 ceils to 1217.
        result = self.tool.execute(
            mode="plan", target_minutes=5.5, wpm=201)
        self.assertEqual(result["budget_words"], 1105.5)
        self.assertEqual(result["min_words"], 994)
        self.assertEqual(result["max_words"], 1217)
        self.assertEqual(result["slot_seconds"], 330)
        self.assertEqual(result["slot_humanized"], "5 min 30 s")

    def test_small_slot(self):
        # 3 min at 140 wpm = 420 words, window 378..462.
        result = self.tool.execute(
            mode="plan", target_minutes=3, wpm=140)
        self.assertEqual(result["budget_words"], 420)
        self.assertEqual(result["min_words"], 378)
        self.assertEqual(result["max_words"], 462)

    def test_default_wpm_is_238(self):
        result = self.tool.execute(mode="plan", target_minutes=1)
        self.assertEqual(result["wpm"], 238)
        self.assertEqual(result["budget_words"], 238)
        self.assertEqual(result["min_words"], 214)
        self.assertEqual(result["max_words"], 262)

    def test_budget_window_brackets_exact_budget(self):
        for minutes, wpm in ((10, 238), (7.5, 160), (5.5, 201), (1, 350)):
            result = self.tool.execute(
                mode="plan", target_minutes=minutes, wpm=wpm)
            budget = result["budget_words"]
            self.assertLessEqual(result["min_words"], budget)
            self.assertGreaterEqual(result["max_words"], budget)
            self.assertGreaterEqual(result["min_words"], 1)


class ReadingTimeValidationTest(unittest.TestCase):
    """Error matrix, exports and packaging."""

    def setUp(self):
        self.tool = ReadingTimeTool()

    def test_unknown_and_non_string_mode(self):
        result = self.tool.execute(mode="nope", text=FOX)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unsupported mode", result["error"])
        self.assertEqual(result["mode"], "nope")
        result = self.tool.execute(mode=42)
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be a string", result["error"])

    def test_mode_case_and_whitespace_normalised(self):
        result = self.tool.execute(mode=" ESTIMATE ", text=FOX)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "estimate")

    def test_missing_or_non_string_text(self):
        for empty in ("", "   ", None):
            result = self.tool.execute(mode="estimate", text=empty)
            self.assertEqual(result["status"], "error", msg=repr(empty))
            self.assertIn("required", result["error"])
        result = self.tool.execute(mode="estimate", text=123)
        self.assertEqual(result["status"], "error")
        self.assertIn("text must be a string", result["error"])

    def test_text_length_bound(self):
        result = self.tool.execute(
            mode="estimate", text="a" * (module._MAX_TEXT_CHARS + 1))
        self.assertEqual(result["status"], "error")
        self.assertIn("exceeds", result["error"])

    def test_reading_wpm_bounds(self):
        for bad in (49, 1001, 0, -100):
            result = self.tool.execute(
                mode="estimate", text=FOX, reading_wpm=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertIn("between 50 and 1000", result["error"])

    def test_reading_wpm_rejects_booleans_and_strings(self):
        for bad in (True, "fast", [200]):
            result = self.tool.execute(
                mode="estimate", text=FOX, reading_wpm=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_custom_wpm_bounds(self):
        for bad in (49, 1001):
            result = self.tool.execute(
                mode="custom", text=FOX, wpm=bad)
            self.assertEqual(result["status"], "error")
            self.assertIn("between 50 and 1000", result["error"])
        result = self.tool.execute(mode="plan", target_minutes=5, wpm=49)
        self.assertEqual(result["status"], "error")
        self.assertIn("between 50 and 1000", result["error"])

    def test_custom_rejects_wpm_and_seconds_per_char_together(self):
        result = self.tool.execute(
            mode="custom", text=FOX, wpm=200, seconds_per_char=0.05)
        self.assertEqual(result["status"], "error")
        self.assertIn("not both", result["error"])

    def test_seconds_per_char_bounds(self):
        for bad in (0, -1, 11, "17", True, float("inf")):
            result = self.tool.execute(
                mode="custom", text=FOX, seconds_per_char=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_target_minutes_strictly_positive(self):
        for bad in (0, -5, None, "ten", True, float("nan")):
            result = self.tool.execute(mode="plan", target_minutes=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_speaking_requires_exactly_one_source(self):
        neither = self.tool.execute(mode="speaking")
        self.assertEqual(neither["status"], "error")
        self.assertIn("text", neither["error"])
        self.assertIn("deck_count", neither["error"])
        both = self.tool.execute(
            mode="speaking", text=FOX, deck_count=5)
        self.assertEqual(both["status"], "error")
        self.assertIn("not both", both["error"])

    def test_deck_count_and_unit_validation(self):
        for bad in (0, -3, 2.5, "10", True):
            result = self.tool.execute(
                mode="speaking", deck_count=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
        for bad in ("cards", 42, ""):
            result = self.tool.execute(
                mode="speaking", deck_count=3, deck_unit=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertIn("deck_unit", result["error"])

    def test_deterministic_repeats(self):
        first = self.tool.execute(mode="estimate", text=FOX)
        second = self.tool.execute(mode="estimate", text=FOX)
        self.assertEqual(first, second)
        deck_a = self.tool.execute(mode="speaking", deck_count=9)
        deck_b = self.tool.execute(mode="speaking", deck_count=9)
        self.assertEqual(deck_a, deck_b)

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import (
            ReadingTimeTool as exported)
        self.assertIs(exported, ReadingTimeTool)

    def test_yaml_exists_and_declares_component(self):
        self.assertTrue(os.path.isfile(YAML_PATH))
        with open(YAML_PATH, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("class: ReadingTimeTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool."
            "reading_time_tool", content)

    def test_tool_name_and_description(self):
        self.assertEqual(self.tool.name, "reading_time_tool")
        self.assertTrue(self.tool.description)


if __name__ == "__main__":
    unittest.main()
