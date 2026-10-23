"""DOI resolver URL components must not become part of the work identifier."""
import json
from urllib.parse import quote

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.crossref_tool import CrossrefTool


@pytest.mark.parametrize('query, expected_doi', [
    ('https://doi.org/10.1000/example', '10.1000/example'),
    ('https://doi.org/10.1000/example?utm_source=share', '10.1000/example'),
    ('https://doi.org/10.1000/example#references', '10.1000/example'),
    ('https://doi.org/10.1000/example?utm_source=share#references', '10.1000/example'),
    ('http://dx.doi.org/10.1000/example?x=1#bookmark', '10.1000/example'),
    ('https://doi.org/10.1000/a%3Fb%23c?track=1#bookmark', '10.1000/a?b#c'),
    ('https://doi.org/10.1000/a%2523b?track=1', '10.1000/a%23b'),
    ('https://doi.org/10.1000/a%3Fb%23c', '10.1000/a?b#c'),
    ('10.1000/a?b#c', '10.1000/a?b#c'),
    ('doi:10.1000/a?b#c', '10.1000/a?b#c'),
])
def test_lookup_uses_doi_path_without_url_query_or_fragment(monkeypatch, query, expected_doi):
    sent = []

    def send(self, request, **kwargs):
        sent.append(request)
        response = requests.Response()
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps({
            'status': 'ok', 'message-type': 'work',
            'message': {'DOI': expected_doi, 'title': ['Offline paper']},
        }).encode()
        response.request = request
        return response

    # Retain Requests' actual preparation/encoding and native response decoding.
    monkeypatch.setattr(requests.Session, 'send', send)
    result = CrossrefTool(email=None).execute(query=query, mode='doi')
    assert result['query'] == expected_doi
    assert len(sent) == 1
    assert sent[0].url == 'https://api.crossref.org/v1/works/' + quote(expected_doi, safe='')
    assert result['works'][0]['doi'] == expected_doi
