#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for XmlSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.xml_splitter \
    import XmlSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestXmlSplitter(unittest.TestCase):

    def _split(self, xml_text, **kwargs):
        proc = XmlSplitter(**kwargs)
        return proc.process_docs([Document(text=xml_text)], None)

    def _paths(self, docs):
        return {d.metadata["xml_path"] for d in docs}

    # ------------------------------------------------------------------ #
    # basic splitting
    # ------------------------------------------------------------------ #
    def test_flat_elements(self):
        docs = self._split("<root><a>hello</a><b>world</b></root>")
        paths = self._paths(docs)
        self.assertIn("root > a", paths)
        self.assertIn("root > b", paths)
        texts = " ".join(d.text for d in docs)
        self.assertIn("hello", texts)
        self.assertIn("world", texts)

    def test_nested_elements(self):
        docs = self._split("<root><a><b>deep</b></a></root>")
        paths = self._paths(docs)
        self.assertIn("root > a > b", paths)

    def test_repeated_elements(self):
        docs = self._split(
            "<items><item>one</item><item>two</item></items>")
        paths = self._paths(docs)
        self.assertIn("items > item", paths)
        texts = {d.text for d in docs if d.metadata["xml_path"] == "items > item"}
        self.assertEqual(texts, {"one", "two"})

    # ------------------------------------------------------------------ #
    # max_depth
    # ------------------------------------------------------------------ #
    def test_max_depth_serialises_subtree(self):
        # max_depth=2 -> at depth 2, <b>'s subtree is serialised as XML text.
        docs = self._split("<root><a><b>deep</b></a></root>", max_depth=2)
        self.assertTrue(len(docs) >= 1)
        joined = " ".join(d.text for d in docs)
        self.assertIn("deep", joined)

    def test_max_depth_one_yields_root(self):
        docs = self._split("<root><a>x</a><b>y</b></root>", max_depth=1)
        # Only the root chunk, serialised as XML.
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["xml_path"], "root")
        self.assertIn("x", docs[0].text)
        self.assertIn("y", docs[0].text)

    # ------------------------------------------------------------------ #
    # attributes
    # ------------------------------------------------------------------ #
    def test_include_attributes_in_text(self):
        docs = self._split('<item id="42">content</item>',
                           include_attributes=True)
        self.assertTrue(any("id=42" in d.text for d in docs))

    def test_include_attributes_off_by_default(self):
        docs = self._split('<item id="42">content</item>')
        self.assertTrue(all("id=42" not in d.text for d in docs))

    # ------------------------------------------------------------------ #
    # drop_empty / edge cases
    # ------------------------------------------------------------------ #
    def test_drop_empty_skips_textless_elements(self):
        docs = self._split("<root><a></a><b>real</b></root>", drop_empty=True)
        texts = [d.text for d in docs if d.metadata["xml_path"] == "root > a"]
        self.assertEqual(texts, [])

    def test_drop_empty_false_keeps_textless(self):
        docs = self._split("<root><a></a><b>real</b></root>", drop_empty=False)
        # Empty element kept as a chunk with empty/whitespace text.
        a_chunks = [d for d in docs if d.metadata["xml_path"] == "root > a"]
        self.assertEqual(len(a_chunks), 1)

    def test_non_xml_returned_unchanged(self):
        docs = self._split("just plain text, not xml")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "just plain text, not xml")
        self.assertNotIn("xml_path", docs[0].metadata or {})

    def test_empty_input(self):
        proc = XmlSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_empty_text_returned_unchanged(self):
        docs = self._split("")
        self.assertEqual(len(docs), 1)
        self.assertNotIn("xml_path", docs[0].metadata or {})

    # ------------------------------------------------------------------ #
    # namespaces, metadata, config
    # ------------------------------------------------------------------ #
    def test_namespace_stripped_from_path(self):
        docs = self._split(
            '<root xmlns="http://example.com"><child>x</child></root>')
        paths = self._paths(docs)
        self.assertIn("root > child", paths)
        self.assertFalse(any("example.com" in p for p in paths))

    def test_preserves_original_metadata(self):
        doc = Document(text="<root><a>1</a></root>", metadata={"src": "api"})
        proc = XmlSplitter()
        docs = proc.process_docs([doc], None)
        for d in docs:
            self.assertEqual(d.metadata["src"], "api")
            self.assertIn("xml_path", d.metadata)

    def test_custom_path_key(self):
        docs = self._split("<root><a>1</a></root>", path_key="my_path")
        self.assertIn("my_path", docs[0].metadata)
        self.assertNotIn("xml_path", docs[0].metadata)

    def test_custom_root_name(self):
        docs = self._split("<items><a>1</a></items>", root_name="doc")
        paths = self._paths(docs)
        self.assertIn("doc > a", paths)
        self.assertFalse(any(p.startswith("items") for p in paths))

    def test_invalid_max_depth_raises(self):
        with self.assertRaises(Exception):
            XmlSplitter(max_depth=0).process_docs(
                [Document(text="<a/>")], None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
