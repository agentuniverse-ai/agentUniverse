# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/13 00:00
# @Author  : Yue Wang
# @FileName: test_product_c_info.py

import unittest
import string

import examples.sample_apps.basic_sop_app.intelligence.utils.constant.product_c_info as product_c_info


class TestProductCInfo(unittest.TestCase):
    """Unit tests for the product_c_info constant module."""

    def test_base_product_description_present(self):
        """The module exposes a non-empty base product description."""
        self.assertIsInstance(product_c_info.BASE_PRODUCT_DESCRIPTION, str)
        self.assertTrue(product_c_info.BASE_PRODUCT_DESCRIPTION.strip())

    def test_base_product_description_mentions_product_name(self):
        """The base description identifies the DaBingYiLiao C product."""
        description = product_c_info.BASE_PRODUCT_DESCRIPTION
        self.assertIn('大病医疗C', description)
        self.assertIn('医疗险', description)

    def test_description_map_keys_are_letters_a_to_m(self):
        """PRODUCT_DESCRIPTION_MAP covers exactly the sections A..M."""
        self.assertEqual(set(product_c_info.PRODUCT_DESCRIPTION_MAP.keys()),
                         set(string.ascii_uppercase[:13]))

    def test_description_map_values_are_non_empty_strings(self):
        """Every mapped section is a non-empty textual description."""
        for key, value in product_c_info.PRODUCT_DESCRIPTION_MAP.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip())

    def test_description_map_contains_cancellation_rules(self):
        """Section H documents the contract cancellation/refund rules."""
        self.assertIn('退保', product_c_info.PRODUCT_DESCRIPTION_MAP['H'])
        self.assertIn('未满期净保险费', product_c_info.PRODUCT_DESCRIPTION_MAP['H'])

    def test_description_map_contains_coverage_section(self):
        """Section E lists coverage amounts for the two versions."""
        coverage = product_c_info.PRODUCT_DESCRIPTION_MAP['E']
        self.assertIn('总保额', coverage)
        self.assertIn('医疗保险金', coverage)

    def test_description_map_contains_waiting_period_info(self):
        """Section M states the waiting-period rules."""
        waiting = product_c_info.PRODUCT_DESCRIPTION_MAP['M']
        self.assertIn('等待期', waiting)
        self.assertIn('20天', waiting)

    def test_description_map_sections_start_with_numbering(self):
        """Most sections keep their ordinal number prefixes."""
        self.assertIn('3、', product_c_info.PRODUCT_DESCRIPTION_MAP['A'])
        self.assertIn('5、', product_c_info.PRODUCT_DESCRIPTION_MAP['C'])
        self.assertIn('6、', product_c_info.PRODUCT_DESCRIPTION_MAP['D'])


if __name__ == '__main__':
    unittest.main()
