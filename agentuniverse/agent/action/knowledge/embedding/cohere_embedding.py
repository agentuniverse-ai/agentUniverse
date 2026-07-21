# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: cohere_embedding.py

"""
Cohere embedding component.

Generates text embeddings using the Cohere Embed v3 API. Supports
multilingual models (embed-multilingual-v3.0) and English-optimised models
(embed-english-v3.0).
"""

import logging
from typing import List, Optional

import requests
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env

logger = logging.getLogger(__name__)

_COHERE_EMBED_URL = "https://api.cohere.com/v2/embed"


class CohereEmbedding(Embedding):
    """Embedding component backed by the Cohere Embed v3 API.

    Attributes:
        embedding_model_name: Cohere embed model
            (default ``embed-multilingual-v3.0``).
        api_key: Cohere API key (env: ``COHERE_API_KEY``).
        input_type: ``"document"`` or ``"query"`` — Cohere recommends
            specifying this for best retrieval quality.
        request_timeout: Timeout in seconds (default 30).
    """

    embedding_model_name: str = "embed-multilingual-v3.0"
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("COHERE_API_KEY"))
    input_type: str = "document"
    request_timeout: int = 30

    def get_embeddings(self, texts: List[str],
                       text_type: str = "document") -> List[List[float]]:
        if not texts:
            return []
        if not self.api_key:
            raise ValueError(
                "CohereEmbedding requires an api_key. Set it on the component "
                "or via the COHERE_API_KEY environment variable.")

        effective_type = text_type if text_type in ("document", "query") \
            else self.input_type

        try:
            response = requests.post(
                _COHERE_EMBED_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.embedding_model_name,
                    "texts": texts,
                    "input_type": effective_type,
                    "embedding_types": ["float"],
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("Cohere embed request timed out.")
            return [[] for _ in texts]
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Cohere embed API returned status "
                f"{exc.response.status_code if exc.response is not None else '?'}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Cohere embed API returned non-JSON: {exc}") from exc

        embeddings_list = data.get("embeddings", {}).get("float", [])
        if not embeddings_list:
            logger.warning("Cohere embed returned empty embeddings list")
            return [[] for _ in texts]
        return [list(emb) for emb in embeddings_list]

    async def async_get_embeddings(self, texts: List[str],
                                   text_type: str = "document") -> List[List[float]]:
        # Cohere v2 does not have a dedicated async endpoint; reuse sync.
        return self.get_embeddings(texts, text_type)
