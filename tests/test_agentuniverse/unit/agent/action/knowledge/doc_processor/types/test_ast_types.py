# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_ast_types.py

"""Unit tests for the AST TypedDicts in ast_types."""

from agentuniverse.agent.action.knowledge.doc_processor.types.ast_types \
    import AstNode, AstNodePoint, CodeBoundary


class TestAstTypes:
    """Test the AST related TypedDict schemas."""

    def test_all_types_are_dict_subclasses(self):
        assert issubclass(AstNode, dict)
        assert issubclass(AstNodePoint, dict)
        assert issubclass(CodeBoundary, dict)

    def test_ast_node_point_keys(self):
        assert AstNodePoint.__required_keys__ == {"row", "column"}
        assert AstNodePoint.__optional_keys__ == frozenset()
        annotations = AstNodePoint.__annotations__
        assert annotations["row"] is int
        assert annotations["column"] is int

    def test_ast_node_required_keys(self):
        assert AstNode.__required_keys__ == {
            "type", "start_point", "end_point", "start_byte",
            "end_byte", "text", "children",
        }
        assert AstNode.__optional_keys__ == frozenset()

    def test_ast_node_annotations(self):
        annotations = AstNode.__annotations__
        assert annotations["type"] is str
        assert annotations["start_point"] is AstNodePoint
        assert annotations["end_point"] is AstNodePoint
        assert annotations["start_byte"] is int
        assert annotations["end_byte"] is int

    def test_code_boundary_keys(self):
        assert CodeBoundary.__required_keys__ == {
            "start", "end", "type", "name", "node",
        }
        assert CodeBoundary.__optional_keys__ == frozenset()
        annotations = CodeBoundary.__annotations__
        assert annotations["start"] is int
        assert annotations["end"] is int
        assert annotations["type"] is str

    def test_valid_nested_ast_dict(self):
        point = {"row": 1, "column": 0}
        node = {
            "type": "function_definition",
            "start_point": point,
            "end_point": {"row": 3, "column": 4},
            "start_byte": 0,
            "end_byte": 30,
            "text": "def f():\n    pass\n",
            "children": [
                {"type": "identifier", "start_point": point,
                 "end_point": point, "start_byte": 4, "end_byte": 5,
                 "text": "f", "children": None},
            ],
        }
        assert isinstance(node, dict)
        assert set(node.keys()) == AstNode.__required_keys__
        assert node["type"] == "function_definition"
        assert node["children"][0]["type"] == "identifier"
        assert node["children"][0]["children"] is None

    def test_code_boundary_node_holds_arbitrary_node(self):
        boundary = {"start": 0, "end": 5, "type": "function",
                    "name": "f", "node": object()}
        assert isinstance(boundary, dict)
        assert set(boundary.keys()) == CodeBoundary.__required_keys__
