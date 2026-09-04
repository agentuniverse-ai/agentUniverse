# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_configer.py

"""Unit tests for the AgentConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.agent_configer import \
    AgentConfiger


class TestAgentConfiger:
    """Test agent configuration loading."""

    def test_defaults(self):
        configer = AgentConfiger()
        assert configer.info == {}
        assert configer.profile == {}
        assert configer.plan == {}
        assert configer.memory == {}
        assert configer.action == {}

    def test_load_by_configer(self):
        configer = AgentConfiger()
        value = {"info": {"name": "agent1"},
                 "profile": {"model": "gpt"},
                 "metadata": {"type": "agent", "module": "m", "class": "C"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.info == {"name": "agent1"}
        assert configer.profile == {"model": "gpt"}
        assert configer.plan == {}
        assert configer.metadata_type == "agent"

    def test_missing_sections_keep_defaults(self):
        configer = AgentConfiger()
        value = {"metadata": {"type": "agent", "module": "m", "class": "C"}}
        configer.load_by_configer(SimpleNamespace(value=value, path="x.yaml"))
        assert configer.info == {}
        assert configer.action == {}
