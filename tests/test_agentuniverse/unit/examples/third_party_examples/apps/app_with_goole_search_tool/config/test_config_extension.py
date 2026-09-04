# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_config_extension.py

"""Unit tests for the ConfigExtension example config hook."""

import unittest

from agentuniverse.base.config.configer import Configer

from examples.third_party_examples.apps.app_with_goole_search_tool.config.config_extension import (
    ConfigExtension,
)


class TestConfigExtension(unittest.TestCase):
    """Unit tests for ConfigExtension."""

    def test_instantiation_with_configer(self):
        """A ConfigExtension can be built from a default Configer."""
        extension = ConfigExtension(configer=Configer())
        self.assertIsInstance(extension, ConfigExtension)

    def test_instantiation_with_path_configer(self):
        """A Configer created from a file path is accepted as well."""
        extension = ConfigExtension(configer=Configer(path="examples/config/config.toml"))
        self.assertIsInstance(extension, ConfigExtension)

    def test_configer_required(self):
        """Omitting the configer argument raises a TypeError."""
        with self.assertRaises(TypeError):
            ConfigExtension()

    def test_positional_configer_accepted(self):
        """The configer argument may also be passed positionally."""
        extension = ConfigExtension(Configer())
        self.assertIsInstance(extension, ConfigExtension)

    def test_extra_attributes_are_none(self):
        """The extension instance exposes no extra initialized state."""
        extension = ConfigExtension(configer=Configer())
        self.assertEqual(extension.__dict__, {})


if __name__ == "__main__":
    unittest.main()
