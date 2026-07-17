# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/5
# @FileName: reader_errors.py
"""Custom exception hierarchy for Reader components.

All Reader-specific exceptions inherit from ReaderError, providing
a consistent and semantic error handling experience across the
knowledge reader subsystem.
"""


class ReaderError(Exception):
    """Base exception for all Reader-related errors."""

    def __init__(self, message: str = "", *, reader_name: str = ""):
        self.reader_name = reader_name
        prefix = f"[{reader_name}] " if reader_name else ""
        super().__init__(f"{prefix}{message}")


class ReaderLoadError(ReaderError, OSError):
    """Raised when a Reader fails to load data from the source.

    Typical causes: network errors, file not found, HTTP 4xx/5xx,
    invalid URL, or permission denied.

    Also inherits from OSError so that existing code catching
    FileNotFoundError or OSError remains compatible.
    """

    def __init__(self, message: str = "", *, reader_name: str = "",
                 source: str = "", status_code: int = None):
        self.source = source
        self.status_code = status_code
        detail = message
        if source:
            detail = f"source={source}: {message}" if message else f"source={source}"
        if status_code:
            detail = f"{detail} (HTTP {status_code})" if detail else f"HTTP {status_code}"
        super().__init__(detail, reader_name=reader_name)


class ReaderDependencyError(ReaderError, ImportError):
    """Raised when an optional dependency required by a Reader is not installed.

    Provides the package name and a pip install hint so users can
    resolve the issue quickly.

    Also inherits from ImportError so that existing code catching
    ImportError remains compatible.
    """

    def __init__(self, message: str = "", *, reader_name: str = "",
                 dependency: str = "", install_hint: str = ""):
        self.dependency = dependency
        self.install_hint = install_hint
        detail = message
        if dependency:
            detail = f"Missing dependency '{dependency}': {message}" if message else f"Missing dependency '{dependency}'"
        if install_hint:
            detail = f"{detail}. Install with: {install_hint}"
        super().__init__(detail, reader_name=reader_name)


class ReaderParseError(ReaderError, ValueError):
    """Raised when a Reader fails to parse the loaded content.

    Typical causes: unexpected HTML structure, unsupported format,
    or corrupted file content.

    Also inherits from ValueError so that existing code catching
    ValueError or json.JSONDecodeError remains compatible.
    """

    def __init__(self, message: str = "", *, reader_name: str = "",
                 source: str = ""):
        self.source = source
        detail = message
        if source:
            detail = f"source={source}: {message}" if message else f"source={source}"
        super().__init__(detail, reader_name=reader_name)


class ReaderConfigError(ReaderError, ValueError, TypeError):
    """Raised when a Reader is misconfigured or missing required configuration.

    Typical causes: missing authentication credentials, invalid
    configuration parameters, or missing environment variables.

    Also inherits from ValueError and TypeError so that existing
    code catching either of those remains compatible.
    """

    def __init__(self, message: str = "", *, reader_name: str = "",
                 config_key: str = ""):
        self.config_key = config_key
        detail = message
        if config_key:
            detail = f"config '{config_key}': {message}" if message else f"Missing or invalid config '{config_key}'"
        super().__init__(detail, reader_name=reader_name)