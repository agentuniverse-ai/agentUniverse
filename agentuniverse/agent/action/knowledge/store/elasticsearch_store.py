#!/usr/bin/env python3
"""Elasticsearch vector store for agentUniverse.

Provides insert, query, upsert, update, delete, and inspection capabilities
using Elasticsearch's dense_vector field type and kNN search. Follows the
same bounded/structured/tested contract as the merged pgvector (#661) and
redis_vector (#687) stores.
"""

# ruff: noqa: TRY003, TRY004

import logging
from typing import Any, ClassVar, List, Optional

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import \
    EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class ElasticsearchStore(Store):
    """Vector store backed by Elasticsearch dense_vector + kNN search.

    Attributes:
        hosts: Comma-separated ES host URLs (e.g. ``"http://localhost:9200"``).
        api_key: Optional ES API key (``"id:api_key"`` format).
        username / password: Optional basic auth credentials.
        index_name: ES index name.
        embedding_model: Name of a registered aU embedding component.
        dimensions: Vector dimension; inferred from first insert if unset.
        similarity: Similarity function — ``"cosine"``, ``"l2"``, or
            ``"dot_product"``.
        similarity_top_k: Default number of results.
        verify_certs: Whether to verify TLS certificates (default True).
        vector_field: Name of the dense_vector field in the index.
    """

    hosts: Optional[str] = "http://localhost:9200"
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    index_name: str = "agentuniverse_documents"
    embedding_model: Optional[str] = None
    dimensions: Optional[int] = None
    similarity: str = "cosine"
    similarity_top_k: int = 10
    verify_certs: bool = True
    vector_field: str = "embedding"

    client: Any = None
    _SIMILARITY_VALUES: ClassVar[set] = {"cosine", "l2", "dot_product"}

    # ------------------------------------------------------------------ #
    # Config
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) -> "ElasticsearchStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "hosts", "api_key", "username", "password", "index_name",
            "embedding_model", "dimensions", "similarity", "similarity_top_k",
            "verify_certs", "vector_field",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        if not self.hosts or not isinstance(self.hosts, str):
            raise ValueError("hosts must be a non-empty string")
        if not self.index_name or not isinstance(self.index_name, str):
            raise ValueError("index_name must be a non-empty string")
        self.similarity = (self.similarity or "cosine").lower()
        if self.similarity not in self._SIMILARITY_VALUES:
            raise ValueError(
                f"similarity must be one of {sorted(self._SIMILARITY_VALUES)}")
        if (isinstance(self.similarity_top_k, bool)
                or not isinstance(self.similarity_top_k, int)
                or self.similarity_top_k <= 0):
            raise ValueError("similarity_top_k must be a positive integer")
        if self.dimensions is not None:
            if (isinstance(self.dimensions, bool)
                    or not isinstance(self.dimensions, int)
                    or self.dimensions <= 0):
                raise ValueError("dimensions must be a positive integer")

    # ------------------------------------------------------------------ #
    # Client
    # ------------------------------------------------------------------ #
    def _new_client(self) -> Any:
        try:
            from elasticsearch import Elasticsearch
        except ImportError as exc:
            raise ImportError(
                "elasticsearch is not installed. Install it with "
                "'pip install elasticsearch'.") from exc

        hosts = [h.strip() for h in self.hosts.split(",") if h.strip()]
        kwargs: dict = {"hosts": hosts, "verify_certs": self.verify_certs}

        if self.api_key:
            kwargs["api_key"] = self.api_key
        elif self.username and self.password:
            kwargs["basic_auth"] = (self.username, self.password)

        self.client = Elasticsearch(**kwargs)
        self._ensure_index()
        return self.client

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    def _ensure_index(self) -> None:
        client = self.client
        if client.indices.exists(index=self.index_name):
            return

        dim = self.dimensions or 1536
        mapping = {
            "properties": {
                "text": {"type": "text"},
                self.vector_field: {
                    "type": "dense_vector",
                    "dims": dim,
                    "index": True,
                    "similarity": self.similarity,
                },
            }
        }
        client.indices.create(index=self.index_name, mappings=mapping)
        logger.info("Created ES index %s with %d-dim %s vectors",
                     self.index_name, dim, self.similarity)

    # ------------------------------------------------------------------ #
    # Embedding
    # ------------------------------------------------------------------ #
    def _get_embedding(self, text: str, text_type: str = "document") -> List[float]:
        if not self.embedding_model:
            raise ValueError(
                "No embedding model configured. Set embedding_model or provide embeddings in Documents.")
        try:
            emb = EmbeddingManager().get_instance_obj(self.embedding_model)
            embeddings = emb.get_embeddings([text], text_type=text_type)
            return embeddings[0] if embeddings else []
        except Exception as exc:
            logger.warning("Failed to get embeddings: %s", exc)
            return []

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def insert_document(self, documents: List[Document], **kwargs) -> None:
        if not documents:
            return
        client = self._ensure_client()
        expected_dim = self.dimensions

        for doc in documents:
            vector = doc.embedding
            if (not vector or len(vector) == 0) and self.embedding_model:
                vector = self._get_embedding(doc.text)
            if not vector or len(vector) == 0:
                logger.warning("No embedding for document %s, skipping", doc.id)
                continue
            if expected_dim is None:
                expected_dim = len(vector)
            elif len(vector) != expected_dim:
                raise ValueError(
                    f"Document {doc.id!r} has a {len(vector)}-dim embedding "
                    f"but the index uses {expected_dim}-dim vectors.")

            body = {
                "text": doc.text or "",
                self.vector_field: vector,
            }
            if doc.metadata:
                for k, v in doc.metadata.items():
                    if k not in ("text", self.vector_field):
                        body[k] = v

            client.index(index=self.index_name, id=str(doc.id), document=body)
        client.indices.refresh(index=self.index_name)

    def query(self, query: Query, **kwargs) -> List[Document]:
        client = self._ensure_client()
        if not client.indices.exists(index=self.index_name):
            return []

        embedding = query.embeddings
        if not embedding:
            if not query.query_str:
                return []
            if not self.embedding_model:
                return []
            embedding = [self._get_embedding(query.query_str, text_type="query")]
        if not embedding or len(embedding[0]) == 0:
            return []

        top_k = query.similarity_top_k or self.similarity_top_k
        try:
            result = client.search(
                index=self.index_name,
                knn={
                    "field": self.vector_field,
                    "query_vector": embedding[0],
                    "k": top_k,
                    "num_candidates": min(top_k * 10, 10000),
                },
                source=["text"],
            )
        except Exception:
            logger.exception("Elasticsearch query failed")
            return []

        documents: List[Document] = []
        for hit in result.get("hits", {}).get("hits", []):
            source = hit.get("_source", {})
            metadata = dict(source)
            metadata.pop("text", None)
            metadata.pop(self.vector_field, None)
            if "_score" in hit:
                metadata["score"] = hit["_score"]
            documents.append(Document(
                text=source.get("text", ""),
                metadata=metadata,
            ))
        return documents

    def upsert_document(self, documents: List[Document], **kwargs) -> None:
        self.insert_document(documents, **kwargs)

    def update_document(self, documents: List[Document], **kwargs) -> None:
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs) -> None:
        client = self._ensure_client()
        try:
            client.delete(index=self.index_name, id=str(document_id))
        except Exception:
            logger.exception("ES delete failed for id %s", document_id)

    def get_document_count(self) -> int:
        client = self._ensure_client()
        try:
            result = client.count(index=self.index_name)
            return result.get("count", 0)
        except Exception:
            return 0

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        client = self._ensure_client()
        try:
            result = client.get(index=self.index_name, id=str(document_id))
            if not result.get("found"):
                return None
            source = result.get("_source", {})
            metadata = dict(source)
            metadata.pop("text", None)
            metadata.pop(self.vector_field, None)
            return Document(text=source.get("text", ""), metadata=metadata)
        except Exception:
            return None

    def list_document_ids(self) -> List[str]:
        client = self._ensure_client()
        try:
            result = client.search(
                index=self.index_name,
                query={"match_all": {}},
                size=10000,
                _source=False,
            )
            return [hit["_id"] for hit in result.get("hits", {}).get("hits", [])]
        except Exception:
            return []
