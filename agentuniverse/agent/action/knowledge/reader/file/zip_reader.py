# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/28 21:21
# @Author  : Saladday
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: zip_reader.py
import io
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Union, Type

from agentuniverse.agent.action.knowledge.reader.file.code_reader import CODE_FILE_EXTENSIONS, CodeReader
from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader
from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader
from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

TEXT_FALLBACK_EXTENSIONS = {
    ".json",
    ".yml",
    ".yaml",
    ".xml",
    ".html",
    ".htm",
    ".ini",
    ".cfg",
    ".conf",
    ".log",
    ".rst",
}


class ZipReader(Reader):
    max_total_size: int = 512 * 1024 * 1024
    max_file_size: int = 64 * 1024 * 1024
    max_depth: int = 5
    max_files: int = 4096
    max_compression_ratio: int = 100
    stream_chunk_size: int = 1024 * 1024
        
    def _get_reader(self, suffix: str) -> Reader:
        if suffix not in self._readers:
            if suffix in CODE_FILE_EXTENSIONS:
                self._readers[suffix] = CodeReader()
            elif suffix in self._reader_classes:
                self._readers[suffix] = self._reader_classes[suffix]()
        return self._readers.get(suffix)

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError("file must be path-like")
        if not file.exists():
            raise FileNotFoundError(f"Zip file not found: {file}")
        
        self._total_size = 0
        self._file_count = 0
        self._readers = {}
        self._reader_classes = {
            ".csv": CSVReader,
            ".txt": TxtReader,
            ".md": MarkdownReader,
            ".pdf": PdfReader,
            ".docx": DocxReader,
            ".pptx": PptxReader,
            ".xlsx": XlsxReader,
            ".epub": EpubReader,
        }
        
        ext_meta = dict(ext_info or {})
        with zipfile.ZipFile(file) as archive:
            with tempfile.TemporaryDirectory() as temp_dir:
                return self._iterate_archive(
                    archive,
                    file,
                    Path(temp_dir),
                    ext_meta,
                    0,
                    [],
                )

    def _iterate_archive(
        self,
        archive: zipfile.ZipFile,
        archive_path: Path,
        temp_dir: Path,
        ext_meta: Dict,
        depth: int,
        path_stack: List[str],
    ) -> List[Document]:
        documents: List[Document] = []
        for info in archive.infolist():
            if info.is_dir():
                continue
            member_path = self._normalize_member(info.filename)
            if member_path is None:
                continue
            self._enforce_limits(info)
            suffix = member_path.suffix.lower()
            current_stack = path_stack + [member_path.as_posix()]
            metadata = self._build_metadata(archive_path, current_stack, depth, ext_meta)
            
            if suffix == ".zip":
                documents.extend(
                    self._handle_nested_zip(
                        archive,
                        info,
                        archive_path,
                        temp_dir,
                        ext_meta,
                        depth,
                        current_stack,
                    )
                )
            elif suffix in TEXT_FALLBACK_EXTENSIONS:
                documents.extend(
                    self._handle_text_fallback(archive, info, metadata)
                )
            elif suffix in CODE_FILE_EXTENSIONS or suffix in self._reader_classes:
                reader = self._get_reader(suffix)
                if reader:
                    documents.extend(
                        self._handle_reader_with_temp(archive, info, temp_dir, metadata, reader)
                    )
        return documents

    def _handle_nested_zip(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        archive_path: Path,
        temp_dir: Path,
        ext_meta: Dict,
        depth: int,
        current_stack: List[str],
    ) -> List[Document]:
        if depth + 1 > self.max_depth:
            raise ValueError("Zip nesting depth exceeded")
        
        data = None
        try:
            with archive.open(info) as raw:
                data = raw.read()
            with zipfile.ZipFile(io.BytesIO(data)) as nested:
                return self._iterate_archive(
                    nested,
                    archive_path,
                    temp_dir,
                    ext_meta,
                    depth + 1,
                    current_stack,
                )
        except zipfile.BadZipFile as exc:
            raise ValueError("Invalid nested zip content") from exc
        finally:
            del data

    def _handle_reader_with_temp(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        temp_dir: Path,
        metadata: Dict,
        reader: Reader,
    ) -> List[Document]:
        file_path = self._write_temp_file(archive, info, temp_dir)
        try:
            docs = reader.load_data(file_path, ext_info=dict(metadata))
            return [self._merge_metadata(doc, metadata) for doc in docs]
        except Exception:
            return []
        finally:
            if file_path.exists():
                file_path.unlink()

    def _handle_text_fallback(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        metadata: Dict,
    ) -> List[Document]:
        with archive.open(info) as raw:
            text = self._read_text(raw)
        if not text:
            return []
        return [Document(text=text, metadata=dict(metadata))]

    def _write_temp_file(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        temp_dir: Path,
    ) -> Path:
        name = PurePosixPath(info.filename).name
        if not name:
            name = uuid.uuid4().hex
        file_path = temp_dir / f"{uuid.uuid4().hex}_{name}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, open(file_path, "wb") as target:
            shutil.copyfileobj(source, target, self.stream_chunk_size)
        return file_path

    def _merge_metadata(self, document: Document, metadata: Dict) -> Document:
        if document.metadata is None:
            document.metadata = {}
        for key in ["file_name", "file_path"]:
            if key in metadata:
                document.metadata[key] = metadata[key]
        document.metadata.update({k: v for k, v in metadata.items() if k not in document.metadata})
        return document

    def _normalize_member(self, member: str) -> Optional[PurePosixPath]:
        if not member:
            return None
        normalized = PurePosixPath(member)
        parts = [part for part in normalized.parts if part not in {"", ".", ".."}]
        if not parts:
            return None
        return PurePosixPath(*parts)

    def _build_metadata(
        self,
        archive_path: Path,
        path_stack: List[str],
        depth: int,
        ext_meta: Dict,
    ) -> Dict:
        metadata = {
            "archive_root": archive_path.name,
            "archive_path": "/".join(path_stack),
            "archive_depth": depth,
            "file_name": PurePosixPath(path_stack[-1]).name if path_stack else archive_path.name,
            "file_path": f"{archive_path.as_posix()}::{ '/'.join(path_stack) if path_stack else '' }".rstrip(":"),
        }
        if ext_meta:
            metadata.update(ext_meta)
        return metadata

    def _read_text(self, stream: io.BufferedReader) -> str:
        text_chunks: List[str] = []
        reader = io.TextIOWrapper(stream, encoding="utf-8", errors="ignore")
        while True:
            chunk = reader.read(self.stream_chunk_size)
            if not chunk:
                break
            text_chunks.append(chunk)
        return "".join(text_chunks)

    def _enforce_limits(self, info: zipfile.ZipInfo) -> None:
        size = info.file_size
        compressed_size = info.compress_size
        
        if size > self.max_file_size:
            raise ValueError(f"Zip entry exceeds maximum size: {info.filename}")
        if self._total_size + size > self.max_total_size:
            raise ValueError("Zip archive exceeds maximum total size")
        if self._file_count + 1 > self.max_files:
            raise ValueError("Zip archive exceeds maximum file count")
        
        if compressed_size > 0:
            compression_ratio = size / compressed_size
            if compression_ratio > self.max_compression_ratio:
                raise ValueError(f"Zip entry has suspicious compression ratio: {info.filename}")
        
        self._total_size += size
        self._file_count += 1
