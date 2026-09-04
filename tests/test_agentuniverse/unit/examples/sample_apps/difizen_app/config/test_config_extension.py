# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the ConfigExtension hook class."""

from agentuniverse.base.config.configer import Configer
from examples.sample_apps.difizen_app.config.config_extension import ConfigExtension


class TestConfigExtension:
    """Test the config extension hook construction."""

    def test_construct_with_configer(self):
        extension = ConfigExtension(Configer())
        assert isinstance(extension, ConfigExtension)
