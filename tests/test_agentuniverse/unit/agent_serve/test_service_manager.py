# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import unittest

# @Time    : 2024/3/18 22:06
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_service_manager.py
import pytest
from unittest.mock import patch, MagicMock

from agentuniverse.agent_serve.service_manager import ServiceManager
from tests.test_agentuniverse.mock.agent_serve.mock_simple_service import SimpleService
from tests.test_agentuniverse.mock.agent_serve.mock_application_config_manager import MockApplicationConfigManager

@patch("agentuniverse.agent_serve.service_manager.Service", new=SimpleService)
@patch("agentuniverse.base.component.component_manager_base.ApplicationConfigManager", new=MockApplicationConfigManager)
def test_service_manager():
    """Test that service manager.
    """
    service_manager: ServiceManager = ServiceManager()
    mock_service = MagicMock()
    mock_service.name = "test_service_1"
    mock_service.service_code = SimpleService.generate_service_code(
        mock_service.name
    )
    service_manager.register(mock_service.service_code, mock_service)

    service = service_manager.get_instance_obj(mock_service.name)
    assert service.name == mock_service.name

    # register a service with same name
    unittest.TestCase().assertRaises(
        ValueError,
        service_manager.register,
        mock_service.service_code,
        mock_service
    )

    assert len(service_manager.get_instance_name_list()) == 1
    service_manager.unregister(
        mock_service.service_code
    )
    assert len(service_manager.get_instance_name_list()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
