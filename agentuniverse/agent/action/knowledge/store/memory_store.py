# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: memory_store.py

import json
import uuid
from typing import List, Optional, Dict, Any
from collections import defaultdict

from agentUniverse.agent.action.knowledge.store.store import Store
from agentUniverse.agent.action.knowledge.store.document import Document
from agentUniverse.agent.action.knowledge.store.query import Query
from agentUniverse.base.config.component_configer.component_configer import ComponentConfiger


class MemoryStore(Store):
    """A simple in-memory store implementation for testing and development.
    
    This store keeps all documents in memory and provides basic CRUD operations.
    It's useful for testing, development, and small-scale applications.
    
    Attributes:
        documents (Dict[str, Document]): Dictionary storing documents by ID.
        similarity_top_k (int): Maximum number of documents to return in queries.
    """
    
    documents: Dict[str, Document] = {}
    similarity_top_k: int = 10
    
    def _new_client(self) -> Any:
        """Initialize the memory store."""
        if not hasattr(self, 'documents') or self.documents is None:
            self.documents = {}
    
    def _new_async_client(self) -> Any:
        """Initialize the async client (same as sync for memory store)."""
        self._new_client()
    
    def _initialize_by_component_configer(self, 
                                       store_configer: ComponentConfiger) -> 'MemoryStore':
        """Initialize the store by the ComponentConfiger object.
        
        Args:
            store_configer (ComponentConfiger): A configer contains store basic info.
            
        Returns:
            MemoryStore: A store instance.
        """
        super()._initialize_by_component_configer(store_configer)
        
        if hasattr(store_configer, 'similarity_top_k'):
            self.similarity_top_k = store_configer.similarity_top_k
            
        return self
    
    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query documents from the store.
        
        Args:
            query (Query): The query object containing search parameters.
            **kwargs: Additional keyword arguments.
            
        Returns:
            List[Document]: List of matching documents.
        """
        if not query.query_str and not query.query_text_bundles:
            return []
        
        # Get search terms
        search_terms = []
        if query.query_str:
            search_terms.append(query.query_str.lower())
        if query.query_text_bundles:
            search_terms.extend([term.lower() for term in query.query_text_bundles])
        
        # Find matching documents
        matching_docs = []
        for doc in self.documents.values():
            score = self._calculate_similarity_score(doc, search_terms)
            if score > 0:
                matching_docs.append((doc, score))
        
        # Sort by score and return top k
        matching_docs.sort(key=lambda x: x[1], reverse=True)
        top_k = query.similarity_top_k or self.similarity_top_k
        return [doc for doc, score in matching_docs[:top_k]]
    
    async def async_query(self, query: Query, **kwargs) -> List[Document]:
        """Asynchronously query documents from the store.
        
        Args:
            query (Query): The query object containing search parameters.
            **kwargs: Additional keyword arguments.
            
        Returns:
            List[Document]: List of matching documents.
        """
        return self.query(query, **kwargs)
    
    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the store.
        
        Args:
            documents (List[Document]): List of documents to insert.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if not document.id:
                document.id = str(uuid.uuid4())
            self.documents[document.id] = document
    
    async def async_insert_document(self, documents: List[Document], **kwargs):
        """Asynchronously insert documents into the store.
        
        Args:
            documents (List[Document]): List of documents to insert.
            **kwargs: Additional keyword arguments.
        """
        self.insert_document(documents, **kwargs)
    
    def delete_document(self, document_id: str, **kwargs):
        """Delete a specific document by ID.
        
        Args:
            document_id (str): The ID of the document to delete.
            **kwargs: Additional keyword arguments.
        """
        if document_id in self.documents:
            del self.documents[document_id]
    
    async def async_delete_document(self, document_id: str, **kwargs):
        """Asynchronously delete a specific document by ID.
        
        Args:
            document_id (str): The ID of the document to delete.
            **kwargs: Additional keyword arguments.
        """
        self.delete_document(document_id, **kwargs)
    
    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert (insert or update) documents into the store.
        
        Args:
            documents (List[Document]): List of documents to upsert.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if not document.id:
                document.id = str(uuid.uuid4())
            self.documents[document.id] = document
    
    async def async_upsert_document(self, documents: List[Document], **kwargs):
        """Asynchronously upsert documents into the store.
        
        Args:
            documents (List[Document]): List of documents to upsert.
            **kwargs: Additional keyword arguments.
        """
        self.upsert_document(documents, **kwargs)
    
    def update_document(self, documents: List[Document], **kwargs):
        """Update documents in the store.
        
        Args:
            documents (List[Document]): List of documents to update.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if document.id in self.documents:
                self.documents[document.id] = document
    
    async def async_update_document(self, documents: List[Document], **kwargs):
        """Asynchronously update documents in the store.
        
        Args:
            documents (List[Document]): List of documents to update.
            **kwargs: Additional keyword arguments.
        """
        self.update_document(documents, **kwargs)
    
    def _calculate_similarity_score(self, document: Document, search_terms: List[str]) -> float:
        """Calculate similarity score between document and search terms.
        
        Args:
            document (Document): The document to score.
            search_terms (List[str]): List of search terms.
            
        Returns:
            float: Similarity score (0.0 to 1.0).
        """
        if not document.text:
            return 0.0
        
        text_lower = document.text.lower()
        score = 0.0
        
        for term in search_terms:
            if term in text_lower:
                # Simple term frequency scoring
                term_count = text_lower.count(term)
                score += term_count * 0.1
        
        # Normalize score
        return min(score, 1.0)
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the store.
        
        Returns:
            int: Number of documents.
        """
        return len(self.documents)
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents from the store.
        
        Returns:
            List[Document]: List of all documents.
        """
        return list(self.documents.values())
    
    def clear(self):
        """Clear all documents from the store."""
        self.documents.clear()
    
    def create_copy(self):
        """Create a copy of the store.
        
        Returns:
            MemoryStore: A new instance with the same configuration.
        """
        new_store = MemoryStore()
        new_store.similarity_top_k = self.similarity_top_k
        new_store.documents = self.documents.copy()
        return new_store
