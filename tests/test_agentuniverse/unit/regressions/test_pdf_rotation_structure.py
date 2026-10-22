"""Rotating pages preserves the PDF document catalog and metadata."""
import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    TextStringObject,
)

from agentuniverse.agent.action.tool.common_tool.pdf_tool import PDFTool


def make_source(path):
    writer = PdfWriter()
    for index in range(3):
        page = writer.add_blank_page(width=200, height=300)
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 20 200 Td (page-{index + 1}) Tj ET".encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {
                        NameObject("/F1"): DictionaryObject(
                            {
                                NameObject("/Type"): NameObject("/Font"),
                                NameObject("/Subtype"): NameObject("/Type1"),
                                NameObject("/BaseFont"): NameObject("/Helvetica"),
                            }
                        )
                    }
                )
            }
        )
    writer.add_metadata({"/Title": "Quarterly report", "/Author": "Example author"})
    writer.add_outline_item("Revenue", 1)
    writer.add_named_destination("revenue", 1)
    writer.set_page_label(0, 1, style=PageLabelStyle.LOWERCASE_ROMAN)
    writer.set_page_label(2, 2, style=PageLabelStyle.DECIMAL, prefix="A-", start=1)
    field = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/FT"): NameObject("/Tx"),
            NameObject("/T"): TextStringObject("answer"),
            NameObject("/V"): TextStringObject("retained"),
            NameObject("/Rect"): ArrayObject(
                [FloatObject(20), FloatObject(20), FloatObject(80), FloatObject(40)]
            ),
        }
    )
    writer.add_annotation(0, field)
    writer._root_object[NameObject("/AcroForm")] = DictionaryObject(
        {NameObject("/Fields"): ArrayObject([writer.pages[0]["/Annots"][0]])}
    )
    with path.open("wb") as stream:
        writer.write(stream)


def inspect(path):
    reader = PdfReader(path)
    fields = reader.get_fields() or {}
    return {
        "metadata": dict(reader.metadata or {}),
        "outlines": [
            [item.title, reader.get_destination_page_number(item)]
            for item in reader.outline
        ],
        "named_destinations": {
            name: reader.get_destination_page_number(destination)
            for name, destination in reader.named_destinations.items()
        },
        "page_labels": reader.page_labels,
        "fields": {name: field.get("/V") for name, field in fields.items()},
        "rotations": [page.rotation for page in reader.pages],
        "texts": [page.extract_text() for page in reader.pages],
    }


@pytest.mark.parametrize("pages,rotation,expected", [([2], 90, [0, 90, 0]), (None, 180, [180, 180, 180])])
def test_rotate_preserves_document_structure(tmp_path, pages, rotation, expected):
    source = tmp_path / "source.pdf"
    make_source(source)
    original_bytes = source.read_bytes()
    before = inspect(source)
    result = PDFTool(base_dir=str(tmp_path)).execute(
        mode="rotate", file_path="source.pdf", output_path="rotated.pdf",
        pages=pages, rotation=rotation,
    )
    assert result["status"] == "success"
    after = inspect(tmp_path / "rotated.pdf")
    for key in ("metadata", "outlines", "named_destinations", "page_labels", "fields", "texts"):
        assert after[key] == before[key], key
    assert after["rotations"] == expected
    assert source.read_bytes() == original_bytes
