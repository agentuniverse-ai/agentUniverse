# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the prod description constant module."""

from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.utils.constant.prod_description import PROD_A_DESCRIPTION, PROD_B_DESCRIPTION


class TestProdDescriptions:
    """Test product description constants."""

    def test_descriptions_are_non_empty_strings(self):
        assert isinstance(PROD_A_DESCRIPTION, str)
        assert isinstance(PROD_B_DESCRIPTION, str)
        assert PROD_A_DESCRIPTION.strip()
        assert PROD_B_DESCRIPTION.strip()

    def test_descriptions_are_long(self):
        assert len(PROD_A_DESCRIPTION.strip()) > 400
        assert len(PROD_B_DESCRIPTION.strip()) > 400

    def test_descriptions_differ(self):
        assert PROD_A_DESCRIPTION != PROD_B_DESCRIPTION

    def test_multiline_structure(self):
        assert PROD_A_DESCRIPTION.count("\n") > 5
        assert PROD_B_DESCRIPTION.count("\n") > 5
