import pytest

from agentuniverse.agent.action.tool.common_tool import readimage_tool


@pytest.mark.parametrize(
    ("width", "height"),
    [(0, 320), (-32, 320), (321, 320), (320, True)],
)
def test_east_dimensions_are_validated_before_loading_model(monkeypatch, width, height):
    monkeypatch.setattr(readimage_tool, "cv2", object())
    monkeypatch.setattr(readimage_tool, "np", object())

    with pytest.raises(ValueError, match="positive multiples of 32"):
        readimage_tool.detect_text_regions(object(), width=width, height=height)
