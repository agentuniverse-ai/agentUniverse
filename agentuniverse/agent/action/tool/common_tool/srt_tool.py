#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: srt_tool.py

"""SubRip (SRT) subtitle utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency subtitle handler for
media preparation agents: inspecting raw subtitle text, re-timing it
after an edit, renumbering cues, and reporting quality statistics.
Nothing in ``common_tool/`` covered SubRip material before, and the
whole implementation is plain ``re`` arithmetic on strings.

Four modes are supported:

* ``parse`` — SRT text to structured cues ``[{index, start, end,
  text}]`` where ``start`` / ``end`` are integer milliseconds.
  Timestamp parsing is tolerant of the real world: the specification's
  ``,`` and the common ``.`` millisecond separator are both accepted,
  1-2 digit hours and 1-3 digit fractions are right-padded
  (``00:00:01,5`` means 1500 ms), a UTF-8 BOM is ignored, CRLF and CR
  line endings are both handled, whitespace-only lines separate cues,
  and trailing positional metadata (for example ``X1:`` / ``Y1:``
  coordinates) after the end timestamp is dropped. Cue numbers that do
  not match their 1-based position (gaps, duplicates, out of order,
  not starting at 1) produce ``warnings`` in the result — not errors —
  because the cues themselves are still usable.
* ``shift`` — move every cue by a constant millisecond offset
  (negative allowed) and re-serialize as canonical SRT. Shifted
  timestamps are clamped into the representable range
  ``[0, 99:59:59.999]`` (documented: a large negative shift pins cues
  to ``00:00:00,000``) and the result reports which cue positions
  were clamped.
* ``renumber`` — re-index the cues from 1 while preserving the
  order-as-found, re-serialized as canonical SRT.
* ``stats`` — cue count, total / minimum / maximum / mean cue
  duration in milliseconds, overlapping cue pairs (a cue whose end is
  later than the next cue's start, with the overlap amount), and
  too-long-to-read warnings using a documented heuristic: a cue is
  flagged when it lasts longer than 7 seconds or when its reading
  speed exceeds 42 characters per second (characters counted without
  line breaks; zero-duration cues are always flagged).

Canonical SRT output uses the comma millisecond separator,
``-->`` surrounded by single spaces, LF line endings, exactly one
blank line between cues and a single trailing newline.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, a ``text`` that is not a string,
is empty or whitespace-only, exceeds the 1,000,000-character limit,
or parses to more than 10,000 cues, and — for ``shift`` — a
``milliseconds`` value that is not an integer or whose magnitude
exceeds 359,999,999) raise a ``ValueError``, mirroring the other
common tools. Errors that depend on the *content being processed* —
a cue that does not start with a number line, a missing or malformed
timing line, out-of-range timestamp components (minutes or seconds
over 59, three-digit hours, anything beyond 99:59:59.999), and a cue
that ends before it starts — are returned as a structured ``error``
payload carrying the offending cue's 1-based position and claimed
number so an agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A cue number is a plain run of ASCII digits.
_CUE_NUMBER_RE = re.compile(r"[0-9]+")
# "HH:MM:SS,mmm --> HH:MM:SS,mmm" with ',' or '.' before the fraction,
# 1-2 digit hours, 1-3 fraction digits, and (tolerated, then dropped)
# trailing positional metadata such as "X1:100 Y1:50".
_TIMING_RE = re.compile(
    r"(?P<sh>[0-9]{1,2}):(?P<sm>[0-9]{2}):(?P<ss>[0-9]{2})"
    r"[,.](?P<sms>[0-9]{1,3})"
    r"\s*-->\s*"
    r"(?P<eh>[0-9]{1,2}):(?P<em>[0-9]{2}):(?P<es>[0-9]{2})"
    r"[,.](?P<ems>[0-9]{1,3})"
    r"(?:\s.*)?"
)


class _CueParseError(Exception):
    """Internal: one malformed cue, converted to a structured payload.

    Attributes:
        error_type (str): Stable machine-readable error code.
        message (str): Human-readable explanation with an excerpt.
        cue_position (int): 1-based position of the cue in the file.
        cue_index (int | None): The cue's claimed number, when the
            number line itself was readable.
    """

    def __init__(
        self,
        error_type: str,
        message: str,
        cue_position: int,
        cue_index: Any = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.cue_position = cue_position
        self.cue_index = cue_index


class SrtTool(Tool):
    """SubRip (SRT) subtitle utility tool built purely on the stdlib.

    Attributes:
        max_text_chars (ClassVar[int]): Upper bound on the ``text``
            input length; longer inputs are rejected before any work.
        max_cues (ClassVar[int]): Upper bound on the number of cues a
            single input may parse to.
        max_time_ms (ClassVar[int]): Largest representable SRT
            timestamp, 99:59:59.999 in milliseconds.
        max_shift_ms (ClassVar[int]): Largest magnitude of the shift
            offset (the full representable range).
        long_cue_ms (ClassVar[int]): Duration above which ``stats``
            flags a cue as too long to read.
        max_chars_per_second (ClassVar[int]): Reading speed above
            which ``stats`` flags a cue as too fast to read.
        max_warnings (ClassVar[int]): Number of index-sequence
            warnings kept in a ``parse`` result before truncation.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "srt_tool"
    description: str = (
        "SRT subtitle tool — pure Python stdlib, no network required. "
        "Parse SubRip text into structured cues with tolerant "
        "timestamp handling (mode='parse'), shift all cues by a "
        "millisecond offset, negative allowed, clamped to the "
        "representable range and re-serialized as canonical SRT "
        "(mode='shift'), renumber cues from 1 preserving "
        "order-as-found (mode='renumber'), and report cue count, "
        "total/min/max/mean durations, overlapping pairs and "
        "reading-speed warnings (mode='stats')."
    )

    MODES: ClassVar[tuple] = ("parse", "shift", "renumber", "stats")
    MAX_TEXT_CHARS: ClassVar[int] = 1_000_000
    MAX_CUES: ClassVar[int] = 10_000
    # 99:59:59.999 — the largest representable SRT timestamp.
    MAX_TIME_MS: ClassVar[int] = 359_999_999
    MAX_SHIFT_MS: ClassVar[int] = 359_999_999
    LONG_CUE_MS: ClassVar[int] = 7_000
    MAX_CHARS_PER_SECOND: ClassVar[int] = 42
    MAX_WARNINGS: ClassVar[int] = 20

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        milliseconds: Any = None,
    ) -> dict[str, Any]:
        """Run one subtitle operation.

        Args:
            mode (str): One of ``parse`` / ``shift`` / ``renumber`` /
                ``stats``.
            text (str): The raw SRT subtitle text. Required by every
                mode; a UTF-8 BOM, CRLF and CR line endings are
                tolerated.
            milliseconds (int): Shift mode only — the constant offset
                applied to every cue timestamp, in milliseconds;
                negative values are allowed. Defaults are not
                permitted: shift requires an explicit integer.

        Returns:
            Dict[str, Any]: ``parse`` returns ``cues`` plus index
                ``warnings``; ``shift`` / ``renumber`` return the
                canonical SRT text under ``result``; ``stats`` returns
                the inspection report. Content-level failures return a
                structured ``error`` payload with the offending cue's
                position and claimed number.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens), including over-length text and
                over-cap cue counts.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_ms: int | None = None
        if mode == "shift":
            clean_ms = self._validate_milliseconds(milliseconds)

        try:
            cues, warnings, warnings_truncated = self._parse_cues(clean_text)
        except _CueParseError as exc:
            return self._error_result({"mode": mode}, exc)

        if mode == "parse":
            return {
                "mode": "parse",
                "cue_count": len(cues),
                "cues": cues,
                "warnings": warnings,
                "warnings_truncated": warnings_truncated,
            }
        if mode == "shift":
            return self._run_shift(cues, clean_ms)
        if mode == "renumber":
            renumbered = [
                {**cue, "index": position}
                for position, cue in enumerate(cues, start=1)
            ]
            return {
                "mode": "renumber",
                "cue_count": len(renumbered),
                "result": self._serialize(renumbered),
            }
        return self._run_stats(cues)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"srt_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (raw SRT subtitle content)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text.strip():
            cls._invalid(
                "text must contain at least one non-whitespace character "
                "(an empty document has no cues to work on)"
            )
        if len(text) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {cls.MAX_TEXT_CHARS:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_milliseconds(cls, milliseconds: Any) -> int:
        """Validate the shift offset (any sign, bounded magnitude)."""
        if isinstance(milliseconds, bool) or not isinstance(milliseconds, int):
            cls._invalid(
                "milliseconds must be an integer (negative allowed) for "
                f"shift mode (got {milliseconds!r})"
            )
        if abs(milliseconds) > cls.MAX_SHIFT_MS:
            cls._invalid(
                "milliseconds magnitude must not exceed "
                f"{cls.MAX_SHIFT_MS:,} (the full representable SRT range "
                f"0 to 99:59:59.999) — got {milliseconds:,}"
            )
        return milliseconds

    # ------------------------------------------------------------------ #
    # Parsing (tolerant reader, strict boundaries)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_cues(
        cls, text: str
    ) -> tuple[list[dict[str, Any]], list[str], bool]:
        """Parse raw SRT text into cues plus index-sequence warnings.

        Returns:
            Tuple of (cues, warnings, warnings_truncated) where each
            cue is ``{"index": int, "start": int, "end": int,
            "text": str}`` with millisecond integers.

        Raises:
            _CueParseError: On the first malformed cue (converted to a
                structured payload by the caller).
        """
        if text.startswith("\ufeff"):
            text = text[1:]
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

        blocks: list[list[str]] = []
        current: list[str] = []
        for line in lines:
            if line.strip():
                current.append(line)
            elif current:
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)

        if len(blocks) > cls.MAX_CUES:
            cls._invalid(
                f"input parses to more than {cls.MAX_CUES:,} cues "
                f"(got {len(blocks):,}); split the subtitle before "
                "processing it"
            )

        cues: list[dict[str, Any]] = []
        warnings: list[str] = []
        for position, block in enumerate(blocks, start=1):
            number_line = block[0].strip()
            if _CUE_NUMBER_RE.fullmatch(number_line) is None:
                raise _CueParseError(
                    "missing_cue_number",
                    f"cue at position {position} does not start with a cue "
                    f"number line (got {block[0][:64]!r})",
                    position,
                    None,
                )
            cue_index = int(number_line)
            if len(block) < 2:
                raise _CueParseError(
                    "missing_timing_line",
                    f"cue {cue_index} (position {position}) ends after its "
                    "number line — the 'HH:MM:SS,mmm --> HH:MM:SS,mmm' "
                    "timing line is missing",
                    position,
                    cue_index,
                )
            timing_line = block[1].strip()
            if "-->" not in timing_line:
                raise _CueParseError(
                    "missing_timing_line",
                    f"cue {cue_index} (position {position}) has no '-->' "
                    f"timing line (got {timing_line[:64]!r})",
                    position,
                    cue_index,
                )
            match = _TIMING_RE.fullmatch(timing_line)
            if match is None:
                raise _CueParseError(
                    "invalid_timestamp",
                    f"cue {cue_index} (position {position}) has a malformed "
                    "timing line — expected "
                    "'HH:MM:SS,mmm --> HH:MM:SS,mmm' with a ',' or '.' "
                    "before the milliseconds (got "
                    f"{timing_line[:64]!r})",
                    position,
                    cue_index,
                )
            groups = match.groupdict()
            start_ms = cls._parts_to_ms(
                groups["sh"], groups["sm"], groups["ss"], groups["sms"]
            )
            end_ms = cls._parts_to_ms(
                groups["eh"], groups["em"], groups["es"], groups["ems"]
            )
            if start_ms is None or end_ms is None:
                raise _CueParseError(
                    "invalid_timestamp",
                    f"cue {cue_index} (position {position}) has out-of-range "
                    "timestamp components — minutes and seconds must be "
                    "00-59 and the maximum representable time is "
                    f"99:59:59.999 (got {timing_line[:64]!r})",
                    position,
                    cue_index,
                )
            if start_ms > end_ms:
                raise _CueParseError(
                    "end_before_start",
                    f"cue {cue_index} (position {position}) ends before it "
                    f"starts (got {timing_line[:64]!r})",
                    position,
                    cue_index,
                )

            text_lines = [line.rstrip() for line in block[2:]]
            while text_lines and not text_lines[0]:
                text_lines.pop(0)
            while text_lines and not text_lines[-1]:
                text_lines.pop()
            cues.append(
                {
                    "index": cue_index,
                    "start": start_ms,
                    "end": end_ms,
                    "text": "\n".join(text_lines),
                }
            )
            if cue_index != position:
                warnings.append(
                    f"cue position {position} is numbered {cue_index}; "
                    f"expected {position}"
                )

        warnings_truncated = len(warnings) > cls.MAX_WARNINGS
        if warnings_truncated:
            warnings = warnings[: cls.MAX_WARNINGS]
        return cues, warnings, warnings_truncated

    @staticmethod
    def _parts_to_ms(
        hours: str, minutes: str, seconds: str, fraction: str
    ) -> int | None:
        """Convert matched timestamp parts to milliseconds.

        Fraction digits are right-padded to three (```,5`` is 500 ms).
        Returns ``None`` when minutes or seconds are out of range;
        hours are bounded to two digits by the pattern already.
        """
        hour, minute, second = int(hours), int(minutes), int(seconds)
        if minute > 59 or second > 59:
            return None
        millis = int(fraction.ljust(3, "0"))
        return ((hour * 60 + minute) * 60 + second) * 1000 + millis

    # ------------------------------------------------------------------ #
    # Canonical SRT serialization
    # ------------------------------------------------------------------ #

    @classmethod
    def _serialize(cls, cues: list[dict[str, Any]]) -> str:
        """Serialize cues as canonical SRT (comma millis, LF endings)."""
        blocks = [
            f"{cue['index']}\n"
            f"{cls._ms_to_timestamp(cue['start'])} --> "
            f"{cls._ms_to_timestamp(cue['end'])}\n"
            f"{cue['text']}"
            for cue in cues
        ]
        if not blocks:
            return ""
        return "\n\n".join(blocks) + "\n"

    @staticmethod
    def _ms_to_timestamp(milliseconds: int) -> str:
        """Render milliseconds as the canonical ``HH:MM:SS,mmm`` form."""
        return (
            f"{milliseconds // 3_600_000:02d}:"
            f"{milliseconds % 3_600_000 // 60_000:02d}:"
            f"{milliseconds % 60_000 // 1_000:02d},"
            f"{milliseconds % 1_000:03d}"
        )

    # ------------------------------------------------------------------ #
    # shift / stats modes
    # ------------------------------------------------------------------ #

    def _run_shift(
        self, cues: list[dict[str, Any]], milliseconds: int
    ) -> dict[str, Any]:
        """Shift every cue by the offset, clamped to [0, 99:59:59.999]."""
        clamped_positions: list[int] = []
        shifted: list[dict[str, Any]] = []
        for position, cue in enumerate(cues, start=1):
            raw_start = cue["start"] + milliseconds
            raw_end = cue["end"] + milliseconds
            new_start = min(max(raw_start, 0), self.MAX_TIME_MS)
            new_end = min(max(raw_end, 0), self.MAX_TIME_MS)
            if new_start != raw_start or new_end != raw_end:
                clamped_positions.append(position)
            shifted.append({**cue, "start": new_start, "end": new_end})
        return {
            "mode": "shift",
            "milliseconds": milliseconds,
            "cue_count": len(shifted),
            "clamped_cue_count": len(clamped_positions),
            "clamped_positions": clamped_positions,
            "result": self._serialize(shifted),
        }

    def _run_stats(self, cues: list[dict[str, Any]]) -> dict[str, Any]:
        """Report duration, overlap and reading-speed statistics."""
        durations = [cue["end"] - cue["start"] for cue in cues]
        total = sum(durations)

        overlapping_pairs: list[dict[str, Any]] = []
        for i in range(len(cues) - 1):
            first, second = cues[i], cues[i + 1]
            if first["end"] > second["start"]:
                overlapping_pairs.append(
                    {
                        "first_position": i + 1,
                        "second_position": i + 2,
                        "first_index": first["index"],
                        "second_index": second["index"],
                        "overlap_ms": first["end"] - second["start"],
                    }
                )

        reading_warnings: list[dict[str, Any]] = []
        for position, cue in enumerate(cues, start=1):
            duration = cue["end"] - cue["start"]
            chars = len(cue["text"].replace("\n", ""))
            reasons: list[str] = []
            chars_per_second = None
            if duration > self.LONG_CUE_MS:
                reasons.append("duration_over_7s")
            if duration <= 0:
                reasons.append("zero_duration")
            else:
                raw_speed = chars * 1000 / duration
                chars_per_second = round(raw_speed, 2)
                if raw_speed > self.MAX_CHARS_PER_SECOND:
                    reasons.append("reading_speed_over_42cps")
            if reasons:
                reading_warnings.append(
                    {
                        "position": position,
                        "index": cue["index"],
                        "duration_ms": duration,
                        "chars": chars,
                        "chars_per_second": chars_per_second,
                        "reasons": reasons,
                    }
                )

        return {
            "mode": "stats",
            "cue_count": len(cues),
            "total_duration_ms": total,
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "mean_duration_ms": round(total / len(cues), 3),
            "overlap_count": len(overlapping_pairs),
            "overlapping_pairs": overlapping_pairs,
            "reading_warning_count": len(reading_warnings),
            "reading_warnings": reading_warnings,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], exc: _CueParseError
    ) -> dict[str, Any]:
        """Build a structured error payload for a malformed cue."""
        return {
            **context,
            "error": {
                "type": exc.error_type,
                "message": str(exc.message)[:500],
                "cue_position": exc.cue_position,
                "cue_index": exc.cue_index,
            },
        }
