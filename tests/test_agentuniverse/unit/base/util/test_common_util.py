# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_common_util.py
"""Unit tests for the common_util pure helpers."""

import json
from queue import Queue

import pytest

from agentuniverse.base.util.common_util import (
    stream_output,
    parse_partial_json,
    parse_json_markdown,
    parse_and_check_json_markdown,
)


class TestStreamOutput:
    """Test stream_output queue behavior."""

    def test_puts_data_on_queue(self):
        """stream_output enqueues the provided dict."""
        q = Queue()
        stream_output(q, {"a": 1})
        assert q.get_nowait() == {"a": 1}

    def test_none_stream_is_noop(self):
        """stream_output tolerates a None stream without raising."""
        stream_output(None, {"a": 1})


class TestParsePartialJson:
    """Test parse_partial_json recovery of truncated JSON."""

    def test_complete_json(self):
        """A complete JSON string is parsed directly."""
        assert parse_partial_json('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}

    def test_missing_closing_brace(self):
        """A trailing unclosed object is auto-closed."""
        assert parse_partial_json('{"a": 1, "b": 2') == {"a": 1, "b": 2}

    def test_unclosed_nested_string(self):
        """An unterminated string literal is closed before parsing."""
        assert parse_partial_json('{"a": "unterminated') == {"a": "unterminated"}

    def test_mismatched_closer_returns_none(self):
        """A mismatched closing bracket yields None."""
        assert parse_partial_json('{"a": [1}') is None


class TestParseJsonMarkdown:
    """Test parse_json_markdown extraction and escaping."""

    def test_fenced_json_block(self):
        """JSON wrapped in a triple-backtick fence is extracted and parsed."""
        text = "Result:\n```json\n{\"a\": 1}\n```\ndone"
        assert parse_json_markdown(text) == {"a": 1}

    def test_plain_json_string(self):
        """A bare JSON string with no fence is parsed as-is."""
        assert parse_json_markdown('  {"x": 2}  ') == {"x": 2}

    def test_multiline_action_input(self):
        """Raw newlines inside action_input are escaped to \\n."""
        text = '{"action_input": "line1\nline2"}'
        result = parse_json_markdown(text)
        assert result == {"action_input": "line1\nline2"}
        assert json.loads(json.dumps(result))["action_input"] == "line1\nline2"


class TestParseAndCheckJsonMarkdown:
    """Test parse_and_check_json_markdown key validation."""

    def test_all_expected_keys_present(self):
        """The dict is returned when every expected key is present."""
        obj = parse_and_check_json_markdown('{"a": 1, "b": 2}', ["a", "b"])
        assert obj == {"a": 1, "b": 2}

    def test_missing_expected_key_raises(self):
        """An Exception is raised when an expected key is absent."""
        with pytest.raises(Exception):
            parse_and_check_json_markdown('{"a": 1}', ["a", "b"])
