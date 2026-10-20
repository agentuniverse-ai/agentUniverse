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
