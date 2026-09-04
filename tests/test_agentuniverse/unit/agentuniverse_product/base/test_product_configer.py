# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_product_configer.py

"""Unit tests for the ProductConfiger."""

from types import SimpleNamespace

import pytest

from agentuniverse_product.base.product_configer import (
    PRODUCT_COMPONENT_TYPE,
    ProductConfiger,
)


def make_configer(value):
    return SimpleNamespace(value=value, path="product.yaml")


class TestProductConfiger:
    """Test product configuration loading."""

    def test_component_type_list(self):
        assert "AGENT" in PRODUCT_COMPONENT_TYPE
        assert "PLUGIN" in PRODUCT_COMPONENT_TYPE

    def test_defaults(self):
        configer = ProductConfiger()
        assert configer.nickname is None
        assert configer.id is None
        assert configer.type is None
        assert configer.metadata_module == "agentuniverse_product.base.product"
        assert configer.metadata_class == "Product"

    def test_load_by_configer(self):
        configer = ProductConfiger()
        value = {"nickname": "product", "id": "p1", "type": "AGENT",
                 "avatar": "a.png", "description": "desc"}
        returned = configer.load_by_configer(make_configer(value))
        assert returned is configer
        assert configer.nickname == "product"
        assert configer.id == "p1"
        assert configer.type == "AGENT"
        assert configer.avatar == "a.png"
        assert configer.description == "desc"

    def test_missing_id_raises(self):
        configer = ProductConfiger()
        with pytest.raises(Exception, match="Failed to parse"):
            configer.load_by_configer(make_configer({"nickname": "p"}))

    def test_invalid_type_raises(self):
        configer = ProductConfiger()
        value = {"nickname": "p", "id": "p1", "type": "BOGUS"}
        with pytest.raises(Exception, match="Failed to parse"):
            configer.load_by_configer(make_configer(value))
