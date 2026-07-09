from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.openai_embedding import (
    OpenAIEmbedding,
)


def test_as_langchain_allows_uninitialized_async_client():
    sync_client = MagicMock()
    langchain_embedding = MagicMock()
    embedding = OpenAIEmbedding(
        embedding_model_name="text-embedding-3-small",
        openai_api_key="test-key",
        client=sync_client,
    )

    with patch(
        "agentuniverse.agent.action.knowledge.embedding.openai_embedding.OpenAIEmbeddings",
        return_value=langchain_embedding,
    ) as langchain_client:
        result = embedding.as_langchain()

    assert result is langchain_embedding
    langchain_client.assert_called_once_with(
        openai_api_key="test-key",
        client=sync_client.embeddings,
        async_client=None,
    )
