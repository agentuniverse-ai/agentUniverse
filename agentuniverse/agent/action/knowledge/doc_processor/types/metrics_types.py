# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:06
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: metrics_types.py

from typing import TypedDict


class CodeMetrics(TypedDict):
    """Typed dictionary describing basic metrics of a code snippet.

    Attributes:
        line_count: Total number of lines in the snippet.
        code_line_count: Number of non-empty, non-comment code lines.
        avg_line_length: Average length of the code lines.
        max_line_length: Length of the longest code line.
        character_count: Total number of characters in the snippet.
    """
    line_count: int
    code_line_count: int
    avg_line_length: float
    max_line_length: int
    character_count: int
