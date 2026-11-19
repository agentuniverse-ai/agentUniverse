#!/usr/bin/env python3
"""MyScale (ClickHouse-based) vector knowledge store."""

# Identifiers (table name) are validated against a strict allowlist before any
# SQL string is assembled, and all data values flow through clickhouse-connect's
# native parameter binding ({name:Type}); none are interpolated into the text.
# ruff: noqa: TRY003, S608

import json
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class MyScaleStore(Store):
    """Persistent vector store backed by MyScale / ClickHouse.

    MyScale is a ClickHouse fork with first-class vector types and an MSTG
    vector index. This component talks to it through the standard
    ``clickhouse-connect`` driver, stores each document as a row with an
    ``Array(Float32)`` embedding column, and performs exact (brute-force)
    nearest-neighbour search via ClickHouse's built-in distance functions.
    """

    host: str = "localhost"
    port: int = 8443
    username: str | None = None
    password: str | None = None
    database: str = "default"
    table_name: str = "agentuniverse_documents"
    secure: bool = True
    embedding_model: str | None = None
    dimensions: int | None = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    create_table: bool = True
    client: Any = None
    async_client: Any = None

    _IDENTIFIER: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    # distance -> (ClickHouse distance expression template, ascending order).
    # The expression substitutes {p} for the query vector parameter placeholder.
    _DISTANCES: ClassVar[dict[str, str]] = {
        "cosine": "cosineDistance(embedding, {p})",
        "l2": "L2Distance(embedding, {p})",
        "inner_product": "negate(dotProduct(embedding, {p}))",
    }

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "MyScaleStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "host",
            "port",
            "username",
            "password",
            "database",
            "table_name",
            "secure",
            "embedding_model",
            "dimensions",
            "distance",
            "similarity_top_k",
            "create_table",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config(require_dimensions=False)
        return self

    def _validate_config(self, require_dimensions: bool = True) -> None:
        for name in ("database", "table_name"):
            if not self._IDENTIFIER.fullmatch(getattr(self, name) or ""):
                raise ValueError(f"{name} must be a simple ClickHouse identifier")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCES:
            raise ValueError("distance must be cosine, l2, or inner_product")
        if (
            isinstance(self.port, bool)
            or not isinstance(self.port, int)
            or not (1 <= self.port <= 65535)
        ):
            raise ValueError("port must be an integer between 1 and 65535")
        if (
            isinstance(self.similarity_top_k, bool)
            or not isinstance(self.similarity_top_k, int)
            or self.similarity_top_k <= 0
        ):
            raise ValueError("similarity_top_k must be a positive integer")
        if self.dimensions is not None and (
            isinstance(self.dimensions, bool)
            or not isinstance(self.dimensions, int)
            or self.dimensions <= 0
        ):
            raise ValueError("dimensions must be a positive integer")
        if require_dimensions and self.dimensions is None:
            raise ValueError("dimensions must be configured or inferred from the first document")
        if not isinstance(self.secure, bool):
            raise TypeError("secure must be a boolean")
        if not isinstance(self.create_table, bool):
            raise TypeError("create_table must be a boolean")

    @staticmethod
    def _dependencies() -> Any:
        try:
            import clickhouse_connect
        except ImportError as exc:
            raise ImportError("MyScaleStore requires the clickhouse-connect package") from exc
        return clickhouse_connect

    def _new_client(self) -> Any:
        driver = self._dependencies()
        self.client = driver.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
            secure=self.secure,
        )
        if self.create_table and self.dimensions:
            self._ensure_table(self.dimensions)
        return self.client

    async def _new_async_client(self) -> Any:
        # clickhouse-connect is synchronous; the async entrypoints simply reuse
        # the shared connection so CRUD methods can run in a worker thread.
        if self.client is None:
            self._new_client()
        self.async_client = self.client
        return self.async_client

    def _ensure_client(self) -> Any:
        return self.client or self._new_client()

    async def _ensure_async_client(self) -> Any:
        return self.async_client or await self._new_async_client()

    def _create_table_sql(self, dimensions: int) -> str:
        self.dimensions = self.dimensions or dimensions
        if dimensions != self.dimensions:
            raise ValueError(
                f"embedding dimension {dimensions} does not match configured dimensions {self.dimensions}"
            )
        self._validate_config()
        return (
            f"CREATE TABLE IF NOT EXISTS {self.database}.{self.table_name} ("
            f"id String, "
            f"text String, "
            f"metadata String, "
            f"embedding Array(Float32)"
            f") ENGINE = MergeTree ORDER BY id"
        )

    def _ensure_table(self, dimensions: int) -> None:
        if not self.create_table:
            self._create_table_sql(dimensions)
            return
        self._ensure_client().command(self._create_table_sql(dimensions))

    async def _async_ensure_table(self, dimensions: int) -> None:
        if not self.create_table:
            self._create_table_sql(dimensions)
            return
        (await self._ensure_async_client()).command(self._create_table_sql(dimensions))

    # ------------------------------------------------------------------ #
    # Embedding helpers
    # ------------------------------------------------------------------ #
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
                isinstance(value, bool) or not isinstance(value, (int, float))
                for value in vector
            )
        ):
            raise ValueError("embedding must be a non-empty numeric list")
        if self.dimensions is None:
            self.dimensions = len(vector)
        if len(vector) != self.dimensions:
            raise ValueError(
                f"embedding dimension {len(vector)} does not match configured dimensions {self.dimensions}"
            )

    def _top_k(self, query: Query) -> int:
        value = query.similarity_top_k or self.similarity_top_k
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("similarity_top_k must be a positive integer")
        return value

    # ------------------------------------------------------------------ #
    # SQL builders
    # ------------------------------------------------------------------ #
    def _distance_expr(self) -> str:
        return self._DISTANCES[self.distance].format(p="{p:Array(Float32)}")

    def _select_sql_and_params(
        self, vector: list[float], top_k: int, metadata_filter: Any
    ) -> tuple[str, dict[str, Any]]:
        distance_expr = self._distance_expr()
        where_clauses: list[str] = []
        params: dict[str, Any] = {"p": vector, "top_k": top_k}
        if metadata_filter is not None:
            if not isinstance(metadata_filter, dict):
                raise TypeError("metadata_filter must be an object")
            for index, (key, value) in enumerate(metadata_filter.items()):
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(key)):
                    raise ValueError(f"metadata_filter key {key!r} is not a valid identifier")
                if isinstance(value, bool):
                    text = "true" if value else "false"
                elif isinstance(value, (int, float)):
                    text = repr(value)
                elif isinstance(value, str):
                    text = value
                else:
                    raise TypeError(f"metadata_filter.{key} must be a scalar value")
                where_clauses.append(
                    f"JSONExtractString(metadata, %(f_key_{index})s) = %(f_val_{index})s"
                )
                params[f"f_key_{index}"] = str(key)
                params[f"f_val_{index}"] = text
        where = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        sql = (
            f"SELECT id, text, metadata, embedding, {distance_expr} AS distance "
            f"FROM {self.database}.{self.table_name}{where} "
            f"ORDER BY distance LIMIT %(top_k)s"
        )
        return sql, params

    @classmethod
    def _rows_to_documents(cls, rows: list[tuple]) -> list[Document]:
        documents: list[Document] = []
        for row in (rows or []):
            metadata_raw = row[2]
            if isinstance(metadata_raw, (str, bytes)) and metadata_raw:
                try:
                    metadata = json.loads(metadata_raw)
                except (TypeError, ValueError):
                    metadata = {}
            elif isinstance(metadata_raw, dict):
                metadata = metadata_raw
            else:
                metadata = {}
            embedding = row[3]
            documents.append(
                Document(
                    id=str(row[0]),
                    text=row[1],
                    metadata=metadata,
                    embedding=[float(value) for value in embedding] if isinstance(embedding, (list, tuple)) else [],
                )
            )
        return documents

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        self._ensure_table(len(vector))
        sql, params = self._select_sql_and_params(vector, top_k, kwargs.get("metadata_filter"))
        result = self._ensure_client().query(sql, parameters=params)
        return self._rows_to_documents(result.result_rows)

    async def async_query(self, query: Query, **kwargs: Any) -> list[Document]:
        import asyncio

        return await asyncio.to_thread(self.query, query, **kwargs)

    def _upsert_rows(self, documents: list[Document], vectors: list[list[float]]) -> None:
        rows = [
            (
                str(document.id),
                document.text or "",
                json.dumps(document.metadata or {}, ensure_ascii=False, sort_keys=True),
                [float(value) for value in vector],
            )
            for document, vector in zip(documents, vectors, strict=True)
        ]
        client = self._ensure_client()
        client.insert(
            self.table_name,
            rows,
            column_names=["id", "text", "metadata", "embedding"],
            database=self.database,
        )

    def upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        self._ensure_table(len(vectors[0]))
        self._upsert_rows(documents, vectors)

    async def async_upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        import asyncio

        await asyncio.to_thread(self.upsert_document, documents, **kwargs)

    def insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def update_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_update_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs: Any) -> None:
        # ClickHouse lightweight deletes require a setting; identifier is
        # validated, the id value is bound as a parameter.
        self._ensure_client().command(
            f"DELETE FROM {self.database}.{self.table_name} WHERE id = %(doc_id)s",
            parameters={"doc_id": str(document_id)},
        )

    async def async_delete_document(self, document_id: str, **kwargs: Any) -> None:
        import asyncio

        await asyncio.to_thread(self.delete_document, document_id, **kwargs)
