# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py
from enum import Enum


class NodeEnum(Enum):
    """The enumeration of the supported nodes."""

    START = "start"
    END = "end"
    LLM = "llm"
    TOOL = "tool"
    KNOWLEDGE = "knowledge"
    AGENT = "agent"
    CONDITION = "ifelse"

    @staticmethod
    def to_value_list():
        """Return the value list of the enumeration."""
        return [item.value for item in NodeEnum]

    @staticmethod
    def from_value(value):
        """Return the enum member corresponding to the given value."""
        for item in NodeEnum:
            if item.value == value:
                return item
        raise ValueError(f"No enum member with value {value}")


class NodeStatusEnum(Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ConditionComparisonEnum(Enum):
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    BLANK = "blank"
