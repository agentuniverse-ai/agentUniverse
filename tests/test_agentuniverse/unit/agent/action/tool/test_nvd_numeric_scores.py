"""Malformed upstream CVSS numbers must not escape or break JSON output."""
import json
import math

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.nvd_cve_tool import NvdCveTool


@pytest.mark.parametrize('field', ['baseScore', 'exploitabilityScore', 'impactScore'])
@pytest.mark.parametrize('raw_value,expected', [
    (10 ** 400, 0.0),
    ('1e400', 0.0),
    (float('inf'), 0.0),
    (float('-inf'), 0.0),
    (float('nan'), 0.0),
    ('NaN', 0.0),
    (None, 0.0),
    (True, 0.0),
    ('invalid', 0.0),
    (0, 0.0),
    (7.5, 7.5),
    ('3.9', 3.9),
])
def test_scores_are_finite_through_public_execute(monkeypatch, field, raw_value, expected):
    metric = {'type': 'Primary', 'source': 'test',
              'cvssData': {'version': '3.1', 'baseScore': 9.8},
              'exploitabilityScore': 3.9, 'impactScore': 5.9}
    if field == 'baseScore':
        metric['cvssData'][field] = raw_value
    else:
        metric[field] = raw_value
    payload = {'totalResults': 1, 'startIndex': 0, 'resultsPerPage': 1,
               'vulnerabilities': [{'cve': {'id': 'CVE-2021-44228',
                   'metrics': {'cvssMetricV31': [metric]}}}]}
    requests_seen = []

    def send(session, request, **kwargs):
        requests_seen.append(request)
        response = requests.Response()
        response.request = request
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps(payload).encode()
        return response

    monkeypatch.setattr(requests.Session, 'send', send)
    result = NvdCveTool(api_key=None).execute('CVE-2021-44228')
    assert len(requests_seen) == 1
    assert 'error' not in result
    key = {'baseScore': 'base_score', 'exploitabilityScore': 'exploitability_score',
           'impactScore': 'impact_score'}[field]
    scores = result['cves'][0]['cvss']
    assert math.isfinite(scores[key])
    assert scores[key] == expected
    json.dumps(result, allow_nan=False)
