# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: output_object.py
import json


class OutputObject(object):
    def __init__(self, params: dict):
        self.__params = params.copy()
        for k, v in self.__params.items():
            self.__dict__[k] = v

    def to_dict(self):
        return self.__params.copy()

    def to_json_str(self):
        return json.dumps(self.__params, ensure_ascii=False)

    def get_data(self, key, default=None):
        return self.__params.get(key, default)
