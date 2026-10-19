# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the LLMConfiger component configer."""

import pytest

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer


def _build_configer(value: dict) -> Configer:
    configer = Configer()
    configer.value = value
    return configer


class TestLLMConfiger:
    """Tests for the LLMConfiger class."""

    def test_properties_default_to_none(self):
        configer = LLMConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.model_name is None
        assert configer.temperature is None
        assert configer.request_timeout is None
        assert configer.max_tokens is None
        assert configer.max_retries is None
        assert configer.streaming is None
        assert configer.ext_info is None
        assert configer.max_content_length is None
        assert configer.tracing is None

    def test_load_by_configer_populates_all_fields(self):
        configer = _build_configer({
            "name": "test_llm",
            "description": "a test llm",
            "model_name": "gpt-4o",
            "temperature": 0.7,
            "request_timeout": 60,
            "max_tokens": 2048,
            "max_retries": 3,
            "streaming": True,
            "ext_info": {"key": "value"},
            "max_context_length": 8192,
            "tracing": True,
        })
        llm_configer = LLMConfiger().load_by_configer(configer)
        assert llm_configer.name == "test_llm"
        assert llm_configer.description == "a test llm"
        assert llm_configer.model_name == "gpt-4o"
        assert llm_configer.temperature == 0.7
        assert llm_configer.request_timeout == 60
        assert llm_configer.max_tokens == 2048
        assert llm_configer.max_retries == 3
        assert llm_configer.streaming is True
        assert llm_configer.ext_info == {"key": "value"}
        assert llm_configer.max_content_length == 8192
        assert llm_configer.tracing is True

    def test_load_by_configer_missing_keys_stay_none(self):
        configer = _build_configer({"name": "partial_llm"})
        llm_configer = LLMConfiger().load_by_configer(configer)
        assert llm_configer.name == "partial_llm"
        assert llm_configer.model_name is None
        assert llm_configer.temperature is None

    def test_load_uses_constructor_configer(self):
        configer = _build_configer({"name": "ctor_llm", "model_name": "gpt-4o"})
        llm_configer = LLMConfiger(configer).load()
        assert llm_configer.name == "ctor_llm"
        assert llm_configer.model_name == "gpt-4o"

    def test_load_returns_self(self):
        configer = _build_configer({"name": "self_llm"})
        llm_configer = LLMConfiger()
        assert llm_configer.load_by_configer(configer) is llm_configer
        assert llm_configer.load() is llm_configer

    def test_load_without_configer_raises(self):
        with pytest.raises(Exception):
            LLMConfiger().load()
