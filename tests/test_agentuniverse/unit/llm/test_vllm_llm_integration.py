#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests completing the vLLM LLM integration.

The vLLM component itself (VLLMOpenAIStyleLLM) is covered by
``test_vllm_openai_style_llm.py``. These tests cover the remaining pieces of
the integration added for issue #250: the extended per-model context-length
table, the environment-variable wiring (VLLM_API_BASE / VLLM_API_KEY), the
shipped buildin example configurations and the guidebook list entries.

All tests are fully offline: no network access and no ``vllm`` package import
is required (the component talks to a vLLM server through the OpenAI HTTP
API, it never imports the ``vllm`` runtime).
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from agentuniverse.llm.default.vllm_openai_style_llm import (
    VLLM_MAX_CONTEXT_LENGTH,
    VLLMOpenAIStyleLLM,
)

REPO_ROOT = Path(__file__).resolve().parents[4]

BUILDIN_YAMLS = [
    Path('examples/sample_apps/toolkit_demo_app/intelligence/agentic/llm/buildin/vllm/vllm_llama_3_1_8b.yaml'),
    Path('examples/sample_apps/toolkit_demo_app/intelligence/agentic/llm/buildin/vllm/vllm_qwen_2_5_7b.yaml'),
    Path('examples/sample_standard_app/intelligence/agentic/llm/buildin/vllm/vllm_llama_3_1_8b.yaml'),
    Path('examples/sample_standard_app/intelligence/agentic/llm/buildin/vllm/vllm_llama_3_1_70b.yaml'),
    Path('examples/sample_standard_app/intelligence/agentic/llm/buildin/vllm/vllm_qwen_2_5_7b.yaml'),
]

EXPECTED_META_CLASS = 'agentuniverse.llm.default.vllm_openai_style_llm.VLLMOpenAIStyleLLM'


class TestVllmContextLengthTable(unittest.TestCase):
    """Tests for the extended VLLM_MAX_CONTEXT_LENGTH table."""

    def test_table_entries_are_positive_integers(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in VLLM_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_newly_added_models(self) -> None:
        """Models newly added to the table resolve to their documented window."""
        expected = {
            'meta-llama/Llama-3.3-70B-Instruct': 131072,
            'meta-llama/Meta-Llama-3-8B-Instruct': 8192,
            'meta-llama/Meta-Llama-3-70B-Instruct': 8192,
            'Qwen/Qwen2.5-14B-Instruct': 32768,
            'Qwen/Qwen2.5-32B-Instruct': 32768,
            'Qwen/Qwen3-8B': 32768,
            'Qwen/Qwen3-32B': 32768,
            'google/gemma-2-9b-it': 8192,
        }
        for model_name, length in expected.items():
            self.assertEqual(VLLM_MAX_CONTEXT_LENGTH.get(model_name), length,
                             f'Context length mismatch for {model_name}')
            llm = VLLMOpenAIStyleLLM(model_name=model_name)
            self.assertEqual(llm.max_context_length(), length,
                             f'max_context_length mismatch for {model_name}')

    def test_unknown_model_falls_back_to_default(self) -> None:
        """Models missing from the table fall back to the default entry."""
        llm = VLLMOpenAIStyleLLM(model_name='unknown-org/unknown-model')
        self.assertEqual(llm.max_context_length(), VLLM_MAX_CONTEXT_LENGTH['default'])

    def test_explicit_max_context_length_wins(self) -> None:
        """A YAML-configured max_context_length overrides the table lookup."""
        llm = VLLMOpenAIStyleLLM(model_name='meta-llama/Llama-3.1-8B-Instruct')
        self.assertEqual(llm.max_context_length(), 131072)
        llm._max_context_length = 32768
        self.assertEqual(llm.max_context_length(), 32768)


class TestVllmEnvironmentWiring(unittest.TestCase):
    """Tests for the VLLM_API_BASE / VLLM_API_KEY environment wiring."""

    def test_defaults_without_environment(self) -> None:
        """Without env vars the local vLLM endpoint and the EMPTY key are used."""
        env = {k: v for k, v in os.environ.items()
               if k not in ('VLLM_API_BASE', 'VLLM_API_KEY')}
        with patch.dict(os.environ, env, clear=True):
            llm = VLLMOpenAIStyleLLM(model_name='meta-llama/Llama-3.1-8B-Instruct')
        self.assertEqual(llm.api_base, 'http://localhost:8000/v1')
        self.assertEqual(llm.api_key, 'EMPTY')

    def test_environment_overrides(self) -> None:
        """VLLM_API_BASE and VLLM_API_KEY override the local defaults."""
        env = dict(os.environ)
        env['VLLM_API_BASE'] = 'http://vllm.example.com:9000/v1'
        env['VLLM_API_KEY'] = 'secret-token'
        with patch.dict(os.environ, env, clear=True):
            llm = VLLMOpenAIStyleLLM(model_name='meta-llama/Llama-3.1-8B-Instruct')
        self.assertEqual(llm.api_base, 'http://vllm.example.com:9000/v1')
        self.assertEqual(llm.api_key, 'secret-token')


class TestVllmBuildinConfigs(unittest.TestCase):
    """Tests for the shipped vLLM buildin example configurations."""

    def test_buildin_yamls_are_valid(self) -> None:
        """Every buildin yaml parses and points at the vLLM component class."""
        self.assertTrue(len(BUILDIN_YAMLS) > 0)
        for rel_path in BUILDIN_YAMLS:
            abs_path = REPO_ROOT / rel_path
            self.assertTrue(abs_path.is_file(), f'missing buildin config {rel_path}')
            with open(abs_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.assertIsInstance(config, dict, f'{rel_path} is not a mapping')
            for key in ('name', 'description', 'model_name', 'api_base', 'meta_class'):
                self.assertIn(key, config, f'{key} missing in {rel_path}')
            self.assertEqual(config['meta_class'], EXPECTED_META_CLASS,
                             f'unexpected meta_class in {rel_path}')

    def test_buildin_model_context_lengths_agree_with_table(self) -> None:
        """Buildin configs set max_context_length consistently with the table."""
        for rel_path in BUILDIN_YAMLS:
            with open(REPO_ROOT / rel_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            model_name = config['model_name']
            expected = VLLM_MAX_CONTEXT_LENGTH.get(
                model_name, VLLM_MAX_CONTEXT_LENGTH['default'])
            self.assertEqual(config.get('max_context_length'), expected,
                             f'{rel_path}: max_context_length should be {expected}')


class TestVllmGuidebookEntries(unittest.TestCase):
    """Tests for the guidebook usage docs and list entries."""

    LIST_EN = REPO_ROOT / 'docs/guidebook/en/In-Depth_Guides/Components/LLMs/0.List_Of_LLMs.md'
    LIST_ZH = REPO_ROOT / 'docs/guidebook/zh/In-Depth_Guides/组件列表/模型列表/模型列表.md'
    DOC_EN = REPO_ROOT / 'docs/guidebook/en/In-Depth_Guides/Components/LLMs/VLLM_LLM_Use.md'
    DOC_ZH = REPO_ROOT / 'docs/guidebook/zh/In-Depth_Guides/组件列表/模型列表/vLLM使用.md'

    def test_usage_docs_exist(self) -> None:
        """English and Chinese vLLM usage docs must ship with the repo."""
        for doc in (self.DOC_EN, self.DOC_ZH):
            self.assertTrue(doc.is_file(), f'missing usage doc {doc}')
            content = doc.read_text(encoding='utf-8')
            self.assertIn('VLLMOpenAIStyleLLM', content)

    def test_list_entries_exist(self) -> None:
        """Both shared LLM lists must link to the vLLM usage docs."""
        en = self.LIST_EN.read_text(encoding='utf-8')
        self.assertIn('[vLLM](VLLM_LLM_Use.md)', en)
        zh = self.LIST_ZH.read_text(encoding='utf-8')
        self.assertIn('[vLLM](vLLM使用.md)', zh)


class TestVllmPackageIsolation(unittest.TestCase):
    """The component must work without the vllm runtime package installed."""

    def test_module_import_does_not_pull_vllm_runtime(self) -> None:
        """Importing the component module must not import the vllm package."""
        sys.modules.pop('vllm', None)
        importlib.import_module('agentuniverse.llm.default.vllm_openai_style_llm')
        self.assertNotIn('vllm', sys.modules)


if __name__ == '__main__':
    unittest.main()
