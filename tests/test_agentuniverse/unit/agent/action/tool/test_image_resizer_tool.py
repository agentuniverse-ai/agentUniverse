#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for ImageResizerTool."""

import os
import tempfile
import unittest

from PIL import Image  # noqa: F401 - asserts Pillow is available in the test env

from agentuniverse.agent.action.tool.common_tool import image_resizer_tool as module
from agentuniverse.agent.action.tool.common_tool.image_resizer_tool import ImageResizerTool

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "image_resizer_tool.yaml.example")


class ImageResizerToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = ImageResizerTool(base_dir=self.directory.name)
        self.make_image("src.png", 100, 60, "RGBA")

    def tearDown(self):
        self.directory.cleanup()

    def make_image(self, name, width, height, mode="RGB"):
        path = os.path.join(self.directory.name, name)
        Image.new(mode, (width, height), (10, 20, 30, 255) if mode == "RGBA" else (10, 20, 30)).save(path)
        return path

    # --- info -----------------------------------------------------------
    def test_info(self):
        result = self.tool.execute(mode="info", file_path="src.png")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["width"], 100)
        self.assertEqual(result["height"], 60)
        self.assertEqual(result["format"], "PNG")

    # --- resize ---------------------------------------------------------
    def test_resize(self):
        result = self.tool.execute(mode="resize", file_path="src.png",
                                   output_path="out.png", width=50, height=30)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["width"], 50)
        self.assertEqual(result["height"], 30)
        with Image.open(result["output_path"]) as opened:
            self.assertEqual(opened.size, (50, 30))

    def test_resize_requires_width_and_height(self):
        result = self.tool.execute(mode="resize", file_path="src.png", output_path="o.png", width=50)
        self.assertEqual(result["status"], "error")
        self.assertIn("width and height", result["error"])

    # --- scale ----------------------------------------------------------
    def test_scale_halves_dimensions(self):
        result = self.tool.execute(mode="scale", file_path="src.png",
                                   output_path="half.png", factor=0.5)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["width"], 50)
        self.assertEqual(result["height"], 30)

    def test_scale_rejects_non_positive_factor(self):
        result = self.tool.execute(mode="scale", file_path="src.png",
                                   output_path="o.png", factor=0)
        self.assertEqual(result["status"], "error")
        self.assertIn("positive", result["error"])

    # --- crop -----------------------------------------------------------
    def test_crop(self):
        result = self.tool.execute(mode="crop", file_path="src.png",
                                   output_path="c.png", box=[10, 10, 60, 50])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["width"], 50)
        self.assertEqual(result["height"], 40)

    def test_crop_out_of_bounds(self):
        result = self.tool.execute(mode="crop", file_path="src.png",
                                   output_path="c.png", box=[0, 0, 200, 200])
        self.assertEqual(result["status"], "error")
        self.assertIn("bounds", result["error"])

    def test_crop_inverted_box(self):
        result = self.tool.execute(mode="crop", file_path="src.png",
                                   output_path="c.png", box=[50, 50, 10, 10])
        self.assertEqual(result["status"], "error")
        self.assertIn("right must exceed left", result["error"])

    # --- convert --------------------------------------------------------
    def test_convert_png_to_jpeg_flattens_alpha(self):
        result = self.tool.execute(mode="convert", file_path="src.png",
                                   output_path="out.jpg", target_format="jpg", overwrite=False)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["format"], "JPEG")
        with Image.open(result["output_path"]) as converted:
            self.assertEqual(converted.mode, "RGB")

    def test_convert_requires_target_format(self):
        result = self.tool.execute(mode="convert", file_path="src.png", output_path="o.jpg")
        self.assertEqual(result["status"], "error")
        self.assertIn("target_format", result["error"])

    def test_convert_disallowed_format(self):
        tool = ImageResizerTool(base_dir=self.directory.name, allowed_formats=("png",))
        result = tool.execute(mode="convert", file_path="src.png", output_path="o.jpg", target_format="jpg")
        self.assertEqual(result["status"], "error")
        self.assertIn("allowed_formats", result["error"])

    # --- path safety / overwrite ---------------------------------------
    def test_path_confined_to_base_dir(self):
        result = self.tool.execute(mode="info", file_path="../../../etc/passwd")
        self.assertEqual(result["status"], "error")
        # Either rejected as escaping base_dir or as not existing under it.
        self.assertTrue("error" in result)

    def test_refuses_overwrite(self):
        self.make_image("exists.png", 10, 10)
        result = self.tool.execute(mode="resize", file_path="src.png",
                                   output_path="exists.png", width=5, height=5)
        self.assertEqual(result["status"], "error")
        self.assertIn("overwrite=true", result["error"])

    def test_overwrite_allowed(self):
        self.make_image("exists.png", 10, 10)
        result = self.tool.execute(mode="resize", file_path="src.png",
                                   output_path="exists.png", width=5, height=5, overwrite=True)
        self.assertEqual(result["status"], "success")

    # --- errors ---------------------------------------------------------
    def test_missing_file(self):
        result = self.tool.execute(mode="info", file_path="nope.png")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_invalid_mode(self):
        result = self.tool.execute(mode="rotate", file_path="src.png")
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be", result["error"])

    def test_input_too_large(self):
        tool = ImageResizerTool(base_dir=self.directory.name, max_input_bytes=10)
        result = tool.execute(mode="info", file_path="src.png")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_bytes", result["error"])

    def test_quality_out_of_range(self):
        result = self.tool.execute(mode="convert", file_path="src.png",
                                   output_path="o.jpg", target_format="jpg", quality=200)
        self.assertEqual(result["status"], "error")
        self.assertIn("quality", result["error"])


class ImageResizerYamlTest(unittest.TestCase):
    def test_yaml_example_exists(self):
        self.assertTrue(os.path.isfile(YAML_PATH))

    def test_yaml_example_has_required_fields(self):
        import yaml

        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "image_resizer_tool")
        self.assertEqual(data["metadata"]["class"], "ImageResizerTool")
        self.assertIn("mode", data["input_keys"])
        self.assertEqual(data["allowed_formats"], ["jpg", "jpeg", "png", "webp"])


if __name__ == "__main__":
    unittest.main()
