# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: input_object.py
import json


class InputObject(object):
    """Input object for agent execution.

    Encapsulates input parameters for agent execution, providing convenient
    access to parameters through dictionary-like interface.
    """

    def __init__(self, params: dict):
        """Initialize InputObject with parameters.

        Args:
            params (dict): Input parameters dictionary.
        """
        self.__params = params
        for k, v in params.items():
            self.__dict__[k] = v

    def to_dict(self):
        """Convert input object to dictionary.

        Returns:
            dict: Parameters dictionary.
        """
        return self.__params

    def to_json_str(self):
        """Convert input object to JSON string.

        Returns:
            str: JSON string representation of parameters.
        """
        return json.dumps(self.__params)

    def add_data(self, key, value):
        """Add or update a parameter value.

        Args:
            key: Parameter key.
            value: Parameter value.
        """
        self.__params[key] = value
        self.__dict__[key] = value

    def get_data(self, key, default=None):
        """Get parameter value by key.

        Args:
            key: Parameter key.
            default: Default value if key not found.

        Returns:
            Any: Parameter value or default.
        """
        return self.__params.get(key, default)
