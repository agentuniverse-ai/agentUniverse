#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: text_sampler_tool.py

"""Representative text sampling / excerpt extraction tool built on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency sampler that pulls
*representative excerpts* out of long text — the pieces a human (or an
LLM with a context budget) would quote when skimming.

Distinct from its sibling tools: ``TextTruncateTool`` keeps only the
head of the text under a budget, and ``TextChunkerTool`` returns *all*
chunks of the text. This tool deliberately DROPS material and reports
what it kept: four sampling modes, all deterministic pure functions
of the input:

* ``head_tail`` — the first N and the last N characters joined by a
  ``…[K chars omitted]…`` separator that names exactly how many
  characters were skipped in between (``K = len - 2N``). The omitted
  count is also reported structurally as ``omitted_chars``.
* ``evenly_spaced`` — k windows of exactly L characters taken at
  evenly spaced offsets computed by the documented formula
  ``offset_i = floor(i * (len - L) / (k - 1))`` for ``i = 0 .. k-1``
  (``k >= 2``): the first window always starts at character 0 and the
  last always ends at the final character. The degenerate ``k == 1``
  takes the single window centered on the text:
  ``offset = floor((len - L) / 2)``. When the text is too short for k
  distinct windows, offsets that round to the same position are
  merged and a ``note`` explains how many were dropped.
* ``strategic`` — the first N characters, the last N characters and a
  middle window of N characters centered on the midpoint
  (``start = floor((len - N) / 2)``, so the window's center is
  ``len / 2``) — the head/middle/tail shape LLM context windows use
  when fitting a long document into a limited prompt.
* ``outline_sample`` — sentence-level skim: the first sentence, every
  Nth sentence after it, and the last sentence, capped at k sentences
  total (k = 1 yields just the first sentence). Sentences are found
  with conservative segmentation — terminators ``.`` ``!`` ``?`` and
  the CJK ``。`` ``！`` ``？``, closing quotes/brackets absorbed into
  the sentence, an ASCII ``.`` only ends a sentence at whitespace or
  end of text (so ``3.14`` never splits), plus a guard for common
  English abbreviations (``Mr.``, ``Dr.``, ``e.g.``, ``i.e.``,
  ``Inc.`` … including interior dots) and single uppercase initials
  (``J. Smith``). The guard errs toward fewer, longer sentences.

Every mode returns ``samples`` (the excerpt strings), ``spans``
(exact ``[start, end)`` offsets into the original text — Python code
points, so one CJK ideograph or emoji counts as exactly one
character), ``total_length`` and ``sampled_ratio`` (the fraction of
the text covered by the union of the spans, rounded to four
decimals). A text shorter than what the mode requests (head + tail,
L, N, or a second sentence) is returned whole with a ``note``
instead of being padded or split.

Input validation is strict and happens before any computation:
malformed parameters — wrong types, boolean traps like
``sample_size=True``, unknown mode, empty or oversized text,
out-of-range ``sample_size`` / ``sample_length`` (1 .. 100,000),
``sample_count`` (1 .. 100) or ``every_n`` (1 .. 10,000), a missing
required option, or an option used with a mode that does not take it
— raise a ``ValueError``, mirroring the other common tools.
"""

from typing import Any, ClassVar, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Sentence terminators (ASCII + CJK ideographic and fullwidth forms).
_TERMINATORS = ".!?" + "。！？"
_CJK_TERMINATORS = "。！？"
# Closing quotes / brackets absorbed into the sentence that ends
# right before them, so 'He said "stop."' keeps its final quote.
_CLOSERS = "\"'”’)】》」』"
# Common English abbreviations whose trailing '.' must not end a
# sentence (compared case-insensitively, interior dots included).
_ABBREVIATIONS = frozenset(
    {
        "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc",
        "e.g", "i.e", "inc", "ltd", "co", "corp", "fig", "figs", "eq",
        "eqs", "no", "nos", "vol", "vols", "pp", "ca", "cf", "al",
        "approx", "dept", "univ", "assn", "bros", "dist", "est", "min",
        "max", "misc", "ave", "blvd", "rd", "apt", "ph.d", "u.s",
        "u.k", "u.n", "u.s.a",
    }
)


class TextSamplerTool(Tool):
    """Representative text sampling tool built purely on the stdlib."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_sampler_tool"
    description: str = (
        "Text sampler tool — pure Python stdlib, no network required. "
        "Extracts representative excerpts from long text instead of "
        "returning all of it: head + tail with an omission-count "
        "separator (mode='head_tail'), k evenly spaced windows of L "
        "characters at documented offsets (mode='evenly_spaced'), "
        "first/middle/last windows like an LLM context window "
        "(mode='strategic'), or a sentence-level outline of first + "
        "every Nth + last sentence (mode='outline_sample'). All modes "
        "report the samples, their exact spans, the total length and "
        "the sampled ratio."
    )

    MODES: ClassVar[tuple] = (
        "head_tail",
        "evenly_spaced",
        "strategic",
        "outline_sample",
    )
    # Which modes accept which keyword option (for cross-mode checks).
    _PARAM_MODES: ClassVar[dict] = {
        "sample_size": ("head_tail", "strategic"),
        "sample_count": ("evenly_spaced", "outline_sample"),
        "sample_length": ("evenly_spaced",),
        "every_n": ("outline_sample",),
    }

    # Upper bound on the text input length and on the sample_size /
    # sample_length options; longer values are rejected before any work.
    MAX_TEXT_CHARS: ClassVar[int] = 100_000
    MAX_SAMPLES: ClassVar[int] = 100
    MAX_EVERY_N: ClassVar[int] = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        sample_size: Any = None,
        sample_count: Any = None,
        sample_length: Any = None,
        every_n: Any = None,
    ) -> dict:
        """Run one sampling operation.

        Args:
            mode (str): One of ``head_tail`` / ``evenly_spaced`` /
                ``strategic`` / ``outline_sample``.
            text (str): The text to sample. A non-empty string of at
                most 100,000 characters.
            sample_size (int): ``head_tail`` and ``strategic`` modes —
                the size N of each excerpt (characters, 1 .. 100,000).
                ``head_tail`` uses N for the head and N for the tail.
            sample_count (int): ``evenly_spaced`` mode — the number k of
                windows (1 .. 100); ``outline_sample`` mode — the cap k
                on the number of sentences returned (1 .. 100).
            sample_length (int): ``evenly_spaced`` mode — the length L
                of every window (1 .. 100,000).
            every_n (int): ``outline_sample`` mode — the sentence stride
                N: after the first sentence, every Nth one is kept
                (1 .. 10,000).

        Returns:
            Dict[str, Any]: Always ``mode`` + mode context, ``samples``
            (list of excerpt strings), ``spans`` (list of exact
            ``[start, end)`` offsets into the original text),
            ``total_length`` and ``sampled_ratio``; plus mode-specific
            fields (``omitted_chars`` / composed ``result`` for
            ``head_tail``, ``offsets`` for ``evenly_spaced``,
            ``sections`` for ``strategic``, ``sentence_count`` /
            ``selected_indices`` for ``outline_sample``) and a ``note``
            whenever the text was too short for the request and is
            returned whole.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "head_tail":
            size = self._validate_int(
                "sample_size", sample_size, 1, self.MAX_TEXT_CHARS
            )
            self._forbid_for_mode(
                mode,
                sample_count=sample_count,
                sample_length=sample_length,
                every_n=every_n,
            )
            return self._run_head_tail(clean_text, size)
        if mode == "evenly_spaced":
            count = self._validate_int(
                "sample_count", sample_count, 1, self.MAX_SAMPLES
            )
            length = self._validate_int(
                "sample_length", sample_length, 1, self.MAX_TEXT_CHARS
            )
            self._forbid_for_mode(
                mode, sample_size=sample_size, every_n=every_n
            )
            return self._run_evenly_spaced(clean_text, count, length)
        if mode == "strategic":
            size = self._validate_int(
                "sample_size", sample_size, 1, self.MAX_TEXT_CHARS
            )
            self._forbid_for_mode(
                mode,
                sample_count=sample_count,
                sample_length=sample_length,
                every_n=every_n,
            )
            return self._run_strategic(clean_text, size)
        count = self._validate_int(
            "sample_count", sample_count, 1, self.MAX_SAMPLES
        )
        stride = self._validate_int("every_n", every_n, 1, self.MAX_EVERY_N)
        self._forbid_for_mode(
            mode, sample_size=sample_size, sample_length=sample_length
        )
        return self._run_outline(clean_text, count, stride)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_sampler_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {cls.MAX_TEXT_CHARS:,}-character "
                f"limit (got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_int(
        cls, name: str, value: Any, low: int, high: int
    ) -> int:
        """Validate an integer option (int or digit string, no bools)."""
        if isinstance(value, bool):
            cls._invalid(
                f"{name} must be an integer between {low} and {high} "
                f"(got {value!r})"
            )
        if isinstance(value, int):
            number = value
        elif (
            isinstance(value, str)
            and value.strip() != ""
            and value.strip().lstrip("+-").isdigit()
        ):
            number = int(value.strip())
        else:
            cls._invalid(
                f"{name} must be an integer between {low} and {high} "
                f"(got {value!r})"
            )
        if not low <= number <= high:
            cls._invalid(
                f"{name} must be between {low} and {high} (got {number})"
            )
        return number

    @classmethod
    def _forbid_for_mode(cls, mode: str, **values: Any) -> None:
        """Reject options that the chosen mode does not accept."""
        for name, value in values.items():
            if value is None:
                continue
            allowed = " or ".join(cls._PARAM_MODES[name])
            cls._invalid(
                f"{name} is only used by the {allowed} mode(s), "
                f"not {mode!r}"
            )

    # ------------------------------------------------------------------ #
    # head_tail mode
    # ------------------------------------------------------------------ #

    def _run_head_tail(self, text: str, size: int) -> dict:
        """First N + last N characters with an omission-count separator."""
        total = len(text)
        context = {"mode": "head_tail", "sample_size": size}
        if total < 2 * size:
            return self._passthrough(
                text,
                note=(
                    f"text length {total} is below the requested head + "
                    f"tail size of {2 * size} characters "
                    f"(2 x {size}); the whole text is returned"
                ),
                **context,
            )
        head = text[:size]
        tail = text[total - size:]
        omitted = total - 2 * size
        if omitted:
            plural = "s" if omitted != 1 else ""
            composed = f"{head}…[{omitted} char{plural} omitted]…{tail}"
        else:
            # Exact fit: head and tail are contiguous, no separator.
            composed = text
        spans = [[0, size], [total - size, total]]
        return {
            **context,
            "result": composed,
            "samples": [head, tail],
            "spans": spans,
            "omitted_chars": omitted,
            "truncated": omitted > 0,
            "total_length": total,
            "sampled_ratio": self._ratio(spans, total),
        }

    # ------------------------------------------------------------------ #
    # evenly_spaced mode
    # ------------------------------------------------------------------ #

    def _run_evenly_spaced(
        self, text: str, count: int, length: int
    ) -> dict:
        """k windows of L characters at evenly spaced offsets.

        Documented formula: ``offset_i = floor(i * (len - L) / (k - 1))``
        for ``i = 0 .. k-1`` and ``k >= 2`` — the first window starts
        at character 0 and the last ends at the final character. For
        ``k == 1`` the single window is centered:
        ``offset = floor((len - L) / 2)``.
        """
        total = len(text)
        context = {
            "mode": "evenly_spaced",
            "sample_count": count,
            "sample_length": length,
        }
        if length >= total:
            return self._passthrough(
                text,
                note=(
                    f"sample_length {length} is >= the text length "
                    f"{total}; the whole text is returned as one sample"
                ),
                **context,
            )
        if count == 1:
            offsets = [(total - length) // 2]
        else:
            spread = total - length
            offsets = [i * spread // (count - 1) for i in range(count)]
        # Text too short for k distinct windows: merge offsets that
        # round to the same position, keeping document order.
        unique_offsets: List[int] = []
        for offset in offsets:
            if offset not in unique_offsets:
                unique_offsets.append(offset)
        merged = count - len(unique_offsets)
        spans = [[offset, offset + length] for offset in unique_offsets]
        result = {
            **context,
            "offsets": unique_offsets,
            "samples": [text[s:e] for s, e in spans],
            "spans": spans,
            "samples_returned": len(spans),
            "total_length": total,
            "sampled_ratio": self._ratio(spans, total),
        }
        if merged:
            result["note"] = (
                f"{merged} of the {count} requested samples rounded to "
                f"the same offset and were merged — the text is too "
                f"short for {count} distinct windows of {length} "
                f"characters"
            )
        return result

    # ------------------------------------------------------------------ #
    # strategic mode
    # ------------------------------------------------------------------ #

    def _run_strategic(self, text: str, size: int) -> dict:
        """First N + middle N + last N, LLM-context-window style.

        The middle window starts at ``floor((len - N) / 2)`` so its
        center is the text midpoint ``len / 2``. Windows that coincide
        exactly with an already-kept window are dropped.
        """
        total = len(text)
        context = {"mode": "strategic", "sample_size": size}
        if total <= size:
            return self._passthrough(
                text,
                note=(
                    f"sample_size {size} is >= the text length {total}; "
                    f"the whole text is returned as one sample"
                ),
                **context,
            )
        middle_start = (total - size) // 2
        labelled = (
            ("head", 0, size),
            ("middle", middle_start, middle_start + size),
            ("tail", total - size, total),
        )
        sections: List[str] = []
        spans: List[List[int]] = []
        for label, start, end in labelled:
            if [start, end] in spans:
                continue
            sections.append(label)
            spans.append([start, end])
        return {
            **context,
            "sections": sections,
            "samples": [text[s:e] for s, e in spans],
            "spans": spans,
            "total_length": total,
            "sampled_ratio": self._ratio(spans, total),
        }

    # ------------------------------------------------------------------ #
    # outline_sample mode
    # ------------------------------------------------------------------ #

    def _run_outline(self, text: str, count: int, stride: int) -> dict:
        """Sentence-level skim: first + every Nth + last, capped at k.

        Selection rule (0-based sentence indices): keep index 0, then
        stride, 2*stride, ... while fewer than k - 1 indices are kept
        (one slot stays reserved for the last sentence); the last
        sentence is appended when it is not already selected and room
        remains. ``k == 1`` therefore yields just the first sentence.
        """
        sentences = self._split_sentences(text)
        total_sentences = len(sentences)
        context = {
            "mode": "outline_sample",
            "every_n": stride,
            "max_sentences": count,
            "sentence_count": total_sentences,
        }
        if total_sentences <= 1:
            return self._passthrough(
                text,
                note=(
                    f"only {total_sentences} sentence detected; the whole "
                    f"text is returned as the outline"
                ),
                **context,
            )
        indices = [0]
        index = stride
        while index < total_sentences and len(indices) < count - 1:
            indices.append(index)
            index += stride
        last = total_sentences - 1
        if last not in indices and len(indices) < count:
            indices.append(last)
        indices = sorted(set(indices))
        spans = [[sentences[i][0], sentences[i][1]] for i in indices]
        return {
            **context,
            "selected_indices": indices,
            "samples": [text[s:e] for s, e in spans],
            "spans": spans,
            "total_length": len(text),
            "sampled_ratio": self._ratio(spans, len(text)),
        }

    @classmethod
    def _split_sentences(cls, text: str) -> List[Tuple[int, int]]:
        """Split text into sentences with exact ``[start, end)`` spans.

        Conservative segmentation: a sentence ends at a run of
        terminators (``.!?`` and ``。！？``) followed — after absorbing
        closing quotes/brackets — by whitespace or the end of the text.
        A CJK terminator (``。！？``) ends the sentence regardless of
        what follows, because CJK text carries no inter-sentence
        whitespace. An ASCII ``.`` is additionally guarded against
        common abbreviations and single uppercase initials. Leading
        whitespace before each sentence is skipped and never part of a
        span; a trailing fragment without a terminator becomes the
        last sentence. Whitespace-only text yields one whole-text
        sentence.
        """
        sentences: List[Tuple[int, int]] = []
        total = len(text)
        i = 0
        while i < total and text[i].isspace():
            i += 1
        start = i
        while i < total:
            if text[i] not in _TERMINATORS:
                i += 1
                continue
            j = i
            while j < total and text[j] in _TERMINATORS:
                j += 1
            end = j
            while end < total and text[end] in _CLOSERS:
                end += 1
            after = text[end] if end < total else ""
            has_cjk = any(c in _CJK_TERMINATORS for c in text[i:j])
            ends = has_cjk or after == "" or after.isspace()
            if ends and not has_cjk and "." in text[i:j]:
                if cls._is_abbreviation(text, i):
                    i = end
                    continue
            if ends:
                sentences.append((start, end))
                i = end
                while i < total and text[i].isspace():
                    i += 1
                start = i
            else:
                i = end
        if start < total:
            sentences.append((start, total))
        if not sentences:
            sentences = [(0, total)]
        return sentences

    @staticmethod
    def _is_abbreviation(text: str, dot_index: int) -> bool:
        """True when the ``.`` at ``dot_index`` must not end a sentence.

        Looks back to the previous whitespace: a single uppercase
        letter is an initial (``J. Smith``), and a token matching a
        common abbreviation (case-insensitive, interior dots kept, so
        both dots of ``e.g.`` are guarded) does not end the sentence.
        """
        k = dot_index - 1
        while k >= 0 and not text[k].isspace():
            k -= 1
        token = text[k + 1:dot_index]
        if not token:
            return False
        if len(token) == 1 and token.isupper():
            return True
        return token.lower() in _ABBREVIATIONS

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _passthrough(
        cls, text: str, note: str, **context: Any
    ) -> dict:
        """Whole-text result for a request the text is too short for."""
        total = len(text)
        return {
            "mode": context.pop("mode"),
            **context,
            "samples": [text],
            "spans": [[0, total]],
            "note": note,
            "total_length": total,
            "sampled_ratio": 1.0,
        }

    @staticmethod
    def _union_length(spans: List[List[int]]) -> int:
        """Characters covered by the union of the spans."""
        covered = 0
        last_end = -1
        for start, end in sorted(spans):
            clamped = max(start, last_end)
            if end > clamped:
                covered += end - clamped
                last_end = end
        return covered

    @classmethod
    def _ratio(cls, spans: List[List[int]], total: int) -> float:
        """Union coverage of the spans over the text length."""
        if total <= 0:
            return 1.0
        return round(cls._union_length(spans) / total, 4)
