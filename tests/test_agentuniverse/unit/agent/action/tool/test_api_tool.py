# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_api_tool.py

"""Unit tests for APITool pure helpers (no HTTP requests)."""

import httpx
import pytest

from agentuniverse.agent.action.tool.api_tool import APITool


@pytest.fixture
def api_tool():
    return APITool(openapi_spec={"url": "http://x", "method": "get"})


class TestConverters:
    """Test primitive conversion helpers."""

    def test_convert_integer(self, api_tool):
        assert api_tool._convert_integer("42") == 42
        assert api_tool._convert_integer(3) == 3
        with pytest.raises(ValueError):
            api_tool._convert_integer(True)
        with pytest.raises(ValueError):
            api_tool._convert_integer("3.5")

    def test_convert_number(self, api_tool):
        assert api_tool._convert_number(5) == 5
        assert api_tool._convert_number("1.5") == 1.5
        assert api_tool._convert_number("1e3") == 1000.0
        assert api_tool._convert_number("7") == 7
        with pytest.raises(ValueError):
            api_tool._convert_number(True)

    def test_convert_boolean(self, api_tool):
        assert api_tool._convert_boolean(True) is True
        assert api_tool._convert_boolean(0) is False
        assert api_tool._convert_boolean("true") is True
        assert api_tool._convert_boolean("TRUE") is True
        assert api_tool._convert_boolean("1") is True
        assert api_tool._convert_boolean("false") is False
        with pytest.raises(ValueError):
            api_tool._convert_boolean("maybe")

    def test_convert_body_property_type(self, api_tool):
        assert api_tool.convert_body_property_type(
            {"type": "integer"}, "7") == 7
        assert api_tool.convert_body_property_type(
            {"type": "string"}, 7) == "7"
        assert api_tool.convert_body_property_type(
            {"type": "boolean"}, "true") is True
        assert api_tool.convert_body_property_type(
            {"type": "object"}, '{"a": 1}') == {"a": 1}
        assert api_tool.convert_body_property_type(
            {"type": "object"}, {"a": 1}) == {"a": 1}
        # Unsupported types fall back to the original value.
        assert api_tool.convert_body_property_type(
            {"type": "array"}, [1]) == [1]

    def test_convert_body_property_any_of(self, api_tool):
        assert api_tool.convert_body_property_any_of(
            {}, "5", [{"type": "integer"}, {"type": "string"}]) == 5
        # Failed conversions fall back to the original value.
        assert api_tool.convert_body_property_any_of(
            {}, "5", [{"type": "boolean"}]) == "5"
        with pytest.raises(Exception, match="Max recursion depth reached"):
            api_tool.convert_body_property_any_of(
                {}, "5", [{"anyOf": [{"anyOf": []}]}], max_recursive=0)


class TestParameterAndResponse:
    """Test parameter extraction and response parsing."""

    def test_get_parameter_value_present(self):
        assert APITool.get_parameter_value({"name": "q"}, {"q": "x"}) == "x"

    def test_get_parameter_value_default(self):
        assert APITool.get_parameter_value(
            {"name": "q", "schema": {"default": 9}}, {}) == 9

    def test_get_parameter_value_missing_required_raises(self):
        with pytest.raises(Exception, match="Missing required parameter"):
            APITool.get_parameter_value({"name": "q", "required": True}, {})

    def test_validate_and_parse_response_json(self):
        response = httpx.Response(200, text='{"ok": true}')
        assert APITool.validate_and_parse_response(response) == '{"ok": true}'

    def test_validate_and_parse_empty_response(self):
        response = httpx.Response(200, content=b"")
        assert "Empty response" in APITool.validate_and_parse_response(
            response)

    def test_validate_and_parse_error_response(self):
        response = httpx.Response(500, text="boom")
        with pytest.raises(Exception, match="status code 500"):
            APITool.validate_and_parse_response(response)

    def test_validate_and_parse_invalid_response_type(self):
        with pytest.raises(ValueError, match="Invalid response type"):
            APITool.validate_and_parse_response("not a response")
