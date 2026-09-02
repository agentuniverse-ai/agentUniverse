# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_context_archive_utils.py
"""Unit tests for the context archive utilities."""

from unittest.mock import patch

import pytest

from agentuniverse.base.context import context_archive_utils
from agentuniverse.base.context.context_archive_utils import (
    get_current_context_archive,
    update_context_archive,
)
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class TestContextArchiveUtils:
    """Test the archive helpers against the framework context manager."""

    @pytest.fixture(autouse=True)
    def shared_manager(self):
        """Patch the module-level manager and clear the archive per test."""
        manager = FrameworkContextManager()
        manager.del_context("context_archive", force=True)
        with patch.object(
            context_archive_utils, "FrameworkContextManager", return_value=manager
        ):
            yield manager
        manager.del_context("context_archive", force=True)

    def test_get_returns_dict(self, shared_manager):
        """The helper always yields a dict."""
        assert get_current_context_archive() == {}
        assert isinstance(get_current_context_archive(), dict)

    def test_get_sees_preexisting_archive(self, shared_manager):
        """A non-empty stored archive is returned unchanged."""
        seed = {"seed": {"data": 1, "description": "s"}}
        shared_manager.set_context("context_archive", seed)
        assert get_current_context_archive() is seed

    def test_get_initializes_missing_archive(self, shared_manager):
        """A missing archive is initialized as an empty dict in the context."""
        assert not shared_manager.is_context_exist("context_archive")
        assert get_current_context_archive() == {}
        assert shared_manager.get_context("context_archive") == {}

    def test_update_appends_record(self, shared_manager):
        """update_context_archive appends data and description to the archive."""
        shared_manager.set_context(
            "context_archive", {"seed": {"data": 1, "description": "s"}}
        )
        update_context_archive("retrieval", {"docs": 3}, "top-3 docs")
        archive = shared_manager.get_context("context_archive")
        assert archive["retrieval"] == {
            "data": {"docs": 3},
            "description": "top-3 docs",
        }

    def test_update_overwrites_same_name(self, shared_manager):
        """Updating an existing name replaces its previous record."""
        shared_manager.set_context("context_archive", {"base": {"data": 0}})
        update_context_archive("step", {"v": 1}, "first")
        update_context_archive("step", {"v": 2}, "second")
        record = shared_manager.get_context("context_archive")["step"]
        assert record == {"data": {"v": 2}, "description": "second"}

    def test_multiple_records_coexist(self, shared_manager):
        """Distinct names are archived side by side."""
        shared_manager.set_context("context_archive", {"base": {"data": 0}})
        update_context_archive("a", 1, "record a")
        update_context_archive("b", 2, "record b")
        archive = get_current_context_archive()
        assert set(archive.keys()) == {"base", "a", "b"}
        assert archive["a"] == {"data": 1, "description": "record a"}
        assert archive["b"] == {"data": 2, "description": "record b"}
