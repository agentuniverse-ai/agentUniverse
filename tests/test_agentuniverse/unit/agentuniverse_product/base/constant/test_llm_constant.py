# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_llm_constant.py

"""Unit tests for the LLM model name constant map."""

from agentuniverse_product.base.constant.llm_constant import LLM_MODEL_NAME


class TestLlmModelName:
    """Test the LLM_MODEL_NAME constant mapping."""

    def test_expected_keys_present(self):
        for key in ["demo_llm", "openai_llm", "qwen_llm", "wenxin_llm",
                    "kimi_llm", "deepseek_llm", "baichuan_llm"]:
            assert key in LLM_MODEL_NAME

    def test_all_lists_non_empty(self):
        for name_list in LLM_MODEL_NAME.values():
            assert len(name_list) > 0

    def test_no_duplicates_in_list(self):
        for name_list in LLM_MODEL_NAME.values():
            assert len(name_list) == len(set(name_list))

    def test_default_variants_share_models(self):
        assert set(LLM_MODEL_NAME["openai_llm"]) == set(
            LLM_MODEL_NAME["default_openai_llm"])
        assert set(LLM_MODEL_NAME["qwen_llm"]) == set(
            LLM_MODEL_NAME["default_qwen_llm"])

    def test_common_models_included(self):
        assert "gpt-4o" in LLM_MODEL_NAME["openai_llm"]
        assert "deepseek-chat" in LLM_MODEL_NAME["deepseek_llm"]
