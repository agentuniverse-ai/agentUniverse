# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02 10:00
# @Author  : Yue Wang
# @FileName: test_recursive_character_text_splitter.py
"""Unit tests for the RecursiveCharacterTextSplitter doc processor."""

import pytest
from langchain.text_splitter import \
    RecursiveCharacterTextSplitter as LangchainRecursiveCharacterTextSplitter

from agentuniverse.agent.action.knowledge.doc_processor.\
    recursive_character_text_splitter import RecursiveCharacterTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestRecursiveCharacterTextSplitter:
    """Test pure recursive splitting behavior and class defaults."""

    @pytest.fixture
    def splitter(self):
        """Splitter with small chunks and no overlap."""
        return RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=0)

    @pytest.fixture
    def spaced_words(self):
        """Space-separated words longer than the fixture chunk size."""
        return "aaaaaa bbbbbb cccccc dddddd"

    def test_class_defaults(self):
        """Test the class-level default parameters."""
        splitter = RecursiveCharacterTextSplitter()
        assert splitter.chunk_size == 200
        assert splitter.chunk_overlap == 20
        assert splitter.separators == ["\n\n", "\n", " ", ""]
        lc_splitter = splitter.splitter
        assert isinstance(lc_splitter, LangchainRecursiveCharacterTextSplitter)
        assert lc_splitter._chunk_size == 200
        assert splitter.splitter is lc_splitter

    def test_empty_and_short_text(self, splitter):
        """Test splitting empty and short inputs."""
        assert splitter.splitter.split_text("") == []
        assert splitter.splitter.split_text("hi") == ["hi"]

    def test_words_never_cut_and_text_reassembled(self, splitter,
                                                  spaced_words):
        """Test words stay intact, chunks are bounded and lossless."""
        chunks = splitter.splitter.split_text(spaced_words)
        assert chunks == ["aaaaaa", "bbbbbb", "cccccc", "dddddd"]
        assert all(len(c) <= 10 for c in chunks)
        assert " ".join(chunks) == spaced_words

    def test_chunk_overlap_carries_tail(self):
        """Test overlapping chunks share the trailing characters."""
        text = "".join(chr(ord("a") + i) for i in range(20))
        splitter = RecursiveCharacterTextSplitter(chunk_size=5, chunk_overlap=2)
        chunks = splitter.splitter.split_text(text)
        assert chunks[0] == text[:5]
        assert len(chunks) == 6
        assert all(len(c) <= 5 for c in chunks)
        for prev, cur in zip(chunks, chunks[1:]):
            assert cur.startswith(prev[-2:])

    def test_separator_ordering_prefers_highest_priority(self):
        """Test the first matching separator in the list drives splitting."""
        paragraphs = [f"para{i}-" + "x" * 10 for i in range(6)]
        splitter = RecursiveCharacterTextSplitter(chunk_size=25, chunk_overlap=0)
        assert splitter.splitter.split_text(
            "\n\n".join(paragraphs)) == paragraphs
        lines = [f"line{i}-" + "x" * 16 for i in range(4)]
        splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=0)
        chunks = splitter.splitter.split_text("\n".join(lines))
        assert chunks == lines
        assert all(len(c) <= 30 for c in chunks)

    def test_process_docs_round_trip(self, splitter, spaced_words):
        """Test the Document-level processing pipeline."""
        docs = splitter.process_docs([Document(text=spaced_words, metadata={})])
        assert [d.text for d in docs] == ["aaaaaa", "bbbbbb", "cccccc", "dddddd"]
        assert splitter.process_docs([Document(text="", metadata={})]) == []
