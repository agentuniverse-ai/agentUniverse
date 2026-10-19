import pytest

from agentuniverse.agent.action.tool.common_tool.request_tool import RequestTool


@pytest.mark.parametrize("url", [None, "", "   ", "  ''  "])
def test_clean_url_rejects_empty_values(url):
    with pytest.raises(ValueError, match="url must be a non-empty string"):
        RequestTool._clean_url(url)


def test_clean_url_removes_whitespace_and_quotes():
    assert RequestTool._clean_url('  "https://example.com"  ') == "https://example.com"
