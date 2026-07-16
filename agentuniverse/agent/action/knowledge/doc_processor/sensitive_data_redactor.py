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
unit-testable offline. The built-in entity patterns are deliberately
high-precision (structured formats such as emails, credit-card digit runs,
China resident-id, US SSN, IPv4 addresses, well-known API-key prefixes) to
avoid the noisy over-matching that a loose "find anything private" heuristic
would produce. ``phone`` is available but opt-in, since phone matching is
inherently fuzzier. Callers can add ``custom_patterns`` for domain-specific
identifiers.

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
            for name, pattern in patterns:
                text, count = pattern.subn(self.replacement, text)
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
        """Return ``(name, compiled_pattern)`` for enabled + custom entities."""
        compiled: List[tuple] = []
        for entity in self.entities:
            raw = _BUILTIN_PATTERNS.get(entity)
            if raw is None:
                logger.warning(
                    f"Unknown sensitive-data entity '{entity}'; skipping.")
                continue
            compiled.append((entity, re.compile(raw)))
        for entry in self.custom_patterns or []:
            name = entry.get("name")
            raw = entry.get("pattern")
            if not name or not raw:
                logger.warning(
                    "custom_patterns entry missing 'name' or 'pattern'; "
                    "skipping.")
                continue
            try:
                compiled.append((name, re.compile(raw)))
            except re.error as exc:
                logger.warning(
                    f"Invalid custom_patterns regex for '{name}': {exc}; "
                    f"skipping.")
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
        return self
