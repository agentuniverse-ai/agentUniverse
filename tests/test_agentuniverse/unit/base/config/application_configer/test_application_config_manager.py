# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_application_config_manager.py

"""Unit tests for the ApplicationConfigManager singleton."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager


@pytest.fixture
def manager():
    return ApplicationConfigManager()


class TestApplicationConfigManager:
    """Test app configer storage semantics."""

    def test_singleton_identity(self):
        assert ApplicationConfigManager() is ApplicationConfigManager()

    def test_unset_raises_value_error(self, manager):
        manager.app_configer = None
        with pytest.raises(ValueError, match="not set"):
            manager.app_configer

    def test_set_and_get(self, manager):
        app_configer = SimpleNamespace(base_info_appname="demo")
        manager.app_configer = app_configer
        assert manager.app_configer is app_configer
        manager.app_configer = None
