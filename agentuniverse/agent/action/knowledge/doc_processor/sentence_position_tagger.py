# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: sentence_position_tagger.py

from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks. Same rules family as the
# question_detector segmentation (duplicated here because that
# component ships separately; the rules are kept in sync deliberately).
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"He said so."' stay whole.
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

# Exact marker literals inserted around the opening / closing sentences in
# tag_text mode. The literals themselves double as the re-processing guard:
# they are stripped before analysis, so a second pass recovers the very
# text the first pass saw and re-wraps it identically (a no-op).
_OPEN_PREFIX = "[[OPEN]]"
_OPEN_SUFFIX = "[[/OPEN]]"
_CLOSE_PREFIX = "[[CLOSE]]"
_CLOSE_SUFFIX = "[[/CLOSE]]"
_MARKERS = (_OPEN_PREFIX, _OPEN_SUFFIX, _CLOSE_PREFIX, _CLOSE_SUFFIX)

# Sentence position roles.
ROLE_OPENING = "opening"
ROLE_BODY = "body"
ROLE_CLOSING = "closing"


class SentencePositionTagger(DocProcessor):
    """Classify every sentence's position role into document metadata.

    Where a sentence sits in a document carries signal that retrieval
    pipelines routinely want: the opening sentence states what a piece is
    about, the closing one often carries conclusions or calls to action,
    and the middle carries the bulk. Extractive display components can
    bold the bookends instead of a mid-paragraph sample, prompt-budget
    pipelines can keep the opening and closing while trimming body
    sentences under pressure, and rerankers can boost chunks stamped as
    document bookends. This pre-processing component walks every
    document, splits it into sentences and stamps each one's position
    role — offline, deterministically, without any model call.

    Sentence segmentation follows the same conservative rule family as
    the question detector: sentences end at ``. ! ?`` and their CJK
    counterparts ``。！？``， with three English guards on the dot — known
    abbreviations ("Dr. Smith asked..."), single-letter initials
    ("J. K. Rowling", "e.g.") and decimals ("3.14") do not split, and an
    ellipsis splits only at its final dot. A terminal-punctuation run
    ("真的吗？！") plus closing quotes belongs to the sentence it
    terminates; punctuation-only husks (a bare "？") are dropped, and a
    trailing sentence without terminal punctuation still counts.

    Role assignment is a deliberately clean rule:

    * fewer than 3 sentences — every sentence is ``body``; a document
      with one or two sentences has no meaningful bookends, so no
      opening/closing roles are invented;
    * 3 or more sentences — the first is ``opening``, the last is
      ``closing``, everything in between is ``body``.

    Every sentence is recorded in ``metadata['sentence_positions']`` as
    ``{"index": int, "role": "opening" | "body" | "closing", "span":
    (start, end)}`` where ``span`` holds character offsets into the
    analysed text with ``sentence == text[start:end]`` — spans are
    ordered and non-overlapping, so consumers can slice or highlight
    without re-tokenising. The list is capped at ``max_sentences``
    entries (default 200) while ``metadata['position_counts']`` —
    ``{"opening": n, "body": n, "closing": n}`` — always counts every
    sentence, so a capped list never hides the true magnitude; the three
    counts sum to the document's total sentence count.

    With ``tag_text`` enabled the component additionally rewrites the
    document text, wrapping the opening sentence in ``[[OPEN]] ...
    [[/OPEN]]`` and the closing sentence in ``[[CLOSE]] ... [[/CLOSE]]``
    so downstream consumers that only see the text (display layers,
    LLM prompts) can spot the bookends without reading metadata. Before
    analysis the four exact marker literals are stripped from the input,
    which makes re-processing a no-op: markers are never doubled, and
    spans / roles / counts come out identical on every pass because they
    always index the marker-free text. Documents with fewer than 3
    sentences are never rewrapped, and text is left untouched unless
    wrapping actually happens.

    Every document passes through in order — id and existing metadata
    entries are never modified, and metadata mappings are copied before
    mutation. The component is pure Python with zero dependencies,
    deterministic across runs, and complementary to the question
    detector (which classifies sentence *type*): this one classifies
    sentence *position*.

    Attributes:
        max_sentences: Maximum number of entries kept in
            ``metadata['sentence_positions']``; must be >= 0. Counts are
            always the uncapped totals.
        tag_text: When true, also wrap the opening / closing sentences in
            ``[[OPEN]]``/``[[CLOSE]]`` markers inside the document text.
        positions_key: Metadata key the (capped) position list is written
            to; an empty value disables that stamp.
        counts_key: Metadata key the role counts are written to; an empty
            value disables that stamp.
    """

    max_sentences: int = 200
    tag_text: bool = False
    positions_key: str = "sentence_positions"
    counts_key: str = "position_counts"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp sentence position roles into every document's metadata.

        Args:
            origin_docs: Documents to analyse, in batch order.
            query: Query object (unused; position roles depend only on
                the documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, each
            carrying the position list and role counts in its metadata.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            text = doc.text or ""
            # In tag_text mode the analysis runs on the marker-free text:
            # stripping the exact literals makes a second pass a no-op
            # and keeps spans stable (always indexing marker-free text).
            clean = self._strip_markers(text) if self.tag_text else text

            spans = self._sentences(clean)
            total = len(spans)
            positions = [
                {"index": index, "role": self._role(index, total),
                 "span": span}
                for index, span in enumerate(spans)
            ]
            counts = {
                ROLE_OPENING: 0,
                ROLE_BODY: total if total < 3 else total - 2,
                ROLE_CLOSING: 0,
            }
            if total >= 3:
                counts[ROLE_OPENING] = 1
                counts[ROLE_CLOSING] = 1

            if self.positions_key:
                self._stamp(doc, self.positions_key,
                            positions[:self.max_sentences])
            if self.counts_key:
                self._stamp(doc, self.counts_key, counts)

            if self.tag_text and total >= 3:
                doc.text = self._wrap(clean, spans[0], spans[-1])
        return origin_docs

    # ------------------------------------------------------------------ #
    # Role assignment
    # ------------------------------------------------------------------ #

    @staticmethod
    def _role(index: int, total: int) -> str:
        """Return the position role of sentence ``index`` of ``total``.

        The rule is deliberately clean and documented: fewer than 3
        sentences means no meaningful bookends, so everything is body;
        with 3 or more the first is the opening, the last the closing.

        Args:
            index: Zero-based sentence index.
            total: Total number of sentences in the document.

        Returns:
            str: "opening", "body" or "closing".
        """
        if total < 3:
            return ROLE_BODY
        if index == 0:
            return ROLE_OPENING
        if index == total - 1:
            return ROLE_CLOSING
        return ROLE_BODY

    # ------------------------------------------------------------------ #
    # Segmentation
    # ------------------------------------------------------------------ #

    def _sentences(self, text: str) -> List[Tuple[int, int]]:
        """Split text into sentence spans.

        A sentence is a maximal run of non-terminal characters plus its
        terminating punctuation run and closing quotes. Boundaries are
        ``. ! ?`` and ``。！？``； the dot additionally respects the
        abbreviation, single-letter-initial, decimal and ellipsis guards,
        so "Dr. Smith asked. Ms. Lee replied." yields exactly two
        sentences. Leading whitespace is skipped, so every span satisfies
        ``sentence == text[start:end]`` exactly. Segments without at
        least one word (a bare "？") are dropped and never counted; a
        trailing sentence without terminal punctuation still counts.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int]]: Ordered, non-overlapping (start, end)
            character offsets.
        """
        spans: List[Tuple[int, int]] = []
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
                if self._word_count(text[start:end]) >= 1:
                    spans.append((start, end))
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
            else:
                i += 1
        # Trailing sentence without terminal punctuation ("...and so on").
        if start < length and self._word_count(text[start:length]) >= 1:
            spans.append((start, length))
        return spans

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
    def _word_count(sentence: str) -> int:
        """Count words in a sentence.

        A word is a whitespace-delimited token containing at least one
        alphanumeric character (CJK ideographs included, so "为什么？" is
        one word and a bare "？" is zero).

        Args:
            sentence: Sentence text.

        Returns:
            int: Number of words.
        """
        return sum(1 for token in sentence.split()
                   if any(ch.isalnum() for ch in token))

    # ------------------------------------------------------------------ #
    # Text tagging
    # ------------------------------------------------------------------ #

    @staticmethod
    def _strip_markers(text: str) -> str:
        """Remove the component's own marker literals from a text.

        Stripping the four exact literals recovers the text a first pass
        analysed: re-processing is therefore a no-op (markers are never
        doubled) and spans / roles / counts stay identical across passes
        because they always index marker-free text.

        Args:
            text: Document text, possibly tagged by an earlier pass.

        Returns:
            str: The text with every marker literal removed.
        """
        for marker in _MARKERS:
            text = text.replace(marker, "")
        return text

    @staticmethod
    def _wrap(text: str, opening: Tuple[int, int],
              closing: Tuple[int, int]) -> str:
        """Wrap the opening and closing sentences with marker literals.

        Called only with ``total >= 3`` sentences, so the opening and
        closing spans are always distinct, ordered and non-overlapping.

        Args:
            text: Marker-free document text.
            opening: (start, end) span of the opening sentence.
            closing: (start, end) span of the closing sentence.

        Returns:
            str: The text with both bookend sentences wrapped.
        """
        return (text[:opening[0]] + _OPEN_PREFIX +
                text[opening[0]:opening[1]] + _OPEN_SUFFIX +
                text[opening[1]:closing[0]] + _CLOSE_PREFIX +
                text[closing[0]:closing[1]] + _CLOSE_SUFFIX +
                text[closing[1]:])

    # ------------------------------------------------------------------ #
    # Bookkeeping
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
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
            -> 'SentencePositionTagger':
        """Initialize and validate the tagger from component configuration.

        Validation happens eagerly at load time: a misconfigured tagger
        that silently recorded no positions would be far harder to notice
        in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            SentencePositionTagger: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_sentences") and \
                doc_processor_configer.max_sentences is not None:
            cap = doc_processor_configer.max_sentences
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_sentences must be an integer")
            self.max_sentences = cap
            if self.max_sentences < 0:
                raise ValueError("max_sentences must be >= 0")

        if hasattr(doc_processor_configer, "tag_text") and \
                doc_processor_configer.tag_text is not None:
            self.tag_text = bool(doc_processor_configer.tag_text)

        if hasattr(doc_processor_configer, "positions_key") and \
                doc_processor_configer.positions_key is not None:
            key = doc_processor_configer.positions_key
            if not isinstance(key, str):
                raise ValueError("positions_key must be a string")
            self.positions_key = key

        if hasattr(doc_processor_configer, "counts_key") and \
                doc_processor_configer.counts_key is not None:
            key = doc_processor_configer.counts_key
            if not isinstance(key, str):
                raise ValueError("counts_key must be a string")
            self.counts_key = key

        return self
