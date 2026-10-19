# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 22:03
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_simple_service.py

class SimpleService:
    """Mock class of agentuniverse.agent_serve.service.Service."""

    def __init__(self, service_name: str):
        """Initialize the __init__ instance.
        """
        self.service_code = SimpleService.generate_service_code(service_name)

    @staticmethod
    def generate_service_code(service_name: str) -> str:
        """Return the generated service code.
        """
        return "test_app.service." + service_name
