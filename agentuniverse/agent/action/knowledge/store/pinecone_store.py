#!/usr/bin/env python3
"""Pinecone vector knowledge store.

Pinecone (https://www.pinecone.io) is a fully-managed, cloud-native vector
database. This store wraps the v3 ``pinecone`` client API to provide insert,
query, upsert, update, delete, and inspection capabilities with configurable
vector dimensions, distance metrics, optional on-demand embedding through a
registered aU embedding component, and bounded resource usage
(``similarity_top_k``).
"""

# Validation failures surface as ValueError at the public boundary.
# ruff: noqa: TRY003

import json
import logging
import os
import re
from typing import Any, ClassVar, List, Optional

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import \
    EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class PineconeStore(Store):
    """Vector store backed by Pinecone (v3 client API).

    Attributes:
        api_key: Pinecone API key. If not set, the ``PINECONE_API_KEY``
            environment variable is used.
        environment: Pinecone environment / cloud region hint, e.g.
            ``aws-us-east-1``. Used to build the serverless spec when the
            store must create the index.
        index_host: Fully-qualified host of an existing Pinecone index, e.g.
            ``my-index-xyz.svc.us-east-1-aws.pinecone.io``. When set, the
            store connects directly without listing indexes.
        index_name: Pinecone index name.
        embedding_model: Name of a registered aU embedding component used to
            embed documents / queries on demand.
        dimensions: Vector dimension. If ``None``, inferred from the first
            inserted document.
        distance: Distance metric — ``cosine``, ``euclidean``, or
            ``dotproduct``.
        similarity_top_k: Default number of results returned by ``query``.
        namespace: Optional Pinecone namespace used to partition records.
    """

    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_host: Optional[str] = None
    index_name: str = "agentuniverse-documents"
    embedding_model: Optional[str] = None
    dimensions: Optional[int] = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    namespace: str = ""

    client: Any = None
    _index: Any = None

    _INDEX_NAME: ClassVar["re.Pattern[str]"] = re.compile(
        r"^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
    )
    _DISTANCES: ClassVar[dict] = {
        "cosine": "cosine",
        "euclidean": "euclidean",
        "dotproduct": "dotproduct",
    }

    # ------------------------------------------------------------------ #
    # Configuration & lifecycle
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) \
            -> "PineconeStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "api_key", "environment", "index_host", "index_name",
            "embedding_model", "dimensions", "distance",
            "similarity_top_k", "namespace",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCES:
            raise ValueError(
                f"distance must be one of {list(self._DISTANCES.keys())}, "
                f"got {self.distance!r}")
        if (isinstance(self.similarity_top_k, bool)
                or not isinstance(self.similarity_top_k, int)
                or self.similarity_top_k <= 0):
            raise ValueError("similarity_top_k must be a positive integer")
        if self.dimensions is not None:
            if (isinstance(self.dimensions, bool)
                    or not isinstance(self.dimensions, int)
                    or self.dimensions <= 0):
                raise ValueError("dimensions must be a positive integer")
        if self.namespace is not None and not isinstance(self.namespace, str):
            raise TypeError("namespace must be a string")

    # ------------------------------------------------------------------ #
    # Client management
    # ------------------------------------------------------------------ #
    def _resolve_api_key(self) -> str:
        value = self.api_key or os.getenv("PINECONE_API_KEY")
        if not value:
            raise ValueError(
                "api_key is required; set it in YAML or the PINECONE_API_KEY "
                "environment variable")
        return value

    def _new_client(self) -> Any:
        try:
            from pinecone import Pinecone, ServerlessSpec
        except ImportError as exc:  # pragma: no cover - lazy import
            raise ImportError(
                "pinecone is not installed. Install it with "
                "'pip install pinecone'.") from exc
        self.client = Pinecone(api_key=self._resolve_api_key())
        if self.index_host:
            # A fully-qualified host bypasses the describe-index lookup.
            self._index = self.client.Index(host=self.index_host,
                                            index_name=self.index_name)
        else:
            self._ensure_index()
        return self.client

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    @property
    def index(self) -> Any:
        if self._index is None:
            self._ensure_client()
        return self._index

    def _ensure_index(self) -> None:
        """Create the index if it does not exist, or connect to it."""
        from pinecone import ServerlessSpec

        client = self.client
        existing: List[str] = []
        try:
            existing = list(client.list_indexes().names())
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to list Pinecone indexes")

        if self.index_name in existing:
            self._index = client.Index(self.index_name)
            return

        if self.dimensions is None:
            raise ValueError(
                "dimensions must be configured before creating a Pinecone "
                "index, or set index_host to connect to an existing index")

        cloud, region = self._serverless_spec()
        client.create_index(
            name=self.index_name,
            dimension=self.dimensions,
            metric=self._DISTANCES[self.distance],
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        self._index = client.Index(self.index_name)

    def _serverless_spec(self) -> tuple:
        """Parse the environment hint into a (cloud, region) pair.

        Accepts ``cloud-region`` (e.g. ``aws-us-east-1``); the first token is
        treated as the cloud provider and the remainder as the region.
        Defaults to ``aws`` / ``us-east-1`` when unset.
        """
        env = (self.environment or "aws-us-east-1").strip().lower()
        if "-" in env:
            cloud, _, region = env.partition("-")
            return cloud or "aws", region or "us-east-1"
        return "aws", env

    # ------------------------------------------------------------------ #
    # Embedding resolution & dimension validation
    # ------------------------------------------------------------------ #
    def _get_embedding(self, text: str, text_type: str = "document") \
            -> List[float]:
        if not self.embedding_model:
            raise ValueError(
                "No embedding model configured. Set embedding_model on the "
                "PineconeStore component or provide embeddings in Documents.")
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
    # CRUD
    # ------------------------------------------------------------------ #
    def _metadata_payload(self, document: Document) -> dict:
        return {
            "text": document.text or "",
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

    def insert_document(self, documents: List[Document], **kwargs) -> None:
        if not documents:
            return
        self.upsert_document(documents, **kwargs)

    def upsert_document(self, documents: List[Document], **kwargs) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        index = self.index
        records = []
        for document, vector in zip(documents, vectors, strict=True):
            records.append((str(document.id), vector,
                            self._metadata_payload(document)))
        index.upsert(vectors=records, namespace=self.namespace or "")

    def update_document(self, documents: List[Document], **kwargs) -> None:
        self.upsert_document(documents, **kwargs)

    def query(self, query: Query, **kwargs) -> List[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        index = self.index
        filter_expr = kwargs.get("metadata_filter")
        query_kwargs: dict = {
            "vector": vector,
            "top_k": top_k,
            "include_metadata": True,
            "namespace": self.namespace or "",
        }
        if filter_expr is not None:
            if not isinstance(filter_expr, dict):
                raise TypeError("metadata_filter must be an object")
            query_kwargs["filter"] = filter_expr
        try:
            response = index.query(**query_kwargs)
        except Exception:
            logger.exception("Pinecone query failed")
            return []
        return self._matches_to_documents(response)

    def _matches_to_documents(self, response: Any) -> List[Document]:
        matches: list = []
        try:
            matches = response.get("matches", []) if isinstance(response, dict) \
                else getattr(response, "matches", []) or []
        except AttributeError:
            matches = []
        documents: List[Document] = []
        for match in matches:
            is_dict = isinstance(match, dict)
            metadata = match.get("metadata", {}) if is_dict \
                else getattr(match, "metadata", {}) or {}
            score = match.get("score") if is_dict \
                else getattr(match, "score", None)
            text = metadata.pop("text", "") if isinstance(metadata, dict) \
                else getattr(metadata, "text", "")
            decoded = self._decode_metadata(
                metadata.get("metadata_json")) if isinstance(metadata, dict) \
                else {}
            if score is not None:
                decoded["score"] = score
            match_id = match.get("id") if is_dict \
                else getattr(match, "id", None)
            documents.append(Document(
                id=str(match_id) if match_id is not None else None,
                text=text or "",
                metadata=decoded,
            ))
        return documents

    def delete_document(self, document_id: str, **kwargs) -> None:
        index = self.index
        try:
            index.delete(ids=[str(document_id)],
                         namespace=self.namespace or "")
        except Exception:
            logger.exception("Pinecone delete failed for id %s", document_id)

    def get_document_count(self) -> int:
        index = self.index
        try:
            stats = index.describe_index_stats(
                namespace=self.namespace or "")
        except Exception:
            logger.exception("Pinecone describe_index_stats failed")
            return 0
        try:
            namespaces = stats.get("namespaces", {}) if isinstance(stats, dict) \
                else getattr(stats, "namespaces", {}) or {}
            if self.namespace and self.namespace in namespaces:
                ns = namespaces[self.namespace]
                return ns.get("vector_count", 0) if isinstance(ns, dict) \
                    else getattr(ns, "vector_count", 0)
            total = 0
            for ns in namespaces.values():
                total += ns.get("vector_count", 0) if isinstance(ns, dict) \
                    else getattr(ns, "vector_count", 0)
            return total
        except Exception:
            logger.exception("Pinecone count parse failed")
            return 0

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        index = self.index
        try:
            response = index.fetch(ids=[str(document_id)],
                                   namespace=self.namespace or "")
        except Exception:
            logger.exception("Pinecone fetch failed for %s", document_id)
            return None
        try:
            vectors = response.get("vectors", {}) if isinstance(response, dict) \
                else getattr(response, "vectors", {}) or {}
        except Exception:
            return None
        if not vectors:
            return None
        # fetch returns a dict keyed by id; take the matching record.
        key = str(document_id)
        record = vectors.get(key) or next(iter(vectors.values()))
        metadata = record.get("metadata", {}) if isinstance(record, dict) \
            else getattr(record, "metadata", {}) or {}
        text = metadata.pop("text", "") if isinstance(metadata, dict) \
            else getattr(metadata, "text", "")
        decoded = self._decode_metadata(
            metadata.get("metadata_json")) if isinstance(metadata, dict) \
            else {}
        return Document(id=key, text=text or "", metadata=decoded)

    def list_document_ids(self) -> List[str]:
        """Return up to 10000 document ids in the namespace.

        Pinecone does not provide a native list-all; we approximate it by
        querying against a zero vector and returning the matched ids.
        """
        index = self.index
        if self.dimensions is None:
            logger.warning("Cannot list ids: dimensions unknown")
            return []
        zero_vector = [0.0] * self.dimensions
        try:
            response = index.query(
                vector=zero_vector,
                top_k=10000,
                include_values=False,
                include_metadata=False,
                namespace=self.namespace or "",
            )
        except Exception:
            logger.exception("Pinecone list ids failed")
            return []
        ids: List[str] = []
        try:
            matches = response.get("matches", []) if isinstance(response, dict) \
                else getattr(response, "matches", []) or []
        except Exception:
            return ids
        for match in matches:
            mid = match.get("id") if isinstance(match, dict) \
                else getattr(match, "id", None)
            if mid is not None:
                ids.append(str(mid))
        return ids
