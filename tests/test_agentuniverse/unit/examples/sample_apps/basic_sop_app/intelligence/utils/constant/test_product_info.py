# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/13 00:00
# @Author  : Yue Wang
# @FileName: test_product_info.py

import unittest

import examples.sample_apps.basic_sop_app.intelligence.utils.constant.product_info as product_info


class TestProductInfo(unittest.TestCase):
    """Unit tests for the product_info constant module."""

    def test_product_item_map_key_mapping(self):
        """PRODUCT_ITEM_MAP maps section letters to their Chinese titles."""
        expected = {
            'A': '投/被保险人',
            'C': '投保份数',
            'D': '保险期限',
            'E': '保障责任',
            'I': '续保规则',
            'J': '增值服务',
            'K': '责任免除',
        }
        for key, title in expected.items():
            with self.subTest(key=key):
                self.assertEqual(product_info.PRODUCT_ITEM_MAP[key], title)

    def test_product_item_map_values_are_non_empty_strings(self):
        """Every item title in PRODUCT_ITEM_MAP is a non-empty string."""
        for key, value in product_info.PRODUCT_ITEM_MAP.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, str)
                self.assertTrue(value)

    def test_product_name_map_keys(self):
        """PRODUCT_NAME_MAP only covers products B and C."""
        self.assertEqual(set(product_info.PRODUCT_NAME_MAP.keys()), {'B', 'C'})

    def test_product_name_map_contains_names(self):
        """Each product name entry mentions the product and its category."""
        self.assertIn('责任险B', product_info.PRODUCT_NAME_MAP['B'])
        self.assertIn('大病医疗C', product_info.PRODUCT_NAME_MAP['C'])
        self.assertIn('对应险种', product_info.PRODUCT_NAME_MAP['B'])

    def test_recommendation_map_keys_match_name_map(self):
        """Recommendation keys mirror the product name map keys."""
        self.assertEqual(set(product_info.PRODUCT_RECOMMENDATION_MAP.keys()),
                         set(product_info.PRODUCT_NAME_MAP.keys()))

    def test_recommendation_map_values_are_non_empty_strings(self):
        """Every recommendation entry is a non-empty string."""
        for key, value in product_info.PRODUCT_RECOMMENDATION_MAP.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip())

    def test_recommendation_contains_summary_and_strengths(self):
        """Recommendations include the 总评 and 优势点 sections."""
        rec_b = product_info.PRODUCT_RECOMMENDATION_MAP['B']
        rec_c = product_info.PRODUCT_RECOMMENDATION_MAP['C']
        self.assertIn('总评', rec_b)
        self.assertIn('优势点', rec_b)
        self.assertIn('总评', rec_c)
        self.assertIn('优势点', rec_c)


if __name__ == '__main__':
    unittest.main()
