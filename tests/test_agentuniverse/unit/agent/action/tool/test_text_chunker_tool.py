#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_chunker_tool.py

"""Offline unit tests for TextChunkerTool.

The tool is built purely on the standard library (re + string slicing)
and never touches the network, so this suite runs fully offline. Every
assertion is deterministic: chunk boundaries are checked against
hand-computed ground-truth offsets, the three strategies are exercised
with exact expected chunk lists, lossless/coverage properties are
verified for the char and word modes, and the strict parameter
validation matrix is covered case by case.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TextChunkerTool
from agentuniverse.agent.action.tool.common_tool.text_chunker_tool import (
    TextChunkerTool as DirectTextChunkerTool,
)

UNICODE_TEXT = "héllo 世界 — naïve café 🌍 query"


class TextChunkerToolCharTest(unittest.TestCase):
    """char strategy — fixed-size sliding character window."""

    def setUp(self) -> None:
        self.tool = TextChunkerTool()

    def test_char_exact_chunks_no_overlap(self) -> None:
        result = self.tool.execute(
            strategy="char", text="abcdefghij", chunk_size=4, overlap=0
        )
        self.assertEqual(
            result,
            {
                "strategy": "char",
                "chunk_size": 4,
                "overlap": 0,
                "chunk_count": 3,
                "total_chars": 10,
                "chunks": [
                    {"index": 0, "text": "abcd", "start": 0, "end": 4},
                    {"index": 1, "text": "efgh", "start": 4, "end": 8},
                    {"index": 2, "text": "ij", "start": 8, "end": 10},
                ],
            },
        )

    def test_char_single_chunk_when_text_fits(self) -> None:
        result = self.tool.execute(
            strategy="char", text="abc", chunk_size=10, overlap=4
        )
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(
            result["chunks"][0],
            {"index": 0, "text": "abc", "start": 0, "end": 3},
        )

    def test_char_overlap_window_positions(self) -> None:
        result = self.tool.execute(
            strategy="char", text="abcdefghij", chunk_size=4, overlap=2
        )
        self.assertEqual(
            [(c["start"], c["end"]) for c in result["chunks"]],
            [(0, 4), (2, 6), (4, 8), (6, 10)],
        )
        self.assertEqual(
            [c["text"] for c in result["chunks"]],
            ["abcd", "cdef", "efgh", "ghij"],
        )

    def test_char_consecutive_chunks_share_overlap_chars(self) -> None:
        chunks = self.tool.execute(
            strategy="char", text="abcdefghij", chunk_size=4, overlap=2
        )["chunks"]
        for previous, current in zip(chunks, chunks[1:]):
            self.assertEqual(
                previous["text"][-2:],
                current["text"][:2],
                "neighbouring chunks must share the overlap characters",
            )

    def test_char_lossless_without_overlap(self) -> None:
        for text in ("abcdefghij", UNICODE_TEXT, "line1\nline2\ttab", "  \n\t "):
            chunks = self.tool.execute(
                strategy="char", text=text, chunk_size=3, overlap=0
            )["chunks"]
            self.assertEqual("".join(c["text"] for c in chunks), text)

    def test_char_full_coverage_with_overlap(self) -> None:
        text = "z" * 25
        chunks = self.tool.execute(
            strategy="char", text=text, chunk_size=6, overlap=4
        )["chunks"]
        covered = set()
        for chunk in chunks:
            covered.update(range(chunk["start"], chunk["end"]))
        self.assertEqual(covered, set(range(len(text))))

    def test_char_default_chunk_size_and_overlap(self) -> None:
        result = self.tool.execute(strategy="char", text="a" * 450)
        self.assertEqual(result["chunk_size"], 200)
        self.assertEqual(result["overlap"], 0)
        self.assertEqual(result["chunk_count"], 3)
        self.assertEqual(
            [len(c["text"]) for c in result["chunks"]], [200, 200, 50]
        )

    def test_char_offsets_index_original_text(self) -> None:
        text = UNICODE_TEXT
        for chunk in self.tool.execute(
            strategy="char", text=text, chunk_size=7, overlap=3
        )["chunks"]:
            self.assertEqual(
                chunk["text"], text[chunk["start"]:chunk["end"]]
            )


class TextChunkerToolWordTest(unittest.TestCase):
    """word strategy — whitespace-word windows preserving original spans."""

    def setUp(self) -> None:
        self.tool = TextChunkerTool()
        self.text = "the quick brown fox jumps over"

    def test_word_exact_chunks_no_overlap(self) -> None:
        result = self.tool.execute(
            strategy="word", text=self.text, chunk_size=2, overlap=0
        )
        self.assertEqual(result["total_words"], 6)
        self.assertEqual(result["chunk_count"], 3)
        self.assertEqual(
            result["chunks"],
            [
                {
                    "index": 0,
                    "text": "the quick",
                    "start": 0,
                    "end": 9,
                    "word_count": 2,
                },
                {
                    "index": 1,
                    "text": "brown fox",
                    "start": 10,
                    "end": 19,
                    "word_count": 2,
                },
                {
                    "index": 2,
                    "text": "jumps over",
                    "start": 20,
                    "end": 30,
                    "word_count": 2,
                },
            ],
        )

    def test_word_overlap_shares_words(self) -> None:
        chunks = self.tool.execute(
            strategy="word", text=self.text, chunk_size=3, overlap=1
        )["chunks"]
        self.assertEqual(
            [c["text"] for c in chunks],
            ["the quick brown", "brown fox jumps", "jumps over"],
        )
        self.assertEqual(
            [c["word_count"] for c in chunks], [3, 3, 2]
        )
        for previous, current in zip(chunks, chunks[1:]):
            self.assertEqual(
                previous["text"].split()[-1:], current["text"].split()[:1]
            )

    def test_word_preserves_internal_whitespace(self) -> None:
        result = self.tool.execute(
            strategy="word", text="alpha\tbeta\ngamma  delta", chunk_size=2
        )
        self.assertEqual(
            [c["text"] for c in result["chunks"]],
            ["alpha\tbeta", "gamma  delta"],
        )
        self.assertEqual(
            [(c["start"], c["end"]) for c in result["chunks"]],
            [(0, 10), (11, 23)],
        )

    def test_word_all_words_recovered_in_order(self) -> None:
        chunks = self.tool.execute(
            strategy="word", text=UNICODE_TEXT, chunk_size=2, overlap=0
        )["chunks"]
        recovered = [w for c in chunks for w in c["text"].split()]
        self.assertEqual(recovered, UNICODE_TEXT.split())

    def test_word_offsets_index_original_text(self) -> None:
        for chunk in self.tool.execute(
            strategy="word", text=UNICODE_TEXT, chunk_size=2, overlap=1
        )["chunks"]:
            self.assertEqual(
                chunk["text"], UNICODE_TEXT[chunk["start"]:chunk["end"]]
            )

    def test_word_whitespace_only_text_yields_no_chunks(self) -> None:
        result = self.tool.execute(
            strategy="word", text="   \n\t ", chunk_size=3, overlap=1
        )
        self.assertEqual(result["total_words"], 0)
        self.assertEqual(result["chunk_count"], 0)
        self.assertEqual(result["chunks"], [])


class TextChunkerToolSentenceTest(unittest.TestCase):
    """sentence strategy — packing sentences under a character budget."""

    def setUp(self) -> None:
        self.tool = TextChunkerTool()
        self.text = "One. Two! Three? Four."

    def test_sentence_single_chunk_when_budget_allows(self) -> None:
        result = self.tool.execute(
            strategy="sentence", text=self.text, chunk_size=100, overlap=0
        )
        self.assertEqual(result["total_sentences"], 4)
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(
            result["chunks"][0],
            {
                "index": 0,
                "text": self.text,
                "start": 0,
                "end": 22,
                "sentence_count": 4,
                "oversized": False,
            },
        )

    def test_sentence_packing_respects_budget(self) -> None:
        result = self.tool.execute(
            strategy="sentence", text=self.text, chunk_size=10, overlap=0
        )
        self.assertEqual(
            [(c["text"], c["sentence_count"]) for c in result["chunks"]],
            [("One. Two!", 2), ("Three?", 1), ("Four.", 1)],
        )
        self.assertEqual(
            [(c["start"], c["end"]) for c in result["chunks"]],
            [(0, 9), (10, 16), (17, 22)],
        )

    def test_sentence_overlap_repeats_sentences(self) -> None:
        chunks = self.tool.execute(
            strategy="sentence", text=self.text, chunk_size=10, overlap=1
        )["chunks"]
        self.assertEqual(
            [c["text"] for c in chunks],
            ["One. Two!", "Two!", "Three?", "Four."],
        )

    def test_sentence_oversized_flagged_not_truncated(self) -> None:
        long_sentence = "a" * 20 + "."
        result = self.tool.execute(
            strategy="sentence", text=long_sentence, chunk_size=10, overlap=0
        )
        self.assertEqual(result["chunk_count"], 1)
        self.assertTrue(result["chunks"][0]["oversized"])
        self.assertEqual(result["chunks"][0]["text"], long_sentence)

    def test_sentence_unterminated_tail_is_final_sentence(self) -> None:
        text = "First. no terminator tail"
        result = self.tool.execute(
            strategy="sentence", text=text, chunk_size=100, overlap=0
        )
        self.assertEqual(result["total_sentences"], 2)
        self.assertEqual(
            [c["text"] for c in result["chunks"]], [text]
        )

    def test_sentence_leading_whitespace_and_quotes(self) -> None:
        text = '  He said "Stop!" Then left.'
        result = self.tool.execute(
            strategy="sentence", text=text, chunk_size=100, overlap=0
        )
        self.assertEqual(result["total_sentences"], 2)
        chunk = result["chunks"][0]
        self.assertEqual(chunk["text"], 'He said "Stop!" Then left.')
        self.assertEqual(chunk["start"], 2)

    def test_sentence_large_overlap_still_progresses(self) -> None:
        # overlap far larger than any chunk's sentence count must not
        # stall: each chunk advances by at least one sentence.
        chunks = self.tool.execute(
            strategy="sentence", text=self.text, chunk_size=4, overlap=100
        )["chunks"]
        self.assertEqual(
            [c["text"] for c in chunks], ["One.", "Two!", "Three?", "Four."]
        )

    def test_sentence_unicode_oversized_and_recovery(self) -> None:
        # UNICODE_TEXT + "." is 30 characters: alone it exceeds the 12
        # character budget and must be emitted as one flagged chunk;
        # "Second part." is exactly 12 characters and fits.
        text = UNICODE_TEXT + ". Second part."
        result = self.tool.execute(
            strategy="sentence", text=text, chunk_size=12, overlap=1
        )
        self.assertEqual(
            [(c["text"], c["oversized"]) for c in result["chunks"]],
            [(UNICODE_TEXT + ".", True), ("Second part.", False)],
        )
        self.assertEqual(
            [c["sentence_count"] for c in result["chunks"]], [1, 1]
        )


class TextChunkerToolValidationTest(unittest.TestCase):
    """Strict parameter validation — ValueError before any computation."""

    def setUp(self) -> None:
        self.tool = TextChunkerTool()

    def test_unknown_strategy_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(strategy="paragraph", text="hi")
        self.assertIn("strategy must be one of", str(ctx.exception))

    def test_missing_strategy_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(text="hi")

    def test_non_string_text_rejected(self) -> None:
        for bad in (None, 123, True, ["ab"], {"a": 1}):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(strategy="char", text=bad)
            self.assertIn("text must be a non-empty string", str(ctx.exception))

    def test_empty_text_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(strategy="char", text="")

    def test_text_over_cap_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(strategy="char", text="a" * 1_000_001)
        self.assertIn("1,000,000-character limit", str(ctx.exception))

    def test_invalid_chunk_size_rejected(self) -> None:
        for bad in (0, -5, "10", 2.5, True, [4]):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(strategy="char", text="abc", chunk_size=bad)
            self.assertIn("chunk_size", str(ctx.exception))

    def test_invalid_overlap_rejected(self) -> None:
        for bad in (-1, "2", 1.5, True):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(strategy="char", text="abc", overlap=bad)
            self.assertIn("overlap must be a non-negative integer", str(ctx.exception))

    def test_overlap_not_smaller_than_chunk_size_rejected(self) -> None:
        for strategy in ("char", "word"):
            with self.assertRaises(ValueError) as ctx:
                self.tool.execute(
                    strategy=strategy, text="abc def", chunk_size=5, overlap=5
                )
            self.assertIn("overlap must be smaller than chunk_size", str(ctx.exception))

    def test_sentence_mode_allows_any_non_negative_overlap(self) -> None:
        # sentence overlap is measured in sentences, so it may exceed
        # the character budget — progress is guaranteed structurally.
        result = self.tool.execute(
            strategy="sentence", text="A. B! C? D.", chunk_size=3, overlap=99
        )
        self.assertGreaterEqual(result["chunk_count"], 1)

    def test_max_chunks_exceeded_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(strategy="char", text="a" * 10_001, chunk_size=1)
        self.assertIn("more than the 10,000-chunk limit", str(ctx.exception))

    def test_max_chunks_boundary_allowed(self) -> None:
        result = self.tool.execute(
            strategy="char", text="a" * 10_000, chunk_size=1
        )
        self.assertEqual(result["chunk_count"], 10_000)


class TextChunkerToolConfigTest(unittest.TestCase):
    """Package export, YAML configuration and determinism."""

    def setUp(self) -> None:
        self.tool = TextChunkerTool()

    def test_package_and_direct_exports_match(self) -> None:
        self.assertIs(TextChunkerTool, DirectTextChunkerTool)

    def test_tool_identity(self) -> None:
        self.assertEqual(self.tool.name, "text_chunker_tool")
        self.assertIn("stdlib", self.tool.description)

    def test_yaml_configuration_structure(self) -> None:
        import os

        import yaml

        import agentuniverse.agent.action.tool.common_tool.text_chunker_tool \
            as chunker_module

        path = os.path.join(
            os.path.dirname(chunker_module.__file__), "text_chunker_tool.yaml"
        )
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "text_chunker_tool")
        self.assertEqual(config["metadata"]["class"], "TextChunkerTool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.text_chunker_tool",
        )
        self.assertIn("strategy", config["input_keys"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["strategy"]["enum"],
            ["char", "word", "sentence"],
        )
        self.assertEqual(config["args_model_schema"]["required"], ["strategy"])

    def test_identical_calls_are_deterministic(self) -> None:
        first = self.tool.execute(
            strategy="sentence", text="A. B! C? D. E.", chunk_size=8, overlap=1
        )
        second = self.tool.execute(
            strategy="sentence", text="A. B! C? D. E.", chunk_size=8, overlap=1
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
