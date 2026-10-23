import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.image.image_ocr_reader import ImageOCRReader


class _FakeImage:
    def __init__(self):
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closed = True


def test_pytesseract_input_is_closed_before_easyocr_fallback():
    image = _FakeImage()
    tesseract = SimpleNamespace(
        image_to_string=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("ocr failed"))
    )
    easy_reader = SimpleNamespace(readtext=lambda _file, detail=0: ["fallback"])
    easyocr = SimpleNamespace(Reader=lambda *_args, **_kwargs: easy_reader)

    with patch.dict(
        sys.modules,
        {"paddleocr": None, "pytesseract": tesseract, "easyocr": easyocr},
    ), patch("PIL.Image.open", return_value=image):
        text, engine = ImageOCRReader()._ocr(Path("image.png"))

    assert (text, engine) == ("fallback", "easyocr")
    assert image.closed is True
