import unittest

from agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter import (
    HierarchicalRegexTextSplitter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


class TestHierarchicalSplitterContentPreservation(unittest.TestCase):
    def setUp(self):
        self.processor = HierarchicalRegexTextSplitter()
        self.processor.hierarchical_index = [
            {'reg_exp': r'^Chapter ', 'need_summary': False},
        ]

    def test_no_heading_keeps_original_document(self):
        original = Document(text='Plain text without a chapter', metadata={'source': 'file'})
        self.assertEqual(self.processor._process_docs([original]), [original])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(self.processor._process_docs([]), [])

    def test_preamble_before_first_heading_is_retained(self):
        source = Document(
            text='Introduction\nChapter One\nDetails',
            metadata={'source': 'file'},
        )
        docs = self.processor._process_docs([source])
        self.assertEqual(len(docs), 2)
        self.assertIn('Introduction', [doc.text.strip() for doc in docs])
        self.assertTrue(any('Details' in doc.text for doc in docs))
        preamble = next(doc for doc in docs if 'Introduction' in doc.text)
        self.assertEqual(preamble.metadata['source'], 'file')
        self.assertEqual(preamble.metadata['hierarchical_level'], -1)

    def test_merge_first_does_not_modify_input_on_repeated_calls(self):
        self.processor.merge_first = True
        originals = [Document(text='Chapter One\nFirst'), Document(text='Chapter Two\nSecond')]
        first = self.processor._process_docs(originals)
        second = self.processor._process_docs(originals)
        self.assertEqual([doc.text for doc in first], [doc.text for doc in second])
        self.assertEqual([doc.text for doc in originals],
                         ['Chapter One\nFirst', 'Chapter Two\nSecond'])

    def test_merge_first_preserves_first_document_fields(self):
        self.processor.merge_first = True
        first = Document(id='source-id', text='First', metadata={'source': 'file'},
                         embedding=[0.5], keywords={'key'})
        result = self.processor._process_docs([first, Document(text='Second')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, first.id)
        self.assertEqual(result[0].metadata, first.metadata)
        self.assertEqual(result[0].embedding, first.embedding)
        self.assertEqual(result[0].keywords, first.keywords)
        self.assertEqual(first.text, 'First')
