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
    search_depth: int = None
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

        embedding = query.embeddings
        if self.embedding_model is not None and len(embedding) == 0:
            embedding = EmbeddingManager().get_instance_obj(
                self.embedding_model
            ).get_embeddings([query.query_str], text_type="query")[0]

        top_k_ids = []
        query_result = []

        for depth in range(self.search_depth):
            if len(top_k_ids) > 0:
                top_k = self.similarity_top_k_list[depth] if len(
                    self.similarity_top_k_list) >= depth + 1 else self.similarity_top_k

                # Collect the children of every parent matched at the previous level.
                merged_results = []
                for parent_id in top_k_ids:
                    # Query for each parent_id
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
                    for i in range(len(results['ids'][0])):
                        merged_results.append({
                            'id': results['ids'][0][i],
                            'text': results['documents'][0][i] if results['documents'] else None,
                            'embedding': results['embeddings'][0][i] if results['embeddings'] else [],
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else None,
                            'distance': results['distances'][0][i] if results['distances'] else 0.0,
                        })

                # Rank the merged children by distance and keep the top k.
                merged_results.sort(key=lambda item: item['distance'])
                merged_results = merged_results[:top_k]

                # Rebuild a single QueryResult so that to_documents can parse it.
                query_result = {
                    'ids': [[item['id'] for item in merged_results]],
                    'documents': [[item['text'] for item in merged_results]],
                    'embeddings': [[item['embedding'] for item in merged_results]] if any(
                        item['embedding'] for item in merged_results) else None,
                    'metadatas': [[item['metadata'] for item in merged_results]] if any(
                        item['metadata'] is not None for item in merged_results) else None,
                }
            else:
                filter_condition = {
                   "hierarchical_level": depth
                }
                if len(embedding) > 0:
                    query_result = self.collection.query(
                        n_results=self.similarity_top_k_list[depth] if len(
                            self.similarity_top_k_list) >= depth + 1 else self.similarity_top_k,
                        query_embeddings=embedding,
                        where=filter_condition
                    )
                else:
                    query_result = self.collection.query(
                        n_results=self.similarity_top_k_list[depth] if len(
                            self.similarity_top_k_list) >= depth + 1 else self.similarity_top_k,
                        query_texts=[query.query_str],
                        where=filter_condition
                    )

            documents = self.to_documents(query_result)
            top_k_ids = [doc.id for doc in documents]

        return self.to_documents(query_result)

    def _initialize_by_component_configer(self,
                                          chroma_store_configer: ComponentConfiger) -> 'DocProcessor':
        super()._initialize_by_component_configer(chroma_store_configer)
        if hasattr(chroma_store_configer, "search_depth"):
            self.search_depth = chroma_store_configer.search_depth
        return self
