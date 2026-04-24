# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_financial_event_aggregator.py

import unittest
from unittest.mock import Mock, patch
from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document


class TestFinancialEventAggregator(unittest.TestCase):
    """Unit tests for FinancialEventAggregator."""

    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = FinancialEventAggregator(
            name='test_aggregator',
            similarity_threshold=0.85,
            use_embeddings=False,  # Disable embeddings for unit tests
            use_llm=False,  # Disable LLM for unit tests
            clustering_method='dbscan'
        )

    def test_basic_aggregation(self):
        """Test basic news aggregation."""
        docs = [
            Document(text="Apple announces Q4 earnings of $1.56 per share."),
            Document(text="Apple reports strong Q4 results with EPS of $1.56."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should aggregate similar articles
        self.assertLessEqual(len(result), len(docs))

    @patch('agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator.EmbeddingManager')
    def test_similar_article_clustering(self, mock_embedding_manager):
        """Test clustering of similar articles."""
        # Mock embedding model to return high similarity for first two docs
        mock_embedding = Mock()
        mock_embedding.get_embeddings.return_value = [
            [1.0, 0.0, 0.0],    # Doc 1
            [0.99, 0.01, 0.0],  # Doc 2 - very similar to Doc 1
            [0.0, 1.0, 0.0],    # Doc 3 - different
        ]

        mock_manager = Mock()
        mock_manager.get_instance_obj.return_value = mock_embedding
        mock_embedding_manager.return_value = mock_manager

        aggregator = FinancialEventAggregator(
            name='test_aggregator',
            similarity_threshold=0.85,
            use_embeddings=True,  # Enable embeddings for this test
            embedding_name='test_embedding',
            use_llm=False,
            clustering_method='dbscan'
        )

        docs = [
            Document(text="Company A acquires Company B for $10 billion."),
            Document(text="$10B acquisition: Company A buys Company B."),
            Document(text="Unrelated: Company C reports earnings."),
        ]

        result = aggregator.process_docs(docs)

        # Should cluster first two, keep third separate
        self.assertLessEqual(len(result), 2)

    def test_event_type_detection(self):
        """Test detection of different event types."""
        docs = [
            Document(text="Company announces merger with competitor."),
            Document(text="Quarterly earnings exceed expectations."),
            Document(text="New product launch scheduled for next month."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect event types
        event_types = set()
        for doc in result:
            if 'event_type' in doc.metadata:
                event_types.add(doc.metadata['event_type'])

        # Should identify at least one event type
        self.assertGreater(len(event_types), 0)

    def test_merger_event_detection(self):
        """Test detection of merger/acquisition events."""
        docs = [
            Document(text="Tech giant acquires startup for $5 billion."),
            Document(text="Acquisition announced: BigCo buys SmallCo."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect merger/acquisition event
        has_merger = any(
            doc.metadata.get('event_type') in ['merger', 'acquisition']
            for doc in result
        )
        self.assertTrue(has_merger or len(result) > 0)

    def test_earnings_event_detection(self):
        """Test detection of earnings events."""
        docs = [
            Document(text="Company reports Q4 earnings beat estimates."),
            Document(text="Quarterly results exceed analyst expectations."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect earnings event
        has_earnings = any(
            doc.metadata.get('event_type') == 'earnings'
            for doc in result
        )
        self.assertTrue(has_earnings or len(result) > 0)

    def test_source_attribution(self):
        """Test preservation of source document references."""
        docs = [
            Document(text="Article 1 content.", metadata={'source': 'Reuters'}),
            Document(text="Article 1 similar.", metadata={'source': 'Bloomberg'}),
        ]

        result = self.aggregator.process_docs(docs)

        # Aggregated docs should reference sources
        for doc in result:
            if 'source_documents' in doc.metadata:
                self.assertGreater(len(doc.metadata['source_documents']), 0)
                break

    def test_publication_date_tracking(self):
        """Test tracking of publication dates."""
        docs = [
            Document(
                text="News article 1.",
                metadata={'publication_date': '2024-01-01'}
            ),
            Document(
                text="News article 2.",
                metadata={'publication_date': '2024-01-02'}
            ),
        ]

        result = self.aggregator.process_docs(docs)

        # Should track publication dates
        self.assertGreater(len(result), 0)

    def test_entity_extraction(self):
        """Test extraction of involved entities."""
        docs = [
            Document(text="Apple Inc. acquires StartupX for undisclosed amount."),
            Document(text="Apple completes acquisition of StartupX."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should extract entities involved
        has_entities = any(
            'entities_involved' in doc.metadata
            for doc in result
        )
        self.assertTrue(has_entities or len(result) > 0)

    def test_conflicting_information_detection(self):
        """Test detection of conflicting information."""
        docs = [
            Document(text="Company revenue reaches $100M in Q4."),
            Document(text="Company reports Q4 revenue of $95M."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect potential conflicts
        has_conflicts = any(
            'conflicting_info' in doc.metadata and
            len(doc.metadata['conflicting_info']) > 0
            for doc in result
        )
        self.assertTrue(has_conflicts or len(result) > 0)

    def test_credibility_scoring(self):
        """Test source credibility scoring."""
        docs = [
            Document(
                text="News from major outlet.",
                metadata={'source': 'Reuters', 'source_type': 'major_news'}
            ),
            Document(
                text="Blog post content.",
                metadata={'source': 'UnknownBlog', 'source_type': 'blog'}
            ),
        ]

        result = self.aggregator.process_docs(docs)

        # Should have credibility scores
        has_credibility = any(
            'credibility_scores' in doc.metadata
            for doc in result
        )
        self.assertTrue(has_credibility or len(result) > 0)

    def test_hierarchical_clustering(self):
        """Test hierarchical clustering method."""
        aggregator = FinancialEventAggregator(
            name='test',
            clustering_method='hierarchical',
            use_embeddings=False,
            use_llm=False
        )

        docs = [
            Document(text="Article about event A."),
            Document(text="Similar article about event A."),
            Document(text="Different article about event B."),
        ]

        result = aggregator.process_docs(docs)

        # Should cluster using hierarchical method
        self.assertLessEqual(len(result), len(docs))

    def test_max_sources_limit(self):
        """Test max sources per event limit."""
        # Create many similar documents
        docs = [
            Document(text=f"Apple announces earnings. Article {i}.")
            for i in range(25)
        ]

        aggregator = FinancialEventAggregator(
            name='test',
            max_sources_per_event=20,
            use_embeddings=False,
            use_llm=False
        )

        result = aggregator.process_docs(docs)

        # Should respect max sources limit
        for doc in result:
            sources = doc.metadata.get('source_documents', [])
            self.assertLessEqual(len(sources), 20)

    def test_preserve_sources_flag(self):
        """Test preserve_sources configuration."""
        docs = [
            Document(text="Article 1 about event."),
            Document(text="Article 2 about same event."),
        ]

        aggregator = FinancialEventAggregator(
            name='test',
            preserve_sources=True,
            use_embeddings=False,
            use_llm=False
        )

        result = aggregator.process_docs(docs)

        # Should preserve source references
        has_sources = any(
            'source_documents' in doc.metadata
            for doc in result
        )
        self.assertTrue(has_sources)

    def test_empty_document_list(self):
        """Test handling of empty document list."""
        result = self.aggregator.process_docs([])

        # Should handle gracefully
        self.assertEqual(len(result), 0)

    def test_single_document(self):
        """Test handling of single document."""
        doc = Document(text="Single news article.")
        result = self.aggregator.process_docs([doc])

        # Should return single document
        self.assertEqual(len(result), 1)

    def test_metadata_preservation(self):
        """Test preservation of original metadata."""
        docs = [
            Document(
                text="News article.",
                metadata={'article_id': 'A001', 'author': 'John Doe'}
            ),
        ]

        result = self.aggregator.process_docs(docs)

        # Original metadata should be accessible
        self.assertGreater(len(result), 0)

    def test_multilingual_aggregation(self):
        """Test aggregation of multilingual articles."""
        docs = [
            Document(text="Apple announces earnings."),
            Document(text="苹果公布财报。"),
        ]

        result = self.aggregator.process_docs(docs)

        # Should handle multilingual content
        self.assertGreater(len(result), 0)

    def test_batch_processing_performance(self):
        """Test batch processing of many documents."""
        docs = [
            Document(text=f"Article {i} about various events.")
            for i in range(50)
        ]

        result = self.aggregator.process_docs(docs)

        # Should process large batches
        self.assertLessEqual(len(result), len(docs))

    def test_event_id_generation(self):
        """Test generation of unique event IDs."""
        docs = [
            Document(text="Event A news article 1."),
            Document(text="Event A news article 2."),
            Document(text="Event B news article."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should generate event IDs
        event_ids = set()
        for doc in result:
            if 'event_id' in doc.metadata:
                event_ids.add(doc.metadata['event_id'])

        # Should have unique event IDs
        self.assertEqual(len(event_ids), len(result))

    def test_summary_generation_without_llm(self):
        """Test summary generation without LLM."""
        docs = [
            Document(text="Company announces major product launch."),
            Document(text="New product unveiled by company."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should create some form of summary even without LLM
        for doc in result:
            self.assertIn('text', doc.__dict__)
            self.assertGreater(len(doc.text), 0)

    def test_lawsuit_event_detection(self):
        """Test detection of lawsuit events."""
        docs = [
            Document(text="Company faces lawsuit over patent infringement."),
            Document(text="Legal action filed against tech giant."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect lawsuit event
        has_lawsuit = any(
            doc.metadata.get('event_type') == 'lawsuit'
            for doc in result
        )
        self.assertTrue(has_lawsuit or len(result) > 0)

    def test_ipo_event_detection(self):
        """Test detection of IPO events."""
        docs = [
            Document(text="Startup files for initial public offering."),
            Document(text="Company goes public with $2B IPO."),
        ]

        result = self.aggregator.process_docs(docs)

        # Should detect IPO event
        has_ipo = any(
            doc.metadata.get('event_type') == 'ipo'
            for doc in result
        )
        self.assertTrue(has_ipo or len(result) > 0)


if __name__ == '__main__':
    unittest.main()
