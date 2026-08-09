#!/usr/bin/env python3
"""LanceDB vector store for agentUniverse.

LanceDB is an embedded (serverless) vector database — no separate server
process is required, and data persists to a local directory. This component
provides insert, query, upsert, update, delete, and inspection capabilities
following the same bounded/structured/tested contract as the merged pgvector
(#661) and redis_vector (#687) stores.
"""

# Validation failures are converted to structured responses at the public
# boundary, so bespoke exception subclasses add no useful signal.
# ruff: noqa: TRY003, TRY004

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


class LanceDBStore(Store):
    """Embedded vector store backed by LanceDB.

    LanceDB persists data to a local directory (``db_path``); no server
    process is needed. This makes it ideal for development, testing, and
    single-node production deployments.

    Attributes:
        db_path: Local directory for the LanceDB database. Created on first
            connect if it does not exist.
        table_name: LanceDB table name.
        embedding_model: Name of a registered aU embedding component.
        dimensions: Vector dimension. If ``None``, inferred from the first
            inserted document.
        distance: Distance metric — ``cosine``, ``l2``, or ``dot``.
        similarity_top_k: Default number of results to return.
        max_insert_batch: Maximum documents per insert batch.
    """

    db_path: str = "./lancedb"
    table_name: str = "agentuniverse_documents"
    embedding_model: Optional[str] = None
    dimensions: Optional[int] = None
    distance: str = "cosine"
    similarity_top_k: int = 10
    max_insert_batch: int = 500

    client: Any = None
    _table: Any = None
    _schema: Any = None

    _DISTANCE_METRICS: ClassVar[set] = {"cosine", "l2", "dot"}

    # ------------------------------------------------------------------ #
    # Configuration & lifecycle
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          configer: ComponentConfiger) -> "LanceDBStore":
        super()._initialize_by_component_configer(configer)
        for field in (
            "db_path", "table_name", "embedding_model", "dimensions",
            "distance", "similarity_top_k", "max_insert_batch",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        if not self.db_path or not isinstance(self.db_path, str):
            raise ValueError("db_path must be a non-empty string")
        if not self.table_name or not isinstance(self.table_name, str):
            raise ValueError("table_name must be a non-empty string")
        self.distance = (self.distance or "").lower()
        if self.distance not in self._DISTANCE_METRICS:
            raise ValueError(
                f"distance must be one of {sorted(self._DISTANCE_METRICS)}")
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
            import lancedb
            import pyarrow as pa
        except ImportError as exc:
            raise ImportError(
                "lancedb is not installed. Install it with "
                "'pip install lancedb'.") from exc

        os.makedirs(self.db_path, exist_ok=True)
        self.client = lancedb.connect(self.db_path)
        self._pa = pa  # cache pyarrow module for schema building
        self._ensure_table()
        return self.client

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    @property
    def table(self) -> Any:
        if self._table is None:
            self._ensure_client()
        return self._table

    def _ensure_table(self) -> None:
        """Open or create the LanceDB table."""
        client = self.client
        if self.table_name in client.table_names():
            self._table = client.open_table(self.table_name)
            return

        # Create with a schema if dimensions are known; otherwise defer
        # creation until the first insert provides concrete vectors.
        if self.dimensions is not None:
            schema = self._pa.schema([
                self._pa.field("id", self._pa.string()),
                self._pa.field("text", self._pa.string()),
                self._pa.field("vector",
                               self._pa.list_(self._pa.float32(), self.dimensions)),
                self._pa.field("metadata_json", self._pa.string()),
            ])
            self._table = client.create_table(self.table_name, schema=schema)
        else:
            # Table will be created on first insert with inferred schema.
            self._table = None

    # ------------------------------------------------------------------ #
    # Embedding resolution
    # ------------------------------------------------------------------ #
    def _get_embedding(self, text: str, text_type: str = "document") -> List[float]:
        if not self.embedding_model:
            raise ValueError(
                "No embedding model configured. Set embedding_model on the "
                "LanceDBStore component or provide embeddings in Documents.")
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
        self._ensure_client()

        # Resolve / validate dimensions from the first document.
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

        # Build records for insertion.
        records = []
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
            records.append({
                "id": str(doc.id),
                "text": doc.text or "",
                "vector": vector,
                "metadata_json": json.dumps(doc.metadata or {}, default=str,
                                            ensure_ascii=False),
            })

        if not records:
            return

        # Create table on first insert if it was deferred (dimensions were
        # not known at connect time).
        if self._table is None:
            schema = self._pa.schema([
                self._pa.field("id", self._pa.string()),
                self._pa.field("text", self._pa.string()),
                self._pa.field("vector",
                               self._pa.list_(self._pa.float32(), expected_dim)),
                self._pa.field("metadata_json", self._pa.string()),
            ])
            self._table = self.client.create_table(
                self.table_name, data=records, schema=schema, mode="overwrite")
        else:
            # Batch insert respecting max_insert_batch.
            for i in range(0, len(records), self.max_insert_batch):
                self._table.add(records[i:i + self.max_insert_batch])

    def query(self, query: Query, **kwargs) -> List[Document]:
        table = self.table
        if table is None:
            return []

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
        metric = self.distance

        try:
            search = table.search(embedding[0]).limit(top_k)
            if metric == "cosine":
                search = search.metric("cosine")
            elif metric == "dot":
                search = search.metric("dot")
            results = search.to_list()
        except Exception:
            logger.exception("LanceDB query failed")
            return []

        documents: List[Document] = []
        for row in results:
            metadata = {}
            raw_meta = row.get("metadata_json")
            if raw_meta:
                try:
                    metadata = json.loads(raw_meta)
                except (ValueError, TypeError):
                    metadata = {}
            if "_distance" in row:
                metadata["score"] = row["_distance"]
            documents.append(Document(
                text=row.get("text", ""),
                metadata=metadata,
            ))
        return documents

    def upsert_document(self, documents: List[Document], **kwargs) -> None:
        # LanceDB does not have a native upsert; delete then insert.
        for doc in documents:
            self.delete_document(doc.id)
        self.insert_document(documents, **kwargs)

    def update_document(self, documents: List[Document], **kwargs) -> None:
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs) -> None:
        table = self.table
        if table is None:
            return
        try:
            table.delete(f'id = "{document_id}"')
        except Exception:
            logger.exception("LanceDB delete failed for id %s", document_id)

    def get_document_count(self) -> int:
        table = self.table
        if table is None:
            return 0
        try:
            return table.count_rows()
        except Exception:
            logger.exception("LanceDB count_rows failed")
            return 0

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        table = self.table
        if table is None:
            return None
        try:
            results = table.search().where(f'id = "{document_id}"').limit(1).to_list()
        except Exception:
            logger.exception("LanceDB get_by_id failed for %s", document_id)
            return None
        if not results:
            return None
        row = results[0]
        metadata = {}
        raw_meta = row.get("metadata_json")
        if raw_meta:
            try:
                metadata = json.loads(raw_meta)
            except (ValueError, TypeError):
                metadata = {}
        return Document(text=row.get("text", ""), metadata=metadata)

    def list_document_ids(self) -> List[str]:
        table = self.table
        if table is None:
            return []
        try:
            results = table.to_arrow().to_pydict()
            return results.get("id", [])
        except Exception:
            logger.exception("LanceDB list ids failed")
            return []
