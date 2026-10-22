"""Invalid embedding responses must not corrupt fallback documents or scores."""

from copy import deepcopy
from unittest.mock import Mock, call, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor import mmr_processor as module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def documents():
    """Create intentionally stale vectors that an unsuccessful call must retain."""
    return [
        Document(text="a", embedding=[7, 8], metadata={"score": 0.4}),
        Document(text="b", embedding=[9, 10], metadata={"source": "b"}),
    ]


@pytest.mark.parametrize(
    "computed",
    [
        [],
        [[1, 0]],
        [[1, 0], [0, 1], [1, 1]],
        [[1, 0], []],
        [[1, 0], [1]],
        [[1, 0], None],
        [[1, 0], [float("nan"), 1]],
        [[1, 0], [float("inf"), 1]],
        [[1, 0], ["bad", 1]],
        [[1, 0], [True, False]],
        None,
    ],
)
def test_invalid_document_batch_falls_back_without_partial_writes(computed):
    docs = documents()
    before = deepcopy([doc.model_dump() for doc in docs])
    model = Mock()
    model.get_embeddings.side_effect = [computed, [[1, 0]]]
    with patch.object(module, "EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = module.MMRProcessor(
            embedding_name="fixture", top_n=1, score_key="score"
        ).process_docs(docs, Query(query_str="q"))
    assert len(result) == 1 and result[0] is docs[0]
    assert [doc.model_dump() for doc in docs] == before


@pytest.mark.parametrize(
    "query_batch",
    [
        [],
        [[1]],
        [[]],
        [[1, 0], [0, 1]],
        [[float("nan"), 0]],
        None,
        RuntimeError("offline"),
    ],
)
def test_invalid_query_batch_preserves_existing_document_embeddings(query_batch):
    docs = documents()
    before = deepcopy([doc.model_dump() for doc in docs])
    model = Mock()
    model.get_embeddings.side_effect = [[[0, 1], [1, 0]], query_batch]
    with patch.object(module, "EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = module.MMRProcessor(
            embedding_name="fixture", score_key="score"
        ).process_docs(docs, Query(query_str="q"))
    assert [id(doc) for doc in result] == [id(doc) for doc in docs]
    assert [doc.model_dump() for doc in docs] == before


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("target", ["doc", "query"])
def test_nonfinite_precomputed_vectors_do_not_publish_scores(bad, target):
    docs = [Document(text="a", embedding=[0, 1]), Document(text="b", embedding=[1, 0])]
    query = Query(query_str="q", embeddings=[[1, 0]])
    if target == "doc":
        docs[1].embedding = [bad, 0]
    else:
        query.embeddings = [[bad, 0]]
    result = module.MMRProcessor(
        lambda_coef=1, score_key="score", top_n=1
    ).process_docs(docs, query)
    assert result[0] is docs[0]
    assert all(doc.metadata is None for doc in docs)


@pytest.mark.parametrize("scale", [1e-300, 1.0, 1e300])
def test_finite_vector_scale_does_not_change_cosine_ranking(scale):
    docs = [
        Document(text="orthogonal", embedding=[0, scale]),
        Document(text="aligned", embedding=[scale, 0]),
    ]
    result = module.MMRProcessor(lambda_coef=1, score_key="score").process_docs(
        docs, Query(embeddings=[[scale, 0]])
    )
    assert [doc.text for doc in result] == ["aligned", "orthogonal"]
    assert [doc.metadata["score"] for doc in result] == pytest.approx([1, 0])


def test_valid_batch_is_committed_and_ranked():
    docs = documents()
    model = Mock()
    model.get_embeddings.side_effect = [[[0, 1], [1, 0]], [[1, 0]]]
    with patch.object(module, "EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = module.MMRProcessor(
            embedding_name="fixture", lambda_coef=1
        ).process_docs(docs, Query(query_str="q"))
    assert [doc.text for doc in result] == ["b", "a"]
    assert [doc.embedding for doc in docs] == [[0, 1], [1, 0]]
    assert model.get_embeddings.call_args_list == [
        call(["a", "b"]), call(["q"], text_type="query")
    ]


def test_missing_query_text_does_not_publish_unusable_model_vectors():
    docs = documents()
    before = deepcopy([doc.model_dump() for doc in docs])
    model = Mock()
    model.get_embeddings.return_value = [[0, 1], [1, 0]]
    with patch.object(module, "EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = module.MMRProcessor(embedding_name="fixture").process_docs(
            docs, Query(embeddings=[[1, 0]])
        )
    assert [id(doc) for doc in result] == [id(doc) for doc in docs]
    assert [doc.model_dump() for doc in docs] == before


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ([0, 0], [1e300, 0], 0),
        ([1e300, 0], [-1e-300, 0], -1),
        ([3e300, 4e300], [3e-300, 4e-300], 1),
        ([3, 4], [-4, 3], 0),
    ],
)
def test_cosine_retains_zero_negative_and_mixed_scale_semantics(a, b, expected):
    assert module.MMRProcessor._cosine(a, b) == pytest.approx(expected)
