# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_product_manager.py

"""Unit tests for the singleton ProductManager registry."""

import pytest

from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return ProductManager()


@pytest.fixture
def product():
    return Product(id="p1", nickname="product")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestProductManager:
    """Test ProductManager registry semantics."""

    def test_singleton_identity(self):
        assert ProductManager() is ProductManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.PRODUCT

    def test_register_and_list(self, manager, product):
        manager.register("p1", product)
        manager.register("p2", Product(id="p2"))
        assert manager.get_instance_name_list() == ["p1", "p2"]

    def test_duplicate_register_keeps_first(self, manager, product):
        manager.register("p1", product)
        manager.register("p1", Product(id="p2"))
        assert manager.get_instance_name_list() == ["p1"]
        assert manager.get_instance_obj_list()[0] is product

    def test_unregister_removes_instance(self, manager, product):
        manager.register("p1", product)
        manager.unregister("p1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = Product(id="p1", default_symbol=True)
        manager.register("p1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, product):
        manager.register("p1", product)
        assert "__default_instance__" not in manager.get_instance_name_list()
