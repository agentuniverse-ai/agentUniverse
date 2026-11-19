# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: qa_pair_extractor.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Format names accepted by the `formats` configuration, in detector
# priority order (most explicit marker first).
_FORMAT_PREFIX = "prefix"
_FORMAT_NUMBERED = "numbered"
_FORMAT_HEADING = "heading"
_KNOWN_FORMATS = (_FORMAT_PREFIX, _FORMAT_NUMBERED, _FORMAT_HEADING)

# Explicit "Q:"/"A:" markers; the Latin variants accept an optional item
# number ("Q1:" / "A12:") and are case-insensitive, both colon widths work.
_Q_PREFIX = re.compile(r'^\s*(?:question|q)\s*\d{0,3}\s*[:：]\s*(.*)$',
                       re.IGNORECASE)
_A_PREFIX = re.compile(r'^\s*(?:answer|a)\s*\d{0,3}\s*[:：]\s*(.*)$',
                       re.IGNORECASE)
_CJK_Q_PREFIX = re.compile(r'^\s*(?:提问|问题|问)\s*[:：]\s*(.*)$')
_CJK_A_PREFIX = re.compile(r'^\s*(?:回答|答案|答)\s*[:：]\s*(.*)$')

# ATX markdown headings ("## Title", up to three leading spaces) and
# standalone bold lines ("**Question?**") used as implicit questions.
_HEADING = re.compile(r'^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$')
_BOLD = re.compile(r'^\s*\*\*(.+?)\*\*\s*:?\s*$')

# Numbered FAQ items: "1. What is X?", "2、如何安装？", "3) Question?".
_NUMBERED_ITEM = re.compile(r'^\s*(\d{1,3})\s*[.、)）]\s*(.+?)\s*$')
# Inline separator between question and answer on one numbered line; the
# question part must end with a half/full-width question mark.
_NUMBERED_SEP = re.compile(r'^(.+?[?？])\s*(?:-{1,3}|——|—|–|：|:)\s*(.*)$')


class QAPairExtractor(DocProcessor):
    """Extract question-answer pairs from FAQ-style documents.

    FAQ-style source material — support pages, product manuals, community
    threads — embeds knowledge in a question/answer shape that a plain text
    splitter shreds: a chunker cuts between a question and its answer and
    neither half retrieves well alone. This pre-processing component
    addresses the *knowledge extraction* direction of the aU knowledge
    roadmap: it detects QA blocks inside each document and re-emits every
    pair as a self-contained paired document whose text reads
    ``Q: {question}\\nA: {answer}``, so both halves land in the same chunk,
    embed together, and surface together at recall time.

    Three FAQ conventions are recognized, each bilingual (EN/ZH):

    1. ``prefix`` — explicit markers: ``Q:``/``A:``, ``Question:``/
       ``Answer:`` (case-insensitive, optional item number as in ``Q1:``)
       and ``问：``/``答：``, ``问题：``/``回答：``, ``提问：`` with either
       colon width. The answer runs from its marker line until the next
       marker line, so multi-line answers are kept intact.
    2. ``numbered`` — numbered items whose text is a question: either with
       an inline separator (``1. What is X? — An agent framework.``,
       ``2、如何安装？——执行 pip install``, separators ``- -- --- — —— –
       : ：``) or with the answer on the following lines.
    3. ``heading`` — markdown structure: an ATX heading (``## What is it?``)
       or a standalone bold line (``**What is it?**``) followed by its
       answer paragraph.

    Detection is line-based, pure regex and deterministic: each detector
    returns (start, end, question, answer) spans; answer collection always
    stops at any other format's marker line, so spans of different formats
    nest cleanly instead of overlapping, and the collected spans are
    scheduled in document order (earliest start first; longer span and
    detector priority break ties) as a safety net for full determinism.
    Extraction order therefore always follows the document's own order.

    Each kept pair becomes a NEW Document (fresh id; the source is never
    mutated) with metadata ``pair_index`` (0-based within the source, after
    filtering and capping), ``question``, ``answer`` and ``source_doc_id``.
    With ``keep_source`` false (default) the paired documents replace the
    source; with true the source is kept in place and the pairs follow it.
    A document in which no pair is found always passes through unchanged.
    Answers shorter than ``min_answer_chars`` or longer than
    ``max_answer_chars`` (0 = unlimited) are discarded, at most
    ``max_pairs`` pairs are emitted per source document.

    Attributes:
        formats: FAQ conventions to detect, a non-empty subset of
            ``('prefix', 'numbered', 'heading')``; default: all three.
        min_answer_chars: Minimum answer length in characters for a pair
            to be kept; must be >= 0.
        max_answer_chars: Maximum answer length in characters; 0 (the
            default) means unlimited. When > 0 it must be >=
            min_answer_chars.
        max_pairs: Maximum number of pairs emitted per source document;
            must be >= 1. Default 100.
        keep_source: When false (default) documents with extracted pairs
            are replaced by those pairs; when true the source document is
            kept in place and the pairs are appended after it.
    """

    formats: List[str] = list(_KNOWN_FORMATS)
    min_answer_chars: int = 1
    max_answer_chars: int = 0
    max_pairs: int = 100
    keep_source: bool = False

    def _process_docs(self, origin_docs: List[Document],
                      query: Optional[Query] = None) -> List[Document]:
        """Rebuild the batch with extracted QA pair documents.

        Args:
            origin_docs: Documents to scan for FAQ blocks, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: For every source document either its extracted
            pair documents (with the source kept first when
            ``keep_source``) or the unchanged source itself when no pair
            was found; batch order is preserved.
        """
        if not origin_docs:
            return []

        output: List[Document] = []
        for doc in origin_docs:
            pairs = self._extract_pairs(doc.text or "")
            if not pairs:
                output.append(doc)
                continue
            if self.keep_source:
                output.append(doc)
            for pair_index, (question, answer) in enumerate(pairs):
                output.append(Document(
                    text=f"Q: {question}\nA: {answer}",
                    metadata={
                        "pair_index": pair_index,
                        "question": question,
                        "answer": answer,
                        "source_doc_id": doc.id,
                    },
                ))
        return output

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #

    def _extract_pairs(self, text: str) -> List[Tuple[str, str]]:
        """Detect all QA pairs in one text, in document order.

        Args:
            text: Raw document text (None treated as empty).

        Returns:
            List[Tuple[str, str]]: (question, answer) tuples after answer
            length filtering, capped at ``max_pairs``.
        """
        lines = (text or "").split("\n")
        spans: List[Tuple[int, int, int, str, str]] = []
        detectors = (
            (_FORMAT_PREFIX, self._detect_prefix_pairs),
            (_FORMAT_NUMBERED, self._detect_numbered_pairs),
            (_FORMAT_HEADING, self._detect_heading_pairs),
        )
        for priority, (name, detector) in enumerate(detectors):
            if name in self.formats:
                spans.extend(
                    (start, end, priority, question, answer)
                    for start, end, question, answer in detector(lines))

        # Greedy interval scheduling in document order: earliest start
        # first, longer span and detector priority break ties. Detectors
        # already stop answer collection at other formats' markers, so in
        # practice spans never overlap; this pass keeps the result fully
        # deterministic even for pathological inputs.
        spans.sort(key=lambda span: (span[0], -span[1], span[2]))
        accepted: List[Tuple[str, str]] = []
        last_end = -1
        for start, end, _priority, question, answer in spans:
            if start >= last_end:
                accepted.append((question, answer))
                last_end = end

        accepted = [
            (question, answer) for question, answer in accepted
            if len(answer) >= self.min_answer_chars
            and (not self.max_answer_chars
                 or len(answer) <= self.max_answer_chars)
        ]
        return accepted[:self.max_pairs]

    def _detect_prefix_pairs(self, lines: List[str]
                             ) -> List[Tuple[int, int, str, str]]:
        """Detect explicit ``Q:``/``A:`` marker blocks.

        A question marker with a non-empty inline question must be
        followed (blank lines allowed) by an answer marker; the answer
        then continues over subsequent non-marker lines, preserving
        multi-line answers. Orphan questions without an answer marker are
        skipped.

        Args:
            lines: Document lines.

        Returns:
            List[Tuple[int, int, str, str]]: (start, end, question,
            answer) spans.
        """
        spans: List[Tuple[int, int, str, str]] = []
        total = len(lines)
        index = 0
        while index < total:
            question_match = self._match_q_prefix(lines[index])
            if question_match and question_match.group(1).strip():
                answer_line = index + 1
                while answer_line < total and not lines[answer_line].strip():
                    answer_line += 1
                answer_match = self._match_a_prefix(
                    lines[answer_line]) if answer_line < total else None
                if answer_match:
                    parts = [answer_match.group(1)]
                    end = answer_line + 1
                    while end < total and not self._is_boundary(lines[end]):
                        parts.append(lines[end])
                        end += 1
                    answer = "\n".join(parts).strip()
                    if answer:
                        spans.append((index, end,
                                      question_match.group(1).strip(),
                                      answer))
                    index = end
                    continue
            index += 1
        return spans

    def _detect_numbered_pairs(self, lines: List[str]
                               ) -> List[Tuple[int, int, str, str]]:
        """Detect numbered FAQ items.

        An item counts as a question when its text ends with a half/full
        width question mark or carries an inline separator after one
        (``1. What is X? — Answer.``). The answer is either the text after
        the separator on the same line or the following lines up to the
        next marker; items that are plain statements are left alone.

        Args:
            lines: Document lines.

        Returns:
            List[Tuple[int, int, str, str]]: (start, end, question,
            answer) spans.
        """
        spans: List[Tuple[int, int, str, str]] = []
        total = len(lines)
        for index, line in enumerate(lines):
            item_match = _NUMBERED_ITEM.match(line)
            if not item_match:
                continue
            item = item_match.group(2).strip()
            separator_match = _NUMBERED_SEP.match(item)
            if separator_match:
                question = separator_match.group(1).strip()
                inline_answer = separator_match.group(2).strip()
                if inline_answer:
                    spans.append((index, index + 1, question, inline_answer))
                    continue
            elif item.endswith(("?", "？")):
                question = item
            else:
                continue
            parts = []
            end = index + 1
            while end < total and not self._is_boundary(lines[end]):
                parts.append(lines[end])
                end += 1
            answer = "\n".join(parts).strip()
            if answer:
                spans.append((index, end, question, answer))
        return spans

    def _detect_heading_pairs(self, lines: List[str]
                              ) -> List[Tuple[int, int, str, str]]:
        """Detect markdown heading / bold-line question blocks.

        Any ATX heading (``##`` to ``######``) or standalone bold line is
        taken as the question and the following non-marker lines up to the
        next marker are its answer; a heading without a non-empty answer
        paragraph yields no pair.

        Args:
            lines: Document lines.

        Returns:
            List[Tuple[int, int, str, str]]: (start, end, question,
            answer) spans.
        """
        spans: List[Tuple[int, int, str, str]] = []
        total = len(lines)
        for index, line in enumerate(lines):
            heading_match = _HEADING.match(line)
            bold_match = None if heading_match else _BOLD.match(line)
            if heading_match:
                question = heading_match.group(2).strip()
            elif bold_match:
                question = bold_match.group(1).strip()
            else:
                continue
            if not question:
                continue
            parts = []
            end = index + 1
            while end < total and not self._is_boundary(lines[end]):
                parts.append(lines[end])
                end += 1
            answer = "\n".join(parts).strip()
            if answer:
                spans.append((index, end, question, answer))
        return spans

    # ------------------------------------------------------------------ #
    # Marker helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _match_q_prefix(line: str) -> Optional[re.Match]:
        """Match a line against the question markers of the prefix format.

        Args:
            line: Single document line.

        Returns:
            Optional[re.Match]: Match with the question text in group 1,
            or None when the line is not a question marker.
        """
        return (_Q_PREFIX.match(line) or _CJK_Q_PREFIX.match(line))

    @staticmethod
    def _match_a_prefix(line: str) -> Optional[re.Match]:
        """Match a line against the answer markers of the prefix format.

        Args:
            line: Single document line.

        Returns:
            Optional[re.Match]: Match with the answer text in group 1, or
            None when the line is not an answer marker.
        """
        return (_A_PREFIX.match(line) or _CJK_A_PREFIX.match(line))

    def _is_boundary(self, line: str) -> bool:
        """Report whether a line terminates answer collection.

        Answer collection of every format stops at any other format's
        marker line — question/answer prefixes, markdown headings,
        standalone bold lines and numbered items that look like questions
        — which is what keeps spans of different formats from overlapping.

        Args:
            line: Single document line.

        Returns:
            bool: True when the line is a marker line.
        """
        return bool(
            self._match_q_prefix(line) or self._match_a_prefix(line)
            or _HEADING.match(line) or _BOLD.match(line)
            or self._is_numbered_question_line(line)
        )

    @staticmethod
    def _is_numbered_question_line(line: str) -> bool:
        """Report whether a line is a numbered item phrased as a question.

        Args:
            line: Single document line.

        Returns:
            bool: True for lines like ``1. What is X? — ...`` or
            ``2、如何安装？``; plain numbered statements return False.
        """
        item_match = _NUMBERED_ITEM.match(line)
        if not item_match:
            return False
        item = item_match.group(2).strip()
        return item.endswith(("?", "？")) or bool(_NUMBERED_SEP.match(item))

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'QAPairExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: a silently misconfigured
        extractor (say, an empty format list) that let FAQ documents pass
        through unextracted would be far harder to notice downstream than
        a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            QAPairExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "formats") and \
                doc_processor_configer.formats is not None:
            formats = doc_processor_configer.formats
            if isinstance(formats, str) or \
                    not isinstance(formats, (list, tuple)):
                raise ValueError(
                    "formats must be a list drawn from "
                    f"{list(_KNOWN_FORMATS)}")
            cleaned: List[str] = []
            for item in formats:
                if item not in _KNOWN_FORMATS:
                    raise ValueError(
                        f"unknown format {item!r}; formats must be a "
                        f"subset of {list(_KNOWN_FORMATS)}")
                if item not in cleaned:
                    cleaned.append(item)
            if not cleaned:
                raise ValueError("formats must not be empty")
            self.formats = cleaned

        if hasattr(doc_processor_configer, "min_answer_chars") and \
                doc_processor_configer.min_answer_chars is not None:
            minimum = doc_processor_configer.min_answer_chars
            if isinstance(minimum, bool) or not isinstance(minimum, int):
                raise ValueError("min_answer_chars must be an integer")
            self.min_answer_chars = minimum
            if self.min_answer_chars < 0:
                raise ValueError("min_answer_chars must be >= 0")

        if hasattr(doc_processor_configer, "max_answer_chars") and \
                doc_processor_configer.max_answer_chars is not None:
            maximum = doc_processor_configer.max_answer_chars
            if isinstance(maximum, bool) or not isinstance(maximum, int):
                raise ValueError("max_answer_chars must be an integer")
            self.max_answer_chars = maximum
            if self.max_answer_chars < 0:
                raise ValueError(
                    "max_answer_chars must be >= 0 (0 means unlimited)")
            if self.max_answer_chars and \
                    self.min_answer_chars > self.max_answer_chars:
                raise ValueError(
                    "min_answer_chars must not exceed max_answer_chars "
                    f"({self.min_answer_chars} > {self.max_answer_chars})")

        if hasattr(doc_processor_configer, "max_pairs") and \
                doc_processor_configer.max_pairs is not None:
            pairs = doc_processor_configer.max_pairs
            if isinstance(pairs, bool) or not isinstance(pairs, int):
                raise ValueError("max_pairs must be an integer")
            self.max_pairs = pairs
            if self.max_pairs < 1:
                raise ValueError("max_pairs must be >= 1")

        if hasattr(doc_processor_configer, "keep_source") and \
                doc_processor_configer.keep_source is not None:
            self.keep_source = bool(doc_processor_configer.keep_source)

        return self
