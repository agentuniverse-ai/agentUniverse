# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_html_file_reader.py

"""Tests for the HtmlFileReader (local .html/.htm) reader."""

import io
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import agentuniverse.agent.action.knowledge.reader.file.html_file_reader as hfr_module
from agentuniverse.agent.action.knowledge.reader.file.file_reader import DEFAULT_FILE_READERS, FileReader
from agentuniverse.agent.action.knowledge.reader.file.html_file_reader import HtmlFileReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(hfr_module.__file__), "html_file_reader.yaml")

_PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="Description" content="  A short   summary. ">
  <title>  Annual   Report  </title>
  <style>p { color: red; }</style>
  <script>var secret = "js source";</script>
</head>
<body>
  <!-- internal boilerplate comment -->
  <h1>Heading</h1>
  <p>First paragraph.</p>
  <noscript><p>enable js</p></noscript>
  <template><p>template text</p></template>
  <p>Second paragraph.</p>
</body>
</html>
"""


def _write(tmp_dir, name, content):
    path = Path(tmp_dir) / name
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


def _read(path, **kwargs):
    return HtmlFileReader(**kwargs).load_data(file=Path(path))[0]


class TestHtmlExtraction(unittest.TestCase):
    """Visible text is extracted; non-content markup is not."""

    def test_title_heading_and_paragraphs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = _read(path)
        self.assertTrue(doc.text.startswith("Title: Annual Report\n"))
        self.assertIn("Heading", doc.text)
        self.assertIn("First paragraph.", doc.text)
        self.assertIn("Second paragraph.", doc.text)

    def test_script_style_comment_noscript_template_stripped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = _read(path)
        for forbidden in ("js source", "color: red", "boilerplate comment", "enable js", "template text"):
            self.assertNotIn(forbidden, doc.text)

    def test_metadata_title_and_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = _read(path)
        # <title> and meta content are whitespace-collapsed.
        self.assertEqual(doc.metadata["html_title"], "Annual Report")
        self.assertEqual(doc.metadata["html_description"], "A short summary.")
        self.assertEqual(doc.metadata["file_name"], "page.html")
        self.assertEqual(doc.metadata["text_length"], len(doc.text))

    def test_meta_description_case_insensitive(self) -> None:
        html = '<html><head><META NAME="description" CONTENT="desc here"></head><body>x</body></html>'
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "meta.html", html)
            doc = _read(path)
        self.assertEqual(doc.metadata["html_description"], "desc here")

    def test_title_omitted_from_text_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = _read(path, include_title_in_text=False)
        self.assertNotIn("Title:", doc.text)
        # Metadata still carries the title.
        self.assertEqual(doc.metadata["html_title"], "Annual Report")

    def test_page_without_title_or_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "plain.html", "<html><body><p>only body</p></body></html>")
            doc = _read(path)
        self.assertEqual(doc.text, "only body")
        self.assertNotIn("html_title", doc.metadata)
        self.assertNotIn("html_description", doc.metadata)

    def test_text_truncated_to_max_chars(self) -> None:
        html = "<html><body><p>" + "x" * 500 + "</p></body></html>"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "long.html", html)
            doc = _read(path, max_text_chars=100)
        self.assertEqual(len(doc.text), 100)
        self.assertEqual(doc.metadata["text_length"], 100)

    def test_empty_file_yields_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "empty.html", b"")
            doc = _read(path)
        self.assertEqual(doc.text, "")
        self.assertEqual(doc.metadata["text_length"], 0)

    def test_utf8_chinese_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "cn.html", "<html><head><title>标题</title></head><body><p>中文段落</p></body></html>")
            doc = _read(path)
        self.assertEqual(doc.metadata["html_title"], "标题")
        self.assertIn("中文段落", doc.text)

    def test_declared_latin1_encoding_honored(self) -> None:
        html = '<html><head><meta charset="latin-1"></head>' "<body><p>café</p></body></html>"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "latin.html", html.encode("latin-1"))
            doc = _read(path)
        self.assertIn("café", doc.text)

    def test_ext_info_merged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = HtmlFileReader().load_data(file=Path(path), ext_info={"crawl": "c1"})[0]
        self.assertEqual(doc.metadata["crawl"], "c1")
        self.assertEqual(doc.metadata["html_title"], "Annual Report")


class TestHtmlSafety(unittest.TestCase):
    """Bounds and input-type guards."""

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            HtmlFileReader().load_data(file=Path("/nonexistent/p.html"))

    def test_oversized_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "big.html", b"<p>" + b"x" * 100 + b"</p>")
            with self.assertRaises(ValueError) as ctx:
                _read(path, max_file_bytes=50)
        self.assertIn("max_file_bytes", str(ctx.exception))

    def test_oversized_stream_rejected(self) -> None:
        with self.assertRaises(ValueError):
            HtmlFileReader(max_file_bytes=10).load_data(file=io.BytesIO(b"<p>xxxxxxxxxxxxxxxx</p>"))

    def test_text_stream_rejected(self) -> None:
        with self.assertRaises(TypeError):
            HtmlFileReader().load_data(file=io.StringIO("<p>x</p>"))

    def test_unsupported_input_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            HtmlFileReader().load_data(file=12345)


class TestHtmlInputTypes(unittest.TestCase):
    def test_str_path_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "page.html", _PAGE)
            doc = HtmlFileReader().load_data(file=str(path))[0]
        self.assertIn("First paragraph.", doc.text)

    def test_binary_stream_accepted(self) -> None:
        handle = io.BytesIO(_PAGE.encode("utf-8"))
        doc = HtmlFileReader().load_data(file=handle)[0]
        self.assertIn("Second paragraph.", doc.text)
        self.assertEqual(doc.metadata["file_name"], "unknown")


class TestHtmlConfig(unittest.TestCase):
    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="html", description="d", max_file_bytes=123, max_text_chars=456, include_title_in_text=False
        )
        reader = HtmlFileReader()._initialize_by_component_configer(configer)
        self.assertEqual(reader.max_file_bytes, 123)
        self.assertEqual(reader.max_text_chars, 456)
        self.assertFalse(reader.include_title_in_text)

    def test_bad_values_raise(self) -> None:
        for bad in (
            SimpleNamespace(name="h", description="d", max_file_bytes=0),
            SimpleNamespace(name="h", description="d", max_text_chars=0),
        ):
            with self.assertRaises(ValueError):
                HtmlFileReader()._initialize_by_component_configer(bad)

    def test_bad_types_raise(self) -> None:
        for bad in (
            SimpleNamespace(name="h", description="d", max_file_bytes="1MB"),
            SimpleNamespace(name="h", description="d", max_text_chars=2.5),
            SimpleNamespace(name="h", description="d", include_title_in_text="yes"),
        ):
            with self.assertRaises(TypeError):
                HtmlFileReader()._initialize_by_component_configer(bad)


class TestHtmlRegistration(unittest.TestCase):
    def test_yaml_resolves_to_reader_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.READER.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module, "agentuniverse.agent.action.knowledge.reader.file.html_file_reader"
        )
        self.assertEqual(component_configer.metadata_class, "HtmlFileReader")

    def test_shipped_yaml_initializes_cleanly(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        reader = HtmlFileReader()._initialize_by_component_configer(component_configer)
        self.assertEqual(reader.max_file_bytes, 10 * 1024 * 1024)
        self.assertTrue(reader.include_title_in_text)

    def test_default_file_readers_routes_html_suffixes(self) -> None:
        self.assertIs(DEFAULT_FILE_READERS[".html"], HtmlFileReader)
        self.assertIs(DEFAULT_FILE_READERS[".htm"], HtmlFileReader)

    def test_reader_manager_maps_html_types(self) -> None:
        self.assertEqual(ReaderManager.DEFAULT_READER["html"], "default_html_file_reader")
        self.assertEqual(ReaderManager.DEFAULT_READER["htm"], "default_html_file_reader")

    def test_file_reader_dispatches_html_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "dispatch.html", "<html><body><p>dispatched content</p></body></html>")
            docs = FileReader().load_data(file_paths=[Path(path)])
        self.assertEqual(len(docs), 1)
        self.assertIn("dispatched content", docs[0].text)


if __name__ == "__main__":
    unittest.main()
