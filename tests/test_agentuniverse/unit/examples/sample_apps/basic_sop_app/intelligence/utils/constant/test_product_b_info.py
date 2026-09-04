# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/13 00:00
# @Author  : Yue Wang
# @FileName: test_product_b_info.py

import unittest
import string

import examples.sample_apps.basic_sop_app.intelligence.utils.constant.product_b_info as product_b_info


class TestProductBInfo(unittest.TestCase):
    """Unit tests for the product_b_info constant module."""

    def test_base_product_description_present(self):
        """The module exposes a non-empty base product description."""
        self.assertIsInstance(product_b_info.BASE_PRODUCT_DESCRIPTION, str)
        self.assertTrue(product_b_info.BASE_PRODUCT_DESCRIPTION.strip())

    def test_base_product_description_mentions_product_name(self):
        """The base description identifies the ZeRenXian B product."""
        description = product_b_info.BASE_PRODUCT_DESCRIPTION
        self.assertIn('责任险', description)
        self.assertIn('基础版', description)

    def test_description_map_keys_are_letters_a_to_m(self):
        """PRODUCT_DESCRIPTION_MAP covers exactly the sections A..M."""
        self.assertEqual(set(product_b_info.PRODUCT_DESCRIPTION_MAP.keys()),
                         set(string.ascii_uppercase[:13]))

    def test_description_map_values_are_non_empty_strings(self):
        """Every mapped section is a non-empty textual description."""
        for key, value in product_b_info.PRODUCT_DESCRIPTION_MAP.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip())

    def test_description_map_contains_applicant_rules(self):
        """Section A states the applicant/insured eligibility rules."""
        applicant = product_b_info.PRODUCT_DESCRIPTION_MAP['A']
        self.assertIn('投保人', applicant)
        self.assertIn('被保险人', applicant)

    def test_description_map_contains_purchase_limit(self):
        """Section C states the maximum purchase quantity."""
        self.assertIn('限购', product_b_info.PRODUCT_DESCRIPTION_MAP['C'])

    def test_description_map_contains_cancellation_rules(self):
        """Section H documents the contract cancellation/refund rules."""
        cancellation = product_b_info.PRODUCT_DESCRIPTION_MAP['H']
        self.assertIn('退保', cancellation)
        self.assertIn('未满期净保险费', cancellation)

    def test_description_map_contains_waiting_period_info(self):
        """Section M states that there is no waiting period."""
        waiting = product_b_info.PRODUCT_DESCRIPTION_MAP['M']
        self.assertIn('等待期', waiting)
        self.assertIn('无等待期', waiting)


if __name__ == '__main__':
    unittest.main()
