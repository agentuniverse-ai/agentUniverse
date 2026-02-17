# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/26 18:11
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: markdown_reader.py
import re
from typing import Union
from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class MarkdownReader(Reader):
    """Markdown reader that parses markdown files into plain text documents."""

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the markdown file into a Document.

        Reads the raw markdown content and strips common markup to produce
        clean plain text suitable for downstream processing.

        Args:
            file: Path to the markdown file.
            ext_info: Optional extra metadata to attach to the document.

        Returns:
            A single-element list containing the parsed Document.
        """
        if isinstance(file, str):
            file = Path(file)

        text = file.read_text(encoding='utf-8')

        # Strip common markdown syntax to produce plain text
        text = self._strip_markdown(text)

        metadata = {"file_name": file.name}
        if ext_info is not None:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove common markdown formatting to produce plain text."""
        # Remove code blocks (``` ... ```)
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code (` ... `)
        text = re.sub(r'`([^`]*)`', r'\1', text)
        # Remove images ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
        # Remove links [text](url) → text
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        # Remove heading markers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic markers
        text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
        text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        # Remove blockquote markers
        text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Collapse multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
