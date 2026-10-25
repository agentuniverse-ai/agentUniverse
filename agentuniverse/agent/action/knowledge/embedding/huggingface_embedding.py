# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: huggingface_embedding.py

from typing import Any, List, Optional

import httpx
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

HUGGINGFACE_INFERENCE_API_BASE = "https://api-inference.huggingface.co"


class HuggingFaceEmbedding(Embedding):
    """The Hugging Face embedding class.

    Calls the feature-extraction pipeline of the Hugging Face Inference API,
    so any sentence-embedding model published on the Hub can be used with a
    single Hugging Face token, e.g.
    `sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-large-zh-v1.5`.

    The Inference API returns either one pooled vector per input or one
    vector per token depending on the model; token level outputs are mean
    pooled here so the result is always one vector per input text.

    Attributes:
        api_base (Optional[str]): The Inference API base url.
        api_key (Optional[str]): The Hugging Face token.
        timeout (Optional[int]): Request timeout in seconds.
    """

    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("HF_API_BASE") or HUGGINGFACE_INFERENCE_API_BASE
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HF_TOKEN") or get_from_env("HUGGINGFACEHUB_API_TOKEN")
    )
    timeout: Optional[int] = Field(default=30)

    client: Any = None
    async_client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of input texts.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: One embedding vector per input text.

        Raises:
            ValueError: If no api key or embedding model is configured.
            Exception: If the API call fails.
        """
        self._check_config()
        if self.client is None:
            self.client = httpx.Client(timeout=self.timeout)
        response = self.client.post(
            self._feature_extraction_url(),
            json={"inputs": texts, "options": {"wait_for_model": True}},
            headers=self._headers(),
        )
        response.raise_for_status()
        return self._normalize(response.json(), len(texts))

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously retrieve text embeddings for a list of input texts.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: One embedding vector per input text.

        Raises:
            ValueError: If no api key or embedding model is configured.
            Exception: If the API call fails.
        """
        self._check_config()
        if self.async_client is None:
            self.async_client = httpx.AsyncClient(timeout=self.timeout)
        response = await self.async_client.post(
            self._feature_extraction_url(),
            json={"inputs": texts, "options": {"wait_for_model": True}},
            headers=self._headers(),
        )
        response.raise_for_status()
        return self._normalize(response.json(), len(texts))

    def _feature_extraction_url(self) -> str:
        return f"{self.api_base.rstrip('/')}/pipeline/feature-extraction/{self.embedding_model_name}"

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _check_config(self):
        if not self.api_key:
            raise ValueError(
                "HuggingFaceEmbedding: api_key is required. Set the HF_TOKEN "
                "environment variable or configure api_key in the yaml.")
        if not self.embedding_model_name:
            raise ValueError(
                "HuggingFaceEmbedding: embedding_model_name is required, e.g. "
                "sentence-transformers/all-MiniLM-L6-v2.")

    @staticmethod
    def _normalize(payload: Any, expected_count: int) -> List[List[float]]:
        """Normalize the Inference API answer to one vector per input.

        Args:
            payload: The decoded json answer; either a list of pooled
                vectors, or a list of token level vector lists.
            expected_count: The number of input texts.

        Returns:
            One embedding per input text, mean pooling token level outputs.

        Raises:
            ValueError: If the payload does not match the input count.
        """
        vectors = [_mean_pool_if_needed(item) for item in payload]
        if len(vectors) != expected_count:
            raise ValueError(
                f"HuggingFaceEmbedding: expected {expected_count} embeddings, "
                f"got {len(vectors)}.")
        return vectors

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) \
            -> 'HuggingFaceEmbedding':
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_base"):
            self.api_base = embedding_configer.api_base
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self


def _mean_pool_if_needed(item: Any) -> List[float]:
    """Mean pool token level vectors, passing pooled vectors through.

    Args:
        item: Either a vector (list of floats) or a list of token vectors.

    Returns:
        A single vector of the same dimensionality.
    """
    if not item or not isinstance(item, list):
        return []
    if isinstance(item[0], (int, float)):
        return [float(value) for value in item]
    dimension = len(item[0])
    pooled = [0.0] * dimension
    for token_vector in item:
        for index, value in enumerate(token_vector):
            pooled[index] += value
    return [value / len(item) for value in pooled]
