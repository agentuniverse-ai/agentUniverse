# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_yaml_func_extension.py

"""Unit tests for the YamlFuncExtension example config helper."""

import os
import unittest
from unittest.mock import patch

from examples.third_party_examples.apps.app_with_goole_search_tool.config.yaml_func_extension import (
    LLMModelEnum,
    YamlFuncExtension,
)


class TestYamlFuncExtension(unittest.TestCase):
    """Unit tests for YamlFuncExtension."""

    def setUp(self):
        """Set up test fixtures."""
        self.extension = YamlFuncExtension()

    def test_instantiation(self):
        """The extension can be instantiated without arguments."""
        self.assertIsInstance(YamlFuncExtension(), YamlFuncExtension)

    def test_unknown_model_returns_empty_string(self):
        """An unknown model name yields an empty string."""
        self.assertEqual(self.extension.load_api_key("unknown_model"), "")

    def test_missing_env_returns_none(self):
        """Missing API key env vars resolve to None."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DASHSCOPE_API_KEY", None)
            self.assertIsNone(YamlFuncExtension().load_api_key("qwen"))

    def test_qwen_reads_dashscope_env(self):
        """'qwen' reads the DASHSCOPE_API_KEY variable."""
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "key-qwen"}, clear=False):
            self.assertEqual(YamlFuncExtension().load_api_key("qwen"), "key-qwen")

    def test_deepseek_reads_env(self):
        """'deepseek' reads the DEEPSEEK_API_KEY variable."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "key-ds"}, clear=False):
            self.assertEqual(YamlFuncExtension().load_api_key("deepseek"), "key-ds")

    def test_openai_reads_env(self):
        """'openai' reads the OPENAI_API_KEY variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "key-oa"}, clear=False):
            self.assertEqual(YamlFuncExtension().load_api_key("openai"), "key-oa")

    def test_model_enum_values(self):
        """LLMModelEnum maps each member to the expected string value."""
        expected = {
            "QWEN": "qwen",
            "DEEPSEEK": "deepseek",
            "OPENAI": "openai",
            "CLAUDE": "claude",
            "KIMI": "kimi",
            "ZHIPU": "zhipu",
            "BAICHUAN": "baichuan",
            "GEMINI": "gemini",
            "WENXIN": "wenxin",
        }
        self.assertEqual({m.name: m.value for m in LLMModelEnum}, expected)


if __name__ == "__main__":
    unittest.main()
