#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import text_statistics_tool as text_module
from agentuniverse.agent.action.tool.common_tool.text_statistics_tool import TextStatisticsTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = text_module.__file__.replace(".py", ".yaml")


class TextStatisticsToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = TextStatisticsTool()

    def analyze(self, text: str, **kwargs):
        return self.tool.execute(text=text, **kwargs)

    def test_counts_basic_sentence(self) -> None:
        result = self.analyze("Hello world. This is a test.")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["counts"]["words"], 6)
        self.assertEqual(result["counts"]["sentences"], 2)
        self.assertEqual(result["counts"]["paragraphs"], 1)

    def test_counts_characters(self) -> None:
        result = self.analyze("Hi there!")
        self.assertEqual(result["counts"]["characters"], len("Hi there!"))
        self.assertEqual(result["counts"]["characters_no_spaces"], 8)
        self.assertEqual(result["counts"]["whitespace"], 1)

    def test_letters_and_digits(self) -> None:
        result = self.analyze("abc 123 def")
        self.assertEqual(result["counts"]["letters"], 6)
        self.assertEqual(result["counts"]["digits"], 3)

    def test_multiple_paragraphs(self) -> None:
        text = "First paragraph here.\n\nSecond one.\n\nThird paragraph."
        result = self.analyze(text)
        self.assertEqual(result["counts"]["paragraphs"], 3)

    def test_unique_word_count_case_insensitive(self) -> None:
        result = self.analyze("Hello hello HELLO world")
        self.assertEqual(result["counts"]["words"], 4)
        self.assertEqual(result["counts"]["unique_words"], 2)

    def test_question_and_exclamation_split_sentences(self) -> None:
        result = self.analyze("What? Yes! Okay.")
        self.assertEqual(result["counts"]["sentences"], 3)

    def test_averages_words_per_sentence(self) -> None:
        result = self.analyze("One sentence. Two words here.")
        self.assertEqual(result["averages"]["words_per_sentence"], 2.5)

    def test_chars_per_word(self) -> None:
        result = self.analyze("hello world")
        # 10 non-space chars / 2 words = 5.0
        self.assertEqual(result["averages"]["chars_per_word"], 5.0)

    def test_syllables_per_word(self) -> None:
        result = self.analyze("hello world")
        self.assertGreater(result["averages"]["syllables_per_word"], 0.0)

    def test_reading_time_default_wpm(self) -> None:
        # 200 wpm => 200 words = 60s.
        text = " ".join(["word"] * 200) + "."
        result = self.analyze(text)
        self.assertAlmostEqual(result["reading_time_seconds"], 60.0, delta=0.5)
        self.assertEqual(result["words_per_minute"], 200)

    def test_reading_time_custom_wpm(self) -> None:
        text = " ".join(["word"] * 100) + "."
        result = self.analyze(text, words_per_minute=100)
        self.assertAlmostEqual(result["reading_time_seconds"], 60.0, delta=0.5)
        self.assertEqual(result["words_per_minute"], 100)

    def test_complexity_for_simple_text(self) -> None:
        result = self.analyze("The cat sat on the mat. The dog ran fast.")
        comp = result["complexity"]
        self.assertIsNotNone(comp["flesch_reading_ease"])
        self.assertIsNotNone(comp["flesch_kincaid_grade"])
        self.assertIn(comp["difficulty_label"], {
            "very easy", "easy", "moderate", "difficult", "very difficult"
        })

    def test_complexity_none_for_empty_words(self) -> None:
        result = self.analyze("   ... !!!  ")
        self.assertEqual(result["counts"]["words"], 0)
        self.assertIsNone(result["complexity"]["flesch_reading_ease"])
        self.assertEqual(result["complexity"]["difficulty_label"], "n/a")

    def test_longest_word(self) -> None:
        result = self.analyze("a quick brown hippopotamus")
        self.assertEqual(result["longest_word"], "hippopotamus")

    def test_rejects_non_string_text(self) -> None:
        result = self.tool.execute(text=42)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_rejects_bad_wpm(self) -> None:
        result = self.analyze("hi there", words_per_minute=0)
        self.assertIn("words_per_minute", result["error"])
        result = self.analyze("hi there", words_per_minute=99999)
        self.assertIn("words_per_minute", result["error"])

    def test_chinese_full_stop_sentence_split(self) -> None:
        result = self.analyze("你好。世界！测试？")
        self.assertEqual(result["counts"]["sentences"], 3)

    def test_syllable_heuristic_silent_e(self) -> None:
        # "name" -> 1 (silent e), "testing" -> 2
        self.assertEqual(self.tool._count_syllables("name"), 1)
        self.assertEqual(self.tool._count_syllables("testing"), 2)
        self.assertEqual(self.tool._count_syllables("a"), 1)


class TextStatisticsRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=YAML_PATH).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "TextStatisticsTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, TextStatisticsTool)
        self.assertEqual(tool.input_keys, ["text"])
        self.assertEqual(tool.words_per_minute, 200)

    def test_yaml_loads_as_dict(self):
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "text_statistics_tool")
        self.assertEqual(data["metadata"]["class"], "TextStatisticsTool")


if __name__ == "__main__":
    unittest.main()
