"""Exercise JSONL loading using real UTF-8 files and component routing."""
import importlib
import json
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.jsonl_reader import JsonlReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize("as_string", [False, True])
def test_records_preserve_unicode_and_physical_line_numbers(tmp_path, as_string):
    path = tmp_path / "corpus.jsonl"
    path.write_bytes(
        '\n{"text": "中文 🚀", "nested": {"ok": true}}\r\n \t\r\n[1, 2]'.encode("utf-8")
    )
    docs = JsonlReader().load_data(str(path) if as_string else path)
    assert [json.loads(doc.text) for doc in docs] == [
        {"text": "中文 🚀", "nested": {"ok": True}}, [1, 2]
    ]
    assert "中文 🚀" in docs[0].text
    assert [doc.metadata["line_number"] for doc in docs] == [2, 4]
    assert [doc.metadata["json_type"] for doc in docs] == ["object", "array"]
    assert docs[0].metadata["file_name"] == path.name
    assert docs[0].metadata["file_path"] == str(path)


@pytest.mark.parametrize("value", [None, False, True, 0, -3.25, "", "escaped\nline"])
def test_json_primitive_records(tmp_path, value):
    path = tmp_path / "values.ndjson"
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    doc, = JsonlReader().load_data(path)
    assert json.loads(doc.text) == value
    assert doc.metadata["json_type"] == "primitive"


@pytest.mark.parametrize("record", ["1e400", '{"precise": 0.12345678901234567890}'])
def test_source_numbers_are_not_changed_by_float_conversion(tmp_path, record):
    path = tmp_path / "numbers.jsonl"
    path.write_text(record + "\n", encoding="utf-8")
    doc, = JsonlReader().load_data(path)
    assert doc.text == record


@pytest.mark.parametrize("contents", ["", "\n\r\n \t\n"])
def test_empty_and_blank_files(tmp_path, contents):
    path = tmp_path / "empty.jsonl"
    path.write_text(contents, encoding="utf-8")
    assert JsonlReader().load_data(path) == []


def test_metadata_is_independent_and_ext_info_is_not_modified(tmp_path):
    path = tmp_path / "metadata.jsonl"
    path.write_text('{}\n{}\n', encoding="utf-8")
    extra = {"source": "uploaded", "file_name": "display.jsonl"}
    first, second = JsonlReader().load_data(path, ext_info=extra)
    assert first.metadata["source"] == second.metadata["source"] == "uploaded"
    assert first.metadata["file_name"] == "display.jsonl"
    first.metadata["source"] = "changed"
    assert second.metadata["source"] == "uploaded"
    assert extra == {"source": "uploaded", "file_name": "display.jsonl"}


@pytest.mark.parametrize("invalid", [
    '{"unfinished":', '{} {}', 'NaN', 'Infinity', '-Infinity', '\ufeff{}'
])
def test_invalid_record_reports_source_and_physical_line(tmp_path, invalid):
    path = tmp_path / "broken.jsonl"
    path.write_text('{}\n\n' + invalid + '\n', encoding="utf-8")
    with pytest.raises(ValueError) as error:
        JsonlReader().load_data(path)
    assert str(path) in str(error.value)
    assert "line 3" in str(error.value)
    assert isinstance(error.value.__cause__, ValueError)
    # Reading must release the source even after a parse failure (also on Windows).
    path.unlink()


def test_non_utf8_input_is_not_silently_replaced(tmp_path):
    path = tmp_path / "invalid_utf8.jsonl"
    path.write_bytes(b'{"text": "\xff"}\n')
    with pytest.raises(UnicodeDecodeError):
        JsonlReader().load_data(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        JsonlReader().load_data(tmp_path / "missing.jsonl")


@pytest.mark.parametrize("suffix", [".jsonl", ".ndjson", ".JSONL", ".NDJSON"])
def test_file_reader_routes_both_extensions(tmp_path, suffix):
    path = tmp_path / ("data" + suffix)
    path.write_text('{"id": 1}\n{"id": 2}\n', encoding="utf-8")
    docs = FileReader().load_data(file_paths=[path], ext_info={"collection": "test"})
    assert [json.loads(doc.text) for doc in docs] == [{"id": 1}, {"id": 2}]
    assert all(doc.metadata["collection"] == "test" for doc in docs)


def test_yaml_component_and_manager_lookup(tmp_path, monkeypatch):
    module = importlib.import_module(JsonlReader.__module__)
    config_path = Path(module.__file__).with_suffix(".yaml")
    config = ComponentConfiger(Configer(str(config_path)).load()).load()
    reader_class = getattr(importlib.import_module(config.metadata_module),
                           config.metadata_class)
    reader = reader_class().initialize_by_component_configer(config)
    assert config.metadata_type == "READER"
    manager = ReaderManager()
    # Isolate the singleton's pool and application name, restoring both afterwards.
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    app_config = Configer()
    app_config.value = {"BASE_INFO": {"appname": "jsonl_reader_test"}}
    app_manager = ApplicationConfigManager()
    previous_app = app_manager.__dict__.copy()
    app_manager.app_configer = AppConfiger().load_by_configer(app_config)
    path = tmp_path / "routed.jsonl"
    path.write_text('{"routed": true}\n', encoding="utf-8")
    try:
        manager.register(reader.get_instance_code(), reader)
        for file_type in ("jsonl", "ndjson"):
            doc, = manager.get_file_default_reader(file_type).load_data(path)
            assert json.loads(doc.text) == {"routed": True}
    finally:
        app_manager.__dict__.clear()
        app_manager.__dict__.update(previous_app)
