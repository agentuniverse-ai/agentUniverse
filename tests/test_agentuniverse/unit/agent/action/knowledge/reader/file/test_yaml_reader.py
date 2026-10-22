# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
    FileReader,
)
from agentuniverse.agent.action.knowledge.reader.file.yaml_reader import YamlReader


def test_yaml_reader_loads_multi_document_unicode_yaml(tmp_path):
    path = tmp_path / "knowledge.yml"
    path.write_text(
        "name: first\ntext: 开始\n---\n\nitems:\n  - one\n  - 二\n",
        encoding="utf-8",
    )

    documents = YamlReader().load_data(path, ext_info={"source": "test"})

    assert len(documents) == 2
    assert [doc.metadata["document_index"] for doc in documents] == [1, 2]
    assert "开始" in documents[0].text
    assert "二" in documents[1].text
    assert all(doc.metadata["source"] == "test" for doc in documents)


def test_yaml_reader_chains_parse_errors(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("items: [unclosed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML") as error:
        YamlReader().load_data(path)

    assert error.value.__cause__ is not None


def test_yaml_reader_is_registered_for_yaml_extensions():
    assert DEFAULT_FILE_READERS[".yaml"] is YamlReader
    assert DEFAULT_FILE_READERS[".yml"] is YamlReader
    assert FileReader().file_readers[".yaml"] is YamlReader
