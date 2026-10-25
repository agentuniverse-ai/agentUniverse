from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


XLSX_READER_YAML = "agentuniverse/agent/action/knowledge/reader/file/xlsx_reader.yaml"


def test_default_reader_registry_covers_file_reader_formats():
    expected = {
        "epub": "default_epub_reader",
        "xlsx": "xlsx_reader",
        "7z": "default_sevenzip_reader",
    }

    for file_type, reader_name in expected.items():
        assert ReaderManager.DEFAULT_READER[file_type] == reader_name


def test_sevenzip_legacy_alias_remains_available():
    assert ReaderManager.DEFAULT_READER["sevenzip"] == "default_sevenzip_reader"


def test_xlsx_yaml_bootstraps_and_reader_manager_resolves_reader(monkeypatch):
    configer = Configer(path=XLSX_READER_YAML).load()
    component_configer = ComponentConfiger().load_by_configer(configer)

    component_class = ComponentConfigerUtil.get_component_object_clz_by_component_configer(
        component_configer
    )
    assert component_class is XlsxReader

    app_config_manager = ApplicationConfigManager()
    previous_app_configer = getattr(app_config_manager, "_ApplicationConfigManager__app_configer", None)
    monkeypatch.setattr(
        app_config_manager,
        "_ApplicationConfigManager__app_configer",
        SimpleNamespace(base_info_appname="xlsx-bootstrap-test"),
    )

    reader = component_class().initialize_by_component_configer(component_configer)
    manager = ReaderManager()
    instance_code = reader.get_instance_code()
    manager.register(instance_code, reader)

    try:
        resolved = manager.get_file_default_reader("xlsx", new_instance=False)
        assert isinstance(resolved, XlsxReader)
        assert resolved.name == "xlsx_reader"
    finally:
        manager._instance_obj_map.pop(instance_code, None)
        monkeypatch.setattr(
            app_config_manager,
            "_ApplicationConfigManager__app_configer",
            previous_app_configer,
        )
