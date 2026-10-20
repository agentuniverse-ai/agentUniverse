"""Exercise EAST rectangle decoding with real OpenCV non-maxima suppression."""

import pytest

from agentuniverse.agent.action.tool.common_tool import readimage_tool

np = pytest.importorskip("numpy")
pytest.importorskip("cv2")


@pytest.mark.parametrize(
    "rectangles,expected_indices,scale",
    [
        ([(100, 100, 120, 120), (132, 100, 152, 120)], [0, 1], 1),
        ([(100, 100, 120, 120), (132, 100, 152, 120)], [0, 1], 2),
        ([(100, 100, 160, 120), (104, 100, 164, 120)], [0], 1),
        ([(100, 100, 120, 120)], [0], 1),
        ([], [], 1),
    ],
)
def test_east_nms_uses_rectangle_sizes(monkeypatch, rectangles, expected_indices, scale):
    """Distinct offset boxes survive while overlapping duplicates are suppressed."""
    scores = np.zeros((1, 1, 80, 80), dtype=np.float32)
    geometry = np.zeros((1, 5, 80, 80), dtype=np.float32)
    for index, (left, top, right, bottom) in enumerate(rectangles):
        y, x = 27, 27 + 8 * index
        scores[0, 0, y, x] = 0.9 - index * 0.1
        geometry[0, :, y, x] = [4 * y - top, right - 4 * x,
                               bottom - 4 * y, 4 * x - left, 0]

    class Network:
        def setInput(self, blob):
            assert blob.shape == (1, 3, 320, 320)

        def forward(self, layers):
            return scores, geometry

    monkeypatch.setattr(readimage_tool.cv2.dnn, "readNet", lambda path: Network())
    image = np.arange((320 * scale) ** 2 * 3, dtype=np.uint8).reshape(
        320 * scale, 320 * scale, 3)
    regions = readimage_tool.detect_text_regions(image)
    assert len(regions) == len(expected_indices)
    for region, index in zip(regions, expected_indices, strict=True):
        left, top, right, bottom = rectangles[index]
        np.testing.assert_array_equal(
            region, image[top * scale:bottom * scale, left * scale:right * scale])
