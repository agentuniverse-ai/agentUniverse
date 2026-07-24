#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import base64
import os
import tempfile
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import base64_image_tool as base64_module
from agentuniverse.agent.action.tool.common_tool.base64_image_tool import Base64ImageTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = base64_module.__file__.replace(".py", ".yaml")

PNG_HEADER = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32).decode("ascii")

# Minimal valid 1x1 transparent PNG.
VALID_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c63000100000005000100a0f903390000000049454e44ae426082"
)
VALID_PNG_B64 = base64.b64encode(VALID_PNG_BYTES).decode("ascii")


class Base64ImageToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = Base64ImageTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write(self, name, content):
        path = os.path.join(self.directory.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(content)
        return path

    # ---- encode -------------------------------------------------------------
    def test_encode_returns_base64(self):
        self.write("logo.png", b"\x89PNG\r\n\x1a\n" + b"pixel-data")
        result = self.tool.execute(mode="encode", file_path="logo.png")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mime_type"], "image/png")
        self.assertEqual(
            base64.b64decode(result["base64"]),
            b"\x89PNG\r\n\x1a\n" + b"pixel-data",
        )

    def test_encode_as_data_uri(self):
        self.write("a.jpg", b"jpegbytes")
        result = self.tool.execute(mode="encode", file_path="a.jpg", as_data_uri=True)
        self.assertTrue(result["data_uri"].startswith("data:image/jpeg;base64,"))
        self.assertEqual(
            result["data_uri"].split(",")[1],
            base64.b64encode(b"jpegbytes").decode("ascii"),
        )

    def test_encode_rejects_non_image_extension(self):
        self.write("notes.txt", b"hi")
        result = self.tool.execute(mode="encode", file_path="notes.txt")
        self.assertIn("must be an image", result["error"])

    def test_encode_rejects_missing_file(self):
        result = self.tool.execute(mode="encode", file_path="nope.png")
        self.assertIn("does not exist", result["error"])

    def test_encode_rejects_path_escape(self):
        result = self.tool.execute(mode="encode", file_path="../escape.png")
        self.assertEqual(result["status"], "error")
        self.assertIn("escapes", result["error"])

    def test_encode_rejects_oversized(self):
        self.write("big.png", b"x")
        self.tool.max_read_bytes = 0
        # max_read_bytes must be positive, so bump to 1 and write 2 bytes
        self.tool.max_read_bytes = 1
        self.write("big2.png", b"xy")
        result = self.tool.execute(mode="encode", file_path="big2.png")
        self.assertIn("max_read_bytes", result["error"])

    # ---- decode -------------------------------------------------------------
    def test_decode_writes_file(self):
        payload = base64.b64encode(b"hello-image").decode("ascii")
        result = self.tool.execute(mode="decode", data=payload, output_path="out.png")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mime_type"], "image/png")
        with open(os.path.join(self.directory.name, "out.png"), "rb") as handle:
            self.assertEqual(handle.read(), b"hello-image")

    def test_decode_accepts_data_uri(self):
        data_uri = "data:image/png;base64," + base64.b64encode(b"x").decode("ascii")
        result = self.tool.execute(mode="decode", data=data_uri, output_path="o.png")
        self.assertEqual(result["status"], "success")

    def test_decode_rejects_invalid_base64(self):
        result = self.tool.execute(mode="decode", data="!!!notbase64!!!", output_path="o.png")
        self.assertIn("not valid base64", result["error"])

    def test_decode_rejects_non_image_output(self):
        payload = base64.b64encode(b"x").decode("ascii")
        result = self.tool.execute(mode="decode", data=payload, output_path="o.txt")
        self.assertIn("must be an image", result["error"])

    def test_decode_refuses_overwrite_without_flag(self):
        payload = base64.b64encode(b"x").decode("ascii")
        self.write("exists.png", b"old")
        result = self.tool.execute(mode="decode", data=payload, output_path="exists.png")
        self.assertIn("overwrite=true", result["error"])
        # existing file is preserved
        with open(os.path.join(self.directory.name, "exists.png"), "rb") as handle:
            self.assertEqual(handle.read(), b"old")

    def test_decode_overwrite_flag_replaces(self):
        payload = base64.b64encode(b"new").decode("ascii")
        self.write("exists.png", b"old")
        result = self.tool.execute(
            mode="decode", data=payload, output_path="exists.png", overwrite=True
        )
        self.assertEqual(result["status"], "success")
        with open(os.path.join(self.directory.name, "exists.png"), "rb") as handle:
            self.assertEqual(handle.read(), b"new")

    def test_decode_rejects_oversized_payload(self):
        big = base64.b64encode(b"x" * 200).decode("ascii")
        self.tool.max_write_bytes = 10
        result = self.tool.execute(mode="decode", data=big, output_path="o.png")
        self.assertIn("max_write_bytes", result["error"])

    # ---- info ---------------------------------------------------------------
    def test_info_reports_size_without_pillow(self):
        result = self.tool.execute(mode="info", data=VALID_PNG_B64)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["size"], len(VALID_PNG_BYTES))
        # When Pillow is installed we additionally get dimensions/format.
        if result.get("width") is not None:
            self.assertEqual(result["width"], 1)
            self.assertEqual(result["height"], 1)
            self.assertEqual(result["format"], "png")

    def test_info_rejects_invalid_base64(self):
        result = self.tool.execute(mode="info", data="@@@bad@@@")
        self.assertIn("not valid base64", result["error"])

    def test_info_rejects_empty_data(self):
        result = self.tool.execute(mode="info", data="   ")
        self.assertEqual(result["status"], "error")

    # ---- round-trip & validation -------------------------------------------
    def test_encode_decode_round_trip(self):
        original = b"\x89PNG\r\n\x1a\n" + b"round" + b"\x00" * 16
        self.write("src.png", original)
        encoded = self.tool.execute(mode="encode", file_path="src.png")["base64"]
        self.tool.execute(mode="decode", data=encoded, output_path="dst.png")
        with open(os.path.join(self.directory.name, "dst.png"), "rb") as handle:
            self.assertEqual(handle.read(), original)

    def test_rejects_bad_mode(self):
        result = self.tool.execute(mode="rotate", file_path="a.png")
        self.assertIn("mode must be", result["error"])

    def test_as_data_uri_must_be_boolean(self):
        self.write("a.png", b"x")
        result = self.tool.execute(mode="encode", file_path="a.png", as_data_uri="yes")
        self.assertEqual(result["error_type"], "validation_error")


class Base64ImageRegistrationTest(unittest.TestCase):
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
        self.assertEqual(component.metadata_class, "Base64ImageTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, Base64ImageTool)
        self.assertEqual(tool.input_keys, ["mode"])

    def test_yaml_loads_as_dict(self):
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "base64_image_tool")
        self.assertEqual(data["metadata"]["class"], "Base64ImageTool")


if __name__ == "__main__":
    unittest.main()
