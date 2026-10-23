"""Keep score validation inside the structured response-error contract."""
import json

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool import OpenSsfScorecardTool


def execute_response(monkeypatch, field, score):
    payload = {
        'repo': {'name': 'github.com/owner/repo'},
        'scorecard': {'version': 'v5.0.0'},
        'score': 8,
        'checks': [{'name': 'Maintained', 'score': 10}],
    }
    if field == 'overall':
        payload['score'] = score
    else:
        payload['checks'][0]['score'] = score

    def send(self, request, **kwargs):
        assert request.url == 'https://api.securityscorecards.dev/projects/github.com/owner/repo'
        response = requests.Response()
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps(payload).encode('utf-8')
        response.request = request
        return response

    # Preserve Requests' native request preparation and JSON decoding.
    monkeypatch.setattr(requests.Session, 'send', send)
    return OpenSsfScorecardTool().execute('owner/repo')


@pytest.mark.parametrize('field', ['overall', 'check'])
@pytest.mark.parametrize('sign', [-1, 1])
def test_huge_json_integer_is_reported_as_invalid_response(monkeypatch, field, sign):
    result = execute_response(monkeypatch, field, sign * 10**400)
    assert result['error']['type'] == 'invalid_response'
    assert 'must be between' in result['error']['message']
    assert result['repository'] == 'owner/repo'
    assert result['scorecard_result'] == {}


@pytest.mark.parametrize('field, score', [
    ('overall', 0), ('overall', 10), ('overall', 8.5),
    ('check', -1), ('check', 0), ('check', 10),
])
def test_valid_score_boundaries_are_preserved(monkeypatch, field, score):
    result = execute_response(monkeypatch, field, score)
    assert 'error' not in result
    parsed = result['scorecard_result']
    actual = parsed['score'] if field == 'overall' else parsed['checks'][0]['score']
    assert actual == score
    assert type(actual) is type(score)


@pytest.mark.parametrize('field, score', [('overall', -1), ('check', 11)])
def test_ordinary_out_of_range_scores_remain_invalid(monkeypatch, field, score):
    result = execute_response(monkeypatch, field, score)
    assert result['error']['type'] == 'invalid_response'
