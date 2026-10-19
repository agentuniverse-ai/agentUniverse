# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_yaml_func_extension.py
"""Unit tests for the YamlFuncExtension YAML @FUNC helper.

The extension resolves an API key for a model name from a fixed environment
variable mapping, so its behavior can be tested without any framework setup.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[6]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[6]
                       / 'examples' / 'sample_standard_app' / 'config'))

from yaml_func_extension import LLMModelEnum, YamlFuncExtension

MODEL_ENV_MAP = [
    ('qwen', 'DASHSCOPE_API_KEY'),
    ('deepseek', 'DEEPSEEK_API_KEY'),
    ('openai', 'OPENAI_API_KEY'),
    ('claude', 'ANTHROPIC_API_KEY'),
    ('kimi', 'KIMI_API_KEY'),
    ('zhipu', 'ZHIPU_API_KEY'),
    ('baichuan', 'BAICHUAN_API_KEY'),
    ('gemini', 'GEMINI_API_KEY'),
    ('wenxin', 'QIANFAN_AK'),
]


class TestLLMModelEnum:
    """Test the LLMModelEnum enum."""

    def test_enum_values(self):
        assert LLMModelEnum.QWEN.value == 'qwen'
        assert LLMModelEnum.DEEPSEEK.value == 'deepseek'
        assert LLMModelEnum.OPENAI.value == 'openai'
        assert LLMModelEnum.CLAUDE.value == 'claude'
        assert LLMModelEnum.WENXIN.value == 'wenxin'

    def test_enum_covers_all_models(self):
        assert len(LLMModelEnum) == 9


class TestYamlFuncExtension:
    """Test the YamlFuncExtension API key loader."""

    @pytest.fixture
    def extension(self) -> YamlFuncExtension:
        return YamlFuncExtension()

    @pytest.mark.parametrize('model_name,env_key', MODEL_ENV_MAP)
    def test_load_api_key_reads_expected_env_var(self, monkeypatch, extension,
                                                 model_name, env_key):
        expected = f'sk-test-{model_name}'
        monkeypatch.setenv(env_key, expected)
        assert extension.load_api_key(model_name) == expected

    def test_known_model_without_env_returns_none(self, monkeypatch, extension):
        monkeypatch.delenv('DASHSCOPE_API_KEY', raising=False)
        assert extension.load_api_key('qwen') is None

    def test_unknown_model_returns_empty_string(self, extension):
        assert extension.load_api_key('unknown-model') == ''

    def test_load_api_key_returns_string(self, monkeypatch, extension):
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-str-test')
        assert isinstance(extension.load_api_key('openai'), str)
