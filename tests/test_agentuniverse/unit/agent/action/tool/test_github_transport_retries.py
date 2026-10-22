"""Transient transport failures must reach the GitHub request retry policy."""
from unittest.mock import MagicMock, patch

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool

MODULE = 'agentuniverse.agent.action.tool.common_tool.github_tool'


@pytest.mark.parametrize('method', [
    'search_repositories', 'search_users', 'search_issues', 'search_code',
])
@pytest.mark.parametrize('failure', [requests.Timeout, requests.ConnectionError])
def test_search_recovers_from_transient_transport_failure(method, failure):
    response = MagicMock()
    response.json.return_value = {'items': []}
    tool = GitHubTool(api_key=None)
    with patch(f'{MODULE}.requests.get', side_effect=[failure('temporary'), response]) as get, \
            patch(f'{MODULE}.time.sleep') as sleep:
        result = getattr(tool, method)('agentUniverse')

    assert result == []
    assert get.call_count == 2
    assert get.call_args_list[0] == get.call_args_list[1]
    sleep.assert_called_once_with(1.0)


@pytest.mark.parametrize('failure,expected', [
    (requests.Timeout, 'Request timeout. Please try again.'),
    (requests.ConnectionError, 'Request failed: offline'),
])
def test_exhausted_transport_retries_keep_structured_error(failure, expected):
    with patch(f'{MODULE}.requests.get', side_effect=failure('offline')) as get, \
            patch(f'{MODULE}.time.sleep') as sleep:
        result = GitHubTool(api_key=None).search_repositories('agentUniverse')

    assert result == [{'error': expected}]
    assert get.call_count == 3
    assert sleep.call_count == 2


@pytest.mark.parametrize('status', [403, 404, 500])
def test_http_errors_are_returned_without_transport_retries(status):
    response = requests.Response()
    response.status_code = status
    response.url = 'https://api.github.com/search/repositories'
    with patch(f'{MODULE}.requests.get', return_value=response) as get, \
            patch(f'{MODULE}.time.sleep') as sleep:
        result = GitHubTool(api_key=None).search_repositories('agentUniverse')

    assert 'error' in result[0]
    get.assert_called_once()
    sleep.assert_not_called()
