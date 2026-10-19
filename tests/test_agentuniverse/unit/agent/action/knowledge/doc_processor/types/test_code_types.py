# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_code_types.py

"""Unit tests for the code analysis TypedDicts in code_types."""

from typing import Dict, Optional

from agentuniverse.agent.action.knowledge.doc_processor.types.ast_types \
    import AstNode
from agentuniverse.agent.action.knowledge.doc_processor.types.code_types \
    import CodeFeatures, CodeRepresentation, ChunkRepresentation
from agentuniverse.agent.action.knowledge.doc_processor.types.metrics_types \
    import CodeMetrics


class TestCodeTypes:
    """Test the code feature/representation TypedDict schemas."""

    def test_all_types_are_dict_subclasses(self):
        assert issubclass(CodeFeatures, dict)
        assert issubclass(CodeRepresentation, dict)
        assert issubclass(ChunkRepresentation, dict)

    def test_code_features_required_keys(self):
        assert CodeFeatures.__required_keys__ == {
            "node_counts", "code_metrics", "identifier_count",
            "function_count", "class_count", "statement_count",
        }

    def test_code_features_annotations(self):
        annotations = CodeFeatures.__annotations__
        assert annotations["node_counts"] == Dict[str, int]
        assert annotations["code_metrics"] is CodeMetrics
        assert annotations["identifier_count"] is int
        assert annotations["function_count"] is int
        assert annotations["class_count"] is int
        assert annotations["statement_count"] is int

    def test_code_representation_required_keys_and_annotations(self):
        assert CodeRepresentation.__required_keys__ == {
            "ast", "features", "language", "code_length",
        }
        annotations = CodeRepresentation.__annotations__
        assert annotations["ast"] is AstNode
        assert annotations["features"] is CodeFeatures
        assert annotations["language"] is str
        assert annotations["code_length"] is int

    def test_chunk_representation_required_keys_and_annotations(self):
        assert ChunkRepresentation.__required_keys__ == {
            "ast", "code", "language", "name", "type",
        }
        annotations = ChunkRepresentation.__annotations__
        assert annotations["ast"] is AstNode
        assert annotations["code"] is str
        assert annotations["name"] == Optional[str]  # Optional[str] field
        assert annotations["type"] is str

    def test_valid_nested_dict_matches_schema(self):
        node = {"type": "function_definition", "children": []}
        features = {
            "node_counts": {"function_definition": 1},
            "code_metrics": {"line_count": 5, "code_line_count": 4,
                             "avg_line_length": 20.0, "max_line_length": 40,
                             "character_count": 100},
            "identifier_count": 3, "function_count": 1,
            "class_count": 0, "statement_count": 2,
        }
        representation = {
            "ast": node,
            "features": features,
            "language": "python",
            "code_length": 100,
        }
        assert isinstance(representation, dict)
        assert set(representation.keys()) == CodeRepresentation.__required_keys__
