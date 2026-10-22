#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_regex_explain_tool.py

"""Offline unit tests for RegexExplainerTool.

The tool is built purely on the standard library ``re`` module and
never touches the network, so this suite runs fully offline.  Every
assertion is deterministic: token breakdowns are checked against
hand-written ground-truth tokens (token text, kind, meaning and
position), summaries and example strings against exact expected
values, and every generated example is additionally re-verified with
``re.fullmatch`` inside the test itself.
"""

import re
import unittest

from agentuniverse.agent.action.tool.common_tool import RegexExplainerTool
from agentuniverse.agent.action.tool.common_tool.regex_explain_tool import (
    RegexExplainerTool as DirectRegexExplainerTool,
)


class RegexExplainerToolBasicsTest(unittest.TestCase):
    """Identity, defaults and input validation."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def test_identity_and_export(self) -> None:
        self.assertIs(RegexExplainerTool, DirectRegexExplainerTool)
        self.assertEqual(self.tool.name, "regex_explain_tool")

    def test_description_mentions_modes(self) -> None:
        for word in ("explain", "validate", "examples"):
            self.assertIn(word, self.tool.description)

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="frobnicate", pattern="a")
        self.assertIn("mode must be one of", str(ctx.exception))

    def test_none_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode=None, pattern="a")

    def test_non_string_pattern_raises(self) -> None:
        for bad in (None, 123, True, ["a"], b"a"):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(mode="explain", pattern=bad)
            self.assertIn("pattern must be a string", str(ctx.exception))

    def test_overlong_pattern_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="explain", pattern="a" * 10_001)
        self.assertIn("10,000-character limit", str(ctx.exception))

    def test_non_compiling_pattern_raises_in_explain(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="explain", pattern="a(")
        self.assertIn("pattern does not compile", str(ctx.exception))

    def test_non_compiling_pattern_raises_in_examples(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="examples", pattern="[")

    def test_dangling_backslash_raises_in_explain(self) -> None:
        # A trailing backslash is broken syntax, not an unsupported
        # construct, so explain mode rejects it with ValueError.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="explain", pattern="abc\\")


class RegexExplainTokenTest(unittest.TestCase):
    """Ground truths for every supported token kind."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def _tokens(self, pattern: str):
        result = self.tool.execute(mode="explain", pattern=pattern)
        self.assertEqual(result["mode"], "explain")
        self.assertEqual(result["pattern"], pattern)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["compile_error"])
        self.assertEqual(result["unsupported"], [])
        return result["tokens"]

    def test_literal_and_run(self) -> None:
        tokens = self._tokens("ab1")
        self.assertEqual(tokens, [
            {"token": "a", "kind": "literal",
             "meaning": "the literal character 'a'", "position": 0,
             "char": "a"},
            {"token": "b", "kind": "literal",
             "meaning": "the literal character 'b'", "position": 1,
             "char": "b"},
            {"token": "1", "kind": "literal",
             "meaning": "the literal character '1'", "position": 2,
             "char": "1"},
        ])

    def test_dot(self) -> None:
        token = self._tokens("a.c")[1]
        self.assertEqual(token["token"], ".")
        self.assertEqual(token["kind"], "dot")
        self.assertEqual(
            token["meaning"],
            "any character except a newline (any character at all with "
            "the dotall flag)",
        )
        self.assertEqual(token["position"], 1)

    def test_anchor_caret(self) -> None:
        token = self._tokens("^a")[0]
        self.assertEqual(token["kind"], "anchor")
        self.assertEqual(
            token["meaning"],
            "anchor — the start of the string (or the start of a line "
            "with the multiline flag)",
        )

    def test_anchor_dollar(self) -> None:
        token = self._tokens("a$")[1]
        self.assertEqual(token["kind"], "anchor")
        self.assertEqual(
            token["meaning"],
            "anchor — the end of the string (or the end of a line with "
            "the multiline flag)",
        )

    def test_class_enumeration(self) -> None:
        token = self._tokens("[abc]")[0]
        self.assertEqual(token["kind"], "char_class")
        self.assertEqual(token["token"], "[abc]")
        self.assertFalse(token["negated"])
        self.assertEqual(token["items"], [
            {"type": "char", "value": "a"},
            {"type": "char", "value": "b"},
            {"type": "char", "value": "c"},
        ])
        self.assertEqual(
            token["meaning"], "any character in: 'a', 'b', 'c'")

    def test_class_ranges(self) -> None:
        token = self._tokens("[a-z0-9_]")[0]
        self.assertEqual(token["items"], [
            {"type": "range", "start": "a", "end": "z"},
            {"type": "range", "start": "0", "end": "9"},
            {"type": "char", "value": "_"},
        ])
        self.assertEqual(
            token["meaning"],
            "any character in: 'a' to 'z', '0' to '9', '_'")

    def test_class_negated(self) -> None:
        token = self._tokens("[^0-9]")[0]
        self.assertTrue(token["negated"])
        self.assertEqual(
            token["meaning"], "any character NOT in: '0' to '9'")

    def test_class_with_shorthand_and_escapes(self) -> None:
        token = self._tokens(r"[\d\-\\]")[0]
        self.assertEqual(token["items"], [
            {"type": "shorthand", "value": "d"},
            {"type": "char", "value": "-"},
            {"type": "char", "value": "\\"},
        ])
        self.assertEqual(
            token["meaning"],
            "any character in: digits, '-', '\\'")

    def test_all_class_shorthand_escapes(self) -> None:
        expectations = {
            r"\d": "any digit character (0-9)",
            r"\D": "any character that is not a digit",
            r"\w": "any word character (a letter, a digit or an "
                   "underscore)",
            r"\W": "any character that is not a word character (not a "
                   "letter, digit or underscore)",
            r"\s": "any whitespace character (space, tab, newline and "
                   "similar)",
            r"\S": "any character that is not whitespace",
        }
        for pattern, meaning in expectations.items():
            tokens = self._tokens(f"a{pattern}")
            token = tokens[1]
            self.assertEqual(token["kind"], "shorthand", pattern)
            self.assertEqual(token["token"], pattern)
            self.assertEqual(token["meaning"], meaning, pattern)
            self.assertEqual(token["which"], pattern[1], pattern)
            self.assertEqual(token["position"], 1, pattern)

    def test_boundaries(self) -> None:
        tokens = self._tokens(r"\ba\B")
        self.assertEqual(tokens[0]["kind"], "boundary")
        self.assertEqual(
            tokens[0]["meaning"],
            "a word boundary (a position between a word character and a "
            "non-word character)")
        self.assertEqual(tokens[2]["kind"], "boundary")
        self.assertEqual(
            tokens[2]["meaning"], "a position that is not a word boundary")

    def test_control_escapes(self) -> None:
        tokens = self._tokens(r"a\n\t")
        self.assertEqual(tokens[1]["token"], r"\n")
        self.assertEqual(tokens[1]["kind"], "literal")
        self.assertEqual(tokens[1]["meaning"], "a newline character")
        self.assertEqual(tokens[1]["char"], "\n")
        self.assertEqual(tokens[2]["token"], r"\t")
        self.assertEqual(tokens[2]["meaning"], "a tab character")
        self.assertEqual(tokens[2]["char"], "\t")

    def test_escaped_literal_characters(self) -> None:
        tokens = self._tokens(r"a\.\*\\")
        self.assertEqual(tokens[1]["token"], r"\.")
        self.assertEqual(tokens[1]["kind"], "literal")
        self.assertEqual(tokens[1]["meaning"],
                         "the literal character '.'")
        self.assertEqual(tokens[1]["char"], ".")
        self.assertEqual(tokens[2]["token"], r"\*")
        self.assertEqual(tokens[2]["char"], "*")
        self.assertEqual(tokens[3]["token"], "\\\\")
        self.assertEqual(tokens[3]["char"], "\\")

    def test_capturing_group(self) -> None:
        tokens = self._tokens("(ab)")
        self.assertEqual(tokens[0], {
            "token": "(", "kind": "group_open",
            "meaning": "start of a capturing group (the matched text is "
            "kept for backreferences)",
            "position": 0, "style": "capturing",
        })
        self.assertEqual(tokens[-1], {
            "token": ")", "kind": "group_close",
            "meaning": "end of the innermost currently open group",
            "position": 3,
        })

    def test_non_capturing_group(self) -> None:
        token = self._tokens("(?:ab)")[0]
        self.assertEqual(token["token"], "(?:")
        self.assertEqual(token["style"], "non_capturing")
        self.assertEqual(
            token["meaning"],
            "start of a non-capturing group (grouping only, the matched "
            "text is not kept)")

    def test_named_group(self) -> None:
        token = self._tokens("(?P<word>ab)")[0]
        self.assertEqual(token["token"], "(?P<word>")
        self.assertEqual(token["style"], "named")
        self.assertEqual(token["name"], "word")
        self.assertEqual(
            token["meaning"],
            "start of a named capturing group 'word' (the matched text "
            "is kept under that name)")

    def test_lookahead_groups(self) -> None:
        positive = self._tokens(r"a(?=b)")[1]
        self.assertEqual(positive["token"], "(?=")
        self.assertEqual(positive["style"], "lookahead_positive")
        self.assertEqual(
            positive["meaning"],
            "start of a positive lookahead (the enclosed pattern must "
            "match here, without consuming input)")
        negative = self._tokens(r"a(?!b)")[1]
        self.assertEqual(negative["token"], "(?!")
        self.assertEqual(negative["style"], "lookahead_negative")
        self.assertEqual(
            negative["meaning"],
            "start of a negative lookahead (the enclosed pattern must "
            "NOT match here, without consuming input)")

    def test_alternation(self) -> None:
        token = self._tokens("cat|dog")[3]
        self.assertEqual(token["token"], "|")
        self.assertEqual(token["kind"], "alternation")
        self.assertEqual(
            token["meaning"],
            "alternation — the pattern matches the part before or the "
            "part after this marker")
        self.assertEqual(token["position"], 3)

    def test_simple_quantifiers(self) -> None:
        tokens = self._tokens("ab*c+d?e")
        by_token = {t["token"]: t for t in tokens}
        star, plus, question = by_token["*"], by_token["+"], by_token["?"]
        self.assertEqual(
            (star["min"], star["max"], star["lazy"]),
            (0, None, False))
        self.assertEqual(
            star["meaning"],
            "zero or more repetitions of the previous element (greedy)")
        self.assertEqual((plus["min"], plus["max"]), (1, None))
        self.assertEqual(
            plus["meaning"],
            "one or more repetitions of the previous element (greedy)")
        self.assertEqual((question["min"], question["max"]), (0, 1))
        self.assertEqual(
            question["meaning"],
            "zero or one repetition of the previous element (greedy)")

    def test_brace_quantifiers(self) -> None:
        tokens = self._tokens("a{3}b{2,}c{2,4}d{,5}")
        expected = [
            ("{3}", 3, 3, "exactly 3 repetitions of the previous element"),
            ("{2,}", 2, None,
             "2 or more repetitions of the previous element (greedy)"),
            ("{2,4}", 2, 4,
             "between 2 and 4 repetitions of the previous element "
             "(greedy)"),
            ("{,5}", 0, 5,
             "between 0 and 5 repetitions of the previous element "
             "(greedy)"),
        ]
        quantifiers = [t for t in tokens if t["kind"] == "quantifier"]
        self.assertEqual(len(quantifiers), 4)
        for token, (text, low, high, meaning) in zip(quantifiers,
                                                     expected):
            self.assertEqual(token["token"], text)
            self.assertEqual(token["min"], low)
            self.assertEqual(token["max"], high)
            self.assertEqual(token["meaning"], meaning)

    def test_lazy_quantifiers(self) -> None:
        tokens = self._tokens(r"a.*?b+?c??d{2,4}?e*?")
        expected = [
            ("*?", "zero or more repetitions of the previous element — "
             "lazy: matches as few repetitions as possible"),
            ("+?", "one or more repetitions of the previous element — "
             "lazy: matches as few repetitions as possible"),
            ("??", "zero or one repetition of the previous element — "
             "lazy: matches as few repetitions as possible"),
            ("{2,4}?", "between 2 and 4 repetitions of the previous "
             "element — lazy: matches as few repetitions as possible"),
            ("*?", "zero or more repetitions of the previous element — "
             "lazy: matches as few repetitions as possible"),
        ]
        quantifiers = [t for t in tokens if t["kind"] == "quantifier"]
        self.assertEqual(len(quantifiers), 5)
        for token, (text, meaning) in zip(quantifiers, expected):
            self.assertEqual(token["token"], text)
            self.assertTrue(token["lazy"])
            self.assertNotIn("(greedy)", token["meaning"])
            self.assertEqual(token["meaning"], meaning)

    def test_literal_brace_is_not_a_quantifier(self) -> None:
        tokens = self._tokens("a{")
        self.assertEqual(tokens[1]["kind"], "literal")
        self.assertEqual(tokens[1]["char"], "{")

    def test_inline_flags(self) -> None:
        tokens = self._tokens("(?i)a")
        self.assertEqual(tokens[0], {
            "token": "(?i)", "kind": "flag",
            "meaning": "inline flag — case-insensitive matching",
            "position": 0, "flags": "i",
        })
        self.assertEqual(
            self._tokens("(?m)a")[0]["meaning"],
            "inline flag — multiline: '^' and '$' match at line "
            "boundaries")
        self.assertEqual(
            self._tokens("(?s)a")[0]["meaning"],
            "inline flag — dotall: '.' also matches newline")
        combined = self._tokens("(?is)a")[0]
        self.assertEqual(combined["flags"], "is")
        self.assertEqual(
            combined["meaning"],
            "inline flag — case-insensitive matching; dotall: '.' also "
            "matches newline")

    def test_positions_are_pattern_offsets(self) -> None:
        pattern = r"ab(?:c)|\d"
        tokens = self._tokens(pattern)
        starts = [t["position"] for t in tokens]
        ends = [t["position"] + len(t["token"]) for t in tokens]
        # The tokens tile the pattern exactly, in order.
        self.assertEqual(starts[0], 0)
        self.assertEqual(ends[:-1], starts[1:])
        self.assertEqual(ends[-1], len(pattern))

    def test_empty_pattern(self) -> None:
        result = self.tool.execute(mode="explain", pattern="")
        self.assertEqual(result["tokens"], [])
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["summary"],
            "the empty pattern — matches any string (including the "
            "empty string)")


class RegexExplainUnsupportedTest(unittest.TestCase):
    """Unsupported constructs are flagged with positions, never guessed."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def _flags(self, pattern: str):
        result = self.tool.execute(mode="explain", pattern=pattern)
        return result, result["unsupported"]

    def test_positive_lookbehind_flagged(self) -> None:
        result, flags = self._flags(r"(?<=ab)c")
        self.assertTrue(result["valid"])
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["construct"], "(?<=")
        self.assertEqual(flags[0]["position"], 0)
        self.assertIn("positive lookbehind", flags[0]["message"])

    def test_negative_lookbehind_flagged(self) -> None:
        _, flags = self._flags(r"c(?<!ab)")
        self.assertEqual(flags[0]["construct"], "(?<!")
        self.assertEqual(flags[0]["position"], 1)
        self.assertIn("negative lookbehind", flags[0]["message"])

    def test_numbered_backreference_flagged(self) -> None:
        _, flags = self._flags(r"(a)\1")
        self.assertEqual(flags[0]["construct"], r"\1")
        self.assertEqual(flags[0]["position"], 3)
        self.assertIn("backreference", flags[0]["message"])

    def test_unicode_class_flagged_with_compile_error(self) -> None:
        # \p is not valid Python re syntax at all: the breakdown is
        # still returned, together with the compile error details.
        result, flags = self._flags(r"a\p{L}b")
        self.assertFalse(result["valid"])
        self.assertEqual(flags[0]["construct"], r"\p")
        self.assertEqual(flags[0]["position"], 1)
        self.assertIn("does not support \\p", flags[0]["message"])
        error = result["compile_error"]
        self.assertIsNotNone(error)
        self.assertIsNotNone(error["position"])
        self.assertIn("message", error)

    def test_absolute_anchors_flagged(self) -> None:
        _, flags = self._flags(r"\Aa\b\Z")
        constructs = [f["construct"] for f in flags]
        self.assertEqual(constructs, [r"\A", r"\Z"])
        self.assertEqual([f["position"] for f in flags], [0, 5])

    def test_named_backreference_flagged(self) -> None:
        result, flags = self._flags(r"(?P<x>a)(?P=x)")
        self.assertTrue(result["valid"])
        self.assertEqual(flags[0]["construct"], "(?P=x)")
        self.assertEqual(flags[0]["position"], 8)
        self.assertIn("named backreference", flags[0]["message"])

    def test_comment_group_flagged(self) -> None:
        _, flags = self._flags(r"a(?# note)b")
        self.assertEqual(flags[0]["construct"], "(?# note)")
        self.assertEqual(flags[0]["position"], 1)

    def test_scoped_flags_flagged(self) -> None:
        _, flags = self._flags(r"(?i:ab)c")
        self.assertEqual(flags[0]["construct"], "(?i:")
        self.assertEqual(flags[0]["position"], 0)
        self.assertIn("scoped inline flags", flags[0]["message"])

    def test_hex_escape_flagged(self) -> None:
        result, flags = self._flags(r"\x41")
        self.assertIn("outside the supported subset",
                      flags[0]["message"])
        # \x41 is valid Python re (it is 'A'), so it compiles.
        self.assertTrue(result["valid"])

    def test_multiple_flags_each_with_position(self) -> None:
        result, flags = self._flags(r"(?<=a)\1\A")
        self.assertEqual(
            [(f["construct"], f["position"]) for f in flags],
            [("(?<=", 0), (r"\1", 6), (r"\A", 8)],
        )
        self.assertFalse(result["valid"])
        self.assertIsNotNone(result["compile_error"])

    def test_unsupported_class_escape_flagged(self) -> None:
        result, flags = self._flags(r"[\x41]")
        self.assertEqual(flags[0]["position"], 1)
        self.assertIn("inside a character class", flags[0]["message"])


class RegexSummaryTest(unittest.TestCase):
    """One-line summaries for simple patterns; notes for the rest."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def _summary(self, pattern: str):
        result = self.tool.execute(mode="explain", pattern=pattern)
        return result["summary"], result["summary_note"]

    def test_reference_example(self) -> None:
        summary, note = self._summary(r"^\d{3}-\d{4}$")
        self.assertEqual(summary,
                         "3 digits, a hyphen, 4 digits, anchored")
        self.assertIsNone(note)

    def test_plain_literal_run(self) -> None:
        self.assertEqual(self._summary("abc")[0], "the text 'abc'")

    def test_single_named_literal(self) -> None:
        self.assertEqual(self._summary("-")[0], "a hyphen")
        self.assertEqual(self._summary("@")[0], "an at sign")

    def test_single_unnamed_literal(self) -> None:
        self.assertEqual(self._summary("x")[0], "the character 'x'")

    def test_quantified_literal(self) -> None:
        self.assertEqual(self._summary("a-{3}b")[0],
                         "the character 'a', 3 hyphens, the character 'b'")

    def test_optional_and_star_literals(self) -> None:
        self.assertEqual(self._summary("a-?b")[0],
                         "the character 'a', an optional hyphen, "
                         "the character 'b'")
        self.assertEqual(self._summary("x_")[0], "the text 'x_'")

    def test_bounded_range_summary(self) -> None:
        self.assertEqual(self._summary(r"\w{2,4}")[0],
                         "2 to 4 word characters")

    def test_open_range_and_plus_summaries(self) -> None:
        self.assertEqual(self._summary(r"\d{2,}")[0], "2 or more digits")
        self.assertEqual(self._summary(r"\d+")[0], "one or more digits")
        self.assertEqual(self._summary(r"\s*")[0],
                         "zero or more whitespace characters")

    def test_negated_shorthand_summary(self) -> None:
        self.assertEqual(self._summary(r"\D+")[0],
                         "one or more non-digits")

    def test_lazy_annotation_in_summary(self) -> None:
        self.assertEqual(self._summary(r"\d+?")[0],
                         "one or more digits (lazy)")

    def test_start_only_anchor(self) -> None:
        self.assertEqual(self._summary(r"^\d+")[0],
                         "one or more digits, anchored at the start")

    def test_end_only_anchor(self) -> None:
        self.assertEqual(self._summary(r"\d+$")[0],
                         "one or more digits, anchored at the end")

    def test_anchor_only_patterns(self) -> None:
        self.assertEqual(self._summary("^$")[0],
                         "matches only the empty string")
        self.assertEqual(self._summary("$")[0],
                         "matches only the empty string")

    def test_control_escape_summary(self) -> None:
        self.assertEqual(self._summary(r"a\n")[0],
                         "the character 'a', a newline character")

    def test_omitted_for_dot(self) -> None:
        summary, note = self._summary(r"a.c")
        self.assertIsNone(summary)
        self.assertEqual(
            note,
            "summary omitted: the summary covers only literals, the "
            "class shorthands (\\d \\w \\s and their negations) and "
            "quantifiers; this pattern uses the any-character dot '.'")

    def test_omitted_for_bracket_class(self) -> None:
        _, note = self._summary("[abc]")
        self.assertIn("bracket character classes '[...]'", note)

    def test_omitted_for_group(self) -> None:
        _, note = self._summary("(ab)+")
        self.assertIn("groups", note)

    def test_omitted_for_alternation(self) -> None:
        _, note = self._summary("a|b")
        self.assertIn("alternation '|'", note)

    def test_omitted_for_boundary(self) -> None:
        _, note = self._summary(r"\ba\b")
        self.assertIn("word boundaries", note)

    def test_omitted_for_flag(self) -> None:
        _, note = self._summary("(?i)abc")
        self.assertIn("inline flags", note)

    def test_omitted_for_unsupported(self) -> None:
        _, note = self._summary(r"\Aabc")
        self.assertIn("constructs outside the supported subset", note)

    def test_omitted_for_mid_pattern_anchor(self) -> None:
        _, note = self._summary("a^b")
        self.assertIn("anchors are only summarised", note)


class RegexExamplesTest(unittest.TestCase):
    """Deterministic, verified example strings for simple patterns."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def test_reference_example(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"\d{3}-\d{4}")
        self.assertIsNone(result["note"])
        self.assertEqual(result["examples"],
                         ["000-0000", "555-5555", "999-9999"])
        for sample in result["examples"]:
            self.assertIsNotNone(re.fullmatch(r"\d{3}-\d{4}", sample))

    def test_bracket_class_with_ranges(self) -> None:
        result = self.tool.execute(mode="examples",
                                   pattern=r"[a-c]{2}[0-9]{1,2}")
        self.assertEqual(result["examples"], ["aa0", "bb44", "cc9"])
        for sample in result["examples"]:
            self.assertIsNotNone(
                re.fullmatch(r"[a-c]{2}[0-9]{1,2}", sample))

    def test_star_gives_empty_then_one(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a*")
        self.assertEqual(result["examples"], ["", "a"])

    def test_optional_gives_empty_then_char(self) -> None:
        result = self.tool.execute(mode="examples", pattern="ab?")
        self.assertEqual(result["examples"], ["a", "ab"])

    def test_plus_gives_one_then_two(self) -> None:
        result = self.tool.execute(mode="examples", pattern="ab+")
        self.assertEqual(result["examples"], ["ab", "abb"])

    def test_negated_class_examples(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"[^0-9]+")
        self.assertEqual(result["examples"], ["a", "AA", "X"])
        for sample in result["examples"]:
            self.assertIsNotNone(re.fullmatch(r"[^0-9]+", sample))

    def test_anchored_pattern_examples(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"^\d{2}$")
        self.assertEqual(result["examples"], ["00", "55", "99"])

    def test_fixed_counts_deduplicate_to_one(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a{3}")
        self.assertEqual(result["examples"], ["aaa"])

    def test_all_examples_verified(self) -> None:
        patterns = [
            r"\w+", r"[abc]+", r"a{2,4}", r"\d{5}", r"[a-z0-9]*",
            r"\s?", r"x?", r"[A-F0-9]{2}-[A-F0-9]{2}",
        ]
        for pattern in patterns:
            result = self.tool.execute(mode="examples", pattern=pattern)
            self.assertIsNone(result["note"], pattern)
            self.assertGreaterEqual(len(result["examples"]), 1, pattern)
            for sample in result["examples"]:
                self.assertIsNotNone(
                    re.fullmatch(pattern, sample), pattern)

    def test_examples_deterministic_across_calls(self) -> None:
        first = self.tool.execute(mode="examples", pattern=r"[a-f0-9]{3}")
        second = self.tool.execute(mode="examples", pattern=r"[a-f0-9]{3}")
        self.assertEqual(first["examples"], second["examples"])

    def test_note_for_groups(self) -> None:
        result = self.tool.execute(mode="examples", pattern="(ab)+")
        self.assertEqual(result["examples"], [])
        self.assertIn("this pattern uses groups", result["note"])

    def test_note_for_alternation(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a|b")
        self.assertIn("alternation '|'", result["note"])

    def test_note_for_dot(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a.c")
        self.assertIn("the any-character dot '.'", result["note"])

    def test_note_for_boundary(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"\ba\b")
        self.assertIn("word boundaries", result["note"])

    def test_note_for_inline_flag(self) -> None:
        result = self.tool.execute(mode="examples", pattern="(?i)abc")
        self.assertIn("inline flags", result["note"])

    def test_note_for_unsupported_construct(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"\Aa+")
        self.assertIn("constructs outside the supported subset",
                      result["note"])

    def test_note_for_huge_required_count(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a{200}")
        self.assertIn("repetition count exceeds", result["note"])

    def test_empty_pattern_example(self) -> None:
        result = self.tool.execute(mode="examples", pattern="")
        self.assertEqual(result["examples"], [""])


class RegexValidateTest(unittest.TestCase):
    """validate mode: the compile error is the payload, never a raise."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def test_valid_pattern(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="validate", pattern=r"^\d{3}-\d{4}$"),
            {"mode": "validate", "pattern": r"^\d{3}-\d{4}$",
             "valid": True, "result": "valid", "error": None},
        )

    def test_unbalanced_paren(self) -> None:
        result = self.tool.execute(mode="validate", pattern="a(")
        self.assertFalse(result["valid"])
        self.assertTrue(result["result"].startswith("invalid: "))
        error = result["error"]
        self.assertIn("missing ), unterminated subpattern",
                      error["message"])
        self.assertEqual(error["position"], 1)
        self.assertIsNotNone(error["lineno"])
        self.assertIsNotNone(error["colno"])

    def test_unterminated_class(self) -> None:
        result = self.tool.execute(mode="validate", pattern="[abc")
        self.assertFalse(result["valid"])
        self.assertIn("unterminated character set",
                      result["error"]["message"])
        self.assertEqual(result["error"]["position"], 0)

    def test_bad_quantifier_range(self) -> None:
        result = self.tool.execute(mode="validate", pattern="a{4,2}")
        self.assertFalse(result["valid"])
        self.assertIn("min repeat greater than max repeat",
                      result["error"]["message"])

    def test_validate_never_raises_on_bad_syntax(self) -> None:
        for pattern in ("a(", "[", "a{4,2}", "(?", "*", r"\p{L}",
                        "abc\\", "(?P<x>a", "a**"):
            result = self.tool.execute(mode="validate", pattern=pattern)
            self.assertFalse(result["valid"], pattern)
            self.assertIsNotNone(result["error"]["message"], pattern)

    def test_validate_empty_pattern(self) -> None:
        self.assertTrue(
            self.tool.execute(mode="validate", pattern="")["valid"])


class RegexExplainRegressionTest(unittest.TestCase):
    """Regressions for constructs that must be flagged, never guessed."""

    def setUp(self) -> None:
        self.tool = RegexExplainerTool()

    def _explain(self, pattern):
        return self.tool.execute(mode="explain", pattern=pattern)

    @staticmethod
    def _tiles(pattern, tokens):
        position = 0
        for token in tokens:
            if token["position"] != position:
                return False
            position += len(token["token"])
        return position == len(pattern)

    def test_possessive_quantifiers_flagged(self) -> None:
        for pattern, position in [("a*+", 2), ("a++", 2), ("a?+", 2),
                                  ("a{2,4}+", 6)]:
            result = self._explain(pattern)
            self.assertTrue(result["valid"], pattern)
            self.assertTrue(self._tiles(pattern, result["tokens"]), pattern)
            self.assertEqual(
                [(f["construct"], f["position"])
                 for f in result["unsupported"]],
                [("+", position)], pattern)
            flagged = [t for t in result["tokens"]
                       if t["kind"] == "unsupported"]
            self.assertEqual(len(flagged), 1, pattern)
            self.assertIn("possessive", flagged[0]["meaning"], pattern)

    def test_atomic_group_flagged(self) -> None:
        result = self._explain("(?>ab)")
        self.assertTrue(result["valid"])
        self.assertTrue(self._tiles("(?>ab)", result["tokens"]))
        self.assertEqual(result["unsupported"][0]["construct"], "(?>")
        self.assertEqual(result["unsupported"][0]["position"], 0)
        self.assertIn("atomic group", result["unsupported"][0]["message"])

    def test_unknown_group_letters_tile_exactly(self) -> None:
        for pattern in ("(?x)", "(?a)", "(?q)", "(?>a)"):
            result = self._explain(pattern)
            self.assertTrue(self._tiles(pattern, result["tokens"]), pattern)
            rendered = "".join(t["token"] for t in result["tokens"])
            self.assertEqual(rendered, pattern, pattern)

    def test_octal_zero_escape_message(self) -> None:
        result = self._explain(r"\0")
        self.assertEqual(result["unsupported"][0]["construct"], r"\0")
        self.assertIn("octal", result["unsupported"][0]["message"])
        self.assertNotIn("backreference",
                         result["unsupported"][0]["message"])

    def test_posix_class_flagged(self) -> None:
        result = self._explain(r"[[:alpha:]]")
        self.assertTrue(result["valid"])
        self.assertTrue(self._tiles(r"[[:alpha:]]", result["tokens"]))
        self.assertEqual(result["unsupported"][0]["construct"],
                         "[:alpha:]")
        self.assertEqual(result["unsupported"][0]["position"], 1)
        self.assertIn("POSIX", result["unsupported"][0]["message"])

    def test_posix_class_examples_blocked(self) -> None:
        result = self.tool.execute(mode="examples", pattern=r"[[:alpha:]]")
        self.assertEqual(result["examples"], [])
        self.assertIn("outside the supported subset", result["note"])

    def test_examples_blocked_by_unsupported_in_class(self) -> None:
        for pattern in (r"[\d\x41]", r"[\d\D]"):
            result = self.tool.execute(mode="examples", pattern=pattern)
            self.assertEqual(result["examples"], [], pattern)
            self.assertIn("outside the supported subset", result["note"],
                          pattern)

    def test_examples_mode_never_raises_re_error(self) -> None:
        for pattern in (r"[\A]", r"[\d\e]", r"\p{L}", r"[\b]"):
            result = self.tool.execute(mode="examples", pattern=pattern)
            self.assertEqual(result["examples"], [], pattern)
            self.assertIsNotNone(result["note"], pattern)

    def test_possessive_examples_blocked(self) -> None:
        result = self.tool.execute(mode="examples", pattern="a*+")
        self.assertEqual(result["examples"], [])
        self.assertIsNotNone(result["note"])

    def test_supported_patterns_still_unflagged(self) -> None:
        for pattern in (r"[.\d]", r"a+", r"[\d]", r"[a-z]+", r"\d{,5}"):
            result = self._explain(pattern)
            self.assertEqual(result["unsupported"], [], pattern)
            self.assertTrue(self._tiles(pattern, result["tokens"]), pattern)


if __name__ == "__main__":
    unittest.main()
