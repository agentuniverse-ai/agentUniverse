# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent_serve.service_configer import ServiceConfiger
from agentuniverse.base.config.configer import Configer


def _build_configer(value: dict, path: str = "config/test_service.yaml") -> Configer:
    configer = Configer(path)
    configer.value = value
    return configer


def test_service_configer_requires_agent():
    configer = _build_configer({
        "name": "test_service",
        "description": "service without agent",
    })

    with pytest.raises(ValueError) as exc_info:
        ServiceConfiger().load_by_configer(configer)

    message = str(exc_info.value)
    assert "test_service" in message
    assert "config/test_service.yaml" in message
    assert "must define a non-empty 'agent'" in message


def test_service_configer_reports_missing_agent_context():
    mock_agent_manager = MagicMock()
    mock_agent_manager.get_instance_obj.return_value = None
    mock_agent_manager.get_instance_name_list.return_value = [
        "sample_app.agent.existing_agent"
    ]
    fake_agent_manager_module = types.ModuleType("agentuniverse.agent.agent_manager")
    fake_agent_manager_module.AgentManager = lambda: mock_agent_manager
    configer = _build_configer({
        "name": "test_service",
        "description": "service with unknown agent",
        "agent": "missing_agent",
    })

    with patch.dict(sys.modules, {
        "agentuniverse.agent.agent_manager": fake_agent_manager_module
    }):
        with pytest.raises(ValueError) as exc_info:
            ServiceConfiger().load_by_configer(configer)

    message = str(exc_info.value)
    assert "missing_agent" in message
    assert "test_service" in message
    assert "config/test_service.yaml" in message
    assert "sample_app.agent.existing_agent" in message
