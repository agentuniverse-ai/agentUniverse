# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: checklist_completeness_analyzer.py

import re
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# One checklist item per physical line: optional indentation, an optional
# list marker (bullet or ordered), then a checkbox whose bracket holds
# exactly one state character. The match is anchored at line start, so a
# backslash-escaped "\[x]" never qualifies (the backslash sits where the
# "[" is expected) and a checkbox in mid-sentence is ignored.
_CHECKBOX_LINE_RE = re.compile(
    r"^(?P<indent>[ \t]*)"
    r"(?:(?P<marker>[-*+]|\d+[.)])[ \t]+)?"
    r"\[(?P<state>[ xX])][ \t]*"
    r"(?P<label>.*)$"
)

# Fenced code blocks: a line whose first non-space characters are three
# backticks or three tildes toggles fence state. Checkboxes inside a fence
# are sample text, not tasks, and are not counted.
_FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")

_RATIO_DIGITS = 4


class ChecklistCompletenessAnalyzer(DocProcessor):
    """Measure how complete the checklists inside each document are.

        Knowledge corpora and ops runbooks are full of task lists:
        onboarding guides, release checklists, incident review action
        items. The dangerous ones are the half-finished ones — a runbook
        whose "verify backups" box is still open is misinformation once it
        is indexed. This processor scans every document for checkbox-style
        list items, computes the completion ratio and stamps the analysis
        into ``metadata[checklist]``:

        * ``total`` / ``checked`` / ``unchecked`` — item counts;
        * ``ratio`` — ``checked / total`` rounded to 4 decimals, or None
          when the document contains no checklist (no fabricated score);
        * ``missing_items`` — labels of the unchecked items in document
          order, capped at ``max_items_reported`` with a
          ``missing_truncated`` flag when the list was cut short;
        * ``empty_labels`` — checkboxes without any label text, a common
          authoring mistake worth surfacing on its own.

        The detection rules are deliberately conservative and
        dependency-free:

        * an item is a line that starts (after optional indentation) with
          an optional list marker (``-``, ``*``, ``+``, ``1.`` or ``1)``)
          followed by a checkbox ``[ ]`` (unchecked) or ``[x]`` / ``[X]``
          (checked); a bare checkbox at line start counts too;
        * bracket contents other than a single space, ``x`` or ``X``
          (``[o]``, ``[maybe]``, ``[]``) are ordinary text, as are
          checkboxes in mid-sentence, escaped ones (``\\[x]``) and every
          line inside a fenced code block (``` ``` ``` or ``~~~``, an
          unclosed fence runs to the end of the text);
        * labels are right-stripped; an empty label is counted in
          ``empty_labels`` but never listed in ``missing_items``.

        By default the processor only stamps metadata. Setting
        ``min_ratio`` and/or ``max_ratio`` switches on a filter mode that
        drops documents whose ratio falls outside the inclusive range —
        documents without a computable ratio (no checkboxes found) are
        always kept, since no evidence exists to reject them.

        This component is about *list completeness*, which makes it
        complementary to structural processors such as
        ``ListStructureExtractor``: it does not re-shape lists, it scores
        how much of them is done, and the metrics travel with the document
        into the store.

        Everything is pure Python, deterministic and offline: identical
        inputs always produce identical metadata, with no model calls and
        no randomness.

        Attributes:
            min_ratio: Optional minimum completion ratio (0..1) for the
                filter mode; None (default) disables the lower bound.
            max_ratio: Optional maximum completion ratio (0..1) for the
                filter mode; None (default) disables the upper bound.
            checklist_key: Metadata key the analysis dictionary is
                written to; an empty value disables stamping.
            note_key: Metadata key the "no checkboxes found" note is
                written to; an empty value disables the note.
            max_items_reported: Maximum number of unchecked labels kept
                in ``missing_items``; 0 keeps none.
        """

    min_ratio: Optional[float] = None
    max_ratio: Optional[float] = None
    checklist_key: str = "checklist"
    note_key: str = "checklist_note"
    max_items_reported: int = 25

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp checklist analysis into every document, then filter.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; completeness depends only on the
                documents' own text).

        Returns:
            List[Document]: All documents when no ratio bounds are set;
            otherwise the documents whose completion ratio lies within
            [min_ratio, max_ratio], plus every document without a
            computable ratio. Order is preserved.
        """
        kept: List[Document] = []
        for doc in origin_docs:
            report = self._analyze(doc.text or "")
            if self.checklist_key:
                self._stamp(doc, self.checklist_key, report)
            if self.note_key and report["total"] == 0:
                self._stamp(doc, self.note_key, "no checkboxes found")
            ratio = report["ratio"]
            if (ratio is not None and self.min_ratio is not None
                    and ratio < self.min_ratio) or (
                    ratio is not None and self.max_ratio is not None
                    and ratio > self.max_ratio):
                continue
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Analysis helpers
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> dict:
        """Compute the full analysis dictionary for one text.

        Args:
            text: Document text (None/empty treated as blank).

        Returns:
            dict: ``total`` / ``checked`` / ``unchecked`` / ``empty_labels``
            integers, ``ratio`` (float rounded to 4 decimals, or None when
            no checkbox was found), ``missing_items`` (labels of unchecked
            items, capped) and ``missing_truncated`` (whether unchecked
            labels were omitted because of the cap).
        """
        total = checked = empty_labels = 0
        missing: List[str] = []
        missing_candidates = 0
        in_fence = False
        for line in (text or "").splitlines():
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = _CHECKBOX_LINE_RE.match(line)
            if not match:
                continue
            total += 1
            label = match.group("label").rstrip()
            if match.group("state") in ("x", "X"):
                checked += 1
            else:
                if not label:
                    empty_labels += 1
                else:
                    missing_candidates += 1
                    if len(missing) < self.max_items_reported:
                        missing.append(label)
        return {
            "total": total,
            "checked": checked,
            "unchecked": total - checked,
            "ratio": (round(checked / total, _RATIO_DIGITS)
                      if total else None),
            "missing_items": missing,
            "missing_truncated": len(missing) < missing_candidates,
            "empty_labels": empty_labels,
        }

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

    @staticmethod
    def _configured_value(doc_processor_configer: ComponentConfiger,
                          attr: str):
        """Read one optional attribute from the configuration.

        Args:
            doc_processor_configer: Configuration object.
            attr: Attribute name.

        Returns:
            The configured value, or None when the key is absent or null.
        """
        return getattr(doc_processor_configer, attr, None) \
            if hasattr(doc_processor_configer, attr) else None

    def _init_ratio_bounds(self, doc_processor_configer: ComponentConfiger) \
            -> None:
        """Load and validate the optional filter-mode ratio bounds.

        Args:
            doc_processor_configer: Configuration object.

        Raises:
            ValueError: On a non-number, out-of-range bound or an empty
                ratio range.
        """
        for attr in ("min_ratio", "max_ratio"):
            value = self._configured_value(doc_processor_configer, attr)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{attr} must be a number between 0 and 1")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{attr} must be between 0 and 1, got {value}")
            setattr(self, attr, float(value))

        if self.min_ratio is not None and self.max_ratio is not None and \
                self.min_ratio > self.max_ratio:
            raise ValueError(
                f"min_ratio ({self.min_ratio}) must not exceed max_ratio "
                f"({self.max_ratio})")

    def _init_string_keys(self, doc_processor_configer: ComponentConfiger) \
            -> None:
        """Load and validate the optional metadata key names.

        Args:
            doc_processor_configer: Configuration object.

        Raises:
            ValueError: On a non-string key name.
        """
        for attr in ("checklist_key", "note_key"):
            value = self._configured_value(doc_processor_configer, attr)
            if value is None:
                continue
            if not isinstance(value, str):
                raise ValueError(f"{attr} must be a string")
            setattr(self, attr, value)

    def _init_max_items_reported(
            self, doc_processor_configer: ComponentConfiger) -> None:
        """Load and validate the optional missing-items cap.

        Args:
            doc_processor_configer: Configuration object.

        Raises:
            ValueError: On a negative or non-integer cap.
        """
        value = self._configured_value(doc_processor_configer,
                                       "max_items_reported")
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("max_items_reported must be an integer")
        if value < 0:
            raise ValueError(f"max_items_reported must be >= 0, got {value}")
        self.max_items_reported = value

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'ChecklistCompletenessAnalyzer':
        """Initialize and validate the analyzer from component configuration.

        Validation happens eagerly at load time: a typo like
        ``min_ratio: 'high'`` must fail at startup, not silently disable
        the filter for a whole ingestion run.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ChecklistCompletenessAnalyzer: The initialized instance.

        Raises:
            ValueError: On invalid parameter values or an empty ratio range.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        self._init_ratio_bounds(doc_processor_configer)
        self._init_string_keys(doc_processor_configer)
        self._init_max_items_reported(doc_processor_configer)
        return self
