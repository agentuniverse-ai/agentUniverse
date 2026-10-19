import json
import sys
import types
import urllib.parse
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader import (
    yuque_reader,
)
from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.feishu_reader import (
    PublicFeishuReader,
)
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer

CLOUD_READER_PACKAGE = "agentuniverse.agent.action.knowledge.reader.cloud_file_reader"
FEISHU_URL = "https://www.feishu.cn/docx/public-document"
YUQUE_URL = "https://www.yuque.com/example/book"


def _build_app_configer() -> AppConfiger:
    configer = Configer()
    configer.value = {
        "BASE_INFO": {"appname": "cloud_reader_test"},
        "CORE_PACKAGE": {"default": []},
        "PLUGINS": {"llm_plugins": []},
    }
    return AppConfiger().load_by_configer(configer)


@pytest.fixture
def registered_cloud_readers(monkeypatch):
    application_config_manager = ApplicationConfigManager()
    previous_app_configer = application_config_manager._ApplicationConfigManager__app_configer
    reader_manager = ReaderManager()
    previous_reader_map = reader_manager._instance_obj_map
    reader_manager._instance_obj_map = {}
    application_config_manager.app_configer = _build_app_configer()

    session = MagicMock()
    session_factory = MagicMock(return_value=session)
    monkeypatch.setattr(yuque_reader.requests, "Session", session_factory)
    monkeypatch.setitem(sys.modules, "selenium", None)

    try:
        agent_universe = AgentUniverse()
        component_configers = agent_universe.scan(
            [CLOUD_READER_PACKAGE],
            ConfigTypeEnum.YAML,
            ComponentEnum.READER,
        )
        agent_universe._AgentUniverse__register(
            ComponentEnum.READER,
            component_configers,
        )
        yield reader_manager, component_configers, session
    finally:
        reader_manager._instance_obj_map = previous_reader_map
        application_config_manager._ApplicationConfigManager__app_configer = previous_app_configer


def _module(name: str, *, package: bool = False) -> types.ModuleType:
    module = types.ModuleType(name)
    if package:
        module.__path__ = []
    return module


def _install_fake_selenium(monkeypatch, drivers: list[MagicMock]):
    selenium = _module("selenium", package=True)
    webdriver = _module("selenium.webdriver", package=True)
    chrome = _module("selenium.webdriver.chrome", package=True)
    chrome_options = _module("selenium.webdriver.chrome.options")
    support = _module("selenium.webdriver.support", package=True)
    support_ui = _module("selenium.webdriver.support.ui")

    options = MagicMock()
    options_class = MagicMock(return_value=options)
    chrome_factory = MagicMock(side_effect=drivers)
    waiters = []

    def build_waiter(driver, _timeout):
        waiter = MagicMock()
        waiter.until.side_effect = lambda condition: condition(driver)
        waiters.append(waiter)
        return waiter

    web_driver_wait = MagicMock(side_effect=build_waiter)

    selenium.webdriver = webdriver
    webdriver.Chrome = chrome_factory
    webdriver.chrome = chrome
    webdriver.support = support
    chrome.options = chrome_options
    chrome_options.Options = options_class
    support.ui = support_ui
    support_ui.WebDriverWait = web_driver_wait

    modules = {
        "selenium": selenium,
        "selenium.webdriver": webdriver,
        "selenium.webdriver.chrome": chrome,
        "selenium.webdriver.chrome.options": chrome_options,
        "selenium.webdriver.support": support,
        "selenium.webdriver.support.ui": support_ui,
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)

    return SimpleNamespace(
        chrome_factory=chrome_factory,
        options=options,
        waiters=waiters,
        web_driver_wait=web_driver_wait,
    )


def _encoded_yuque_book() -> str:
    payload = {
        "book": {
            "id": 42,
            "toc": [{"title": "Example Book", "url": "first-page"}],
        }
    }
    encoded = urllib.parse.quote(json.dumps(payload))
    return f'JSON.parse(decodeURIComponent("{encoded}"));'


def test_cloud_reader_yaml_scan_and_register_without_selenium(
    registered_cloud_readers,
):
    reader_manager, component_configers, session = registered_cloud_readers

    assert {configer.name for configer in component_configers} == {
        "default_feishu_reader",
        "default_yuque_reader",
    }
    feishu_reader = reader_manager.get_instance_obj(
        "default_feishu_reader",
        new_instance=False,
    )
    registered_yuque_reader = reader_manager.get_instance_obj(
        "default_yuque_reader",
        new_instance=False,
    )
    assert isinstance(feishu_reader, Reader)
    assert isinstance(registered_yuque_reader, Reader)
    assert feishu_reader.driver is None
    assert feishu_reader.component_config_path.endswith("feishu_reader.yaml")
    assert registered_yuque_reader.component_config_path.endswith("yuque_reader.yaml")
    assert registered_yuque_reader.session is session


def test_feishu_load_data_lazily_reuses_and_closes_driver(monkeypatch):
    first_driver = MagicMock()
    first_driver.execute_script.return_value = True
    first_driver.page_source = (
        "<html><body><h1>Demo</h1>" '<div class="doc-content"><p>Rendered body</p></div>' "</body></html>"
    )
    second_driver = MagicMock()
    second_driver.execute_script.return_value = True
    second_driver.page_source = first_driver.page_source
    selenium = _install_fake_selenium(
        monkeypatch,
        [first_driver, second_driver],
    )
    reader = PublicFeishuReader(wait_timeout=2.5)

    assert reader.driver is None
    assert selenium.chrome_factory.call_count == 0

    documents = reader.load_data(FEISHU_URL)
    reader.load_data(FEISHU_URL)

    assert selenium.chrome_factory.call_count == 1
    assert first_driver.get.call_args_list == [call(FEISHU_URL), call(FEISHU_URL)]
    assert selenium.web_driver_wait.call_args_list == [
        call(first_driver, 2.5),
        call(first_driver, 2.5),
    ]
    assert first_driver.execute_script.call_count == 2
    readiness_script = first_driver.execute_script.call_args.args[0]
    assert "document.readyState === 'complete'" in readiness_script
    assert "document.body.innerText.trim().length > 0" in readiness_script
    assert [waiter.until.call_count for waiter in selenium.waiters] == [1, 1]
    assert len(documents) == 1
    assert documents[0].text == "Title: Demo\nRendered body"
    assert documents[0].metadata == {"source": FEISHU_URL}

    reader.close()
    reader.close()
    first_driver.quit.assert_called_once_with()
    assert reader.driver is None

    reader.load_data(FEISHU_URL)
    assert selenium.chrome_factory.call_count == 2
    assert reader.driver is second_driver
    reader.close()
    second_driver.quit.assert_called_once_with()


def test_feishu_missing_selenium_fails_on_first_load(monkeypatch):
    monkeypatch.setitem(sys.modules, "selenium", None)
    reader = PublicFeishuReader()

    assert reader.driver is None
    with pytest.raises(ImportError, match="pip install selenium"):
        reader.load_data(FEISHU_URL)
    assert reader.driver is None


def test_registered_yuque_reader_loads_with_mocked_http(
    registered_cloud_readers,
    monkeypatch,
):
    reader_manager, _, session = registered_cloud_readers
    reader = reader_manager.get_instance_obj(
        "default_yuque_reader",
        new_instance=False,
    )
    book_response = MagicMock()
    book_response.raise_for_status.return_value = None
    book_response.text = _encoded_yuque_book()
    title_response = MagicMock()
    title_response.raise_for_status.return_value = None
    title_response.text = "<html><head><title>Example Book · 语雀</title></head></html>"
    page_response = MagicMock()
    page_response.status_code = 200
    page_response.json.return_value = {"data": {"sourcecode": "# Offline body"}}
    session.get.side_effect = [
        book_response,
        title_response,
        page_response,
    ]
    sleep = MagicMock()
    monkeypatch.setattr(yuque_reader.time, "sleep", sleep)

    documents = reader.load_data(YUQUE_URL)

    assert len(documents) == 1
    assert documents[0].text == "# Offline body"
    assert documents[0].metadata == {
        "source": YUQUE_URL,
        "doc_title": "Example Book",
        "sanitized_title": "Example Book",
    }
    assert [request.kwargs["timeout"] for request in session.get.call_args_list] == [
        10,
        10,
        20,
    ]
    sleep.assert_called_once()
