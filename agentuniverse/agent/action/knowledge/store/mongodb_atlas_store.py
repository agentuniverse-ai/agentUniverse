#!/usr/bin/env python3
"""MongoDB Atlas Vector Search knowledge store.

MongoDB Atlas (https://www.mongodb.com/atlas) provides vector search via the
``$vectorSearch`` aggregation pipeline stage. This store wraps the ``pymongo``
client to provide insert, query, upsert, update, delete, and inspection
capabilities with configurable vector dimensions, similarity functions
(``cosine`` / ``euclidean`` / ``dotProduct``), optional on-demand embedding
through a registered aU embedding component, optional metadata filtering,
and bounded resource usage (``similarity_top_k``).

The collection is expected to live on a cluster with a configured Atlas
Vector Search index named ``vector_index`` over the configured
``vector_field``. The store will create the underlying collection if it does
not exist; the search index itself must be provisioned in the Atlas UI / via
the Atlas Administration API.
"""

# Validation failures surface as ValueError at the public boundary.
# ruff: noqa: TRY003

import json
import logging
import os
from typing import Any, ClassVar, List, Optional

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import \
    EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class MongoDBAtlasStore(Store):
    """Vector store backed by MongoDB Atlas Vector Search.

    Attributes:
        connection_url: MongoDB connection string. If not set, the
            ``MONGODB_ATLAS_URI`` environment variable is used.
        database_name: MongoDB database that holds the collection.
        collection_name: MongoDB collection used to store documents.
        embedding_model: Name of a registered aU embedding component used to
            embed documents / queries on demand.
        dimensions: Vector dimension. If ``None``, inferred from the first
            inserted document.
        similarity: Similarity function used by ``$vectorSearch`` —
            ``cosine``, ``euclidean``, or ``dotProduct``.
        similarity_top_k: Default number of results returned by ``query``.
        vector_field: Field name that stores the embedding vector.
        text_field: Field name that stores the document text.
        index_name: Name of the Atlas Vector Search index (default
            ``vector_index``).
    """

    connection_url: Optional[str] = None
    database_name: str = "agentuniverse"
    collection_name: str = "documents"
    embedding_model: Optional[str] = None
    dimensions: Optional[int] = None
    similarity: str = "cosine"
    similarity_top_k: int = 10
    vector_field: str = "embedding"
    text_field: str = "text"
    index_name: str = "vector_index"

    client: Any = None
    _collection: Any = None

    _SIMILARITIES: ClassVar[dict] = {
        "cosine": "cosine",
        "euclidean": "euclidean",
        "dotproduct": "dotProduct",
        "dot": "dotProduct",
    }

    # ------------------------------------------------------------------ #
    # Configuration & lifecycle
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) \
            -> "MongoDBAtlasStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "connection_url", "database_name", "collection_name",
            "embedding_model", "dimensions", "similarity",
            "similarity_top_k", "vector_field", "text_field", "index_name",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        if not self.database_name or not isinstance(self.database_name, str):
            raise ValueError("database_name must be a non-empty string")
        if not self.collection_name or not isinstance(self.collection_name, str):
            raise ValueError("collection_name must be a non-empty string")
        self.similarity = (self.similarity or "").lower()
        if self.similarity not in self._SIMILARITIES:
            raise ValueError(
                f"similarity must be one of {list(self._SIMILARITIES.keys())}, "
                f"got {self.similarity!r}")
        if (isinstance(self.similarity_top_k, bool)
                or not isinstance(self.similarity_top_k, int)
                or self.similarity_top_k <= 0):
            raise ValueError("similarity_top_k must be a positive integer")
        if self.dimensions is not None:
            if (isinstance(self.dimensions, bool)
                    or not isinstance(self.dimensions, int)
                    or self.dimensions <= 0):
                raise ValueError("dimensions must be a positive integer")
        for name in ("vector_field", "text_field", "index_name"):
            value = getattr(self, name)
            if not value or not isinstance(value, str):
                raise ValueError(f"{name} must be a non-empty string")

    # ------------------------------------------------------------------ #
    # Client management
    # ------------------------------------------------------------------ #
    def _resolve_connection_url(self) -> str:
        value = self.connection_url or os.getenv("MONGODB_ATLAS_URI")
        if not value:
            raise ValueError(
                "connection_url is required; set it in YAML or the "
                "MONGODB_ATLAS_URI environment variable")
        return value

    def _new_client(self) -> Any:
        try:
            from pymongo import MongoClient
        except ImportError as exc:  # pragma: no cover - lazy import
            raise ImportError(
                "pymongo is not installed. Install it with "
                "'pip install pymongo'.") from exc
        self.client = MongoClient(self._resolve_connection_url())
        # Trigger a cheap round-trip so connection errors surface early.
        try:
            self.client.admin.command("ping")
        except Exception:  # pragma: no cover - network-dependent
            logger.exception("MongoDB Atlas ping failed")
        database = self.client[self.database_name]
        # Create the collection lazily; insert will create it implicitly, but
        # we materialise it so list_collection_names / counts behave.
        if self.collection_name not in database.list_collection_names():
            try:
                database.create_collection(self.collection_name)
            except Exception:  # pragma: no cover - already exists race
                pass
        self._collection = database[self.collection_name]
        return self.client

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    @property
    def collection(self) -> Any:
        if self._collection is None:
            self._ensure_client()
        return self._collection

    # ------------------------------------------------------------------ #
    # Embedding resolution & dimension validation
    # ------------------------------------------------------------------ #
    def _get_embedding(self, text: str, text_type: str = "document") \
            -> List[float]:
        if not self.embedding_model:
            raise ValueError(
                "No embedding model configured. Set embedding_model on the "
                "MongoDBAtlasStore component or provide embeddings in "
                "Documents.")
        emb = EmbeddingManager().get_instance_obj(self.embedding_model,
                                                  strict=True)
        embeddings = emb.get_embeddings([text], text_type=text_type)
        if not embeddings:
            raise ValueError("Embedding model returned no vectors")
        return embeddings[0]

    def _check_vector(self, vector: Any) -> None:
        if (not isinstance(vector, list)
                or not vector
                or any(isinstance(v, bool) or not isinstance(v, (int, float))
                       for v in vector)):
            raise ValueError("embedding must be a non-empty numeric list")
        if self.dimensions is None:
            self.dimensions = len(vector)
        if len(vector) != self.dimensions:
            raise ValueError(
                f"embedding dimension {len(vector)} does not match configured "
                f"dimensions {self.dimensions}")

    def _vectors_for_documents(self, documents: List[Document]) \
            -> List[List[float]]:
        missing = [i for i, d in enumerate(documents) if not d.embedding]
        if missing:
            if not self.embedding_model:
                raise ValueError(
                    "documents without embeddings require embedding_model")
            model = EmbeddingManager().get_instance_obj(self.embedding_model,
                                                        strict=True)
            generated = model.get_embeddings(
                [documents[i].text or "" for i in missing])
            for i, vec in zip(missing, generated, strict=True):
                documents[i].embedding = vec
        vectors = [d.embedding for d in documents]
        for vec in vectors:
            self._check_vector(vec)
        return vectors

    def _embedding_for_query(self, query: Query) -> List[float]:
        if query.embeddings:
            vector = query.embeddings[0]
        elif self.embedding_model and query.query_str:
            vector = self._get_embedding(query.query_str, text_type="query")
        else:
            raise ValueError(
                "query requires embeddings or an embedding_model plus "
                "query_str")
        self._check_vector(vector)
        return vector

    def _top_k(self, query: Query) -> int:
        value = query.similarity_top_k or self.similarity_top_k
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("similarity_top_k must be a positive integer")
        return value

    # ------------------------------------------------------------------ #
    # Document <-> BSON mapping
    # ------------------------------------------------------------------ #
    def _to_doc(self, document: Document, vector: List[float]) -> dict:
        return {
            "_id": str(document.id),
            self.text_field: document.text or "",
            self.vector_field: [float(v) for v in vector],
            "metadata_json": json.dumps(document.metadata or {},
                                        default=str, ensure_ascii=False),
        }

    @staticmethod
    def _decode_metadata(raw: Any) -> dict:
        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}

    def _from_doc(self, record: dict, score: Any = None) -> Document:
        metadata = self._decode_metadata(record.get("metadata_json"))
        if score is not None:
            metadata["score"] = score
        return Document(
            id=str(record.get("_id")) if record.get("_id") is not None else None,
            text=record.get(self.text_field, "") or "",
            metadata=metadata,
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def insert_document(self, documents: List[Document], **kwargs) -> None:
        if not documents:
            return
        self.upsert_document(documents, **kwargs)

    def upsert_document(self, documents: List[Document], **kwargs) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        collection = self.collection
        for document, vector in zip(documents, vectors, strict=True):
            doc = self._to_doc(document, vector)
            collection.replace_one(
                {"_id": doc["_id"]}, doc, upsert=True)

    def update_document(self, documents: List[Document], **kwargs) -> None:
        self.upsert_document(documents, **kwargs)

    def query(self, query: Query, **kwargs) -> List[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        collection = self.collection
        filter_expr = kwargs.get("metadata_filter")
        pre_filter: Optional[dict] = None
        if filter_expr is not None:
            if not isinstance(filter_expr, dict):
                raise TypeError("metadata_filter must be an object")
            pre_filter = {"metadata_json": json.dumps(filter_expr)}
        pipeline = self._vector_search_pipeline(
            vector=vector, top_k=top_k, pre_filter=pre_filter)
        try:
            cursor = collection.aggregate(pipeline)
        except Exception:
            logger.exception("MongoDB Atlas vector search failed")
            return []
        documents: List[Document] = []
        for record in cursor:
            score = record.get("score")
            documents.append(self._from_doc(record, score=score))
        return documents

    def _vector_search_pipeline(self, vector: List[float], top_k: int,
                                pre_filter: Optional[dict]) -> List[dict]:
        vector_search: dict = {
            "index": self.index_name,
            "path": self.vector_field,
            "queryVector": [float(v) for v in vector],
            "numCandidates": max(top_k * 10, top_k),
            "limit": top_k,
        }
        if pre_filter is not None:
            vector_search["filter"] = pre_filter
        return [
            {"$vectorSearch": vector_search},
            {"$project": {
                "_id": 1,
                self.text_field: 1,
                "metadata_json": 1,
                "score": {"$meta": "vectorSearchScore"},
            }},
        ]

    def delete_document(self, document_id: str, **kwargs) -> None:
        collection = self.collection
        try:
            collection.delete_one({"_id": str(document_id)})
        except Exception:
            logger.exception("MongoDB delete failed for id %s", document_id)

    def get_document_count(self) -> int:
        collection = self.collection
        try:
            return collection.count_documents({})
        except Exception:
            logger.exception("MongoDB count_documents failed")
            return 0

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        collection = self.collection
        try:
            record = collection.find_one({"_id": str(document_id)})
        except Exception:
            logger.exception("MongoDB find_one failed for %s", document_id)
            return None
        if record is None:
            return None
        return self._from_doc(record)

    def list_document_ids(self) -> List[str]:
        collection = self.collection
        try:
            cursor = collection.find({}, {"_id": 1})
            return [str(record["_id"]) for record in cursor
                    if record.get("_id") is not None]
        except Exception:
            logger.exception("MongoDB list ids failed")
            return []
