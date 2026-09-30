# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 09:19
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_service.py
import pytest
from unittest.mock import patch

from agentuniverse.agent_serve.service import Service
from agentuniverse.agent_serve.service_configer import ServiceConfiger
from tests.test_agentuniverse.mock.agent_serve.mock_application_config_manager import MockApplicationConfigManager
from tests.test_agentuniverse.mock.agent_serve.mock_agent import MockAgent


@patch('agentuniverse.agent_serve.service.Agent', new=MockAgent)
@patch('agentuniverse.agent_serve.service.ApplicationConfigManager', new=MockApplicationConfigManager)
def test_service():
    """Test that service.
    """
    agent = MockAgent({"test_result": "ok"})
    service_configer = ServiceConfiger()
    service_configer._ServiceConfiger__name = "test_service"
    service_configer._ServiceConfiger__description = "test_service"
    service_configer._ServiceConfiger__agent = agent
    service = Service(name="test_service")
    service.initialize_by_component_configer(service_configer)
    run_result = service.run()
    assert service.run() == '{"test_result": "ok"}'


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
