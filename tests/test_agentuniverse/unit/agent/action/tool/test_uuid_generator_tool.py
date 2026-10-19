#!/usr/bin/env python3

"""Tests for the built-in UUIDGeneratorTool."""

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import uuid_generator_tool as uuid_module
from agentuniverse.agent.action.tool.common_tool.uuid_generator_tool import UUIDGeneratorTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(uuid_module.__file__), "uuid_generator_tool.yaml")
CANONICAL = "550e8400-e29b-41d4-a716-446655440000"


class TestUUIDGeneratorValidation(unittest.TestCase):
    """Input and configuration boundaries."""

    def setUp(self) -> None:
        self.tool = UUIDGeneratorTool()

    def test_invalid_mode_is_structured_error(self) -> None:
        result = self.tool.execute(mode="delete")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("mode must be", result["error"])

    def test_validate_requires_value(self) -> None:
        result = self.tool.execute(mode="validate")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("value is required", result["error"])

    def test_extract_requires_value(self) -> None:
        result = self.tool.execute(mode="extract")
        self.assertIn("value is required", result["error"])

    def test_rejects_unsupported_version(self) -> None:
        result = self.tool.execute(mode="generate", version=2)
        self.assertIn("version must be one of", result["error"])

    def test_rejects_unsupported_format(self) -> None:
        result = self.tool.execute(mode="generate", format="base64")
        self.assertIn("format must be one of", result["error"])

    def test_rejects_invalid_count(self) -> None:
        result = self.tool.execute(mode="generate_batch", count=0)
        self.assertIn("count must be a positive integer", result["error"])

    def test_rejects_batch_over_limit(self) -> None:
        result = self.tool.execute(mode="generate_batch", count=10_000)
        self.assertIn("max_batch_size", result["error"])

    def test_v5_requires_namespace(self) -> None:
        result = self.tool.execute(mode="generate", version=5, name="example.com", namespace="")
        self.assertIn("namespace is required for uuid5", result["error"])

    def test_v5_rejects_unknown_namespace(self) -> None:
        result = self.tool.execute(
            mode="generate",
            version=5,
            namespace="not-a-namespace",
            name="example.com",
        )
        self.assertIn("namespace must be one of", result["error"])

    def test_v5_requires_name(self) -> None:
        result = self.tool.execute(mode="generate", version=5, namespace="dns", name="")
        self.assertIn("name is required for uuid5", result["error"])

    def test_extract_rejects_oversized_text(self) -> None:
        self.tool.max_extract_chars = 4
        result = self.tool.execute(mode="extract", value="abcdefgh")
        self.assertIn("max_extract_chars", result["error"])

    def test_rejects_boolean_count_config(self) -> None:
        self.tool.count = True
        result = self.tool.execute(mode="generate_batch")
        self.assertIn("count must be a positive integer", result["error"])

    def test_rejects_invalid_tool_level_config(self) -> None:
        self.tool.version = 2
        result = self.tool.execute(mode="generate")
        self.assertIn("version must be one of", result["error"])


class TestUUIDGeneratorOperations(unittest.TestCase):
    """Deterministic UUID operations."""

    def setUp(self) -> None:
        self.tool = UUIDGeneratorTool()

    def test_generate_uuid4_default(self) -> None:
        result = self.tool.execute(mode="generate")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["version"], 4)
        self.assertEqual(result["format"], "string")
        self.assertEqual(len(result["uuid"]), 36)
        self.assertNotIn("namespace", result)

    def test_generate_hex_format(self) -> None:
        result = self.tool.execute(mode="generate", format="hex")
        self.assertEqual(len(result["uuid"]), 32)
        self.assertEqual(result["format"], "hex")
        self.assertNotIn("-", result["uuid"])

    def test_generate_urn_format(self) -> None:
        result = self.tool.execute(mode="generate", format="urn")
        self.assertTrue(result["uuid"].startswith("urn:uuid:"))
        self.assertEqual(result["format"], "urn")

    def test_v5_is_deterministic(self) -> None:
        first = self.tool.execute(mode="generate", version=5, namespace="dns", name="example.com")
        second = self.tool.execute(mode="generate", version=5, namespace="dns", name="example.com")
        self.assertEqual(first["uuid"], second["uuid"])
        self.assertEqual(first["version"], 5)
        self.assertEqual(first["namespace"], "6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        self.assertEqual(first["name"], "example.com")

    def test_v5_uuid_string_namespace(self) -> None:
        ns_uuid = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
        result = self.tool.execute(mode="generate", version=5, namespace=ns_uuid, name="example.com")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["namespace"], ns_uuid)

    def test_v3_is_deterministic(self) -> None:
        first = self.tool.execute(mode="generate", version=3, namespace="url", name="hello")
        second = self.tool.execute(mode="generate", version=3, namespace="url", name="hello")
        self.assertEqual(first["uuid"], second["uuid"])
        self.assertEqual(first["version"], 3)

    def test_generate_batch_returns_unique_uuids(self) -> None:
        result = self.tool.execute(mode="generate_batch", count=10)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 10)
        self.assertEqual(len(result["uuids"]), 10)
        self.assertEqual(len(set(result["uuids"])), 10)

    def test_generate_batch_uses_tool_level_count(self) -> None:
        self.tool.count = 4
        result = self.tool.execute(mode="generate_batch")
        self.assertEqual(result["count"], 4)

    def test_generate_batch_v5_is_deterministic(self) -> None:
        result = self.tool.execute(mode="generate_batch", version=5, namespace="dns", name="example.com", count=2)
        self.assertEqual(len(set(result["uuids"])), 1)

    def test_validate_accepts_canonical_uuid(self) -> None:
        result = self.tool.execute(mode="validate", value=CANONICAL)
        self.assertTrue(result["valid"])
        self.assertEqual(result["uuid"], CANONICAL)
        self.assertEqual(result["version"], 4)

    def test_validate_rejects_non_uuid(self) -> None:
        result = self.tool.execute(mode="validate", value="not-a-uuid")
        self.assertFalse(result["valid"])
        self.assertNotIn("uuid", result)

    def test_validate_rejects_hex_only_string(self) -> None:
        result = self.tool.execute(mode="validate", value="550e8400e29b41d4a716446655440000")
        self.assertFalse(result["valid"])

    def test_extract_finds_all_uuids(self) -> None:
        text = f"first {CANONICAL} then 123e4567-e89b-12d3-a456-426614174000 done"
        result = self.tool.execute(mode="extract", value=text)
        self.assertEqual(result["count"], 2)
        self.assertIn(CANONICAL, result["uuids"])

    def test_extract_deduplicates(self) -> None:
        text = f"{CANONICAL} and again {CANONICAL}"
        result = self.tool.execute(mode="extract", value=text)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total_matches"], 2)

    def test_extract_returns_empty_when_none_found(self) -> None:
        result = self.tool.execute(mode="extract", value="no uuids here at all")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["uuids"], [])


class TestUUIDGeneratorRegistration(unittest.TestCase):
    """Component registration through the YAML configuration."""

    def setUp(self) -> None:
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self) -> None:
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self) -> None:
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "UUIDGeneratorTool")

    def test_manager(self) -> None:
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, UUIDGeneratorTool)
        self.assertEqual(tool.input_keys, ["mode"])
        self.assertEqual(tool.version, 4)
        self.assertEqual(tool.format, "string")


if __name__ == "__main__":
    unittest.main()
