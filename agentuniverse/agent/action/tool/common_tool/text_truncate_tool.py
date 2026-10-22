#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_truncate_tool.py

"""Budget-aware text truncation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text truncation
utility for agents that must produce constrained output — token or
character budgets, UI length limits, storage caps.

``TextChunkerTool`` splits text into chunks and ``TextWrapTool``
reflows text at a width; this tool TRUNCATES text to a budget using
smart boundaries. It supports four modes:

* ``chars`` — hard cap of ``max`` characters (Python code points, so
  one CJK ideograph or emoji counts as one). With
  ``word_boundary=True`` the cut snaps back so it lands after a whole
  word: if the budget falls mid-word, everything from the previous
  whitespace onwards is dropped (trailing whitespace is stripped).
  When the prefix contains no usable whitespace — CJK runs are never
  space-separated, and neither are URLs or long identifiers — the
  hard cut is kept.
* ``words`` — keep the first ``max`` words. ``whitespace='normalize'``
  (the default) rejoins the kept words with single spaces (adjacent
  CJK characters stay unspaced); ``whitespace='preserve'`` cuts the
  original text at the offset of the last kept word, keeping the
  original inter-word spacing. CJK runs fall back to a character
  budget: because CJK text is not space-separated, every CJK
  ideograph / kana / hangul character counts as exactly one word, so
  a pure-CJK input of ``max`` characters or fewer is returned
  unchanged and longer inputs are cut at the ``max``-th character.
* ``sentences`` — keep the first ``max`` sentences using conservative
  segmentation: a sentence ends at ``.`` ``!`` ``?`` or the CJK
  ``。`` ``！`` ``？``. An ASCII ``.`` ends a sentence only when
  whitespace or the end of the text follows (which also rules out
  decimals like ``3.14``); because CJK text carries no
  inter-sentence whitespace, ``!`` ``?`` and the CJK ``。`` ``！``
  ``？`` accept any following character. ASCII '.'
  additionally respects a guard for common English abbreviations
  (``Mr.``, ``Dr.``, ``e.g.``, ``i.e.``, ``etc.``, ``Inc.`` …,
  including interior dots of dotted abbreviations), single uppercase
  initials (``J. Smith``) and decimals (``3.14``). The guard errs on
  the side of fewer, longer sentences. The result is a byte-exact
  prefix of the original ending at the last kept terminator.
* ``head_chars_keep_sentences`` — a character budget like ``chars``,
  but the cut moves to the sentence boundary closest to the budget as
  long as it lies within ``tolerance`` characters (extend or shrink;
  default ``max(10, max // 10)``). Ties prefer the boundary not
  exceeding the budget; when no boundary lies within the tolerance
  the tool falls back to the exact character cut and reports
  ``boundary='char_fallback'``.

Shared options: ``max`` (the budget, required, >= 1); ``add_ellipsis``
appends ``...`` for ``language='en'`` (the default) or ``…`` for
``language='cjk'`` when truncation actually happened — an input that
already fits the budget is returned byte-identical with no ellipsis.
By default (``count_ellipsis=False``) the ellipsis is NOT counted
against the budget, so the result may exceed ``max`` by the ellipsis
length; with ``count_ellipsis=True`` (character-based modes only —
``chars`` and ``head_chars_keep_sentences``; it has no effect in the
``words`` / ``sentences`` modes, where the budget counts words or
sentences) the
ellipsis IS counted — the text budget shrinks by the ellipsis length,
so the hard character cut plus ellipsis never exceeds ``max``
(``head_chars_keep_sentences`` may still exceed it when the snap to a
sentence boundary deliberately extends past the budget — that is the
point of the mode). ``min_length`` (optional, in characters; must
not exceed ``max`` in the character-based modes) refuses cuts that
would leave fewer than ``min_length`` characters: if the whole
original fits within 1.5x the budget
(measured in the mode's natural unit — characters, words or
sentences) the original is returned unchanged with
``refusal='min_length'``; otherwise a structured ``error`` payload is
returned instead of raising.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, boolean traps like ``max=True``,
empty or oversized text, unknown mode / language / whitespace value,
``min_length`` exceeding ``max`` in the character-based modes,
``count_ellipsis`` without ``add_ellipsis``, mode-specific options
used with the wrong mode) raise a ``ValueError``. Content-level
outcomes are returned structurally, never by raising.
"""

import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Sentence terminators (ASCII + CJK ideographic and fullwidth forms).
_TERMINATORS = ".!?。！？"
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
# CJK ideographs, kana and hangul: in words mode every code point in
# these ranges counts as exactly one word.
_CJK_CLASS = (
    "\u3040-\u30ff"   # hiragana + katakana
    "\u3400-\u4dbf"   # CJK extension A
    "\u4e00-\u9fff"   # CJK unified ideographs
    "\uac00-\ud7af"   # hangul syllables
    "\uf900-\ufaff"   # CJK compatibility ideographs
)
_CJK_CHAR = re.compile(f"[{_CJK_CLASS}]")
# A word unit: a single CJK character, or a maximal run of
# non-whitespace non-CJK characters.
_WORD_UNIT = re.compile(f"[{_CJK_CLASS}]|[^\\s{_CJK_CLASS}\\ufeff]+")

_ELLIPSIS = {"en": "...", "cjk": "…"}


def _is_cjk(char: str) -> bool:
    """True when ``char`` (exactly one code point) is CJK/kana/hangul."""
    return _CJK_CHAR.fullmatch(char) is not None


class TextTruncateTool(Tool):
    """Budget-aware text truncation tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_truncate_tool"
    description: str = (
        "Text truncation tool — pure Python stdlib, no network "
        "required. Budget-aware truncation with smart boundaries: "
        "mode='chars' caps characters with optional word-boundary "
        "snap-back, mode='words' keeps the first N words "
        "(whitespace-normalized or original-preserved rejoin; CJK "
        "ideographs count one word each), mode='sentences' keeps the "
        "first N sentences using conservative .!? plus CJK 。！？ "
        "segmentation with an English abbreviation guard, and "
        "mode='head_chars_keep_sentences' spends a character budget "
        "but snaps the cut to the nearest sentence boundary within a "
        "tolerance. Optional ellipsis ('...' or '…') appended when "
        "truncation happened, and a min_length guard that refuses "
        "over-aggressive cuts."
    )

    MODES: ClassVar[tuple] = (
        "chars", "words", "sentences", "head_chars_keep_sentences",
    )
    LANGUAGES: ClassVar[tuple] = ("en", "cjk")
    WHITESPACE_MODES: ClassVar[tuple] = ("normalize", "preserve")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        max: Any = None,  # noqa: A002 — the documented option name
        add_ellipsis: Any = None,
        language: Any = None,
        count_ellipsis: Any = None,
        min_length: Any = None,
        word_boundary: Any = None,
        whitespace: Any = None,
        tolerance: Any = None,
    ) -> Dict[str, Any]:
        """Run one truncation.

        Args:
            mode (str): One of ``chars`` / ``words`` / ``sentences`` /
                ``head_chars_keep_sentences``.
            text (str): The non-empty text to truncate (at most
                100,000 characters).
            max (int): The budget — characters for the ``chars`` and
                ``head_chars_keep_sentences`` modes, words for
                ``words``, sentences for ``sentences``. Required,
                >= 1, at most 1,000,000.
            add_ellipsis (bool): Append ``...`` (``language='en'``,
                the default) or ``…`` (``language='cjk'``) when
                truncation actually happened. Inputs that already fit
                the budget are returned byte-identical with no
                ellipsis.
            language (str): ``en`` (``...``) or ``cjk`` (``…``);
                ellipsis style only, default ``en``.
            count_ellipsis (bool): When ``add_ellipsis`` is set —
                ``False`` (default): the ellipsis is NOT counted
                against the budget, the result may exceed ``max`` by
                the ellipsis length; ``True``: the ellipsis IS
                counted, the text budget shrinks by the ellipsis
                length and the hard cut plus ellipsis never exceeds
                ``max`` (sentence-snap extension may still exceed
                it by design). Meaningful only in the character-based
                modes (``chars`` and ``head_chars_keep_sentences``);
                it has no effect in the ``words`` / ``sentences``
                modes, where the budget counts words or sentences.
                Requires ``add_ellipsis``.
            min_length (int): Optional guard (>= 1, characters; must
                not exceed ``max`` in the character-based modes): if
                a cut would leave fewer characters than this, the
                tool refuses — returning the original unchanged when
                the whole input fits within 1.5x the budget (in the
                mode's natural unit), otherwise a structured error.
            word_boundary (bool): ``chars`` mode only — snap the cut
                back so it lands after a whole word.
            whitespace (str): ``words`` mode only — ``normalize``
                (default; rejoin kept words with single spaces) or
                ``preserve`` (keep the original inter-word spacing).
            tolerance (int): ``head_chars_keep_sentences`` mode only —
                how far (characters) the cut may move to reach the
                nearest sentence boundary; default
                ``max(10, max // 10)``.

        Returns:
            Dict[str, Any]: The truncation result (always a ``result``
                string plus the call context) or a structured
                ``error`` payload for the min-length refusal.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_max = self._validate_max(max)
        use_ellipsis = self._validate_bool_option("add_ellipsis", add_ellipsis)
        clean_language = self._validate_language(language)
        count_ell = self._validate_bool_option("count_ellipsis", count_ellipsis)
        clean_min_length = self._validate_min_length(
            min_length, clean_max, mode
        )
        clean_word_boundary = self._validate_mode_bool_option(
            "word_boundary", word_boundary, mode, "chars"
        )
        clean_whitespace = self._validate_whitespace(whitespace, mode)
        clean_tolerance = self._validate_tolerance(tolerance, mode, clean_max)

        if count_ell and not use_ellipsis:
            self._invalid(
                "count_ellipsis=True requires add_ellipsis=True — an "
                "ellipsis that is not appended cannot be counted"
            )

        ellipsis = _ELLIPSIS[clean_language] if use_ellipsis else ""
        # Effective character budget for the ellipsis-counted case.
        # Only the character-based modes count the ellipsis against
        # ``max``; in the words / sentences modes the budget is a word
        # or sentence count, so count_ellipsis has no effect there and
        # must not reject small budgets.
        char_budget = clean_max
        if (
            use_ellipsis
            and count_ell
            and mode in ("chars", "head_chars_keep_sentences")
        ):
            char_budget = clean_max - len(ellipsis)
            if char_budget < 1:
                self._invalid(
                    f"max ({clean_max}) is too small to fit the "
                    f"{clean_language!r} ellipsis ({len(ellipsis)} "
                    "characters) plus at least one character of text"
                )

        runners = {
            "chars": self._run_chars,
            "words": self._run_words,
            "sentences": self._run_sentences,
            "head_chars_keep_sentences": self._run_head_chars,
        }
        return runners[mode](
            clean_text,
            clean_max,
            char_budget,
            ellipsis,
            clean_min_length,
            clean_word_boundary,
            clean_whitespace,
            clean_tolerance,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_truncate_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_max(cls, value: Any) -> int:
        """Validate the ``max`` budget (rejects booleans outright)."""
        if value is None:
            cls._invalid("max is required (the truncation budget)")
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"max must be an integer >= 1 (got {value!r})")
        if value < 1:
            cls._invalid(f"max must be an integer >= 1 (got {value!r})")
        if value > 1_000_000:
            cls._invalid(f"max exceeds the 1,000,000 limit (got {value:,})")
        return value

    @classmethod
    def _validate_bool_option(cls, name: str, value: Any) -> bool:
        """Validate a boolean option (None means False; no 0/1/'yes')."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean (got {value!r})")
        return False  # pragma: no cover - _invalid always raises

    @classmethod
    def _validate_language(cls, language: Any) -> str:
        """Validate the ellipsis ``language`` selector."""
        if language is None:
            return "en"
        if (
            isinstance(language, bool)
            or not isinstance(language, str)
            or language not in cls.LANGUAGES
        ):
            cls._invalid(
                f"language must be one of: {', '.join(cls.LANGUAGES)} "
                f"(got {language!r})"
            )
        return language

    @classmethod
    def _validate_min_length(
        cls, min_length: Any, clean_max: int, mode: str
    ) -> int:
        """Validate the ``min_length`` guard.

        In the character-based modes ``min_length`` must not exceed
        ``max`` (no cut could ever satisfy that); in the words /
        sentences modes the budget is a count while ``min_length``
        is characters, so only ``>= 1`` is enforced there.
        """
        if min_length is None:
            return 0
        if (
            isinstance(min_length, bool)
            or not isinstance(min_length, int)
            or min_length < 1
        ):
            cls._invalid(
                f"min_length must be an integer >= 1 (got {min_length!r})"
            )
        if (
            mode in ("chars", "head_chars_keep_sentences")
            and min_length > clean_max
        ):
            cls._invalid(
                f"min_length ({min_length}) cannot exceed max "
                f"({clean_max}) — no cut could ever satisfy it"
            )
        return min_length

    @classmethod
    def _validate_mode_bool_option(
        cls, name: str, value: Any, mode: str, only_mode: str
    ) -> bool:
        """Validate a boolean option that only one mode understands."""
        if value is None:
            return False
        if mode != only_mode:
            cls._invalid(
                f"{name} is only valid in the {only_mode!r} mode "
                f"(got {name}={value!r} with mode={mode!r})"
            )
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean (got {value!r})")
        return False  # pragma: no cover - _invalid always raises

    @classmethod
    def _validate_whitespace(cls, whitespace: Any, mode: str) -> str:
        """Validate the ``words``-mode whitespace handling."""
        if whitespace is None:
            return "normalize"
        if mode != "words":
            cls._invalid(
                "whitespace is only valid in the 'words' mode "
                f"(got whitespace={whitespace!r} with mode={mode!r})"
            )
        if (
            isinstance(whitespace, bool)
            or not isinstance(whitespace, str)
            or whitespace not in cls.WHITESPACE_MODES
        ):
            cls._invalid(
                "whitespace must be one of: "
                f"{', '.join(cls.WHITESPACE_MODES)} (got {whitespace!r})"
            )
        return whitespace

    @classmethod
    def _validate_tolerance(
        cls, tolerance: Any, mode: str, clean_max: int
    ) -> int:
        """Validate (or default) the sentence-snap ``tolerance``."""
        if tolerance is None:
            # Default: 10% of the budget, at least 10 characters
            # (computed without the shadowed builtin).
            default = clean_max // 10
            return default if default > 10 else 10
        if mode != "head_chars_keep_sentences":
            cls._invalid(
                "tolerance is only valid in the "
                "'head_chars_keep_sentences' mode "
                f"(got tolerance={tolerance!r} with mode={mode!r})"
            )
        if (
            isinstance(tolerance, bool)
            or not isinstance(tolerance, int)
            or tolerance < 0
        ):
            cls._invalid(
                f"tolerance must be an integer >= 0 (got {tolerance!r})"
            )
        if tolerance > 1_000_000:
            cls._invalid(
                f"tolerance exceeds the 1,000,000 limit (got {tolerance:,})"
            )
        return tolerance

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _base_context(mode: str, budget: int, ellipsis: str) -> Dict[str, Any]:
        """Build the common result context."""
        return {"mode": mode, "max": budget}

    @classmethod
    def _assemble(
        cls,
        context: Dict[str, Any],
        original: str,
        core: str,
        ellipsis: str,
        extra: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Attach the final result (original, or core + ellipsis).

        The reported ``ellipsis`` reflects only what was actually
        appended: an input returned unchanged never carries one.
        """
        truncated = core != original
        result = core + ellipsis if truncated else original
        return {
            **context,
            **extra,
            "truncated": truncated,
            "ellipsis": (ellipsis or None) if truncated else None,
            "original_length": len(original),
            "result_length": len(result),
            "result": result,
        }

    @classmethod
    def _min_length_refusal(
        cls,
        context: Dict[str, Any],
        extra: Dict[str, Any],
        original: str,
        min_length: int,
        core: str,
        budget: int,
        original_units: int,
    ) -> Dict[str, Any]:
        """Handle a cut that would drop below ``min_length``.

        If the whole original fits within 1.5x the budget (measured in
        the mode's natural unit) it is returned unchanged with
        ``refusal='min_length'``; otherwise a structured error payload
        is returned instead of raising.
        """
        if original_units <= 1.5 * budget:
            return {
                **context,
                **extra,
                "refusal": "min_length",
                "truncated": False,
                "ellipsis": None,
                "original_length": len(original),
                "result_length": len(original),
                "result": original,
            }
        return {
            **context,
            "error": {
                "type": "min_length_violation",
                "message": (
                    f"truncating to the budget would leave only "
                    f"{len(core)} characters, below min_length="
                    f"{min_length}, and the original ({original_units} "
                    f"budget units) does not fit within 1.5x the "
                    f"budget ({budget}); raise max, lower min_length, "
                    "or split the text first"
                ),
            },
        }

    # ------------------------------------------------------------------ #
    # chars mode
    # ------------------------------------------------------------------ #

    def _run_chars(
        self,
        text: str,
        budget: int,
        char_budget: int,
        ellipsis: str,
        min_length: int,
        word_boundary: bool,
        whitespace: str,
        tolerance: int,
    ) -> Dict[str, Any]:
        """Hard character cap with optional word-boundary snap-back."""
        context = self._base_context("chars", budget, ellipsis)
        extra: Dict[str, Any] = {"word_boundary": word_boundary}
        if len(text) <= char_budget:
            return self._assemble(context, text, text, "", extra)

        if word_boundary:
            core = self._snap_to_word_boundary(text, char_budget)
        else:
            core = text[:char_budget]

        if min_length and len(core) < min_length:
            return self._min_length_refusal(
                context, extra, text, min_length, core, char_budget,
                len(text),
            )
        return self._assemble(context, text, core, ellipsis, extra)

    @staticmethod
    def _snap_to_word_boundary(text: str, char_budget: int) -> str:
        """Re-cut the ``char_budget`` prefix so it ends after a word.

        If the budget lands mid-word, everything from the previous
        whitespace onwards is dropped (trailing whitespace stripped)
        so the cut lands after a whole word. When the prefix holds no
        usable boundary — CJK runs, URLs, single long words — the
        hard cut is kept.
        """
        prefix = text[:char_budget]
        if char_budget < len(text) and not text[char_budget].isspace():
            # The cut lands mid-word: snap back to the previous
            # whitespace so the cut lands after a whole word.
            snap = -1
            for index in range(char_budget - 1, -1, -1):
                if text[index].isspace():
                    snap = index
                    break
            if snap > 0 and text[:snap].rstrip():
                return text[:snap].rstrip()
            return prefix  # no usable boundary: keep the hard cut
        # The cut already lands on a word edge; strip the trailing
        # whitespace so it ends after a whole word.
        return prefix.rstrip()

    # ------------------------------------------------------------------ #
    # words mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _word_units(text: str) -> List[Tuple[int, int]]:
        """Split ``text`` into word units ``(start, end)``.

        A non-CJK unit is a maximal run of non-whitespace characters;
        a CJK unit is a single ideograph / kana / hangul character,
        so every unit carries exactly one word of weight.
        """
        return [(m.start(), m.end()) for m in _WORD_UNIT.finditer(text)]

    def _run_words(
        self,
        text: str,
        budget: int,
        char_budget: int,
        ellipsis: str,
        min_length: int,
        word_boundary: bool,
        whitespace: str,
        tolerance: int,
    ) -> Dict[str, Any]:
        """Keep the first ``budget`` words (CJK chars count one each)."""
        context = self._base_context("words", budget, ellipsis)
        units = self._word_units(text)
        total_words = len(units)
        kept = total_words if total_words < budget else budget
        extra: Dict[str, Any] = {
            "whitespace": whitespace,
            "words_total": total_words,
            "words_kept": kept,
        }
        if total_words <= budget:
            return self._assemble(context, text, text, "", extra)

        # Each unit weighs one word, so the cut goes right before the
        # (budget+1)-th unit; a CJK run is already exploded into
        # per-character units, cutting it at the exact character count.
        cut_end = units[budget][0]

        if whitespace == "preserve":
            core = text[:cut_end].rstrip()
        else:
            pieces: List[str] = []
            for start, end in units[:budget]:
                piece = text[start:end]
                if (
                    pieces
                    and _is_cjk(pieces[-1][-1])
                    and _is_cjk(piece[0])
                ):
                    pieces[-1] += piece  # adjacent CJK: no inserted space
                else:
                    pieces.append(piece)
            core = " ".join(pieces)

        if min_length and len(core) < min_length:
            return self._min_length_refusal(
                context, extra, text, min_length, core, budget, total_words,
            )
        return self._assemble(context, text, core, ellipsis, extra)

    # ------------------------------------------------------------------ #
    # sentences mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sentence_ends(text: str) -> List[int]:
        """Return the end offsets of every sentence in ``text``.

        Conservative segmentation: a sentence ends at a run of
        ``.!?。！？`` (plus absorbed closing quotes/brackets) only when
        whitespace or the end of the text follows (the ASCII '.' also
        respects the abbreviation / initial guards). A final
        unterminated fragment (any non-whitespace tail) counts as one
        more sentence ending at ``len(text)``.
        """
        ends: List[int] = []
        length = len(text)
        index = 0
        while index < length:
            if text[index] not in _TERMINATORS:
                index += 1
                continue
            run_end, close_end = TextTruncateTool._scan_terminator_run(
                text, index
            )
            if TextTruncateTool._terminator_ends_sentence(
                text, index, close_end
            ):
                ends.append(close_end)
                index = close_end
            else:
                index = run_end
        # A trailing non-whitespace fragment is a final sentence.
        tail = text[ends[-1]:] if ends else text
        if tail.strip():
            ends.append(length)
        return ends

    @staticmethod
    def _scan_terminator_run(text: str, index: int) -> Tuple[int, int]:
        """Scan the terminator run at ``index`` and its closing quotes.

        Returns ``(run_end, close_end)``: offsets just past the run of
        terminators and just past any closing quotes / brackets that
        immediately follow (so ``He said "stop."`` keeps its quote).
        """
        length = len(text)
        run_end = index
        while run_end < length and text[run_end] in _TERMINATORS:
            run_end += 1
        close_end = run_end
        while close_end < length and text[close_end] in _CLOSERS:
            close_end += 1
        return run_end, close_end

    @staticmethod
    def _terminator_ends_sentence(
        text: str, index: int, close_end: int
    ) -> bool:
        """True when the terminator run starting at ``index`` ends a sentence.

        CJK text carries no inter-sentence whitespace, so ``!?。！？``
        accept any following character; the ASCII '.' keeps the strict
        whitespace-or-end-of-text requirement that powers the
        abbreviation and decimal guards.
        """
        if text[index] != ".":
            return True
        if close_end < len(text) and not text[close_end].isspace():
            return False
        return TextTruncateTool._period_ends_sentence(text, index)

    @staticmethod
    def _period_ends_sentence(text: str, dot_index: int) -> bool:
        """Abbreviation / initial guards for one ASCII '.'."""
        # Interior dot of a dotted abbreviation ('e.g', 'U.S'):
        # a letter immediately followed by another '.' continues the
        # token, so this '.' cannot end a sentence.
        if (
            dot_index + 2 < len(text)
            and text[dot_index + 1].isalpha()
            and text[dot_index + 2] == "."
        ):
            return False
        token = TextTruncateTool._token_before(text, dot_index)
        if not token:
            return True
        if token.lower() in _ABBREVIATIONS:
            return False
        if len(token) == 1 and token.isupper():
            return False  # single uppercase initial, e.g. 'J. Smith'
        return True

    @staticmethod
    def _token_before(text: str, dot_index: int) -> str:
        """The run of letters/dots immediately before ``dot_index``."""
        start = dot_index
        while start > 0 and (
            text[start - 1].isalpha() or text[start - 1] == "."
        ):
            start -= 1
        return text[start:dot_index]

    def _run_sentences(
        self,
        text: str,
        budget: int,
        char_budget: int,
        ellipsis: str,
        min_length: int,
        word_boundary: bool,
        whitespace: str,
        tolerance: int,
    ) -> Dict[str, Any]:
        """Keep the first ``budget`` sentences (byte-exact prefix cut)."""
        context = self._base_context("sentences", budget, ellipsis)
        ends = self._sentence_ends(text)
        total = len(ends)
        kept = total if total < budget else budget
        extra: Dict[str, Any] = {
            "sentences_total": total,
            "sentences_kept": kept,
        }
        if total <= budget:
            return self._assemble(context, text, text, "", extra)

        core = text[:ends[budget - 1]]
        if min_length and len(core) < min_length:
            return self._min_length_refusal(
                context, extra, text, min_length, core, budget, total,
            )
        return self._assemble(context, text, core, ellipsis, extra)

    # ------------------------------------------------------------------ #
    # head_chars_keep_sentences mode
    # ------------------------------------------------------------------ #

    def _run_head_chars(
        self,
        text: str,
        budget: int,
        char_budget: int,
        ellipsis: str,
        min_length: int,
        word_boundary: bool,
        whitespace: str,
        tolerance: int,
    ) -> Dict[str, Any]:
        """Spend a character budget, snapped to the nearest sentence."""
        context = self._base_context(
            "head_chars_keep_sentences", budget, ellipsis
        )
        extra: Dict[str, Any] = {"tolerance": tolerance}
        if len(text) <= char_budget:
            extra["boundary"] = "none"
            return self._assemble(context, text, text, "", extra)

        # Sentence boundaries usable as a real cut: strictly inside
        # the text and followed by more than whitespace.
        candidates = [
            end
            for end in self._sentence_ends(text)
            if 1 <= end < len(text) and text[end:].strip()
        ]
        within = [
            end for end in candidates if abs(end - char_budget) <= tolerance
        ]
        if within:
            # Nearest to the budget; ties prefer the boundary that
            # does not exceed it.
            chosen = min(within, key=lambda end: (abs(end - char_budget), end))
            core = text[:chosen]
            extra["boundary"] = "sentence"
        else:
            core = text[:char_budget]
            extra["boundary"] = "char_fallback"

        if min_length and len(core) < min_length:
            return self._min_length_refusal(
                context, extra, text, min_length, core, char_budget,
                len(text),
            )
        return self._assemble(context, text, core, ellipsis, extra)
