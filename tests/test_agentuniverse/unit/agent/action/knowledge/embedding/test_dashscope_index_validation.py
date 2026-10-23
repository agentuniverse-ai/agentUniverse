import pytest

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import DashscopeEmbedding


def test_indexed_response_is_sorted_and_requires_complete_unique_indices():
    rows = [
        {"text_index": 2, "embedding": [2.0]},
        {"text_index": 0, "embedding": [0.0]},
        {"text_index": 1, "embedding": [1.0]},
    ]

    ordered = DashscopeEmbedding._order_batch_embeddings(rows, 3)

    assert [row["text_index"] for row in ordered] == [0, 1, 2]


@pytest.mark.parametrize(
    "indices",
    [
        [0, 0, 2],
        [-1, 1, 2],
        [0, 1, 3],
        [0, 1, True],
    ],
)
def test_invalid_indexed_response_is_rejected(indices):
    rows = [{"text_index": index, "embedding": [float(position)]} for position, index in enumerate(indices)]

    with pytest.raises(ValueError):
        DashscopeEmbedding._order_batch_embeddings(rows, 3)


def test_unindexed_legacy_response_keeps_arrival_order():
    rows = [{"embedding": [2.0]}, {"embedding": [0.0]}]

    assert DashscopeEmbedding._order_batch_embeddings(rows, 2) is rows


def test_missing_index_in_mixed_response_is_rejected():
    rows = [{"text_index": 0, "embedding": [0.0]}, {"embedding": [1.0]}]

    with pytest.raises(ValueError):
        DashscopeEmbedding._order_batch_embeddings(rows, 2)
