#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: text_directionality_tool.py

"""Script direction analysis tool built purely on ``unicodedata``.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper that tells an
agent which way text flows — useful before rendering, logging,
tokenizing or any mixed-script processing where a wrong direction
assumption garbles the output.

The tool classifies every character by its Unicode bidirectional
category (``unicodedata.bidirectional``) and aggregates the strong
directional classes into a verdict, supporting four modes:

* ``detect`` — overall dominant direction of one text:
  ``ltr`` / ``rtl`` / ``mixed`` (or ``neutral`` when no strong
  character exists at all, e.g. digits/punctuation-only input).
  Strong right-to-left classes are ``R`` (e.g. Hebrew) and ``AL``
  (Arabic letters); the strong left-to-right class is ``L`` (Latin,
  Greek, Cyrillic, CJK, ...). Weak and neutral characters — European
  (``EN``) and Arabic-Indic (``AN``) digits, separators, whitespace,
  punctuation — are counted and reported but never decide the
  direction. The result carries the per-class counts and the
  ``rtl_ratio`` (strong RTL / all strong characters).
* ``per_paragraph`` — split the text on blank lines and analyze each
  paragraph independently (same verdict rules), returning per-
  paragraph direction, counts, 1-based line ranges, previews and the
  list of mixed paragraph indices.
* ``bidi_chars`` — locate the explicit bidi control characters:
  U+200E LRM, U+200F RLM, U+202A-202E embedding/override marks
  (LRE/RLE/PDF/LRO/RLO) and U+2066-2069 isolates (LRI/RLI/FSI/PDI),
  with index, name and kind for every occurrence plus a security
  note — override marks can reorder how text *renders* and are a
  known display-spoofing technique (e.g. hiding an ``.exe`` extension
  inside what looks like ``file.png``).
* ``strip_bidi`` — remove those bidi control characters and return
  the cleaned text with per-codepoint removal counts. LRM/RLM are
  invisible display hints that are safe to strip in data contexts;
  embedding/override/isolate marks actively reorder display, so
  investigate them with ``bidi_chars`` before stripping.

Design note: the eleven explicit bidi control characters above carry
strong bidi classes themselves (e.g. LRM is class ``L``, RLM is class
``R``) but are *formatting marks, not content* — they are excluded
from the strong counts of the ``detect`` / ``per_paragraph`` verdicts
and reported separately as ``bidi_control_count`` so an invisible
mark can never flip a verdict.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing / non-string / empty /
oversized text) raise a ``ValueError``, mirroring the other common
tools. All output is deterministic — no randomness, no network, no
new dependencies.
"""

import unicodedata
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Bounds used by validation and result capping. Module-level (not
# pydantic fields) so class-level access works inside classmethods.
_MAX_TEXT_CHARS = 100_000
_MAX_OCCURRENCES = 100
_PREVIEW_CHARS = 40


class TextDirectionalityTool(Tool):
    """Script direction analysis tool built purely on ``unicodedata``.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
        max_occurrences (int): Cap on the per-occurrence records
            returned by the ``bidi_chars`` mode (the total count is
            always reported in full).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_directionality_tool"
    description: str = (
        "Text directionality tool — pure Python stdlib unicodedata, no "
        "network required. Detect the dominant direction of text "
        "(ltr/rtl/mixed/neutral) from Unicode bidi classes with "
        "per-class counts and ratio (mode='detect'), analyze each "
        "paragraph split on blank lines and flag mixed paragraphs "
        "(mode='per_paragraph'), locate explicit bidi control "
        "characters LRM/RLM, U+202A-202E embedding/override marks and "
        "U+2066-2069 isolates with a display-spoofing security note "
        "(mode='bidi_chars'), and strip those controls returning the "
        "cleaned text with removal counts (mode='strip_bidi')."
    )

    MODES: ClassVar[tuple] = (
        "detect",
        "per_paragraph",
        "bidi_chars",
        "strip_bidi",
    )
    max_text_chars: int = _MAX_TEXT_CHARS
    max_occurrences: int = _MAX_OCCURRENCES
    preview_chars: int = _PREVIEW_CHARS

    # Strong directional bidi classes: R/AL are right-to-right content
    # (Hebrew / Arabic letters), L is left-to-right content (Latin,
    # Greek, Cyrillic, CJK, ...).
    STRONG_RTL_CLASSES: ClassVar[frozenset] = frozenset({"R", "AL"})
    STRONG_LTR_CLASSES: ClassVar[frozenset] = frozenset({"L"})

    # The eleven explicit bidi control characters (format category Cf),
    # built from codepoints to keep the source free of invisible
    # literals. kind: the role the character plays in the Unicode Bidi
    # Algorithm. (codepoint, name, kind, description)
    _BIDI_CONTROL_SPECS: ClassVar[tuple] = (
        (0x200E, "LEFT-TO-RIGHT MARK", "mark",
         "invisible LTR hint mark (LRM)"),
        (0x200F, "RIGHT-TO-LEFT MARK", "mark",
         "invisible RTL hint mark (RLM)"),
        (0x202A, "LEFT-TO-RIGHT EMBEDDING", "embedding",
         "start an LTR embedding (LRE)"),
        (0x202B, "RIGHT-TO-LEFT EMBEDDING", "embedding",
         "start an RTL embedding (RLE)"),
        (0x202C, "POP DIRECTIONAL FORMATTING", "pop",
         "end the current embedding/override (PDF)"),
        (0x202D, "LEFT-TO-RIGHT OVERRIDE", "override",
         "force LTR character order (LRO)"),
        (0x202E, "RIGHT-TO-LEFT OVERRIDE", "override",
         "force RTL character order (RLO)"),
        (0x2066, "LEFT-TO-RIGHT ISOLATE", "isolate",
         "isolated LTR run (LRI)"),
        (0x2067, "RIGHT-TO-LEFT ISOLATE", "isolate",
         "isolated RTL run (RLI)"),
        (0x2068, "FIRST STRONG ISOLATE", "isolate",
         "isolated run, direction from first strong character (FSI)"),
        (0x2069, "POP DIRECTIONAL ISOLATE", "pop",
         "end the current isolate (PDI)"),
    )
    BIDI_CONTROLS: ClassVar[dict[str, dict[str, Any]]] = {
        f"U+{codepoint:04X}": {
            "char": chr(codepoint),
            "name": name,
            "kind": kind,
            "description": description,
        }
        for codepoint, name, kind, description in _BIDI_CONTROL_SPECS
    }
    _CONTROL_CHARS: ClassVar[frozenset] = frozenset(
        info["char"] for info in BIDI_CONTROLS.values()
    )

    SECURITY_NOTE: ClassVar[str] = (
        "Explicit bidi controls are invisible formatting characters. "
        "Override marks (U+202D LRO / U+202E RLO) and the "
        "embedding/isolate controls reorder how text renders and are a "
        "known display-spoofing technique — e.g. 'photo\\u202egnp.exe' "
        "renders as 'photoexe.png', hiding the real extension. Review "
        "every occurrence before trusting the surrounding text, and "
        "compare the logical order with mode='strip_bidi' when in "
        "doubt."
    )
    STRIP_NOTE: ClassVar[str] = (
        "LRM (U+200E) and RLM (U+200F) are invisible display hints "
        "that are safe to remove in data contexts — they never change "
        "content. Embedding/override marks (U+202A-U+202E) and "
        "isolates (U+2066-U+2069) actively reorder display: stripping "
        "them restores the logical character order but discards the "
        "intended visual ordering, so inspect them with "
        "mode='bidi_chars' first when the text matters."
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any = None, text: Any = None) -> dict[str, Any]:
        """Run one directionality analysis.

        Args:
            mode (str): One of ``detect`` / ``per_paragraph`` /
                ``bidi_chars`` / ``strip_bidi``.
            text (str): The text to analyze (non-empty, at most
                100,000 characters).

        Returns:
            Dict[str, Any]: The analysis result — always a ``mode``
                echo plus the mode-specific fields described in the
                class docstring.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "detect":
            return self._run_detect(clean_text)
        if mode == "per_paragraph":
            return self._run_per_paragraph(clean_text)
        if mode == "bidi_chars":
            return self._run_bidi_chars(clean_text)
        return self._run_strip_bidi(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_directionality_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (a non-empty bounded string)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > _MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {_MAX_TEXT_CHARS:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    # ------------------------------------------------------------------ #
    # Core classification
    # ------------------------------------------------------------------ #

    @classmethod
    def _analyze(cls, text: str) -> dict[str, Any]:
        """Classify every character of ``text`` by bidi class.

        Returns raw per-class counts plus the strong-direction counts.
        Explicit bidi control characters (LRM/RLM/embeddings/overrides/
        isolates) are formatting marks, not content: they are excluded
        from the strong counts and counted separately.
        """
        class_counts: dict[str, int] = {}
        ltr_strong = 0
        rtl_strong = 0
        control_count = 0
        for char in text:
            bidi_class = unicodedata.bidirectional(char)
            class_counts[bidi_class] = class_counts.get(bidi_class, 0) + 1
            if char in cls._CONTROL_CHARS:
                control_count += 1
                continue
            if bidi_class in cls.STRONG_RTL_CLASSES:
                rtl_strong += 1
            elif bidi_class in cls.STRONG_LTR_CLASSES:
                ltr_strong += 1
        return {
            "class_counts": class_counts,
            "ltr_strong": ltr_strong,
            "rtl_strong": rtl_strong,
            "control_count": control_count,
        }

    @classmethod
    def _verdict(cls, ltr_strong: int, rtl_strong: int) -> str:
        """Map strong counts to the dominant-direction verdict."""
        if ltr_strong and rtl_strong:
            return "mixed"
        if ltr_strong:
            return "ltr"
        if rtl_strong:
            return "rtl"
        return "neutral"

    @staticmethod
    def _sorted_counts(counts: dict[str, int]) -> dict[str, int]:
        """Sort a count dict by count descending then key ascending."""
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    @classmethod
    def _ratio(cls, ltr_strong: int, rtl_strong: int) -> Any:
        """Strong-RTL share of all strong characters (None if no strong)."""
        total = ltr_strong + rtl_strong
        if total == 0:
            return None
        return round(rtl_strong / total, 4)

    # ------------------------------------------------------------------ #
    # detect / per_paragraph modes
    # ------------------------------------------------------------------ #

    def _run_detect(self, text: str) -> dict[str, Any]:
        """Overall dominant direction of the whole text."""
        analysis = self._analyze(text)
        ltr_strong = analysis["ltr_strong"]
        rtl_strong = analysis["rtl_strong"]
        total_strong = ltr_strong + rtl_strong
        return {
            "mode": "detect",
            "dominant_direction": self._verdict(ltr_strong, rtl_strong),
            "strong_counts": {"ltr": ltr_strong, "rtl": rtl_strong},
            "total_strong": total_strong,
            "rtl_ratio": self._ratio(ltr_strong, rtl_strong),
            "bidi_class_counts": self._sorted_counts(analysis["class_counts"]),
            "neutral_char_count": len(text) - total_strong
            - analysis["control_count"],
            "bidi_control_count": analysis["control_count"],
            "total_chars": len(text),
        }

    @classmethod
    def _split_paragraphs(cls, text: str) -> list[tuple[int, int, str]]:
        """Split on blank lines into (start_line, end_line, paragraph).

        A paragraph is a maximal run of non-blank lines (1-based line
        numbers, ``\\n`` line separators); blank lines — lines that are
        empty or whitespace-only — separate paragraphs.
        """
        paragraphs: list[tuple[int, int, str]] = []
        current: list[str] = []
        start = 0
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            if line.strip():
                if not current:
                    start = line_no
                current.append(line)
            elif current:
                paragraphs.append((start, line_no - 1, "\n".join(current)))
                current = []
        if current:
            paragraphs.append((start, len(lines), "\n".join(current)))
        return paragraphs

    def _run_per_paragraph(self, text: str) -> dict[str, Any]:
        """Per-paragraph direction, flagging mixed paragraphs."""
        records: list[dict[str, Any]] = []
        summary = {"ltr": 0, "rtl": 0, "mixed": 0, "neutral": 0}
        mixed_paragraphs: list[int] = []
        for index, (start, end, paragraph) in enumerate(
            self._split_paragraphs(text)
        ):
            analysis = self._analyze(paragraph)
            direction = self._verdict(
                analysis["ltr_strong"], analysis["rtl_strong"]
            )
            summary[direction] += 1
            if direction == "mixed":
                mixed_paragraphs.append(index)
            records.append(
                {
                    "index": index,
                    "direction": direction,
                    "strong_counts": {
                        "ltr": analysis["ltr_strong"],
                        "rtl": analysis["rtl_strong"],
                    },
                    "rtl_ratio": self._ratio(
                        analysis["ltr_strong"], analysis["rtl_strong"]
                    ),
                    "bidi_control_count": analysis["control_count"],
                    "char_count": len(paragraph),
                    "start_line": start,
                    "end_line": end,
                    "preview": paragraph[: _PREVIEW_CHARS],
                }
            )
        return {
            "mode": "per_paragraph",
            "paragraph_count": len(records),
            "paragraphs": records,
            "summary": summary,
            "mixed_paragraphs": mixed_paragraphs,
        }

    # ------------------------------------------------------------------ #
    # bidi_chars / strip_bidi modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_bidi_chars(cls, text: str) -> dict[str, Any]:
        """Locate every explicit bidi control character in the text."""
        occurrences: list[dict[str, Any]] = []
        counts: dict[str, int] = {}
        has_override = False
        for index, char in enumerate(text):
            if char not in cls._CONTROL_CHARS:
                continue
            codepoint = f"U+{ord(char):04X}"
            info = cls.BIDI_CONTROLS[codepoint]
            counts[codepoint] = counts.get(codepoint, 0) + 1
            if info["kind"] == "override":
                has_override = True
            occurrences.append(
                {
                    "index": index,
                    "char": char,
                    "codepoint": codepoint,
                    "name": info["name"],
                    "kind": info["kind"],
                    "description": info["description"],
                }
            )
        total_found = len(occurrences)
        truncated = total_found > _MAX_OCCURRENCES
        return {
            "mode": "bidi_chars",
            "total_found": total_found,
            "counts_by_codepoint": cls._sorted_counts(counts),
            "occurrences": occurrences[: _MAX_OCCURRENCES],
            "occurrence_list_truncated": truncated,
            "has_override": has_override,
            "security_note": cls.SECURITY_NOTE,
        }

    @classmethod
    def _run_strip_bidi(cls, text: str) -> dict[str, Any]:
        """Remove the explicit bidi control characters from the text."""
        removed_by_codepoint: dict[str, int] = {}
        cleaned_chars: list[str] = []
        for char in text:
            if char in cls._CONTROL_CHARS:
                codepoint = f"U+{ord(char):04X}"
                removed_by_codepoint[codepoint] = (
                    removed_by_codepoint.get(codepoint, 0) + 1
                )
                continue
            cleaned_chars.append(char)
        cleaned = "".join(cleaned_chars)
        return {
            "mode": "strip_bidi",
            "cleaned": cleaned,
            "removed_count": len(text) - len(cleaned),
            "removed_by_codepoint": cls._sorted_counts(removed_by_codepoint),
            "changed": cleaned != text,
            "note": cls.STRIP_NOTE,
        }
