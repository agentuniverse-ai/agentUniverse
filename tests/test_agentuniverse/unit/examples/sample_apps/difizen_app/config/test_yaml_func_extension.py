# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the YamlFuncExtension api-key loader."""

from examples.sample_apps.difizen_app.config.yaml_func_extension import LLMModelEnum, YamlFuncExtension


class TestYamlFuncExtension:
    """Test env-based api key loading."""

    def test_loads_known_model_keys(self, monkeypatch):
        ext = YamlFuncExtension()
        monkeypatch.setenv("DASHSCOPE_API_KEY", "qwen-key")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-key")
        monkeypatch.setenv("OPENAI_API_KEY", "oa-key")
        assert ext.load_api_key("qwen") == "qwen-key"
        assert ext.load_api_key("deepseek") == "ds-key"
        assert ext.load_api_key("openai") == "oa-key"

    def test_unknown_model_returns_empty(self):
        assert YamlFuncExtension().load_api_key("unknown_model") == ""

    def test_model_enum_values(self):
        assert LLMModelEnum.QWEN.value == "qwen"
        assert LLMModelEnum.DEEPSEEK.value == "deepseek"
        assert LLMModelEnum.GEMINI.value == "gemini"
