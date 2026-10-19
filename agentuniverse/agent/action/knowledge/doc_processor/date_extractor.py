# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: date_extractor.py

import datetime
import re
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# English month names (full and common abbreviations) mapped to month
# numbers; looked up on the lowercased match so 'SEPTEMBER' and 'sep'
# both resolve.
_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5,
    'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10,
    'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7,
    'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

# Alternation ordered longest-first so 'september' is preferred over
# 'sept' where both could start a match.
_MONTH_ALTERNATION = '|'.join(sorted(_MONTHS, key=len, reverse=True))

# ISO-style year-first dates with a consistent separator:
# 2026-10-19, 2026/10/19, 2026.10.19. The backreference forces both
# separators to be the same character; digit guards avoid matching
# inside longer digit runs (order numbers, phone numbers, ...).
_ISO_RE = re.compile(r'(?<!\d)(\d{4})([-/.])(\d{1,2})\2(\d{1,2})(?!\d)')

# Compact 8-digit form: 20261019 (YYYYMMDD), never part of a longer
# digit run.
_COMPACT_RE = re.compile(r'(?<!\d)(\d{8})(?!\d)')

# Numeric month/day order with 4-digit year: 10/19/2026 (US) or
# 19/10/2026 (EU). Which component is the month is decided per match
# (see _candidate_from_slash).
_SLASH_RE = re.compile(r'(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)')

# Month-name dates: Oct 19, 2026 / October 19 2026 / October 19th, 2026
# / SEP 5, 2026 — case-insensitive, optional period after the month
# abbreviation, optional ordinal suffix on the day, comma optional.
# Group 1 is the month name, group 2 the day, group 3 the year.
_MONTH_NAME_RE = re.compile(
    r'\b(%s)\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*|\s+)(\d{4})(?!\d)'
    % _MONTH_ALTERNATION,
    re.IGNORECASE)

# CJK dates with an explicit year: 2026年10月19日.
_CJK_FULL_RE = re.compile(r'(?<!\d)(\d{4})年(\d{1,2})月(\d{1,2})日')

# Yearless CJK dates: 10月19日 — the year is taken from the reference
# date. The leading digit guard plus overlap resolution keep this from
# double-reporting the tail of a full CJK date.
_CJK_YEARLESS_RE = re.compile(r'(?<!\d)(\d{1,2})月(\d{1,2})日')

# Relative keywords, English (word-bounded, case-insensitive) and CJK.
# Resolved as an offset in days against the reference date.
_RELATIVE_RE = re.compile(
    r'\b(?:today|tomorrow|yesterday)\b|今天|明天|昨天', re.IGNORECASE)
_RELATIVE_OFFSETS = {
    'today': 0, 'tomorrow': 1, 'yesterday': -1,
    '今天': 0, '明天': 1, '昨天': -1,
}

# Gap text (whitespace-stripped) that merges two adjacent concrete dates
# into one range entry: the ASCII/full-width tilde, hyphen and en/em
# dashes, the CJK 至/到 and the English 'to'.
_RANGE_SEPARATORS = frozenset({'~', '～', '-', '–', '—', '至', '到', 'to'})

# Strict reference-date configuration format: YYYY-MM-DD.
_REFERENCE_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')


class DateExtractor(DocProcessor):
    """Extract date expressions from document text into metadata.

    Knowledge bases rarely store when a document is *about*. Reports,
    contracts and news cite the dates they discuss — quarterly periods,
    effective dates, publication days — yet that temporal signal is
    buried in the prose and invisible to retrieval filters. This
    pre-processing component scans each document's text for date
    expressions, normalizes every hit to ISO-8601 (``YYYY-MM-DD``), and
    stamps the findings into metadata so downstream stages can filter,
    sort or boost by time — a natural companion to post-processors such
    as ``TemporalDecayFilter``.

    Recognized expression families (all pure ``re`` + ``datetime``,
    offline and dependency-free):

    - ISO year-first with a consistent separator: ``2026-10-19``,
      ``2026/10/19``, ``2026.10.19`` — never ambiguous;
    - compact ``YYYYMMDD``: ``20261019``;
    - numeric day/month with 4-digit year: ``10/19/2026`` (US) or
      ``19/10/2026`` (EU). When both leading numbers fit both roles
      (``05/06/2026``) the reading is genuinely ambiguous: the entry is
      flagged ``ambiguous=True`` and interpreted per ``day_first``
      (default ``False`` = month first). When only one reading is
      calendar-valid (``19/10/2026``, ``10/19/2026``) that reading is
      used and the entry is not flagged;
    - month-name dates: ``Oct 19, 2026``, ``October 19 2026``,
      ``October 19th, 2026``, ``SEP 5, 2026`` — never ambiguous;
    - CJK dates: ``2026年10月19日`` and yearless ``10月19日`` (the
      reference date's year is assumed);
    - relative keywords: today / tomorrow / yesterday (and 今天/明天/
      昨天), resolved as day offsets against the reference date;
    - simple ranges: two adjacent concrete dates separated by ``~``,
      ``～``, ``-``, ``–``, ``—``, ``至``, ``到`` or ``to`` (optionally
      spaced), e.g. ``2026-10-01~2026-10-19`` or
      ``从2026年10月1日到2026年10月19日``, reported as one entry with
      ISO-8601 interval notation ``start/end``.

    Every hit is validated against the real calendar (``2026-02-30``
    and friends are silently skipped, not normalized to March). Findings
    land in ``metadata[dates_key]`` as a list of
    ``{text, iso, span, kind, ambiguous}`` records in order of
    appearance — ``span`` is ``[start, end)`` over the document text so
    ``text[span[0]:span[1]] == text`` field — and, when at least two
    distinct dates were found (range endpoints included), the bounding
    pair ``[min, max]`` in ``metadata[range_key]``. Metadata mappings
    are copied before mutation; text, id and other metadata fields are
    never modified, and documents without any date pass through
    untouched.

    Relative resolution and yearless dates are defined by
    ``reference_date``. The default ``None`` resolves against the
    current day at processing time — convenient for interactive use but
    non-deterministic across days; inject an explicit ``YYYY-MM-DD``
    for reproducible output (both are documented in the yaml).

    Attributes:
        reference_date: Anchor ``YYYY-MM-DD`` string for relative
            keywords and yearless CJK dates; ``None`` (default) uses
            the current day at processing time.
        day_first: How ambiguous numeric dates whose first two numbers
            both fit month and day (``05/06/2026``) are read —
            ``False`` (default) reads month first (US), ``True`` reads
            day first (EU). Unambiguous dates ignore this switch.
        dates_key: Metadata key the list of date records is written to;
            an empty value disables stamping.
        range_key: Metadata key the ``[min, max]`` bounding pair is
            written to when >= 2 distinct dates were found; an empty
            value disables stamping.
    """

    reference_date: Optional[str] = None
    day_first: bool = False
    dates_key: str = "dates"
    range_key: str = "date_range"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp date metadata onto every document, preserving the batch.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text and the reference date).

        Returns:
            List[Document]: The same documents in the same order — this
            component annotates rather than filters. Documents without
            any date expression are returned with metadata untouched.
        """
        if not origin_docs:
            return []

        reference = self._resolve_reference(self.reference_date)
        for doc in origin_docs:
            entries = self._extract(doc.text or "", reference)
            if not entries:
                continue

            meta = dict(doc.metadata or {})
            if self.dates_key:
                meta[self.dates_key] = entries
            if self.range_key:
                distinct = self._distinct_isos(entries)
                if len(distinct) >= 2:
                    meta[self.range_key] = [min(distinct), max(distinct)]
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction pipeline
    # ------------------------------------------------------------------ #

    def _extract(self, text: str, reference: datetime.date) -> List[dict]:
        """Find, resolve and merge all date expressions in one text.

        Args:
            text: Document text to scan.
            reference: Reference date for relative keywords and
                yearless CJK dates.

        Returns:
            List[dict]: Date records sorted by position, each
            ``{text, iso, span, kind, ambiguous}``.
        """
        candidates = []
        candidates.extend(self._iso_candidates(text))
        candidates.extend(self._compact_candidates(text))
        candidates.extend(self._slash_candidates(text))
        candidates.extend(self._month_name_candidates(text))
        candidates.extend(self._cjk_candidates(text, reference))
        candidates.extend(self._relative_candidates(text, reference))
        if not candidates:
            return []

        # Earliest match wins; on ties the longer match wins, which
        # keeps the full CJK form over its yearless tail and suppresses
        # any other pattern contained inside a bigger hit.
        candidates.sort(key=lambda c: (c['start'],
                                       -(c['end'] - c['start'])))
        kept = []
        last_end = -1
        for cand in candidates:
            if cand['start'] >= last_end:
                kept.append(cand)
                last_end = cand['end']

        # Two adjacent concrete dates joined by a range separator
        # collapse into a single interval entry spanning both.
        merged: List[dict] = []
        i = 0
        while i < len(kept):
            current = kept[i]
            if i + 1 < len(kept) and current['kind'] == 'date' \
                    and kept[i + 1]['kind'] == 'date' \
                    and self._is_range_gap(text, current['end'],
                                           kept[i + 1]['start']):
                nxt = kept[i + 1]
                merged.append({
                    'text': text[current['start']:nxt['end']],
                    'iso': "%s/%s" % (current['iso'], nxt['iso']),
                    'span': [current['start'], nxt['end']],
                    'kind': 'range',
                    'ambiguous': bool(current['ambiguous']
                                      or nxt['ambiguous']),
                })
                i += 2
            else:
                merged.append({
                    'text': text[current['start']:current['end']],
                    'iso': current['iso'],
                    'span': [current['start'], current['end']],
                    'kind': current['kind'],
                    'ambiguous': bool(current['ambiguous']),
                })
                i += 1
        return merged

    @staticmethod
    def _valid_date(year: int, month: int, day: int) \
            -> Optional[datetime.date]:
        """Build a calendar-checked date, or None if impossible.

        Args:
            year: Year number.
            month: Month number candidate.
            day: Day number candidate.

        Returns:
            Optional[datetime.date]: The date, or None when month/day
            do not exist on the real calendar (e.g. 2026-02-30).
        """
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None

    @staticmethod
    def _candidate(match: re.Match, iso: str, kind: str = 'date',
                   ambiguous: bool = False) -> dict:
        """Wrap one regex match and its resolution into a candidate.

        Args:
            match: The regex match object.
            iso: Resolved ISO-8601 date string.
            kind: Entry kind — 'date' or 'relative'.
            ambiguous: Whether the source expression admits more than
                one month/day reading.

        Returns:
            dict: Candidate record with span and text.
        """
        return {
            'start': match.start(),
            'end': match.end(),
            'text': match.group(0),
            'iso': iso,
            'kind': kind,
            'ambiguous': ambiguous,
        }

    def _iso_candidates(self, text: str) -> List[dict]:
        """Collect year-first ISO-style dates (never ambiguous).

        Args:
            text: Document text.

        Returns:
            List[dict]: Candidates for valid calendar dates only.
        """
        out = []
        for m in _ISO_RE.finditer(text):
            parsed = self._valid_date(int(m.group(1)), int(m.group(3)),
                                      int(m.group(4)))
            if parsed:
                out.append(self._candidate(m, parsed.isoformat()))
        return out

    def _compact_candidates(self, text: str) -> List[dict]:
        """Collect compact YYYYMMDD dates.

        Args:
            text: Document text.

        Returns:
            List[dict]: Candidates for valid calendar dates only.
        """
        out = []
        for m in _COMPACT_RE.finditer(text):
            digits = m.group(1)
            parsed = self._valid_date(int(digits[:4]), int(digits[4:6]),
                                      int(digits[6:8]))
            if parsed:
                out.append(self._candidate(m, parsed.isoformat()))
        return out

    def _slash_candidates(self, text: str) -> List[dict]:
        """Collect numeric month/day/year dates, resolving ambiguity.

        ``19/10/2026`` forces day-first (19 cannot be a month) and
        ``10/19/2026`` forces month-first; neither is flagged. When both
        leading numbers fit both roles the entry is flagged ambiguous
        and read per ``day_first``. Impossible readings are dropped.

        Args:
            text: Document text.

        Returns:
            List[dict]: Candidates for valid calendar dates only.
        """
        out = []
        for m in _SLASH_RE.finditer(text):
            first, second, year = int(m.group(1)), int(m.group(2)), \
                int(m.group(3))
            ambiguous = first <= 12 and second <= 12
            if ambiguous:
                if self.day_first:
                    day, month = first, second
                else:
                    month, day = first, second
            elif first > 12:
                day, month = first, second
            else:
                month, day = first, second
            parsed = self._valid_date(year, month, day)
            if parsed:
                out.append(self._candidate(m, parsed.isoformat(),
                                           ambiguous=ambiguous))
        return out

    def _month_name_candidates(self, text: str) -> List[dict]:
        """Collect month-name dates such as 'Oct 19, 2026'.

        The month is explicit, so these are never ambiguous.

        Args:
            text: Document text.

        Returns:
            List[dict]: Candidates for valid calendar dates only.
        """
        out = []
        for m in _MONTH_NAME_RE.finditer(text):
            month = _MONTHS[m.group(1).lower()]
            parsed = self._valid_date(int(m.group(3)), month,
                                      int(m.group(2)))
            if parsed:
                out.append(self._candidate(m, parsed.isoformat()))
        return out

    def _cjk_candidates(self, text: str,
                        reference: datetime.date) -> List[dict]:
        """Collect CJK dates, full and yearless.

        Yearless forms (``10月19日``) borrow the reference date's year.
        A yearless match embedded in a full form (``2026年10月19日``) is
        removed later by overlap resolution, since the full form starts
        earlier and is longer.

        Args:
            text: Document text.
            reference: Reference date supplying the assumed year.

        Returns:
            List[dict]: Candidates for valid calendar dates only.
        """
        out = []
        for m in _CJK_FULL_RE.finditer(text):
            parsed = self._valid_date(int(m.group(1)), int(m.group(2)),
                                      int(m.group(3)))
            if parsed:
                out.append(self._candidate(m, parsed.isoformat()))
        for m in _CJK_YEARLESS_RE.finditer(text):
            parsed = self._valid_date(reference.year, int(m.group(1)),
                                      int(m.group(2)))
            if parsed:
                out.append(self._candidate(m, parsed.isoformat()))
        return out

    def _relative_candidates(self, text: str,
                             reference: datetime.date) -> List[dict]:
        """Collect relative keywords resolved against the reference.

        Args:
            text: Document text.
            reference: Reference date the offsets apply to.

        Returns:
            List[dict]: One candidate per keyword occurrence, kind
            'relative', never ambiguous.
        """
        out = []
        for m in _RELATIVE_RE.finditer(text):
            keyword = m.group(0).lower()
            offset = _RELATIVE_OFFSETS[keyword]
            iso = (reference
                   + datetime.timedelta(days=offset)).isoformat()
            out.append(self._candidate(m, iso, kind='relative'))
        return out

    @staticmethod
    def _is_range_gap(text: str, end: int, start: int) -> bool:
        """Report whether the gap between two matches is a range link.

        The gap must be exactly one range separator optionally
        surrounded by whitespace — anything else (' and ', multiple
        dashes, prose) leaves the two dates as independent entries.

        Args:
            text: Document text.
            end: End offset of the first match.
            start: Start offset of the second match.

        Returns:
            bool: True when the gap joins the two dates into a range.
        """
        gap = text[end:start]
        return bool(gap) and gap.strip() in _RANGE_SEPARATORS

    @staticmethod
    def _distinct_isos(entries: List[dict]) -> set:
        """Collect the distinct ISO dates behind a list of entries.

        Range entries contribute both endpoints; relative entries
        contribute their resolved date.

        Args:
            entries: Date records produced by _extract.

        Returns:
            set: Distinct ISO-8601 date strings.
        """
        distinct = set()
        for entry in entries:
            if entry['kind'] == 'range':
                distinct.update(entry['iso'].split('/'))
            else:
                distinct.add(entry['iso'])
        return distinct

    # ------------------------------------------------------------------ #
    # Reference date handling
    # ------------------------------------------------------------------ #

    @staticmethod
    def _resolve_reference(value) -> datetime.date:
        """Resolve the configured reference date into a datetime.date.

        Args:
            value: ``None`` (current day), a strict ``YYYY-MM-DD``
            string, or a datetime/date object.

        Returns:
            datetime.date: The resolved reference date.

        Raises:
            ValueError: On a malformed or impossible date string.
        """
        if value is None:
            return datetime.date.today()
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            m = _REFERENCE_RE.match(value)
            if m:
                parsed = DateExtractor._valid_date(
                    int(m.group(1)), int(m.group(2)), int(m.group(3)))
                if parsed:
                    return parsed
            raise ValueError(
                "reference_date must be a YYYY-MM-DD date string, got "
                f"{value!r}")
        raise ValueError(
            "reference_date must be a YYYY-MM-DD date string or a date "
            f"object, got {type(value).__name__}")

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'DateExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: a mistyped
        reference_date that silently shifted every relative date would
        be far harder to notice than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            DateExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "reference_date") and \
                doc_processor_configer.reference_date is not None:
            value = doc_processor_configer.reference_date
            # An empty string in yaml means "no fixed reference".
            self.reference_date = value if value != "" else None
            if self.reference_date is not None:
                self._resolve_reference(self.reference_date)

        if hasattr(doc_processor_configer, "day_first") and \
                doc_processor_configer.day_first is not None:
            value = doc_processor_configer.day_first
            if not isinstance(value, bool):
                raise ValueError("day_first must be a boolean")
            self.day_first = value

        if hasattr(doc_processor_configer, "dates_key") and \
                doc_processor_configer.dates_key is not None:
            key = doc_processor_configer.dates_key
            if not isinstance(key, str):
                raise ValueError("dates_key must be a string")
            self.dates_key = key

        if hasattr(doc_processor_configer, "range_key") and \
                doc_processor_configer.range_key is not None:
            key = doc_processor_configer.range_key
            if not isinstance(key, str):
                raise ValueError("range_key must be a string")
            self.range_key = key

        return self
