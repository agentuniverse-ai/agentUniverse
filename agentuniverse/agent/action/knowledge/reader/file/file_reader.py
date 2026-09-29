# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 14:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: file_reader.py
from pathlib import Path
from typing import Dict, Type, List, Optional

from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader
from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader
from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.rar_reader import RarReader
from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader
from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader
from agentuniverse.agent.action.knowledge.reader.file.sevenzip_reader import SevenZipReader
from agentuniverse.agent.action.knowledge.reader.file.tar_reader import TarReader
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

DEFAULT_FILE_READERS: Dict[str, Type[Reader]] = {
    ".pdf": PdfReader,
    ".docx": DocxReader,
    ".pptx": PptxReader,
    ".xlsx": XlsxReader,
    ".epub": EpubReader,
    ".txt": TxtReader,
    ".md": MarkdownReader,
    ".markdown": MarkdownReader,
    ".csv": CSVReader,
    ".rar": RarReader,
    ".zip": ZipReader,
    ".7z": SevenZipReader,
    ".tar": TarReader,
    ".tgz": TarReader,
    ".tar.gz": TarReader,
    ".tar.bz2": TarReader,
    ".tar.xz": TarReader,
}


class FileReader(Reader):
    """The agentUniverse(aU) file reader class.

    FileReader is used to load data from files based on the provided file paths.

    Attributes:
        file_readers (Dict[str, Type[Reader]], optional): The file reader dictionary,
        the key is the suffix of the file, and the value is the specific file reader class.
    """

    file_readers: Dict[str, Type[Reader]] = DEFAULT_FILE_READERS

    def _load_data(self, file_paths: List[Path], ext_info: Optional[Dict] = None) -> List[Document]:
        document_list = []
        for file_path in file_paths:
            file_suffix = self._resolve_suffix(file_path)
            if file_suffix in self.file_readers.keys():
                file_reader = self.file_readers[file_suffix]()
                document_list.extend(file_reader.load_data(file=file_path, ext_info=ext_info))
        return document_list

    def _resolve_suffix(self, file_path: Path) -> str:
        """Resolve the reader key for a file, honouring compound archive suffixes.

        ``Path.suffix`` only returns the final component, so ``bundle.tar.gz``
        would otherwise resolve to ``.gz`` and silently match no reader. A
        registered compound suffix (``.tar.gz``) takes priority; every other
        file keeps the previous single-extension behaviour.
        """
        suffixes = file_path.suffixes
        if len(suffixes) >= 2:
            compound = "".join(suffixes[-2:]).lower()
            if compound in self.file_readers:
                return compound
        return file_path.suffix.lower()
