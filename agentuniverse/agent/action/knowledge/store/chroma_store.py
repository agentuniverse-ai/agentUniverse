# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 16:31
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chroma_store.py
from urllib.parse import urlparse
from typing import List, Any, Optional
from pydantic import SkipValidation

import chromadb
from chromadb import QueryResult
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ChromaStore(Store):
    """Object encapsulating the ChromaDB store that has vector search enabled.

    The ChromaStore object provides insert and retrieval capabilities.

    Attributes:
        collection_name (str): The name of the chroma collection to use.
        collection (Collection): A chroma collection object.
        persist_path (Optional[str]): Path to save the chroma database.
    """

    collection_name: Optional[str] = "chroma_db"
    collection: SkipValidation[Collection] = None
    persist_path: Optional[str] = None
    embedding_model: Optional[str] = None
    similarity_top_k: Optional[int] = 10

    def _new_client(self) -> Any:
        """Initialize the chroma client."""
        if self.persist_path.startswith("http") or self.persist_path.startswith("https"):
            # Remote database URL
            parsed_url = urlparse(self.persist_path)
            settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=parsed_url.hostname,
                chroma_server_http_port=str(parsed_url.port),
            )
        else:
            settings = Settings(is_persistent=True, persist_directory=self.persist_path)

        client = chromadb.Client(settings)
        if self.collection is None:
            # default to create a new collection or get an existed collection.
            self.collection = client.get_or_create_collection(name=self.collection_name)
        return client

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query the chroma collection with the given query and return the top k results.

        Args:
            query (Query): The query object.
            **kwargs: Arbitrary keyword arguments.

        Note:
            If there is no embedding in the specific query, but the embedding model is configured in the store,
            the embedding data of the query is automatically obtained by the embedding model.

        Returns:
            List[Document]: List of documents retrieved by the query.
        """

        embedding = query.embeddings
        if self.embedding_model is not None and len(embedding) == 0:
            embedding = (
                EmbeddingManager()
                .get_instance_obj(self.embedding_model)
                .get_embeddings([query.query_str], text_type="query")[0]
            )
        if len(embedding) > 0:
            query_result = self.collection.query(
                n_results=query.similarity_top_k if query.similarity_top_k else self.similarity_top_k,
                query_embeddings=embedding,
            )
        else:
            query_result = self.collection.query(
                n_results=query.similarity_top_k if query.similarity_top_k else self.similarity_top_k,
                query_texts=[query.query_str],
            )
        # convert to the agentUniverse(aU) document format
        return self.to_documents(query_result)

    def insert_document(self, documents: List[Document], **kwargs: Any):
        """Insert documents to the chroma collection.

        Args:
            documents (List[Document]): The documents to be inserted.
            **kwargs: Arbitrary keyword arguments.

        Note:
            If there is no embedding in the specific document, but the embedding model is configured in the store,
            the embedding data of the document is automatically obtained by the embedding model.
        """

        for document in documents:
            embedding = document.embedding
            if self.embedding_model is not None and len(embedding) == 0:
                embedding = EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([document.text])[0]
            self.collection.add(
                documents=[document.text],
                metadatas=[document.metadata],
                embeddings=[embedding] if len(embedding) > 0 else None,
                ids=[document.id],
            )

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert document into the store."""
        for document in documents:
            embedding = document.embedding
            if self.embedding_model is not None and len(embedding) == 0:
                embedding = EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([document.text])[0]
            self.collection.upsert(
                documents=[document.text],
                metadatas=[document.metadata],
                embeddings=[embedding] if embedding is not None else None,
                ids=[document.id],
            )

    def update_document(self, documents: List[Document], **kwargs):
        """Update document into the store."""
        for document in documents:
            embedding = document.embedding
            if self.embedding_model is not None and len(embedding) == 0:
                embedding = EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([document.text])[0]
            self.collection.update(
                documents=[document.text],
                metadatas=[document.metadata],
                embeddings=[embedding] if embedding is not None else None,
                ids=[document.id],
            )

    @staticmethod
    def to_documents(query_result: QueryResult) -> List[Document]:
        """Convert the query results of ChromaDB to the agentUniverse(aU) document format."""

        if query_result is None:
            return []
        documents = []
        for i in range(len(query_result["ids"][0])):
            documents.append(
                Document(
                    id=query_result["ids"][0][i],
                    text=query_result["documents"][0][i],
                    embedding=query_result["embeddings"][0][i] if query_result["embeddings"] is not None else [],
                    metadata=query_result["metadatas"][0][i] if query_result["metadatas"] is not None else None,
                )
            )
        return documents

    def _initialize_by_component_configer(self, chroma_store_configer: ComponentConfiger) -> "DocProcessor":
        super()._initialize_by_component_configer(chroma_store_configer)
        if hasattr(chroma_store_configer, "collection_name"):
            self.collection_name = chroma_store_configer.collection_name
        if hasattr(chroma_store_configer, "persist_path"):
            self.persist_path = chroma_store_configer.persist_path
        if hasattr(chroma_store_configer, "embedding_model"):
            self.embedding_model = chroma_store_configer.embedding_model
        if hasattr(chroma_store_configer, "similarity_top_k"):
            self.similarity_top_k = chroma_store_configer.similarity_top_k
        return self
