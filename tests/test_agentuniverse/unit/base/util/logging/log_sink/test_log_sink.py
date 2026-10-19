# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_log_sink.py

"""Unit tests for the base LogSink component."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.component.component_enum import ComponentEnum


class TestLogSink:
    """Test LogSink defaults, filtering and depth."""

    def test_default_attributes(self):
        sink = LogSink()
        assert sink.name is None
        assert sink.level == "INFO"
        assert sink.sink_id == -1
        assert sink.log_type == LogTypeEnum.default
        assert sink.enqueue is True
        assert sink.component_type == ComponentEnum.LOG_SINK

    def test_inheritance_depth(self):
        assert LogSink().get_inheritance_depth() == 0

    def test_subclass_depth_is_greater(self):
        class Child(LogSink):
            pass

        assert Child().get_inheritance_depth() == 1

    def test_filter_matching_log_type(self):
        record = {"extra": {"log_type": LogTypeEnum.default}}
        assert LogSink().filter(record) is True

    def test_filter_non_matching_log_type(self):
        record = {"extra": {"log_type": LogTypeEnum.agent_input}}
        assert LogSink().filter(record) is False

    def test_call_dispatches_to_process_record(self):
        sink = LogSink()
        with pytest.raises(NotImplementedError, match="Subclasses must"):
            sink(SimpleNamespace(record={}))

    def test_register_sink_skips_when_already_registered(self):
        sink = LogSink()
        sink.sink_id = 7
        sink.register_sink()
        assert sink.sink_id == 7
