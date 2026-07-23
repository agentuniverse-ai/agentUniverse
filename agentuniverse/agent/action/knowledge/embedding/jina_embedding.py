# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : agentuniverse
# @FileName: jina_embedding.py

"""
Jina AI Embedding component.

[Jina AI](https://jina.ai) provides state-of-the-art multilingual
embeddings through the ``jina-embeddings-v3`` model family, exposed via a
simple HTTP API at ``https://api.jina.ai/v1/embeddings``.

Unlike the OpenAI / DashScope embeddings which are consumed through a
dedicated SDK, the Jina Embeddings API is a plain JSON-over-HTTPS endpoint
with no first-party Python client, so this component calls it directly with
``requests`` (synchronous) and ``asyncio + requests`` (asynchronous). The
response shape is compatible with the OpenAI embeddings response, so the
component only needs to read ``data[*].embedding``.

The component implements the agentUniverse :class:`Embedding` interface, so
it can be referenced from any store / reader that consumes an embedding
component.
"""

import asyncio
from typing import Any, List, Optional

import requests
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

# Default Jina Embeddings API endpoint. It can be overridden through the
# ``JINA_API_BASE`` environment variable or the ``api_base`` YAML field.
JINA_EMBEDDING_API_BASE = "https://api.jina.ai/v1/embeddings"

# Default embedding model. jina-embeddings-v3 is the current flagship; it
# supports configurable output dimensions (default 1024) and multilingual
# text.
JINA_DEFAULT_EMBEDDING_MODEL = "jina-embeddings-v3"

# Default output dimensionality. jina-embeddings-v3 supports 32, 64, 128,
# 256, 512, 768, 1024; 1024 is the recommended default.
JINA_DEFAULT_DIMENSIONS = 1024


class JinaEmbedding(Embedding):
    """Jina AI Embedding class.

    Calls the Jina Embeddings HTTP API to turn a list of texts into vectors.
    Because the API has no first-party Python client this component uses
    ``requests`` directly and exposes the :meth:`get_embeddings` /
    :meth:`async_get_embeddings` methods required by the agentUniverse
    :class:`Embedding` base class.

    Attributes:
        api_key: Jina AI API key. Falls back to the ``JINA_API_KEY``
            environment variable when not provided explicitly.
        api_base: Jina Embeddings endpoint URL. Defaults to
            ``https://api.jina.ai/v1/embeddings``.
        embedding_model_name: The embedding model id, defaults to
            ``jina-embeddings-v3``.
        dimensions: Output vector dimensionality, defaults to ``1024``.
        request_timeout: Timeout in seconds for the HTTP call. ``requests``
            defaults to no timeout, so without this a stalled Jina API would
            hang the whole embedding step indefinitely.
        batch_size: Maximum number of texts sent in a single API call.
            Jina accepts batched inputs; larger batches reduce round-trips
            but increase per-request payload size.
    """

    # Override the base-class attribute so the Jina flagship model is the
    # default; users can still pass a different model name in YAML / code.
    embedding_model_name: Optional[str] = Field(default=JINA_DEFAULT_EMBEDDING_MODEL)

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("JINA_API_KEY"))
    api_base: str = JINA_EMBEDDING_API_BASE
    dimensions: Optional[int] = JINA_DEFAULT_DIMENSIONS
    request_timeout: int = 30
    batch_size: int = 32

    def get_embeddings(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        """Get the Jina embeddings for a list of texts (synchronous).

        Note:
            The ``embedding_model_name`` attribute must be provided (it
            defaults to ``jina-embeddings-v3``). The ``dimensions`` attribute
            is optional and defaults to ``1024``.

        Args:
            texts: A list of texts that need to be embedded.
            **kwargs: Reserved for future use / overrides.

        Returns:
            A list of embedding vectors, one per input text, in the same
            order as the input.

        Raises:
            ValueError: If ``texts`` is empty or ``embedding_model_name``
                is missing.
            Exception: If the API key is missing or the HTTP call fails.
        """
        if not texts:
            raise ValueError("Jina embedding received an empty text list.")
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        self._ensure_api_key()

        all_embeddings: List[List[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start:start + self.batch_size]
            payload = self._build_payload(batch)
            response_json = self._post(payload)
            for item in sorted(response_json.get("data", []),
                               key=lambda d: d.get("index", 0)):
                all_embeddings.append(item.get("embedding", []))
        return all_embeddings

    async def async_get_embeddings(self, texts: List[str], **kwargs: Any) -> \
            List[List[float]]:
        """Asynchronously get the Jina embeddings for a list of texts.

        The Jina API has no native async client, so this method runs the
        blocking :meth:`get_embeddings` in a thread executor via
        :func:`asyncio.to_thread`, allowing it to be ``await``ed without
        blocking the event loop.

        Args:
            texts: A list of texts that need to be embedded.
            **kwargs: Reserved for future use / overrides.

        Returns:
            A list of embedding vectors, one per input text, in the same
            order as the input.
        """
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _ensure_api_key(self) -> None:
        """Validate that an API key is configured before calling the API."""
        if not self.api_key:
            raise Exception(
                "Jina AI API key is not set. Please configure it in the "
                "component or set the JINA_API_KEY environment variable.")

    def _build_payload(self, batch: List[str]) -> dict:
        """Build the JSON request body for the Jina Embeddings API.

        Args:
            batch: The slice of texts to embed in a single request.

        Returns:
            A dict payload suitable for ``requests.post(json=...)``.
        """
        payload: dict = {
            "model": self.embedding_model_name,
            "input": batch,
        }
        if self.dimensions is not None:
            payload["dimensions"] = self.dimensions
        return payload

    def _post(self, payload: dict) -> dict:
        """Send a POST request to the Jina Embeddings API and decode JSON.

        The HTTP send and the JSON decode are isolated: a non-JSON body
        (e.g. an upstream HTML error page) is surfaced as a non-JSON
        response rather than misreported as an API-call error.

        Args:
            payload: The request body.

        Returns:
            The decoded JSON response dict.

        Raises:
            Exception: If the HTTP call fails or the body is not valid JSON.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            response = requests.post(self.api_base, headers=headers,
                                     json=payload, timeout=self.request_timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jina AI embedding API call error: {e}")

        try:
            return response.json()
        except ValueError as e:
            raise Exception(
                f"Jina AI embedding API returned a non-JSON response: {e}")

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) \
            -> 'JinaEmbedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer: A configer containing the embedding basic
                info.

        Returns:
            The initialized embedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "api_base"):
            self.api_base = embedding_configer.api_base
        if hasattr(embedding_configer, "dimensions"):
            self.dimensions = embedding_configer.dimensions
        if hasattr(embedding_configer, "embedding_dims"):
            self.dimensions = embedding_configer.embedding_dims
        if hasattr(embedding_configer, "request_timeout"):
            self.request_timeout = self._validate_request_timeout(
                embedding_configer.request_timeout)
        if hasattr(embedding_configer, "batch_size"):
            self.batch_size = embedding_configer.batch_size
        return self

    @staticmethod
    def _validate_request_timeout(value) -> int:
        """Validate a configured request timeout.

        ``requests`` treats ``None`` as "no timeout" and accepts ``0`` /
        negative values without complaint, so a bad config must fail loudly
        here instead of hanging the embedding step or silently disabling
        the timeout.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Exception(
                f"Jina embedding request_timeout must be a positive number, "
                f"got {value!r}.")
        if value <= 0:
            raise Exception(
                f"Jina embedding request_timeout must be a positive number, "
                f"got {value!r}.")
        return value
