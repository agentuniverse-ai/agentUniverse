# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: number_conflict_detector.py

import re
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Two dimensions of numeric claims. Values only ever compare inside one
# dimension: "growth was 45%" and "growth hit 45 million" are different
# kinds of claims, never a conflict.
DIM_PERCENT = "percent"
DIM_AMOUNT = "amount"

# Resolution priority when candidates overlap in the text: percentages
# win over scaled amounts, scaled amounts over plain unit counts, and
# plain unit counts over bare numbers.
_DIM_PRIORITY = {DIM_PERCENT: 0, DIM_AMOUNT: 1}

# How many mention records each conflict shows at most (the earliest
# mentions by sentence order).
_MAX_VALUES_SHOWN = 5

# Tokens scanned on each side of a number when looking for its anchor
# noun.
_ANCHOR_WINDOW = 4

# English magnitude words resolvable into the numeric value.
_EN_MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
}

# CJK magnitude characters (万 = 1e4, 亿 = 1e8; combinable as 万亿).
_CJK_MULTIPLIERS = {"万": 1_0000, "亿": 1_0000_0000}

# CJK numeral alphabet for parsing 百分之四十五-style percentages.
_CJK_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
               "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CJK_UNITS = {"十": 10, "百": 100, "千": 1000}

# English words that may follow a number but never denote a unit ("3 of
# the users" must not record the unit "of"; "5 million but" must not
# record the unit "but"). Calendar words are listed so "3 May" reads as
# a date, not a count, and approximators/conjunctions/measure verbs so
# post-number words never stretch a hit's span or steal its anchor.
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
    "but", "yet", "however", "although", "though", "whereas", "whether",
    "therefore", "thus", "hence", "instead", "meanwhile", "later",
    "earlier", "before", "after", "when", "once", "where", "rather",
    "about", "around", "approximately", "roughly", "nearly", "almost",
    "hold", "holds", "held", "holding",
    "stay", "stays", "stayed", "staying",
})

# Words never accepted as an *anchor* (the claim's subject noun). Beyond
# the unit stopwords this holds approximators, quantifiers, calendar and
# ordinal words, and the common claim verbs ("revenue reached 6 million"
# must anchor on "revenue", not "reached"). Both the raw lowercase token
# and its light stem are checked against this set, so irregular forms
# ("grew", "paid") are listed verbatim while regular ones match through
# their stem ("reached" -> "reach").
_EN_ANCHOR_STOP = _EN_UNIT_STOPWORDS | frozenset({
    "about", "around", "approximately", "roughly", "nearly", "almost",
    "some", "more", "less", "most", "few", "several", "various", "many",
    "much", "all", "any", "both", "each", "every", "other", "others",
    "only", "also", "just", "still", "yet", "then", "later", "now",
    "very", "too", "quite", "so", "if", "because", "while", "during",
    "since", "until", "unless", "between", "among", "within", "without",
    "across", "against", "along", "toward", "towards", "through",
    "despite", "besides", "except", "via", "there", "here", "when",
    "where", "why", "how", "who", "whom", "whose", "which", "what",
    "never", "ever", "always", "often", "sometimes", "usually",
    "quarter", "week", "month", "year", "years", "day", "days",
    "q1", "q2", "q3", "q4", "fy",
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "last", "next", "previous", "prior",
    "reach", "reaches", "reached", "reaching", "reache",
    "hold", "holds", "held", "holding",
    "stay", "stays", "stayed", "staying",
    "grow", "grows", "grew", "grown", "growing",
    "rise", "rises", "rose", "risen", "rising",
    "fall", "falls", "fell", "fallen", "falling",
    "drop", "drops", "dropped", "dropping",
    "increase", "increases", "increased", "increasing",
    "decrease", "decreases", "decreased", "decreasing",
    "hit", "hits", "hitting", "stand", "stands", "stood", "standing",
    "total", "totals", "totaled", "totalled", "totalling", "totaling",
    "amount", "amounts", "amounted",
    "account", "accounts", "accounted",
    "report", "reports", "reported", "reporting",
    "spend", "spends", "spent", "spending",
    "pay", "pays", "paid", "paying",
    "come", "comes", "came", "coming",
    "remain", "remains", "remained", "remaining",
    "climb", "climbs", "climbed", "climbing",
    "jump", "jumps", "jumped", "jumping",
    "plunge", "plunges", "plunged", "surge", "surges", "surged",
    "decline", "declines", "declined",
    "double", "doubles", "doubled", "doubling",
    "triple", "triples", "tripled",
    "gain", "gains", "gained", "gaining",
    "earn", "earns", "earned", "earning",
    "lose", "loses", "lost", "losing",
    "exceed", "exceeds", "exceeded",
    "pass", "passes", "passed",
    "top", "tops", "topping", "breach", "breaches", "breached",
    "add", "adds", "added", "adding",
    "onboard", "onboards", "onboarded", "onboarding",
    "serve", "serves", "served", "serving",
    "see", "sees", "saw", "seen", "seeing",
    "support", "supports", "supported", "supporting",
    "process", "processes", "processed", "processing",
    "handle", "handles", "handled", "handling",
    "represent", "represents", "represented",
    "include", "includes", "included", "including",
    "worth",
})

# CJK characters stripped (iteratively) from the head of a candidate
# anchor run: time and determiner prefixes such as 2024年营收, 次年营收
# or 一周后转化率 reduce to their trailing subject 营收 / 转化率. A
# character is only stripped while at least two characters would
# remain, so genuine short words starting with these characters (日活,
# 年费, 上海) survive intact.
_CJK_HEAD_STRIP = frozenset(
    "年月日周次上下去今明本该当同一二两三四五六七八九十后前")

# CJK suffixes stripped (iteratively, longest first) from the tail of a
# candidate CJK anchor run: "营收达到" reduces to "营收", "用户数为" to
# "用户数". A run that strips to nothing is skipped and the scan moves
# one token further from the number.
_CJK_TAIL_STRIP = tuple(sorted({
    "达到", "超过", "约为", "增至", "升至", "降至", "上涨", "下跌",
    "增长", "减少", "接近", "突破", "高达", "总计", "合计", "共计",
    "约为", "花费", "支出为", "收入为",
    "为", "是", "达", "约", "超", "近", "至", "到", "有", "了", "的",
    "共", "已", "将", "才", "又", "再", "均", "亦", "且", "而", "并",
    "和", "与", "及", "对", "从", "被", "把", "在", "于", "增", "升",
    "降", "涨", "跌", "含",
}, key=len, reverse=True))

# Number body shared by most patterns: comma-grouped integer part with
# an optional decimal fraction ("1,200", "3.5", "45").
_NUM = r"\d+(?:,\d{3})*(?:\.\d+)?"

# --- Extraction patterns ------------------------------------------------- #

# 45% / 45.3% / 45 ％ (full-width sign, optional space before it).
_RE_PERCENT_SIGN = re.compile(rf"(?<![A-Za-z\d])({_NUM})\s*[％%]")

# 45.3 percent / 45 per cent (word forms).
_RE_PERCENT_WORD = re.compile(
    rf"(?<![A-Za-z\d])({_NUM})\s+(?:percent|per\s+cent)\b", re.IGNORECASE)

# 百分之四十五 / 百分之三点五 / 百分之45 — Arabic digits or basic CJK
# numerals (万亿 included so sectioned numerals parse fully).
_RE_PERCENT_CJK = re.compile(
    r"百分之(\d+(?:\.\d+)?|[零〇一二三四五六七八九十百千点两万亿]{1,16})")

# 3 million items — multiplier word, unit word optional.
_RE_COUNT_EN_MULT = re.compile(
    rf"(?<![A-Za-z\d])({_NUM})\s+"
    rf"(hundred|thousand|million|billion|trillion)"
    rf"\b(?:\s+([A-Za-z][A-Za-z-]*))?", re.IGNORECASE)

# 5万次 — 万/亿 multiplier (up to two chars, e.g. 万亿), CJK unit
# optional.
_RE_COUNT_CJK_MULT = re.compile(
    rf"(?<![A-Za-z\d])({_NUM})\s*([万亿]{{1,2}})(?:\s*([一-龥]+))?")

# 1,200 users — plain number followed by an English unit word (space
# required, so "1st" never parses as unit "st").
_RE_COUNT_EN_PLAIN = re.compile(
    rf"(?<![A-Za-z\d])({_NUM})\s+([A-Za-z][A-Za-z-]*)")

# 5次 — plain number fused with a CJK unit run.
_RE_COUNT_CJK_PLAIN = re.compile(rf"(?<![A-Za-z\d])({_NUM})\s*([一-龥]+)")

# Comma-grouped bare number: 1,234,567 (>= 1000 by construction).
_RE_COMMA_NUMBER = re.compile(
    r"(?<![A-Za-z\d.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?)(?!\d)(?!\.\d)")

# Bare number without separators: recorded only at values >= 1000 so
# small quantities, ordinals and noise stay out. Blocked when glued to
# letters (product names like "Q5"), separators (URL paths, slash or
# colon pairs) or multipliers ("5000x", "5000倍").
_RE_BARE_NUMBER = re.compile(
    r"(?<![A-Za-z0-9.,/:])(\d+(?:\.\d+)?)(?![\d,/])(?!\.\d)(?![xX倍])")

# --- Guard patterns (spans excluded from every extraction) --------------- #

# Version tokens: v1.2.3, V2.0, and bare multi-dot runs (1.2.3, IPs).
_RE_VERSION_V = re.compile(r"(?<![A-Za-z0-9])[vV]\d+(?:\.\d+)+")
_RE_MULTI_DOT = re.compile(r"(?<![\d.])\d+(?:\.\d+){2,}(?![\d.])")

# ISO-style dates with dashes or slashes, and US month/day/year.
_RE_ISO_DATE = re.compile(
    r"(?<!\d)(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}(?!\d)")
_RE_SLASH_DATE_FULL = re.compile(
    r"(?<!\d)\d{1,2}/\d{1,2}/(?:19|20)\d{2}(?!\d)")

# Ordinals: 1st, 22nd, 103rd, 1,000th — and the CJK 第N ordinal marker.
_RE_ORDINAL = re.compile(
    r"(?<![\d.])\d{1,3}(?:,\d{3})*(?:st|nd|rd|th)\b", re.IGNORECASE)
_RE_CJK_ORDINAL = re.compile(r"第(\d+)")

# URLs — numbers inside them are paths, ports and ids, not claims.
_RE_URL = re.compile(r"\b(?:https?|ftp)://\S+|\bwww\.\S+", re.IGNORECASE)

# CJK calendar fragments: 2026年, 10月19日, 5日. Each alternative
# carries a lookbehind rejecting digits and commas so the fragment must
# stand at the head of its own number; inside "1,000日元" the "00日"
# tail is part of a comma-grouped amount, not a day-of-month.
_RE_CJK_CALENDAR = re.compile(
    r"(?<![\d,])(?:19|20)\d{2}年|(?<![\d,])\d{1,2}月|(?<![\d,])\d{1,2}日")

# Four-digit years with explicit year context: "in 2024", "fiscal 2024",
# "FY2024" (the year token itself is guarded) and "2024 years" /
# "2024 fiscal years".
_RE_YEAR_PRE = re.compile(
    r"\b(?:in|of|since|by|from|fiscal|fy)\s+((?:19|20)\d{2})\b",
    re.IGNORECASE)
_RE_YEAR_WORD = re.compile(
    r"\b((?:19|20)\d{2})\s*(?:fiscal\s+)?(?:year|yr)s?\b", re.IGNORECASE)

# Sentence boundary: a run of terminal punctuation not followed by a
# digit (so decimal points survive), CJK commas, or newlines.
_SENTENCE_BOUNDARY_RE = re.compile(r"(?:[.!?;。！？；，、]+(?!\d)|\n+)")

# Word tokens used for anchor scanning: ASCII words or CJK runs.
_RE_WORD_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9'-]*|[一-龥]+")

# Bare number floor: separator-free numbers below this value are noise.
_MIN_BARE_NUMBER = 1000


class NumberConflictDetector(DocProcessor):
    """Flag the same measured claim repeated with different numbers.

    Documents about the same subject are full of measured claims, and
    copies drift: one paragraph says "revenue was 5 million", the next
    says "revenue reached 6 million", a translated section restates
    "5万" as "60000". Whatever the cause — retyped figures, stale
    copies, unit slips — a chunk pair that disagrees with itself is a
    data-quality signal worth surfacing *before* the numbers are
    embedded and retrieved. This processor scans every document with
    pure regular expressions (no model calls, no network, no
    dependencies) and records each disagreement in
    ``metadata[conflicts_key]``:

    .. code-block:: python

        {"anchor": "revenue", "dimension": "amount",
         "values": [{"value": 5000000, "text": "5 million",
                     "span": [16, 26], "sentence_index": 0},
                    {"value": 6000000, "text": "6 million",
                     "span": [61, 70], "sentence_index": 1}],
         "relative_gap": 0.166667}

    How a conflict is found:

    1. **Value extraction** — the StatisticsExtractor-style numeric
       forms are located within each sentence: percentages (``45%``,
       ``45.3 percent``, full-width ``45％``, CJK ``百分之四十五``),
       scaled amounts whose magnitude words resolve into the value with
       exact Decimal arithmetic (``5万`` -> 50000, ``3 million`` ->
       3000000, ``1.5亿`` -> 150000000, ``1.13万`` -> 11300 — never an
       ulp off), unit counts (``1,200 users``, ``5万次``) and bare
       numbers (comma-grouped ``1,234,567`` always; separator-free
       numbers only from 1000 up). Each value belongs to one
       *dimension* — ``percent`` or ``amount`` — and values only ever
       compare inside their own dimension: "growth was 45%" and
       "growth reached 45 million" are different claims, not a
       conflict.
    2. **Anchoring** — each number is attached to the claim's subject:
       a unit word directly glued to the number wins (``1,200 users``
       anchors on ``user``), otherwise the nearest noun-ish word within
       a 4-token window *before* the number ("revenue was 5 million" /
       "revenue reached 6 million" both anchor on ``revenue`` — link
       and measure verbs are skipped), otherwise the nearest noun-ish
       word within 4 tokens *after* it. English words are lowercased
       and lightly stemmed (trailing s / es / ed / ing stripped while
       the stem keeps at least three letters); CJK runs are reduced
       from the tail first (``营收达到`` -> ``营收``) and then from the
       head (time/determiner prefixes, ``2024年营收`` -> ``营收``),
       keeping short words like 日活 intact. Numbers with no noun in
       any window are dropped — a bare figure is not a claim about
       anything.
    3. **Grouping** — mentions sharing an anchor and dimension are
       chained while consecutive mentions sit within ``window_size``
       sentences of each other (the default 3 compares mentions inside
       a sliding 3-sentence window; mentions in sentences 1 and 4 fall
       into separate chains and never conflict). Each chain of two or
       more mentions is evaluated.
    4. **Conflict test** — inside a chain, any pair of values whose
       difference exceeds ``tolerance + near_conflict_ratio *`` the
       larger magnitude makes a conflict. With the defaults
       (``tolerance`` 0, ``near_conflict_ratio`` 0.001) identical
       normalized values and near-identical ones (a 0.1% relative
       difference, e.g. rounding drift) count as consistent; anything
       wider — 5 million against 6 million, ``5万`` against
       ``60000`` — disagrees. ``relative_gap`` records the worst
       offending pair's gap. Every mention keeps its text, span and
       sentence index; conflicts show at most 5 value records.

    False positives are guarded out before extraction: dates and ISO
    calendars (``2026-10-19``, ``10/19/2026``, CJK ``2026年10月19日``
    and bare ``2026年``/``10月``/``5日`` fragments), four-digit years
    with explicit year context (``in 2024``, ``fiscal 2024``,
    ``2024 years``), version tokens (``v1.2.3``, ``1.2.3``, IPs),
    ordinals (``21st``, ``1,000th``, ``第3``), URLs and slash/colon
    fragments inside them, and multiplier suffixes (``5000x``,
    ``5000倍``). Identical values repeated are *not* conflicts — they
    are counted in ``metadata[repeats_key]`` as ``consistent_repeats``.

    Alongside the conflict list, ``metadata[consistency_key]`` receives
    ``conflicts_found`` or ``consistent`` and ``metadata[count_key]``
    the full conflict count (the list itself is truncated to
    ``max_conflicts``, default 20). Documents pass through untouched in
    every other respect: text and id are never modified, order is
    preserved, and metadata mappings are copied before mutation.
    Everything is deterministic — the same text always yields the same
    conflicts — which makes the output safe to store, diff and test.
    The component extends the family of offline quality probes:
    ``StatisticsExtractor`` stamps numeric claims without comparing
    them, and lexical contradiction detectors flip on words like
    "however" without seeing numbers at all; this one compares the
    numbers themselves.

    Attributes:
        window_size: Maximum sentence distance for two mentions of the
            same anchor to share a chain, in [1, 5]; the default 3
            compares mentions inside a sliding 3-sentence window.
        max_conflicts: Maximum number of conflicts stored in the
            conflict list; must be an integer >= 1. ``conflict_count``
            still reflects every conflict found.
        tolerance: Absolute value difference tolerated before two
            values disagree; a number >= 0, default 0 (exact
            comparison).
        near_conflict_ratio: Relative difference tolerated before two
            values disagree (fraction of the larger magnitude); a
            number >= 0, default 0.001 so rounding drift of 0.1% stays
            consistent.
        conflicts_key: Metadata key the conflict list is written to; an
            empty value disables list stamping.
        count_key: Metadata key the full conflict count is written to;
            an empty value disables count stamping.
        consistency_key: Metadata key the overall verdict
            (``consistent`` / ``conflicts_found``) is written to; an
            empty value disables verdict stamping.
        repeats_key: Metadata key the count of consistent repeat groups
            is written to; an empty value disables repeat stamping.
    """

    window_size: int = 3
    max_conflicts: int = 20
    tolerance: float = 0
    near_conflict_ratio: float = 0.001
    conflicts_key: str = "number_conflicts"
    count_key: str = "conflict_count"
    consistency_key: str = "numeric_consistency"
    repeats_key: str = "consistent_repeats"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp number-conflict metadata onto every document.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; conflicts depend only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, in the same
            order, each stamped with its conflicts, verdict and repeat
            count; nothing is filtered or rewritten.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            conflicts, repeats = self._scan(doc.text or "")
            meta = dict(doc.metadata or {})
            if self.conflicts_key:
                meta[self.conflicts_key] = conflicts[:self.max_conflicts]
            if self.count_key:
                meta[self.count_key] = len(conflicts)
            if self.consistency_key:
                meta[self.consistency_key] = \
                    "conflicts_found" if conflicts else "consistent"
            if self.repeats_key:
                meta[self.repeats_key] = repeats
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Scanning
    # ------------------------------------------------------------------ #

    def _scan(self, text: str) -> Tuple[List[Dict[str, Any]], int]:
        """Collect conflicts and consistent repeats across one text.

        Args:
            text: Document text (None treated as empty).

        Returns:
            Tuple[List[Dict[str, Any]], int]: Conflicts in deterministic
            order (anchor, dimension, sentence position), and the number
            of mention chains that repeat a value consistently.
        """
        if not text:
            return [], 0

        groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for sent_index, sentence in enumerate(self._split_sentences(text)):
            offset, body = sentence
            for hit in self._extract(body):
                anchor = self._anchor(body, hit)
                if anchor is None:
                    # A number with no noun in any window is not a
                    # claim about anything measurable.
                    continue
                start, end = hit["span"]
                groups.setdefault((anchor, hit["dimension"]), []).append({
                    "anchor": anchor,
                    "dimension": hit["dimension"],
                    "value": hit["value"],
                    "text": hit["text"],
                    "span": [offset + start, offset + end],
                    "sentence_index": sent_index,
                })

        tolerance = Decimal(str(self.tolerance))
        ratio = Decimal(str(self.near_conflict_ratio))

        conflicts: List[Dict[str, Any]] = []
        repeats = 0
        for key in sorted(groups):
            mentions = groups[key]
            chains: List[List[Dict[str, Any]]] = []
            for mention in mentions:
                # Mentions arrive in sentence order, so chaining only
                # needs the gap to the previous mention.
                if chains and mention["sentence_index"] - \
                        chains[-1][-1]["sentence_index"] <= \
                        self.window_size - 1:
                    chains[-1].append(mention)
                else:
                    chains.append([mention])
            for chain in chains:
                if len(chain) < 2:
                    continue
                gap = self._worst_gap(chain, tolerance, ratio)
                if gap is None:
                    repeats += 1
                    continue
                conflicts.append({
                    "anchor": chain[0]["anchor"],
                    "dimension": chain[0]["dimension"],
                    "values": [
                        {"value": self._finalize(mention["value"]),
                         "text": mention["text"],
                         "span": mention["span"],
                         "sentence_index": mention["sentence_index"]}
                        for mention in chain[:_MAX_VALUES_SHOWN]
                    ],
                    "relative_gap": float(round(gap, 6)),
                })
        return conflicts, repeats

    def _worst_gap(self, chain: List[Dict[str, Any]], tolerance: Decimal,
                   ratio: Decimal) -> Optional[Decimal]:
        """Find the worst disagreeing pair gap inside one mention chain.

        Args:
            chain: Two or more mentions of one anchor and dimension, in
                sentence order.
            tolerance: Absolute tolerated difference.
            ratio: Relative tolerated difference (fraction of the
                larger magnitude).

        Returns:
            Optional[Decimal]: The relative gap of the widest
            disagreeing pair, or None when every pair agrees within
            tolerance (a consistent repeat).
        """
        worst: Optional[Decimal] = None
        for i in range(len(chain)):
            for j in range(i + 1, len(chain)):
                left = chain[i]["value"]
                right = chain[j]["value"]
                scale = max(abs(left), abs(right))
                if abs(left - right) > tolerance + ratio * scale:
                    gap = self._relative_gap(left, right)
                    if worst is None or gap > worst:
                        worst = gap
        return worst

    # ------------------------------------------------------------------ #
    # Sentence handling
    # ------------------------------------------------------------------ #

    @staticmethod
    def _split_sentences(text: str) -> List[Tuple[int, str]]:
        """Split text into sentences with their character offsets.

        Sentences are delimited by terminal punctuation (. ! ? ; and
        their CJK counterparts, plus CJK commas 、，) or newlines. A
        punctuation run followed by a digit is not a boundary, so
        decimal points ("5.5 million") never split a sentence. Each
        record carries the ``[start, start + len)`` offset of the
        trimmed sentence inside the original text.

        Args:
            text: Document text.

        Returns:
            List[Tuple[int, str]]: (offset, sentence) pairs in document
            order; empty segments are dropped.
        """
        sentences: List[Tuple[int, str]] = []
        cursor = 0
        boundaries = list(_SENTENCE_BOUNDARY_RE.finditer(text))
        for boundary in boundaries + [None]:
            end = boundary.start() if boundary else len(text)
            segment = text[cursor:end]
            stripped = segment.strip()
            if stripped:
                offset = cursor + (len(segment) - len(segment.lstrip()))
                sentences.append((offset, stripped))
            if boundary:
                cursor = boundary.end()
        return sentences

    # ------------------------------------------------------------------ #
    # Value extraction (StatisticsExtractor-style, per sentence)
    # ------------------------------------------------------------------ #

    def _extract(self, text: str) -> List[Dict[str, Any]]:
        """Collect every numeric claim in one sentence, in text order.

        Args:
            text: Sentence text (empty text yields no hits).

        Returns:
            List[Dict[str, Any]]: Hits sorted by span start, each
            holding value (Decimal) / dimension / unit / text / span.
        """
        if not text:
            return []

        # Guard spans first: any candidate overlapping one is a date,
        # version, ordinal, URL or year and is dropped outright.
        guarded: List[Tuple[int, int]] = []
        for pattern in (_RE_VERSION_V, _RE_MULTI_DOT, _RE_ISO_DATE,
                        _RE_SLASH_DATE_FULL, _RE_ORDINAL, _RE_URL,
                        _RE_CJK_CALENDAR):
            for match in pattern.finditer(text):
                guarded.append(match.span())
        for match in _RE_CJK_ORDINAL.finditer(text):
            guarded.append(match.span(1))
        for match in _RE_YEAR_PRE.finditer(text):
            guarded.append(match.span(1))
        for match in _RE_YEAR_WORD.finditer(text):
            guarded.append(match.span(1))

        candidates: List[Tuple[int, int, int, Dict[str, Any]]] = []
        for collector in (self._collect_percentages, self._collect_amounts):
            for start, end, hit in collector(text):
                if any(start < g_end and g_start < end
                       for g_start, g_end in guarded):
                    continue
                # Sort key: dimension priority, then document position,
                # then longer span first (-end).
                candidates.append((_DIM_PRIORITY[hit["dimension"]], start,
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
            hit["span"] = (start, end)
            taken.append((start, end))
            accepted.append((start, end, hit))

        accepted.sort(key=lambda item: item[0])
        return [hit for _, _, hit in accepted]

    def _collect_percentages(self, text: str):
        """Yield percentage hits: 45%, 45.3 percent, 45％, 百分之四十五.

        Args:
            text: Sentence text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples
            with dimension ``percent`` and no anchor unit.
        """
        for match in _RE_PERCENT_SIGN.finditer(text):
            yield self._hit(DIM_PERCENT, match, value_raw=match.group(1),
                            unit="")
        for match in _RE_PERCENT_WORD.finditer(text):
            yield self._hit(DIM_PERCENT, match, value_raw=match.group(1),
                            unit="")
        for match in _RE_PERCENT_CJK.finditer(text):
            raw = match.group(1)
            if raw[0].isdigit():
                value = self._to_decimal(raw)
            else:
                value = self._parse_cjk_numeral(raw)
            if value is None:
                continue
            yield (match.start(), match.end(), self._make_hit(
                DIM_PERCENT, value, "", match.group(0)))

    def _collect_amounts(self, text: str):
        """Yield amount hits: scaled, unit-count and bare numbers.

        A number glued directly onto a ``/`` or ``:`` separator belongs
        to a ratio, URL or clock in disguise and is never claimed as an
        amount.

        Args:
            text: Sentence text.

        Yields:
            Tuple[int, int, Dict[str, Any]]: (start, end, hit) triples
            with dimension ``amount``.
        """
        def _after_separator(match: re.Match) -> bool:
            """True when the matched number directly follows / or :."""
            before = text[max(0, match.start() - 1):match.start()]
            return before in ("/", ":", "：", "／")

        # Multiplier forms first so their longer spans win the overlap
        # race against the plain-unit regexes on the same number.
        # Scaling goes through Decimal: float multiplication is off by
        # an ulp for many two-decimal inputs ("1.13万").
        for match in _RE_COUNT_EN_MULT.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group(3) or ""
            if unit.lower() in _EN_UNIT_STOPWORDS:
                # "5 billion in cash": a function word is not a unit —
                # trim the hit back to the multiplier itself.
                end = match.end(2)
                unit = ""
            else:
                end = match.end()
            yield (match.start(), end, self._make_hit(
                DIM_AMOUNT, self._scaled_decimal(
                    match.group(1),
                    _EN_MULTIPLIERS[match.group(2).lower()]),
                unit, text[match.start():end]))
        for match in _RE_COUNT_CJK_MULT.finditer(text):
            if _after_separator(match):
                continue
            factor = 1
            for char in match.group(2):
                factor *= _CJK_MULTIPLIERS[char]
            yield (match.start(), match.end(), self._make_hit(
                DIM_AMOUNT, self._scaled_decimal(match.group(1), factor),
                match.group(3) or "", match.group(0)))
        for match in _RE_COUNT_EN_PLAIN.finditer(text):
            if _after_separator(match):
                continue
            if match.group(2).lower() in _EN_UNIT_STOPWORDS:
                continue
            yield (match.start(), match.end(), self._make_hit(
                DIM_AMOUNT, self._to_decimal(match.group(1)),
                match.group(2), match.group(0)))
        for match in _RE_COUNT_CJK_PLAIN.finditer(text):
            if _after_separator(match):
                continue
            unit = match.group(2)
            if unit[0] in _CJK_MULTIPLIERS:
                # 3.5万 belongs to the multiplier form above, not a
                # count of 万-things.
                continue
            yield (match.start(), match.end(), self._make_hit(
                DIM_AMOUNT, self._to_decimal(match.group(1)),
                unit, match.group(0)))
        for pattern in (_RE_COMMA_NUMBER, _RE_BARE_NUMBER):
            for match in pattern.finditer(text):
                if _after_separator(match):
                    continue
                value = self._to_decimal(match.group(1))
                if value < _MIN_BARE_NUMBER:
                    continue
                yield (match.start(), match.end(), self._make_hit(
                    DIM_AMOUNT, value, "", match.group(0)))

    @staticmethod
    def _hit(dimension: str, match: re.Match, value_raw: Optional[str],
             unit: str) -> Tuple[int, int, Dict[str, Any]]:
        """Build one (start, end, hit) candidate triple.

        Args:
            dimension: One of the two dimension constants.
            match: The regex match supplying the span and text.
            value_raw: Numeric text to parse, or None when the value is
                already resolved (percentages parse their own group).
            unit: Unit word glued to the number ("" when none).

        Returns:
            Tuple[int, int, Dict[str, Any]]: Candidate triple.
        """
        value = NumberConflictDetector._to_decimal(value_raw) \
            if value_raw is not None else Decimal(0)
        return (match.start(), match.end(),
                NumberConflictDetector._make_hit(
                    dimension, value, unit, match.group(0)))

    @staticmethod
    def _make_hit(dimension: str, value: Decimal, unit: str,
                  text: str) -> Dict[str, Any]:
        """Assemble one candidate hit dictionary.

        Args:
            dimension: Dimension constant.
            value: Parsed Decimal value.
            unit: Unit word glued to the number ("" when none).
            text: Matched text.

        Returns:
            Dict[str, Any]: Hit record without the span (added on
            acceptance).
        """
        return {"dimension": dimension, "value": value, "unit": unit,
                "text": text}

    # ------------------------------------------------------------------ #
    # Anchoring
    # ------------------------------------------------------------------ #

    def _anchor(self, text: str, hit: Dict[str, Any]) -> Optional[str]:
        """Find the anchor noun for one numeric hit inside its sentence.

        A unit word directly glued to the number wins (it is the
        nearest noun after: ``1,200 users`` anchors on ``user``).
        Otherwise the nearest noun-ish word within a 4-token window
        before the number is taken ("revenue was 5 million" and
        "revenue reached 6 million" both anchor on ``revenue``), and
        only when the before-window is empty does the scan continue on
        the after-side. CJK word tokens that overlap the number span
        are clipped to their prefix/suffix, so ``转化率百分之四十五``
        still offers ``转化率`` as a before-token.

        Args:
            text: Sentence text.
            hit: One accepted extraction hit with a local span.

        Returns:
            Optional[str]: The normalized anchor, or None when no
            noun-ish word sits in any window.
        """
        unit = hit.get("unit") or ""
        if unit:
            anchor = self._anchor_word(unit)
            if anchor is not None:
                return anchor

        start, end = hit["span"]
        before: List[Tuple[int, int, str]] = []
        after: List[Tuple[int, int, str]] = []
        for token in _RE_WORD_TOKEN.finditer(text):
            token_start, token_end = token.span()
            # Clip CJK runs that straddle the number so the parts
            # outside the span stay usable as anchor candidates.
            prefix_end = min(token_end, start)
            if token_start < prefix_end:
                before.append((token_start, prefix_end,
                               text[token_start:prefix_end]))
            suffix_start = max(token_start, end)
            if suffix_start < token_end:
                after.append((suffix_start, token_end,
                              text[suffix_start:token_end]))
        before = before[-_ANCHOR_WINDOW:]
        after = after[:_ANCHOR_WINDOW]

        for _, _, word in reversed(before):
            anchor = self._anchor_word(word)
            if anchor is not None:
                return anchor
        for _, _, word in after:
            anchor = self._anchor_word(word)
            if anchor is not None:
                return anchor
        return None

    @classmethod
    def _anchor_word(cls, word: str) -> Optional[str]:
        """Normalize one word into an anchor candidate.

        English words are lowercased and lightly stemmed (trailing
        s / es / ed / ing stripped while the stem keeps at least three
        letters); both the raw word and the stem are checked against
        the anchor stop set. CJK runs are reduced from the tail first
        (common verb/particle suffixes, longest first, iteratively) and
        then from the head (time/determiner characters, while two
        characters remain, so short words like 日活 survive); a run
        that strips to nothing is rejected.

        Args:
            word: One word token (ASCII word or CJK run).

        Returns:
            Optional[str]: The normalized anchor, or None when the word
            is a function word, measure verb or magnitude word.
        """
        if not word:
            return None
        if word[0].isascii() and word[0].isalpha():
            raw = word.lower()
            if raw in _EN_ANCHOR_STOP:
                return None
            stem = cls._stem(raw)
            if stem in _EN_ANCHOR_STOP:
                return None
            return stem
        stripped = word
        changed = True
        while changed and stripped:
            changed = False
            for suffix in _CJK_TAIL_STRIP:
                if stripped.endswith(suffix) and \
                        len(stripped) > len(suffix):
                    stripped = stripped[: -len(suffix)]
                    changed = True
                    break
        while len(stripped) > 2 and stripped[0] in _CJK_HEAD_STRIP:
            stripped = stripped[1:]
        return stripped or None

    @staticmethod
    def _stem(word: str) -> str:
        """Lightly stem an English word by trailing suffix stripping.

        Strips one trailing s / es / ed / ing suffix when the remaining
        stem keeps at least three letters, so "users" -> "user",
        "reached" -> "reach", "revenues" -> "revenue", while "its" and
        "was" survive intact.

        Args:
            word: Lowercased English word.

        Returns:
            str: The stemmed word (possibly unchanged).
        """
        for suffix in ("s", "es", "ed", "ing"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[: -len(suffix)]
        return word

    # ------------------------------------------------------------------ #
    # Numeric helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_decimal(raw: str) -> Decimal:
        """Parse a numeric token into a Decimal, dropping separators.

        Args:
            raw: Numeric text such as "1,200" or "3.5".

        Returns:
            Decimal: Parsed value (never None; regexes pre-validate
            shape).
        """
        return Decimal(raw.replace(",", ""))

    @staticmethod
    def _scaled_decimal(raw: str, factor: int) -> Decimal:
        """Parse a numeric token and scale it by an exact integer factor.

        The arithmetic stays in :class:`decimal.Decimal` so magnitude
        words fold into the value exactly: float multiplication misses
        by an ulp on many two-decimal inputs ("1.13万" would yield
        11299.999999999998 instead of 11300).

        Args:
            raw: Numeric text such as "1.13" or "2,000".
            factor: Exact integer multiplier (e.g. 10000 for 万).

        Returns:
            Decimal: The scaled value.
        """
        return Decimal(raw.replace(",", "")) * factor

    @staticmethod
    def _finalize(value: Decimal):
        """Render integral Decimals as ints so metadata stays compact.

        Args:
            value: Parsed Decimal value.

        Returns:
            int | float: ``Decimal("50000")`` becomes ``50000``;
            ``Decimal("3.5")`` becomes ``3.5``.
        """
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    @staticmethod
    def _relative_gap(left: Decimal, right: Decimal) -> Decimal:
        """Compute the relative gap between two values.

        Args:
            left: First value.
            right: Second value.

        Returns:
            Decimal: ``|left - right| / max(|left|, |right|)``, or 0
            when both values are zero.
        """
        scale = max(abs(left), abs(right))
        if scale == 0:
            return Decimal(0)
        return abs(left - right) / scale

    @staticmethod
    def _parse_cjk_numeral(raw: str) -> Optional[Decimal]:
        """Parse a basic CJK numeral sequence such as 四十五 or 三点五.

        Supports the digits 零〇一二两三四五六七八九, the unit characters
        十百千, the section characters 万亿 and the decimal point 点.
        None is returned only when no numeral character was consumed at
        all.

        Args:
            raw: CJK numeral text without the leading 百分之.

        Returns:
            Optional[Decimal]: Parsed value (45 for 四十五, 3.5 for
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
            return Decimal(f"{whole}." + "".join(str(d) for d in fraction))
        return Decimal(whole)

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'NumberConflictDetector':
        """Initialize and validate the detector from component config.

        Validation happens eagerly at load time: a silently
        misconfigured window or tolerance would corrupt stored verdicts
        long before anyone noticed.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            NumberConflictDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "window_size") and \
                doc_processor_configer.window_size is not None:
            window = doc_processor_configer.window_size
            if isinstance(window, bool) or not isinstance(window, int):
                raise ValueError("window_size must be an integer")
            self.window_size = window
            if not 1 <= self.window_size <= 5:
                raise ValueError("window_size must be in [1, 5]")

        if hasattr(doc_processor_configer, "max_conflicts") and \
                doc_processor_configer.max_conflicts is not None:
            cap = doc_processor_configer.max_conflicts
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_conflicts must be an integer")
            self.max_conflicts = cap
            if self.max_conflicts < 1:
                raise ValueError("max_conflicts must be >= 1")

        if hasattr(doc_processor_configer, "tolerance") and \
                doc_processor_configer.tolerance is not None:
            tolerance = doc_processor_configer.tolerance
            if isinstance(tolerance, bool) or \
                    not isinstance(tolerance, (int, float)):
                raise ValueError("tolerance must be a number")
            self.tolerance = tolerance
            if self.tolerance < 0:
                raise ValueError("tolerance must be >= 0")

        if hasattr(doc_processor_configer, "near_conflict_ratio") and \
                doc_processor_configer.near_conflict_ratio is not None:
            ratio = doc_processor_configer.near_conflict_ratio
            if isinstance(ratio, bool) or \
                    not isinstance(ratio, (int, float)):
                raise ValueError("near_conflict_ratio must be a number")
            self.near_conflict_ratio = ratio
            if self.near_conflict_ratio < 0:
                raise ValueError("near_conflict_ratio must be >= 0")

        for attr in ("conflicts_key", "count_key", "consistency_key",
                     "repeats_key"):
            value = getattr(doc_processor_configer, attr, None)
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, value)

        return self
