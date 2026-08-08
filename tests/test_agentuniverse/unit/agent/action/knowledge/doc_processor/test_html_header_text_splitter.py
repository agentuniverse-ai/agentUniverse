#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for HtmlHeaderTextSplitter DocProcessor."""

import os
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.html_header_text_splitter \
    import HtmlHeaderTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document

_YAML_PATH = os.path.join(
    os.path.dirname(HtmlHeaderTextSplitter.__module__.replace(".", "/") + ".py"),
    "html_header_text_splitter.yaml")  # not used directly; placeholder


SIMPLE_HTML = """
<html>
<head><title>Ignored</title><style>body { color: red; }</style></head>
<body>
<p>Preamble text before headers.</p>
<h1>Installation</h1>
<p>Install via pip.</p>
<h2>macOS</h2>
<p>brew install agentuniverse</p>
<h2>Linux</h2>
<p>apt install agentuniverse</p>
<h1>Usage</h1>
<p>Import and go.</p>
</body>
</html>
"""

NESTED_HTML = """
<h1>Level One</h1>
<p>Text under level one.</p>
<h3>Level Three (skips h2)</h3>
<p>Text under level three.</p>
<h2>Level Two</h2>
<p>After h2, h3 context resets.</p>
"""

NO_HEADER_HTML = """
<div>
<p>Just some text.</p>
<p>No headers at all.</p>
</div>
"""


class TestHtmlHeaderTextSplitter(unittest.TestCase):

    def _split(self, html, **kwargs):
        proc = HtmlHeaderTextSplitter(**kwargs)
        docs = proc.process_docs([Document(text=html)], None)
        return docs

    def test_splits_by_headers(self):
        docs = self._split(SIMPLE_HTML)
        paths = [d.metadata["header_path"] for d in docs]
        self.assertIn("Installation", paths)
        self.assertIn("Installation > macOS", paths)
        self.assertIn("Installation > Linux", paths)
        self.assertIn("Usage", paths)

    def test_preamble_with_unsectioned(self):
        docs = self._split(SIMPLE_HTML, include_unsectioned=True)
        # The preamble should be a chunk with an empty header path.
        empty_chunks = [d for d in docs if d.metadata["header_path"] == ""]
        self.assertGreater(len(empty_chunks), 0)
        self.assertIn("Preamble", empty_chunks[0].text)

    def test_preamble_without_unsectioned(self):
        docs = self._split(SIMPLE_HTML, include_unsectioned=False)
        empty_chunks = [d for d in docs if d.metadata["header_path"] == ""]
        self.assertEqual(len(empty_chunks), 0)

    def test_nested_headers_reset_correctly(self):
        docs = self._split(NESTED_HTML)
        paths = [d.metadata["header_path"] for d in docs]
        self.assertIn("Level One", paths)
        self.assertIn("Level One > Level Three (skips h2)", paths)
        # After h2, the h3 is cleared (lower-level headers are reset when
        # a higher-level or same-level header appears).
        self.assertIn("Level One > Level Two", paths)
        self.assertNotIn("Level One > Level Two > Level Three (skips h2)", paths)

    def test_no_headers_returns_single_chunk_or_empty(self):
        docs = self._split(NO_HEADER_HTML, include_unsectioned=True)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["header_path"], "")
        self.assertIn("Just some text", docs[0].text)

    def test_script_style_noscript_are_skipped(self):
        html = '<h1>OK</h1><script>alert(1)</script><style>a{}</style><p>visible</p>'
        docs = self._split(html)
        combined = " ".join(d.text for d in docs)
        self.assertNotIn("alert", combined)
        self.assertNotIn("{}", combined)
        self.assertIn("visible", combined)

    def test_empty_input_returns_empty(self):
        proc = HtmlHeaderTextSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_none_text_handled(self):
        proc = HtmlHeaderTextSplitter()
        # Document.text is Optional[str]; pass empty string (None would
        # crash the Document id validator, which is a separate concern).
        docs = proc.process_docs([Document(text="")], None)
        # Empty input text yields no chunks.
        self.assertEqual(len(docs), 0)

    def test_custom_header_path_key(self):
        docs = self._split('<h1>X</h1><p>Y</p>', header_path_key="my_path")
        self.assertIn("my_path", docs[0].metadata)
        self.assertEqual(docs[0].metadata["my_path"], "X")

    def test_preserves_original_metadata(self):
        doc = Document(text="<h1>H</h1><p>B</p>", metadata={"source": "test"})
        proc = HtmlHeaderTextSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "test")
        self.assertIn("header_path", docs[0].metadata)


if __name__ == "__main__":
    unittest.main(verbosity=2)
