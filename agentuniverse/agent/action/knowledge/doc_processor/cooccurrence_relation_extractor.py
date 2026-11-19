# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: cooccurrence_relation_extractor.py

import logging
import re
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

# Sentence terminators. The CJK/full-width forms always end a window; the
# ASCII period only does so when the abbreviation guard below passes.
_SENTENCE_TERMINATORS = "。！？!?"

# Abbreviations whose trailing period must NOT be read as a sentence end
# ("Boeing Inc. announced", "Mr. Li chairs ..."). Matched case-insensitively
# against the alphabetic run immediately preceding the period.
_ABBREVIATIONS = frozenset({
    "inc", "ltd", "llc", "plc", "corp", "co", "dept", "est", "approx",
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc",
    "eg", "ie", "al", "no", "vol", "fig", "ave", "blvd", "rd",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep",
    "oct", "nov", "dec", "mon", "tue", "wed", "thu", "fri", "sat", "sun",
})

# Capitalized Latin sequences for auto_capitalized mode: one or more
# words that each start with an uppercase letter. Two word forms are
# recognized: dotted initials runs ("U.S.", "J.P.") which keep their
# trailing period, and ordinary words of letters, digits, ampersands,
# apostrophes and hyphens in which internal periods require another
# token character to follow. A sentence-final period can therefore
# never glue the next sentence's names onto a candidate ("TSMC. U.S.
# Army" yields "TSMC" and "U.S. Army"), while lowercase words simply
# break the sequence.
_CAPITALIZED_WORD = (
    r"[A-Z](?:\.[A-Z])+\.?"
    r"|[A-Z][A-Za-z0-9&'\-]*"
    r"(?:\.(?=[A-Za-z0-9&'\-])[A-Za-z0-9&'\-]+)*")
_CAPITALIZED_TERM_RE = re.compile(
    "(?:" + _CAPITALIZED_WORD + r")(?:[ \t]+(?:" + _CAPITALIZED_WORD +
    r"))*")

# Words removed from the head of auto-detected candidates (and rejecting
# single-word candidates made only of them). These are the common
# sentence-initial function words that capitalized-sequence detection
# would otherwise lift as "entities". Kept deliberately free of words
# that open real proper nouns ("New", "First", "United", ...).
_DEFAULT_STOPWORDS = frozenset({
    "the", "a", "an", "and", "but", "or", "nor", "for", "yet", "so",
    "because", "although", "though", "if", "while", "when", "where",
    "why", "how", "what", "who", "whom", "whose", "which", "that",
    "this", "these", "those", "there", "here", "we", "you", "they",
    "he", "she", "it", "us", "them", "him", "her", "me", "my", "your",
    "our", "their", "its", "his", "in", "on", "at", "by", "to", "of",
    "with", "from", "into", "onto", "over", "under", "above", "below",
    "between", "among", "through", "during", "before", "after", "since",
    "until", "upon", "about", "against", "off", "out", "up", "down",
    "again", "then", "once", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "not", "only", "own", "same",
    "than", "too", "very", "can", "will", "just", "should", "now",
    "however", "therefore", "moreover", "furthermore", "meanwhile",
    "instead", "also", "thus", "hence", "otherwise", "nevertheless",
    "nonetheless", "finally", "today", "yesterday", "tomorrow",
    "according", "said", "says",
})

# Paragraph boundary: a blank line (newline, optional whitespace,
# newline).
_PARAGRAPH_RE = re.compile(r"\n[ \t\r]*\n")


class CooccurrenceRelationExtractor(DocProcessor):
    """Extract entity co-occurrence relations into document metadata.

    Knowledge-graph builders for supply-chain or financial corpora need
    edges, not just nodes: which suppliers, companies and products are
    talked about *together* is often the strongest signal of a real-world
    relationship, and it can be measured without any model. This
    processor — addressing the knowledge-extraction direction of issue
    #258 — segments each document into windows (sentences by default,
    paragraphs optionally), collects the distinct tracked terms present
    in every window, and turns each unordered pair of co-present terms
    into a relation whose ``count`` is the number of windows the pair
    was observed in together.

    Tracked terms come from two sources, usable alone or combined:

    1. ``terms`` — an explicit list of entity names, optionally enriched
       by ``alias_map`` which folds surface forms onto canonical names
       ({"AAPL": "Apple"}); matching is case-insensitive with
       Latin-alphanumeric boundary checks, so "Apple" matches inside
       neither "Pineapple" nor "Apples";
    2. ``auto_capitalized`` — auto-detection of Latin capitalized
       sequences ("Boeing", "U.S. Army"), with sentence-start noise
       removed by a stoplist (configurable via ``stopwords``), trailing
       possessives stripped ("Apple's" -> "Apple") and sentence-final
       periods dropped.

    Sentence segmentation splits on ASCII and CJK terminators (``.!?``
    and ``。！？``) with an abbreviation guard: a period preceded by a
    known abbreviation ("Inc.", "Ltd."), a single uppercase initial
    ("J. P. Morgan") or digits on both sides ("3.14") does not end a
    sentence. Every pair found in a window is counted at most once per
    window no matter how often its members repeat, and terms never
    co-occur with themselves.

    Results are stamped into copied document metadata as
    ``metadata['relations']`` — a list of ``{source, target, count}``
    dicts sorted by count descending then name pair, capped at
    ``max_relations`` — and ``metadata['relation_graph']`` — an adjacency
    mapping ``{term: {other_term: count}}`` covering every relation that
    passed ``min_count``. Text, id and all other metadata fields are
    never modified, and the whole pipeline is pure Python, offline and
    deterministic.

    Attributes:
        terms: Tracked entity names; each is canonical under its own
            spelling (case-insensitively matched).
        alias_map: Mapping of alias surface form -> canonical term name;
            aliases are matched like terms and folded onto their
            canonical target. Alias entries take precedence when a
            surface collides with a ``terms`` entry.
        auto_capitalized: When true, Latin capitalized sequences are
            auto-detected as terms in addition to ``terms``/``alias_map``.
        window: Co-occurrence window — 'sentence' (default) or
            'paragraph' (blank-line separated blocks).
        max_relations: Maximum number of relations kept in the stamped
            relations list; must be >= 1, default 50.
        min_count: Minimum co-occurrence count for a relation to be
            kept anywhere; must be >= 1, default 1.
        stopwords: Extra stop words appended to the built-in stoplist
            used to trim auto-detected candidates; compared
            case-insensitively.
    """

    terms: Optional[List[str]] = None
    alias_map: Optional[Dict[str, str]] = None
    auto_capitalized: bool = False
    window: str = "sentence"
    max_relations: int = 50
    min_count: int = 1
    stopwords: Optional[List[str]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.terms is None:
            self.terms = []
        if self.alias_map is None:
            self.alias_map = {}
        if self.stopwords is None:
            self.stopwords = []

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp co-occurrence relations into every document's metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, each carrying
            'relations' and 'relation_graph' in a copied metadata
            mapping.
        """
        if not origin_docs:
            return []

        if not self.terms and not self.auto_capitalized:
            logger.warning(
                "CooccurrenceRelationExtractor has neither terms nor "
                "auto_capitalized configured; no relation can be found")
            for doc in origin_docs:
                self._stamp(doc, {})
            return list(origin_docs)

        surface_map = self._build_surface_map()
        surface_patterns = self._compile_surface_patterns(surface_map)

        for doc in origin_docs:
            counts: Dict[Tuple[str, str], int] = {}
            for window_text in self._split_windows(doc.text or ""):
                present = self._terms_in_window(window_text, surface_map,
                                                surface_patterns)
                # Each unordered pair of distinct canonical terms is
                # counted exactly once per window, however often its
                # members (or their aliases) repeat inside it.
                for left, right in combinations(sorted(present), 2):
                    counts[(left, right)] = counts.get((left, right), 0) + 1
            self._stamp(doc, counts)
            logger.debug(
                "Extracted %d co-occurrence relations from document %s",
                len(counts), doc.id)
        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Term detection
    # ------------------------------------------------------------------ #

    def _build_surface_map(self) -> Dict[str, str]:
        """Map every searchable surface form to its canonical term.

        Terms map to themselves; alias_map entries then override any
        lowercase collision, since an explicit alias is the stronger
        user intent. Keys are lowercased so configured-term matching
        stays case-insensitive.

        Returns:
            Dict[str, str]: lowercased surface form -> canonical name.
        """
        surface_map: Dict[str, str] = {}
        for term in self.terms:
            # setdefault: case-variant duplicates fold onto the first
            # spelling encountered.
            surface_map.setdefault(term.lower(), term)
        for alias, canonical in self.alias_map.items():
            surface_map[alias.lower()] = canonical
        return surface_map

    @staticmethod
    def _compile_surface_patterns(
            surface_map: Dict[str, str]) -> Dict[str, re.Pattern]:
        """Compile one boundary-guarded regex per configured surface form.

        The lookarounds reject matches glued to Latin letters or digits
        ("Pineapple", "Apples") while still allowing adjacency to CJK
        characters, which carry no spaces.

        Args:
            surface_map: Lowercased surface form -> canonical name.

        Returns:
            Dict[str, re.Pattern]: lowercased surface form -> compiled
            case-insensitive pattern.
        """
        return {
            surface: re.compile(
                r"(?<![A-Za-z0-9])" + re.escape(surface) +
                r"(?![A-Za-z0-9])", re.IGNORECASE)
            for surface in surface_map
        }

    def _terms_in_window(self, window_text: str,
                         surface_map: Dict[str, str],
                         surface_patterns: Dict[str, re.Pattern]) -> Set[str]:
        """Collect the distinct canonical terms present in one window.

        Args:
            window_text: Text of the sentence or paragraph window.
            surface_map: Lowercased surface form -> canonical name.
            surface_patterns: Compiled matching patterns per surface.

        Returns:
            Set[str]: Canonical names of every tracked term detected in
            the window.
        """
        found: Set[str] = set()
        for surface, pattern in surface_patterns.items():
            if pattern.search(window_text):
                found.add(surface_map[surface])
        if self.auto_capitalized:
            stopset = self._stopword_set()
            for match in _CAPITALIZED_TERM_RE.finditer(window_text):
                candidate = self._clean_auto_candidate(match.group(0),
                                                       stopset)
                if not candidate:
                    continue
                # alias_map folds auto-detected surfaces too, so a
                # detected "AAPL" still lands on "Apple" when mapped.
                canonical = surface_map.get(candidate.lower(), candidate)
                found.add(canonical)
        return found

    def _stopword_set(self) -> frozenset:
        """Merge the built-in stoplist with the configured extras.

        Returns:
            frozenset: Lowercased stop words.
        """
        return _DEFAULT_STOPWORDS | {word.lower() for word in self.stopwords}

    @staticmethod
    def _clean_auto_candidate(raw: str, stopset: frozenset) -> Optional[str]:
        """Normalize one capitalized-sequence match into a term name.

        Strips trailing possessives ("Apple's" -> "Apple") and
        sentence-final periods ("Boeing." -> "Boeing"), then drops the
        leading stoplisted words that sentence capitalization injects
        ("The Boeing Company" -> "Boeing Company"; a bare "The" is
        rejected entirely).

        Args:
            raw: Matched capitalized sequence.
            stopset: Lowercased stop words to trim from the head.

        Returns:
            Optional[str]: Cleaned candidate, or None when nothing
            meaningful survives.
        """
        candidate = raw
        if candidate.endswith("'s"):
            candidate = candidate[:-2]
        candidate = candidate.rstrip(".")
        words = [word for word in candidate.split() if word]
        while words and words[0].lower().strip(".,'&-") in stopset:
            words.pop(0)
        candidate = " ".join(words).strip("'&- ").strip()
        if len(candidate) < 2 or not re.search(r"[A-Za-z]", candidate):
            return None
        return candidate

    # ------------------------------------------------------------------ #
    # Window segmentation
    # ------------------------------------------------------------------ #

    def _split_windows(self, text: str) -> List[str]:
        """Cut document text into co-occurrence windows.

        Args:
            text: Document text.

        Returns:
            List[str]: Non-blank window texts, in document order.
        """
        if self.window == "paragraph":
            parts = _PARAGRAPH_RE.split(text)
        else:
            parts = self._split_sentences(text)
        return [part.strip() for part in parts if part and part.strip()]

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences with an abbreviation guard.

        ASCII and CJK terminators ('.!?。！？') end a sentence, except a
        period that directly follows an abbreviation ("Inc."), a single
        uppercase initial ("J. P. Morgan"), another period (ellipsis) or
        sits between digits ("3.14").

        Args:
            text: Document text.

        Returns:
            List[str]: Non-blank sentence texts, in document order.
        """
        bounds = []
        length = len(text)
        for idx, char in enumerate(text):
            if char in _SENTENCE_TERMINATORS:
                bounds.append(idx + 1)
            elif char == "." and CooccurrenceRelationExtractor \
                    ._period_ends_sentence(text, idx):
                bounds.append(idx + 1)

        sentences = []
        start = 0
        for bound in bounds + [length]:
            sentence = text[start:bound]
            if sentence.strip():
                sentences.append(sentence)
            start = bound
        return sentences

    @staticmethod
    def _period_ends_sentence(text: str, idx: int) -> bool:
        """Decide whether the period at ``idx`` terminates a sentence.

        Args:
            text: Full document text.
            idx: Index of the period character.

        Returns:
            bool: True when the period ends a sentence.
        """
        length = len(text)
        prev_char = text[idx - 1] if idx > 0 else ""
        next_char = text[idx + 1] if idx + 1 < length else ""

        # Ellipsis: any period glued to another period continues it.
        if prev_char == "." or next_char == ".":
            return False
        # Decimal numbers ("3.14", "12.5%").
        if prev_char.isdigit() and next_char.isdigit():
            return False

        # Alphabetic run immediately before the period. Note isalpha()
        # also covers CJK runs; those never match the abbreviation
        # rules below and fall through to "ends sentence".
        cursor = idx - 1
        while cursor >= 0 and text[cursor].isalpha():
            cursor -= 1
        word = text[cursor + 1:idx]
        if not word:
            return True
        if word.lower() in _ABBREVIATIONS:
            return False
        if len(word) == 1 and word.isupper():
            return False
        return True

    # ------------------------------------------------------------------ #
    # Result stamping
    # ------------------------------------------------------------------ #

    def _stamp(self, doc: Document,
               counts: Dict[Tuple[str, str], int]) -> None:
        """Write relations and adjacency graph into copied metadata.

        Relations are filtered by min_count, then ordered by count
        descending and name pair ascending; the relations list is capped
        at max_relations while relation_graph keeps every surviving
        pair for adjacency completeness.

        Args:
            doc: Document to stamp.
            counts: (source, target) pair -> co-occurrence count.
        """
        surviving = [(pair, count) for pair, count in counts.items()
                     if count >= self.min_count]
        ordered = sorted(surviving,
                         key=lambda item: (-item[1], item[0][0], item[0][1]))

        relations = [{"source": pair[0], "target": pair[1], "count": count}
                     for pair, count in ordered[:self.max_relations]]

        graph: Dict[str, Dict[str, int]] = {}
        for (left, right), count in ordered:
            graph.setdefault(left, {})[right] = count
            graph.setdefault(right, {})[left] = count

        metadata = dict(doc.metadata or {})
        metadata["relations"] = relations
        metadata["relation_graph"] = graph
        doc.metadata = metadata

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'CooccurrenceRelationExtractor':
        """Initialize and validate the extractor from configuration.

        Validation happens eagerly at load time: a silently misconfigured
        extractor stamping empty relations on every document would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            CooccurrenceRelationExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value or when neither
                terms nor auto_capitalized is configured.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "terms") and \
                doc_processor_configer.terms is not None:
            terms = doc_processor_configer.terms
            if not isinstance(terms, list) or not all(
                    isinstance(term, str) and term.strip()
                    for term in terms):
                raise ValueError(
                    "terms must be a list of non-empty strings")
            self.terms = list(dict.fromkeys(terms))

        if hasattr(doc_processor_configer, "alias_map") and \
                doc_processor_configer.alias_map is not None:
            alias_map = doc_processor_configer.alias_map
            if not isinstance(alias_map, dict) or not all(
                    isinstance(key, str) and key.strip() and
                    isinstance(value, str) and value.strip()
                    for key, value in alias_map.items()):
                raise ValueError(
                    "alias_map must map non-empty strings to non-empty "
                    "strings")
            self.alias_map = dict(alias_map)

        if hasattr(doc_processor_configer, "auto_capitalized") and \
                doc_processor_configer.auto_capitalized is not None:
            self.auto_capitalized = bool(
                doc_processor_configer.auto_capitalized)

        if hasattr(doc_processor_configer, "window") and \
                doc_processor_configer.window is not None:
            self.window = doc_processor_configer.window
            if self.window not in ("sentence", "paragraph"):
                raise ValueError(
                    "window must be 'sentence' or 'paragraph', got "
                    f"'{self.window}'")

        if hasattr(doc_processor_configer, "max_relations") and \
                doc_processor_configer.max_relations is not None:
            max_relations = doc_processor_configer.max_relations
            if isinstance(max_relations, bool) or \
                    not isinstance(max_relations, int):
                raise ValueError("max_relations must be an integer")
            self.max_relations = max_relations
            if self.max_relations < 1:
                raise ValueError("max_relations must be >= 1")

        if hasattr(doc_processor_configer, "min_count") and \
                doc_processor_configer.min_count is not None:
            min_count = doc_processor_configer.min_count
            if isinstance(min_count, bool) or \
                    not isinstance(min_count, int):
                raise ValueError("min_count must be an integer")
            self.min_count = min_count
            if self.min_count < 1:
                raise ValueError("min_count must be >= 1")

        if hasattr(doc_processor_configer, "stopwords") and \
                doc_processor_configer.stopwords is not None:
            stopwords = doc_processor_configer.stopwords
            if not isinstance(stopwords, list) or not all(
                    isinstance(word, str) and word.strip()
                    for word in stopwords):
                raise ValueError(
                    "stopwords must be a list of non-empty strings")
            self.stopwords = list(stopwords)

        if not self.terms and not self.auto_capitalized:
            raise ValueError(
                "either terms or auto_capitalized must be configured to "
                "track entities")

        return self
