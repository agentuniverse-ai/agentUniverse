# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_xml_reader.py

"""Tests for the XmlReader (.xml structure-preserving) reader."""

import io
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import agentuniverse.agent.action.knowledge.reader.file.xml_reader as xml_module
from agentuniverse.agent.action.knowledge.reader.file.file_reader import DEFAULT_FILE_READERS, FileReader
from agentuniverse.agent.action.knowledge.reader.file.xml_reader import XmlReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(xml_module.__file__), "xml_reader.yaml")

_CATALOG_XML = """<?xml version="1.0" encoding="utf-8"?>
<catalog>
  <book id="b1">
    <title>Hyperion</title>
    <author>Dan Simmons</author>
  </book>
  <book id="b2">
    <title>Neuromancer</title>
    <author>William Gibson</author>
  </book>
</catalog>
"""


def _write(tmp_dir, name, content):
    path = Path(tmp_dir) / name
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


def _read(path, **kwargs):
    return XmlReader(**kwargs).load_data(file=Path(path))[0]


class TestXmlExtraction(unittest.TestCase):
    """Tree serialization keeps structural context in the text."""

    def test_nested_paths_and_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = _read(path)
        self.assertIn("catalog/book/title: Hyperion", doc.text)
        self.assertIn("catalog/book/author: William Gibson", doc.text)
        # Indentation whitespace does not produce junk lines.
        for line in doc.text.splitlines():
            self.assertIn(": ", line)

    def test_document_order_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = _read(path)
        lines = doc.text.splitlines()
        self.assertLess(lines.index("catalog/book/title: Hyperion"), lines.index("catalog/book/title: Neuromancer"))

    def test_attributes_excluded_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = _read(path)
        self.assertNotIn("b1", doc.text)

    def test_attributes_included_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = _read(path, include_attributes=True)
        self.assertIn('catalog/book [attributes]: id="b1"', doc.text)

    def test_mixed_content_tails_kept_in_order(self) -> None:
        xml = "<p>before <b>bold</b> after</p>"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "mixed.xml", xml)
            doc = _read(path)
        lines = doc.text.splitlines()
        self.assertEqual(lines, ["p: before", "p/b: bold", "p: after"])

    def test_namespaces_stripped_to_local_names(self) -> None:
        xml = '<root xmlns:n="http://example.com/ns">' "<n:item>value</n:item></root>"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "ns.xml", xml)
            doc = _read(path)
        self.assertIn("root/item: value", doc.text)
        self.assertNotIn("http://example.com", doc.text)
        self.assertEqual(doc.metadata["root_tag"], "root")

    def test_metadata_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = _read(path)
        self.assertEqual(doc.metadata["file_name"], "catalog.xml")
        self.assertEqual(doc.metadata["root_tag"], "catalog")
        # root + 2 books + 4 leaves
        self.assertEqual(doc.metadata["element_count"], 7)

    def test_empty_root_yields_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "empty.xml", "<root/>")
            doc = _read(path)
        self.assertEqual(doc.text, "")
        self.assertEqual(doc.metadata["element_count"], 1)

    def test_utf8_chinese_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "cn.xml", "<根><条目>中文内容</条目></根>")
            doc = _read(path)
        self.assertIn("根/条目: 中文内容", doc.text)

    def test_declared_encoding_honored(self) -> None:
        xml = '<?xml version="1.0" encoding="latin-1"?><r><t>café</t></r>'
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "latin.xml", xml.encode("latin-1"))
            doc = _read(path)
        self.assertIn("café", doc.text)

    def test_ext_info_merged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = XmlReader().load_data(file=Path(path), ext_info={"src": "s3"})[0]
        self.assertEqual(doc.metadata["src"], "s3")
        self.assertEqual(doc.metadata["root_tag"], "catalog")


class TestXmlSafety(unittest.TestCase):
    """DTD/XXE/entity-bomb refusal and size/depth bounds."""

    def test_doctype_rejected(self) -> None:
        xml = '<!DOCTYPE r [<!ENTITY a "text">]><r>&a;</r>'
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "dtd.xml", xml)
            with self.assertRaises(ValueError) as ctx:
                _read(path)
        self.assertIn("DTD/ENTITY", str(ctx.exception))

    def test_billion_laughs_rejected_before_expansion(self) -> None:
        xml = (
            '<?xml version="1.0"?>'
            "<!DOCTYPE lolz ["
            '<!ENTITY lol "lol">'
            '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;">'
            "]><lolz>&lol2;</lolz>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "laughs.xml", xml)
            with self.assertRaises(ValueError):
                _read(path)

    def test_utf16_dtd_rejected_before_entity_expansion(self) -> None:
        xml = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE r [<!ENTITY a "expanded">]><r>&a;</r>'
        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            with self.subTest(encoding=encoding), self.assertRaisesRegex(ValueError, "DTD/ENTITY"):
                XmlReader().load_data(file=io.BytesIO(xml.encode(encoding)))

    def test_utf16_without_dtd_is_supported(self) -> None:
        raw = '<?xml version="1.0" encoding="UTF-16"?><root>安全</root>'.encode("utf-16")
        self.assertEqual(XmlReader().load_data(file=io.BytesIO(raw))[0].text, "root: 安全")

    def test_depth_bound_checked_before_malformed_tail(self) -> None:
        # Abort as soon as nesting crosses the limit, before parsing the
        # remainder or constructing an entire hostile tree.
        raw = ("<a>" * 6 + "<broken").encode()
        with self.assertRaisesRegex(ValueError, "max_depth"):
            XmlReader(max_depth=5).load_data(file=io.BytesIO(raw))

    def test_external_entity_dtd_rejected(self) -> None:
        xml = '<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>' "<r>&x;</r>"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "xxe.xml", xml)
            with self.assertRaises(ValueError):
                _read(path)

    def test_uppercase_doctype_also_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "upper.xml", b"<!DocType r []><r/>")
            with self.assertRaises(ValueError):
                _read(path)

    def test_malformed_xml_raises_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "bad.xml", "<root><unclosed></root>")
            with self.assertRaises(ValueError) as ctx:
                _read(path)
        self.assertIn("Failed to parse XML", str(ctx.exception))

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            XmlReader().load_data(file=Path("/nonexistent/x.xml"))

    def test_oversized_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "big.xml", b"<r>" + b"x" * 100 + b"</r>")
            with self.assertRaises(ValueError) as ctx:
                _read(path, max_file_bytes=50)
        self.assertIn("max_file_bytes", str(ctx.exception))

    def test_oversized_stream_rejected(self) -> None:
        with self.assertRaises(ValueError):
            XmlReader(max_file_bytes=10).load_data(file=io.BytesIO(b"<r>xxxxxxxxxxxxxxxx</r>"))

    def test_depth_bomb_rejected(self) -> None:
        xml = "<a>" * 30 + "deep" + "</a>" * 30
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "deep.xml", xml)
            with self.assertRaises(ValueError) as ctx:
                _read(path, max_depth=5)
        self.assertIn("max_depth", str(ctx.exception))

    def test_text_stream_rejected(self) -> None:
        with self.assertRaises(TypeError):
            XmlReader().load_data(file=io.StringIO("<r/>"))

    def test_unsupported_input_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            XmlReader().load_data(file=12345)


class TestXmlInputTypes(unittest.TestCase):
    def test_str_path_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "catalog.xml", _CATALOG_XML)
            doc = XmlReader().load_data(file=str(path))[0]
        self.assertIn("Hyperion", doc.text)

    def test_binary_stream_accepted(self) -> None:
        handle = io.BytesIO(_CATALOG_XML.encode("utf-8"))
        doc = XmlReader().load_data(file=handle)[0]
        self.assertIn("Neuromancer", doc.text)
        self.assertEqual(doc.metadata["file_name"], "unknown")


class TestXmlConfig(unittest.TestCase):
    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="xml", description="d", max_file_bytes=123, max_depth=7, include_attributes=True
        )
        reader = XmlReader()._initialize_by_component_configer(configer)
        self.assertEqual(reader.max_file_bytes, 123)
        self.assertEqual(reader.max_depth, 7)
        self.assertTrue(reader.include_attributes)

    def test_bad_values_raise(self) -> None:
        for bad in (
            SimpleNamespace(name="x", description="d", max_file_bytes=0),
            SimpleNamespace(name="x", description="d", max_depth=0),
        ):
            with self.assertRaises(ValueError):
                XmlReader()._initialize_by_component_configer(bad)

    def test_bad_types_raise(self) -> None:
        for bad in (
            SimpleNamespace(name="x", description="d", max_file_bytes="1MB"),
            SimpleNamespace(name="x", description="d", max_depth=2.5),
            SimpleNamespace(name="x", description="d", include_attributes="yes"),
        ):
            with self.assertRaises(TypeError):
                XmlReader()._initialize_by_component_configer(bad)


class TestXmlRegistration(unittest.TestCase):
    def test_yaml_resolves_to_reader_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.READER.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module, "agentuniverse.agent.action.knowledge.reader.file.xml_reader"
        )
        self.assertEqual(component_configer.metadata_class, "XmlReader")

    def test_shipped_yaml_initializes_cleanly(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        reader = XmlReader()._initialize_by_component_configer(component_configer)
        self.assertEqual(reader.max_depth, 64)
        self.assertFalse(reader.include_attributes)

    def test_default_file_readers_routes_xml_suffix(self) -> None:
        self.assertIs(DEFAULT_FILE_READERS[".xml"], XmlReader)

    def test_reader_manager_maps_xml_type(self) -> None:
        self.assertEqual(ReaderManager.DEFAULT_READER["xml"], "default_xml_reader")

    def test_file_reader_dispatches_xml_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "dispatch.xml", "<note><body>dispatched</body></note>")
            docs = FileReader().load_data(file_paths=[Path(path)])
        self.assertEqual(len(docs), 1)
        self.assertIn("note/body: dispatched", docs[0].text)


if __name__ == "__main__":
    unittest.main()
