"""Exercise supported file formats through the shared loading entry point."""
import json

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import (
    LineTxtReader, TxtReader)


def test_json_is_kept_in_a_mixed_file_collection(tmp_path):
    """Preserve JSON text/metadata and the existing order and skip behavior."""
    text_path = tmp_path / "readme.txt"
    text_path.write_text("Read me", encoding="utf-8")
    json_path = tmp_path / "records.JSON"
    data = {"name": "中文记录", "records": [1, None, {"enabled": True}]}
    json_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    skipped = tmp_path / "ignored.unsupported"
    skipped.write_text("skip", encoding="utf-8")
    csv_path = tmp_path / "table.csv"
    csv_path.write_text("name,value\none,2", encoding="utf-8")
    extra = {"batch": "sample"}

    docs = FileReader().load_data(
        [text_path, json_path, csv_path, skipped], ext_info=extra)

    assert len(docs) == 3
    assert docs[0].text == "Read me"
    assert json.loads(docs[1].text) == data
    assert docs[1].text == json.dumps(data, indent=2, ensure_ascii=False)
    assert docs[1].metadata == {
        "file_name": "records.JSON", "file_path": str(json_path),
        "json_type": "object", "batch": "sample"}
    assert docs[0].metadata["batch"] == "sample"
    assert docs[2].text == "name, value\none, 2"
    assert docs[2].metadata["batch"] == "sample"
    assert extra == {"batch": "sample"}


def test_invalid_json_is_reported_instead_of_silently_skipped(tmp_path):
    """The shared entry point preserves the JSON parser's contextual error."""
    path = tmp_path / "invalid.json"
    path.write_text('{"unfinished":', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError, match="invalid.json"):
        FileReader().load_data([path])


def test_missing_json_is_reported_instead_of_silently_skipped(tmp_path):
    """A recognized but missing JSON source raises the existing file error."""
    path = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError, match="missing.json"):
        FileReader().load_data([path])


@pytest.mark.parametrize("reader_class, expected", [
    (TxtReader, ["one\ntwo\n"]),
    (LineTxtReader, ["one\n", "two\n"]),
])
def test_text_readers_accept_the_forwarded_path(
        tmp_path, reader_class, expected):
    """The public custom-reader map also supports built-ins using fpath."""
    path = tmp_path / "notes.TXT"
    path.write_text("one\ntwo\n", encoding="utf-8")
    reader = FileReader(file_readers={".txt": reader_class})
    docs = reader.load_data([path], ext_info={"group": "notes"})
    assert [doc.text for doc in docs] == expected
    assert all(doc.metadata == {"file_name": "notes.TXT", "group": "notes"}
               for doc in docs)
