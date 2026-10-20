# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: numeric_range_extractor.py

import re
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

DEFAULT_MAX_RANGES = 50

# Single CJK characters recognized as measurement/counting units.
_CJK_UNIT_CHARS = (
    '元圆角分个只条台件人天年次秒米里吨斤克升张页本辆间名款层'
    '度字号码颗倍头匹岁'
)

# CJK magnitude multipliers applied to an adjacent number (family rule shared
# with the other numeric knowledge components).
_CJK_MULTIPLIERS: Dict[str, Decimal] = {
    '万': Decimal(10) ** 4,
    '亿': Decimal(10) ** 8,
}

# ASCII tokens that directly follow a number but are connectors or common
# words, never units. They are excluded from unit extraction.
_UNIT_STOP_WORDS = (
    'to', 'and', 'from', 'between', 'or', 'of', 'in', 'on', 'for', 'the',
    'a', 'an', 'is', 'are', 'was', 'were', 'per', 'over', 'above', 'under',
    'below', 'through', 'up', 'down', 'by', 'at', 'as', 'with', 'than',
    'then', 'more', 'less', 'least', 'most', 'no', 'not', 'only', 'th',
    'st', 'nd', 'rd', 'each', 'every',
)

_NUM_CORE = r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?'

_UNIT_RE = (
    r'(?:%|％|℃|°C|°F'
    r'|(?!(?:' + '|'.join(_UNIT_STOP_WORDS) + r')\b)[A-Za-z][A-Za-z0-9]{0,15}'
    r'|[' + _CJK_UNIT_CHARS + r'])'
)

_CURRENCY_RE = r'[$¥€£]'


def _number_fragment(tag: str) -> str:
    """Build a regex fragment matching one number with optional currency
    prefix, CJK magnitude multiplier and trailing unit.

    Named groups use `tag` as suffix so several fragments can coexist in a
    single pattern: cur<tag>, num<tag>, mult<tag>, unit<tag>.
    """
    return (
        r'(?:(?P<cur' + tag + r'>' + _CURRENCY_RE + r')\s*)?'
        r'(?P<num' + tag + r'>' + _NUM_CORE + r')'
        r'(?P<mult' + tag + r'>[万亿])?'
        r'(?:\s*(?P<unit' + tag + r'>' + _UNIT_RE + r'))?'
    )


_NU_L = _number_fragment('1')
_NU_R = _number_fragment('2')

# Closed-range patterns (min ... max).
_BETWEEN_RE = re.compile(
    r'\bbetween\s+' + _NU_L + r'\s+and\b\s+' + _NU_R, re.IGNORECASE)
_FROM_TO_RE = re.compile(
    r'\bfrom\s+' + _NU_L + r'\s+(?:to|through)\b\s+' + _NU_R, re.IGNORECASE)
_TO_RE = re.compile(
    _NU_L + r'\s+(?:to|through)\b\s+' + _NU_R, re.IGNORECASE)
_DASH_RE = re.compile(
    _NU_L + r'\s*[-–—~]\s*' + _NU_R)
_ZH_CLOSED_RE = re.compile(
    _NU_L + r'\s*(?:至|到)\s*' + _NU_R)

# Open-range patterns (single bound).
_OVER_RE = re.compile(
    r'\b(?:over|above)\s+' + _NU_R, re.IGNORECASE)
_EXCEED_RE = re.compile(
    r'超过\s*' + _NU_R)
_ZH_AT_LEAST_RE = re.compile(
    _NU_L + r'\s*(?:或以上|及以上|以上)')
_NOT_EXCEED_RE = re.compile(
    r'不超过\s*' + _NU_R)
_EN_AT_LEAST_RE = re.compile(
    _NU_L + r'\s+(?:or|and)\s+above\b', re.IGNORECASE)
_EN_BELOW_RE = re.compile(
    _NU_L + r'\s+(?:(?:or|and)\s+)?below\b', re.IGNORECASE)
_BELOW_RE = re.compile(
    _NU_L + r'\s*(?:及以下|以下)')

# Guard spans inside which no range is extracted.
_URL_RE = re.compile(r'https?://\S+|www\.\S+')
_EMAIL_RE = re.compile(r'\S+@\S+')
_IP_RE = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')
_VERSION_RE = re.compile(r'(?i)(?<![0-9a-z])v\d+(?:\.\d+)+')
_DOTTED_RUN_RE = re.compile(r'\d+\.\d+\.\d+(?:\.\d+)*')
_DATE_RE = re.compile(
    r'\b\d{4}[-/.]\d{1,2}(?:[-/.]\d{1,4})?\b'
    r'|\b\d{1,2}[-/.]\d{1,4}[-/.]\d{4}\b')
_PHONE_RE = re.compile(
    r'\b\d{2,4}[-–]\d{6,}\b'
    r'|\b\d{1,4}(?:[-–]\d{2,4}){2,}\b')

_GUARD_RES = (
    _URL_RE, _EMAIL_RE, _IP_RE, _VERSION_RE, _DOTTED_RUN_RE, _DATE_RE,
    _PHONE_RE,
)

_SYMBOL_CONNECTOR_KINDS = frozenset({'dash'})


def _decimal_value(num: str, mult: Optional[str]) -> Decimal:
    """Convert a matched number (comma groups allowed) plus optional CJK
    magnitude multiplier into an exact Decimal."""
    value = Decimal(num.replace(',', ''))
    if mult:
        value = value * _CJK_MULTIPLIERS[mult]
    return value


def _format_decimal(value: Decimal) -> str:
    """Render a Decimal as a plain (non-exponent) normalized string."""
    return format(value.normalize(), 'f')


def _is_year_like(num: str) -> bool:
    """True for bare 4-digit integers within 1900-2100 (year-shaped)."""
    return len(num) == 4 and num.isdigit() and 1900 <= int(num) <= 2100


def _mask_spans(text: str) -> List[Tuple[int, int]]:
    """Spans of URLs, emails, IPs, versions, dates and phone-like runs."""
    spans: List[Tuple[int, int]] = []
    for regex in _GUARD_RES:
        for m in regex.finditer(text):
            spans.append((m.start(), m.end()))
    return spans


def _overlaps(start: int, end: int, spans: List[Tuple[int, int]]) -> bool:
    return any(start < e and s < end for s, e in spans)


def _resolve_unit(unit_left: Optional[str],
                  unit_right: Optional[str]) -> Tuple[Optional[str],
                                                      Optional[str]]:
    """Resolve the range unit.

    The token attached to the second number wins when both sides carry a
    unit; if the two units differ a `unit_mismatch(left|right)` note is
    returned alongside.
    """
    if unit_left and unit_right and unit_left != unit_right:
        return unit_right, 'unit_mismatch({}|{})'.format(unit_left, unit_right)
    return (unit_right or unit_left), None


def _closed_candidate(match: re.Match, connector_kind: str) -> Dict[str, Any]:
    group = match.groupdict()
    return {
        'start': match.start(),
        'end': match.end(),
        'kind': 'closed',
        'num1': group['num1'],
        'mult1': group['mult1'],
        'num2': group['num2'],
        'mult2': group['mult2'],
        'unit1': group['unit1'] or group['cur1'],
        'unit2': group['unit2'] or group['cur2'],
        'connector_kind': connector_kind,
    }


def _open_candidate(match: re.Match, kind: str,
                    left_bound: bool) -> Dict[str, Any]:
    group = match.groupdict()
    if left_bound:
        num, mult = group['num1'], group['mult1']
        unit = group['unit1'] or group['cur1']
    else:
        num, mult = group['num2'], group['mult2']
        unit = group['unit2'] or group['cur2']
    return {
        'start': match.start(),
        'end': match.end(),
        'kind': kind,
        'num1': num,
        'mult1': mult,
        'num2': None,
        'mult2': None,
        'unit1': None if not left_bound else unit,
        'unit2': None if left_bound else unit,
        'connector_kind': 'open',
    }


def _collect_candidates(text: str) -> List[Dict[str, Any]]:
    """Run every pattern and return raw candidates in text order.

    Longer matches starting earlier win; contained or overlapping shorter
    candidates are dropped by the caller.
    """
    candidates: List[Dict[str, Any]] = []
    for regex, kind in ((_BETWEEN_RE, 'word'), (_FROM_TO_RE, 'word'),
                        (_TO_RE, 'word'), (_DASH_RE, 'dash'),
                        (_ZH_CLOSED_RE, 'word')):
        for m in regex.finditer(text):
            candidates.append(_closed_candidate(m, kind))
    for regex, kind, left in ((_OVER_RE, 'open_lower', False),
                              (_EXCEED_RE, 'open_lower', False),
                              (_ZH_AT_LEAST_RE, 'open_lower', True),
                              (_EN_AT_LEAST_RE, 'open_lower', True),
                              (_NOT_EXCEED_RE, 'open_upper', False),
                              (_EN_BELOW_RE, 'open_upper', True),
                              (_BELOW_RE, 'open_upper', True)):
        for m in regex.finditer(text):
            candidates.append(_open_candidate(m, kind, left))
    # Earlier start first, longer match first: makes containment
    # de-duplication deterministic.
    candidates.sort(key=lambda c: (c['start'], -c['end'], c['kind']))
    return candidates


def _candidate_allowed(candidate: Dict[str, Any],
                       masks: List[Tuple[int, int]]) -> bool:
    """Apply the documented guards to a raw candidate."""
    if _overlaps(candidate['start'], candidate['end'], masks):
        return False
    if candidate['kind'] != 'closed':
        return True
    # Both endpoints bare 4-digit years: defer to DateExtractor.
    if _is_year_like(candidate['num1']) and _is_year_like(candidate['num2']):
        return False
    # Symbol-connector ranges whose both endpoints carry a decimal point are
    # version-shaped (v?X.Y-Z); guard them.
    if (candidate['connector_kind'] in _SYMBOL_CONNECTOR_KINDS
            and '.' in candidate['num1'] and '.' in candidate['num2']):
        return False
    return True


def _build_hit(text: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
    notes: List[str] = []
    if candidate['kind'] == 'closed':
        min_value = _decimal_value(candidate['num1'], candidate['mult1'])
        max_value = _decimal_value(candidate['num2'], candidate['mult2'])
        unit, mismatch_note = _resolve_unit(candidate['unit1'],
                                            candidate['unit2'])
        if mismatch_note:
            notes.append(mismatch_note)
        if min_value > max_value:
            notes.append('inverted_range')
    else:
        min_value = max_value = None
        if candidate['kind'] == 'open_lower':
            min_value = _decimal_value(candidate['num1'], candidate['mult1'])
        else:
            max_value = _decimal_value(candidate['num1'], candidate['mult1'])
        unit = candidate['unit1'] or candidate['unit2']
    return {
        'kind': candidate['kind'],
        'min': _format_decimal(min_value) if min_value is not None else None,
        'max': _format_decimal(max_value) if max_value is not None else None,
        'unit': unit,
        'text': text[candidate['start']:candidate['end']],
        'span': [candidate['start'], candidate['end']],
        'notes': notes,
    }


def extract_numeric_ranges(text: str) -> List[Dict[str, Any]]:
    """Extract numeric ranges from `text` deterministically.

    Returns hits ordered by position, each shaped as
    ``{kind, min, max, unit, text, span, notes}`` where `kind` is one of
    ``closed`` / ``open_lower`` / ``open_upper``, `min`/`max` are exact
    Decimal-normalized strings (``None`` for an open bound) and `span` is a
    ``[start, end)`` character interval with
    ``text[start:end] == hit['text']``.
    """
    if not text:
        return []
    masks = _mask_spans(text)
    accepted: List[Dict[str, Any]] = []
    accepted_spans: List[Tuple[int, int]] = []
    for candidate in _collect_candidates(text):
        if not _candidate_allowed(candidate, masks):
            continue
        if _overlaps(candidate['start'], candidate['end'], accepted_spans):
            continue
        accepted.append(candidate)
        accepted_spans.append((candidate['start'], candidate['end']))
    return [_build_hit(text, candidate) for candidate in accepted]


class NumericRangeExtractor(DocProcessor):
    """Stamp numeric ranges with units into document metadata.

    A deterministic, offline pre-processing component (pure standard
    library, no external dependencies) that scans document text for numeric
    ranges such as price bands, thresholds and capacities and stores them
    under ``metadata['numeric_ranges']`` plus ``metadata['range_count']``.

    Recognized shapes (English and Chinese):
      - closed ranges: ``X to Y``, ``from X to Y``, ``between X and Y``,
        ``X-Y`` / ``X–Y`` / ``X—Y`` / ``X~Y``, ``X至Y``, ``X到Y``
      - open lower bound: ``over X``, ``above X``, ``X or above``,
        ``X and above``, ``超过X``, ``X以上``, ``X或以上``, ``X及以上``
      - open upper bound: ``不超过Y``, ``Y以下``, ``Y及以下``, ``Y or below``,
        ``Y and below``

    Values are parsed with ``decimal.Decimal`` (comma groups supported) and
    the 万 (1e4) / 亿 (1e8) magnitude multipliers are applied before
    normalization. The unit is the token attached to a range endpoint
    (``%``, ``USD``, ``元``, ``个``, ``users``, ``ms``, ``$`` ...); when the
    two endpoints carry different units the second number's unit wins and a
    ``unit_mismatch(left|right)`` note is attached. A closed range whose
    first value exceeds the second is kept with an ``inverted_range`` note.

    Guards (matching spans are skipped): URLs, emails, IP addresses,
    versions (``v?X.Y`` and multi-dot runs, plus dash ranges whose both
    endpoints are decimal numbers), dates and phone-like digit runs; a
    closed range whose both endpoints are bare years in 1900-2100 is left
    to the DateExtractor.

    Attributes:
        max_ranges: Maximum number of ranges stored per document
            (default 50). Must be a positive integer.
    """

    max_ranges: int = DEFAULT_MAX_RANGES

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp extracted numeric ranges into each document's metadata.

        Documents are returned as-is (same objects, text untouched); only
        metadata is extended.

        Args:
            origin_docs: Documents whose text is scanned for ranges.
            query: Optional query object (unused).

        Returns:
            The input document list.
        """
        self._validate_config()
        for doc in origin_docs:
            hits = extract_numeric_ranges(doc.text or '')
            stored = hits[:self.max_ranges]
            metadata = doc.metadata if doc.metadata is not None else {}
            metadata['numeric_ranges'] = stored
            metadata['range_count'] = len(stored)
            if len(hits) > self.max_ranges:
                metadata['range_truncated'] = True
            doc.metadata = metadata
        return origin_docs

    def _validate_config(self) -> None:
        """Validate component configuration.

        Raises:
            ValueError: If max_ranges is not a positive integer.
        """
        if isinstance(self.max_ranges, bool) or not isinstance(
                self.max_ranges, int):
            raise ValueError(
                'max_ranges must be a positive integer, got: {!r}'.format(
                    self.max_ranges))
        if self.max_ranges < 1:
            raise ValueError(
                'max_ranges must be a positive integer, got: {!r}'.format(
                    self.max_ranges))

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger
    ) -> 'NumericRangeExtractor':
        """Initialize the extractor from the component configuration.

        Args:
            doc_processor_configer: Configer holding max_ranges.

        Returns:
            The initialized instance.

        Raises:
            ValueError: If max_ranges is not a positive integer.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, 'max_ranges'):
            self.max_ranges = doc_processor_configer.max_ranges
        self._validate_config()
        return self
