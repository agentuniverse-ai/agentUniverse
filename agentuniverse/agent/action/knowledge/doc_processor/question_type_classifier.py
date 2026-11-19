# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: question_type_classifier.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks. Mirrors the segmentation shared
# by the QuestionDetector family of components.
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"Are you sure?"' stay
# whole.
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

# The question-type taxonomy. These are the only values that can appear
# in metadata['question_types'][i]['type'], question_type_counts keys and
# dominant_question_type.
_TYPES = ("what", "who", "when", "where", "why", "how", "quantity",
          "which", "yes_no", "choice")

# English interrogative words mapped to taxonomy types, matched whole-word
# and case-insensitively anywhere in the sentence. \bwhat\b also covers
# "what's"; who/whom/whose all fold into the single "who" type.
_EN_WH = (
    ("what", "what"),
    ("whom", "who"),
    ("whose", "who"),
    ("who", "who"),
    ("when", "when"),
    ("where", "where"),
    ("why", "why"),
    ("which", "which"),
    ("how", "how"),
)
_EN_WH_PATTERNS = tuple(
    (word, re.compile(rf"\b{word}\b", re.IGNORECASE)) for word, _ in _EN_WH
)

# Words that, combined with a leading "how", ask about an amount and so
# take precedence over the plain "how" → how mapping (two-word look-ahead).
_HOW_QUANTITY_WORDS = frozenset(("many", "much"))

# English auxiliary verbs. A sentence whose first word is one of them is
# an inversion-shaped polar (yes/no) question: "Is the service running?",
# "Can you help me?".
_EN_AUXILIARIES = frozenset((
    "is", "are", "do", "does", "did", "can", "could", "would", "should",
    "will",
))

# English opinion-solicitation phrase: a mid-sentence "do you think"
# ("What do you think?" is wh-typed by "what" first, but "You, do you
# think this works?" has no wh token at all) marks a yes/no question.
_EN_OPINION_PHRASE = "do you think"

# Chinese A-not-A question marker, unambiguous wherever it appears.
_ZH_A_NOT_A = "是不是"

# Chinese polar question particle 吗 at the end of an otherwise
# declarative-shaped sentence.
_ZH_POLAR = "吗"

# Chinese interrogative tokens mapped to taxonomy types. Chinese has no
# word boundaries or capitalisation, so these are matched anywhere inside
# the sentence. Longest-first at equal positions is enforced by the scan
# (为什么 over the 什么 nested inside it, 什么时候 over 什么).
_ZH_TOKENS = (
    ("什么时候", "when"),
    ("为什么", "why"),
    ("哪里", "where"),
    ("哪儿", "where"),
    ("哪些", "which"),
    ("哪个", "which"),
    ("何时", "when"),
    ("怎么", "how"),
    ("如何", "how"),
    ("多少", "quantity"),
    ("什么", "what"),
    ("还是", "choice"),
    ("谁", "who"),
    ("几", "quantity"),
)

# Standalone English "or" between whitespace-separated alternatives
# ("Tea or coffee?"). \s on both sides keeps "for", "word" or "actor"
# from matching; the surrounding words are the "noun-ish alternatives"
# approximation — real part-of-speech tagging would need a dependency.
_EN_OR = re.compile(r"\s+or\s+", re.IGNORECASE)

# First alphabetic run of a sentence, skipping leading punctuation,
# quotes and digits ("\"Why" -> "why").
_FIRST_EN_WORD = re.compile(r"^[^\w]*([A-Za-z]+)")

# First alphabetic run after a given offset, skipping punctuation and
# spaces — the two-word look-ahead word after a matched "how". No ^
# anchor: it is applied via Pattern.match(string, pos), and ^ only
# matches at the true start of the string, not at pos.
_NEXT_EN_WORD = re.compile(r"[^A-Za-z0-9]*([A-Za-z]+)")

# Trailing non-alphanumeric tail of a sentence (terminal punctuation run
# plus closing quotes), used when looking at what precedes it.
_TRAILING_PUNCT = re.compile(r"[^A-Za-z0-9\u4e00-\u9fff]+$")


class QuestionTypeClassifier(DocProcessor):
    """Classify detected questions into a ten-type taxonomy and stamp the
    types into document metadata.

    Question detection (QuestionDetector) answers *whether* a sentence
    asks; FAQ mining, intent routing and QA-pair ranking quickly also need
    to know *what kind* of thing is being asked, because a "why" question
    wants reasons, a "how many" question wants numbers and a yes/no
    question wants a boolean — mixing them degrades every downstream
    matcher. This pre-processing component walks every document, splits it
    into sentences with the same conservative segmentation as the
    QuestionDetector family, keeps only the interrogative ones and maps
    each to exactly one type of the taxonomy ``what | who | when | where |
    why | how | quantity | which | yes_no | choice`` — offline,
    deterministically, without any model call — then stamps the hits into
    ``metadata['question_types']`` together with per-type counts and the
    dominant type, so FAQ corpora can be sliced by question kind.

    A sentence counts as interrogative when its terminal punctuation run
    carries ``?`` / ``？``, when it opens with an English interrogative or
    auxiliary word (terminal punctuation not required: "How to configure
    this." still counts), or when it contains a Chinese interrogative
    marker (为什么 / 什么 / 谁 / 何时 / 什么时候 / 哪里 / 哪儿 / 哪个 / 哪些 /
    怎么 / 如何 / 多少 / 几 / 还是 / 是不是, or a final 吗). Declarative
    sentences are never reported.

    Each interrogative sentence is typed by the first interrogative token
    found, in this documented priority order:

    1. **English wh word** — the earliest whole-word, case-insensitive
       match anywhere in the sentence (a wh word need not be the first
       word: "You did what?" is typed ``what``). what/what's → what;
       who/whom/whose → who; when → when; where → where; why → why;
       which → which; how → how, **except** that a two-word look-ahead
       promotes "how many" / "how much" to ``quantity`` — two-word
       evidence always outranks the single word.
    2. **Chinese interrogative token** — the earliest match anywhere in
       the sentence, longest token winning at the same position: 为什么 →
       why, 什么 → what, 谁 → who, 何时 / 什么时候 → when (什么时候 outranks
       the 什么 nested inside it), 哪里 / 哪儿 → where, 哪个 / 哪些 →
       which, 怎么 / 如何 → how, 多少 (and 几) → quantity, 还是 → choice.
    3. **Polar shape** — no wh token anywhere, but the sentence opens
       with an English auxiliary (is / are / do / does / did / can /
       could / would / should / will), contains "do you think", or
       contains the Chinese A-not-A form 是不是 → ``yes_no``.
    4. **English alternative** — a standalone " or " between
       whitespace-separated alternatives and no wh token → ``choice``.
       (An auxiliary-initial alternative question such as "Would you
       like tea or coffee?" is typed ``yes_no`` by rule 3 — the earlier
       rule wins.)
    5. **Chinese polar particle** — the sentence ends with 吗 →
       ``yes_no``.
    6. **Terminal fallback** — nothing matched; the sentence is
       interrogative only through its terminal question mark, i.e. a
       statement-shaped question with rising intonation ("She left?",
       "真的？") → ``yes_no``.

    Note the priority consequences: English evidence outranks Chinese
    evidence in mixed sentences, two-word constructs (how many / 多少-style
    amount questions, 什么时候) outrank their single-word substrings, and
    the heuristic limits inherent to token matching are inherited: 还是 in
    "还是算了" (let it go) or 几 in 几乎 are declarative uses this component
    cannot distinguish.

    Each hit is ``{"text": str, "span": (start, end), "type": str}`` where
    ``span`` are character offsets into the original document text with
    ``text == document.text[start:end]`` truncated to the first
    ``preview_chars`` characters (default 100), spans are non-overlapping
    and ordered, and ``type`` is one of the taxonomy above.

    Aggregates land next to the list: ``metadata['question_type_counts']``
    maps every type to its **uncapped** occurrence count over the whole
    document, and ``metadata['dominant_question_type']`` is the most
    frequent type with ties broken alphabetically (None when the document
    asks nothing) — both computed over all questions, so capping the hit
    list never skews the aggregates. Segments with fewer than ``min_words``
    words are ignored entirely.

    Every document passes through untouched — text, id and existing
    metadata entries are never modified, and metadata mappings are copied
    before mutation. The component is pure Python with zero dependencies
    and deterministic across runs. It is complementary to QuestionDetector
    (which only *detects* questions) and SectionRoleClassifier (which
    classifies headings): this one supplies the *type* dimension.

    Attributes:
        max_question_types: Maximum number of hits kept in
            ``metadata['question_types']``; must be >= 0. The counts
            aggregate is always uncapped, so a capped list never hides
            the true magnitude.
        min_words: Minimum number of words (whitespace tokens containing
            at least one alphanumeric character) for a segment to count
            as a sentence; must be >= 1. Default 1 — single-word
            questions such as "Why?" still count, only punctuation-only
            segments are dropped.
        preview_chars: Maximum number of characters of each question kept
            in its ``text`` field; must be >= 1. Default 100.
        question_types_key: Metadata key the (capped) hit list is written
            to; an empty value disables that stamp.
        counts_key: Metadata key the uncapped per-type count mapping is
            written to; an empty value disables that stamp.
        dominant_key: Metadata key the dominant type is written to; an
            empty value disables that stamp.
    """

    max_question_types: int = 50
    min_words: int = 1
    preview_chars: int = 100
    question_types_key: str = "question_types"
    counts_key: str = "question_type_counts"
    dominant_key: str = "dominant_question_type"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp classified question types into every document's metadata.

        Args:
            origin_docs: Documents to analyse, in batch order.
            query: Query object (unused; classification depends only on
                the documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, each
            carrying the typed question hits and aggregates in its
            metadata.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            hits = self._classify_text(doc.text or "")
            if self.question_types_key:
                self._stamp(doc, self.question_types_key,
                            hits[:self.max_question_types])
            if self.counts_key:
                counts = {}
                for hit in hits:
                    counts[hit["type"]] = counts.get(hit["type"], 0) + 1
                self._stamp(doc, self.counts_key, counts)
            if self.dominant_key:
                self._stamp(doc, self.dominant_key,
                            self._dominant(hits))
        return origin_docs

    # ------------------------------------------------------------------ #
    # Classification
    # ------------------------------------------------------------------ #

    def _classify_text(self, text: str) -> List[dict]:
        """Segment text, keep interrogative sentences and type each one.

        Args:
            text: Raw document text (None treated as empty).

        Returns:
            List[dict]: Ordered hits ``{"text", "span", "type"}`` for
            every interrogative sentence; declaratives are skipped.
        """
        hits: List[dict] = []
        for start, end in self._sentences(text):
            sentence = text[start:end]
            if not self._is_question(sentence):
                continue
            qtype = self._question_type(sentence)
            if qtype is None:
                continue
            hits.append({
                "text": sentence[:self.preview_chars],
                "span": (start, end),
                "type": qtype,
            })
        return hits

    def _is_question(self, sentence: str) -> bool:
        """Report whether a sentence asks at all.

        Gate, in the same spirit as QuestionDetector: a terminal question
        mark, an English interrogative/auxiliary opener (terminal
        punctuation not required), a Chinese interrogative token or
        A-not-A marker anywhere, a final 吗, or a mid-sentence "do you
        think".

        Args:
            sentence: Sentence text, exactly as sliced from the document.

        Returns:
            bool: True when the sentence is interrogative.
        """
        if self._ends_with_question_mark(sentence):
            return True
        match = _FIRST_EN_WORD.match(sentence)
        if match:
            word = match.group(1).lower()
            if word in _EN_AUXILIARIES or \
                    any(word == wh for wh, _ in _EN_WH):
                return True
        if _EN_OPINION_PHRASE in sentence.lower():
            return True
        for token, _ in _ZH_TOKENS:
            if token in sentence:
                return True
        if _ZH_A_NOT_A in sentence:
            return True
        return self._ends_with_ma(sentence)

    def _question_type(self, sentence: str) -> Optional[str]:
        """Map one interrogative sentence to its taxonomy type.

        Follows the documented priority order: English wh word (with the
        how many / how much look-ahead) > Chinese token > auxiliary /
        opinion / A-not-A polar shape > English "or" alternative > final
        吗 > terminal-question-mark fallback.

        Args:
            sentence: Sentence text, already known to be interrogative.

        Returns:
            str: One of the taxonomy types, or None when no rule fires
            (cannot happen for sentences admitted by ``_is_question``
            except a bare "do you think" hit, which falls back to
            yes_no).
        """
        qtype = self._en_wh_type(sentence)
        if qtype is not None:
            return qtype

        qtype = self._zh_type(sentence)
        if qtype is not None:
            return qtype

        match = _FIRST_EN_WORD.match(sentence)
        if (match and match.group(1).lower() in _EN_AUXILIARIES) or \
                _EN_OPINION_PHRASE in sentence.lower() or \
                _ZH_A_NOT_A in sentence:
            return "yes_no"

        if _EN_OR.search(sentence):
            return "choice"

        if self._ends_with_ma(sentence):
            return "yes_no"

        if self._ends_with_question_mark(sentence):
            return "yes_no"
        return None

    @staticmethod
    def _en_wh_type(sentence: str) -> Optional[str]:
        """Return the type of the earliest English wh word in the sentence.

        Every wh word is matched whole-word and case-insensitively
        anywhere in the sentence ("You did what?" → what); the earliest
        match wins. When that match is "how", one word of look-ahead
        promotes "how many" / "how much" to the quantity type before the
        plain how mapping applies — two-word evidence outranks the
        single word.

        Args:
            sentence: Sentence text.

        Returns:
            str: The taxonomy type of the earliest wh word, with the
            how-many/how-much promotion applied, or None.
        """
        best: Optional[str] = None
        best_pos = -1
        best_end = -1
        for word, pattern in _EN_WH_PATTERNS:
            match = pattern.search(sentence)
            if match and (best_pos < 0 or match.start() < best_pos):
                best, best_pos, best_end = word, match.start(), match.end()
        if best is None:
            return None
        if best == "how":
            nxt = _NEXT_EN_WORD.match(sentence, best_end)
            if nxt and nxt.group(1).lower() in _HOW_QUANTITY_WORDS:
                return "quantity"
        for word, qtype in _EN_WH:
            if word == best:
                return qtype
        return None

    @staticmethod
    def _zh_type(sentence: str) -> Optional[str]:
        """Return the type of the earliest Chinese interrogative token.

        Tokens are matched anywhere in the sentence (Chinese has no
        spaces or capitalisation to anchor an opener). The earliest match
        wins; at equal positions the longest token wins — 为什么 over the
        什么 nested inside it, 什么时候 over 什么. Note the inherited
        heuristic limits: 还是 in "还是算了" or 几 in 几乎 are declarative
        uses this token match cannot distinguish.

        Args:
            sentence: Sentence text.

        Returns:
            str: The taxonomy type of the matched token, or None.
        """
        best_type: Optional[str] = None
        best_pos = -1
        best_len = -1
        for token, qtype in _ZH_TOKENS:
            pos = sentence.find(token)
            if pos < 0:
                continue
            if best_pos < 0 or pos < best_pos or \
                    (pos == best_pos and len(token) > best_len):
                best_type, best_pos, best_len = qtype, pos, len(token)
        return best_type

    @staticmethod
    def _ends_with_question_mark(sentence: str) -> bool:
        """Report whether the sentence's terminal punctuation asks.

        The terminal punctuation run (plus closing quotes) of a segmented
        sentence is always a suffix, so stripping the closing characters
        and inspecting that run as a whole is exact. A question mark
        anywhere in the run counts — emphatic runs such as "She left?!"
        or "你来了？！" ask just as much as run-final "?".

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when the terminal run contains ? or ？.
        """
        stripped = sentence.rstrip(_CLOSING_CHARS)
        run = stripped.rstrip(_TERMINAL_CHARS)
        terminal_run = stripped[len(run):]
        return "?" in terminal_run or "？" in terminal_run

    @staticmethod
    def _ends_with_ma(sentence: str) -> bool:
        """Report whether a Chinese statement ends with the particle 吗.

        Trailing punctuation (。！？,， spaces) is ignored, so "你吃了吗。",
        "你吃了吗？" and a bare "你吃了吗" all qualify. Tagged forms such as
        对吗 end with 吗 as well and are polar questions.

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when the sentence ends with 吗.
        """
        return _TRAILING_PUNCT.sub("", sentence).endswith(_ZH_POLAR)

    @staticmethod
    def _dominant(hits: List[dict]) -> Optional[str]:
        """Return the most frequent type, ties broken alphabetically.

        Args:
            hits: The full (uncapped) list of typed question hits.

        Returns:
            str: The dominant taxonomy type, or None for no hits.
        """
        if not hits:
            return None
        counts = {}
        for hit in hits:
            counts[hit["type"]] = counts.get(hit["type"], 0) + 1
        top = max(counts.values())
        return min(t for t, c in counts.items() if c == top)

    # ------------------------------------------------------------------ #
    # Segmentation (shared design with the QuestionDetector family)
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
        ``min_words`` (a bare "？") are dropped and never counted.

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
            -> 'QuestionTypeClassifier':
        """Initialize and validate the classifier from component configuration.

        Validation happens eagerly at load time: a misconfigured
        classifier that silently typed no questions would be far harder
        to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            QuestionTypeClassifier: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_question_types") and \
                doc_processor_configer.max_question_types is not None:
            cap = doc_processor_configer.max_question_types
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_question_types must be an integer")
            self.max_question_types = cap
            if self.max_question_types < 0:
                raise ValueError("max_question_types must be >= 0")

        if hasattr(doc_processor_configer, "min_words") and \
                doc_processor_configer.min_words is not None:
            minimum = doc_processor_configer.min_words
            if isinstance(minimum, bool) or not isinstance(minimum, int):
                raise ValueError("min_words must be an integer")
            self.min_words = minimum
            if self.min_words < 1:
                raise ValueError("min_words must be >= 1")

        if hasattr(doc_processor_configer, "preview_chars") and \
                doc_processor_configer.preview_chars is not None:
            preview = doc_processor_configer.preview_chars
            if isinstance(preview, bool) or not isinstance(preview, int):
                raise ValueError("preview_chars must be an integer")
            self.preview_chars = preview
            if self.preview_chars < 1:
                raise ValueError("preview_chars must be >= 1")

        for attr in ("question_types_key", "counts_key", "dominant_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        return self
