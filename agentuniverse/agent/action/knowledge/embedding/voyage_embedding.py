# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: voyage_embedding.py

"""
Voyage AI embedding component.

Generates text embeddings using the Voyage AI embeddings API
(``https://api.voyageai.com/v1/embeddings``). Voyage AI provides a family of
state-of-the-art embedding models such as ``voyage-3``, ``voyage-3-lite``,
``voyage-3-large`` and ``voyage-large-2``. An API key is required and can be
obtained from https://dash.voyageai.com/.

This component only depends on ``requests`` (already a core dependency of
agentUniverse) — no extra install is required.
"""

import logging
from typing import Any, List, Optional

import requests
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env

logger = logging.getLogger(__name__)

# Voyage AI embeddings endpoint. The host and path are fixed by the public API
# contract; keeping them as a module-level constant makes the URL easy to
# discover from a single place and trivial to patch in unit tests.
_VOYAGE_EMBED_URL = "https://api.voyageai.com/v1/embeddings"

# Voyage AI recommends telling the API whether each call is embedding
# documents for storage or a query for retrieval. Only these two values are
# accepted by the API; anything else falls back to the component default.
_VALID_INPUT_TYPES = ("document", "query")


class VoyageEmbedding(Embedding):
    """Embedding component backed by the Voyage AI embeddings API.

    Attributes:
        embedding_model_name: Voyage AI embedding model
            (default ``voyage-3``).
        api_key: Voyage AI API key (env: ``VOYAGE_API_KEY``).
        input_type: ``"document"`` or ``"query"`` — Voyage AI recommends
            specifying this for best retrieval quality. Defaults to
            ``"document"`` and can be overridden per-call via ``text_type``.
        request_timeout: Timeout in seconds for the HTTP call (default 30).
            ``requests`` defaults to no timeout, so without this a stalled
            Voyage API would hang the whole embed step indefinitely.
        client: Reserved for testing / dependency injection. When set, the
            value's ``post`` callable is used instead of ``requests.post``.
    """

    embedding_model_name: str = "voyage-3"
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("VOYAGE_API_KEY"))
    input_type: str = "document"
    request_timeout: int = 30
    client: Any = None

    def _resolve_input_type(self, text_type: Optional[str]) -> str:
        """Pick the effective ``input_type`` for a single embed call.

        A per-call ``text_type`` wins when it is one of the API-accepted
        values; otherwise we fall back to the component-level ``input_type``
        so a stray kwarg never produces an invalid request body.
        """
        if text_type in _VALID_INPUT_TYPES:
            return text_type
        return self.input_type if self.input_type in _VALID_INPUT_TYPES \
            else "document"

    def get_embeddings(self, texts: List[str],
                       input_type: str = "document",
                       **kwargs) -> List[List[float]]:
        """Return embeddings for ``texts`` via the Voyage AI API.

        Args:
            texts: List of input strings to embed. An empty list short-circuits
                to an empty result without calling the API.
            input_type: ``"document"`` (default) or ``"query"``. Falls back to
                the component-level ``input_type`` when invalid.
            **kwargs: Reserved for forward compatibility — currently unused.

        Returns:
            A list of embedding vectors, one per input text, preserving the
            input order. On timeout an empty-vector list is returned so a
            single slow request does not crash a whole ingestion pipeline.

        Raises:
            ValueError: If ``api_key`` is missing.
            RuntimeError: If the API returns a non-2xx status or a body that
                cannot be decoded as JSON.
        """
        if not texts:
            return []
        if not self.api_key:
            raise ValueError(
                "VoyageEmbedding requires an api_key. Set it on the component "
                "or via the VOYAGE_API_KEY environment variable.")

        effective_type = self._resolve_input_type(input_type)
        post_callable = self.client.post if self.client is not None \
            else requests.post

        try:
            response = post_callable(
                _VOYAGE_EMBED_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.embedding_model_name,
                    "inputs": texts,
                    "input_type": effective_type,
                    "truncation": True,
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("Voyage AI embed request timed out.")
            return [[] for _ in texts]
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None \
                else "?"
            raise RuntimeError(
                f"Voyage AI embed API returned status {status}") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Voyage AI embed API call failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Voyage AI embed API returned non-JSON: {exc}") from exc

        embeddings_list = data.get("data", [])
        if not embeddings_list:
            logger.warning("Voyage AI embed returned empty embeddings list")
            return [[] for _ in texts]
        return [list(item.get("embedding", [])) for item in embeddings_list]

    async def async_get_embeddings(self, texts: List[str],
                                   input_type: str = "document",
                                   **kwargs) -> List[List[float]]:
        """Asynchronously return embeddings for ``texts``.

        The Voyage AI public API does not currently expose a dedicated async
        endpoint, so this delegates to the synchronous implementation. The
        signature is async to satisfy the ``Embedding`` base contract and to
        allow a future swap to an async HTTP client without breaking callers.
        """
        return self.get_embeddings(texts, input_type=input_type, **kwargs)

    def as_langchain(self):
        """Wrap this component as a langchain-compatible Embeddings object."""
        from langchain_core.embeddings import Embeddings as LCEmbeddings

        outer = self

        class _VoyageLangchainEmbedding(LCEmbeddings):
            """Langchain adapter delegating to ``VoyageEmbedding``."""

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return outer.get_embeddings(texts, input_type="document")

            def embed_query(self, text: str) -> List[float]:
                return outer.get_embeddings(
                    [text], input_type="query")[0]

        return _VoyageLangchainEmbedding()

    def _initialize_by_component_configer(
            self, embedding_configer) -> 'VoyageEmbedding':
        """Initialize the component from a ComponentConfiger.

        Honours the base embedding fields (name, description,
        embedding_model_name, embedding_dims) and the Voyage-specific fields
        declared on the YAML.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key"):
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "input_type"):
            self.input_type = embedding_configer.input_type
        if hasattr(embedding_configer, "request_timeout"):
            self.request_timeout = self._validate_request_timeout(
                embedding_configer.request_timeout)
        return self

    @staticmethod
    def _validate_request_timeout(value) -> int:
        """Validate a configured request timeout.

        ``requests`` treats ``None`` as "no timeout" and accepts ``0`` /
        negative values without complaint, so a bad config must fail loudly
        here instead of silently hanging the embed step.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(
                f"VoyageEmbedding request_timeout must be a positive number, "
                f"got {value!r}.")
        if value <= 0:
            raise ValueError(
                f"VoyageEmbedding request_timeout must be a positive number, "
                f"got {value!r}.")
        return value
