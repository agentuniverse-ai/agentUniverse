# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/16 14:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py
import enum
from enum import Enum


@enum.unique
class PromptProcessEnum(Enum):
    TRUNCATE = "truncate"
    STUFF = "stuff"
    MAP_REDUCE = "map_reduce"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"No enum member with value: {value}")
