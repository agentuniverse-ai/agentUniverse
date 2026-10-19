#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_diff_tool.py

"""Text comparison tool built purely on the stdlib ``difflib`` module.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text diff agents can
call to compare two texts: reviewing edits, checking whether two
drafts are the same, or summarizing how far apart two documents are.

The tool is a thin, strictly-validated façade over ``difflib`` and
supports three modes:

* ``unified`` — a unified diff in the exact format ``difflib.unified_diff``
  produces (``--- text1`` / ``+++ text2`` headers, ``@@ -a,b +c,d @@``
  hunk headers, ``'`` `` ``'``/``'-'``/``'+'`` line prefixes) plus the
  hunk count and added / removed / equal line counts. The context
  window around each change is controlled by ``context_lines``
  (default 3, capped at 50). The diff is computed on normalized lines
  (see the options below) but rendered from the original lines, so a
  line that only differs in case or surrounding whitespace does not
  appear in the output at all.
* ``summary`` — side-by-side change statistics: the
  ``difflib.SequenceMatcher`` similarity ratio of the two line
  sequences, added / removed / equal line counts, per-text line totals,
  and ``identical`` / ``equal_after_normalization`` flags.
* ``words`` — word-level change regions: both texts are tokenized into
  whitespace-separated words, compared with ``SequenceMatcher`` opcodes
  and every non-equal opcode (insert / delete / replace region) is
  reported with word-index ranges and the changed words themselves.

Normalization options shared by all modes:

* ``ignore_case`` — compare lines (and words) case-insensitively.
* ``ignore_whitespace`` — ignore leading and trailing whitespace of
  each line. Word tokens contain no whitespace, so this option has no
  additional effect in ``words`` mode.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode, non-boolean flags,
``context_lines`` outside ``0..50``, texts over 100,000 characters)
raise a ``ValueError``, mirroring the other common tools. Empty texts
are valid input — diffing against an empty text is well defined (every
line becomes an insertion or a deletion). Lines are produced with
``str.splitlines()``, so a trailing newline at the very end of a text
is not distinguished from its absence. Errors that depend on the
*content being processed* — currently a unified diff that would exceed
the 200,000-character output cap — are returned as a structured
``error`` payload so an agent can react (for example by re-running in
``summary`` mode) without catching exceptions.
"""

import difflib
import re
from typing import Any, ClassVar, Dict, List

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A word is any run of non-whitespace characters.
_WORD_TOKEN = re.compile(r"\S+")


class TextDiffTool(Tool):
    """Text diff tool built purely on the stdlib ``difflib`` module.

    Attributes:
        max_text_chars (int): Upper bound on each text input
            (``text1`` / ``text2``); longer inputs are rejected before
            any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_diff_tool"
    description: str = (
        "Text diff tool — pure Python stdlib difflib, no network "
        "required. Compares two texts: mode='unified' renders a "
        "unified diff (difflib.unified_diff format) with hunk and "
        "added/removed/equal line counts and a configurable "
        "context_lines window; mode='summary' returns the "
        "SequenceMatcher similarity ratio plus added/removed/equal "
        "line counts and identical flags; mode='words' returns "
        "word-level change opcodes with the changed words. Optional "
        "ignore_case and ignore_whitespace normalization."
    )

    MODES: ClassVar[tuple] = ("unified", "summary", "words")
    # Context window for unified hunks: difflib's default is 3 lines.
    DEFAULT_CONTEXT_LINES: ClassVar[int] = 3
    MAX_CONTEXT_LINES: ClassVar[int] = 50
    # Unified diffs larger than this return a structured error payload
    # instead of flooding the agent context (summary mode still works).
    MAX_DIFF_CHARS: ClassVar[int] = 200_000
    # Words-mode payload caps: at most 100 change opcodes are returned
    # and at most 20 words per side per opcode (exact counts are always
    # included; only the listings are capped).
    MAX_OPCODES: ClassVar[int] = 100
    MAX_OPCODE_WORDS: ClassVar[int] = 20

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text1: Any = None,
        text2: Any = None,
        ignore_case: Any = None,
        ignore_whitespace: Any = None,
        context_lines: Any = None,
    ) -> Dict[str, Any]:
        """Compare ``text1`` and ``text2`` in one of three modes.

        Args:
            mode (str): One of ``unified`` / ``summary`` / ``words``.
            text1 (str): The first (older) text. Empty strings are
                valid; every line of a non-empty counterpart then shows
                up as an insertion.
            text2 (str): The second (newer) text. Empty strings are
                valid; every line of a non-empty counterpart then shows
                up as a deletion.
            ignore_case (bool): Compare case-insensitively. Defaults to
                ``False``. Applies to all modes.
            ignore_whitespace (bool): Ignore leading and trailing
                whitespace of each line. Defaults to ``False``. Has no
                additional effect in ``words`` mode (word tokens contain
                no whitespace).
            context_lines (int): Number of unchanged context lines
                around each hunk — unified mode only, defaults to 3,
                accepted range 0..50. Ignored by the other modes.

        Returns:
            Dict[str, Any]: The comparison result (mode-specific fields
                plus the call context) or a structured ``error`` payload
                for content-level failures (unified diff larger than
                ``MAX_DIFF_CHARS``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_a = self._validate_text(text1, "text1")
        clean_b = self._validate_text(text2, "text2")
        clean_ignore_case = self._validate_bool(ignore_case, "ignore_case")
        clean_ignore_whitespace = self._validate_bool(
            ignore_whitespace, "ignore_whitespace"
        )

        a_lines = clean_a.splitlines()
        b_lines = clean_b.splitlines()
        normalized_a = self._normalize_lines(
            a_lines, clean_ignore_case, clean_ignore_whitespace
        )
        normalized_b = self._normalize_lines(
            b_lines, clean_ignore_case, clean_ignore_whitespace
        )

        if mode == "unified":
            return self._run_unified(
                clean_a,
                clean_b,
                a_lines,
                b_lines,
                normalized_a,
                normalized_b,
                context_lines,
                clean_ignore_case,
                clean_ignore_whitespace,
            )
        if mode == "summary":
            return self._run_summary(
                clean_a,
                clean_b,
                a_lines,
                b_lines,
                normalized_a,
                normalized_b,
                clean_ignore_case,
                clean_ignore_whitespace,
            )
        return self._run_words(clean_a, clean_b, clean_ignore_case)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_diff_tool: {message}")

    def _validate_text(self, text: Any, name: str) -> str:
        """Validate one text input (empty strings are allowed)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"{name} must be a string (got {text!r})")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"{name} exceeds the {self.max_text_chars:,}-character "
                f"limit (got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_bool(cls, value: Any, name: str) -> bool:
        """Validate a boolean flag; ``None`` means ``False``."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean or None (got {value!r})")

    def _validate_context_lines(self, context_lines: Any) -> int:
        """Validate the unified-mode ``context_lines`` window."""
        if context_lines is None:
            return self.DEFAULT_CONTEXT_LINES
        if (
            isinstance(context_lines, int)
            and not isinstance(context_lines, bool)
        ):
            value = context_lines
        elif isinstance(context_lines, str) and context_lines.strip().isdigit():
            value = int(context_lines)
        else:
            self._invalid(
                "context_lines must be an integer between 0 and "
                f"{self.MAX_CONTEXT_LINES} (got {context_lines!r})"
            )
            raise  # pragma: no cover - _invalid always raises
        if not 0 <= value <= self.MAX_CONTEXT_LINES:
            self._invalid(
                "context_lines must be an integer between 0 and "
                f"{self.MAX_CONTEXT_LINES} (got {context_lines!r})"
            )
        return value

    # ------------------------------------------------------------------ #
    # Normalization helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_lines(
        lines: List[str], ignore_case: bool, ignore_whitespace: bool
    ) -> List[str]:
        """Apply the ``ignore_case`` / ``ignore_whitespace`` options.

        The returned list has the same length as ``lines`` so opcode
        index ranges stay valid for both the normalized sequences (used
        for matching) and the original lines (used for rendering).
        """
        if not ignore_case and not ignore_whitespace:
            return list(lines)
        normalized = []
        for line in lines:
            if ignore_case:
                line = line.lower()
            if ignore_whitespace:
                line = line.strip()
            normalized.append(line)
        return normalized

    @staticmethod
    def _format_range(start: int, stop: int) -> str:
        """Format a line range the way ``difflib.unified_diff`` does."""
        # Lines start numbering with one; empty ranges begin at the
        # line just before the range (the "ed" format).
        beginning = start + 1
        length = stop - start
        if length == 1:
            return str(beginning)
        if not length:
            beginning -= 1
        return f"{beginning},{length}"

    @staticmethod
    def _count_line_changes(opcodes: Any) -> Dict[str, int]:
        """Tally added / removed / equal lines from diff opcodes."""
        added = removed = equal = 0
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                equal += i2 - i1
                continue
            if tag in ("replace", "delete"):
                removed += i2 - i1
            if tag in ("replace", "insert"):
                added += j2 - j1
        return {
            "added_lines": added,
            "removed_lines": removed,
            "equal_lines": equal,
        }

    # ------------------------------------------------------------------ #
    # unified mode
    # ------------------------------------------------------------------ #

    def _run_unified(
        self,
        clean_a: str,
        clean_b: str,
        a_lines: List[str],
        b_lines: List[str],
        normalized_a: List[str],
        normalized_b: List[str],
        context_lines: Any,
        ignore_case: bool,
        ignore_whitespace: bool,
    ) -> Dict[str, Any]:
        """Render a unified diff (difflib format) plus change counts.

        Matching runs on the normalized line sequences while rendering
        uses the original lines, so options can hide whitespace- or
        case-only noise without altering the shown content. With no
        options active the output is byte-for-byte identical to
        ``difflib.unified_diff(a, b, fromfile='text1',
        tofile='text2', n=context_lines)`` joined together — including
        the empty string for identical inputs, which difflib also
        produces.
        """
        clean_context = self._validate_context_lines(context_lines)
        context: Dict[str, Any] = {
            "mode": "unified",
            "ignore_case": ignore_case,
            "ignore_whitespace": ignore_whitespace,
            "context_lines": clean_context,
        }
        matcher = difflib.SequenceMatcher(None, normalized_a, normalized_b)
        # Counts cover the whole comparison (like summary mode), not
        # just the lines rendered as context inside the hunks.
        counts = self._count_line_changes(matcher.get_opcodes())
        parts: List[str] = []
        hunks = 0
        for group in matcher.get_grouped_opcodes(clean_context):
            if hunks == 0:
                parts.append("--- text1\n")
                parts.append("+++ text2\n")
            hunks += 1
            first, last = group[0], group[-1]
            parts.append(
                "@@ -{} +{} @@\n".format(
                    self._format_range(first[1], last[2]),
                    self._format_range(first[3], last[4]),
                )
            )
            for tag, i1, i2, j1, j2 in group:
                if tag == "equal":
                    parts.extend(f" {line}\n" for line in a_lines[i1:i2])
                    continue
                if tag in ("replace", "delete"):
                    parts.extend(f"-{line}\n" for line in a_lines[i1:i2])
                if tag in ("replace", "insert"):
                    parts.extend(f"+{line}\n" for line in b_lines[j1:j2])
        diff_text = "".join(parts)
        if len(diff_text) > self.MAX_DIFF_CHARS:
            return self._error_result(
                {**context, **counts},
                error_type="diff_too_large",
                message=(
                    f"the unified diff exceeds the {self.MAX_DIFF_CHARS:,}"
                    f"-character output limit (got {len(diff_text):,} "
                    "characters); re-run with mode='summary' or "
                    "mode='words' for a bounded change overview"
                ),
            )
        return {
            **context,
            **counts,
            "hunks": hunks,
            "identical": clean_a == clean_b,
            "result": diff_text,
        }

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def _run_summary(
        self,
        clean_a: str,
        clean_b: str,
        a_lines: List[str],
        b_lines: List[str],
        normalized_a: List[str],
        normalized_b: List[str],
        ignore_case: bool,
        ignore_whitespace: bool,
    ) -> Dict[str, Any]:
        """Return similarity ratio and per-side line statistics."""
        matcher = difflib.SequenceMatcher(None, normalized_a, normalized_b)
        counts = self._count_line_changes(matcher.get_opcodes())
        return {
            "mode": "summary",
            "ignore_case": ignore_case,
            "ignore_whitespace": ignore_whitespace,
            "identical": clean_a == clean_b,
            "equal_after_normalization": normalized_a == normalized_b,
            "similarity_ratio": round(matcher.ratio(), 6),
            **counts,
            "total_lines_text1": len(a_lines),
            "total_lines_text2": len(b_lines),
        }

    # ------------------------------------------------------------------ #
    # words mode
    # ------------------------------------------------------------------ #

    def _run_words(
        self, clean_a: str, clean_b: str, ignore_case: bool
    ) -> Dict[str, Any]:
        """Return word-level change opcodes with the changed words.

        Both texts are tokenized into whitespace-separated words,
        compared with ``SequenceMatcher`` on the (optionally
        lower-cased) tokens, and every non-equal opcode is listed with
        word-index ranges and the changed words. Listings are capped
        (``MAX_OPCODES`` opcodes, ``MAX_OPCODE_WORDS`` words per side)
        while all counts stay exact.
        """
        tokens_a = _WORD_TOKEN.findall(clean_a)
        tokens_b = _WORD_TOKEN.findall(clean_b)
        normalized_a = (
            [token.lower() for token in tokens_a] if ignore_case else tokens_a
        )
        normalized_b = (
            [token.lower() for token in tokens_b] if ignore_case else tokens_b
        )
        matcher = difflib.SequenceMatcher(None, normalized_a, normalized_b)
        added = removed = equal = 0
        changed_regions = 0
        opcodes: List[Dict[str, Any]] = []
        opcodes_truncated = False
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                equal += i2 - i1
                continue
            if tag in ("replace", "delete"):
                removed += i2 - i1
            if tag in ("replace", "insert"):
                added += j2 - j1
            changed_regions += 1
            if len(opcodes) >= self.MAX_OPCODES:
                opcodes_truncated = True
                continue
            words_a = tokens_a[i1:i2]
            words_b = tokens_b[j1:j2]
            entry: Dict[str, Any] = {
                "tag": tag,
                "text1_start": i1,
                "text1_end": i2,
                "text2_start": j1,
                "text2_end": j2,
                "text1_words": words_a[: self.MAX_OPCODE_WORDS],
                "text2_words": words_b[: self.MAX_OPCODE_WORDS],
            }
            if len(words_a) > self.MAX_OPCODE_WORDS:
                entry["text1_words_truncated"] = True
            if len(words_b) > self.MAX_OPCODE_WORDS:
                entry["text2_words_truncated"] = True
            opcodes.append(entry)
        return {
            "mode": "words",
            "ignore_case": ignore_case,
            "identical": clean_a == clean_b,
            "equal_after_normalization": normalized_a == normalized_b,
            "similarity_ratio": round(matcher.ratio(), 6),
            "word_count_text1": len(tokens_a),
            "word_count_text2": len(tokens_b),
            "added_words": added,
            "removed_words": removed,
            "equal_words": equal,
            "changed_regions": changed_regions,
            "opcodes": opcodes,
            "opcodes_truncated": opcodes_truncated,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
