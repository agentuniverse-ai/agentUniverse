# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_base_file_log_sink.py

"""Unit tests for the BaseFileLogSink component."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import     BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.logging.logging_config import LoggingConfig


class TestBaseFileLogSink:
    """Test BaseFileLogSink defaults, filtering and configer init."""

    def test_default_attributes(self):
        sink = BaseFileLogSink()
        assert sink.file_prefix is None
        assert sink.log_rotation == LoggingConfig.log_rotation
        assert sink.log_retention == LoggingConfig.log_retention
        assert sink.compression is None

    def test_filter_rejects_other_log_type(self):
        sink = BaseFileLogSink()
        record = {"extra": {"log_type": LogTypeEnum.agent_input}}
        assert sink.filter(record) is False

    def test_filter_matching_type_calls_process_record(self):
        sink = BaseFileLogSink()
        record = {"extra": {"log_type": LogTypeEnum.default}}
        with pytest.raises(NotImplementedError):
            sink.filter(record)

    def test_initialize_by_component_configer(self):
        sink = BaseFileLogSink()
        configer = SimpleNamespace(file_prefix="au", log_rotation="5 MB",
                                   log_retention="7 days",
                                   compression="zip")
        returned = sink._initialize_by_component_configer(configer)
        assert returned is sink
        assert sink.file_prefix == "au"
        assert sink.log_rotation == "5 MB"
        assert sink.log_retention == "7 days"
        assert sink.compression == "zip"

    def test_register_sink_skips_when_already_registered(self):
        sink = BaseFileLogSink()
        sink.sink_id = 3
        sink.register_sink()
        assert sink.sink_id == 3
