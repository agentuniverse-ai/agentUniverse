# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/26 18:11
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: markdown_reader.py
from typing import Union
from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding
from agentuniverse.agent.action.knowledge.store.document import Document


class MarkdownReader(Reader):
    """Markdown reader.

    Note:
        The markdown file cannot be process in pagination.

        Markdown is parsed with `unstructured` when it is installed. That
        package is optional and is not a declared dependency, so the reader
        falls back to returning the file's text unchanged -- the same content
        the archive readers emit for a `.md` entry. Install `unstructured` and
        `markdown` (`pip install unstructured markdown`) to get parsed output.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the markdown file.

        Args:
            file: Path to the markdown file.
            ext_info: Metadata merged into the returned document.

        Returns:
            A single document holding the markdown content.
        """
        if isinstance(file, str):
            file = Path(file)

        metadata = {"file_name": file.name}
        if ext_info is not None:
            metadata.update(ext_info)

        parsed = self._load_with_unstructured(file)
        if parsed is not None:
            return [Document(text=parsed, metadata=metadata)]

        return [Document(text=self._read_text(file), metadata=metadata)]

    def _load_with_unstructured(self, file: Path) -> Optional[str]:
        """Return the parsed text, or ``None`` when the optional parser is missing.

        `UnstructuredMarkdownLoader` imports `unstructured` lazily, so the
        ImportError surfaces from the constructor as well as from `load()`.
        """
        try:
            from langchain_community.document_loaders import UnstructuredMarkdownLoader

            documents = UnstructuredMarkdownLoader(file).load()
        except ImportError:
            return None
        return documents[0].page_content

    def _read_text(self, file: Path) -> str:
        """Read the file as text, matching the other plain-text readers."""
        with open(file, "r", encoding=detect_file_encoding(file)) as reader:
            return reader.read()
