import json

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader


def test_file_reader_loads_json_through_default_reader(tmp_path):
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"answer": 42}), encoding="utf-8")

    documents = FileReader().load_data([path])

    assert len(documents) == 1
    assert '"answer": 42' in documents[0].text
    assert documents[0].metadata["json_type"] == "object"
