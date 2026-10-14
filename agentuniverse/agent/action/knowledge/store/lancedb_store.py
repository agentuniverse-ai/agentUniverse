# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: lancedb_store.py

from typing import Any, List, Optional

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import (
    EmbeddingManager,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)

DEFAULT_URI = "./lancedb"


def _quote(value: str) -> str:
    """Format a value as a LanceDB SQL single-quoted string literal.

    LanceDB predicates follow DataFusion SQL, where double quotes delimit
    identifiers; string literals must use single quotes with embedded
    single quotes doubled up.

    Args:
        value: The raw string value.

    Returns:
        The quoted literal, safe to embed in a where clause.
    """
    return "'" + str(value).replace("'", "''") + "'"


class LanceDBStore(Store):
    """LanceDB-based vector store implementation.

    Stores documents with vectors in a LanceDB table and supports similarity
    search. LanceDB is embedded by default: pointing `uri` at a local
    directory requires no server at all, while a `db://` uri together with
    `api_key` targets LanceDB Cloud.

    Attributes:
        uri (Optional[str]): The LanceDB connection uri; a local directory
            path (embedded mode) or a `db://` cloud uri.
        table_name (Optional[str]): LanceDB table name.
        api_key (Optional[str]): The LanceDB Cloud API key.
        region (Optional[str]): The LanceDB Cloud region.
        distance (Optional[str]): Distance metric, one of "COSINE", "EUCLID",
            "DOT".
        embedding_model (Optional[str]): Embedding model key managed by
            `EmbeddingManager`.
        similarity_top_k (Optional[int]): Default top-k for search.
        with_vectors (bool): If True, include vectors in query results.
    """

    uri: Optional[str] = DEFAULT_URI
    table_name: Optional[str] = "agentuniverse"
    api_key: Optional[str] = None
    region: Optional[str] = "us-east-1"
    distance: Optional[str] = "COSINE"
    embedding_model: Optional[str] = None
    similarity_top_k: Optional[int] = 10
    with_vectors: bool = False

    def _distance_type(self) -> str:
        """Map the configured distance name to a LanceDB distance type.

        Returns:
            One of "cosine", "l2", "dot", defaulting to "cosine".
        """
        return {
            "COSINE": "cosine",
            "EUCLID": "l2",
            "DOT": "dot",
        }.get((self.distance or "COSINE").upper(), "cosine")

    def _new_client(self) -> Any:
        """Initialize the LanceDB connection.

        Raises:
            ImportError: If the `lancedb` package is not installed.
        """
        if self.client is not None:
            return self.client
        try:
            import lancedb
        except ImportError:
            raise ImportError(
                "lancedb is required for LanceDBStore. "
                "Install it with: pip install lancedb"
            )
        self.client = lancedb.connect(
            self.uri or DEFAULT_URI,
            api_key=self.api_key,
            region=self.region,
        )
        return self.client

    def _initialize_by_component_configer(self, lancedb_store_configer: ComponentConfiger) -> "LanceDBStore":
        super()._initialize_by_component_configer(lancedb_store_configer)
        if hasattr(lancedb_store_configer, "uri"):
            self.uri = lancedb_store_configer.uri
        if hasattr(lancedb_store_configer, "table_name"):
            self.table_name = lancedb_store_configer.table_name
        if hasattr(lancedb_store_configer, "api_key"):
            self.api_key = lancedb_store_configer.api_key
        if hasattr(lancedb_store_configer, "region"):
            self.region = lancedb_store_configer.region
        if hasattr(lancedb_store_configer, "distance"):
            self.distance = lancedb_store_configer.distance
        if hasattr(lancedb_store_configer, "embedding_model"):
            self.embedding_model = lancedb_store_configer.embedding_model
        if hasattr(lancedb_store_configer, "similarity_top_k"):
            self.similarity_top_k = lancedb_store_configer.similarity_top_k
        if hasattr(lancedb_store_configer, "with_vectors"):
            self.with_vectors = bool(lancedb_store_configer.with_vectors)
        return self

    def _prepare_embeddings(self, documents: List[Document]):
        """Resolve document embeddings through the configured embedding model.

        Args:
            documents: The documents being inserted or upserted.

        Returns:
            The first resolved embedding, or None when no document carries
            an embedding and no embedding model is configured.
        """
        if self.embedding_model is not None:
            for document in documents:
                if not document.embedding or len(document.embedding) == 0:
                    document.embedding = EmbeddingManager().get_instance_obj(
                        self.embedding_model).get_embeddings([document.text])[0]
        for document in documents:
            if document.embedding and len(document.embedding) > 0:
                return document.embedding
        return None

    def _table(self, documents: List[Document]):
        """Return the open table handle, creating the table on first use.

        The rows of the first batch are written by the creation itself and
        must not be appended again, so None is returned in that case.

        Returns:
            The open table handle, or None when the table was just created
            or no document carries an embedding, mirroring the silent
            no-op behavior of the base stores.
        """
        self._prepare_embeddings(documents)
        rows = self._to_rows(documents)
        if not rows:
            return None
        if self.client is None:
            self.client = self._new_client()
        if self.table_name not in self.client.table_names():
            self.client.create_table(self.table_name, data=rows)
            return None
        return self.client.open_table(self.table_name)

    @staticmethod
    def _to_rows(documents: List[Document]) -> List[dict]:
        """Convert documents to LanceDB rows."""
        return [
            {
                "id": str(document.id),
                "vector": document.embedding,
                "text": document.text,
                "metadata": document.metadata or {},
            }
            for document in documents
            if document.embedding and len(document.embedding) > 0
        ]

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query similar documents from the LanceDB table.

        Args:
            query: The query object with embeddings or a query string.
            **kwargs: Additional keyword arguments.

        Returns:
            The list of similar documents, empty when no embedding resolves.
        """
        if self.client is None:
            return []

        embedding = query.embeddings
        if self.embedding_model is not None and (not embedding or len(embedding) == 0):
            model = EmbeddingManager().get_instance_obj(self.embedding_model)
            embedding = model.get_embeddings([query.query_str], text_type="query")

        if not embedding or len(embedding) == 0:
            return []

        if self.table_name not in self.client.table_names():
            return []

        limit = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        table = self.client.open_table(self.table_name)
        results = table.search(embedding[0]) \
            .distance_type(self._distance_type()) \
            .limit(limit) \
            .to_list()
        return self.to_documents(results, with_vectors=self.with_vectors)

    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the LanceDB table.

        Documents whose embedding stays empty after the optional embedding
        model lookup are skipped.
        """
        table = self._table(documents)
        if table is not None:
            rows = self._to_rows(documents)
            if rows:
                table.add(rows)

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert documents into the LanceDB table.

        Documents whose embedding stays empty after the optional embedding
        model lookup are skipped.
        """
        table = self._table(documents)
        if table is None:
            return
        rows = self._to_rows(documents)
        ids = ", ".join(_quote(row["id"]) for row in rows)
        table.delete(f"id IN ({ids})")
        table.add(rows)

    def update_document(self, documents: List[Document], **kwargs):
        """Update documents in the LanceDB table."""
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs):
        """Delete a document from the LanceDB table by id.

        Args:
            document_id: The document id to delete.
        """
        if self.client is None:
            return
        if self.table_name not in self.client.table_names():
            return
        table = self.client.open_table(self.table_name)
        table.delete(f'id = {_quote(document_id)}')

    @staticmethod
    def to_documents(results, with_vectors: bool = False) -> List[Document]:
        """Convert LanceDB query results to documents.

        Args:
            results: The rows returned by a LanceDB search.
            with_vectors: If True, keep the vectors on the documents.

        Returns:
            The converted document list.
        """
        if results is None:
            return []
        documents: List[Document] = []
        for row in results:
            documents.append(
                Document(
                    id=str(row.get("id")),
                    text=row.get("text"),
                    embedding=row.get("vector") if with_vectors else [],
                    metadata=row.get("metadata"),
                )
            )
        return documents
