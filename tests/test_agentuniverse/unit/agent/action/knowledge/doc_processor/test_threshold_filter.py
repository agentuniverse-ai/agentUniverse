# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/09
# @Author  : kaichuan
# @FileName: test_threshold_filter.py

import unittest
from unittest.mock import Mock

from agentuniverse.agent.action.knowledge.doc_processor.threshold_filter import ThresholdFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestThresholdFilter(unittest.TestCase):
    """Comprehensive test suite for ThresholdFilter."""

    def setUp(self):
        """Create test fixtures."""
        self.filter = ThresholdFilter()
        self.sample_docs = self._create_sample_docs()

    def _create_sample_docs(self):
        """Create sample documents with varying scores and lengths."""
        return [
            Document(text="A" * 10, metadata={"relevance_score": 0.2}),
            Document(text="B" * 50, metadata={"relevance_score": 0.4}),
            Document(text="C" * 100, metadata={"relevance_score": 0.6}),
            Document(text="D" * 500, metadata={"relevance_score": 0.8}),
            Document(text="E" * 1000, metadata={"relevance_score": 1.0}),
        ]

    def _create_configer(self, config_dict):
        """Create mock ComponentConfiger from dictionary."""
        cfg = Configer()
        cfg.value = config_dict

        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        # Ensure required attributes exist
        if not hasattr(configer, 'name'):
            configer.name = config_dict.get('name', 'test_filter')
        if not hasattr(configer, 'description'):
            configer.description = config_dict.get('description', 'Test filter description')

        return configer

    # ========== Initialization Tests ==========

    def test_initialization_default_config(self):
        """Test initialization with default configuration."""
        filter_obj = ThresholdFilter()

        self.assertEqual(filter_obj.filters, [])
        self.assertEqual(filter_obj.logic_operator, "AND")
        self.assertEqual(filter_obj.score_field, "relevance_score")
        self.assertEqual(filter_obj.default_score, 0.0)
        self.assertTrue(filter_obj.preserve_order)

    def test_initialization_custom_config(self):
        """Test initialization with custom YAML configuration."""
        config = {
            'name': 'test_threshold_filter',
            'description': 'Test filter',
            'filters': [
                {'type': 'score', 'min_score': 0.5}
            ],
            'logic_operator': 'OR',
            'score_field': 'custom_score',
            'default_score': 0.1,
            'preserve_order': False
        }

        configer = self._create_configer(config)
        filter_obj = ThresholdFilter()
        filter_obj._initialize_by_component_configer(configer)

        self.assertEqual(len(filter_obj.filters), 1)
        self.assertEqual(filter_obj.logic_operator, 'OR')
        self.assertEqual(filter_obj.score_field, 'custom_score')
        self.assertEqual(filter_obj.default_score, 0.1)
        self.assertFalse(filter_obj.preserve_order)

    def test_initialization_invalid_filter_type(self):
        """Test that invalid filter type raises ValueError."""
        config = {
            'name': 'test_threshold_filter',
            'filters': [
                {'type': 'invalid_type'}
            ]
        }

        configer = self._create_configer(config)
        filter_obj = ThresholdFilter()

        with self.assertRaises(ValueError) as context:
            filter_obj._initialize_by_component_configer(configer)

        self.assertIn('Invalid filter type', str(context.exception))

    def test_initialization_invalid_logic_operator(self):
        """Test that invalid logic operator raises ValueError."""
        config = {
            'name': 'test_threshold_filter',
            'logic_operator': 'XOR'
        }

        configer = self._create_configer(config)
        filter_obj = ThresholdFilter()

        with self.assertRaises(ValueError) as context:
            filter_obj._initialize_by_component_configer(configer)

        self.assertIn('Invalid logic_operator', str(context.exception))

    # ========== Score Filter Tests ==========

    def test_score_filter_min_threshold(self):
        """Test filtering with minimum score threshold."""
        self.filter.filters = [{'type': 'score', 'min_score': 0.6}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with scores >= 0.6 (0.6, 0.8, 1.0)
        self.assertEqual(len(result), 3)
        scores = [self.filter._get_score(doc) for doc in result]
        self.assertTrue(all(s >= 0.6 for s in scores))

    def test_score_filter_max_threshold(self):
        """Test filtering with maximum score threshold."""
        self.filter.filters = [{'type': 'score', 'max_score': 0.5}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with scores <= 0.5 (0.2, 0.4)
        self.assertEqual(len(result), 2)
        scores = [self.filter._get_score(doc) for doc in result]
        self.assertTrue(all(s <= 0.5 for s in scores))

    def test_score_filter_range(self):
        """Test filtering with both min and max thresholds."""
        self.filter.filters = [{'type': 'score', 'min_score': 0.4, 'max_score': 0.8}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with 0.4 <= score <= 0.8 (0.4, 0.6, 0.8)
        self.assertEqual(len(result), 3)
        scores = [self.filter._get_score(doc) for doc in result]
        self.assertTrue(all(0.4 <= s <= 0.8 for s in scores))

    def test_score_filter_missing_score(self):
        """Test handling of documents with missing scores."""
        docs = [
            Document(text="No score", metadata={}),
            Document(text="With score", metadata={"relevance_score": 0.7})
        ]

        self.filter.filters = [{'type': 'score', 'min_score': 0.5}]
        self.filter.default_score = 0.0

        result = self.filter._process_docs(docs)

        # Only doc with score >= 0.5 should pass
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "With score")

    def test_score_filter_custom_score_field(self):
        """Test using custom metadata field for scores."""
        docs = [
            Document(text="Doc 1", metadata={"custom_score": 0.3}),
            Document(text="Doc 2", metadata={"custom_score": 0.7})
        ]

        self.filter.filters = [{'type': 'score', 'min_score': 0.5}]
        self.filter.score_field = 'custom_score'

        result = self.filter._process_docs(docs)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Doc 2")

    # ========== Length Filter Tests ==========

    def test_length_filter_min_length(self):
        """Test filtering by minimum text length."""
        self.filter.filters = [{'type': 'length', 'min_length': 100}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with length >= 100 (100, 500, 1000)
        self.assertEqual(len(result), 3)
        lengths = [len(doc.text) for doc in result]
        self.assertTrue(all(l >= 100 for l in lengths))

    def test_length_filter_max_length(self):
        """Test filtering by maximum text length."""
        self.filter.filters = [{'type': 'length', 'max_length': 100}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with length <= 100 (10, 50, 100)
        self.assertEqual(len(result), 3)
        lengths = [len(doc.text) for doc in result]
        self.assertTrue(all(l <= 100 for l in lengths))

    def test_length_filter_range(self):
        """Test filtering with both min and max length."""
        self.filter.filters = [{'type': 'length', 'min_length': 50, 'max_length': 500}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep docs with 50 <= length <= 500 (50, 100, 500)
        self.assertEqual(len(result), 3)
        lengths = [len(doc.text) for doc in result]
        self.assertTrue(all(50 <= l <= 500 for l in lengths))

    def test_length_filter_empty_text(self):
        """Test handling of documents with empty or None text."""
        docs = [
            Document(text="", metadata={"relevance_score": 0.5}),  # Empty text
            Document(text="A", metadata={"relevance_score": 0.5}),  # Single char (will be filtered)
            Document(text="Valid", metadata={"relevance_score": 0.5})
        ]

        self.filter.filters = [{'type': 'length', 'min_length': 2}]

        result = self.filter._process_docs(docs)

        # Only doc with length >= 2 should pass
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Valid")

    # ========== Top-K Filter Tests ==========

    def test_topk_filter_basic(self):
        """Test top-K filtering with k < len(docs)."""
        self.filter.filters = [{'type': 'topk', 'k': 3}]

        result = self.filter._process_docs(self.sample_docs)

        # Should keep top 3 by score (1.0, 0.8, 0.6)
        self.assertEqual(len(result), 3)
        scores = [self.filter._get_score(doc) for doc in result]
        self.assertEqual(sorted(scores, reverse=True), [1.0, 0.8, 0.6])

    def test_topk_filter_k_greater_than_docs(self):
        """Test top-K when k > number of documents."""
        self.filter.filters = [{'type': 'topk', 'k': 10}]

        result = self.filter._process_docs(self.sample_docs)

        # Should return all documents
        self.assertEqual(len(result), len(self.sample_docs))

    def test_topk_filter_k_equals_docs(self):
        """Test top-K when k equals number of documents."""
        self.filter.filters = [{'type': 'topk', 'k': 5}]

        result = self.filter._process_docs(self.sample_docs)

        self.assertEqual(len(result), 5)

    # ========== Percentile Filter Tests ==========

    def test_percentile_filter_basic(self):
        """Test percentile filtering with valid percentile."""
        self.filter.filters = [{'type': 'percentile', 'percentile': 0.6}]

        result = self.filter._process_docs(self.sample_docs)

        # 5 docs * 0.6 = 3.0 -> ceil(3.0) = 3 docs
        self.assertEqual(len(result), 3)

    def test_percentile_filter_edge_values(self):
        """Test percentile with 0.0 and 1.0."""
        # Test percentile = 0.0
        self.filter.filters = [{'type': 'percentile', 'percentile': 0.0}]
        result = self.filter._process_docs(self.sample_docs)
        self.assertEqual(len(result), 0)

        # Test percentile = 1.0
        self.filter.filters = [{'type': 'percentile', 'percentile': 1.0}]
        result = self.filter._process_docs(self.sample_docs)
        self.assertEqual(len(result), 5)

    def test_percentile_filter_clamping(self):
        """Test clamping of invalid percentile values."""
        # Test percentile > 1.0 (should clamp to 1.0)
        self.filter.filters = [{'type': 'percentile', 'percentile': 1.5}]
        result = self.filter._process_docs(self.sample_docs)
        self.assertEqual(len(result), 5)

        # Test percentile < 0.0 (should clamp to 0.0)
        self.filter.filters = [{'type': 'percentile', 'percentile': -0.3}]
        result = self.filter._process_docs(self.sample_docs)
        self.assertEqual(len(result), 0)

    def test_percentile_filter_rounding(self):
        """Test ceiling behavior for fractional counts."""
        # 5 docs * 0.5 = 2.5 -> ceil(2.5) = 3 docs
        self.filter.filters = [{'type': 'percentile', 'percentile': 0.5}]
        result = self.filter._process_docs(self.sample_docs)
        self.assertEqual(len(result), 3)

    # ========== Logic Combination Tests ==========

    def test_and_logic_intersection(self):
        """Test AND logic returns intersection of filters."""
        self.filter.filters = [
            {'type': 'score', 'min_score': 0.5},  # Returns docs with scores >= 0.5
            {'type': 'length', 'min_length': 100}  # Returns docs with length >= 100
        ]
        self.filter.logic_operator = 'AND'

        result = self.filter._process_docs(self.sample_docs)

        # Intersection: docs that satisfy BOTH filters
        # Docs: score >= 0.5 are [0.6, 0.8, 1.0]
        # Docs: length >= 100 are [100, 500, 1000]
        # Intersection should be docs with both conditions
        self.assertTrue(len(result) > 0)
        for doc in result:
            self.assertGreaterEqual(self.filter._get_score(doc), 0.5)
            self.assertGreaterEqual(len(doc.text), 100)

    def test_or_logic_union(self):
        """Test OR logic returns union of filters."""
        self.filter.filters = [
            {'type': 'score', 'min_score': 0.9},  # Returns only highest score doc
            {'type': 'length', 'max_length': 10}  # Returns only shortest doc
        ]
        self.filter.logic_operator = 'OR'

        result = self.filter._process_docs(self.sample_docs)

        # Union: docs that satisfy EITHER filter
        # Should include both extremes
        self.assertGreaterEqual(len(result), 2)

    def test_and_logic_no_overlap(self):
        """Test AND logic with no overlapping documents."""
        self.filter.filters = [
            {'type': 'score', 'max_score': 0.3},  # Only first doc
            {'type': 'score', 'min_score': 0.9}   # Only last doc
        ]
        self.filter.logic_operator = 'AND'

        result = self.filter._process_docs(self.sample_docs)

        # No overlap, should return empty
        self.assertEqual(len(result), 0)

    def test_single_filter_logic_irrelevant(self):
        """Test that logic operator is ignored with single filter."""
        self.filter.filters = [{'type': 'score', 'min_score': 0.5}]
        self.filter.logic_operator = 'AND'

        result_and = self.filter._process_docs(self.sample_docs)

        self.filter.logic_operator = 'OR'
        result_or = self.filter._process_docs(self.sample_docs)

        # Should get same results regardless of logic operator
        self.assertEqual(len(result_and), len(result_or))

    # ========== Order Preservation Tests ==========

    def test_preserve_order_enabled(self):
        """Test that original order is preserved when enabled."""
        self.filter.filters = [{'type': 'score', 'min_score': 0.4}]
        self.filter.preserve_order = True

        result = self.filter._process_docs(self.sample_docs)

        # Check that result maintains original relative order
        # Original order: scores [0.2, 0.4, 0.6, 0.8, 1.0]
        # Filtered (>= 0.4): should be [0.4, 0.6, 0.8, 1.0] in that order
        result_scores = [self.filter._get_score(doc) for doc in result]
        self.assertEqual(result_scores, [0.4, 0.6, 0.8, 1.0])

    # ========== Edge Case Tests ==========

    def test_empty_document_list(self):
        """Test handling of empty document list."""
        result = self.filter._process_docs([])

        self.assertEqual(result, [])

    def test_no_filters_configured(self):
        """Test that documents pass through unchanged when no filters."""
        self.filter.filters = []

        result = self.filter._process_docs(self.sample_docs)

        self.assertEqual(len(result), len(self.sample_docs))
        self.assertEqual(result, self.sample_docs)

    def test_all_documents_filtered_out(self):
        """Test when all documents fail filter criteria."""
        self.filter.filters = [{'type': 'score', 'min_score': 1.5}]

        result = self.filter._process_docs(self.sample_docs)

        self.assertEqual(len(result), 0)

    def test_complex_multi_filter_scenario(self):
        """Test complex scenario with multiple filters and AND logic."""
        self.filter.filters = [
            {'type': 'score', 'min_score': 0.5},
            {'type': 'length', 'min_length': 100},
            {'type': 'percentile', 'percentile': 0.8}
        ]
        self.filter.logic_operator = 'AND'

        result = self.filter._process_docs(self.sample_docs)

        # Verify all conditions are met
        for doc in result:
            self.assertGreaterEqual(self.filter._get_score(doc), 0.5)
            self.assertGreaterEqual(len(doc.text), 100)

    # ========== Integration Tests ==========

    def test_integration_with_component_configer(self):
        """Test initialization from ComponentConfiger."""
        config = {
            'name': 'integration_test',
            'description': 'Integration test filter',
            'filters': [
                {'type': 'score', 'min_score': 0.7},
                {'type': 'topk', 'k': 5}
            ],
            'logic_operator': 'OR',
            'score_field': 'relevance_score',
            'default_score': 0.0,
            'preserve_order': True
        }

        configer = self._create_configer(config)
        filter_obj = ThresholdFilter()
        filter_obj._initialize_by_component_configer(configer)

        # Test that filter works with configuration
        result = filter_obj._process_docs(self.sample_docs)

        # With OR logic, should get union of high-score docs and top-5
        self.assertTrue(len(result) > 0)

    def test_integration_with_query_object(self):
        """Test that Query object parameter is handled correctly."""
        self.filter.filters = [{'type': 'score', 'min_score': 0.5}]

        query = Query(query_str="test query")
        result = self.filter._process_docs(self.sample_docs, query=query)

        # Query parameter should not affect filtering
        self.assertEqual(len(result), 3)


if __name__ == '__main__':
    unittest.main()
