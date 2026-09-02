# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_metrics_types.py

"""Unit tests for the CodeMetrics TypedDict in metrics_types."""

from agentuniverse.agent.action.knowledge.doc_processor.types.metrics_types \
    import CodeMetrics


class TestCodeMetrics:
    """Test the CodeMetrics TypedDict schema."""

    def test_is_typed_dict_subclass(self):
        assert issubclass(CodeMetrics, dict)

    def test_required_keys(self):
        assert CodeMetrics.__required_keys__ == {
            "line_count", "code_line_count", "avg_line_length",
            "max_line_length", "character_count",
        }

    def test_no_optional_keys(self):
        assert CodeMetrics.__optional_keys__ == frozenset()

    def test_field_annotations(self):
        annotations = CodeMetrics.__annotations__
        assert annotations["line_count"] is int
        assert annotations["code_line_count"] is int
        assert annotations["avg_line_length"] is float
        assert annotations["max_line_length"] is int
        assert annotations["character_count"] is int

    def test_valid_dict_matches_schema(self):
        metrics = {
            "line_count": 120,
            "code_line_count": 90,
            "avg_line_length": 42.5,
            "max_line_length": 200,
            "character_count": 3800,
        }
        assert isinstance(metrics, dict)
        assert set(metrics.keys()) == CodeMetrics.__required_keys__

    def test_typed_dict_is_total_by_default(self):
        # no default values may be omitted at construction time
        assert CodeMetrics.__total__ is True
