# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/5 10:51
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_base_sls_log_sink.py

"""Unit tests for the BaseSLSLogSink log sink."""

import pytest

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse_extension.logger.log_sink.base_sls_log_sink import \
    BaseSLSLogSink


class _RecordingSLSLogSink(BaseSLSLogSink):
    """Concrete sink recording every process_record call."""

    processed_records: list = []

    def process_record(self, record):
        self.processed_records.append(record)


@pytest.fixture
def sink():
    return _RecordingSLSLogSink(log_type=LogTypeEnum.sls)


class TestBaseSLSLogSink:
    """Tests for BaseSLSLogSink.filter and process_record."""

    def test_filter_rejects_mismatched_log_type(self, sink):
        record = {"extra": {"log_type": LogTypeEnum.llm_input}}
        assert sink.filter(record) is False
        assert sink.processed_records == []

    def test_filter_rejects_missing_log_type(self, sink):
        record = {"extra": {}}
        assert sink.filter(record) is False
        assert sink.processed_records == []

    def test_filter_accepts_matching_log_type(self, sink):
        record = {"extra": {"log_type": LogTypeEnum.sls}}
        assert sink.filter(record) is True
        assert sink.processed_records == [record]

    def test_filter_accepts_matching_string_log_type(self, sink):
        record = {"extra": {"log_type": "sls"}}
        assert sink.filter(record) is True
        assert sink.processed_records == [record]

    def test_filter_default_log_type(self):
        default_sink = _RecordingSLSLogSink()
        record = {"extra": {"log_type": LogTypeEnum.default}}
        assert default_sink.filter(record) is True
        assert default_sink.processed_records == [record]

    def test_base_process_record_raises_not_implemented(self):
        base_sink = BaseSLSLogSink()
        with pytest.raises(NotImplementedError):
            base_sink.process_record({"extra": {}})
