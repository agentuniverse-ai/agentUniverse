# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/27 21:38
# @Author  : zhangdongxu
# @Email   : zhangdongxu0852@163.com
# @FileName: test_readimage_tool.py
import builtins
import importlib
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


READIMAGE_TOOL_MODULE = "agentuniverse.agent.action.tool.common_tool.readimage_tool"
READIMAGE_TOOL_FILE = (
    Path(__file__).resolve().parents[6]
    / "agentuniverse"
    / "agent"
    / "action"
    / "tool"
    / "common_tool"
    / "readimage_tool.py"
)


class FakeImageArray:
    """Minimal stand-in for a numpy image array exposing shape, size, copy and item access."""
    def __init__(self, shape=(100, 100, 3), size=1):
        """Store the array shape and element size."""
        self.shape = shape
        self.size = size

    def copy(self):
        """Return a new FakeImageArray with the same shape and element size."""
        return FakeImageArray(self.shape, self.size)

    def __getitem__(self, _):
        """Return a small FakeImageArray slice carrying the same element size."""
        return FakeImageArray((1, 1, 3), self.size)


class FakeScores:
    """Fake EAST text-detection scores output with a 1x1x1x1 shape."""
    shape = (1, 1, 1, 1)

    def __getitem__(self, _):
        """Return a list containing a single zero score value."""
        return [0.0]


class FakeGeometry:
    """Fake EAST text-detection geometry output with a 1x5x1x1 shape."""
    shape = (1, 5, 1, 1)

    def __getitem__(self, _):
        """Return a list containing a single zero geometry value."""
        return [0.0]


class FakeNet:
    """Fake OpenCV DNN net exposing setInput and forward mocks that return fake scores and geometry."""
    def __init__(self):
        """Create the net with a mocked setInput and a forward returning fake scores and geometry."""
        self.setInput = Mock()
        self.forward = Mock(return_value=(FakeScores(), FakeGeometry()))


class FakeDnn:
    """Fake OpenCV dnn module exposing net, readNet, blobFromImage and NMSBoxes mocks."""
    def __init__(self):
        """Wire the dnn mocks around a shared FakeNet instance."""
        self.net = FakeNet()
        self.readNet = Mock(return_value=self.net)
        self.blobFromImage = Mock(return_value="blob")
        self.NMSBoxes = Mock(return_value=[])


class FakeClahe:
    """Fake CLAHE object whose apply returns a grayscale FakeImageArray."""
    def apply(self, _):
        """Return a grayscale FakeImageArray derived from the input image."""
        return FakeImageArray((100, 100))


class FakeCv2:
    """Fake cv2 module providing color constants and mocked image functions returning FakeImageArray values."""
    COLOR_BGR2GRAY = 1
    COLOR_GRAY2BGR = 2
    COLOR_BGRA2BGR = 3
    COLOR_BGR2RGB = 4
    FONT_HERSHEY_SIMPLEX = 5
    IMREAD_UNCHANGED = -1

    def __init__(self):
        """Set up the mocked dnn module and image functions backed by FakeImageArray values."""
        self.dnn = FakeDnn()
        self.imread = Mock(return_value=FakeImageArray())
        self.imwrite = Mock(return_value=True)
        self.putText = Mock()
        self.resize = Mock(side_effect=lambda image, _: image)
        self.cvtColor = Mock(side_effect=self._cvt_color)
        self.createCLAHE = Mock(return_value=FakeClahe())
        self.bilateralFilter = Mock(side_effect=lambda image, *_: image)

    def _cvt_color(self, image, code):
        """Return a grayscale FakeImageArray for BGR2GRAY conversions and the input image otherwise."""
        if code == self.COLOR_BGR2GRAY:
            return FakeImageArray((100, 100), image.size)
        return image


class FakePillowImage:
    """Fake PIL.Image wrapper whose fromarray returns a SimpleNamespace carrying the source image."""
    @staticmethod
    def fromarray(image):
        """Wrap the given image array in a SimpleNamespace exposing it as the source."""
        return SimpleNamespace(source=image)


def unload_readimage_tool():
    """Remove the readimage_tool module from sys.modules and drop it from its parent package."""
    sys.modules.pop(READIMAGE_TOOL_MODULE, None)
    parent_name, _, module_name = READIMAGE_TOOL_MODULE.rpartition(".")
    parent = sys.modules.get(parent_name)
    if parent is not None and hasattr(parent, module_name):
        delattr(parent, module_name)


def import_readimage_tool_without(blocked=()):
    """Import readimage_tool from source with fake optional dependencies, optionally blocking real modules."""
    blocked = set(blocked)
    fake_modules = {
        "cv2": FakeCv2(),
        "pytesseract": SimpleNamespace(image_to_string=Mock(return_value="Mocked OCR\ntext")),
        "PIL": SimpleNamespace(Image=FakePillowImage),
        "numpy": SimpleNamespace(cos=math.cos, sin=math.sin),
    }
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Import hook that serves fake modules for stubbed dependencies, raises ImportError for blocked names and defers to the real import otherwise."""
        root_name = name.split(".", 1)[0]
        if name in blocked or root_name in blocked:
            raise ImportError(f"No module named {name}")
        if name in fake_modules:
            return fake_modules[name]
        return original_import(name, globals, locals, fromlist, level)

    unload_readimage_tool()
    with patch("builtins.__import__", side_effect=guarded_import):
        spec = importlib.util.spec_from_file_location(READIMAGE_TOOL_MODULE, READIMAGE_TOOL_FILE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[READIMAGE_TOOL_MODULE] = module
        spec.loader.exec_module(module)
    return module, fake_modules


class TestReadImageTool(unittest.TestCase):
    """Unit tests for readimage_tool helpers exercised against fake optional dependencies."""
    def tearDown(self):
        """Unload the imported readimage_tool module so each test starts from a clean state."""
        unload_readimage_tool()

    def test_enhance_image(self):
        """Verify enhance_image returns a two-dimensional grayscale image."""
        readimage_tool, _ = import_readimage_tool_without()

        enhanced = readimage_tool.enhance_image(FakeImageArray())

        self.assertEqual(len(enhanced.shape), 2)

    def test_clean_extracted_text(self):
        """Verify clean_extracted_text collapses newlines and runs of spaces."""
        readimage_tool, _ = import_readimage_tool_without()

        dirty_text = "This   is   a   test.\nNew    line."
        clean_text = readimage_tool.clean_extracted_text(dirty_text)

        self.assertNotIn("\n", clean_text)
        self.assertNotIn("  ", clean_text)
        self.assertEqual(clean_text, "This is a test. New line.")

    def test_save_text_to_file(self):
        """Verify save_text_to_file writes the given text to the target file."""
        readimage_tool, _ = import_readimage_tool_without()
        test_text = "Sample text for testing."

        with tempfile.TemporaryDirectory() as temp_dir:
            test_filename = os.path.join(temp_dir, "test_extracted_text.txt")
            readimage_tool.save_text_to_file(test_text, test_filename)

            self.assertTrue(os.path.exists(test_filename))
            with open(test_filename, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, test_text)

    def test_extract_text_from_image_without_east(self):
        """Verify text extraction without EAST delegates to pytesseract with the requested language."""
        readimage_tool, fake_modules = import_readimage_tool_without()

        text = readimage_tool.extract_text_from_image("input.png", use_east=False, lang="eng")

        self.assertEqual(text, "Mocked OCR text")
        fake_modules["pytesseract"].image_to_string.assert_called_once()
        self.assertEqual(fake_modules["pytesseract"].image_to_string.call_args.kwargs["lang"], "eng")

    def test_detect_text_regions_no_text(self):
        """Verify detect_text_regions drives the EAST dnn pipeline and returns no regions when none are found."""
        readimage_tool, fake_modules = import_readimage_tool_without()

        regions = readimage_tool.detect_text_regions(FakeImageArray())

        self.assertEqual(regions, [])
        fake_cv2 = fake_modules["cv2"]
        fake_cv2.dnn.readNet.assert_called_once_with("frozen_east_text_detection.pb")
        fake_cv2.dnn.blobFromImage.assert_called_once()
        fake_cv2.dnn.net.setInput.assert_called_once_with("blob")
        fake_cv2.dnn.net.forward.assert_called_once_with(
            ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
        )

    def test_import_succeeds_and_runtime_error_is_clear_when_optional_dependency_is_absent(self):
        """Verify the module imports without an optional dependency but raises a clear ImportError when the affected helper is used."""
        cases = [
            ("cv2", "cv2", "enhance_image", (FakeImageArray(),), "opencv-python is required"),
            ("numpy", "np", "detect_text_regions", (FakeImageArray(),), "numpy is required"),
            ("PIL", "Image", "ocr_on_regions", ([FakeImageArray()],), "Pillow is required"),
            (
                "pytesseract",
                "pytesseract",
                "ocr_on_regions",
                ([FakeImageArray()],),
                "pytesseract is required",
            ),
        ]

        for missing_module, attribute_name, function_name, args, message in cases:
            with self.subTest(missing_module=missing_module):
                readimage_tool, _ = import_readimage_tool_without(blocked={missing_module})

                self.assertIsNone(getattr(readimage_tool, attribute_name))
                with self.assertRaisesRegex(ImportError, message):
                    getattr(readimage_tool, function_name)(*args)


if __name__ == "__main__":
    unittest.main()
