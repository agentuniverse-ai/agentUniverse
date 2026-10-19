# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:35
# @Author  : yuewang
# @FileName: test_flask_request_log_sink.py
"""Unit tests for FlaskRequestLogSink."""

import pytest

from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import FlaskRequestLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


@pytest.fixture
def sink():
    """Create a FlaskRequestLogSink."""
    return FlaskRequestLogSink()


def _record(log_type, flask_request=None):
    return {'extra': {'log_type': log_type, 'flask_request': flask_request}}


class TestFlaskRequestLogSink:
    """Test FlaskRequestLogSink filter and record processing."""

    def test_log_type_default(self, sink):
        assert sink.log_type == LogTypeEnum.flask_request

    def test_filter_rejects_other_log_types(self, sink):
        assert sink.filter(_record(LogTypeEnum.default, {})) is False

    def test_filter_accepts_matching_record(self, sink):
        record = _record(LogTypeEnum.flask_request, {'path': '/x'})
        assert sink.filter(record) is True
        assert 'flask_request' not in record['extra']
        assert record['message'] is None  # generate_log not overridden

    def test_process_record_sets_message_and_pops_extra(self, sink):
        record = _record(LogTypeEnum.flask_request, {'path': '/y'})
        sink.process_record(record)
        assert 'message' in record
        assert 'flask_request' not in record['extra']

    def test_generate_log_returns_none_by_default(self, sink):
        assert sink.generate_log(flask_request={'path': '/z'}) is None
