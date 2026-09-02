# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:10
# @Author  : kaichuan
# @FileName: test_agent_configer.py
"""Unit tests for AgentConfiger in base.config.component_configer.configers."""

import pytest

from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.config.configer import Configer


def _configer_with(value):
    """Build a Configer whose value is the given dict."""
    configer = Configer()
    configer.value = value
    return configer


FULL_CONFIG = {
    "name": "demo_agent",
    "description": "A demo agent",
    "metadata": {"type": "AGENT", "module": "pkg.demo", "class": "DemoAgent"},
    "info": {"note": "info-data"},
    "profile": {"model": "qwen"},
    "plan": {"max_step": 3},
    "memory": {"type": "RAM"},
    "action": {"knowledge": ["kb1"]},
}


class TestAgentConfiger:
    """Test AgentConfiger defaults and configuration loading."""

    def test_default_sections_are_empty_dicts(self):
        """A fresh AgentConfiger exposes empty dicts for all sections."""
        configer = AgentConfiger()
        assert configer.info == {}
        assert configer.profile == {}
        assert configer.plan == {}
        assert configer.memory == {}
        assert configer.action == {}

    def test_load_returns_same_instance(self):
        """load() is a fluent operation returning the same object."""
        configer = AgentConfiger(_configer_with(FULL_CONFIG))
        assert configer.load() is configer

    def test_load_populates_sections(self):
        """All configured sections are available after load()."""
        configer = AgentConfiger(_configer_with(FULL_CONFIG)).load()
        assert configer.info == {"note": "info-data"}
        assert configer.profile == {"model": "qwen"}
        assert configer.plan == {"max_step": 3}
        assert configer.memory == {"type": "RAM"}
        assert configer.action == {"knowledge": ["kb1"]}

    def test_missing_sections_stay_empty(self):
        """Sections absent from the config remain empty dicts."""
        value = dict(FULL_CONFIG)
        del value["action"]
        del value["plan"]
        configer = AgentConfiger(_configer_with(value)).load()
        assert configer.action == {}
        assert configer.plan == {}
        assert configer.memory == {"type": "RAM"}

    def test_name_and_description_attributes(self):
        """Base config keys such as name are copied onto the instance."""
        configer = AgentConfiger(_configer_with(FULL_CONFIG)).load()
        assert configer.name == "demo_agent"
        assert configer.description == "A demo agent"

    def test_metadata_parsed(self):
        """metadata type/module/class are parsed from the config value."""
        configer = AgentConfiger(_configer_with(FULL_CONFIG)).load()
        assert configer.metadata_type == "AGENT"
        assert configer.metadata_module == "pkg.demo"
        assert configer.metadata_class == "DemoAgent"

    def test_load_by_configer_replaces_configer(self):
        """load_by_configer binds the passed Configer to the instance."""
        configer = AgentConfiger()
        other = _configer_with(FULL_CONFIG)
        result = configer.load_by_configer(other)
        assert result is configer
        assert configer.configer is other
