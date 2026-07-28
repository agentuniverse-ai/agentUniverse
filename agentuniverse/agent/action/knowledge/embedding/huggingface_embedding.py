# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: huggingface_embedding.py

"""
Hugging Face Hub embedding component.

Generates text embeddings using models hosted on the Hugging Face Hub via
the ``InferenceClient`` from ``huggingface_hub``. Supports sentence-
transformers models, BGE, GTE, and any embedding model on the Hub.
"""

import logging
from typing import List, Optional

from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env

logger = logging.getLogger(__name__)


class HuggingFaceEmbedding(Embedding):
    """Embedding component backed by Hugging Face Hub Inference API.

    Attributes:
        embedding_model_name: The Hugging Face model repo ID
            (e.g. ``"sentence-transformers/all-MiniLM-L6-v2"``).
        api_key: Hugging Face API token (env: ``HUGGINGFACE_API_KEY``
            or ``HF_TOKEN``).
        timeout: Request timeout in seconds (default 30).
    """

    embedding_model_name: Optional[str] = Field(
        default="sentence-transformers/all-MiniLM-L6-v2")
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_API_KEY")
        or get_from_env("HF_TOKEN"))
    timeout: float = 30.0

    _client: Optional[object] = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise ImportError(
                "huggingface_hub is not installed. Install it with "
                "'pip install huggingface_hub'.") from exc
        self._client = InferenceClient(
            model=self.embedding_model_name,
            token=self.api_key,
            timeout=self.timeout,
        )
        return self._client

    def get_embeddings(self, texts: List[str],
                       text_type: str = "document") -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.
            text_type: ``"document"`` or ``"query"`` (informational; the HF
                Inference API does not distinguish, but the parameter is
                kept for interface compatibility).

        Returns:
            List of embedding vectors (one per input text).
        """
        if not texts:
            return []
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name must be set")

        client = self._get_client()
        result: List[List[float]] = []
        # The HF feature-extraction API processes one text at a time.
        for text in texts:
            try:
                embedding = client.feature_extraction(text)
                # The response is a numpy array or list of floats.
                if hasattr(embedding, "tolist"):
                    embedding = embedding.tolist()
                # Some models return a nested list (batch dimension).
                if isinstance(embedding, list) and embedding and isinstance(embedding[0], list):
                    # Take the first (and only) sentence's embedding.
                    if len(embedding) == 1:
                        embedding = embedding[0]
                    else:
                        # Mean-pool token-level embeddings.
                        embedding = self._mean_pool(embedding)
                result.append(list(embedding))
            except Exception as exc:
                logger.warning("HuggingFace embedding failed for text "
                               "(len=%d): %s", len(text), exc)
                result.append([])
        return result

    async def async_get_embeddings(self, texts: List[str],
                                   text_type: str = "document") -> List[List[float]]:
        """Async embedding generation."""
        if not texts:
            return []
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name must be set")

        try:
            from huggingface_hub import AsyncInferenceClient
        except ImportError as exc:
            raise ImportError(
                "huggingface_hub is not installed. Install it with "
                "'pip install huggingface_hub'.") from exc

        client = AsyncInferenceClient(
            model=self.embedding_model_name,
            token=self.api_key,
            timeout=self.timeout,
        )
        result: List[List[float]] = []
        for text in texts:
            try:
                embedding = await client.feature_extraction(text)
                if hasattr(embedding, "tolist"):
                    embedding = embedding.tolist()
                if isinstance(embedding, list) and embedding and isinstance(embedding[0], list):
                    if len(embedding) == 1:
                        embedding = embedding[0]
                    else:
                        embedding = self._mean_pool(embedding)
                result.append(list(embedding))
            except Exception as exc:
                logger.warning("HuggingFace async embedding failed: %s", exc)
                result.append([])
        return result

    @staticmethod
    def _mean_pool(token_embeddings: List[List[float]]) -> List[float]:
        """Mean-pool a list of token-level embeddings into one vector."""
        if not token_embeddings:
            return []
        dim = len(token_embeddings[0])
        sums = [0.0] * dim
        for emb in token_embeddings:
            for i, val in enumerate(emb):
                if i < dim:
                    sums[i] += val
        n = len(token_embeddings)
        return [s / n for s in sums]
