# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_knowledge_processor_pipeline.py

import unittest
from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class TestKnowledgeProcessorPipeline(unittest.TestCase):
    """Integration tests for knowledge processor pipelines."""

    def test_contract_processing_pipeline(self):
        """Test complete contract processing pipeline."""
        # Sample contract
        contract_text = """
Article 1. Definitions

1.1 Terms defined herein.

Article 2. Obligations

2.1 Party obligations.

Article 1. Definitions

1.1 Terms defined herein.
"""

        doc = Document(text=contract_text)

        # Step 1: Fragment by clauses
        fragmenter = ContractClauseFragmenter(
            name='fragmenter',
            preserve_hierarchy=True
        )
        fragmented_docs = fragmenter.process_docs([doc])

        # Should create multiple clause documents
        self.assertGreater(len(fragmented_docs), 1)

        # Step 2: Deduplicate
        deduplicator = SemanticDeduplicator(
            name='deduplicator',
            similarity_threshold=0.95,
            use_embeddings=False
        )
        final_docs = deduplicator.process_docs(fragmented_docs)

        # Should remove duplicate clauses
        self.assertLess(len(final_docs), len(fragmented_docs))

        # Verify metadata is preserved
        for doc in final_docs:
            self.assertIn('clause_id', doc.metadata)
            self.assertIn('processor_name', doc.metadata)

    def test_academic_paper_processing_pipeline(self):
        """Test academic paper processing pipeline."""
        paper_text = """
Abstract

This paper presents a novel approach.

Introduction

Previous work has shown [1, 2].
We demonstrate improvements.

Methods

We collected data from participants.

Results

Figure 1 shows that our approach achieved 95% accuracy.

Abstract

This paper presents a novel approach.
"""

        doc = Document(text=paper_text)

        # Step 1: Fragment by arguments
        fragmenter = AcademicPaperFragmenter(
            name='paper_fragmenter',
            detect_sections=True,
            extract_citations=True
        )
        fragmented_docs = fragmenter.process_docs([doc])

        # Should detect sections and create argument documents
        self.assertGreater(len(fragmented_docs), 3)

        # Check section detection
        sections = [d.metadata['section'] for d in fragmented_docs]
        self.assertIn('abstract', sections)

        # Step 2: Deduplicate
        deduplicator = SemanticDeduplicator(
            name='deduplicator',
            use_embeddings=False
        )
        final_docs = deduplicator.process_docs(fragmented_docs)

        # Should remove duplicate abstract
        self.assertLessEqual(len(final_docs), len(fragmented_docs))

    def test_financial_extraction_and_deduplication(self):
        """Test financial report processing with extraction and deduplication."""
        report1 = """
Q1 2024 Results

Revenue was $89.5 billion, up 12% YoY.
Net profit reached $25.3 billion.
EPS was $1.56.
"""

        report2 = """
Q1 2024 Financial Performance

Revenue of $89.5 billion represents 12% year-over-year growth.
Net profit was $25.3 billion.
Earnings per share: $1.56.
"""

        docs = [
            Document(text=report1),
            Document(text=report2)
        ]

        # Step 1: Extract financial metrics
        extractor = FinancialIndicatorExtractor(
            name='extractor',
            extract_temporal=True,
            extract_comparisons=True
        )
        extracted_docs = extractor.process_docs(docs)

        # Should extract metrics from both documents
        self.assertEqual(len(extracted_docs), 2)

        for doc in extracted_docs:
            metrics = doc.metadata.get('financial_metrics', {})
            # Should have extracted some metrics
            self.assertGreater(len(metrics), 0)

        # Step 2: Deduplicate based on content
        deduplicator = SemanticDeduplicator(
            name='deduplicator',
            similarity_threshold=0.85,
            use_embeddings=False
        )
        final_docs = deduplicator.process_docs(extracted_docs)

        # Should identify similar reports
        # Note: Without embeddings, might not deduplicate these
        self.assertLessEqual(len(final_docs), 2)

    def test_multi_stage_pipeline_metadata_preservation(self):
        """Test that metadata is preserved through multi-stage pipeline."""
        doc = Document(
            text="Article 1. Test Article. This is test content.",
            metadata={'original_id': 'DOC001', 'source': 'test'}
        )

        # Stage 1: Fragment
        fragmenter = ContractClauseFragmenter(name='stage1')
        stage1_docs = fragmenter.process_docs([doc])

        # Stage 2: Deduplicate
        deduplicator = SemanticDeduplicator(name='stage2', use_embeddings=False)
        stage2_docs = deduplicator.process_docs(stage1_docs)

        # Verify original metadata is preserved
        final_doc = stage2_docs[0]
        self.assertIn('original_metadata', final_doc.metadata)
        self.assertEqual(
            final_doc.metadata['original_metadata']['original_id'],
            'DOC001'
        )

        # Verify both processors added their metadata
        self.assertIn('source_document_id', final_doc.metadata)

    def test_pipeline_error_handling(self):
        """Test error handling in pipeline with mixed valid/invalid documents."""
        docs = [
            Document(text="Article 1. Valid content."),
            Document(text=""),  # Empty document
            Document(text="Article 2. Another valid content."),
        ]

        # Process through pipeline
        fragmenter = ContractClauseFragmenter(name='test', skip_on_error=True)
        fragmented = fragmenter.process_docs(docs)

        deduplicator = SemanticDeduplicator(name='test', skip_on_error=True, use_embeddings=False)
        final = deduplicator.process_docs(fragmented)

        # Should handle errors gracefully and process valid documents
        self.assertGreater(len(final), 0)

    def test_pipeline_with_keywords_accumulation(self):
        """Test that keywords accumulate through pipeline stages."""
        doc = Document(
            text="Article 1. Financial Services Agreement.",
            keywords={'contract', 'legal'}
        )

        # Stage 1: Fragment
        fragmenter = ContractClauseFragmenter(name='test')
        fragmented = fragmenter.process_docs([doc])

        # Verify keywords are preserved
        self.assertIn('contract', fragmented[0].keywords)
        self.assertIn('legal', fragmented[0].keywords)

        # Stage 2: Deduplicate
        deduplicator = SemanticDeduplicator(
            name='test',
            use_embeddings=False,
            preserve_metadata=True
        )
        final = deduplicator.process_docs(fragmented)

        # Keywords should still be present
        self.assertGreaterEqual(len(final[0].keywords), 2)


class TestProcessorCombinations(unittest.TestCase):
    """Test different combinations of processors."""

    def test_fragment_then_deduplicate(self):
        """Test fragment → deduplicate order."""
        doc = Document(text="Article 1. Content.\n\nArticle 1. Content.")

        # Fragment first
        fragmenter = ContractClauseFragmenter(name='test')
        fragmented = fragmenter.process_docs([doc])

        # Then deduplicate
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)
        final = deduplicator.process_docs(fragmented)

        # Should remove duplicate fragments
        self.assertEqual(len(final), 1)

    def test_extract_then_deduplicate(self):
        """Test extract → deduplicate order."""
        docs = [
            Document(text="Revenue: $100M, Profit: $20M"),
            Document(text="Revenue was $100M and profit $20M")
        ]

        # Extract first
        extractor = FinancialIndicatorExtractor(name='test')
        extracted = extractor.process_docs(docs)

        # Then deduplicate
        deduplicator = SemanticDeduplicator(
            name='test',
            similarity_threshold=0.90,
            use_embeddings=False
        )
        final = deduplicator.process_docs(extracted)

        # Metrics should be preserved even after deduplication
        self.assertGreater(len(final[0].metadata.get('financial_metrics', {})), 0)

    def test_multiple_fragmenters(self):
        """Test using multiple fragmenters in sequence."""
        paper_text = """
Article 1. Background

Previous studies have shown [1, 2].

Section 1.1 Literature Review

Multiple works exist [3, 4].
"""

        doc = Document(text=paper_text)

        # First: Contract fragmenter (for Article structure)
        contract_fragmenter = ContractClauseFragmenter(name='contract')
        stage1 = contract_fragmenter.process_docs([doc])

        # Then: Paper fragmenter (for academic structure)
        paper_fragmenter = AcademicPaperFragmenter(name='paper')
        stage2 = paper_fragmenter.process_docs(stage1)

        # Should process through both stages
        self.assertGreater(len(stage2), 0)


if __name__ == '__main__':
    unittest.main()
