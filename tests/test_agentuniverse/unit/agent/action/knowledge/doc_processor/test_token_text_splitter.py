# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_token_text_splitter.py

"""Unit tests for TokenTextSplitter."""

import pytest
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.doc_processor.token_text_splitter import \
    TokenTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum


def make_doc(text: str) -> Document:
    """Create a document with an empty metadata dict."""
    return Document(text=text, metadata={})


class TestTokenTextSplitter:
    """Test the TokenTextSplitter doc processor."""

    @pytest.fixture
    def splitter(self):
        return TokenTextSplitter()

    def test_default_attributes(self, splitter):
        assert splitter.chunk_size == 200
        assert splitter.chunk_overlap == 20
        assert splitter.encoding_name == "gpt2"
        assert splitter.model_name is None
        assert splitter.component_type == ComponentEnum.DOC_PROCESSOR

    def test_split_long_text_into_multiple_chunks(self, splitter):
        # repeated single words keep a deterministic one-token-per-word text
        text = " ".join(["word"] * 1000)
        chunks = splitter.process_docs([make_doc(text)])
        assert len(chunks) > 1
        assert all(chunk.text for chunk in chunks)
        # each word costs at least one token, so every chunk stays within size
        assert all(len(chunk.text.split()) <= splitter.chunk_size
                   for chunk in chunks)
        covered = set()
        for chunk in chunks:
            covered.update(chunk.text.split())
        assert covered == {"word"}

    def test_short_text_stays_in_single_chunk(self, splitter):
        chunks = splitter.process_docs([make_doc("hello world")])
        assert len(chunks) == 1
        assert chunks[0].text == "hello world"

    def test_empty_text_yields_no_chunks(self, splitter):
        assert splitter.process_docs([make_doc("")]) == []

    def test_multiple_documents_split_independently(self, splitter):
        first = " ".join(f"alpha{i}" for i in range(500))
        second = " ".join(f"beta{i}" for i in range(500))
        chunks = splitter.process_docs([make_doc(first), make_doc(second)])
        assert len(chunks) > 2
        joined = " ".join(chunk.text for chunk in chunks)
        assert "alpha0" in joined and "beta0" in joined

    def test_langchain_splitter_is_lazily_cached(self, splitter):
        assert splitter.splitter is splitter.splitter

    def test_initialize_by_component_configer_updates_params(self):
        splitter = TokenTextSplitter()
        configer = SimpleNamespace(
            name="token_split", description="desc",
            chunk_size=30, chunk_overlap=5,
            encoding_name="gpt2", model_name=None)
        splitter.initialize_by_component_configer(configer)
        assert splitter.name == "token_split"
        assert splitter.description == "desc"
        assert splitter.chunk_size == 30
        assert splitter.chunk_overlap == 5
        chunks = splitter.process_docs(
            [make_doc(" ".join(["token"] * 300))])
        assert len(chunks) >= 2
        assert all(len(chunk.text.split()) <= 30 for chunk in chunks)
