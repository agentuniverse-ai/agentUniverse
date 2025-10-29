# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/30 23:23
# @Author  : SaladDay
# @FileName: rar_reader.py

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Union, Optional, Dict, Type, Set

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class RarReader(Reader):
    """
    RAR (.rar) archive reader.
    
    Supports reading various file formats from RAR archives with security limits,
    nested RAR handling, and automatic format detection.
    """

    def __init__(self):
        super().__init__()
        self._reader_cache: Dict[str, Type[Reader]] = {}

    def _load_data(
        self,
        file: Union[str, Path],
        max_file_size: int = 64 * 1024 * 1024,
        max_total_size: int = 512 * 1024 * 1024,
        max_files: int = 4096,
        max_depth: int = 5,
        max_compression_ratio: float = 1000.0,
        ext_info: Optional[Dict] = None,
    ) -> List[Document]:
        """Parse RAR archive file.

        Args:
            file: RAR file path
            max_file_size: Maximum size per extracted file (bytes)
            max_total_size: Maximum total extracted size (bytes)
            max_files: Maximum number of files to process
            max_depth: Maximum nesting depth for RAR archives
            max_compression_ratio: Maximum compression ratio for bomb detection
            ext_info: Additional metadata

        Returns:
            List[Document]: Documents extracted from RAR archive

        Note:
            `rarfile` is required to read RAR files: `pip install rarfile`
            External unrar tool is also required
        """
        try:
            import rarfile
            import os
            user_unrar = os.path.expanduser('~/library/bin/unrar')
            if os.path.exists(user_unrar):
                rarfile.UNRAR_TOOL = user_unrar
        except ImportError:
            raise ImportError(
                "rarfile is required to read RAR files: "
                "`pip install rarfile`"
            )

        if isinstance(file, str):
            file = Path(file)

        if not file.exists():
            raise FileNotFoundError(f"RAR file not found: {file}")

        temp_dir = tempfile.mkdtemp(prefix="rar_reader_")
        try:
            documents = self._process_rar(
                rar_path=file,
                temp_dir=temp_dir,
                current_depth=0,
                max_depth=max_depth,
                max_file_size=max_file_size,
                max_total_size=max_total_size,
                max_files=max_files,
                max_compression_ratio=max_compression_ratio,
                base_metadata=ext_info or {},
                archive_root=file.name,
            )
            return documents
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _process_rar(
        self,
        rar_path: Path,
        temp_dir: str,
        current_depth: int,
        max_depth: int,
        max_file_size: int,
        max_total_size: int,
        max_files: int,
        max_compression_ratio: float,
        base_metadata: Dict,
        archive_root: str,
        parent_path: str = "",
    ) -> List[Document]:
        """Process a RAR archive recursively."""
        import rarfile

        documents = []
        total_extracted = 0
        file_count = 0

        try:
            with rarfile.RarFile(str(rar_path), 'r') as rar:
                entries = rar.infolist()

                for entry in entries:
                    if file_count >= max_files:
                        break

                    if entry.is_dir():
                        continue

                    if '..' in entry.filename or entry.filename.startswith('/'):
                        continue

                    compressed_size = entry.compress_size
                    uncompressed_size = entry.file_size

                    if compressed_size > 0:
                        ratio = uncompressed_size / compressed_size
                        if ratio > max_compression_ratio:
                            raise ValueError(
                                f"Rar entry has suspicious compression ratio: {entry.filename}"
                            )

                    if uncompressed_size > max_file_size:
                        continue

                    if total_extracted + uncompressed_size > max_total_size:
                        break

                    extract_dir = os.path.join(temp_dir, f"extract_{file_count}")
                    os.makedirs(extract_dir, exist_ok=True)

                    try:
                        rar.extract(entry, extract_dir)
                        extracted_path = Path(extract_dir) / entry.filename
                        total_extracted += uncompressed_size
                        file_count += 1

                        full_path = os.path.join(parent_path, entry.filename) if parent_path else entry.filename

                        if extracted_path.suffix.lower() == '.rar' and current_depth < max_depth:
                            nested_docs = self._process_rar(
                                rar_path=extracted_path,
                                temp_dir=temp_dir,
                                current_depth=current_depth + 1,
                                max_depth=max_depth,
                                max_file_size=max_file_size,
                                max_total_size=max_total_size - total_extracted,
                                max_files=max_files - file_count,
                                max_compression_ratio=max_compression_ratio,
                                base_metadata=base_metadata,
                                archive_root=archive_root,
                                parent_path=full_path,
                            )
                            documents.extend(nested_docs)
                        else:
                            doc = self._process_file(
                                file_path=extracted_path,
                                archive_path=full_path,
                                archive_root=archive_root,
                                archive_depth=current_depth,
                                base_metadata=base_metadata,
                            )
                            if doc:
                                documents.extend(doc)

                    except Exception as e:
                        continue

        except rarfile.Error as e:
            raise ValueError(f"Failed to read RAR file: {str(e)}")

        return documents

    def _process_file(
        self,
        file_path: Path,
        archive_path: str,
        archive_root: str,
        archive_depth: int,
        base_metadata: Dict,
    ) -> List[Document]:
        """Process individual file from archive."""
        if not file_path.exists() or not file_path.is_file():
            return []

        reader = self._get_reader_for_file(file_path)
        if not reader:
            return []

        try:
            metadata = {
                "file_name": file_path.name,
                "file_path": f"{archive_root}::{archive_path}",
                "file_suffix": file_path.suffix.lower(),
                "archive_root": archive_root,
                "archive_path": archive_path,
                "archive_depth": archive_depth,
            }
            metadata.update(base_metadata)

            documents = reader.load_data(file_path, ext_info=metadata)
            return documents

        except Exception as e:
            return []

    def _get_reader_for_file(self, file_path: Path) -> Optional[Reader]:
        """Get appropriate reader for file based on extension."""
        suffix = file_path.suffix.lower()

        if suffix in self._reader_cache:
            reader_class = self._reader_cache[suffix]
            return reader_class()

        reader_class = self._get_reader_class(suffix)
        if reader_class:
            self._reader_cache[suffix] = reader_class
            return reader_class()

        return None

    def _get_reader_class(self, suffix: str) -> Optional[Type[Reader]]:
        """Map file extension to reader class."""
        reader_map = {
            '.pdf': 'PdfReader',
            '.docx': 'DocxReader',
            '.pptx': 'PptxReader',
            '.xlsx': 'XlsxReader',
            '.epub': 'EpubReader',
            '.txt': 'TxtReader',
            '.md': 'MarkdownReader',
            '.csv': 'CSVReader',
            '.conf': 'TxtReader',
            '.log': 'TxtReader',
            '.ini': 'TxtReader',
            '.cfg': 'TxtReader',
            '.py': 'CodeReader',
            '.js': 'CodeReader',
            '.ts': 'CodeReader',
            '.java': 'CodeReader',
            '.cpp': 'CodeReader',
            '.c': 'CodeReader',
            '.h': 'CodeReader',
            '.hpp': 'CodeReader',
            '.cs': 'CodeReader',
            '.go': 'CodeReader',
            '.rb': 'CodeReader',
            '.php': 'CodeReader',
            '.swift': 'CodeReader',
            '.kt': 'CodeReader',
            '.rs': 'CodeReader',
            '.sh': 'CodeReader',
            '.html': 'CodeReader',
            '.css': 'CodeReader',
            '.sql': 'CodeReader',
            '.json': 'CodeReader',
            '.xml': 'CodeReader',
            '.yaml': 'CodeReader',
            '.yml': 'CodeReader',
        }

        reader_name = reader_map.get(suffix)
        if not reader_name:
            return None

        try:
            if reader_name == 'PdfReader':
                from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
                return PdfReader
            elif reader_name == 'DocxReader':
                from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader
                return DocxReader
            elif reader_name == 'PptxReader':
                from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader
                return PptxReader
            elif reader_name == 'XlsxReader':
                from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader
                return XlsxReader
            elif reader_name == 'EpubReader':
                from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader
                return EpubReader
            elif reader_name == 'TxtReader':
                from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
                return TxtReader
            elif reader_name == 'MarkdownReader':
                from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader
                return MarkdownReader
            elif reader_name == 'CSVReader':
                from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
                return CSVReader
            elif reader_name == 'CodeReader':
                from agentuniverse.agent.action.knowledge.reader.file.code_reader import CodeReader
                return CodeReader
            else:
                return None
        except ImportError:
            return None
