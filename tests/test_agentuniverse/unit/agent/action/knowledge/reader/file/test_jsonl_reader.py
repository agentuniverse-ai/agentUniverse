# -*- coding:utf-8 -*-

import json

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
    FileReader,
)
from agentuniverse.agent.action.knowledge.reader.file.jsonl_reader import JsonlReader


def test_jsonl_reader_loads_records_and_preserves_source_lines(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"event": "start", "message": "开始"}\n'
        '\n'
        '[1, 2, 3]\n'
        '"done"\n',
        encoding="utf-8",
    )

    documents = JsonlReader().load_data(path, ext_info={"source": "test"})

    assert len(documents) == 3
    assert [document.metadata["line_number"] for document in documents] == [1, 3, 4]
    assert [document.metadata["json_type"] for document in documents] == [
        "object", "array", "primitive"
    ]
    assert json.loads(documents[0].text)["message"] == "开始"
    assert json.loads(documents[1].text) == [1, 2, 3]
    assert json.loads(documents[2].text) == "done"
    assert all(document.metadata["source"] == "test" for document in documents)


def test_jsonl_reader_reports_invalid_record_line_and_preserves_cause(tmp_path):
    path = tmp_path / "broken.ndjson"
    path.write_text('{"valid": true}\n{"broken": }\n', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError, match=r"broken\.ndjson at line 2") as error:
        JsonlReader().load_data(path)

    assert isinstance(error.value.__cause__, json.JSONDecodeError)


def test_jsonl_reader_is_registered_for_both_suffixes():
    assert DEFAULT_FILE_READERS[".jsonl"] is JsonlReader
    assert DEFAULT_FILE_READERS[".ndjson"] is JsonlReader
    assert FileReader().file_readers[".jsonl"] is JsonlReader
