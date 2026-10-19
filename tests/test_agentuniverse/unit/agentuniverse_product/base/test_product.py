# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_product.py

"""Unit tests for the Product base class."""

from agentuniverse_product.base.product import Product
from agentuniverse.base.component.component_enum import ComponentEnum


class TestProduct:
    """Test Product defaults and instance property."""

    def test_defaults(self):
        product = Product()
        assert product.id is None
        assert product.nickname is None
        assert product.type is None
        assert product.avatar is None
        assert product.description is None
        assert product.component_type == ComponentEnum.PRODUCT

    def test_construction_with_fields(self):
        product = Product(id="p1", nickname="product", type="AGENT",
                          avatar="a.png", description="desc")
        assert product.id == "p1"
        assert product.nickname == "product"
        assert product.type == "AGENT"
        assert product.description == "desc"

    def test_instance_property_defaults_to_none(self):
        assert Product(id="p1").instance is None

    def test_equality(self):
        assert Product(id="p1") == Product(id="p1")
        assert Product(id="p1") != Product(id="p2")
