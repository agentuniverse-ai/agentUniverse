# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_log_sink.py
"""Unit tests for the base LogSink class."""

from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class _RecordingSink(LogSink):
    """A LogSink subclass with a concrete process_record."""

    def process_record(self, record):
        self.last = record


class TestLogSink:
    """Test LogSink defaults, filtering, and registration."""

    def test_default_attributes(self):
        """A bare LogSink exposes its documented defaults."""
        sink = LogSink()
        assert sink.component_type == ComponentEnum.LOG_SINK
        assert sink.name is None
        assert sink.level == "INFO"
        assert sink.sink_id == -1
        assert sink.log_type == LogTypeEnum.default
        assert sink.enqueue is True

    def test_get_inheritance_depth(self):
        """Depth counts steps from the subclass down to LogSink."""
        assert LogSink().get_inheritance_depth() == 0
        assert _RecordingSink().get_inheritance_depth() == 1

    def test_process_record_not_implemented_on_base(self):
        """The base process_record raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            LogSink().process_record({})

    def test_filter_matches_log_type(self):
        """filter accepts only records tagged with the sink's log_type."""
        sink = LogSink()
        matching = {"extra": {"log_type": LogTypeEnum.default}}
        other = {"extra": {"log_type": LogTypeEnum.agent_input}}
        assert sink.filter(matching) is True
        assert sink.filter(other) is False

    def test_call_delegates_to_process_record(self):
        """Calling the sink forwards message.record to process_record."""
        sink = LogSink()
        message = MagicMock()
        message.record = {"k": 1}
        with patch.object(LogSink, "process_record") as mock_pr:
            sink(message)
            mock_pr.assert_called_once_with({"k": 1})

    def test_register_sink_sets_id_and_skips_when_registered(self):
        """register_sink adds once and is a no-op after sink_id is set."""
        with patch(
                "agentuniverse.base.util.logging.log_sink."
                "log_sink.logger.add",
                return_value=42) as mock_add:
            sink = LogSink()
            sink.register_sink()
            assert sink.sink_id == 42
            mock_add.assert_called_once()

            again = LogSink()
            again.sink_id = 7
            again.register_sink()
            mock_add.assert_called_once()
            assert again.sink_id == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
