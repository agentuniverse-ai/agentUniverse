# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: reading_level_scorer.py

import re
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Words are Latin alphabetic runs (hyphens and apostrophes kept inside one
# token), digit runs, or single CJK characters (Han, kana, Hangul — each
# character approximates one word, the usual convention for unsegmented
# scripts).
_WORD_RE = re.compile(
    r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[0-9]+|[\u4e00-\u9fff\u3040-\u30ff"
    r"\uac00-\ud7af]")
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")

# Sentence terminators: ASCII . ! ? and their CJK counterparts.
_ASCII_TERMINATORS = ".!?"
_CJK_TERMINATORS = "\u3002\uff01\uff1f"  # 。！？

# Trailing word fragments that do NOT end a sentence when followed by a
# period. Multi-dot forms (e.g. "e.g", "p.m") are matched against the whole
# fragment back to the previous whitespace, so every dot inside them is
# guarded; single uppercase letters are treated as initials ("J. Smith").
_ABBREVIATIONS = frozenset((
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "inc",
    "ltd", "co", "corp", "dept", "univ", "assn", "approx", "fig", "figs",
    "eq", "eqs", "no", "nos", "vol", "pp", "al", "ca", "cf", "min", "max",
    "e.g", "i.e", "p.m", "a.m", "u.s", "u.k",
))

# Share of CJK characters above which syllable formulas are skipped: they
# are defined for English (Latin) words only.
_CJK_RATIO_THRESHOLD = 0.3


class ReadingLevelScorer(DocProcessor):
    """Stamp classic text-readability metrics into document metadata.

        Knowledge corpora mix audiences: installation notes written for
        anyone, regulatory filings written for specialists, children's
        stories, academic abstracts. Retrieval quality improves when the
        expected reading level of each document is known at insertion time —
        agents can prefer answers phrased at the user's level, dashboards can
        surface the mix, and downstream processors can route kindergarten
        material away from the legal corpus. This processor computes the
        three classic readability formulas for every document and stamps
        them into ``metadata[reading_level]``:

        * Flesch Reading Ease (higher = easier):
          ``206.835 - 1.015 * words/sentences - 84.6 * syllables/words``
        * Flesch-Kincaid Grade (US school grade):
          ``0.39 * words/sentences + 11.8 * syllables/words - 15.59``
        * Gunning-Fog index (years of education):
          ``0.4 * (words/sentences + 100 * complex_words/words)`` where a
          complex word has >= 3 syllables; capitalized tokens outside
          sentence-initial position are excluded as proper-noun-ish, and a
          hyphenated compound counts as complex only when one of its parts
          alone reaches 3 syllables.

        The analysis is deliberately conservative and dependency-free:

        * sentences end at ``. ! ?`` (followed by whitespace or end of text)
          or at CJK ``。！？`` (no trailing space required); a period is
          ignored when its preceding fragment is a known abbreviation
          (``Mr.``, ``etc.`` ...) or a single uppercase initial, and runs of
          terminators (``!!!``) end one sentence;
        * syllables use the standard heuristic on vowel groups with
          silent-terminal-e (kept for ``-le`` as in ``table``) and silent
          ``-ed`` (kept after t/d as in ``wanted``); every token containing
          letters counts as at least one syllable. The heuristic is exact
          for regular words (``reading`` = 2) but approximates irregular
          ones (``algorithm`` counts 3, not 4) — an accepted trade-off of
          all stdlib readability implementations;
        * for predominantly non-Latin text (CJK characters > 30% of
          letters) syllable formulas do not apply: they are set to None,
          ``metadata[note_key]`` records ``"syllable formulas apply to
          English text only"`` and sentence/word statistics are still
          stamped.

        Text that has no words or no sentences (blank input) yields zero
        counts with all three formula fields set to None rather than a
        fabricated score.

        By default the processor only stamps metadata. Setting ``min_grade``
        and/or ``max_grade`` switches on a filter mode that drops documents
        whose Flesch-Kincaid grade falls outside the inclusive range —
        documents without a computable grade (blank or non-Latin text) are
        always kept, since no evidence exists to reject them.

        This component is about *how hard* a text is to read. It is distinct
        from ``TextQualityScorer`` (#3500), which measures *content quality
        ratios* (signal vs. boilerplate in the text), and from tool-side
        statistics components that answer on demand: readability formulas
        are a separate, classic metric family, computed here as a doc
        processor so the metrics travel with the document into the store.

        Everything is pure Python, deterministic and offline: identical
        inputs always produce identical metadata, with no model calls, no
        randomness and no per-process hash salt.

        Attributes:
            min_grade: Optional minimum Flesch-Kincaid grade for the filter
                mode; None (default) disables the lower bound.
            max_grade: Optional maximum Flesch-Kincaid grade for the filter
                mode; None (default) disables the upper bound.
            reading_level_key: Metadata key the metrics dictionary is
                written to; an empty value disables stamping.
            note_key: Metadata key the non-Latin skip note is written to;
                an empty value disables the note.
        """

    min_grade: Optional[float] = None
    max_grade: Optional[float] = None
    reading_level_key: str = "reading_level"
    note_key: str = "readability_note"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp readability metrics into every document, then filter.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; readability depends only on the
                documents' own text).

        Returns:
            List[Document]: All documents when no grade bounds are set;
            otherwise the documents whose Flesch-Kincaid grade lies within
            [min_grade, max_grade], plus every document without a
            computable grade. Order is preserved.
        """
        kept: List[Document] = []
        for doc in origin_docs:
            level = self._analyze(doc.text or "")
            non_latin = level.pop("_non_latin")
            if self.reading_level_key:
                self._stamp(doc, self.reading_level_key, level)
            if self.note_key and non_latin:
                self._stamp(doc, self.note_key,
                            "syllable formulas apply to English text only")
            grade = level["flesch_kincaid_grade"]
            if (grade is not None and self.min_grade is not None
                    and grade < self.min_grade) or (
                    grade is not None and self.max_grade is not None
                    and grade > self.max_grade):
                continue
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Analysis helpers
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> dict:
        """Compute the full metrics dictionary for one text.

        Args:
            text: Document text (None/empty treated as blank).

        Returns:
            dict: ``flesch_reading_ease`` / ``flesch_kincaid_grade`` /
            ``gunning_fog`` (floats rounded to 2 decimals, or None when not
            computable), ``word_count`` / ``sentence_count`` /
            ``syllable_count`` integers, plus a private ``_non_latin``
            flag consumed by :meth:`_process_docs`.
        """
        text = text or ""
        sentences = self._split_sentences(text)
        tokens: List[str] = []
        sentence_initial: List[bool] = []
        for sentence in sentences:
            sentence_tokens = _WORD_RE.findall(sentence)
            tokens.extend(sentence_tokens)
            sentence_initial.extend(
                pos == 0 for pos, _ in enumerate(sentence_tokens))

        word_count = len(tokens)
        syllable_count = sum(self._token_syllables(t) for t in tokens)
        complex_count = sum(
            1 for token, initial in zip(tokens, sentence_initial)
            if self._is_complex(token, initial))

        non_latin = self._cjk_ratio(text) > _CJK_RATIO_THRESHOLD
        level = {
            "flesch_reading_ease": None,
            "flesch_kincaid_grade": None,
            "gunning_fog": None,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "syllable_count": syllable_count,
            "_non_latin": non_latin,
        }
        if non_latin or word_count == 0 or not sentences:
            return level

        words_per_sentence = word_count / len(sentences)
        syllables_per_word = syllable_count / word_count
        level["flesch_reading_ease"] = round(
            206.835 - 1.015 * words_per_sentence
            - 84.6 * syllables_per_word, 2)
        level["flesch_kincaid_grade"] = round(
            0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59, 2)
        level["gunning_fog"] = round(
            0.4 * (words_per_sentence + 100.0 * complex_count / word_count),
            2)
        return level

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences with conservative terminator rules.

        ASCII ``.!?`` ends a sentence only when followed by whitespace or
        end of text (so ``3.14`` never splits); a period is additionally
        ignored when its preceding fragment is a known abbreviation or a
        single uppercase initial. CJK ``。！？`` end a sentence
        unconditionally. Runs of ASCII terminators collapse into one
        boundary.

        Args:
            text: Raw document text.

        Returns:
            List[str]: Non-blank sentence strings.
        """
        sentences: List[str] = []
        start = 0
        pos = 0
        length = len(text)
        while pos < length:
            char = text[pos]
            if char in _CJK_TERMINATORS:
                sentences.append(text[start:pos + 1])
                start = pos + 1
                pos += 1
            elif char in _ASCII_TERMINATORS:
                end = pos
                while end < length and text[end] in _ASCII_TERMINATORS:
                    end += 1
                if (end >= length or text[end].isspace()) and not (
                        char == "." and ReadingLevelScorer._is_abbreviation(
                            text, pos)):
                    sentences.append(text[start:end])
                    start = end
                pos = end
            else:
                pos += 1
        if text[start:].strip():
            sentences.append(text[start:])
        return [s for s in sentences if s.strip()]

    @staticmethod
    def _is_abbreviation(text: str, dot_pos: int) -> bool:
        """Report whether the period at ``dot_pos`` belongs to an
        abbreviation rather than ending a sentence.

        The fragment back to the previous whitespace is matched (encoding
        its dots) against the abbreviation list; a single uppercase letter
        counts as an initial.

        Args:
            text: Full text being split.
            dot_pos: Index of the period under consideration.

        Returns:
            bool: True when the period must not end a sentence.
        """
        start = dot_pos
        while start > 0 and not text[start - 1].isspace():
            start -= 1
        fragment = text[start:dot_pos]
        if fragment.lower() in _ABBREVIATIONS:
            return True
        return len(fragment) == 1 and fragment.isalpha() and \
            fragment.isupper()

    @staticmethod
    def _token_syllables(token: str) -> int:
        """Count syllables in one token with the standard heuristic.

        Vowel groups (``aeiouy`` runs) are counted, a silent terminal ``e``
        is subtracted (kept for ``-le`` as in ``table``) and a silent
        ``-ed`` is subtracted unless it follows ``t``/``d`` (``wanted``
        keeps two). Tokens without letters (digits, CJK characters) count
        zero; a lettered token always counts at least one syllable.

        Args:
            token: One word token from the tokenizer.

        Returns:
            int: Syllable estimate (>= 1 for lettered tokens).
        """
        letters = re.sub(r"[^a-zA-Z]", "", token).lower()
        if not letters:
            return 0
        count = len(_VOWEL_GROUP_RE.findall(letters))
        if count > 1:
            if letters.endswith("ed") and len(letters) > 2 and \
                    letters[-3] not in "td":
                count -= 1
            elif letters.endswith("e") and not letters.endswith("le"):
                count -= 1
        return max(count, 1)

    def _is_complex(self, token: str, sentence_initial: bool) -> bool:
        """Report whether a token is a Gunning-Fog complex word.

        Complex means >= 3 syllables, with two classic exclusions:
        capitalized tokens outside sentence-initial position are treated as
        proper-noun-ish and never complex, and a hyphenated compound is
        complex only when one of its parts alone reaches 3 syllables (so
        ``state-of-the-art`` stays simple while
        ``computer-communication-application`` counts).

        Args:
            token: One word token from the tokenizer.
            sentence_initial: Whether the token starts its sentence.

        Returns:
            bool: True when the token counts as a complex word.
        """
        if not sentence_initial and token[:1].isupper():
            return False
        return any(self._token_syllables(part) >= 3
                   for part in token.split("-") if part)

    @staticmethod
    def _cjk_ratio(text: str) -> float:
        """Compute the share of CJK characters among all letters.

        Args:
            text: Raw document text.

        Returns:
            float: Ratio in [0, 1]; 0.0 for text without any letters.
        """
        cjk = len(_CJK_RE.findall(text))
        latin = len(_LATIN_RE.findall(text))
        if cjk + latin == 0:
            return 0.0
        return cjk / (cjk + latin)

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'ReadingLevelScorer':
        """Initialize and validate the scorer from component configuration.

        Validation happens eagerly at load time: a typo like
        ``min_grade: 'six'`` must fail at startup, not silently disable the
        filter for a whole ingestion run.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ReadingLevelScorer: The initialized instance.

        Raises:
            ValueError: On invalid parameter values or an empty grade range.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        for attr in ("min_grade", "max_grade"):
            value = getattr(doc_processor_configer, attr, None) \
                if hasattr(doc_processor_configer, attr) else None
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{attr} must be a number")
            setattr(self, attr, float(value))

        if self.min_grade is not None and self.max_grade is not None and \
                self.min_grade > self.max_grade:
            raise ValueError(
                f"min_grade ({self.min_grade}) must not exceed max_grade "
                f"({self.max_grade})")

        for attr in ("reading_level_key", "note_key"):
            value = getattr(doc_processor_configer, attr, None) \
                if hasattr(doc_processor_configer, attr) else None
            if value is None:
                continue
            if not isinstance(value, str):
                raise ValueError(f"{attr} must be a string")
            setattr(self, attr, value)

        return self
