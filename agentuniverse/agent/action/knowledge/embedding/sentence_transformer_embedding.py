# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: sentence_transformer_embedding.py

"""
Sentence-Transformers embedding component.

Generates text embeddings using locally-hosted sentence-transformers models
(via the ``sentence-transformers`` package). No API key or network connection
required — models run entirely on-device. Ideal for development, testing,
privacy-sensitive deployments, and offline use.
"""

import logging
from typing import List, Optional

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedding(Embedding):
    """Embedding component backed by locally-hosted sentence-transformers.

    Attributes:
        embedding_model_name: The model name or path
            (default ``all-MiniLM-L6-v2``).
        device: Device to run the model on (``"cpu"``, ``"cuda"``,
            ``"mps"``). Default ``"cpu"``.
        normalize_embeddings: If True, L2-normalise the output vectors
            (default True — recommended for cosine similarity).
        batch_size: Batch size for encoding (default 32).
    """

    embedding_model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    normalize_embeddings: bool = True
    batch_size: int = 32

    _model: Optional[object] = None

    def _initialize_by_component_configer(
            self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Apply component-specific fields from the YAML configuration.

        The base class only copies ``name``, ``description``,
        ``embedding_dims`` and ``embedding_model_name``; without this
        override, ``device`` / ``normalize_embeddings`` / ``batch_size``
        set in YAML would be silently ignored.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "device"):
            self.device = embedding_configer.device
        if hasattr(embedding_configer, "normalize_embeddings"):
            self.normalize_embeddings = embedding_configer.normalize_embeddings
        if hasattr(embedding_configer, "batch_size"):
            self.batch_size = embedding_configer.batch_size
        return self

    def _get_model(self):
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed. Install it with "
                "'pip install sentence-transformers'.") from exc
        self._model = SentenceTransformer(
            self.embedding_model_name, device=self.device)
        logger.info("Loaded sentence-transformers model %s on %s",
                     self.embedding_model_name, self.device)
        return self._model

    def get_embeddings(self, texts: List[str],
                       text_type: str = "document") -> List[List[float]]:
        if not texts:
            return []
        model = self._get_model()
        try:
            embeddings = model.encode(
                texts,
                normalize_embeddings=self.normalize_embeddings,
                batch_size=self.batch_size,
            )
            # Convert numpy array to list of lists.
            if hasattr(embeddings, "tolist"):
                embeddings = embeddings.tolist()
            return [list(emb) for emb in embeddings]
        except Exception as exc:
            logger.warning("SentenceTransformer embedding failed: %s", exc)
            return [[] for _ in texts]

    async def async_get_embeddings(self, texts: List[str],
                                   text_type: str = "document") -> List[List[float]]:
        # sentence-transformers is CPU-bound (no native async); reuse sync.
        return self.get_embeddings(texts, text_type)
