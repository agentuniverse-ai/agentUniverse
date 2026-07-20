#!/usr/bin/env python3
"""Weaviate vector store for agentUniverse.

Provides insert, query, upsert, update, delete, and inspection capabilities
using the Weaviate vector database (v4 client API). Supports cosine, dot, and
L2 distance metrics, configurable vector dimensions, optional metadata
filtering, and bounded resource usage (top-k, max insert batch).
"""

# Validation failures are converted to structured responses at the public
# boundary, so bespoke exception subclasses add no useful signal.
# ruff: noqa: TRY003, TRY004

import json
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


class WeaviateStore(Store):
    """Vector store backed by Weaviate v4.

    Attributes:
        url: Weaviate server URL (e.g. ``http://localhost:8080``). If
            ``grpc_port`` is set, the gRPC port is used for faster data
            transfer.
        grpc_port: gRPC port (default 50051). Set to ``0`` to disable gRPC.
        api_key: Optional Weaviate API key for authenticated clusters.
        collection_name: Weaviate collection (class) name. Must be a valid
            Weaviate identifier.
        embedding_model: Name of a registered aU embedding component used to
            embed documents / queries on demand.
        dimensions: Vector dimension. If ``None``, inferred from the first
            inserted document.
        distance: Distance metric — ``cosine``, ``dot``, or ``l2``.
        similarity_top_k: Default number of results to return.
        max_insert_batch: Maximum documents per Weaviate batch insert.
    """

    url: Optional[str] = "http://localhost:8080"
    grpc_port: int = 50051
    api_key: Optional[str] = None
    collection_name: str = "AgentuniverseDocument"
    embedding_model: Optional[str] = None
    dimensions: Optional[int] = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    max_insert_batch: int = 500

    client: Any = None
    _collection: Any = None

    _DISTANCE_METRICS: ClassVar[dict] = {
        "cosine": "cosine",
        "dot": "dot",
        "l2": "l2",
        "euclidean": "l2",
        "manhattan": "l2",  # Weaviate uses squared L2 internally
    }

    # ------------------------------------------------------------------ #
    # Configuration & lifecycle
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) -> "WeaviateStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "url", "grpc_port", "api_key", "collection_name",
            "embedding_model", "dimensions", "distance",
            "similarity_top_k", "max_insert_batch",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        if not self.url or not isinstance(self.url, str):
            raise ValueError("url must be a non-empty string")
        if not self.collection_name or not isinstance(self.collection_name, str):
            raise ValueError("collection_name must be a non-empty string")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCE_METRICS:
            raise ValueError(
                f"distance must be one of {list(self._DISTANCE_METRICS.keys())}")
        if (isinstance(self.similarity_top_k, bool)
                or not isinstance(self.similarity_top_k, int)
                or self.similarity_top_k <= 0):
            raise ValueError("similarity_top_k must be a positive integer")
        if (isinstance(self.max_insert_batch, bool)
                or not isinstance(self.max_insert_batch, int)
                or self.max_insert_batch <= 0):
            raise ValueError("max_insert_batch must be a positive integer")
        if self.dimensions is not None:
            if (isinstance(self.dimensions, bool)
                    or not isinstance(self.dimensions, int)
                    or self.dimensions <= 0):
                raise ValueError("dimensions must be a positive integer")

    # ------------------------------------------------------------------ #
    # Client management
    # ------------------------------------------------------------------ #
    def _new_client(self) -> Any:
        try:
            import weaviate
        except ImportError as exc:
            raise ImportError(
                "weaviate-client is not installed. Install it with "
                "'pip install weaviate-client'.") from exc

        headers: dict = {}
        auth = None
        if self.api_key:
            auth = weaviate.auth.AuthApiKey(self.api_key)

        connect_kwargs: dict = {
            "headers": headers,
        }
        if auth:
            connect_kwargs["auth_client_secret"] = auth

        if self.grpc_port and self.grpc_port > 0:
            client = weaviate.connect_to_local(
                url=self.url, grpc_port=self.grpc_port, **connect_kwargs)
        else:
            client = weaviate.connect_to_custom(
                http_host=self._parse_host(self.url),
                http_port=self._parse_port(self.url),
                http_secure=self._parse_secure(self.url),
                **connect_kwargs)
        self.client = client
        self._ensure_collection()
        return self.client

    @staticmethod
    def _parse_host(url: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname or "localhost"

    @staticmethod
    def _parse_port(url: str) -> int:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.port or 8080

    @staticmethod
    def _parse_secure(url: str) -> bool:
        return url.lower().startswith("https://")

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    @property
    def collection(self) -> Any:
        if self._collection is None:
            self._ensure_client()
        return self._collection

    def _ensure_collection(self) -> None:
        """Create the collection if it does not exist, or fetch it."""
        try:
            import weaviate.classes as wvc
        except ImportError:
            raise ImportError("weaviate-client is not installed.")

        client = self.client
        metric = self._DISTANCE_METRICS[self.distance]

        if client.collections.exists(self.collection_name):
            self._collection = client.collections.get(self.collection_name)
            return

        # Determine dimensions for vector index config.
        vector_index_config = self._build_vector_index_config(wvc, metric)

        self._collection = client.collections.create(
            name=self.collection_name,
            properties=[
                wvc.config.Property(
                    name="text",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="metadata_json",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
            ],
            vector_index_config=vector_index_config,
        )

    def _build_vector_index_config(self, wvc: Any, metric: str) -> Any:
        """Build a VectorIndex configuration for the given distance metric."""
        try:
            return wvc.config.Configure.VectorIndex.hnsw(
                vector_index_config=self._vector_config(wvc, metric)
            )
        except Exception:
            # Older weaviate-client versions use a different signature.
            return wvc.config.Configure.VectorIndex.hnsw()

    @staticmethod
    def _vector_config(wvc: Any, metric: str) -> Any:
        try:
            return wvc.config.VectorIndexHnsw(metric=metric)
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Embedding resolution
    # ------------------------------------------------------------------ #
    def _get_embedding(self, text: str, text_type: str = "document") -> List[float]:
        if not self.embedding_model:
            raise ValueError(
                "No embedding model configured. Set embedding_model on the "
                "WeaviateStore component or provide embeddings in Documents.")
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
        collection = self.collection
        if collection is None:
            return

        # Resolve / validate dimensions from the first document with an embedding.
        expected_dim = self.dimensions
        for doc in documents:
            if doc.embedding and len(doc.embedding) > 0:
                if expected_dim is None:
                    expected_dim = len(doc.embedding)
                elif len(doc.embedding) != expected_dim:
                    raise ValueError(
                        f"Document {doc.id!r} has a {len(doc.embedding)}-dim "
                        f"embedding but the collection uses {expected_dim}-dim "
                        f"vectors; re-embed with a consistent model.")

        # Batch insert, respecting max_insert_batch.
        batch = []
        for doc in documents:
            vector = doc.embedding
            if (not vector or len(vector) == 0) and self.embedding_model:
                vector = self._get_embedding(doc.text)
            if not vector or len(vector) == 0:
                logger.warning("No embedding for document %s, skipping", doc.id)
                continue
            if expected_dim is not None and len(vector) != expected_dim:
                raise ValueError(
                    f"Document {doc.id!r} embedding dimension {len(vector)} "
                    f"does not match expected {expected_dim}.")

            properties = {
                "text": doc.text or "",
                "metadata_json": json.dumps(doc.metadata or {}, default=str,
                                            ensure_ascii=False),
            }
            batch.append((str(doc.id), properties, vector))

            if len(batch) >= self.max_insert_batch:
                self._batch_insert(collection, batch)
                batch = []

        if batch:
            self._batch_insert(collection, batch)

    def _batch_insert(self, collection: Any, batch: list) -> None:
        for doc_id, properties, vector in batch:
            collection.data.insert(
                properties=properties,
                vector=vector,
                uuid=doc_id,
            )

    def query(self, query: Query, **kwargs) -> List[Document]:
        collection = self.collection
        if collection is None:
            return []

        # Resolve query embedding.
        embedding = query.embeddings
        if not embedding:
            if not query.query_str:
                return []
            if not self.embedding_model:
                logger.warning("No embedding in query and no embedding_model configured")
                return []
            embedding = [self._get_embedding(query.query_str, text_type="query")]

        if not embedding or len(embedding[0]) == 0:
            return []

        top_k = query.similarity_top_k or self.similarity_top_k
        try:
            import weaviate.classes as wvc
        except ImportError:
            return []

        try:
            results = collection.query.near_vector(
                near_vector=embedding[0],
                limit=top_k,
                return_metadata=wvc.query.MetadataQuery(distance=True),
                return_properties=["text", "metadata_json"],
            )
        except Exception:
            logger.exception("Weaviate query failed")
            return []

        documents: List[Document] = []
        for obj in results.objects:
            props = obj.properties or {}
            metadata = {}
            raw_meta = props.get("metadata_json")
            if raw_meta:
                try:
                    metadata = json.loads(raw_meta)
                except (ValueError, TypeError):
                    metadata = {}
            if obj.metadata and obj.metadata.distance is not None:
                metadata["score"] = obj.metadata.distance
            documents.append(Document(
                text=props.get("text", ""),
                metadata=metadata,
            ))
        return documents

    def upsert_document(self, documents: List[Document], **kwargs) -> None:
        # Weaviate v4 insert with a uuid replaces existing objects, so upsert
        # is equivalent to insert.
        self.insert_document(documents, **kwargs)

    def update_document(self, documents: List[Document], **kwargs) -> None:
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs) -> None:
        collection = self.collection
        if collection is None:
            return
        try:
            collection.data.delete_by_id(uuid=str(document_id))
        except Exception:
            logger.exception("Weaviate delete failed for id %s", document_id)

    def get_document_count(self) -> int:
        collection = self.collection
        if collection is None:
            return 0
        try:
            result = collection.aggregate.over_all(total_count=True)
            return result.total_count or 0
        except Exception:
            logger.exception("Weaviate count failed")
            return 0

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        collection = self.collection
        if collection is None:
            return None
        try:
            obj = collection.query.fetch_object_by_id(uuid=str(document_id))
        except Exception:
            logger.exception("Weaviate fetch_by_id failed for %s", document_id)
            return None
        if obj is None:
            return None
        props = obj.properties or {}
        metadata = {}
        raw_meta = props.get("metadata_json")
        if raw_meta:
            try:
                metadata = json.loads(raw_meta)
            except (ValueError, TypeError):
                metadata = {}
        return Document(text=props.get("text", ""), metadata=metadata)

    def list_document_ids(self) -> List[str]:
        collection = self.collection
        if collection is None:
            return []
        try:
            result = collection.query.fetch_objects(
                limit=10000,
                return_properties=[],
            )
            return [str(obj.uuid) for obj in result.objects]
        except Exception:
            logger.exception("Weaviate list ids failed")
            return []
