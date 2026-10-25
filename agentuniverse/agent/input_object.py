# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: input_object.py
import json


class InputObject(object):
    """Input data with attribute access for keys that do not shadow the API.

    Colliding keys remain available through get_data and serialization.
    """
    def __init__(self, params: dict):
        self.__params = params.copy()
        for k, v in self.__params.items():
            if k != '_InputObject__params' and (
                    not isinstance(k, str) or not hasattr(type(self), k)):
                self.__dict__[k] = v

    def to_dict(self):
        return self.__params.copy()

    def to_json_str(self):
        return json.dumps(self.__params)

    def add_data(self, key, value):
        self.__params[key] = value
        if key != '_InputObject__params' and (
                not isinstance(key, str) or not hasattr(type(self), key)):
            self.__dict__[key] = value

    def get_data(self, key, default=None):
        return self.__params.get(key, default)
