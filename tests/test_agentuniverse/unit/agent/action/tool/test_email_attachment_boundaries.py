"""Read and extract real serialized MIME attachments through public operations."""

import base64
import quopri
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

import pytest

from agentuniverse.agent.action.tool.common_tool.email_document_tool import EmailDocumentTool


def message(text="Outer body", html=False):
    result = EmailMessage()
    result["From"] = "sender@example.test"
    result["To"] = "recipient@example.test"
    result["Subject"] = "消息 subject"
    result.set_content(text)
    if html:
        result.add_alternative("<p>Outer HTML</p>", subtype="html")
    return result


def forwarded(html=False, inner_attachment=False):
    result = message("Private forwarded text", html)
    result.replace_header("Subject", "Forwarded subject")
    if html:
        result.get_payload()[1].set_content("<p>Private forwarded HTML</p>", subtype="html")
    if inner_attachment:
        result.add_attachment(b"inner bytes", maintype="application", subtype="octet-stream", filename="inside.bin")
    return result


def save(tmp_path, item):
    path = tmp_path / "message.eml"
    path.write_bytes(item.as_bytes(policy=policy.default))
    return str(path)


def execute(tool, mode, path, **kwargs):
    result = tool.execute(mode=mode, file_path=path, **kwargs)
    assert result["status"] == "success", result
    return result


@pytest.mark.parametrize("mode", ["read", "info"])
@pytest.mark.parametrize("html", [False, True])
def test_attached_message_body_is_separate_from_parent(tmp_path, mode, html):
    outer = message(html=html)
    outer.add_attachment(forwarded(html), filename="forwarded.eml")
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    result = execute(tool, mode, save(tmp_path, outer))
    if mode == "read":
        assert result["text_body"] == "Outer body"
        assert result["html_body"] == ("<p>Outer HTML</p>" if html else "")
    else:
        assert result["text_chars"] == len("Outer body")
        assert result["html_chars"] == (len("<p>Outer HTML</p>") if html else 0)
    assert not result["truncated"]


@pytest.mark.parametrize("mode", ["read", "info"])
def test_forwarded_size_matches_nonempty_extracted_message(tmp_path, mode):
    outer = message()
    outer.add_attachment(forwarded(), filename="forwarded.eml")
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    path = save(tmp_path, outer)
    metadata = execute(tool, mode, path)
    execute(tool, "extract", path, output_dir=str(tmp_path / "out"))
    payload = (tmp_path / "out/forwarded.eml").read_bytes()
    assert payload
    size = metadata["attachments"][0]["size"] if mode == "read" else metadata["attachment_bytes"]
    assert size == len(payload)


@pytest.mark.parametrize("subtype", ["rfc822", "global"])
def test_forwarded_extract_reopens_as_the_original_message(tmp_path, subtype):
    outer = message()
    outer.add_attachment(forwarded(html=True, inner_attachment=True), filename="forwarded.eml")
    outer.get_payload()[-1].set_type("message/" + subtype)
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    path = save(tmp_path, outer)
    execute(tool, "extract", path, output_dir=str(tmp_path / "out"), attachment_names=["forwarded.eml"])
    payload = (tmp_path / "out/forwarded.eml").read_bytes()
    assert payload
    child = BytesParser(policy=policy.default).parsebytes(payload)
    assert str(child["Subject"]) == "Forwarded subject"
    assert child.get_body(preferencelist=("plain",)).get_content().strip() == "Private forwarded text"
    assert child.get_body(preferencelist=("html",)).get_content().strip() == "<p>Private forwarded HTML</p>"
    parts = list(child.iter_attachments())
    assert len(parts) == 1 and parts[0].get_filename() == "inside.bin"
    assert parts[0].get_payload(decode=True) == b"inner bytes"


@pytest.mark.parametrize("limit", ["max_attachment_bytes", "max_total_attachment_bytes"])
def test_forwarded_message_is_included_in_byte_budgets(tmp_path, limit):
    outer = message()
    outer.add_attachment(forwarded(), filename="forwarded.eml")
    tool = EmailDocumentTool(base_dir=str(tmp_path), **{limit: 1})
    result = tool.execute(mode="read", file_path=save(tmp_path, outer))
    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"
    assert limit in result["error"]


def test_forwarded_body_does_not_consume_parent_body_budget(tmp_path):
    outer = message()
    outer.add_attachment(forwarded(), filename="forwarded.eml")
    tool = EmailDocumentTool(base_dir=str(tmp_path), max_body_chars=len("Outer body"))
    result = execute(tool, "read", save(tmp_path, outer))
    assert result["text_body"] == "Outer body"
    assert not result["truncated"]


def test_nested_attachment_names_are_scoped_to_the_attached_message(tmp_path):
    outer = message()
    for name in ["first.eml", "second.eml"]:
        outer.add_attachment(forwarded(inner_attachment=True), filename=name)
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    result = execute(tool, "read", save(tmp_path, outer))
    assert [item["name"] for item in result["attachments"]] == ["first.eml", "second.eml"]


def test_unnamed_attached_message_is_not_parent_body(tmp_path):
    outer = message()
    outer.add_attachment(forwarded())
    result = execute(EmailDocumentTool(base_dir=str(tmp_path)), "read", save(tmp_path, outer))
    assert result["text_body"] == "Outer body"
    assert result["attachments"] == []


def test_unnamed_text_attachment_is_not_parent_body(tmp_path):
    outer = message()
    outer.add_attachment("Private text attachment")
    result = execute(EmailDocumentTool(base_dir=str(tmp_path)), "read", save(tmp_path, outer))
    assert result["text_body"] == "Outer body"


@pytest.mark.parametrize("kind", ["binary", "text"])
def test_regular_attachment_payload_stays_byte_exact(tmp_path, kind):
    outer = message()
    payload = b"\x00\xff\r\nbytes" if kind == "binary" else b"Text attachment\n"
    if kind == "binary":
        outer.add_attachment(payload, maintype="application", subtype="octet-stream", filename="data.bin")
        name = "data.bin"
    else:
        outer.add_attachment(payload.decode(), subtype="plain", filename="notes.txt")
        name = "notes.txt"
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    path = save(tmp_path, outer)
    result = execute(tool, "read", path)
    assert result["text_body"] == "Outer body"
    execute(tool, "extract", path, output_dir=str(tmp_path / "out"))
    assert (tmp_path / "out" / name).read_bytes() == payload
    assert result["attachments"][0]["size"] == len(payload)


def test_plain_alternative_body_without_attachments_is_unchanged(tmp_path):
    result = execute(EmailDocumentTool(base_dir=str(tmp_path)), "read", save(tmp_path, message(html=True)))
    assert result["text_body"] == "Outer body"
    assert result["html_body"] == "<p>Outer HTML</p>"
    assert result["headers"]["subject"] == "消息 subject"
    assert not result["truncated"] and result["attachments"] == []


def test_named_multipart_attachment_is_preserved_as_a_mime_document(tmp_path):
    bundle = EmailMessage()
    bundle.make_mixed()
    bundle.add_attachment("Bundle text")
    bundle.add_attachment(b"bundle bytes", maintype="application", subtype="octet-stream", filename="inside.bin")
    bundle["Content-Disposition"] = 'attachment; filename="bundle.mime"'
    outer = message()
    outer.make_mixed()
    outer.attach(bundle)
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    path = save(tmp_path, outer)
    execute(tool, "extract", path, output_dir=str(tmp_path / "out"), attachment_names=["bundle.mime"])
    payload = (tmp_path / "out/bundle.mime").read_bytes()
    assert payload
    restored = BytesParser(policy=policy.default).parsebytes(payload)
    assert restored.get_content_type() == "multipart/mixed"
    parts = list(restored.iter_parts())
    assert parts[0].get_content().strip() == "Bundle text"
    assert parts[1].get_payload(decode=True) == b"bundle bytes"


@pytest.mark.parametrize("subtype", ["rfc822", "global"])
@pytest.mark.parametrize("encoding", ["base64", "quoted-printable"])
@pytest.mark.parametrize("long_subject", [False, True])
@pytest.mark.parametrize("linesep", ["\n", "\r\n"])
def test_transfer_encoded_forwarded_message_preserves_content(tmp_path, subtype, encoding, long_subject, linesep):
    child = forwarded(html=True, inner_attachment=True)
    subject = "转发 Subject " + ("x" * 180 if long_subject else "short")
    child.replace_header("Subject", subject)
    raw = child.as_bytes(policy=policy.default.clone(linesep=linesep, utf8=subtype == "global"))
    encode = base64.encodebytes if encoding == "base64" else quopri.encodestring
    part = EmailMessage()
    part["Content-Type"] = "message/" + subtype
    part["Content-Disposition"] = 'attachment; filename="forwarded.eml"'
    part["Content-Transfer-Encoding"] = encoding
    part.set_payload(encode(raw).decode("ascii"))
    outer = message()
    outer.make_mixed()
    outer.attach(part)
    tool = EmailDocumentTool(base_dir=str(tmp_path))
    path = save(tmp_path, outer)
    metadata = execute(tool, "read", path)
    assert metadata["text_body"] == "Outer body"
    execute(tool, "extract", path, output_dir=str(tmp_path / "out"))
    payload = (tmp_path / "out/forwarded.eml").read_bytes()
    restored = BytesParser(policy=policy.default).parsebytes(payload)
    assert str(restored["Subject"]) == subject
    assert restored.get_body(preferencelist=("plain",)).get_content().strip() == "Private forwarded text"
    assert restored.get_body(preferencelist=("html",)).get_content().strip() == "<p>Private forwarded HTML</p>"
    assert list(restored.iter_attachments())[0].get_payload(decode=True) == b"inner bytes"
    assert metadata["attachments"][0]["size"] == len(payload)
