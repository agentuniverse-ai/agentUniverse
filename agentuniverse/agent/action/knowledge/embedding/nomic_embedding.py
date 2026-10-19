# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: nomic_embedding.py

from typing import Any, List, Optional

import asyncio
import httpx
from langchain_core.embeddings import Embeddings as LCEmbeddings
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

# Nomic embeddings API limit: at most 128 inputs per request.
NOMIC_MAX_BATCH_INPUTS = 128

# Task types supported by the Nomic embeddings API.
NOMIC_TASK_TYPES = ("search_query", "search_document", "document", "annotation")

# Supported embedding models and their dimensions:
#
# +------------------------+--------------------------+---------------------------+
# | Model                  | Supported dimensions     | Note                      |
# +========================+==========================+===========================+
# | nomic-embed-text-v1.5  | 768                      | default 768               |
# +------------------------+--------------------------+---------------------------+


class NomicEmbedding(Embedding):
    """The Nomic embedding class.

    Calls the Nomic embeddings API (``POST {api_base}/embeddings``, an
    OpenAI-compatible endpoint) with ``Authorization: Bearer <api_key>`` and
    returns the embedding vectors in input order.

    Attributes:
        api_key (Optional[str]): The Nomic API key, read from the
            ``NOMIC_API_KEY`` environment variable by default. An empty
            string is treated as unset.
        api_base (str): The Nomic API base URL.
        embedding_model_name (Optional[str]): The embedding model name,
            defaults to ``nomic-embed-text-v1.5``.
        task_type (Optional[str]): Optional Nomic task type, one of
            ``search_query``, ``search_document``, ``document`` or
            ``annotation``. When set it is sent along with each request so
            the model is tuned for the intended use case.
        embedding_dims (Optional[int]): The output embedding dimension.
            ``nomic-embed-text-v1.5`` produces 768-dimensional vectors.
        max_batch_size (int): Maximum number of inputs per request
            (Nomic limit: 128).
        timeout (Optional[int]): The request timeout in seconds.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("NOMIC_API_KEY"))
    api_base: str = "https://api.nomic.ai/v1"
    embedding_model_name: Optional[str] = "nomic-embed-text-v1.5"
    task_type: Optional[str] = None
    max_batch_size: int = NOMIC_MAX_BATCH_INPUTS
    timeout: Optional[int] = 30

    client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of texts using the Nomic API.

        Inputs are split client-side into batches that respect the Nomic
        per-request limit (128 inputs) and the results are merged back in
        input order.

        Args:
            texts (List[str]): The input texts to be embedded. Must be
                non-empty.
            kwargs: Additional keyword arguments (reserved for future use).

        Returns:
            List[List[float]]: The embedding vectors corresponding to the
            input texts.

        Raises:
            ValueError: If ``texts`` is empty, the API key is missing, the
                task type is unknown or the response is malformed.
            Exception: If the Nomic API request fails.
        """
        if not texts:
            raise ValueError("texts must be a non-empty list of strings")
        # An empty string api_key placeholder is treated as unset.
        if not self.api_key:
            raise ValueError("api_key is required but not set (configure it "
                             "or set the NOMIC_API_KEY environment variable)")
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name is required but not set")
        if self.task_type is not None and self.task_type not in NOMIC_TASK_TYPES:
            raise ValueError(
                f"Invalid task_type {self.task_type!r}: expected one of "
                f"{', '.join(NOMIC_TASK_TYPES)}")

        client = self._get_client()
        embeddings: List[List[float]] = []
        try:
            for start in range(0, len(texts), self.max_batch_size):
                batch = texts[start:start + self.max_batch_size]
                request_body = {
                    "input": batch,
                    "model": self.embedding_model_name,
                }
                if self.task_type is not None:
                    request_body["task_type"] = self.task_type
                response = client.post(
                    f"{self.api_base}/embeddings",
                    json=request_body,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                embeddings.extend(
                    self._parse_response(response.json(), len(batch)))
            return embeddings
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to get embeddings from Nomic API: "
                f"HTTP {e.response.status_code} - {e.response.text}") from e
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to get embeddings from Nomic API: {e}") from e

    async def async_get_embeddings(self, texts: List[str],
                                   **kwargs) -> List[List[float]]:
        """Asynchronously retrieve text embeddings using the Nomic API.

        The blocking ``get_embeddings`` call is off-loaded to a worker thread
        via ``asyncio.to_thread`` so that the event loop is not blocked.
        """
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    def as_langchain(self) -> LCEmbeddings:
        """Convert to a LangChain Embedding class."""
        nomic_embedding = self

        class NomicLangchainEmbedding(LCEmbeddings):
            """Wrapper for NomicEmbedding conforming to LangChain's interface."""

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return nomic_embedding.get_embeddings(texts)

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return nomic_embedding.get_embeddings([text])[0]

        return NomicLangchainEmbedding()

    def _initialize_by_component_configer(
            self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains
                embedding configuration.
        Returns:
            Embedding: A NomicEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "api_base"):
            self.api_base = embedding_configer.api_base
        if hasattr(embedding_configer, "task_type"):
            self.task_type = embedding_configer.task_type
        if hasattr(embedding_configer, "max_batch_size"):
            self.max_batch_size = embedding_configer.max_batch_size
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self

    def _get_client(self) -> httpx.Client:
        """Lazily build the httpx client."""
        if self.client is None:
            self.client = httpx.Client(timeout=self.timeout)
        return self.client

    @staticmethod
    def _parse_response(response_json: dict,
                        expected_count: int) -> List[List[float]]:
        """Parse a Nomic embeddings response, ordered by the index field."""
        data = response_json.get("data")
        if not isinstance(data, list) or len(data) != expected_count:
            raise ValueError(
                "Malformed Nomic embeddings response: expected "
                f"{expected_count} embedding(s) but got "
                f"{len(data) if isinstance(data, list) else data}")
        embeddings: List[List[float]] = []
        try:
            for item in sorted(data, key=lambda d: d["index"]):
                embeddings.append(item["embedding"])
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Malformed Nomic embeddings response: missing {e}") from e
        return embeddings
