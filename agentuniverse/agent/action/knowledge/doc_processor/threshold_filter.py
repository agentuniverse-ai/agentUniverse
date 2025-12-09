# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/09
# @Author  : kaichuan
# @FileName: threshold_filter.py

import math
from typing import List, Dict, Any, Optional, Literal

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ThresholdFilter(DocProcessor):
    """Multi-mode document filter supporting score, length, top-k, and percentile filtering.

    This processor provides flexible document filtering capabilities with support for:
    - Score threshold filtering (min/max relevance scores)
    - Document length filtering (min/max text length)
    - Top-K filtering (keep top K documents by score)
    - Percentile filtering (keep top X% documents by score)
    - AND/OR logic combination for multiple filters

    Attributes:
        filters: List of filter configurations, each specifying a filter type and parameters.
        logic_operator: Logic operator for combining multiple filters ('AND' or 'OR').
        score_field: Metadata field name containing relevance scores.
        default_score: Default score for documents without score metadata.
        preserve_order: Whether to maintain original document order in results.

    Example:
        ```yaml
        filters:
          - type: 'score'
            min_score: 0.7
          - type: 'length'
            min_length: 100
        logic_operator: 'AND'
        ```
    """

    filters: List[Dict[str, Any]] = []
    logic_operator: Literal["AND", "OR"] = "AND"
    score_field: str = "relevance_score"
    default_score: float = 0.0
    preserve_order: bool = True

    # Filter type to handler method mapping
    _FILTER_HANDLERS = {
        "score": "_apply_score_filter",
        "length": "_apply_length_filter",
        "topk": "_apply_topk_filter",
        "percentile": "_apply_percentile_filter"
    }

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Apply configured filters to documents.

        Processing pipeline:
        1. Validate input (return [] if empty, return all if no filters)
        2. Apply each filter independently to create result sets
        3. Combine result sets using logic operator
        4. Optionally restore original order
        5. Return filtered documents

        Args:
            origin_docs: List of documents to be filtered.
            query: Query object (currently unused, but required by interface).

        Returns:
            List[Document]: Filtered documents based on configured criteria.
        """
        # Handle empty input
        if not origin_docs:
            return []

        # Handle no filters configured - pass through all documents
        if not self.filters:
            return origin_docs

        # Apply each filter independently
        filter_results = []
        for filter_config in self.filters:
            filter_type = filter_config.get("type")
            if filter_type not in self._FILTER_HANDLERS:
                raise ValueError(f"Invalid filter type: {filter_type}")

            handler_name = self._FILTER_HANDLERS[filter_type]
            handler = getattr(self, handler_name)
            filtered = handler(origin_docs, filter_config)
            filter_results.append(filtered)

        # Combine results using logic operator
        combined = self._combine_results(filter_results, self.logic_operator)

        # Preserve original order if configured
        if self.preserve_order:
            combined = self._restore_order(combined, origin_docs)

        return combined

    def _apply_score_filter(self, docs: List[Document], config: Dict[str, Any]) -> List[Document]:
        """Filter documents by score range.

        Filters documents based on min_score and/or max_score thresholds.
        Documents without scores use default_score.

        Args:
            docs: Documents to filter.
            config: Filter configuration with 'min_score' and/or 'max_score'.

        Returns:
            List[Document]: Documents within the specified score range.
        """
        min_score = config.get("min_score", float("-inf"))
        max_score = config.get("max_score", float("inf"))

        filtered = []
        for doc in docs:
            score = self._get_score(doc)
            if min_score <= score <= max_score:
                filtered.append(doc)

        return filtered

    def _apply_length_filter(self, docs: List[Document], config: Dict[str, Any]) -> List[Document]:
        """Filter documents by text length.

        Filters documents based on min_length and/or max_length thresholds.
        Documents with None or empty text are treated as length 0.

        Args:
            docs: Documents to filter.
            config: Filter configuration with 'min_length' and/or 'max_length'.

        Returns:
            List[Document]: Documents within the specified length range.
        """
        min_length = config.get("min_length", 0)
        max_length = config.get("max_length", float("inf"))

        filtered = []
        for doc in docs:
            length = len(doc.text) if doc.text else 0
            if min_length <= length <= max_length:
                filtered.append(doc)

        return filtered

    def _apply_topk_filter(self, docs: List[Document], config: Dict[str, Any]) -> List[Document]:
        """Keep top K documents by score.

        Sorts documents by score in descending order and returns top K.
        If k > len(docs), returns all documents.

        Args:
            docs: Documents to filter.
            config: Filter configuration with 'k' parameter.

        Returns:
            List[Document]: Top K documents by score.
        """
        k = config.get("k", len(docs))

        # Score each document
        scored_docs = [(doc, self._get_score(doc)) for doc in docs]

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return top K
        return [doc for doc, score in scored_docs[:k]]

    def _apply_percentile_filter(self, docs: List[Document], config: Dict[str, Any]) -> List[Document]:
        """Keep top X% documents by score.

        Calculates cutoff count as ceil(len(docs) * percentile), sorts by score,
        and returns top documents. Percentile is clamped to [0.0, 1.0].

        Args:
            docs: Documents to filter.
            config: Filter configuration with 'percentile' parameter (0.0-1.0).

        Returns:
            List[Document]: Top percentile documents by score.
        """
        percentile = config.get("percentile", 1.0)
        # Clamp percentile to valid range [0.0, 1.0]
        percentile = max(0.0, min(1.0, percentile))

        cutoff_count = math.ceil(len(docs) * percentile)

        # Score each document
        scored_docs = [(doc, self._get_score(doc)) for doc in docs]

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return top percentile
        return [doc for doc, score in scored_docs[:cutoff_count]]

    def _get_score(self, doc: Document) -> float:
        """Extract score from document metadata.

        Attempts to retrieve score from metadata[score_field].
        Returns default_score if metadata is missing or score field not found.

        Args:
            doc: Document to extract score from.

        Returns:
            float: Document score or default_score if not found.
        """
        if not doc.metadata:
            return self.default_score

        return doc.metadata.get(self.score_field, self.default_score)

    def _combine_results(self, results: List[List[Document]], logic: str) -> List[Document]:
        """Combine filter results using AND/OR logic.

        AND logic: Returns intersection - documents present in ALL result sets.
        OR logic: Returns union - documents present in ANY result set.

        Args:
            results: List of filtered document lists from each filter.
            logic: Logic operator ('AND' or 'OR').

        Returns:
            List[Document]: Combined result set based on logic operator.
        """
        if not results:
            return []

        if len(results) == 1:
            return results[0]

        if logic == "AND":
            # Intersection: documents present in ALL result sets
            # Use document ID for comparison
            result_set = set(id(doc) for doc in results[0])
            for result in results[1:]:
                result_set &= set(id(doc) for doc in result)

            # Reconstruct documents preserving metadata
            # Build map from all results to ensure we get the document objects
            doc_map = {id(doc): doc for result in results for doc in result}
            return [doc_map[doc_id] for doc_id in result_set if doc_id in doc_map]

        else:  # OR
            # Union: documents present in ANY result set
            seen = set()
            combined = []
            for result in results:
                for doc in result:
                    doc_id = id(doc)
                    if doc_id not in seen:
                        seen.add(doc_id)
                        combined.append(doc)
            return combined

    def _restore_order(self, filtered_docs: List[Document], original_docs: List[Document]) -> List[Document]:
        """Restore original document order.

        Iterates through original documents in order and includes those
        present in the filtered set.

        Args:
            filtered_docs: Documents after filtering.
            original_docs: Original document list with desired order.

        Returns:
            List[Document]: Filtered documents in original order.
        """
        filtered_ids = set(id(doc) for doc in filtered_docs)
        return [doc for doc in original_docs if id(doc) in filtered_ids]

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> 'ThresholdFilter':
        """Initialize filter parameters from component configuration.

        Validates configuration including filter types and logic operator.

        Args:
            doc_processor_configer: Configuration object containing filter parameters.

        Returns:
            ThresholdFilter: The initialized filter instance.

        Raises:
            ValueError: If configuration is invalid (bad filter type or logic operator).
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        # Initialize filters
        if hasattr(doc_processor_configer, "filters"):
            self.filters = doc_processor_configer.filters

            # Validate filter types
            if not isinstance(self.filters, list):
                raise ValueError("filters must be a list")

            valid_types = {"score", "length", "topk", "percentile"}
            for i, filter_config in enumerate(self.filters):
                filter_type = filter_config.get("type")
                if filter_type not in valid_types:
                    raise ValueError(f"Invalid filter type at index {i}: {filter_type}. "
                                   f"Valid types are: {', '.join(valid_types)}")

        # Initialize logic operator
        if hasattr(doc_processor_configer, "logic_operator"):
            self.logic_operator = doc_processor_configer.logic_operator

            # Validate logic operator
            if self.logic_operator not in {"AND", "OR"}:
                raise ValueError(f"Invalid logic_operator: {self.logic_operator}. "
                               f"Must be 'AND' or 'OR'")

        # Initialize score field
        if hasattr(doc_processor_configer, "score_field"):
            self.score_field = doc_processor_configer.score_field

        # Initialize default score
        if hasattr(doc_processor_configer, "default_score"):
            self.default_score = doc_processor_configer.default_score

        # Initialize preserve order
        if hasattr(doc_processor_configer, "preserve_order"):
            self.preserve_order = doc_processor_configer.preserve_order

        return self
