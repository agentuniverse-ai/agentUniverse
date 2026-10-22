# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: voyage_embedding.py

from typing import Any, List, Optional

import asyncio
import httpx
from langchain_core.embeddings import Embeddings as LCEmbeddings
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

# Voyage AI request limits, see https://docs.voyageai.com/docs/rate-limits:
# at most 128 inputs and 32,000 tokens per embeddings request.
VOYAGE_MAX_BATCH_INPUTS = 128
VOYAGE_MAX_BATCH_TOKENS = 32000

# Supported embedding models and their dimensions:
#
# +-----------------+--------------------------+---------------------------+
# | Model           | Supported dimensions     | Note                      |
# +=================+==========================+===========================+
# | voyage-3.5      | 256 / 512 / 1024 / 2048  | default 1024              |
# | voyage-3-lite   | 512                      | default 512               |
# | voyage-3-large  | 2048                     | default 2048              |
# | voyage-code-3   | 256 / 512 / 1024 / 2048  | default 1024, code search |
# +-----------------+--------------------------+---------------------------+


class VoyageEmbedding(Embedding):
    """The Voyage AI embedding class.

    Calls the Voyage AI embeddings API (``POST {api_base}/embeddings``) with
    ``Authorization: Bearer <api_key>`` and returns the embedding vectors in
    input order.

    Attributes:
        api_key (Optional[str]): The Voyage AI API key, read from the
            ``VOYAGE_API_KEY`` environment variable by default. An empty
            string is treated as unset.
        api_base (str): The Voyage AI API base URL.
        embedding_model_name (Optional[str]): The embedding model name,
            defaults to ``voyage-3.5``.
        embedding_dims (Optional[int]): The output embedding dimension
            (``output_dimension`` request parameter). Must be one of the
            dimensions supported by the chosen model.
        input_type (Optional[str]): ``document`` or ``query``. Voyage AI
            recommends always specifying it; it can also be overridden per
            call via the ``input_type`` keyword argument.
        max_batch_size (int): Maximum number of inputs per request
            (Voyage AI limit: 128).
        max_batch_tokens (int): Maximum number of estimated tokens per
            request (Voyage AI limit: 32,000).
        timeout (Optional[int]): The request timeout in seconds.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("VOYAGE_API_KEY"))
    api_base: str = "https://api.voyageai.com/v1"
    embedding_model_name: Optional[str] = "voyage-3.5"
    input_type: Optional[str] = "document"
    max_batch_size: int = VOYAGE_MAX_BATCH_INPUTS
    max_batch_tokens: int = VOYAGE_MAX_BATCH_TOKENS
    timeout: Optional[int] = 30

    client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of texts using the Voyage AI API.

        Inputs are split client-side into batches that respect the Voyage AI
        per-request limits (128 inputs / 32,000 tokens) and the results are
        merged back in input order.

        Args:
            texts (List[str]): The input texts to be embedded. Must be
                non-empty.
            kwargs: Additional keyword arguments, e.g. ``input_type`` to
                override the configured ``input_type`` for this call.

        Returns:
            List[List[float]]: The embedding vectors corresponding to the
            input texts.

        Raises:
            ValueError: If ``texts`` is empty, the API key is missing, the
                input_type is invalid or the response is malformed.
            Exception: If the Voyage AI API request fails.
        """
        if not texts:
            raise ValueError("texts must be a non-empty list of strings")
        # An empty string api_key placeholder is treated as unset.
        if not self.api_key:
            raise ValueError("api_key is required but not set (configure it "
                             "or set the VOYAGE_API_KEY environment variable)")
        input_type = kwargs.get("input_type", self.input_type)
        if input_type is not None and input_type not in ("document", "query"):
            raise ValueError(
                f"Invalid input_type: {input_type}. "
                "input_type must be 'document' or 'query'")
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name is required but not set")

        client = self._get_client()
        embeddings: List[List[float]] = []
        try:
            for batch in self._split_into_batches(texts):
                payload = {
                    "input": batch,
                    "model": self.embedding_model_name,
                }
                if input_type is not None:
                    payload["input_type"] = input_type
                if self.embedding_dims is not None:
                    payload["output_dimension"] = self.embedding_dims
                response = client.post(
                    f"{self.api_base}/embeddings",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                embeddings.extend(
                    self._parse_response(response.json(), len(batch)))
            return embeddings
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to get embeddings from Voyage AI API: "
                f"HTTP {e.response.status_code} - {e.response.text}") from e
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to get embeddings from Voyage AI API: {e}") from e

    async def async_get_embeddings(self, texts: List[str],
                                   **kwargs) -> List[List[float]]:
        """Asynchronously retrieve text embeddings using the Voyage AI API.

        The blocking ``get_embeddings`` call is off-loaded to a worker thread
        via ``asyncio.to_thread`` so that the event loop is not blocked.
        """
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    def as_langchain(self) -> LCEmbeddings:
        """Convert to a LangChain Embedding class."""
        voyage_embedding = self

        class VoyageLangchainEmbedding(LCEmbeddings):
            """Wrapper for VoyageEmbedding conforming to LangChain's interface."""

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return voyage_embedding.get_embeddings(
                    texts, input_type="document")

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return voyage_embedding.get_embeddings(
                    [text], input_type="query")[0]

        return VoyageLangchainEmbedding()

    def _initialize_by_component_configer(
            self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains
                embedding configuration.
        Returns:
            Embedding: A VoyageEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "api_base"):
            self.api_base = embedding_configer.api_base
        if hasattr(embedding_configer, "input_type"):
            self.input_type = embedding_configer.input_type
        if hasattr(embedding_configer, "max_batch_size"):
            self.max_batch_size = embedding_configer.max_batch_size
        if hasattr(embedding_configer, "max_batch_tokens"):
            self.max_batch_tokens = embedding_configer.max_batch_tokens
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self

    def _get_client(self) -> httpx.Client:
        """Lazily build the httpx client."""
        if self.client is None:
            self.client = httpx.Client(timeout=self.timeout)
        return self.client

    def _estimate_tokens(self, text: str) -> int:
        """Conservatively estimate the Voyage AI token count of a text.

        A character-based approximation (~4 characters per token) is used so
        that batches stay under the 32,000-token per-request limit.
        """
        return max(1, (len(text) + 3) // 4)

    def _split_into_batches(self, texts: List[str]) -> List[List[str]]:
        """Split texts into batches within the Voyage AI per-request limits."""
        batches: List[List[str]] = []
        current: List[str] = []
        current_tokens = 0
        for text in texts:
            estimated = self._estimate_tokens(text)
            if current and (len(current) >= self.max_batch_size or
                            current_tokens + estimated > self.max_batch_tokens):
                batches.append(current)
                current = []
                current_tokens = 0
            current.append(text)
            current_tokens += estimated
        if current:
            batches.append(current)
        return batches

    @staticmethod
    def _parse_response(response_json: dict,
                        expected_count: int) -> List[List[float]]:
        """Parse a Voyage AI embeddings response, ordered by the index field."""
        data = response_json.get("data")
        if not isinstance(data, list) or len(data) != expected_count:
            raise ValueError(
                "Malformed Voyage AI embeddings response: expected "
                f"{expected_count} embedding(s) but got "
                f"{len(data) if isinstance(data, list) else data}")
        embeddings: List[List[float]] = []
        try:
            for item in sorted(data, key=lambda d: d["index"]):
                embeddings.append(item["embedding"])
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Malformed Voyage AI embeddings response: missing {e}") from e
        return embeddings
