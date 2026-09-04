# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_prod_description.py
"""Unit tests for the product description constants in the startup demo example."""

from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.utils.constant.prod_description import (
    PROD_A_DESCRIPTION,
    PROD_B_DESCRIPTION,
)


class TestProdDescription:
    """Test the PROD_A_DESCRIPTION and PROD_B_DESCRIPTION constants."""

    def test_constants_are_non_empty_strings(self):
        assert isinstance(PROD_A_DESCRIPTION, str)
        assert isinstance(PROD_B_DESCRIPTION, str)
        assert PROD_A_DESCRIPTION.strip()
        assert PROD_B_DESCRIPTION.strip()

    def test_product_names_are_present(self):
        assert '保险产品A' in PROD_A_DESCRIPTION
        assert '保险产品B' in PROD_B_DESCRIPTION

    def test_product_a_contains_its_key_rules(self):
        assert '重大疾病' in PROD_A_DESCRIPTION
        assert '健康关怀金人民币5万元' in PROD_A_DESCRIPTION
        assert '犹豫期内退保' in PROD_A_DESCRIPTION

    def test_product_b_contains_its_key_rules(self):
        assert '意外伤害医疗保险金' in PROD_B_DESCRIPTION
        assert '紧急医疗转运' in PROD_B_DESCRIPTION
        assert '犹豫期外退保' in PROD_B_DESCRIPTION

    def test_premium_amounts_are_mentioned(self):
        assert '1200元' in PROD_A_DESCRIPTION
        assert '800元/年' in PROD_B_DESCRIPTION
        assert '2,000元/年' in PROD_B_DESCRIPTION

    def test_constants_differ(self):
        assert PROD_A_DESCRIPTION != PROD_B_DESCRIPTION
