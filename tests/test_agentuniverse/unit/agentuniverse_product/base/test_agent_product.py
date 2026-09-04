# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_product.py

"""Unit tests for the AgentProduct."""

from agentuniverse_product.base.agent_product import AgentProduct
from agentuniverse.base.component.component_enum import ComponentEnum


class TestAgentProduct:
    """Test AgentProduct defaults and typed instance property."""

    def test_defaults(self):
        product = AgentProduct()
        assert product.opening_speech is None
        assert product.id is None

    def test_construction_with_fields(self):
        product = AgentProduct(id="a1", nickname="agent",
                               opening_speech="hi")
        assert product.id == "a1"
        assert product.nickname == "agent"
        assert product.opening_speech == "hi"
        assert product.component_type == ComponentEnum.PRODUCT

    def test_instance_property_defaults_to_none(self):
        assert AgentProduct(id="a1").instance is None

    def test_equality(self):
        assert AgentProduct(id="a1") == AgentProduct(id="a1")
        assert AgentProduct(id="a1") != AgentProduct(id="a2")
