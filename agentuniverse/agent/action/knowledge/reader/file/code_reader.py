# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 13:19
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: code_reader.py
import os
from pathlib import Path
from typing import List, Union, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


CODE_FILE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.rs': 'rust',
    '.sh': 'shell',
    '.html': 'html',
    '.css': 'css',
    '.sql': 'sql',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
}


class CodeReader(Reader):

    def _load_data(self,
                   file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if not file.exists():
                raise FileNotFoundError(f"Code file not found: {file}")
        file_content = file.read_text(encoding="utf-8")
        file_name = file.name
        file_suffix = file.suffix.lower()
        language = CODE_FILE_EXTENSIONS.get(file_suffix, 'unknown')
        metadata = {
            "file_name": file_name,
            "file_path": str(file),
            "language": language,
            "file_suffix": file_suffix,
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=file_content, metadata=metadata)]
