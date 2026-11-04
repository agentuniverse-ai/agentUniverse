"""Defensive boundaries for unexpected OpenAlex responses."""

from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool import openalex_tool as module


@pytest.mark.parametrize("maximum", [1, 5, 20])
def test_service_overdelivery_does_not_expand_agent_context(monkeypatch, maximum):
    records = [{"id": f"https://openalex.org/W{i}"} for i in range(25)]
    response = Mock()
    response.json.return_value = {"meta": {"count": 100, "next_cursor": "next"}, "results": records}
    request = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "get", request)
    result = module.OpenAlexTool(api_key=None, email=None).execute("query", max_results=maximum, cursor="*")
    assert result["returned_results"] == maximum
    assert result["results_truncated"] is True
    assert len(result["works"]) == maximum
    assert result["total_results"] == 100
    assert result["next_cursor"] == "next"
    request.assert_called_once()


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan"), {}, "invalid"])
def test_nonfinite_or_invalid_counts_do_not_escape_structured_response(monkeypatch, value):
    response = Mock()
    response.json.return_value = {"meta": {"count": value}, "results": [{"cited_by_count": value}]}
    monkeypatch.setattr(module.requests, "get", Mock(return_value=response))
    result = module.OpenAlexTool(api_key=None, email=None).execute("query")
    assert "error" not in result
    assert result["total_results"] == result["works"][0]["citation_count"] == 0


@pytest.mark.parametrize("date_value", ["2024-02", "2023-02"])
def test_partial_date_upper_bound_respects_leap_year(monkeypatch, date_value):
    response = Mock()
    response.json.return_value = {"meta": {"count": 0}, "results": []}
    request = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "get", request)
    result = module.OpenAlexTool(api_key=None, email=None).execute("query", to_publication_date=date_value)
    expected = date_value + ("-29" if date_value.startswith("2024") else "-28")
    assert result["to_publication_date"] == expected
    assert request.call_args.kwargs["params"]["filter"] == f"to_publication_date:{expected}"
