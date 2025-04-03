# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:06
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: metrics_types.py

from typing import TypedDict


class CodeMetrics(TypedDict):
    line_count: int
    code_line_count: int
    avg_line_length: float
    max_line_length: int
    character_count: int
