# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:25
# @Author  : yuewang
# @FileName: test_llm_manager.py
"""Unit tests for LLMManager."""

import sys
import types
from types import SimpleNamespace

import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.llm.llm_manager import LLMManager


class DummyLLM(ComponentBase):
    """Minimal LLM component for registration tests."""
    name: str = None
    component_type: ComponentEnum = ComponentEnum.LLM

    def initialize_by_component_configer(self, configer):
        return self


class AppConfigerWithLLMs(AppConfiger):
    """AppConfiger exposing a configurable llm_configer_map."""

    def __init__(self):
        super().__init__()
        self._llm_map = {}

    @property
    def llm_configer_map(self):
        return self._llm_map


@pytest.fixture
def manager():
    """Return the LLMManager singleton with a bare app configer."""
    app = AppConfigerWithLLMs()
    ApplicationConfigManager().app_configer = app
    return LLMManager()


class TestLLMManager:
    """Test LLMManager lookup behavior."""

    def test_singleton(self, manager):
        assert manager is LLMManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.LLM

    def test_register_and_get(self, manager):
        llm = DummyLLM(name='l1')
        manager.register('app.llm.l1', llm)
        assert manager.get_instance_obj('l1', appname='app', new_instance=False) is llm

    def test_unknown_name_returns_none(self, manager):
        assert manager.get_instance_obj('absent_llm_xyz', appname='app') is None

    def test_dynamic_creation_from_configer(self, manager, monkeypatch):
        module = types.ModuleType('du_llm_mod')
        module.DummyLLM = DummyLLM
        monkeypatch.setitem(sys.modules, 'du_llm_mod', module)
        app = ApplicationConfigManager().app_configer
        app._llm_map['dyn_llm'] = SimpleNamespace(
            meta_class='du_llm_mod.DummyLLM',
            configer=SimpleNamespace(path='p'))
        instance = manager.get_instance_obj('dyn_llm', appname='app', new_instance=False)
        assert isinstance(instance, DummyLLM)
        assert instance.component_config_path == 'p'
