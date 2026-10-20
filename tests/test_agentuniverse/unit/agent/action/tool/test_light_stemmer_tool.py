import os
import unittest

from agentuniverse.agent.action.tool.common_tool import light_stemmer_tool as stemmer_module
from agentuniverse.agent.action.tool.common_tool.light_stemmer_tool import LightStemmerTool
from agentuniverse.agent.action.tool.common_tool import LightStemmerTool as ExportedLightStemmerTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(stemmer_module.__file__), "light_stemmer_tool.yaml")


class LightStemmerToolTest(unittest.TestCase):
    """Offline, deterministic unit tests for LightStemmerTool."""

    def setUp(self):
        self.tool = LightStemmerTool()

    # ------------------------------------------------------------------ #
    # Porter measure (m) — the paper's own example vectors
    # ------------------------------------------------------------------ #

    def test_measure_paper_vectors(self) -> None:
        cases = [
            ("tr", 0), ("tree", 0), ("y", 0), ("by", 0),
            ("trouble", 1), ("oats", 1), ("trees", 1), ("ivy", 1),
            ("troubles", 2), ("private", 2), ("oaten", 2), ("orrery", 2),
        ]
        for word, expected in cases:
            with self.subTest(word=word):
                self.assertEqual(LightStemmerTool._measure(word), expected)

    def test_measure_y_is_vowel_only_after_consonant(self) -> None:
        # 'toy': y preceded by a vowel -> consonant -> [C](VC)^1 -> m=1
        self.assertEqual(LightStemmerTool._measure("toy"), 1)
        # 'syzygy': every y preceded by a consonant -> vowels -> [C](VC)^2[V]
        self.assertEqual(LightStemmerTool._measure("syzygy"), 2)
        self.assertTrue(LightStemmerTool._contains_vowel("fly"))
        self.assertFalse(LightStemmerTool._contains_vowel("fl"))

    # ------------------------------------------------------------------ #
    # stem mode — classic Porter examples inside the light subset
    # ------------------------------------------------------------------ #

    def test_stem_classic_ground_truths(self) -> None:
        cases = {
            # step 1a
            "caresses": "caress", "ponies": "poni", "ties": "ti",
            "caress": "caress", "cats": "cat", "misses": "miss",
            # step 1b
            "feed": "feed", "agreed": "agree", "plastered": "plaster",
            "bled": "bled", "motoring": "motor", "sing": "sing",
            # step 1c
            "happy": "happi", "sky": "sky", "city": "citi",
            # step 2 lite
            "relational": "relate", "conditional": "condition",
            "digitizer": "digitize", "goodness": "good",
            "happiness": "happi", "organizer": "organize",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                result = self.tool.execute(mode="stem", word=word)
                self.assertEqual(
                    result,
                    {"mode": "stem", "lowercase": False, "result": expected},
                )

    def test_stem_documented_divergences_from_full_porter(self) -> None:
        """Pin exact light outputs that differ from (or fall outside) full Porter."""
        cases = {
            # no step-1b cleanup: doubled consonant kept, no 'e' restoration
            "running": "runn", "hoping": "hop",
            # laxer trailing-e rule (m > 0, inside step 1b, not step 5a)
            "rate": "rat", "love": "lov",
            # stricter step 1c: requires a consonant before the final y
            "enjoy": "enjoy", "obey": "obey",
            # y after consonant is a vowel: 'flying' -> 'fly', then m("fl") == 0
            "flying": "fly",
            # no special (t)ied rule: 'died' -> 'di' via plain ed-removal
            "died": "di",
            # step 2 lite needs m > 0, and there is no step-4 'al' rule:
            # full Porter reaches 'ration', the light stemmer stops here
            "rational": "rational",
            # 'er' is not a light suffix
            "runner": "runner",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(
                    self.tool.execute(mode="stem", word=word)["result"],
                    expected,
                )

    def test_stem_step1a_guards(self) -> None:
        # single-letter 's' is kept intact
        self.assertEqual(self.tool.execute(mode="stem", word="s")["result"], "s")
        # bare suffix words survive (empty stems have no vowel / m == 0)
        for word in ("e", "ed", "eed", "ing", "ies", "ss", "sses"):
            with self.subTest(word=word):
                stemmed = self.tool.execute(mode="stem", word=word)["result"]
                self.assertTrue(stemmed and stemmed.isalpha())

    def test_stem_step1b_first_match_dispatch(self) -> None:
        # 'feed' matches the eed branch; its condition fails and no other
        # rule of the step fires (an 'ed' rule would wrongly give 'fe')
        self.assertEqual(self.tool.execute(mode="stem", word="feed")["result"], "feed")
        # 'agree' does not end in 'eed'/'ed'/'ing': only the e-branch applies
        self.assertEqual(self.tool.execute(mode="stem", word="agree")["result"], "agre")

    def test_stem_step2_ational_before_tional(self) -> None:
        # 'relational' ends in both suffixes; 'ational' must win -> 'relate'
        self.assertEqual(
            self.tool.execute(mode="stem", word="relational")["result"], "relate"
        )
        # 'conditional' only ends in 'tional' -> 'condition'
        self.assertEqual(
            self.tool.execute(mode="stem", word="conditional")["result"], "condition"
        )
        # a matching suffix with m == 0 blocks the rest of the step
        self.assertEqual(
            self.tool.execute(mode="stem", word="rational")["result"], "rational"
        )

    def test_stem_word_list_shape(self) -> None:
        result = self.tool.execute(
            mode="stem", words=["running", "runs", "runner"]
        )
        self.assertEqual(
            result,
            {
                "mode": "stem",
                "lowercase": False,
                "count": 3,
                "result": ["runn", "run", "runner"],
            },
        )

    def test_stem_lowercase_option(self) -> None:
        # suffix rules are lowercase: 'CATS' matches nothing as-is
        self.assertEqual(
            self.tool.execute(mode="stem", word="CATS")["result"], "CATS"
        )
        self.assertEqual(
            self.tool.execute(mode="stem", word="CATS", lowercase=True),
            {"mode": "stem", "lowercase": True, "result": "cat"},
        )
        self.assertEqual(
            self.tool.execute(
                mode="stem", words=["CATS", "Ponies"], lowercase=True
            )["result"],
            ["cat", "poni"],
        )

    def test_stem_deterministic(self) -> None:
        words = ["caresses", "running", "relational", "happy", "sky"] * 20
        first = self.tool.execute(mode="stem", words=words)["result"]
        for _ in range(5):
            again = self.tool.execute(mode="stem", words=words)["result"]
            self.assertEqual(first, again)

    # ------------------------------------------------------------------ #
    # stem_text mode
    # ------------------------------------------------------------------ #

    def test_stem_text_pairing(self) -> None:
        result = self.tool.execute(
            mode="stem_text", text="The ponies are running!", lowercase=True
        )
        self.assertEqual(
            result,
            {
                "mode": "stem_text",
                "lowercase": True,
                "token_count": 4,
                "result": [
                    {"original": "The", "stem": "the"},
                    {"original": "ponies", "stem": "poni"},
                    {"original": "are", "stem": "ar"},
                    {"original": "running", "stem": "runn"},
                ],
            },
        )

    def test_stem_text_separators_are_dropped(self) -> None:
        # punctuation, digits and whitespace separate alphabetic runs
        result = self.tool.execute(
            mode="stem_text", text="cats, 42 dogs; don't stop..."
        )
        self.assertEqual(
            result["result"],
            [
                {"original": "cats", "stem": "cat"},
                {"original": "dogs", "stem": "dog"},
                {"original": "don", "stem": "don"},
                {"original": "t", "stem": "t"},
                {"original": "stop", "stem": "stop"},
            ],
        )
        self.assertEqual(result["token_count"], 5)

    def test_stem_text_without_lowercase_keeps_case(self) -> None:
        result = self.tool.execute(mode="stem_text", text="Running fast")
        self.assertEqual(
            result["result"],
            [{"original": "Running", "stem": "Runn"}, {"original": "fast", "stem": "fast"}],
        )

    def test_stem_text_no_letters_yields_empty_tokens(self) -> None:
        result = self.tool.execute(mode="stem_text", text="123 ?!")
        self.assertEqual(result["token_count"], 0)
        self.assertEqual(result["result"], [])

    def test_stem_text_list_input_shape(self) -> None:
        result = self.tool.execute(
            mode="stem_text", texts=["cats run", "ponies!"], lowercase=True
        )
        self.assertEqual(result["mode"], "stem_text")
        self.assertEqual(result["token_count"], 3)
        self.assertEqual(
            result["result"],
            [
                [{"original": "cats", "stem": "cat"}, {"original": "run", "stem": "run"}],
                [{"original": "ponies", "stem": "poni"}],
            ],
        )

    # ------------------------------------------------------------------ #
    # group mode
    # ------------------------------------------------------------------ #

    def test_group_collapses_inflections(self) -> None:
        result = self.tool.execute(
            mode="group", words=["caresses", "caress", "cats", "cat"]
        )
        self.assertEqual(
            result,
            {
                "mode": "group",
                "lowercase": False,
                "group_count": 2,
                "result": {"caress": ["caresses", "caress"], "cat": ["cats", "cat"]},
            },
        )

    def test_group_running_runs_runner_behavior(self) -> None:
        """Pinned light behavior: 'running'->'runn' (no doubling undo),
        'runs'->'run', 'runner' unchanged — three groups, not one."""
        result = self.tool.execute(mode="group", words=["running", "runs", "runner"])
        self.assertEqual(
            result["result"],
            {"runn": ["running"], "run": ["runs"], "runner": ["runner"]},
        )
        self.assertEqual(result["group_count"], 3)

    def test_group_dedupes_and_preserves_first_seen_order(self) -> None:
        result = self.tool.execute(
            mode="group", words=["ponies", "pony", "ponies", "cats", "cat", "pony"]
        )
        self.assertEqual(
            result["result"],
            {"poni": ["ponies", "pony"], "cat": ["cats", "cat"]},
        )
        self.assertEqual(list(result["result"]), ["poni", "cat"])

    def test_group_lowercase_merges_case_variants(self) -> None:
        result = self.tool.execute(
            mode="group", words=["Running", "running", "runs"], lowercase=True
        )
        self.assertEqual(
            result["result"], {"runn": ["Running", "running"], "run": ["runs"]}
        )

    # ------------------------------------------------------------------ #
    # Validation error matrix
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(mode="porter")

    def test_stem_requires_word_or_words(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a word"):
            self.tool.execute(mode="stem")

    def test_stem_rejects_word_and_words_together(self) -> None:
        with self.assertRaisesRegex(ValueError, "not both"):
            self.tool.execute(mode="stem", word="cat", words=["cats"])

    def test_stem_text_rejects_text_and_texts_together(self) -> None:
        with self.assertRaisesRegex(ValueError, "not both"):
            self.tool.execute(mode="stem_text", text="a", texts=["b"])

    def test_stem_text_requires_text_or_texts(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a text"):
            self.tool.execute(mode="stem_text")

    def test_group_requires_words_list(self) -> None:
        # no words at all — with or without a stray single word
        with self.assertRaisesRegex(ValueError, "group mode requires words"):
            self.tool.execute(mode="group")
        with self.assertRaisesRegex(ValueError, "group mode requires words"):
            self.tool.execute(mode="group", word="cat")
        # both given: the single-word variant is explicitly rejected
        with self.assertRaisesRegex(ValueError, "not a single word"):
            self.tool.execute(mode="group", word="cat", words=["cats"])

    def test_word_must_be_a_non_empty_string(self) -> None:
        for bad in ("", 42, True, ["cats"], {"word": "cats"}):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "word must be"):
                    self.tool.execute(mode="stem", word=bad)

    def test_word_must_be_pure_ascii_letters(self) -> None:
        for bad in ("well-known", "state of the art", "don't", "café", "cat3", " cat", "cat ", "c@t", "猫"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "must contain only ASCII English letters"):
                    self.tool.execute(mode="stem", word=bad)

    def test_hyphenated_compound_error_mentions_splitting(self) -> None:
        with self.assertRaisesRegex(ValueError, "hyphenated compounds.*split"):
            self.tool.execute(mode="stem", word="state-of-the-art")

    def test_words_list_validation(self) -> None:
        for bad in (None, "cats", 42, [], ["cats", 1], ["cats", None], [True], ["ok", ""]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="stem", words=bad)

    def test_word_too_long(self) -> None:
        with self.assertRaisesRegex(ValueError, "1,000-character limit"):
            self.tool.execute(mode="stem", word="a" * 1001)

    def test_words_over_ten_thousand_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "10,000-item limit"):
            self.tool.execute(mode="stem", words=["cat"] * 10001)
        result = self.tool.execute(mode="stem", words=["cat"] * 10000)
        self.assertEqual(result["count"], 10000)

    def test_text_validation(self) -> None:
        for bad in ("", 42, True):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "text must be"):
                    self.tool.execute(mode="stem_text", text=bad)
        with self.assertRaisesRegex(ValueError, "100,000-character limit"):
            self.tool.execute(mode="stem_text", text="a" * 100001)

    def test_texts_list_validation(self) -> None:
        for bad in (None, "cats", 42, [], [1], ["ok", ""]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="stem_text", texts=bad)

    def test_stem_text_token_cap(self) -> None:
        with self.assertRaisesRegex(ValueError, "10,000-token limit"):
            self.tool.execute(mode="stem_text", text="a " * 10001)
        result = self.tool.execute(mode="stem_text", text="a " * 10000)
        self.assertEqual(result["token_count"], 10000)

    def test_lowercase_must_be_boolean(self) -> None:
        for bad in ("yes", 1, ["true"]):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "lowercase must be a boolean"):
                    self.tool.execute(mode="stem", word="cats", lowercase=bad)

    # ------------------------------------------------------------------ #
    # Packaging: yaml registration and package export
    # ------------------------------------------------------------------ #

    def test_package_export(self) -> None:
        self.assertIs(ExportedLightStemmerTool, LightStemmerTool)


class LightStemmerRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped light_stemmer_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the LightStemmerTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "LightStemmerTool")

    def test_manager(self):
        """Verify the LightStemmerTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, LightStemmerTool)
        self.assertEqual(tool.name, "light_stemmer_tool")
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
