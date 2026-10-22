"""Page-scoped fallback using actual saved PDFs and the native pypdf parser."""
from pathlib import Path
import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NumberObject,
)

from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import (
    ScannedPdfOCRReader,
)


def write_pdf(path, kinds):
    """Create text, blank, and unreadable-font pages without parser mocks."""
    writer = PdfWriter()
    for index, kind in enumerate(kinds):
        page = writer.add_blank_page(width=300, height=300)
        if kind == "blank":
            continue
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
        })
        content = DecodedStreamObject()
        content.set_data(
            f"BT /F1 12 Tf 10 100 Td (native-{index}) Tj ET".encode("ascii")
        )
        page[NameObject("/Contents")] = content
        if kind == "broken":
            # The page tree remains readable, but the native text extractor
            # rejects this invalid font resource when it reaches the page.
            page[NameObject("/Resources")] = DictionaryObject({
                NameObject("/Font"): NumberObject(7),
            })
    with path.open("wb") as output:
        writer.write(output)


def install_ocr(monkeypatch, calls):
    """Replace only the heavyweight OCR boundary, not PDF parsing or reading."""
    def ocr(self, path, index):
        assert isinstance(path, Path)
        assert path.exists()
        calls.append(index)
        return f"ocr-{index}", "test-ocr"
    monkeypatch.setattr(ScannedPdfOCRReader, "_ocr_pdf_page", ocr)


@pytest.mark.parametrize("as_string", [False, True])
@pytest.mark.parametrize("broken_index", [0, 1, 2])
def test_only_unreadable_page_uses_ocr(tmp_path, monkeypatch, as_string, broken_index):
    path = tmp_path / "mixed.pdf"
    kinds = ["text"] * 3
    kinds[broken_index] = "broken"
    write_pdf(path, kinds)
    calls = []
    install_ocr(monkeypatch, calls)

    docs = ScannedPdfOCRReader().load_data(str(path) if as_string else path)

    assert calls == [broken_index]
    assert len(docs) == 1
    assert docs[0].text == "\n\n".join(
        f"ocr-{i}" if i == broken_index else f"native-{i}" for i in range(3)
    )
    assert docs[0].metadata == {
        "source": "pdf", "file_name": "mixed.pdf", "engine": "pypdf,test-ocr",
    }


@pytest.mark.parametrize("kinds", [
    ["broken", "text", "broken"],
    ["blank", "text", "broken", "blank", "text"],
    ["text", "text", "text"],
    ["broken", "broken", "broken"],
])
def test_each_page_appears_once_in_original_order(tmp_path, monkeypatch, kinds):
    path = tmp_path / "ordered.pdf"
    write_pdf(path, kinds)
    calls = []
    install_ocr(monkeypatch, calls)

    doc, = ScannedPdfOCRReader().load_data(path)

    assert calls == [i for i, kind in enumerate(kinds) if kind != "text"]
    assert doc.text == "\n\n".join(
        f"native-{i}" if kind == "text" else f"ocr-{i}"
        for i, kind in enumerate(kinds)
    )
    expected_engines = {"pypdf" if kind == "text" else "test-ocr" for kind in kinds}
    assert doc.metadata["engine"] == ",".join(sorted(expected_engines))


@pytest.mark.parametrize("failing_index", [0, 1, 2])
@pytest.mark.parametrize("error_type", [ImportError, RuntimeError])
def test_ocr_failure_propagates_without_restarting_completed_pages(
    tmp_path, monkeypatch, failing_index, error_type,
):
    path = tmp_path / "ocr-failure.pdf"
    kinds = ["text"] * 3
    kinds[failing_index] = "blank"
    write_pdf(path, kinds)
    calls = []
    failure = error_type("OCR unavailable for this page")

    def ocr(self, file, index):
        calls.append(index)
        raise failure
    monkeypatch.setattr(ScannedPdfOCRReader, "_ocr_pdf_page", ocr)

    with pytest.raises(error_type) as caught:
        ScannedPdfOCRReader().load_data(path)
    assert caught.value is failure
    assert calls == [failing_index]


def test_metadata_overrides_and_repeated_loads(tmp_path, monkeypatch):
    broken = tmp_path / "broken.pdf"
    plain = tmp_path / "plain.pdf"
    write_pdf(broken, ["text", "broken", "text"])
    write_pdf(plain, ["text"])
    calls = []
    install_ocr(monkeypatch, calls)
    reader = ScannedPdfOCRReader()
    ext_info = {"source": "custom", "file_name": "display.pdf", "collection": "manuals"}
    original = ext_info.copy()

    first, = reader.load_data(broken, ext_info=ext_info)
    second, = reader.load_data(plain)

    assert first.text == "native-0\n\nocr-1\n\nnative-2"
    assert first.metadata == {**original, "engine": "pypdf,test-ocr"}
    assert ext_info == original
    assert second.text == "native-0"
    assert second.metadata == {"source": "pdf", "file_name": "plain.pdf", "engine": "pypdf"}
    assert calls == [1]


def test_empty_pdf_keeps_existing_empty_document(tmp_path, monkeypatch):
    path = tmp_path / "empty.pdf"
    write_pdf(path, [])
    calls = []
    install_ocr(monkeypatch, calls)

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == ""
    assert doc.metadata == {"source": "pdf", "file_name": "empty.pdf", "engine": "unknown"}
    assert calls == []
