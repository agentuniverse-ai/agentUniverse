# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 14:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py
import enum
from enum import Enum


@enum.unique
class ToolTypeEnum(Enum):
    """Enumeration of the supported agent tool types.

    Members:
        API: Tool type with value 'api'.
        MCP: Tool type with value 'mcp'.
        FUNC: Tool type with value 'func'.
    """
    API = 'api'
    MCP = 'mcp'
    FUNC = 'func'
