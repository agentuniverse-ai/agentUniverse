"""Exercise real TSV files, quoted fields and default component dispatch."""
import importlib
import io
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.tsv_reader import TSVReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.configer import Configer


TABLE = '名称\t说明\n条目\t"含\t制表符"\n下一项\t"第一行\n第二行"\n'
EXPECTED = '名称, 说明\n条目, 含\t制表符\n下一项, 第一行\n第二行'


@pytest.mark.parametrize("encoding", ["utf-8", "gb18030"])
@pytest.mark.parametrize("source_kind", ["str_path", "path", "binary_stream"])
def test_paths_and_binary_inputs(tmp_path, encoding, source_kind):
    path = tmp_path / "table.tsv"
    contents = TABLE.encode(encoding)
    path.write_bytes(contents)
    if source_kind == "str_path":
        source = str(path)
    elif source_kind == "path":
        source = path
    else:
        source = io.BytesIO(contents)
    try:
        doc, = TSVReader().load_data(source, ext_info={"collection": "faq"})
        assert doc.text == EXPECTED
        expected_name = "unknown" if source_kind == "binary_stream" else path.name
        assert doc.metadata == {"file_name": expected_name, "collection": "faq"}
        if source_kind == "binary_stream":
            assert not source.closed
    finally:
        if source_kind == "binary_stream":
            source.close()


def test_text_stream_remains_open():
    with io.StringIO(TABLE) as source:
        doc, = TSVReader().load_data(source)
        assert doc.text == EXPECTED
        assert not source.closed


def test_custom_quote_character():
    with io.StringIO("key\tvalue\nitem\t'left\tright'\n") as source:
        doc, = TSVReader().load_data(source, quotechar="'")
    assert doc.text == "key, value\nitem, left\tright"


def test_crlf_inside_quoted_field_is_preserved(tmp_path):
    path = tmp_path / "windows.tsv"
    path.write_bytes(b'key\tvalue\r\nitem\t"first\r\nsecond"\r\n')
    doc, = TSVReader().load_data(path)
    assert doc.text == "key, value\nitem, first\r\nsecond"


@pytest.mark.parametrize("suffix", [".tsv", ".TSV"])
def test_file_reader_dispatches_tsv(tmp_path, suffix):
    path = tmp_path / ("table" + suffix)
    path.write_bytes(TABLE.encode("utf-8"))
    docs = FileReader().load_data(file_paths=[path], ext_info={"collection": "faq"})
    assert len(docs) == 1
    assert docs[0].text == EXPECTED
    assert docs[0].metadata == {"file_name": path.name, "collection": "faq"}


def test_empty_input():
    with io.StringIO("") as source:
        doc, = TSVReader().load_data(source)
    assert doc.text == ""


def test_missing_file_reports_original_cause(tmp_path):
    with pytest.raises(ValueError) as error:
        TSVReader().load_data(tmp_path / "missing.tsv")
    assert isinstance(error.value.__cause__, FileNotFoundError)


def test_yaml_component_and_manager_lookup(tmp_path, monkeypatch):
    module = importlib.import_module(TSVReader.__module__)
    config_path = Path(module.__file__).with_suffix(".yaml")
    config = ComponentConfiger(Configer(str(config_path)).load()).load()
    reader_class = getattr(importlib.import_module(config.metadata_module),
                           config.metadata_class)
    reader = reader_class().initialize_by_component_configer(config)
    assert config.metadata_type == "READER"
    manager = ReaderManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    app_config = Configer()
    app_config.value = {"BASE_INFO": {"appname": "tsv_reader_test"}}
    app_manager = ApplicationConfigManager()
    previous_app = app_manager.__dict__.copy()
    app_manager.app_configer = AppConfiger().load_by_configer(app_config)
    path = tmp_path / "routed.tsv"
    path.write_text("key\tvalue\nitem\tanswer\n", encoding="utf-8")
    try:
        manager.register(reader.get_instance_code(), reader)
        doc, = manager.get_file_default_reader("tsv").load_data(path)
        assert doc.text == "key, value\nitem, answer"
    finally:
        app_manager.__dict__.clear()
        app_manager.__dict__.update(previous_app)
