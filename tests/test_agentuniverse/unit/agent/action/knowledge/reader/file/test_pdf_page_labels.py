"""Exercise real PDF ingestion and bound per-page label resolution work."""
import cProfile

import pytest

pypdf = pytest.importorskip("pypdf")

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader


def _pdf_writer(page_count):
    """Build blank PDF pages using the optional reader dependency."""
    writer = pypdf.PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=100, height=100)
    return writer


@pytest.mark.parametrize("page_count", [1, 10, 64])
def test_label_resolution_work_is_linear(tmp_path, page_count):
    """Adding pages must not cause repeated whole-document label scans."""
    path = tmp_path / "numbered.pdf"
    writer = _pdf_writer(page_count)
    writer.set_page_label(0, page_count - 1, style="/D", prefix="Page ", start=1)
    writer.write(path)

    # Count actual pypdf resolution calls, without stubbing its property, file
    # parser or label algorithm. A work bound avoids flaky timing assertions.
    label_code = pypdf.PdfReader.page_labels.fget.__globals__[
        "page_index2page_label"].__code__
    profile = cProfile.Profile()
    docs = profile.runcall(PdfReader().load_data, path)
    resolutions = sum(entry.callcount for entry in profile.getstats()
                      if entry.code is label_code)

    assert len(docs) == page_count
    assert [doc.metadata["page_label"] for doc in docs] == [
        f"Page {index + 1}" for index in range(page_count)]
    assert page_count <= resolutions <= 2 * page_count


def test_mixed_labels_and_text_survive_file_dispatch(tmp_path):
    """Preserve content, Roman/decimal labels and per-page metadata."""
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    writer = pypdf.PdfWriter()
    for text in ["Introduction", "Contents", "First chapter", "Second chapter"]:
        page = writer.add_blank_page(width=200, height=200)
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode("ascii"))
        page.replace_contents(stream)
    writer.set_page_label(0, 1, style="/r", start=1)
    writer.set_page_label(2, 3, style="/D", prefix="chapter-", start=1)
    path = tmp_path / "chapters.pdf"
    writer.write(path)

    extra = {"collection": "reference"}
    docs = FileReader().load_data([path], ext_info=extra)

    assert [doc.text.strip() for doc in docs] == [
        "Introduction", "Contents", "First chapter", "Second chapter"]
    assert [doc.metadata for doc in docs] == [
        {"page_label": label, "file_name": "chapters.pdf", **extra}
        for label in ["i", "ii", "chapter-1", "chapter-2"]]
    docs[0].metadata["collection"] = "changed"
    assert docs[1].metadata["collection"] == "reference"
    assert extra == {"collection": "reference"}


def test_default_labels_and_metadata_overrides(tmp_path):
    """Keep default page numbers and existing ext_info precedence."""
    path = tmp_path / "plain.pdf"
    _pdf_writer(2).write(path)
    reader = PdfReader()
    assert [doc.metadata["page_label"]
            for doc in reader.load_data(str(path))] == ["1", "2"]
    docs = reader.load_data(
        path, ext_info={"page_label": "custom", "file_name": "override"})
    assert [doc.text for doc in docs] == ["", ""]
    assert [doc.metadata for doc in docs] == [
        {"page_label": "custom", "file_name": "override"}] * 2


def test_empty_pdf_returns_no_documents(tmp_path):
    """A valid zero-page PDF still yields an empty document list."""
    path = tmp_path / "empty.pdf"
    _pdf_writer(0).write(path)
    assert PdfReader().load_data(path) == []
