#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Simple Store Implementation Demo

This demonstrates how to implement the Store class methods with a concrete example.
This is a standalone implementation that doesn't depend on the full agentUniverse framework.
"""

import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Document:
    """Simple document representation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    keywords: set = field(default_factory=set)


@dataclass
class Query:
    """Simple query representation."""
    query_str: Optional[str] = None
    query_text_bundles: List[str] = field(default_factory=list)
    keywords: set = field(default_factory=set)
    similarity_top_k: Optional[int] = 10


class BaseStore:
    """Base store class with abstract methods."""
    
    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query documents."""
        raise NotImplementedError("Subclasses must implement query method")
    
    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents."""
        raise NotImplementedError("Subclasses must implement insert_document method")
    
    def delete_document(self, document_id: str, **kwargs):
        """Delete document by ID."""
        raise NotImplementedError("Subclasses must implement delete_document method")
    
    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert (insert or update) documents."""
        raise NotImplementedError("Subclasses must implement upsert_document method")
    
    def update_document(self, documents: List[Document], **kwargs):
        """Update documents."""
        raise NotImplementedError("Subclasses must implement update_document method")


class MemoryStore(BaseStore):
    """Concrete implementation of Store using in-memory storage.
    
    This demonstrates how to implement all the abstract methods from the base Store class.
    """
    
    def __init__(self, similarity_top_k: int = 10):
        """Initialize the memory store.
        
        Args:
            similarity_top_k (int): Maximum number of documents to return in queries.
        """
        self.documents: Dict[str, Document] = {}
        self.similarity_top_k = similarity_top_k
    
    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query documents from the store.
        
        This method implements the abstract query method from BaseStore.
        It performs text-based similarity search using simple term matching.
        
        Args:
            query (Query): The query object containing search parameters.
            **kwargs: Additional keyword arguments.
            
        Returns:
            List[Document]: List of matching documents, sorted by relevance.
        """
        if not query.query_str and not query.query_text_bundles:
            return []
        
        # Get search terms
        search_terms = []
        if query.query_str:
            search_terms.append(query.query_str.lower())
        if query.query_text_bundles:
            search_terms.extend([term.lower() for term in query.query_text_bundles])
        
        # Find matching documents with scores
        matching_docs = []
        for doc in self.documents.values():
            score = self._calculate_similarity_score(doc, search_terms)
            if score > 0:
                matching_docs.append((doc, score))
        
        # Sort by score and return top k
        matching_docs.sort(key=lambda x: x[1], reverse=True)
        top_k = query.similarity_top_k or self.similarity_top_k
        return [doc for doc, score in matching_docs[:top_k]]
    
    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the store.
        
        This method implements the abstract insert_document method from BaseStore.
        It adds new documents to the store, generating IDs if not provided.
        
        Args:
            documents (List[Document]): List of documents to insert.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if not document.id:
                document.id = str(uuid.uuid4())
            self.documents[document.id] = document
    
    def delete_document(self, document_id: str, **kwargs):
        """Delete a specific document by ID.
        
        This method implements the abstract delete_document method from BaseStore.
        It removes the document with the specified ID from the store.
        
        Args:
            document_id (str): The ID of the document to delete.
            **kwargs: Additional keyword arguments.
        """
        if document_id in self.documents:
            del self.documents[document_id]
    
    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert (insert or update) documents into the store.
        
        This method implements the abstract upsert_document method from BaseStore.
        It inserts new documents or updates existing ones based on their IDs.
        
        Args:
            documents (List[Document]): List of documents to upsert.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if not document.id:
                document.id = str(uuid.uuid4())
            self.documents[document.id] = document
    
    def update_document(self, documents: List[Document], **kwargs):
        """Update documents in the store.
        
        This method implements the abstract update_document method from BaseStore.
        It updates existing documents, only if they exist in the store.
        
        Args:
            documents (List[Document]): List of documents to update.
            **kwargs: Additional keyword arguments.
        """
        for document in documents:
            if document.id in self.documents:
                self.documents[document.id] = document
    
    def _calculate_similarity_score(self, document: Document, search_terms: List[str]) -> float:
        """Calculate similarity score between document and search terms.
        
        This is a helper method that implements a simple text-based similarity scoring.
        In a real implementation, this could use more sophisticated algorithms like
        TF-IDF, BM25, or vector similarity.
        
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


def demonstrate_store_implementation():
    """Demonstrate the Store implementation."""
    print("Store Implementation Demo")
    print("=" * 50)
    print("This demonstrates how to implement the abstract Store class methods.")
    print()
    
    # Initialize the store
    store = MemoryStore(similarity_top_k=5)
    
    # Create sample documents
    documents = [
        Document(text="Python is a high-level programming language known for its simplicity."),
        Document(text="Machine learning is a subset of artificial intelligence."),
        Document(text="Data science combines statistics, programming, and domain expertise."),
        Document(text="Web development involves creating websites and web applications."),
        Document(text="Database management systems store and organize data efficiently."),
        Document(text="Cloud computing provides on-demand access to computing resources."),
        Document(text="Cybersecurity protects digital systems from unauthorized access."),
        Document(text="Software engineering involves designing and developing software systems."),
        Document(text="DevOps combines development and operations to improve delivery."),
        Document(text="Artificial intelligence aims to create intelligent machines.")
    ]
    
    print("Step 1: Inserting documents...")
    store.insert_document(documents)
    print(f"Inserted {store.get_document_count()} documents")
    
    print("\nStep 2: Testing query functionality...")
    queries = [
        "Python programming",
        "machine learning",
        "data science",
        "web development",
        "cloud computing"
    ]
    
    for query_text in queries:
        print(f"\nQuery: '{query_text}'")
        query = Query(query_str=query_text, similarity_top_k=3)
        results = store.query(query)
        
        print(f"Found {len(results)} relevant documents:")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.text[:60]}{'...' if len(doc.text) > 60 else ''}")
    
    print("\nStep 3: Testing document operations...")
    
    # Test update
    print("Testing update_document...")
    first_doc = list(store.documents.values())[0]
    updated_doc = Document(id=first_doc.id, text="Python is an excellent high-level programming language known for its simplicity and readability.")
    store.update_document([updated_doc])
    print(f"Updated document: {store.documents[first_doc.id].text[:60]}...")
    
    # Test upsert
    print("\nTesting upsert_document...")
    new_doc = Document(text="Blockchain technology enables secure and decentralized transactions.")
    store.upsert_document([new_doc])
    print(f"Upserted document. Total documents: {store.get_document_count()}")
    
    # Test delete
    print("\nTesting delete_document...")
    store.delete_document(new_doc.id)
    print(f"Deleted document. Total documents: {store.get_document_count()}")
    
    print("\nStep 4: Testing similarity scoring...")
    test_query = Query(query_str="programming language", similarity_top_k=3)
    results = store.query(test_query)
    print(f"Query: 'programming language'")
    print(f"Found {len(results)} relevant documents:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.text}")
    
    print("\nStep 5: Testing clear functionality...")
    store.clear()
    print(f"Cleared store. Total documents: {store.get_document_count()}")
    
    print("\nStore implementation demonstration completed successfully!")
    print("\nSummary of implemented methods:")
    print("  - query() - Search documents with similarity scoring")
    print("  - insert_document() - Add new documents")
    print("  - delete_document() - Remove documents by ID")
    print("  - upsert_document() - Insert or update documents")
    print("  - update_document() - Update existing documents")
    print("  - Additional helper methods for store management")


if __name__ == "__main__":
    demonstrate_store_implementation()
