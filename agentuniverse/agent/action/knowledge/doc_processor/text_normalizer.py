# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: text_normalizer.py

import re
import unicodedata
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Unicode normalization forms accepted by `unicode_normalization`.
_NORMALIZATION_FORMS = ('NFC', 'NFKC', 'NFD', 'NFKD')

# Fullwidth forms U+FF01..U+FF5E map one-to-one onto ASCII U+0021..U+007E
# by shifting the code point by 0xFEE0, and the ideographic space U+3000
# maps to a plain space. Halfwidth katakana (U+FF61..U+FF9F) have no ASCII
# counterpart and are deliberately left untouched.
_FULLWIDTH_SHIFT = 0xFEE0
_FULLWIDTH_SOURCES = {chr(code): chr(code - _FULLWIDTH_SHIFT)
                      for code in range(0xFF01, 0xFF5F)}
_FULLWIDTH_SOURCES['\u3000'] = ' '
# str.translate expects ordinal keys, hence the maketrans conversion.
_FULLWIDTH_TABLE = str.maketrans(_FULLWIDTH_SOURCES)

# Typographic quotes and dashes replaced with their ASCII counterparts.
# The minus sign (U+2212) is deliberately absent: folding it into a hyphen
# would corrupt formulas and numeric ranges.
_SMART_REPLACEMENTS = {
    '\u2018': "'",  # left single quotation mark
    '\u2019': "'",  # right single quotation mark
    '\u201a': ',',  # single low-9 quotation mark
    '\u201b': "'",  # single high-reversed-9 quotation mark
    '\u201c': '"',  # left double quotation mark
    '\u201d': '"',  # right double quotation mark
    '\u201e': '"',  # double low-9 quotation mark
    '\u201f': '"',  # double high-reversed-9 quotation mark
    '\u2013': '-',  # en dash
    '\u2014': '-',  # em dash
    '\u2015': '-',  # horizontal bar
}
_SMART_TABLE = str.maketrans(_SMART_REPLACEMENTS)

# URL pattern: an explicit scheme or a www. host, up to the first
# whitespace character.
_URL_PATTERN = re.compile(r'(?:https?://|www\.)\S+', re.IGNORECASE)
# Sentence punctuation clinging to a URL tail belongs to the sentence,
# not to the URL; it is preserved after the mask token.
_URL_TRAILING_PUNCT = '.,;:!?)\'"'

# Order in which enabled operations execute and are reported in metadata.
_OPERATION_ORDER = (
    'unicode_normalization', 'fullwidth_to_ascii', 'smart_quotes',
    'strip_control_chars', 'whitespace', 'lowercase', 'url_masking',
)


class TextNormalizer(DocProcessor):
    """Normalize document text before splitting and embedding.

    Documents collected from heterogeneous sources — office exporters, PDF
    extractors, chat logs, pasted web pages — carry the same words in
    visually identical but byte-wise different spellings: decomposed
    accents, fullwidth Latin letters and digits, curly quotes and em
    dashes, non-breaking spaces, stray control bytes, CRLF line endings
    and quadruple blank lines. Downstream components feel every one of
    these: splitters cut chunks at inconsistent boundaries, near-
    duplicate detectors miss matches that differ only in width or quotes,
    and embedding models spend capacity distinguishing typographic
    variants of the same token. This processor rewrites every document's
    text through a fixed pipeline of small, individually toggleable
    canonicalization steps so that later stages see one consistent
    spelling per word:

    1. ``unicode_normalization`` — apply a Unicode normalization form
       (default NFC; NFKC/NFD/NFKD selectable, empty string disables).
       NFC folds combining accents back into precomposed characters
       (``e`` + U+0301 becomes ``é``), so visually identical accents hash
       and tokenize identically.
    2. ``fullwidth_to_ascii`` — fold fullwidth ASCII forms (ＡＢＣ１２３，
       ：，！？) onto their halfwidth counterparts and the ideographic
       space onto a plain space. CJK ideographs and CJK-only punctuation
       (。、《》) have no ASCII counterpart and pass through untouched.
    3. ``smart_quotes`` — replace typographic quotes and dashes (curly
       single/double quotes, en/em dashes) with their ASCII equivalents.
       The minus sign U+2212 is deliberately preserved.
    4. ``strip_control_chars`` — delete every C0/C1 control character
       (Unicode category Cc) except ``\\n`` and ``\\t``; ``\\r`` is
       removed here, so CRLF pairs collapse to ``\\n`` even when the
       whitespace step is disabled.
    5. ``whitespace`` — canonicalize newlines (CRLF/CR → LF), turn every
       remaining non-newline whitespace (tabs, non-breaking spaces,
       U+3000) into plain spaces, collapse space runs, strip line edges,
       cap consecutive blank lines at ``max_blank_lines`` and drop
       leading/trailing blank lines. CJK text without spaces passes
       through unchanged.
    6. ``lowercase`` — fold text to lowercase (off by default; enable for
       case-insensitive retrieval pipelines).
    7. ``url_masking`` — replace URLs (``http(s)://`` or ``www.`` hosts)
       with ``url_mask_token`` so that volatile link noise stops
       dominating embeddings (off by default). Trailing sentence
       punctuation is kept out of the mask; when ``lowercase`` is also
       enabled the token is inserted already lowercased, so running the
       normalizer twice leaves the text unchanged.

    Every operation is pure ``str``/``unicodedata``/``re`` work: the
    component is deterministic, offline and dependency-free. Processing
    is idempotent — normalizing already-normalized text returns it
    unchanged. The list of operations actually executed is stamped into
    ``metadata[applied_key]`` (default key ``normalization_applied``) via
    a copied mapping, so pipeline observability comes for free; ``id``,
    pre-existing metadata and (when all operations are disabled) the
    text itself are never modified.

    Attributes:
        unicode_normalization: Unicode normalization form — 'NFC'
            (default), 'NFKC', 'NFD', 'NFKD' — or '' to disable.
        fullwidth_to_ascii: When true (default), fold fullwidth ASCII
            forms and the ideographic space onto halfwidth equivalents.
        smart_quotes: When true (default), replace typographic quotes and
            dashes with ASCII equivalents.
        strip_control_chars: When true (default), remove C0/C1 control
            characters except newline and tab.
        whitespace: When true (default), canonicalize newlines, collapse
            whitespace runs, strip line edges and cap blank-line runs.
        max_blank_lines: Maximum number of consecutive blank lines kept
            by the whitespace step; must be >= 0 (default 1, i.e. one
            blank line between paragraphs).
        lowercase: When true (default false), fold the text to lowercase.
        url_masking: When true (default false), replace URLs with
            ``url_mask_token``.
        url_mask_token: Replacement token written for each URL; must be a
            non-empty string (default '[URL]'). When ``lowercase`` is
            enabled the token is inserted in lowercase so repeated
            normalization stays idempotent.
        applied_key: Metadata key the list of applied operations is
            written to; an empty value disables stamping.
    """

    unicode_normalization: str = 'NFC'
    fullwidth_to_ascii: bool = True
    smart_quotes: bool = True
    strip_control_chars: bool = True
    whitespace: bool = True
    max_blank_lines: int = 1
    lowercase: bool = False
    url_masking: bool = False
    url_mask_token: str = '[URL]'
    applied_key: str = 'normalization_applied'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Rewrite every document's text through the enabled operations.

        Args:
            origin_docs: Documents to normalize, in batch order.
            query: Query object (unused; normalization depends only on
                the documents' own text).

        Returns:
            List[Document]: The same documents, in order, with normalized
            text and the applied-operations list stamped in metadata.
        """
        if not origin_docs:
            return []
        for doc in origin_docs:
            text, applied = self._normalize(doc.text or '')
            doc.text = text
            if self.applied_key:
                self._stamp(doc, self.applied_key, applied)
        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Normalization pipeline
    # ------------------------------------------------------------------ #

    def _normalize(self, text: str) -> Tuple[str, List[str]]:
        """Run all enabled operations in fixed order.

        Args:
            text: Raw document text.

        Returns:
            Tuple[str, List[str]]: The normalized text and the names of
            the operations executed, in execution order.
        """
        applied: List[str] = []
        if self.unicode_normalization:
            text = unicodedata.normalize(self.unicode_normalization, text)
            applied.append('unicode_normalization')
        if self.fullwidth_to_ascii:
            text = text.translate(_FULLWIDTH_TABLE)
            applied.append('fullwidth_to_ascii')
        if self.smart_quotes:
            text = text.translate(_SMART_TABLE)
            applied.append('smart_quotes')
        if self.strip_control_chars:
            text = self._strip_control_chars(text)
            applied.append('strip_control_chars')
        if self.whitespace:
            text = self._collapse_whitespace(text)
            applied.append('whitespace')
        if self.lowercase:
            text = text.lower()
            applied.append('lowercase')
        if self.url_masking:
            text = self._mask_urls(text)
            applied.append('url_masking')
        return text, applied

    @staticmethod
    def _strip_control_chars(text: str) -> str:
        """Delete C0/C1 control characters except newline and tab.

        Category Cc covers the C0 range (U+0000..U+001F, including DEL's
        neighbours), DEL (U+007F) and the C1 range (U+0080..U+009F).
        Newline and tab survive so that the whitespace step — which may
        itself be disabled — decides their fate.

        Args:
            text: Text possibly carrying control bytes from extraction.

        Returns:
            str: Text without control characters other than \\n and \\t.
        """
        return ''.join(ch for ch in text
                       if ch in ('\n', '\t') or
                       unicodedata.category(ch) != 'Cc')

    def _collapse_whitespace(self, text: str) -> str:
        """Canonicalize newlines and collapse whitespace runs per line.

        The steps, in order: CRLF/CR become LF; every other whitespace
        character (tabs, vertical tabs, non-breaking spaces, the
        ideographic space) becomes a plain space; space runs inside a
        line collapse to one space and line edges are stripped; runs of
        blank lines are capped at ``max_blank_lines``; leading and
        trailing blank lines are dropped. CJK text written without
        spaces passes through byte-identical.

        Args:
            text: Text with arbitrary whitespace spellings.

        Returns:
            str: Text with canonical whitespace.
        """
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = ''.join(
            '\n' if ch == '\n' else (' ' if ch.isspace() else ch)
            for ch in text)
        lines = [re.sub(r' +', ' ', line).strip()
                 for line in text.split('\n')]
        kept: List[str] = []
        blanks = 0
        for line in lines:
            if line:
                blanks = 0
                kept.append(line)
            else:
                blanks += 1
                if blanks <= self.max_blank_lines:
                    kept.append(line)
        while kept and not kept[0]:
            kept.pop(0)
        while kept and not kept[-1]:
            kept.pop()
        return '\n'.join(kept)

    def _mask_urls(self, text: str) -> str:
        """Replace every URL with ``url_mask_token``.

        A URL is an ``http://``/``https://`` scheme or a ``www.`` host
        followed by non-whitespace characters. Trailing sentence
        punctuation (``.,;:!?)'"``) is not swallowed: it is emitted after
        the token, so ``see https://x.com.`` becomes ``see [URL].``.
        When ``lowercase`` is enabled the token is inserted in
        lowercase, keeping the pipeline idempotent across repeated runs.

        Args:
            text: Text possibly containing URLs.

        Returns:
            str: Text with URLs masked.
        """
        token = self.url_mask_token.lower() if self.lowercase \
            else self.url_mask_token

        def _replace(match: 're.Match[str]') -> str:
            url = match.group(0)
            tail = ''
            while url and url[-1] in _URL_TRAILING_PUNCT:
                tail = url[-1] + tail
                url = url[:-1]
            return token + tail

        return _URL_PATTERN.sub(_replace, text)

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
            -> 'TextNormalizer':
        """Initialize and validate the normalizer from component config.

        Validation happens eagerly at load time: a silently mis-spelled
        normalization form would leave documents half-canonicalized with
        no visible failure, which is far harder to notice in production
        than a startup error.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            TextNormalizer: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, 'unicode_normalization') and \
                doc_processor_configer.unicode_normalization is not None:
            form = doc_processor_configer.unicode_normalization
            if not isinstance(form, str):
                raise ValueError("unicode_normalization must be a string")
            form = form.strip().upper()
            if form and form not in _NORMALIZATION_FORMS:
                raise ValueError(
                    "unicode_normalization must be one of "
                    f"{_NORMALIZATION_FORMS} or '' to disable, got "
                    f"'{doc_processor_configer.unicode_normalization}'")
            self.unicode_normalization = form

        for attr in ('fullwidth_to_ascii', 'smart_quotes',
                     'strip_control_chars', 'whitespace', 'lowercase',
                     'url_masking'):
            value = getattr(doc_processor_configer, attr, None)
            if value is not None:
                setattr(self, attr, bool(value))

        if hasattr(doc_processor_configer, 'max_blank_lines') and \
                doc_processor_configer.max_blank_lines is not None:
            limit = doc_processor_configer.max_blank_lines
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise ValueError("max_blank_lines must be an integer")
            if limit < 0:
                raise ValueError("max_blank_lines must be >= 0")
            self.max_blank_lines = limit

        if hasattr(doc_processor_configer, 'url_mask_token') and \
                doc_processor_configer.url_mask_token is not None:
            token = doc_processor_configer.url_mask_token
            if not isinstance(token, str) or not token:
                raise ValueError(
                    "url_mask_token must be a non-empty string")
            self.url_mask_token = token

        if hasattr(doc_processor_configer, 'applied_key') and \
                doc_processor_configer.applied_key is not None:
            key = doc_processor_configer.applied_key
            if not isinstance(key, str):
                raise ValueError("applied_key must be a string")
            self.applied_key = key

        return self
