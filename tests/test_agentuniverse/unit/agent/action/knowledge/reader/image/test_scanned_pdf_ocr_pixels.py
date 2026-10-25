"""Scanned PDF raster images satisfy each OCR backend's input contract."""

import io
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image

from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import (
    ScannedPdfOCRReader,
)


def install_pdf(monkeypatch, tmp_path, image, page_texts=("",)):
    """Stub parsing/rendering, retaining real Pillow images and a local file."""
    path = tmp_path / "scan.pdf"
    image.convert("RGB").save(path, format="PDF")
    pages = [SimpleNamespace(extract_text=Mock(return_value=text))
             for text in page_texts]
    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(
        PdfReader=Mock(return_value=SimpleNamespace(pages=pages))))
    render = Mock(return_value=[image])
    monkeypatch.setitem(sys.modules, "pdf2image", SimpleNamespace(
        convert_from_path=render))
    for name in ("paddleocr", "pytesseract", "easyocr"):
        monkeypatch.setitem(sys.modules, name, None)
    return path, render


def install_backend(monkeypatch, name, received):
    """Use the ndarray API shared by PaddleOCR 2.x and EasyOCR 1.7.x."""
    def recognize(pixels, **kwargs):
        received.append(pixels)
        if not isinstance(pixels, np.ndarray):
            message = "OCR backend does not accept a Pillow image"
            raise TypeError(message)
        if name == "paddleocr":
            assert kwargs == {"cls": True}
            return [[(None, ("recognized page", 0.99))]]
        assert kwargs == {"detail": 0}
        return ["recognized page"]

    if name == "paddleocr":
        factory = Mock(return_value=SimpleNamespace(ocr=recognize))
        module = SimpleNamespace(PaddleOCR=factory)
    else:
        factory = Mock(return_value=SimpleNamespace(readtext=recognize))
        module = SimpleNamespace(Reader=factory)
    monkeypatch.setitem(sys.modules, name, module)
    return factory


@pytest.mark.parametrize("backend", ["paddleocr", "easyocr"])
@pytest.mark.parametrize("mode,color,expected", [
    ("RGB", (255, 0, 0), [0, 0, 255]),
    ("L", 120, [120, 120, 120]),
    ("RGBA", (0, 0, 255, 255), [255, 0, 0]),
])
def test_scanned_page_reaches_backend_as_bgr(
    monkeypatch, tmp_path, backend, mode, color, expected,
):
    image = Image.new(mode, (3, 2), color)
    before = image.tobytes()
    path, render = install_pdf(monkeypatch, tmp_path, image)
    received = []
    factory = install_backend(monkeypatch, backend, received)

    doc, = ScannedPdfOCRReader().load_data(path, ext_info={"batch": "reports"})

    assert doc.text == "recognized page"
    assert doc.metadata == {
        "source": "pdf", "file_name": "scan.pdf", "engine": backend,
        "batch": "reports",
    }
    render.assert_called_once_with(str(path), first_page=1, last_page=1)
    assert len(received) == 1
    pixels = received[0]
    assert pixels.shape == (2, 3, 3)
    assert pixels.dtype == np.uint8
    assert pixels.flags.c_contiguous
    assert pixels[0, 0].tolist() == expected
    assert image.mode == mode
    assert image.tobytes() == before
    if backend == "paddleocr":
        factory.assert_called_once_with(use_angle_cls=True, lang="ch")
    else:
        factory.assert_called_once_with(["ch_sim", "en"])


@pytest.mark.parametrize("backend", ["paddleocr", "easyocr"])
def test_pdf2image_default_ppm_image_is_supported(monkeypatch, tmp_path, backend):
    # pdf2image's default output is PPM, not EasyOCR's special JPEG PIL type.
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), (12, 34, 56)).save(buffer, format="PPM")
    buffer.seek(0)
    with Image.open(buffer) as image:
        assert image.format == "PPM"
        path, _ = install_pdf(monkeypatch, tmp_path, image)
        received = []
        install_backend(monkeypatch, backend, received)

        doc, = ScannedPdfOCRReader().load_data(str(path))

        assert doc.text == "recognized page"
        assert doc.metadata["engine"] == backend
        assert received[0][0, 0].tolist() == [56, 34, 12]


def test_tesseract_fallback_keeps_original_pillow_image(monkeypatch, tmp_path):
    image = Image.new("RGB", (3, 2), (12, 34, 56))
    path, _ = install_pdf(monkeypatch, tmp_path, image)
    paddle = Mock(side_effect=RuntimeError("PaddleOCR unavailable"))
    monkeypatch.setitem(sys.modules, "paddleocr", SimpleNamespace(PaddleOCR=paddle))
    tesseract = Mock(return_value="tesseract page")
    monkeypatch.setitem(sys.modules, "pytesseract", SimpleNamespace(
        image_to_string=tesseract))

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == "tesseract page"
    assert doc.metadata["engine"] == "pytesseract"
    tesseract.assert_called_once_with(image, lang="chi_sim+eng")


def test_easyocr_fallback_after_backend_errors(monkeypatch, tmp_path):
    image = Image.new("RGB", (3, 2), (12, 34, 56))
    path, _ = install_pdf(monkeypatch, tmp_path, image)
    paddle = Mock(side_effect=RuntimeError("PaddleOCR inference failed"))
    monkeypatch.setitem(sys.modules, "paddleocr", SimpleNamespace(
        PaddleOCR=Mock(return_value=SimpleNamespace(ocr=paddle))))
    tesseract = Mock(side_effect=RuntimeError("Tesseract unavailable"))
    monkeypatch.setitem(sys.modules, "pytesseract", SimpleNamespace(
        image_to_string=tesseract))
    received = []
    install_backend(monkeypatch, "easyocr", received)

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == "recognized page"
    assert doc.metadata["engine"] == "easyocr"
    assert isinstance(paddle.call_args.args[0], np.ndarray)
    tesseract.assert_called_once_with(image, lang="chi_sim+eng")
    assert received[0][0, 0].tolist() == [56, 34, 12]


def test_mixed_pdf_preserves_page_order_and_native_text(monkeypatch, tmp_path):
    image = Image.new("RGB", (2, 2), "white")
    path, render = install_pdf(monkeypatch, tmp_path, image,
                               ("native first", "", "native last"))
    received = []
    install_backend(monkeypatch, "paddleocr", received)

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == "native first\n\nrecognized page\n\nnative last"
    assert doc.metadata["engine"] == "paddleocr,pypdf"
    render.assert_called_once_with(str(path), first_page=2, last_page=2)


def test_native_text_does_not_invoke_ocr(monkeypatch, tmp_path):
    image = Image.new("RGB", (2, 2), "white")
    path, render = install_pdf(monkeypatch, tmp_path, image, ("native text",))

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == "native text"
    assert doc.metadata["engine"] == "pypdf"
    render.assert_not_called()


@pytest.mark.parametrize("empty_render", [False, True])
def test_unavailable_ocr_and_empty_render_keep_existing_results(
    monkeypatch, tmp_path, empty_render,
):
    image = Image.new("RGB", (2, 2), "white")
    path, render = install_pdf(monkeypatch, tmp_path, image)
    if empty_render:
        render.return_value = []

    doc, = ScannedPdfOCRReader().load_data(path)

    assert doc.text == ""
    assert doc.metadata["engine"] == ("none" if empty_render else "unknown")
