# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 17:47
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_enum.py
from enum import Enum


class ComponentEnum(Enum):
    """The enumeration of the supported components."""
    AGENT = "AGENT"
    KNOWLEDGE = "KNOWLEDGE"
    LLM = "LLM"
    PLANNER = "PLANNER"
    TOOL = "TOOL"
    TOOLKIT = "TOOLKIT"
    DEFAULT = "DEFAULT"
    SERVICE = "SERVICE"
    MEMORY = "MEMORY"
    PROMPT = "PROMPT"
    SQLDB_WRAPPER = "SQLDB_WRAPPER"
    PRODUCT = "PRODUCT"
    WORKFLOW = "WORKFLOW"
    EMBEDDING = "EMBEDDING"
    DOC_PROCESSOR = "DOC_PROCESSOR"
    READER = "READER"
    STORE = "STORE"
    RAG_ROUTER = "RAG_ROUTER"
    QUERY_PARAPHRASER = "QUERY_PARAPHRASER"
    WORK_PATTERN = "WORK_PATTERN"
    MEMORY_COMPRESSOR = "MEMORY_COMPRESSOR"
    MEMORY_STORAGE = "MEMORY_STORAGE"
    LOG_SINK = "LOG_SINK"
    LLM_CHANNEL = "LLM_CHANNEL"

    @staticmethod
    def to_value_list():
        """Return the value list of the enumeration."""
        return [item.value for item in ComponentEnum]

    @staticmethod
    def from_value(value):
        """Return the enum member corresponding to the given value."""
        for item in ComponentEnum:
            if item.value == value:
                return item
        raise ValueError(f"No enum member with value {value}")
