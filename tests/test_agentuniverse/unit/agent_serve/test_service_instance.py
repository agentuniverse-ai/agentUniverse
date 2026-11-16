# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import unittest

# @Time    : 2024/3/18 22:45
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_service_instance.py
import pytest
from unittest.mock import patch

from agentuniverse.agent_serve.service_instance import ServiceInstance
from tests.test_agentuniverse.mock.agent_serve.mock_service_manager import (
    ServiceManager, TEST_SERVICE_LIST, TEST_STR
)


@patch('agentuniverse.agent_serve.service_instance.ServiceManager', new=ServiceManager)
def test_service_instance():
    """Test that service instance.
    """
    unittest.TestCase().assertRaises(Exception,
                                     ServiceInstance.__init__,
                                     "not_exist_service_code")

    service_instance = ServiceInstance(TEST_SERVICE_LIST[0])
    result = service_instance.run()
    assert result == TEST_STR


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

