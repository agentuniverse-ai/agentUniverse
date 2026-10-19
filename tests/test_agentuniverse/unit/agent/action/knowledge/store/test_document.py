# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/03
# @FileName: test_document.py

"""Tests for the Document data model and its LangChain conversion helpers."""

import unittest

from agentuniverse.agent.action.knowledge.store.document import Document


class TestDocumentConversion(unittest.TestCase):
    """as_langchain / as_langchain_list conversion."""

    def test_as_langchain_defaults_none_metadata_to_empty_dict(self) -> None:
        doc = Document(text="hello")
        lc_doc = doc.as_langchain()
        self.assertEqual(lc_doc.page_content, "hello")
        self.assertEqual(lc_doc.metadata, {})

    def test_as_langchain_preserves_metadata(self) -> None:
        doc = Document(text="hello", metadata={"source": "a.md"})
        self.assertEqual(doc.as_langchain().metadata, {"source": "a.md"})

    def test_as_langchain_list_defaults_none_metadata_to_empty_dict(self) -> None:
        # Regression: a Document without metadata must not crash the
        # list conversion (previously raised a pydantic ValidationError).
        docs = [Document(text="a"), Document(text="b")]
        lc_docs = Document.as_langchain_list(docs)
        self.assertEqual([d.page_content for d in lc_docs], ["a", "b"])
        self.assertEqual([d.metadata for d in lc_docs], [{}, {}])

    def test_as_langchain_list_preserves_metadata(self) -> None:
        docs = [Document(text="a", metadata={"source": "a.md"}),
                Document(text="b", metadata={"source": "b.md"})]
        lc_docs = Document.as_langchain_list(docs)
        self.assertEqual([d.metadata["source"] for d in lc_docs],
                         ["a.md", "b.md"])

    def test_as_langchain_list_handles_none_and_empty_input(self) -> None:
        self.assertEqual(Document.as_langchain_list(None), [])
        self.assertEqual(Document.as_langchain_list([]), [])

    def test_from_langchain_list_round_trip(self) -> None:
        lc_docs = Document.as_langchain_list(
            [Document(text="a", metadata={"k": "v"})])
        docs = Document.from_langchain_list(lc_docs)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "a")
        self.assertEqual(docs[0].metadata, {"k": "v"})

    def test_from_langchain_list_handles_none(self) -> None:
        self.assertEqual(Document.from_langchain_list(None), [])


class TestDocumentModel(unittest.TestCase):
    """Basic model behavior."""

    def test_id_is_generated_deterministically_from_text(self) -> None:
        a = Document(text="same text")
        b = Document(text="same text")
        self.assertEqual(a.id, b.id)

    def test_default_fields(self) -> None:
        doc = Document(text="x")
        self.assertEqual(doc.metadata, None)
        self.assertEqual(doc.embedding, [])
        self.assertEqual(doc.keywords, set())


if __name__ == '__main__':
    unittest.main()
