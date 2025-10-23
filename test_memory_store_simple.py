#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Simple test script for MemoryStore implementation.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our classes directly
from agentUniverse.agent.action.knowledge.store.memory_store import MemoryStore
from agentUniverse.agent.action.knowledge.store.document import Document
from agentUniverse.agent.action.knowledge.store.query import Query


def test_memory_store():
    """Test the MemoryStore implementation."""
    print("🧪 Testing MemoryStore Implementation")
    print("=" * 50)
    
    # Initialize the store
    store = MemoryStore()
    store._new_client()
    
    # Test 1: Insert documents
    print("📝 Test 1: Inserting documents...")
    doc1 = Document(text="Python is a programming language.")
    doc2 = Document(text="Machine learning is a subset of AI.")
    doc3 = Document(text="Python has great ML libraries.")
    
    store.insert_document([doc1, doc2, doc3])
    print(f"✅ Inserted {store.get_document_count()} documents")
    
    # Test 2: Query documents
    print("\n🔍 Test 2: Querying documents...")
    query = Query(query_str="Python programming", similarity_top_k=2)
    results = store.query(query)
    print(f"✅ Found {len(results)} relevant documents:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.text}")
    
    # Test 3: Update document
    print("\n📝 Test 3: Updating document...")
    updated_doc = Document(id=doc1.id, text="Python is an excellent programming language.")
    store.update_document([updated_doc])
    print(f"✅ Updated document: {store.documents[doc1.id].text}")
    
    # Test 4: Delete document
    print("\n🗑️ Test 4: Deleting document...")
    store.delete_document(doc2.id)
    print(f"✅ Deleted document. Total documents: {store.get_document_count()}")
    
    # Test 5: Upsert document
    print("\n📝 Test 5: Upserting document...")
    new_doc = Document(text="Data science combines statistics and programming.")
    store.upsert_document([new_doc])
    print(f"✅ Upserted document. Total documents: {store.get_document_count()}")
    
    # Test 6: Clear store
    print("\n🧹 Test 6: Clearing store...")
    store.clear()
    print(f"✅ Cleared store. Total documents: {store.get_document_count()}")
    
    print("\n🎉 All tests passed successfully!")


if __name__ == "__main__":
    test_memory_store()
