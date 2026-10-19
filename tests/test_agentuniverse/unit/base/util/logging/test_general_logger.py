# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 11:00
# @Author  : Yue Wang
# @FileName: test_general_logger.py
"""Unit tests for general_logger helpers and GeneralLogger."""

from unittest.mock import patch

import pytest

from agentuniverse.base.util.logging.general_logger import (
    GeneralLogger,
    Logger,
    _get_source_filter,
    get_context_prefix,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


def _make_logger(**kwargs):
    """Build a GeneralLogger without registering a loguru handler."""
    params = dict(module_name="test_module", log_path="/tmp/test.log",
                  log_format="{message}", log_rotation="10 MB",
                  log_retention="1 week", add_handler=False)
    params.update(kwargs)
    return GeneralLogger(**params)


class TestGetContextPrefix:
    """Test get_context_prefix formatting."""

    @pytest.mark.parametrize(
        ("trace_dict", "log_context", "expected"),
        [
            ({}, None, "[default]"),
            ({"trace_id": "t1"}, None, '["trace_id": "t1"]'),
            ({}, {"foo": "bar"}, '["foo": "bar"]'),
        ],
    )
    @patch("agentuniverse.base.util.logging.general_logger.FrameworkContextManager")
    @patch("agentuniverse.base.util.logging.general_logger.AuTraceManager")
    def test_prefix(self, mock_trace, mock_ctx, trace_dict, log_context, expected):
        """Prefix renders the trace dict, merging any dict LOG_CONTEXT."""
        mock_trace.return_value.get_trace_dict.return_value = trace_dict
        mock_ctx.return_value.get_context.return_value = log_context
        assert get_context_prefix() == expected


class TestSourceFilter:
    """Test _get_source_filter."""

    def test_accepts_matching_record(self):
        """A record with matching log_type and source is accepted."""
        record = {"extra": {"log_type": LogTypeEnum.default, "source": "mod"}}
        assert _get_source_filter("mod")(record) is True

    @pytest.mark.parametrize("log_type", [LogTypeEnum.llm_input, LogTypeEnum.tool_invocation])
    def test_rejects_other_log_type(self, log_type):
        record = {"extra": {"log_type": log_type, "source": "mod"}}
        assert _get_source_filter("mod")(record) is False

    def test_rejects_other_source(self):
        record = {"extra": {"log_type": LogTypeEnum.default, "source": "other"}}
        assert _get_source_filter("mod")(record) is False


class TestGeneralLogger:
    """Test GeneralLogger configuration handling."""

    def test_stores_config_attributes(self):
        """Constructor stores the provided configuration."""
        logger = _make_logger(module_name="my_module", log_path="/tmp/x.log")
        assert logger.module_name == "my_module"
        assert logger.log_path == "/tmp/x.log"
        assert logger.log_rotation == "10 MB"

    def test_update_properties(self):
        """update_properties modifies existing attributes only."""
        logger = _make_logger()
        logger.update_properties(log_path="/tmp/new.log")
        assert logger.log_path == "/tmp/new.log"
        with pytest.raises(AttributeError):
            logger.update_properties(bogus_attribute=1)

    def test_get_inheritance_depth(self):
        """GeneralLogger sits one level below the abstract Logger."""
        assert Logger in GeneralLogger.__mro__
        assert _make_logger().get_inheritance_depth() == 1
