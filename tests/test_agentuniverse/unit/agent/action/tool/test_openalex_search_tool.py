#!/usr/bin/env python3

"""Offline contracts for OpenAlex search and real component registration."""

import asyncio
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.openalex_search_tool import OpenAlexSearchTool
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


@pytest.fixture(autouse=True)
def http_get(monkeypatch):
    """Keep credentials and all HTTP responses independent of the host machine."""
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    response = Mock(status_code=200)
    response.json.return_value = {"meta": {"count": 0}, "results": []}
    get = Mock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    return get


@pytest.fixture
def tool():
    return OpenAlexSearchTool()


@pytest.fixture
def work():
    return {
        "id": "https://openalex.org/W123",
        "doi": "https://doi.org/10.1234/example",
        "display_name": "An example research article",
        "publication_year": 2024,
        "publication_date": "2024-02-29",
        "type": "article",
        "language": "en",
        "cited_by_count": 12,
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A123",
                    "display_name": "A. Researcher",
                    "orcid": "https://orcid.org/0000-0000-0000-0001",
                }
            }
        ],
        "primary_location": {"source": {"display_name": "Example Journal"}},
        "open_access": {"is_oa": True, "oa_url": "https://example.org/article"},
        "best_oa_location": {"pdf_url": "https://example.org/article.pdf"},
        "abstract_inverted_index": {"retrieval": [2], "We": [0], "study": [1, 3]},
    }


def test_search_normalizes_metadata_and_preserves_remote_order(tool, http_get, work):
    other = {"id": "https://openalex.org/W456", "display_name": "Second"}
    http_get.return_value.json.return_value = {
        "meta": {"count": 12},
        "results": [work, other],
    }
    original = deepcopy(work)
    result = tool.execute("  retrieval  ", max_results=2)
    assert result["query"] == "retrieval"
    assert result["total_results"] == 12
    assert result["returned_results"] == 2
    assert result["next_page"] == 2
    assert [item["id"] for item in result["works"]] == [work["id"], other["id"]]
    item = result["works"][0]
    assert item["doi"] == work["doi"]
    assert item["title"] == work["display_name"]
    assert item["abstract"] == "We study retrieval study"
    assert item["abstract_truncated"] is False
    assert item["authors"][0]["name"] == "A. Researcher"
    assert item["authors_truncated"] is False
    assert item["venue"] == "Example Journal"
    assert item["publication_year"] == 2024
    assert item["cited_by_count"] == 12
    assert item["is_open_access"] is True
    assert item["open_access_url"] == "https://example.org/article"
    assert item["pdf_url"] == "https://example.org/article.pdf"
    assert work == original
    http_get.assert_called_once()


def test_request_maps_filters_pagination_and_server_sorting(tool, http_get):
    tool.execute(
        '"machine learning" AND medicine',
        max_results=20,
        page=3,
        sort="cited_by_count",
        order="asc",
        open_access_only=True,
        from_publication_date="2020-01-01",
        to_publication_date="2024-02-29",
    )
    args, kwargs = http_get.call_args
    assert args == ("https://api.openalex.org/works",)
    assert kwargs["params"] == {
        "search": '"machine learning" AND medicine',
        "per_page": 20,
        "page": 3,
        "sort": "cited_by_count:asc",
        "select": OpenAlexSearchTool.WORK_FIELDS,
        "filter": "from_publication_date:2020-01-01,to_publication_date:2024-02-29,is_oa:true",
    }
    assert kwargs["timeout"] == 15.0
    assert kwargs["allow_redirects"] is False
    assert "Authorization" not in kwargs["headers"]


@pytest.mark.parametrize("field", ["from_publication_date", "to_publication_date"])
def test_one_sided_date_filters(tool, http_get, field):
    tool.execute("test", **{field: "2024-01-01"})
    assert http_get.call_args.kwargs["params"]["filter"] == f"{field}:2024-01-01"


def test_default_request_has_no_filters(tool, http_get):
    result = tool.execute("test")
    assert "filter" not in http_get.call_args.kwargs["params"]
    assert result["total_results"] == 0
    assert result["returned_results"] == 0
    assert result["next_page"] is None
    assert result["works"] == []
    assert "error" not in result


@pytest.mark.parametrize("page,total,expected", [(1, 5, None), (1, 6, 2), (2000, 12000, None)])
def test_next_page_respects_result_count_and_basic_paging_limit(tool, http_get, page, total, expected):
    http_get.return_value.json.return_value = {
        "meta": {"count": total},
        "results": [{"id": f"https://openalex.org/W{i}"} for i in range(5)],
    }
    assert tool.execute("test", page=page)["next_page"] == expected


def test_null_optional_metadata_is_normalized(tool, http_get):
    http_get.return_value.json.return_value = {
        "meta": {"count": 1},
        "results": [
            {
                "id": "https://openalex.org/W1",
                "doi": None,
                "display_name": None,
                "authorships": None,
                "abstract_inverted_index": None,
                "primary_location": {"source": None},
                "open_access": None,
                "best_oa_location": None,
            }
        ],
    }
    result = tool.execute("test")["works"][0]
    for field in ("doi", "title", "abstract", "venue", "open_access_url", "pdf_url"):
        assert result[field] == ""
    for field in ("publication_year", "cited_by_count", "is_open_access"):
        assert result[field] is None
    assert result["authors"] == []


def test_abstract_and_authors_are_bounded(tool, http_get, work):
    work["abstract_inverted_index"] = {"word": list(range(1100)), "remote": [10**12]}
    work["authorships"] *= 21
    http_get.return_value.json.return_value = {"meta": {"count": 1}, "results": [work]}
    result = tool.execute("test")["works"][0]
    assert len(result["abstract"]) == 4000
    assert result["abstract_truncated"] is True
    assert "remote" not in result["abstract"]
    assert len(result["authors"]) == 20
    assert result["authors_truncated"] is True


def test_sparse_abstract_positions_do_not_add_padding():
    assert OpenAlexSearchTool._abstract({"last": [5], "first": [0]}) == ("first last", False)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"query": ""},
        {"query": " \n "},
        {"query": None},
        {"query": 1},
        {"max_results": 0},
        {"max_results": 21},
        {"max_results": True},
        {"max_results": 1.5},
        {"max_results": "5"},
        {"page": 0},
        {"page": True},
        {"page": 1.5},
        {"page": "2"},
        {"page": 2001},
        {"max_results": 20, "page": 501},
        {"sort": "invalid"},
        {"sort": ["relevance_score"]},
        {"sort": None},
        {"order": "invalid"},
        {"order": None},
        {"open_access_only": "false"},
        {"open_access_only": 1},
        {"from_publication_date": "2023-02-29"},
        {"from_publication_date": "2024"},
        {"from_publication_date": "2024-1-01"},
        {"from_publication_date": ""},
        {"to_publication_date": 2024},
        {"to_publication_date": "2024-01-32"},
        {"from_publication_date": "2025-01-01", "to_publication_date": "2024-01-01"},
        {"query": "x" * 4000},
        {"query": "\u4e2d" * 500},
    ],
)
def test_invalid_inputs_fail_before_http(tool, http_get, kwargs):
    with pytest.raises(ValueError):
        tool.execute(**{"query": "test", **kwargs})
    http_get.assert_not_called()


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), "15", True])
def test_invalid_timeout_from_yaml_assignment_fails_before_http(tool, http_get, timeout):
    tool.timeout = timeout
    with pytest.raises(ValueError, match="timeout"):
        tool.execute("test")
    http_get.assert_not_called()


def test_key_uses_header_and_is_excluded_from_model_serialization(http_get, monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "environment-secret")
    tool = OpenAlexSearchTool()
    tool.execute("test")
    assert http_get.call_args.kwargs["headers"]["Authorization"] == "Bearer environment-secret"
    assert "api_key" not in http_get.call_args.kwargs["params"]
    assert "environment-secret" not in repr(tool)
    assert "environment-secret" not in tool.model_dump_json()
    OpenAlexSearchTool(api_key="explicit-secret").execute("test")
    assert http_get.call_args.kwargs["headers"]["Authorization"] == "Bearer explicit-secret"


@pytest.mark.parametrize(
    "error,error_type",
    [
        (requests.Timeout("secret"), "request_timeout"),
        (requests.ConnectionError("secret"), "request_error"),
        (requests.RequestException("secret"), "request_error"),
    ],
)
def test_network_failures_preserve_context_without_leaking_credentials(tool, http_get, error, error_type):
    tool.api_key = "secret"
    http_get.side_effect = error
    result = tool.execute("test", page=2, open_access_only=True)
    assert result["error"]["type"] == error_type
    assert result["page"] == 2
    assert result["open_access_only"] is True
    assert result["total_results"] is None
    assert result["returned_results"] == 0
    assert result["works"] == []
    assert "secret" not in str(result)
    http_get.assert_called_once()


@pytest.mark.parametrize("status", [301, 302, 400, 401, 403, 429, 500, 503])
def test_http_errors_are_actionable_and_do_not_echo_bodies(tool, http_get, status):
    http_get.return_value.status_code = status
    http_get.return_value.text = "secret"
    result = tool.execute("test")
    assert result["error"]["type"] == "http_error"
    assert result["error"]["status_code"] == status
    if status == 429:
        assert "retry later" in result["error"]["message"]
    if status in (401, 403):
        assert "OPENALEX_API_KEY" in result["error"]["message"]
    assert "secret" not in str(result)
    http_get.return_value.json.assert_not_called()
    http_get.assert_called_once()


def test_api_error_body_is_not_exposed(tool, http_get):
    http_get.return_value.json.return_value = {"error": "secret", "message": "secret"}
    result = tool.execute("test")
    assert result["error"]["type"] == "api_error"
    assert "secret" not in str(result)


def test_requests_json_decode_error_is_an_invalid_response(tool, http_get):
    http_get.return_value.json.side_effect = requests.exceptions.JSONDecodeError("secret", "secret", 0)
    result = tool.execute("test")
    assert result["error"]["type"] == "invalid_response"
    assert "secret" not in str(result)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"results": []},
        {"meta": {"count": 0}},
        {"meta": {"count": "1"}, "results": []},
        {"meta": {"count": True}, "results": []},
        {"meta": {"count": -1}, "results": []},
        {"meta": {"count": 1}, "results": [None]},
        {"meta": {"count": 1}, "results": [{}]},
        {"meta": {"count": 1}, "results": [{"id": "W1", "primary_location": []}]},
        {"meta": {"count": 1}, "results": [{"id": "W1", "authorships": {}}]},
        {"meta": {"count": 1}, "results": [{"id": "W1", "display_name": 5}]},
        {"meta": {"count": 6}, "results": [{"id": "W1"}] * 6},
    ],
)
def test_malformed_payloads_return_structured_errors(tool, http_get, payload):
    http_get.return_value.json.return_value = payload
    assert tool.execute("test")["error"]["type"] == "invalid_response"


@pytest.mark.parametrize("index", [[], {"word": "0"}, {"word": [-1]}, {"word": [True]}, {"word": ["0"]}])
def test_invalid_abstract_indexes_return_structured_errors(tool, http_get, index):
    http_get.return_value.json.return_value = {
        "meta": {"count": 1},
        "results": [{"id": "W1", "abstract_inverted_index": index}],
    }
    assert tool.execute("test")["error"]["type"] == "invalid_response"


@pytest.mark.parametrize(
    "fields",
    [
        {"publication_year": "2024"},
        {"publication_year": True},
        {"cited_by_count": -1},
        {"cited_by_count": {}},
        {"open_access": {"is_oa": "true"}},
        {"authorships": ["invalid"]},
    ],
)
def test_invalid_optional_metadata_types_are_rejected(tool, http_get, fields):
    http_get.return_value.json.return_value = {
        "meta": {"count": 1},
        "results": [{"id": "W1", **fields}],
    }
    assert tool.execute("test")["error"]["type"] == "invalid_response"


def test_example_yaml_loads_registers_and_runs_sync_and_async(http_get, monkeypatch):
    root = Path(__file__).resolve().parents[6]
    path = root / "examples/sample_standard_app/intelligence/agentic/tool/buildin/openalex_search_tool.yaml"
    configer = Configer(str(path)).load()
    tool_configer = ToolConfiger().load_by_configer(configer)
    assert tool_configer.get_component_config_type() == ComponentEnum.TOOL.value
    manager = ApplicationConfigManager()
    try:
        previous = manager.app_configer
    except ValueError:
        previous = None
    app = AppConfiger()
    app.tool_configer_map = {tool_configer.name: tool_configer}
    monkeypatch.setattr(ToolManager(), "_instance_obj_map", {})
    try:
        manager.app_configer = app
        tool = ToolManager().get_instance_obj("openalex_search_tool")
        assert isinstance(tool, OpenAlexSearchTool)
        assert tool.tool_type is ToolTypeEnum.API
        assert tool.input_keys == ["query"]
        assert tool.timeout == 15.0
        assert not tool.check_execute_signature_deprecated()
        assert tool.run(query="test")["works"] == []
        assert asyncio.run(tool.async_run(query="test"))["works"] == []
        assert http_get.call_count == 2
    finally:
        manager.app_configer = previous
