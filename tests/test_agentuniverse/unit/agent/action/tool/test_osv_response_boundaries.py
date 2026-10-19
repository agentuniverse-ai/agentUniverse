"""Keep valid OSV advisories despite individual malformed reference URLs."""

from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool import osv_vulnerability_tool as module


@pytest.mark.parametrize("url", ["https://[", "http://[invalid]/reference", "https://example.com\uff0f@evil.test"])
def test_invalid_reference_does_not_discard_entire_advisory(monkeypatch, url):
    response = Mock()
    response.json.return_value = {
        "id": "TEST-1",
        "references": [{"type": "WEB", "url": url}, {"type": "ADVISORY", "url": "https://example.com/advisory"}],
    }
    request = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "get", request)
    result = module.OsvVulnerabilityTool().execute("TEST-1", mode="vulnerability")
    assert "error" not in result
    advisory = result["vulnerabilities"][0]
    assert advisory["references"] == [{"type": "ADVISORY", "url": "https://example.com/advisory"}]
    assert advisory["reference_count"] == 2
    assert advisory["references_truncated"] is True
    request.assert_called_once()


def test_nested_range_and_event_limits_preserve_truncation_metadata():
    tool = module.OsvVulnerabilityTool
    events = [{"fixed": str(index)} for index in range(tool.MAX_EVENTS + 1)]
    ranges = [{"type": "ECOSYSTEM", "events": events} for _ in range(tool.MAX_RANGES + 1)]
    affected = [{"package": {"name": "demo"}, "ranges": ranges} for _ in range(tool.MAX_AFFECTED + 1)]
    result = tool._parse_vulnerability({"id": "TEST-1", "affected": affected})
    assert len(result["affected"]) == tool.MAX_AFFECTED
    assert result["affected_truncated"]
    for package in result["affected"]:
        assert len(package["ranges"]) == tool.MAX_RANGES
        assert package["ranges_truncated"]
        for item in package["ranges"]:
            assert len(item["events"]) == tool.MAX_EVENTS
            assert item["event_count"] == tool.MAX_EVENTS + 1
            assert item["events_truncated"]
    assert len(result["fixed_versions"]) <= tool.MAX_IDENTIFIERS
