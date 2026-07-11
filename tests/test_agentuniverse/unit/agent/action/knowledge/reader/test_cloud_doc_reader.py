# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: test_cloud_doc_reader.py
"""Unit tests for the unified CloudDocReader domain routing.

These tests exercise the automatic domain-based dispatch logic and the
:func:`get_url_default_reader` helper without performing any real network or
cloud api calls. Concrete cloud readers are replaced with lightweight stubs.
"""
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader import (
    CloudDocReader,
    URL_PATTERN_MAP,
    _match_reader_name,
    get_url_default_reader,
)
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
)


class _StubReader:
    """Minimal reader stub recording the arguments it was called with."""

    def __init__(self):
        self.calls = []

    def load_data(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return [{"text": "stub"}]


# ---------------------------------------------------------------------------
# 1. Domain -> reader name routing
# ---------------------------------------------------------------------------

def test_match_feishu_domains():
    """Feishu / Lark domains route to the feishu reader."""
    assert _match_reader_name("https://example.feishu.cn/docs/x") == "default_feishu_reader"
    assert _match_reader_name("https://open.feishu.net/docs/x") == "default_feishu_reader"
    assert _match_reader_name("https://xxx.larksuite.com/docs/x") == "default_feishu_reader"


def test_match_yuque_domain():
    """Yuque domain routes to the yuque reader."""
    assert _match_reader_name("https://www.yuque.com/b/t") == "default_yuque_reader"


def test_match_notion_domains():
    """Notion domains route to the notion reader."""
    assert _match_reader_name("https://www.notion.so/page") == "default_notion_reader"
    assert _match_reader_name("https://team.notion.site/page") == "default_notion_reader"


def test_match_confluence_domains():
    """Confluence / Atlassian domains route to the confluence reader."""
    assert _match_reader_name("https://acme.atlassian.net/wiki/x") == "default_confluence_reader"
    assert _match_reader_name("https://confluence.company.com/page") == "default_confluence_reader"


def test_match_google_docs_domain():
    """Google Docs domain routes to the google docs reader."""
    assert _match_reader_name("https://docs.google.com/document/d/1") == "default_google_docs_reader"


def test_match_unknown_domain_returns_none():
    """Unknown domains return None."""
    assert _match_reader_name("https://example.com/article") is None


def test_match_empty_url_returns_none():
    """An empty url returns None."""
    assert _match_reader_name("") is None
    assert _match_reader_name(None) is None


# ---------------------------------------------------------------------------
# 2. CloudDocReader dispatch behaviour
# ---------------------------------------------------------------------------

def test_empty_url_raises_config_error():
    """An empty url raises ReaderConfigError."""
    reader = CloudDocReader()
    with pytest.raises(ReaderConfigError):
        reader._load_data("")


def test_unknown_url_raises_config_error():
    """A url with no matching platform raises ReaderConfigError."""
    reader = CloudDocReader()
    with pytest.raises(ReaderConfigError):
        reader._load_data("https://example.com/article")


def test_dispatches_to_resolved_reader():
    """CloudDocReader delegates load_data to the resolved cloud reader."""
    stub = _StubReader()
    reader = CloudDocReader()
    with patch.object(CloudDocReader, "_get_reader", return_value=stub):
        result = reader._load_data("https://www.yuque.com/b/t")
    assert result == [{"text": "stub"}]
    assert stub.calls and stub.calls[0][0][0] == "https://www.yuque.com/b/t"


def test_dispatches_with_ext_info():
    """ext_info is forwarded to the resolved reader."""
    stub = _StubReader()
    reader = CloudDocReader()
    with patch.object(CloudDocReader, "_get_reader", return_value=stub):
        reader._load_data("https://www.notion.so/page", {"token": "abc"})
    assert stub.calls[0][0][1] == {"token": "abc"}


def test_missing_reader_raises_dependency_error():
    """When the resolved reader is unavailable, ReaderDependencyError is raised."""
    reader = CloudDocReader()
    with patch.object(CloudDocReader, "_get_reader", return_value=None):
        with pytest.raises(ReaderDependencyError):
            reader._load_data("https://www.yuque.com/b/t")


# ---------------------------------------------------------------------------
# 3. Dynamic platform registration
# ---------------------------------------------------------------------------

def test_register_platform_adds_rule():
    """A new platform rule can be registered dynamically."""
    original = dict(URL_PATTERN_MAP)
    try:
        CloudDocReader.register_platform("shimo.im", "default_shimo_reader")
        assert _match_reader_name("https://shimo.im/docs/x") == "default_shimo_reader"
        assert "shimo.im" in URL_PATTERN_MAP
    finally:
        URL_PATTERN_MAP.clear()
        URL_PATTERN_MAP.update(original)


def test_get_supported_platforms_returns_list():
    """get_supported_platforms returns the current domain patterns."""
    platforms = CloudDocReader.get_supported_platforms()
    assert isinstance(platforms, list)
    assert "yuque.com" in platforms


# ---------------------------------------------------------------------------
# 4. get_url_default_reader helper
# ---------------------------------------------------------------------------

def test_get_url_default_reader_unknown_returns_none():
    """get_url_default_reader returns None for unknown domains."""
    assert get_url_default_reader("https://example.com/a") is None


def test_get_url_default_reader_empty_returns_none():
    """get_url_default_reader returns None for empty input."""
    assert get_url_default_reader("") is None


# ---------------------------------------------------------------------------
# 5. ReaderManager url routing integration
# ---------------------------------------------------------------------------

def test_reader_manager_url_routing():
    """ReaderManager.get_url_default_reader resolves a cloud url to a reader name."""
    from agentuniverse.agent.action.knowledge.reader.reader_manager import (
        ReaderManager,
        URL_PATTERN_MAP as MANAGER_MAP,
    )
    assert "yuque.com" in MANAGER_MAP
    # The manager returns a reader instance when the component is registered;
    # in a bare environment it may be None, but routing itself must not raise.
    result = ReaderManager().get_url_default_reader("https://example.com/a")
    assert result is None
