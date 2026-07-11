# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: test_reader_errors.py
"""Unit tests for the unified reader exception hierarchy."""
import pytest

from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderError,
    ReaderLoadError,
    ReaderParseError,
)


def test_reader_error_is_base():
    """ReaderError is the base of the hierarchy."""
    assert issubclass(ReaderLoadError, ReaderError)
    assert issubclass(ReaderDependencyError, ReaderError)
    assert issubclass(ReaderParseError, ReaderError)
    assert issubclass(ReaderConfigError, ReaderError)


def test_reader_error_is_exception():
    """ReaderError subclasses Exception."""
    assert issubclass(ReaderError, Exception)


def test_reader_error_message_without_name():
    """A bare message is preserved when no reader name is given."""
    err = ReaderLoadError("network down")
    assert "network down" in str(err)


def test_reader_error_message_with_name():
    """The reader name is included in the message."""
    err = ReaderConfigError("missing token", reader_name="NotionReader")
    assert "NotionReader" in str(err)
    assert "missing token" in str(err)
    assert err.reader_name == "NotionReader"


def test_reader_error_can_be_raised_and_caught():
    """Each sub-exception is catchable as ReaderError."""
    with pytest.raises(ReaderError):
        raise ReaderParseError("bad doc")


def test_each_subtype_distinct():
    """Each sub-exception is distinct."""
    assert ReaderLoadError is not ReaderDependencyError
    assert ReaderParseError is not ReaderConfigError
