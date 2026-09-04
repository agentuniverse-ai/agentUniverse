# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: input_object.py
import json


class InputObject(object):
    """Container that holds the input parameters of an agent and exposes them both as dict-like data and object attributes.
    """
    def __init__(self, params: dict):
        """Initialize the input object from a params dict.

        Args:
            params(dict): The input parameters; each key is also exposed as an attribute.
        """
        self.__params = params.copy()
        for k, v in self.__params.items():
            self.__dict__[k] = v

    def to_dict(self):
        return self.__params.copy()

    def to_json_str(self):
        """Serialize the input parameters to a JSON string.

        Returns:
            str: The JSON representation of the parameters.
        """
        return json.dumps(self.__params)

    def add_data(self, key, value):
        """Add or update a single input parameter.

        Args:
            key: The parameter key.
            value: The parameter value.
        """
        self.__params[key] = value
        self.__dict__[key] = value

    def get_data(self, key, default=None):
        """Return the value of an input parameter.

        Args:
            key: The parameter key.
            default: The value returned when the key is absent.

        Returns:
            The stored value or the default.
        """
        return self.__params.get(key, default)
