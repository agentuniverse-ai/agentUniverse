# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
)
from agentuniverse.agent.action.knowledge.reader.file.xml_reader import XmlReader


def test_xml_reader_preserves_source_and_extracts_root_metadata(tmp_path):
    path = tmp_path / "feed.xml"
    source = '<?xml version="1.0" encoding="UTF-8"?><feed><item>知识</item></feed>'
    path.write_text(source, encoding="utf-8")

    documents = XmlReader().load_data(path, ext_info={"source": "test"})

    assert len(documents) == 1
    assert documents[0].text == source
    assert documents[0].metadata["root_tag"] == "feed"
    assert documents[0].metadata["source"] == "test"


def test_xml_reader_chains_parse_errors(tmp_path):
    path = tmp_path / "broken.xml"
    path.write_text("<feed><item></feed>", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid XML") as error:
        XmlReader().load_data(path)

    assert error.value.__cause__ is not None


def test_xml_reader_is_registered_for_xml_extension():
    assert DEFAULT_FILE_READERS[".xml"] is XmlReader
