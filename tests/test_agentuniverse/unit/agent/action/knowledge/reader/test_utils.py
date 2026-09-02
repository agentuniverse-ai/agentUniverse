# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_utils.py
"""Unit tests for the reader encoding detection utilities."""

import io

from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


class TestDetectFileEncoding:
    """Test the detect_file_encoding helper function."""

    def test_empty_input_defaults_to_utf8(self):
        """An empty sample should default to utf-8."""
        assert detect_file_encoding(b"") == "utf-8"

    def test_ascii_and_utf8_bytes_detected_as_utf8(self):
        """Plain ascii and utf-8 encoded text are detected as utf-8."""
        assert detect_file_encoding(b"plain ascii text") == "utf-8"
        assert detect_file_encoding("示例文本".encode("utf-8")) == "utf-8"
        assert detect_file_encoding("示例文本".encode("utf-8-sig")) == "utf-8"

    def test_gb18030_family_bytes_detected_as_gb18030(self):
        """gb18030/gbk encoded text decodes with the gb18030 candidate."""
        assert detect_file_encoding("示例文本".encode("gb18030")) == "gb18030"
        assert detect_file_encoding("中文测试".encode("gbk")) == "gb18030"

    def test_custom_fallback_encodings_are_respected(self):
        """The caller provided candidate list controls the detection."""
        big5_data = "你好".encode("big5")
        # default candidate order reports gb18030 (it precedes big5)...
        assert detect_file_encoding(big5_data) == "gb18030"
        # ...while an explicit list can surface big5 / latin-1 instead.
        assert detect_file_encoding(big5_data, fallback_encodings=("big5",)) == "big5"
        assert detect_file_encoding("示例文本".encode("gb18030"),
                                    fallback_encodings=("latin-1",)) == "latin-1"

    def test_invalid_bytes_fall_back_to_latin1(self):
        """Bytes rejected by every CJK candidate fall back to latin-1."""
        assert detect_file_encoding(bytes([0x80])) == "latin-1"

    def test_bytearray_and_file_like_sources(self):
        """Bytearray and binary stream sources are supported."""
        data = "示例文本".encode("gb18030")
        assert detect_file_encoding(bytearray(data)) == "gb18030"

        stream = io.BytesIO(data)
        assert detect_file_encoding(stream) == "gb18030"
        assert stream.tell() == 0  # original pointer must be preserved

    def test_file_like_stream_at_end_returns_utf8(self):
        """Reading from an exhausted stream yields an empty sample."""
        stream = io.BytesIO(b"abc")
        stream.seek(0, io.SEEK_END)
        assert detect_file_encoding(stream) == "utf-8"
        assert stream.tell() == 3  # pointer is restored to the end

    def test_path_inputs_and_sample_size_probe(self, tmp_path):
        """Paths (str or Path) work and sample_size bounds the probe."""
        gb_path = tmp_path / "gb.txt"
        gb_path.write_bytes("示例文本".encode("gb18030"))
        assert detect_file_encoding(gb_path) == "gb18030"
        assert detect_file_encoding(str(gb_path)) == "gb18030"

        mixed_path = tmp_path / "mixed.txt"
        mixed_path.write_bytes(b"a" * 64 + "示例文本".encode("gb18030"))
        assert detect_file_encoding(mixed_path) == "gb18030"
        # A sample cut before the gb18030 tail only sees valid utf-8.
        assert detect_file_encoding(mixed_path, sample_size=64) == "utf-8"
