# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Deterministic metadata filtering for recalled documents."""

from numbers import Number
from typing import Any, Dict, List, Literal

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class MetadataFilter(DocProcessor):
    """Filter documents using explicit metadata conditions.

    Each condition has ``field``, ``operator``, and optional ``value`` keys.
    Supported operators are ``eq``, ``ne``, ``in``, ``not_in``, ``contains``,
    ``exists``, ``gt``, ``gte``, ``lt``, and ``lte``.
    """

    conditions: List[Dict[str, Any]] = []
    match_mode: Literal["all", "any"] = "all"
    missing: Literal["exclude", "include"] = "exclude"

    _OPERATORS = {
        "eq", "ne", "in", "not_in", "contains", "exists",
        "gt", "gte", "lt", "lte",
    }

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        if not origin_docs or not self.conditions:
            return origin_docs
        if self.match_mode not in {"all", "any"}:
            raise ValueError("match_mode must be either 'all' or 'any'")
        if self.missing not in {"exclude", "include"}:
            raise ValueError("missing must be either 'exclude' or 'include'")

        for condition in self.conditions:
            self._validate_condition(condition)

        matched = [
            document for document in origin_docs
            if self._matches_document(document)
        ]
        return matched

    def _matches_document(self, document: Document) -> bool:
        results = [self._matches_condition(document, condition)
                   for condition in self.conditions]
        return all(results) if self.match_mode == "all" else any(results)

    def _matches_condition(self, document: Document,
                           condition: Dict[str, Any]) -> bool:
        field = condition["field"]
        operator = condition.get("operator", "eq")
        metadata = document.metadata or {}

        if operator == "exists":
            return (field in metadata) == bool(condition.get("value", True))

        if field not in metadata:
            return self.missing == "include"

        actual = metadata[field]
        expected = condition.get("value")
        if operator == "eq":
            return actual == expected
        if operator == "ne":
            return actual != expected
        if operator == "in":
            return actual in self._require_collection(expected, operator)
        if operator == "not_in":
            return actual not in self._require_collection(expected, operator)
        if operator == "contains":
            return expected in actual
        if operator in {"gt", "gte", "lt", "lte"}:
            if not isinstance(actual, Number) or not isinstance(expected, Number):
                return False
            return {
                "gt": actual > expected,
                "gte": actual >= expected,
                "lt": actual < expected,
                "lte": actual <= expected,
            }[operator]
        raise ValueError(f"Unsupported metadata filter operator: {operator}")

    @staticmethod
    def _require_collection(value: Any, operator: str) -> Any:
        if isinstance(value, (str, bytes)) or not hasattr(value, "__contains__"):
            raise TypeError(f"metadata filter operator '{operator}' requires a collection")
        return value

    def _validate_condition(self, condition: Dict[str, Any]) -> None:
        if not isinstance(condition, dict):
            raise TypeError("metadata filter conditions must be dictionaries")
        field = condition.get("field")
        operator = condition.get("operator", "eq")
        if not isinstance(field, str) or not field:
            raise ValueError("metadata filter condition requires a non-empty field")
        if operator not in self._OPERATORS:
            raise ValueError(f"Unsupported metadata filter operator: {operator}")
        if operator != "exists" and "value" not in condition:
            raise ValueError(
                f"metadata filter condition for '{field}' requires a value"
            )
