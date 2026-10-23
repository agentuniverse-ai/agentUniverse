"""Both conventional TIFF extensions are accepted by ImageReader."""

import pytest
from PIL import Image

from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader


@pytest.mark.parametrize("suffix", [".tif", ".TIF", ".tiff", ".TIFF"])
def test_tiff_extension_passes_decoded_pixels_to_backends(tmp_path, monkeypatch, suffix):
    """Read native TIFF pixels without invoking external OCR or caption models."""
    path = tmp_path / ("scan" + suffix)
    Image.new("RGB", (3, 2), (12, 34, 56)).save(path, format="TIFF")
    calls = []

    def ocr(self, image):
        calls.append(("ocr", image.format, image.size, image.getpixel((0, 0))))
        return "recognized text"

    def caption(self, image):
        calls.append(("caption", image.format, image.size, image.getpixel((0, 0))))
        return "image description"

    monkeypatch.setattr(ImageReader, "extract_text", ocr)
    monkeypatch.setattr(ImageReader, "generate_description", caption)
    documents = ImageReader()._load_data(path, ext_info={"source": "scan"})
    assert calls == [
        ("ocr", "TIFF", (3, 2), (12, 34, 56)),
        ("caption", "TIFF", (3, 2), (12, 34, 56)),
    ]
    assert len(documents) == 1
    assert documents[0].text == "recognized text\nimage description"
    assert documents[0].metadata["file_name"] == path.name
    assert documents[0].metadata["format"] == suffix[1:].lower()
    assert documents[0].metadata["source"] == "scan"
    assert documents[0].metadata["image_size"] == {"width": 3, "height": 2}


def test_unsupported_extension_is_still_rejected(tmp_path, monkeypatch):
    """Adding the TIFF alias does not accept arbitrary file extensions."""
    path = tmp_path / "scan.unknown"
    Image.new("RGB", (1, 1)).save(path, format="TIFF")
    def unexpected_backend(self, image):
        pytest.fail("Unsupported extension reached an OCR or caption backend")
    monkeypatch.setattr(ImageReader, "extract_text", unexpected_backend)
    monkeypatch.setattr(ImageReader, "generate_description", unexpected_backend)
    with pytest.raises(Exception, match="Unsupported image format"):
        ImageReader()._load_data(path)
