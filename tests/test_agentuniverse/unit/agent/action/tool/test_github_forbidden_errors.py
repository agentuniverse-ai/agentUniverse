"""GitHub permission failures and actual rate limiting need distinct errors."""
import json

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool


@pytest.fixture
def invoke(monkeypatch):
    def run(mode, status, message, headers=None):
        sent = []

        def send(self, request, **kwargs):
            sent.append(request)
            response = requests.Response()
            response.status_code = status
            response.headers.update({'Content-Type': 'application/json', **(headers or {})})
            response._content = json.dumps({'message': message}).encode()
            response.request = request
            response.url = request.url
            return response

        # Exercise Requests' native HTTPError attachment and response decoding.
        monkeypatch.setattr(requests.Session, 'send', send)
        result = GitHubTool(api_key=None).execute(mode=mode, query='agent', owner='owner', repo='repo')
        assert len(sent) == 1
        return result[0] if isinstance(result, list) else result
    return run


@pytest.mark.parametrize('mode', ['repository', 'repo_info'])
@pytest.mark.parametrize('message', [
    'Resource not accessible by integration',
    'Resource not accessible by personal access token',
    'Resource protected by organization SAML enforcement.',
])
def test_forbidden_keeps_permission_error(invoke, mode, message):
    result = invoke(mode, 403, message, {'x-ratelimit-remaining': '4999'})
    assert 'HTTP Error 403' in result['error']
    assert message in result['error']
    assert 'API rate limit exceeded' not in result['error']


@pytest.mark.parametrize('mode', ['repository', 'repo_info'])
@pytest.mark.parametrize('message, headers', [
    ('API rate limit exceeded', {'x-ratelimit-remaining': '0'}),
    ('Please wait before retrying.', {'retry-after': '60', 'x-ratelimit-remaining': '4999'}),
    ('You have exceeded a secondary rate limit.', {'x-ratelimit-remaining': '4999'}),
])
def test_real_rate_limit_keeps_existing_error(invoke, mode, message, headers):
    result = invoke(mode, 403, message, headers)
    assert result == {'error': 'API rate limit exceeded. Please check your API key or try again later.'}


@pytest.mark.parametrize('status, expected', [(404, 'Resource not found.'), (500, 'HTTP Error 500')])
def test_other_http_errors_remain_available(invoke, status, expected):
    result = invoke('repository', status, 'Service failure')
    assert expected in result['error']


@pytest.mark.parametrize('body', [b'<h1>Forbidden</h1>', b'[]', b''])
def test_nonstandard_forbidden_body_retains_http_error(monkeypatch, body):
    def send(self, request, **kwargs):
        response = requests.Response()
        response.status_code = 403
        response._content = body
        response.request = request
        response.url = request.url
        return response

    monkeypatch.setattr(requests.Session, 'send', send)
    result = GitHubTool(api_key=None).execute(mode='repo_info', owner='owner', repo='repo')
    assert result['error'] == 'HTTP Error 403: ' + body.decode()
