#!/usr/bin/env python3
"""Redis Stack vector knowledge store."""

# Dynamic identifiers are validated against strict allowlists before command construction.
# ruff: noqa: TRY003

import json
import math
import os
import re
import sys
from array import array
from typing import Any, ClassVar

from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class RedisVectorStore(Store):
    """Persistent vector store backed by Redis Stack/RediSearch."""

    connection_url: str | None = None
    index_name: str = "agentuniverse_documents"
    key_prefix: str = "agentuniverse:document:"
    embedding_model: str | None = None
    dimensions: int | None = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    create_index: bool = True
    filter_tag_fields: list[str] = Field(default_factory=list)
    hnsw_m: int = 16
    hnsw_ef_construction: int = 200
    client: Any = None
    async_client: Any = None

    _IDENTIFIER: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _PREFIX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9:_-]+$")
    _DISTANCES: ClassVar[dict[str, str]] = {"cosine": "COSINE", "l2": "L2", "inner_product": "IP"}
    _TAG_ESCAPE: ClassVar[re.Pattern[str]] = re.compile(r"([\\,\.<>\{\}\[\]\"':;!@#$%\^&*\(\)\-\+=~|/ ])")

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "RedisVectorStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "connection_url",
            "index_name",
            "key_prefix",
            "embedding_model",
            "dimensions",
            "distance",
            "similarity_top_k",
            "create_index",
            "filter_tag_fields",
            "hnsw_m",
            "hnsw_ef_construction",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config(require_dimensions=False)
        return self

    def _validate_config(self, require_dimensions: bool = True) -> None:  # noqa: C901
        if not self._IDENTIFIER.fullmatch(self.index_name or ""):
            raise ValueError("index_name must be a simple identifier")
        if not self._PREFIX.fullmatch(self.key_prefix or ""):
            raise ValueError("key_prefix contains unsupported characters")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCES:
            raise ValueError("distance must be cosine, l2, or inner_product")
        for name in ("similarity_top_k", "hnsw_m", "hnsw_ef_construction"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.dimensions is not None and (
            isinstance(self.dimensions, bool) or not isinstance(self.dimensions, int) or self.dimensions <= 0
        ):
            raise ValueError("dimensions must be a positive integer")
        if require_dimensions and self.dimensions is None:
            raise ValueError("dimensions must be configured or inferred from the first document")
        if not isinstance(self.filter_tag_fields, list) or any(
            not isinstance(item, str) or not self._IDENTIFIER.fullmatch(item) for item in self.filter_tag_fields
        ):
            raise ValueError("filter_tag_fields must contain simple identifiers")
        if len(set(self.filter_tag_fields)) != len(self.filter_tag_fields):
            raise ValueError("filter_tag_fields must not contain duplicates")
        if not isinstance(self.create_index, bool):
            raise TypeError("create_index must be a boolean")

    @staticmethod
    def _dependencies() -> tuple[Any, Any, Any]:
        try:
            import redis
            from redis import ResponseError
            from redis.asyncio import from_url as async_from_url
        except ImportError as exc:
            raise ImportError("RedisVectorStore requires the redis package and Redis Stack") from exc
        return redis, async_from_url, ResponseError

    def _url(self) -> str:
        value = self.connection_url or os.getenv("REDIS_VECTOR_URL")
        if not value:
            raise ValueError("connection_url is required; set it in YAML or REDIS_VECTOR_URL")
        return value

    def _new_client(self) -> Any:
        redis, _, _ = self._dependencies()
        self.client = redis.from_url(self._url(), decode_responses=False)
        self.client.ping()
        if self.create_index and self.dimensions:
            self._ensure_index(self.dimensions)
        return self.client

    async def _new_async_client(self) -> Any:
        _, async_from_url, _ = self._dependencies()
        self.async_client = async_from_url(self._url(), decode_responses=False)
        await self.async_client.ping()
        if self.create_index and self.dimensions:
            await self._async_ensure_index(self.dimensions)
        return self.async_client

    def _ensure_client(self) -> Any:
        return self.client or self._new_client()

    async def _ensure_async_client(self) -> Any:
        return self.async_client or await self._new_async_client()

    def _index_command(self, dimensions: int) -> list[Any]:
        self.dimensions = self.dimensions or dimensions
        if dimensions != self.dimensions:
            raise ValueError(f"embedding dimension {dimensions} does not match configured dimensions {self.dimensions}")
        self._validate_config()
        command: list[Any] = [
            "FT.CREATE",
            self.index_name,
            "ON",
            "HASH",
            "PREFIX",
            1,
            self.key_prefix,
            "SCHEMA",
            "id",
            "TAG",
            "text",
            "TEXT",
            "metadata",
            "TEXT",
            "NOINDEX",
        ]
        for field in self.filter_tag_fields:
            command.extend((f"meta_{field}", "TAG", "SEPARATOR", "\x1f"))
        command.extend(
            (
                "embedding",
                "VECTOR",
                "HNSW",
                10,
                "TYPE",
                "FLOAT32",
                "DIM",
                self.dimensions,
                "DISTANCE_METRIC",
                self._DISTANCES[self.distance],
                "M",
                self.hnsw_m,
                "EF_CONSTRUCTION",
                self.hnsw_ef_construction,
            )
        )
        return command

    @staticmethod
    def _already_exists(exc: Exception) -> bool:
        return "index already exists" in str(exc).lower()

    def _ensure_index(self, dimensions: int) -> None:
        if not self.create_index:
            self._index_command(dimensions)
            return
        connection = self._ensure_client()
        try:
            connection.execute_command(*self._index_command(dimensions))
        except Exception as exc:
            if not self._already_exists(exc):
                raise

    async def _async_ensure_index(self, dimensions: int) -> None:
        if not self.create_index:
            self._index_command(dimensions)
            return
        connection = await self._ensure_async_client()
        try:
            await connection.execute_command(*self._index_command(dimensions))
        except Exception as exc:
            if not self._already_exists(exc):
                raise

    def _embedding_for_query(self, query: Query) -> list[float]:
        if query.embeddings:
            vector = query.embeddings[0]
        elif self.embedding_model and query.query_str:
            model = EmbeddingManager().get_instance_obj(self.embedding_model, strict=True)
            vector = model.get_embeddings([query.query_str], text_type="query")[0]
        else:
            raise ValueError("query requires embeddings or an embedding_model plus query_str")
        self._check_vector(vector)
        return vector

    def _vectors_for_documents(self, documents: list[Document]) -> list[list[float]]:
        missing = [index for index, document in enumerate(documents) if not document.embedding]
        if missing:
            if not self.embedding_model:
                raise ValueError("documents without embeddings require embedding_model")
            model = EmbeddingManager().get_instance_obj(self.embedding_model, strict=True)
            generated = model.get_embeddings([documents[index].text or "" for index in missing])
            for index, vector in zip(missing, generated, strict=True):
                documents[index].embedding = vector
        vectors = [document.embedding for document in documents]
        for vector in vectors:
            self._check_vector(vector)
        return vectors

    def _check_vector(self, vector: Any) -> None:
        if (
            not isinstance(vector, list)
            or not vector
            or any(
                isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value))
                for value in vector
            )
        ):
            raise ValueError("embedding must be a non-empty list of finite numbers")
        if self.dimensions is None:
            self.dimensions = len(vector)
        if len(vector) != self.dimensions:
            raise ValueError(
                f"embedding dimension {len(vector)} does not match configured dimensions {self.dimensions}"
            )

    @staticmethod
    def _vector_bytes(vector: list[float]) -> bytes:
        values = array("f", (float(value) for value in vector))
        if sys.byteorder != "little":
            values.byteswap()
        return values.tobytes()

    @staticmethod
    def _bytes_vector(value: Any) -> list[float]:
        if value is None:
            return []
        raw = bytes(value)
        if len(raw) % 4:
            raise ValueError("Redis returned an invalid FLOAT32 vector")
        values = array("f")
        values.frombytes(raw)
        if sys.byteorder != "little":
            values.byteswap()
        return list(values)

    def _top_k(self, query: Query) -> int:
        value = query.similarity_top_k or self.similarity_top_k
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("similarity_top_k must be a positive integer")
        return value

    @classmethod
    def _tag_value(cls, value: Any, field: str) -> str:
        if isinstance(value, bool):
            text = "true" if value else "false"
        elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
            text = str(value)
        else:
            raise TypeError(f"metadata_filter.{field} must be a scalar value")
        if not text:
            raise ValueError(f"metadata_filter.{field} must not be empty")
        return cls._TAG_ESCAPE.sub(r"\\\1", text)

    def _filter(self, value: Any) -> str:
        if value is None:
            return "*"
        if not isinstance(value, dict):
            raise TypeError("metadata_filter must be an object")
        unknown = set(value) - set(self.filter_tag_fields)
        if unknown:
            raise ValueError(f"metadata_filter fields are not indexed: {', '.join(sorted(unknown))}")
        return " ".join(f"@meta_{field}:{{{self._tag_value(item, field)}}}" for field, item in value.items()) or "*"

    def _search_command(self, vector: list[float], top_k: int, metadata_filter: Any) -> list[Any]:
        base_filter = self._filter(metadata_filter)
        query = f"({base_filter})=>[KNN {top_k} @embedding $query_vector AS vector_distance]"
        return [
            "FT.SEARCH",
            self.index_name,
            query,
            "PARAMS",
            2,
            "query_vector",
            self._vector_bytes(vector),
            "SORTBY",
            "vector_distance",
            "RETURN",
            5,
            "id",
            "text",
            "metadata",
            "embedding",
            "vector_distance",
            "LIMIT",
            0,
            top_k,
            "DIALECT",
            2,
        ]

    @staticmethod
    def _decode(value: Any) -> str:
        return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    @classmethod
    def _rows_to_documents(cls, response: Any) -> list[Document]:
        values = list(response or [])
        documents = []
        for index in range(1, len(values), 2):
            fields = values[index + 1]
            mapping = {cls._decode(fields[i]): fields[i + 1] for i in range(0, len(fields), 2)}
            documents.append(
                Document(
                    id=cls._decode(mapping.get("id", values[index])),
                    text=cls._decode(mapping.get("text", "")),
                    metadata=json.loads(cls._decode(mapping.get("metadata", b"{}"))),
                    embedding=cls._bytes_vector(mapping.get("embedding")),
                )
            )
        return documents

    def query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        self._ensure_index(len(vector))
        response = self._ensure_client().execute_command(
            *self._search_command(vector, top_k, kwargs.get("metadata_filter"))
        )
        return self._rows_to_documents(response)

    async def async_query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        await self._async_ensure_index(len(vector))
        response = await (await self._ensure_async_client()).execute_command(
            *self._search_command(vector, top_k, kwargs.get("metadata_filter"))
        )
        return self._rows_to_documents(response)

    def _mapping(self, document: Document, vector: list[float]) -> dict[str, Any]:
        metadata = document.metadata or {}
        mapping: dict[str, Any] = {
            "id": str(document.id),
            "text": document.text or "",
            "metadata": json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            "embedding": self._vector_bytes(vector),
        }
        for field in self.filter_tag_fields:
            if field in metadata:
                value = metadata[field]
                self._tag_value(value, field)
                mapping[f"meta_{field}"] = str(value).lower() if isinstance(value, bool) else str(value)
        return mapping

    def upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        self._ensure_index(len(vectors[0]))
        connection = self._ensure_client()
        pipeline = connection.pipeline(transaction=False)
        for document, vector in zip(documents, vectors, strict=True):
            pipeline.hset(f"{self.key_prefix}{document.id}", mapping=self._mapping(document, vector))
        pipeline.execute()

    async def async_upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        await self._async_ensure_index(len(vectors[0]))
        connection = await self._ensure_async_client()
        async with connection.pipeline(transaction=False) as pipeline:
            for document, vector in zip(documents, vectors, strict=True):
                pipeline.hset(f"{self.key_prefix}{document.id}", mapping=self._mapping(document, vector))
            await pipeline.execute()

    def insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def update_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_update_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs: Any) -> None:
        self._ensure_client().delete(f"{self.key_prefix}{document_id}")

    async def async_delete_document(self, document_id: str, **kwargs: Any) -> None:
        await (await self._ensure_async_client()).delete(f"{self.key_prefix}{document_id}")
