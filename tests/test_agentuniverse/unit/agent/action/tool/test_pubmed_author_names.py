"""Preserve optional NLM author name parts through the public PubMed search."""

import json

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool


@pytest.mark.parametrize("author,expected", [
    ("<LastName>Smith</LastName><Initials>DJ</Initials>", "DJ Smith"),
    ("<LastName>Smith</LastName><ForeName>David J</ForeName><Suffix>Jr</Suffix>", "David J Smith Jr"),
    ("<LastName>Smith</LastName><Initials>DJ</Initials><Suffix>IV</Suffix>", "DJ Smith IV"),
    ("<LastName>Smith</LastName><ForeName>David J</ForeName><Initials>DJ</Initials>", "David J Smith"),
    ("<CollectiveName>Study Group</CollectiveName>", "Study Group"),
    ("<LastName>Smith</LastName>", "Smith"),
])
def test_pubmed_preserves_author_name_parts(monkeypatch, author, expected):
    """ForeName takes precedence; initials and suffixes must not be discarded."""
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        response = requests.Response()
        response.status_code = 200
        if url.endswith("esearch.fcgi"):
            response._content = json.dumps({"esearchresult": {"count": "1", "idlist": ["123"]}}).encode()
        else:
            assert url.endswith("efetch.fcgi")
            response._content = (
                "<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article>"
                "<ArticleTitle>Example citation</ArticleTitle><AuthorList><Author>" + author
                + "</Author><Author><CollectiveName>Other Group</CollectiveName></Author></AuthorList>"
                "</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"
            ).encode()
        return response

    monkeypatch.setattr(requests, "get", get)
    result = PubMedTool(api_key=None, email=None).execute("example")
    assert "error" not in result
    assert result["papers"][0]["authors"] == [expected, "Other Group"]
    assert result["papers"][0]["title"] == "Example citation"
    assert result["returned_results"] == 1
    assert len(calls) == 2
