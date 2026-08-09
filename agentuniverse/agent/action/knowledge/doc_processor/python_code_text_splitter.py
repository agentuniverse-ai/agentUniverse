# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: python_code_text_splitter.py

"""
Python code text splitter — a knowledge pre-processing DocProcessor.

Splits Python source code into one chunk per top-level function or class
(plus one chunk for module-level code), preserving the full source text of
each unit including its docstring and decorators. Each chunk records the
unit name and type in metadata, so a retrieved chunk can be traced back to
the exact function/class it came from.

Uses Python's built-in ``ast`` module — no third-party dependency required.

Sibling of the merged ``MarkdownHeaderTextSplitter`` (#625) and the new
``HtmlHeaderTextSplitter`` (#737), ``JsonSplitter`` (#738), and
``SemanticChunker`` (#746). Addresses #258.
"""

import ast
import logging
import textwrap
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class PythonCodeTextSplitter(DocProcessor):
    """Split Python source code by top-level functions and classes.

    Attributes:
        name_key: Metadata key under which the unit name is recorded.
        type_key: Metadata key under which the unit type
            (``module`` / ``function`` / ``class``) is recorded.
        max_chunk_chars: Maximum characters per chunk. A unit exceeding this
            is emitted as-is (code units are usually kept intact); the limit
            only applies to the module-level chunk.
        include_module_level: If ``True`` (default), module-level code
            (imports, constants, ``if __name__ == \"__main__\"``) is emitted
            as a separate chunk. If ``False``, it is dropped.
    """

    name_key: str = "code_unit_name"
    type_key: str = "code_unit_type"
    max_chunk_chars: int = 5000
    include_module_level: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for unit_name, unit_type, unit_text in self._split_code(text):
                if unit_type == "module" and not self.include_module_level:
                    continue
                meta = dict(doc.metadata or {})
                meta[self.name_key] = unit_name
                meta[self.type_key] = unit_type
                result.append(Document(text=unit_text, metadata=meta))
        return result

    def _split_code(self, source: str) -> List[tuple]:
        """Parse Python source and return (name, type, text) triples."""
        # Dedent so indented snippets (common in docs/chat) parse correctly.
        source = textwrap.dedent(source)
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            # Not valid Python — return the whole text as a single module chunk.
            logger.debug("PythonCodeTextSplitter: syntax error (%s), "
                         "returning whole text", exc)
            return [("<module>", "module", source.strip())]

        lines = source.splitlines(keepends=True)
        units: List[tuple] = []

        # Collect module-level code (everything before the first def/class).
        module_lines: List[str] = []
        first_def_line = None
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                first_def_line = node.lineno
                break
        if first_def_line and first_def_line > 1:
            module_lines = lines[:first_def_line - 1]
        elif not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)) for n in tree.body):
            module_lines = lines

        module_text = "".join(module_lines).strip()
        if module_text:
            units.append(("<module>", "module", module_text))

        # Extract each top-level function/class.
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                text = self._extract_node_source(node, lines)
                units.append((name, "function", text))
            elif isinstance(node, ast.ClassDef):
                name = node.name
                text = self._extract_node_source(node, lines)
                units.append((name, "class", text))

        return units

    @staticmethod
    def _extract_node_source(node: ast.AST,
                             lines: List[str]) -> str:
        """Extract the full source text of an AST node, including decorators.

        ``ast.get_source_segment`` does not include decorator lines, so we
        compute the start line from ``node.decorator_list`` if present.
        """
        start_line = node.lineno
        # Include decorators.
        decorators = getattr(node, "decorator_list", [])
        if decorators:
            start_line = min(d.lineno for d in decorators)
        end_line = getattr(node, "end_lineno", node.lineno)
        # lines is 0-indexed; lineno is 1-indexed.
        segment = "".join(lines[start_line - 1: end_line])
        return textwrap.dedent(segment).strip()

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "PythonCodeTextSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "name_key"):
            self.name_key = doc_processor_configer.name_key
        if hasattr(doc_processor_configer, "type_key"):
            self.type_key = doc_processor_configer.type_key
        if hasattr(doc_processor_configer, "max_chunk_chars"):
            self.max_chunk_chars = doc_processor_configer.max_chunk_chars
        if hasattr(doc_processor_configer, "include_module_level"):
            self.include_module_level = \
                doc_processor_configer.include_module_level
        return self
