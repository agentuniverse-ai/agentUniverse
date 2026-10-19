#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for reader robustness fixes (pdf, docx, xlsx, pptx, epub).

All tests use source-contract checks (inspect.getsource) to verify the
fixes are in place, since the actual library dependencies are optional
and constructing real corrupt files is heavy.
"""

import unittest


class TestPdfReaderRobustness(unittest.TestCase):

    def test_extract_text_guards_none(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.pdf_reader \
            import PdfReader
        src = inspect.getsource(PdfReader._load_data)
        # Must guard extract_text returning None.
        self.assertIn('or ""', src,
                      "extract_text() return must be guarded against None")

    def test_page_labels_has_fallback(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.pdf_reader \
            import PdfReader
        src = inspect.getsource(PdfReader._load_data)
        self.assertIn("except", src)
        self.assertIn("page + 1", src,
                      "page_labels access must have a fallback to page number")


class TestDocxReaderRobustness(unittest.TestCase):

    def test_parse_has_try_except(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.docx_reader \
            import DocxReader
        src = inspect.getsource(DocxReader._load_data)
        self.assertIn("try:", src)
        self.assertIn("Failed to parse DOCX", src,
                      "docx parse failure must raise ValueError with context")

    def test_text_none_guard(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.docx_reader \
            import DocxReader
        src = inspect.getsource(DocxReader._load_data)
        self.assertIn("is None", src,
                      "docx2txt.process result must be guarded against None")


class TestXlsxReaderRobustness(unittest.TestCase):

    def test_load_workbook_has_try_except(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader \
            import XlsxReader
        src = inspect.getsource(XlsxReader._load_data)
        self.assertIn("Failed to parse XLSX", src,
                      "openpyxl load_workbook must be wrapped in try/except")

    def test_no_identical_if_else_branches(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader \
            import XlsxReader
        src = inspect.getsource(XlsxReader._load_data)
        # The old dead code had identical if/else bodies. The fix handles
        # datetime/date specially.
        self.assertIn("datetime", src,
                      "cell value handling should special-case datetime")
        self.assertIn("isoformat", src,
                      "datetime cells should use isoformat()")

    def test_no_duplicate_str_append(self):
        """Verify the identical if/else dead code is gone."""
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader \
            import XlsxReader
        src = inspect.getsource(XlsxReader._load_data)
        # The old code had:
        #   if isinstance(cell.value, (int, float)):
        #       row_data.append(str(cell.value))
        #   else:
        #       row_data.append(str(cell.value))
        # Both branches identical. Verify it's gone.
        self.assertNotIn(
            "if isinstance(cell.value, (int, float)):\n"
            "                            row_data.append(str(cell.value))\n"
            "                        else:\n"
            "                            row_data.append(str(cell.value))",
            src,
            "the identical if/else dead code must be removed")


class TestPptxReaderRobustness(unittest.TestCase):

    def test_empty_shapes_skipped(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.pptx_reader \
            import PptxReader
        src = inspect.getsource(PptxReader._load_data)
        # Must check that shape.text is non-empty before appending.
        self.assertIn(".strip()", src,
                      "empty shape text must be skipped")

    def test_parse_has_try_except(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.pptx_reader \
            import PptxReader
        src = inspect.getsource(PptxReader._load_data)
        self.assertIn("Failed to parse PPTX", src,
                      "Presentation() must be wrapped in try/except")


class TestEpubReaderRobustness(unittest.TestCase):

    def test_metadata_uses_safe_helper(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.epub_reader \
            import EpubReader
        src = inspect.getsource(EpubReader._load_data)
        self.assertIn("_safe_meta", src,
                      "metadata extraction must use a None-safe helper")
        # Old code used [0][0] directly.
        self.assertNotIn(
            "book.get_metadata('DC', 'title')[0][0]",
            src,
            "raw [0][0] indexing on metadata must be replaced with safe access")

    def test_get_content_none_guard(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.epub_reader \
            import EpubReader
        src = inspect.getsource(EpubReader._load_data)
        self.assertIn("is None", src,
                      "item.get_content() must be guarded against None")

    def test_parse_has_try_except(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.epub_reader \
            import EpubReader
        src = inspect.getsource(EpubReader._load_data)
        self.assertIn("Failed to parse EPUB", src,
                      "epub.read_epub must be wrapped in try/except")


if __name__ == "__main__":
    unittest.main(verbosity=2)
