"""PDF and email output modes must preserve a concurrent successful writer."""

import threading
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

import pytest

from agentuniverse.agent.action.tool.common_tool.email_document_tool import EmailDocumentTool
from agentuniverse.agent.action.tool.common_tool.pdf_tool import PDFTool


@pytest.fixture(params=["pdf-merge", "pdf-split", "pdf-rotate", "email-create", "email-extract"])
def output_operation(request, tmp_path):
    mode = request.param
    out = tmp_path / "out"
    if mode.startswith("pdf-"):
        pypdf = pytest.importorskip("pypdf")
        tool = PDFTool(base_dir=str(tmp_path))
        sources = {}
        for marker, width in [("first", 101), ("winner", 202)]:
            path = tmp_path / marker / "source.pdf"
            path.parent.mkdir()
            writer = pypdf.PdfWriter()
            writer.add_blank_page(width=width, height=300)
            with path.open("wb") as stream:
                writer.write(stream)
            sources[marker] = path
        target = out / ("source-page-1.pdf" if mode == "pdf-split" else "result.pdf")

        def perform(marker, overwrite=False):
            if mode == "pdf-merge":
                return tool.execute(mode="merge", file_path=str(target),
                                    input_paths=[str(sources[marker])], overwrite=overwrite)
            if mode == "pdf-split":
                return tool.execute(mode="split", file_path=str(sources[marker]),
                                    output_dir=str(out), pages=[1], overwrite=overwrite)
            return tool.execute(mode="rotate", file_path=str(sources[marker]),
                                output_path=str(target), rotation=90, overwrite=overwrite)

        def contents():
            width = int(pypdf.PdfReader(target).pages[0].mediabox.width)
            return {101: "first", 202: "winner"}[width]

        boundary = (pypdf.PdfWriter, "write")
    else:
        tool = EmailDocumentTool(base_dir=str(tmp_path))
        if mode == "email-create":
            target = out / "result.eml"

            def perform(marker, overwrite=False):
                return tool.execute(mode="create", file_path=str(target),
                                    headers={"from": "sender@example.test", "to": "recipient@example.test"},
                                    text_body=marker, overwrite=overwrite)

            def contents():
                message = BytesParser(policy=policy.default).parsebytes(target.read_bytes())
                return message.get_body(preferencelist=("plain",)).get_content().strip()
        else:
            target = out / "result.bin"
            sources = {}
            for marker in ["first", "winner"]:
                message = EmailMessage()
                message.set_content("Envelope body")
                message.add_attachment(marker.encode(), maintype="application", subtype="octet-stream",
                                       filename="result.bin")
                path = tmp_path / (marker + ".eml")
                path.write_bytes(message.as_bytes(policy=policy.default))
                sources[marker] = path

            def perform(marker, overwrite=False):
                return tool.execute(mode="extract", file_path=str(sources[marker]), output_dir=str(out),
                                    overwrite=overwrite)

            def contents():
                return target.read_bytes().decode()

        boundary = (EmailDocumentTool, "_atomic_write")
    return perform, contents, target, boundary


@pytest.mark.parametrize("overwrite", [False, True])
def test_concurrent_output_does_not_replace_a_successful_winner(output_operation, monkeypatch, overwrite):
    perform, contents, target, (owner, method) = output_operation
    paused, release = threading.Event(), threading.Event()
    original = getattr(owner, method)
    result = []

    def first_write():
        result.append(perform("first", overwrite))

    first = threading.Thread(target=first_write)

    def delayed_write(instance, *args, **kwargs):
        if threading.current_thread() is first:
            paused.set()
            assert release.wait(15)
        return original(instance, *args, **kwargs)

    # Preserve the real serializers and filesystem writes; only interleave
    # their save boundary after the public operation's existence check.
    monkeypatch.setattr(owner, method, delayed_write)
    first.start()
    try:
        assert paused.wait(15)
        winner = perform("winner")
        assert winner["status"] == "success", winner
        winner_bytes = target.read_bytes()
    finally:
        release.set()
        first.join(15)
    assert not first.is_alive()
    assert contents() == ("first" if overwrite else "winner")
    if not overwrite:
        assert target.read_bytes() == winner_bytes
    assert result[0]["status"] == ("success" if overwrite else "error"), result
    assert not list(target.parent.glob(".pdf-*"))
    assert not list(target.parent.glob(".email-*"))


def test_already_existing_output_is_preserved(output_operation):
    perform, _, target, _ = output_operation
    assert perform("winner")["status"] == "success"
    before = target.read_bytes()
    result = perform("first")
    assert result["status"] == "error", result
    assert target.read_bytes() == before
