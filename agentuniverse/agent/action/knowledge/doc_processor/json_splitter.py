# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/20
# @FileName: json_splitter.py

"""
JSON structure splitter — a knowledge pre-processing DocProcessor.

Recursively traverses JSON objects/arrays and emits one chunk per leaf
value (or per configurable depth), recording the JSON path as metadata.
This is useful for indexing structured data sources (API docs, database
schemas, configuration files) where each field/value pair should be a
retrievable unit.

Sibling of the merged ``MarkdownHeaderTextSplitter`` (#625) and the
``HtmlHeaderTextSplitter`` (#737): all three address the *knowledge
pre-processing* direction of #258.

Pure Python with no third-party dependency.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class JsonSplitter(DocProcessor):
    """Split JSON documents into one chunk per leaf value or per depth level.

    Traverses the JSON tree and emits a ``Document`` for each scalar value
    found at or below ``max_depth``. The JSON path (e.g. ``root > users > [0]
    > name``) is recorded in metadata under ``path_key``.

    Attributes:
        path_key: Metadata key for the JSON path.
        max_depth: Maximum traversal depth (``None`` = unlimited). At
            ``max_depth``, a nested object/array is serialised as JSON text
            rather than traversed further.
        max_value_length: Maximum characters of a scalar value to include in
            the chunk text; longer values are truncated with an ellipsis.
        drop_empty: If ``True`` (default), empty strings / None / empty
            lists are not emitted as chunks.
    """

    path_key: str = "json_path"
    max_depth: Optional[int] = None
    max_value_length: int = 10_000
    drop_empty: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            parsed = self._parse_json(text)
            if parsed is None:
                # Not valid JSON — emit the original document unchanged.
                result.append(doc)
                continue
            for path, value_text in self._traverse(parsed, depth=0, prefix="root"):
                if self.drop_empty and not value_text.strip():
                    continue
                meta = dict(doc.metadata or {})
                meta[self.path_key] = path
                result.append(Document(text=value_text, metadata=meta))
        return result

    def _parse_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            return None

    def _traverse(self, obj: Any, depth: int, prefix: str) -> List[Tuple[str, str]]:
        """Recursively traverse ``obj`` and yield (path, text) pairs."""
        results: List[Tuple[str, str]] = []

        if self.max_depth is not None and depth >= self.max_depth:
            # At max depth, serialise the remaining structure as a chunk.
            serialised = json.dumps(obj, ensure_ascii=False, default=str)
            results.append((prefix, self._truncate(serialised)))
            return results

        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix} > {key}"
                results.extend(self._traverse(value, depth + 1, path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                path = f"{prefix} > [{i}]"
                results.extend(self._traverse(item, depth + 1, path))
        else:
            # Leaf value.
            text = self._leaf_to_text(obj)
            results.append((prefix, text))

        return results

    def _leaf_to_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        text = str(value)
        return self._truncate(text)

    def _truncate(self, text: str) -> str:
        if len(text) <= self.max_value_length:
            return text
        return text[: max(0, self.max_value_length - 1)] + "…"

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "JsonSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "path_key"):
            self.path_key = doc_processor_configer.path_key
        if hasattr(doc_processor_configer, "max_depth"):
            self.max_depth = doc_processor_configer.max_depth
        if hasattr(doc_processor_configer, "max_value_length"):
            self.max_value_length = doc_processor_configer.max_value_length
        if hasattr(doc_processor_configer, "drop_empty"):
            self.drop_empty = doc_processor_configer.drop_empty
        return self
