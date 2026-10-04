"""Regression coverage for multibyte characters crossing an encoding sample."""

import io
import json

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


@pytest.mark.parametrize("character", ["é", "中", "😀"])
@pytest.mark.parametrize("source_kind", ["path", "bytes", "bytearray", "stream"])
def test_utf8_character_crossing_sample(tmp_path, character, source_kind):
    """A truncated sample must not disqualify an otherwise valid UTF-8 file."""
    content = ("a" * 7 + character + "end").encode("utf-8")
    if source_kind == "path":
        source = tmp_path / "sample.txt"
        source.write_bytes(content)
    elif source_kind == "stream":
        source = io.BytesIO(b"prefix" + content)
        source.seek(6)
    elif source_kind == "bytearray":
        source = bytearray(content)
    else:
        source = content

    assert detect_file_encoding(source, sample_size=8) == "utf-8"
    if source_kind == "stream":
        assert source.tell() == 6


@pytest.mark.parametrize("data", [b"abc\xffdef", b"abc\xc3"])
def test_invalid_or_incomplete_full_input_still_uses_fallback(data):
    """Only a truncated sample may leave an incomplete sequence buffered."""
    assert detect_file_encoding(data, sample_size=len(data), fallback_encodings=("utf-8", "latin-1")) == "latin-1"


def test_invalid_byte_inside_truncated_sample_still_uses_fallback():
    """Incremental decoding must retain strict validation within the sample."""
    assert detect_file_encoding(b"a\xffbcdef", sample_size=4, fallback_encodings=("utf-8", "latin-1")) == "latin-1"


@pytest.mark.parametrize(
    "reader_class,suffix",
    [
        (TxtReader, ".txt"),
        (CSVReader, ".csv"),
        (JsonReader, ".json"),
    ],
)
def test_reader_preserves_utf8_at_default_sample_boundary(tmp_path, reader_class, suffix):
    """Exercise real readers with an emoji split at the default 32 KiB limit."""
    prefix = '{"text": "' if suffix == ".json" else ""
    value = "a" * (32 * 1024 - len(prefix) - 1) + "😀尾部"
    content = json.dumps({"text": value}, ensure_ascii=False) if prefix else value
    source = tmp_path / ("sample" + suffix)
    source.write_text(content, encoding="utf-8")

    documents = reader_class().load_data(source)

    assert len(documents) == 1
    result = documents[0].text
    if prefix:
        result = json.loads(result)["text"]
    assert result == value
    assert documents[0].metadata["file_name"] == source.name
