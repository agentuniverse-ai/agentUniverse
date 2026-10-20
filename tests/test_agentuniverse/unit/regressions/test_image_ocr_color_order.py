"""Real Pillow images are converted to EasyOCR's BGR ndarray contract."""
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image

from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader


@pytest.mark.parametrize('mode,color,expected', [
    ('RGB', (255, 0, 0), [0, 0, 255]),
    ('RGBA', (0, 0, 255, 17), [255, 0, 0]),
    ('L', 120, [120, 120, 120]),
    ('1', 1, [255, 255, 255]),
    ('P', 1, [255, 255, 255]),
    ('CMYK', (0, 255, 255, 0), [0, 0, 255]),
])
def test_file_ocr_pixels_preserve_color_and_original_metadata(tmp_path, mode, color, expected):
    path = tmp_path / ('image.tif' if mode == 'CMYK' else 'image.png')
    with Image.new(mode, (2, 3), color) as image:
        if mode == 'P':
            image.putpalette([0, 0, 0, 255, 255, 255] + [0] * 762)
        image.save(path)
    before = path.read_bytes()
    received = []
    ocr = Mock()

    def readtext(pixels):
        received.append(pixels)
        return [(None, 'recognized', .9)]

    ocr.readtext.side_effect = readtext
    reader = ImageReader()
    reader._ocr_reader = ocr
    original_modes = []

    def caption(image):
        original_modes.append(image.mode)
        return [{'generated_text': 'caption'}]

    reader._description_pipeline = caption
    doc = reader.load_data(path, ext_info={'batch': 'fixture'})[0]
    pixels = received[0]
    assert pixels.shape == (3, 2, 3)
    assert pixels.dtype == np.uint8
    assert pixels.flags.c_contiguous
    assert pixels[0, 0].tolist() == expected
    assert original_modes == [mode]
    assert doc.metadata['color_mode'] == mode
    assert doc.metadata['channel'] == Image.getmodebands(mode)
    assert doc.metadata['batch'] == 'fixture'
    assert doc.text == 'recognized\ncaption'
    assert path.read_bytes() == before


def test_existing_ndarray_input_remains_unchanged():
    pixels = np.array([[[10, 20, 30]]], dtype=np.uint8)
    ocr = Mock()
    ocr.readtext.return_value = []
    reader = ImageReader()
    reader._ocr_reader = ocr
    assert reader.extract_text(pixels) == ''
    np.testing.assert_array_equal(ocr.readtext.call_args.args[0], pixels)
