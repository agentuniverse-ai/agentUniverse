"""Optional request configuration retains the tool's declared defaults."""

from unittest.mock import patch

import pytest
from langchain_community.utilities.requests import GenericRequestsWrapper

from agentuniverse.agent.action.tool.common_tool.request_tool import RequestTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


def configure(tool, **settings):
    config = Configer()
    config.value.update(name="fetch", description="Fetch a page", input_keys=["input"], tool_type="api", **settings)
    return tool.initialize_by_component_configer(ToolConfiger(config).load())


def test_minimal_config_builds_default_get_text_wrapper():
    tool = configure(RequestTool())
    assert tool.method == "GET"
    assert tool.headers == {}
    assert tool.response_content_type == "text"
    assert tool.requests_wrapper.response_content_type == "text"
    assert tool.requests_wrapper.headers == {}
    with patch.object(GenericRequestsWrapper, "get", return_value="body") as get:
        assert tool.execute("https://example.invalid/page") == "body"
    get.assert_called_once_with("https://example.invalid/page")


def test_omitted_config_keeps_explicit_constructor_values():
    tool = configure(RequestTool(method="POST", headers={"Accept": "application/json"},
                                 response_content_type="json", json_parser=True))
    assert tool.method == "POST"
    assert tool.headers == {"Accept": "application/json"}
    assert tool.requests_wrapper.headers == tool.headers
    assert tool.requests_wrapper.response_content_type == "json"
    assert tool.json_parser is True


def test_explicit_config_overrides_constructor_values():
    tool = configure(RequestTool(method="POST", headers={"Accept": "application/json"},
                                 response_content_type="json", json_parser=True),
                     method="GET", headers={}, response_content_type="text", json_parser=False)
    assert tool.method == "GET"
    assert tool.requests_wrapper.headers == {}
    assert tool.requests_wrapper.response_content_type == "text"
    assert tool.json_parser is False


def test_explicit_null_response_type_is_not_silently_defaulted():
    with pytest.raises(ValueError, match="response_content_type"):
        configure(RequestTool(), response_content_type=None)
