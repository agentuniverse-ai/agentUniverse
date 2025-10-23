# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from typing import List

from agentUniverse.agent.action.knowledge.store.memory_store import MemoryStore
from agentUniverse.agent.action.knowledge.store.document import Document
from agentUniverse.agent.action.knowledge.store.query import Query


class TestMemoryStore(unittest.TestCase):
    """Test cases for MemoryStore implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.store = MemoryStore()
        self.store._new_client()
    
    def tearDown(self):
        """Clean up after tests."""
        self.store.clear()
    
    def test_insert_document(self):
        """Test inserting documents."""
        doc1 = Document(text="This is a test document about Python programming.")
        doc2 = Document(text="Another document about machine learning algorithms.")
        
        documents = [doc1, doc2]
        self.store.insert_document(documents)
        
        self.assertEqual(self.store.get_document_count(), 2)
        self.assertIn(doc1.id, self.store.documents)
        self.assertIn(doc2.id, self.store.documents)
    
    def test_query_documents(self):
        """Test querying documents."""
        # Insert test documents
        doc1 = Document(text="Python is a great programming language.")
        doc2 = Document(text="Machine learning is fascinating.")
        doc3 = Document(text="Python has excellent machine learning libraries.")
        
        self.store.insert_document([doc1, doc2, doc3])
        
        # Test query
        query = Query(query_str="Python programming")
        results = self.store.query(query)
        
        self.assertGreater(len(results), 0)
        # Should return documents containing "Python"
        for doc in results:
            self.assertIn("python", doc.text.lower())
    
    def test_delete_document(self):
        """Test deleting documents."""
        doc = Document(text="Test document to be deleted.")
        self.store.insert_document([doc])
        
        self.assertEqual(self.store.get_document_count(), 1)
        
        self.store.delete_document(doc.id)
        
        self.assertEqual(self.store.get_document_count(), 0)
        self.assertNotIn(doc.id, self.store.documents)
    
    def test_upsert_document(self):
        """Test upserting documents."""
        doc = Document(id="test-id", text="Original text.")
        self.store.insert_document([doc])
        
        # Update the document
        updated_doc = Document(id="test-id", text="Updated text.")
        self.store.upsert_document([updated_doc])
        
        self.assertEqual(self.store.get_document_count(), 1)
        self.assertEqual(self.store.documents["test-id"].text, "Updated text.")
    
    def test_update_document(self):
        """Test updating documents."""
        doc = Document(id="test-id", text="Original text.")
        self.store.insert_document([doc])
        
        # Update the document
        updated_doc = Document(id="test-id", text="Updated text.")
        self.store.update_document([updated_doc])
        
        self.assertEqual(self.store.documents["test-id"].text, "Updated text.")
    
    def test_similarity_scoring(self):
        """Test similarity scoring."""
        doc1 = Document(text="Python programming language")
        doc2 = Document(text="Java programming language")
        doc3 = Document(text="Python machine learning")
        
        self.store.insert_document([doc1, doc2, doc3])
        
        query = Query(query_str="Python")
        results = self.store.query(query)
        
        # Should return documents with "Python" in them
        python_docs = [doc for doc in results if "python" in doc.text.lower()]
        self.assertGreater(len(python_docs), 0)
    
    def test_empty_query(self):
        """Test querying with empty query."""
        doc = Document(text="Test document.")
        self.store.insert_document([doc])
        
        query = Query(query_str="")
        results = self.store.query(query)
        
        self.assertEqual(len(results), 0)
    
    def test_clear_store(self):
        """Test clearing the store."""
        doc1 = Document(text="Document 1")
        doc2 = Document(text="Document 2")
        
        self.store.insert_document([doc1, doc2])
        self.assertEqual(self.store.get_document_count(), 2)
        
        self.store.clear()
        self.assertEqual(self.store.get_document_count(), 0)
    
    def test_get_all_documents(self):
        """Test getting all documents."""
        doc1 = Document(text="Document 1")
        doc2 = Document(text="Document 2")
        
        self.store.insert_document([doc1, doc2])
        all_docs = self.store.get_all_documents()
        
        self.assertEqual(len(all_docs), 2)
        self.assertIn(doc1, all_docs)
        self.assertIn(doc2, all_docs)
    
    def test_create_copy(self):
        """Test creating a copy of the store."""
        doc = Document(text="Test document.")
        self.store.insert_document([doc])
        
        copy_store = self.store.create_copy()
        
        self.assertIsInstance(copy_store, MemoryStore)
        self.assertEqual(copy_store.get_document_count(), 1)
        self.assertEqual(copy_store.similarity_top_k, self.store.similarity_top_k)


if __name__ == '__main__':
    unittest.main()
