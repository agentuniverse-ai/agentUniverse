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


class TestContractClauseFragmenterEnhancements(unittest.TestCase):
    """Tests for lettered/CJK markers, ALLCAPS boilerplate headings, char spans
    and the max_fragment_chars bound."""

    EN_CONTRACT = """
SERVICE AGREEMENT

This agreement is entered into by the parties below.

WHEREAS, the seller provides consulting services to businesses;

WHEREAS, the buyer desires to engage the seller for such services;

NOW, THEREFORE, in consideration of the mutual covenants below, the parties agree:

1. Services

The seller shall provide consulting services as described herein.

(a) Consulting services are performed remotely.

(b) Travel requires prior written approval of the buyer.

2. Term

This agreement runs for twelve months from the effective date.

IN WITNESS WHEREOF, the parties have executed this agreement.
"""

    ZH_CONTRACT = """
第一条 付款方式

买方应在收货后三十日内付款。

（一）逾期付款按月计息。

（二）争议金额应在十日内书面提出。

第二条 交货

货物应在五个工作日内发出。
"""

    def setUp(self):
        """Set up test fixtures."""
        self.fragmenter = ContractClauseFragmenter(
            name='test_fragmenter',
            preserve_hierarchy=True,
            extract_references=True,
            skip_on_error=True,
        )

    def _types(self, result):
        """Return the list of clause_type values of the fragments."""
        return [d.metadata['clause_type'] for d in result]

    def test_lettered_markers_nested_under_numbered_clause(self):
        """Test that (a)/(b) markers become lettered fragments under their numbered parent."""
        result = self.fragmenter.process_docs([Document(text=self.EN_CONTRACT)])

        types = self._types(result)
        self.assertIn('lettered', types)

        lettered = [d for d in result if d.metadata['clause_type'] == 'lettered']
        self.assertEqual({d.metadata['clause_id'] for d in lettered},
                         {'lettered_a', 'lettered_b'})

        # Lettered items nest below numbered sub-clauses ("1." -> level 2)
        for item in lettered:
            self.assertEqual(item.metadata['hierarchy_level'], 4)
            self.assertEqual(item.metadata['parent_clause'], 'clause_1')

        self.assertIn('clause_1', item.metadata['parent_clause'])
        self.assertIn('(a) Consulting', ''.join(d.text for d in lettered))

    def test_chinese_parenthesized_markers(self):
        """Test that （一）/（二） markers become lettered fragments under 第X条."""
        result = self.fragmenter.process_docs([Document(text=self.ZH_CONTRACT)])

        types = self._types(result)
        self.assertEqual(types.count('lettered'), 2)

        lettered = [d for d in result if d.metadata['clause_type'] == 'lettered']
        self.assertEqual({d.metadata['clause_id'] for d in lettered},
                         {'lettered_一', 'lettered_二'})
        for item in lettered:
            self.assertEqual(item.metadata['parent_clause'], 'article_一')

    def test_half_width_chinese_marker(self):
        """Test that half-width (一) markers are detected as well."""
        contract_text = """
第一条 付款方式

买方应在收货后三十日内付款。

(一) 逾期付款按月计息。
"""
        result = self.fragmenter.process_docs([Document(text=contract_text)])

        self.assertIn('lettered', self._types(result))

    def test_allcaps_boilerplate_default_drops_recitals_keeps_operative(self):
        """Test WHEREAS/NOW THEREFORE/IN WITNESS WHEREOF handling with defaults."""
        result = self.fragmenter.process_docs([Document(text=self.EN_CONTRACT)])

        types = self._types(result)
        # Recitals and the leading preamble are non-operative: dropped by default
        self.assertNotIn('recital', types)
        self.assertNotIn('preamble', types)
        for d in result:
            self.assertNotIn('SERVICE AGREEMENT', d.text)
            self.assertNotIn('WHEREAS', d.text)
        # The operative grant and the execution block are kept as fragments
        self.assertIn('operative', types)
        self.assertIn('execution', types)
        execution = next(d for d in result if d.metadata['clause_type'] == 'execution')
        self.assertIn('IN WITNESS WHEREOF', execution.text)

    def test_keep_preamble_retains_preamble_and_recitals(self):
        """Test that keep_preamble=True keeps the preamble and recital blocks."""
        fragmenter = ContractClauseFragmenter(name='test', keep_preamble=True)
        result = fragmenter.process_docs([Document(text=self.EN_CONTRACT)])

        types = self._types(result)
        self.assertIn('preamble', types)
        self.assertEqual(types.count('recital'), 2)

        preamble = next(d for d in result if d.metadata['clause_type'] == 'preamble')
        self.assertTrue(preamble.text.startswith('SERVICE AGREEMENT'))
        self.assertEqual(preamble.metadata['char_start'], 1)  # after the leading newline

        recital_ids = [d.metadata['clause_id'] for d in result
                       if d.metadata['clause_type'] == 'recital']
        self.assertEqual(recital_ids, ['recital_1', 'recital_2'])

    def test_recital_only_document_falls_back_to_single_fragment(self):
        """Test that a recitals-only page degrades to one unstructured fragment."""
        contract_text = """
WHEREAS, the seller provides consulting services;

WHEREAS, the buyer desires to engage the seller;
"""
        result = self.fragmenter.process_docs([Document(text=contract_text)])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata['clause_type'], 'unstructured')
        self.assertIn('WHEREAS', result[0].text)

    def test_char_span_invariant_english(self):
        """Test that char_start/char_end map exactly back to the fragment text."""
        source = self.EN_CONTRACT
        result = self.fragmenter.process_docs([Document(text=source)])

        self.assertGreater(len(result), 0)
        spans = []
        for d in result:
            m = d.metadata
            self.assertIn('char_start', m)
            self.assertIn('char_end', m)
            self.assertEqual(source[m['char_start']:m['char_end']], d.text)
            spans.append((m['char_start'], m['char_end']))

        # Fragments must not overlap
        spans.sort()
        for (_, prev_end), (next_start, _) in zip(spans, spans[1:]):
            self.assertGreaterEqual(next_start, prev_end)

    def test_char_span_invariant_chinese(self):
        """Test char span correctness for CJK texts."""
        source = self.ZH_CONTRACT
        result = self.fragmenter.process_docs([Document(text=source)])

        self.assertGreaterEqual(len(result), 4)
        for d in result:
            m = d.metadata
            self.assertEqual(source[m['char_start']:m['char_end']], d.text)

    def test_char_span_single_fragment_fallback(self):
        """Test char spans on the unstructured single-fragment fallback."""
        source = "This is just plain text without any clause structure."
        result = self.fragmenter.process_docs([Document(text=source)])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata['char_start'], 0)
        self.assertEqual(result[0].metadata['char_end'], len(source))

    def test_max_fragment_chars_splits_and_stamps_parts(self):
        """Test that over-long clauses split with part metadata and exact spans."""
        whole_result = self.fragmenter.process_docs([Document(text=self.EN_CONTRACT)])
        whole_clause = next(d.text for d in whole_result
                            if d.metadata['clause_id'] == 'clause_1')

        fragmenter = ContractClauseFragmenter(name='test', max_fragment_chars=60)
        result = fragmenter.process_docs([Document(text=self.EN_CONTRACT)])

        parts = [d for d in result if d.metadata['clause_id'] == 'clause_1']
        self.assertGreaterEqual(len(parts), 2)
        for d in parts:
            self.assertLessEqual(len(d.text), 60)
            self.assertIn('part_index', d.metadata)
            self.assertIn('part_count', d.metadata)

        # Complete, ordered part indices
        self.assertEqual([d.metadata['part_index'] for d in parts],
                         list(range(len(parts))))
        self.assertEqual({d.metadata['part_count'] for d in parts}, {len(parts)})

        # Exact spans per part, and the parts tile the clause without content loss
        source = self.EN_CONTRACT
        for d in parts:
            self.assertEqual(source[d.metadata['char_start']:d.metadata['char_end']],
                             d.text)
        joined = ''.join(d.text for d in parts)
        self.assertEqual(''.join(joined.split()), ''.join(whole_clause.split()))
        self.assertTrue(parts[0].text.startswith('1. Services'))

        # The run-on operative sentence (no internal sentence enders) exercises
        # the raw character fallback
        operative = [d for d in result if d.metadata['clause_id'] == 'operative_1']
        self.assertGreaterEqual(len(operative), 2)
        for d in operative:
            self.assertLessEqual(len(d.text), 60)

    def test_max_fragment_chars_disabled_by_default(self):
        """Test that no splitting happens and no part metadata exists by default."""
        result = self.fragmenter.process_docs([Document(text=self.EN_CONTRACT)])

        self.assertGreater(len(result), 0)
        for d in result:
            self.assertNotIn('part_index', d.metadata)
            self.assertNotIn('part_count', d.metadata)
        clause_ids = [d.metadata['clause_id'] for d in result]
        self.assertEqual(len(clause_ids), len(set(clause_ids)))

    def test_split_clause_parts_sentence_packing(self):
        """Test the pure span splitter: sentence packing with exact offsets."""
        from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter \
            import ClauseNode

        fragmenter = ContractClauseFragmenter(name='test', max_fragment_chars=5)
        node = ClauseNode(id='clause_1', text='A. BB. CCC. DDDD',
                          clause_type='subsection_level_0', hierarchy_level=2,
                          char_start=100, char_end=116)
        parts = fragmenter._split_clause_parts(node)

        self.assertEqual(parts, [
            ('A.', 100, 102),
            ('BB.', 103, 106),
            ('CCC.', 107, 111),
            ('DDDD', 112, 116),
        ])

    def test_split_clause_parts_runon_fallback(self):
        """Test the raw character fallback for sentences without punctuation."""
        from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter \
            import ClauseNode

        fragmenter = ContractClauseFragmenter(name='test', max_fragment_chars=4)
        node = ClauseNode(id='clause_1', text='abcdefghij',
                          clause_type='subsection_level_0', hierarchy_level=2,
                          char_start=0, char_end=10)
        parts = fragmenter._split_clause_parts(node)

        self.assertEqual(parts, [
            ('abcd', 0, 4),
            ('efgh', 4, 8),
            ('ij', 8, 10),
        ])

    def test_split_clause_parts_disabled(self):
        """Test that max_fragment_chars=0 returns the clause unsplit."""
        from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter \
            import ClauseNode

        fragmenter = ContractClauseFragmenter(name='test', max_fragment_chars=0)
        node = ClauseNode(id='clause_1', text='A. BB. CCC. DDDD',
                          clause_type='subsection_level_0', hierarchy_level=2,
                          char_start=7, char_end=23)
        parts = fragmenter._split_clause_parts(node)

        self.assertEqual(parts, [('A. BB. CCC. DDDD', 7, 23)])

    def test_inline_lettered_marker_is_not_a_boundary(self):
        """Test that '(a)' inside a Section header line does not split it."""
        contract_text = """
Section 1.1 (a) Sub-section

Content of the sub-section.
"""
        result = self.fragmenter.process_docs([Document(text=contract_text)])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata['clause_type'], 'section')
        self.assertNotIn('lettered', self._types(result))


class _StubConfiger:
    """Minimal duck-typed stand-in for ComponentConfiger in wiring tests."""

    def __init__(self, **overrides):
        self.name = 'stub_fragmenter'
        self.description = 'stub'
        for key, value in overrides.items():
            setattr(self, key, value)


class TestContractClauseFragmenterConfiguration(unittest.TestCase):
    """Tests for configuration defaults and configer wiring of the new keys."""

    def test_new_option_defaults(self):
        """Test the defaults of the new configuration keys."""
        fragmenter = ContractClauseFragmenter(name='test')

        self.assertFalse(fragmenter.keep_preamble)
        self.assertEqual(fragmenter.max_fragment_chars, 0)
        self.assertEqual(len(fragmenter.boilerplate_patterns), 3)
        self.assertTrue(any(r'\([a-zA-Z]\)' in p for p in fragmenter.clause_patterns))
        self.assertTrue(any('（' in p or '([' in p for p in fragmenter.clause_patterns))

    def test_configer_wiring_of_new_keys(self):
        """Test that _initialize_by_component_configer applies the new keys."""
        fragmenter = ContractClauseFragmenter(name='test')
        configer = _StubConfiger(
            keep_preamble=True,
            max_fragment_chars=128,
            boilerplate_patterns=[r'^RECITAL\b[,\s]*'],
        )

        fragmenter._initialize_by_component_configer(configer)

        self.assertEqual(fragmenter.name, 'stub_fragmenter')
        self.assertTrue(fragmenter.keep_preamble)
        self.assertEqual(fragmenter.max_fragment_chars, 128)
        self.assertEqual(fragmenter.boilerplate_patterns, [r'^RECITAL\b[,\s]*'])

    def test_configer_without_new_keys_keeps_defaults(self):
        """Test that a configer lacking the new keys leaves defaults intact."""
        fragmenter = ContractClauseFragmenter(name='test')
        fragmenter._initialize_by_component_configer(_StubConfiger())

        self.assertFalse(fragmenter.keep_preamble)
        self.assertEqual(fragmenter.max_fragment_chars, 0)
        self.assertEqual(len(fragmenter.boilerplate_patterns), 3)


if __name__ == '__main__':
    unittest.main()
