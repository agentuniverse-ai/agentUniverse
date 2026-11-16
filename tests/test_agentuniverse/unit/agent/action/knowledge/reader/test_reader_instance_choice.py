"""Reader lookup preserves copying by default and honors explicit sharing."""

import zipfile
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component import component_manager_base


@pytest.fixture
def registry(monkeypatch):
    manager = ReaderManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    monkeypatch.setattr(component_manager_base, "ApplicationConfigManager", lambda: SimpleNamespace(
        app_configer=SimpleNamespace(base_info_appname="reader-test")))
    reader = ZipReader()
    reader._file_count = 0
    reader._readers = {}
    manager.register("reader-test.reader.default_zip_reader", reader)
    return manager, reader


@pytest.mark.parametrize("options", [{}, {"new_instance": True}])
def test_default_and_explicit_copy_keep_zip_read_state_isolated(tmp_path, registry, options):
    manager, registered = registry
    first = manager.get_file_default_reader("zip", **options)
    second = manager.get_file_default_reader("zip", **options)
    assert first is not registered and second is not registered and first is not second
    path = tmp_path / "content.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("content.txt", "hello reader")
    assert [doc.text for doc in first.load_data(path)] == ["hello reader"]
    assert first._file_count == 1
    assert registered._file_count == second._file_count == 0
    assert registered._readers == second._readers == {}


def test_explicit_shared_lookup_returns_registered_identity(registry):
    manager, registered = registry
    result = manager.get_file_default_reader("zip", new_instance=False)
    assert result is registered
    result._readers["custom"] = "marker"
    assert registered._readers == {"custom": "marker"}


@pytest.mark.parametrize("new_instance", [False, True])
def test_unknown_extension_and_unregistered_reader_still_return_none(registry, new_instance):
    manager, _ = registry
    assert manager.get_file_default_reader("unknown", new_instance=new_instance) is None
    manager.unregister("reader-test.reader.default_zip_reader")
    assert manager.get_file_default_reader("zip", new_instance=new_instance) is None
