# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: output_object.py
import json


class OutputObject(object):
    """A container that exposes agent output data both as attributes and via helpers.

    Each key of the wrapped params dict is copied onto the object as an
    attribute, while to_dict/to_json_str/get_data give dict-style access.
    """

    def __init__(self, params: dict):
        """Initialize the output object with the given parameters.

        Args:
            params: The output data mapping; a copy is stored internally and
                each key is also set as an attribute of this object.
        """
        self.__params = params.copy()
        for k, v in self.__params.items():
            self.__dict__[k] = v

    def to_dict(self):
        return self.__params.copy()

    def to_json_str(self):
        """Serialize the wrapped parameters to a JSON string.

        Returns:
            The JSON string of the stored parameters; non-ASCII characters
            are not escaped.
        """
        return json.dumps(self.__params, ensure_ascii=False)

    def get_data(self, key, default=None):
        """Return the value of a wrapped parameter.

        Args:
            key: The name of the parameter to read.
            default: The value returned when the parameter is absent.

        Returns:
            The parameter value if present, otherwise the default.
        """
        return self.__params.get(key, default)
