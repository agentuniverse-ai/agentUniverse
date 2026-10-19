#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for image OCR None-guard, print cleanup, and raise-from-e.

1. PaddleOCR returns [[None]] / [[(box, (None, conf))]] for low-confidence
   pages; the previous loop did `for line in page` / `line[1][0]`
   unconditionally and raised TypeError, which the outer except caught and
   silently downgraded to pytesseract without surfacing the cause.
2. Stray `print("debugging: ...")` statements removed.
3. image_reader `raise Exception(...)` lost the original traceback; now
   `raise RuntimeError(...) from e`.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestImageOCRReaderPaddleNoneGuard(unittest.TestCase):
    """PaddleOCR None page/line must be skipped, not crash into fallback."""

    def _reader(self):
        from agentuniverse.agent.action.knowledge.reader.image.\
            image_ocr_reader import ImageOCRReader
        return ImageOCRReader()

    def test_none_page_is_skipped_not_crashing(self):
        reader = self._reader()
        fake_paddle = MagicMock()
        # PaddleOCR.ocr returns [[None, [(box, ('text', 0.9))]]] — first page
        # is None, second has a real line.
        fake_paddle.PaddleOCR.return_value.ocr.return_value = [
            None,
            [[((0, 0), (1, 0), (1, 1), (0, 1)), ("hello", 0.95)]],
        ]
        with patch.dict("sys.modules", {"paddleocr": fake_paddle}):
            text, engine = reader._ocr(__file__)
        self.assertEqual(engine, "paddleocr")
        self.assertIn("hello", text)

    def test_none_line_is_skipped(self):
        reader = self._reader()
        fake_paddle = MagicMock()
        fake_paddle.PaddleOCR.return_value.ocr.return_value = [
            [[((0, 0), (1, 0), (1, 1), (0, 1)), None],
             [((0, 0), (1, 0), (1, 1), (0, 1)), ("world", 0.9)]],
        ]
        with patch.dict("sys.modules", {"paddleocr": fake_paddle}):
            text, engine = reader._ocr(__file__)
        self.assertIn("world", text)
        self.assertNotIn("None", text)


class TestImageOCRReaderPrintCleanup(unittest.TestCase):
    """No stray print('debugging: ...') statements."""

    def test_source_has_no_debug_prints(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.image.\
            image_ocr_reader import ImageOCRReader

        src = inspect.getsource(ImageOCRReader)
        self.assertNotIn('print("debugging:', src,
                         "ImageOCRReader must not ship debug print statements")
        self.assertNotIn("print(f\"debugging:", src)


class TestImageReaderRaiseFromE(unittest.TestCase):
    """image_reader must chain the original exception."""

    def test_source_uses_from_e(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.image.\
            image_reader import ImageReader

        # The raise is in _load_data; check the source has `from e`.
        src = inspect.getsource(ImageReader)
        # Find the error-handling raise.
        self.assertIn("raise RuntimeError", src,
                      "image_reader should raise RuntimeError, not bare Exception")
        self.assertIn("from e", src,
                      "image_reader must chain the original exception with `from e`")


if __name__ == "__main__":
    unittest.main(verbosity=2)
