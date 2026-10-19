# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_prod_description.py

"""Unit tests for the prod_description example constants."""

import unittest

from examples.startup_app.demo_startup_app_with_single_agent.intelligence.utils.constant.prod_description import (
    PROD_DESCRIPTION_A)


class TestProdDescription(unittest.TestCase):
    """Verify the pet-insurance background knowledge constants."""

    def test_constant_is_non_empty_string(self):
        self.assertIsInstance(PROD_DESCRIPTION_A, str)
        self.assertTrue(PROD_DESCRIPTION_A.strip())

    def test_contains_product_name(self):
        self.assertIn('保险产品A', PROD_DESCRIPTION_A)

    def test_contains_insurance_period(self):
        self.assertIn('保险期间', PROD_DESCRIPTION_A)

    def test_contains_premium_details(self):
        self.assertIn('保费标准', PROD_DESCRIPTION_A)
        self.assertIn('1200元', PROD_DESCRIPTION_A)

    def test_contains_surrender_rules(self):
        self.assertIn('退保', PROD_DESCRIPTION_A)
        self.assertIn('犹豫期', PROD_DESCRIPTION_A)

    def test_contains_critical_illness_cover(self):
        self.assertIn('重大疾病', PROD_DESCRIPTION_A)

    def test_is_multiline_document(self):
        self.assertIn('\n', PROD_DESCRIPTION_A)


if __name__ == '__main__':
    unittest.main()
