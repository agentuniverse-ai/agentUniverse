# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the Reader exception hierarchy."""

import unittest

from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderError,
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
    ReaderConfigError,
)


class TestReaderErrorHierarchy(unittest.TestCase):
    """Test the exception class hierarchy and inheritance."""

    def test_reader_error_is_exception(self):
        """ReaderError should inherit from Exception."""
        err = ReaderError("test message")
        self.assertIsInstance(err, Exception)

    def test_reader_error_message(self):
        """ReaderError should store and display the message."""
        err = ReaderError("something went wrong")
        self.assertIn("something went wrong", str(err))

    def test_reader_error_with_reader_name(self):
        """ReaderError should prefix message with reader_name."""
        err = ReaderError("load failed", reader_name="PdfReader")
        self.assertIn("[PdfReader]", str(err))
        self.assertIn("load failed", str(err))

    def test_reader_error_without_reader_name(self):
        """ReaderError without reader_name should not have prefix."""
        err = ReaderError("generic error")
        self.assertNotIn("[", str(err))
        self.assertIn("generic error", str(err))

    def test_reader_error_reader_name_attribute(self):
        """ReaderError should expose reader_name attribute."""
        err = ReaderError("test", reader_name="WebPageReader")
        self.assertEqual(err.reader_name, "WebPageReader")


class TestReaderLoadError(unittest.TestCase):
    """Test ReaderLoadError specific behavior."""

    def test_inherits_reader_error(self):
        """ReaderLoadError should inherit from ReaderError."""
        err = ReaderLoadError("file not found")
        self.assertIsInstance(err, ReaderError)

    def test_source_attribute(self):
        """ReaderLoadError should store source URL/path."""
        err = ReaderLoadError("not found", reader_name="PdfReader", source="/tmp/test.pdf")
        self.assertEqual(err.source, "/tmp/test.pdf")

    def test_status_code_attribute(self):
        """ReaderLoadError should store HTTP status code."""
        err = ReaderLoadError("HTTP 404", reader_name="WebPageReader", source="http://x.com", status_code=404)
        self.assertEqual(err.status_code, 404)

    def test_message_includes_source(self):
        """ReaderLoadError message should include source context."""
        err = ReaderLoadError("fetch failed", reader_name="WebPageReader", source="http://example.com")
        self.assertIn("fetch failed", str(err))

    def test_catch_as_reader_error(self):
        """ReaderLoadError should be catchable as ReaderError."""
        with self.assertRaises(ReaderError):
            raise ReaderLoadError("load failed", reader_name="TestReader")


class TestReaderDependencyError(unittest.TestCase):
    """Test ReaderDependencyError specific behavior."""

    def test_inherits_reader_error(self):
        """ReaderDependencyError should inherit from ReaderError."""
        err = ReaderDependencyError("missing dep")
        self.assertIsInstance(err, ReaderError)

    def test_dependency_attribute(self):
        """ReaderDependencyError should store dependency name."""
        err = ReaderDependencyError("missing", reader_name="PdfReader", dependency="pypdf")
        self.assertEqual(err.dependency, "pypdf")

    def test_install_hint_attribute(self):
        """ReaderDependencyError should store install hint."""
        err = ReaderDependencyError("missing", reader_name="PdfReader",
                                    dependency="pypdf", install_hint="pip install pypdf")
        self.assertEqual(err.install_hint, "pip install pypdf")

    def test_catch_as_reader_error(self):
        """ReaderDependencyError should be catchable as ReaderError."""
        with self.assertRaises(ReaderError):
            raise ReaderDependencyError("missing", dependency="test_pkg")


class TestReaderParseError(unittest.TestCase):
    """Test ReaderParseError specific behavior."""

    def test_inherits_reader_error(self):
        """ReaderParseError should inherit from ReaderError."""
        err = ReaderParseError("parse failed")
        self.assertIsInstance(err, ReaderError)

    def test_catch_as_reader_error(self):
        """ReaderParseError should be catchable as ReaderError."""
        with self.assertRaises(ReaderError):
            raise ReaderParseError("bad content", reader_name="JsonReader")


class TestReaderConfigError(unittest.TestCase):
    """Test ReaderConfigError specific behavior."""

    def test_inherits_reader_error(self):
        """ReaderConfigError should inherit from ReaderError."""
        err = ReaderConfigError("bad config")
        self.assertIsInstance(err, ReaderError)

    def test_catch_as_reader_error(self):
        """ReaderConfigError should be catchable as ReaderError."""
        with self.assertRaises(ReaderError):
            raise ReaderConfigError("missing credentials", reader_name="FeishuReader")


class TestExceptionSelectiveCatch(unittest.TestCase):
    """Test that specific exceptions can be caught selectively."""

    def test_catch_only_load_errors(self):
        """Only ReaderLoadError should be caught, not ReaderDependencyError."""
        caught = []
        try:
            raise ReaderLoadError("not found", reader_name="R1")
        except ReaderLoadError:
            caught.append("load")
        try:
            raise ReaderDependencyError("missing", reader_name="R2")
        except ReaderDependencyError:
            caught.append("dep")
        self.assertEqual(caught, ["load", "dep"])

    def test_catch_all_reader_errors(self):
        """All ReaderError subclasses should be catchable via base class."""
        errors = []
        for exc_class in [ReaderLoadError, ReaderDependencyError, ReaderParseError, ReaderConfigError]:
            try:
                raise exc_class("test", reader_name="TestReader")
            except ReaderError as e:
                errors.append(type(e).__name__)
        self.assertEqual(errors, ["ReaderLoadError", "ReaderDependencyError", "ReaderParseError", "ReaderConfigError"])


if __name__ == "__main__":
    unittest.main()