from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.embedding.doubao_embedding import DoubaoEmbedding


class FakeEmbeddings:
    def create(self, **kwargs):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.0] * 8)])


def test_unsupported_dimension_error_lists_supported_values():
    embedding = DoubaoEmbedding(
        client=SimpleNamespace(embeddings=FakeEmbeddings()),
        endpoint_id="endpoint",
        embedding_dims=8,
    )

    with pytest.raises(
        Exception,
        match="Supported dimensions are: 512, 1024, 2048",
    ):
        embedding.get_embeddings(["text"])
