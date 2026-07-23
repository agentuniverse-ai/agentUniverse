#!/usr/bin/env python3

"""Tests for the built-in QRCodeTool."""

import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import qrcode_tool as qrcode_module
from agentuniverse.agent.action.tool.common_tool.qrcode_tool import QRCodeTool
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

QRCODE_AVAILABLE = importlib.util.find_spec("qrcode") is not None
PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None
PYZBAR_AVAILABLE = importlib.util.find_spec("pyzbar") is not None
YAML_PATH = os.path.join(os.path.dirname(qrcode_module.__file__), "qrcode_tool.yaml")


@unittest.skipUnless(QRCODE_AVAILABLE and PIL_AVAILABLE, "qrcode and Pillow required")
class TestQRCodeValidation(unittest.TestCase):
    """Input, configuration, and path boundaries."""

    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir_context.name
        self.tool = QRCodeTool(base_dir=self.base_dir)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_invalid_mode_is_structured_error(self) -> None:
        result = self.tool.execute(mode="delete", data="x", file_path="a.png")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("mode must be", result["error"])

    def test_generate_requires_data(self) -> None:
        result = self.tool.execute(mode="generate", file_path="a.png")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("data", result["error"])

    def test_generate_requires_file_path(self) -> None:
        result = self.tool.execute(mode="generate", data="hello")
        self.assertIn("file_path is required", result["error"])

    def test_decode_requires_file_path(self) -> None:
        result = self.tool.execute(mode="decode")
        self.assertIn("file_path is required", result["error"])

    def test_rejects_non_image_extension(self) -> None:
        result = self.tool.execute(mode="decode", file_path="notes.txt")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("supported image extension", result["error"])

    def test_rejects_parent_path_escape(self) -> None:
        result = self.tool.execute(mode="generate", data="x", file_path="../escape.png")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            outside_file = os.path.join(outside, "outside.png")
            with open(outside_file, "wb") as output:
                output.write(b"not a qr code")
            os.symlink(outside, os.path.join(self.base_dir, "linked"))
            result = self.tool.execute(mode="decode", file_path="linked/outside.png")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_rejects_input_over_budget(self) -> None:
        self.tool.max_input_chars = 4
        result = self.tool.execute(mode="generate", data="abcdef", file_path="a.png")
        self.assertIn("max_input_chars", result["error"])

    def test_rejects_invalid_error_correction(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="x",
            file_path="a.png",
            error_correction="Z",
        )
        self.assertIn("error_correction must be one of", result["error"])

    def test_rejects_out_of_range_box_size(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="x",
            file_path="a.png",
            box_size=0,
        )
        self.assertIn("box_size must be between", result["error"])
        result = self.tool.execute(
            mode="generate",
            data="x",
            file_path="a.png",
            box_size=10_000,
        )
        self.assertIn("box_size must be between", result["error"])

    def test_rejects_out_of_range_border(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="x",
            file_path="a.png",
            border=99,
        )
        self.assertIn("border must be between", result["error"])

    def test_rejects_boolean_numeric_config(self) -> None:
        self.tool.max_input_chars = True
        result = self.tool.execute(mode="generate", data="x", file_path="a.png")
        self.assertIn("max_input_chars must be a positive integer", result["error"])

    def test_missing_dependency_has_install_hint(self) -> None:
        with patch.object(
            self.tool,
            "_load_qrcode",
            side_effect=ImportError("missing"),
        ):
            result = self.tool.execute(mode="generate", data="x", file_path="a.png")
        self.assertEqual(result["error_type"], "dependency_error")
        self.assertIn("pip install qrcode[pil]", result["error"])


@unittest.skipUnless(QRCODE_AVAILABLE and PIL_AVAILABLE, "qrcode and Pillow required")
class TestQRCodeOperations(unittest.TestCase):
    """Deterministic QR code generation round trips."""

    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir_context.name
        self.tool = QRCodeTool(base_dir=self.base_dir)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_generate_creates_png_file(self) -> None:
        result = self.tool.execute(mode="generate", data="hello world", file_path="qr.png")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.isfile(result["file_path"]))
        self.assertGreater(os.path.getsize(result["file_path"]), 0)
        self.assertEqual(result["data_length"], len("hello world"))
        self.assertEqual(result["error_correction"], "M")

    def test_generate_in_subdirectory(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="nested",
            file_path="output/qr.png",
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.isfile(os.path.join(self.base_dir, "output/qr.png")))

    def test_generate_respects_custom_geometry(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="config",
            file_path="qr.png",
            box_size=5,
            border=2,
            error_correction="H",
        )
        self.assertEqual(result["box_size"], 5)
        self.assertEqual(result["border"], 2)
        self.assertEqual(result["error_correction"], "H")

    def test_size_is_alias_for_box_size(self) -> None:
        result = self.tool.execute(
            mode="generate",
            data="config",
            file_path="qr.png",
            size=7,
        )
        self.assertEqual(result["box_size"], 7)

    def test_generate_refuses_overwrite_and_preserves_file(self) -> None:
        first = self.tool.execute(mode="generate", data="one", file_path="qr.png")
        self.assertEqual(first["status"], "success")
        original = os.path.getsize(first["file_path"])
        result = self.tool.execute(mode="generate", data="two", file_path="qr.png")
        self.assertEqual(result["status"], "error")
        self.assertIn("set overwrite=true", result["error"])
        self.assertEqual(os.path.getsize(first["file_path"]), original)

    def test_generate_overwrite_replaces_file(self) -> None:
        self.tool.execute(mode="generate", data="one", file_path="qr.png")
        result = self.tool.execute(
            mode="generate",
            data="two",
            file_path="qr.png",
            overwrite=True,
        )
        self.assertEqual(result["status"], "success")

    def test_generate_base64_returns_encoded_png(self) -> None:
        result = self.tool.execute(mode="generate_base64", data="encoded")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["image_base64"])
        self.assertEqual(result["image_format"], "PNG")

    def test_generate_base64_respects_output_format(self) -> None:
        result = self.tool.execute(
            mode="generate_base64",
            data="encoded",
            output_format="bmp",
        )
        self.assertEqual(result["image_format"], "BMP")

    def test_decode_missing_file(self) -> None:
        result = self.tool.execute(mode="decode", file_path="missing.png")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("does not exist", result["error"])

    def test_decode_oversized_file_rejected(self) -> None:
        path = os.path.join(self.base_dir, "big.png")
        with open(path, "wb") as output:
            output.write(b"\x00" * 64)
        self.tool.max_read_bytes = 8
        result = self.tool.execute(mode="decode", file_path="big.png")
        self.assertIn("max_read_bytes", result["error"])

    def test_decode_without_decoder_reports_dependency(self) -> None:
        if PYZBAR_AVAILABLE:
            self.skipTest("pyzbar is installed, skipping dependency-error path")
        self.tool.execute(mode="generate", data="hello", file_path="qr.png")
        result = self.tool.execute(mode="decode", file_path="qr.png")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "dependency_error")
        self.assertIn("pyzbar", result["error"])


class TestQRCodeRegistration(unittest.TestCase):
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
        self.assertEqual(component.metadata_class, "QRCodeTool")

    def test_manager(self) -> None:
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, QRCodeTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
