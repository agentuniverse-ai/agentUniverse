# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/30 16:30
# @Author  : mutianyu
# @Email   : 3417633465@qq.com
# @FileName: web_html_reader.py

from typing import Union, List, Optional, Dict
from pathlib import Path

from bs4 import BeautifulSoup
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class HtmlReader(Reader):
    """HTML reader."""

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the HTML file.

        Note:
            BeautifulSoup is required to parse HTML files: `pip install beautifulsoup4`
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(
                "BeautifulSoup is required to parse HTML files: "
                "`pip install beautifulsoup4`"
            )

        if isinstance(file, str):
            file = Path(file)

        # Load and parse the HTML file
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # Extract main content (e.g., text within <body>)
        text = soup.get_text(separator="\n").strip()
        metadata = {"file_name": file.name}
        if ext_info is not None:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata or {})]