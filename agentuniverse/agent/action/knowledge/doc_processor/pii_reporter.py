# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: pii_reporter.py

"""
PII detection-and-report pre-processing component.

Detects personally identifiable information in documents at knowledge
*pre-processing* (insertion) time and records what it found in document
metadata — WITHOUT modifying the text. This is deliberately the opposite
trade-off from ``SensitiveDataRedactor``: the redactor is a post-processing
component that masks matches in recalled text (a destructive, point-in-time
edit), while this component is an audit pass. Knowing *that* a corpus
contains card numbers, resident IDs or IBANs — where, how many, and with
what confidence — lets a pipeline owner decide what to do before anything is
embedded or stored: drop the document, redact it, route it to a restricted
store, or escalate for review. A reporting pass therefore composes cleanly
with the redactor instead of duplicating it: report first, decide, then (if
warranted) destroy.

Detection is regex-shaped plus checksum-validated, so precision is high
without any model call: credit-card-shaped 13-19 digit runs count as
``card`` only when they pass the Luhn checksum (otherwise the same run is
reported as the weaker ``numeric_id``), China resident IDs must satisfy the
GB 11643 modulo-11 checksum, and IBANs are checked against a
length-per-country table for the most common countries and the ISO 13616
mod-97 check digit via exact integer arithmetic. Emails and phone numbers
are shape-matched, with phone candidates guarded against date- and
arithmetic-looking context (``2023-01-15`` or ``3 + 86 137 ...`` are not
phones). Passport numbers are only ever reported as the explicitly
low-confidence ``passport_candidate`` — the 2-letters-plus-6-digits shape is
shared with too many invoice and case numbers to claim more.

Privacy of the report itself matters as much as the detection: metadata is
for logs, indexes and audits, so a finding NEVER carries the matched value.
Every entry stores only a masked form (first two plus last two characters,
``ab***yz``), the character span, the kind and a confidence level. The full
text stays where it already was — in the document, untouched.

Output per document: ``metadata['pii']`` — the capped list of findings;
``metadata['pii_counts']`` — total counts per kind (not subject to the cap);
``metadata['pii_risk']`` — none / low / medium / high, where card numbers,
resident IDs and IBANs rate high. Everything is deterministic, offline and
dependency-free (pure ``re`` and integer arithmetic), so runs are
reproducible and unit-testable without network access.
"""

import logging
import re
from typing import Any, Dict, List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Detected entity kinds.
KIND_EMAIL = "email"
KIND_PHONE = "phone"
KIND_CARD = "card"
KIND_NUMERIC_ID = "numeric_id"
KIND_CN_ID = "cn_id"
KIND_IBAN = "iban"
KIND_PASSPORT = "passport_candidate"

_ALL_KINDS = (
    KIND_EMAIL, KIND_PHONE, KIND_CARD, KIND_NUMERIC_ID,
    KIND_CN_ID, KIND_IBAN, KIND_PASSPORT,
)

# When two detectors claim overlapping spans, the stronger kind wins: a
# checksum-validated identifier explains the text better than a loose shape
# that happens to cover the same characters (e.g. the digit tail of an IBAN
# is card-shaped; the local part of "+1 202 555 0179" is a 13-digit run).
# Lower number = stronger.
_KIND_PRIORITY = {
    KIND_CN_ID: 0,
    KIND_IBAN: 1,
    KIND_PHONE: 2,
    KIND_CARD: 3,
    KIND_EMAIL: 4,
    KIND_PASSPORT: 5,
    KIND_NUMERIC_ID: 6,
}

# How sure the detector is that a match really is that kind.
_CONFIDENCE = {
    KIND_CN_ID: "high",       # GB 11643 checksum passed
    KIND_IBAN: "high",        # mod-97 + country length passed
    KIND_CARD: "high",        # Luhn checksum passed
    KIND_EMAIL: "high",       # unambiguous address shape
    KIND_PHONE: "medium",     # shape + context guards only
    KIND_NUMERIC_ID: "medium",  # 13-19 digit run that failed Luhn
    KIND_PASSPORT: "low",     # shape shared with invoice/case numbers
}

# How damaging the data would be if it leaked; drives pii_risk.
_RISK = {
    KIND_CARD: "high",
    KIND_CN_ID: "high",
    KIND_IBAN: "high",
    KIND_PHONE: "medium",
    KIND_NUMERIC_ID: "medium",
    KIND_EMAIL: "low",
    KIND_PASSPORT: "low",
}
_RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}

# ------------------------------------------------------------------ #
# Patterns
# ------------------------------------------------------------------ #
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Phone shapes: international with explicit country code (separated or
# contiguous), China mobile, and North-American 3-3-4 with separators.
# Loose 10-digit runs are deliberately NOT matched.
_PHONE_RES = [
    re.compile(r"\+\d{1,3}[\s.-]\d{2,4}(?:[\s.-]\d{2,4}){1,5}(?!\d)"),
    re.compile(r"\+\d{11,15}(?!\d)"),
    re.compile(r"\b1[3-9]\d{9}(?!\d)"),
    re.compile(r"\(\d{3}\)[\s.]?\d{3}[\s.-]\d{4}(?!\d)"),
    re.compile(r"(?<![\d(])(?:1[\s.-])?\d{3}[\s.-]\d{3}[\s.-]\d{4}(?!\d)"),
]

# Context that disqualifies phone candidates: dates and arithmetic.
_DATE_RES = [
    re.compile(r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b"),
    re.compile(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b"),
]
# A '+candidate' directly preceded by a number or closing bracket looks
# like addition, not a country code ("3 +86 137 ..."). An '=' whose right
# hand side continues in digits ("growth = 44 123 456 7890") marks an
# arithmetic value, and '=' or '+' followed by another number right after
# the candidate marks the continuation of one. Separators common in
# prose ('-', '/', '*') are deliberately NOT treated as arithmetic.
_ARITH_OPERAND_BEFORE = re.compile(r"(?:\d|\))\s*$")
_ARITH_ASSIGN_BEFORE = re.compile(r"=\s*[\d\s]*$")
_ARITH_AFTER = re.compile(r"^\s*[=+]\s*\d")

# Credit-card shape: 13 to 19 digits with single spaces/dashes tolerated
# between groups ("4111 1111 1111 1111", "3782-8224-6310-005").
_CARD_RE = re.compile(r"\b(?:\d[ -]?){12,18}\d(?!\d)")

# China resident identity card: 6-digit region code, birth date, 3-digit
# sequence and the GB 11643 check character.
_CN_ID_RE = re.compile(r"\b[1-9]\d{5}(?:19|20)\d{2}"
                       r"(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])"
                       r"\d{3}[\dXx](?![\dXx])")

# IBAN loose shape (spaces tolerated); country length + mod-97 decide.
_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{1,4}){3,10}(?![A-Z0-9])")
# Strips the trailing space-delimited group from an IBAN candidate.
_IBAN_TRIM_RE = re.compile(r" ?[A-Z0-9]+$")

# Passport-ish document number: 2 letters + 6 digits. Reported only as a
# low-confidence candidate.
_PASSPORT_RE = re.compile(r"\b[A-Z]{2}\d{6}(?![A-Z0-9])")

# Total length (characters, spaces removed) of an IBAN per country for the
# most common issuing countries. Anything else is not validated and thus
# never reported.
_IBAN_LENGTHS = {
    "DE": 22, "GB": 22, "FR": 27, "ES": 24, "IT": 27,
    "NL": 18, "BE": 16, "CH": 21, "AT": 20, "PL": 28,
}

# GB 11643-1999 checksum: weights for the first 17 digits and the check
# character table indexed by (weighted sum mod 11).
_CN_ID_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
_CN_ID_CHECK_CODES = "10X98765432"

# ------------------------------------------------------------------ #
# Checksum helpers
# ------------------------------------------------------------------ #
def _luhn_ok(digits: str) -> bool:
    """Return True when ``digits`` passes the Luhn checksum.

    Args:
        digits: Digit string (no separators).

    Returns:
        bool: Luhn validity.
    """
    total, parity = 0, len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _cn_id_ok(value: str) -> bool:
    """Validate an 18-character China resident ID (GB 11643 modulo-11).

    Args:
        value: The 18 matched characters (last may be X/x).

    Returns:
        bool: True when the check character matches the weighted sum.
    """
    value = value.upper()
    total = sum(int(value[i]) * _CN_ID_WEIGHTS[i] for i in range(17))
    return _CN_ID_CHECK_CODES[total % 11] == value[17]


def _iban_ok(normalized: str) -> bool:
    """Validate a space-free, uppercase IBAN candidate (ISO 13616 mod-97).

    The country code must be in the supported length table and the total
    length must match it; the check is then the standard rearrangement
    (BBAN + country + check digits), letters mapped to 10..35, interpreted
    as one big integer that must be congruent to 1 modulo 97. Python's
    arbitrary-precision integers make this exact — no chunking needed.

    Args:
        normalized: Uppercase alphanumeric IBAN candidate, no spaces.

    Returns:
        bool: True when the candidate is a structurally valid IBAN.
    """
    if len(normalized) < 5 or not normalized[:2].isalpha() \
            or not normalized[2:4].isdigit():
        return False
    expected = _IBAN_LENGTHS.get(normalized[:2])
    if expected is None or len(normalized) != expected:
        return False
    rearranged = normalized[4:] + normalized[:4]
    remainder = 0
    for ch in rearranged:
        # ISO 13616 reads the rearranged string as a DECIMAL number in
        # which every letter expands to its two-digit code (A=10..Z=35):
        # appending a digit multiplies by 10, appending a letter by 100.
        if "0" <= ch <= "9":
            remainder = (remainder * 10 + int(ch)) % 97
        else:
            remainder = (remainder * 100 + int(ch, 36)) % 97
    return remainder == 1


def _mask(value: str) -> str:
    """Mask a matched value for metadata: first2 + *** + last2.

    Values of four characters or fewer are fully masked so nothing is
    revealed; every kind this component reports is at least six characters
    long, so in practice exactly two head and two tail characters survive —
    enough to correlate findings across runs, far too little to reuse the
    data.

    Args:
        value: The raw matched text.

    Returns:
        str: The masked representation; never the full value.
    """
    if len(value) <= 4:
        return "***"
    return value[:2] + "***" + value[-2:]


class PIIReporter(DocProcessor):
    """Detect PII in documents and report it via metadata; text untouched.

    The reporting counterpart to ``SensitiveDataRedactor``: that component
    masks matches in place (post-processing, destructive), while this one
    audits documents at pre-processing time and leaves every character of
    the text alone. Each document is stamped with a capped list of masked
    findings, per-kind totals and an overall risk level, so pipelines can
    decide — drop, redact, restrict or review — before the text reaches an
    embedding model or a store.

    Attributes:
        kinds: Detector kinds to run. Defaults to all seven; ``card`` and
            ``numeric_id`` share one digit-run scan — Luhn-passing runs
            become ``card``, failing runs become ``numeric_id``.
        max_findings: Maximum number of findings kept in
            ``metadata[pii_key]`` (default 100). Counts and risk always
            reflect every finding, even beyond the cap.
        pii_key: Metadata key for the findings list; '' disables stamping.
        counts_key: Metadata key for the per-kind counts; '' disables.
        risk_key: Metadata key for the overall risk level; '' disables.
    """

    kinds: List[str] = list(_ALL_KINDS)
    max_findings: int = 100
    pii_key: str = "pii"
    counts_key: str = "pii_counts"
    risk_key: str = "pii_risk"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Scan each document for PII and stamp findings into metadata.

        Args:
            origin_docs: Documents entering the knowledge pipeline.
            query: Unused; kept for interface compatibility.

        Returns:
            List[Document]: The same documents, with text, id and all
            pre-existing metadata unchanged and PII findings added under
            the configured metadata keys.
        """
        self._validate_config()
        enabled = set(self.kinds)
        for doc in origin_docs:
            text = doc.text or ""
            findings = self._find_all(text, enabled)
            findings.sort(key=lambda f: (f["span"][0], f["span"][1]))

            counts: Dict[str, int] = {}
            risk = "none"
            for finding in findings:
                counts[finding["kind"]] = counts.get(finding["kind"], 0) + 1
                if _RISK_ORDER[_RISK[finding["kind"]]] > _RISK_ORDER[risk]:
                    risk = _RISK[finding["kind"]]

            reported = findings[:self.max_findings]
            if len(findings) > len(reported):
                logger.debug(
                    "PIIReporter: %d findings truncated to %d for metadata",
                    len(findings), len(reported))

            metadata = dict(doc.metadata or {})
            if self.pii_key:
                metadata[self.pii_key] = reported
            if self.counts_key:
                metadata[self.counts_key] = counts
            if self.risk_key:
                metadata[self.risk_key] = risk
            doc.metadata = metadata
        return origin_docs

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #
    def _find_all(self, text: str, enabled: set) -> List[Dict[str, Any]]:
        """Run every enabled detector and resolve span overlaps.

        Args:
            text: Document text.
            enabled: Set of enabled kinds.

        Returns:
            List[Dict]: Non-overlapping findings, each a dict with kind,
            masked text, span [start, end) and confidence. The stronger
            kind wins an overlap (see ``_KIND_PRIORITY``); survivors are
            re-sorted by span by the caller.
        """
        candidates: List[Dict[str, Any]] = []

        def add(kind: str, start: int, end: int) -> None:
            candidates.append({
                "kind": kind,
                "text": _mask(text[start:end]),
                "span": [start, end],
                "confidence": _CONFIDENCE[kind],
                "_priority": _KIND_PRIORITY[kind],
            })

        # Date-shaped spans disqualify overlapping phone and numeric_id
        # candidates ("2023-01-15" digit groups are calendar data).
        date_spans = [(m.start(), m.end())
                      for pattern in _DATE_RES
                      for m in pattern.finditer(text)]

        if KIND_EMAIL in enabled:
            for m in _EMAIL_RE.finditer(text):
                add(KIND_EMAIL, m.start(), m.end())

        if KIND_PHONE in enabled:
            for pattern in _PHONE_RES:
                for m in pattern.finditer(text):
                    if self._context_ok(text, m.start(), m.end(),
                                        date_spans):
                        add(KIND_PHONE, m.start(), m.end())

        if KIND_CARD in enabled or KIND_NUMERIC_ID in enabled:
            for m in _CARD_RE.finditer(text):
                digits = m.group(0).replace(" ", "").replace("-", "")
                is_card = _luhn_ok(digits)
                if is_card:
                    # A Luhn-passing run is a card regardless of context;
                    # the checksum is strong enough evidence on its own.
                    if KIND_CARD in enabled:
                        add(KIND_CARD, m.start(), m.end())
                elif KIND_NUMERIC_ID in enabled and \
                        self._context_ok(text, m.start(), m.end(),
                                         date_spans):
                    # A failing run might just be arithmetic or another
                    # number-shaped construct; apply the context guards.
                    add(KIND_NUMERIC_ID, m.start(), m.end())

        if KIND_CN_ID in enabled:
            for m in _CN_ID_RE.finditer(text):
                if _cn_id_ok(m.group(0)):
                    add(KIND_CN_ID, m.start(), m.end())

        if KIND_IBAN in enabled:
            pos = 0
            while True:
                m = _IBAN_RE.search(text, pos)
                if m is None:
                    break
                # Space-separated IBANs in a list make the greedy shape
                # swallow the neighbours ("CH93 ... BE68 ..."): walk the
                # candidate's groups from the longest down and report the
                # longest prefix that passes validation, then resume
                # scanning right after it so the neighbour is found too.
                candidate = m.group(0)
                reported_end = None
                while candidate:
                    if _iban_ok(candidate.replace(" ", "")):
                        end = m.start() + len(candidate)
                        # A valid prefix glued directly to more alphanumerics
                        # is part of a longer token, not a standalone IBAN.
                        if end >= len(text) or not text[end].isalnum():
                            reported_end = end
                            add(KIND_IBAN, m.start(), end)
                        break
                    trimmed = _IBAN_TRIM_RE.sub("", candidate)
                    if trimmed == candidate:
                        break
                    candidate = trimmed
                pos = reported_end if reported_end is not None else m.end()

        if KIND_PASSPORT in enabled:
            for m in _PASSPORT_RE.finditer(text):
                add(KIND_PASSPORT, m.start(), m.end())

        # Overlap resolution: stronger kinds claim their spans first.
        candidates.sort(key=lambda c: (c["_priority"],
                                       c["span"][0], c["span"][1]))
        kept: List[Dict[str, Any]] = []
        for candidate in candidates:
            s, e = candidate["span"]
            if any(s < k["span"][1] and k["span"][0] < e for k in kept):
                continue
            kept.append({k: v for k, v in candidate.items()
                         if k != "_priority"})
        return kept

    @staticmethod
    def _context_ok(text: str, start: int, end: int,
                    date_spans: List[tuple]) -> bool:
        """Guard a candidate against date- and math-like context.

        Used for phone candidates and Luhn-failing digit runs, whose
        shapes alone are not distinctive enough.

        Args:
            text: Full document text.
            start: Candidate start offset.
            end: Candidate end offset.
            date_spans: Spans of date-shaped substrings in ``text``.

        Returns:
            True when the candidate may be reported.
        """
        # Inside or adjacent to a date-shaped run: "2023-01-15" style
        # digit groups are calendar data, not phone numbers.
        for ds, de in date_spans:
            if start < de and ds < end:
                return False
        prefix = text[max(0, start - 8):start]
        # "3 +86 137 ..." — a candidate starting with '+' right after a
        # number is an addition operand, not a country code.
        if text[start:start + 1] == "+" and \
                _ARITH_OPERAND_BEFORE.search(prefix):
            return False
        # "growth = 44 123 456 7890" — the right-hand side of an
        # assignment whose digits continue into the candidate.
        if _ARITH_ASSIGN_BEFORE.search(prefix):
            return False
        # "... 456 7890 = 12" — an '=' or '+' followed by another number
        # marks the continuation of an arithmetic expression.
        if _ARITH_AFTER.match(text[end:end + 8]):
            return False
        return True

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Validate configuration; raise ValueError on anything invalid.

        A privacy component must not fail open: an unknown detector kind
        or a nonsensical cap raises instead of being silently skipped.
        """
        if not isinstance(self.kinds, (list, tuple)) or not self.kinds:
            raise ValueError(
                "kinds must be a non-empty list of detector kinds, got "
                f"{self.kinds!r}")
        unknown = [kind for kind in self.kinds if kind not in _ALL_KINDS]
        if unknown:
            raise ValueError(
                f"Unknown PII detector kinds {unknown}. Known kinds: "
                f"{list(_ALL_KINDS)}.")
        if isinstance(self.max_findings, bool) or \
                not isinstance(self.max_findings, int) or \
                self.max_findings < 1:
            raise ValueError(
                f"max_findings must be an integer >= 1, got "
                f"{self.max_findings!r}")
        for key_attr in ("pii_key", "counts_key", "risk_key"):
            if not isinstance(getattr(self, key_attr), str):
                raise ValueError(f"{key_attr} must be a string")

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) -> 'PIIReporter':
        """Initialize and eagerly validate from component configuration.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            PIIReporter: The initialized instance.

        Raises:
            ValueError: On invalid configuration values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "kinds") and \
                doc_processor_configer.kinds is not None:
            self.kinds = list(doc_processor_configer.kinds)
        if hasattr(doc_processor_configer, "max_findings") and \
                doc_processor_configer.max_findings is not None:
            self.max_findings = doc_processor_configer.max_findings
        if hasattr(doc_processor_configer, "pii_key") and \
                doc_processor_configer.pii_key is not None:
            self.pii_key = doc_processor_configer.pii_key
        if hasattr(doc_processor_configer, "counts_key") and \
                doc_processor_configer.counts_key is not None:
            self.counts_key = doc_processor_configer.counts_key
        if hasattr(doc_processor_configer, "risk_key") and \
                doc_processor_configer.risk_key is not None:
            self.risk_key = doc_processor_configer.risk_key

        # Validate eagerly: a misconfigured reporter that silently scanned
        # nothing would be indistinguishable from a clean corpus.
        self._validate_config()
        return self
