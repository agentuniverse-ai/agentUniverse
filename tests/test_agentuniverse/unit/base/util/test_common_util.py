# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.util.common_util."""

import json
from queue import Queue

import pytest

from agentuniverse.base.util.common_util import (
    parse_and_check_json_markdown,
    parse_json_markdown,
    parse_partial_json,
    stream_output,
)


class TestStreamOutput:
    """Tests for stream_output."""

    def test_stream_output_put_nowait(self):
        output_stream = Queue()
        data = {"content": "hello"}
        stream_output(output_stream, data)
        assert output_stream.qsize() == 1
        assert output_stream.get_nowait() == data

    def test_stream_output_none_stream_is_a_noop(self):
        # None stream must be handled gracefully without raising.
        stream_output(None, {"content": "hello"})


class TestParsePartialJson:
    """Tests for parse_partial_json."""

    def test_parse_complete_json(self):
        assert parse_partial_json('{"a": 1, "b": [1, 2]}') == {"a": 1, "b": [1, 2]}

    def test_parse_missing_closing_brackets(self):
        assert parse_partial_json('{"a": [1, 2') == {"a": [1, 2]}

    def test_parse_unterminated_string(self):
        assert parse_partial_json('{"a": "unterminated') == {"a": "unterminated"}

    def test_parse_drops_trailing_unbalanced_characters(self):
        assert parse_partial_json('{"a": 1}{') == {"a": 1}

    def test_parse_malformed_input_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_partial_json("not json at all")

    def test_parse_strict_flag_accepted(self):
        assert parse_partial_json('{"a": 1}', strict=True) == {"a": 1}


class TestParseJsonMarkdown:
    """Tests for parse_json_markdown."""

    def test_parse_fenced_code_block(self):
        text = '```json\n{"b": 2}\n```'
        assert parse_json_markdown(text) == {"b": 2}

    def test_parse_raw_json_object(self):
        assert parse_json_markdown('{"x": 5}') == {"x": 5}

    def test_parse_multiline_action_input_is_escaped(self):
        text = '{"action_input": "line1\nline2", "action": "A"}'
        assert parse_json_markdown(text) == {"action_input": "line1\nline2", "action": "A"}

    def test_parse_invalid_input_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_markdown("not json")


class TestParseAndCheckJsonMarkdown:
    """Tests for parse_and_check_json_markdown."""

    def test_parse_with_expected_keys(self):
        text = '{"action_input": "x", "action": "A"}'
        assert parse_and_check_json_markdown(text, ["action"]) == {
            "action_input": "x",
            "action": "A",
        }

    def test_missing_expected_key_raises(self):
        text = '{"action_input": "x"}'
        with pytest.raises(Exception, match="Expected key `action`"):
            parse_and_check_json_markdown(text, ["action"])
