# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 11:54
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: application_config_manager.py
from typing import Optional
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


@singleton
class ApplicationConfigManager(object):
    """The ConfigManager class, which is used to load and manage the configuration."""

    def __init__(self):
        """Initialize the ConfigManager."""
        self.__app_configer: Optional[AppConfiger] = None

    @property
    def app_configer(self):
        """Return the AppConfiger object."""
        if self.__app_configer is None:
            raise ValueError("The AppConfiger object is not set.")
        return self.__app_configer

    @app_configer.setter
    def app_configer(self, app_configer: AppConfiger):
        """Set the AppConfiger object."""
        self.__app_configer = app_configer

