"""Numerical, configuration, tokenization and copy contracts for BM25."""

import importlib
import inspect
import math
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def docs(*texts):
    return [Document(id=str(i), text=text) for i, text in enumerate(texts)]


def scores(result):
    return {doc.id: doc.metadata["bm25_score"] for doc in result}


def test_hand_calculated_scores_document_frequency_and_query_dedup():
    # N=3, avgdl=2, df(alpha)=2, df(beta)=1; repeated alpha counts once in df.
    batch = docs("alpha alpha beta", "alpha", "gamma delta")
    actual = scores(BM25Reranker().process_docs(batch, Query(query_str="alpha beta alpha")))
    ia, ib = math.log(1.6), math.log(8 / 3)
    assert actual == pytest.approx({"0": ia * 4.4 / 3.65 + ib * 2.2 / 2.65,
                                    "1": ia * 2.2 / 1.75, "2": 0})


@pytest.mark.parametrize("b", [0, 0.75, 1])
def test_length_normalization(b):
    result = BM25Reranker(b=b).process_docs(docs("alpha noise noise", "alpha"), Query(query_str="alpha"))
    assert [doc.id for doc in result] == (["0", "1"] if b == 0 else ["1", "0"])


def test_term_frequency_saturates():
    actual = scores(BM25Reranker(b=0).process_docs(docs("a", "a a", "a a a"), Query(query_str="a")))
    assert actual["0"] < actual["1"] < actual["2"]
    assert actual["2"] - actual["1"] < actual["1"] - actual["0"]


@pytest.mark.parametrize("query,text,other", [
    ("AX-12", "ax-12", "AX-120"), ("v1.2", "V1.2", "v1.20"),
    ("CAFÉ", "cafe\u0301", "cafe"), ("STRASSE", "Straße", "road"),
    ("中文", "中文", "中文说明"), ("foo_bar", "FOO_BAR", "foo bar"),
])
def test_explicit_unicode_identifier_token_policy(query, text, other):
    result = BM25Reranker().process_docs(docs(other, text), Query(query_str=query))
    assert [doc.id for doc in result] == ["1", "0"]
    assert result[1].metadata["bm25_score"] == 0


@pytest.mark.parametrize("top_n,expected", [(None, 3), (0, 0), (1, 1), (3, 3), (99, 3)])
def test_zero_scores_stable_ties_limits_and_empty_documents(top_n, expected):
    result = BM25Reranker(top_n=top_n).process_docs(docs(None, "", "---"), Query(query_str="absent"))
    assert [doc.id for doc in result] == [str(i) for i in range(expected)]
    assert all(doc.metadata["bm25_score"] == 0 for doc in result)


def test_empty_documents_count_in_average_length():
    actual = scores(BM25Reranker().process_docs(docs("alpha", None), Query(query_str="alpha")))
    assert actual["0"] == pytest.approx(math.log(2) * 2.2 / 3.1)


@pytest.mark.parametrize("query", [None, Query(query_str=""), Query(query_str="  "), Query(query_str="---")])
def test_missing_or_tokenless_queries(query):
    with pytest.raises(ValueError, match="at least one token"):
        BM25Reranker().process_docs(docs("alpha"), query)
    assert BM25Reranker().process_docs([], query) == []
    assert BM25Reranker(top_n=0).process_docs(docs("alpha"), query) == []


def test_input_fields_repeated_occurrences_and_repeat_calls_are_preserved():
    doc = Document(text="alpha", metadata={"relevance_score": 99, "nested": {"source": "A"}},
                   embedding=[1.0, 2.0], keywords={"alpha"})
    before = doc.model_dump()
    processor = BM25Reranker()
    for _ in range(2):
        result = processor.process_docs([doc, doc], Query(query_str="alpha"))
        assert len(result) == 2
        assert result[0] is not result[1] and all(item is not doc for item in result)
        for item in result:
            assert item.id == doc.id and item.text == doc.text
            assert item.embedding == doc.embedding and item.keywords == doc.keywords
            assert item.metadata is not doc.metadata
            assert item.metadata["nested"] is doc.metadata["nested"]  # Documented shallow copy.
            assert item.metadata["relevance_score"] == 99
    assert doc.model_dump() == before


def test_explicit_score_overwrite_only_affects_output():
    batch = docs("alpha")
    batch[0].metadata = {"relevance_score": -1}
    result = BM25Reranker(score_field="relevance_score").process_docs(batch, Query(query_str="alpha"))
    assert result[0].metadata["relevance_score"] > 0
    assert batch[0].metadata == {"relevance_score": -1}


INVALID = [
    {"k1": 0}, {"k1": -1}, {"k1": float("inf")}, {"k1": float("nan")},
    {"k1": True}, {"k1": "1.2"}, {"b": -0.1}, {"b": 1.1},
    {"b": float("nan")}, {"b": float("inf")}, {"b": True}, {"b": "0.5"},
    {"top_n": -1}, {"top_n": True}, {"top_n": 1.5}, {"top_n": "2"},
    {"score_field": ""}, {"score_field": " "}, {"score_field": 3},
]


@pytest.mark.parametrize("options", INVALID)
def test_invalid_construction_yaml_and_runtime(options):
    with pytest.raises(ValueError):
        BM25Reranker(**options)
    processor = BM25Reranker()
    key, value = next(iter(options.items()))
    config = Configer(str(Path(inspect.getfile(BM25Reranker)).with_suffix(".yaml"))).load()
    config.set(key, value)
    with pytest.raises(ValueError):
        processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert getattr(processor, key) == getattr(BM25Reranker(), key)
    setattr(processor, key, value)
    with pytest.raises(ValueError):
        processor.process_docs(docs("alpha"), Query(query_str="alpha"))


def test_shipped_yaml_resolves_real_class_and_reconfigures():
    config = Configer(str(Path(inspect.getfile(BM25Reranker)).with_suffix(".yaml"))).load()
    component = ComponentConfiger(config).load()
    cls = getattr(importlib.import_module(component.metadata_module), component.metadata_class)
    processor = cls().initialize_by_component_configer(component)
    assert processor.name == "bm25_reranker" and processor.top_n == 5
    config.set("top_n", None)
    config.set("b", 0)
    processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert processor.top_n is None and processor.b == 0


@pytest.mark.parametrize("k1", [5e-324, 1.2, 1e308])
def test_finite_extreme_saturation_values(k1):
    result = BM25Reranker(k1=k1).process_docs(docs("alpha " * 1000, "alpha"), Query(query_str="alpha"))
    assert all(math.isfinite(doc.metadata["bm25_score"]) for doc in result)


def test_candidate_statistics_do_not_leak_between_calls():
    processor = BM25Reranker()
    first = processor.process_docs(docs("alpha"), Query(query_str="alpha"))
    processor.process_docs(docs("alpha", "beta", "gamma"), Query(query_str="gamma"))
    assert processor.process_docs(docs("alpha"), Query(query_str="alpha")) == first
