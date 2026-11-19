#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import string
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import password_generator_tool as password_module
from agentuniverse.agent.action.tool.common_tool.password_generator_tool import (
    PasswordGeneratorTool,
    SYMBOLS,
)
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = password_module.__file__.replace(".py", ".yaml")

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits


class PasswordGeneratorToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = PasswordGeneratorTool()

    # ---- generate -----------------------------------------------------------
    def test_generate_default_length(self) -> None:
        result = self.tool.execute(mode="generate")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["password"]), self.tool.default_length)
        self.assertGreater(result["entropy_bits"], 0)

    def test_generate_custom_length(self) -> None:
        result = self.tool.execute(mode="generate", length=32)
        self.assertEqual(len(result["password"]), 32)

    def test_generate_contains_all_enabled_classes(self) -> None:
        result = self.tool.execute(mode="generate", length=20)
        password = result["password"]
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in SYMBOLS for c in password))

    def test_generate_only_lowercase(self) -> None:
        result = self.tool.execute(
            mode="generate",
            length=20,
            include_uppercase=False,
            include_lowercase=True,
            include_digits=False,
            include_symbols=False,
        )
        password = result["password"]
        self.assertEqual(password, password.lower())
        self.assertTrue(all(c in LOWERCASE for c in password))

    def test_generate_only_digits(self) -> None:
        result = self.tool.execute(
            mode="generate",
            length=12,
            include_uppercase=False,
            include_lowercase=False,
            include_digits=True,
            include_symbols=False,
        )
        self.assertTrue(all(c in DIGITS for c in result["password"]))

    def test_generate_exclude_similar(self) -> None:
        similar = set("Il1O0o") | set("|`'\"")
        result = self.tool.execute(mode="generate", length=40, exclude_similar=True)
        self.assertFalse(any(c in similar for c in result["password"]))

    def test_generate_uniqueness(self) -> None:
        first = self.tool.execute(mode="generate", length=24)["password"]
        second = self.tool.execute(mode="generate", length=24)["password"]
        self.assertNotEqual(first, second)

    def test_generate_requires_at_least_one_class(self) -> None:
        result = self.tool.execute(
            mode="generate",
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_symbols=False,
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("at least one character class", result["error"])

    def test_generate_rejects_too_short(self) -> None:
        result = self.tool.execute(mode="generate", length=3)
        self.assertIn("at least 4", result["error"])

    def test_generate_rejects_too_long(self) -> None:
        result = self.tool.execute(mode="generate", length=999)
        self.assertIn("at most 256", result["error"])

    def test_generate_rejects_non_integer_length(self) -> None:
        result = self.tool.execute(mode="generate", length=16.0)
        self.assertEqual(result["error_type"], "validation_error")

    def test_generate_rejects_bad_mode(self) -> None:
        result = self.tool.execute(mode="rotate")
        self.assertIn("mode must be", result["error"])

    # ---- generate_batch -----------------------------------------------------
    def test_generate_batch_returns_count(self) -> None:
        result = self.tool.execute(mode="generate_batch", length=16, count=5)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["passwords"]), 5)
        self.assertTrue(all(len(p) == 16 for p in result["passwords"]))

    def test_generate_batch_all_unique(self) -> None:
        result = self.tool.execute(mode="generate_batch", length=24, count=10)
        self.assertEqual(len(set(result["passwords"])), 10)

    def test_generate_batch_rejects_zero_count(self) -> None:
        result = self.tool.execute(mode="generate_batch", count=0)
        self.assertIn("at least 1", result["error"])

    def test_generate_batch_rejects_huge_count(self) -> None:
        result = self.tool.execute(mode="generate_batch", count=5000)
        self.assertIn("at most 1000", result["error"])

    # ---- check_strength -----------------------------------------------------
    def test_check_strength_weak_password(self) -> None:
        result = self.tool.execute(mode="check_strength", password="abc")
        self.assertEqual(result["status"], "success")
        self.assertLess(result["score"], 50)
        self.assertIn(result["rating"], {"weak", "very weak"})

    def test_check_strength_strong_password(self) -> None:
        result = self.tool.execute(mode="check_strength", password="C0rrect-Horse-Battery!Staple#42")
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["score"], 70)

    def test_check_strength_flags_missing_classes(self) -> None:
        result = self.tool.execute(mode="check_strength", password="alllowercase")
        self.assertIn("no uppercase letters", result["issues"])
        self.assertIn("no digits", result["issues"])
        self.assertIn("no symbols", result["issues"])

    def test_check_strength_rejects_empty(self) -> None:
        result = self.tool.execute(mode="check_strength", password="")
        self.assertEqual(result["status"], "error")
        self.assertIn("empty", result["error"])

    def test_check_strength_rejects_non_string(self) -> None:
        result = self.tool.execute(mode="check_strength", password=123456)
        self.assertEqual(result["error_type"], "validation_error")

    def test_check_strength_entropy_grows_with_length(self) -> None:
        short = self.tool.execute(mode="check_strength", password="Aa1!abcd")["entropy_bits"]
        long = self.tool.execute(mode="check_strength", password="Aa1!abcdAa1!abcdAa1!")["entropy_bits"]
        self.assertGreater(long, short)

    def test_check_strength_pool_size_reflects_classes(self) -> None:
        digits_only = self.tool.execute(mode="check_strength", password="123456789012")["pool_size"]
        mixed = self.tool.execute(mode="check_strength", password="Abcdef12!@")["pool_size"]
        self.assertGreater(mixed, digits_only)


class PasswordRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=YAML_PATH).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "PasswordGeneratorTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, PasswordGeneratorTool)
        self.assertEqual(tool.input_keys, ["mode"])
        self.assertEqual(tool.default_length, 16)

    def test_yaml_loads_as_dict(self):
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "password_generator_tool")
        self.assertEqual(data["metadata"]["class"], "PasswordGeneratorTool")


if __name__ == "__main__":
    unittest.main()
