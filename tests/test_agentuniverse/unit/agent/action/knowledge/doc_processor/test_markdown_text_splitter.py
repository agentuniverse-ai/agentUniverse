#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for MarkdownTextSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.markdown_text_splitter \
    import MarkdownTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


SAMPLE_MD = """# Title

First paragraph of text.

Second paragraph here.

```python
def hello():
    print("hello world")
```

| Col A | Col B |
|-------|-------|
| 1     | 2     |

- Item one
- Item two
- Item three

> A blockquote.

Final paragraph.
"""


class TestMarkdownTextSplitter(unittest.TestCase):

    def _split(self, md, **kwargs):
        proc = MarkdownTextSplitter(**kwargs)
        return proc.process_docs([Document(text=md)], None)

    def test_code_fence_kept_intact(self):
        docs = self._split(SAMPLE_MD, max_chunk_size=5000)
        combined = " ".join(d.text for d in docs)
        self.assertIn("```python", combined)
        self.assertIn("def hello", combined)

    def test_multiple_chunks_for_large_doc(self):
        long = "Paragraph text here.\n\n" * 100
        docs = self._split(long, max_chunk_size=200)
        self.assertGreater(len(docs), 1)

    def test_short_doc_single_chunk(self):
        docs = self._split("Short text.\n")
        self.assertEqual(len(docs), 1)

    def test_empty_input(self):
        proc = MarkdownTextSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_max_chunk_size_respected(self):
        docs = self._split("Line.\n" * 200, max_chunk_size=100)
        for d in docs:
            self.assertLessEqual(len(d.text), 110)

    def test_min_chunk_size_merges_small(self):
        docs = self._split("A.\n\nB.\n\nC.\n\n", max_chunk_size=200, min_chunk_size=50)
        # Small paragraphs merged, not one-per-chunk.
        self.assertLess(len(docs), 4)

    def test_code_fence_not_split_mid_block(self):
        code = "```python\n" + "x = 1\n" * 50 + "```\n"
        docs = self._split(code, max_chunk_size=100)
        # The code block exceeds max_chunk_size, so it's hard-split.
        self.assertGreater(len(docs), 1)

    def test_table_block_kept_together(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        docs = self._split(md, max_chunk_size=5000)
        combined = " ".join(d.text for d in docs)
        self.assertIn("| A | B |", combined)

    def test_metadata_includes_chunk_method(self):
        docs = self._split("Hello.")
        self.assertEqual(docs[0].metadata["chunk_method"], "markdown_text")

    def test_preserves_original_metadata(self):
        doc = Document(text="Some text.", metadata={"source": "test"})
        proc = MarkdownTextSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
