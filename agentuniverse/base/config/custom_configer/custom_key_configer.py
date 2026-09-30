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
        """Initialize the CustomKeyConfiger.

        Args:
            config_path(str): the path of the custom key config file; when given
                and readable, the KEY_LIST entries are exported as environment
                variables, otherwise loading is skipped.
        """
        self._Configer__value = {}
        super().__init__(config_path)
        if config_path:
            try:
                self.load()
            except FileNotFoundError as e:
                print(f"Custom key file {config_path} read error, "
                      f"skip load custom key.")
        if self._Configer__value.get("KEY_LIST"):
            for key, value in self._Configer__value.get("KEY_LIST").items():
                os.environ[key] = str(value)