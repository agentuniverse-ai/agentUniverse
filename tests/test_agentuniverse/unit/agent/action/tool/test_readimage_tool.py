# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/27 21:38
# @Author  : zhangdongxu
# @Email   : zhangdongxu0852@163.com
# @FileName: test_readimage_tool.py
import os
import importlib.util
import unittest

HAS_CV_DEPS = (
    importlib.util.find_spec("cv2") is not None
    and importlib.util.find_spec("numpy") is not None
)
HAS_OCR_DEPS = (
    HAS_CV_DEPS
    and importlib.util.find_spec("PIL") is not None
    and importlib.util.find_spec("pytesseract") is not None
)

if HAS_CV_DEPS:
    import cv2
    import numpy as np
else:
    cv2 = None
    np = None

from agentuniverse.agent.action.tool.common_tool.readimage_tool import (
    clean_extracted_text,
    detect_text_regions,
    enhance_image,
    extract_text_from_image,
    save_text_to_file,
)

class TestReadImageTool(unittest.TestCase):
    def setUp(self):
        if HAS_CV_DEPS:
            # Create a simple color test image (100x100 pixels, random content)
            self.test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            # Create an image with black text on a white background for OCR testing
            self.test_ocr_image = np.full((100, 300, 3), 255, dtype=np.uint8)
            cv2.putText(self.test_ocr_image, 'Test', (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

    @unittest.skipUnless(HAS_CV_DEPS, "opencv-python and numpy are required")
    def test_enhance_image(self):
        enhanced = enhance_image(self.test_image)
        # The enhanced image is a grayscale image, and the shape should be two-dimensional
        self.assertEqual(len(enhanced.shape), 2)

    def test_clean_extracted_text(self):
        dirty_text = "This   is   a   test.\nNew    line."
        clean_text = clean_extracted_text(dirty_text)
        self.assertNotIn("\n", clean_text)
        self.assertNotIn("  ", clean_text)
        self.assertEqual(clean_text, "This is a test. New line.")

    def test_save_text_to_file(self):
        test_text = "Sample text for testing."
        test_filename = "test_extracted_text.txt"
        save_text_to_file(test_text, test_filename)
        try:
            self.assertTrue(os.path.exists(test_filename))
            with open(test_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, test_text)
        finally:
            if os.path.exists(test_filename): 
                os.remove(test_filename)

    @unittest.skipUnless(HAS_OCR_DEPS, "OCR dependencies are required")
    def test_extract_text_from_image_without_east(self):
        # Save the test OCR image as a temporary file
        temp_image = "temp_test_ocr.png"
        cv2.imwrite(temp_image, self.test_ocr_image)
        try:
            # Use simple OCR, no EAST detection
            text = extract_text_from_image(temp_image, use_east=False, lang='eng')
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 0)
        finally:
            if os.path.exists(temp_image):
                os.remove(temp_image)

    @unittest.skipUnless(HAS_CV_DEPS, "opencv-python and numpy are required")
    def test_detect_text_regions_no_text(self):
        # Text areas are usually not detected using random images
        regions = detect_text_regions(self.test_image)
        # The test result may be an empty list
        self.assertIsInstance(regions, list)

if __name__ == '__main__':
    unittest.main()

