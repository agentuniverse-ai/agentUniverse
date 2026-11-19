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
    '度字号码颗倍头匹岁座伏安瓦转'
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
    r'(?:%|％|℃|°C|°F|°'
    r'|(?!(?:' + '|'.join(_UNIT_STOP_WORDS) + r')\b)[A-Za-z][A-Za-z0-9]{0,15}'
    r'|[' + _CJK_UNIT_CHARS + r'])'
)

_CURRENCY_RE = r'[$¥￥€£]'

_CURRENCY_EQUIV: Dict[str, str] = {
    '$': 'USD', 'USD': 'USD',
    '€': 'EUR', 'EUR': 'EUR',
    '£': 'GBP', 'GBP': 'GBP',
    '¥': 'CNY', '￥': 'CNY', '元': 'CNY', 'RMB': 'CNY',
}

_SIGN_CHARS = '-−+±'


def _number_fragment(tag: str, signed: bool = False,
                     unit_re: str = _UNIT_RE) -> str:
    """Build a regex fragment matching one number with optional currency
    prefix, leading sign (signed fragments only), CJK magnitude multiplier
    and trailing unit.

    Named groups use `tag` as suffix so several fragments can coexist in a
    single pattern: cur<tag>, num<tag>, mult<tag>, unit<tag> and, for signed
    fragments, sign<tag>. A number glued to a preceding ``.``, digit, ``/``
    or ``:`` (fraction, ratio, section or page glued forms) never matches.
    """
    sign = (r'(?P<sign' + tag + r'>[' + _SIGN_CHARS + r'])?'
            if signed else '')
    return (
        r'(?<![.\d:/])'
        + sign +
        r'(?:(?P<cur' + tag + r'>' + _CURRENCY_RE + r')\s*)?'
        r'(?P<num' + tag + r'>' + _NUM_CORE + r')'
        r'(?P<mult' + tag + r'>[万亿])?'
        r'(?:\s*(?P<unit' + tag + r'>' + unit_re + r'))?'
    )


_CJK_UNIT_CHARS_NO_SHENG = _CJK_UNIT_CHARS.replace('升', '')
_UNIT_RE_NO_SHENG = (
    r'(?:%|％|℃|°C|°F|°'
    r'|(?!(?:' + '|'.join(_UNIT_STOP_WORDS) + r')\b)[A-Za-z][A-Za-z0-9]{0,15}'
    r'|[' + _CJK_UNIT_CHARS_NO_SHENG + r'])'
)

_NU_L = _number_fragment('1')
_NU_R = _number_fragment('2')
_SNU_L = _number_fragment('1', signed=True)
_SNU_R = _number_fragment('2', signed=True)
_SNU_L_NO_SHENG = _number_fragment('1', signed=True,
                                   unit_re=_UNIT_RE_NO_SHENG)

# Closed-range patterns (min ... max).
_BETWEEN_RE = re.compile(
    r'\bbetween\s+' + _SNU_L + r'\s+and\b\s+' + _SNU_R, re.IGNORECASE)
_FROM_TO_RE = re.compile(
    r'\bfrom\s+' + _SNU_L + r'\s+(?:(?:up|down)\s+)?(?:to|through)\b\s+'
    + _SNU_R, re.IGNORECASE)
_TO_RE = re.compile(
    _SNU_L + r'\s+(?:(?:up|down)\s+)?(?:to|through)\b\s+' + _SNU_R,
    re.IGNORECASE)
_DASH_RE = re.compile(
    _NU_L + r'\s*[-–—~]\s*' + _NU_R)
_ZH_CLOSED_RE = re.compile(
    _SNU_L_NO_SHENG + r'\s*[升降]?(?:至|到)\s*' + _SNU_R)

# Open-range patterns (single bound).
_OVER_RE = re.compile(
    r'\b(?:over|above)\s+' + _SNU_R, re.IGNORECASE)
_EXCEED_RE = re.compile(
    r'超过\s*' + _SNU_R)
_ZH_HIGHER_RE = re.compile(
    r'高于\s*' + _SNU_R)
_ZH_NOT_LOWER_RE = re.compile(
    r'不低于\s*' + _SNU_R)
_AT_LEAST_RE = re.compile(
    r'\bat\s+least\s+' + _SNU_R, re.IGNORECASE)
_NO_LESS_THAN_RE = re.compile(
    r'\bno\s+less\s+than\s+' + _SNU_R, re.IGNORECASE)
_ZH_AT_LEAST_RE = re.compile(
    _NU_L + r'\s*(?:或以上|及以上|以上)')
_EN_AT_LEAST_RE = re.compile(
    _NU_L + r'\s+(?:(?:or|and)\s+(?:above|more)|at\s+least)\b', re.IGNORECASE)
_NOT_EXCEED_RE = re.compile(
    r'不超过\s*' + _SNU_R)
_ZH_LOWER_RE = re.compile(
    r'低于\s*' + _SNU_R)
_ZH_NOT_HIGHER_RE = re.compile(
    r'不高于\s*' + _SNU_R)
_UNDER_BELOW_RE = re.compile(
    r'\b(?:under|below)\s+' + _SNU_R, re.IGNORECASE)
_AT_MOST_RE = re.compile(
    r'\bat\s+most\s+' + _SNU_R, re.IGNORECASE)
_NO_MORE_THAN_RE = re.compile(
    r'\bno\s+more\s+than\s+' + _SNU_R, re.IGNORECASE)
_UP_TO_RE = re.compile(
    r'\bup\s+to\s+' + _SNU_R, re.IGNORECASE)
_EN_BELOW_RE = re.compile(
    _NU_L + r'\s+(?:(?:or|and)\s+(?:below|less)|below|at\s+most)\b',
    re.IGNORECASE)
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


def _decimal_value(num: str, mult: Optional[str],
                   sign: Optional[str] = None) -> Decimal:
    """Convert a matched number (comma groups allowed) plus optional leading
    sign and CJK magnitude multiplier into an exact Decimal."""
    value = Decimal(num.replace(',', ''))
    if mult:
        value = value * _CJK_MULTIPLIERS[mult]
    if sign in ('-', '−'):
        value = -value
    return value


def _format_decimal(value: Decimal) -> str:
    """Render a Decimal as a plain (non-exponent) normalized string."""
    return format(value.normalize(), 'f')


def _is_year_like(num: str) -> bool:
    """True for bare 4-digit integers within 1900-2100 (year-shaped)."""
    return len(num) == 4 and num.isdigit() and 1900 <= int(num) <= 2100


def _definite_unit(token: Optional[str]) -> bool:
    """True when a trailing token is unmistakably a unit.

    Covers currency symbols, ``%``-style tokens, degree marks, single CJK
    unit characters and single ASCII letters (``L``, ``x``, ``K`` ...);
    multi-letter ASCII words (``scale``, ``million``) stay ambiguous.
    """
    if not token:
        return False
    if len(token) == 1:
        return (token.isascii() or token in _CJK_UNIT_CHARS
                or token in ('%', '％', '℃', '°'))
    return token in ('°C', '°F')


def _mask_spans(text: str) -> List[Tuple[int, int]]:
    """Spans of URLs, emails, IPs, versions, dates and phone-like runs."""
    spans: List[Tuple[int, int]] = []
    for regex in _GUARD_RES:
        for m in regex.finditer(text):
            spans.append((m.start(), m.end()))
    return spans


def _overlaps(start: int, end: int, spans: List[Tuple[int, int]]) -> bool:
    return any(start < e and s < end for s, e in spans)


def _currency_equiv(unit: Optional[str]) -> Optional[str]:
    if unit is None:
        return None
    return _CURRENCY_EQUIV.get(unit, unit)


def _resolve_unit(unit_left: Optional[str],
                  unit_right: Optional[str]) -> Tuple[Optional[str],
                                                      Optional[str]]:
    """Resolve the range unit.

    The token attached to the second number wins when both sides carry a
    unit; if the two units differ, also beyond the recognized currency
    equivalences (``$``/``USD``, ``¥``/``￥``/``元``, ...), a
    ``unit_mismatch(left|right)`` note is returned alongside.
    """
    if unit_left and unit_right and unit_left != unit_right:
        if _currency_equiv(unit_left) != _currency_equiv(unit_right):
            return unit_right, 'unit_mismatch({}|{})'.format(unit_left,
                                                             unit_right)
    return (unit_right or unit_left), None


def _closed_candidate(match: re.Match, connector_kind: str) -> Dict[str, Any]:
    group = match.groupdict()
    return {
        'start': match.start(),
        'end': match.end(),
        'kind': 'closed',
        'num1': group['num1'],
        'mult1': group['mult1'],
        'sign1': group.get('sign1'),
        'num2': group['num2'],
        'mult2': group['mult2'],
        'sign2': group.get('sign2'),
        'unit1': group['unit1'] or group['cur1'],
        'unit2': group['unit2'] or group['cur2'],
        'connector_kind': connector_kind,
    }


def _open_candidate(match: re.Match, kind: str,
                    left_bound: bool) -> Dict[str, Any]:
    group = match.groupdict()
    if left_bound:
        num, mult, sign = group['num1'], group['mult1'], group.get('sign1')
        unit = group['unit1'] or group['cur1']
    else:
        num, mult, sign = group['num2'], group['mult2'], group.get('sign2')
        unit = group['unit2'] or group['cur2']
    return {
        'start': match.start(),
        'end': match.end(),
        'kind': kind,
        'num1': num,
        'mult1': mult,
        'sign1': sign,
        'num2': None,
        'mult2': None,
        'sign2': None,
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
                              (_ZH_HIGHER_RE, 'open_lower', False),
                              (_ZH_NOT_LOWER_RE, 'open_lower', False),
                              (_AT_LEAST_RE, 'open_lower', False),
                              (_NO_LESS_THAN_RE, 'open_lower', False),
                              (_ZH_AT_LEAST_RE, 'open_lower', True),
                              (_EN_AT_LEAST_RE, 'open_lower', True),
                              (_NOT_EXCEED_RE, 'open_upper', False),
                              (_ZH_LOWER_RE, 'open_upper', False),
                              (_ZH_NOT_HIGHER_RE, 'open_upper', False),
                              (_UNDER_BELOW_RE, 'open_upper', False),
                              (_AT_MOST_RE, 'open_upper', False),
                              (_NO_MORE_THAN_RE, 'open_upper', False),
                              (_UP_TO_RE, 'open_upper', False),
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
    # Symbol-connector ranges whose both endpoints are bare decimal numbers
    # (no definite unit, multiplier or currency on either side) are
    # version-shaped (v?X.Y-Z); guard them.
    if (candidate['connector_kind'] in _SYMBOL_CONNECTOR_KINDS
            and '.' in candidate['num1'] and '.' in candidate['num2']
            and not (candidate['mult1'] or candidate['mult2']
                     or _definite_unit(candidate['unit1'])
                     or _definite_unit(candidate['unit2']))):
        return False
    return True


def _build_hit(text: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
    notes: List[str] = []
    if candidate['kind'] == 'closed':
        min_value = _decimal_value(candidate['num1'], candidate['mult1'],
                                   candidate['sign1'])
        max_value = _decimal_value(candidate['num2'], candidate['mult2'],
                                   candidate['sign2'])
        unit, mismatch_note = _resolve_unit(candidate['unit1'],
                                            candidate['unit2'])
        if mismatch_note:
            notes.append(mismatch_note)
        if bool(candidate['mult1']) != bool(candidate['mult2']):
            mult = candidate['mult1'] or candidate['mult2']
            if candidate['mult2']:
                scaled_min = min_value * _CJK_MULTIPLIERS[mult]
                scaled_max = max_value
            else:
                scaled_min = min_value
                scaled_max = max_value * _CJK_MULTIPLIERS[mult]
            if scaled_min <= scaled_max:
                min_value, max_value = scaled_min, scaled_max
                notes.append('multiplier_inferred')
        if min_value > max_value:
            notes.append('inverted_range')
    else:
        min_value = max_value = None
        if candidate['kind'] == 'open_lower':
            min_value = _decimal_value(candidate['num1'], candidate['mult1'],
                                       candidate['sign1'])
        else:
            max_value = _decimal_value(candidate['num1'], candidate['mult1'],
                                       candidate['sign1'])
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
        ``X up/down to Y``, ``X-Y`` / ``X–Y`` / ``X—Y`` / ``X~Y``, ``X至Y``,
        ``X到Y``, ``X降至Y`` / ``X升到Y``; word-connector endpoints may
        carry a leading sign (``-10 to -5``)
      - open lower bound: ``over X``, ``above X``, ``at least X``,
        ``no less than X``, ``X or/and above``, ``X or more``,
        ``X at least``, ``超过X``, ``高于X``, ``不低于X``, ``X以上``,
        ``X或以上``, ``X及以上``
      - open upper bound: ``up to X``, ``under X``, ``below X``,
        ``at most X``, ``no more than X``, ``X or/and below``, ``X or
        less``, ``X at most``, ``不超过X``, ``低于X``, ``不高于X``,
        ``X以下``, ``X及以下``

    Values are parsed with ``decimal.Decimal`` (comma groups supported) and
    the 万 (1e4) / 亿 (1e8) magnitude multipliers are applied before
    normalization; when exactly one endpoint of a closed range carries a
    multiplier the other endpoint is scaled to match (``3到5万`` becomes
    30000-50000) and a ``multiplier_inferred`` note is attached. The unit is
    the token attached to a range endpoint (``%``, ``USD``, ``元``, ``个``,
    ``users``, ``ms``, ``$`` ...); when the two endpoints carry different
    units the second number's unit wins and a ``unit_mismatch(left|right)``
    note is attached, except for recognized currency equivalences
    (``$``/``USD``, ``€``/``EUR``, ``£``/``GBP``, ``¥``/``￥``/``元``).
    A closed range whose first value exceeds the second is kept with an
    ``inverted_range`` note.

    Guards (matching spans are skipped): URLs, emails, IP addresses,
    versions (``v?X.Y`` and multi-dot runs, plus dash ranges whose both
    endpoints are bare decimal numbers without a definite unit, multiplier
    or currency), dates, phone-like digit runs, and numbers glued to a
    preceding ``.``, ``/`` or ``:`` (``p.3-5``, ``f/2.8``, ``1:2``); a
    closed range whose both endpoints are bare years in 1900-2100 is left
    to the DateExtractor.

    Known limitations: multi-character CJK count nouns (``用户``,
    ``公里``) do not resolve to a unit (single CJK unit characters and
    ASCII word tokens do); arithmetic-looking spans such as ``x = 1-2`` are
    still extracted; negative endpoints are not supported for symbol
    (``-``) connectors.

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
