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
    """Enumeration of the supported tool types.

    Attributes:
        API: REST API based tool, identified by the value 'api'.
        MCP: MCP (Model Context Protocol) based tool, identified by the value 'mcp'.
        FUNC: local Python function based tool, identified by the value 'func'.
    """

    API = 'api'
    MCP = 'mcp'
    FUNC = 'func'
