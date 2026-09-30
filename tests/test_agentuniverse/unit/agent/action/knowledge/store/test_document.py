# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:55
# @Author  : yuewang
# @FileName: test_document.py
"""Unit tests for the knowledge store Document class."""

import uuid

from langchain_core.documents.base import Document as LCDocument

from agentuniverse.agent.action.knowledge.store.document import Document


class TestDocument:
    """Test Document id generation and conversion."""

    def test_id_generated_deterministically_from_text(self):
        d1 = Document(text='hello')
        d2 = Document(text='hello')
        assert d1.id == d2.id
        assert d1.id == str(uuid.uuid5(uuid.NAMESPACE_URL, 'hello'))
        assert Document(text='other').id != d1.id

    def test_explicit_id_preserved(self):
        assert Document(text='x', id='my-id').id == 'my-id'

    def test_defaults(self):
        d = Document(text='t')
        assert d.text == 't'
        assert d.metadata is None
        assert d.embedding == []
        assert d.keywords == set()

    def test_as_langchain(self):
        d = Document(text='t', metadata={'k': 'v'})
        lc = d.as_langchain()
        assert isinstance(lc, LCDocument)
        assert lc.page_content == 't'
        assert lc.metadata == {'k': 'v'}

    def test_as_langchain_list_none_and_items(self):
        assert Document.as_langchain_list(None) == []
        docs = [Document(text='a', metadata={'i': 0}), Document(text='b', metadata={'i': 1})]
        lc_list = Document.as_langchain_list(docs)
        assert [d.page_content for d in lc_list] == ['a', 'b']
        assert [d.metadata for d in lc_list] == [{'i': 0}, {'i': 1}]

    def test_from_langchain_list_roundtrip(self):
        assert Document.from_langchain_list(None) == []
        lc = [LCDocument(page_content='p1', metadata={'m': 1})]
        docs = Document.from_langchain_list(lc)
        assert len(docs) == 1
        assert docs[0].text == 'p1'
        assert docs[0].metadata == {'m': 1}
