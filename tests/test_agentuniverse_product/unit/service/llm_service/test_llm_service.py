# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:27
# @Author  : Yue Wang
# @FileName: test_llm_service.py
"""Unit tests for the LLMService in agentuniverse_product."""

from unittest.mock import patch

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.constant.llm_constant import LLM_MODEL_NAME
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.llm_service.llm_service import LLMService
from agentuniverse_product.service.model.llm_dto import LlmDTO


class MockLLM:
    """Minimal stand-in for an LLM component instance."""

    def __init__(self, temperature=None):
        self.temperature = temperature


def build_product(product_id, nickname, product_type, temperature=None):
    """Build a Product whose underlying instance is a MockLLM."""
    product = Product(id=product_id, nickname=nickname, type=product_type)
    product._instance = MockLLM(temperature=temperature)
    return product


def mock_product_list(products):
    """Return a patcher replacing ProductManager.get_instance_obj_list."""
    return patch.object(
        ProductManager(),
        'get_instance_obj_list',
        return_value=products,
    )


def test_get_llm_list_filters_llm_products():
    llm_product = build_product('demo_llm', 'demo', ComponentEnum.LLM.value, temperature=0.7)
    agent_product = build_product('demo_agent', 'agent', ComponentEnum.AGENT.value)
    with mock_product_list([llm_product, agent_product]):
        result = LLMService.get_llm_list()
    assert len(result) == 1
    dto = result[0]
    assert isinstance(dto, LlmDTO)
    assert dto.id == 'demo_llm'
    assert dto.nickname == 'demo'
    assert dto.temperature == 0.7
    assert dto.model_name == LLM_MODEL_NAME['demo_llm']


def test_get_llm_list_returns_empty_for_no_products():
    with mock_product_list([]):
        assert LLMService.get_llm_list() == []


def test_get_llm_list_skips_non_llm_products():
    agent_product = build_product('demo_agent', 'agent', ComponentEnum.AGENT.value)
    tool_product = build_product('demo_tool', 'tool', ComponentEnum.TOOL.value)
    with mock_product_list([agent_product, tool_product]):
        assert LLMService.get_llm_list() == []


def test_get_llm_list_unknown_model_name_defaults_to_empty():
    llm_product = build_product('unknown_llm', 'unknown', ComponentEnum.LLM.value)
    with mock_product_list([llm_product]):
        result = LLMService.get_llm_list()
    assert len(result) == 1
    assert result[0].model_name == []


def test_get_llm_list_preserves_none_temperature():
    llm_product = build_product('openai_llm', None, ComponentEnum.LLM.value, temperature=None)
    with mock_product_list([llm_product]):
        result = LLMService.get_llm_list()
    assert len(result) == 1
    assert result[0].nickname is None
    assert result[0].temperature is None
