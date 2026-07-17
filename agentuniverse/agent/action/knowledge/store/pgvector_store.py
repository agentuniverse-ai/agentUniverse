#!/usr/bin/env python3
"""PostgreSQL pgvector knowledge store."""

# Dynamic SQL interpolates only table/operator identifiers validated against fixed allowlists.
# ruff: noqa: TRY003, S608

import json
import os
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class PGVectorStore(Store):
    """Persistent vector store backed by PostgreSQL and the pgvector extension."""

    connection_url: str | None = None
    table_name: str = "agentuniverse_documents"
    embedding_model: str | None = None
    dimensions: int | None = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    create_table: bool = True
    create_hnsw_index: bool = True
    client: Any = None
    async_client: Any = None

    _IDENTIFIER: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _DISTANCES: ClassVar[dict[str, tuple[str, str]]] = {
        "cosine": ("<=>", "vector_cosine_ops"),
        "l2": ("<->", "vector_l2_ops"),
        "inner_product": ("<#>", "vector_ip_ops"),
    }

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "PGVectorStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "connection_url",
            "table_name",
            "embedding_model",
            "dimensions",
            "distance",
            "similarity_top_k",
            "create_table",
            "create_hnsw_index",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config(require_dimensions=False)
        return self

    def _validate_config(self, require_dimensions: bool = True) -> None:
        if not self._IDENTIFIER.fullmatch(self.table_name or ""):
            raise ValueError("table_name must be a simple PostgreSQL identifier")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCES:
            raise ValueError("distance must be cosine, l2, or inner_product")
        if (
            isinstance(self.similarity_top_k, bool)
            or not isinstance(self.similarity_top_k, int)
            or self.similarity_top_k <= 0
        ):
            raise ValueError("similarity_top_k must be a positive integer")
        if self.dimensions is not None and (
            isinstance(self.dimensions, bool) or not isinstance(self.dimensions, int) or self.dimensions <= 0
        ):
            raise ValueError("dimensions must be a positive integer")
        if require_dimensions and self.dimensions is None:
            raise ValueError("dimensions must be configured or inferred from the first document")

    @staticmethod
    def _dependencies() -> tuple[Any, Any, Any]:
        try:
            import psycopg
            from pgvector.psycopg import register_vector, register_vector_async
        except ImportError as exc:
            raise ImportError("PGVectorStore requires psycopg[binary] and pgvector") from exc
        return psycopg, register_vector, register_vector_async

    def _url(self) -> str:
        value = self.connection_url or os.getenv("PGVECTOR_CONNECTION_URL")
        if not value:
            raise ValueError("connection_url is required; set it in YAML or PGVECTOR_CONNECTION_URL")
        return value

    def _new_client(self) -> Any:
        psycopg, register_vector, _ = self._dependencies()
        self.client = psycopg.connect(self._url(), autocommit=True)
        # pgvector adapters query the vector type, so the extension must exist first.
        self.client.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(self.client)
        if self.create_table and self.dimensions:
            self._ensure_table(self.dimensions)
        return self.client

    async def _new_async_client(self) -> Any:
        psycopg, _, register_vector_async = self._dependencies()
        self.async_client = await psycopg.AsyncConnection.connect(self._url(), autocommit=True)
        # Async registration has the same ordering requirement as sync registration.
        await self.async_client.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector_async(self.async_client)
        if self.create_table and self.dimensions:
            await self._async_ensure_table(self.dimensions)
        return self.async_client

    def _ensure_client(self) -> Any:
        return self.client or self._new_client()

    async def _ensure_async_client(self) -> Any:
        return self.async_client or await self._new_async_client()

    def _table_sql(self, dimensions: int) -> list[str]:
        self.dimensions = self.dimensions or dimensions
        if dimensions != self.dimensions:
            raise ValueError(f"embedding dimension {dimensions} does not match configured dimensions {self.dimensions}")
        self._validate_config()
        statements = [
            "CREATE EXTENSION IF NOT EXISTS vector",
            f"CREATE TABLE IF NOT EXISTS {self.table_name} (id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb, embedding vector({self.dimensions}) NOT NULL)",
        ]
        if self.create_hnsw_index:
            operator_class = self._DISTANCES[self.distance][1]
            statements.append(
                f"CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_hnsw ON {self.table_name} USING hnsw (embedding {operator_class})"
            )
        return statements

    def _ensure_table(self, dimensions: int) -> None:
        connection = self._ensure_client()
        for statement in self._table_sql(dimensions):
            connection.execute(statement)

    async def _async_ensure_table(self, dimensions: int) -> None:
        connection = await self._ensure_async_client()
        for statement in self._table_sql(dimensions):
            await connection.execute(statement)

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
            or any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in vector)
        ):
            raise ValueError("embedding must be a non-empty numeric list")
        if self.dimensions is None:
            self.dimensions = len(vector)
        if len(vector) != self.dimensions:
            raise ValueError(
                f"embedding dimension {len(vector)} does not match configured dimensions {self.dimensions}"
            )

    def _top_k(self, query: Query) -> int:
        top_k = query.similarity_top_k or self.similarity_top_k
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("similarity_top_k must be a positive integer")
        return top_k

    def query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        self._ensure_table(len(vector))
        filters = kwargs.get("metadata_filter")
        where, params = "", [vector]
        if filters is not None:
            if not isinstance(filters, dict):
                raise TypeError("metadata_filter must be an object")
            where = " WHERE metadata @> %s::jsonb"
            params.append(json.dumps(filters))
        operator = self._DISTANCES[self.distance][0]
        params.append(top_k)
        # psycopg adapts a Python list as float8[], so cast the query parameter to
        # vector explicitly before applying pgvector's distance operators.
        sql = f"SELECT id, text, metadata, embedding, embedding {operator} %s::vector AS distance FROM {self.table_name}{where} ORDER BY distance LIMIT %s"
        rows = self._ensure_client().execute(sql, params).fetchall()
        return self._rows_to_documents(rows)

    async def async_query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        await self._async_ensure_table(len(vector))
        filters = kwargs.get("metadata_filter")
        where, params = "", [vector]
        if filters is not None:
            if not isinstance(filters, dict):
                raise TypeError("metadata_filter must be an object")
            where, params = " WHERE metadata @> %s::jsonb", [vector, json.dumps(filters)]
        operator = self._DISTANCES[self.distance][0]
        params.append(top_k)
        cursor = await (await self._ensure_async_client()).execute(
            f"SELECT id, text, metadata, embedding, embedding {operator} %s::vector AS distance FROM {self.table_name}{where} ORDER BY distance LIMIT %s",
            params,
        )
        return self._rows_to_documents(await cursor.fetchall())

    def upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        self._ensure_table(len(vectors[0]))
        sql = f"INSERT INTO {self.table_name} (id, text, metadata, embedding) VALUES (%s, %s, %s::jsonb, %s) ON CONFLICT (id) DO UPDATE SET text=EXCLUDED.text, metadata=EXCLUDED.metadata, embedding=EXCLUDED.embedding"
        connection = self._ensure_client()
        with connection.cursor() as cursor:
            cursor.executemany(
                sql,
                [
                    (document.id, document.text or "", json.dumps(document.metadata or {}), vector)
                    for document, vector in zip(documents, vectors, strict=True)
                ],
            )

    async def async_upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        await self._async_ensure_table(len(vectors[0]))
        sql = f"INSERT INTO {self.table_name} (id, text, metadata, embedding) VALUES (%s, %s, %s::jsonb, %s) ON CONFLICT (id) DO UPDATE SET text=EXCLUDED.text, metadata=EXCLUDED.metadata, embedding=EXCLUDED.embedding"
        connection = await self._ensure_async_client()
        async with connection.cursor() as cursor:
            await cursor.executemany(
                sql,
                [
                    (document.id, document.text or "", json.dumps(document.metadata or {}), vector)
                    for document, vector in zip(documents, vectors, strict=True)
                ],
            )

    def insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def update_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_update_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs: Any) -> None:
        self._ensure_client().execute(f"DELETE FROM {self.table_name} WHERE id = %s", [str(document_id)])

    async def async_delete_document(self, document_id: str, **kwargs: Any) -> None:
        await (await self._ensure_async_client()).execute(
            f"DELETE FROM {self.table_name} WHERE id = %s", [str(document_id)]
        )

    @staticmethod
    def _rows_to_documents(rows: Any) -> list[Document]:
        return [
            Document(
                id=str(row[0]),
                text=row[1],
                metadata=row[2] or {},
                embedding=PGVectorStore._embedding_list(row[3]),
            )
            for row in (rows or [])
        ]

    @staticmethod
    def _embedding_list(value: Any) -> list[float]:
        if value is None:
            return []
        # Registered pgvector adapters return pgvector.Vector, which exposes
        # to_list() but deliberately does not implement Python iteration.
        to_list = getattr(value, "to_list", None)
        return to_list() if callable(to_list) else list(value)
