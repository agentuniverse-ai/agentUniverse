# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/8/21
# @Author  : Anush008
# @Email   : anushshetty90@gmail.com
# @FileName: qdrant_store.py

from typing import Any, List, Optional, ClassVar
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import (
    EmbeddingManager,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)


DEFAULT_CONNECTION_ARGS = {
    "host": "localhost",
    "port": 6333,
    "https": False,
}


class QdrantStore(Store):
    """Qdrant-based vector store implementation.

    Stores documents with vectors in a Qdrant collection and supports similarity search.

    Attributes:
        connection_args (Optional[dict]): Qdrant connection parameters.
        collection_name (Optional[str]): Qdrant collection name.
        distance (Optional[str]): Distance metric, one of "COSINE", "EUCLID", "DOT".
        embedding_model (Optional[str]): Embedding model key managed by `EmbeddingManager`.
        similarity_top_k (Optional[int]): Default top-k for search.
        with_vectors (bool): If True, include vectors in query results.
    """

    connection_args: Optional[dict] = None
    collection_name: Optional[str] = "qdrant_db"
    distance: Optional[str] = "COSINE"
    embedding_model: Optional[str] = None
    similarity_top_k: Optional[int] = 10
    with_vectors: bool = False

    client: Optional[QdrantClient] = None

    VECTOR_NAME: ClassVar[str] = "embedding"

    def _metric_from_str(self) -> Distance:
        return {
            "COSINE": Distance.COSINE,
            "EUCLID": Distance.EUCLID,
            "DOT": Distance.DOT,
            "MANHATTAN": Distance.MANHATTAN,
        }.get((self.distance or "COSINE").upper(), Distance.COSINE)

    def _new_client(self) -> Any:
        args = self.connection_args or DEFAULT_CONNECTION_ARGS
        self.client = QdrantClient(**args)
        return self.client

    def _initialize_by_component_configer(self, qdrant_store_configer: ComponentConfiger) -> "QdrantStore":
        super()._initialize_by_component_configer(qdrant_store_configer)
        if hasattr(qdrant_store_configer, "connection_args"):
            self.connection_args = qdrant_store_configer.connection_args
        else:
            self.connection_args = DEFAULT_CONNECTION_ARGS
        if hasattr(qdrant_store_configer, "collection_name"):
            self.collection_name = qdrant_store_configer.collection_name
        if hasattr(qdrant_store_configer, "distance"):
            self.distance = qdrant_store_configer.distance
        if hasattr(qdrant_store_configer, "embedding_model"):
            self.embedding_model = qdrant_store_configer.embedding_model
        if hasattr(qdrant_store_configer, "similarity_top_k"):
            self.similarity_top_k = qdrant_store_configer.similarity_top_k
        if hasattr(qdrant_store_configer, "with_vectors"):
            self.with_vectors = bool(qdrant_store_configer.with_vectors)
        return self

    def _ensure_collection(self, dim: int):
        if self.client is None:
            self.client = self._new_client()
        if not self.client.collection_exists(self.collection_name):
            metric = self._metric_from_str()
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={self.VECTOR_NAME: VectorParams(size=dim, distance=metric)},
            )

    def query(self, query: Query, **kwargs) -> List[Document]:
        if self.client is None:
            return []

        embedding = query.embeddings
        if self.embedding_model is not None and (not embedding or len(embedding) == 0):
            model = EmbeddingManager().get_instance_obj(self.embedding_model)
            embedding = model.get_embeddings([query.query_str], text_type="query")

        limit = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k

        if embedding and len(embedding) > 0:
            query_vector = embedding[0]
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using=self.VECTOR_NAME,
                limit=limit,
                with_payload=True,
                with_vectors=self.with_vectors,
            ).points
        else:
            results = []

        return self.to_documents(results)

    def insert_document(self, documents: List[Document], **kwargs):
        self.upsert_document(documents, **kwargs)

    def upsert_document(self, documents: List[Document], **kwargs):
        if self.client is None:
            return

        points: List[PointStruct] = []
        for document in documents:
            vector = document.embedding
            if (not vector or len(vector) == 0) and self.embedding_model:
                vector = EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([document.text])[0]
            if not vector or len(vector) == 0:
                continue

            self._ensure_collection(dim=len(vector))

            payload = {"text": document.text, "metadata": document.metadata}
            try:
                point_id = str(uuid.UUID(str(document.id)))
            except Exception:
                # fallback to deterministic UUID5 if document id is not UUID
                point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(document.id)))
            points.append(
                PointStruct(
                    id=point_id,
                    vector={self.VECTOR_NAME: vector},
                    payload=payload,
                )
            )

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def update_document(self, documents: List[Document], **kwargs):
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs):
        if self.client is None:
            return
        self.client.delete(collection_name=self.collection_name, points_selector=[document_id])

    @staticmethod
    def to_documents(results) -> List[Document]:
        if results is None:
            return []
        documents: List[Document] = []
        for scored_point in results:
            payload = scored_point.payload or {}
            text = payload.get("text")
            metadata = payload.get("metadata")
            vector = scored_point.vector
            if vector and isinstance(vector, dict):
                vector = vector.get(QdrantStore.VECTOR_NAME, [])
            else:
                vector = []
            documents.append(
                Document(
                    id=str(scored_point.id),
                    text=text,
                    embedding=vector,
                    metadata=metadata,
                )
            )
        return documents
