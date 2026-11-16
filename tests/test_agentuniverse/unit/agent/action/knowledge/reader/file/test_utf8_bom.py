import json

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_json_reader_accepts_utf8_with_or_without_bom(tmp_path, encoding):
    path = tmp_path / "data.json"
    data = {"message": "你好"}
    path.write_text(json.dumps(data, ensure_ascii=False), encoding=encoding)

    documents = JsonReader().load_data(path)

    assert len(documents) == 1
    assert json.loads(documents[0].text) == data
    assert documents[0].metadata["file_name"] == "data.json"


@pytest.mark.parametrize("reader, suffix, content, expected", [
    (TxtReader, ".txt", "你好\ufeff世界", "你好\ufeff世界"),
    (CSVReader, ".csv", "name,value\n你好,42\n", "name, value\n你好, 42"),
])
def test_text_readers_strip_only_the_initial_bom(tmp_path, reader, suffix, content, expected):
    path = tmp_path / ("data" + suffix)
    path.write_text(content, encoding="utf-8-sig")

    documents = reader().load_data(path)

    assert documents[0].text == expected
