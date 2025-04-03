# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 14:09
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: code_ast_processor.py
import json
from typing import List, Dict, Any, Optional, cast

from agentuniverse.agent.action.knowledge.doc_processor.types.ast_types import AstNode, AstNodePoint, CodeBoundary
from agentuniverse.agent.action.knowledge.doc_processor.types.code_types import CodeFeatures, CodeRepresentation, ChunkRepresentation
from agentuniverse.agent.action.knowledge.doc_processor.types.metrics_types import CodeMetrics

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class CodeAstProcessor(DocProcessor):

    max_depth: int = 8
    language_dir: str = None
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_node_len: int = 100
    _parser: Optional[Any] = None
    _languages: Dict[str, Any] = {}

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        result_docs = []
        for doc in origin_docs:
            code = doc.text
            language = doc.metadata.get('language', 'unknown') if doc.metadata else 'unknown'
            metadata = doc.metadata.copy() if doc.metadata else {}
            metadata['document_type'] = 'code_ast'
            result_docs.extend(self._process_with_tree_sitter(code, language, metadata))
        return result_docs

    def _process_with_tree_sitter(self, code: str, language: str,
                                  metadata: Dict[str, Any]) -> List[Document]:
        def _ensure_language() -> None:
            if language not in self._languages:
                try:
                    from tree_sitter import Language
                    from importlib import import_module
                    module_name = f'tree_sitter_{language}'
                    lang_module = import_module(module_name)
                    self._languages[language] = Language(lang_module.language())
                except ImportError:
                    raise ImportError(
                        f"Could not import {module_name}. Install with: pip install {module_name}")
        _ensure_language()

        result_docs: List[Document] = []
        self._parser.language = self._languages[language]
        tree = self._parser.parse(bytes(code, "utf8"))
        ast_json: AstNode = self._convert_tree_to_json(tree.root_node, code)
        features: CodeFeatures = self._extract_features(tree.root_node, code, language)
        repr: CodeRepresentation = {
            "ast": ast_json,
            "features": features,
            "language": language,
            "code_length": len(code)
        }
        metadata['processing_method'] = 'tree_sitter'
        ast_doc: Document = Document(
            text=json.dumps(repr),
            metadata=metadata
        )
        result_docs.append(ast_doc)
        if len(code) > self.chunk_size:
            chunk_docs = self._generate_code_chunks(
                code, tree.root_node, language, metadata)
            result_docs.extend(chunk_docs)
        return result_docs

    def _convert_tree_to_json(self, node, code: str, depth: int = 0) -> AstNode:
        if depth > self.max_depth:
            return cast(AstNode, {"type": "max_depth_reached"})
        if not node:
            return cast(AstNode, {})

        start_byte, end_byte = node.start_byte, node.end_byte
        text = code[start_byte:end_byte] if end_byte <= len(code) else ""

        start_point: AstNodePoint = {"row": node.start_point[0], "column": node.start_point[1]}
        end_point: AstNodePoint = {"row": node.end_point[0], "column": node.end_point[1]}

        result: AstNode = {
            "type": node.type,
            "start_point": start_point,
            "end_point": end_point,
            "start_byte": start_byte,
            "end_byte": end_byte
        }

        if len(text) < self.max_node_len or node.child_count == 0:
            result["text"] = text

        if node.child_count > 0:
            children = []
            for child in node.children:
                child_json = self._convert_tree_to_json(child, code, depth + 1)
                if child_json:
                    children.append(child_json)
            result["children"] = children

        return result

    def _extract_features(self, node: Any, code: str, language: str) -> CodeFeatures:

        features: CodeFeatures = {
            "node_counts": self._count_node_types(node),
            "code_metrics": self._calculate_code_metrics(code, language),
            "identifier_count": 0,
            "function_count": 0,
            "class_count": 0,
            "statement_count": 0
        }

        cursor = node.walk()

        def _visit():
            nonlocal features
            current_node = cursor.node

            if current_node.type == "identifier":
                features["identifier_count"] += 1
            elif current_node.type in ("function_definition", "method_definition", "function_declaration"):
                features["function_count"] += 1
            elif current_node.type in ("class_definition", "class_declaration"):
                features["class_count"] += 1
            elif "statement" in current_node.type:
                features["statement_count"] += 1

            if cursor.goto_first_child():
                _visit()
                cursor.goto_parent()
            if cursor.goto_next_sibling():
                _visit()

        _visit()
        return features

    def _count_node_types(self, root_node) -> Dict[str, int]:
        counts = {}

        def _traverse(node):
            if node.type not in counts:
                counts[node.type] = 0
            counts[node.type] += 1

            for child in node.children:
                _traverse(child)

        _traverse(root_node)
        return counts

    def _calculate_code_metrics(self, code: str, language: str) -> CodeMetrics:

        lines = code.splitlines()
        code_lines = [line.strip() for line in lines if line.strip(
        ) and not line.strip().startswith(('#', '//', '/*', '*', '*/'))]

        metrics: CodeMetrics = {
            "line_count": len(lines),
            "code_line_count": len(code_lines),
            "avg_line_length": sum(len(line) for line in code_lines) / max(len(code_lines), 1),
            "max_line_length": max([len(line) for line in code_lines]) if code_lines else 0,
            "character_count": len(code)
        }
        return metrics

    def _generate_code_chunks(
            self,
            code: str,
            root_node,
            language: str,
            metadata: Dict[str, Any]) -> List[Document]:
        chunks = []
        lines = code.splitlines()
        boundaries = []

        def _collect_declarations(node, path=""):

            if node.type in ("function_definition", "method_definition", "class_definition",
                             "function_declaration", "method_declaration", "class_declaration"):
                start_line = node.start_point[0]
                end_line = node.end_point[0]

                if end_line - start_line >= 3:
                    node_type = "function" if "function" in node.type else "class"
                    name = None

                    for child in node.children:
                        if child.type == "identifier":
                            name = code[child.start_byte:child.end_byte]
                            break

                    boundary: CodeBoundary = {
                        "start": start_line,
                        "end": end_line,
                        "type": node_type,
                        "name": name,
                        "node": node
                    }
                    boundaries.append(boundary)

        traverse_cursor = root_node.walk()

        def _traverse_nodes():
            current_node = traverse_cursor.node

            _collect_declarations(current_node)

            if traverse_cursor.goto_first_child():
                _traverse_nodes()
                traverse_cursor.goto_parent()

            if traverse_cursor.goto_next_sibling():
                _traverse_nodes()

        _traverse_nodes()

        if boundaries:
            for boundary in boundaries:
                start_line = boundary["start"]
                end_line = boundary["end"]

                if end_line - start_line < 3:
                    continue

                chunk_code = "\n".join(lines[start_line:end_line + 1])

                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_type"] = boundary["type"]
                chunk_metadata["chunk_name"] = boundary["name"]
                chunk_metadata["start_line"] = start_line
                chunk_metadata["end_line"] = end_line
                chunk_metadata["document_type"] = "code_chunk"

                try:
                    tree = self._parser.parse(bytes(chunk_code, "utf8"))
                    ast_json = self._convert_tree_to_json(tree.root_node, chunk_code)

                    representation: ChunkRepresentation = {
                        "ast": ast_json,
                        "code": chunk_code,
                        "language": language,
                        "name": boundary["name"],
                        "type": boundary["type"]
                    }

                    chunk_doc = Document(
                        text=json.dumps(representation),
                        metadata=chunk_metadata
                    )
                    chunks.append(chunk_doc)
                except BaseException:

                    chunk_metadata["ast_available"] = False
                    chunks.append(Document(text=chunk_code, metadata=chunk_metadata))

        if len(chunks) < 2 and len(lines) > self.chunk_size:
            for i in range(0, len(lines), self.chunk_size - self.chunk_overlap):
                end_idx = min(i + self.chunk_size, len(lines))
                chunk_code = "\n".join(lines[i:end_idx])

                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_type"] = "window"
                chunk_metadata["start_line"] = i
                chunk_metadata["end_line"] = end_idx - 1
                chunk_metadata["document_type"] = "code_chunk"

                chunks.append(Document(text=chunk_code, metadata=chunk_metadata))

                if end_idx >= len(lines):
                    break

        return chunks

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        super()._initialize_by_component_configer(doc_processor_configer)
        try:
            from tree_sitter import Parser
            self._parser = Parser()
            self._languages = {}
        except ImportError:
            raise ImportError(
                "tree-sitter not available. Install with: pip install tree-sitter")

        if hasattr(doc_processor_configer, "max_depth"):
            self.max_depth = doc_processor_configer.max_depth

        if not hasattr(doc_processor_configer, "language_dir"):
            raise ValueError(
                "language_dir is required - tree-sitter needs compiled language libraries (.so files) to parse code, download from https://tree-sitter.github.io/tree-sitter/#available-parsers")
        self.language_dir = doc_processor_configer.language_dir

        if hasattr(doc_processor_configer, "chunk_size"):
            self.chunk_size = doc_processor_configer.chunk_size

        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap

        if hasattr(doc_processor_configer, "max_node_text_length"):
            self.max_node_len = doc_processor_configer.max_node_len
        return self
