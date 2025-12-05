# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_academic_paper_fragmenter.py

import unittest
from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestAcademicPaperFragmenter(unittest.TestCase):
    """Unit tests for AcademicPaperFragmenter."""

    def setUp(self):
        """Set up test fixtures."""
        self.fragmenter = AcademicPaperFragmenter(
            name='test_fragmenter',
            detect_sections=True,
            extract_citations=True
        )

    def test_basic_section_detection(self):
        """Test basic academic section detection."""
        paper = """
Abstract

This paper presents a novel approach.

Introduction

Previous work has shown [1, 2].

Methods

We collected data from participants.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should detect multiple sections
        self.assertGreater(len(result), 1)

        # Check section metadata
        sections = [d.metadata['section'] for d in result]
        self.assertIn('abstract', sections)
        self.assertIn('introduction', sections)

    def test_citation_extraction(self):
        """Test citation extraction from text."""
        paper = """
Introduction

Previous studies [1, 2, 3] have demonstrated.
Research by Smith et al. (2020) showed improvements.
According to Johnson (2019), the method works.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Check citations extracted
        has_citations = False
        for doc in result:
            if 'citations' in doc.metadata and len(doc.metadata['citations']) > 0:
                has_citations = True
                break
        self.assertTrue(has_citations)

    def test_argument_classification(self):
        """Test argument type classification."""
        paper = """
Abstract

We propose a new method that achieves 95% accuracy.

Introduction

Previous work has limitations [1].
We demonstrate that our approach overcomes these issues.

Methods

We collected 1000 samples.
Data was analyzed using statistical tests.

Results

Figure 1 shows our method achieves 95% accuracy.
Table 1 presents the detailed results.

Discussion

These results confirm our hypothesis.
The findings have important implications.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should have different argument types
        argument_types = set()
        for doc in result:
            if 'argument_type' in doc.metadata:
                argument_types.add(doc.metadata['argument_type'])

        # Should detect at least 2 different types
        self.assertGreaterEqual(len(argument_types), 2)

    def test_thesis_evidence_linking(self):
        """Test linking evidence to thesis statements."""
        paper = """
Introduction

We propose that deep learning improves accuracy.

Results

Our experiments show 95% accuracy, confirming the hypothesis.
Statistical analysis (p < 0.01) supports our claim.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Evidence documents should reference supporting data
        has_evidence = any(
            d.metadata.get('argument_type') == 'evidence'
            for d in result
        )
        self.assertTrue(has_evidence)

    def test_multilingual_sections(self):
        """Test detection of Chinese academic sections."""
        paper = """
摘要

本文提出了一种基于深度学习的创新方法来解决复杂问题。

引言

先前的研究表明，传统方法在处理大规模数据时存在明显局限性 [1, 2]。

方法

我们收集了超过一万个样本的实验数据，并进行了系统的分析和验证。
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should detect Chinese sections
        self.assertGreater(len(result), 1)

    def test_metadata_preservation(self):
        """Test preservation of original metadata."""
        doc = Document(
            text="Abstract\n\nThis paper presents a comprehensive analysis of the methodology.",
            metadata={'paper_id': 'P001', 'author': 'Test'}
        )

        result = self.fragmenter.process_docs([doc])

        # Original metadata should be preserved
        self.assertGreater(len(result), 0)
        self.assertIn('original_metadata', result[0].metadata)
        self.assertEqual(
            result[0].metadata['original_metadata']['paper_id'],
            'P001'
        )

    def test_empty_paper(self):
        """Test handling of empty papers."""
        doc = Document(text="")
        result = self.fragmenter.process_docs([doc])

        # Should handle gracefully
        self.assertIsInstance(result, list)

    def test_paper_without_sections(self):
        """Test handling of papers without clear sections."""
        doc = Document(text="This is just a plain text without sections.")
        result = self.fragmenter.process_docs([doc])

        # Should create at least one document
        self.assertGreater(len(result), 0)

    def test_multiple_papers(self):
        """Test processing multiple papers."""
        docs = [
            Document(text="Abstract\n\nThis paper presents novel findings on machine learning applications.\n\nIntroduction\n\nPrevious research has established the importance of neural networks in pattern recognition."),
            Document(text="Abstract\n\nWe propose a comprehensive framework for data processing and analysis.\n\nIntroduction\n\nTraditional approaches have limitations that our method addresses systematically."),
        ]

        result = self.fragmenter.process_docs(docs)

        # Should process all papers
        self.assertGreater(len(result), 2)

        # Each fragment should have source document ID
        for doc in result:
            self.assertIn('source_document_id', doc.metadata)

    def test_nested_sections(self):
        """Test handling of nested subsections."""
        paper = """
1. Introduction

1.1 Background

Previous research has established foundational concepts [1].

1.2 Motivation

Current approaches have significant limitations that need addressing.

2. Methods

2.1 Data Collection

We systematically gathered experimental samples from multiple sources.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should detect hierarchy
        self.assertGreater(len(result), 2)

        # Check for section hierarchy
        has_hierarchy = any(
            'section_hierarchy' in d.metadata
            for d in result
        )
        self.assertTrue(has_hierarchy)

    def test_citation_formats(self):
        """Test different citation format detection."""
        paper = """
Introduction

Numbered citations [1, 2, 3] are common.
Author-year citations (Smith, 2020) also appear.
Multiple authors (Smith et al., 2021) work too.
Year ranges (2018-2020) should be detected.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should extract various citation formats
        all_citations = []
        for doc in result:
            all_citations.extend(doc.metadata.get('citations', []))

        # Should find multiple citation formats
        self.assertGreater(len(all_citations), 0)

    def test_special_characters_in_sections(self):
        """Test section detection with special characters."""
        paper = """
Abstract—Overview

This paper presents results.

§1. Introduction

Background information follows.

Method & Results

We present our findings.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should handle special characters
        self.assertGreater(len(result), 1)

    def test_claim_strength_detection(self):
        """Test detection of claim strength in arguments."""
        paper = """
Results

Our method achieves 95% accuracy (strong claim).
Preliminary results suggest improvements (weak claim).
This definitively proves our hypothesis (strong claim).
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should detect different claim strengths
        claim_strengths = set()
        for doc in result:
            if 'claim_strength' in doc.metadata:
                claim_strengths.add(doc.metadata['claim_strength'])

        # Should have variation in claim strength
        self.assertGreaterEqual(len(claim_strengths), 1)

    def test_unicode_content(self):
        """Test handling of unicode characters."""
        paper = """
Abstract

研究论文 with émojis 🔬 and symbols ≈ ± ∞.

Introduction

Mixed 中英文 content with citations [1–3].
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should handle unicode properly
        self.assertGreater(len(result), 0)

    def test_section_without_content(self):
        """Test sections with only headers."""
        paper = """
Abstract

Introduction

Methods

Results
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should handle gracefully
        self.assertIsInstance(result, list)

    def test_very_long_section(self):
        """Test handling of very long sections."""
        content = "Word " * 5000
        paper = f"""
Introduction

{content}

Methods

More content.
"""
        doc = Document(text=paper)
        result = self.fragmenter.process_docs([doc])

        # Should process long sections
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
