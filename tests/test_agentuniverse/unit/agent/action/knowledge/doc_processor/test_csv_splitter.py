#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for CsvSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.csv_splitter \
    import CsvSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


CSV_10_ROWS = "name,age,city\n" + \
    "\n".join(f"Person{i},{20+i},City{i}" for i in range(1, 11))

TSV_5_ROWS = "name\tage\n" + \
    "\n".join(f"P{i}\t{i}" for i in range(1, 6))


class TestCsvSplitter(unittest.TestCase):

    def _split(self, text, **kwargs):
        proc = CsvSplitter(**kwargs)
        return proc.process_docs([Document(text=text)], None)

    def test_single_chunk_when_rows_fit(self):
        docs = self._split(CSV_10_ROWS, rows_per_chunk=50)
        self.assertEqual(len(docs), 1)

    def test_multiple_chunks(self):
        docs = self._split(CSV_10_ROWS, rows_per_chunk=3)
        # 10 data rows / 3 per chunk = 4 chunks (3+3+3+1).
        self.assertEqual(len(docs), 4)

    def test_header_on_every_chunk(self):
        docs = self._split(CSV_10_ROWS, rows_per_chunk=3)
        for d in docs:
            self.assertIn("name,age,city", d.text)

    def test_tsv_delimiter(self):
        docs = self._split(TSV_5_ROWS, delimiter="\t", rows_per_chunk=2)
        self.assertGreater(len(docs), 1)
        for d in docs:
            self.assertIn("name\tage", d.text)

    def test_empty_input(self):
        proc = CsvSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_header_only(self):
        docs = self._split("col1,col2\n")
        self.assertEqual(len(docs), 1)
        self.assertIn("col1", docs[0].text)

    def test_empty_text(self):
        docs = self._split("")
        self.assertEqual(len(docs), 0)

    def test_max_cell_chars_truncates(self):
        long_val = "x" * 200
        csv_text = f"data\n{long_val}\n"
        docs = self._split(csv_text, max_cell_chars=10)
        self.assertIn("…", docs[0].text)
        # The truncated cell should be short.
        lines = docs[0].text.split("\n")
        self.assertLessEqual(len(lines[1]), 11)

    def test_metadata_includes_chunk_method(self):
        docs = self._split(CSV_10_ROWS)
        self.assertEqual(docs[0].metadata["chunk_method"], "csv")

    def test_preserves_original_metadata(self):
        doc = Document(text="a,b\n1,2", metadata={"source": "file.csv"})
        proc = CsvSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "file.csv")

    def test_quoted_fields_preserved(self):
        csv_text = 'name,desc\n"John Doe","Hello, World"\n'
        docs = self._split(csv_text)
        self.assertIn("John Doe", docs[0].text)
        self.assertIn("Hello, World", docs[0].text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
