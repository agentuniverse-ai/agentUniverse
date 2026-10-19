#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_chunker_tool.py

"""Text chunking tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency splitter agents can
call to prepare long texts for embedding, retrieval or map-reduce style
processing: cut a document into chunks with a controllable size and a
configurable overlap so context is not lost at the seams.

The tool is a thin, strictly-validated façade over the standard library
``re`` module and plain string slicing, and supports three strategies:

* ``char`` — fixed-size sliding window over characters. Each chunk is
  exactly ``chunk_size`` characters of the original text (the last one
  may be shorter); consecutive windows advance by
  ``chunk_size - overlap`` characters, so ``overlap`` characters are
  shared between neighbouring chunks.
* ``word`` — whitespace-delimited words (any run of non-whitespace
  characters). Each chunk holds exactly ``chunk_size`` consecutive
  words (the last one may hold fewer) and its ``text`` is the original
  span from the first word's first character to the last word's last
  character, so original inner spacing and line breaks survive.
  Consecutive chunks share ``overlap`` words.
* ``sentence`` — sentence-aware packing. Sentences end at a run of
  ``.`` ``!`` ``?`` or ``…`` terminators optionally followed by closing
  quotes / brackets; unterminated trailing text forms a final
  sentence. Consecutive sentences are packed greedily into chunks whose
  original-text span stays within ``chunk_size`` characters, and
  neighbouring chunks share ``overlap`` sentences. A single sentence
  longer than ``chunk_size`` becomes its own chunk flagged
  ``oversized``. As a pure regex tokenizer it has no abbreviation
  model: ``3.14`` or ``Dr.`` split at the dot.

Every result is a structured dictionary with the call context, the
chunk count and the list of chunks; each chunk carries its ``index``,
``text``, and the ``start`` / ``end`` character offsets of its span in
the original text (plus ``word_count`` in word mode and
``sentence_count`` / ``oversized`` in sentence mode).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown strategy,
``chunk_size`` below 1 or above the input cap, negative ``overlap``,
``overlap`` not smaller than ``chunk_size`` in the char / word modes,
text over 1,000,000 characters, or an input that would produce more
than ``max_chunks`` chunks) raise a ``ValueError``, mirroring the other
common tools. Chunking itself cannot fail on content — there are no
content-level error payloads, the output is a pure deterministic
function of the input.
"""

import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A sentence is a run of non-terminator characters followed by a run of
# terminators (optionally closed by quotes / brackets), or — for text
# that never terminates — everything up to the end.
_SENTENCE_RE = re.compile(r"[^.!?…]+[.!?…]+['\")\]]*|[^.!?…]+")
# A word is any run of non-whitespace characters.
_WORD_RE = re.compile(r"\S+")


class TextChunkerTool(Tool):
    """Text chunking tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
        max_chunks (int): Upper bound on the number of chunks a single
            call may produce; inputs needing more are rejected (raise
            the ``chunk_size`` instead of flooding the context).
    """

    # NOTE: the two caps are ClassVars so the validating classmethods
    # can read them through ``cls``; pydantic keeps instance fields off
    # the class namespace.

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_chunker_tool"
    description: str = (
        "Text chunker tool — pure Python stdlib, no network required. "
        "Split text into overlapping chunks for embedding, retrieval or "
        "map-reduce processing: fixed-size character windows "
        "(strategy='char'), whitespace-word windows that preserve the "
        "original spans (strategy='word'), or sentence-aware packing "
        "under a character budget with sentence overlap "
        "(strategy='sentence'). Every chunk reports its character "
        "offsets in the original text."
    )

    STRATEGIES: ClassVar[tuple] = ("char", "word", "sentence")

    # Class-level caps: input size and output chunk count limits.
    max_text_chars: ClassVar[int] = 1_000_000
    max_chunks: ClassVar[int] = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        strategy: Any = None,
        text: Any = None,
        chunk_size: Any = None,
        overlap: Any = None,
    ) -> Dict[str, Any]:
        """Split ``text`` into chunks.

        Args:
            strategy (str): One of ``char`` / ``word`` / ``sentence`` —
                required.
            text (str): The text to chunk; a non-empty string of at
                most 1,000,000 characters.
            chunk_size (int): Chunk target size — characters for the
                ``char`` and ``sentence`` strategies, words for the
                ``word`` strategy. Defaults to ``200``; must be at
                least 1.
            overlap (int): Overlap between consecutive chunks —
                characters (``char``), words (``word``) or sentences
                (``sentence``). Defaults to ``0``; must be ``0`` or
                more and strictly smaller than ``chunk_size`` in the
                char / word modes.

        Returns:
            Dict[str, Any]: The chunking result — call context
                (``strategy`` / ``chunk_size`` / ``overlap``),
                ``chunk_count``, ``total_chars`` (plus
                ``total_words`` / ``total_sentences`` in the word /
                sentence modes) and the ``chunks`` list. Each chunk is
                ``{"index", "text", "start", "end"}`` plus
                ``word_count`` (word mode) or ``sentence_count`` and
                ``oversized`` (sentence mode); ``start`` / ``end`` are
                character offsets into the original text.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if strategy not in self.STRATEGIES:
            self._invalid(
                "strategy must be one of: "
                f"{', '.join(self.STRATEGIES)} (got {strategy!r})"
            )
        clean_text = self._validate_text(text)
        clean_size = self._validate_chunk_size(chunk_size)
        clean_overlap = self._validate_overlap(overlap, clean_size, strategy)
        if strategy == "char":
            return self._run_char(clean_text, clean_size, clean_overlap)
        if strategy == "word":
            return self._run_word(clean_text, clean_size, clean_overlap)
        return self._run_sentence(clean_text, clean_size, clean_overlap)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_chunker_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > cls.max_text_chars:
            cls._invalid(
                f"text exceeds the {cls.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_chunk_size(cls, chunk_size: Any) -> int:
        """Validate the ``chunk_size`` target."""
        if chunk_size is None:
            return 200
        if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
            cls._invalid(
                f"chunk_size must be a positive integer (got {chunk_size!r})"
            )
        if chunk_size < 1 or chunk_size > cls.max_text_chars:
            cls._invalid(
                "chunk_size must be between 1 and "
                f"{cls.max_text_chars:,} (got {chunk_size!r})"
            )
        return chunk_size

    @classmethod
    def _validate_overlap(
        cls, overlap: Any, chunk_size: int, strategy: str
    ) -> int:
        """Validate the ``overlap`` between consecutive chunks."""
        if overlap is None:
            return 0
        if isinstance(overlap, bool) or not isinstance(overlap, int):
            cls._invalid(
                f"overlap must be a non-negative integer (got {overlap!r})"
            )
        if overlap < 0:
            cls._invalid(
                f"overlap must be a non-negative integer (got {overlap!r})"
            )
        if strategy in ("char", "word") and overlap >= chunk_size:
            cls._invalid(
                f"overlap must be smaller than chunk_size "
                f"({overlap} >= {chunk_size})"
            )
        return overlap

    @classmethod
    def _check_chunk_budget(cls, chunks: List[Dict[str, Any]]) -> None:
        """Reject inputs that would produce more than ``max_chunks``."""
        if len(chunks) > cls.max_chunks:
            cls._invalid(
                f"input produces {len(chunks):,} chunks, more than the "
                f"{cls.max_chunks:,}-chunk limit — increase chunk_size"
            )

    # ------------------------------------------------------------------ #
    # char strategy
    # ------------------------------------------------------------------ #

    def _run_char(
        self, text: str, chunk_size: int, overlap: int
    ) -> Dict[str, Any]:
        """Slide a fixed-size character window over the text."""
        chunks: List[Dict[str, Any]] = []
        total = len(text)
        step = chunk_size - overlap
        start = 0
        index = 0
        while start < total:
            end = min(start + chunk_size, total)
            chunks.append(
                {
                    "index": index,
                    "text": text[start:end],
                    "start": start,
                    "end": end,
                }
            )
            index += 1
            if end == total:
                break
            start += step
        self._check_chunk_budget(chunks)
        return {
            "strategy": "char",
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunk_count": len(chunks),
            "total_chars": total,
            "chunks": chunks,
        }

    # ------------------------------------------------------------------ #
    # word strategy
    # ------------------------------------------------------------------ #

    def _run_word(
        self, text: str, chunk_size: int, overlap: int
    ) -> Dict[str, Any]:
        """Group consecutive whitespace-delimited words into chunks."""
        words = [(m.start(), m.end()) for m in _WORD_RE.finditer(text)]
        chunks: List[Dict[str, Any]] = []
        step = chunk_size - overlap
        start = 0
        index = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunks.append(
                {
                    "index": index,
                    "text": text[words[start][0]:words[end - 1][1]],
                    "start": words[start][0],
                    "end": words[end - 1][1],
                    "word_count": end - start,
                }
            )
            index += 1
            if end == len(words):
                break
            start += step
        self._check_chunk_budget(chunks)
        return {
            "strategy": "word",
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunk_count": len(chunks),
            "total_chars": len(text),
            "total_words": len(words),
            "chunks": chunks,
        }

    # ------------------------------------------------------------------ #
    # sentence strategy
    # ------------------------------------------------------------------ #

    @staticmethod
    def _split_sentences(text: str) -> List[Tuple[int, int]]:
        """Return ``(start, end)`` spans of the sentences in ``text``.

        A sentence ends at a run of ``.`` / ``!`` / ``?`` / ``…``
        terminators optionally followed by closing quotes or brackets;
        unterminated trailing text forms a final sentence. Leading
        whitespace (the separator left over after the previous
        sentence) is skipped, and whitespace-only matches are dropped.
        """
        spans: List[Tuple[int, int]] = []
        for match in _SENTENCE_RE.finditer(text):
            start, end = match.start(), match.end()
            while start < end and text[start].isspace():
                start += 1
            if start < end:
                spans.append((start, end))
        return spans

    def _run_sentence(
        self, text: str, chunk_size: int, overlap: int
    ) -> Dict[str, Any]:
        """Pack consecutive sentences under a character budget."""
        sentences = self._split_sentences(text)
        total_sentences = len(sentences)
        chunks: List[Dict[str, Any]] = []
        index = 0
        start = 0
        while start < total_sentences:
            end = start
            while end + 1 < total_sentences and (
                sentences[end + 1][1] - sentences[start][0] <= chunk_size
            ):
                end += 1
            span_start, span_end = sentences[start][0], sentences[end][1]
            chunks.append(
                {
                    "index": index,
                    "text": text[span_start:span_end],
                    "start": span_start,
                    "end": span_end,
                    "sentence_count": end - start + 1,
                    "oversized": span_end - span_start > chunk_size,
                }
            )
            index += 1
            if end == total_sentences - 1:
                break
            start = max(start + 1, end + 1 - overlap)
        self._check_chunk_budget(chunks)
        return {
            "strategy": "sentence",
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunk_count": len(chunks),
            "total_chars": len(text),
            "total_sentences": total_sentences,
            "chunks": chunks,
        }
