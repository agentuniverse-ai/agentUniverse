# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 22:53
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_service_manager.py
from unittest.mock import MagicMock

TEST_STR = "TEST_STR"
TEST_MOCK_SERVICE = MagicMock()
TEST_MOCK_SERVICE.run.return_value = TEST_STR
TEST_SERVICE_LIST = ["test_app.service.test_service"]
TEST_SERVICE_MAP = {"test_app.service.test_service":TEST_MOCK_SERVICE}


class ServiceManager:
    """Mock class of agentuniverse.agent_serve.service.Service."""

    def __init__(self):
        self.__service_list: list = TEST_SERVICE_LIST
        self.__service_map: dict = TEST_SERVICE_MAP

    def get_instance_obj(self, service_code: str):
        service_base = self.__service_map.get(service_code)
        if service_base is None:
            raise Exception(f"Service {service_code} not found.")
        return service_base