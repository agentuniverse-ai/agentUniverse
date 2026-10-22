# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
)
from agentuniverse.agent.action.knowledge.reader.file.toml_reader import TomlReader


def test_toml_reader_loads_nested_unicode_configuration(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text(
        'title = "知识库"\n[server]\nport = 8080\nfeatures = ["a", "b"]\n',
        encoding="utf-8",
    )

    documents = TomlReader().load_data(path, ext_info={"source": "test"})

    assert len(documents) == 1
    assert '"title": "知识库"' in documents[0].text
    assert '"port": 8080' in documents[0].text
    assert documents[0].metadata["format"] == "toml"
    assert documents[0].metadata["source"] == "test"


def test_toml_reader_chains_parse_errors(tmp_path):
    path = tmp_path / "broken.toml"
    path.write_text("port = [", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid TOML") as error:
        TomlReader().load_data(path)

    assert error.value.__cause__ is not None


def test_toml_reader_is_registered_for_toml_extension():
    assert DEFAULT_FILE_READERS[".toml"] is TomlReader
