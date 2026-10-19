# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 13:30
# @Author  : Yue Wang
# @FileName: test_metrics_types.py
"""Unit tests for CodeMetrics typed dict."""

import typing

from agentuniverse.agent.action.knowledge.doc_processor.types.metrics_types import \
    CodeMetrics


class TestCodeMetrics:
    """Test CodeMetrics structure and usage."""

    def test_is_typed_dict(self):
        """CodeMetrics is a TypedDict subclass."""
        assert issubclass(CodeMetrics, dict)
        assert typing.get_type_hints(CodeMetrics)

    def test_expected_fields(self):
        """CodeMetrics declares exactly the documented metric fields."""
        assert set(CodeMetrics.__annotations__) == {
            "line_count",
            "code_line_count",
            "avg_line_length",
            "max_line_length",
            "character_count",
        }

    def test_field_types(self):
        """Field annotations use int for counts and float for the average."""
        hints = typing.get_type_hints(CodeMetrics)
        assert hints["line_count"] is int
        assert hints["code_line_count"] is int
        assert hints["avg_line_length"] is float
        assert hints["max_line_length"] is int
        assert hints["character_count"] is int

    def test_instantiation_and_access(self):
        """A CodeMetrics value is a plain dict with the metric fields."""
        metrics: CodeMetrics = {
            "line_count": 100,
            "code_line_count": 80,
            "avg_line_length": 25.5,
            "max_line_length": 120,
            "character_count": 2000,
        }
        assert metrics["code_line_count"] == 80
        assert metrics["avg_line_length"] == 25.5
