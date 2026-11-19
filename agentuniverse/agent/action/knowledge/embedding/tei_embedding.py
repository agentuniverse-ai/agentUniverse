# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: tei_embedding.py

from typing import Any, List, Optional

import asyncio
import httpx
from langchain_core.embeddings import Embeddings as LCEmbeddings
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

# Client-side cap on the number of inputs per request. A self-hosted TEI
# server queues requests internally; this keeps each request within the
# default server-side batch budgets (raise it together with the server's
# --max-batch-tokens / --max-client-batch-size settings if needed).
TEI_MAX_BATCH_INPUTS = 256

# Supported embedding models and their dimensions (self-hosted with TEI):
#
# +---------------------------+--------------------------+---------------------------+
# | Model                     | Supported dimensions     | Note                      |
# +===========================+==========================+===========================+
# | BAAI/bge-m3               | 1024 (Matryoshka)        | default, multilingual     |
# | BAAI/bge-large-en-v1.5    | 1024                     |                           |
# | BAAI/bge-large-zh-v1.5    | 1024                     |                           |
# | intfloat/multilingual-e5- | 1024                     |                           |
# | large                     |                          |                           |
# +---------------------------+--------------------------+---------------------------+
# TEI serves the model it was started with; the `model` field is accepted by
# the OpenAI-compatible endpoint but the server decides what is loaded.


class TEIEmbedding(Embedding):
    """The Text Embeddings Inference (TEI) embedding class.

    Calls the OpenAI-compatible embeddings endpoint of a self-hosted TEI
    server (``POST {api_base}/embeddings``, by default
    ``http://localhost:8080/v1/embeddings``) and returns the embedding
    vectors in input order. TEI is keyless by default, so no API key is
    required unless the deployment sits behind an authenticating proxy.

    Attributes:
        api_key (Optional[str]): Optional bearer token, read from the
            ``TEI_API_KEY`` environment variable by default. An empty
            string is treated as unset and no Authorization header is
            sent (TEI itself does not require authentication).
        api_base (str): The TEI OpenAI-compatible API base URL.
        embedding_model_name (Optional[str]): The embedding model name,
            defaults to ``BAAI/bge-m3``. TEI serves the model it was
            launched with; this field is informational for the server.
        embedding_dims (Optional[int]): The output embedding dimension.
            When set it is sent as the ``dimensions`` parameter so that
            Matryoshka-capable models (e.g. bge-m3) are truncated.
        max_batch_size (int): Maximum number of inputs per request.
        timeout (Optional[int]): The request timeout in seconds.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("TEI_API_KEY"))
    api_base: str = "http://localhost:8080/v1"
    embedding_model_name: Optional[str] = "BAAI/bge-m3"
    max_batch_size: int = TEI_MAX_BATCH_INPUTS
    timeout: Optional[int] = 30

    client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of texts from a TEI server.

        Inputs are split client-side into batches of at most
        ``max_batch_size`` items and the results are merged back in input
        order.

        Args:
            texts (List[str]): The input texts to be embedded. Must be
                non-empty.
            kwargs: Additional keyword arguments (reserved for future use).

        Returns:
            List[List[float]]: The embedding vectors corresponding to the
            input texts.

        Raises:
            ValueError: If ``texts`` is empty, the model name is missing or
                the response is malformed.
            Exception: If the TEI server request fails.
        """
        if not texts:
            raise ValueError("texts must be a non-empty list of strings")
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name is required but not set")

        client = self._get_client()
        embeddings: List[List[float]] = []
        try:
            for start in range(0, len(texts), self.max_batch_size):
                batch = texts[start:start + self.max_batch_size]
                payload = {
                    "input": batch,
                    "model": self.embedding_model_name,
                }
                if self.embedding_dims:
                    payload["dimensions"] = self.embedding_dims
                response = client.post(
                    f"{self.api_base}/embeddings",
                    json=payload,
                    headers=self._auth_headers(),
                )
                response.raise_for_status()
                embeddings.extend(
                    self._parse_response(response.json(), len(batch)))
            return embeddings
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to get embeddings from the TEI server: "
                f"HTTP {e.response.status_code} - {e.response.text}") from e
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to get embeddings from the TEI server: {e}") from e

    async def async_get_embeddings(self, texts: List[str],
                                   **kwargs) -> List[List[float]]:
        """Asynchronously retrieve text embeddings from a TEI server.

        The blocking ``get_embeddings`` call is off-loaded to a worker thread
        via ``asyncio.to_thread`` so that the event loop is not blocked.
        """
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    def as_langchain(self) -> LCEmbeddings:
        """Convert to a LangChain Embedding class."""
        tei_embedding = self

        class TEILangchainEmbedding(LCEmbeddings):
            """Wrapper for TEIEmbedding conforming to LangChain's interface."""

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return tei_embedding.get_embeddings(texts)

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return tei_embedding.get_embeddings([text])[0]

        return TEILangchainEmbedding()

    def _initialize_by_component_configer(
            self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains
                embedding configuration.
        Returns:
            Embedding: A TEIEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "api_base"):
            self.api_base = embedding_configer.api_base
        if hasattr(embedding_configer, "max_batch_size"):
            self.max_batch_size = embedding_configer.max_batch_size
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self

    def _auth_headers(self) -> dict:
        """Build the request headers; TEI is keyless unless a token is set."""
        # An empty string api_key placeholder is treated as unset.
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}

    def _get_client(self) -> httpx.Client:
        """Lazily build the httpx client."""
        if self.client is None:
            self.client = httpx.Client(timeout=self.timeout)
        return self.client

    @staticmethod
    def _parse_response(response_json: dict,
                        expected_count: int) -> List[List[float]]:
        """Parse a TEI embeddings response, ordered by the index field."""
        data = response_json.get("data")
        if not isinstance(data, list) or len(data) != expected_count:
            raise ValueError(
                "Malformed TEI embeddings response: expected "
                f"{expected_count} embedding(s) but got "
                f"{len(data) if isinstance(data, list) else data}")
        embeddings: List[List[float]] = []
        try:
            for item in sorted(data, key=lambda d: d["index"]):
                embeddings.append(item["embedding"])
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Malformed TEI embeddings response: missing {e}") from e
        return embeddings
