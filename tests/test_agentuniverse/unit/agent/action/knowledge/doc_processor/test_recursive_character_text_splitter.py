# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/03
# @FileName: test_recursive_character_text_splitter.py

"""Tests for the RecursiveCharacterTextSplitter doc processor."""

import os
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.\
    recursive_character_text_splitter import RecursiveCharacterTextSplitter
import agentuniverse.agent.action.knowledge.doc_processor.\
    recursive_character_text_splitter as _splitter_module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

# The shipped yaml lives next to the processor module.
_YAML_PATH = os.path.join(
    os.path.dirname(_splitter_module.__file__),
    "recursive_character_text_splitter.yaml")


class TestRecursiveCharacterTextSplitter(unittest.TestCase):
    """Pure, deterministic splitting logic."""

    def setUp(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter()

    def _run(self, text: str):
        return self.splitter.process_docs([Document(text=text)])

    def test_short_text_is_not_split(self) -> None:
        out = self._run("hello world")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "hello world")

    def test_long_text_is_split_into_chunks(self) -> None:
        out = self._run("word " * 300)
        self.assertGreater(len(out), 1)
        for doc in out:
            self.assertLessEqual(len(doc.text), self.splitter.chunk_size)

    def test_chunk_size_config_is_respected(self) -> None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=50, chunk_overlap=5)
        out = splitter.process_docs([Document(text="a" * 300)])
        self.assertGreater(len(out), 1)
        for doc in out:
            self.assertLessEqual(len(doc.text), 50)

    def test_chunk_overlap_produces_repeated_tail(self) -> None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=50, chunk_overlap=5)
        out = splitter.process_docs([Document(text="x" * 300)])
        # Every non-first chunk starts with the tail of the previous chunk.
        for prev, cur in zip(out, out[1:]):
            self.assertEqual(prev.text[-5:], cur.text[:5])

    def test_empty_text_returns_no_documents(self) -> None:
        self.assertEqual(self._run(""), [])

    def test_empty_input_list_returns_empty(self) -> None:
        self.assertEqual(self.splitter.process_docs([]), [])

    def test_metadata_is_preserved_on_chunks(self) -> None:
        out = self.splitter.process_docs([
            Document(text="a" * 300, metadata={"source": "readme.md"})])
        for doc in out:
            self.assertEqual(doc.metadata["source"], "readme.md")

    def test_splitter_is_lazily_cached(self) -> None:
        first = self.splitter.splitter
        second = self.splitter.splitter
        self.assertIs(first, second)


class TestRecursiveCharacterTextSplitterRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.DOC_PROCESSOR.value,
        )

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor."
            "recursive_character_text_splitter")
        self.assertEqual(
            component_configer.metadata_class, "RecursiveCharacterTextSplitter")


if __name__ == '__main__':
    unittest.main()
