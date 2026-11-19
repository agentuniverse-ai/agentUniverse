# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: contact_entity_extractor.py

import re
from typing import Dict, List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Supported entity kinds, in canonical order (also the default order of the
# stamped metadata mapping).
SUPPORTED_ENTITY_TYPES = ("email", "url", "phone")

# High-precision built-in patterns. Each matches a structured shape rather
# than a loose guess so that order numbers, long digit runs and bare domain
# mentions are not mistaken for entities.
#
# email: local part @ domain with a letter-only TLD of 2+ characters.
# url: scheme://host[:port][/path] or a bare www. host; the path excludes
#   whitespace, quotes, brackets and CJK blocks (Chinese prose carries no
#   spaces, so an unexcluded CJK character class would swallow the sentence
#   after the URL). Unencoded CJK inside a path is therefore cut — a
#   documented trade-off, as real-world URLs percent-encode non-ASCII.
# phone: mainland-China mobile (1[3-9] + 9 digits), North-American number
#   with mandatory separators, or a leading-plus international form with
#   separators. A bare 10-digit run is deliberately NOT a phone: without
#   separators it is more likely an order id.
ENTITY_PATTERNS: Dict[str, re.Pattern] = {
    "email": re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "url": re.compile(
        r"https?://[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*(?::\d{1,5})?"
        r"(?:/[^\s<>\"'{}\[\]"
        r"\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]*)?"
        r"|www\.[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*(?::\d{1,5})?"
        r"(?:/[^\s<>\"'{}\[\]"
        r"\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]*)?"),
    "phone": re.compile(
        r"(?<![0-9])1[3-9][0-9]{9}(?![0-9])"
        r"|(?<![0-9])\(?[0-9]{3}\)?[ .-][0-9]{3}[ .-][0-9]{4}(?![0-9])"
        r"|\+[0-9]{1,3}[ -][0-9]{2,4}(?:[ -][0-9]{2,4}){1,3}(?![0-9])"),
}

# Trailing sentence punctuation stripped from a raw match. Full-width forms
# are included because CJK sentences end without spaces.
_TRAIL_PUNCT = ".,;:!?\"'" + "。，；：！？、…"

# Closing brackets trimmed only when unbalanced within the match, so the
# trailing ')' of "Python_(programming_language)" survives while the ')'
# wrapped around a URL by prose "(see https://x.com)" does not.
_TRAIL_PAIRS = ((")", "("), ("]", "["), ("}", "{"), ("）", "（"))


class ContactEntityExtractor(DocProcessor):
    """Lift contact entities (emails, URLs, phone numbers) into metadata.

    A large share of ingested business documents — supplier notices, CRM
    notes, due-diligence folders, support threads — carry their most
    queryable facts as contact entities rather than prose: who to email,
    which portal to open, which number to call. Downstream stages want
    those facts as structured data, for routing documents to an owner's
    mailbox domain, filtering recall results by company site, or counting
    contact points per supplier, yet none of that is possible while the
    entities stay buried in free text. This processor scans every document
    with high-precision regular expressions for the three universal
    contact kinds — ``email``, ``url`` and ``phone`` — and stamps the
    findings into document metadata, leaving the text itself untouched.

    Extraction is shape-based, deterministic and offline:

    1. each enabled entity kind is matched with a purpose-built pattern
       (see ``ENTITY_PATTERNS``): emails need a letter TLD, URLs need a
       scheme or a ``www.`` host, phones need either a mainland-China
       mobile shape, separator-structured North-American digits, or a
       leading-plus international form. Precision is preferred over
       recall: a bare 10-digit run, an IPv4 address or a bare ``@domain``
       mention is deliberately not an entity;
    2. raw matches are trimmed of sentence punctuation that regexes drag
    along (``Visit https://example.com.`` yields the bare URL); closing
       brackets are trimmed only when unbalanced inside the match, so the
       final ')' of a Wikipedia-style path is kept while the ')' of
       prose-wrapped ``(see https://example.com)`` is not. Full-width CJK
       punctuation is handled too, since Chinese sentences end without
       spaces;
    3. values are optionally deduplicated — case-insensitively for
       emails and URLs, digit-wise for phones, so ``(555) 123-4567`` and
       ``555-123-4567`` count as one contact — keeping the first
       spelling and first-occurrence order;
    4. each list is capped at ``max_per_type`` (0 = unlimited).

    Results land in metadata: ``metadata[entities_key]`` maps every
    enabled kind to its (possibly empty) list, and
    ``metadata[counts_key]`` maps each kind to its list length — the
    counts of extracted entities after dedupe and capping. Empty lists
    are stamped on purpose: a caller can distinguish "extraction ran and
    found nothing" from "extraction never ran". Metadata mappings are
    copied before mutation, text / id / other metadata fields are never
    modified, and every document survives processing — extraction adds
    structure, it does not filter.

    The component is the constructive counterpart of
    ``SensitiveDataRedactor``: that processor destroys contact-shaped PII
    in recalled text for privacy, while this one preserves the text and
    lifts the same shapes into metadata at pre-processing time for
    routing and aggregation. Pure Python, no dependencies, byte-stable
    output for a given input.

    Attributes:
        entity_types: Kinds to extract, a non-empty subset of
            ``('email', 'url', 'phone')``; order defines the stamped
            mapping's key order.
        entities_key: Metadata key the {kind: [values]} mapping is
            written to; an empty value disables stamping.
        counts_key: Metadata key the {kind: count} mapping is written
            to; an empty value disables stamping.
        dedupe: When true (default), repeated contacts collapse to their
            first spelling (case-insensitive for email/url, digit-wise
            for phone); when false, every occurrence is kept in order.
        max_per_type: Maximum values kept per kind after dedupe; 0
            (default) means unlimited.
    """

    entity_types: List[str] = list(SUPPORTED_ENTITY_TYPES)
    entities_key: str = "entities"
    counts_key: str = "entity_counts"
    dedupe: bool = True
    max_per_type: int = 0

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp contact entities of each document into its metadata.

        Args:
            origin_docs: Documents to inspect, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order, each
            stamped with the entities found in its text.
        """
        for doc in origin_docs:
            found: Dict[str, List[str]] = {}
            for entity_type in self.entity_types:
                found[entity_type] = self._extract(doc.text or "",
                                                   entity_type)
            if self.entities_key:
                self._stamp(doc, self.entities_key, found)
            if self.counts_key:
                self._stamp(doc, self.counts_key,
                            {kind: len(values)
                             for kind, values in found.items()})
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction helpers
    # ------------------------------------------------------------------ #

    def _extract(self, text: str, entity_type: str) -> List[str]:
        """Extract one entity kind from a text, in first-occurrence order.

        Args:
            text: Document text (empty string for None).
            entity_type: One of SUPPORTED_ENTITY_TYPES.

        Returns:
            List[str]: Trimmed values, deduplicated when ``dedupe`` and
            capped at ``max_per_type``.
        """
        values: List[str] = []
        seen = set()
        for match in ENTITY_PATTERNS[entity_type].finditer(text):
            value = self._trim(match.group(0))
            if not value:
                continue
            if self.dedupe:
                identity = self._identity(value, entity_type)
                if identity in seen:
                    continue
                seen.add(identity)
            values.append(value)
            if self.max_per_type and len(values) >= self.max_per_type:
                break
        return values

    @staticmethod
    def _trim(value: str) -> str:
        """Strip sentence punctuation dragged along by a raw match.

        Trailing commas, periods and friends are removed; a closing
        bracket survives unless it is unbalanced within the match itself.

        Args:
            value: Raw regex match.

        Returns:
            str: Cleaned value; may be empty if the match was pure
            punctuation.
        """
        changed = True
        while changed:
            changed = False
            if value and value[-1] in _TRAIL_PUNCT:
                value = value[:-1]
                changed = True
                continue
            for close, opener in _TRAIL_PAIRS:
                if value.endswith(close) and \
                        value.count(close) > value.count(opener):
                    value = value[:-1]
                    changed = True
                    break
        return value

    @staticmethod
    def _identity(value: str, entity_type: str) -> str:
        """Normalize a value for duplicate comparison.

        Emails and URLs are case-insensitive, so comparison uses the
        case-folded string while the original spelling is what gets
        kept. Phones compare by digits only, so separator and bracket
        variants of one number collapse together.

        Args:
            value: Trimmed entity value.
            entity_type: One of SUPPORTED_ENTITY_TYPES.

        Returns:
            str: Comparison key.
        """
        if entity_type == "phone":
            return re.sub(r"\D", "", value)
        return value.casefold()

    def _stamp(self, doc: Document, key: str, value) -> None:
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
            -> 'ContactEntityExtractor':
        """Initialize and validate the extractor from component configuration.

        Validation happens eagerly at load time: a typo'd entity kind or
        a negative cap that silently produced wrong metadata would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ContactEntityExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "entity_types") and \
                doc_processor_configer.entity_types is not None:
            entity_types = doc_processor_configer.entity_types
            if not isinstance(entity_types, (list, tuple)) or \
                    not all(isinstance(item, str)
                            for item in entity_types):
                raise ValueError(
                    "entity_types must be a list of strings")
            unknown = [item for item in entity_types
                       if item not in SUPPORTED_ENTITY_TYPES]
            if unknown:
                raise ValueError(
                    f"unknown entity types {unknown}; supported: "
                    f"{list(SUPPORTED_ENTITY_TYPES)}")
            if not entity_types:
                raise ValueError(
                    "entity_types must not be empty; supported: "
                    f"{list(SUPPORTED_ENTITY_TYPES)}")
            self.entity_types = list(entity_types)

        if hasattr(doc_processor_configer, "entities_key") and \
                doc_processor_configer.entities_key is not None:
            key = doc_processor_configer.entities_key
            if not isinstance(key, str):
                raise ValueError("entities_key must be a string")
            self.entities_key = key

        if hasattr(doc_processor_configer, "counts_key") and \
                doc_processor_configer.counts_key is not None:
            key = doc_processor_configer.counts_key
            if not isinstance(key, str):
                raise ValueError("counts_key must be a string")
            self.counts_key = key

        if hasattr(doc_processor_configer, "dedupe") and \
                doc_processor_configer.dedupe is not None:
            self.dedupe = bool(doc_processor_configer.dedupe)

        if hasattr(doc_processor_configer, "max_per_type") and \
                doc_processor_configer.max_per_type is not None:
            cap = doc_processor_configer.max_per_type
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_per_type must be an integer")
            self.max_per_type = cap
            if self.max_per_type < 0:
                raise ValueError("max_per_type must be >= 0")

        return self
