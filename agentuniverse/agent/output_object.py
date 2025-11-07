# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: output_object.py
import json


class OutputObject(object):
    """A generic output data container class providing dictionary-like data storage and access interfaces.

    This class converts dictionary data into object attributes, supporting convenient data retrieval
    and serialization, while maintaining the integrity of the original dictionary data.

    Attributes:
        __params: Private attribute storing the original dictionary data
    """
    def __init__(self, params: dict):
        """Initialize the output object.

        Args:
            params (dict): Output parameter dictionary that will be converted to object attributes
        """
        self.__params = params
        for k, v in params.items():
            self.__dict__[k] = v

    def to_dict(self):
        """Convert the output object to dictionary format.

        Returns:
            dict: Dictionary containing all output parameters
        """
        return self.__params

    def to_json_str(self):
        """Convert the output object to JSON string.

        Returns:
            str: JSON string representation of the output parameters
        """
        return json.dumps(self.__params, ensure_ascii=False)

    def get_data(self, key, default=None):
        """Retrieve data from the output object.

        Args:
            key (str): Data key name
            default (Optional[Any]): Default value to return when key does not exist
        Returns:
            Any: Value corresponding to the key, or default value if key doesn't exist
        """
        return self.__params.get(key, default)
