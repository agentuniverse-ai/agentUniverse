import sys
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer

SYSTEM_READER_PACKAGES = [
    "agentuniverse.agent.action.knowledge.reader.file",
    "agentuniverse.agent.action.knowledge.reader.web",
    "agentuniverse.agent.action.knowledge.reader.image",
]
WEB_AND_IMAGE_READER_PACKAGES = SYSTEM_READER_PACKAGES[1:]
OPTIONAL_READER_DEPENDENCIES = {
    "bs4",
    "easyocr",
    "httpx",
    "paddleocr",
    "pdf2image",
    "playwright",
    "pypdf",
    "pytesseract",
    "readability",
    "requests",
    "trafilatura",
    "transformers",
}


class CustomWebReader(Reader):
    name: str = "default_web_page_reader"

    def _load_data(self, *args, **kwargs):
        return []


def _build_app_configer(reader_packages=None):
    configer = Configer()
    configer.value = {
        "BASE_INFO": {"appname": "reader_registration_test"},
        "CORE_PACKAGE": {
            "default": [],
            "reader": reader_packages or [],
        },
        "PLUGINS": {"llm_plugins": []},
    }
    return AppConfiger().load_by_configer(configer)


def _loaded_optional_reader_modules():
    return {
        module_name
        for module_name in sys.modules
        if module_name.split(".", maxsplit=1)[0] in OPTIONAL_READER_DEPENDENCIES
    }


@pytest.fixture
def isolated_reader_registration():
    application_config_manager = ApplicationConfigManager()
    previous_app_configer = application_config_manager._ApplicationConfigManager__app_configer
    reader_manager = ReaderManager()
    previous_reader_map = reader_manager._instance_obj_map
    reader_manager._instance_obj_map = {}

    try:
        yield application_config_manager, reader_manager
    finally:
        reader_manager._instance_obj_map = previous_reader_map
        application_config_manager._ApplicationConfigManager__app_configer = previous_app_configer


def test_default_reader_packages_follow_custom_packages():
    agent_universe = AgentUniverse()
    app_configer = _build_app_configer(["custom.reader.package"])

    with (
        patch.object(agent_universe, "scan", return_value=[]) as mock_scan,
        patch.object(agent_universe, "_AgentUniverse__register"),
    ):
        agent_universe._AgentUniverse__scan_and_register(app_configer)

    reader_scan_call = next(call for call in mock_scan.call_args_list if call.args[2] == ComponentEnum.READER)
    assert reader_scan_call.args[0] == ["custom.reader.package", *SYSTEM_READER_PACKAGES]


def test_web_and_image_readers_are_registered_without_loading_optional_dependencies(
    isolated_reader_registration,
):
    application_config_manager, reader_manager = isolated_reader_registration
    application_config_manager.app_configer = _build_app_configer()
    agent_universe = AgentUniverse()
    optional_modules_before = _loaded_optional_reader_modules()

    component_configers = agent_universe.scan(
        WEB_AND_IMAGE_READER_PACKAGES,
        ConfigTypeEnum.YAML,
        ComponentEnum.READER,
    )
    config_names = {component_configer.name for component_configer in component_configers}
    assert {
        "default_web_page_reader",
        "default_rendered_web_page_reader",
        "default_image_reader",
        "default_image_ocr_reader",
        "default_scanned_pdf_ocr_reader",
    } <= config_names

    agent_universe._AgentUniverse__register(ComponentEnum.READER, component_configers)

    assert type(reader_manager.get_file_default_reader("url")).__name__ == "WebPageReader"
    assert type(reader_manager.get_file_default_reader("png")).__name__ == "ImageOCRReader"
    assert reader_manager.get_default_instance() is None
    assert _loaded_optional_reader_modules() == optional_modules_before


def test_custom_reader_wins_over_system_reader(isolated_reader_registration):
    application_config_manager, reader_manager = isolated_reader_registration
    application_config_manager.app_configer = _build_app_configer()
    custom_reader = CustomWebReader()
    reader_manager.register(custom_reader.get_instance_code(), custom_reader)
    agent_universe = AgentUniverse()

    component_configers = agent_universe.scan(
        ["agentuniverse.agent.action.knowledge.reader.web"],
        ConfigTypeEnum.YAML,
        ComponentEnum.READER,
    )
    agent_universe._AgentUniverse__register(ComponentEnum.READER, component_configers)

    assert (
        reader_manager.get_instance_obj(
            "default_web_page_reader",
            new_instance=False,
        )
        is custom_reader
    )
