# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_semantic_deduplicator.py

import unittest
from unittest.mock import Mock, patch
from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.store.document import Document


class TestSemanticDeduplicator(unittest.TestCase):
    """Test cases for SemanticDeduplicator."""

    def setUp(self):
        """Set up test fixtures."""
        self.deduplicator = SemanticDeduplicator(
            name='test_deduplicator',
            similarity_threshold=0.95,
            use_embeddings=False,  # Disable embeddings for unit tests
            skip_on_error=True
        )

    def test_exact_duplicate_removal(self):
        """Test exact duplicate removal using content hash."""
        docs = [
            Document(text="This is a test document."),
            Document(text="This is a test document."),  # Exact duplicate
            Document(text="This is another document."),
        ]

        result = self.deduplicator.process_docs(docs)

        # Should remove one exact duplicate
        self.assertEqual(len(result), 2)
        self.assertIn("This is a test document.", [d.text for d in result])
        self.assertIn("This is another document.", [d.text for d in result])

    def test_empty_document_list(self):
        """Test handling of empty document list."""
        result = self.deduplicator.process_docs([])
        self.assertEqual(len(result), 0)

    def test_single_document(self):
        """Test processing single document."""
        docs = [Document(text="Single document")]
        result = self.deduplicator.process_docs(docs)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Single document")

    def test_no_duplicates(self):
        """Test processing documents with no duplicates."""
        docs = [
            Document(text="Document one"),
            Document(text="Document two"),
            Document(text="Document three"),
        ]

        result = self.deduplicator.process_docs(docs)
        self.assertEqual(len(result), 3)

    def test_merge_strategy_keep_first(self):
        """Test keep_first merge strategy."""
        deduplicator = SemanticDeduplicator(
            name='test',
            merge_strategy='keep_first',
            use_embeddings=False
        )

        docs = [
            Document(text="Same content", metadata={'source': 'first'}),
            Document(text="Same content", metadata={'source': 'second'}),
        ]

        result = deduplicator.process_docs(docs)

        self.assertEqual(len(result), 1)
        # Should keep first document
        self.assertEqual(result[0].metadata.get('source'), 'first')

    def test_merge_strategy_keep_best(self):
        """Test keep_best merge strategy."""
        deduplicator = SemanticDeduplicator(
            name='test',
            merge_strategy='keep_best',
            use_embeddings=False
        )

        docs = [
            Document(text="Same content", metadata={'field1': 'value1'}),
            Document(text="Same content", metadata={'field1': 'value1', 'field2': 'value2'}),
        ]

        result = deduplicator.process_docs(docs)

        self.assertEqual(len(result), 1)
        # Should keep document with more metadata (doc2 has both field1 and field2)
        self.assertIn('field1', result[0].metadata)
        self.assertIn('field2', result[0].metadata)

    def test_merge_strategy_merge(self):
        """Test merge strategy."""
        deduplicator = SemanticDeduplicator(
            name='test',
            merge_strategy='merge',
            preserve_metadata=True,
            use_embeddings=False
        )

        docs = [
            Document(text="Same content", metadata={'field1': 'value1'}, keywords={'keyword1'}),
            Document(text="Same content", metadata={'field2': 'value2'}, keywords={'keyword2'}),
        ]

        result = deduplicator.process_docs(docs)

        self.assertEqual(len(result), 1)
        # Should merge metadata
        self.assertIn('field1', result[0].metadata)
        self.assertIn('field2', result[0].metadata)
        # Should merge keywords
        self.assertIn('keyword1', result[0].keywords)
        self.assertIn('keyword2', result[0].keywords)

    def test_metadata_update(self):
        """Test that processor metadata is added."""
        docs = [Document(text="Test document")]
        result = self.deduplicator.process_docs(docs)

        self.assertIsNotNone(result[0].metadata)
        self.assertEqual(result[0].metadata['processor_name'], 'test_deduplicator')
        self.assertEqual(result[0].metadata['processor_version'], '1.0')
        self.assertIn('processing_timestamp', result[0].metadata)

    def test_hash_computation(self):
        """Test hash computation for content."""
        text1 = "Test content"
        text2 = "Test content"
        text3 = "Different content"

        hash1 = self.deduplicator._compute_hash(text1)
        hash2 = self.deduplicator._compute_hash(text2)
        hash3 = self.deduplicator._compute_hash(text3)

        # Same content should have same hash
        self.assertEqual(hash1, hash2)
        # Different content should have different hash
        self.assertNotEqual(hash1, hash3)

    def test_cosine_similarity(self):
        """Test cosine similarity computation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        sim1 = self.deduplicator._compute_similarity(vec1, vec2)
        sim2 = self.deduplicator._compute_similarity(vec1, vec3)

        # Identical vectors should have similarity 1.0
        self.assertAlmostEqual(sim1, 1.0, places=5)
        # Orthogonal vectors should have similarity 0.0
        self.assertAlmostEqual(sim2, 0.0, places=5)

    def test_error_handling_skip_on_error_true(self):
        """Test error handling with skip_on_error=True."""
        deduplicator = SemanticDeduplicator(
            name='test',
            skip_on_error=True,
            use_embeddings=False
        )

        # Create a document that might cause issues
        docs = [
            Document(text="Valid document"),
            Document(text=""),  # Empty text
            Document(text="Another valid document"),
        ]

        # Should not raise exception
        result = deduplicator.process_docs(docs)
        # Should process successfully
        self.assertGreaterEqual(len(result), 2)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator.EmbeddingManager')
    def test_with_embeddings(self, mock_embedding_manager):
        """Test deduplication with embeddings."""
        # Mock embedding model
        mock_embedding = Mock()
        mock_embedding.get_embeddings.return_value = [
            [1.0, 0.0, 0.0],
            [0.99, 0.01, 0.0],  # Very similar
            [0.0, 1.0, 0.0],  # Different
        ]

        mock_manager = Mock()
        mock_manager.get_instance_obj.return_value = mock_embedding
        mock_embedding_manager.return_value = mock_manager

        deduplicator = SemanticDeduplicator(
            name='test',
            similarity_threshold=0.95,
            use_embeddings=True,
            embedding_name='test_embedding'
        )

        docs = [
            Document(text="Document 1"),
            Document(text="Document 1 similar"),
            Document(text="Different document"),
        ]

        result = deduplicator.process_docs(docs)

        # Should identify semantic duplicates
        self.assertEqual(len(result), 2)


class TestSemanticDeduplicatorEdgeCases(unittest.TestCase):
    """Test edge cases for SemanticDeduplicator."""

    def test_very_long_text(self):
        """Test handling of very long text."""
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)

        long_text = "A" * 10000
        docs = [
            Document(text=long_text),
            Document(text=long_text),
        ]

        result = deduplicator.process_docs(docs)
        self.assertEqual(len(result), 1)

    def test_special_characters(self):
        """Test handling of special characters."""
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)

        docs = [
            Document(text="Text with émojis 😀 and spëcial çhars"),
            Document(text="Text with émojis 😀 and spëcial çhars"),
        ]

        result = deduplicator.process_docs(docs)
        self.assertEqual(len(result), 1)

    def test_unicode_text(self):
        """Test handling of unicode text."""
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)

        docs = [
            Document(text="中文文本测试"),
            Document(text="中文文本测试"),
            Document(text="日本語テキスト"),
        ]

        result = deduplicator.process_docs(docs)
        self.assertEqual(len(result), 2)

    def test_whitespace_variations(self):
        """Test that whitespace variations are treated as different."""
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)

        docs = [
            Document(text="Text with spaces"),
            Document(text="Text  with  spaces"),  # Different spacing
        ]

        result = deduplicator.process_docs(docs)
        # Different whitespace = different hash
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
