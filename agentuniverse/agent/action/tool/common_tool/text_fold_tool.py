#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: text_fold_tool.py

"""Unicode text folding tool built purely on the stdlib ``unicodedata``.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency normalizer for
SEARCH-KEY equality: arbitrary strings that differ only by accents,
compatibility forms (fullwidth / halfwidth, ligatures, superscripts),
typographic symbols, case or whitespace collapse to ONE stable key,
so an agent or index can compare or bucket them without fuzzy
matching. The folded key is also a stable sort key, because folding
is deterministic and idempotent (``fold(fold(x)) == fold(x)``,
verified exhaustively for every single code point and over seeded
multi-character samples).

Four modes:

* ``fold`` — fold one string to its canonical key through the
  documented five-stage pipeline below.
* ``search_key`` — fold, then squash every run of non-alphanumeric
  characters to a single ``-`` separator (lucene-ish token key) and
  trim the ends, producing the stable key used for index equality.
* ``compare`` — fold two strings and report ``equal_after_fold``,
  both keys and the ``differing_positions`` of the KEYS (0-based,
  capped at 20 entries with a total count and a truncation flag).
* ``reverse_map`` — given a folded key and the original string it
  supposedly came from, verify the key and list the mapping
  EVIDENCE: every original character that transformed, with its
  codepoint, its folded fragment and the rule that fired — the
  transparency mode, so a caller can audit exactly why two strings
  became (or did not become) the same key.

The fold pipeline (order matters and is documented with its reason):

1. **NFKD decomposition** — ``unicodedata.normalize('NFKD', ...)``.
   This one stage performs every *compatibility* fold the Unicode
   standard defines: fullwidth ``ＡＢＣ`` -> ``abc``'s letters,
   halfwidth katakana ``ｶﾌｪ`` -> ``カフェ``, ligatures ``ﬁ`` ->
   ``fi`` and ``ﬀ`` -> ``ff``, superscript ``²`` -> ``2``, NBSP and
   the ideographic space ``　`` -> plain space, ``…`` -> ``...``, and
   Hangul syllables -> Jamo (``가`` -> ``가`` — a *deterministic*
   mapping, so precomposed syllables and explicit Jamo sequences
   produce the SAME key, which is exactly the search equality one
   wants). Han ideographs (``汉字``) have no decomposition of any
   kind and pass through NFKD untouched.
2. **Combining-mark strip** — drop every character of general
   category ``Mn`` / ``Me`` (accents, diaereses, Zalgo marks,
   Hebrew / Arabic diacritics). ``é`` and ``e`` become the same
   letter. Spacing combining marks (``Mc`` — Indic and Thai vowel
   signs) are deliberately KEPT: they carry lexical meaning, and
   stripping them would corrupt words rather than normalize them.
   Format characters (category ``Cf`` — the zero-width joiner and
   non-joiner, LRM / RLM, the word joiner, the soft hyphen) are not
   marks either: NFKD does not decompose them, so ``fold`` KEEPS
   them verbatim (an emoji ZWJ sequence survives intact) while
   ``search_key`` counts them as plain separators. A text made only
   of combining marks folds to the empty key, like a whitespace-only
   text — ``is_empty_after_fold`` reports both.
3. **Symbol map** — a small, fully enumerated table applied AFTER
   NFKD: ``×`` -> ``x``, ``÷`` -> ``/``, ``’`` -> ``'``,
   ``“`` / ``”`` -> ``"``, ``–`` / ``—`` -> ``-``, ``…`` -> ``...``.
   The map runs after NFKD so it only has to key the *canonical*
   post-decomposition alphabet — compatibility clones of these
   symbols are already reduced by stage 1 and cannot escape the map
   through a form the table does not list. (``…`` is additionally
   expanded by NFKD itself; the entry is kept so the documented
   behavior does not depend on that side effect.)
4. **Case fold** — ``str.casefold()``, the aggressive Unicode full
   case folding: ``ß`` -> ``ss``, ``Σ`` / ``ς`` / ``σ`` all ->
   ``σ`` (final-sigma distinction erased), ``İ`` -> ``i``. It runs
   AFTER the mark strip on purpose: full case folding of a few code
   points can re-introduce combining marks (``U+0130 İ`` folds to
   ``i`` + combining dot above — NFKD happens to pre-decompose it,
   but folding after the strip makes "no combining marks in the
   output" a structural guarantee instead of an accident). Case
   folding is locale-independent: Turkish dotless ``ı`` stays ``ı``.
5. **Whitespace collapse** — every run of whitespace collapses to one
   single space, with the ends trimmed. Compatibility spaces (NBSP,
   the U+2000..U+200A typographic family, the ideographic space)
   were already turned into plain spaces by stage 1; ASCII
   whitespace (tabs, newlines) NFKD passes through untouched and is
   handled directly here.

Idempotence holds for the composition: the folded output contains no
compatibility characters (stage 1 destroyed them), no combining
marks (stages 2 + 4), no mapped symbols (stage 3's replacements are
not themselves map keys) and no whitespace runs (stage 5), so
re-folding is a no-op — asserted in the tests over every single code
point and 300 seeded random texts.

Determinism: folding is a pure function of its input via the
interpreter's Unicode tables, so keys are stable within and across
runs on the same Python build.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types — booleans rejected
— missing / empty ``text`` / ``text_1`` / ``text_2``, strings over
the 100,000-character cap) raise a ``ValueError``, mirroring the
other common tools. The one content-level failure — a
``reverse_map`` key that does not match the recomputed fold of the
original — is returned as a structured ``error`` payload so an agent
can react without catching exceptions.
"""

import unicodedata
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class TextFoldTool(Tool):
    """Unicode text folding / search-key tool on the pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on any single string input;
            longer inputs are rejected before any work.
        max_differing_positions (int): Number of differing key
            positions reported individually by the ``compare`` mode
            (the rest are only counted).
        max_evidence_entries (int): Number of transformed characters
            listed individually by the ``reverse_map`` mode (the rest
            are only counted).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_fold_tool"
    description: str = (
        "Unicode text folding tool — collapse arbitrary strings to a "
        "stable search/sort key with the pure Python stdlib "
        "(unicodedata), no network required. Accent-insensitive, "
        "width-insensitive, ligature- and symbol-folding "
        "(mode='fold'), a lucene-ish non-alphanumeric-squashed index "
        "key (mode='search_key'), two-string comparison with "
        "differing key positions (mode='compare'), and a "
        "transparency mode listing every character transformation "
        "behind a key (mode='reverse_map')."
    )

    MODES: ClassVar[tuple] = ("fold", "search_key", "compare", "reverse_map")
    # The complete, enumerated symbol canonicalization table — the
    # ONLY character substitutions outside the Unicode tables.
    SYMBOL_MAP: ClassVar[Dict[str, str]] = {
        "×": "x",   # U+00D7 multiplication sign
        "÷": "/",   # U+00F7 division sign
        "’": "'",   # U+2019 right single quotation mark
        "“": '"',   # U+201C left double quotation mark
        "”": '"',   # U+201D right double quotation mark
        "–": "-",   # U+2013 en dash
        "—": "-",   # U+2014 em dash
        "…": "...",  # U+2026 horizontal ellipsis (NFKD also expands)
    }
    # Combining-mark categories stripped by stage 2. ``Mc`` (spacing
    # marks: Indic/Thai vowel signs) is deliberately NOT stripped.
    MARK_CATEGORIES: ClassVar[tuple] = ("Mn", "Me")
    # The documented pipeline, echoed in every ``fold`` result.
    PIPELINE: ClassVar[tuple] = (
        "nfkd_decomposition",
        "combining_mark_strip",
        "symbol_map",
        "case_fold",
        "whitespace_collapse",
    )

    max_text_chars: int = 100_000
    max_differing_positions: int = 20
    max_evidence_entries: int = 200

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        text_1: Any = None,
        text_2: Any = None,
        folded_key: Any = None,
    ) -> Dict[str, Any]:
        """Run one folding operation.

        Args:
            mode (str): One of ``fold`` / ``search_key`` / ``compare``
                / ``reverse_map``.
            text (str): The string to fold — required for the
                ``fold``, ``search_key`` and ``reverse_map`` modes.
            text_1 (str): First string of the ``compare`` mode.
            text_2 (str): Second string of the ``compare`` mode.
            folded_key (str): ``reverse_map`` only — the key the
                ``text`` supposedly folded to; recomputed and checked.

        Returns:
            Dict[str, Any]: The folding result (always including the
                mode) — the mode-specific payload, or a structured
                ``error`` payload for the one content-level failure
                (a ``reverse_map`` key that does not match).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "fold":
            return self._run_fold(self._validate_text(text, "text"))
        if mode == "search_key":
            return self._run_search_key(
                self._validate_text(text, "text")
            )
        if mode == "compare":
            first = self._validate_text(text_1, "text_1")
            second = self._validate_text(text_2, "text_2")
            return self._run_compare(first, second)
        return self._run_reverse_map(
            self._validate_text(text, "text"),
            self._validate_folded_key(folded_key),
        )

    # ------------------------------------------------------------------ #
    # The fold pipeline (pure functions)
    # ------------------------------------------------------------------ #

    @classmethod
    def _strip_marks(cls, text: str) -> str:
        """Stage 2 — drop Mn/Me combining characters."""
        return "".join(
            ch
            for ch in text
            if unicodedata.category(ch) not in cls.MARK_CATEGORIES
        )

    @classmethod
    def _apply_symbol_map(cls, text: str) -> str:
        """Stage 3 — the enumerated canonicalization table."""
        return "".join(cls.SYMBOL_MAP.get(ch, ch) for ch in text)

    @classmethod
    def _core_fold(cls, text: str) -> str:
        """Stages 1-4, before whitespace handling."""
        decomposed = unicodedata.normalize("NFKD", text)
        stripped = cls._strip_marks(decomposed)
        mapped = cls._apply_symbol_map(stripped)
        return mapped.casefold()

    @classmethod
    def fold_text(cls, text: str) -> str:
        """The complete five-stage fold — the stable canonical key."""
        return " ".join(cls._core_fold(text).split())

    @classmethod
    def key_text(cls, text: str) -> str:
        """The ``search_key`` fold — non-alnum runs squashed to ``-``.

        Alphanumeric is Unicode-aware (``str.isalnum``): Han
        ideographs, kana and Hangul Jamo count as word characters and
        survive intact; only separators / punctuation / symbols are
        squashed. Leading and trailing separators are trimmed, so any
        text without a single alphanumeric character — punctuation,
        symbols, whitespace, combining marks or emoji only — folds to
        the empty key.
        """
        folded = cls.fold_text(text)
        pieces: List[str] = []
        pending_separator = False
        for ch in folded:
            if ch.isalnum():
                if pending_separator and pieces:
                    pieces.append("-")
                pending_separator = False
                pieces.append(ch)
            else:
                pending_separator = True
        return "".join(pieces)

    # ------------------------------------------------------------------ #
    # Mode runners
    # ------------------------------------------------------------------ #

    def _run_fold(self, text: str) -> Dict[str, Any]:
        """``fold`` — one string through the full pipeline."""
        folded = self.fold_text(text)
        return {
            "mode": "fold",
            "text": text,
            "folded": folded,
            "is_empty_after_fold": folded == "",
            "pipeline": list(self.PIPELINE),
        }

    def _run_search_key(self, text: str) -> Dict[str, Any]:
        """``search_key`` — the index-equality key with its separator."""
        folded = self.fold_text(text)
        return {
            "mode": "search_key",
            "text": text,
            "search_key": self.key_text(text),
            "separator": "-",
            "folded": folded,
        }

    def _run_compare(self, text_1: str, text_2: str) -> Dict[str, Any]:
        """``compare`` — fold both strings and diff the KEYS."""
        key_1 = self.fold_text(text_1)
        key_2 = self.fold_text(text_2)
        differences = self._key_differences(key_1, key_2)
        return {
            "mode": "compare",
            "text_1": text_1,
            "text_2": text_2,
            "key1": key_1,
            "key2": key_2,
            "equal_after_fold": key_1 == key_2,
            "equal_after_search_key": self.key_text(text_1)
            == self.key_text(text_2),
            "len_key1": len(key_1),
            "len_key2": len(key_2),
            "differing_count": len(differences),
            "differing_positions": differences[
                : self.max_differing_positions
            ],
            "truncated": len(differences) > self.max_differing_positions,
        }

    @classmethod
    def _key_differences(
        cls, key_1: str, key_2: str
    ) -> List[Dict[str, Any]]:
        """Position-wise differences of two KEYS (0-based, both sides).

        Where one key is exhausted the missing side is ``None``.
        """
        differences: List[Dict[str, Any]] = []
        common = min(len(key_1), len(key_2))
        for index in range(common):
            if key_1[index] != key_2[index]:
                differences.append(
                    {
                        "position": index,
                        "key1_char": key_1[index],
                        "key2_char": key_2[index],
                    }
                )
        longer, label = (
            (key_1, "key1_char") if len(key_1) > len(key_2)
            else (key_2, "key2_char")
        )
        for index in range(common, len(longer)):
            entry: Dict[str, Any] = {"position": index}
            entry["key1_char"] = (
                longer[index] if label == "key1_char" else None
            )
            entry["key2_char"] = (
                longer[index] if label == "key2_char" else None
            )
            differences.append(entry)
        return differences

    def _run_reverse_map(
        self, text: str, folded_key: str
    ) -> Dict[str, Any]:
        """``reverse_map`` — the evidence of every transformation."""
        recomputed = self.fold_text(text)
        if recomputed != folded_key:
            return {
                "mode": "reverse_map",
                "text": text,
                "error": "key_mismatch",
                "message": (
                    "the provided folded_key does not match the "
                    "recomputed fold of text"
                ),
                "provided_key": folded_key,
                "expected_key": recomputed,
            }
        evidence, rule_counts = self._evidence(text)
        transformed = len(evidence)
        listed = evidence[: self.max_evidence_entries]
        return {
            "mode": "reverse_map",
            "text": text,
            "folded_key": folded_key,
            "matches": True,
            "evidence": listed,
            "evidence_count": transformed,
            "rule_counts": rule_counts,
            "unchanged_count": len(text) - transformed,
            "truncated": transformed > self.max_evidence_entries,
        }

    @classmethod
    def _fragment(cls, ch: str) -> str:
        """The folded fragment ONE original character contributes.

        Whitespace characters contribute the single collapsed space
        of stage 5 (a run of them collapses together); concatenating
        the fragments of a text and collapsing whitespace reproduces
        the full fold exactly — the invariant the evidence rests on.
        """
        if ch.isspace():
            return " "
        return cls._core_fold(ch)

    def _evidence(
        self, text: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Per-character mapping evidence for ``reverse_map``.

        Returns the list of entries for every TRANSFORMED original
        character (with the rule that fired) and per-rule counts.
        """
        evidence: List[Dict[str, Any]] = []
        rule_counts: Dict[str, int] = {}
        for index, ch in enumerate(text):
            rule = self._rule_for(ch)
            if rule is None:
                continue
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
            evidence.append(
                {
                    "index": index,
                    "original": ch,
                    "codepoint": f"U+{ord(ch):04X}",
                    "rule": rule,
                    "folded_to": self._fragment(ch),
                }
            )
        return evidence, rule_counts

    @classmethod
    def _rule_for(cls, ch: str) -> Optional[str]:
        """The first pipeline rule that transforms ``ch`` (or None).

        Checks run in the documented stage order (1 NFKD, 2 marks,
        3 map, 4 casefold, 5 whitespace), so a character reachable
        by an earlier stage is never attributed to a later one:
        NBSP and the ideographic space transform at stage 1 and
        report ``nfkd_decomposition``, while tabs / newlines (which
        NFKD passes through) report ``whitespace_collapsed``.
        """
        if unicodedata.normalize("NFKD", ch) != ch:
            return "nfkd_decomposition"
        if unicodedata.category(ch) in cls.MARK_CATEGORIES:
            return "mark_stripped"
        if ch in cls.SYMBOL_MAP:
            return "symbol_mapped"
        if ch.casefold() != ch:
            return "case_folded"
        if ch.isspace() and ch != " ":
            return "whitespace_collapsed"
        return None

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_fold_tool: {message}")

    def _validate_text(self, value: Any, label: str) -> str:
        """Validate a required text parameter (type, emptiness, size)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            self._invalid(
                f"{label} must be a non-empty string of at most "
                f"{self.max_text_chars:,} characters (got {value!r})"
            )
        if not value:
            self._invalid(f"{label} must be a non-empty string (got '')")
        if len(value) > self.max_text_chars:
            self._invalid(
                f"{label} exceeds the {self.max_text_chars:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    def _validate_folded_key(self, value: Any) -> str:
        """Validate the ``reverse_map`` key.

        The empty string is a legitimate folded key (a whitespace-only
        text folds to it), so only the type and size are checked.
        """
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            self._invalid(
                "folded_key must be a string of at most "
                f"{self.max_text_chars:,} characters (got {value!r})"
            )
        if len(value) > self.max_text_chars:
            self._invalid(
                f"folded_key exceeds the {self.max_text_chars:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value
