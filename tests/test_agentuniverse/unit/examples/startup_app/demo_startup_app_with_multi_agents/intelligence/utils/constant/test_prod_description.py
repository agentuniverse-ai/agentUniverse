# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_prod_description.py
import unittest

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.utils.constant.prod_description import (
    PROD_A_DESCRIPTION,
    PROD_B_DESCRIPTION,
)


class ProdADescriptionTest(unittest.TestCase):
    """Test cases for the PROD_A_DESCRIPTION constant."""

    def test_description_is_not_empty(self):
        self.assertTrue(PROD_A_DESCRIPTION.strip())

    def test_description_contains_product_name(self):
        self.assertIn('保险产品A', PROD_A_DESCRIPTION)

    def test_description_contains_insurance_period(self):
        self.assertIn('一年期', PROD_A_DESCRIPTION)

    def test_description_contains_premium_amount(self):
        self.assertIn('1200元', PROD_A_DESCRIPTION)

    def test_description_does_not_contain_product_b(self):
        self.assertNotIn('保险产品B', PROD_A_DESCRIPTION)


class ProdBDescriptionTest(unittest.TestCase):
    """Test cases for the PROD_B_DESCRIPTION constant."""

    def test_description_is_not_empty(self):
        self.assertTrue(PROD_B_DESCRIPTION.strip())

    def test_description_contains_product_name(self):
        self.assertIn('保险产品B', PROD_B_DESCRIPTION)

    def test_description_contains_accidental_medical_coverage(self):
        self.assertIn('意外伤害医疗', PROD_B_DESCRIPTION)

    def test_description_contains_grace_period_rule(self):
        self.assertIn('退保', PROD_B_DESCRIPTION)

    def test_description_does_not_contain_product_a(self):
        self.assertNotIn('保险产品A', PROD_B_DESCRIPTION)


class ProdDescriptionsRelationTest(unittest.TestCase):
    """Cross-constant assertions for the two product descriptions."""

    def test_two_descriptions_are_different(self):
        self.assertNotEqual(PROD_A_DESCRIPTION, PROD_B_DESCRIPTION)
