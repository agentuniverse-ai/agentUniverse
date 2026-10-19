# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: test_eml_reader.py

"""Tests for the EmlReader (.eml RFC 822 / MIME email) reader."""

import base64
import io
import os
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import agentuniverse.agent.action.knowledge.reader.file.eml_reader as eml_module
from agentuniverse.agent.action.knowledge.reader.file.eml_reader import EmlReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import DEFAULT_FILE_READERS, FileReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(eml_module.__file__), "eml_reader.yaml")


def _eml_bytes(subject="Hello there", body="Plain body text", from_="alice@example.com", to="bob@example.com"):
    """Build a real RFC 822 message with the stdlib email package."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_
    msg["To"] = to
    msg["Date"] = "Wed, 01 Oct 2026 10:00:00 +0800"
    msg["Message-ID"] = "<msg-1@example.com>"
    msg.set_content(body)
    return msg.as_bytes()


def _write(tmp_dir, name, data):
    path = Path(tmp_dir) / name
    path.write_bytes(data if isinstance(data, bytes | bytearray) else data.encode("utf-8"))
    return path


def _read(path, **kwargs):
    return EmlReader(**kwargs).load_data(file=Path(path))[0]


class TestEmlReaderBasic(unittest.TestCase):
    """A simple message becomes one Document with headers in metadata."""

    def test_plain_message_text_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "mail.eml", _eml_bytes())
            doc = _read(path)
        self.assertIn("Subject: Hello there", doc.text)
        self.assertIn("Plain body text", doc.text)
        self.assertEqual(doc.metadata["file_name"], "mail.eml")
        self.assertEqual(doc.metadata["email_subject"], "Hello there")
        self.assertEqual(doc.metadata["email_from"], "alice@example.com")
        self.assertEqual(doc.metadata["email_to"], "bob@example.com")
        self.assertEqual(doc.metadata["email_message_id"], "<msg-1@example.com>")
        self.assertIn("2026", doc.metadata["email_date"])
        self.assertEqual(doc.metadata["attachment_count"], 0)
        self.assertNotIn("attachment_names", doc.metadata)

    def test_str_path_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "mail.eml", _eml_bytes(body="str path body"))
            doc = EmlReader().load_data(file=str(path))[0]
        self.assertIn("str path body", doc.text)

    def test_binary_file_object_accepted(self) -> None:
        handle = io.BytesIO(_eml_bytes(body="binary stream body"))
        doc = EmlReader().load_data(file=handle)[0]
        self.assertIn("binary stream body", doc.text)
        self.assertEqual(doc.metadata["file_name"], "unknown")

    def test_text_file_object_accepted(self) -> None:
        handle = io.StringIO(_eml_bytes(body="text stream body").decode("utf-8"))
        doc = EmlReader().load_data(file=handle)[0]
        self.assertIn("text stream body", doc.text)

    def test_ext_info_merged_into_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "mail.eml", _eml_bytes())
            doc = EmlReader().load_data(file=Path(path), ext_info={"batch": "b1"})[0]
        self.assertEqual(doc.metadata["batch"], "b1")
        self.assertEqual(doc.metadata["email_subject"], "Hello there")

    def test_include_headers_false_yields_body_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "mail.eml", _eml_bytes(body="only me"))
            doc = _read(path, include_headers_in_text=False)
        self.assertEqual(doc.text, "only me")
        # Metadata still carries the full headers.
        self.assertEqual(doc.metadata["email_subject"], "Hello there")

    def test_headerless_message_still_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "bare.eml", b"just a bare body")
            doc = _read(path)
        self.assertIn("just a bare body", doc.text)


class TestEmlReaderMultipart(unittest.TestCase):
    """Multipart handling: plain preferred, HTML stripped, attachments named."""

    def test_alternative_prefers_plain_over_html(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "alt"
        msg.set_content("the plain version")
        msg.add_alternative("<html><body><p>the html version</p></body></html>", subtype="html")
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "alt.eml", msg.as_bytes())
            doc = _read(path)
        self.assertIn("the plain version", doc.text)
        self.assertNotIn("html version", doc.text)

    def test_html_only_message_strips_tags_scripts_styles(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "html only"
        msg.set_content(
            "<html><head><style>p {color: red}</style>"
            "<script>var evil = 1;</script></head>"
            "<body><p>visible text</p></body></html>",
            subtype="html",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "html.eml", msg.as_bytes())
            doc = _read(path)
        self.assertIn("visible text", doc.text)
        for forbidden in ("<p>", "color: red", "var evil"):
            self.assertNotIn(forbidden, doc.text)

    def test_attachment_named_but_never_decoded(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "with attachment"
        msg.set_content("body stays clean")
        msg.add_attachment(
            b"\x00\x01\x02MALICIOUS", maintype="application", subtype="octet-stream", filename="evil.bin"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "att.eml", msg.as_bytes())
            doc = _read(path)
        self.assertIn("body stays clean", doc.text)
        self.assertNotIn("MALICIOUS", doc.text)
        self.assertEqual(doc.metadata["attachment_count"], 1)
        self.assertEqual(doc.metadata["attachment_names"], ["evil.bin"])

    def test_unnamed_attachment_counted(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "unnamed"
        msg.set_content("body")
        msg.add_attachment(b"data", maintype="application", subtype="octet-stream")
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "unnamed.eml", msg.as_bytes())
            doc = _read(path)
        self.assertEqual(doc.metadata["attachment_count"], 1)
        self.assertNotIn("attachment_names", doc.metadata)

    def test_attachment_names_list_is_capped(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "many"
        msg.set_content("body")
        for i in range(3):
            msg.add_attachment(b"x", maintype="application", subtype="octet-stream", filename=f"f{i}.bin")
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "many.eml", msg.as_bytes())
            with patch.object(eml_module, "_MAX_ATTACHMENT_NAMES", 2):
                doc = _read(path)
        self.assertEqual(doc.metadata["attachment_count"], 3)
        self.assertEqual(len(doc.metadata["attachment_names"]), 2)

    def test_multiple_plain_parts_concatenated(self) -> None:
        raw = (
            b"Subject: multi\r\n"
            b"MIME-Version: 1.0\r\n"
            b"Content-Type: multipart/mixed; boundary=BB\r\n"
            b"\r\n--BB\r\nContent-Type: text/plain\r\n\r\nfirst part\r\n"
            b"--BB\r\nContent-Type: text/plain\r\n\r\nsecond part\r\n"
            b"--BB--\r\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "multi.eml", raw)
            doc = _read(path)
        self.assertIn("first part", doc.text)
        self.assertIn("second part", doc.text)


class TestEmlReaderCharsets(unittest.TestCase):
    """Charset handling degrades instead of crashing."""

    def test_utf8_chinese_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "cn.eml", _eml_bytes(subject="会议通知", body="这是一封中文邮件"))
            doc = _read(path)
        self.assertEqual(doc.metadata["email_subject"], "会议通知")
        self.assertIn("这是一封中文邮件", doc.text)

    def test_gbk_charset_body(self) -> None:
        payload = base64.b64encode("中文内容GBK".encode("gbk")).decode()
        raw = (
            "Subject: gbk\r\nMIME-Version: 1.0\r\n"
            "Content-Type: text/plain; charset=gbk\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n" + payload + "\r\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "gbk.eml", raw.encode("ascii"))
            doc = _read(path)
        self.assertIn("中文内容GBK", doc.text)

    def test_unknown_charset_falls_back_to_replacement(self) -> None:
        payload = base64.b64encode(b"hello bytes").decode()
        raw = (
            "Subject: bogus\r\nMIME-Version: 1.0\r\n"
            "Content-Type: text/plain; charset=bogus-999\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n" + payload + "\r\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "bogus.eml", raw.encode("ascii"))
            doc = _read(path)
        self.assertIn("hello bytes", doc.text)


class TestEmlReaderSafety(unittest.TestCase):
    """Bounds and sanitization guards against hostile messages."""

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            EmlReader().load_data(file=Path("/nonexistent/mail.eml"))

    def test_oversized_path_rejected_before_full_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "big.eml", _eml_bytes(body="x" * 100))
            with self.assertRaises(ValueError) as ctx:
                _read(path, max_file_bytes=50)
        self.assertIn("max_file_bytes", str(ctx.exception))

    def test_oversized_stream_rejected(self) -> None:
        handle = io.BytesIO(_eml_bytes(body="x" * 100))
        with self.assertRaises(ValueError):
            EmlReader(max_file_bytes=50).load_data(file=handle)

    def test_part_bomb_rejected(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "bomb"
        msg.set_content("part one")
        msg.add_alternative("<p>part two</p>", subtype="html")
        msg.add_alternative("<p>part three</p>", subtype="html")
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "bomb.eml", msg.as_bytes())
            with self.assertRaises(ValueError) as ctx:
                _read(path, max_parts=2)
        self.assertIn("max_parts", str(ctx.exception))

    def test_header_newlines_cannot_inject_metadata(self) -> None:
        raw = b"Subject: evil\nX-Injected: yes\nFrom: a@b.example\n\nbody"
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "inject.eml", raw)
            doc = _read(path)
        for key, value in doc.metadata.items():
            if isinstance(value, str):
                self.assertNotIn("\n", value, key)

    def test_long_header_truncated(self) -> None:
        raw = ("Subject: " + "x" * 5000 + "\r\n\r\nbody").encode()
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "long.eml", raw)
            doc = _read(path)
        self.assertLessEqual(len(doc.metadata["email_subject"]), 2000)

    def test_unsupported_input_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            EmlReader().load_data(file=12345)


class TestEmlReaderConfig(unittest.TestCase):
    """Component-configer initialization validates the safety bounds."""

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="eml", description="d", max_file_bytes=123, max_parts=7, include_headers_in_text=False
        )
        reader = EmlReader()._initialize_by_component_configer(configer)
        self.assertEqual(reader.max_file_bytes, 123)
        self.assertEqual(reader.max_parts, 7)
        self.assertFalse(reader.include_headers_in_text)

    def test_bad_values_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="eml", description="d", max_file_bytes=0),
            SimpleNamespace(name="eml", description="d", max_parts=0),
        ):
            with self.assertRaises(ValueError):
                EmlReader()._initialize_by_component_configer(bad)

    def test_bad_types_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="eml", description="d", max_file_bytes="1MB"),
            SimpleNamespace(name="eml", description="d", max_parts=2.5),
            SimpleNamespace(name="eml", description="d", include_headers_in_text="yes"),
        ):
            with self.assertRaises(TypeError):
                EmlReader()._initialize_by_component_configer(bad)


class TestEmlReaderRegistration(unittest.TestCase):
    """Shipped yaml resolves and both default registries route .eml here."""

    def test_yaml_resolves_to_reader_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.READER.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module, "agentuniverse.agent.action.knowledge.reader.file.eml_reader"
        )
        self.assertEqual(component_configer.metadata_class, "EmlReader")

    def test_default_file_readers_routes_eml_suffix(self) -> None:
        self.assertIs(DEFAULT_FILE_READERS[".eml"], EmlReader)

    def test_reader_manager_maps_eml_type(self) -> None:
        self.assertEqual(ReaderManager.DEFAULT_READER["eml"], "default_eml_reader")

    def test_extracted_eml_attachment_routes_through_file_reader(self) -> None:
        from agentuniverse.agent.action.tool.common_tool.email_document_tool import EmailDocumentTool

        # Exercise the producer's output paths, including an uppercase
        # extension, rather than reconstructing a reader-specific path.
        message = EmailMessage()
        message.set_content("Attachment container")
        message.add_attachment(
            _eml_bytes(subject="Attached message", body="Extracted attachment content"),
            maintype="application",
            subtype="octet-stream",
            filename="attached.EML",
        )
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "container.eml", message.as_bytes())
            result = EmailDocumentTool(base_dir=tmp).execute(
                mode="extract", file_path="container.eml", output_dir="downloads"
            )
            self.assertEqual(result["status"], "success", result)
            paths = [Path(path) for path in result["output_paths"]]
            self.assertEqual([path.name for path in paths], ["attached.EML"])
            docs = FileReader().load_data(file_paths=paths, ext_info={"source": "attachment"})

        self.assertEqual(len(docs), 1)
        self.assertIn("Extracted attachment content", docs[0].text)
        self.assertEqual(docs[0].metadata["email_subject"], "Attached message")
        self.assertEqual(docs[0].metadata["source"], "attachment")

    def test_file_reader_dispatches_eml_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "dispatch.eml", _eml_bytes(subject="Dispatched", body="routed through FileReader"))
            docs = FileReader().load_data(file_paths=[Path(path)])
        self.assertEqual(len(docs), 1)
        self.assertIn("routed through FileReader", docs[0].text)
        self.assertEqual(docs[0].metadata["email_subject"], "Dispatched")


if __name__ == "__main__":
    unittest.main()
