"""Opt-in dense/sparse Qdrant retrieval; vectors are explicitly supplied by callers."""

import hashlib
import json
import math
import re
import uuid
from copy import deepcopy
from threading import Lock
from typing import ClassVar, Literal

from pydantic import Field, PrivateAttr, StrictBool, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store


class QdrantHybridStore(Store):
    """Own a dedicated dense/sparse collection, leaving the legacy Store unchanged.

    Write both vectors together. Document.embedding is dense; metadata.qdrant_sparse
    supplies indices/values. Queries supply embeddings[0] and ext_info.sparse_vector.
    No implicit model downloads, cloud inference or invented sparse vocabulary.
    """

    connection_args: dict = Field(default_factory=dict)
    collection_name: StrictStr = "agentuniverse_hybrid"
    dimensions: StrictInt = 384
    create_collection: StrictBool = False
    mode: Literal["dense", "sparse", "hybrid"] = "hybrid"
    similarity_top_k: StrictInt = 10
    candidate_k: StrictInt = 50
    with_vectors: StrictBool = False
    max_documents: StrictInt = 500
    max_sparse_terms: StrictInt = 10000
    max_text_chars: StrictInt = 100000
    max_payload_bytes: StrictInt = 10000000
    max_result_chars: StrictInt = 2000000
    timeout_seconds: StrictInt = 30

    DENSE: ClassVar[str] = "au_dense"
    SPARSE: ClassVar[str] = "au_sparse"
    _OPTIONS: ClassVar[tuple] = (
        "connection_args",
        "collection_name",
        "dimensions",
        "create_collection",
        "mode",
        "similarity_top_k",
        "candidate_k",
        "with_vectors",
        "max_documents",
        "max_sparse_terms",
        "max_text_chars",
        "max_payload_bytes",
        "max_result_chars",
        "timeout_seconds",
    )
    _client_lock: Lock = PrivateAttr(default_factory=Lock)

    @staticmethod
    def _dependencies():
        try:
            from qdrant_client import AsyncQdrantClient, QdrantClient, models
        except ImportError as error:
            raise ImportError("Install agentuniverse[qdrant_hybrid_ext] on Python 3.10–3.12") from error
        return QdrantClient, AsyncQdrantClient, models

    def _validate(self):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", self.collection_name):
            raise ValueError("collection_name must be a simple dedicated collection name")
        for key, upper in (
            ("dimensions", 65536),
            ("similarity_top_k", 1000),
            ("candidate_k", 1000),
            ("max_documents", 10000),
            ("max_sparse_terms", 100000),
            ("max_text_chars", 10000000),
            ("max_payload_bytes", 100000000),
            ("max_result_chars", 100000000),
            ("timeout_seconds", 300),
        ):
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= upper:
                raise ValueError(key + " must be a positive bounded integer")
        if self.similarity_top_k > self.candidate_k:
            raise ValueError("similarity_top_k cannot exceed candidate_k")
        if self.mode not in ("dense", "sparse", "hybrid"):
            raise ValueError("invalid retrieval mode")
        if type(self.create_collection) is not bool or type(self.with_vectors) is not bool:
            raise ValueError("create_collection/with_vectors must be Boolean")
        if not isinstance(self.connection_args, dict):
            raise ValueError("connection_args must be a mapping")

    def _initialize_by_component_configer(self, config):
        candidate = QdrantHybridStore(
            **{key: deepcopy(getattr(config, key, getattr(self, key))) for key in self._OPTIONS}
        )
        candidate._validate()
        for key in self._OPTIONS:
            setattr(self, key, getattr(candidate, key))
        return super()._initialize_by_component_configer(config)

    def _client_args(self):
        return {"url": "https://localhost:6333", "timeout": self.timeout_seconds, **self.connection_args}

    def _new_client(self):
        self._validate()
        self.client = self._dependencies()[0](**self._client_args())
        return self.client

    def _new_async_client(self):
        self._validate()
        self.async_client = self._dependencies()[1](**self._client_args())
        return self.async_client

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    async def aclose(self):
        if self.async_client is not None:
            await self.async_client.close()
            self.async_client = None

    def _schema(self):
        models = self._dependencies()[2]
        return {
            "collection_name": self.collection_name,
            "vectors_config": {self.DENSE: models.VectorParams(size=self.dimensions, distance=models.Distance.COSINE)},
            "sparse_vectors_config": {self.SPARSE: models.SparseVectorParams()},
            "timeout": self.timeout_seconds,
        }

    def _check_schema(self, info):
        models = self._dependencies()[2]
        dense = info.config.params.vectors
        sparse = info.config.params.sparse_vectors or {}
        if not isinstance(dense, dict) or set(dense) != {self.DENSE} or set(sparse) != {self.SPARSE}:
            raise ValueError("collection must contain exactly the dedicated dense/sparse vector names")
        if dense[self.DENSE].size != self.dimensions or dense[self.DENSE].distance != models.Distance.COSINE:
            raise ValueError("incompatible dense vector dimension/distance")
        if dense[self.DENSE].multivector_config is not None:
            raise ValueError("multivector collections are not supported")
        if sparse[self.SPARSE].modifier is not None:
            raise ValueError("sparse modifier must be unset; caller supplies final sparse weights")

    def _ready(self):
        self._validate()
        with self._client_lock:
            client = self.client if self.client is not None else self._new_client()
        if self.create_collection and not client.collection_exists(self.collection_name):
            # Provision once before concurrent workers; racing creation is an explicit error.
            client.create_collection(**self._schema())
        self._check_schema(client.get_collection(self.collection_name))
        return client

    async def _async_ready(self):
        self._validate()
        client = self.async_client if self.async_client is not None else self._new_async_client()
        if self.create_collection and not await client.collection_exists(self.collection_name):
            await client.create_collection(**self._schema())
        self._check_schema(await client.get_collection(self.collection_name))
        return client

    @staticmethod
    def _point_id(identity):
        if not isinstance(identity, str) or not identity or len(identity.encode()) > 512:
            raise ValueError("document ID must be a nonempty string of at most 512 UTF-8 bytes")
        # Map ALL IDs, including UUID-looking strings, into this component's namespace.
        return str(uuid.uuid5(uuid.NAMESPACE_URL, "agentuniverse:qdrant-hybrid:" + identity))

    def _dense(self, vector):
        if not isinstance(vector, (list, tuple)) or len(vector) != self.dimensions:
            raise ValueError("dense vector dimension mismatch")
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in vector):
            raise ValueError("dense vector must contain finite numbers")
        norm = math.hypot(*vector)
        if not norm or not math.isfinite(norm):
            raise ValueError("dense cosine vector must have a finite nonzero norm")
        return [value / norm for value in vector]

    def _sparse(self, value):
        if not isinstance(value, dict) or set(value) != {"indices", "values"}:
            raise ValueError("sparse vector requires exactly indices and values")
        indices, values = value["indices"], value["values"]
        if (
            not isinstance(indices, list)
            or not isinstance(values, list)
            or not 1 <= len(indices) <= self.max_sparse_terms
            or len(indices) != len(values)
        ):
            raise ValueError("sparse indices/values must be nonempty bounded lists of equal length")
        if any(type(index) is not int or not 0 <= index <= 4294967295 for index in indices) or len(set(indices)) != len(
            indices
        ):
            raise ValueError("sparse indices must be unique uint32 integers")
        if any(
            type(v) not in (int, float) or not math.isfinite(v) or not 1.1754944e-38 <= abs(v) <= 3.4028234e38
            for v in values
        ):
            raise ValueError("sparse weights must be finite nonzero float32-representable values")
        pairs = sorted(zip(indices, values))
        models = self._dependencies()[2]
        return models.SparseVector(indices=[p[0] for p in pairs], values=[float(p[1]) for p in pairs])

    @staticmethod
    def _token(key, value):
        if not isinstance(key, str) or type(value) not in (str, int, float, bool, type(None)):
            raise ValueError("filters require string keys and scalar JSON values")
        return hashlib.sha256(json.dumps([key, type(value).__name__, value], allow_nan=False).encode()).hexdigest()

    def _points(self, documents, kwargs):
        self._validate()
        if kwargs or not isinstance(documents, list) or len(documents) > self.max_documents:
            raise ValueError("unsupported arguments or oversized document batch")
        if not documents:
            return []
        models = self._dependencies()[2]
        points, ids = [], set()
        for document in deepcopy(documents):
            point_id = self._point_id(document.id)
            if point_id in ids:
                raise ValueError("duplicate document ID in batch")
            ids.add(point_id)
            if not isinstance(document.text, str) or len(document.text) > self.max_text_chars:
                raise ValueError("invalid or oversized document text")
            metadata = document.metadata or {}
            if "qdrant_retrieval" in metadata:
                raise ValueError("qdrant_retrieval is reserved result metadata")
            sparse = self._sparse(metadata.pop("qdrant_sparse", None))
            dense = self._dense(document.embedding)
            tokens = [
                self._token(key, value)
                for key, value in metadata.items()
                if type(value) in (str, int, float, bool, type(None))
            ]
            payload = {
                "id": document.id,
                "text": document.text,
                "metadata": metadata,
                "_au_qdrant_hybrid": 1,
                "_au_filters": tokens,
            }
            points.append(
                models.PointStruct(id=point_id, vector={self.DENSE: dense, self.SPARSE: sparse}, payload=payload)
            )
        if len(json.dumps([p.model_dump() for p in points], allow_nan=False).encode()) > self.max_payload_bytes:
            raise ValueError("encoded write exceeds byte budget")
        return points

    def _outcome(self, result):
        models = self._dependencies()[2]
        if result.status != models.UpdateStatus.COMPLETED:
            raise RuntimeError("Qdrant write not confirmed complete; reconcile stored IDs before retrying")
        return {"status": result.status.value, "operation_id": result.operation_id}

    def upsert_document(self, documents, **kwargs):
        points = self._points(documents, kwargs)
        if not points:
            return {"status": "completed", "operation_id": None}
        return self._outcome(self._ready().upsert(collection_name=self.collection_name, points=points, wait=True))

    # Match the legacy Qdrant component's idempotent upsert semantics.
    def insert_document(self, documents, **kwargs):
        return self.upsert_document(documents, **kwargs)

    def update_document(self, documents, **kwargs):
        return self.upsert_document(documents, **kwargs)

    async def async_upsert_document(self, documents, **kwargs):
        points = self._points(documents, kwargs)
        if not points:
            return {"status": "completed", "operation_id": None}
        client = await self._async_ready()
        return self._outcome(await client.upsert(collection_name=self.collection_name, points=points, wait=True))

    async def async_insert_document(self, documents, **kwargs):
        return await self.async_upsert_document(documents, **kwargs)

    async def async_update_document(self, documents, **kwargs):
        return await self.async_upsert_document(documents, **kwargs)

    def delete_document(self, document_id, **kwargs):
        if kwargs:
            raise ValueError("unsupported delete arguments")
        identity = self._point_id(document_id)
        return self._outcome(
            self._ready().delete(
                collection_name=self.collection_name,
                points_selector=[identity],
                wait=True,
            )
        )

    async def async_delete_document(self, document_id, **kwargs):
        if kwargs:
            raise ValueError("unsupported delete arguments")
        identity = self._point_id(document_id)
        client = await self._async_ready()
        return self._outcome(
            await client.delete(
                collection_name=self.collection_name,
                points_selector=[identity],
                wait=True,
            )
        )

    def _request(self, query, kwargs):
        self._validate()
        if kwargs or query.query_text_bundles or query.query_image_bundles:
            raise ValueError("only explicit single-vector queries are supported")
        q = deepcopy(query)
        top = self.similarity_top_k if q.similarity_top_k is None else q.similarity_top_k
        if type(top) is not int or not 0 <= top <= self.candidate_k:
            raise ValueError("top_k must be between zero and candidate_k")
        if set(q.ext_info) - {"sparse_vector", "filters"}:
            raise ValueError("only ext_info.sparse_vector/filters are supported")
        if top == 0:
            return None
        filters = q.ext_info.get("filters", {})
        if (
            not isinstance(filters, dict)
            or len(filters) > 64
            or len(json.dumps(filters, allow_nan=False).encode()) > self.max_payload_bytes
        ):
            raise ValueError("filters exceed mapping/count/byte limits")
        models = self._dependencies()[2]
        conditions = [models.FieldCondition(key="_au_qdrant_hybrid", match=models.MatchValue(value=1))]
        conditions += [
            models.FieldCondition(key="_au_filters", match=models.MatchValue(value=self._token(k, v)))
            for k, v in filters.items()
        ]
        query_filter = models.Filter(must=conditions)
        request = {
            "collection_name": self.collection_name,
            "query_filter": query_filter,
            "limit": top,
            "with_payload": True,
            "with_vectors": self.with_vectors,
            "timeout": self.timeout_seconds,
        }
        dense, sparse = None, None
        if self.mode in ("dense", "hybrid"):
            if len(q.embeddings) != 1:
                raise ValueError("dense/hybrid mode requires one explicit dense embedding")
            dense = self._dense(q.embeddings[0])
        if self.mode in ("sparse", "hybrid"):
            sparse = self._sparse(q.ext_info.get("sparse_vector"))
        if self.mode == "hybrid":
            request.update(
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                prefetch=[
                    models.Prefetch(query=dense, using=self.DENSE, filter=query_filter, limit=self.candidate_k),
                    models.Prefetch(query=sparse, using=self.SPARSE, filter=query_filter, limit=self.candidate_k),
                ],
            )
        else:
            request.update(
                query=dense if self.mode == "dense" else sparse,
                using=self.DENSE if self.mode == "dense" else self.SPARSE,
            )
        return request

    def _documents(self, response):
        documents, seen, total = [], set(), 0
        for point in response.points:
            payload = point.payload or {}
            identity = payload.get("id")
            if payload.get("_au_qdrant_hybrid") != 1 or self._point_id(identity) != str(point.id):
                raise RuntimeError("incompatible/corrupt Qdrant document identity")
            if identity in seen:
                raise RuntimeError("duplicate document in query response")
            seen.add(identity)
            text = payload.get("text")
            if not isinstance(text, str) or not math.isfinite(point.score):
                raise RuntimeError("invalid Qdrant result payload/score")
            total += len(text)
            if total > self.max_result_chars:
                raise ValueError("result text exceeds byte-independent character budget")
            metadata = deepcopy(payload.get("metadata") or {})
            embedding = []
            if self.with_vectors:
                vectors = point.vector or {}
                embedding = list(vectors[self.DENSE])
                metadata["qdrant_sparse"] = vectors[self.SPARSE].model_dump()
            metadata["qdrant_retrieval"] = {"mode": self.mode, "score": point.score, "candidate_k": self.candidate_k}
            documents.append(Document(id=identity, text=text, metadata=metadata, embedding=embedding))
        # Preserve Qdrant's native fusion ordering; tied top-k membership is engine-defined.
        return documents

    def query(self, query: Query, **kwargs):
        request = self._request(query, kwargs)
        return [] if request is None else self._documents(self._ready().query_points(**request))

    async def async_query(self, query: Query, **kwargs):
        request = self._request(query, kwargs)
        if request is None:
            return []
        client = await self._async_ready()
        return self._documents(await client.query_points(**request))
