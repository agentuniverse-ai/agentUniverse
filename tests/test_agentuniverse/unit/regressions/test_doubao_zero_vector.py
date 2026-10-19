from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.embedding.doubao_embedding import DoubaoEmbedding


class FakeEmbeddings:
    def create(self, **kwargs):
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=[0.0] * 512)],
        )


def test_zero_vector_normalization_remains_finite():
    embedding = DoubaoEmbedding(
        client=SimpleNamespace(embeddings=FakeEmbeddings()),
        endpoint_id="endpoint",
        embedding_dims=512,
    )

    result = embedding.get_embeddings(["text"])

    assert result == [[0.0] * 512]
