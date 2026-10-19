#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: line_ops_tool.py

"""Line-level text operations tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency line utility agents
can call when cleaning model outputs, generated lists and logs:
sorting, deduplicating, trimming, numbering and truncating lines.

The tool is a thin, strictly-validated façade over built-in string
operations and supports seven modes:

* ``sort`` — sort lines. The default ordering is plain lexicographic
  (Unicode code point) and stable: lines with equal keys keep their
  input order. ``natural=True`` switches to a human numeric-aware key
  that chunks digit runs and compares them numerically, so ``file2``
  sorts before ``file10``; leading zeros make digit runs equal (``v07``
  and ``v7`` compare equal, keeping input order). ``case_insensitive``
  lowercases lines (or the non-digit chunks in natural mode) before
  comparison, ``reverse=True`` flips the ordering while preserving
  stability for equal keys, and ``unique=True`` removes duplicate lines
  (exact string equality, first occurrence kept) before sorting.
* ``unique`` — remove duplicate lines, preserving the order of first
  occurrences, and report how many duplicates were removed.
* ``trim`` — strip trailing whitespace from every line; with
  ``drop_empty=True`` lines that are empty after stripping (or were
  already empty) are dropped and the dropped count is reported.
* ``number`` — prefix every line with its running number:
  ``1. line`` (``number_format="dot"``) or ``1) line``
  (``number_format="paren"``), starting at ``start`` (default 1) and
  optionally zero-padded to ``pad`` digits (``pad=3`` gives
  ``001. line``).
* ``reverse`` — reverse the line order.
* ``head`` / ``tail`` — keep the first / last ``n`` lines (default 10)
  and report the total line count, the returned line count and whether
  the input was truncated.

Line endings: ``\\r\\n`` and stray ``\\r`` are normalized to ``\\n`` before
processing, and a single trailing newline does not introduce an extra
empty line. Output is joined with ``\\n`` by default; ``newline="crlf"``
joins with ``\\r\\n`` instead.

Everything is deterministic — no randomness, no time dependence, no
network. Input validation is strict and happens before any work:
malformed parameters (unknown mode, wrong ``text`` type, empty text,
boolean flags passed as non-booleans, unknown ``number_format`` /
``newline`` values, out-of-bounds ``n`` / ``start`` / ``pad``,
mode-specific options used with the wrong mode, text
over the character or line caps) raise a ``ValueError`` mirroring the
other common tools. Line operations themselves never fail on content,
so no error payloads are needed.
"""

# Strict validation raises ValueError with a descriptive message.
# ruff: noqa: TRY003

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Capturing split: even chunks are text, odd chunks are digit runs.
_DIGIT_RUNS = re.compile(r"(\d+)")


class LineOpsTool(Tool):
    """Line-level text operations tool built purely on the stdlib.

    Attributes:
        max_lines (int): Upper bound on the number of input lines;
            larger inputs are rejected before any work.
        max_text_chars (int): Upper bound on the ``text`` input length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "line_ops_tool"
    description: str = (
        "Line operations tool — pure Python stdlib, no network required. "
        "Sort lines lexicographically or naturally (digit runs compared "
        "numerically so file2 < file10) with case-insensitive, reverse "
        "and unique-then-sort options (mode='sort'), deduplicate lines "
        "preserving first-occurrence order (mode='unique'), strip "
        "trailing whitespace per line with an optional drop-empty-lines "
        "flag (mode='trim'), prefix running numbers as '1. ' / '1) ' "
        "with zero-padding and custom start (mode='number'), reverse "
        "line order (mode='reverse'), and keep the first/last N lines "
        "with count and truncation reporting (mode='head'/'tail'). "
        "CRLF input is normalized; output uses LF or CRLF."
    )

    MODES: ClassVar[tuple] = (
        "sort",
        "unique",
        "trim",
        "number",
        "reverse",
        "head",
        "tail",
    )
    FORMATS: ClassVar[tuple] = ("dot", "paren")
    NEWLINES: ClassVar[tuple] = ("lf", "crlf")

    max_lines: int = 100_000
    max_text_chars: int = 1_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        natural: Any = None,
        case_insensitive: Any = None,
        reverse: Any = None,
        unique: Any = None,
        drop_empty: Any = None,
        number_format: Any = None,
        start: Any = None,
        pad: Any = None,
        n: Any = None,
        newline: Any = None,
    ) -> dict[str, Any]:
        """Run one line operation.

        Args:
            mode (str): One of ``sort`` / ``unique`` / ``trim`` /
                ``number`` / ``reverse`` / ``head`` / ``tail``.
            text (str): The input text. Required for every mode;
                ``\\r\\n`` and stray ``\\r`` are normalized to ``\\n`` and a
                single trailing newline does not add an empty line.
            natural (bool): Sort mode only — compare digit runs
                numerically (``file2`` sorts before ``file10``);
                default lexicographic.
            case_insensitive (bool): Sort mode only — lowercase lines
                (or non-digit chunks in natural mode) before comparing.
            reverse (bool): Sort mode only — flip the ordering; equal
                keys still keep their input order.
            unique (bool): Sort mode only — remove duplicate lines
                before sorting.
            drop_empty (bool): Trim mode only — drop lines that are
                empty after trailing-whitespace stripping.
            number_format (str): Number mode only — ``dot``
                (``1. line``) or ``paren`` (``1) line``).
            start (int): Number mode only — first number (default 1).
            pad (int): Number mode only — zero-pad the number to this
                many digits (0-9; 0 means no padding).
            n (int): Head/tail modes only — number of lines to keep
                (default 10; 1-100000).
            newline (str): Output line ending — ``lf`` (default) or
                ``crlf``.

        Returns:
            Dict[str, Any]: The operation result — always the joined
            ``result`` string, the ``mode``, the chosen ``newline``,
            ``input_lines`` / ``output_lines`` counts, and the
            mode-specific flags and counts (sort: option flags and
            ``duplicates_removed``; unique: ``duplicates_removed``;
            trim: ``drop_empty`` and ``lines_dropped``; number:
            ``number_format`` / ``start`` / ``pad``; head/tail:
            effective ``n`` and a ``truncated`` flag).

        Raises:
            ValueError: If any parameter is malformed (before any
                processing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        self._validate_option_modes(
            mode,
            natural=natural,
            case_insensitive=case_insensitive,
            reverse=reverse,
            unique=unique,
            drop_empty=drop_empty,
            number_format=number_format,
            start=start,
            pad=pad,
            n=n,
        )
        clean_newline = self._validate_newline(newline)
        lines = self._split_lines(text)
        context: dict[str, Any] = {
            "mode": mode,
            "newline": clean_newline,
            "input_lines": len(lines),
        }
        if mode == "sort":
            return self._finish(
                context,
                self._run_sort(
                    lines, natural, case_insensitive, reverse, unique
                ),
                clean_newline,
            )
        if mode == "unique":
            return self._finish(
                context, self._run_unique(lines), clean_newline
            )
        if mode == "trim":
            return self._finish(
                context, self._run_trim(lines, drop_empty), clean_newline
            )
        if mode == "number":
            return self._finish(
                context, self._run_number(lines, number_format, start, pad),
                clean_newline,
            )
        if mode == "reverse":
            return self._finish(
                context, {"result_lines": lines[::-1]}, clean_newline
            )
        if mode == "head":
            return self._finish(
                context, self._run_head_tail(lines, n, head=True),
                clean_newline,
            )
        return self._finish(
            context, self._run_head_tail(lines, n, head=False),
            clean_newline,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any processing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"line_ops_tool: {message}")

    # Options that only some modes understand, mapped to the modes
    # that accept them; every other mode must omit them (None).
    _OPTION_MODES: ClassVar[dict] = {
        "natural": ("sort",),
        "case_insensitive": ("sort",),
        "reverse": ("sort",),
        "unique": ("sort",),
        "drop_empty": ("trim",),
        "number_format": ("number",),
        "start": ("number",),
        "pad": ("number",),
        "n": ("head", "tail"),
    }

    @classmethod
    def _validate_option_modes(cls, mode: str, **options: Any) -> None:
        """Reject mode-specific options passed with the wrong mode.

        Silently ignoring ``natural`` in the ``trim`` mode (or a
        mistyped ``natural=1`` there) would hide caller mistakes, so
        an option that only some modes understand must be omitted
        (``None``) everywhere else — mirroring the other common tools.
        """
        for name, value in options.items():
            if value is None:
                continue
            allowed = cls._OPTION_MODES[name]
            if mode not in allowed:
                modes = "/".join(repr(m) for m in allowed)
                noun = "modes" if len(allowed) > 1 else "mode"
                cls._invalid(
                    f"{name} is only valid in the {modes} {noun} "
                    f"(got {name}={value!r} with mode={mode!r})"
                )

    def _split_lines(self, text: Any) -> list[str]:
        """Validate ``text`` and split it into normalized lines.

        ``\\r\\n`` and stray ``\\r`` are normalized to ``\\n``; one trailing
        newline is treated as the terminator of the last line, not as an
        extra empty line (``"a\\nb\\n"`` and ``"a\\nb"`` both have two
        lines, like ``str.splitlines``).
        """
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            self._invalid("text must be a non-empty string (got '')")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        if normalized.endswith("\n"):
            normalized = normalized[:-1]
        lines = normalized.split("\n")
        if len(lines) > self.max_lines:
            self._invalid(
                f"text exceeds the {self.max_lines:,}-line limit "
                f"(got {len(lines):,} lines)"
            )
        return lines

    @classmethod
    def _validate_flag(cls, value: Any, name: str) -> bool:
        """Validate a boolean option (``None`` means ``False``)."""
        if value is None:
            return False
        if not isinstance(value, bool):
            cls._invalid(f"{name} must be a boolean or omitted (got {value!r})")
        return value

    @classmethod
    def _validate_count(
        cls, value: Any, name: str, minimum: int, maximum: int, default: int
    ) -> int:
        """Validate an integer option (``None`` means ``default``).

        Accepts real integers and pure ASCII digit strings (so callers
        may pass ``n="5"``); booleans, floats and anything else are
        rejected.
        """
        if value is None:
            return default
        if isinstance(value, bool):
            cls._invalid(f"{name} must be an integer, not a boolean (got {value!r})")
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and value.isascii() and value.isdigit():
            number = int(value)
        else:
            cls._invalid(f"{name} must be an integer (got {value!r})")
        if not minimum <= number <= maximum:
            cls._invalid(
                f"{name} must be between {minimum:,} and {maximum:,} "
                f"(got {number:,})"
            )
        return number

    @classmethod
    def _validate_newline(cls, newline: Any) -> str:
        """Validate the output line-ending selector."""
        if newline is None:
            return "lf"
        if newline not in cls.NEWLINES:
            cls._invalid(
                "newline must be one of: "
                f"{', '.join(cls.NEWLINES)} (got {newline!r})"
            )
        return newline

    # ------------------------------------------------------------------ #
    # sort mode
    # ------------------------------------------------------------------ #

    def _run_sort(
        self,
        lines: list[str],
        natural: Any,
        case_insensitive: Any,
        reverse: Any,
        unique: Any,
    ) -> dict[str, Any]:
        """Sort lines with the requested key, direction and dedup."""
        clean_natural = self._validate_flag(natural, "natural")
        clean_ci = self._validate_flag(case_insensitive, "case_insensitive")
        clean_reverse = self._validate_flag(reverse, "reverse")
        clean_unique = self._validate_flag(unique, "unique")
        working = self._dedupe(lines) if clean_unique else lines
        duplicates_removed = len(lines) - len(working)
        if clean_natural:
            key = self._natural_key_factory(clean_ci)
        elif clean_ci:
            key = str.lower
        else:
            key = None
        # sorted() is stable, including with reverse=True: lines with
        # equal keys always keep their input order.
        ordered = sorted(working, key=key, reverse=clean_reverse)
        return {
            "natural": clean_natural,
            "case_insensitive": clean_ci,
            "reverse": clean_reverse,
            "unique": clean_unique,
            "duplicates_removed": duplicates_removed,
            "result_lines": ordered,
        }

    @staticmethod
    def _natural_key_factory(case_insensitive: bool):
        """Build a natural-sort key: digit runs compare numerically.

        Each line is split into alternating text and digit-run chunks
        (``re.split(r'(\\d+)')``). Digit chunks are compared as integers
        (so ``file2`` sorts before ``file10``, and ``v07`` equals
        ``v7``); text chunks compare as strings (lowercased when
        ``case_insensitive``). Every chunk maps to the same
        ``(int, int, str)`` triple shape, so chunks of different kinds
        never mix types inside one tuple comparison.
        """

        def natural_key(line: str):
            key = []
            for index, chunk in enumerate(_DIGIT_RUNS.split(line)):
                if index % 2:
                    key.append((1, int(chunk), ""))
                else:
                    text = chunk.lower() if case_insensitive else chunk
                    key.append((0, 0, text))
            return key

        return natural_key

    # ------------------------------------------------------------------ #
    # unique / trim / number / reverse / head / tail modes
    # ------------------------------------------------------------------ #

    @staticmethod
    def _dedupe(lines: list[str]) -> list[str]:
        """Drop duplicates, keeping first occurrences and their order."""
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        return unique_lines

    def _run_unique(self, lines: list[str]) -> dict[str, Any]:
        """Deduplicate lines preserving first-occurrence order."""
        unique_lines = self._dedupe(lines)
        return {
            "duplicates_removed": len(lines) - len(unique_lines),
            "result_lines": unique_lines,
        }

    def _run_trim(self, lines: list[str], drop_empty: Any) -> dict[str, Any]:
        """Strip trailing whitespace per line, optionally drop empties."""
        clean_drop = self._validate_flag(drop_empty, "drop_empty")
        stripped = [line.rstrip() for line in lines]
        if clean_drop:
            kept = [line for line in stripped if line]
            return {
                "drop_empty": True,
                "lines_dropped": len(stripped) - len(kept),
                "result_lines": kept,
            }
        return {
            "drop_empty": False,
            "lines_dropped": 0,
            "result_lines": stripped,
        }

    def _run_number(
        self, lines: list[str], number_format: Any, start: Any, pad: Any
    ) -> dict[str, Any]:
        """Prefix every line with its running number."""
        if number_format is None:
            number_format = "dot"
        if number_format not in self.FORMATS:
            self._invalid(
                f"number_format must be one of: {', '.join(self.FORMATS)} "
                f"(got {number_format!r})"
            )
        clean_start = self._validate_count(
            start, "start", minimum=0, maximum=999_999, default=1
        )
        clean_pad = self._validate_count(
            pad, "pad", minimum=0, maximum=9, default=0
        )
        suffix = "." if number_format == "dot" else ")"
        numbered = [
            f"{str(number).zfill(clean_pad)}{suffix} {line}"
            for number, line in enumerate(lines, start=clean_start)
        ]
        return {
            "number_format": number_format,
            "start": clean_start,
            "pad": clean_pad,
            "result_lines": numbered,
        }

    def _run_head_tail(
        self, lines: list[str], n: Any, head: bool
    ) -> dict[str, Any]:
        """Keep the first or last ``n`` lines (default 10)."""
        clean_n = self._validate_count(
            n, "n", minimum=1, maximum=self.max_lines, default=10
        )
        selected = lines[:clean_n] if head else lines[-clean_n:]
        return {
            "n": clean_n,
            "truncated": len(lines) > clean_n,
            "result_lines": selected,
        }

    # ------------------------------------------------------------------ #
    # Result assembly
    # ------------------------------------------------------------------ #

    @staticmethod
    def _finish(
        context: dict[str, Any], outcome: dict[str, Any], newline: str
    ) -> dict[str, Any]:
        """Join the produced lines and merge the result payload."""
        eol = "\r\n" if newline == "crlf" else "\n"
        result_lines = outcome.pop("result_lines")
        return {
            **context,
            **outcome,
            "output_lines": len(result_lines),
            "result": eol.join(result_lines),
        }
