"""Verify the pixels passed to image backends using real Pillow files."""
import pytest
from PIL import Image

from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader


EXPECTED_GRIDS = {
    None: [[20, 60, 100], [140, 180, 220]],
    1: [[20, 60, 100], [140, 180, 220]],
    2: [[100, 60, 20], [220, 180, 140]],
    3: [[220, 180, 140], [100, 60, 20]],
    4: [[140, 180, 220], [20, 60, 100]],
    5: [[20, 140], [60, 180], [100, 220]],
    6: [[140, 20], [180, 60], [220, 100]],
    7: [[220, 100], [180, 60], [140, 20]],
    8: [[100, 220], [60, 180], [20, 140]],
}


def save_fixture(path, orientation):
    with Image.new("RGB", (72, 48)) as image:
        for row, values in enumerate(EXPECTED_GRIDS[None]):
            for column, value in enumerate(values):
                image.paste((value, value, value), (column * 24, row * 24,
                                                   (column + 1) * 24, (row + 1) * 24))
        exif = Image.Exif()
        exif[305] = "orientation fixture"
        if orientation is not None:
            exif[274] = orientation
        image.save(path, exif=exif, quality=100, subsampling=0)


@pytest.mark.parametrize("suffix", ["png", "jpg"])
@pytest.mark.parametrize("orientation", list(EXPECTED_GRIDS))
def test_both_backends_receive_display_orientation(tmp_path, monkeypatch, suffix, orientation):
    path = tmp_path / ("photo." + suffix)
    save_fixture(path, orientation)
    original_bytes = path.read_bytes()
    received = []

    def capture(phase, image):
        width, height = image.size
        grid = [[image.getpixel((x * 24 + 12, y * 24 + 12))[0]
                 for x in range(width // 24)] for y in range(height // 24)]
        received.append((phase, image.size, grid, dict(image.getexif())))

    def ocr(self, image):
        capture("ocr", image)
        return "recognized text"

    def describe(self, image):
        capture("description", image)
        return "image description"

    monkeypatch.setattr(ImageReader, "extract_text", ocr)
    monkeypatch.setattr(ImageReader, "generate_description", describe)
    ext_info = {"batch": "photos"}
    documents = ImageReader().load_data(path, ext_info=ext_info)

    expected_grid = EXPECTED_GRIDS[orientation]
    expected_size = (len(expected_grid[0]) * 24, len(expected_grid) * 24)
    assert [entry[0] for entry in received] == ["ocr", "description"]
    for _, size, grid, exif in received:
        assert size == expected_size
        assert grid == expected_grid
        assert exif[305] == "orientation fixture"
        if orientation not in (None, 1):
            assert 274 not in exif  # Prevent a backend from rotating the pixels again.
    assert len(documents) == 1
    assert documents[0].text == "recognized text\nimage description"
    assert documents[0].metadata == {
        "file_name": path.name, "format": suffix,
        "image_size": {"width": expected_size[0], "height": expected_size[1]},
        "channel": 3, "color_mode": "RGB", "batch": "photos",
        "has_text": True, "has_description": True,
    }
    assert ext_info == {"batch": "photos"}
    assert path.read_bytes() == original_bytes


@pytest.mark.parametrize("failure_stage", ["ocr", "description"])
def test_source_file_is_closed_when_backend_fails(tmp_path, monkeypatch, failure_stage):
    path = tmp_path / "failed.png"
    save_fixture(path, 6)
    captured = []

    def ocr(self, image):
        captured.append(image)
        if failure_stage == "ocr":
            raise RuntimeError("backend failure")
        return "text"

    def describe(self, image):
        raise RuntimeError("backend failure")

    monkeypatch.setattr(ImageReader, "extract_text", ocr)
    monkeypatch.setattr(ImageReader, "generate_description", describe)
    try:
        with pytest.raises(Exception, match="backend failure"):
            ImageReader().load_data(path)
        assert captured[0].fp is None or captured[0].fp.closed
    finally:
        for image in captured:
            image.close()
