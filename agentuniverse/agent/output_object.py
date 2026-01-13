# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: output_object.py
import json


class OutputObject(object):
    """Output object for agent execution results.

    Encapsulates output parameters from agent execution, providing convenient
    access to results through dictionary-like interface.
    """

    def __init__(self, params: dict):
        """Initialize OutputObject with parameters.

        Args:
            params (dict): Output parameters dictionary.
        """
        self.__params = params
        for k, v in params.items():
            self.__dict__[k] = v

    def to_dict(self):
        """Convert output object to dictionary.

        Returns:
            dict: Parameters dictionary.
        """
        return self.__params

    def to_json_str(self):
        """Convert output object to JSON string.

        Returns:
            str: JSON string representation of parameters, preserving non-ASCII characters.
        """
        return json.dumps(self.__params, ensure_ascii=False)

    def get_data(self, key, default=None):
        """Get parameter value by key.

        Args:
            key: Parameter key.
            default: Default value if key not found.

        Returns:
            Any: Parameter value or default.
        """
        return self.__params.get(key, default)
