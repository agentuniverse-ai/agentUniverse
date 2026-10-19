import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.store.document import Document


class TestExactDedupHashIndex(unittest.TestCase):
    def test_keep_best_hashes_each_document_once(self):
        processor = SemanticDeduplicator(use_embeddings=False, merge_strategy='keep_best')
        docs = [Document(text=f'unique_{i}') for i in range(39)]
        docs += [Document(text='same', metadata={'rank': i}) for i in range(41)]
        calls = []
        original = SemanticDeduplicator._compute_hash
        def count_hash(self, text):
            calls.append(text)
            return original(self, text)
        with patch.object(SemanticDeduplicator, '_compute_hash', count_hash):
            unique, grouped = processor._remove_exact_duplicates(docs)
        self.assertEqual(len(unique), 40)
        self.assertEqual(unique[-1].metadata['rank'], 0)
        self.assertEqual(len(grouped[processor._compute_hash('same')]), 41)
        self.assertEqual(len(calls), len(docs))

    def test_merge_hashes_each_document_once(self):
        processor = SemanticDeduplicator(use_embeddings=False, merge_strategy='merge')
        docs = [Document(text=f'unique_{i}') for i in range(39)]
        docs += [Document(text='same', metadata={f'field_{i}': i}) for i in range(41)]
        calls = []
        original = SemanticDeduplicator._compute_hash
        def count_hash(self, text):
            calls.append(text)
            return original(self, text)
        with patch.object(SemanticDeduplicator, '_compute_hash', count_hash):
            unique, _ = processor._remove_exact_duplicates(docs)
        self.assertEqual(len(unique), 40)
        self.assertEqual(unique[-1].metadata['field_40'], 40)
        self.assertEqual(len(calls), len(docs))
