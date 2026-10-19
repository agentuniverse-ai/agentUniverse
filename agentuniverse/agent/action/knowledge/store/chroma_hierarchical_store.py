# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/30 15:13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: chroma_hierarchical_store.py

from typing import List, Any, Optional
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class ChromaHierarchicalStore(ChromaStore):
    """Object encapsulating the ChromaDB store that has vector search enabled.

    The ChromaStore object provides insert and retrieval capabilities.

    Attributes:
        collection_name (str): The name of the chroma collection to use.
        collection (Collection): A chroma collection object.
        persist_path (Optional[str]): Path to save the chroma database.
    """
    search_depth: Optional[int] = 1
    similarity_top_k_list: Optional[List[int]] = []

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query the chroma collection with the given query and perform multi-layered search.

        Args:
            query (Query): The query object.
            **kwargs: Arbitrary keyword arguments.

        Note:
            If there is no embedding in the specific query, but the embedding model is configured in the store,
            the embedding data of the query is automatically obtained by the embedding model.

        Returns:
            List[Document]: List of documents retrieved by the query.
        """
        if not self.search_depth or self.search_depth <= 0:
            return []

        embedding = query.embeddings
        if self.embedding_model is not None and len(embedding) == 0:
            embedding = EmbeddingManager().get_instance_obj(
                self.embedding_model
            ).get_embeddings([query.query_str], text_type="query")[0]

        top_k_ids = []
        query_result: list[dict] = []

        for depth in range(self.search_depth):
            if len(top_k_ids) > 0:
                # Flatten results across all parent_ids into a single ranked
                # list of per-doc dicts, then keep the top-k by distance. The
                # previous code did ``all_results.extend(results)`` on a Chroma
                # dict (which extends with the dict's *keys*: 'ids',
                # 'documents', ...), then ``sorted(..., key=lambda x:
                # x['distance'])`` on those string keys — a guaranteed
                # TypeError on every multi-parent query.
                flat: list[dict] = []
                top_k = (self.similarity_top_k_list[depth]
                         if len(self.similarity_top_k_list) >= depth + 1
                         else self.similarity_top_k)
                for parent_id in top_k_ids:
                    if len(embedding) > 0:
                        results = self.collection.query(
                            n_results=top_k,
                            query_embeddings=embedding,
                            where={"hierarchical_parent": parent_id}
                        )
                    else:
                        results = self.collection.query(
                            n_results=top_k,
                            query_texts=[query.query_str],
                            where={"hierarchical_parent": parent_id}
                        )
                    flat.extend(self._flatten_chroma_results(results))
                # Lower distance == better match in Chroma.
                flat.sort(key=lambda x: x['distance'])
                query_result = flat[:top_k]
            else:
                filter_condition = {
                   "hierarchical_level": depth
                }
                top_k = (self.similarity_top_k_list[depth]
                         if len(self.similarity_top_k_list) >= depth + 1
                         else self.similarity_top_k)
                if len(embedding) > 0:
                    raw = self.collection.query(
                        n_results=top_k,
                        query_embeddings=embedding,
                        where=filter_condition
                    )
                else:
                    raw = self.collection.query(
                        n_results=top_k,
                        query_texts=[query.query_str],
                        where=filter_condition
                    )
                query_result = self._flatten_chroma_results(raw)

            documents = self._flat_to_documents(query_result)
            top_k_ids = [doc.id for doc in documents]

        return self._flat_to_documents(query_result)

    @staticmethod
    def _flatten_chroma_results(results: Any) -> list[dict]:
        """Flatten Chroma's nested-list-of-lists result dict into per-doc dicts.

        Chroma returns ``{'ids': [[...]], 'documents': [[...]], 'distances':
        [[...]], 'metadatas': [[...]], 'embeddings': [[...]] | None}``. Each
        outer list corresponds to one query; we flatten the first query's
        results into a list of ``{id, document, distance, metadata,
        embedding}`` dicts that downstream sorting / pagination can use.
        """
        if not isinstance(results, dict):
            return []
        ids = results.get('ids') or []
        documents = results.get('documents') or []
        distances = results.get('distances') or []
        metadatas = results.get('metadatas') or []
        embeddings = results.get('embeddings') or []
        if not ids or not isinstance(ids[0], list):
            return []
        flat: list[dict] = []
        for i, doc_id in enumerate(ids[0]):
            flat.append({
                'id': doc_id,
                'document': documents[0][i] if documents and len(documents[0]) > i else '',
                'distance': distances[0][i] if distances and len(distances[0]) > i else 0.0,
                'metadata': metadatas[0][i] if metadatas and len(metadatas[0]) > i else None,
                'embedding': embeddings[0][i] if embeddings and len(embeddings[0]) > i else [],
            })
        return flat

    @staticmethod
    def _flat_to_documents(flat: list[dict]) -> List[Document]:
        """Build Documents from the flattened per-doc dicts."""
        documents: List[Document] = []
        for item in flat:
            metadata = item.get('metadata')
            documents.append(Document(
                id=item.get('id'),
                text=item.get('document') or '',
                embedding=item.get('embedding') or [],
                metadata=metadata if isinstance(metadata, dict) else None,
            ))
        return documents

    def _initialize_by_component_configer(self,
                                          chroma_store_configer: ComponentConfiger) -> 'DocProcessor':
        super()._initialize_by_component_configer(chroma_store_configer)
        if hasattr(chroma_store_configer, "search_depth"):
            self.search_depth = chroma_store_configer.search_depth
        return self
