#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Memory Store Demo

This demo shows how to use the MemoryStore implementation for document storage and retrieval.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agentUniverse.agent.action.knowledge.store.memory_store import MemoryStore
from agentUniverse.agent.action.knowledge.store.document import Document
from agentUniverse.agent.action.knowledge.store.query import Query


def main():
    """Main function to demonstrate MemoryStore usage."""
    print("🚀 MemoryStore Demo")
    print("=" * 50)
    
    # Initialize the store
    store = MemoryStore()
    store._new_client()
    
    # Create some sample documents
    documents = [
        Document(text="Python is a high-level programming language known for its simplicity and readability."),
        Document(text="Machine learning is a subset of artificial intelligence that focuses on algorithms."),
        Document(text="Data science combines statistics, programming, and domain expertise to extract insights."),
        Document(text="Web development involves creating websites and web applications using various technologies."),
        Document(text="Database management systems store and organize data efficiently for applications."),
        Document(text="Cloud computing provides on-demand access to computing resources over the internet."),
        Document(text="Cybersecurity protects digital systems and data from unauthorized access and attacks."),
        Document(text="Software engineering involves designing, developing, and maintaining software systems."),
        Document(text="DevOps combines development and operations to improve software delivery processes."),
        Document(text="Artificial intelligence aims to create machines that can perform tasks requiring human intelligence.")
    ]
    
    print(f"📝 Inserting {len(documents)} documents into the store...")
    store.insert_document(documents)
    print(f"✅ Successfully inserted {store.get_document_count()} documents")
    
    # Test different queries
    queries = [
        "Python programming",
        "machine learning algorithms", 
        "data science",
        "web development",
        "cloud computing"
    ]
    
    print("\n🔍 Testing queries:")
    print("-" * 30)
    
    for query_text in queries:
        print(f"\nQuery: '{query_text}'")
        query = Query(query_str=query_text, similarity_top_k=3)
        results = store.query(query)
        
        print(f"Found {len(results)} relevant documents:")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.text[:80]}{'...' if len(doc.text) > 80 else ''}")
    
    # Test document operations
    print("\n📋 Testing document operations:")
    print("-" * 30)
    
    # Test upsert
    new_doc = Document(text="Blockchain technology enables secure and decentralized transactions.")
    store.upsert_document([new_doc])
    print(f"✅ Upserted document. Total documents: {store.get_document_count()}")
    
    # Test update
    updated_doc = Document(id=new_doc.id, text="Blockchain technology enables secure, decentralized, and transparent transactions.")
    store.update_document([updated_doc])
    print(f"✅ Updated document. Document text: {store.documents[new_doc.id].text}")
    
    # Test delete
    store.delete_document(new_doc.id)
    print(f"✅ Deleted document. Total documents: {store.get_document_count()}")
    
    # Test similarity scoring
    print("\n🎯 Testing similarity scoring:")
    print("-" * 30)
    
    test_query = Query(query_str="programming language", similarity_top_k=5)
    results = store.query(test_query)
    
    print(f"Query: 'programming language'")
    print(f"Found {len(results)} relevant documents:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.text}")
    
    # Test store copy
    print("\n📋 Testing store copy:")
    print("-" * 30)
    
    copy_store = store.create_copy()
    print(f"✅ Created copy. Original store: {store.get_document_count()} docs, Copy store: {copy_store.get_document_count()} docs")
    
    # Clear the store
    print("\n🧹 Cleaning up:")
    print("-" * 30)
    store.clear()
    print(f"✅ Cleared store. Total documents: {store.get_document_count()}")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    main()
