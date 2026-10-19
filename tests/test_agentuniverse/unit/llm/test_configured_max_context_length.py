# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""A configured ``max_context_length`` must win over the built-in model table.

``LLM._initialize_by_component_configer`` stores the ``max_context_length`` key
of an LLM yaml in ``_max_context_length``, and ``prompt_util.process_llm_token``
sizes the agent prompt budget from ``llm.max_context_length() - max_tokens``.
An LLM class that answers from its model table alone silently ignores the
configured value, so the prompt is truncated to the table entry instead.
"""

import unittest

from agentuniverse.base.config.component_configer.configers.llm_configer import (
    LLMConfiger,
)
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.deep_seek_openai_style_llm import DefaultDeepSeekLLM
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM
from agentuniverse.llm.default.zhipu_openai_style_llm import DefaultZhiPuLLM

# (class, model_name, max_context_length configured in the yaml)
# The OpenAI entries mirror the shipped examples/sample_standard_app LLM yamls.
# Every configured value differs from the class's model table entry, so each
# case fails while the table entry is answered instead of the configuration.
CASES = [
    (DefaultOpenAILLM, 'o3-mini', 2000000),
    (DefaultOpenAILLM, 'o1', 200000),
    (DefaultOpenAILLM, 'o1-mini', 128000),
    (DefaultOpenAILLM, 'gpt-4o-mini', 128000),
    (DefaultDeepSeekLLM, 'deepseek-reasoner', 65792),
    (DefaultZhiPuLLM, 'GLM-4-Air', 32768),
]

# model name -> the entry of the class's own table, used to pin the fallback.
TABLE_ENTRIES = [
    (DefaultOpenAILLM, 'gpt-4o', 128000),
    (DefaultDeepSeekLLM, 'deepseek-chat', 64000),
    (DefaultZhiPuLLM, 'GLM-4-Air', 128000),
]


def _llm_from_yaml_values(llm_class, **value):
    """Build an LLM the way the component bootstrap does, from yaml values."""
    configer = Configer()
    configer.value = value
    llm = llm_class()
    llm.initialize_by_component_configer(LLMConfiger().load_by_configer(configer))
    return llm


class ConfiguredMaxContextLengthTest(unittest.TestCase):
    """The yaml value must be reported, not a table entry for the model name."""

    def test_configured_value_is_used(self):
        for llm_class, model_name, configured in CASES:
            with self.subTest(llm=llm_class.__name__, model_name=model_name):
                llm = _llm_from_yaml_values(
                    llm_class, name=model_name, model_name=model_name,
                    max_tokens=2000, max_context_length=configured)
                self.assertEqual(llm._max_context_length, configured)
                self.assertEqual(llm.max_context_length(), configured)

    def test_table_is_used_when_nothing_is_configured(self):
        """The fallback must stay intact for LLMs configured without the key."""
        for llm_class, model_name, table_entry in TABLE_ENTRIES:
            with self.subTest(llm=llm_class.__name__, model_name=model_name):
                llm = _llm_from_yaml_values(
                    llm_class, name=model_name, model_name=model_name, max_tokens=2000)
                self.assertIsNone(llm._max_context_length)
                self.assertEqual(llm.max_context_length(), table_entry)

    def test_prompt_budget_follows_the_configured_value(self):
        """The budget process_llm_token derives must not collapse to the table entry."""
        llm = _llm_from_yaml_values(
            DefaultOpenAILLM, name='o3-mini', model_name='o3-mini',
            max_tokens=2000, max_context_length=2000000)
        self.assertEqual(llm.max_context_length() - llm.max_tokens, 1998000)


if __name__ == "__main__":
    unittest.main()
