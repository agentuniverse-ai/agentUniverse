# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the ComponentConfigerUtil utility class."""

import pytest

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger


class TestComponentConfigerUtil:
    """Tests for the ComponentConfigerUtil class methods."""

    def test_get_component_config_clz_by_type_known_types(self):
        assert ComponentConfigerUtil.get_component_config_clz_by_type(ComponentEnum.AGENT) is AgentConfiger
        assert ComponentConfigerUtil.get_component_config_clz_by_type(ComponentEnum.LLM) is LLMConfiger
        assert ComponentConfigerUtil.get_component_config_clz_by_type(ComponentEnum.MEMORY) is MemoryConfiger

    def test_get_component_config_clz_by_type_unknown_type_raises(self):
        with pytest.raises(Exception):
            ComponentConfigerUtil.get_component_config_clz_by_type(ComponentEnum.PRODUCT)

    def test_get_component_config_clz_is_component_configer_subclass(self):
        clz = ComponentConfigerUtil.get_component_config_clz_by_type(ComponentEnum.AGENT)
        assert issubclass(clz, ComponentConfiger)

    def test_get_component_manager_clz_by_type_known_type(self):
        assert ComponentConfigerUtil.get_component_manager_clz_by_type(ComponentEnum.AGENT) is AgentManager

    def test_get_component_manager_clz_by_type_unknown_type_returns_none(self):
        assert ComponentConfigerUtil.get_component_manager_clz_by_type(ComponentEnum.PRODUCT) is None

    def test_get_component_object_clz_by_metadata(self):
        configer = ComponentConfiger()
        configer.metadata_module = "agentuniverse.base.component.component_enum"
        configer.metadata_class = "ComponentEnum"
        clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(configer)
        assert clz is ComponentEnum
