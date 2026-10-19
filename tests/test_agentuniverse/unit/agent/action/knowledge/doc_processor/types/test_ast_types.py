# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_ast_types.py
"""Unit tests for the doc_processor AST TypedDict type definitions."""

from agentuniverse.agent.action.knowledge.doc_processor.types.ast_types import (
    AstNode,
    AstNodePoint,
    CodeBoundary,
)


def _keys(typed_dict_cls) -> list:
    """Return the declared field names of a TypedDict in order."""
    return list(typed_dict_cls.__annotations__)


class TestAstTypes:
    """Test the TypedDict schemas declared in ast_types."""

    def test_ast_node_point_fields(self):
        """AstNodePoint declares row and column integer fields."""
        assert _keys(AstNodePoint) == ["row", "column"]

    def test_ast_node_fields(self):
        """AstNode declares the full node schema in the expected order."""
        assert _keys(AstNode) == [
            "type", "start_point", "end_point", "start_byte", "end_byte",
            "text", "children",
        ]

    def test_code_boundary_fields(self):
        """CodeBoundary declares its boundary schema in the expected order."""
        assert _keys(CodeBoundary) == ["start", "end", "type", "name", "node"]

    def test_ast_node_point_constructs(self):
        """A valid AstNodePoint value can be constructed and read back."""
        point = AstNodePoint(row=3, column=7)
        assert point["row"] == 3
        assert point["column"] == 7

    def test_ast_node_with_nested_children(self):
        """An AstNode can hold a nested child node and be read back."""
        child = AstNode(
            type="child",
            start_point={"row": 1, "column": 0},
            end_point={"row": 1, "column": 5},
            start_byte=0,
            end_byte=5,
            text="hello",
            children=None,
        )
        node = AstNode(
            type="root",
            start_point={"row": 0, "column": 0},
            end_point={"row": 9, "column": 0},
            start_byte=0,
            end_byte=42,
            text="root",
            children=[child],
        )
        assert node["type"] == "root"
        assert node["children"][0]["text"] == "hello"
        assert node["children"][0]["end_point"] == {"row": 1, "column": 5}

    def test_code_boundary_constructs(self):
        """A valid CodeBoundary value can be constructed and read back."""
        boundary = CodeBoundary(start=0, end=10, type="def", name="foo", node=None)
        assert boundary["start"] == 0
        assert boundary["end"] == 10
        assert boundary["name"] == "foo"
