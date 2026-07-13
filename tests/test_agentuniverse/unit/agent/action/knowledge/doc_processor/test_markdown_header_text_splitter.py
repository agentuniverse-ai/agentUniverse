# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/13
# @FileName: test_markdown_header_text_splitter.py

"""Tests for the MarkdownHeaderTextSplitter doc processor."""

import os
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.\
    markdown_header_text_splitter import MarkdownHeaderTextSplitter
import agentuniverse.agent.action.knowledge.doc_processor.\
    markdown_header_text_splitter as _splitter_module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

# The shipped yaml lives next to the processor module.
_YAML_PATH = os.path.join(
    os.path.dirname(_splitter_module.__file__),
    "markdown_header_text_splitter.yaml")


class TestMarkdownHeaderSplit(unittest.TestCase):
    """Pure splitting logic."""

    def setUp(self) -> None:
        self.splitter = MarkdownHeaderTextSplitter()

    def _run(self, text: str):
        return self.splitter.process_docs([Document(text=text)])

    def test_splits_by_headers_with_hierarchy(self) -> None:
        out = self._run("# Title\nintro\n## Section\nbody\n")
        paths = [(d.metadata["header_path"], d.text) for d in out]
        self.assertEqual(paths, [
            ("Title", "intro"),
            ("Title > Section", "body"),
        ])

    def test_header_level_reset(self) -> None:
        out = self._run("# A\na\n## B\nb\n# C\nc\n")
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("A", "a"),
            ("A > B", "b"),
            ("C", "c"),
        ])

    def test_sibling_header_replaces_same_level(self) -> None:
        out = self._run("# A\n## B\nb\n## C\nc\n")
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("A > B", "b"),
            ("A > C", "c"),
        ])

    def test_preamble_kept_by_default(self) -> None:
        out = self._run("preamble line\n# A\nbody\n")
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("", "preamble line"),
            ("A", "body"),
        ])

    def test_preamble_dropped_when_configured(self) -> None:
        splitter = MarkdownHeaderTextSplitter(keep_preamble=False)
        out = splitter.process_docs([Document(text="preamble\n# A\nbody\n")])
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("A", "body"),
        ])

    def test_max_header_level_limits_splitting(self) -> None:
        # With max_header_level=1, '## Sub' is content, not a header.
        splitter = MarkdownHeaderTextSplitter(max_header_level=1)
        out = splitter.process_docs([Document(text="# A\na\n## Sub\nsub\n")])
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("A", "a\n## Sub\nsub"),
        ])

    def test_closed_atx_headers_recognized(self) -> None:
        out = self._run("## Title ##\nbody\n")
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("Title", "body"),
        ])

    def test_non_header_hash_lines_are_content(self) -> None:
        # No space after '#', or 7+ hashes → not an ATX header.
        out = self._run("#NoSpace\n####### seven hashes\n# Real\nbody\n")
        self.assertEqual([(d.metadata["header_path"], d.text) for d in out], [
            ("", "#NoSpace\n####### seven hashes"),
            ("Real", "body"),
        ])

    def test_empty_and_no_header_input(self) -> None:
        self.assertEqual(self.splitter.process_docs([Document(text="")]), [])
        # Content but no headers → a single preamble section.
        out = self._run("just plain text\nno headers here")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].metadata["header_path"], "")

    def test_existing_metadata_preserved(self) -> None:
        out = self.splitter.process_docs([
            Document(text="# A\nbody", metadata={"source": "readme.md"})])
        self.assertEqual(out[0].metadata["source"], "readme.md")
        self.assertEqual(out[0].metadata["header_path"], "A")

    def test_header_path_key_omitted_when_none(self) -> None:
        splitter = MarkdownHeaderTextSplitter(header_path_key=None)
        out = splitter.process_docs([Document(text="# A\nbody")])
        self.assertNotIn("header_path", out[0].metadata)
        # Only the original (empty) metadata remains.
        self.assertEqual(out[0].metadata, {})


class TestMarkdownHeaderSplitterRegistration(unittest.TestCase):
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
            "markdown_header_text_splitter")
        self.assertEqual(
            component_configer.metadata_class, "MarkdownHeaderTextSplitter")


if __name__ == '__main__':
    unittest.main()
