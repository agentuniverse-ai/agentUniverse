# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 15:21
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: singleton.py
from functools import wraps


def singleton(cls):
    """Decorator to make a class a Singleton class (only one instance), using closure."""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
