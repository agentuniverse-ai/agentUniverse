import json

import pytest

from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader


@pytest.mark.parametrize("encoding", ["utf-16-le", "utf-16-be", "utf-32", "gb18030"])
def test_json_reader_preserves_encoded_text(tmp_path, encoding):
    path = tmp_path / "data.json"
    data = {"message": "你好"}
    path.write_bytes(json.dumps(data, ensure_ascii=False).encode(encoding))

    document, = JsonReader().load_data(path)

    assert json.loads(document.text) == data
