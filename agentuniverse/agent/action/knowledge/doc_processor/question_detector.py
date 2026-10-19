# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: question_detector.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

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

# English interrogative openers. A sentence whose first word (ignoring
# leading punctuation/quotes) is one of these is classified as a wh question.
_EN_OPENERS = frozenset((
    "what", "why", "how", "when", "where", "who", "which", "whose",
    "is", "are", "do", "does", "did", "can", "could", "would", "should",
    "will",
))

# Chinese interrogative tokens. Chinese has no word boundaries or
# capitalisation, so these are matched anywhere inside the sentence
# ("这是什么？" does not start with 什么). Longest-first so 为什么 is
# reported instead of a nested 什么 at the same position.
_ZH_OPENERS = ("为什么", "什么", "怎么", "如何", "多少", "几", "哪")

# First alphabetic run of a sentence, skipping leading punctuation,
# quotes and digits ("\"Why" -> "why").
_FIRST_EN_WORD = re.compile(r"^[^\w]*([A-Za-z]+)")

# Trailing non-alphanumeric tail of a sentence (terminal punctuation run
# plus closing quotes), used when looking at what precedes it.
_TRAILING_PUNCT = re.compile(r"[^A-Za-z0-9\u4e00-\u9fff]+$")

# English tag question "..., right?" — the word "right" as the last word
# with a question mark in the trailing punctuation.
_EN_RIGHT_TAG = re.compile(r"(\bright\b)([^A-Za-z0-9]*)$",
                           re.IGNORECASE)

# Chinese tag / A-not-A question markers.
_ZH_A_NOT_A = "是不是"
_ZH_TAG = "对吗"

# Chinese polar question particle 吗 at the end of an otherwise
# declarative-shaped sentence.
_ZH_POLAR = "吗"


class QuestionDetector(DocProcessor):
    """Find interrogative sentences and stamp them into document metadata.

    Knowledge corpora are full of questions worth mining: FAQ pages answer
    them in bulk, community posts ask them verbatim, and support
    transcripts are essentially question logs. Yet those questions are
    buried inside running prose, and downstream QA-pair construction needs
    them isolated before anything can be paired, paraphrased or ranked.
    This pre-processing component walks every document, splits it into
    sentences and classifies each sentence as a question or not — offline,
    deterministically and without any model call — then stamps the hits
    into ``metadata['questions']`` together with aggregate counts, so FAQ
    mining and QA-pair workflows can consume them directly.

    Sentence segmentation is deliberately conservative. Sentences end at
    ``. ! ?`` and their CJK counterparts ``。！？``， with three English
    guards on the dot: known abbreviations ("Dr. Smith asked..."), single
    letter initials ("J. K. Rowling", "e.g.") and decimals ("3.14") do not
    split; a trailing terminal-punctuation run ("真的吗？！") plus any
    closing quotes belong to the sentence they terminate.

    A sentence counts as a question when, in priority order:

    1. **wh** — it starts with an English interrogative opener (what, why,
       how, when, where, who, which, whose, is, are, do, does, did, can,
       could, would, should, will — case-insensitive, leading quotes
       allowed) or contains a Chinese interrogative token (为什么 / 什么 /
       怎么 / 如何 / 多少 / 几 / 哪). The matched token is recorded as
       ``opener``. Terminal punctuation is not required ("How to configure
       this." still counts).
    2. **tagged** — it carries an inline question marker: an English
       "..., right?" ending (the question mark is required for the English
       tag), or the Chinese markers 是不是 / 对吗 anywhere near the end
       (these are unambiguous without a question mark).
    3. **polar** — it simply ends with ``?`` / ``？`` (a statement-shaped
       sentence with question intonation: "She left?"), or a Chinese
       statement ends with the particle 吗 ("你吃了吗。").

    Each hit is ``{"text": str, "span": (start, end), "kind": "wh" |
    "polar" | "tagged", "opener": str | None}`` where ``span`` are
    character offsets into the original document text with
    ``text == document.text[start:end]`` — spans are non-overlapping and
    ordered, so consumers can highlight hits without re-tokenising.
    ``opener`` is the matched interrogative token (the tag marker for
    tagged questions) and ``None`` for polar questions, which are
    recognised purely by their ending.

    Aggregates land next to the list: ``metadata['question_count']`` is
    the total number of question sentences found (never capped), and
    ``metadata['question_ratio']`` is question sentences divided by total
    sentences — 0.0 for empty or wordless documents. Segments with fewer
    than ``min_words`` words are ignored entirely (neither sentence nor
    question); the default of 1 only drops punctuation husks like a bare
    "？", while a single-word "Why?" still counts as one word and passes.

    Every document passes through untouched — text, id and existing
    metadata entries are never modified, and metadata mappings are copied
    before mutation. The component is pure Python with zero dependencies,
    deterministic across runs, and complementary to QAPairExtractor (which
    requires *paired* questions and answers) and MultiQueryParaphraser
    (which *generates* questions with an LLM): this one only *detects*
    what is already asked.

    Attributes:
        max_questions: Maximum number of hits kept in
            ``metadata['questions']``; must be >= 0. The count metadata is
            always the uncapped total, so a capped list never hides the
            true magnitude.
        min_words: Minimum number of words (whitespace tokens containing
            at least one alphanumeric character) for a segment to count as
            a sentence; must be >= 1. Default 1 — single-word questions
            such as "Why?" still count, only punctuation-only segments are
            dropped.
        questions_key: Metadata key the (capped) hit list is written to;
            an empty value disables that stamp.
        count_key: Metadata key the uncapped question count is written
            to; an empty value disables that stamp.
        ratio_key: Metadata key the question ratio is written to; an
            empty value disables that stamp.
    """

    max_questions: int = 50
    min_words: int = 1
    questions_key: str = "questions"
    count_key: str = "question_count"
    ratio_key: str = "question_ratio"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp detected questions into every document's metadata.

        Args:
            origin_docs: Documents to analyse, in batch order.
            query: Query object (unused; detection depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, each
            carrying the question hits and aggregates in its metadata.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            hits, total = self._detect(doc.text or "")
            if self.questions_key:
                self._stamp(doc, self.questions_key,
                            hits[:self.max_questions])
            if self.count_key:
                self._stamp(doc, self.count_key, len(hits))
            if self.ratio_key:
                self._stamp(doc, self.ratio_key,
                            (len(hits) / total) if total else 0.0)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #

    def _detect(self, text: str) -> Tuple[List[dict], int]:
        """Segment text and classify every sentence.

        Args:
            text: Raw document text (None treated as empty).

        Returns:
            tuple: (hits, total_sentences) where hits is the ordered list
            of question dictionaries and total_sentences counts every
            word-bearing segment, question or not.
        """
        hits: List[dict] = []
        total = 0
        for start, end in self._sentences(text):
            total += 1
            sentence = text[start:end]
            hit = self._classify(sentence)
            if hit is not None:
                hit["text"] = sentence
                hit["span"] = (start, end)
                hits.append(hit)
        return hits, total

    def _classify(self, sentence: str) -> Optional[dict]:
        """Classify one sentence as a question, or not.

        Priority: wh opener > inline tag marker > terminal polar. This
        makes "What is this, right?" an wh question (opener wins) and
        "这是不是什么新花样？" an wh question rather than a tagged one.

        Args:
            sentence: Sentence text, exactly as sliced from the document.

        Returns:
            dict: ``{"kind": ..., "opener": ...}`` for a question,
            otherwise None.
        """
        opener = self._en_opener(sentence)
        if opener is None:
            opener = self._zh_opener(sentence)
        if opener is not None:
            return {"kind": "wh", "opener": opener}

        tag = self._tag_marker(sentence)
        if tag is not None:
            return {"kind": "tagged", "opener": tag}

        if self._ends_with_question_mark(sentence) or \
                self._ends_with_ma(sentence):
            return {"kind": "polar", "opener": None}
        return None

    @staticmethod
    def _en_opener(sentence: str) -> Optional[str]:
        """Return the English interrogative opener of a sentence.

        Only the first word counts ("Do you..." asks, "You do..." states),
        matched case-insensitively with leading punctuation and quotes
        skipped ('"Why now?' opens with why).

        Args:
            sentence: Sentence text.

        Returns:
            str: The lowercased opener (e.g. "why"), or None.
        """
        match = _FIRST_EN_WORD.match(sentence)
        if match:
            word = match.group(1).lower()
            if word in _EN_OPENERS:
                return word
        return None

    @staticmethod
    def _zh_opener(sentence: str) -> Optional[str]:
        """Return the Chinese interrogative token of a sentence.

        Chinese has no spaces or capitalisation to anchor an opener, so
        tokens are matched anywhere in the sentence ("这是什么？" contains
        什么). The earliest match wins; at equal positions the longest
        token wins (为什么 over the 什么 nested inside it). Note the
        inherent heuristic limits: 哪 in 哪里都行 or 几 in 几乎 are
        declarative uses that this token match cannot distinguish.

        Args:
            sentence: Sentence text.

        Returns:
            str: The matched token (e.g. "为什么"), or None.
        """
        best: Optional[str] = None
        best_pos = -1
        for token in _ZH_OPENERS:
            pos = sentence.find(token)
            if pos < 0:
                continue
            if best is None or pos < best_pos:
                best, best_pos = token, pos
        return best

    @staticmethod
    def _tag_marker(sentence: str) -> Optional[str]:
        """Return the inline question marker of a sentence, if any.

        English "..., right?" requires the question mark (the marker is
        the rising tag, and "It works, right." stays declarative). The
        Chinese A-not-A form 是不是 is asked wherever it appears, and the
        confirmation tag 对吗 is asked even under a full stop.

        Args:
            sentence: Sentence text.

        Returns:
            str: "right", "是不是" or "对吗", or None.
        """
        match = _EN_RIGHT_TAG.search(sentence)
        if match and ("?" in match.group(2) or "？" in match.group(2)):
            return "right"
        if _ZH_A_NOT_A in sentence:
            return _ZH_A_NOT_A
        if _TRAILING_PUNCT.sub("", sentence).endswith(_ZH_TAG):
            return _ZH_TAG
        return None

    @staticmethod
    def _ends_with_question_mark(sentence: str) -> bool:
        """Report whether the sentence terminates in a question mark.

        Called only on segmented sentences, whose terminal punctuation run
        (plus closing quotes) is always at the very end, so a simple
        right-strip of closing characters and a last-character check is
        exact.

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when the sentence ends with ? or ？.
        """
        return sentence.rstrip(_CLOSING_CHARS)[-1:] in ("?", "？")

    @staticmethod
    def _ends_with_ma(sentence: str) -> bool:
        """Report whether a Chinese statement ends with the particle 吗.

        Trailing punctuation (。！？,， spaces) is ignored, so "你吃了吗。",
        "你吃了吗？" and a bare "你吃了吗" all qualify. Used for the polar
        question kind; tagged forms like 对吗 are caught earlier.

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when the sentence ends with 吗.
        """
        return _TRAILING_PUNCT.sub("", sentence).endswith(_ZH_POLAR)

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
        ``text == document.text[start:end]`` exactly. Segments below
        ``min_words`` (a bare "？", or a whole document of "Why?" with
        min_words=2) are dropped and never counted as sentences.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int]]: Ordered, non-overlapping (start, end)
            character offsets, each with at least ``min_words`` words.
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
                if self._word_count(text[start:end]) >= self.min_words:
                    spans.append((start, end))
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
            else:
                i += 1
        # Trailing sentence without terminal punctuation ("...and then what").
        if start < length and \
                self._word_count(text[start:length]) >= self.min_words:
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
            -> 'QuestionDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a misconfigured detector
        that silently recorded no questions would be far harder to notice
        in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            QuestionDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_questions") and \
                doc_processor_configer.max_questions is not None:
            cap = doc_processor_configer.max_questions
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_questions must be an integer")
            self.max_questions = cap
            if self.max_questions < 0:
                raise ValueError("max_questions must be >= 0")

        if hasattr(doc_processor_configer, "min_words") and \
                doc_processor_configer.min_words is not None:
            minimum = doc_processor_configer.min_words
            if isinstance(minimum, bool) or not isinstance(minimum, int):
                raise ValueError("min_words must be an integer")
            self.min_words = minimum
            if self.min_words < 1:
                raise ValueError("min_words must be >= 1")

        for attr in ("questions_key", "count_key", "ratio_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        return self
