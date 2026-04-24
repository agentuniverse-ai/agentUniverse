# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_contract_clause_fragmenter.py

import unittest
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestContractClauseFragmenter(unittest.TestCase):
    """Test cases for ContractClauseFragmenter."""

    def setUp(self):
        """Set up test fixtures."""
        self.fragmenter = ContractClauseFragmenter(
            name='test_fragmenter',
            preserve_hierarchy=True,
            extract_references=True,
            skip_on_error=True
        )

    def test_article_detection(self):
        """Test detection of Article clauses."""
        contract_text = """
Article 1. Definitions

This agreement defines the following terms.

Article 2. Terms and Conditions

The parties agree to the following terms.
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Should detect 2 articles
        self.assertGreaterEqual(len(result), 2)

        # Check that articles are detected
        article_types = [d.metadata['clause_type'] for d in result]
        self.assertIn('article', article_types)

    def test_section_detection(self):
        """Test detection of Section clauses."""
        contract_text = """
Section 1.1 Scope

This section defines the scope.

Section 1.2 Application

This section defines application.
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Should detect sections
        self.assertGreaterEqual(len(result), 2)

    def test_numbered_clauses(self):
        """Test detection of numbered clauses."""
        contract_text = """
1. First Clause

Content of first clause.

1.1 Sub-clause

Content of sub-clause.

2. Second Clause

Content of second clause.
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Should detect numbered clauses
        self.assertGreaterEqual(len(result), 3)

    def test_hierarchy_preservation(self):
        """Test that hierarchy is correctly preserved."""
        contract_text = """
Article 1. Main Article

Main content.

Section 1.1 Subsection

Subsection content.
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Find article and section
        article = next((d for d in result if d.metadata['clause_type'] == 'article'), None)
        section = next((d for d in result if d.metadata['clause_type'] == 'section'), None)

        self.assertIsNotNone(article)
        self.assertIsNotNone(section)

        # Check hierarchy levels
        self.assertEqual(article.metadata['hierarchy_level'], 0)
        self.assertEqual(section.metadata['hierarchy_level'], 1)

        # Check parent-child relationship
        if section:
            self.assertIsNotNone(section.metadata.get('parent_clause'))

    def test_chinese_clause_detection(self):
        """Test detection of Chinese clauses."""
        contract_text = """
第一条 定义

本协议定义如下术语。

第二条 条款与条件

双方同意以下条款。
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Should detect Chinese clauses
        self.assertGreaterEqual(len(result), 2)

    def test_metadata_structure(self):
        """Test that metadata is correctly structured."""
        contract_text = """
Article 1. Test Article

Test content.
"""
        doc = Document(text=contract_text, metadata={'contract_id': 'TEST001'})
        result = self.fragmenter.process_docs([doc])

        clause_doc = result[0]
        metadata = clause_doc.metadata

        # Check required metadata fields
        self.assertIn('processor_name', metadata)
        self.assertIn('clause_id', metadata)
        self.assertIn('clause_type', metadata)
        self.assertIn('hierarchy_level', metadata)
        self.assertIn('position', metadata)
        self.assertIn('original_metadata', metadata)

    def test_empty_document(self):
        """Test handling of empty document."""
        doc = Document(text="")
        result = self.fragmenter.process_docs([doc])

        # Should return at least one document
        self.assertGreaterEqual(len(result), 1)

    def test_unstructured_document(self):
        """Test handling of unstructured document."""
        doc = Document(text="This is just plain text without any clause structure.")
        result = self.fragmenter.process_docs([doc])

        # Should return single unstructured clause
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata['clause_type'], 'unstructured')

    def test_min_clause_length_filter(self):
        """Test that short clauses are filtered out."""
        fragmenter = ContractClauseFragmenter(
            name='test',
            min_clause_length=50  # Require at least 50 characters
        )

        contract_text = """
Article 1. Test

A.

Article 2. Longer Article

This is a longer article with sufficient content to pass the minimum length requirement.
"""
        doc = Document(text=contract_text)
        result = fragmenter.process_docs([doc])

        # Short clause should be filtered out
        self.assertEqual(len(result), 1)

    def test_cross_references(self):
        """Test extraction of cross-references."""
        contract_text = """
Article 1. Definitions

Terms defined herein.

Article 2. Terms

As defined in Article 1, the terms shall apply.
"""
        doc = Document(text=contract_text)
        result = self.fragmenter.process_docs([doc])

        # Find Article 2
        article2 = next((d for d in result if 'Article 2' in d.text), None)

        if article2 and 'clause_references' in article2.metadata:
            # Should detect reference to Article 1
            self.assertGreater(len(article2.metadata['clause_references']), 0)


class TestContractClauseFragmenterEdgeCases(unittest.TestCase):
    """Test edge cases for ContractClauseFragmenter."""

    def test_mixed_numbering_systems(self):
        """Test handling of mixed numbering systems."""
        contract_text = """
Article I. Roman Numerals

Content.

Article 1. Arabic Numerals

Content.

1. Simple Number

Content.
"""
        fragmenter = ContractClauseFragmenter(name='test')
        doc = Document(text=contract_text)
        result = fragmenter.process_docs([doc])

        # Should handle different numbering systems
        self.assertGreaterEqual(len(result), 3)

    def test_nested_clauses(self):
        """Test handling of deeply nested clauses."""
        contract_text = """
1. Top Level

Content.

1.1 Level 2

Content.

1.1.1 Level 3

Content.

1.1.1.1 Level 4

Content.
"""
        fragmenter = ContractClauseFragmenter(name='test')
        doc = Document(text=contract_text)
        result = fragmenter.process_docs([doc])

        # Should handle deep nesting
        hierarchy_levels = [d.metadata['hierarchy_level'] for d in result]
        self.assertGreater(max(hierarchy_levels), 2)

    def test_clause_without_content(self):
        """Test handling of clause headers without content."""
        contract_text = """
Article 1. First Article

Article 2. Second Article

Some content here.
"""
        fragmenter = ContractClauseFragmenter(name='test', min_clause_length=10)
        doc = Document(text=contract_text)
        result = fragmenter.process_docs([doc])

        # Should handle clauses even with minimal content
        self.assertGreaterEqual(len(result), 1)

    def test_special_characters_in_clauses(self):
        """Test handling of special characters in clause headers."""
        contract_text = """
Article 1. Definitions & Interpretations

Content with special characters.

Section 1.1 (a) Sub-section

Content.
"""
        fragmenter = ContractClauseFragmenter(name='test')
        doc = Document(text=contract_text)
        result = fragmenter.process_docs([doc])

        # Should handle special characters
        self.assertGreaterEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
