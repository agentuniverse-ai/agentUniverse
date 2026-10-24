"""Exercise fallback text decoding through real ZIP members."""
import io
import json
import zipfile

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader


def write_zip(path, members):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members:
            archive.writestr(name, content)


@pytest.mark.parametrize("suffix", [".json", ".yaml", ".log"])
@pytest.mark.parametrize("encoding", ["utf-8", "gb18030", "gbk"])
def test_fallback_text_preserves_chinese(tmp_path, suffix, encoding):
    text = 'message: "中文资料，欢迎阅读"\r\nstatus: ready\r\n'
    if encoding == "gb18030":
        text += "emoji: 🌏\r\n"
    path = tmp_path / "documents.zip"
    member = "docs/message" + suffix
    write_zip(path, [(member, text.encode(encoding))])
    ext_info = {"source": "encoding regression"}

    documents = ZipReader().load_data(path, ext_info=ext_info)

    assert len(documents) == 1
    assert documents[0].text == text.replace("\r\n", "\n")
    assert documents[0].metadata["archive_path"] == member
    assert documents[0].metadata["source"] == ext_info["source"]
    assert ext_info == {"source": "encoding regression"}


def test_non_utf8_after_long_ascii_prefix(tmp_path):
    text = "a" * (64 * 1024) + "中文内容🌏\r\n"
    path = tmp_path / "long.zip"
    write_zip(path, [("long.log", text.encode("gb18030"))])

    documents = ZipReader(stream_chunk_size=257).load_data(path)

    assert documents[0].text == text.replace("\r\n", "\n")


@pytest.mark.parametrize("chunk_size", [1, 7])
def test_utf8_multibyte_across_sample_and_read_boundaries(tmp_path, chunk_size):
    text = "a" * (32 * 1024 - 1) + "中文🌏\r\nend"
    path = tmp_path / "unicode.zip"
    write_zip(path, [("unicode.yaml", text.encode("utf-8"))])

    documents = ZipReader(stream_chunk_size=chunk_size).load_data(path)

    assert documents[0].text == text.replace("\r\n", "\n")


def test_utf8_bom_json_can_be_parsed(tmp_path):
    text = '{"message": "中文资料"}'
    path = tmp_path / "bom.zip"
    write_zip(path, [("config.json", text.encode("utf-8-sig"))])

    documents = ZipReader().load_data(path)

    assert documents[0].text == text
    assert json.loads(documents[0].text) == {"message": "中文资料"}


def test_nested_mixed_encodings_through_file_reader(tmp_path):
    nested = io.BytesIO()
    write_zip(nested, [("settings.yaml", "城市: 北京\r\n".encode("gbk"))])
    path = tmp_path / "mixed.zip"
    write_zip(path, [
        ("first.json", '{"城市": "上海"}'.encode("utf-8")),
        ("nested.zip", nested.getvalue()),
        ("last.LOG", "完成🌏\r\n".encode("gb18030")),
    ])

    documents = FileReader().load_data([path], ext_info={"batch": "mixed"})

    assert [doc.text for doc in documents] == [
        '{"城市": "上海"}', "城市: 北京\n", "完成🌏\n",
    ]
    assert [doc.metadata["archive_path"] for doc in documents] == [
        "first.json", "nested.zip/settings.yaml", "last.LOG",
    ]
    assert [doc.metadata["archive_depth"] for doc in documents] == [0, 1, 0]
    assert all(doc.metadata["batch"] == "mixed" for doc in documents)


def test_ascii_and_empty_fallback_members(tmp_path):
    path = tmp_path / "ascii.zip"
    write_zip(path, [("empty.log", b""), ("plain.conf", b"ready\r\n")])

    documents = ZipReader().load_data(path)

    assert len(documents) == 1
    assert documents[0].text == "ready\n"


def test_text_stream_starts_at_current_position_and_stays_open():
    stream = io.BytesIO(b"prefix" + "中文资料🌏\r\n".encode("gb18030"))
    stream.seek(len(b"prefix"))

    text = ZipReader(stream_chunk_size=1)._read_text(stream)

    assert text == "中文资料🌏\n"
    assert not stream.closed
