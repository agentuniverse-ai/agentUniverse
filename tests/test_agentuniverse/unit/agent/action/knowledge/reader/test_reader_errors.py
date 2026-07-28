# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/5
# @FileName: test_reader_errors.py
"""Tests for the Reader exception hierarchy.

Validates:
- Inheritance chain (all exceptions inherit from ReaderError)
- Keyword-only arguments and default values
- Message formatting with reader_name prefix and semantic attributes
- Backward compatibility: ReaderError is still an Exception
"""

import unittest

from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderError,
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
    ReaderConfigError,
)


class TestReaderErrorBase(unittest.TestCase):
    """Tests for the base ReaderError class."""

    def test_inherits_from_exception(self):
        self.assertTrue(issubclass(ReaderError, Exception))

    def test_default_message(self):
        err = ReaderError()
        self.assertEqual(str(err), "")

    def test_message_only(self):
        err = ReaderError("something went wrong")
        self.assertEqual(str(err), "something went wrong")

    def test_reader_name_prefix(self):
        err = ReaderError("fail", reader_name="PdfReader")
        self.assertEqual(str(err), "[PdfReader] fail")

    def test_reader_name_empty_no_prefix(self):
        err = ReaderError("fail", reader_name="")
        self.assertEqual(str(err), "fail")

    def test_reader_name_attribute(self):
        err = ReaderError("x", reader_name="CsvReader")
        self.assertEqual(err.reader_name, "CsvReader")

    def test_reader_name_default_empty(self):
        err = ReaderError("x")
        self.assertEqual(err.reader_name, "")

    def test_keyword_only_reader_name(self):
        # reader_name must be keyword-only
        with self.assertRaises(TypeError):
            ReaderError("msg", "Name")  # type: ignore


class TestReaderLoadError(unittest.TestCase):
    """Tests for ReaderLoadError."""

    def test_inherits_from_reader_error(self):
        self.assertTrue(issubclass(ReaderLoadError, ReaderError))

    def test_basic_message(self):
        err = ReaderLoadError("file not found", reader_name="PdfReader")
        self.assertIn("file not found", str(err))
        self.assertIn("[PdfReader]", str(err))

    def test_source_attribute(self):
        err = ReaderLoadError("fail", reader_name="R", source="/tmp/a.pdf")
        self.assertEqual(err.source, "/tmp/a.pdf")
        self.assertIn("source=/tmp/a.pdf", str(err))

    def test_status_code_attribute(self):
        err = ReaderLoadError("forbidden", reader_name="R", status_code=403)
        self.assertEqual(err.status_code, 403)
        self.assertIn("HTTP 403", str(err))

    def test_source_and_status_code(self):
        err = ReaderLoadError("denied", reader_name="R",
                              source="https://x.com", status_code=403)
        self.assertIn("source=https://x.com", str(err))
        self.assertIn("HTTP 403", str(err))

    def test_defaults(self):
        err = ReaderLoadError("msg")
        self.assertEqual(err.source, "")
        self.assertIsNone(err.status_code)
        self.assertEqual(err.reader_name, "")


class TestReaderDependencyError(unittest.TestCase):
    """Tests for ReaderDependencyError."""

    def test_inherits_from_reader_error(self):
        self.assertTrue(issubclass(ReaderDependencyError, ReaderError))

    def test_dependency_attribute(self):
        err = ReaderDependencyError("missing", reader_name="R",
                                    dependency="pymupdf")
        self.assertEqual(err.dependency, "pymupdf")
        self.assertIn("Missing dependency 'pymupdf'", str(err))

    def test_install_hint(self):
        err = ReaderDependencyError("missing", reader_name="R",
                                    dependency="pymupdf",
                                    install_hint="pip install pymupdf")
        self.assertEqual(err.install_hint, "pip install pymupdf")
        self.assertIn("Install with: pip install pymupdf", str(err))

    def test_defaults(self):
        err = ReaderDependencyError("msg")
        self.assertEqual(err.dependency, "")
        self.assertEqual(err.install_hint, "")


class TestReaderParseError(unittest.TestCase):
    """Tests for ReaderParseError."""

    def test_inherits_from_reader_error(self):
        self.assertTrue(issubclass(ReaderParseError, ReaderError))

    def test_source_attribute(self):
        err = ReaderParseError("bad html", reader_name="R",
                               source="https://x.com")
        self.assertEqual(err.source, "https://x.com")
        self.assertIn("source=https://x.com", str(err))

    def test_defaults(self):
        err = ReaderParseError("msg")
        self.assertEqual(err.source, "")


class TestReaderConfigError(unittest.TestCase):
    """Tests for ReaderConfigError."""

    def test_inherits_from_reader_error(self):
        self.assertTrue(issubclass(ReaderConfigError, ReaderError))

    def test_config_key_attribute(self):
        err = ReaderConfigError("missing", reader_name="R",
                                config_key="api_key")
        self.assertEqual(err.config_key, "api_key")
        self.assertIn("config 'api_key'", str(err))

    def test_defaults(self):
        err = ReaderConfigError("msg")
        self.assertEqual(err.config_key, "")


class TestExceptionCatching(unittest.TestCase):
    """Test that specific exceptions can be caught by their base class."""

    def test_catch_load_error_as_reader_error(self):
        with self.assertRaises(ReaderError):
            raise ReaderLoadError("not found", reader_name="R", source="f.pdf")

    def test_catch_dependency_error_as_reader_error(self):
        with self.assertRaises(ReaderError):
            raise ReaderDependencyError("missing dep", reader_name="R",
                                        dependency="pymupdf")

    def test_catch_parse_error_as_reader_error(self):
        with self.assertRaises(ReaderError):
            raise ReaderParseError("bad format", reader_name="R")

    def test_catch_config_error_as_reader_error(self):
        with self.assertRaises(ReaderError):
            raise ReaderConfigError("bad config", reader_name="R")

    def test_catch_reader_error_as_exception(self):
        with self.assertRaises(Exception):
            raise ReaderError("generic")


class TestPackageExports(unittest.TestCase):
    """Verify that all exceptions are exported from the reader package."""

    def test_imports_from_package(self):
        from agentuniverse.agent.action.knowledge.reader import (
            ReaderError,
            ReaderLoadError,
            ReaderDependencyError,
            ReaderParseError,
            ReaderConfigError,
        )
        # Just verify they're importable and are exception classes
        self.assertTrue(issubclass(ReaderError, Exception))
        self.assertTrue(issubclass(ReaderLoadError, ReaderError))
        self.assertTrue(issubclass(ReaderDependencyError, ReaderError))
        self.assertTrue(issubclass(ReaderParseError, ReaderError))
        self.assertTrue(issubclass(ReaderConfigError, ReaderError))


if __name__ == "__main__":
    unittest.main()