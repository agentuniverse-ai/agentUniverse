# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: weaviate_store.py

import uuid as uuid_module
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
    "http_host": "localhost",
    "http_port": 8080,
    "http_secure": False,
    "grpc_host": "localhost",
    "grpc_port": 50051,
    "grpc_secure": False,
}


class WeaviateStore(Store):
    """Weaviate-based vector store implementation.

    Stores documents with vectors in a Weaviate collection and supports
    similarity search through the Weaviate v4 Python client.

    Attributes:
        connection_args (Optional[dict]): Weaviate connection parameters for
            `weaviate.connect_to_custom`: http_host, http_port, http_secure,
            grpc_host, grpc_port, grpc_secure. When `api_key` is set it is
            sent as an API key credential.
        collection_name (Optional[str]): Weaviate collection name.
        distance (Optional[str]): Distance metric, one of "COSINE", "EUCLID",
            "DOT", "MANHATTAN", "HAMMING".
        embedding_model (Optional[str]): Embedding model key managed by
            `EmbeddingManager`.
        similarity_top_k (Optional[int]): Default top-k for search.
        with_vectors (bool): If True, include vectors in query results.
    """

    connection_args: Optional[dict] = None
    collection_name: Optional[str] = "agentuniverse"
    distance: Optional[str] = "COSINE"
    embedding_model: Optional[str] = None
    similarity_top_k: Optional[int] = 10
    with_vectors: bool = False
    api_key: Optional[str] = None

    def _distance_metric(self):
        """Map the configured distance name to a Weaviate VectorDistances value.

        Returns:
            The Weaviate distance metric enum value, defaulting to COSINE.
        """
        from weaviate.classes.config import VectorDistances
        return {
            "COSINE": VectorDistances.COSINE,
            "EUCLID": VectorDistances.L2_SQUARED,
            "DOT": VectorDistances.DOT,
            "MANHATTAN": VectorDistances.MANHATTAN,
            "HAMMING": VectorDistances.HAMMING,
        }.get((self.distance or "COSINE").upper(), VectorDistances.COSINE)

    def _new_client(self) -> Any:
        """Initialize the Weaviate client.

        Raises:
            ImportError: If the `weaviate-client` package is not installed.
        """
        if self.client is not None:
            return self.client
        try:
            import weaviate
        except ImportError:
            raise ImportError(
                "weaviate-client is required for WeaviateStore. "
                "Install it with: pip install weaviate-client"
            )
        args = dict(DEFAULT_CONNECTION_ARGS)
        args.update(self.connection_args or {})
        auth_credentials = None
        if self.api_key:
            from weaviate.auth import AuthApiKey
            auth_credentials = AuthApiKey(api_key=self.api_key)
        self.client = weaviate.connect_to_custom(
            http_host=args.get("http_host"),
            http_port=args.get("http_port"),
            http_secure=args.get("http_secure", False),
            grpc_host=args.get("grpc_host"),
            grpc_port=args.get("grpc_port"),
            grpc_secure=args.get("grpc_secure", False),
            auth_credentials=auth_credentials,
        )
        return self.client

    def _initialize_by_component_configer(self, weaviate_store_configer: ComponentConfiger) -> "WeaviateStore":
        super()._initialize_by_component_configer(weaviate_store_configer)
        if hasattr(weaviate_store_configer, "connection_args"):
            self.connection_args = weaviate_store_configer.connection_args
        else:
            self.connection_args = DEFAULT_CONNECTION_ARGS
        if hasattr(weaviate_store_configer, "collection_name"):
            self.collection_name = weaviate_store_configer.collection_name
        if hasattr(weaviate_store_configer, "distance"):
            self.distance = weaviate_store_configer.distance
        if hasattr(weaviate_store_configer, "embedding_model"):
            self.embedding_model = weaviate_store_configer.embedding_model
        if hasattr(weaviate_store_configer, "similarity_top_k"):
            self.similarity_top_k = weaviate_store_configer.similarity_top_k
        if hasattr(weaviate_store_configer, "with_vectors"):
            self.with_vectors = bool(weaviate_store_configer.with_vectors)
        if hasattr(weaviate_store_configer, "api_key"):
            self.api_key = weaviate_store_configer.api_key
        return self

    def _ensure_collection(self, dim: int):
        if self.client is None:
            self.client = self._new_client()
        if not self.client.collections.exists(self.collection_name):
            from weaviate.classes.config import Configure
            self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=[
                    Configure.NamedVectors.none(
                        name="embedding",
                        vector_index_config=Configure.VectorIndex.hnsw(
                            distance_metric=self._distance_metric(),
                        ),
                    )
                ],
            )

    def _document_uuid(self, document: Document) -> str:
        """Return a stable UUID for a document id.

        Args:
            document: The document whose id is converted.

        Returns:
            The document id itself when it is a valid UUID, otherwise a
            deterministic UUID5 derived from it.
        """
        try:
            return str(uuid_module.UUID(str(document.id)))
        except Exception:
            return str(uuid_module.uuid5(uuid_module.NAMESPACE_URL, str(document.id)))

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query similar documents from the Weaviate collection.

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

        limit = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        collection = self.client.collections.get(self.collection_name)
        results = collection.query.near_vector(
            near_vector=embedding[0],
            limit=limit,
            include_vector=self.with_vectors,
        )
        return self.to_documents(results)

    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the Weaviate collection.

        Documents whose embedding stays empty after the optional embedding
        model lookup are skipped.
        """
        collection = self._collection_for(documents)
        if collection is None:
            return
        for document in documents:
            if not document.embedding or len(document.embedding) == 0:
                continue
            collection.data.insert(
                properties=self._properties(document),
                uuid=self._document_uuid(document),
                vector=document.embedding,
            )

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert documents into the Weaviate collection.

        Documents whose embedding stays empty after the optional embedding
        model lookup are skipped.
        """
        collection = self._collection_for(documents)
        if collection is None:
            return
        for document in documents:
            if not document.embedding or len(document.embedding) == 0:
                continue
            collection.data.replace(
                uuid=self._document_uuid(document),
                properties=self._properties(document),
                vector=document.embedding,
            )

    def _prepare_embeddings(self, documents: List[Document]):
        """Resolve document embeddings through the configured embedding model.

        Args:
            documents: The documents being inserted or upserted.

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

    def _collection_for(self, documents: List[Document]):
        """Return the collection handle, creating the collection on first use.

        Returns None when the store has no client yet or no embedding
        resolved, mirroring the silent no-op behavior of the base stores.
        """
        vector = self._prepare_embeddings(documents)
        if self.client is None:
            if vector is None:
                return None
            self.client = self._new_client()
        if vector is not None:
            self._ensure_collection(dim=len(vector))
        return self.client.collections.get(self.collection_name)

    def update_document(self, documents: List[Document], **kwargs):
        """Update documents in the Weaviate collection."""
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs):
        """Delete a document from the Weaviate collection by id.

        Args:
            document_id: The document id whose stable UUID is deleted.
        """
        if self.client is None:
            return
        collection = self.client.collections.get(self.collection_name)
        try:
            point_id = str(uuid_module.UUID(str(document_id)))
        except Exception:
            point_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_URL, str(document_id)))
        collection.data.delete_by_id(point_id)

    @staticmethod
    def _properties(document: Document) -> dict:
        return {"text": document.text, "metadata": document.metadata}

    @staticmethod
    def to_documents(results) -> List[Document]:
        """Convert Weaviate query results to documents.

        Args:
            results: The objects returned by a Weaviate query.

        Returns:
            The converted document list.
        """
        if results is None:
            return []
        documents: List[Document] = []
        for result in results:
            properties = getattr(result, "properties", None) or {}
            vector = getattr(result, "vector", None)
            if isinstance(vector, dict):
                vector = vector.get("embedding", [])
            documents.append(
                Document(
                    id=str(getattr(result, "uuid", "")),
                    text=properties.get("text"),
                    embedding=vector or [],
                    metadata=properties.get("metadata"),
                )
            )
        return documents
