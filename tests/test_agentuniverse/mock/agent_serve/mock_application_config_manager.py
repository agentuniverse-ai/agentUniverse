# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 21:03
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_application_config_manager.py

BASE_INFO_APPNAME = "test_app"


class MockAppConfiger:

    """Mockappconfiger.
    """
    def __init__(self):
        """Initialize the __init__ instance.
        """
        self.base_info_appname = BASE_INFO_APPNAME


class MockApplicationConfigManager:
    """Mock class of ApplicationConfigManager."""

    def __init__(self):
        """Initialize the __init__ instance.
        """
        self.app_configer = MockAppConfiger()