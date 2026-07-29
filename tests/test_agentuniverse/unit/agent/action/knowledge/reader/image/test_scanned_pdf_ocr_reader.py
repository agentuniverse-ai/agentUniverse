#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import builtins
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import ScannedPdfOCRReader


class ScannedPdfOCRReaderTest(unittest.TestCase):
    def test_load_data_logs_pypdf_fallback_without_printing(self):
        reader = ScannedPdfOCRReader()
        with tempfile.NamedTemporaryFile(suffix=".pdf") as fp:
            pdf_file = Path(fp.name)

            with patch.object(builtins, "print") as mock_print, \
                    patch.object(reader, "_count_pdf_pages", return_value=1), \
                    patch.object(reader, "_ocr_pdf_page", return_value=("ocr text", "fake-ocr")), \
                    patch("agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader.LOGGER") as mock_logger:
                docs = reader._load_data(pdf_file)

        self.assertEqual(docs[0].text, "ocr text")
        self.assertEqual(docs[0].metadata["engine"], "fake-ocr")
        mock_print.assert_not_called()
        self.assertGreaterEqual(mock_logger.debug.call_count, 2)


if __name__ == "__main__":
    unittest.main()
