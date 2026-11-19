"""Split supported Markdown pipe tables without detaching rows from headers."""

import json
import re
import uuid
from typing import List

from pydantic import StrictInt

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


def _cells(line):
    """Split unescaped pipes, retaining raw cells; require two or more columns."""
    text = line.rstrip("\r\n")
    if len(text) - len(text.lstrip(" ")) > 3 or text.startswith("\t"):
        return None
    parts, start, slashes = [], 0, 0
    for i, char in enumerate(text):
        if char == "|" and slashes % 2 == 0:
            parts.append(text[start:i])
            start = i + 1
        slashes = slashes + 1 if char == "\\" else 0
    if not parts:
        return None
    parts.append(text[start:])
    if not parts[0].strip():
        parts.pop(0)
    if parts and not parts[-1].strip():
        parts.pop()
    return parts if len(parts) >= 2 else None


class TableHeaderSplitter(DocProcessor):
    """Fragment pipe tables into row groups with repeated original headers.

    max_chars is a soft character budget for table chunks, including repeated
    heading/header context. An indivisible row may exceed it and is marked.
    Non-table prose is preserved, not budget-split. Unsupported/ragged tables
    remain verbatim. This is not a complete Markdown parser.
    """

    max_chars: StrictInt = 2000

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_options()

    def _validate_options(self):
        if type(self.max_chars) is not int or self.max_chars <= 0:
            raise ValueError("max_chars must be a positive integer")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Return source-addressed chunks, clearing obsolete vectors/keywords.

        The reserved metadata key ``table_chunk`` must not already exist on
        documents that contain a recognized table. Inputs are never mutated.
        """
        self._validate_options()
        result = []
        for doc in origin_docs:
            result.extend(self._split_document(doc))
        return result

    def _split_document(self, doc):
        lines = (doc.text or "").splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))
        tables = []
        headings = []
        fence = None
        i = 0
        while i < len(lines):
            raw = lines[i].rstrip("\r\n")
            match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", raw)
            if fence:
                if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                    fence = None
                i += 1
                continue
            if match and (match[1][0] != "`" or "`" not in match[2]):
                fence = (match[1][0], len(match[1]))
                i += 1
                continue
            heading = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+|$)", raw)
            if heading:
                level = len(heading[1])
                headings = [(depth, line) for depth, line in headings if depth < level]
                headings.append((level, lines[i]))
            header = _cells(lines[i])
            separator = _cells(lines[i + 1]) if i + 1 < len(lines) else None
            if (not header or not separator or len(header) != len(separator) or
                    not all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in separator)):
                i += 1
                continue
            end = i + 2
            valid = True
            while end < len(lines):
                cells = _cells(lines[end])
                if cells is None:
                    break
                valid = valid and len(cells) == len(header)
                end += 1
            if valid:
                # Preserve the nearest plain paragraph too: units/captions
                # often live immediately above a table, outside its header.
                context = "".join(line for _, line in headings)
                previous = i
                while previous > 0 and not lines[previous - 1].strip():
                    previous -= 1
                begin = previous
                while begin > 0:
                    candidate = lines[begin - 1]
                    if (not candidate.strip() or _cells(candidate) or
                            re.match(r"^ {0,3}(?:#{1,6}(?:\s|$)|`{3,}|~{3,})", candidate) or
                            candidate.startswith(("    ", "\t"))):
                        break
                    begin -= 1
                preceding = "".join(lines[begin:previous])
                tables.append((i, end, context, preceding))
            i = end
        if not tables:
            return [doc]
        if "table_chunk" in (doc.metadata or {}):
            raise ValueError("table_chunk metadata is reserved; do not split the same chunks twice")

        source = (doc.metadata or {}).get("source", (doc.metadata or {}).get("file_name", ""))
        if not isinstance(source, str):
            raise ValueError("source/file_name metadata must be a string for stable chunk identity")
        chunks = []

        def emit(text, info):
            identity = json.dumps([doc.id, source, info], sort_keys=True, ensure_ascii=False)
            metadata = dict(doc.metadata or {})
            metadata["table_chunk"] = dict(info, source_document_id=doc.id)
            chunks.append(doc.model_copy(update={
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, identity)), "text": text,
                "metadata": metadata, "embedding": [], "keywords": set(),
            }))

        cursor = 0
        for start, end, context, preceding in tables:
            if cursor < start:
                emit("".join(lines[cursor:start]), {"kind": "prose", "source_start": offsets[cursor], "source_end": offsets[start]})
            header_text = "".join(lines[start:start + 2])
            prefix = context + preceding + header_text
            table_id = str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps([doc.id, source, offsets[start]])))
            row = start + 2
            groups = []
            if row == end:
                groups.append((row, row))
            while row < end:
                stop, length = row, len(prefix)
                while stop < end:
                    if stop > row and length + len(lines[stop]) > self.max_chars:
                        break
                    length += len(lines[stop])
                    stop += 1
                groups.append((row, stop))
                row = stop
            for first, stop in groups:
                text = prefix + "".join(lines[first:stop])
                emit(text, {"kind": "table", "table_id": table_id,
                            "table_start": offsets[start], "table_end": offsets[end],
                            "source_start": offsets[first], "source_end": offsets[stop],
                            "row_start": first - start - 2, "row_end": stop - start - 2,
                            "header_text": header_text, "heading_context": context,
                            "preceding_context": preceding,
                            "over_budget": len(text) > self.max_chars})
            cursor = end
        if cursor < len(lines):
            emit("".join(lines[cursor:]), {"kind": "prose", "source_start": offsets[cursor], "source_end": offsets[-1]})
        return chunks

    def _initialize_by_component_configer(self, config: ComponentConfiger) -> 'TableHeaderSplitter':
        validated = TableHeaderSplitter(max_chars=getattr(config, "max_chars", self.max_chars))
        super()._initialize_by_component_configer(config)
        self.max_chars = validated.max_chars
        return self
