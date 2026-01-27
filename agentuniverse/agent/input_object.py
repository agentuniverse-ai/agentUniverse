# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:39
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: input_object.py
import json


class InputObject(object):
    """A generic input data container class providing dictionary-like data storage and access interfaces.

    This class converts dictionary data into object attributes, supporting dynamic data addition and retrieval,
    while maintaining the integrity of the original dictionary data.

    Attributes:
        __params: Private attribute storing the original dictionary data
    """
    def __init__(self, params: dict):
        """Initialize the input object.

        Args:
            params (dict): Input parameter dictionary that will be converted to object attributes
        """
        self.__params = params
        for k, v in params.items():
            self.__dict__[k] = v

    def to_dict(self):
        """Convert the input object to dictionary format.

        Returns:
            dict: Dictionary containing all parameters
        """
        return self.__params

    def to_json_str(self):
        """Convert the input object to JSON string.

        Returns:
            str: JSON string representation of the parameters
        """
        return json.dumps(self.__params)

    def add_data(self, key, value):
        """Add data to the input object.

        Args:
            key (str): Data key name
            value (Any): Data value
        """
        self.__params[key] = value
        self.__dict__[key] = value

    def get_data(self, key, default=None):
        """Retrieve data from the input object.

        Args:
            key (str): Data key name.
            default (Optional[Any]): Default value to return when key does
                not exist. Defaults to None.
        Returns:
            Any: Value corresponding to the key, or default value if key doesn't exist
        """
        return self.__params.get(key, default)
