# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_planner_product.py

"""Unit tests for the PlannerProduct."""

from agentuniverse_product.base.planner_product import PlannerProduct
from agentuniverse.base.component.component_enum import ComponentEnum


class TestPlannerProduct:
    """Test PlannerProduct defaults and typed instance property."""

    def test_defaults(self):
        product = PlannerProduct()
        assert product.member_keys is None
        assert product.id is None
        assert product.component_type == ComponentEnum.PRODUCT

    def test_construction_with_fields(self):
        product = PlannerProduct(id="p1", nickname="planner",
                                 member_keys=["m1"])
        assert product.id == "p1"
        assert product.member_keys == ["m1"]

    def test_instance_property_defaults_to_none(self):
        assert PlannerProduct(id="p1").instance is None
