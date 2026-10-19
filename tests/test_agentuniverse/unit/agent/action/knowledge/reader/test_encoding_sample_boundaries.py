"""Detect encodings without rejecting a character split by the sample limit."""

import io

import pytest

from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


@pytest.mark.parametrize("source_type", ["bytes", "bytearray", "path", "handle"])
@pytest.mark.parametrize("prefix_size", [32765, 32766, 32767])
@pytest.mark.parametrize("payload", ["中文", "🙂"])
def test_utf8_sample_boundary(tmp_path, source_type, prefix_size, payload):
    """The default sample may end inside a three- or four-byte character."""
    text = "a" * prefix_size + payload * 3
    raw = text.encode("utf-8")
    if source_type == "path":
        source = tmp_path / "sample.txt"
        source.write_bytes(raw)
    elif source_type == "handle":
        source = io.BytesIO(raw)
    elif source_type == "bytearray":
        source = bytearray(raw)
    else:
        source = raw

    encoding = detect_file_encoding(source)

    assert encoding == "utf-8"
    assert raw.decode(encoding) == text
    if source_type == "handle":
        assert source.tell() == 0
        assert not source.closed


@pytest.mark.parametrize("sample_size", [1, 2, 3, 4, 5])
def test_utf8_bom_at_small_sample_limits(sample_size):
    """A BOM and Unicode characters can also straddle a custom sample limit."""
    text = "中文🙂"
    raw = text.encode("utf-8-sig")

    encoding = detect_file_encoding(raw, sample_size=sample_size)

    assert encoding == "utf-8-sig"
    assert raw.decode(encoding) == text


@pytest.mark.parametrize("text", ["abc中文", "abc\U00020000中文"])
def test_gb18030_sample_boundary(text):
    """Lookahead must reject a UTF-8-looking lead byte in GB18030 input."""
    raw = text.encode("gb18030")

    encoding = detect_file_encoding(raw, sample_size=4)

    assert encoding == "gb18030"
    assert raw.decode(encoding) == text


@pytest.mark.parametrize("raw", [b"abc\xe4", b"abc\xe4\xbd"])
def test_incomplete_character_at_eof_is_not_utf8(raw):
    """An actually truncated file must not be accepted as valid UTF-8."""
    assert detect_file_encoding(raw, sample_size=4) != "utf-8"


def test_invalid_lookahead_rejects_incomplete_utf8_prefix():
    """A trailing lead byte is insufficient evidence for UTF-8 detection."""
    assert detect_file_encoding(b"abc\xc2xmore", sample_size=4) != "utf-8"


def test_invalid_interior_byte_still_rejects_utf8():
    """Completing the boundary must not hide invalid bytes inside the sample."""
    assert detect_file_encoding(b"a\xffbcdef", sample_size=4) != "utf-8"


def test_binary_handle_position_is_preserved():
    """The extra lookahead must preserve the caller-owned stream position."""
    handle = io.BytesIO(b"skip" + "abc中文".encode("utf-8"))
    handle.seek(4)

    assert detect_file_encoding(handle, sample_size=4) == "utf-8"
    assert handle.tell() == 4
    assert not handle.closed


@pytest.mark.parametrize("raw", [b"", b"plain ascii", "中文".encode("utf-8")])
def test_short_utf8_inputs(raw):
    """Empty and complete inputs retain their existing UTF-8 result."""
    assert detect_file_encoding(raw) == "utf-8"


@pytest.mark.parametrize("reader_type", ["txt", "line", "csv"])
def test_readers_preserve_unicode_after_default_sample(tmp_path, reader_type):
    """Real text, line and CSV readers must return uncorrupted Unicode."""
    from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
    from agentuniverse.agent.action.knowledge.reader.file.txt_reader import (
        LineTxtReader,
        TxtReader,
    )

    content = "column\n" + "a" * (32766 - len("column\n")) + "中文🙂\n"
    path = tmp_path / "sample.txt"
    path.write_text(content, encoding="utf-8", newline="")
    readers = {"txt": TxtReader, "line": LineTxtReader, "csv": CSVReader}

    documents = readers[reader_type]().load_data(path)

    recovered = "".join(document.text for document in documents)
    assert recovered == (content.rstrip("\n") if reader_type == "csv" else content)
    assert all(document.metadata["file_name"] == path.name for document in documents)
