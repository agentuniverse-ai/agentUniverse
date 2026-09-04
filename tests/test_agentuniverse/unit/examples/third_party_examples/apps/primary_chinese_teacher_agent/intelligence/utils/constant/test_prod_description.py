# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the prod description constant module."""

from examples.third_party_examples.apps.primary_chinese_teacher_agent.intelligence.utils.constant.prod_description import PROD_DESCRIPTION_A


class TestProdDescription:
    """Test the product description constant."""

    def test_description_is_non_empty_string(self):
        assert isinstance(PROD_DESCRIPTION_A, str)
        assert PROD_DESCRIPTION_A.strip()

    def test_description_is_long(self):
        assert len(PROD_DESCRIPTION_A.strip()) > 400

    def test_multiline_structure(self):
        assert PROD_DESCRIPTION_A.count("\n") > 5

    def test_keywords_present(self):
        assert "教学目标" in PROD_DESCRIPTION_A
        assert "教学内容" in PROD_DESCRIPTION_A
