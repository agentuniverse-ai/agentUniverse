"""Tesseract fallback must release native Pillow resources on every exit."""
import sys
from types import SimpleNamespace

import pytest
from PIL import Image

from agentuniverse.agent.action.knowledge.reader.image.image_ocr_reader import ImageOCRReader


@pytest.mark.parametrize('suffix', ['.png', '.tiff', '.multi.tiff'])
@pytest.mark.parametrize('outcome', ['success', 'fallback', 'failure'])
def test_tesseract_image_is_closed_before_return_or_fallback(tmp_path, monkeypatch, suffix, outcome):
    path = tmp_path / ('image' + suffix)
    with Image.new('RGB', (3, 3), (1, 2, 3)) as source:
        if suffix == '.multi.tiff':
            source.save(path, save_all=True, append_images=[source])
        else:
            source.save(path)
    opened = []
    native_open = Image.open

    def tracking_open(*args, **kwargs):
        image = native_open(*args, **kwargs)
        opened.append((image, image.fp))
        return image

    def paddle(*args, **kwargs):
        raise RuntimeError('Paddle unavailable')

    def tesseract(image, **kwargs):
        assert image is opened[0][0]
        assert not opened[0][1].closed
        if outcome != 'success':
            raise RuntimeError('Tesseract failed before decoding')
        assert image.getpixel((0, 0)) == (1, 2, 3)
        return 'recognized'

    def easy_reader(*args, **kwargs):
        assert opened[0][1].closed
        if outcome == 'failure':
            raise RuntimeError('EasyOCR unavailable')
        return SimpleNamespace(readtext=lambda *a, **k: ['fallback'])

    monkeypatch.setattr(Image, 'open', tracking_open)
    monkeypatch.setitem(sys.modules, 'paddleocr', SimpleNamespace(PaddleOCR=paddle))
    monkeypatch.setitem(sys.modules, 'pytesseract', SimpleNamespace(image_to_string=tesseract))
    monkeypatch.setitem(sys.modules, 'easyocr', SimpleNamespace(Reader=easy_reader))
    reader = ImageOCRReader()
    if outcome == 'failure':
        with pytest.raises(ImportError, match='No OCR engine available'):
            reader.load_data(path)
    else:
        docs = reader.load_data(path, ext_info={'tag': 'kept'})
        assert docs[0].text == ('recognized' if outcome == 'success' else 'fallback')
        assert docs[0].metadata['tag'] == 'kept'
        assert docs[0].metadata['engine'] == ('pytesseract' if outcome == 'success' else 'easyocr')
    assert len(opened) == 1
    assert opened[0][1].closed
