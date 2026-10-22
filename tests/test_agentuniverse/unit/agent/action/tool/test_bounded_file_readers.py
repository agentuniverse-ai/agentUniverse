# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_bounded_file_readers.py

"""Known-answer and bounds-discipline tests for the bounded file readers.

These readers supersede the competing reader additions #3324 #3327 #3328
#3329: stdlib-only, strictly bounded inputs, deterministic output, and a
ValueError that quotes the offending value on every discipline failure.
"""

import tempfile
import unittest
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.reader.file.bounded_eml_reader import (
    BoundedEmlReader,
)
from agentuniverse.agent.action.knowledge.reader.file.bounded_html_reader import (
    BoundedHtmlReader,
)
from agentuniverse.agent.action.knowledge.reader.file.bounded_xml_reader import (
    BoundedXmlReader,
)
from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
)
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager

_EML_HTML = "<p>HTML body 2</p>"


def _eml_bytes() -> bytes:
    message = MIMEMultipart()
    message["Subject"] = "Project   Phoenix   Status"  # 3x spaces: collapse discipline
    message["From"] = "Alice <alice@example.com>"
    message["To"] = "Bob <bob@example.com>"
    message["Cc"] = "Carol <carol@example.com>"
    message["Date"] = "Sun, 19 Oct 2026 12:00:00 +0000"
    message["Message-ID"] = "<id-1@example.com>"
    message.attach(MIMEText("Plain body", "plain"))
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload("BINARYPAYLOAD")  # names only; payload never decoded
    attachment.add_header("Content-Disposition", "attachment", filename="report.pdf")
    message.attach(attachment)
    return message.as_bytes()


def _eml_html_only_bytes() -> bytes:
    message = MIMEMultipart()
    message["Subject"] = "HTML only"
    message.attach(MIMEText(_EML_HTML, "html"))
    return message.as_bytes()


class TestBoundedFileReaders(unittest.TestCase):
    """Known answers, then the bounds/ValueError discipline."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)

    def _write(self, name: str, data: bytes) -> Path:
        path = self.base / name
        path.write_bytes(data)
        return path

    # --- known answers ---------------------------------------------------

    def test_eml_known_answer(self) -> None:
        path = self._write("a.eml", _eml_bytes())
        document = BoundedEmlReader().load_data(file=path)[0]
        self.assertEqual(document.text, "Plain body")
        metadata = document.metadata
        self.assertEqual(metadata["file_name"], "a.eml")
        self.assertEqual(metadata["email_subject"], "Project Phoenix Status")
        self.assertEqual(metadata["email_from"], "Alice <alice@example.com>")
        self.assertEqual(metadata["email_to"], "Bob <bob@example.com>")
        self.assertEqual(metadata["email_cc"], "Carol <carol@example.com>")
        self.assertEqual(metadata["email_message_id"], "<id-1@example.com>")
        self.assertEqual(metadata["attachment_names"], ["report.pdf"])
        self.assertEqual(metadata["attachment_count"], 1)
        self.assertNotIn("BINARYPAYLOAD", document.text)

    def test_eml_html_only_falls_back_to_shared_stripper(self) -> None:
        path = self._write("b.eml", _eml_html_only_bytes())
        document = BoundedEmlReader().load_data(file=path)[0]
        self.assertEqual(document.text, "HTML body 2")
        self.assertEqual(document.metadata["email_subject"], "HTML only")

    def test_html_known_answer(self) -> None:
        path = self._write("c.html", (
            b"<html><head><title>My  Title</title></head><body>"
            b"<script>ignored</script><p>hello world</p><p>line two</p>"
            b"</body></html>"))
        document = BoundedHtmlReader().load_data(file=path)[0]
        self.assertEqual(document.text, "hello world\nline two")
        self.assertEqual(document.metadata["html_title"], "My Title")
        self.assertEqual(document.metadata["file_name"], "c.html")
        self.assertNotIn("ignored", document.text)

    def test_xml_known_answer(self) -> None:
        path = self._write("d.xml",
                           b'<?xml version="1.0"?><root id="r1">'
                           b"<a>alpha<b>beta</b></a></root>")
        document = BoundedXmlReader().load_data(file=path)[0]
        self.assertEqual(document.text, "alpha beta")
        self.assertEqual(document.metadata["xml_root"], "root")

    # --- registration (the shared-hunk mechanic) --------------------------

    def test_readers_are_registered_in_the_shared_tables(self) -> None:
        self.assertIs(DEFAULT_FILE_READERS[".eml"], BoundedEmlReader)
        self.assertIs(DEFAULT_FILE_READERS[".html"], BoundedHtmlReader)
        self.assertIs(DEFAULT_FILE_READERS[".htm"], BoundedHtmlReader)
        self.assertIs(DEFAULT_FILE_READERS[".xml"], BoundedXmlReader)
        self.assertEqual(ReaderManager.DEFAULT_READER["eml"], "default_bounded_eml_reader")
        self.assertEqual(ReaderManager.DEFAULT_READER["html"], "default_bounded_html_reader")
        self.assertEqual(ReaderManager.DEFAULT_READER["xml"], "default_bounded_xml_reader")

    # --- bounds discipline: oversize raises, quoting the offending value --

    def test_oversize_files_raise_with_quoted_values(self) -> None:
        cases = (
            (BoundedEmlReader, "e.eml", b"x" * 11, "EML file is 11 bytes"),
            (BoundedHtmlReader, "f.html", b"y" * 11, "HTML file is 11 bytes"),
            (BoundedXmlReader, "g.xml", b"z" * 11, "XML file is 11 bytes"),
        )
        for reader_cls, name, data, expected in cases:
            path = self._write(name, data)
            with self.assertRaises(ValueError) as context:
                reader_cls(max_file_bytes=10).load_data(file=path)
            self.assertIn(expected, str(context.exception))
            self.assertIn("max_file_bytes=10", str(context.exception))

    def test_oversize_file_is_read_bounded_not_fully(self) -> None:
        path = self._write("h.html", b"y" * (10 * 1024 * 1024 + 5))
        with self.assertRaises(ValueError) as context:
            BoundedHtmlReader().load_data(file=path)
        # the error quotes the *bounded read* (max_file_bytes + 1), not the
        # 10485765-byte file: the read really stopped early
        self.assertIn("10485761 bytes", str(context.exception))
        self.assertIn("max_file_bytes=10485760", str(context.exception))

    def test_xml_depth_guard_raises(self) -> None:
        path = self._write("deep.xml",
                           b"<root>" + b"<a>" * 80 + b"X" + b"</a>" * 80 + b"</root>")
        with self.assertRaises(ValueError) as context:
            BoundedXmlReader().load_data(file=path)
        self.assertIn("depth 65", str(context.exception))
        self.assertIn("max_depth=64", str(context.exception))

    def test_xml_text_truncation(self) -> None:
        path = self._write("long.xml", b"<r>0123456789ABCDEF</r>")
        document = BoundedXmlReader(max_text_chars=10).load_data(file=path)[0]
        self.assertEqual(document.text, "0123456789")

    # --- misc discipline ---------------------------------------------------

    def test_ext_info_is_passed_through(self) -> None:
        path = self._write("i.txt-eml", b"<!DOCTYPEkbd><x>1</x>")
        for reader_cls, name in ((BoundedEmlReader, "j.eml"), (BoundedHtmlReader, "k.html"),
                                 (BoundedXmlReader, "l.xml")):
            path = self._write(name, (b"Subject: s\r\n\r\nbody" if name.endswith(".eml")
                                      else b"<p>2</p>" if name.endswith(".html") else b"<x>1</x>"))
            document = reader_cls().load_data(file=path, ext_info={"k": "v"})[0]
            self.assertEqual(document.metadata["k"], "v")

    def test_positional_call_shape_also_binds(self) -> None:
        path = self._write("m.xml", b"<x>1</x>")
        document = BoundedXmlReader().load_data(path)[0]
        self.assertEqual(document.metadata["xml_root"], "x")

    def test_same_input_is_deterministic(self) -> None:
        for reader_cls, name, data in (
                (BoundedEmlReader, "n.eml", _eml_bytes()),
                (BoundedHtmlReader, "o.html", b"<p>3</p>"),
                (BoundedXmlReader, "p.xml", b"<x>4</x>"),
        ):
            path = self._write(name, data)
            first = reader_cls().load_data(file=path)[0]
            second = reader_cls().load_data(file=path)[0]
            self.assertEqual((first.text, first.metadata), (second.text, second.metadata))

    def test_bounds_validation_quotes_the_offending_value(self) -> None:
        for assertion in (
                (BoundedEmlReader(max_file_bytes=-1), "-1"),
                (BoundedHtmlReader(max_text_chars=-5), "-5"),
                (BoundedXmlReader(max_depth=0), "0"),
        ):
            with self.assertRaises(ValueError) as context:
                assertion[0]._validate_config()
            self.assertIn(assertion[1], str(context.exception))

    def test_bad_bound_fails_at_component_configer_load(self) -> None:
        with self.assertRaises(ValueError) as context:
            BoundedHtmlReader()._initialize_by_component_configer(
                SimpleNamespace(name="x", description="d", max_file_bytes="big"))
        self.assertIn("'big'", str(context.exception))


if __name__ == "__main__":
    unittest.main()
