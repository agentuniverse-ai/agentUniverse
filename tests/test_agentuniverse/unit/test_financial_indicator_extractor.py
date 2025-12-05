# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_financial_indicator_extractor.py

import unittest
from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class TestFinancialIndicatorExtractor(unittest.TestCase):
    """Unit tests for FinancialIndicatorExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialIndicatorExtractor(
            name='test_extractor',
            extract_temporal=True,
            extract_comparisons=True,
            use_llm=False  # Disable LLM for unit tests
        )

    def test_basic_revenue_extraction(self):
        """Test extraction of revenue metrics."""
        report = """
Q4 2024 Results

Revenue reached $100 million.
Total revenue was $100M for the quarter.
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        self.assertEqual(len(result), 1)
        metrics = result[0].metadata.get('financial_metrics', {})
        self.assertIn('revenue', metrics)
        self.assertGreater(len(metrics['revenue']), 0)

    def test_profit_metrics_extraction(self):
        """Test extraction of profit-related metrics."""
        report = """
Financial Performance

Net profit: $25 million
Gross profit reached $50M
Operating profit was $35M
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        # Should extract different types of profit
        profit_keys = [k for k in metrics.keys() if 'profit' in k.lower()]
        self.assertGreater(len(profit_keys), 0)

    def test_margin_extraction(self):
        """Test extraction of margin percentages."""
        report = """
Margins Analysis

Gross margin: 45%
Operating margin was 30%
Net profit margin reached 20%
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        margin_keys = [k for k in metrics.keys() if 'margin' in k.lower()]
        self.assertGreater(len(margin_keys), 0)

    def test_eps_extraction(self):
        """Test earnings per share extraction."""
        report = """
Earnings Report

Diluted EPS: $1.56
Basic earnings per share was $1.60
EPS reached $1.56 per share
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        self.assertIn('eps', metrics)

    def test_temporal_context_extraction(self):
        """Test extraction of time periods."""
        report = """
Q1 2024 Results

Revenue: $100M for Q1 2024
Q2 2024 profit: $25M
FY 2023 total revenue was $400M
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should have temporal context
        has_temporal = False
        for metric_list in result[0].metadata.get('financial_metrics', {}).values():
            for metric in metric_list:
                if metric.get('time_period'):
                    has_temporal = True
                    break

        self.assertTrue(has_temporal)

    def test_yoy_comparison_extraction(self):
        """Test year-over-year comparison extraction."""
        report = """
Growth Metrics

Revenue up 12% year-over-year
Profit increased 15% YoY
YoY growth of 10%
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should detect comparisons
        comparisons = result[0].metadata.get('comparative_metrics', [])
        self.assertGreater(len(comparisons), 0)

        # Check for YoY type
        has_yoy = any(c.get('comparison_type') == 'yoy' for c in comparisons)
        self.assertTrue(has_yoy)

    def test_qoq_comparison_extraction(self):
        """Test quarter-over-quarter comparison extraction."""
        report = """
Sequential Growth

Revenue grew 5% quarter-over-quarter
QoQ improvement of 3%
Sequential growth: 4%
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        comparisons = result[0].metadata.get('comparative_metrics', [])
        has_qoq = any(
            c.get('comparison_type') in ['qoq', 'sequential']
            for c in comparisons
        )
        self.assertTrue(has_qoq)

    def test_currency_detection(self):
        """Test different currency format detection."""
        report = """
International Results

US revenue: $100M
European revenue: €80M
UK revenue: £60M
China revenue: ¥500M
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should detect multiple currencies
        currencies = set()
        for metric_list in result[0].metadata.get('financial_metrics', {}).values():
            for metric in metric_list:
                if metric.get('currency'):
                    currencies.add(metric['currency'])

        self.assertGreater(len(currencies), 1)

    def test_scale_factor_detection(self):
        """Test detection of billion/million/thousand scale."""
        report = """
Financial Scale

Revenue: $1.5 billion
Profit: $250 million
Cash: $50 thousand
Assets: $2.3B
Debt: $500M
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should detect different scales
        scales = set()
        for metric_list in result[0].metadata.get('financial_metrics', {}).values():
            for metric in metric_list:
                if metric.get('scale'):
                    scales.add(metric['scale'])

        self.assertGreater(len(scales), 1)

    def test_ratio_extraction(self):
        """Test financial ratio extraction."""
        report = """
Key Ratios

Debt-to-equity ratio: 1.5
Current ratio: 2.0
P/E ratio: 25
ROE: 15%
ROA: 10%
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        # Should extract various ratios
        ratio_count = sum(
            1 for key in metrics.keys()
            if 'ratio' in key.lower() or key.lower() in ['roe', 'roa', 'roi']
        )
        self.assertGreater(ratio_count, 0)

    def test_multiple_metrics_in_sentence(self):
        """Test extraction when multiple metrics in same sentence."""
        report = """
Q4 Performance

Revenue was $100M with profit of $25M and EPS of $1.50.
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        # Should extract all three metrics
        self.assertGreaterEqual(len(metrics), 2)

    def test_negative_values(self):
        """Test extraction of negative financial values."""
        report = """
Loss Report

Net loss: -$10M
Negative earnings: -$5 million
Operating loss of ($3M)
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should handle negative values
        has_negative = False
        for metric_list in result[0].metadata.get('financial_metrics', {}).values():
            for metric in metric_list:
                if metric.get('value', 0) < 0:
                    has_negative = True
                    break

        self.assertTrue(has_negative)

    def test_percentage_metrics(self):
        """Test extraction of percentage-based metrics."""
        report = """
Performance Metrics

Growth rate: 15%
Market share: 25%
Churn rate: 5%
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should extract percentage metrics
        metrics = result[0].metadata.get('financial_metrics', {})
        self.assertGreater(len(metrics), 0)

    def test_metadata_preservation(self):
        """Test preservation of original metadata."""
        doc = Document(
            text="Revenue: $100M",
            metadata={'company': 'TestCo', 'report_date': '2024-01-01'}
        )

        result = self.extractor.process_docs([doc])

        # Original metadata should be preserved
        self.assertIn('original_metadata', result[0].metadata)
        self.assertEqual(
            result[0].metadata['original_metadata']['company'],
            'TestCo'
        )

    def test_empty_document(self):
        """Test handling of empty documents."""
        doc = Document(text="")
        result = self.extractor.process_docs([doc])

        # Should handle gracefully
        self.assertEqual(len(result), 1)

    def test_document_without_metrics(self):
        """Test handling of documents with no financial metrics."""
        doc = Document(text="This is a document with no financial information.")
        result = self.extractor.process_docs([doc])

        # Should return document with empty or minimal metrics
        self.assertEqual(len(result), 1)

    def test_batch_processing(self):
        """Test processing multiple documents."""
        docs = [
            Document(text="Revenue: $100M"),
            Document(text="Profit: $25M"),
            Document(text="EPS: $1.50"),
        ]

        result = self.extractor.process_docs(docs)

        # Should process all documents
        self.assertEqual(len(result), 3)

        # Each should have metrics
        for doc in result:
            self.assertIn('financial_metrics', doc.metadata)

    def test_complex_report_extraction(self):
        """Test extraction from complex real-world report."""
        report = """
Q4 2024 Financial Results

Revenue and Profitability

Total revenue for Q4 2024 reached $89.5 billion, representing a 12% YoY growth.
Net income was $25.3 billion, up from $22.1 billion YoY, a 14.5% increase.

Earnings Per Share

Diluted EPS reached $1.56, compared to $1.35 in Q4 2023.

Operating Metrics

Gross margin was 46.2%, compared to 45.2% in the year-ago quarter.
Operating margin reached 32.5%, up from 31.4% in Q4 2023.
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        metrics = result[0].metadata.get('financial_metrics', {})
        comparisons = result[0].metadata.get('comparative_metrics', [])

        # Should extract multiple metric types
        self.assertGreaterEqual(len(metrics), 4)

        # Should extract comparisons
        self.assertGreater(len(comparisons), 0)

    def test_unicode_and_special_chars(self):
        """Test handling of unicode and special characters."""
        report = """
财务报告

收入：¥100M
利润：€50M with growth → 15%
特殊符号 ≈ $25M ± $2M
"""
        doc = Document(text=report)
        result = self.extractor.process_docs([doc])

        # Should handle unicode gracefully
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
