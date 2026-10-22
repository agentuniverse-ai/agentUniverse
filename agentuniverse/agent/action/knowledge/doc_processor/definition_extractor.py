# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: definition_extractor.py

import logging
import re
import string
from typing import Any, Dict, List, Optional, Set, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

# Sentence boundaries: latin and CJK terminators, semicolons and newlines.
_SENTENCE_RE = re.compile(r'[^.!?;。！？；\n]+[.!?;。！？；\n]*')
_SENTENCE_TERMINATOR_RE = re.compile(r'[.!?;。！？；\n]+$')

# English copula triggers, longest first so multi-word triggers win.
_EN_COPULA_RE = re.compile(r'\b(is\s+defined\s+as|refers\s+to|means|is|are)\b')

# Chinese copula triggers, longest first so 是指/指的是 win over bare 是.
_ZH_COPULA_RE = re.compile('(的定义为|的定义是|指的是|定义为|定义是|是指|所谓|是)')
# Copulas accepted after 所谓X，...
_ZH_SUOWEI_COPULA_RE = re.compile('(就是|即是|是指|指的是|是|即)')

# Definition body stops at a comma / semicolon / colon / period / sentence
# terminator (latin and full-width).
_DEFINITION_BOUNDARY_RE = re.compile(r'[,;:.!?\n、，。；：！？]')

_EN_WORD_CHARS = set(string.ascii_letters + string.digits + "-_'")

_EN_RELATIVE_PRONOUNS: Set[str] = {'which', 'that', 'who', 'whom', 'whose'}
_EN_PRONOUNS: Set[str] = {
    'it', 'this', 'that', 'these', 'those', 'they', 'he', 'she', 'we', 'you',
    'i', 'who', 'which', 'what', 'there', 'here',
}
# Determiners, conjunctions and other function words stripped from the head
# of an English term candidate.
_EN_STRIP_LEADING: Set[str] = {
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'its', 'their', 'his',
    'her', 'our', 'your', 'my', 'one', 'and', 'or', 'but', 'nor', 'yet', 'so',
}
# Single-word English terms that are pure function words are rejected.
_EN_STOPWORDS: Set[str] = {
    'about', 'above', 'after', 'again', 'all', 'also', 'always', 'any', 'both',
    'each', 'either', 'enough', 'even', 'every', 'few', 'how', 'less', 'many',
    'more', 'most', 'much', 'never', 'no', 'nor', 'not', 'now', 'often',
    'only', 'other', 'own', 'same', 'several', 'some', 'sometimes', 'such',
    'than', 'then', 'there', 'therefore', 'thus', 'too', 'usually', 'very',
    'when', 'where', 'whether', 'while', 'why', 'yet', 'just', 'still',
}

_ZH_PRONOUN_START_CHARS = '我你他她它这那其此谁'
_ZH_STOPCHARS: Set[str] = set(
    '的了和与及或在也是都就还又再很被把对从向到为会能可要有不没太则而且并但')


def _is_zh_term_char(ch: str) -> bool:
    """Return True when ch may appear inside a Chinese term candidate."""
    return '\u4e00' <= ch <= '\u9fff' or ch.isalnum() or ch == '·'


class DefinitionExtractor(DocProcessor):
    """Extract term-definition pairs from document text into document metadata.

    This processor mines glossary / concept style knowledge from unstructured
    text. Within each sentence it detects definitional patterns and stamps the
    extracted pairs into ``metadata['definitions']`` so downstream components
    (stores, agents, retrievers) can consume them:

    English patterns:
        - ``X is a/an/the Y``        -> pattern ``is``
        - ``X are Ys``               -> pattern ``are``
        - ``X means Y``              -> pattern ``means``
        - ``X refers to Y``          -> pattern ``refers_to``
        - ``X is defined as Y``      -> pattern ``is_defined_as``
        - ``X, which is Y, ...``     -> pattern ``relative_clause``

    Chinese patterns:
        - ``X是Y``                    -> pattern ``zh_is``
        - ``X是指Y``                  -> pattern ``zh_refers_to``
        - ``X(的)定义为/定义是Y``       -> pattern ``zh_defined_as``
        - ``所谓X，是指Y``             -> pattern ``zh_suowei``

    The term is the noun phrase before the copula (an English word run of up
    to ``max_term_words`` words with leading determiners stripped, or a CJK
    run of at most 12 characters). Guards:
        - existential ``there is / here is`` is NOT treated as a definition;
        - questions (sentences ending with ``?`` / ``？``) are skipped;
        - pronoun terms (it/this/that/they/这/它/...) and single common
          stopword terms are rejected;
        - quoted text receives no special handling (documented limitation).

    Each extracted entry is a dict:
    ``{term, definition, pattern, span: [start, end], truncated}`` where
    ``span`` indexes the original document text and ``truncated`` marks
    definitions cut at ``max_definition_length``.

    Attributes:
        max_definitions: Maximum number of definition entries stamped into
            metadata['definitions'] (extra hits are dropped).
        max_definition_length: Maximum length of the definition text; longer
            definitions are cut and flagged with truncated=True.
        max_term_words: Maximum number of words in an English term candidate.
        dedup_by_term: When True, keep only the first definition per term and
            count repeats in metadata['definition_repeats'].
    """

    max_definitions: int = 50
    max_definition_length: int = 200
    max_term_words: int = 4
    dedup_by_term: bool = True

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Extract term-definition pairs and stamp them into doc metadata.

        Args:
            origin_docs: List of documents to process.
            query: Optional query object (not used in this processor).

        Returns:
            List of documents, unchanged except for the stamped metadata.
        """
        if not origin_docs:
            return []

        self._validate_params()

        logger.info(f"Starting definition extraction on {len(origin_docs)} documents")
        for doc in origin_docs:
            hits = self._extract_definitions(doc.text or '')
            self._stamp_metadata(doc, hits)
            logger.debug(f"Extracted {len(hits)} definition candidates from document {doc.id}")
        logger.info(f"Definition extraction complete for {len(origin_docs)} documents")
        return origin_docs

    def _validate_params(self) -> None:
        """Validate configuration values, raising ValueError when invalid."""
        for field in ('max_definitions', 'max_definition_length', 'max_term_words'):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field} must be a positive integer, got {value!r}")
        if not isinstance(self.dedup_by_term, bool):
            raise ValueError(f"dedup_by_term must be a boolean, got {self.dedup_by_term!r}")

    def _extract_definitions(self, text: str) -> List[Dict[str, Any]]:
        """Extract all definition hits from the given text, in text order.

        Args:
            text: Full document text.

        Returns:
            List of hit dicts with term/definition/pattern/span/truncated.
        """
        hits: List[Dict[str, Any]] = []
        if not text:
            return hits
        for match in _SENTENCE_RE.finditer(text):
            sentence = match.group(0)
            if not sentence.strip():
                continue
            terminators = _SENTENCE_TERMINATOR_RE.search(sentence)
            if terminators and ('?' in terminators.group() or '？' in terminators.group()):
                continue  # questions are excluded
            sentence_hits = self._process_sentence(sentence, match.start())
            hits.extend(sentence_hits)
        return hits

    def _process_sentence(self, sentence: str, offset: int) -> List[Dict[str, Any]]:
        """Run English and Chinese extraction over one sentence.

        Args:
            sentence: Sentence text (may include its terminator punctuation).
            offset: Character offset of the sentence inside the document.

        Returns:
            List of hit dicts for this sentence, in text order.
        """
        hits: List[Dict[str, Any]] = []
        hits.extend(self._extract_english(sentence, offset))
        hits.extend(self._extract_chinese(sentence, offset))
        hits.sort(key=lambda h: h['span'][0])
        return hits

    # ------------------------------------------------------------------ EN --

    def _extract_english(self, sentence: str, offset: int) -> List[Dict[str, Any]]:
        """Detect English definitional patterns within one sentence."""
        hits: List[Dict[str, Any]] = []
        for match in _EN_COPULA_RE.finditer(sentence):
            definition_info = self._cut_definition(sentence, match.end())
            if definition_info is None:
                continue
            definition, truncated, y_start, y_end = definition_info
            term_info = self._extract_en_term(sentence, match.start())
            if term_info is None:
                continue
            term, term_start, relative = term_info
            trigger = re.sub(r'\s+', ' ', match.group(1))
            if trigger.startswith('is defined as'):
                pattern = 'is_defined_as'
            elif trigger.startswith('refers'):
                pattern = 'refers_to'
            elif relative:
                pattern = 'relative_clause'
            elif trigger == 'means':
                pattern = 'means'
            elif trigger == 'are':
                pattern = 'are'
            else:
                pattern = 'is'
            hits.append({
                'term': term,
                'definition': definition,
                'pattern': pattern,
                'span': [offset + term_start, offset + match.end() + y_end],
                'truncated': truncated,
            })
        return hits

    def _extract_en_term(self, sentence: str, copula_start: int) -> Optional[Tuple[str, int, bool]]:
        """Extract the English term candidate ending right before the copula.

        Walks backward from the copula collecting up to ``max_term_words``
        word tokens; relative pronouns (and the comma around them) are skipped
        so that ``X, which is Y`` attributes the term X.

        Args:
            sentence: Sentence text.
            copula_start: Index of the copula match inside the sentence.

        Returns:
            Tuple of (term, term start index, relative clause flag), or None
            when the candidate is rejected by the guards.
        """
        pre = sentence[:copula_start]
        i = len(pre) - 1
        words: List[Tuple[str, int]] = []  # right-to-left while walking
        relative = False
        adjacent: Optional[str] = None
        while i >= 0 and len(words) < self.max_term_words:
            while i >= 0 and pre[i].isspace():
                i -= 1
            if i < 0:
                break
            if pre[i] in _EN_WORD_CHARS:
                j = i
                while j >= 0 and pre[j] in _EN_WORD_CHARS:
                    j -= 1
                word = pre[j + 1:i + 1]
                if adjacent is None:
                    adjacent = word
                if word.lower() in _EN_RELATIVE_PRONOUNS:
                    relative = True
                    i = j
                    continue
                words.append((word, j + 1))
                i = j
            else:
                # Punctuation: cross it only right after a relative pronoun.
                if relative and not words:
                    i -= 1
                    continue
                break
        if not words:
            return None
        if adjacent is not None and adjacent.lower() in ('there', 'here'):
            return None  # existential "there is a" is not a definition
        words.reverse()
        while words and words[0][0].lower() in _EN_STRIP_LEADING:
            words.pop(0)
        if not words:
            return None
        term = ' '.join(word for word, _ in words)
        term_lower = term.lower()
        if term_lower in _EN_PRONOUNS:
            return None
        if len(words) == 1 and term_lower in _EN_STOPWORDS:
            return None
        if not any(ch.isalpha() for ch in term):
            return None
        return term, words[0][1], relative

    # ------------------------------------------------------------------ ZH --

    def _extract_chinese(self, sentence: str, offset: int) -> List[Dict[str, Any]]:
        """Detect Chinese definitional patterns within one sentence."""
        hits: List[Dict[str, Any]] = []
        consumed: Set[int] = set()
        for match in _ZH_COPULA_RE.finditer(sentence):
            if match.start() in consumed:
                continue
            trigger = match.group(0)
            if trigger == '所谓':
                hit = self._extract_suowei(sentence, offset, match)
                if hit is not None:
                    copula_start = hit.pop('_copula_start')
                    consumed.add(copula_start)
                    hits.append(hit)
                continue
            definition_info = self._cut_definition(sentence, match.end())
            if definition_info is None:
                continue
            definition, truncated, y_start, y_end = definition_info
            term_info = self._extract_zh_term(sentence, match.start())
            if term_info is None:
                continue
            term, term_start = term_info
            if trigger in ('的定义为', '定义为', '的定义是', '定义是'):
                pattern = 'zh_defined_as'
            elif trigger in ('指的是', '是指'):
                pattern = 'zh_refers_to'
            else:
                pattern = 'zh_is'
            hits.append({
                'term': term,
                'definition': definition,
                'pattern': pattern,
                'span': [offset + term_start, offset + match.end() + y_end],
                'truncated': truncated,
            })
        return hits

    def _extract_suowei(self, sentence: str, offset: int, match: re.Match) -> Optional[Dict[str, Any]]:
        """Handle the 所谓X，是指Y pattern.

        Args:
            sentence: Sentence text.
            offset: Sentence offset inside the document.
            match: The 所谓 trigger match.

        Returns:
            Hit dict with an extra ``_copula_start`` marker (removed by the
            caller), or None when the pattern does not apply.
        """
        p = match.end()
        j = p
        while j < len(sentence) and _is_zh_term_char(sentence[j]):
            j += 1
        term = sentence[p:j]
        if not term or len(term) > 12:
            return None
        if term[0] in _ZH_PRONOUN_START_CHARS:
            return None
        copula = _ZH_SUOWEI_COPULA_RE.search(sentence, j)
        if copula is None:
            return None
        gap = sentence[j:copula.start()]
        if any(ch not in '，,、:： \t' for ch in gap):
            return None
        definition_info = self._cut_definition(sentence, copula.end())
        if definition_info is None:
            return None
        definition, truncated, y_start, y_end = definition_info
        return {
            'term': term,
            'definition': definition,
            'pattern': 'zh_suowei',
            'span': [offset + p, offset + copula.end() + y_end],
            'truncated': truncated,
            '_copula_start': copula.start(),
        }

    def _extract_zh_term(self, sentence: str, copula_start: int) -> Optional[Tuple[str, int]]:
        """Extract the Chinese term candidate immediately before the copula.

        Collects the CJK/alnum run ending at ``copula_start``; runs longer
        than 12 characters, pronoun-initial runs and single stopword
        characters are rejected.

        Args:
            sentence: Sentence text.
            copula_start: Index of the copula trigger inside the sentence.

        Returns:
            Tuple of (term, term start index) or None when rejected.
        """
        i = copula_start - 1
        count = 0
        while i >= 0 and _is_zh_term_char(sentence[i]):
            count += 1
            if count > 12:
                return None  # CJK runs longer than 12 chars are not terms
            i -= 1
        term = sentence[i + 1:copula_start]
        if not term:
            return None
        if term[0] in _ZH_PRONOUN_START_CHARS:
            return None
        if len(term) == 1 and term in _ZH_STOPCHARS:
            return None
        return term, i + 1

    # -------------------------------------------------------------- shared --

    def _cut_definition(self, sentence: str, start: int) -> Optional[Tuple[str, bool, int, int]]:
        """Cut the definition body after a copula.

        The definition runs from just after the copula up to the first comma,
        semicolon, colon or sentence terminator (or the sentence end), is
        whitespace-trimmed, and is capped at ``max_definition_length``.

        Args:
            sentence: Sentence text.
            start: Index just after the copula inside the sentence.

        Returns:
            Tuple of (definition, truncated, y_start, y_end) with offsets
            relative to ``start``; or None when the definition is empty.
        """
        post = sentence[start:]
        boundary = _DEFINITION_BOUNDARY_RE.search(post)
        end = boundary.start() if boundary else len(post)
        segment = post[:end]
        y_start = len(segment) - len(segment.lstrip())
        y_end = len(segment.rstrip())
        definition = segment.strip()
        if not definition:
            return None
        truncated = False
        if len(definition) > self.max_definition_length:
            definition = definition[:self.max_definition_length]
            y_end = y_start + self.max_definition_length
            truncated = True
        return definition, truncated, y_start, y_end

    # ---------------------------------------------------------- metadata ----

    def _stamp_metadata(self, doc: Document, hits: List[Dict[str, Any]]) -> None:
        """Stamp extracted definitions into the document metadata.

        Args:
            doc: Document being processed.
            hits: All definition hits found in the document text.
        """
        repeats: Dict[str, int] = {}
        if self.dedup_by_term:
            seen: Set[str] = set()
            unique: List[Dict[str, Any]] = []
            for hit in hits:
                key = hit['term'].casefold()
                if key in seen:
                    repeats[hit['term']] = repeats.get(hit['term'], 0) + 1
                else:
                    seen.add(key)
                    unique.append(hit)
            hits = unique
        if doc.metadata is None:
            doc.metadata = {}
        doc.metadata['definitions'] = hits[:self.max_definitions]
        doc.metadata['definition_count'] = len(doc.metadata['definitions'])
        if self.dedup_by_term:
            doc.metadata['definition_repeats'] = repeats

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) -> 'DefinitionExtractor':
        """Initialize the extractor parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing extractor
                parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_definitions"):
            self.max_definitions = doc_processor_configer.max_definitions
        if hasattr(doc_processor_configer, "max_definition_length"):
            self.max_definition_length = doc_processor_configer.max_definition_length
        if hasattr(doc_processor_configer, "max_term_words"):
            self.max_term_words = doc_processor_configer.max_term_words
        if hasattr(doc_processor_configer, "dedup_by_term"):
            self.dedup_by_term = doc_processor_configer.dedup_by_term

        self._validate_params()
        return self
