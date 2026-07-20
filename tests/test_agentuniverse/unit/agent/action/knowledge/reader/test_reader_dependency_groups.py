# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/16
# @FileName: test_reader_dependency_groups.py
"""Tests for reader dependency groups in pyproject.toml.

Validates:
- All optional reader dependencies are declared correctly
- All extras groups reference valid optional dependencies
- Extras groups cover all expected reader categories
- reader-all includes all reader optional dependencies
- Backward compatibility: existing extras (log_ext, store_ext) unchanged
"""

import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


PYPROJECT_PATH = Path(__file__).resolve().parents[7] / "pyproject.toml"


class _PyprojectMixin:
    """Shared fixture: load pyproject.toml once per test class."""

    @classmethod
    def _load_pyproject(cls):
        with open(PYPROJECT_PATH, "rb") as f:
            cls._pyproject = tomllib.load(f)
        cls._dependencies = cls._pyproject["tool"]["poetry"]["dependencies"]
        cls._extras = cls._pyproject["tool"]["poetry"]["extras"]


class TestOptionalDependencies(_PyprojectMixin, unittest.TestCase):
    """Validate optional reader dependency declarations."""

    @classmethod
    def setUpClass(cls):
        cls._load_pyproject()

    def _is_optional(self, name: str) -> bool:
        dep = self._dependencies.get(name)
        if dep is None:
            return False
        if isinstance(dep, dict):
            return dep.get("optional", False)
        return False

    def test_pypdf_optional(self):
        self.assertTrue(self._is_optional("pypdf"))

    def test_docx2txt_optional(self):
        self.assertTrue(self._is_optional("docx2txt"))

    def test_python_pptx_optional(self):
        self.assertTrue(self._is_optional("python-pptx"))

    def test_trafilatura_optional(self):
        self.assertTrue(self._is_optional("trafilatura"))

    def test_readability_lxml_optional(self):
        self.assertTrue(self._is_optional("readability-lxml"))

    def test_lxml_optional(self):
        self.assertTrue(self._is_optional("lxml"))

    def test_paddleocr_optional(self):
        self.assertTrue(self._is_optional("paddleocr"))

    def test_paddlepaddle_optional(self):
        self.assertTrue(self._is_optional("paddlepaddle"))

    def test_pytesseract_optional(self):
        self.assertTrue(self._is_optional("pytesseract"))

    def test_easyocr_optional(self):
        self.assertTrue(self._is_optional("easyocr"))

    def test_selenium_optional(self):
        self.assertTrue(self._is_optional("selenium"))

    def test_playwright_optional(self):
        self.assertTrue(self._is_optional("playwright"))

    def test_pdf2image_optional(self):
        self.assertTrue(self._is_optional("pdf2image"))

    def test_atlassian_python_api_optional(self):
        self.assertTrue(self._is_optional("atlassian-python-api"))

    def test_notion_client_optional(self):
        self.assertTrue(self._is_optional("notion-client"))

    def test_google_api_python_client_optional(self):
        self.assertTrue(self._is_optional("google-api-python-client"))

    def test_google_auth_optional(self):
        self.assertTrue(self._is_optional("google-auth"))

    def test_google_auth_oauthlib_optional(self):
        self.assertTrue(self._is_optional("google-auth-oauthlib"))


class TestExtrasGroups(_PyprojectMixin, unittest.TestCase):
    """Validate extras group definitions."""

    @classmethod
    def setUpClass(cls):
        cls._load_pyproject()

    def test_pdf_group(self):
        self.assertIn("pdf", self._extras)
        self.assertIn("pypdf", self._extras["pdf"])

    def test_docx_group(self):
        self.assertIn("docx", self._extras)
        self.assertIn("docx2txt", self._extras["docx"])

    def test_pptx_group(self):
        self.assertIn("pptx", self._extras)
        self.assertIn("python-pptx", self._extras["pptx"])

    def test_web_extract_group(self):
        self.assertIn("web-extract", self._extras)
        self.assertIn("trafilatura", self._extras["web-extract"])
        self.assertIn("readability-lxml", self._extras["web-extract"])
        self.assertIn("lxml", self._extras["web-extract"])

    def test_web_render_group(self):
        self.assertIn("web-render", self._extras)
        self.assertIn("playwright", self._extras["web-render"])

    def test_ocr_paddle_group(self):
        self.assertIn("ocr-paddle", self._extras)
        self.assertIn("paddleocr", self._extras["ocr-paddle"])
        self.assertIn("paddlepaddle", self._extras["ocr-paddle"])

    def test_ocr_tesseract_group(self):
        self.assertIn("ocr-tesseract", self._extras)
        self.assertIn("pytesseract", self._extras["ocr-tesseract"])

    def test_ocr_easy_group(self):
        self.assertIn("ocr-easy", self._extras)
        self.assertIn("easyocr", self._extras["ocr-easy"])

    def test_ocr_group(self):
        self.assertIn("ocr", self._extras)
        self.assertIn("paddleocr", self._extras["ocr"])
        self.assertIn("pytesseract", self._extras["ocr"])
        self.assertIn("easyocr", self._extras["ocr"])

    def test_pdf_ocr_group(self):
        self.assertIn("pdf-ocr", self._extras)
        self.assertIn("pdf2image", self._extras["pdf-ocr"])
        self.assertIn("pypdf", self._extras["pdf-ocr"])

    def test_selenium_reader_group(self):
        self.assertIn("selenium-reader", self._extras)
        self.assertIn("selenium", self._extras["selenium-reader"])

    def test_cloud_group(self):
        self.assertIn("cloud", self._extras)
        self.assertIn("atlassian-python-api", self._extras["cloud"])
        self.assertIn("notion-client", self._extras["cloud"])
        self.assertIn("google-api-python-client", self._extras["cloud"])

    def test_reader_all_group(self):
        self.assertIn("reader-all", self._extras)
        all_pkgs = self._extras["reader-all"]
        expected = [
            "pypdf", "docx2txt", "python-pptx", "trafilatura",
            "readability-lxml", "lxml", "paddleocr", "paddlepaddle",
            "pytesseract", "easyocr", "pdf2image", "playwright",
            "atlassian-python-api", "notion-client",
            "google-api-python-client", "google-auth",
            "google-auth-oauthlib", "selenium",
        ]
        for pkg in expected:
            self.assertIn(pkg, all_pkgs, f"reader-all missing {pkg}")


class TestBackwardCompatibility(_PyprojectMixin, unittest.TestCase):
    """Existing extras must remain unchanged."""

    @classmethod
    def setUpClass(cls):
        cls._load_pyproject()

    def test_log_ext_unchanged(self):
        self.assertIn("log_ext", self._extras)
        self.assertEqual(self._extras["log_ext"], ["aliyun-log-python-sdk"])

    def test_store_ext_unchanged(self):
        self.assertIn("store_ext", self._extras)
        self.assertEqual(self._extras["store_ext"], ["pymilvus"])


if __name__ == "__main__":
    unittest.main()