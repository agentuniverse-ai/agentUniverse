# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 11:43
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: custom_key_configer.py

import os

from agentuniverse.base.annotation.singleton import singleton
from ..configer import Configer


@singleton
class CustomKeyConfiger(Configer):
    """Use to manage user secret key."""
    def __init__(self, config_path: str = None):
        self._Configer__value = {}
        super().__init__(config_path)
        if config_path:
            try:
                self.load()
            except FileNotFoundError as e:
                print(f"Custom key file {config_path} read error, "
                      f"skip load custom key.")
        key_list = self._Configer__value.get("KEY_LIST")
        if isinstance(key_list, dict):
            for key, value in key_list.items():
                os.environ[key] = str(value)
