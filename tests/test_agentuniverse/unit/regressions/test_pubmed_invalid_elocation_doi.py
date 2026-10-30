"""Respect PubMed's explicit invalid-value flag on fallback DOIs."""
import json

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool

INVALID = '<ELocationID EIdType="doi" ValidYN="N">10.1000/wrong</ELocationID>'
VALID = '<ELocationID EIdType="doi" ValidYN="Y">10.1000/correct</ELocationID>'
DEFAULT = '<ELocationID EIdType="doi">10.1000/correct</ELocationID>'


@pytest.mark.parametrize('locations,primary,expected', [
    (INVALID, '', ''),
    (INVALID + VALID, '', '10.1000/correct'),
    (INVALID + DEFAULT, '', '10.1000/correct'),
    (VALID + INVALID, '', '10.1000/correct'),
    (DEFAULT, '', '10.1000/correct'),
    ('<ELocationID EIdType="pii">publisher-id</ELocationID>' + INVALID, '', ''),
    (INVALID + INVALID, '', ''),
    (INVALID, '10.1000/primary', '10.1000/primary'),
    ('<ELocationID EIdType="doi" ValidYN="Y"> </ELocationID>' + DEFAULT, '', '10.1000/correct'),
])
def test_public_search_ignores_invalid_location_dois(monkeypatch, locations, primary, expected):
    calls = []
    xml = f'''<PubmedArticleSet><PubmedArticle><MedlineCitation>
      <PMID>123</PMID><Article><ArticleTitle>Example title</ArticleTitle>{locations}</Article>
      </MedlineCitation><PubmedData><ArticleIdList>
      <ArticleId IdType="doi">{primary}</ArticleId></ArticleIdList></PubmedData>
      </PubmedArticle></PubmedArticleSet>'''

    def send(self, request, **kwargs):
        calls.append(request)
        response = requests.Response()
        response.status_code = 200
        response.request = request
        if '/esearch.fcgi' in request.url:
            response._content = json.dumps({'esearchresult': {'count': '1', 'idlist': ['123']}}).encode()
            response.headers['Content-Type'] = 'application/json'
        else:
            assert '/efetch.fcgi' in request.url
            response._content = xml.encode()
            response.headers['Content-Type'] = 'application/xml'
        return response

    monkeypatch.setattr(requests.Session, 'send', send)
    result = PubMedTool().execute(query='metadata')
    assert 'error' not in result
    assert result['returned_results'] == 1
    assert result['papers'][0]['doi'] == expected
    assert result['papers'][0]['title'] == 'Example title'
    assert result['papers'][0]['pmid'] == '123'
    assert len(calls) == 2
