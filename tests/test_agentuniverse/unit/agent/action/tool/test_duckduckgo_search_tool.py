#!/usr/bin/env python3

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from pydantic import ValidationError

from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import (
    DuckDuckGoSearchTool,
)
from agentuniverse.agent.action.tool.tool import Tool

MODULE = "agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool"


@pytest.fixture
def tool():
    return DuckDuckGoSearchTool(name="duckduckgo_search_tool")


@pytest.fixture
def text_results():
    return [
        {
            "title": "Python",
            "href": "https://python.org",
            "body": "Python language home page.",
        },
        {
            "title": "Tutorial",
            "url": "https://docs.python.org/tutorial",
            "snippet": "The Python tutorial.",
        },
    ]


@pytest.fixture
def news_results():
    return [
        {
            "title": "Framework release",
            "url": "https://example.com/release",
            "body": "A new framework version was released.",
            "date": "2026-08-15T01:02:03Z",
            "source": "Example News",
            "image": "https://example.com/release.jpg",
        }
    ]


def ddgs_context(*, text=None, news=None):
    client = MagicMock()
    client.text.return_value = text if text is not None else []
    client.news.return_value = news if news is not None else []
    context = MagicMock()
    context.__enter__.return_value = client
    context.__exit__.return_value = False
    return context, client


def test_text_search_returns_normalized_structured_results(tool, text_results):
    context, client = ddgs_context(text=text_results)
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = tool.execute("  python programming  ")

    assert result == {
        "status": "success",
        "query": "python programming",
        "search_type": "text",
        "region": None,
        "safesearch": "moderate",
        "timelimit": None,
        "count": 2,
        "results": [
            {
                "title": "Python",
                "url": "https://python.org",
                "snippet": "Python language home page.",
            },
            {
                "title": "Tutorial",
                "url": "https://docs.python.org/tutorial",
                "snippet": "The Python tutorial.",
            },
        ],
    }
    client.text.assert_called_once_with(
        keywords="python programming",
        safesearch="moderate",
        max_results=5,
        backend="auto",
    )
    client.news.assert_not_called()


def test_news_search_preserves_news_metadata(tool, news_results):
    context, client = ddgs_context(news=news_results)
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = tool.execute(
            "agent framework",
            search_type="news",
            region="us-en",
            max_results=10,
            safesearch="on",
            timelimit="w",
            backend="html",
        )

    assert result["status"] == "success"
    assert result["search_type"] == "news"
    assert result["count"] == 1
    assert result["results"][0]["source"] == "Example News"
    assert result["results"][0]["date"] == "2026-08-15T01:02:03Z"
    client.news.assert_called_once_with(
        keywords="agent framework",
        region="us-en",
        safesearch="on",
        timelimit="w",
        max_results=10,
    )
    client.text.assert_not_called()


def test_empty_result_is_success_with_stable_shape(tool):
    context, _ = ddgs_context(text=[])
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = tool.execute("query with no results")

    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["results"] == []


@pytest.mark.parametrize("query", ["", "   ", "\n\t"])
def test_empty_query_is_rejected_without_calling_client(tool, query):
    with patch(f"{MODULE}.DDGS") as ddgs:
        result = tool.execute(query)

    assert result["status"] == "error"
    assert result["error"]["type"] == "validation_error"
    assert result["results"] == []
    ddgs.assert_not_called()


def test_non_string_query_is_rejected(tool):
    result = tool.execute(123)  # type: ignore[arg-type]
    assert result["error"]["type"] == "validation_error"
    assert "string" in result["error"]["message"]


@pytest.mark.parametrize("value", [0, 21, -1])
def test_result_count_bounds_are_enforced(tool, value):
    result = tool.execute("query", max_results=value)
    assert result["error"]["type"] == "validation_error"
    assert "between 1 and 20" in result["error"]["message"]


@pytest.mark.parametrize("value", [True, 1.5, "5"])
def test_result_count_type_is_enforced(tool, value):
    result = tool.execute("query", max_results=value)  # type: ignore[arg-type]
    assert result["error"]["type"] == "validation_error"
    assert "integer" in result["error"]["message"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("search_type", "images", "text, news"),
        ("safesearch", "strict", "on, moderate, off"),
        ("timelimit", "hour", "d, w, m, y"),
        ("backend", "", "non-empty"),
    ],
)
def test_enum_and_backend_validation(tool, field, value, message):
    result = tool.execute("query", **{field: value})
    assert result["error"]["type"] == "validation_error"
    assert message in result["error"]["message"]


def test_runtime_overrides_do_not_mutate_configured_defaults(tool, text_results):
    context, _ = ddgs_context(text=text_results)
    with patch(f"{MODULE}.DDGS", return_value=context):
        tool.execute(
            "query",
            max_results=2,
            region="cn-zh",
            safesearch="off",
            timelimit="m",
            backend="html",
        )

    assert tool.max_results == 5
    assert tool.region is None
    assert tool.safesearch == "moderate"
    assert tool.timelimit is None
    assert tool.backend == "auto"


def test_proxy_and_timeout_are_client_constructor_arguments(tool, text_results):
    context, _ = ddgs_context(text=text_results)
    tool.proxy = "socks5://127.0.0.1:1080"
    tool.timeout = 25
    with patch(f"{MODULE}.DDGS", return_value=context) as ddgs:
        tool.execute("query")

    ddgs.assert_called_once_with(proxy="socks5://127.0.0.1:1080", timeout=25)


def test_network_error_returns_error_without_fake_results(tool):
    with patch(f"{MODULE}.DDGS", side_effect=RuntimeError("rate limited")):
        result = tool.execute("query")

    assert result["status"] == "error"
    assert result["error"] == {
        "type": "search_error",
        "message": "rate limited",
    }
    assert result["count"] == 0
    assert result["results"] == []


def test_missing_dependency_returns_actionable_error(tool):
    with (
        patch(f"{MODULE}.DDGS", None),
        patch(f"{MODULE}._DDGS_IMPORT_ERROR", ImportError("missing")),
    ):
        result = tool.execute("query")

    assert result["error"]["type"] == "dependency_error"
    assert "pip install duckduckgo-search" in result["error"]["message"]
    assert result["results"] == []


def test_async_execute_matches_sync_contract(tool, news_results):
    context, _ = ddgs_context(news=news_results)
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = asyncio.run(
            tool.async_execute(
                input="framework release",
                search_type="news",
                max_results=3,
            )
        )

    assert result["status"] == "success"
    assert result["search_type"] == "news"
    assert result["count"] == 1


def test_framework_run_uses_modern_keyword_signature(tool, text_results):
    context, _ = ddgs_context(text=text_results)
    tool.input_keys = ["input"]
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = Tool.run.__wrapped__(tool, input="python")

    assert result["status"] == "success"
    assert result["query"] == "python"


def test_framework_async_run_uses_modern_keyword_signature(tool, text_results):
    context, _ = ddgs_context(text=text_results)
    tool.input_keys = ["input"]
    with patch(f"{MODULE}.DDGS", return_value=context):
        result = asyncio.run(Tool.async_run.__wrapped__(tool, input="python"))

    assert result["status"] == "success"
    assert result["query"] == "python"


def test_model_configuration_bounds_are_validated():
    with pytest.raises(ValidationError):
        DuckDuckGoSearchTool(name="ddg", max_results=100)
    with pytest.raises(ValidationError):
        DuckDuckGoSearchTool(name="ddg", timeout=0)


def test_component_yaml_matches_runtime_contract():
    config_path = (
        Path(__file__).parents[6]
        / "agentuniverse"
        / "agent"
        / "action"
        / "tool"
        / "common_tool"
        / "duckduckgo_search_tool.yaml"
    )
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    assert config["metadata"]["class"] == "DuckDuckGoSearchTool"
    assert config["input_keys"] == ["input"]
    schema = config["args_model_schema"]
    assert schema["required"] == ["input"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]["search_type"]["enum"]) == {"text", "news"}
