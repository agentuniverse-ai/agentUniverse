import os
import unittest

from agentuniverse.agent.action.tool.common_tool import WordShapeTool
from agentuniverse.agent.action.tool.common_tool import word_shape_tool as shape_module
from agentuniverse.agent.action.tool.common_tool.word_shape_tool import WordShapeTool as WordShapeToolDirect

YAML_PATH = os.path.join(
    os.path.dirname(shape_module.__file__), "word_shape_tool.yaml"
)

# Ground-truth shape table: (word, full shape, collapsed shape).
# Hand-computed from the documented character-to-symbol mapping.
SHAPE_TABLE = [
    ("Apple", "Xxxxx", "Xx"),
    ("APPLE", "XXXXX", "X"),
    ("123", "ddd", "d"),
    ("McDonald's", "XxXxxxxxpx", "XxXxpx"),
    ("USA1", "XXXd", "Xd"),
    ("hello-world", "xxxxxpxxxxx", "xpx"),
    ("CAFÉ", "XXXX", "X"),
    ("naïve", "xxxxx", "x"),
    ("北京2026", "CCdddd", "Cd"),
    ("こんにちは", "LLLLL", "L"),
    ("€20", "sdd", "sd"),
    ("a b", "xox", "xox"),
    ("½", "o", "o"),
    ("²", "d", "d"),
    ("Ⅷ", "X", "X"),
    ("、。", "pp", "p"),
    ("ァ", "L", "L"),
    ("＄5", "sd", "sd"),
]


class WordShapeToolShapeTest(unittest.TestCase):
    """Unit tests for the shape mode (full and collapsed shapes)."""

    def setUp(self):
        self.tool = WordShapeTool()

    def test_shape_table_ground_truths(self):
        """Every canonical table row maps to its exact full shape."""
        for word, expected, _ in SHAPE_TABLE:
            with self.subTest(word=word):
                result = self.tool.execute(mode="shape", word=word)
                self.assertEqual(
                    result,
                    {"mode": "shape", "collapsed": False, "word": word, "result": expected},
                )

    def test_shape_length_invariant(self):
        """The full shape always has exactly one symbol per character."""
        for word, _, _ in SHAPE_TABLE:
            with self.subTest(word=word):
                shape = self.tool.execute(mode="shape", word=word)["result"]
                self.assertEqual(len(shape), len(word))

    def test_collapsed_shape_ground_truths(self):
        """Every canonical table row maps to its exact collapsed shape."""
        for word, _, expected in SHAPE_TABLE:
            with self.subTest(word=word):
                result = self.tool.execute(
                    mode="shape", word=word, collapsed=True
                )
                self.assertEqual(
                    result,
                    {"mode": "shape", "collapsed": True, "word": word, "result": expected},
                )

    def test_collapsed_never_longer_than_full(self):
        """Collapsing runs can only shorten (or keep) the shape."""
        for word, _, _ in SHAPE_TABLE:
            with self.subTest(word=word):
                full = self.tool.execute(mode="shape", word=word)["result"]
                collapsed = self.tool.execute(
                    mode="shape", word=word, collapsed=True
                )["result"]
                self.assertLessEqual(len(collapsed), len(full))

    def test_shape_word_list(self):
        """A word list maps to a per-word list of shapes, order preserved."""
        result = self.tool.execute(
            mode="shape", words=["Apple", "USA1", "123", "北京2026"]
        )
        self.assertEqual(
            result,
            {
                "mode": "shape",
                "collapsed": False,
                "count": 4,
                "result": ["Xxxxx", "XXXd", "ddd", "CCdddd"],
            },
        )

    def test_shape_word_list_collapsed(self):
        """The collapsed option collapses each list entry independently."""
        result = self.tool.execute(
            mode="shape", words=["Apple", "USA1", "123", "北京2026"], collapsed=True
        )
        self.assertEqual(
            result["result"], ["Xx", "Xd", "d", "Cd"]
        )
        self.assertTrue(result["collapsed"])

    def test_shape_word_list_order_and_duplicates(self):
        """Duplicates and ordering are preserved verbatim."""
        result = self.tool.execute(mode="shape", words=["b", "a", "b"])
        self.assertEqual(result["result"], ["x", "x", "x"])
        result = self.tool.execute(mode="shape", words=["A", "a", "A"])
        self.assertEqual(result["result"], ["X", "x", "X"])

    def test_shape_deterministic(self):
        """Repeated calls return byte-identical results."""
        first = self.tool.execute(mode="shape", word="McDonald's")
        for _ in range(5):
            self.assertEqual(self.tool.execute(mode="shape", word="McDonald's"), first)


class WordShapeToolNormalizeDigitsTest(unittest.TestCase):
    """Unit tests for the normalize_digits mode."""

    def setUp(self):
        self.tool = WordShapeTool()

    def test_normalize_ground_truths(self):
        """Digit runs collapse to a single zero; non-digits are untouched."""
        cases = [
            ("iPhone 15 Pro", "iPhone 0 Pro", 1),
            ("123", "0", 1),
            ("a12b345", "a0b0", 2),
            ("2026-10-20", "0-0-0", 3),
            ("hello", "hello", 0),
            ("1a2", "0a0", 2),
            ("٣٤x9", "0x0", 2),
            ("²²", "0", 1),
            ("v1.2.3", "v0.0.0", 3),
        ]
        for text, expected, runs in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="normalize_digits", text=text)
                self.assertEqual(
                    result,
                    {"mode": "normalize_digits", "digit_runs": runs, "result": expected},
                )

    def test_normalize_never_adds_zeros_without_digits(self):
        """Text without digits is returned unchanged."""
        self.assertEqual(
            self.tool.execute(mode="normalize_digits", text="一、二。三")["result"],
            "一、二。三",
        )

    def test_normalize_round_trips_with_shape(self):
        """Normalized text and its shape are consistent (zeros -> d)."""
        normalized = self.tool.execute(mode="normalize_digits", text="iPhone 15 Pro")["result"]
        shape = self.tool.execute(mode="shape", word=normalized)["result"]
        self.assertEqual(shape, "xXxxxxodoXxx")


class WordShapeToolAnalyzeTest(unittest.TestCase):
    """Unit tests for the analyze mode (hand-computed arithmetic)."""

    def setUp(self):
        self.tool = WordShapeTool()

    def assertAnalysis(self, word, expected):
        """Assert the full analyze payload for a word."""
        result = self.tool.execute(mode="analyze", word=word)
        self.assertEqual(result["mode"], "analyze")
        self.assertEqual(result["word"], word)
        self.assertEqual(result["result"], expected)

    def test_analyze_iphone7(self):
        """'iPhone7': 1 digit and 6 letters out of 7 characters."""
        self.assertAnalysis(
            "iPhone7",
            {
                "shape": "xXxxxxd",
                "collapsed": "xXxd",
                "is_capitalized": False,
                "is_all_caps": False,
                "digit_ratio": 1 / 7,
                "alpha_ratio": 6 / 7,
                "has_hyphen": False,
                "length": 7,
                "script": "latin",
            },
        )

    def test_analyze_usa_hyphen_digit(self):
        """'USA-1': all caps with a hyphen; ratios 1/5 and 3/5."""
        self.assertAnalysis(
            "USA-1",
            {
                "shape": "XXXpd",
                "collapsed": "Xpd",
                "is_capitalized": True,
                "is_all_caps": True,
                "digit_ratio": 1 / 5,
                "alpha_ratio": 3 / 5,
                "has_hyphen": True,
                "length": 5,
                "script": "latin",
            },
        )

    def test_analyze_cjk(self):
        """'北京2026': CJK script; ratios 4/6 and 2/6."""
        self.assertAnalysis(
            "北京2026",
            {
                "shape": "CCdddd",
                "collapsed": "Cd",
                "is_capitalized": False,
                "is_all_caps": False,
                "digit_ratio": 4 / 6,
                "alpha_ratio": 2 / 6,
                "has_hyphen": False,
                "length": 6,
                "script": "cjk",
            },
        )

    def test_analyze_mixed_script(self):
        """'你好world': CJK plus Latin letters -> mixed; ratios 0/7 and 7/7."""
        self.assertAnalysis(
            "你好world",
            {
                "shape": "CCxxxxx",
                "collapsed": "Cx",
                "is_capitalized": False,
                "is_all_caps": False,
                "digit_ratio": 0 / 7,
                "alpha_ratio": 7 / 7,
                "has_hyphen": False,
                "length": 7,
                "script": "mixed",
            },
        )

    def test_analyze_no_letters(self):
        """'123': no letters at all -> unknown script; ratios 1.0 and 0.0."""
        self.assertAnalysis(
            "123",
            {
                "shape": "ddd",
                "collapsed": "d",
                "is_capitalized": False,
                "is_all_caps": False,
                "digit_ratio": 1.0,
                "alpha_ratio": 0.0,
                "has_hyphen": False,
                "length": 3,
                "script": "unknown",
            },
        )

    def test_analyze_unicode_letters(self):
        """'Naïve-Word2': ratios 1/11 and 9/11; hyphen and two capitals."""
        self.assertAnalysis(
            "Naïve-Word2",
            {
                "shape": "XxxxxpXxxxd",
                "collapsed": "XxpXxd",
                "is_capitalized": True,
                "is_all_caps": False,
                "digit_ratio": 1 / 11,
                "alpha_ratio": 9 / 11,
                "has_hyphen": True,
                "length": 11,
                "script": "latin",
            },
        )

    def test_analyze_all_caps_accented(self):
        """'CAFÉ': accented capitals count as uppercase letters."""
        self.assertAnalysis(
            "CAFÉ",
            {
                "shape": "XXXX",
                "collapsed": "X",
                "is_capitalized": True,
                "is_all_caps": True,
                "digit_ratio": 0 / 4,
                "alpha_ratio": 4 / 4,
                "has_hyphen": False,
                "length": 4,
                "script": "latin",
            },
        )

    def test_analyze_superscript_digit(self):
        """'²x': the superscript two is a digit for both shape and ratio."""
        self.assertAnalysis(
            "²x",
            {
                "shape": "dx",
                "collapsed": "dx",
                "is_capitalized": False,
                "is_all_caps": False,
                "digit_ratio": 1 / 2,
                "alpha_ratio": 1 / 2,
                "has_hyphen": False,
                "length": 2,
                "script": "latin",
            },
        )

    def test_analyze_ratios_sum_bounds(self):
        """digit_ratio and alpha_ratio stay within [0, 1] for table words."""
        for word, _, _ in SHAPE_TABLE:
            with self.subTest(word=word):
                analysis = self.tool.execute(mode="analyze", word=word)["result"]
                for key in ("digit_ratio", "alpha_ratio"):
                    self.assertGreaterEqual(analysis[key], 0.0)
                    self.assertLessEqual(analysis[key], 1.0)


class WordShapeToolBatchShapesTest(unittest.TestCase):
    """Unit tests for the batch_shapes mode (frequency profiling)."""

    def setUp(self):
        self.tool = WordShapeTool()

    def test_batch_frequency(self):
        """Counts aggregate per unique shape across all tokens."""
        result = self.tool.execute(
            mode="batch_shapes", text="the cat sat on the mat the"
        )
        self.assertEqual(
            result,
            {
                "mode": "batch_shapes",
                "token_count": 7,
                "unique_count": 2,
                "top_n": None,
                "result": [
                    {"shape": "xxx", "count": 6},
                    {"shape": "xx", "count": 1},
                ],
            },
        )

    def test_batch_tie_breaks_alphabetically(self):
        """Equal counts are ordered by ascending shape string."""
        result = self.tool.execute(mode="batch_shapes", text="a bb ccc bb a")
        self.assertEqual(
            result["result"],
            [
                {"shape": "x", "count": 2},
                {"shape": "xx", "count": 2},
                {"shape": "xxx", "count": 1},
            ],
        )

    def test_batch_mixed_case_ordering(self):
        """All-unique shapes sort deterministically by ASCII shape string."""
        result = self.tool.execute(mode="batch_shapes", text="Apple apple APPLE 123")
        self.assertEqual(result["token_count"], 4)
        self.assertEqual(result["unique_count"], 4)
        self.assertEqual(
            [entry["shape"] for entry in result["result"]],
            ["XXXXX", "Xxxxx", "ddd", "xxxxx"],
        )

    def test_batch_top_n(self):
        """top_n truncates the frequency-sorted list."""
        full = self.tool.execute(
            mode="batch_shapes", text="the cat sat on the mat the"
        )
        top = self.tool.execute(
            mode="batch_shapes", text="the cat sat on the mat the", top_n=1
        )
        self.assertEqual(top["top_n"], 1)
        self.assertEqual(top["result"], full["result"][:1])
        self.assertEqual(top["token_count"], full["token_count"])
        self.assertEqual(top["unique_count"], full["unique_count"])

    def test_batch_top_n_larger_than_unique_count(self):
        """An oversized top_n returns the full list."""
        result = self.tool.execute(mode="batch_shapes", text="a bb ccc bb a", top_n=100)
        self.assertEqual(len(result["result"]), 3)

    def test_batch_whitespace_split(self):
        """Any whitespace run separates tokens; none is kept."""
        result = self.tool.execute(mode="batch_shapes", text="A\tb\n\nA  c")
        self.assertEqual(result["token_count"], 4)
        self.assertEqual(
            result["result"],
            [
                {"shape": "X", "count": 2},
                {"shape": "x", "count": 2},
            ],
        )

    def test_batch_cjk_and_punct_tokens(self):
        """CJK and punctuation tokens profile like any other token."""
        result = self.tool.execute(mode="batch_shapes", text="北京 2026 北京 !")
        self.assertEqual(result["token_count"], 4)
        self.assertEqual(
            result["result"],
            [
                {"shape": "CC", "count": 2},
                {"shape": "dddd", "count": 1},
                {"shape": "p", "count": 1},
            ],
        )


class WordShapeToolErrorTest(unittest.TestCase):
    """Unit tests for the strict validation error matrix."""

    def setUp(self):
        self.tool = WordShapeTool()

    def assertInvalid(self, **kwargs):
        """Every malformed call raises ValueError mentioning the tool."""
        with self.assertRaises(ValueError) as raised:
            self.tool.execute(**kwargs)
        self.assertIn("word_shape_tool", str(raised.exception))

    def test_unknown_mode(self):
        """Modes outside the four documented ones are rejected."""
        self.assertInvalid(mode="shapes", word="Apple")
        self.assertInvalid(mode="word_shape", word="Apple")
        self.assertInvalid(mode=1, word="Apple")
        self.assertInvalid(mode=None, word="Apple")

    def test_shape_requires_exactly_one_word_argument(self):
        """word and words are mutually exclusive and jointly required."""
        self.assertInvalid(mode="shape")
        self.assertInvalid(mode="shape", word=None, words=None)
        self.assertInvalid(mode="shape", word="Apple", words=["Pear"])
        self.assertInvalid(mode="shape", word="Apple", words=[])

    def test_shape_bad_word(self):
        """word must be a non-empty string."""
        self.assertInvalid(mode="shape", word="")
        self.assertInvalid(mode="shape", word=123)
        self.assertInvalid(mode="shape", word=True)
        self.assertInvalid(mode="shape", word=["Apple"])
        self.assertInvalid(mode="shape", word=None)

    def test_shape_bad_words(self):
        """words must be a non-empty list of non-empty strings."""
        self.assertInvalid(mode="shape", words=[])
        self.assertInvalid(mode="shape", words="Apple")
        self.assertInvalid(mode="shape", words={"word": "Apple"})
        self.assertInvalid(mode="shape", words=None)
        self.assertInvalid(mode="shape", words=["ok", ""])
        self.assertInvalid(mode="shape", words=["ok", 5])
        self.assertInvalid(mode="shape", words=["ok", None])
        self.assertInvalid(mode="shape", words=["ok", True])

    def test_shape_bad_collapsed(self):
        """collapsed must be a boolean or None."""
        self.assertInvalid(mode="shape", word="Apple", collapsed="yes")
        self.assertInvalid(mode="shape", word="Apple", collapsed=1)
        self.assertInvalid(mode="shape", word="Apple", collapsed="true")

    def test_normalize_digits_bad_text(self):
        """normalize_digits requires a non-empty string."""
        self.assertInvalid(mode="normalize_digits")
        self.assertInvalid(mode="normalize_digits", text="")
        self.assertInvalid(mode="normalize_digits", text=None)
        self.assertInvalid(mode="normalize_digits", text=42)
        self.assertInvalid(mode="normalize_digits", text=True)

    def test_analyze_bad_word(self):
        """analyze requires a single non-empty string word."""
        self.assertInvalid(mode="analyze")
        self.assertInvalid(mode="analyze", word="")
        self.assertInvalid(mode="analyze", word=None)
        self.assertInvalid(mode="analyze", word=["Apple"])
        self.assertInvalid(mode="analyze", word=3.14)

    def test_batch_shapes_bad_text(self):
        """batch_shapes requires a non-empty string with at least one token."""
        self.assertInvalid(mode="batch_shapes")
        self.assertInvalid(mode="batch_shapes", text="")
        self.assertInvalid(mode="batch_shapes", text=None)
        self.assertInvalid(mode="batch_shapes", text=1234)
        self.assertInvalid(mode="batch_shapes", text="   ")
        self.assertInvalid(mode="batch_shapes", text="\t\n ")

    def test_batch_shapes_bad_top_n(self):
        """top_n must be a positive integer or None."""
        self.assertInvalid(mode="batch_shapes", text="a b", top_n=0)
        self.assertInvalid(mode="batch_shapes", text="a b", top_n=-3)
        self.assertInvalid(mode="batch_shapes", text="a b", top_n="3")
        self.assertInvalid(mode="batch_shapes", text="a b", top_n=2.5)
        self.assertInvalid(mode="batch_shapes", text="a b", top_n=True)

    def test_oversized_inputs(self):
        """Inputs beyond the documented caps are rejected."""
        self.assertInvalid(mode="shape", word="a" * 100_001)
        self.assertInvalid(mode="normalize_digits", text="a" * 100_001)
        self.assertInvalid(mode="analyze", word="a" * 100_001)
        self.assertInvalid(mode="batch_shapes", text="a " * 100_001)
        self.assertInvalid(mode="shape", words=["x"] * 10_001)
        self.assertInvalid(mode="batch_shapes", text="a b", top_n=10_001)

    def test_long_but_valid_input_accepted(self):
        """Inputs exactly at the caps are accepted."""
        result = self.tool.execute(mode="shape", word="a" * 100_000)
        self.assertEqual(len(result["result"]), 100_000)
        result = self.tool.execute(mode="shape", words=["x"] * 10_000)
        self.assertEqual(result["count"], 10_000)


class WordShapeToolPackageTest(unittest.TestCase):
    """Package-level checks: export and YAML configuration."""

    def test_package_export(self):
        """The tool is exported from the common_tool package."""
        self.assertIs(WordShapeTool, WordShapeToolDirect)

    def test_tool_metadata(self):
        """The tool carries the documented name and modes."""
        tool = WordShapeTool()
        self.assertEqual(tool.name, "word_shape_tool")
        self.assertIn("shape", tool.MODES)
        self.assertIn("normalize_digits", tool.MODES)
        self.assertIn("analyze", tool.MODES)
        self.assertIn("batch_shapes", tool.MODES)

    def test_yaml_config_exists_and_declares_class(self):
        """The YAML config declares the tool module and class."""
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("name: word_shape_tool", content)
        self.assertIn("class: WordShapeTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool.word_shape_tool",
            content,
        )


if __name__ == "__main__":
    unittest.main()
