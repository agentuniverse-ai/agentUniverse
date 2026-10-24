# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : dxz0069
# @FileName: elasticsearch_store.py

from typing import Any, List, Optional

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
    "hosts": "http://localhost:9200",
}

VECTOR_FIELD = "embedding"


class ElasticsearchStore(Store):
    """Elasticsearch-based vector store implementation.

    Stores documents with vectors in an Elasticsearch index and supports
    similarity search through the kNN search of the dense_vector field.
    Indexing a document with an explicit id is idempotent in Elasticsearch,
    so insert, upsert and update all go through the same path.

    Attributes:
        connection_args (Optional[dict]): Arguments passed to the
            `elasticsearch.Elasticsearch` client, e.g. hosts, api_key,
            basic_auth, cloud_id, ca_certs.
        index_name (Optional[str]): The Elasticsearch index storing the
            documents; created automatically on first insert.
        distance (Optional[str]): The dense_vector similarity, one of
            "COSINE", "EUCLID", "DOT".
        embedding_model (Optional[str]): Embedding model key managed by
            `EmbeddingManager`.
        similarity_top_k (Optional[int]): Default top-k for search.
        num_candidates (Optional[int]): The kNN num_candidates parameter;
            defaults to 10 x similarity_top_k as recommended by Elasticsearch.
        with_vectors (bool): If True, include vectors in query results.
    """

    connection_args: Optional[dict] = None
    index_name: Optional[str] = "agentuniverse"
    distance: Optional[str] = "COSINE"
    embedding_model: Optional[str] = None
    similarity_top_k: Optional[int] = 10
    num_candidates: Optional[int] = None
    with_vectors: bool = False

    def _similarity(self) -> str:
        """Map the configured distance name to an Elasticsearch similarity.

        Returns:
            One of "cosine", "l2_norm", "dot_product", defaulting to
            "cosine".
        """
        return {
            "COSINE": "cosine",
            "EUCLID": "l2_norm",
            "DOT": "dot_product",
        }.get((self.distance or "COSINE").upper(), "cosine")

    def _new_client(self) -> Any:
        """Initialize the Elasticsearch client.

        Raises:
            ImportError: If the `elasticsearch` package is not installed.
        """
        if self.client is not None:
            return self.client
        try:
            from elasticsearch import Elasticsearch
        except ImportError:
            raise ImportError(
                "elasticsearch is required for ElasticsearchStore. "
                "Install it with: pip install elasticsearch"
            )
        args = dict(DEFAULT_CONNECTION_ARGS)
        args.update(self.connection_args or {})
        self.client = Elasticsearch(**args)
        return self.client

    def _initialize_by_component_configer(self, elasticsearch_store_configer: ComponentConfiger) -> "ElasticsearchStore":
        super()._initialize_by_component_configer(elasticsearch_store_configer)
        if hasattr(elasticsearch_store_configer, "connection_args"):
            self.connection_args = elasticsearch_store_configer.connection_args
        else:
            self.connection_args = DEFAULT_CONNECTION_ARGS
        if hasattr(elasticsearch_store_configer, "index_name"):
            self.index_name = elasticsearch_store_configer.index_name
        if hasattr(elasticsearch_store_configer, "distance"):
            self.distance = elasticsearch_store_configer.distance
        if hasattr(elasticsearch_store_configer, "embedding_model"):
            self.embedding_model = elasticsearch_store_configer.embedding_model
        if hasattr(elasticsearch_store_configer, "similarity_top_k"):
            self.similarity_top_k = elasticsearch_store_configer.similarity_top_k
        if hasattr(elasticsearch_store_configer, "num_candidates"):
            self.num_candidates = elasticsearch_store_configer.num_candidates
        if hasattr(elasticsearch_store_configer, "with_vectors"):
            self.with_vectors = bool(elasticsearch_store_configer.with_vectors)
        return self

    def _prepare_embeddings(self, documents: List[Document]):
        """Resolve document embeddings through the configured embedding model.

        Args:
            documents: The documents being written.

        Returns:
            The first resolved embedding, or None when no document carries
            an embedding and no embedding model is configured.
        """
        if self.embedding_model is not None:
            for document in documents:
                if not document.embedding or len(document.embedding) == 0:
                    document.embedding = EmbeddingManager().get_instance_obj(
                        self.embedding_model).get_embeddings([document.text])[0]
        for document in documents:
            if document.embedding and len(document.embedding) > 0:
                return document.embedding
        return None

    def _ensure_index(self, dim: int):
        if self.client is None:
            self.client = self._new_client()
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                mappings={
                    "properties": {
                        VECTOR_FIELD: {
                            "type": "dense_vector",
                            "dims": dim,
                            "similarity": self._similarity(),
                        },
                    }
                },
            )

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query similar documents from the Elasticsearch index.

        Args:
            query: The query object with embeddings or a query string.
            **kwargs: Additional keyword arguments.

        Returns:
            The list of similar documents, empty when no embedding resolves.
        """
        if self.client is None:
            return []

        embedding = query.embeddings
        if self.embedding_model is not None and (not embedding or len(embedding) == 0):
            model = EmbeddingManager().get_instance_obj(self.embedding_model)
            embedding = model.get_embeddings([query.query_str], text_type="query")

        if not embedding or len(embedding) == 0:
            return []

        if not self.client.indices.exists(index=self.index_name):
            return []

        limit = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        response = self.client.search(
            index=self.index_name,
            knn={
                "field": VECTOR_FIELD,
                "query_vector": embedding[0],
                "k": limit,
                "num_candidates": self.num_candidates or max(10 * limit, limit),
            },
        )
        return self.to_documents(response, with_vectors=self.with_vectors)

    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the Elasticsearch index.

        Documents whose embedding stays empty after the optional embedding
        model lookup are skipped.
        """
        self._write_documents(documents)

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert documents into the Elasticsearch index.

        Indexing with an explicit id replaces an existing document with the
        same id, which makes this identical to an insert.
        """
        self._write_documents(documents)

    def update_document(self, documents: List[Document], **kwargs):
        """Update documents in the Elasticsearch index."""
        self._write_documents(documents)

    def _write_documents(self, documents: List[Document]):
        """Write documents, creating the index on first use.

        Args:
            documents: The documents to write; documents without an
                embedding after the optional model lookup are skipped.
        """
        vector = self._prepare_embeddings(documents)
        if vector is None:
            return
        self._ensure_index(dim=len(vector))
        for document in documents:
            if not document.embedding or len(document.embedding) == 0:
                continue
            self.client.index(
                index=self.index_name,
                id=str(document.id),
                document={
                    "text": document.text,
                    "metadata": document.metadata or {},
                },
            )

    def delete_document(self, document_id: str, **kwargs):
        """Delete a document from the Elasticsearch index by id.

        Args:
            document_id: The document id to delete.
        """
        if self.client is None:
            return
        if not self.client.indices.exists(index=self.index_name):
            return
        self.client.delete(index=self.index_name, id=str(document_id), ignore=[404])

    @staticmethod
    def to_documents(response, with_vectors: bool = False) -> List[Document]:
        """Convert an Elasticsearch search response to documents.

        Args:
            response: The search response body.
            with_vectors: If True, keep the stored vectors on the documents.

        Returns:
            The converted document list.
        """
        if response is None:
            return []
        documents: List[Document] = []
        for hit in (response.get("hits") or {}).get("hits") or []:
            source = hit.get("_source") or {}
            documents.append(
                Document(
                    id=str(hit.get("_id")),
                    text=source.get("text"),
                    embedding=source.get(VECTOR_FIELD) if with_vectors else [],
                    metadata=source.get("metadata"),
                )
            )
        return documents
