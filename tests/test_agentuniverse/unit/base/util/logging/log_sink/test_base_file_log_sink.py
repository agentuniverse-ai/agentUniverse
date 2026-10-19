# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_base_file_log_sink.py
"""Unit tests for BaseFileLogSink."""

from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.log_sink.base_file_log_sink import (
    BaseFileLogSink,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class RecordingSink(BaseFileLogSink):
    """Concrete sink that records the records it processes."""

    def process_record(self, record):
        self._processed = getattr(self, "_processed", []) + [record]


class TestBaseFileLogSink:
    """Test BaseFileLogSink defaults, filtering and sink registration."""

    def test_model_defaults(self):
        """Field defaults match the documented log sink contract."""
        sink = BaseFileLogSink()
        assert sink.component_type == ComponentEnum.LOG_SINK
        assert sink.file_prefix is None
        assert sink.compression is None
        assert sink.sink_id == -1
        assert sink.level == "INFO"
        assert sink.enqueue is True

    def test_filter_matching_type_processes_record(self):
        """Records with the configured log type are processed and pass."""
        sink = RecordingSink()
        record = {"extra": {"log_type": LogTypeEnum.default}}
        assert sink.filter(record) is True
        assert sink._processed == [record]

    def test_filter_mismatched_type_skips_record(self):
        """Records with another log type are rejected without processing."""
        sink = RecordingSink()
        record = {"extra": {"log_type": LogTypeEnum.sls}}
        assert sink.filter(record) is False
        assert getattr(sink, "_processed", []) == []

    def test_initialize_copies_configer_attributes(self):
        """Present configer attributes override the sink defaults."""
        configer = SimpleNamespace(
            file_prefix="audit",
            log_rotation="1 hour",
            log_retention="7 days",
            compression="zip",
        )
        sink = BaseFileLogSink()
        result = sink._initialize_by_component_configer(configer)
        assert result is sink
        assert sink.file_prefix == "audit"
        assert sink.log_rotation == "1 hour"
        assert sink.log_retention == "7 days"
        assert sink.compression == "zip"

    def test_register_sink_adds_file_sink_once(self):
        """register_sink wires loguru with the file path and skips repeats."""
        sink = RecordingSink()
        with patch("loguru.logger.add", return_value=42) as add, \
                patch(
                    "agentuniverse.base.util.logging.log_sink."
                    "base_file_log_sink._get_log_file_path",
                    return_value="/tmp/audit.log",
                ):
            sink.register_sink()
            assert sink.sink_id == 42
            assert add.call_count == 1
            sink.register_sink()
            assert add.call_count == 1
        kwargs = add.call_args.kwargs
        assert kwargs["sink"] == "/tmp/audit.log"
        assert kwargs["encoding"] == "utf-8"
        assert kwargs["rotation"] == sink.log_rotation
