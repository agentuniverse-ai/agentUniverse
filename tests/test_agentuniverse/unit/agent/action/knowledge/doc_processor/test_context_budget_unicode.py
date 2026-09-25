"""Unicode and token-budget regressions using real, offline BPE vocabularies."""

import unittest
from unittest.mock import patch

import tiktoken

from agentuniverse.agent.action.knowledge.doc_processor import context_budget_compressor as cbc
from agentuniverse.agent.action.knowledge.store.document import Document


class ContextBudgetUnicodeTest(unittest.TestCase):
    def setUp(self):
        ranks = {bytes([i]): i for i in range(256)}
        self.byte_encoder = tiktoken.Encoding(
            name="unicode-byte-test", pat_str=r"(?s).+", mergeable_ranks=ranks, special_tokens={}
        )
        # One token contains a space, Cyrillic A, and half of Cyrillic BE.
        # Removing the partial character makes that prefix require three tokens.
        # This models a real cl100k_base boundary where re-encoding expands.
        ranks = {**ranks, b"\xb0\xd0": 256, b"\xd0\xb0\xd0": 257, b" \xd0\xb0\xd0": 258}
        self.merged_encoder = tiktoken.Encoding(
            name="unicode-merged-test", pat_str=r"(?s).+", mergeable_ranks=ranks, special_tokens={}
        )
        self.cache = patch.dict(
            cbc._TIKTOKEN_ENCODERS,
            {
                self.byte_encoder.name: self.byte_encoder,
                self.merged_encoder.name: self.merged_encoder,
            },
        )
        self.cache.start()
        self.addCleanup(self.cache.stop)

    def processor(self, budget, encoder=None, **kwargs):
        return cbc.ContextBudgetCompressor(
            counter="tiktoken", budget=budget, tiktoken_encoding=(encoder or self.byte_encoder).name, **kwargs
        )

    def test_incomplete_chinese_character_is_not_replaced(self):
        result = self.processor(4).process_docs([Document(text="中文")])
        self.assertEqual([doc.text for doc in result], ["中"])

    def test_no_complete_character_fits(self):
        self.assertEqual(self.processor(1).process_docs([Document(text="🙂abc")]), [])

    def test_remaining_budget_after_an_earlier_document(self):
        first = Document(text="ok")
        result = self.processor(7).process_docs([first, Document(text="🙂中文")])
        self.assertEqual([doc.text for doc in result], ["ok", "🙂"])
        self.assertEqual(sum(len(self.byte_encoder.encode(doc.text)) for doc in result), 6)

    def test_reencoding_prefix_cannot_exceed_budget(self):
        text = " \u0430\u0431"
        tokens = self.merged_encoder.encode(text)
        self.assertEqual(len(tokens), 2)
        naive_prefix = self.merged_encoder.decode(tokens[:1], errors="ignore")
        self.assertEqual(naive_prefix, " \u0430")
        self.assertEqual(len(self.merged_encoder.encode(naive_prefix)), 3)
        result = self.processor(1, self.merged_encoder).process_docs([Document(text=text)])
        self.assertEqual([doc.text for doc in result], [" "])
        self.assertEqual(len(self.merged_encoder.encode(result[0].text)), 1)

    def test_literal_replacement_character_is_preserved(self):
        result = self.processor(3).process_docs([Document(text="\ufffdmore")])
        self.assertEqual([doc.text for doc in result], ["\ufffd"])

    def test_all_boundaries_preserve_prefix_and_budget(self):
        for text in ["中文🙂abc", "éclair", "a\u0301b", "👨‍👩‍👧‍👦", "plain ASCII", "\ufffdtext"]:
            for budget in range(1, len(self.byte_encoder.encode(text))):
                with self.subTest(text=text, budget=budget):
                    result = self.processor(budget).process_docs([Document(text=text)])
                    prefix = "".join(doc.text for doc in result)
                    self.assertTrue(text.startswith(prefix), repr(prefix))
                    self.assertLessEqual(len(self.byte_encoder.encode(prefix)), budget)

    def test_truncation_keeps_identity_and_does_not_mutate_input(self):
        original = Document(id="source", text="中文", metadata={"source": "notes"})
        result = self.processor(4).process_docs([original])
        self.assertEqual(result[0].id, "source")
        self.assertEqual(result[0].metadata, {"source": "notes", "truncated": True})
        self.assertEqual(original.text, "中文")
        self.assertEqual(original.metadata, {"source": "notes"})

    def test_whole_documents_and_disabled_truncation(self):
        original = Document(text="中文")
        self.assertEqual(self.processor(6).process_docs([original]), [original])
        self.assertEqual(self.processor(4, truncate=False).process_docs([original]), [])


if __name__ == "__main__":
    unittest.main()
