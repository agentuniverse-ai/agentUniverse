# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:40
# @Author  : yuewang
# @FileName: test_flask_response_log_sink.py
"""Unit tests for FlaskResponseLogSink."""

import pytest

from agentuniverse.base.util.logging.log_sink.flask_response_log_sink import FlaskResponseLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


@pytest.fixture
def sink():
    """Create a FlaskResponseLogSink."""
    return FlaskResponseLogSink()


def _record(log_type, flask_response=None):
    record = {'extra': {'log_type': log_type, 'elapsed_time': 0.5}}
    if flask_response is not None:
        record['extra']['flask_response'] = flask_response
    return record


class TestFlaskResponseLogSink:
    """Test FlaskResponseLogSink filter and record processing."""

    def test_log_type_default(self, sink):
        assert sink.log_type == LogTypeEnum.flask_response

    def test_filter_rejects_other_log_types(self, sink):
        assert sink.filter(_record(LogTypeEnum.llm_input)) is False

    def test_filter_accepts_matching_record(self, sink):
        record = _record(LogTypeEnum.flask_response, {'status': 200})
        assert sink.filter(record) is True
        assert 'flask_response' not in record['extra']
        assert 'elapsed_time' in record['extra']

    def test_process_record_requires_elapsed_time(self, sink):
        record = _record(LogTypeEnum.flask_response, {'status': 200})
        sink.process_record(record)
        assert 'message' in record
        assert 'flask_response' not in record['extra']

    def test_generate_log_returns_none_by_default(self, sink):
        assert sink.generate_log(flask_response={'status': 200}, elapsed_time=0.1) is None
