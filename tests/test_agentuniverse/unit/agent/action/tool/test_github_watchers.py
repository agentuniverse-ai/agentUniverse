"""GitHub repository watchers are subscribers, not stargazers."""

import json
from unittest.mock import patch

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool


@pytest.mark.parametrize("subscribers", [0, 7, 150])
def test_repository_info_separates_watchers_from_stars(subscribers):
    """Map the documented repository fields through the public execute path."""
    data = {
        "name": "sample", "full_name": "example/sample", "description": "Sample",
        "html_url": "https://github.com/example/sample", "stargazers_count": 100,
        "watchers_count": 100, "subscribers_count": subscribers, "forks_count": 4,
        "language": "Python", "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z", "pushed_at": "2024-01-02T00:00:00Z",
        "size": 12, "open_issues_count": 2, "license": None, "topics": [],
        "owner": {"login": "example", "avatar_url": "", "html_url": "https://github.com/example"},
    }
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(data).encode()
    tool = GitHubTool(api_key=None)
    with patch("agentuniverse.agent.action.tool.common_tool.github_tool.requests.get", return_value=response) as get:
        result = tool.execute(mode="repo_info", owner="example", repo="sample")
    assert result["watchers"] == subscribers
    assert result["stars"] == 100
    assert result["forks"] == 4
    assert result["full_name"] == "example/sample"
    get.assert_called_once()
    assert get.call_args.args == ("https://api.github.com/repos/example/sample",)
