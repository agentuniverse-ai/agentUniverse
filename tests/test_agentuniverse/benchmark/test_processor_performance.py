# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_processor_performance.py

import time
import unittest
from typing import List
import statistics

from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class PerformanceBenchmark:
    """Helper class for performance benchmarking."""

    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        return result, elapsed

    @staticmethod
    def run_multiple_times(func, iterations=10, *args, **kwargs):
        """Run function multiple times and return statistics."""
        times = []
        results = []

        for _ in range(iterations):
            result, elapsed = PerformanceBenchmark.measure_execution_time(func, *args, **kwargs)
            times.append(elapsed)
            results.append(result)

        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'results': results
        }


class TestSemanticDeduplicatorPerformance(unittest.TestCase):
    """Performance benchmarks for SemanticDeduplicator."""

    def setUp(self):
        """Set up test fixtures."""
        self.deduplicator = SemanticDeduplicator(
            name='benchmark',
            use_embeddings=False  # Disable for faster tests
        )

    def test_small_dataset_performance(self):
        """Benchmark with small dataset (10 documents)."""
        docs = [Document(text=f"Document {i} with unique content.") for i in range(10)]

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.deduplicator.process_docs, docs
        )

        print(f"\nSmall dataset (10 docs): {elapsed:.4f}s")
        self.assertLess(elapsed, 0.1, "Small dataset should process in <100ms")

    def test_medium_dataset_performance(self):
        """Benchmark with medium dataset (100 documents)."""
        docs = [Document(text=f"Document {i} " * 50) for i in range(100)]

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.deduplicator.process_docs, docs
        )

        print(f"\nMedium dataset (100 docs): {elapsed:.4f}s")
        self.assertLess(elapsed, 2.0, "Medium dataset should process in <2s")

    def test_large_dataset_performance(self):
        """Benchmark with large dataset (1000 documents)."""
        docs = [Document(text=f"Document {i} " * 100) for i in range(1000)]

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.deduplicator.process_docs, docs
        )

        print(f"\nLarge dataset (1000 docs): {elapsed:.4f}s")
        self.assertLess(elapsed, 30.0, "Large dataset should process in <30s")

    def test_duplicate_detection_performance(self):
        """Benchmark duplicate detection with various duplicate ratios."""
        # 50% duplicates
        docs = []
        for i in range(50):
            docs.append(Document(text=f"Unique document {i}"))
            docs.append(Document(text=f"Unique document {i}"))  # Duplicate

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.deduplicator.process_docs, docs
        )

        print(f"\n50% duplicates (100 docs): {elapsed:.4f}s")
        self.assertEqual(len(result), 50, "Should remove all duplicates")


class TestContractClauseFragmenterPerformance(unittest.TestCase):
    """Performance benchmarks for ContractClauseFragmenter."""

    def setUp(self):
        """Set up test fixtures."""
        self.fragmenter = ContractClauseFragmenter(name='benchmark')

    def test_simple_contract_performance(self):
        """Benchmark with simple contract."""
        contract = """
Article 1. Definitions
Content here.

Article 2. Terms
More content.
"""
        doc = Document(text=contract)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.fragmenter.process_docs, [doc]
        )

        print(f"\nSimple contract: {elapsed:.4f}s")
        self.assertLess(elapsed, 0.05, "Simple contract should process in <50ms")

    def test_complex_contract_performance(self):
        """Benchmark with complex contract (many clauses)."""
        # Generate contract with 100 clauses
        clauses = []
        for i in range(100):
            clauses.append(f"Article {i}. Clause Title\n\nClause content " * 10)

        contract = "\n\n".join(clauses)
        doc = Document(text=contract)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.fragmenter.process_docs, [doc]
        )

        print(f"\nComplex contract (100 clauses): {elapsed:.4f}s")
        print(f"  Generated {len(result)} clause documents")
        self.assertLess(elapsed, 2.0, "Complex contract should process in <2s")

    def test_very_long_contract_performance(self):
        """Benchmark with very long contract."""
        # Generate 1MB contract
        content = "Article 1. Test\n\n" + "Content. " * 50000
        doc = Document(text=content)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.fragmenter.process_docs, [doc]
        )

        print(f"\nVery long contract (~1MB): {elapsed:.4f}s")
        self.assertLess(elapsed, 5.0, "Very long contract should process in <5s")


class TestAcademicPaperFragmenterPerformance(unittest.TestCase):
    """Performance benchmarks for AcademicPaperFragmenter."""

    def setUp(self):
        """Set up test fixtures."""
        self.fragmenter = AcademicPaperFragmenter(
            name='benchmark',
            detect_sections=True,
            extract_citations=True
        )

    def test_short_paper_performance(self):
        """Benchmark with short paper."""
        paper = """
Abstract

This paper presents a method [1, 2].

Introduction

Previous work has shown [3, 4, 5].
"""
        doc = Document(text=paper)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.fragmenter.process_docs, [doc]
        )

        print(f"\nShort paper: {elapsed:.4f}s")
        self.assertLess(elapsed, 0.1, "Short paper should process in <100ms")

    def test_full_paper_performance(self):
        """Benchmark with full-length paper."""
        # Generate realistic paper (5000 words)
        sections = {
            'Abstract': 200,
            'Introduction': 1000,
            'Related Work': 800,
            'Methods': 1000,
            'Results': 1000,
            'Discussion': 800,
            'Conclusion': 200
        }

        paper_parts = []
        for section, word_count in sections.items():
            content = f"{section}\n\n" + " ".join([f"word{i}" for i in range(word_count)])
            paper_parts.append(content)

        paper = "\n\n".join(paper_parts)
        doc = Document(text=paper)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.fragmenter.process_docs, [doc]
        )

        print(f"\nFull paper (~5000 words): {elapsed:.4f}s")
        print(f"  Generated {len(result)} argument documents")
        self.assertLess(elapsed, 2.0, "Full paper should process in <2s")


class TestFinancialIndicatorExtractorPerformance(unittest.TestCase):
    """Performance benchmarks for FinancialIndicatorExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialIndicatorExtractor(
            name='benchmark',
            use_llm=False  # Disable LLM for benchmark
        )

    def test_simple_report_performance(self):
        """Benchmark with simple financial report."""
        report = """
Q1 2024 Results

Revenue: $100M
Profit: $20M
EPS: $1.50
"""
        doc = Document(text=report)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.extractor.process_docs, [doc]
        )

        print(f"\nSimple financial report: {elapsed:.4f}s")
        self.assertLess(elapsed, 0.1, "Simple report should process in <100ms")

    def test_detailed_report_performance(self):
        """Benchmark with detailed financial report."""
        # Generate detailed report with many metrics
        metrics = []
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            q_num = int(quarter[1:])
            metrics.append(f"""
{quarter} 2024 Results

Revenue: ${100 + q_num}M, up 10% YoY
Net profit: ${20 + q_num}M
Gross margin: 45%
Operating margin: 30%
EPS: $1.50
Free cash flow: ${25 + q_num}M
""")

        report = "\n\n".join(metrics)
        doc = Document(text=report)

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.extractor.process_docs, [doc]
        )

        print(f"\nDetailed financial report: {elapsed:.4f}s")
        metrics_count = len(result[0].metadata.get('financial_metrics', {}))
        print(f"  Extracted {metrics_count} metrics")
        self.assertLess(elapsed, 1.0, "Detailed report should process in <1s")

    def test_batch_processing_performance(self):
        """Benchmark batch processing of multiple reports."""
        docs = []
        for i in range(10):
            report = f"""
Report {i}

Revenue: ${100 + i}M
Profit: ${20 + i}M
EPS: ${1.5 + i * 0.1}
"""
            docs.append(Document(text=report))

        result, elapsed = PerformanceBenchmark.measure_execution_time(
            self.extractor.process_docs, docs
        )

        print(f"\nBatch processing (10 reports): {elapsed:.4f}s")
        print(f"  Average per report: {elapsed / 10:.4f}s")
        self.assertLess(elapsed, 1.0, "Batch should process in <1s")


class TestPipelinePerformance(unittest.TestCase):
    """Performance benchmarks for processor pipelines."""

    def test_full_pipeline_performance(self):
        """Benchmark complete processing pipeline."""
        # Generate test documents
        docs = []
        for i in range(20):
            text = f"""
Article {i}. Test Article

This is test content for article {i}.

Article {i}. Test Article

This is test content for article {i}.
"""
            docs.append(Document(text=text))

        # Stage 1: Fragment
        fragmenter = ContractClauseFragmenter(name='test')
        start = time.time()
        fragmented = fragmenter.process_docs(docs)
        fragment_time = time.time() - start

        # Stage 2: Deduplicate
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)
        start = time.time()
        final = deduplicator.process_docs(fragmented)
        dedupe_time = time.time() - start

        total_time = fragment_time + dedupe_time

        print(f"\nFull pipeline (20 docs):")
        print(f"  Fragmentation: {fragment_time:.4f}s")
        print(f"  Deduplication: {dedupe_time:.4f}s")
        print(f"  Total: {total_time:.4f}s")
        print(f"  Input docs: {len(docs)}")
        print(f"  After fragmentation: {len(fragmented)}")
        print(f"  Final docs: {len(final)}")

        self.assertLess(total_time, 5.0, "Full pipeline should complete in <5s")


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage patterns."""

    def test_large_document_memory(self):
        """Test memory handling with large documents."""
        import sys

        # Create large document (10MB)
        large_text = "A" * (10 * 1024 * 1024)
        doc = Document(text=large_text)

        # Get initial size
        initial_size = sys.getsizeof(doc)
        print(f"\nLarge document size: {initial_size / 1024 / 1024:.2f}MB")

        # Process through deduplicator
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)
        result = deduplicator.process_docs([doc])

        # Verify processing completes
        self.assertEqual(len(result), 1)

    def test_batch_memory_efficiency(self):
        """Test memory efficiency with batch processing."""
        # Create many small documents
        docs = [Document(text=f"Document {i} content") for i in range(1000)]

        # Process in batch
        deduplicator = SemanticDeduplicator(name='test', use_embeddings=False)
        result = deduplicator.process_docs(docs)

        # Should complete without memory issues
        self.assertGreaterEqual(len(result), 1)


def run_all_benchmarks():
    """Run all performance benchmarks and generate report."""
    print("\n" + "=" * 60)
    print("KNOWLEDGE PROCESSOR PERFORMANCE BENCHMARK REPORT")
    print("=" * 60)

    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_all_benchmarks()
