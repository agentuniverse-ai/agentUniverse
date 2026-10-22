"""DOI resolver URLs are decoded once before constructing Scholar requests."""
from unittest.mock import Mock
from urllib.parse import quote

import pytest

from agentuniverse.agent.action.tool.common_tool import semantic_scholar_tool as module


@pytest.mark.parametrize("mode", ["paper", "citations", "references"])
@pytest.mark.parametrize("source,identifier", [
    ("https://doi.org/10.1000/res%23test", "10.1000/res#test"),
    ("http://dx.doi.org/10.1000/a%2523b", "10.1000/a%23b"),
    ("HTTPS://DOI.ORG/10.1000/a%2Bb+c", "10.1000/a+b+c"),
    ("https://doi.org/10.1000/caf%C3%A9", "10.1000/café"),
    ("10.1000/a%23b", "10.1000/a%23b"),
    ("doi:10.1000/a%23b", "10.1000/a%23b"),
    ("https://doi.org/10.1000/a%23b.pdf", "10.1000/a#b.pdf"),
    ("https://doi.org/10.1000/a%2Epdf", "10.1000/a.pdf"),
    ("http://dx.doi.org/10.1000/a%252Epdf", "10.1000/a%2Epdf"),
    ("HTTPS://DOI.ORG/10.1000/a.PDF", "10.1000/a.PDF"),
    ("10.1000/a.pdf", "10.1000/a.pdf"),
    ("DOI:10.1000/a%2Epdf", "10.1000/a%2Epdf"),
])
def test_encoded_doi_request_paths(monkeypatch, mode, source, identifier):
    response = Mock()
    response.json.return_value = {"paperId": "abc"} if mode == "paper" else {"data": []}
    get = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "get", get)
    output = module.SemanticScholarTool().execute(query=source, mode=mode)
    expected = "DOI:" + identifier
    suffix = "" if mode == "paper" else "/" + mode
    assert get.call_args.args[0] == "https://api.semanticscholar.org/graph/v1/paper/" + quote(expected, safe="") + suffix
    assert output["query"] == expected


def test_batch_decodes_urls_but_preserves_raw_identifier(monkeypatch):
    response = Mock()
    response.json.return_value = [None, None]
    post = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "post", post)
    output = module.SemanticScholarTool().execute(
        query=["https://doi.org/10.1000/res%23test", "DOI:10.1000/res%23test"],
        mode="batch",
    )
    expected = ["DOI:10.1000/res#test", "DOI:10.1000/res%23test"]
    assert post.call_args.kwargs["json"] == {"ids": expected}
    assert output["query"] == expected
    assert output["not_found_ids"] == expected


@pytest.mark.parametrize("source,expected", [
    ("https://arxiv.org/pdf/2401.12345.pdf", "ARXIV:2401.12345"),
    ("HTTP://ARXIV.ORG/pdf/hep-th/9901001.PDF", "ARXIV:hep-th/9901001"),
    ("https://arxiv.org/abs/2401.12345.pdf", "ARXIV:2401.12345.pdf"),
    ("ARXIV:2401.12345.pdf", "ARXIV:2401.12345.pdf"),
    ("URL:https://example.org/paper.pdf", "URL:https://example.org/paper.pdf"),
])
def test_only_arxiv_pdf_urls_strip_pdf_suffix(source, expected):
    assert module.SemanticScholarTool._normalize_paper_id(source) == expected


def test_batch_preserves_doi_pdf_suffix_and_normalizes_arxiv(monkeypatch):
    response = Mock()
    response.json.return_value = [None] * 4
    post = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "post", post)
    output = module.SemanticScholarTool().execute(
        query=[
            "https://doi.org/10.1000/a%2Epdf",
            "http://dx.doi.org/10.1000/a%252Epdf",
            "DOI:10.1000/raw.pdf",
            "https://arxiv.org/pdf/2401.12345.pdf",
        ],
        mode="batch",
    )
    expected = ["DOI:10.1000/a.pdf", "DOI:10.1000/a%2Epdf", "DOI:10.1000/raw.pdf", "ARXIV:2401.12345"]
    assert post.call_args.args[0] == "https://api.semanticscholar.org/graph/v1/paper/batch"
    assert post.call_args.kwargs["json"] == {"ids": expected}
    assert output["query"] == expected
