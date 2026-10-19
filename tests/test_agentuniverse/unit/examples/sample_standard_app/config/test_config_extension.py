# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_config_extension.py
"""Unit tests for the ConfigExtension example config hook.

The example only documents an initialization hook: it accepts a ``Configer``
and currently performs no work. The tests pin down that constructor contract,
so regressions that change instantiation behavior are caught.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[6]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[6]
                       / 'examples' / 'sample_standard_app' / 'config'))

from config_extension import ConfigExtension


class TestConfigExtension:
    """Test the ConfigExtension example configuration hook."""

    def test_instantiation_with_none(self):
        extension = ConfigExtension(None)
        assert isinstance(extension, ConfigExtension)

    def test_instantiation_with_arbitrary_configer(self):
        extension = ConfigExtension(object())
        assert isinstance(extension, ConfigExtension)

    def test_instantiation_does_not_raise(self):
        ConfigExtension(None)

    def test_configer_is_not_stored_as_attribute(self):
        extension = ConfigExtension({'dummy': 'configer'})
        assert not hasattr(extension, 'configer')

    def test_no_extra_instance_attributes(self):
        extension = ConfigExtension(None)
        assert vars(extension) == {}

    def test_no_public_helpers_defined(self):
        public_members = [member for member in dir(ConfigExtension)
                          if not member.startswith('_')]
        assert public_members == []

    def test_each_instance_is_distinct(self):
        first = ConfigExtension(None)
        second = ConfigExtension(None)
        assert first is not second
