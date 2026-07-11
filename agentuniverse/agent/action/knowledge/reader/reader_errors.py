# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: reader_errors.py
"""Unified exception hierarchy for the knowledge reader subsystem.

All reader implementations should raise the dedicated exceptions defined here
instead of raw built-in exceptions such as ``ValueError`` or ``ImportError``,
so that callers can handle reader failures in a consistent manner.
"""


class ReaderError(Exception):
    """Base class for all reader related errors."""

    def __init__(self, message: str = "", reader_name: str = ""):
        """Initialize the reader error.

        Args:
            message (str): Human readable description of the error.
            reader_name (str): Name of the reader that raised the error.
        """
        self.reader_name = reader_name
        self.message = message
        full_message = f"[{reader_name}] {message}" if reader_name else message
        super().__init__(full_message)


class ReaderLoadError(ReaderError):
    """Raised when a reader fails to load or fetch the source data.

    This covers network failures, authentication issues, missing resources,
    file-not-found scenarios and any problem occurring while retrieving the
    raw content to be parsed.
    """


class ReaderDependencyError(ReaderError):
    """Raised when an optional third-party dependency is required but missing.

    Readers keep heavy/optional libraries out of the core install. When such a
    dependency is needed at runtime and cannot be imported, this exception
    should be raised so callers can surface actionable installation hints.
    """


class ReaderParseError(ReaderError):
    """Raised when a reader fails to parse or extract structured content.

    This covers malformed documents, unexpected schemas, decoding errors and
    any failure happening between raw content retrieval and ``Document`` output.
    """


class ReaderConfigError(ReaderError):
    """Raised when a reader is invoked with invalid or missing configuration.

    Examples include missing authentication tokens, invalid URLs, unsupported
    parameters and other misuses of the reader interface.
    """
