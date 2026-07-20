# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: input_object.py
import json


class InputObject(object):
    def __init__(self, params: dict):
        self.__params = params.copy()
        for k, v in self.__params.items():
            self.__dict__[k] = v

    def to_dict(self):
        return self.__params.copy()

    def to_json_str(self):
        return json.dumps(self.__params)

    def add_data(self, key, value):
        self.__params[key] = value
        self.__dict__[key] = value

    def get_data(self, key, default=None):
        return self.__params.get(key, default)
