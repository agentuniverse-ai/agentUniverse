# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_txt_reader.py
"""Unit tests for TxtReader and LineTxtReader."""

import pytest

from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader, LineTxtReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestTxtReaders:
    """Test TxtReader and LineTxtReader implementations."""

    @pytest.fixture
    def text_file(self, tmp_path):
        """Create a plain text file with three lines."""
        path = tmp_path / "sample.txt"
        path.write_text("alpha\nbeta\nlast line\n", encoding="utf-8")
        return path

    def test_txt_reader_reads_whole_file_as_one_document(self, text_file):
        """TxtReader returns a single Document holding the whole file content."""
        docs = TxtReader().load_data(text_file)
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].text == "alpha\nbeta\nlast line\n"

    def test_txt_reader_default_metadata_has_file_name(self, text_file):
        """TxtReader default metadata contains the basename of the file."""
        docs = TxtReader().load_data(text_file)
        assert docs[0].metadata == {"file_name": "sample.txt"}

    def test_txt_reader_ext_info_merged_into_metadata(self, text_file):
        """ext_info keys are merged into metadata and can override file_name."""
        docs = TxtReader().load_data(text_file, ext_info={"source": "local", "file_name": "renamed.txt"})
        assert docs[0].metadata["source"] == "local"
        assert docs[0].metadata["file_name"] == "renamed.txt"
        assert docs[0].text == "alpha\nbeta\nlast line\n"

    def test_line_txt_reader_splits_lines_into_documents(self, text_file):
        """Each raw line (newline kept) becomes its own Document."""
        docs = LineTxtReader().load_data(text_file)
        assert len(docs) == 3
        assert [d.text for d in docs] == ["alpha\n", "beta\n", "last line\n"]
        assert all(d.metadata == {"file_name": "sample.txt"} for d in docs)

    def test_line_txt_reader_ext_info_applied_to_each_document(self, text_file):
        """Every line document receives the merged ext_info metadata."""
        docs = LineTxtReader().load_data(text_file, ext_info={"source": "local"})
        assert len(docs) == 3
        assert all(d.metadata["source"] == "local" for d in docs)

    def test_empty_file(self, tmp_path):
        """An empty file yields no line documents but one empty txt document."""
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")
        assert LineTxtReader().load_data(empty) == []
        docs = TxtReader().load_data(empty)
        assert len(docs) == 1
        assert docs[0].text == ""

    def test_non_utf8_gbk_file_decoded(self, tmp_path):
        """A GBK-encoded file is decoded with a detected encoding."""
        content = "中文内容\n第二行\n"
        path = tmp_path / "gbk.txt"
        path.write_bytes(content.encode("gbk"))
        docs = TxtReader().load_data(path)
        assert len(docs) == 1
        assert docs[0].text == content

    def test_ext_info_none_and_empty_keep_default_metadata(self, text_file):
        """Passing no ext_info or an empty dict keeps only the file_name key."""
        assert TxtReader().load_data(text_file)[0].metadata == {"file_name": "sample.txt"}
        assert TxtReader().load_data(text_file, ext_info={})[0].metadata == {"file_name": "sample.txt"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
