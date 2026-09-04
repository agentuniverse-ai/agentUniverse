# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_document.py

"""Unit tests for the Document knowledge model."""

from langchain_core.documents.base import Document as LCDocument

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document


class TestDocument:
    """Test Document construction, ids and langchain conversions."""

    def test_default_values(self):
        doc = Document()
        assert doc.text == ""
        assert doc.metadata is None
        assert doc.embedding == []
        assert doc.keywords == set()
        assert doc.id  # id is auto-generated

    def test_deterministic_id_from_text(self):
        assert Document(text="hello").id == Document(text="hello").id
        assert Document(text="hello").id != Document(text="world").id

    def test_explicit_id_is_preserved(self):
        assert Document(id="custom-id", text="hello").id == "custom-id"

    def test_as_langchain(self):
        doc = Document(text="payload", metadata={"src": "test"})
        lc = doc.as_langchain()
        assert isinstance(lc, LCDocument)
        assert lc.page_content == "payload"
        assert lc.metadata == {"src": "test"}

    def test_as_langchain_with_none_metadata(self):
        lc = Document(text="payload").as_langchain()
        assert lc.page_content == "payload"
        assert lc.metadata == {}

    def test_as_langchain_list_roundtrip(self):
        docs = [Document(text="one", metadata={"a": 1}),
                Document(text="two", metadata={})]
        lc_list = Document.as_langchain_list(docs)
        assert len(lc_list) == 2
        assert [d.page_content for d in lc_list] == ["one", "two"]
        assert Document.as_langchain_list(None) == []

    def test_from_langchain_list_roundtrip(self):
        lc_list = [LCDocument(page_content="one", metadata={"a": 1}),
                   LCDocument(page_content="two")]
        docs = Document.from_langchain_list(lc_list)
        assert len(docs) == 2
        assert [d.text for d in docs] == ["one", "two"]
        assert docs[0].metadata == {"a": 1}
        assert Document.from_langchain_list(None) == []
