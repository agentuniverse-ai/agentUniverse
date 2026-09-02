# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02 10:00
# @Author  : Yue Wang
# @FileName: test_character_text_splitter.py
"""Unit tests for the CharacterTextSplitter doc processor."""

import pytest
from langchain.text_splitter import \
    CharacterTextSplitter as LangchainCharacterTextSplitter

from agentuniverse.agent.action.knowledge.doc_processor.character_text_splitter \
    import CharacterTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestCharacterTextSplitter:
    """Test pure character-splitting behavior and class defaults."""

    @pytest.fixture
    def splitter(self):
        """Splitter configured with explicit small chunk parameters."""
        return CharacterTextSplitter(chunk_size=20, chunk_overlap=4,
                                     separator="\n\n")

    @pytest.fixture
    def paragraphs(self):
        """Six paragraphs of 16 characters each."""
        return [f"para{i}-" + "x" * 10 for i in range(6)]

    def test_class_defaults(self):
        """Test the class-level default parameters."""
        splitter = CharacterTextSplitter()
        assert splitter.chunk_size == 200
        assert splitter.chunk_overlap == 20
        assert splitter.separator == "/n/n"

    def test_splitter_is_lazy_cached_langchain_instance(self, splitter):
        """Test the underlying LangChain splitter is built once and cached."""
        lc_splitter = splitter.splitter
        assert isinstance(lc_splitter, LangchainCharacterTextSplitter)
        assert splitter.splitter is lc_splitter
        assert lc_splitter._chunk_size == 20
        assert lc_splitter._chunk_overlap == 4
        assert lc_splitter._separator == "\n\n"

    def test_split_multiple_paragraphs(self, splitter, paragraphs):
        """Test paragraphs are emitted as separate chunks."""
        chunks = splitter.splitter.split_text("\n\n".join(paragraphs))
        assert chunks == paragraphs
        assert len(chunks) == 6
        assert all(len(c) <= 20 for c in chunks)

    def test_configured_separator_drives_splitting(self):
        """Test the default and a custom separator end to end."""
        text = "\n\n".join(["x" * 120] * 3)
        default = CharacterTextSplitter()
        assert default.splitter.split_text(text) == [text]
        custom = CharacterTextSplitter(chunk_size=100, separator="\n\n")
        assert custom.splitter.split_text(text) == ["x" * 120] * 3

    def test_empty_and_short_text(self, splitter):
        """Test splitting empty and short inputs."""
        assert splitter.splitter.split_text("") == []
        assert splitter.splitter.split_text("tiny") == ["tiny"]

    def test_process_docs_round_trip(self, splitter, paragraphs):
        """Test the Document-level processing pipeline."""
        text = "\n\n".join(paragraphs)
        docs = splitter.process_docs([Document(text=text, metadata={})])
        assert [d.text for d in docs] == paragraphs
        assert splitter.process_docs(
            [Document(text="", metadata={})]) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
