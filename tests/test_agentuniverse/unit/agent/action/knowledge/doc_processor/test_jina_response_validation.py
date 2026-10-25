"""Malformed rerank rows must not select or mutate unrelated documents."""

import json
from copy import deepcopy
from unittest.mock import patch

import pytest
import requests

from agentuniverse.agent.action.knowledge.doc_processor.jina_reranker import (
    JinaReranker,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def run(payload, docs):
    """Parse an actual HTTP response body without calling a paid service."""
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode()
    with patch("requests.post", return_value=response):
        return JinaReranker(api_key="fixture").process_docs(docs, Query(query_str="q"))


@pytest.mark.parametrize(
    "row",
    [
        None,
        "bad",
        [],
        12,
        {},
        {"index": -1, "relevance_score": 0.9},
        {"index": 2, "relevance_score": 0.9},
        {"index": True, "relevance_score": 0.9},
        {"index": False, "relevance_score": 0.9},
        {"index": "0", "relevance_score": 0.9},
        {"index": 0.0, "relevance_score": 0.9},
        {"index": 0, "relevance_score": None},
        {"index": 0, "relevance_score": "high"},
        {"index": 0, "relevance_score": True},
        {"index": 0, "relevance_score": []},
        {"index": 0, "relevance_score": float("nan")},
        {"index": 0, "relevance_score": float("inf")},
        {"index": 0, "relevance_score": -float("inf")},
        {"index": 0, "relevance_score": 10**400},
    ],
)
@pytest.mark.parametrize("bad_first", [True, False])
def test_invalid_row_is_skipped_without_losing_valid_results(row, bad_first):
    docs = [Document(text="a", metadata={"source": "a"}), Document(text="b")]
    rows = [row, {"index": 1, "relevance_score": 0}]
    result = run({"results": rows if bad_first else rows[::-1]}, docs)
    assert len(result) == 1
    assert result[0] is docs[1]
    assert docs[0].metadata == {"source": "a"}
    assert docs[1].metadata == {"relevance_score": 0}


@pytest.mark.parametrize(
    "payload", [None, [], "bad", {"results": None}, {"results": {}}, {"results": "bad"}]
)
def test_invalid_envelope_fails_clearly_without_mutating_input(payload):
    docs = [Document(text="a", metadata={"source": "a"})]
    before = deepcopy(docs[0].model_dump())
    with pytest.raises(ValueError, match="results"):
        run(payload, docs)
    assert docs[0].model_dump() == before


def test_duplicate_index_keeps_first_valid_score_and_api_order():
    docs = [Document(text="a"), Document(text="b"), Document(text="c")]
    result = run(
        {
            "results": [
                {"index": 1, "relevance_score": None},
                {"index": 2, "relevance_score": 1},
                {"index": 1, "relevance_score": 0.75},
                {"index": 2, "relevance_score": 0.25},
                {"index": 0, "relevance_score": 0},
            ]
        },
        docs,
    )
    assert [doc.text for doc in result] == ["c", "b", "a"]
    assert [doc.metadata["relevance_score"] for doc in result] == [1, 0.75, 0]


@pytest.mark.parametrize("payload", [{}, {"results": []}])
def test_missing_or_empty_results_retain_empty_result_behavior(payload):
    assert run(payload, [Document(text="a")]) == []
