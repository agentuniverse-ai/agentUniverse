# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:06
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: code_types.py

from typing import Dict, Optional, TypedDict

from agentuniverse.agent.action.knowledge.doc_processor.types.ast_types import AstNode
from agentuniverse.agent.action.knowledge.doc_processor.types.metrics_types import CodeMetrics


class CodeFeatures(TypedDict):
    """TypedDict describing per-node code metrics and feature counts of a parsed code file.

    Keys: node_counts, code_metrics, identifier_count, function_count, class_count, statement_count.
    """
    node_counts: Dict[str, int]
    code_metrics: CodeMetrics
    identifier_count: int
    function_count: int
    class_count: int
    statement_count: int


class CodeRepresentation(TypedDict):
    """TypedDict describing the full representation of a parsed code file.

    Keys: ast, features, language, code_length.
    """
    ast: AstNode
    features: CodeFeatures
    language: str
    code_length: int


class ChunkRepresentation(TypedDict):
    """TypedDict describing one chunk of code extracted from a file.

    Keys: ast, code, language, name, type.
    """
    ast: AstNode
    code: str
    language: str
    name: Optional[str]
    type: str
