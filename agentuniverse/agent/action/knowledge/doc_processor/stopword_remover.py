# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: stopword_remover.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# --------------------------------------------------------------------------- #
# Built-in stopword inventories — conservative on purpose.
# --------------------------------------------------------------------------- #

# 120 high-frequency English function words: articles, conjunctions,
# pronouns, be/do/have and modal verbs, prepositions, and a handful of
# quantifier adverbs. Content-bearing words (nouns, lexical verbs,
# adjectives) are never listed, so removal thins grammatical glue without
# changing what a document is about.
_EN_STOPWORDS = frozenset((
    # articles
    'a', 'an', 'the',
    # conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'if', 'then', 'than', 'that',
    'because', 'while', 'when', 'where', 'although', 'though', 'unless',
    'until', 'since', 'after', 'before',
    # pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
    'them', 'my', 'your', 'his', 'its', 'our', 'their', 'this', 'these',
    'those', 'who', 'whom', 'whose', 'which', 'what',
    # be / do / have and modal verbs
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'do', 'does',
    'did', 'have', 'has', 'had', 'will', 'would', 'shall', 'should', 'can',
    'could', 'may', 'might', 'must',
    # prepositions
    'of', 'to', 'in', 'on', 'at', 'by', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'above', 'below', 'from', 'up',
    'down', 'out', 'off', 'over', 'under', 'again', 'across', 'near',
    'past',
    # quantifiers / adverbs / negation
    'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'too',
    'very', 'just', 'as',
))

# 81 single CJK characters: aspect/possessive particles, modal suffixes,
# conjunctions, coverbs, pronouns, high-frequency adverbs and the two
# existential/quantity words 有 and 个. Each entry is one character, which
# is what the char-level Chinese pass can safely remove without a word
# segmenter.
_ZH_STOPWORDS = frozenset((
    # particles and sentence-final markers
    '的', '了', '着', '过', '地', '得', '是', '之', '者', '也', '乎', '矣',
    '呢', '吧', '吗', '啊', '呀', '哦',
    # conjunctions
    '和', '与', '及', '或', '但', '而', '且', '并', '若', '则', '虽', '因',
    '故',
    # coverbs / prepositions
    '在', '从', '向', '往', '对', '为', '以', '于', '被', '把', '将', '给',
    '让', '比',
    # pronouns and determiners
    '我', '你', '他', '她', '它', '们', '这', '那', '其', '此', '某', '各',
    '每',
    # adverbs, negation, degree
    '不', '没', '就', '还', '才', '只', '再', '又', '更', '最', '很', '太',
    '挺', '极', '稍', '略', '曾', '已', '正', '未',
    # existential and measure
    '有', '个', '些',
))

_BUILTIN_STOPWORDS = {'en': _EN_STOPWORDS, 'zh': _ZH_STOPWORDS}

# Unified CJK ideograph ranges: Extension A, the main block, and the
# compatibility ideographs.
_CJK_CLASS = '\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufa6d'

# One scanning regex, tried left to right at every position:
#   1. a Latin word — letters plus at most one internal apostrophe —
#      carrying any punctuation glued to either side of it (quotes,
#      commas, sentence periods, digits directly attached, ...). The
#      named group captures the bare word core used for stopword lookup;
#   2. a run of CJK ideographs (passed through verbatim by the English
#      pass);
#   3. any other non-whitespace run (digits, standalone punctuation,
#      other scripts such as Cyrillic or Greek), also passed through.
_CHUNK_RE = re.compile(
    '[^\\sA-Za-z' + _CJK_CLASS + ']*'
    "(?P<word>[A-Za-z]+(?:'[A-Za-z]+)?)"
    '[^\\sA-Za-z' + _CJK_CLASS + ']*'
    '|[' + _CJK_CLASS + ']+'
    '|[^\\sA-Za-z' + _CJK_CLASS + ']+'
)


def _is_cjk(ch: str) -> bool:
    """Report whether one character is a CJK ideograph.

    Args:
        ch: Single character.

    Returns:
        bool: True inside the unified CJK ideograph ranges (Extension A,
        the main block, or the compatibility block).
    """
    return ('\u3400' <= ch <= '\u4dbf'
            or '\u4e00' <= ch <= '\u9fff'
            or '\uf900' <= ch <= '\ufa6d')


class StopwordRemover(DocProcessor):
    """Strip stopwords from document text before splitting and embedding.

    Function words — *the*, *is*, *of*, 的, 了, 是 — carry almost no
    retrieval signal but a large share of every document's mass. Left in
    place they dilute chunk embeddings and let near-identical boilerplate
    phrasing dominate similarity. This processor rewrites each document's
    text with its stopword tokens deleted, addressing the pre-processing
    direction of issue #258. It is deliberately distinct from the
    neighbouring components: ``TextNormalizer`` repairs unicode and
    whitespace defects but removes no vocabulary, and ``KeywordExtractor``
    ranks top terms into metadata without rewriting the text — this
    component is the one that actually thins the text itself, cheaply and
    before any splitter or embedding model runs.

    Two script-specific passes run over the text, gated by ``languages``:

    * **English word pass.** The text is scanned into chunks with a single
      regular expression: a Latin word (letters plus at most one internal
      apostrophe, so contractions such as *don't* stay whole) together
      with any punctuation glued to either side of it; runs of CJK
      ideographs; and any other non-whitespace run (digits, standalone
      punctuation, other scripts). A word chunk whose lowercased core is
      in the active stopword set is dropped — punctuation attached to a
      dropped stopword goes with it — and the surviving chunks are
      re-joined with single spaces, which normalizes runs of whitespace
      (tabs, newlines, multiples) between chunks to one space. CJK runs
      are never matched against the English list, and intra-word hyphens
      or abbreviation periods act as chunk boundaries.
    * **Chinese character pass.** Every CJK ideograph in the text that is
      in the active stopword set is deleted, one character at a time.
      This char-level strategy needs no word segmenter, which keeps the
      component a pure-stdlib, offline, deterministic pass that is safe
      for non-segmented Chinese; the trade-off is that the stopword list
      must stay conservative. Only the characters themselves are removed
      — whitespace they leave behind is kept (a lone gap in the middle of
      the text survives), and leading/trailing whitespace left over after
      any removal is stripped from the final text.

    The two built-in inventories are compact by design — 120 English
    function words and 81 single CJK characters — chosen for precision
    over recall. ``custom_stopwords`` extends them with domain-specific
    entries (list addition); with ``replace_builtin`` the custom list
    replaces them entirely. A custom entry only takes effect for the pass
    whose script it belongs to and whose language is enabled: Latin words
    are matched by the English word pass, single CJK characters by the
    Chinese character pass.

    Every processed document — in either mode — is stamped through a
    copied metadata mapping with ``metadata['stopword_removed_count']``
    and ``metadata['stopword_ratio']``. The ratio follows the formula

    ::

        stopword_ratio = removed / considered

    where ``considered`` counts, over the *original* text and restricted
    to the enabled languages, every Latin word chunk (English pass) plus
    every CJK ideograph character (Chinese pass), and ``removed`` counts
    the subset of those found in the active stopword set. A document with
    nothing to consider (empty, punctuation-only, or all-other-script
    text) gets a ratio of 0.0, never a division error. Documents are
    neither dropped nor reordered — the output list maps 1:1 onto the
    input — and ``mode='tag'`` stamps the same statistics while leaving
    the text byte-identical, for pipelines that only want the signal.

    Removal can legitimately produce an empty string (a stopword-only
    document); such documents are kept with empty text and a ratio of
    1.0, and filtering them out is left to a downstream component such as
    ``ThresholdFilter``.

    Attributes:
        languages: Language codes whose passes run — 'en' enables the
            Latin word pass, 'zh' the CJK character pass. Default
            ``['en', 'zh']`` so mixed corpora are handled in one go.
        custom_stopwords: Optional extra stopwords merged into the active
            set; default None keeps only the built-ins.
        replace_builtin: When true, ``custom_stopwords`` replaces the
            built-in lists instead of extending them. Requires a
            non-empty ``custom_stopwords``.
        mode: 'remove' (default) rewrites the text; 'tag' leaves the text
            untouched and only stamps the metadata statistics.
    """

    languages: List[str] = ['en', 'zh']
    custom_stopwords: Optional[List[str]] = None
    replace_builtin: bool = False
    mode: str = 'remove'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Rewrite (or tag) every document with stopword statistics.

        Args:
            origin_docs: Documents to process, in batch order.
            query: Query object (unused; stopword removal depends only on
                the documents' own text).

        Returns:
            List[Document]: The same document objects, in the same order,
            with stopwords removed from the text (unless tagging) and
            stopword statistics stamped into the metadata.
        """
        if not origin_docs:
            return []

        stopwords = self._active_stopwords()
        use_en = 'en' in self.languages
        use_zh = 'zh' in self.languages

        for doc in origin_docs:
            text = doc.text or ''

            en_tokens = en_removed = 0
            kept_chunks: List[str] = []
            if use_en:
                en_tokens, en_removed, kept_chunks = self._en_scan(
                    text, stopwords)

            zh_tokens = zh_removed = 0
            if use_zh:
                zh_tokens, zh_removed = self._zh_scan(text, stopwords)

            considered = en_tokens + zh_tokens
            removed = en_removed + zh_removed
            ratio = removed / considered if considered else 0.0

            if self.mode == 'remove':
                new_text = ' '.join(kept_chunks) if use_en else text
                if use_zh:
                    new_text = self._zh_strip(new_text, stopwords)
                doc.text = new_text.strip()

            self._stamp(doc, 'stopword_removed_count', removed)
            self._stamp(doc, 'stopword_ratio', ratio)

        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Text passes
    # ------------------------------------------------------------------ #

    @staticmethod
    def _en_scan(text: str, stopwords: frozenset) -> Tuple[int, int, List[str]]:
        """Scan text into English-pass chunks, counting and filtering.

        Args:
            text: Original document text.
            stopwords: Active stopword set.

        Returns:
            Tuple[int, int, List[str]]: (word chunk count, stopword hits,
            surviving chunks in order).
        """
        tokens = removed = 0
        kept: List[str] = []
        for match in _CHUNK_RE.finditer(text):
            word = match.group('word')
            if word is not None:
                tokens += 1
                if word.lower() not in stopwords:
                    kept.append(match.group(0))
                else:
                    removed += 1
            else:
                kept.append(match.group(0))
        return tokens, removed, kept

    @staticmethod
    def _zh_scan(text: str, stopwords: frozenset) -> Tuple[int, int]:
        """Count CJK ideographs and stopword hits among them.

        Args:
            text: Original document text.
            stopwords: Active stopword set.

        Returns:
            Tuple[int, int]: (CJK character count, stopword hits).
        """
        tokens = removed = 0
        for ch in text:
            if _is_cjk(ch):
                tokens += 1
                if ch in stopwords:
                    removed += 1
        return tokens, removed

    @staticmethod
    def _zh_strip(text: str, stopwords: frozenset) -> str:
        """Delete stopword CJK characters from text, keeping all else.

        Args:
            text: Text after the English pass (or the original when the
                English pass is disabled).
            stopwords: Active stopword set.

        Returns:
            str: Text without stopword CJK characters; non-CJK characters
            (including Latin stopwords) and whitespace are untouched.
        """
        return ''.join(ch for ch in text
                       if not (_is_cjk(ch) and ch in stopwords))

    def _active_stopwords(self) -> frozenset:
        """Build the stopword set the enabled passes will consult.

        With ``replace_builtin`` the set is exactly ``custom_stopwords``;
        otherwise it is the built-in lists of every enabled language plus
        the custom entries.

        Returns:
            frozenset: Active stopword set (possibly empty).
        """
        if self.replace_builtin:
            return frozenset(self.custom_stopwords or [])
        words = set(self.custom_stopwords or [])
        for language in self.languages:
            words |= _BUILTIN_STOPWORDS.get(language, frozenset())
        return frozenset(words)

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
            -> 'StopwordRemover':
        """Initialize and validate the remover from component configuration.

        Validation happens eagerly at load time: a silently misconfigured
        remover (unknown language code, string instead of list, tagging
        mode typo) would be far harder to notice in production than a
        startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            StopwordRemover: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, 'languages') and \
                doc_processor_configer.languages is not None:
            configured = doc_processor_configer.languages
            if isinstance(configured, str) or \
                    not isinstance(configured, (list, tuple)):
                raise ValueError(
                    "languages must be a list of language codes, e.g. "
                    "['en', 'zh']")
            normalized: List[str] = []
            for code in configured:
                if not isinstance(code, str) or code not in ('en', 'zh'):
                    raise ValueError(
                        f"unsupported language code {code!r}; expected "
                        "'en' or 'zh'")
                if code not in normalized:
                    normalized.append(code)
            if not normalized:
                raise ValueError("languages must not be empty")
            self.languages = normalized

        if hasattr(doc_processor_configer, 'custom_stopwords') and \
                doc_processor_configer.custom_stopwords is not None:
            configured = doc_processor_configer.custom_stopwords
            if isinstance(configured, str) or \
                    not isinstance(configured, (list, tuple)):
                raise ValueError("custom_stopwords must be a list of strings")
            words: List[str] = []
            for word in configured:
                if not isinstance(word, str) or not word:
                    raise ValueError(
                        "custom_stopwords entries must be non-empty strings")
                if word not in words:
                    words.append(word)
            self.custom_stopwords = words

        if hasattr(doc_processor_configer, 'replace_builtin') and \
                doc_processor_configer.replace_builtin is not None:
            self.replace_builtin = bool(doc_processor_configer.replace_builtin)

        if hasattr(doc_processor_configer, 'mode') and \
                doc_processor_configer.mode is not None:
            configured = doc_processor_configer.mode
            if not isinstance(configured, str) or \
                    configured not in ('remove', 'tag'):
                raise ValueError(
                    f"mode must be 'remove' or 'tag', got {configured!r}")
            self.mode = configured

        if self.replace_builtin and not self.custom_stopwords:
            raise ValueError(
                "replace_builtin=true requires a non-empty "
                "custom_stopwords list")

        return self
