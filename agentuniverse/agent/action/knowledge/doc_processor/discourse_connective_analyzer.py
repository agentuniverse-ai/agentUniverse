# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: discourse_connective_analyzer.py

import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# --------------------------------------------------------------------- #
# Sentence segmentation (conservative, same family as SentenceLengthFilter)
# --------------------------------------------------------------------- #

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks.
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"Are you sure?"' stay whole.
_CLOSING_CHARS = "\"'”’」』》）】)]"

# English words that, when the only thing following them is a dot, do NOT
# end a sentence ("Dr. Smith asked..."). Lowercase; matched on the alpha run
# immediately before the dot. Single-letter initials ("J.", "e.g.") are
# handled separately by length, which is why they are absent here.
_ABBREVIATIONS = frozenset((
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "mt", "rev", "hon",
    "gen", "col", "capt", "lt", "sgt", "vs", "etc", "inc", "ltd", "co",
    "corp", "dept", "univ", "assn", "bros", "no", "nos", "vol", "vols",
    "fig", "figs", "eq", "approx", "est", "cf", "al", "ca", "ed", "eds",
    "pp", "ch", "sec", "para", "ph", "md", "ba", "ma", "msc", "jan", "feb",
    "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
))

# --------------------------------------------------------------------- #
# Bundled connective lists
# --------------------------------------------------------------------- #

# English connective phrases, lowercase. Matched case-insensitively as
# whole words / whole phrases: a phrase must not be flanked by letters or
# digits, so "but" never fires inside "butter" and "first" never fires
# inside "firstly".
_EN_PHRASES: Dict[str, Tuple[str, ...]] = {
    "contrast": ("however", "but", "yet", "although", "though", "whereas",
                 "nevertheless", "nonetheless", "in contrast",
                 "on the other hand"),
    "cause": ("because", "since", "as", "therefore", "thus", "hence",
              "consequently", "accordingly", "as a result", "due to"),
    "addition": ("moreover", "furthermore", "additionally", "in addition",
                 "also", "besides"),
    "sequence": ("first", "next", "then", "finally", "subsequently",
                 "meanwhile", "afterwards"),
    "exemplification": ("for example", "for instance", "e.g.", "such as",
                        "namely"),
    "concession": ("despite", "in spite of", "even though", "granted"),
}

# Chinese connectives. Matched as substrings — correct for a script
# without word spacing: 因此 fires inside 因此评审改期.
_ZH_PHRASES: Dict[str, Tuple[str, ...]] = {
    "contrast": ("但是", "然而", "虽然", "不过", "与此相反"),
    "cause": ("因为", "由于", "因此", "所以", "导致"),
    "addition": ("而且", "此外", "另外", "并且"),
    "sequence": ("首先", "其次", "然后", "最后", "接着", "与此同时"),
    "exemplification": ("例如", "譬如", "比如"),
    "concession": ("尽管", "即使", "纵然"),
}

# Category names in alphabetical order — the order used for reporting and
# for deterministic tie-breaking of the dominant category.
_CATEGORIES = ("addition", "cause", "concession", "contrast",
               "exemplification", "sequence")


def _combined_pattern(phrases_by_category: Dict[str, Tuple[str, ...]]
                      ) -> Tuple[Dict[str, str], str]:
    """Flatten one script's connective lists into a match table.

    Alternatives are sorted longest-first so that when phrases nest —
    "even though" over "though", "such as" over "as", "as a result" over
    "as" — the longest phrase wins and the shorter one is consumed rather
    than double-counted.

    Args:
        phrases_by_category: Category name -> connective phrases.

    Returns:
        Tuple[Dict[str, str], str]: Matched-text -> category lookup and
            the "|" joined escaped alternation (empty when no phrases).
    """
    entries = sorted(
        ((phrase, category)
         for category, phrases in phrases_by_category.items()
         for phrase in phrases),
        key=lambda entry: (-len(entry[0]), entry[0]))
    lookup = {phrase: category for phrase, category in entries}
    alternation = "|".join(re.escape(phrase) for phrase, _ in entries)
    return lookup, alternation


_EN_LOOKUP, _EN_ALTERNATION = _combined_pattern(_EN_PHRASES)
_ZH_LOOKUP, _ZH_ALTERNATION = _combined_pattern(_ZH_PHRASES)

# One combined matcher per script. The English pattern anchors both ends
# with word-boundary lookarounds so matches are whole words / phrases; the
# Chinese pattern has no anchors because substring matching is the correct
# semantics for unsegmented CJK text. A single combined alternation per
# script means each span of text is consumed by exactly one match.
_EN_RE = re.compile(r"(?<!\w)(?:" + _EN_ALTERNATION + r")(?!\w)")
_ZH_RE = re.compile("(?:" + _ZH_ALTERNATION + ")")


class DiscourseConnectiveAnalyzer(DocProcessor):
    """Measure discourse-connective usage and classify a discourse profile.

    How a document argues shapes how it should be summarized: an opinion
    piece pivots on "however" and "therefore", a runbook marches through
    "first / next / finally", and a story simply tells. Downstream stages
    — summarization strategy, chunk ranking, prompt hints — can branch on
    that register, but only if something records it. This pre-processing
    component counts discourse connectives across six rhetorical
    categories and writes the tally, plus a coarse discourse profile,
    into document metadata. It never drops or rewrites documents; it is
    an analyzer, not a filter.

    Counting is deliberately simple and entirely offline. The document is
    segmented into sentences with the same conservative splitter used by
    the SentenceLengthFilter family (terminal characters ``. ! ? 。 ！ ？``
    with abbreviation, single-letter-initial, decimal and ellipsis guards
    — so "Dr. Smith arrived. Ms. Lee left." is two sentences and "e.g."
    never splits). English connectives from the bundled lists are matched
    case-insensitively as whole words or phrases ("but" does not fire
    inside "butter"); Chinese connectives are matched as substrings,
    which is the correct semantics for an unsegmented script. Within one
    script all phrases share a single longest-match-first pass, so nested
    phrases are counted once under their longest form: "even though"
    counts only as concession (the inner "though" is consumed), "such as"
    only as exemplification (the inner "as" is consumed).

    Per document the metadata gains:

    * ``metadata[discourse_key]`` (default ``discourse``) — a dict with
      ``sentence_count``, one count per category (``addition``, ``cause``,
      ``concession``, ``contrast``, ``exemplification``, ``sequence``),
      ``total``, ``density_per_100_sentences`` (connectives per 100
      sentences, rounded to two decimals) and ``dominant`` (the category
      with the highest count; ties break alphabetically; ``None`` when no
      connective was found).
    * ``metadata[profile_key]`` (default ``discourse_profile``) — one of
      the labels below, or ``None`` for a document without any
      word-bearing sentence (empty or blank text carries no discourse
      signal, so no label is guessed).

    The profile is a documented heuristic, evaluated in this order:

    1. ``narrative`` — total density below ``narrative_max_density``
       (default 2 per 100 sentences); covers texts that simply tell
       without marking their rhetoric, including connective-free texts.
    2. ``argumentative`` — contrast plus cause make up at least
       ``argumentative_min_share`` (default 60%) of all connectives AND
       density is at least ``argumentative_min_density`` (default 5).
       Takes precedence over the procedural label when both hold.
    3. ``procedural`` — sequence connectives alone make up at least
       ``procedural_min_share`` (default 40%) of all connectives.
    4. ``descriptive`` — anything else: connected prose whose rhetoric
       is mixed or mild.

    Thresholds are configurable so corpora can be tuned, but they remain
    surface heuristics over marker words — a skilled author can argue
    without "however" and a story can be connective-dense. Treat the
    profile as a cheap prior for routing, not ground truth about intent.

    The analysis is deterministic and dependency-free: same input, same
    metadata, across processes and runs. Text, id and all pre-existing
    metadata entries are preserved; new keys are written through a copied
    mapping, and empty key values disable the corresponding stamp.

    Attributes:
        narrative_max_density: Total density strictly below this value
            yields the ``narrative`` profile; must be >= 0.
        argumentative_min_density: Minimum total density for the
            ``argumentative`` profile; must be >= 0.
        argumentative_min_share: Minimum share of contrast+cause among
            all connectives for ``argumentative``; in (0, 1].
        procedural_min_share: Minimum share of sequence connectives for
            ``procedural``; in (0, 1].
        discourse_key: Metadata key the counts dict is written under;
            '' disables the stamp.
        profile_key: Metadata key the profile label is written under;
            '' disables the stamp.
    """

    narrative_max_density: float = 2.0
    argumentative_min_density: float = 5.0
    argumentative_min_share: float = 0.6
    procedural_min_share: float = 0.4
    discourse_key: str = "discourse"
    profile_key: str = "discourse_profile"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Analyze every document and stamp discourse metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; profiling depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, each
            carrying its discourse tally and profile in metadata.
        """
        if not origin_docs:
            return []
        for doc in origin_docs:
            discourse, profile = self._analyze(doc.text or "")
            if self.discourse_key:
                self._stamp(doc, self.discourse_key, discourse)
            if self.profile_key:
                self._stamp(doc, self.profile_key, profile)
        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Analysis
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> Tuple[dict, Optional[str]]:
        """Compute the discourse tally and profile for one text.

        Args:
            text: Document text (None or blank treated as empty).

        Returns:
            Tuple[dict, Optional[str]]: The discourse counts dict and the
            profile label (None when the text has no word-bearing
            sentence).
        """
        counts = {category: 0 for category in _CATEGORIES}
        sentences = self._sentences(text or "")
        for sentence in sentences:
            for category, hits in self._count_connectives(sentence).items():
                counts[category] += hits

        total = sum(counts.values())
        sentence_count = len(sentences)
        density = round(total / sentence_count * 100, 2) \
            if sentence_count else 0.0

        discourse = {"sentence_count": sentence_count}
        discourse.update(counts)
        discourse["total"] = total
        discourse["density_per_100_sentences"] = density
        discourse["dominant"] = self._dominant(counts)

        profile = self._profile(sentence_count, counts, total, density)
        return discourse, profile

    @staticmethod
    def _count_connectives(sentence: str) -> Dict[str, int]:
        """Count connectives of every category inside one sentence.

        The sentence is lowercased once (Chinese is unaffected), then the
        combined English and Chinese matchers each make one longest-match
        first pass; the two scripts cannot overlap.

        Args:
            sentence: One sentence of text.

        Returns:
            Dict[str, int]: Per-category connective counts.
        """
        counts = {category: 0 for category in _CATEGORIES}
        haystack = sentence.lower()
        for match in _EN_RE.finditer(haystack):
            counts[_EN_LOOKUP[match.group(0)]] += 1
        for match in _ZH_RE.finditer(haystack):
            counts[_ZH_LOOKUP[match.group(0)]] += 1
        return counts

    @staticmethod
    def _dominant(counts: Dict[str, int]) -> Optional[str]:
        """Pick the category with the highest connective count.

        Categories are visited in alphabetical order and only a strictly
        greater count takes over, so ties resolve to the alphabetically
        first category — a deterministic rule that needs no timestamps,
        randomness or insertion order.

        Args:
            counts: Per-category connective counts.

        Returns:
            Optional[str]: Dominant category name; None when every count
            is zero.
        """
        best: Optional[str] = None
        best_count = 0
        for category in _CATEGORIES:
            if counts[category] > best_count:
                best, best_count = category, counts[category]
        return best

    def _profile(self, sentence_count: int, counts: Dict[str, int],
                 total: int, density: float) -> Optional[str]:
        """Classify the discourse profile from the tally.

        Rules are evaluated in the documented order; see the class
        docstring for the rationale and the caveat that these are
        surface heuristics.

        Args:
            sentence_count: Number of word-bearing sentences.
            counts: Per-category connective counts.
            total: Sum of all category counts.
            density: Connectives per 100 sentences (already rounded).

        Returns:
            Optional[str]: One of 'narrative', 'argumentative',
            'procedural', 'descriptive'; None without sentences.
        """
        if sentence_count == 0:
            return None
        if density < self.narrative_max_density:
            return "narrative"
        if total == 0:
            # Reachable only with narrative_max_density <= 0: shares over
            # an empty tally are defined as zero, so no stronger label
            # applies.
            return "descriptive"
        reasoning_share = (counts["contrast"] + counts["cause"]) / total
        if reasoning_share >= self.argumentative_min_share and \
                density >= self.argumentative_min_density:
            return "argumentative"
        if counts["sequence"] / total >= self.procedural_min_share:
            return "procedural"
        return "descriptive"

    # ------------------------------------------------------------------ #
    # Segmentation (conservative, same family as SentenceLengthFilter)
    # ------------------------------------------------------------------ #

    def _sentences(self, text: str) -> List[str]:
        """Split text into sentences.

        A sentence is a maximal run of non-terminal characters plus its
        terminating punctuation run and closing quotes. Boundaries are
        ``. ! ?`` and ``。！？``; the dot additionally respects the
        abbreviation, single-letter-initial, decimal and ellipsis guards,
        so "Dr. Smith asked. Ms. Lee replied." yields exactly two
        sentences. Leading whitespace is skipped, so every returned
        string is exactly the sentence's text. A segment must contain at
        least one alphanumeric character (CJK included) to count as a
        sentence — bare punctuation husks are not measured.

        Args:
            text: Raw document text.

        Returns:
            List[str]: Word-bearing sentences in document order.
        """
        sentences: List[str] = []
        length = len(text)
        start = 0
        i = 0
        while i < length:
            if text[i] in _TERMINAL_CHARS and self._is_boundary(text, i):
                end = i + 1
                # A run of terminal punctuation ("？！", "!!") plus any
                # closing quotes belongs to the sentence it terminates.
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                while end < length and text[end] in _CLOSING_CHARS:
                    end += 1
                if self._has_word(text[start:end]):
                    sentences.append(text[start:end])
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
            else:
                i += 1
        # Trailing sentence without terminal punctuation ("...and then").
        if start < length and self._has_word(text[start:length]):
            sentences.append(text[start:length])
        return sentences

    @staticmethod
    def _is_boundary(text: str, index: int) -> bool:
        """Report whether the terminal character at index really splits.

        Args:
            text: Full document text.
            index: Position of the candidate terminal character.

        Returns:
            bool: True when a sentence boundary, False for dots inside
            ellipses, decimals, abbreviations and initials. Non-dot
            terminals (! ? 。！？) always split.
        """
        if text[index] != ".":
            return True
        # Ellipsis "..." splits only at its final dot.
        if index + 1 < len(text) and text[index + 1] == ".":
            return False
        # Decimal point inside a number.
        if index > 0 and text[index - 1].isdigit() and \
                index + 1 < len(text) and text[index + 1].isdigit():
            return False
        # Alpha run immediately before the dot.
        j = index
        while j > 0 and text[j - 1].isalpha():
            j -= 1
        word = text[j:index]
        # Single-letter initial: "J.", "e.g.", "a.m.".
        if len(word) == 1:
            return False
        return word.lower() not in _ABBREVIATIONS

    @staticmethod
    def _has_word(sentence: str) -> bool:
        """Report whether a segment carries at least one word.

        A word is any alphanumeric character (CJK ideographs included),
        so "为什么？" carries one and a bare "？" carries none.

        Args:
            sentence: Segment text.

        Returns:
            bool: True when the segment contains a word character.
        """
        return any(ch.isalnum() for ch in sentence)

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
            -> 'DiscourseConnectiveAnalyzer':
        """Initialize and validate the analyzer from component configuration.

        Validation happens eagerly at load time: thresholds that silently
        mislabeled every document would be far harder to notice in
        production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            DiscourseConnectiveAnalyzer: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "narrative_max_density") and \
                doc_processor_configer.narrative_max_density is not None:
            value = doc_processor_configer.narrative_max_density
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("narrative_max_density must be a number")
            self.narrative_max_density = float(value)
            if self.narrative_max_density < 0:
                raise ValueError("narrative_max_density must be >= 0")

        if hasattr(doc_processor_configer, "argumentative_min_density") and \
                doc_processor_configer.argumentative_min_density is not None:
            value = doc_processor_configer.argumentative_min_density
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    "argumentative_min_density must be a number")
            self.argumentative_min_density = float(value)
            if self.argumentative_min_density < 0:
                raise ValueError("argumentative_min_density must be >= 0")

        if hasattr(doc_processor_configer, "argumentative_min_share") and \
                doc_processor_configer.argumentative_min_share is not None:
            value = doc_processor_configer.argumentative_min_share
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    "argumentative_min_share must be a number")
            self.argumentative_min_share = float(value)
            if not 0 < self.argumentative_min_share <= 1:
                raise ValueError(
                    "argumentative_min_share must be in (0, 1]")

        if hasattr(doc_processor_configer, "procedural_min_share") and \
                doc_processor_configer.procedural_min_share is not None:
            value = doc_processor_configer.procedural_min_share
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("procedural_min_share must be a number")
            self.procedural_min_share = float(value)
            if not 0 < self.procedural_min_share <= 1:
                raise ValueError("procedural_min_share must be in (0, 1]")

        if hasattr(doc_processor_configer, "discourse_key") and \
                doc_processor_configer.discourse_key is not None:
            key = doc_processor_configer.discourse_key
            if not isinstance(key, str):
                raise ValueError("discourse_key must be a string")
            self.discourse_key = key

        if hasattr(doc_processor_configer, "profile_key") and \
                doc_processor_configer.profile_key is not None:
            key = doc_processor_configer.profile_key
            if not isinstance(key, str):
                raise ValueError("profile_key must be a string")
            self.profile_key = key

        return self
