# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: statistics_extractor.py

import re
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Kinds of numeric claims the extractor recognizes.
KIND_PERCENTAGE = "percentage"
KIND_COUNT = "count"
KIND_RATIO = "ratio"
KIND_RAW_NUMBER = "raw_number"

# Resolution priority when two candidates overlap in the text: percentages
# win over counts, counts over ratios, ratios over bare numbers.
_KIND_PRIORITY = {KIND_PERCENTAGE: 0, KIND_COUNT: 1, KIND_RATIO: 2,
                  KIND_RAW_NUMBER: 3}

# English magnitude words resolvable into the numeric value.
_EN_MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
}

# CJK magnitude characters (万 = 1e4, 亿 = 1e8; combinable as 万亿 = 1e12).
_CJK_MULTIPLIERS = {"万": 1_0000, "亿": 1_0000_0000}

# CJK numeral alphabet for parsing 百分之四十五-style percentages.
_CJK_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
               "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CJK_UNITS = {"十": 10, "百": 100, "千": 1000}

# English words that may follow a number but never denote a unit ("3 of the
# users" must not record a count with unit "of"). Calendar words are listed
# so "3 May" reads as a date, not a count.
_EN_UNIT_STOPWORDS = frozenset({
    "of", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for",
    "with", "by", "from", "as", "per", "than", "out", "into", "over",
    "under", "up", "down", "is", "are", "was", "were", "be", "been",
    "being", "has", "have", "had", "will", "would", "can", "could",
    "should", "may", "might", "must", "do", "does", "did", "not", "no",
    "that", "this", "these", "those", "it", "its", "we", "you", "they",
    "he", "she", "his", "her", "their", "our", "your", "my",
    "percent", "cent", "percentage",
    "hundred", "thousand", "million", "billion", "trillion",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
    "sunday",
})

# Bare numbers below this value are never recorded (raw numbers must be
# comma-grouped anyway, which implies >= 1000; kept as an explicit cap).
_MIN_RAW_NUMBER = 1000

# Number body shared by most patterns: comma-grouped integer part with an
# optional decimal fraction ("1,200", "3.5", "45").
_NUM = r"\d+(?:,\d{3})*(?:\.\d+)?"

# --- Extraction patterns ------------------------------------------------- #

# 45% / 45.3% / 45 ％ (full-width sign, optional space before it).
_RE_PERCENT_SIGN = re.compile(rf"(?P<num>{_NUM})\s*[％%]")

# 45.3 percent / 45 per cent (word forms).
_RE_PERCENT_WORD = re.compile(
    rf"(?P<num>{_NUM})\s+(?:percent|per\s+cent)\b", re.IGNORECASE)

# 百分之四十五 / 百分之三点五 / 百分之45 — Arabic digits or basic CJK numerals.
_RE_PERCENT_CJK = re.compile(
    r"百分之(?P<num>\d+(?:\.\d+)?|[零〇一二三四五六七八九十百千点两]{1,16})")

# 1,200 users — plain number followed by an English unit word (space
# required, so "1st" never parses as unit "st").
_RE_COUNT_EN_PLAIN = re.compile(
    rf"(?P<num>{_NUM})\s+(?P<unit>[A-Za-z][A-Za-z-]*)")

# 3 million items — multiplier word, unit word optional.
_RE_COUNT_EN_MULT = re.compile(
    rf"(?P<num>{_NUM})\s+(?P<mult>hundred|thousand|million|billion|trillion)"
    rf"\b(?:\s+(?P<unit>[A-Za-z][A-Za-z-]*))?", re.IGNORECASE)

# 5万次 — 万/亿 multiplier (up to two chars, e.g. 万亿), CJK unit optional.
# The gap before the unit lives inside the optional group so a missing
# unit leaves no trailing space in the matched text.
_RE_COUNT_CJK_MULT = re.compile(
    rf"(?P<num>{_NUM})\s*(?P<cmult>[万亿]{{1,2}})(?:\s*(?P<cunit>[一-龥]+))?")

# 5次 — plain number directly fused with a CJK unit run.
_RE_COUNT_CJK_PLAIN = re.compile(
    rf"(?P<num>{_NUM})\s*(?P<cunit>[一-龥]+)")

# 3:2 / 3：2 (full-width colon tolerated).
_RE_RATIO_COLON = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*[:：]\s*(?P<b>\d+(?:\.\d+)?)")

# 3/4 — guarded against dates, slash chains and URLs.
_RE_RATIO_SLASH = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*/\s*(?P<b>\d+(?:\.\d+)?)")

# 1,234,567 — comma-grouped bare number.
_RE_RAW_NUMBER = re.compile(
    r"(?<![\d.])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d.])")

# --- Guard patterns (spans excluded from every kind) --------------------- #

# Version tokens: v1.2.3, V2.0, and bare multi-dot runs (1.2.3, IPs).
_RE_VERSION_V = re.compile(r"(?<![A-Za-z0-9])[vV]\d+(?:\.\d+)+")
_RE_MULTI_DOT = re.compile(r"(?<![\d.])\d+(?:\.\d+){2,}(?![\d.])")

# ISO-style dates with dashes or slashes, and US month/day/year.
_RE_ISO_DATE = re.compile(
    r"(?<!\d)(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}(?!\d)")
_RE_SLASH_DATE_FULL = re.compile(
    r"(?<!\d)\d{1,2}/\d{1,2}/(?:19|20)\d{2}(?!\d)")

# Ordinals: 1st, 22nd, 103rd, 1,000th.
_RE_ORDINAL = re.compile(
    r"(?<![\d.])\d{1,3}(?:,\d{3})*(?:st|nd|rd|th)\b", re.IGNORECASE)

# URLs — slash ratios inside them are paths, not fractions.
_RE_URL = re.compile(r"\b(?:https?|ftp)://\S+|\bwww\.\S+", re.IGNORECASE)

# CJK calendar fragments: 2026年, 10月19日, 5日.
_RE_CJK_CALENDAR = re.compile(r"(?:19|20)\d{2}年|\d{1,2}月|\d{1,2}日")

# am/pm right after a colon pair marks a clock time.
_RE_AMPM = re.compile(r"\s*(?:a\.?m\.?|p\.?m\.?)\b", re.IGNORECASE)

# "at " immediately before a colon pair marks a clock time.
_RE_AT_PREFIX = re.compile(r"\bat\s+$", re.IGNORECASE)


class StatisticsExtractor(DocProcessor):
    """Pull numeric claims out of documents into metadata.

    Documents are full of numbers that downstream stages — retrieval
    filters, ranking boosts, dashboard generation — would love to see as
    structured data instead of prose: "45.3% of users", "1,200 accounts",
    "3 million items", "5万次", a "3:2" aspect ratio. This processor scans
    every document with pure regular expressions (no model calls, no
    network, no dependencies) and records each numeric claim as one hit in
    ``metadata[statistics_key]``:

    .. code-block:: python

        {"kind": "count", "value": 50000, "unit": "次",
         "text": "5万次", "span": [12, 16]}

    Four kinds are recognized:

    1. ``percentage`` — ``45%``, ``45.3 percent``, the full-width ``45％``
       and basic CJK forms ``百分之四十五`` (parsed to 45, including
       ``百分之三点五`` -> 3.5 and ``百分之百`` -> 100).
    2. ``count`` — a number followed by a unit word, optionally through a
       magnitude word: ``1,200 users``, ``3 million items``, ``5万次``,
       ``7 billion`` (unit empty when only the magnitude word follows).
       Magnitude words are resolved into ``value``: ``5万`` -> 50000,
       ``3 million`` -> 3000000, ``1.5亿`` -> 150000000. The unit is the
       following English word (function words and calendar words rejected)
       or the full following CJK character run.
    3. ``ratio`` — ``3:2`` and ``3/4`` (value is the quotient, e.g. 1.5
       and 0.75). Slash pairs carry a context guard against calendar
       readings: ``a/b`` with a <= 12 and 13 <= b <= 31 is treated as a
       month/day date (so ``10/19`` is skipped while ``3/4`` is kept), as
       are full dates (``2026-10-19``, ``10/19/2026``), slash chains
       (``a/3/4``) and anything inside a URL. Colon pairs skip clock
       shapes: a two-digit right side with a leading zero (``10:05``), an
       am/pm suffix (``10:30 am``) or an ``at`` prefix.
    4. ``raw_number`` — comma-grouped bare numbers ``1,234,567``, capped at
       values >= 1000 by construction so small quantities stay out.

    Common false positives are guarded out before any hit is accepted:
    dates (``2026-10-19``, ``10/19/2026``, CJK ``2026年10月19日`` and
    bare ``2026年``/``10月``/``5日`` fragments), version numbers
    (``v1.2.3``, ``1.2.3``, IP addresses) and ordinals (``21st``,
    ``1,000th``). Overlapping candidates resolve by kind priority
    percentage > count > ratio > raw_number, longest match first, so
    ``1,200 users`` yields exactly one count hit rather than a count plus
    a stray raw number.

    Alongside the hit list, ``metadata[summary_key]`` receives a compact
    digest computed over *all* hits (before capping): total count, hits
    per kind, and min/max value per kind — enough for filtering without
    reading every hit. The hit list itself is truncated to
    ``max_statistics`` entries (default 100).

    Documents pass through untouched in every other respect: text and id
    are never modified, order is preserved, and metadata mappings are
    copied before mutation. Documents without any numeric claim come back
    byte-identical with no statistics keys stamped. Everything is
    deterministic — the same text always yields the same hits — which
    makes the output safe to store, diff and test. Unlike
    ``FinancialIndicatorExtractor`` whose patterns are hardcoded to
    revenue/profit/metric scenarios, this component is domain-agnostic:
    it knows the *shape* of a numeric claim, not the vocabulary of any
    industry.

    Attributes:
        max_statistics: Maximum number of hits stored in the statistics
            list; must be an integer >= 1. The summary still reflects
            every hit found.
        statistics_key: Metadata key the hit list is written to; an empty
            value disables list stamping.
        summary_key: Metadata key the per-kind digest is written to; an
            empty value disables digest stamping.
    """

    max_statistics: int = 100
    statistics_key: str = "statistics"
    summary_key: str = "statistics_summary"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp numeric-claim metadata onto every document.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, in the same order,
            each stamped with its statistics hits and summary.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            hits = self._extract(doc.text or "")
            if not hits:
                continue
            if self.statistics_key:
                self._stamp(doc, self.statistics_key,
                            hits[:self.max_statistics])
            if self.summary_key:
                self._stamp(doc, self.summary_key, self._summarize(hits))
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #

    def _extract(self, text: str) -> List[Dict[str, Any]]:
        """Collect every numeric claim in one text, in document order.

        Args:
            text: Document text (empty text yields no hits).

        Returns:
            List[Dict[str, Any]]: Hits sorted by span start, each holding
            kind / value / unit / text / span.
        """
        if not text:
            return []

        # Guard spans first: any candidate overlapping one is a date,
        # version, ordinal or URL and is dropped outright.
        guarded: List[Tuple[int, int]] = []
        for pattern in (_RE_VERSION_V, _RE_MULTI_DOT, _RE_ISO_DATE,
                        _RE_SLASH_DATE_FULL, _RE_ORDINAL, _RE_URL,
                        _RE_CJK_CALENDAR):
            for match in pattern.finditer(text):
                guarded.append(match.span())

        candidates: List[Tuple[int, int, int, Dict[str, Any]]] = []
        for collector in (self._collect_percentages, self._collect_counts,
                          self._collect_ratios, self._collect_raw_numbers):
            for start, end, hit in collector(text):
                if any(start < g_end and g_start < end
                       for g_start, g_end in guarded):
                    continue
                # Sort key: kind priority, then document position, then
                # longer span first (-end).
                candidates.append((_KIND_PRIORITY[hit["kind"]], start,
                                   -end, hit))

        # Higher-priority (and, within a priority, longer and earlier)
        # candidates claim their span first; overlapping latecomers drop.
        candidates.sort(key=lambda item: item[:3])
        accepted: List[Tuple[int, int, Dict[str, Any]]] = []
        taken: List[Tuple[int, int]] = []
        for _, start, neg_end, hit in candidates:
            end = -neg_end
            if any(start < t_end and t_start < end for t_start, t_end in taken):
                continue
            hit["span"] = [start, end]
            taken.append((start, end))
            accepted.append((start, end, hit))

        accepted.sort(key=lambda item: item[0])
        return [hit for _, _, hit in accepted]

    # -- percentage ----------------------------------------------------- #

    def _collect_percentages(self, text: str):
        """Yield percentage hits: 45%, 45.3 percent, 45％, 百分之四十五.

        Args:
            text: Document text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples.
        """
        for match in _RE_PERCENT_SIGN.finditer(text):
            yield self._hit(KIND_PERCENTAGE, match.group("num"),
                            "%", match)
        for match in _RE_PERCENT_WORD.finditer(text):
            yield self._hit(KIND_PERCENTAGE, match.group("num"),
                            "%", match)
        for match in _RE_PERCENT_CJK.finditer(text):
            raw = match.group("num")
            if raw[0].isdigit():
                value = self._to_number(raw)
            else:
                value = self._parse_cjk_numeral(raw)
            if value is None:
                continue
            yield (match.start(), match.end(),
                   {"kind": KIND_PERCENTAGE,
                    "value": self._normalize(value), "unit": "%",
                    "text": match.group(0)})

    # -- count ---------------------------------------------------------- #

    def _collect_counts(self, text: str):
        """Yield count hits: 1,200 users, 3 million items, 5万次, 7 billion.

        A number glued directly onto a ``/`` or ``:`` separator is a
        ratio or clock denominator in disguise ("3/4 preferred",
        "10:30 am") and is never claimed as a count.

        Args:
            text: Document text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples.
        """
        def _after_separator(match: re.Match) -> bool:
            """True when the matched number directly follows / or :."""
            before = text[max(0, match.start() - 1):match.start()]
            return before in ("/", ":", "：")

        # Multiplier forms first so their longer spans win the overlap
        # race against the plain-unit regex on the same number.
        for match in _RE_COUNT_EN_MULT.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group("unit") or ""
            value = self._apply_multiplier(self._to_number(
                match.group("num")), match.group("mult").lower())
            yield self._hit(KIND_COUNT, value, unit, match, raw=False)
        for match in _RE_COUNT_CJK_MULT.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group("cunit") or ""
            value = self._to_number(match.group("num"))
            for char in match.group("cmult"):
                value *= _CJK_MULTIPLIERS[char]
            yield self._hit(KIND_COUNT, value, unit, match, raw=False)
        for match in _RE_COUNT_EN_PLAIN.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group("unit")
            if unit.lower() in _EN_UNIT_STOPWORDS:
                continue
            yield self._hit(KIND_COUNT, match.group("num"), unit, match)
        for match in _RE_COUNT_CJK_PLAIN.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group("cunit")
            if unit[0] in _CJK_MULTIPLIERS:
                # 3.5万 belongs to the multiplier form above, not a
                # count of 万-things.
                continue
            yield self._hit(KIND_COUNT, match.group("num"), unit, match)

    # -- ratio ---------------------------------------------------------- #

    def _collect_ratios(self, text: str):
        """Yield ratio hits: 3:2 (value 1.5) and 3/4 (value 0.75).

        Colon pairs are skipped when they read like clock times (leading-
        zero right side, am/pm suffix, "at" prefix). Slash pairs are
        skipped when they read like dates — month/day shapes (a <= 12,
        13 <= b <= 31, so 10/19 drops while 3/4 survives), full dates
        (covered by guard spans), slash chains and URL paths.

        Args:
            text: Document text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples.
        """
        for match in _RE_RATIO_COLON.finditer(text):
            right = match.group("b")
            left = match.group("a")
            if self._to_number(right) == 0:
                continue
            if len(right) == 2 and right[0] == "0":
                continue  # 10:05 — clock minutes
            if _RE_AMPM.match(text, match.end()):
                continue  # 10:30 am
            if _RE_AT_PREFIX.search(text[max(0, match.start() - 8):
                                         match.start()]):
                continue  # at 10:30
            yield self._hit(KIND_RATIO,
                            self._to_number(left) / self._to_number(right),
                            "", match, raw=False)
        for match in _RE_RATIO_SLASH.finditer(text):
            right = match.group("b")
            left = match.group("a")
            if self._to_number(right) == 0:
                continue
            before = text[max(0, match.start() - 1):match.start()].rstrip()
            after = text[match.end():match.end() + 1]
            if before.endswith("/") or after.startswith("/"):
                continue  # a/3/4 chains and 10/19/2026 interiors
            if left.isdigit() and right.isdigit() \
                    and int(left) <= 12 and 13 <= int(right) <= 31:
                continue  # month/day calendar shape (10/19)
            yield self._hit(KIND_RATIO,
                            self._to_number(left) / self._to_number(right),
                            "", match, raw=False)

    # -- raw number ------------------------------------------------------ #

    def _collect_raw_numbers(self, text: str):
        """Yield bare comma-grouped numbers: 1,234,567 (>= 1000 only).

        Args:
            text: Document text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples.
        """
        for match in _RE_RAW_NUMBER.finditer(text):
            value = self._to_number(match.group(0))
            if value < _MIN_RAW_NUMBER:
                continue
            yield self._hit(KIND_RAW_NUMBER, value, "", match, raw=False)

    # ------------------------------------------------------------------ #
    # Hit construction and numeric helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _hit(kind: str, value, unit: str, match: re.Match,
             raw: bool = True) -> Tuple[int, int, Dict[str, Any]]:
        """Build one (start, end, hit) candidate triple.

        Args:
            kind: One of the four kind constants.
            value: Numeric value, or the raw numeric text when ``raw``
                (normalized by :meth:`_to_number`).
            unit: Unit word ("" when the claim carries none).
            match: The regex match supplying the span and text.
            raw: When true, ``value`` still needs numeric parsing.

        Returns:
            Tuple[int, int, Dict[str, Any]]: Candidate triple.
        """
        if raw:
            value = StatisticsExtractor._to_number(value)
        return (match.start(), match.end(),
                {"kind": kind, "value": StatisticsExtractor._normalize(value),
                 "unit": unit, "text": match.group(0)})

    @staticmethod
    def _to_number(raw: str) -> float:
        """Parse a numeric token, dropping comma separators.

        Args:
            raw: Numeric text such as "1,200" or "3.5".

        Returns:
            float: Parsed value (never None; regexes pre-validate shape).
        """
        return float(raw.replace(",", ""))

    @staticmethod
    def _normalize(value: float):
        """Render integral floats as ints so metadata stays compact.

        Args:
            value: Parsed numeric value.

        Returns:
            int | float: ``5.0`` becomes ``5``; ``3.5`` stays ``3.5``.
        """
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @staticmethod
    def _apply_multiplier(value: float, word: str) -> float:
        """Scale a value by an English magnitude word.

        Args:
            value: Parsed number.
            word: Multiplier word, lowercased.

        Returns:
            float: value * multiplier ("3" + "million" -> 3000000.0).
        """
        return value * _EN_MULTIPLIERS[word]

    @staticmethod
    def _parse_cjk_numeral(raw: str) -> Optional[float]:
        """Parse a basic CJK numeral sequence such as 四十五 or 三点五.

        Supports the digits 零〇一二两三四五六七八九, the unit characters
        十百千, the section characters 万亿 and the decimal point 点.
        Malformed sequences (a lone 点, trailing 十 unit with no digit
        context beyond the standard rules) still parse positionally; None
        is returned only when no numeral character was consumed at all.

        Args:
            raw: CJK numeral text without the leading 百分之.

        Returns:
            Optional[float]: Parsed value (45 for 四十五, 3.5 for
            三点五), or None when nothing parses.
        """
        total = 0
        section = 0
        current = 0
        fraction: List[int] = []
        in_fraction = False
        consumed = False
        for char in raw:
            if char == "点":
                in_fraction = True
                consumed = True
            elif in_fraction:
                if char in _CJK_DIGITS:
                    fraction.append(_CJK_DIGITS[char])
                    consumed = True
            elif char in _CJK_DIGITS:
                current = _CJK_DIGITS[char]
                consumed = True
            elif char in _CJK_UNITS:
                section += (current or 1) * _CJK_UNITS[char]
                current = 0
                consumed = True
            elif char in _CJK_MULTIPLIERS:
                section = (section + current) * _CJK_MULTIPLIERS[char]
                total += section
                section = 0
                current = 0
                consumed = True
        if not consumed:
            return None
        whole = total + section + current
        if fraction:
            return float(f"{whole}." + "".join(str(d) for d in fraction))
        return float(whole)

    # ------------------------------------------------------------------ #
    # Summary and metadata stamping
    # ------------------------------------------------------------------ #

    @staticmethod
    def _summarize(hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Digest all hits (pre-cap) into counts and per-kind min/max.

        Args:
            hits: Every hit extracted from one document.

        Returns:
            Dict[str, Any]: ``{"total": n, "counts": {...}, "min": {...},
            "max": {...}}`` with kind keys sorted for stable output.
        """
        counts: Dict[str, int] = {}
        mins: Dict[str, Any] = {}
        maxs: Dict[str, Any] = {}
        for hit in hits:
            kind = hit["kind"]
            value = hit["value"]
            counts[kind] = counts.get(kind, 0) + 1
            if kind not in mins or value < mins[kind]:
                mins[kind] = value
            if kind not in maxs or value > maxs[kind]:
                maxs[kind] = value
        return {
            "total": len(hits),
            "counts": {kind: counts[kind] for kind in sorted(counts)},
            "min": {kind: mins[kind] for kind in sorted(mins)},
            "max": {kind: maxs[kind] for kind in sorted(maxs)},
        }

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place
        edits.

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
            -> 'StatisticsExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: a silently misconfigured
        cap or metadata key would corrupt stored statistics long before
        anyone noticed.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            StatisticsExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_statistics") and \
                doc_processor_configer.max_statistics is not None:
            cap = doc_processor_configer.max_statistics
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_statistics must be an integer")
            self.max_statistics = cap
            if self.max_statistics < 1:
                raise ValueError("max_statistics must be >= 1")

        if hasattr(doc_processor_configer, "statistics_key") and \
                doc_processor_configer.statistics_key is not None:
            key = doc_processor_configer.statistics_key
            if not isinstance(key, str):
                raise ValueError("statistics_key must be a string")
            self.statistics_key = key

        if hasattr(doc_processor_configer, "summary_key") and \
                doc_processor_configer.summary_key is not None:
            key = doc_processor_configer.summary_key
            if not isinstance(key, str):
                raise ValueError("summary_key must be a string")
            self.summary_key = key

        return self
