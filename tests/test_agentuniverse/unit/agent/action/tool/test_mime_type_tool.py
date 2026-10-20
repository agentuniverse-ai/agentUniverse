#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_mime_type_tool.py

"""Offline unit tests for MimeTypeTool.

The tool is built purely on the standard library (an embedded frozen
table plus the ``mimetypes`` fallback module) and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: table entries are spot-verified against IANA-registered
or otherwise well-known media types, reverse mappings and category
listings against the documented table order, and sniff cases against
fixed samples. The one stdlib-fallback case (``.ps``) uses a value
that has been stable in CPython's builtin ``mimetypes`` table for
many years.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import MimeTypeTool
from agentuniverse.agent.action.tool.common_tool.mime_type_tool import (
    MimeTypeTool as DirectMimeTypeTool,
)

# --------------------------------------------------------------------- #
# Ground-truth expectations (IANA / widely established values)
# --------------------------------------------------------------------- #
DOCX_MIME = (
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.document"
)
XLSX_MIME = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
PPTX_MIME = (
    "application/vnd.openxmlformats-officedocument"
    ".presentationml.presentation"
)

# 25 spot-checks across every category (extension -> (mime, category)).
GROUND_TRUTHS = {
    "png": ("image/png", "image"),
    "svg": ("image/svg+xml", "image"),
    "webp": ("image/webp", "image"),
    "jpg": ("image/jpeg", "image"),
    "json": ("application/json", "text"),
    # YAML: text/yaml is the documented table choice (RFC 9512 later
    # registered application/yaml in 2024).
    "yaml": ("text/yaml", "text"),
    "yml": ("text/yaml", "text"),
    "py": ("text/x-python", "code"),
    "tar.gz": ("application/gzip", "archive"),
    "tgz": ("application/gzip", "archive"),
    "gz": ("application/gzip", "archive"),
    "tar": ("application/x-tar", "archive"),
    "docx": (DOCX_MIME, "binary"),
    "pdf": ("application/pdf", "binary"),
    "md": ("text/markdown", "text"),
    "csv": ("text/csv", "text"),
    "css": ("text/css", "text"),
    "html": ("text/html", "text"),
    "woff2": ("font/woff2", "font"),
    "ttf": ("font/ttf", "font"),
    "xlsx": (XLSX_MIME, "binary"),
    "pptx": (PPTX_MIME, "binary"),
    "gltf": ("model/gltf+json", "model"),
    "glb": ("model/gltf-binary", "model"),
    "wasm": ("application/wasm", "binary"),
    "mp3": ("audio/mpeg", "audio"),
    "mp4": ("video/mp4", "video"),
    "zip": ("application/zip", "archive"),
    "sh": ("text/x-shellscript", "code"),
}

# A genuine Base64 payload of "hello world from the mime tool!".
BASE64_SAMPLE = "aGVsbG8gd29ybGQgZnJvbSB0aGUgbWltZSB0b29sIQ=="


class MimeTypeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MimeTypeTool."""

    def setUp(self) -> None:
        self.tool = MimeTypeTool()

    # ------------------------------------------------------------------ #
    # Table ground truths (25 spot-verified entries)
    # ------------------------------------------------------------------ #

    def test_ground_truth_table_entries(self) -> None:
        for ext, (mime, category) in GROUND_TRUTHS.items():
            with self.subTest(extension=ext):
                result = self.tool.execute(mode="lookup", extension=ext)
                self.assertTrue(result["known"])
                self.assertEqual(result["source"], "table")
                self.assertEqual(result["mime"], mime)
                self.assertEqual(result["category"], category)
                self.assertEqual(result["extension"], "." + ext)

    def test_table_size_at_least_180(self) -> None:
        result = self.tool.execute(mode="category", category="text")
        total = 0
        for category in MimeTypeTool.CATEGORIES:
            total += self.tool.execute(
                mode="category", category=category
            )["count"]
        self.assertGreaterEqual(total, 180)
        self.assertGreaterEqual(result["count"], 20)

    def test_ts_follows_iana_video_mp2t(self) -> None:
        # Documented ambiguity resolution: .ts is IANA video/mp2t,
        # TypeScript keeps .tsx.
        ts = self.tool.execute(mode="lookup", extension="ts")
        self.assertEqual(ts["mime"], "video/mp2t")
        self.assertEqual(ts["category"], "video")
        tsx = self.tool.execute(mode="lookup", extension="tsx")
        self.assertEqual(tsx["mime"], "application/typescript")
        self.assertEqual(tsx["category"], "code")

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    def test_lookup_filename_resolves_extension(self) -> None:
        result = self.tool.execute(mode="lookup", filename="logo.png")
        self.assertEqual(
            result,
            {
                "mode": "lookup",
                "input_kind": "filename",
                "filename": "logo.png",
                "extension": ".png",
                "mime": "image/png",
                "category": "image",
                "known": True,
                "source": "table",
                "compound": False,
            },
        )

    def test_lookup_filename_case_insensitive(self) -> None:
        result = self.tool.execute(mode="lookup", filename="IMG_1234.PNG")
        self.assertEqual(result["extension"], ".png")
        self.assertEqual(result["mime"], "image/png")

    def test_lookup_extension_without_dot(self) -> None:
        result = self.tool.execute(mode="lookup", extension="JSON")
        self.assertEqual(result["extension"], ".json")
        self.assertEqual(result["mime"], "application/json")

    def test_lookup_extension_with_dot(self) -> None:
        result = self.tool.execute(mode="lookup", extension=".json")
        self.assertEqual(result["extension"], ".json")
        self.assertEqual(result["mime"], "application/json")

    def test_lookup_strips_directories_posix_and_windows(self) -> None:
        posix = self.tool.execute(
            mode="lookup", filename="/var/log/app/errors.LOG"
        )
        windows = self.tool.execute(
            mode="lookup", filename=r"C:\Users\au\Documents\report.docx"
        )
        self.assertEqual(posix["filename"], "errors.LOG")
        self.assertEqual(posix["mime"], "text/plain")
        self.assertEqual(windows["mime"], DOCX_MIME)

    def test_lookup_dual_suffix_tar_gz(self) -> None:
        result = self.tool.execute(mode="lookup", filename="backup.tar.gz")
        self.assertTrue(result["known"])
        self.assertEqual(result["extension"], ".tar.gz")
        self.assertEqual(result["mime"], "application/gzip")
        self.assertTrue(result["compound"])
        # A plain .tar describes the inner archive, not the compression.
        tar = self.tool.execute(mode="lookup", extension="tar")
        self.assertEqual(tar["mime"], "application/x-tar")
        self.assertFalse(tar["compound"])

    def test_lookup_dual_suffix_case_insensitive(self) -> None:
        result = self.tool.execute(mode="lookup", filename="PKG.TAR.ZST")
        self.assertEqual(result["extension"], ".tar.zst")
        self.assertEqual(result["mime"], "application/zstd")
        self.assertTrue(result["compound"])

    def test_lookup_dual_suffix_falls_back_to_last_segment(self) -> None:
        # "mp4.gz" is not a table compound, so the last segment wins.
        result = self.tool.execute(mode="lookup", filename="video.mp4.gz")
        self.assertEqual(result["extension"], ".gz")
        self.assertEqual(result["mime"], "application/gzip")
        self.assertFalse(result["compound"])

    def test_lookup_unknown_extension(self) -> None:
        result = self.tool.execute(mode="lookup", extension="xyzunknown")
        self.assertEqual(
            result,
            {
                "mode": "lookup",
                "input_kind": "extension",
                "filename": None,
                "extension": ".xyzunknown",
                "mime": None,
                "category": None,
                "known": False,
                "source": None,
                "compound": False,
            },
        )

    def test_lookup_filename_without_extension(self) -> None:
        result = self.tool.execute(mode="lookup", filename="README")
        self.assertIsNone(result["extension"])
        self.assertIsNone(result["mime"])
        self.assertFalse(result["known"])

    def test_lookup_dotfile_has_no_extension(self) -> None:
        # os.path.splitext semantics: a leading dot is not a separator.
        result = self.tool.execute(mode="lookup", filename=".gitignore")
        self.assertIsNone(result["extension"])
        self.assertFalse(result["known"])

    def test_lookup_trailing_dot_filename(self) -> None:
        result = self.tool.execute(mode="lookup", filename="report.")
        self.assertIsNone(result["extension"])
        self.assertFalse(result["known"])

    def test_lookup_stdlib_fallback_beyond_table(self) -> None:
        # .ps is deliberately absent from the embedded table but is a
        # long-stable entry of CPython's builtin mimetypes table.
        result = self.tool.execute(mode="lookup", extension="ps")
        self.assertTrue(result["known"])
        self.assertEqual(result["source"], "stdlib")
        self.assertEqual(result["mime"], "application/postscript")
        self.assertEqual(result["category"], "binary")

    def test_lookup_stdlib_fallback_category_by_maintype(self) -> None:
        result = self.tool.execute(mode="lookup", extension="ra")
        # RealAudio: not in the table; the stdlib maps it under audio/.
        if result["source"] == "stdlib":
            self.assertEqual(result["mime"], "audio/x-pn-realaudio")
            self.assertEqual(result["category"], "audio")
        else:  # pragma: no cover - guards against table growth only
            self.assertEqual(result["source"], "table")

    # ------------------------------------------------------------------ #
    # reverse mode
    # ------------------------------------------------------------------ #

    def test_reverse_popularity_order(self) -> None:
        result = self.tool.execute(mode="reverse", mime="image/jpeg")
        self.assertEqual(
            result,
            {
                "mode": "reverse",
                "mime": "image/jpeg",
                "extensions": [".jpg", ".jpeg"],
                "category": "image",
                "known": True,
            },
        )

    def test_reverse_yaml_both_spellings(self) -> None:
        result = self.tool.execute(mode="reverse", mime="text/yaml")
        self.assertEqual(result["extensions"], [".yaml", ".yml"])
        self.assertEqual(result["category"], "text")

    def test_reverse_gzip_includes_dual_suffix(self) -> None:
        result = self.tool.execute(mode="reverse", mime="application/gzip")
        self.assertEqual(result["extensions"], [".gz", ".tgz", ".tar.gz"])
        self.assertEqual(result["category"], "archive")

    def test_reverse_normalizes_case_and_parameters(self) -> None:
        result = self.tool.execute(
            mode="reverse", mime="IMAGE/JPEG; charset=binary"
        )
        self.assertEqual(result["mime"], "image/jpeg")
        self.assertEqual(result["extensions"], [".jpg", ".jpeg"])

    def test_reverse_single_extension_type(self) -> None:
        result = self.tool.execute(mode="reverse", mime="application/pdf")
        self.assertEqual(result["extensions"], [".pdf"])
        self.assertEqual(result["category"], "binary")

    def test_reverse_unknown_mime_is_not_an_error(self) -> None:
        result = self.tool.execute(mode="reverse", mime="application/x-bogus")
        self.assertEqual(
            result,
            {
                "mode": "reverse",
                "mime": "application/x-bogus",
                "extensions": [],
                "category": None,
                "known": False,
            },
        )

    def test_reverse_is_table_only(self) -> None:
        # Documented limitation: reverse consults the embedded table
        # only, so a stdlib-only type is unknown here.
        result = self.tool.execute(mode="reverse", mime="audio/x-pn-realaudio")
        self.assertFalse(result["known"])
        self.assertEqual(result["extensions"], [])

    # ------------------------------------------------------------------ #
    # category mode
    # ------------------------------------------------------------------ #

    def test_category_font_listing_sorted(self) -> None:
        result = self.tool.execute(mode="category", category="font")
        self.assertEqual(result["mode"], "category")
        self.assertEqual(result["category"], "font")
        self.assertEqual(result["count"], 6)
        self.assertEqual(
            [entry["extension"] for entry in result["entries"]],
            [".eot", ".otf", ".ttc", ".ttf", ".woff", ".woff2"],
        )
        by_extension = {
            entry["extension"]: entry["mime"] for entry in result["entries"]
        }
        self.assertEqual(by_extension[".woff2"], "font/woff2")
        self.assertEqual(by_extension[".eot"], "application/vnd.ms-fontobject")

    def test_category_image_contains_svg(self) -> None:
        result = self.tool.execute(mode="category", category="image")
        pairs = {
            entry["extension"]: entry["mime"] for entry in result["entries"]
        }
        self.assertEqual(pairs[".svg"], "image/svg+xml")
        self.assertEqual(pairs[".png"], "image/png")
        # Sorted by extension, every category is non-empty.
        extensions = [entry["extension"] for entry in result["entries"]]
        self.assertEqual(extensions, sorted(extensions))

    def test_category_model_three_d_formats(self) -> None:
        result = self.tool.execute(mode="category", category="model")
        self.assertEqual(result["count"], 8)
        pairs = {
            entry["extension"]: entry["mime"] for entry in result["entries"]
        }
        self.assertEqual(pairs[".gltf"], "model/gltf+json")
        self.assertEqual(pairs[".glb"], "model/gltf-binary")
        self.assertEqual(pairs[".fbx"], "application/octet-stream")

    def test_category_every_category_non_empty_and_sorted(self) -> None:
        for category in MimeTypeTool.CATEGORIES:
            with self.subTest(category=category):
                result = self.tool.execute(mode="category", category=category)
                self.assertGreaterEqual(result["count"], 1)
                extensions = [
                    entry["extension"] for entry in result["entries"]
                ]
                self.assertEqual(extensions, sorted(extensions))
                for entry in result["entries"]:
                    self.assertTrue(entry["extension"].startswith("."))
                    self.assertIn("/", entry["mime"])

    # ------------------------------------------------------------------ #
    # sniff mode
    # ------------------------------------------------------------------ #

    def test_sniff_json_object_parses(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample='{"name": "au", "stars": 2}'
        )
        self.assertEqual(result["mime"], "application/json")
        self.assertEqual(result["category"], "text")
        self.assertFalse(result["is_base64"])
        self.assertFalse(result["truncated"])
        self.assertIn("parses as a JSON object", result["evidence"][0])

    def test_sniff_json_array(self) -> None:
        result = self.tool.execute(mode="sniff", sample='[1, 2, 3, "x"]')
        self.assertEqual(result["mime"], "application/json")
        self.assertIn("parses as a JSON array", result["evidence"][0])

    def test_sniff_json_truncated_uses_shape(self) -> None:
        sample = '{"key": "' + "x" * 2000 + '"}'
        result = self.tool.execute(mode="sniff", sample=sample)
        self.assertEqual(result["mime"], "application/json")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["analyzed_chars"], 1024)
        self.assertIn("shape", result["evidence"][0])

    def test_sniff_utf8_bom_plain_text(self) -> None:
        result = self.tool.execute(mode="sniff", sample="\ufeffhello world")
        self.assertEqual(result["mime"], "text/plain")
        self.assertIn(
            "UTF-8 BOM (U+FEFF) present at the start", result["evidence"]
        )
        self.assertIn(
            "no structured text signature", result["evidence"][0]
        )

    def test_sniff_utf8_bom_with_json(self) -> None:
        result = self.tool.execute(mode="sniff", sample='\ufeff{"a": 1}')
        self.assertEqual(result["mime"], "application/json")
        self.assertEqual(len(result["evidence"]), 2)
        self.assertIn("UTF-8 BOM", result["evidence"][1])

    def test_sniff_xml_declaration(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample='<?xml version="1.0" encoding="UTF-8"?>\n'
            "<catalog><book /></catalog>"
        )
        self.assertEqual(result["mime"], "application/xml")
        self.assertIn("XML declaration", result["evidence"][0])

    def test_sniff_html(self) -> None:
        result = self.tool.execute(
            mode="sniff",
            sample="<!DOCTYPE html>\n<html><head><title>t</title>"
            "</head><body>hi</body></html>",
        )
        self.assertEqual(result["mime"], "text/html")
        self.assertIn("HTML markup detected", result["evidence"][0])

    def test_sniff_html_via_body_tag(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample="random intro\n<body>\nmore\n</body>"
        )
        self.assertEqual(result["mime"], "text/html")

    def test_sniff_markdown_heading(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample="# Title\n\nSome prose with, commas."
        )
        self.assertEqual(result["mime"], "text/markdown")
        self.assertIn("ATX heading", result["evidence"][0])

    def test_sniff_csv_consistent_columns(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample="name,age,city\nalice,30,ny\nbob,25,sf"
        )
        self.assertEqual(result["mime"], "text/csv")
        self.assertEqual(result["category"], "text")
        self.assertIn(
            "3 non-empty lines each with 3 fields", result["evidence"][0]
        )

    def test_sniff_csv_rejects_inconsistent_columns(self) -> None:
        result = self.tool.execute(
            mode="sniff", sample="name,age\nalice,30,ny\nbob"
        )
        self.assertEqual(result["mime"], "text/plain")

    def test_sniff_base64_charset(self) -> None:
        result = self.tool.execute(mode="sniff", sample=BASE64_SAMPLE)
        self.assertEqual(result["mime"], "application/octet-stream")
        self.assertEqual(result["category"], "binary")
        self.assertTrue(result["is_base64"])
        self.assertIn("Base64 alphabet", result["evidence"][0])

    def test_sniff_base64_rejects_ordinary_words(self) -> None:
        result = self.tool.execute(mode="sniff", sample="hello world")
        self.assertEqual(result["mime"], "text/plain")
        self.assertFalse(result["is_base64"])

    def test_sniff_base64_rejects_squashed_lowercase_prose(self) -> None:
        # Pure lowercase letters match the bare Base64 alphabet but
        # real Base64 of binary data always mixes in digits, uppercase
        # or '+/=' — squashed prose stays plain text.
        result = self.tool.execute(mode="sniff", sample="word " * 40)
        self.assertEqual(result["mime"], "text/plain")
        self.assertFalse(result["is_base64"])

    def test_sniff_plain_text_default(self) -> None:
        sample = "The quick brown fox jumps over 13 dogs."
        result = self.tool.execute(mode="sniff", sample=sample)
        self.assertEqual(result["mime"], "text/plain")
        self.assertEqual(result["category"], "text")
        self.assertIn("no structured text signature", result["evidence"][0])
        self.assertFalse(result["truncated"])
        self.assertEqual(result["analyzed_chars"], len(sample))

    def test_sniff_reports_truncation(self) -> None:
        sample = "word. " * 500  # 3000 characters of plain prose
        result = self.tool.execute(mode="sniff", sample=sample)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["analyzed_chars"], 1024)
        self.assertEqual(result["mime"], "text/plain")

    def test_sniff_bom_only_sample(self) -> None:
        result = self.tool.execute(mode="sniff", sample="\ufeff")
        self.assertEqual(result["mime"], "text/plain")
        self.assertEqual(len(result["evidence"]), 2)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="identify", extension="png")
        self.assert_invalid(mode=None, extension="png")
        self.assert_invalid(mode=123, extension="png")

    def test_lookup_requires_exactly_one_input(self) -> None:
        self.assert_invalid(mode="lookup")
        self.assert_invalid(mode="lookup", filename=None, extension=None)
        self.assert_invalid(
            mode="lookup", filename="a.png", extension="png"
        )

    def test_invalid_filename(self) -> None:
        for bad in (None, 123, True, b"a.png", ""):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="lookup", filename=bad)
        self.assert_invalid(mode="lookup", filename="a\x00.png")
        self.assert_invalid(mode="lookup", filename="x" * 4097)

    def test_invalid_extension(self) -> None:
        for bad in (None, 123, True, b"png", "", "p n g", "a/b", "\\png",
                    ".png v1", ".x" * 30):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="lookup", extension=bad)

    def test_invalid_mime(self) -> None:
        for bad in (None, 123, True, b"image/png", "", "   ",
                    "textplain", "/jpeg", "image/", "a//b", "a b/c"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="reverse", mime=bad)

    def test_invalid_category(self) -> None:
        for bad in ("pictures", None, 123, True, "Text"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="category", category=bad)

    def test_invalid_sample(self) -> None:
        for bad in (None, 123, True, b"hello", ""):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="sniff", sample=bad)
        self.assert_invalid(mode="sniff", sample="a" * 100_001)

    def test_sample_at_limit_is_accepted(self) -> None:
        result = self.tool.execute(mode="sniff", sample="a" * 100_000)
        self.assertEqual(result["analyzed_chars"], 1024)
        self.assertTrue(result["truncated"])

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectMimeTypeTool, MimeTypeTool)
        self.assertEqual(self.tool.name, "mime_type_tool")
        self.assertIn("MIME type", self.tool.description)
        self.assertEqual(
            MimeTypeTool.MODES,
            ("lookup", "reverse", "category", "sniff"),
        )
        self.assertEqual(len(MimeTypeTool.CATEGORIES), 9)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("MimeTypeTool", __all__)


if __name__ == "__main__":
    unittest.main()
