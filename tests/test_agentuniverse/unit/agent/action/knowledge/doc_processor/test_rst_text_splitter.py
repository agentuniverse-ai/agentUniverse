# !/usr/bin/env python3

# @Time    : 2026/10/06
# @FileName: test_rst_text_splitter.py

"""Tests for the RstTextSplitter doc processor."""

import os
import unittest

import agentuniverse.agent.action.knowledge.doc_processor.\
    rst_text_splitter as _splitter_module
from agentuniverse.agent.action.knowledge.doc_processor.\
    rst_text_splitter import RstTextSplitter

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# The shipped yaml lives next to the processor module.
_YAML_PATH = os.path.join(
    os.path.dirname(_splitter_module.__file__),
    "rst_text_splitter.yaml")


class TestRstSplit(unittest.TestCase):
    """Pure splitting logic."""

    def setUp(self) -> None:
        self.splitter = RstTextSplitter()

    def _run(self, text: str):
        return self.splitter.process_docs([Document(text=text)])

    def _paths(self, text: str):
        return [(d.metadata["section_path"], d.text) for d in self._run(text)]

    def test_splits_by_underline_headers_with_hierarchy(self) -> None:
        rst = "Title\n=====\n\nintro\n\nSection\n-------\n\nbody\n"
        self.assertEqual(self._paths(rst), [
            ("Title", "intro"),
            ("Title > Section", "body"),
        ])

    def test_overline_and_underline_style(self) -> None:
        rst = ("+++++++\nTitle A\n+++++++\n\nbody a\n\n"
               "Title B\n+++++++\n\nbody b\n")
        self.assertEqual(self._paths(rst), [
            ("Title A", "body a"),
            ("Title B", "body b"),
        ])

    def test_adornment_char_reuse_returns_to_its_level(self) -> None:
        # First char seen ('=') is level 1, second new char ('-') is level 2;
        # reusing '=' after '-' returns to level 1, as docutils assigns.
        rst = ("A\n=\n\na\n\nB\n-\n\nb\n\nC\n=\n\nc\n\nD\n-\n\nd\n")
        self.assertEqual(self._paths(rst), [
            ("A", "a"),
            ("A > B", "b"),
            ("C", "c"),
            ("C > D", "d"),
        ])

    def test_sibling_section_replaces_same_level(self) -> None:
        rst = "A\n=\n\nB\n-\n\nb1\n\nC\n-\n\nc1\n"
        self.assertEqual(self._paths(rst), [
            ("A > B", "b1"),
            ("A > C", "c1"),
        ])

    def test_max_depth_limits_splitting(self) -> None:
        # With max_depth=1 the '---' title is ordinary content.
        splitter = RstTextSplitter(max_depth=1)
        out = splitter.process_docs([
            Document(text="A\n=\n\na\n\nB\n-\n\nb body\n")])
        self.assertEqual([(d.metadata["section_path"], d.text) for d in out], [
            ("A", "a\n\nB\n-\n\nb body"),
        ])

    def test_preamble_kept_by_default(self) -> None:
        out = self._run("preamble line\n\nA\n=\n\nbody\n")
        self.assertEqual(self._paths("preamble line\n\nA\n=\n\nbody\n"), [
            ("", "preamble line"),
            ("A", "body"),
        ])
        self.assertEqual(out[0].metadata["section_path"], "")

    def test_preamble_dropped_when_configured(self) -> None:
        splitter = RstTextSplitter(keep_preamble=False)
        out = splitter.process_docs([
            Document(text="preamble\n\nA\n=\n\nbody\n")])
        self.assertEqual([(d.metadata["section_path"], d.text) for d in out], [
            ("A", "body"),
        ])

    def test_title_requires_preceding_blank_line(self) -> None:
        # A paragraph directly followed by a dash run is not a title, so an
        # e-mail signature separator never splits a paragraph.
        rst = "plain text\n--\nmore text\n"
        out = self._run(rst)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].metadata["section_path"], "")
        self.assertEqual(out[0].text, "plain text\n--\nmore text")

    def test_short_underline_is_not_a_title(self) -> None:
        # docutils requires the adornment to be at least as long as the
        # title; a short run stays content.
        rst = "A very long title\n==\ncontent\n"
        out = self._run(rst)
        self.assertEqual(len(out), 1)
        self.assertIn("A very long title", out[0].text)
        self.assertIn("==", out[0].text)

    def test_transition_line_is_content(self) -> None:
        rst = "A\n=\nbefore\n\n-----\n\nafter\n"
        out = self._run(rst)
        self.assertEqual([(d.metadata["section_path"], d.text) for d in out], [
            ("A", "before\n\n-----\n\nafter"),
        ])

    def test_literal_block_titles_are_content(self) -> None:
        rst = ("A\n=\nintro\n\nExample::\n\n    Title\n    -----\n    code\n")
        out = self._run(rst)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].metadata["section_path"], "A")
        self.assertIn("Title\n    -----", out[0].text)

    def test_directive_and_comment_blocks_are_content(self) -> None:
        rst = ("A\n=\nintro\n\n.. note:: a note\n\n   Title\n   -----\n   body\n")
        out = self._run(rst)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].metadata["section_path"], "A")
        self.assertIn(".. note::", out[0].text)
        self.assertIn("Title\n   -----", out[0].text)

    def test_header_after_closed_literal_block(self) -> None:
        rst = ("A\n=\n\nExample::\n\n    code\n\nB\n-\nbody\n")
        self.assertEqual(self._paths(rst), [
            ("A", "Example::\n\n    code"),
            ("A > B", "body"),
        ])

    def test_empty_and_no_title_input(self) -> None:
        self.assertEqual(self.splitter.process_docs([Document(text="")]), [])
        out = self._run("just plain text\nno titles here")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].metadata["section_path"], "")

    def test_multiple_documents_and_metadata_preserved(self) -> None:
        out = self.splitter.process_docs([
            Document(text="A\n=\nbody", metadata={"source": "index.rst"}),
            Document(text="X\n=\nbody2", metadata={"source": "other.rst"}),
        ])
        self.assertEqual([d.metadata["source"] for d in out],
                         ["index.rst", "other.rst"])
        self.assertEqual([d.metadata["section_path"] for d in out],
                         ["A", "X"])

    def test_section_path_key_omitted_when_none(self) -> None:
        splitter = RstTextSplitter(section_path_key=None)
        out = splitter.process_docs([Document(text="A\n=\nbody")])
        self.assertNotIn("section_path", out[0].metadata)
        # Only the original (empty) metadata remains.
        self.assertEqual(out[0].metadata, {})


class TestRstSplitterRegistration(unittest.TestCase):
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
            "rst_text_splitter")
        self.assertEqual(
            component_configer.metadata_class, "RstTextSplitter")

    def test_yaml_custom_fields_load_into_processor(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        splitter = RstTextSplitter()
        splitter._initialize_by_component_configer(component_configer)
        self.assertEqual(splitter.section_path_key, "section_path")
        self.assertIsNone(splitter.max_depth)
        self.assertTrue(splitter.keep_preamble)


if __name__ == '__main__':
    unittest.main()
