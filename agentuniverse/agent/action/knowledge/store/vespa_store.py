#!/usr/bin/env python3
"""Vespa open-source search and vector engine knowledge store."""

# The pyvespa client exposes dict payloads to Vespa over HTTP; we validate
# every identifier used in the YQL body against strict allowlists first.
# ruff: noqa: TRY003

import json
import re
from typing import Any, ClassVar
from urllib.parse import urlparse

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class VespaStore(Store):
    """Persistent vector store backed by a running Vespa application.

    Vespa combines inverted-index text search with approximate nearest
    neighbour (ANN) vector search. This component assumes the target schema
    already exists on the application (it is not responsible for deploying a
    package) and only performs data-plane CRUD plus ANN query operations via
    the optional ``pyvespa`` dependency.
    """

    application_url: str | None = None
    cert_path: str | None = None
    key_path: str | None = None
    schema_name: str = "agentuniverse_document"
    namespace: str = "agentuniverse"
    cluster_name: str = "agentuniverse_cluster"
    embedding_model: str | None = None
    dimensions: int | None = None
    embedding_field: str = "embedding"
    id_field: str = "id"
    text_field: str = "text"
    metadata_field: str = "metadata"
    similarity_top_k: int = 10
    client: Any = None
    async_client: Any = None

    _DISTANCES: ClassVar[set[str]] = {"euclidean", "angular", "innerproduct", "geodegrees", "hamming"}

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "VespaStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "application_url",
            "cert_path",
            "key_path",
            "schema_name",
            "namespace",
            "cluster_name",
            "embedding_model",
            "dimensions",
            "embedding_field",
            "id_field",
            "text_field",
            "metadata_field",
            "similarity_top_k",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config(require_dimensions=False)
        return self

    def _validate_config(self, require_dimensions: bool = True) -> None:
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        for name in ("schema_name", "namespace", "cluster_name",
                     "embedding_field", "id_field", "text_field", "metadata_field"):
            value = getattr(self, name)
            if not identifier.fullmatch(value or ""):
                raise ValueError(f"{name} must be a simple Vespa identifier")
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

    @staticmethod
    def _dependencies() -> Any:
        try:
            from vespa.application import Vespa
        except ImportError as exc:
            raise ImportError("VespaStore requires the pyvespa package") from exc
        return Vespa

    def _url(self) -> str:
        value = self.application_url
        if not value:
            raise ValueError("application_url is required; set it in the YAML configuration")
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("application_url must be an absolute http(s) URL")
        return value

    def _new_client(self) -> Any:
        Vespa = self._dependencies()
        kwargs: dict[str, Any] = {"url": self._url()}
        if self.cert_path:
            kwargs["cert"] = self.cert_path
        if self.key_path:
            kwargs["key"] = self.key_path
        self.client = Vespa(**kwargs)
        return self.client

    async def _new_async_client(self) -> Any:
        Vespa = self._dependencies()
        kwargs: dict[str, Any] = {"url": self._url()}
        if self.cert_path:
            kwargs["cert"] = self.cert_path
        if self.key_path:
            kwargs["key"] = self.key_path
        self.async_client = Vespa(**kwargs)
        return self.async_client

    def _ensure_client(self) -> Any:
        return self.client or self._new_client()

    async def _ensure_async_client(self) -> Any:
        return self.async_client or await self._new_async_client()

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
    # Vespa payload helpers
    # ------------------------------------------------------------------ #
    def _fields_for_document(self, document: Document, vector: list[float]) -> dict[str, Any]:
        metadata = document.metadata or {}
        return {
            self.id_field: str(document.id),
            self.text_field: document.text or "",
            self.metadata_field: json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            self.embedding_field: [float(value) for value in vector],
        }

    def _yql(self, vector: list[float], top_k: int, metadata_filter: Any) -> dict[str, Any]:
        nearest = (
            f"({{targetHits:{top_k}}})nearestNeighbor({self.embedding_field}, query_embedding)"
        )
        where = nearest
        if metadata_filter is not None:
            if not isinstance(metadata_filter, dict):
                raise TypeError("metadata_filter must be an object")
            clauses = [nearest]
            for key, value in metadata_filter.items():
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(key)):
                    raise ValueError(f"metadata_filter key {key!r} is not a valid identifier")
                if isinstance(value, bool):
                    literal = "true" if value else "false"
                elif isinstance(value, (int, float)):
                    literal = repr(value)
                elif isinstance(value, str):
                    literal = ", ".join(json.dumps(part) for part in value.split(","))
                    literal = f"[{literal}]"
                else:
                    raise TypeError(f"metadata_filter.{key} must be a scalar value")
                clauses.append(f"{self.metadata_field}.contains({{key:{json.dumps(str(key))}, value:{literal}}})")
            where = " AND ".join(clauses)
        yql = (
            f"select * from {self.schema_name} "
            f"where {where}"
        )
        body: dict[str, Any] = {
            "yql": yql,
            "input.query(query_embedding)": [float(value) for value in vector],
            "hits": top_k,
        }
        return body

    def _hit_to_document(self, hit: Any) -> Document | None:
        if not isinstance(hit, dict):
            return None
        fields = hit.get("fields", {})
        if not fields:
            return None
        metadata_raw = fields.get(self.metadata_field)
        if isinstance(metadata_raw, (str, bytes)) and metadata_raw:
            try:
                metadata = json.loads(metadata_raw)
            except (TypeError, ValueError):
                metadata = {}
        elif isinstance(metadata_raw, dict):
            metadata = metadata_raw
        else:
            metadata = {}
        embedding = fields.get(self.embedding_field)
        if isinstance(embedding, dict):
            embedding = embedding.get("values", embedding)
        return Document(
            id=str(fields.get(self.id_field, hit.get("id", ""))),
            text=fields.get(self.text_field, ""),
            metadata=metadata,
            embedding=[float(value) for value in embedding] if isinstance(embedding, list) else [],
        )

    @classmethod
    def _hits(cls, response: Any) -> list[Any]:
        payload = cls._response_payload(response)
        if not payload:
            return []
        if isinstance(payload, dict):
            root = payload.get("root", {}) or {}
            children = root.get("children", []) if isinstance(root, dict) else []
            if children:
                return children
            return payload.get("hits", []) or []
        return []

    @staticmethod
    def _response_payload(response: Any) -> Any:
        if response is None:
            return {}
        if isinstance(response, dict):
            return response
        # pyvespa response objects expose the decoded JSON via `.json` (attribute)
        # or via the ``get_json()`` / ``json`` helpers depending on the version.
        payload = getattr(response, "json", None)
        if isinstance(payload, dict):
            return payload
        if callable(payload):
            try:
                return payload()
            except TypeError:
                pass
        get_json = getattr(response, "get_json", None)
        if callable(get_json):
            try:
                return get_json()
            except TypeError:
                pass
        return {}

    @staticmethod
    def _ensure_successful(response: Any, operation: str) -> None:
        status = getattr(response, "status_code", None)
        if status is not None and status >= 400:
            raise RuntimeError(f"Vespa {operation} failed with status {status}")
        is_success = getattr(response, "is_successful", None)
        if callable(is_success):
            is_success = is_success()
        if is_success is False:
            raise RuntimeError(f"Vespa {operation} was not successful")

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        body = self._yql(vector, top_k, kwargs.get("metadata_filter"))
        response = self._ensure_client().query(body=body)
        return [doc for doc in (self._hit_to_document(hit) for hit in self._hits(response)) if doc]

    async def async_query(self, query: Query, **kwargs: Any) -> list[Document]:
        vector = self._embedding_for_query(query)
        top_k = self._top_k(query)
        body = self._yql(vector, top_k, kwargs.get("metadata_filter"))
        response = await (await self._ensure_async_client()).query(body=body)
        return [doc for doc in (self._hit_to_document(hit) for hit in self._hits(response)) if doc]

    def upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        client = self._ensure_client()
        for document, vector in zip(documents, vectors, strict=True):
            response = client.feed_data_point(
                schema=self.schema_name,
                data_id=str(document.id),
                fields=self._fields_for_document(document, vector),
                namespace=self.namespace,
            )
            self._ensure_successful(response, "upsert")

    async def async_upsert_document(self, documents: list[Document], **kwargs: Any) -> None:
        if not documents:
            return
        vectors = self._vectors_for_documents(documents)
        client = await self._ensure_async_client()
        for document, vector in zip(documents, vectors, strict=True):
            response = await client.feed_data_point(
                schema=self.schema_name,
                data_id=str(document.id),
                fields=self._fields_for_document(document, vector),
                namespace=self.namespace,
            )
            self._ensure_successful(response, "upsert")

    def insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_insert_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def update_document(self, documents: list[Document], **kwargs: Any) -> None:
        self.upsert_document(documents, **kwargs)

    async def async_update_document(self, documents: list[Document], **kwargs: Any) -> None:
        await self.async_upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs: Any) -> None:
        response = self._ensure_client().delete_data(
            schema=self.schema_name,
            data_id=str(document_id),
            namespace=self.namespace,
        )
        self._ensure_successful(response, "delete")

    async def async_delete_document(self, document_id: str, **kwargs: Any) -> None:
        response = await (await self._ensure_async_client()).delete_data(
            schema=self.schema_name,
            data_id=str(document_id),
            namespace=self.namespace,
        )
        self._ensure_successful(response, "delete")
