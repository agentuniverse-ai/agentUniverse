#!/usr/bin/env python3
"""OpenSearch k-NN vector knowledge store."""

# Dynamic mapping names are validated before request construction.
# ruff: noqa: C901, TRY003

import math
import os
import re
from typing import Any, ClassVar

from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class OpenSearchVectorStore(Store):
    """Persistent sync/async vector store backed by OpenSearch k-NN."""

    connection_args: dict[str, Any] = Field(default_factory=dict)
    index_name: str = "agentuniverse-documents"
    embedding_model: str | None = None
    dimensions: int | None = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    create_index: bool = True
    refresh: bool | str = False
    filter_fields: list[str] = Field(default_factory=list)
    ef_construction: int = 128
    m: int = 16
    client: Any = None
    async_client: Any = None

    _INDEX: ClassVar[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
    _FIELD: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _SPACES: ClassVar[dict[str, str]] = {
        "cosine": "cosinesimil",
        "l2": "l2",
        "inner_product": "innerproduct",
    }

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "OpenSearchVectorStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "connection_args",
            "index_name",
            "embedding_model",
            "dimensions",
            "distance",
            "similarity_top_k",
            "create_index",
            "refresh",
            "filter_fields",
            "ef_construction",
            "m",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config(require_dimensions=False)
        return self

    def _validate_config(self, require_dimensions: bool = True) -> None:
        if not isinstance(self.connection_args, dict):
            raise TypeError("connection_args must be an object")
        if not self._INDEX.fullmatch(self.index_name or "") or self.index_name.startswith(("_", "-", "+")):
            raise ValueError("index_name must be a lowercase OpenSearch index identifier")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._SPACES:
            raise ValueError("distance must be cosine, l2, or inner_product")
        for name in ("similarity_top_k", "ef_construction", "m"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.dimensions is not None and (
            isinstance(self.dimensions, bool) or not isinstance(self.dimensions, int) or self.dimensions <= 0
        ):
            raise ValueError("dimensions must be a positive integer")
        if require_dimensions and self.dimensions is None:
            raise ValueError("dimensions must be configured or inferred from the first document")
        if not isinstance(self.filter_fields, list) or any(
            not isinstance(field, str) or not self._FIELD.fullmatch(field) for field in self.filter_fields
        ):
            raise ValueError("filter_fields must contain simple identifiers")
        if len(set(self.filter_fields)) != len(self.filter_fields):
            raise ValueError("filter_fields must not contain duplicates")
        if not isinstance(self.create_index, bool):
            raise TypeError("create_index must be a boolean")
        if not isinstance(self.refresh, (bool, str)):
            raise TypeError("refresh must be a boolean or string")

    @staticmethod
    def _dependencies() -> tuple[Any, Any]:
        try:
            from opensearchpy import AsyncOpenSearch, OpenSearch
        except ImportError as exc:
            raise ImportError("OpenSearchVectorStore requires opensearch-py") from exc
        return OpenSearch, AsyncOpenSearch

    def _new_client(self) -> Any:
        OpenSearch, _ = self._dependencies()
        self._validate_config(require_dimensions=False)
        self.client = OpenSearch(**self._resolved_connection_args())
        self.client.info()
        if self.create_index and self.dimensions:
            self._ensure_index(self.dimensions)
        return self.client

    async def _new_async_client(self) -> Any:
        _, AsyncOpenSearch = self._dependencies()
        self._validate_config(require_dimensions=False)
        self.async_client = AsyncOpenSearch(**self._resolved_connection_args())
        await self.async_client.info()
        if self.create_index and self.dimensions:
            await self._async_ensure_index(self.dimensions)
        return self.async_client

    def _resolved_connection_args(self) -> dict[str, Any]:
        args = dict(self.connection_args)
        url = os.getenv("OPENSEARCH_VECTOR_URL")
        if "hosts" not in args:
            args["hosts"] = [url] if url else [{"host": "localhost", "port": 9200}]
        return args

    def _ensure_client(self) -> Any:
        return self.client or self._new_client()

    async def _ensure_async_client(self) -> Any:
        return self.async_client or await self._new_async_client()

    def _mapping(self, dimensions: int) -> dict[str, Any]:
        self.dimensions = self.dimensions or dimensions
        if dimensions != self.dimensions:
            raise ValueError(f"embedding dimension {dimensions} does not match configured dimensions {self.dimensions}")
        self._validate_config()
        metadata_properties = {field: {"type": "keyword"} for field in self.filter_fields}
        return {
            "settings": {"index": {"knn": True}},
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {"type": "text"},
                    "metadata": {
                        "type": "object",
                        "dynamic": True,
                        "properties": metadata_properties,
                    },
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": self.dimensions,
                        "method": {
                            "name": "hnsw",
                            "space_type": self._SPACES[self.distance],
                            "engine": "lucene",
                            "parameters": {"ef_construction": self.ef_construction, "m": self.m},
                        },
                    },
                },
            },
        }

    def _ensure_index(self, dimensions: int) -> None:
        client = self._ensure_client()
        mapping = self._mapping(dimensions)
        if self.create_index and not client.indices.exists(index=self.index_name):
            client.indices.create(index=self.index_name, body=mapping)

    async def _async_ensure_index(self, dimensions: int) -> None:
        client = await self._ensure_async_client()
        mapping = self._mapping(dimensions)
        if self.create_index and not await client.indices.exists(index=self.index_name):
            await client.indices.create(index=self.index_name, body=mapping)

    def _embedding(self, document: Document) -> list[float]:
        vector = document.embedding
        if not vector and self.embedding_model:
            model = EmbeddingManager().get_instance_obj(self.embedding_model)
            vector = model.get_embeddings([document.text])[0]
        return self._validate_vector(vector, "document embedding")

    def _query_vector(self, query: Query) -> list[float]:
        embeddings = query.embeddings
        if not embeddings and self.embedding_model:
            model = EmbeddingManager().get_instance_obj(self.embedding_model)
            embeddings = model.get_embeddings([query.query_str], text_type="query")
        if not embeddings:
            raise ValueError("query requires embeddings or an embedding_model")
        return self._validate_vector(embeddings[0], "query embedding")

    def _validate_vector(self, vector: Any, field: str) -> list[float]:
        if not isinstance(vector, list) or not vector:
            raise ValueError(f"{field} must be a non-empty list")
        output = []
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{field} must contain finite numbers")
            output.append(float(value))
        if self.dimensions is not None and len(output) != self.dimensions:
            raise ValueError(
                f"embedding dimension {len(output)} does not match configured dimensions {self.dimensions}"
            )
        return output

    def insert_document(self, documents: list[Document], **kwargs) -> Any:
        return self.upsert_document(documents, **kwargs)

    def update_document(self, documents: list[Document], **kwargs) -> Any:
        return self.upsert_document(documents, **kwargs)

    def upsert_document(self, documents: list[Document], **kwargs) -> Any:
        prepared = self._prepare_documents(documents)
        if not prepared:
            return None
        self._ensure_index(len(prepared[0][1]))
        body = self._bulk_body(prepared)
        result = self._ensure_client().bulk(body=body, refresh=self.refresh)
        self._raise_bulk_errors(result)
        return result

    async def async_insert_document(self, documents: list[Document], **kwargs) -> Any:
        return await self.async_upsert_document(documents, **kwargs)

    async def async_update_document(self, documents: list[Document], **kwargs) -> Any:
        return await self.async_upsert_document(documents, **kwargs)

    async def async_upsert_document(self, documents: list[Document], **kwargs) -> Any:
        prepared = self._prepare_documents(documents)
        if not prepared:
            return None
        await self._async_ensure_index(len(prepared[0][1]))
        result = await (await self._ensure_async_client()).bulk(body=self._bulk_body(prepared), refresh=self.refresh)
        self._raise_bulk_errors(result)
        return result

    def _prepare_documents(self, documents: Any) -> list[tuple[Document, list[float]]]:
        if not isinstance(documents, list):
            raise TypeError("documents must be a list")
        prepared = []
        for document in documents:
            if not isinstance(document, Document):
                raise TypeError("documents must contain Document objects")
            prepared.append((document, self._embedding(document)))
        if prepared:
            dimensions = len(prepared[0][1])
            if any(len(vector) != dimensions for _, vector in prepared):
                raise ValueError("all document embeddings must have the same dimensions")
        return prepared

    def _bulk_body(self, prepared: list[tuple[Document, list[float]]]) -> list[dict[str, Any]]:
        body = []
        for document, vector in prepared:
            metadata = document.metadata or {}
            if not isinstance(metadata, dict):
                raise TypeError("document metadata must be an object")
            body.extend(
                (
                    {"index": {"_index": self.index_name, "_id": str(document.id)}},
                    {"id": str(document.id), "text": document.text or "", "metadata": metadata, "embedding": vector},
                )
            )
        return body

    @staticmethod
    def _raise_bulk_errors(result: Any) -> None:
        if isinstance(result, dict) and result.get("errors"):
            failures = [item for item in result.get("items", []) if next(iter(item.values())).get("error")]
            raise RuntimeError(f"OpenSearch bulk request failed for {len(failures)} document(s)")

    def delete_document(self, document_id: str, **kwargs) -> Any:
        if not isinstance(document_id, str) or not document_id:
            raise ValueError("document_id must be a non-empty string")
        return self._ensure_client().delete(
            index=self.index_name,
            id=document_id,
            refresh=self.refresh,
            ignore=[404],
        )

    async def async_delete_document(self, document_id: str, **kwargs) -> Any:
        if not isinstance(document_id, str) or not document_id:
            raise ValueError("document_id must be a non-empty string")
        return await (await self._ensure_async_client()).delete(
            index=self.index_name,
            id=document_id,
            refresh=self.refresh,
            ignore=[404],
        )

    def query(self, query: Query, **kwargs) -> list[Document]:
        vector, _top_k, body = self._query_request(query, kwargs.get("metadata_filter"))
        self._ensure_index(len(vector))
        result = self._ensure_client().search(index=self.index_name, body=body)
        return self._to_documents(result)

    async def async_query(self, query: Query, **kwargs) -> list[Document]:
        vector, _top_k, body = self._query_request(query, kwargs.get("metadata_filter"))
        await self._async_ensure_index(len(vector))
        result = await (await self._ensure_async_client()).search(index=self.index_name, body=body)
        return self._to_documents(result)

    def _query_request(self, query: Any, metadata_filter: Any) -> tuple[list[float], int, dict[str, Any]]:
        if not isinstance(query, Query):
            raise TypeError("query must be a Query object")
        vector = self._query_vector(query)
        top_k = query.similarity_top_k or self.similarity_top_k
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("similarity_top_k must be a positive integer")
        filters = self._metadata_filters(metadata_filter)
        vector_query: dict[str, Any] = {"vector": vector, "k": top_k}
        if filters:
            # Filtering inside the Lucene k-NN clause selects ``k`` nearest
            # matching documents. A surrounding bool filter is applied after
            # candidate selection and can therefore return fewer than ``k``.
            vector_query["filter"] = {"bool": {"filter": filters}}
        return vector, top_k, {"size": top_k, "query": {"knn": {"embedding": vector_query}}}

    def _metadata_filters(self, value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, dict):
            raise TypeError("metadata_filter must be an object")
        unknown = set(value) - set(self.filter_fields)
        if unknown:
            raise ValueError(f"metadata_filter fields are not indexed: {', '.join(sorted(unknown))}")
        filters = []
        for field, item in value.items():
            if item is None or not isinstance(item, (str, int, float, bool)):
                raise ValueError(f"metadata_filter.{field} must be a non-null scalar")
            filters.append({"term": {f"metadata.{field}": item}})
        return filters

    @staticmethod
    def _to_documents(result: Any) -> list[Document]:
        hits = result.get("hits", {}).get("hits", []) if isinstance(result, dict) else []
        documents = []
        for hit in hits:
            source = hit.get("_source", {})
            metadata = dict(source.get("metadata") or {})
            if hit.get("_score") is not None:
                metadata["_opensearch_score"] = hit["_score"]
            documents.append(
                Document(
                    id=str(source.get("id") or hit.get("_id")),
                    text=source.get("text", ""),
                    metadata=metadata,
                    embedding=source.get("embedding") or [],
                )
            )
        return documents
