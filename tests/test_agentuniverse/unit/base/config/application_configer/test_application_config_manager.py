# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_application_config_manager.py
"""Unit tests for ApplicationConfigManager."""

import pytest

from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)


class TestApplicationConfigManager:
    """Test the singleton configuration manager."""

    @pytest.fixture(autouse=True)
    def reset_manager(self):
        """Reset the singleton's private app configer around each test."""
        manager = ApplicationConfigManager()
        manager._ApplicationConfigManager__app_configer = None
        yield
        manager._ApplicationConfigManager__app_configer = None

    def test_singleton_returns_same_instance(self):
        """Repeated construction returns the same managed instance."""
        first = ApplicationConfigManager()
        second = ApplicationConfigManager()
        assert first is second

    def test_app_configer_unset_raises(self):
        """Reading app_configer before it is set raises ValueError."""
        with pytest.raises(ValueError, match="AppConfiger object is not set"):
            _ = ApplicationConfigManager().app_configer

    def test_setter_then_getter_roundtrip(self):
        """A stored configer is returned unchanged by the property."""
        manager = ApplicationConfigManager()
        sentinel = object()
        manager.app_configer = sentinel
        assert manager.app_configer is sentinel

    def test_setter_replaces_previous_value(self):
        """Assigning again overwrites the previously stored configer."""
        manager = ApplicationConfigManager()
        first = object()
        second = object()
        manager.app_configer = first
        manager.app_configer = second
        assert manager.app_configer is second
        assert manager.app_configer is not first
