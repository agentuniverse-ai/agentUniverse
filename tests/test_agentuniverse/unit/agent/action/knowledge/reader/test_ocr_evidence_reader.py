"""Validation and malformed-result contracts without an OCR executable."""

import pytest
from pydantic import ValidationError

from agentuniverse.agent.action.knowledge.reader.image.ocr_evidence_reader import OcrEvidenceReader


def result():
    return dict(
        text=["word"],
        level=[5],
        conf=[20.5],
        left=[1],
        top=[2],
        width=[10],
        height=[5],
        page_num=[1],
        block_num=[1],
        par_num=[1],
        line_num=[1],
        word_num=[1],
    )


@pytest.mark.parametrize(
    "options",
    [
        dict(engine="easyocr"),
        dict(max_words=0),
        dict(max_pixels=True),
        dict(timeout_seconds=float("nan")),
        dict(page_segmentation=2),
        dict(language="eng --psm 0"),
        dict(low_confidence_threshold=101),
    ],
)
def test_invalid_settings(options):
    with pytest.raises(ValidationError):
        OcrEvidenceReader(**options)


@pytest.mark.parametrize(
    "field,value", [("conf", -1), ("conf", float("nan")), ("conf", 101), ("left", -1), ("width", 0), ("height", 100)]
)
def test_malformed_word_rejected(field, value):
    data = result()
    data[field] = [value]
    with pytest.raises(ValueError):
        OcrEvidenceReader()._words(data, (10, 20, 40, 50), 1, 100, 100)


def test_crop_translation_and_confidence_flag():
    words = OcrEvidenceReader()._words(result(), (10, 20, 40, 50), 1, 100, 100)
    assert words[0]["bbox_display"] == [11, 22, 21, 27]
    assert words[0]["bbox_original"] == [11, 22, 21, 27]
    assert words[0]["low_confidence"] is True
    assert words[0]["text"] == "word"


@pytest.mark.parametrize("data", [{}, {"text": []}, dict(result(), width=[])])
def test_malformed_columns(data):
    with pytest.raises(ValueError):
        OcrEvidenceReader()._words(data, (0, 0, 50, 50), 1, 50, 50)
