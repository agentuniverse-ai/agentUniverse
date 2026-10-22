# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: regex_filter.py

import re
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class RegexFilter(DocProcessor):
    """Keep or drop documents whose text matches a set of regular expressions.

    Real corpora contain many documents that are best identified by their
    lexical surface — error codes, invoice or contract numbers, boilerplate
    disclaimers, legal notices, log lines. This processor filters the batch
    with user-supplied Python regular expressions: each document's text is
    tested with ``re.search`` against every configured pattern, and the
    document counts as *matching* when at least one pattern is found
    anywhere in the text (``require_all`` tightens this to every pattern).
    The batch is then reduced according to ``mode``: matching documents are
    kept under ``keep_matching`` (default) or removed under
    ``drop_matching``.

    The scope is deliberately lexical. The component has no notion of
    language, meaning or similarity — it answers exactly one question,
    "does this text contain a pattern I recognize?", which makes it the
    dependency-free complement to ``ThresholdFilter`` (numeric predicates
    on score, length, top-k or percentile — none of which can express
    lexical structure) and to ``SensitiveDataRedactor`` (which rewrites
    matched spans in place but never removes a document). The whole
    pipeline is pure Python's ``re`` module: deterministic, offline and
    without third-party dependencies.

    Semantics worth knowing:

    - ``re.search`` is used, so a pattern matches when found anywhere in
      the text; anchors such as ``^`` and ``$`` remain available and
      multiline patterns work as usual;
    - ``case_sensitive`` defaults to ``True``, preserving standard Python
      regex semantics; setting it to ``False`` compiles every pattern with
      ``re.IGNORECASE`` (which, as in ``re`` itself, also lets character
      ranges like ``[A-Z]`` match lowercase letters);
    - an empty ``patterns`` list is a no-op — no constraint applies, every
      document is kept and nothing is stamped;
    - a ``None`` text is treated as the empty string, which can still match
      patterns such as ``^$``.

    Bookkeeping lands in document metadata: the list of patterns that
    matched (in configuration order) is written to
    ``metadata[matched_key]`` on **every** processed document, kept and
    removed alike, so callers holding the original list can see exactly why
    each document survived or vanished. Metadata mappings are copied before
    mutation, and text / id / other metadata fields are never modified.

    Configuration is validated eagerly at load time: a non-list
    ``patterns`` value, non-string or empty-string entries, an
    uncompilable regular expression, an unknown ``mode`` or a non-string
    ``matched_key`` all raise ``ValueError`` during component
    initialization — a typo fails the pipeline at startup instead of
    silently passing every document through. Patterns assigned directly as
    attributes (bypassing the configer) are compiled at processing time,
    where an invalid pattern surfaces as ``re.error``.

    Attributes:
        patterns: Regular expressions to test each document with. A
            document matches when ANY pattern is found (``re.search``), or
            ALL of them under ``require_all``. An empty list keeps every
            document untouched.
        mode: ``keep_matching`` (default) keeps documents that match;
            ``drop_matching`` removes them.
        require_all: When false (default) any single matching pattern
            counts; when true every pattern must match.
        case_sensitive: When true (default) patterns use standard Python
            regex semantics; when false they are compiled with
            ``re.IGNORECASE``.
        matched_key: Metadata key the list of matched patterns is written
            to on every processed document; an empty value disables
            stamping.
    """

    patterns: List[str] = []
    mode: str = "keep_matching"
    require_all: bool = False
    case_sensitive: bool = True
    matched_key: str = "regex_matched"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Keep or drop documents according to the configured patterns.

        Args:
            origin_docs: Documents to filter, in batch order.
            query: Query object (unused; matching depends only on the
                documents' own text).

        Returns:
            List[Document]: Documents surviving the filter, in their
            original relative order, each stamped with the list of
            patterns it matched.
        """
        if not origin_docs:
            return []

        compiled = self._compile_patterns()
        if not compiled:
            # No pattern configured: no constraint applies. Documents are
            # returned untouched and nothing is stamped — the same contract
            # an empty allow-list gives in the other filters.
            return list(origin_docs)

        kept: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            matched = [pattern for pattern, regex in zip(self.patterns,
                                                         compiled)
                       if regex.search(text) is not None]
            if self.require_all:
                is_match = len(matched) == len(compiled)
            else:
                is_match = bool(matched)

            if self.matched_key:
                self._stamp(doc, self.matched_key, matched)

            if self.mode == "drop_matching":
                if not is_match:
                    kept.append(doc)
            elif is_match:
                kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Pattern helpers
    # ------------------------------------------------------------------ #

    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile every configured pattern under the case flag.

        Patterns arrive pre-validated when loaded through the component
        configer; re-compiling here stays cheap because Python's ``re``
        module caches compiled patterns internally, and it keeps patterns
        assigned directly as attributes working as well.

        Args:
            None

        Returns:
            List[re.Pattern]: Compiled patterns, in configuration order;
            an empty list when no pattern is configured.

        Raises:
            re.error: If a directly-assigned pattern fails to compile.
        """
        flags = 0 if self.case_sensitive else re.IGNORECASE
        return [re.compile(pattern, flags) for pattern in self.patterns]

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
            -> 'RegexFilter':
        """Initialize and validate the filter from component configuration.

        Validation happens eagerly at load time: a filter that silently
        kept (or dropped) every document because of a typoed pattern would
        be far harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            RegexFilter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "patterns") and \
                doc_processor_configer.patterns is not None:
            patterns = doc_processor_configer.patterns
            if not isinstance(patterns, (list, tuple)):
                raise ValueError("patterns must be a list of strings")
            for index, pattern in enumerate(patterns):
                if not isinstance(pattern, str):
                    raise ValueError(
                        f"patterns[{index}] must be a string, got "
                        f"{type(pattern).__name__}")
                if not pattern:
                    raise ValueError(
                        f"patterns[{index}] must be a non-empty string — an "
                        "empty pattern would match every document")
                try:
                    re.compile(pattern)
                except re.error as exc:
                    raise ValueError(
                        f"patterns[{index}] is not a valid regular "
                        f"expression: {pattern!r} ({exc})")
            self.patterns = list(patterns)

        if hasattr(doc_processor_configer, "mode") and \
                doc_processor_configer.mode is not None:
            self.mode = doc_processor_configer.mode
            if self.mode not in ("keep_matching", "drop_matching"):
                raise ValueError(
                    "mode must be 'keep_matching' or 'drop_matching', got "
                    f"'{self.mode}'")

        if hasattr(doc_processor_configer, "require_all") and \
                doc_processor_configer.require_all is not None:
            self.require_all = bool(doc_processor_configer.require_all)

        if hasattr(doc_processor_configer, "case_sensitive") and \
                doc_processor_configer.case_sensitive is not None:
            self.case_sensitive = bool(doc_processor_configer.case_sensitive)

        if hasattr(doc_processor_configer, "matched_key") and \
                doc_processor_configer.matched_key is not None:
            key = doc_processor_configer.matched_key
            if not isinstance(key, str):
                raise ValueError("matched_key must be a string")
            self.matched_key = key

        return self
