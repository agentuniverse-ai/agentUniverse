"""Exercise service identity on real Service objects, rather than service mocks."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent_serve.service import Service
from agentuniverse.agent_serve.service_configer import ServiceConfiger
from agentuniverse.agent_serve.service_manager import ServiceManager
from agentuniverse.base.config.configer import Configer


class LocalAgent(Agent):
    def input_keys(self):
        return []

    def output_keys(self):
        return []

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result


@pytest.fixture
def app_context():
    app = SimpleNamespace(base_info_appname="sample_app")
    manager = SimpleNamespace(app_configer=app)
    with patch("agentuniverse.agent_serve.service.ApplicationConfigManager", return_value=manager), \
         patch("agentuniverse.base.component.component_manager_base.ApplicationConfigManager", return_value=manager):
        yield app


def test_constructor_service_code(app_context):
    service = Service(name="chat")
    assert service.service_code == "sample_app.service.chat"


def test_configured_name_is_used_after_yaml_initialization(tmp_path, app_context):
    path = tmp_path / "service.yaml"
    path.write_text("name: configured_chat\ndescription: test service\nagent: local\nmetadata:\n  type: SERVICE\n",
                    encoding="utf-8")
    with patch("agentuniverse.agent.agent_manager.AgentManager") as agents:
        agents.return_value.get_instance_obj.return_value = LocalAgent()
        config = ServiceConfiger().load_by_configer(Configer().load_by_path(str(path)))
    service = Service(name="old_name").initialize_by_component_configer(config)
    assert service.service_code == "sample_app.service.configured_chat"
    assert service.description == "test service"


def test_service_code_can_register_real_service(app_context, monkeypatch):
    manager = ServiceManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    service = Service(name="chat")
    manager.register(service.service_code, service)
    assert manager.get_instance_obj("chat", new_instance=False) is service
    copied = manager.get_instance_obj("chat")
    assert copied is not service
    assert copied.service_code == "sample_app.service.chat"


def test_service_construction_can_precede_app_configuration():
    with patch("agentuniverse.agent_serve.service.ApplicationConfigManager",
               side_effect=ValueError("configuration unavailable")) as manager:
        service = Service(name="chat")
        manager.assert_not_called()
    app = SimpleNamespace(app_configer=SimpleNamespace(base_info_appname="late_app"))
    with patch("agentuniverse.agent_serve.service.ApplicationConfigManager", return_value=app):
        assert service.service_code == "late_app.service.chat"


def test_service_code_tracks_current_name(app_context):
    service = Service(name="first")
    assert service.service_code == "sample_app.service.first"
    service.name = "second"
    assert service.service_code == "sample_app.service.second"
