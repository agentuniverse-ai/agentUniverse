# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:05
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: ast_types.py

from typing import List, Any, Optional, TypedDict


class AstNodePoint(TypedDict):
    row: int
    column: int


class AstNode(TypedDict):
    type: str
    start_point: AstNodePoint
    end_point: AstNodePoint
    start_byte: int
    end_byte: int
    text: Optional[str]
    children: Optional[List['AstNode']]


class CodeBoundary(TypedDict):
    start: int
    end: int
    type: str
    name: Optional[str]
    node: Any
