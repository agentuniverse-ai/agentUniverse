# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: sensitive_data_redactor.py

"""
Sensitive-data (PII) redaction post-processor.

Redacts common personally identifiable information from the documents recalled
by a RAG pipeline *before* they are handed to the LLM, so secrets and personal
data do not leak into model context. It is the *post-processing* direction of
issue #248 (knowledge post-processing components) and is distinct from every
existing doc processor: none of them alter text for privacy/compliance.

Detection is regex-based, deterministic, and dependency-free, so it is fully
unit-testable offline. The built-in entity patterns combine a structured
*shape* (emails, credit-card digit runs, China resident-id, US SSN, IPv4
addresses, well-known API-key prefixes) with a semantic check so a
plausible-looking but invalid value is not redacted: credit cards pass the
Luhn checksum, IPv4 octets are in range, China resident IDs and US SSNs pass
their structural/checksum rules. This keeps false positives low without the
noisy over-matching a loose "find anything private" heuristic would produce.
``phone`` is available but opt-in, since phone matching is inherently fuzzier.
Callers can add ``custom_patterns`` for domain-specific identifiers.

Configuration is validated eagerly: an unknown entity, a malformed custom
entry, or an invalid regex raises at load time rather than being silently
skipped — a privacy component must not fail open.

Each match is replaced with ``replacement`` (default ``[REDACTED]``); an
optional per-document ``redaction_summary`` records how many of each entity
were removed, so downstream stages can tell that redaction ran.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# High-precision built-in patterns. Each matches a structured identifier shape
# rather than a loose guess, to keep false positives low.
_BUILTIN_PATTERNS: Dict[str, str] = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "credit_card": r"\b\d{13,16}\b",
    # China resident identity card (18 digits, last may be X), date-structured.
    "id_card": r"\b[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])"
               r"(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "api_key": r"(?:sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
               r"gh[pousr]_[A-Za-z0-9]{36,}|glpat-[A-Za-z0-9_-]{20,})",
    # Opt-in: phone matching is fuzzier, so it is not on by default.
    "phone": r"(?:\b1[3-9]\d{9}\b|\b\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b)",
}

# Semantic validators for built-in entities whose shape alone is not enough.
# A match is only redacted when its validator returns True, so e.g. a random
# 13-16 digit run is not treated as a credit card and 999.999.999.999 is not
# treated as an IP. Entities without an entry here have no extra check.
def _luhn_ok(match: "re.Match") -> bool:
    digits = match.group(0)
    total, parity = 0, len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _ipv4_ok(match: "re.Match") -> bool:
    return all(0 <= int(part) <= 255 for part in match.group(0).split("."))


_CN_ID_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
_CN_ID_CHECK_CODES = "10X98765432"


def _china_id_card_ok(match: "re.Match") -> bool:
    digits = match.group(0).upper()
    total = sum(int(digits[i]) * _CN_ID_WEIGHTS[i] for i in range(17))
    return _CN_ID_CHECK_CODES[total % 11] == digits[17]


def _us_ssn_ok(match: "re.Match") -> bool:
    area, group, serial = match.group(0).split("-")
    area_num = int(area)
    if area_num == 0 or area_num == 666 or 900 <= area_num <= 999:
        return False
    if group == "00" or serial == "0000":
        return False
    return True


_BUILTIN_VALIDATORS = {
    "credit_card": _luhn_ok,
    "ip_address": _ipv4_ok,
    "id_card": _china_id_card_ok,
    "ssn": _us_ssn_ok,
}


class SensitiveDataRedactor(DocProcessor):
    """Redact sensitive/PII patterns from recalled document text.

    Attributes:
        entities: Built-in entity types to redact. Defaults to a high-precision
            set; add ``"phone"`` to enable phone redaction.
        replacement: Text substituted for every match.
        custom_patterns: Extra ``{"name": ..., "pattern": ...}`` regex entries
            for domain-specific identifiers.
        log_key: Metadata key under which a ``{entity: count}`` summary is
            stamped on each document; set to ``None`` to omit it.
    """

    entities: List[str] = [
        "email", "credit_card", "id_card", "ssn", "ip_address", "api_key"]
    replacement: str = "[REDACTED]"
    custom_patterns: List[Dict[str, str]] = []
    log_key: Optional[str] = "redaction_summary"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Redact configured entities from each document's text in place.

        Args:
            origin_docs: Documents recalled by the knowledge query.
            query: Unused; kept for interface compatibility.

        Returns:
            The same documents with sensitive matches replaced by
            ``replacement`` and, when ``log_key`` is set, a per-document
            redaction summary in their metadata.
        """
        patterns = self._compiled_patterns()
        for doc in origin_docs:
            text = doc.text or ""
            summary: Dict[str, int] = {}
            for name, pattern, validator in patterns:
                if validator is None:
                    text, count = pattern.subn(self.replacement, text)
                else:
                    # Only redact matches that pass the semantic check; leave
                    # structurally invalid values (e.g. a non-Luhn digit run,
                    # 999.999.999.999) untouched and uncounted.
                    count = 0

                    def _repl(m, validator=validator):
                        nonlocal count
                        if validator(m):
                            count += 1
                            return self.replacement
                        return m.group(0)

                    text = pattern.sub(_repl, text)
                if count:
                    summary[name] = count
            doc.text = text
            if self.log_key is not None:
                metadata = dict(doc.metadata or {})
                metadata[self.log_key] = summary
                doc.metadata = metadata
        return origin_docs

    # ------------------------------------------------------------------ #
    # Pattern compilation
    # ------------------------------------------------------------------ #
    def _compiled_patterns(self) -> List[tuple]:
        """Return ``(name, compiled_pattern, validator)`` triples.

        A privacy component must not fail open: an unknown entity, a malformed
        custom entry, or an invalid regex is a configuration error and raises
        ``ValueError`` rather than being logged and skipped (a silent skip would
        disable exactly the protection the operator believes is active).
        """
        compiled: List[tuple] = []
        for entity in self.entities:
            raw = _BUILTIN_PATTERNS.get(entity)
            if raw is None:
                raise ValueError(
                    f"Unknown sensitive-data entity {entity!r}. Known "
                    f"entities: {sorted(_BUILTIN_PATTERNS)}.")
            compiled.append((entity, re.compile(raw),
                             _BUILTIN_VALIDATORS.get(entity)))
        for entry in self.custom_patterns or []:
            if (not isinstance(entry, dict)
                    or "name" not in entry or "pattern" not in entry):
                raise ValueError(
                    f"Each custom_patterns entry must be a dict with 'name' and "
                    f"'pattern' keys, got {entry!r}.")
            name, raw = entry["name"], entry["pattern"]
            if not isinstance(name, str) or not name \
                    or not isinstance(raw, str) or not raw:
                raise ValueError(
                    f"custom_patterns entry has an empty or non-string "
                    f"'name'/'pattern': {entry!r}.")
            try:
                compiled.append((name, re.compile(raw), None))
            except re.error as exc:
                raise ValueError(
                    f"Invalid custom_patterns regex for {name!r}: {exc}") from exc
        return compiled

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'SensitiveDataRedactor':
        """Initialize the redactor from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "entities"):
            self.entities = doc_processor_configer.entities
        if hasattr(doc_processor_configer, "replacement"):
            self.replacement = doc_processor_configer.replacement
        if hasattr(doc_processor_configer, "custom_patterns"):
            self.custom_patterns = doc_processor_configer.custom_patterns
        if hasattr(doc_processor_configer, "log_key"):
            self.log_key = doc_processor_configer.log_key
        # Validate and compile eagerly so a misconfiguration (unknown entity,
        # malformed custom entry, invalid regex) fails loudly at load time
        # rather than silently disabling redaction at processing time.
        self._compiled_patterns()
        return self
