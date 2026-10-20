# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: topic_sentence_extractor.py

import re
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Line terminators recognized when grouping text into paragraphs: the
# Unix LF, the Windows CRLF pair and the legacy bare CR — the exact same
# rule family as the paragraph stats profiler (duplicated here because
# that component ships separately; the rules are kept in sync
# deliberately). Exotic Unicode boundaries (\v, \f, \u2028, ...) are
# deliberately NOT terminators here.
_LINE_BREAK_RE = re.compile(r"\r\n|\r|\n")

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks — same conservative rule family
# as the sentence position tagger (duplicated here because that
# component ships separately; the rules are kept in sync deliberately).
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"He said so."' stay whole.
_CLOSING_CHARS = "\"'”’」』》）】)]"

# English words that, when the only thing following them is a dot, do NOT
# end a sentence ("Dr. Smith asked..."). Lowercase; matched on the alpha
# run immediately before the dot. Single-letter initials ("J.", "e.g.")
# are handled separately by length, which is why they are absent here.
_ABBREVIATIONS = frozenset((
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "mt", "rev", "hon",
    "gen", "col", "capt", "lt", "sgt", "vs", "etc", "inc", "ltd", "co",
    "corp", "dept", "univ", "assn", "bros", "no", "nos", "vol", "vols",
    "fig", "figs", "eq", "approx", "est", "cf", "al", "ca", "ed", "eds",
    "pp", "ch", "sec", "para", "ph", "md", "ba", "ma", "msc", "jan", "feb",
    "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
))

# Sentence openers that traditionally announce the point being made —
# applied case-insensitively for the Latin branches, so "this paper",
# "These results", "Here we show" and "In this section" all match, as do
# the Chinese document/section openers 本文 / 本节. The \b applies only
# to the Latin branch, so "Thistle..." does not match while "This," does.
_SIGNPOST_RE = re.compile(
    r"^(?:(?:this|these|here\s+we|in\s+this)\b|本文|本节)", re.IGNORECASE)

# Definitional copula patterns searched anywhere inside a sentence:
# English "is a" and "are" ("A vector store is a database...", "The
# results are reproducible.") and the Chinese definitional 是指
# ("知识库是指结构化的语料集合。"). Case-insensitive on the Latin branch.
_COPULA_RE = re.compile(r"\bis\s+a\b|\bare\b|是指", re.IGNORECASE)

# Default length band (in characters, terminal punctuation included)
# inside which a sentence earns the length-band bonus, and the length
# above which the rambling penalty applies.
_LENGTH_BAND_LOW = 40
_LENGTH_BAND_HIGH = 120
_RAMBLING_LENGTH = 250

# Maximum number of topic-sentence entries stamped into metadata; the
# uncapped total is always reported in topic_count.
_MAX_TOPIC_SENTENCES = 50

# Separator used when assembling the document skeleton preview string.
_SKELETON_SEPARATOR = " … "


class TopicSentenceExtractor(DocProcessor):
    """Extract each paragraph's topic sentence into document metadata.

    Retrieval front-ends rarely have room to show a whole chunk: result
    lists, hover previews and prompt-budget pipelines all want one
    representative sentence per paragraph — the extractive skeleton of
    the document. This pre-processing component walks every document,
    splits it into paragraphs and sentences, scores each sentence with a
    classic weighted-cue heuristic (position, length, signpost openers,
    copula patterns) and stamps the best sentence of every paragraph
    into metadata. It is deterministic, offline and dependency-free: no
    model call, no network, nothing but the standard library — the cheap
    structural counterpart to a summarizer, which produces a global
    abstract instead of per-paragraph anchors.

    Text model, stated precisely:

    - paragraphs follow the exact same rule as the paragraph stats
      profiler: the text is cut into lines on ``\r\n``, ``\r`` or ``\n``;
      a paragraph is a maximal run of consecutive non-blank lines (one
      OR MORE blank lines separate paragraphs equally, single line
      breaks inside a run stay inside the paragraph), and each paragraph
      is trimmed to its first and last non-whitespace character;
    - sentences end at ``. ! ?`` and their CJK counterparts ``。！？``
      with three English guards on the dot — known abbreviations
      ("Dr. Smith asked..."), single-letter initials ("J. K. Rowling",
      "e.g.") and decimals ("3.14") do not split, and an ellipsis splits
      only at its final dot. A terminal-punctuation run ("真的吗？！")
      plus closing quotes belongs to the sentence it terminates,
      punctuation-only husks are dropped, and a trailing sentence
      without terminal punctuation still counts;
    - paragraphs whose trimmed length is under ``min_paragraph_chars``
      (default 20) are skipped — too short to have a topic worth
      anchoring.

    Every sentence of a kept paragraph earns a score, the weighted sum
    of five cues:

    +-----------------------+---------+----------------------------+
    | Cue                   | Weight  | Condition                  |
    +=======================+=========+============================+
    | first sentence        | +2.0    | sentence index 0           |
    +-----------------------+---------+----------------------------+
    | last sentence         | +0.5    | sentence index N-1         |
    +-----------------------+---------+----------------------------+
    | length band           | +1.0    | 40 <= len(sentence) <= 120 |
    +-----------------------+---------+----------------------------+
    | rambling penalty      | -1.0    | len(sentence) > 250        |
    +-----------------------+---------+----------------------------+
    | signpost opener       | +1.5    | starts with This / These / |
    |                       |         | Here we / In this (case-   |
    |                       |         | insensitive) or 本文 / 本节 |
    +-----------------------+---------+----------------------------+
    | definitional copula   | +0.5    | contains "is a" / "are"    |
    |                       |         | (case-insensitive) or 是指 |
    +-----------------------+---------+----------------------------+

    The position bonuses encode the classic extractive bias that
    paragraph openings (and, more weakly, closings) carry the topic; a
    lone sentence in a single-sentence paragraph is both first and last
    and earns both bonuses. Sentence length counts characters of the
    trimmed sentence, terminal punctuation included. The highest score
    wins, and ties go to the earliest sentence, so the result is a pure
    function of the text.

    Findings land in document metadata: ``metadata['topic_sentences']``
    holds at most 50 entries — ``{"paragraph_index", "sentence_index",
    "text", "span", "score"}`` where ``paragraph_index`` is the 0-based
    index into the document's FULL paragraph list (skipped paragraphs
    simply leave a gap) and ``span`` is a ``{"start", "end"}`` dict of
    character offsets into the document text with
    ``text[start:end] == text_entry``; ``metadata['topic_count']``
    always carries the uncapped total. With ``doc_skeleton`` enabled the
    component additionally stamps ``metadata['skeleton']`` — the capped
    entries' sentences joined with ``" … "`` — a ready-to-render preview
    string. Documents are never dropped, reordered or edited, and
    metadata mappings are copied before mutation.

    The component complements its siblings: the paragraph stats
    profiler measures paragraph structure, the sentence position tagger
    labels every sentence's role, and the summarizer tool compresses a
    whole text with a model — this one picks one anchor sentence per
    paragraph, per-paragraph by construction and model-free by design.

    Attributes:
        min_paragraph_chars: Minimum trimmed character length for a
            paragraph to be analysed; integer >= 0, default 20.
        first_bonus: Score bonus for a paragraph's first sentence;
            numeric >= 0, default 2.0.
        last_bonus: Score bonus for a paragraph's last sentence;
            numeric >= 0, default 0.5.
        length_band_bonus: Score bonus for sentences of 40-120
            characters; numeric >= 0, default 1.0.
        rambling_penalty: Score penalty (subtracted) for sentences
            longer than 250 characters; numeric >= 0, default 1.0.
        signpost_bonus: Score bonus for signpost openers; numeric >= 0,
            default 1.5.
        copula_bonus: Score bonus for definitional copula patterns;
            numeric >= 0, default 0.5.
        doc_skeleton: When true, also stamp ``metadata['skeleton']``
            with the topic sentences joined by ``" … "``; default false.
    """

    min_paragraph_chars: int = 20
    first_bonus: float = 2.0
    last_bonus: float = 0.5
    length_band_bonus: float = 1.0
    rambling_penalty: float = 1.0
    signpost_bonus: float = 1.5
    copula_bonus: float = 0.5
    doc_skeleton: bool = False

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp every document's topic sentences into its metadata.

        Args:
            origin_docs: Documents to analyse, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order — none
            is dropped, reordered or edited; each carries the extracted
            topic sentences in its metadata.
        """
        for doc in origin_docs:
            topics = self._extract(doc.text or "")
            entries = topics[:_MAX_TOPIC_SENTENCES]
            self._stamp(doc, "topic_sentences", entries)
            self._stamp(doc, "topic_count", len(topics))
            if self.doc_skeleton:
                self._stamp(doc, "skeleton", _SKELETON_SEPARATOR.join(
                    entry["text"] for entry in entries))
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #

    def _extract(self, text: str) -> List[dict]:
        """Pick the topic sentence of every analysed paragraph.

        Args:
            text: Document text (None already coerced to "").

        Returns:
            List[dict]: One entry per kept paragraph, in paragraph
            order — {"paragraph_index", "sentence_index", "text",
            "span", "score"}; empty when the text has no paragraph long
            enough to analyse.
        """
        results: List[dict] = []
        for paragraph_index, (start, end) in enumerate(
                self._paragraph_spans(text or "")):
            if end - start < self.min_paragraph_chars:
                continue
            sentences = self._sentences(text[start:end], start)
            if not sentences:
                continue
            best_index = 0
            best_score = None
            for sentence_index, (s_start, s_end, body) in \
                    enumerate(sentences):
                score = self._score(sentence_index, len(sentences), body)
                # strictly greater: ties keep the earliest sentence
                if best_score is None or score > best_score:
                    best_score, best_index = score, sentence_index
            s_start, s_end, body = sentences[best_index]
            results.append({
                "paragraph_index": paragraph_index,
                "sentence_index": best_index,
                "text": body,
                "span": {"start": s_start, "end": s_end},
                "score": best_score,
            })
        return results

    def _score(self, index: int, count: int, sentence: str) -> float:
        """Score one sentence with the weighted-cue heuristic.

        Args:
            index: 0-based position of the sentence in its paragraph.
            count: Number of sentences in the paragraph.
            sentence: Trimmed sentence text.

        Returns:
            float: Weighted sum of the cue bonuses; every default weight
            is an exact binary fraction, so default-config scores are
            exact multiples of 0.5.
        """
        score = 0.0
        if index == 0:
            score += self.first_bonus
        if index == count - 1:
            score += self.last_bonus
        length = len(sentence)
        if _LENGTH_BAND_LOW <= length <= _LENGTH_BAND_HIGH:
            score += self.length_band_bonus
        elif length > _RAMBLING_LENGTH:
            score -= self.rambling_penalty
        if _SIGNPOST_RE.match(sentence):
            score += self.signpost_bonus
        if _COPULA_RE.search(sentence):
            score += self.copula_bonus
        return score

    # ------------------------------------------------------------------ #
    # Segmentation helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _paragraph_spans(text: str) -> List[Tuple[int, int]]:
        """Split text into trimmed paragraph spans on runs of blank lines.

        Same paragraph rule as the paragraph stats profiler: paragraphs
        are maximal runs of consecutive non-blank lines, trimmed to their
        first and last non-whitespace character.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int]]: One (start, end) pair per paragraph —
            character offsets into ``text`` with
            ``text[start:end] == paragraph``; empty for text without
            any non-blank line.
        """
        # Line spans in the original text: walk every terminator so each
        # line keeps its exact offsets (the terminator itself belongs to
        # neither line).
        line_spans = []
        start = 0
        for match in _LINE_BREAK_RE.finditer(text):
            line_spans.append((start, match.start()))
            start = match.end()
        line_spans.append((start, len(text)))

        runs: List[List[int]] = []
        run = None
        for line_start, line_end in line_spans:
            if text[line_start:line_end].strip():
                if run is None:
                    run = [line_start, line_end]
                else:
                    run[1] = line_end
            elif run is not None:
                runs.append(run)
                run = None
        if run is not None:
            runs.append(run)

        spans: List[Tuple[int, int]] = []
        for run_start, run_end in runs:
            start = run_start
            while start < run_end and text[start].isspace():
                start += 1
            end = run_end
            while end > start and text[end - 1].isspace():
                end -= 1
            spans.append((start, end))
        return spans

    @classmethod
    def _sentences(cls, text: str, base: int) \
            -> List[Tuple[int, int, str]]:
        """Split one paragraph into trimmed sentences with absolute spans.

        Args:
            text: Paragraph text (already trimmed).
            base: Offset of ``text[0]`` inside the document text, added
                to every returned span so spans address the document.

        Returns:
            List[Tuple[int, int, str]]: One tuple per sentence —
            (start, end, body) with ``text[start - base:end - base] ==
            body``; punctuation-only husks are dropped, so the result
            may be empty for degenerate input.
        """
        length = len(text)
        found: List[Tuple[int, int, str]] = []
        start = 0
        i = 0
        while i < length:
            if text[i] in _TERMINAL_CHARS and not cls._guarded(text, i):
                end = i + 1
                # A run of terminal punctuation ("?!", "真的吗？！") plus
                # closing quotes belongs to the sentence it terminates.
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                while end < length and text[end] in _CLOSING_CHARS:
                    end += 1
                cls._push(found, text, start, end, base)
                start = end
                i = end
            else:
                i += 1
        if start < length:
            cls._push(found, text, start, length, base)
        return found

    @staticmethod
    def _push(found: List[Tuple[int, int, str]], text: str,
              start: int, end: int, base: int) -> None:
        """Append one sentence span unless it is blank or a mere husk.

        Args:
            found: Accumulator list.
            text: Paragraph text being split.
            start: Raw sentence start offset (inside ``text``).
            end: Raw sentence end offset, exclusive (inside ``text``).
            base: Offset of ``text[0]`` inside the document text.
        """
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start >= end:
            return
        body = text[start:end]
        # Punctuation-only husks (a bare "？" left between terminals)
        # carry no topic and would only pollute the indices.
        if not any(char.isalnum() for char in body):
            return
        found.append((base + start, base + end, body))

    @staticmethod
    def _guarded(text: str, index: int) -> bool:
        """Report whether the dot at ``index`` is guarded from splitting.

        Guards, applied only to the ASCII dot: an ellipsis splits only
        at its final dot; decimals ("3.14") never split; an alpha run
        before the dot that is a known abbreviation ("Dr.") or a
        single-letter initial ("J.", "e.g.") never splits.

        Args:
            text: Paragraph text being split.
            index: Position of the dot under test.

        Returns:
            bool: True when this dot does not end a sentence.
        """
        if text[index] != ".":
            return False
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if nxt == ".":
            return True  # ellipsis: not the final dot
        prev = text[index - 1] if index > 0 else ""
        if prev.isdigit() and nxt.isdigit():
            return True  # decimal point
        if prev.isalpha():
            word_start = index
            while word_start > 0 and text[word_start - 1].isalpha():
                word_start -= 1
            # single-letter initials by length, the rest by membership
            return (index - word_start) == 1 or \
                text[word_start:index].lower() in _ABBREVIATIONS
        return False

    # ------------------------------------------------------------------ #
    # Metadata helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping
        shared with other pipeline stages never observes surprising
        in-place edits.

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
            -> 'TopicSentenceExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: weights are the whole
        model, and a silently negative or non-numeric weight would skew
        every document's skeleton unnoticed.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            TopicSentenceExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "min_paragraph_chars") and \
                doc_processor_configer.min_paragraph_chars is not None:
            minimum = doc_processor_configer.min_paragraph_chars
            if isinstance(minimum, bool) or not isinstance(minimum, int):
                raise ValueError("min_paragraph_chars must be an integer")
            self.min_paragraph_chars = minimum
            if self.min_paragraph_chars < 0:
                raise ValueError("min_paragraph_chars must be >= 0")

        for key in ("first_bonus", "last_bonus", "length_band_bonus",
                    "rambling_penalty", "signpost_bonus", "copula_bonus"):
            if hasattr(doc_processor_configer, key) and \
                    getattr(doc_processor_configer, key) is not None:
                weight = getattr(doc_processor_configer, key)
                if isinstance(weight, bool) or \
                        not isinstance(weight, (int, float)):
                    raise ValueError(f"{key} must be a number")
                if weight < 0:
                    raise ValueError(f"{key} must be >= 0")
                setattr(self, key, float(weight))

        if hasattr(doc_processor_configer, "doc_skeleton") and \
                doc_processor_configer.doc_skeleton is not None:
            self.doc_skeleton = bool(doc_processor_configer.doc_skeleton)

        return self
