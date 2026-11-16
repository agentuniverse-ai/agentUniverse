import ast
import logging
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.image.image_ocr_reader import ImageOCRReader
from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import ScannedPdfOCRReader


@pytest.mark.parametrize(
    ("reader", "message"),
    [
        (ImageOCRReader(), "ImageOCRReader starting image load"),
        (ScannedPdfOCRReader(), "ScannedPdfOCRReader starting PDF load"),
    ],
)
def test_ocr_readers_log_diagnostics_without_stdout(reader, message, caplog, capsys):
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(FileNotFoundError):
            reader.load_data(Path("missing-ocr-input"))

    captured = capsys.readouterr()
    assert captured.out == ""
    assert message in caplog.text


@pytest.mark.parametrize(
    "relative_path",
    [
        "agentuniverse/agent/action/knowledge/reader/image/image_ocr_reader.py",
        "agentuniverse/agent/action/knowledge/reader/image/scanned_pdf_ocr_reader.py",
    ],
)
def test_ocr_readers_do_not_use_direct_stdout_writes(relative_path):
    source = Path(relative_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print" for node in ast.walk(tree))
