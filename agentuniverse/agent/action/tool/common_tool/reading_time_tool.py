#!/usr/bin/env python3

# @Time    : 2026/10/20
# @FileName: reading_time_tool.py

"""
Reading Time Tool — reading/speaking/listening time estimation and
inverse word budgets for content-planning agents.

``ReadingLevelScorer`` measures how *difficult* a text is; this tool
answers the orthogonal planning question — how *long* it takes to
consume, and how much text fits a given time slot. Pure Python
standard library, exact ``fractions.Fraction`` arithmetic, no network.

Modes (``mode`` argument):

- ``estimate``: ``text`` -> reading time at three speeds — slow
  150 / average 238 / fast 350 words per minute. The 238 wpm average
  is the silent-prose reading rate from Brysbaert's 2019 meta-analysis
  ("How many words do we read per minute? A meta-analysis of reading
  rate", Journal of Memory and Language 109, 104047). ``reading_wpm``
  (50-1000) replaces the three speeds with one custom speed.
- ``speaking``: either ``text`` -> speaking time at 140/160/180 wpm
  tiers (conversational to brisk delivery), or the deck rule via
  ``deck_count``: one slide (or one bullet talking point, with
  ``deck_unit='bullets'``) is presented in about 30-60 seconds, so a
  deck yields a min-max range plus the midpoint.
- ``custom``: ``text`` plus ``wpm`` (50-1000, default 238) for
  word-based media, or ``seconds_per_char`` for char-based media.
  Subtitle standard: about 17 characters per second, i.e.
  ``seconds_per_char = 1/17 ~= 0.0588`` (the common adult-program
  reading-speed guideline). Char basis counts every character of the
  trimmed text, whitespace included — subtitle lines carry spaces.
- ``plan``: the inverse direction — ``target_minutes`` (> 0) + ``wpm``
  (default 238) -> the word budget that fills the slot, as
  ``min_words``/``max_words`` around the exact budget at +/-10%
  (floor for the minimum, ceil for the maximum).

Word counting is CJK-aware and follows the family tokenizer rule
shared with ``ReadingLevelScorer``: a word is a Latin alphabetic run
(inner hyphens and apostrophes kept, so ``state-of-the-art`` and
``don't`` are one word each), a digit run, or ONE CJK character (Han,
kana, Hangul) — unsegmented scripts approximate one word per
character, so ``你好`` counts as two words and mixed documents are
handled naturally.

Rounding rules (documented, deterministic): raw durations are exact
rationals; ``seconds`` fields are ceiled up to whole seconds;
``humanized`` renders sub-second durations as ``"< 1 s"``, zero as
``"0 s"``, seconds under a minute as ``"42 s"``, minutes as
``"3 min 12 s"`` (trailing ``"0 s"`` dropped) and hour-plus durations
as ``"1 h 5 min 3 s"`` (zero components skipped).

All results are structured dicts with a ``status`` field
(``success`` / ``error``); errors are returned, never raised.
Validation is strict: unknown modes, empty or non-string text, wpm
outside 50-1000, non-positive or non-numeric ``target_minutes``,
out-of-range ``seconds_per_char``, bad deck units/counts and the
mutually exclusive ``wpm``/``seconds_per_char`` pair are all rejected
with informative payloads.

Addresses #252 (other tools).
"""

import math
import re
from fractions import Fraction
from typing import Any

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions into structured tool
# responses instead of raising.
# ruff: noqa: TRY003

_SUPPORTED_MODES = ("estimate", "speaking", "custom", "plan")

# Reading speeds in words per minute. The 238 average is the silent
# prose reading rate from Brysbaert (2019), Journal of Memory and
# Language 109, 104047 — a meta-analysis of 190 reading-rate studies.
_READING_SPEEDS = (("slow", 150), ("average", 238), ("fast", 350))

# Speaking tiers in words per minute: conversational delivery up to a
# brisk presentation pace.
_SPEAKING_TIERS = (("slow", 140), ("average", 160), ("fast", 180))

# Default words per minute for the custom and plan modes.
_DEFAULT_WPM = 238

# Deck pacing rule of thumb: one slide — or one bullet talking point —
# takes 30 to 60 seconds to present.
_DECK_SECONDS_PER_UNIT = (30, 60)

# wpm validation bounds: below 50 or above 1000 is a unit mistake.
_MIN_WPM = 50
_MAX_WPM = 1000

# seconds_per_char validation bounds: a character slower than ten
# seconds is not media pacing.
_MAX_SECONDS_PER_CHAR = 10

# Deck size sanity bound.
_MAX_DECK_COUNT = 10000

# Input text sanity bound (characters).
_MAX_TEXT_CHARS = 2_000_000

# Family tokenizer rule, shared with ReadingLevelScorer: a word is a
# Latin alphabetic run (inner hyphens/apostrophes kept), a digit run,
# or ONE CJK character (Han, kana, Hangul — unsegmented scripts
# approximate one word per character).
_WORD_RE = re.compile(
    r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[0-9]+|[\u4e00-\u9fff\u3040-\u30ff"
    r"\uac00-\ud7af]")
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

_COUNTING_RULE = ("latin/digit tokens plus one word per CJK character "
                  "(Han, kana, Hangul)")

_REFERENCE_NOTE = ("average 238 wpm: Brysbaert (2019) meta-analysis of "
                   "silent reading rate, Journal of Memory and Language "
                   "109")

_SUBTITLE_NOTE = ("subtitle standard ~17 chars/s, i.e. "
                  "seconds_per_char = 1/17 ~= 0.0588")


def _to_fraction(value: int | float) -> Fraction:
    """Exact rational from an int or float via its decimal literal.

    ``Fraction(str(x))`` keeps results deterministic: 0.1 means one
    tenth exactly, not the binary approximation.
    """
    return Fraction(str(value))


def _count_words(text: str) -> tuple[int, int]:
    """Return ``(total words, cjk characters)`` under the family rule."""
    total = len(_WORD_RE.findall(text))
    cjk = len(_CJK_RE.findall(text))
    return total, cjk


def _humanize(raw: Fraction) -> str:
    """Render an exact duration per the documented rounding rules.

    ``0`` -> ``"0 s"``; anything below one second -> ``"< 1 s"``;
    otherwise ceil to whole seconds and format with zero components
    skipped (``"3 min 12 s"``, ``"1 h"``, ``"1 h 5 min 3 s"``).
    """
    if raw <= 0:
        return "0 s"
    if raw < 1:
        return "< 1 s"
    total = math.ceil(raw)
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours} h")
    if minutes:
        parts.append(f"{minutes} min")
    if seconds:
        parts.append(f"{seconds} s")
    return " ".join(parts)


def _ceil_seconds(raw: Fraction) -> int:
    """Ceil an exact duration to whole seconds (0 stays 0)."""
    return 0 if raw <= 0 else math.ceil(raw)


def _number_or_int(frac: Fraction) -> int | float:
    """Serialize an exact rational: int when whole, float otherwise."""
    if frac.denominator == 1:
        return frac.numerator
    return float(frac)


class ReadingTimeTool(Tool):
    """Reading/speaking time estimation and inverse word budgets.

    Attributes:
        nothing configurable beyond the Tool base; every rate and
        bound is a static module constant, so all modes are
        deterministic, offline and dependency-free.
    """

    name: str = "reading_time_tool"
    description: str | None = (
        "Reading, speaking and listening time estimation with inverse "
        "word budgets: estimate reading time at slow/average/fast "
        "speeds (150/238/350 wpm, Brysbaert 2019 average), speaking "
        "time at 140/160/180 wpm tiers plus the 30-60 s per slide or "
        "bullet deck rule, custom wpm or seconds-per-char durations "
        "(subtitle standard 17 chars/s), and plan-mode word budgets "
        "(+/-10%) for a target time slot. CJK-aware word counting, "
        "pure Python, no dependencies, no network."
    )
    input_keys: list[str] | None = Field(default_factory=lambda: ["mode"])

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        mode: str,
        text: str = "",
        reading_wpm: Any = None,
        wpm: Any = None,
        seconds_per_char: Any = None,
        target_minutes: Any = None,
        deck_count: Any = None,
        deck_unit: Any = "slides",
        **_: Any,
    ) -> dict:
        """Run one reading-time ``mode``.

        Returns a structured dict. On success it carries ``mode`` plus
        mode-specific fields; on error it carries ``error_type`` and
        ``error``. Errors are returned, never raised.
        """
        try:
            op = self._normalize_mode(mode)
            if op == "estimate":
                return self._estimate(text, reading_wpm)
            if op == "speaking":
                return self._speaking(text, deck_count, deck_unit)
            if op == "custom":
                return self._custom(text, wpm, seconds_per_char)
            return self._plan(target_minutes, wpm)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), mode)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(
                "operation_error",
                f"Reading time operation failed: {exc}", mode)

    # ------------------------------------------------------------------
    # Argument validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        op = mode.strip().lower()
        if op not in _SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported mode {mode!r}. Supported: "
                + ", ".join(_SUPPORTED_MODES)
            )
        return op

    @staticmethod
    def _error(kind: str, message: str, mode: Any) -> dict:
        result = {
            "status": "error",
            "error_type": kind,
            "error": message,
        }
        if mode is not None:
            result["mode"] = mode
        return result

    def _normalize_text(self, value: Any, label: str) -> str:
        """Validate, bound-check and trim a required text argument."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise TypeError(f"{label} must be a string")
        if len(value) > _MAX_TEXT_CHARS:
            raise ValueError(
                f"{label} exceeds {_MAX_TEXT_CHARS} characters")
        text = value.strip()
        if not text:
            raise ValueError(f"{label} is required and must not be empty")
        return text

    @staticmethod
    def _normalize_wpm(value: Any, label: str) -> int | float:
        """Validate a words-per-minute argument (bounds 50-1000)."""
        if isinstance(value, bool):
            raise TypeError(f"{label} must be a number between "
                            f"{_MIN_WPM} and {_MAX_WPM}, not a boolean")
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"{label} must be a number between {_MIN_WPM} and "
                f"{_MAX_WPM} words per minute")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{label} must be a finite number")
        if not _MIN_WPM <= value <= _MAX_WPM:
            raise ValueError(
                f"{label} must be between {_MIN_WPM} and {_MAX_WPM} "
                f"words per minute (got {value})")
        return value

    @staticmethod
    def _normalize_minutes(value: Any) -> int | float:
        """Validate target_minutes: a finite number greater than zero."""
        if isinstance(value, bool):
            raise TypeError("target_minutes must be a positive number, "
                            "not a boolean")
        if not isinstance(value, (int, float)):
            raise TypeError("target_minutes must be a positive number")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("target_minutes must be a finite number")
        if value <= 0:
            raise ValueError(
                f"target_minutes must be greater than zero (got {value})")
        return value

    @staticmethod
    def _normalize_seconds_per_char(value: Any) -> int | float:
        """Validate seconds_per_char: finite, in (0, 10]."""
        if isinstance(value, bool):
            raise TypeError("seconds_per_char must be a positive number, "
                            "not a boolean")
        if not isinstance(value, (int, float)):
            raise TypeError("seconds_per_char must be a positive number "
                            "of seconds per character")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("seconds_per_char must be a finite number")
        if not 0 < value <= _MAX_SECONDS_PER_CHAR:
            raise ValueError(
                f"seconds_per_char must be greater than zero and at most "
                f"{_MAX_SECONDS_PER_CHAR} seconds per character "
                f"(got {value})")
        return value

    @staticmethod
    def _normalize_deck_count(value: Any) -> int:
        """Validate deck_count: an integer in [1, 10000]."""
        if isinstance(value, bool):
            raise TypeError("deck_count must be an integer between 1 and "
                            f"{_MAX_DECK_COUNT}, not a boolean")
        if not isinstance(value, int):
            raise TypeError("deck_count must be an integer between 1 and "
                            f"{_MAX_DECK_COUNT}")
        if not 1 <= value <= _MAX_DECK_COUNT:
            raise ValueError(
                f"deck_count must be between 1 and {_MAX_DECK_COUNT} "
                f"(got {value})")
        return value

    @staticmethod
    def _normalize_deck_unit(value: Any) -> str:
        """Validate deck_unit: 'slides' (default) or 'bullets'."""
        if value is None:
            value = "slides"
        if not isinstance(value, str):
            raise TypeError("deck_unit must be 'slides' or 'bullets'")
        unit = value.strip().lower()
        if unit not in ("slides", "bullets"):
            raise ValueError(f"Invalid deck_unit {value!r}: expected "
                             "'slides' or 'bullets'")
        return unit

    # ------------------------------------------------------------------
    # mode: estimate
    # ------------------------------------------------------------------
    def _estimate(self, text_value: Any, reading_wpm_value: Any) -> dict:
        text = self._normalize_text(text_value, "text")
        words, cjk = _count_words(text)
        result: dict = {
            "status": "success",
            "mode": "estimate",
            "words": words,
            "latin_words": words - cjk,
            "cjk_chars": cjk,
            "counting_rule": _COUNTING_RULE,
        }
        if reading_wpm_value is not None:
            wpm = self._normalize_wpm(reading_wpm_value, "reading_wpm")
            raw = Fraction(words * 60) / _to_fraction(wpm)
            result["speeds"] = [{
                "speed": "custom",
                "wpm": wpm,
                "seconds": _ceil_seconds(raw),
                "humanized": _humanize(raw),
            }]
            result["reading_wpm"] = wpm
        else:
            result["speeds"] = [
                {
                    "speed": label,
                    "wpm": wpm,
                    "seconds": _ceil_seconds(
                        Fraction(words * 60, wpm)),
                    "humanized": _humanize(Fraction(words * 60, wpm)),
                }
                for label, wpm in _READING_SPEEDS
            ]
            result["reference"] = _REFERENCE_NOTE
        return result

    # ------------------------------------------------------------------
    # mode: speaking
    # ------------------------------------------------------------------
    def _speaking(self, text_value: Any, deck_count_value: Any,
                  deck_unit_value: Any) -> dict:
        has_text = isinstance(text_value, str) and text_value.strip()
        if deck_count_value is not None:
            if has_text:
                raise ValueError(
                    "speaking accepts either text or deck_count, not both")
            unit = self._normalize_deck_unit(deck_unit_value)
            count = self._normalize_deck_count(deck_count_value)
            low, high = _DECK_SECONDS_PER_UNIT
            min_seconds = low * count
            max_seconds = high * count
            mid_seconds = (low + high) * count // 2
            return {
                "status": "success",
                "mode": "speaking",
                "deck_unit": unit,
                "deck_count": count,
                "seconds_per_unit": [low, high],
                "min_seconds": min_seconds,
                "min_humanized": _humanize(Fraction(min_seconds)),
                "max_seconds": max_seconds,
                "max_humanized": _humanize(Fraction(max_seconds)),
                "mid_seconds": mid_seconds,
                "mid_humanized": _humanize(Fraction(mid_seconds)),
            }
        if not has_text:
            raise ValueError(
                "speaking requires text (word tiers) or deck_count "
                "(slide/bullet rule)")
        text = self._normalize_text(text_value, "text")
        words, cjk = _count_words(text)
        return {
            "status": "success",
            "mode": "speaking",
            "words": words,
            "latin_words": words - cjk,
            "cjk_chars": cjk,
            "counting_rule": _COUNTING_RULE,
            "tiers": [
                {
                    "tier": label,
                    "wpm": wpm,
                    "seconds": _ceil_seconds(
                        Fraction(words * 60, wpm)),
                    "humanized": _humanize(Fraction(words * 60, wpm)),
                }
                for label, wpm in _SPEAKING_TIERS
            ],
        }

    # ------------------------------------------------------------------
    # mode: custom
    # ------------------------------------------------------------------
    def _custom(self, text_value: Any, wpm_value: Any,
                seconds_per_char_value: Any) -> dict:
        text = self._normalize_text(text_value, "text")
        if seconds_per_char_value is not None:
            if wpm_value is not None:
                raise ValueError(
                    "custom accepts either wpm or seconds_per_char, "
                    "not both")
            spc = self._normalize_seconds_per_char(seconds_per_char_value)
            chars = len(text)
            raw = _to_fraction(spc) * chars
            return {
                "status": "success",
                "mode": "custom",
                "basis": "chars",
                "chars": chars,
                "seconds_per_char": spc,
                "seconds": _ceil_seconds(raw),
                "humanized": _humanize(raw),
                "note": _SUBTITLE_NOTE,
            }
        wpm = _DEFAULT_WPM if wpm_value is None \
            else self._normalize_wpm(wpm_value, "wpm")
        words, cjk = _count_words(text)
        raw = Fraction(words * 60) / _to_fraction(wpm)
        return {
            "status": "success",
            "mode": "custom",
            "basis": "words",
            "words": words,
            "latin_words": words - cjk,
            "cjk_chars": cjk,
            "counting_rule": _COUNTING_RULE,
            "wpm": wpm,
            "seconds": _ceil_seconds(raw),
            "humanized": _humanize(raw),
        }

    # ------------------------------------------------------------------
    # mode: plan
    # ------------------------------------------------------------------
    def _plan(self, minutes_value: Any, wpm_value: Any) -> dict:
        minutes = self._normalize_minutes(minutes_value)
        wpm = _DEFAULT_WPM if wpm_value is None \
            else self._normalize_wpm(wpm_value, "wpm")
        slot = _to_fraction(minutes) * 60
        budget = _to_fraction(minutes) * _to_fraction(wpm)
        return {
            "status": "success",
            "mode": "plan",
            "target_minutes": minutes,
            "wpm": wpm,
            "slot_seconds": _number_or_int(slot),
            "slot_humanized": _humanize(slot),
            "budget_words": _number_or_int(budget),
            "min_words": math.floor(budget * 9 / 10),
            "max_words": math.ceil(budget * 11 / 10),
            "tolerance": "+/-10%",
        }
