# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: huggingface_hub_embedding.py
from typing import Any, Optional, List

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class HuggingFaceHubEmbedding(Embedding):
    """
    HuggingFace Hub Embedding implementation using the HuggingFace Inference API.

    Attributes:
        api_key (Optional[str]): The HuggingFace API key.
        model_name (Optional[str]): The embedding model name on HuggingFace Hub.
        endpoint_url (Optional[str]): Custom endpoint URL for the embedding model.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("HF_API_KEY"))
    endpoint_url: Optional[str] = Field(default_factory=lambda: get_from_env("HF_EMBEDDING_ENDPOINT_URL"))
    client: Any = None
    async_client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Get embeddings using HuggingFace Hub Inference API.

        Args:
            texts (List[str]): A list of texts to embed.

        Returns:
            List[List[float]]: A list of embeddings.

        Raises:
            ImportError: If huggingface_hub is not installed.
            ValueError: If API key is missing.
        """
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is not installed. "
                "Please install it with `pip install huggingface_hub`"
            )

        if not self.api_key:
            raise ValueError("HF_API_KEY is required for HuggingFace Hub Embedding")

        client = InferenceClient(
            token=self.api_key,
            model=self.endpoint_url or self.embedding_model_name,
            timeout=120,
        )

        embeddings = []
        for text in texts:
            response = client.feature_extraction(text)
            # Convert numpy array to list
            embedding = response.tolist() if hasattr(response, 'tolist') else list(response)
            embeddings.append(embedding)

        return embeddings

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Async get embeddings using HuggingFace Hub Inference API.

        Args:
            texts (List[str]): A list of texts to embed.

        Returns:
            List[List[float]]: A list of embeddings.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.get_embeddings(texts, **kwargs))

    def as_langchain(self):
        """Convert to a LangChain compatible embedding."""
        try:
            from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain_community is not installed. "
                "Please install it with `pip install langchain-community`"
            )

        return HuggingFaceInferenceAPIEmbeddings(
            api_key=self.api_key,
            model_name=self.embedding_model_name,
            api_url=self.endpoint_url,
        )

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.

        Returns:
            Embedding: A HuggingFaceHubEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "endpoint_url"):
            self.endpoint_url = embedding_configer.endpoint_url
        return self
