# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_plugin_product.py

"""Unit tests for the PluginProduct."""

from types import SimpleNamespace

from agentuniverse_product.base.plugin_product import PluginProduct


class TestPluginProduct:
    """Test PluginProduct defaults and configer initialization."""

    def test_defaults(self):
        product = PluginProduct()
        assert product.toolset == []
        assert product.openapi_desc is None
        assert product.id is None

    def test_initialize_sets_fields(self):
        product = PluginProduct()
        configer = SimpleNamespace(nickname="plugin", id="pl1",
                                   type="PLUGIN", avatar="a.png",
                                   description="desc", toolset=["t1"],
                                   openapi_desc="openapi")
        returned = product.initialize_by_component_configer(configer)
        assert returned is product
        assert product.id == "pl1"
        assert product.nickname == "plugin"
        assert product.toolset == ["t1"]
        assert product.openapi_desc == "openapi"

    def test_initialize_ignores_missing_optional_fields(self):
        product = PluginProduct()
        configer = SimpleNamespace(nickname="plugin", id="pl1",
                                   type="PLUGIN", avatar=None,
                                   description=None)
        product.initialize_by_component_configer(configer)
        assert product.toolset == []
        assert product.openapi_desc is None

    def test_equality(self):
        assert PluginProduct(id="pl1") == PluginProduct(id="pl1")
        assert PluginProduct(id="pl1") != PluginProduct(id="pl2")
