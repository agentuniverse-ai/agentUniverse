# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 16:00
# @Author  : kaichuan
# @FileName: __init__.py
"""Context compression strategies for intelligent context reduction."""

from agentuniverse.agent.context.compressor.context_compressor import (
    ContextCompressor,
    CompressionMetrics,
)
from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.compressor.summarize_compressor import SummarizeCompressor
from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor

__all__ = [
    "ContextCompressor",
    "CompressionMetrics",
    "TruncateCompressor",
    "SelectiveCompressor",
    "SummarizeCompressor",
    "AdaptiveCompressor",
]
