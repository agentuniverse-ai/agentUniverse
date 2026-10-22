#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_acronym_generator_tool.py

"""Offline unit tests for AcronymGeneratorTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic: generation results are checked against
hand-computed ground truths including the camelCase compound rule
("HyperText Markup Language" -> HTML), the hyphen rule
("Cross-Origin Resource Sharing" -> CORS), stopword skipping with a
words_skipped report ("Society for the Prevention of Cruelty to
Animals" -> SPCA), the letter styles (upper / keep_case /
first_letters_lower), the 10-word cap with its notes, single-letter
words, all-stopword phrases (structured empty result), CJK phrases
(each character is an initial), the variants listing with labels and
deduplication, the from_name mode including the consonant fallback,
and a full input-validation error matrix.
"""

import os
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import (
    AcronymGeneratorTool,
    acronym_generator_tool as acronym_generator_module,
)
from agentuniverse.agent.action.tool.common_tool.acronym_generator_tool import (
    _STOPWORDS,
    AcronymGeneratorTool as DirectAcronymGeneratorTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(acronym_generator_module.__file__)),
    "acronym_generator_tool.yaml",
)


class AcronymGeneratorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib AcronymGeneratorTool."""

    def setUp(self) -> None:
        self.tool = AcronymGeneratorTool()

    # ------------------------------------------------------------------ #
    # generate mode — ground truths
    # ------------------------------------------------------------------ #

    def test_generate_html_full_payload(self) -> None:
        result = self.tool.execute(
            mode="generate", phrase="HyperText Markup Language"
        )
        self.assertEqual(
            result,
            {
                "mode": "generate",
                "result": "HTML",
                "acronym": "HTML",
                "letters": ["H", "T", "M", "L"],
                "words_used": ["HyperText", "Markup", "Language"],
                "words_skipped": [],
                "word_count": 3,
                "options": {
                    "skip_stopwords": True,
                    "min_word_length": 0,
                    "max_words": 10,
                    "style": "upper",
                },
                "notes": [],
            },
        )

    def test_generate_json_keep_case(self) -> None:
        # Java|Script contribute J and S, Object and Notation O and N —
        # with keep_case the result equals the canonical JSON spelling.
        result = self.tool.execute(
            mode="generate",
            phrase="JavaScript Object Notation",
            style="keep_case",
        )
        self.assertEqual(result["acronym"], "JSON")
        self.assertEqual(result["letters"], ["J", "S", "O", "N"])

    def test_generate_styles_compare(self) -> None:
        phrase = "Content management system"
        self.assertEqual(
            self.tool.execute(mode="generate", phrase=phrase)["acronym"],
            "CMS",
        )
        self.assertEqual(
            self.tool.execute(
                mode="generate", phrase=phrase, style="keep_case"
            )["acronym"],
            "Cms",
        )
        self.assertEqual(
            self.tool.execute(
                mode="generate", phrase=phrase, style="first_letters_lower"
            )["acronym"],
            "cms",
        )

    def test_generate_hyphen_rule_cors(self) -> None:
        # Cross-Origin contributes the first letter of EACH part.
        result = self.tool.execute(
            mode="generate", phrase="Cross-Origin Resource Sharing"
        )
        self.assertEqual(result["acronym"], "CORS")
        self.assertEqual(result["letters"], ["C", "O", "R", "S"])
        self.assertEqual(
            result["words_used"], ["Cross-Origin", "Resource", "Sharing"]
        )

    def test_generate_stopword_skip_with_report(self) -> None:
        result = self.tool.execute(
            mode="generate",
            phrase="Society for the Prevention of Cruelty to Animals",
        )
        self.assertEqual(result["acronym"], "SPCA")
        self.assertEqual(
            result["words_used"],
            ["Society", "Prevention", "Cruelty", "Animals"],
        )
        self.assertEqual(
            result["words_skipped"],
            [
                {"word": "for", "reason": "stopword"},
                {"word": "the", "reason": "stopword"},
                {"word": "of", "reason": "stopword"},
                {"word": "to", "reason": "stopword"},
            ],
        )
        # Stopword matching is case-insensitive and exact ("without"
        # is not "with").
        self.assertEqual(
            self.tool.execute(
                mode="generate", phrase="The Federal Bureau of Investigation"
            )["acronym"],
            "FBI",
        )

    def test_generate_hyphen_stopword_interaction(self) -> None:
        # Stopwords apply per part, also inside hyphen compounds.
        result = self.tool.execute(
            mode="generate", phrase="State-of-the-art systems"
        )
        self.assertEqual(result["acronym"], "SAS")
        self.assertEqual(result["letters"], ["S", "a", "s"])
        self.assertEqual(result["words_used"], ["State-of-the-art", "systems"])

    def test_generate_single_letter_words(self) -> None:
        # "I" is not a stopword and is always included.
        self.assertEqual(
            self.tool.execute(mode="generate", phrase="I Robot")["acronym"],
            "IR",
        )
        # "A" is a stopword: skipped by default, kept when disabled.
        self.assertEqual(
            self.tool.execute(mode="generate", phrase="A Team")["acronym"],
            "T",
        )
        result = self.tool.execute(
            mode="generate", phrase="A Team", skip_stopwords=False
        )
        self.assertEqual(result["acronym"], "AT")
        self.assertEqual(result["words_skipped"], [])

    def test_generate_all_stopwords_structured_empty(self) -> None:
        result = self.tool.execute(mode="generate", phrase="the of and to a in")
        self.assertEqual(result["acronym"], "")
        self.assertEqual(result["result"], "")
        self.assertEqual(result["letters"], [])
        self.assertEqual(result["words_used"], [])
        self.assertEqual(result["word_count"], 0)
        self.assertEqual(
            [entry["reason"] for entry in result["words_skipped"]],
            ["stopword"] * 6,
        )
        self.assertEqual(
            result["notes"],
            ["no words contributed letters — the acronym is empty"],
        )

    def test_generate_punctuation_stripped(self) -> None:
        result = self.tool.execute(mode="generate", phrase="(Hello) World!")
        self.assertEqual(result["acronym"], "HW")
        self.assertEqual(result["words_used"], ["Hello", "World"])
        # Tokens without any letter are skipped with a reason.
        result = self.tool.execute(
            mode="generate", phrase="-- Hyper Text 2024 --"
        )
        self.assertEqual(result["acronym"], "HT")
        self.assertEqual(
            result["words_skipped"],
            [
                {"word": "--", "reason": "no_letters"},
                {"word": "2024", "reason": "no_letters"},
                {"word": "--", "reason": "no_letters"},
            ],
        )

    def test_generate_all_caps_token_rule(self) -> None:
        # An all-caps token has no hump boundary and contributes only
        # its first letter.
        result = self.tool.execute(
            mode="generate", phrase="NASA Launch Program"
        )
        self.assertEqual(result["acronym"], "NLP")
        # Digit-leading parts use their first alphabetic character.
        result = self.tool.execute(mode="generate", phrase="3M Company")
        self.assertEqual(result["acronym"], "MC")

    def test_generate_min_word_length(self) -> None:
        result = self.tool.execute(
            mode="generate", phrase="A Big Corporation", min_word_length=5
        )
        self.assertEqual(result["acronym"], "C")
        self.assertEqual(
            result["words_skipped"],
            [
                {"word": "A", "reason": "min_word_length"},
                {"word": "Big", "reason": "min_word_length"},
            ],
        )

    def test_generate_max_words_cap_and_note(self) -> None:
        phrase = " ".join(
            [
                "one", "two", "three", "four", "five", "six",
                "seven", "eight", "nine", "ten", "eleven", "twelve",
            ]
        )
        result = self.tool.execute(mode="generate", phrase=phrase)
        self.assertEqual(result["acronym"], "OTTFFSSENT")
        self.assertEqual(result["word_count"], 10)
        self.assertEqual(
            result["words_skipped"],
            [
                {"word": "eleven", "reason": "max_words"},
                {"word": "twelve", "reason": "max_words"},
            ],
        )
        self.assertEqual(
            result["notes"],
            ["2 word(s) beyond the 10-word cap were ignored"],
        )
        self.assertEqual(result["options"]["max_words"], 10)

    def test_generate_max_words_explicit_and_clamped(self) -> None:
        phrase = "alpha beta gamma delta epsilon"
        result = self.tool.execute(mode="generate", phrase=phrase, max_words=2)
        self.assertEqual(result["acronym"], "AB")
        self.assertEqual(result["options"]["max_words"], 2)
        self.assertEqual(
            [entry["reason"] for entry in result["words_skipped"]],
            ["max_words"] * 3,
        )
        self.assertEqual(
            result["notes"],
            ["3 word(s) beyond the 2-word cap were ignored"],
        )
        # A max_words above the hard cap is clamped down with a note.
        result = self.tool.execute(mode="generate", phrase=phrase, max_words=15)
        self.assertEqual(result["acronym"], "ABGDE")
        self.assertEqual(result["options"]["max_words"], 10)
        self.assertEqual(
            result["notes"],
            ["max_words=15 exceeds the 10-word cap; using 10"],
        )

    def test_generate_cjk_each_char_is_an_initial(self) -> None:
        result = self.tool.execute(
            mode="generate", phrase="人工智能 数据 系统"
        )
        self.assertEqual(result["acronym"], "人工智能数据系统")
        self.assertEqual(
            result["letters"],
            ["人", "工", "智", "能", "数", "据", "系", "统"],
        )
        self.assertEqual(
            result["words_used"], ["人工智能", "数据", "系统"]
        )
        # A Latin run inside a mixed part contributes only its first
        # letter; every CJK character contributes itself.
        result = self.tool.execute(mode="generate", phrase="AI驱动 引擎")
        self.assertEqual(result["acronym"], "A驱动引擎")
        self.assertEqual(result["letters"], ["A", "驱", "动", "引", "擎"])

    def test_generate_determinism(self) -> None:
        phrase = "Portable Network Graphics"
        first = self.tool.execute(mode="generate", phrase=phrase)
        for _ in range(5):
            self.assertEqual(
                self.tool.execute(mode="generate", phrase=phrase), first
            )
        self.assertEqual(first["acronym"], "PNG")

    # ------------------------------------------------------------------ #
    # variants mode
    # ------------------------------------------------------------------ #

    def test_variants_labelled_listing(self) -> None:
        result = self.tool.execute(
            mode="variants",
            phrase="Society for the Prevention of Cruelty to Animals",
        )
        self.assertEqual(
            result,
            {
                "mode": "variants",
                "result": [
                    {"label": "full", "acronym": "SFTPOCTA", "word_count": 8},
                    {
                        "label": "no_stopwords",
                        "acronym": "SPCA",
                        "word_count": 4,
                    },
                    {
                        "label": "first_2_words",
                        "acronym": "SP",
                        "word_count": 2,
                    },
                    {
                        "label": "first_3_words",
                        "acronym": "SPC",
                        "word_count": 3,
                    },
                ],
                "variant_count": 4,
                "word_count": 8,
                "content_word_count": 4,
                "style": "upper",
            },
        )

    def test_variants_duplicate_collapse(self) -> None:
        # "Portable Network Graphics" has no stopwords: the full and
        # no_stopwords acronyms coincide and collapse into the single
        # "full" entry; the distinct first-2-words form is kept.
        result = self.tool.execute(
            mode="variants", phrase="Portable Network Graphics"
        )
        self.assertEqual(
            result["result"],
            [
                {"label": "full", "acronym": "PNG", "word_count": 3},
                {"label": "first_2_words", "acronym": "PN", "word_count": 2},
            ],
        )
        self.assertEqual(result["content_word_count"], 3)

    def test_variants_single_content_word(self) -> None:
        result = self.tool.execute(mode="variants", phrase="the Internet")
        self.assertEqual(
            result["result"],
            [
                {"label": "full", "acronym": "TI", "word_count": 2},
                {"label": "no_stopwords", "acronym": "I", "word_count": 1},
            ],
        )
        self.assertEqual(result["content_word_count"], 1)

    def test_variants_style_respected(self) -> None:
        result = self.tool.execute(
            mode="variants",
            phrase="Content management system",
            style="keep_case",
        )
        self.assertEqual(
            [entry["acronym"] for entry in result["result"]],
            ["Cms", "Cm"],
        )
        self.assertEqual(
            [entry["label"] for entry in result["result"]],
            ["full", "first_2_words"],
        )

    # ------------------------------------------------------------------ #
    # from_name mode
    # ------------------------------------------------------------------ #

    def test_from_name_initials(self) -> None:
        result = self.tool.execute(
            mode="from_name", name="customer relationship management"
        )
        self.assertEqual(
            result,
            {
                "mode": "from_name",
                "result": "CRM",
                "acronym": "CRM",
                "method": "initials",
                "fallback_used": False,
                "letters": ["c", "r", "m"],
                "name_words": [
                    "customer",
                    "relationship",
                    "management",
                ],
                "notes": [],
            },
        )

    def test_from_name_compound_and_letter_cap(self) -> None:
        result = self.tool.execute(
            mode="from_name", name="HyperText Transfer Protocol"
        )
        self.assertEqual(result["acronym"], "HTTP")
        self.assertEqual(result["method"], "initials")
        self.assertEqual(result["letters"], ["H", "T", "T", "P"])
        # Longer names are truncated to the 4-letter cap.
        result = self.tool.execute(
            mode="from_name",
            name="International Business Machines Data Processing",
        )
        self.assertEqual(result["acronym"], "IBMD")
        self.assertEqual(result["letters"], ["I", "B", "M", "D"])

    def test_from_name_stopwords_skipped(self) -> None:
        result = self.tool.execute(
            mode="from_name", name="the academy of motion picture arts"
        )
        self.assertEqual(result["acronym"], "AMPA")
        self.assertEqual(
            result["name_words"],
            ["academy", "motion", "picture", "arts"],
        )

    def test_from_name_consonant_fallback(self) -> None:
        # Single-word name: only one initial, so the consonants of the
        # first content word are used (y is a consonant, only aeiou
        # are vowels; capped at 4 letters).
        result = self.tool.execute(mode="from_name", name="Blockchain")
        self.assertEqual(result["acronym"], "BLCK")
        self.assertEqual(result["method"], "consonant_fallback")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["letters"], ["B", "L", "C", "K"])
        result = self.tool.execute(mode="from_name", name="System")
        self.assertEqual(result["acronym"], "SYST")
        self.assertTrue(result["fallback_used"])
        self.assertTrue(result["notes"])

    def test_from_name_no_usable_letters(self) -> None:
        result = self.tool.execute(mode="from_name", name="the of and")
        self.assertEqual(result["acronym"], "")
        self.assertEqual(result["method"], "none")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["name_words"], [])
        self.assertTrue(result["notes"])

    # ------------------------------------------------------------------ #
    # package / registration
    # ------------------------------------------------------------------ #

    def test_direct_import_and_name(self) -> None:
        tool = DirectAcronymGeneratorTool()
        self.assertEqual(tool.name, "acronym_generator_tool")
        self.assertIsInstance(tool.description, str)
        self.assertTrue(tool.description)

    def test_stopword_list_contents(self) -> None:
        # The documented small EN stopword list, frozen and exact.
        self.assertEqual(
            sorted(_STOPWORDS),
            sorted(
                [
                    "a", "an", "and", "as", "at", "but", "by", "for",
                    "from", "in", "into", "of", "on", "onto", "or",
                    "the", "to", "with",
                ]
            ),
        )

    def test_yaml_registration_file(self) -> None:
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "acronym_generator_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["metadata"]["type"], "TOOL")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool."
            "acronym_generator_tool",
        )
        self.assertEqual(config["metadata"]["class"], "AcronymGeneratorTool")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["generate", "variants", "from_name"],
        )
        self.assertEqual(
            config["args_model_schema"]["properties"]["style"]["enum"],
            ["upper", "keep_case", "first_letters_lower"],
        )
        self.assertEqual(
            config["args_model_schema"]["required"], ["mode"]
        )

    # ------------------------------------------------------------------ #
    # error matrix — strict validation before any computation
    # ------------------------------------------------------------------ #

    def assert_invalid(self, message_part: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertTrue(
            str(ctx.exception).startswith(
                "acronym_generator_tool: "
            ),
            msg=str(ctx.exception),
        )
        self.assertIn(message_part, str(ctx.exception))

    def test_error_unknown_mode(self) -> None:
        self.assert_invalid(
            "mode must be one of", mode="invert", phrase="Hello World"
        )
        self.assert_invalid(
            "mode must be one of", mode=None, phrase="Hello World"
        )

    def test_error_bad_phrase(self) -> None:
        self.assert_invalid(
            "phrase must be a non-empty string", mode="generate"
        )
        self.assert_invalid(
            "phrase must be a non-empty string", mode="generate", phrase=""
        )
        self.assert_invalid(
            "phrase must be a non-empty string", mode="generate", phrase="   "
        )
        self.assert_invalid(
            "phrase must be a non-empty string", mode="generate", phrase=123
        )
        self.assert_invalid(
            "phrase must be a non-empty string",
            mode="generate",
            phrase=["a", "b"],
        )
        self.assert_invalid(
            "phrase must be a non-empty string", mode="generate", phrase=True
        )
        self.assert_invalid(
            "phrase exceeds the 10,000-character limit",
            mode="generate",
            phrase="a" * 10_001,
        )
        self.assert_invalid(
            "phrase exceeds the 1,000-token limit",
            mode="generate",
            phrase=" ".join(["word"] * 1_001),
        )
        self.assert_invalid(
            "phrase must be a non-empty string", mode="variants"
        )

    def test_error_bad_options(self) -> None:
        base = {"mode": "generate", "phrase": "Hello World"}
        self.assert_invalid(
            "skip_stopwords must be a boolean",
            skip_stopwords="yes", **base,
        )
        self.assert_invalid(
            "skip_stopwords must be a boolean", skip_stopwords=None, **base
        )
        self.assert_invalid(
            "skip_stopwords must be a boolean", skip_stopwords=1, **base
        )
        self.assert_invalid(
            "min_word_length must be an integer",
            min_word_length="2", **base,
        )
        self.assert_invalid(
            "min_word_length must be an integer", min_word_length=1.5, **base
        )
        self.assert_invalid(
            "min_word_length must be an integer", min_word_length=True, **base
        )
        self.assert_invalid(
            "min_word_length must be >= 0", min_word_length=-1, **base
        )
        self.assert_invalid(
            "max_words must be an integer", max_words="5", **base
        )
        self.assert_invalid(
            "max_words must be an integer", max_words=2.0, **base
        )
        self.assert_invalid(
            "max_words must be an integer", max_words=True, **base
        )
        self.assert_invalid(
            "max_words must be >= 1", max_words=0, **base
        )
        self.assert_invalid(
            "max_words must be >= 1", max_words=-3, **base
        )

    def test_error_bad_style(self) -> None:
        self.assert_invalid(
            "style must be one of",
            mode="generate",
            phrase="Hello World",
            style="camel",
        )
        self.assert_invalid(
            "style must be one of",
            mode="variants",
            phrase="Hello World",
            style=None,
        )
        # from_name also validates the style even though it ignores it.
        self.assert_invalid(
            "style must be one of", mode="from_name", name="Hello", style="x"
        )

    def test_error_bad_name(self) -> None:
        self.assert_invalid("name must be a non-empty string", mode="from_name")
        self.assert_invalid(
            "name must be a non-empty string", mode="from_name", name=""
        )
        self.assert_invalid(
            "name must be a non-empty string", mode="from_name", name=42
        )
        self.assert_invalid(
            "name must be a non-empty string", mode="from_name", name=False
        )
        self.assert_invalid(
            "name exceeds the 10,000-character limit",
            mode="from_name",
            name="a" * 10_001,
        )


if __name__ == "__main__":
    unittest.main()
