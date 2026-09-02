# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_agent_model.py
"""Unit tests for the AgentModel pydantic model."""

import pytest

from agentuniverse.agent.agent_model import AgentModel


class TestAgentModel:
    """Test AgentModel defaults and llm_params derivation."""

    def test_default_attributes_are_empty_dicts(self):
        model = AgentModel()
        assert model.info == {}
        assert model.profile == {}
        assert model.action == {}

    def test_llm_params_skips_name_and_prompt_processor(self):
        model = AgentModel(profile={
            "llm_model": {"name": "gpt-4o", "prompt_processor": "x", "temperature": 0.2}
        })
        params = model.llm_params()
        assert params == {"temperature": 0.2}

    def test_llm_params_maps_model_name_to_model_key(self):
        model = AgentModel(profile={"llm_model": {"name": "demo", "model_name": "deepseek"}})
        params = model.llm_params()
        assert params == {"model": "deepseek"}

    def test_llm_params_keeps_other_fields(self):
        model = AgentModel(profile={
            "llm_model": {"name": "demo", "max_tokens": 100, "temperature": 0.5}
        })
        params = model.llm_params()
        assert params == {"max_tokens": 100, "temperature": 0.5}

    def test_attributes_are_independent_between_instances(self):
        first = AgentModel(info={"a": 1})
        second = AgentModel()
        assert first.info == {"a": 1}
        assert second.info == {}
