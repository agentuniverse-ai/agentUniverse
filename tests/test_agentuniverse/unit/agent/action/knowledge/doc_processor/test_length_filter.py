# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/13
# @FileName: test_length_filter.py

"""Tests for the LengthFilter doc processor."""

import os
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.length_filter import \
    LengthFilter
import agentuniverse.agent.action.knowledge.doc_processor.length_filter as \
    _filter_module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(_filter_module.__file__),
                          "length_filter.yaml")


def _texts(docs):
    return [d.text for d in docs]


class TestLengthFilter(unittest.TestCase):
    """Filtering logic."""

    def test_default_drops_empty_and_whitespace_only(self) -> None:
        # Default min_length=1 removes empty / whitespace-only documents.
        docs = [Document(text=""), Document(text="   \n\t  "),
                Document(text="keep me")]
        out = LengthFilter().process_docs(docs)
        self.assertEqual(_texts(out), ["keep me"])

    def test_min_length_threshold(self) -> None:
        f = LengthFilter(min_length=5)
        docs = [Document(text="abc"), Document(text="abcdef"),
                Document(text="exactly five")]
        out = f.process_docs(docs)
        self.assertEqual(_texts(out), ["abcdef", "exactly five"])

    def test_max_length_threshold(self) -> None:
        f = LengthFilter(min_length=None, max_length=4)
        docs = [Document(text="ab"), Document(text="abcde"),
                Document(text="abcd")]
        out = f.process_docs(docs)
        self.assertEqual(_texts(out), ["ab", "abcd"])

    def test_combined_min_and_max_bounds(self) -> None:
        f = LengthFilter(min_length=2, max_length=4)
        docs = [Document(text="a"), Document(text="ab"), Document(text="abcd"),
                Document(text="abcde")]
        out = f.process_docs(docs)
        self.assertEqual(_texts(out), ["ab", "abcd"])

    def test_token_unit(self) -> None:
        # Whitespace-separated token count, not characters.
        f = LengthFilter(length_unit="token", min_length=2)
        docs = [Document(text="oneword"), Document(text="two words"),
                Document(text="a b c")]
        out = f.process_docs(docs)
        self.assertEqual(_texts(out), ["two words", "a b c"])

    def test_trim_false_counts_raw_whitespace(self) -> None:
        # Without trim, "   " has length 3 and survives min_length=1.
        f = LengthFilter(trim=False, min_length=1)
        out = f.process_docs([Document(text="   "), Document(text="")])
        self.assertEqual(_texts(out), ["   "])

    def test_preserves_ids_and_metadata(self) -> None:
        # A filter passes documents through untouched.
        doc = Document(text="payload", metadata={"source": "x"})
        out = LengthFilter().process_docs([doc])
        self.assertIs(out[0], doc)
        self.assertEqual(out[0].metadata["source"], "x")

    def test_empty_input(self) -> None:
        self.assertEqual(LengthFilter().process_docs([]), [])

    def test_none_min_and_max_keeps_everything(self) -> None:
        f = LengthFilter(min_length=None, max_length=None)
        docs = [Document(text=""), Document(text="anything")]
        self.assertEqual(_texts(f.process_docs(docs)), ["", "anything"])


class TestLengthFilterRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.DOC_PROCESSOR.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor.length_filter")
        self.assertEqual(component_configer.metadata_class, "LengthFilter")


if __name__ == '__main__':
    unittest.main()
