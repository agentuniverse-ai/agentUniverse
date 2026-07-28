# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: profanity_filter.py

"""
Profanity filter — a knowledge post-processing DocProcessor.

Filters, masks, or flags recalled documents that contain profanity based on a
built-in English word list. Useful for knowledge bases that serve end-user
facing agents where offensive language should be blocked, redacted, or at
least surfaced for review before the content reaches the model or the user.

Three actions are supported:

- **drop**   — discard any document whose profanity ratio meets ``threshold``;
- **mask**   — replace every matched profane word with ``replacement`` (e.g.
               ``***``) and keep the document;
- **redact** — leave the text untouched but stamp a ``profanity_summary`` into
               the document metadata so downstream stages can decide.

The detector is deterministic, case-insensitive, and dependency-free. It
matches whole words only (so "class" never matches "ass") and tolerates a few
common leet/obfuscation substitutions (``@`` -> ``a``, ``$`` -> ``s``,
``0`` -> ``o``, ``1``/``!`` -> ``i``) so trivial evasions such as ``b@dword``
are still caught. Custom terms can be added via ``extra_words``.

Addresses #248 (knowledge post-processing components). Structurally it mirrors
``LanguageFilter`` (a filter-style post-processor with a conservative keep
policy for borderline input) and is distinct from
``SensitiveDataRedactor``, which targets structured PII rather than offensive
vocabulary.
"""

import logging
import re
from typing import Dict, List, Optional, Set

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# A compact built-in list of common English profanity / slurs. It is not
# exhaustive by design — operators who need broader coverage can extend it via
# ``extra_words``. Kept lowercase; matching is case-insensitive.
_DEFAULT_PROFANITY_WORDS: Set[str] = {
    # generic strong profanity
    "ass", "asshole", "bastard", "bitch", "crap", "damn", "dick",
    "fuck", "fucker", "fucking", "goddamn", "hell", "jackass",
    "piss", "shit", "bullshit", "prick", "bollocks", "wanker",
    "arse", "arsehole", "twat", "cunt", "cock", "dickhead",
    # hateful / slur terms (kept so they are caught and reported)
    "nigger", "nigga", "faggot", "fag", "retard", "dyke", "tranny",
    "chink", "spic", "kike", "paki", "wetback",
}

# Leet-speak normalisation table used before matching. Keys are the obfuscated
# characters, values are the plain characters they commonly stand in for.
_LEET_MAP = {
    "@": "a", "4": "a",
    "$": "s", "5": "s",
    "0": "o",
    "1": "i", "!": "i",
    "3": "e",
    "7": "t",
    "+": "t",
}

# Pre-compiled character class of all leet substitutes for fast normalisation.
_LEET_CHARS = "".join(re.escape(ch) for ch in _LEET_MAP)


def _normalise_token(token: str) -> str:
    """Normalise a token by collapsing common leet substitutions to lowercase.

    For example ``b@dw0rd`` -> ``badword``. Non-substituted characters are
    lowercased and any character outside ``[a-z]`` after normalisation is
    dropped, which lets the whole-word match ignore punctuation that the
    tokenizer has already split on.
    """
    out_chars = []
    for ch in token:
        lower = ch.lower()
        if lower in _LEET_MAP:
            out_chars.append(_LEET_MAP[lower])
        elif "a" <= lower <= "z":
            out_chars.append(lower)
        # anything else is dropped
    return "".join(out_chars)


class ProfanityFilter(DocProcessor):
    """Filter, mask, or flag documents containing profanity.

    Attributes:
        action: How to handle profane content. One of:
            - ``"drop"``   — remove documents whose profanity ratio is at
                             least ``threshold``;
            - ``"mask"``   — replace each matched profane word with
                             ``replacement`` (document is kept);
            - ``"redact"`` — keep the text unchanged but write a
                             ``profanity_summary`` into metadata.
            Default ``"mask"``.
        replacement: Text substituted for each profane match when
            ``action == "mask"``. Default ``"***"``.
        threshold: Profanity ratio in ``[0.0, 1.0]`` above which a document is
            considered offensive. The ratio is ``profane_word_count /
            total_word_count``. Only consulted by the ``drop`` action (and is
            recorded in the summary for the other actions). Default ``0.05``
            — a document is dropped once 5% of its tokens are profane.
        extra_words: Additional profane terms to merge with the built-in list.
            Matching is case-insensitive and whole-word.
        whole_word_only: When ``True`` (default) only whole tokens are matched,
            so "class" never triggers on the substring "ass". Set ``False`` to
            fall back to naive substring matching (faster but produces false
            positives — rarely what you want).
        summary_key: Metadata key under which a per-document
            ``{words: [...], count: int, ratio: float}`` summary is written.
            Set to ``None`` / empty to omit the summary.
    """

    action: str = "mask"
    replacement: str = "***"
    threshold: float = 0.05
    extra_words: Set[str] = set()
    whole_word_only: bool = True
    summary_key: str = "profanity_summary"

    # The effective word set, built lazily from the default list + extra_words.
    _word_set: Set[str] = set()

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Process documents according to the configured ``action``."""
        if not origin_docs:
            return []

        words = self._effective_words()

        result: List[Document] = []
        dropped = 0
        masked = 0
        for doc in origin_docs:
            text = doc.text or ""

            if self.whole_word_only:
                matches = self._find_whole_word_matches(text, words)
            else:
                matches = self._find_substring_matches(text, words)

            ratio, count = self._compute_ratio(text, matches)

            summary = {
                "words": sorted({m["matched"] for m in matches}),
                "count": count,
                "ratio": round(ratio, 6),
                "action": self.action,
            }

            if self.action == "drop":
                if ratio >= self.threshold:
                    dropped += 1
                    # Document is discarded — do not stamp summary.
                    continue
                # Kept: optionally stamp summary for downstream visibility.
                result.append(self._stamp(doc, summary))
            elif self.action == "mask":
                if count > 0:
                    new_text = self._apply_mask(text, matches)
                    masked += 1
                    result.append(self._with_text(doc, new_text, summary))
                else:
                    result.append(self._stamp(doc, summary))
            elif self.action == "redact":
                result.append(self._stamp(doc, summary))
            else:
                raise ValueError(
                    f"Invalid action: {self.action!r}. "
                    f"Must be one of 'drop', 'mask', 'redact'."
                )

        if dropped or masked:
            logger.debug(
                "ProfanityFilter: action=%s dropped=%d masked=%d of %d docs",
                self.action, dropped, masked, len(origin_docs),
            )
        return result

    # ------------------------------------------------------------------ #
    # Matching helpers
    # ------------------------------------------------------------------ #
    def _effective_words(self) -> Set[str]:
        """Return the active profanity word set (built-in + extra)."""
        return _DEFAULT_PROFANITY_WORDS | {w.lower() for w in self.extra_words}

    def _find_whole_word_matches(self, text: str,
                                 words: Set[str]) -> List[Dict[str, object]]:
        """Find whole-word profanity matches, tolerating leet substitutions.

        Returns a list of ``{"start", "end", "matched"}`` dicts. ``start``/
        ``end`` are indices into the *original* ``text`` so masking can replace
        the exact span the user saw. ``matched`` is the normalised profane
        word found.
        """
        matches: List[Dict[str, object]] = []
        # Tokenize on word boundaries while keeping original spans.
        for m in re.finditer(r"[A-Za-z0-9@$_!3+7]+", text):
            token = m.group(0)
            normalised = _normalise_token(token)
            if normalised and normalised in words:
                matches.append({
                    "start": m.start(),
                    "end": m.end(),
                    "matched": normalised,
                })
        return matches

    def _find_substring_matches(self, text: str,
                                words: Set[str]) -> List[Dict[str, object]]:
        """Naive case-insensitive substring matching (whole_word_only=False).

        Matches may overlap; earlier matches win to avoid double-counting.
        """
        matches: List[Dict[str, object]] = []
        lower = text.lower()
        occupied = [False] * len(text)
        # Search longer words first so "asshole" is found before "ass".
        for word in sorted(words, key=len, reverse=True):
            if not word:
                continue
            start = lower.find(word)
            while start != -1:
                end = start + len(word)
                if not any(occupied[start:end]):
                    matches.append({
                        "start": start,
                        "end": end,
                        "matched": word,
                    })
                    for i in range(start, end):
                        occupied[i] = True
                start = lower.find(word, start + 1)
        # Restore original (left-to-right) order regardless of search order.
        matches.sort(key=lambda d: d["start"])
        return matches

    def _compute_ratio(self, text: str,
                       matches: List[Dict[str, object]]) -> tuple:
        """Return ``(ratio, count)`` for ``text`` given ``matches``.

        ``ratio = count / total_word_count`` and is clamped to ``[0.0, 1.0]``.
        A "word" here is any maximal run of alphanumerics; empty text has a
        ratio of ``0.0``.
        """
        if not text:
            return 0.0, 0
        total = len(re.findall(r"\w+", text))
        if total == 0:
            return 0.0, 0
        count = len(matches)
        ratio = count / total
        return max(0.0, min(1.0, ratio)), count

    def _apply_mask(self, text: str,
                    matches: List[Dict[str, object]]) -> str:
        """Replace each matched span in ``text`` with ``self.replacement``.

        Iterates from the end backwards so earlier indices stay valid.
        """
        out = text
        for m in sorted(matches, key=lambda d: d["start"], reverse=True):
            out = out[:m["start"]] + self.replacement + out[m["end"]:]
        return out

    # ------------------------------------------------------------------ #
    # Document mutation helpers
    # ------------------------------------------------------------------ #
    def _stamp(self, doc: Document, summary: Dict[str, object]) -> Document:
        """Return ``doc`` with the profanity summary stamped into metadata."""
        if not self.summary_key:
            return doc
        meta = dict(doc.metadata or {})
        meta[self.summary_key] = summary
        return Document(text=doc.text, metadata=meta)

    def _with_text(self, doc: Document, new_text: str,
                   summary: Dict[str, object]) -> Document:
        """Return a copy of ``doc`` with replaced text and stamped summary."""
        meta = dict(doc.metadata or {})
        if self.summary_key:
            meta[self.summary_key] = summary
        return Document(text=new_text, metadata=meta)

    # ------------------------------------------------------------------ #
    # Config initialisation
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) -> "ProfanityFilter":
        """Initialise the filter from its component configuration.

        Validates ``action`` and clamps ``threshold`` to ``[0.0, 1.0]``.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "action"):
            self.action = doc_processor_configer.action
            if self.action not in {"drop", "mask", "redact"}:
                raise ValueError(
                    f"Invalid action: {self.action!r}. "
                    f"Must be one of 'drop', 'mask', 'redact'."
                )

        if hasattr(doc_processor_configer, "replacement"):
            self.replacement = doc_processor_configer.replacement

        if hasattr(doc_processor_configer, "threshold"):
            self.threshold = doc_processor_configer.threshold
            if not 0.0 <= float(self.threshold) <= 1.0:
                raise ValueError(
                    f"threshold must be in [0.0, 1.0], got {self.threshold}."
                )

        if hasattr(doc_processor_configer, "extra_words"):
            extra = doc_processor_configer.extra_words
            if isinstance(extra, (list, tuple, set)):
                self.extra_words = {str(w).lower() for w in extra}
            else:
                raise ValueError(
                    "extra_words must be a list/tuple/set of strings."
                )

        if hasattr(doc_processor_configer, "whole_word_only"):
            self.whole_word_only = bool(doc_processor_configer.whole_word_only)

        if hasattr(doc_processor_configer, "summary_key"):
            self.summary_key = doc_processor_configer.summary_key

        return self
