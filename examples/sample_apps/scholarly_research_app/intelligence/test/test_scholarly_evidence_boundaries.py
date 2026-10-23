"""Regression cases for identifier conflicts and malformed source URLs."""

from itertools import permutations
from unittest.mock import patch

import pytest

from scholarly_research_app.intelligence.agentic.tool.scholarly_evidence_tool import ScholarlyEvidenceTool


@pytest.mark.parametrize("identifier,values", [("doi", ("10.1000/first", "10.1000/second")), ("pmid", ("111", "222"))])
@pytest.mark.parametrize("order", list(permutations(range(3))))
def test_title_only_bridge_never_merges_conflicting_identifiers(identifier, values, order):
    raw = [{"title": "A deliberately identical scholarly title", identifier: value} for value in (*values, "")]
    records = [ScholarlyEvidenceTool._normalize_record("pubmed", raw[index]) for index in order]
    result = ScholarlyEvidenceTool._deduplicate(records)
    assert len(result) == 2
    assert {record["identifiers"][identifier] for record in result} == set(values)


@pytest.mark.parametrize("url", ["https://[", "http://[invalid]/paper", "https://example.com\uff0f@evil.test"])
def test_malformed_source_url_does_not_discard_successful_evidence(url):
    tool = ScholarlyEvidenceTool()
    sources = {
        "pubmed": {"papers": []},
        "crossref": {"works": [{"title": "Useful evidence from a source", "doi": "10.1000/test", "url": url}]},
        "semantic_scholar": {"papers": []},
    }
    with patch.object(tool, "_collect_sources", return_value=sources):
        result = tool.execute("evidence")
    assert result["returned_results"] == 1
    assert result["evidence"][0]["source_urls"]["crossref"] == "https://doi.org/10.1000/test"


def test_compatible_identifier_bridge_still_combines_provenance():
    raw = [
        ("pubmed", {"pmid": "111", "title": "First scholarly title"}),
        ("crossref", {"doi": "10.1000/test", "title": "Different scholarly title"}),
        ("semantic_scholar", {"doi": "10.1000/test", "pmid": "111", "title": "Third scholarly title"}),
    ]
    records = [ScholarlyEvidenceTool._normalize_record(source, record) for source, record in raw]
    result = ScholarlyEvidenceTool._deduplicate(records)
    assert len(result) == 1
    assert set(result[0]["sources"]) == {"pubmed", "crossref", "semantic_scholar"}
