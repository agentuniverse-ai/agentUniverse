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
    """Enumeration of the prompt processing strategies supported by prompts."""

    TRUNCATE = 'truncate'
    STUFF = 'stuff'
    MAP_REDUCE = 'map_reduce'

    @classmethod
    def from_value(cls, value):
        """Return the enum member whose value matches the given value case-insensitively.

        Args:
            value: The raw enum value.

        Returns:
            PromptProcessEnum: The matching member.

        Raises:
            ValueError: If no member matches the value.
        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"No enum member with value: {value}")
