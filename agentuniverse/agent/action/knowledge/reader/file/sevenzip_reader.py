import importlib.util
import os
import shutil
import tempfile
import threading
import uuid
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Dict, List, NoReturn, Optional, Type, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _raise_reader_error(
    error_type: type[Exception],
    message: str,
    cause: Exception | None = None,
) -> NoReturn:
    """Raise a reader error while preserving an optional exception cause."""
    if cause is None:
        raise error_type(message)
    raise error_type(message) from cause


class _ExtractionBudget:
    """Shared limits for one root archive and all of its nested archives."""

    def __init__(self, max_file_size: int, max_total_size: int, max_files: int):
        self.max_file_size = max_file_size
        self.max_total_size = max_total_size
        self.max_files = max_files
        self.file_count = 0
        self.reserved_bytes = 0
        self.written_bytes = 0
        self.lock = threading.Lock()

    def claim(self, size: int) -> bool:
        """Reserve a declared member size, returning False when a limit is full."""
        if size < 0 or size > self.max_file_size:
            return False
        with self.lock:
            if self.file_count >= self.max_files:
                return False
            if self.reserved_bytes + size > self.max_total_size:
                return False
            self.file_count += 1
            self.reserved_bytes += size
        return True

    def reserve_write(self, size: int) -> None:
        """Enforce the total limit against bytes actually produced by py7zr."""
        with self.lock:
            if self.written_bytes + size > self.max_total_size:
                _raise_reader_error(ValueError, "7Z archive exceeds maximum total size")
            self.written_bytes += size


class _BoundedFileIO:
    """py7zr-compatible writer backed by a short, generated temporary path."""

    def __init__(
        self,
        temp_dir: Path,
        suffix: str,
        expected_size: int,
        budget: _ExtractionBudget,
    ):
        self.path = temp_dir / f"{uuid.uuid4().hex}{suffix}"
        self._file = self.path.open("w+b")
        self._expected_size = expected_size
        self._budget = budget
        self._written = 0
        self._closed = False

    def write(self, data: Union[bytes, bytearray]) -> int:
        size = len(data)
        if self._written + size > self._expected_size:
            _raise_reader_error(ValueError, "7Z member produced more data than declared")
        if self._written + size > self._budget.max_file_size:
            _raise_reader_error(ValueError, "7Z entry exceeds maximum size")
        self._budget.reserve_write(size)
        written = self._file.write(data)
        self._written += written
        return written

    def read(self, size: Optional[int] = None) -> bytes:
        return self._file.read(-1 if size is None else size)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._file.seek(offset, whence)

    def flush(self) -> None:
        self._file.flush()

    def size(self) -> int:
        return self._written

    def close(self) -> None:
        if not self._closed:
            try:
                # File.close() flushes and releases the handle even if flushing
                # fails. A separate flush here could prevent closing entirely.
                self._file.close()
            finally:
                self._closed = self._file.closed


class _BoundedWriterFactory:
    """Map validated archive names to bounded, generated temporary files."""

    def __init__(
        self,
        temp_dir: Path,
        selected_sizes: Dict[str, int],
        budget: _ExtractionBudget,
    ):
        self.temp_dir = temp_dir.resolve()
        self.selected_sizes = selected_sizes
        self.budget = budget
        self.products: Dict[str, _BoundedFileIO] = {}
        self.lock = threading.Lock()

    def create(self, filename: str) -> _BoundedFileIO:
        try:
            relative = Path(filename).resolve().relative_to(self.temp_dir)
        except ValueError as exc:
            _raise_reader_error(ValueError, "7Z extraction target escaped the temporary root", exc)
        member_name = PurePosixPath(relative.as_posix()).as_posix()
        if member_name not in self.selected_sizes:
            _raise_reader_error(ValueError, f"Unexpected 7Z extraction target: {member_name}")
        suffix = PurePosixPath(member_name).suffix.lower()
        writer = _BoundedFileIO(
            self.temp_dir,
            suffix,
            self.selected_sizes[member_name],
            self.budget,
        )
        with self.lock:
            if member_name in self.products:
                writer.close()
                _raise_reader_error(ValueError, f"Duplicate 7Z member name: {member_name}")
            self.products[member_name] = writer
        return writer

    def close(self) -> None:
        """Attempt every close, even when one member reports an I/O error."""
        first_error = None
        for writer in self.products.values():
            try:
                writer.close()
            except OSError as exc:
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error


class SevenZipReader(Reader):
    """
    7Z (.7z) archive reader.

    Supports reading various file formats from 7Z archives with security limits,
    nested 7Z handling, and automatic format detection.
    """

    def __init__(self):
        # 调用父类构造函数
        super().__init__()
        # 初始化读取器缓存，避免重复创建相同类型的读取器
        self._reader_cache: Dict[str, Type[Reader]] = {}

    def _load_data(
        self,
        file: Union[str, Path],
        max_file_size: int = 64 * 1024 * 1024,  # 默认64MB单文件限制
        max_total_size: int = 512 * 1024 * 1024,  # 默认512MB总大小限制
        max_files: int = 4096,  # 默认最多处理4096个文件
        max_depth: int = 5,  # 默认最大嵌套深度5层
        max_compression_ratio: float = 1000.0,  # 默认最大压缩比1000:1（防压缩炸弹）
        ext_info: Optional[Dict] = None,  # 额外的元数据信息
    ) -> List[Document]:
        """Parse 7Z archive file.
        Args:
            file: 7Z文件路径
            max_file_size: 单个文件最大大小（字节）
            max_total_size: 提取文件总大小限制（字节）
            max_files: 最大处理文件数
            max_depth: 7Z文件最大嵌套深度
            max_compression_ratio: 压缩炸弹检测的最大压缩比
            ext_info: 额外元数据
        Returns:
            List[Document]: 从7Z档案中提取的文档列表
        Note:
            需要py7zr库来读取7Z文件：`pip install py7zr`
        """
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            _raise_reader_error(TypeError, "file must be path-like")
        if not file.exists():
            _raise_reader_error(FileNotFoundError, f"7Z file not found: {file}")
        for name, value in {
            "max_file_size": max_file_size,
            "max_total_size": max_total_size,
            "max_files": max_files,
        }.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                _raise_reader_error(ValueError, f"{name} must be a positive integer")
        if isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0:
            _raise_reader_error(ValueError, "max_depth must be a non-negative integer")
        if (
            isinstance(max_compression_ratio, bool)
            or not isinstance(max_compression_ratio, int | float)
            or max_compression_ratio <= 0
        ):
            _raise_reader_error(ValueError, "max_compression_ratio must be positive")

        if importlib.util.find_spec("py7zr") is None:
            _raise_reader_error(ImportError, 'py7zr is required to read 7Z files: `pip install "py7zr>=1.1.3"`')

        temp_dir = tempfile.mkdtemp(prefix="7z_reader_")
        try:
            budget = _ExtractionBudget(
                max_file_size=max_file_size,
                max_total_size=max_total_size,
                max_files=max_files,
            )
            documents = self._process_7z(
                sevenzip_path=file,
                temp_dir=temp_dir,
                current_depth=0,
                max_depth=max_depth,
                max_compression_ratio=max_compression_ratio,
                base_metadata=ext_info or {},
                archive_root=file.name,
                budget=budget,
            )
            return documents
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _process_7z(
        self,
        sevenzip_path: Path,
        temp_dir: str,
        current_depth: int,
        max_depth: int,
        max_compression_ratio: float,
        base_metadata: Dict,
        archive_root: str,
        budget: _ExtractionBudget,
        parent_path: str = "",
    ) -> List[Document]:
        """Process a 7Z archive without writing archive-controlled paths."""
        import py7zr

        documents: List[Document] = []
        try:
            try:
                archive_context = py7zr.SevenZipFile(
                    str(sevenzip_path),
                    "r",
                    max_extract_size=budget.max_total_size,
                )
            except TypeError as exc:
                _raise_reader_error(ImportError, "SevenZipReader requires py7zr>=1.1.3 for bounded extraction", exc)

            with archive_context as archive:
                selected_sizes: Dict[str, int] = {}
                for file_info in archive.list():
                    if getattr(file_info, "is_directory", False):
                        continue
                    entry_name = self._normalize_entry_name(file_info.filename)
                    if entry_name is None:
                        continue

                    uncompressed_size = getattr(file_info, "uncompressed", None)
                    if not isinstance(uncompressed_size, int):
                        continue
                    compressed_size = getattr(file_info, "compressed", None)
                    if isinstance(compressed_size, int) and compressed_size > 0:
                        ratio = uncompressed_size / compressed_size
                        if ratio > max_compression_ratio:
                            _raise_reader_error(
                                ValueError,
                                f"7Z entry has suspicious compression ratio: {entry_name}",
                            )

                    suffix = PurePosixPath(entry_name).suffix.lower()
                    if suffix != ".7z" and self._get_reader_class(suffix) is None:
                        continue
                    if suffix == ".7z" and current_depth >= max_depth:
                        _raise_reader_error(ValueError, "7Z nesting depth exceeded")
                    if entry_name in selected_sizes:
                        continue
                    if uncompressed_size < 0 or uncompressed_size > budget.max_file_size:
                        continue
                    if not budget.claim(uncompressed_size):
                        break
                    selected_sizes[entry_name] = uncompressed_size

                if not selected_sizes:
                    return []
                factory = _BoundedWriterFactory(Path(temp_dir), selected_sizes, budget)
                try:
                    archive.extract(
                        path=Path(temp_dir),
                        targets=list(selected_sizes),
                        factory=factory,
                    )
                except BaseException:
                    # py7zr does not close custom writers after failed extraction.
                    # Release handles before the outer temporary-directory cleanup.
                    try:
                        factory.close()
                    except OSError:
                        pass  # Keep the original extraction error after cleanup.
                    raise
                else:
                    factory.close()

            for entry_name in selected_sizes:
                writer = factory.products.get(entry_name)
                if writer is None or not writer.path.exists():
                    continue
                full_path = f"{parent_path}/{entry_name}" if parent_path else entry_name
                if PurePosixPath(entry_name).suffix.lower() == ".7z":
                    documents.extend(
                        self._process_7z(
                            sevenzip_path=writer.path,
                            temp_dir=temp_dir,
                            current_depth=current_depth + 1,
                            max_depth=max_depth,
                            max_compression_ratio=max_compression_ratio,
                            base_metadata=base_metadata,
                            archive_root=archive_root,
                            budget=budget,
                            parent_path=full_path,
                        )
                    )
                else:
                    documents.extend(
                        self._process_file(
                            file_path=writer.path,
                            archive_path=full_path,
                            archive_root=archive_root,
                            archive_depth=current_depth,
                            base_metadata=base_metadata,
                            original_name=PurePosixPath(entry_name).name,
                        )
                    )

        except (py7zr.Bad7zFile, py7zr.exceptions.Bad7zFile) as exc:
            _raise_reader_error(ValueError, f"Failed to read 7Z file: {exc!s}", exc)

        return documents

    @staticmethod
    def _normalize_entry_name(entry_name: str) -> Optional[str]:
        """Return a portable relative member path, or None when it is unsafe."""
        if not entry_name or "\x00" in entry_name:
            return None
        posix_path = PurePosixPath(entry_name.replace("\\", "/"))
        windows_path = PureWindowsPath(entry_name)
        if posix_path.is_absolute() or windows_path.is_absolute():
            return None
        if windows_path.drive or windows_path.root:
            return None
        if ".." in posix_path.parts or ".." in windows_path.parts:
            return None
        parts = [part for part in posix_path.parts if part not in {"", "."}]
        if not parts or any(":" in part for part in parts):
            return None
        return PurePosixPath(*parts).as_posix()

    def _process_file(
        self,
        file_path: Path,
        archive_path: str,
        archive_root: str,
        archive_depth: int,
        base_metadata: Dict,
        original_name: Optional[str] = None,
    ) -> List[Document]:
        """处理归档中的单个文件"""
        # 检查文件是否存在且为普通文件
        if not file_path.exists() or not file_path.is_file():
            return []

        # 根据文件扩展名获取对应的读取器
        reader = self._get_reader_for_file(file_path)

        if not reader:
            return []

        try:
            # 构建文件元数据
            display_name = original_name or file_path.name
            metadata = {
                "file_name": display_name,
                "file_path": f"{archive_root}::{archive_path}",  # 格式：根文件::内部路径
                "file_suffix": PurePosixPath(display_name).suffix.lower(),
                "archive_root": archive_root,
                "archive_path": archive_path,
                "archive_depth": archive_depth,
            }
            # 合并基础元数据
            metadata.update(base_metadata)

            # 使用对应的读取器加载文件数据
            documents = reader.load_data(file_path, ext_info=metadata)
            return documents

        except Exception:
            # 处理失败时返回空列表
            return []

    def _get_reader_for_file(self, file_path: Path) -> Optional[Reader]:
        """根据文件扩展名获取合适的读取器"""
        suffix = file_path.suffix.lower()

        # 首先检查缓存
        if suffix in self._reader_cache:
            reader_class = self._reader_cache[suffix]
            return reader_class()

        # 如果缓存中没有，获取读取器类
        reader_class = self._get_reader_class(suffix)
        if reader_class:
            # 缓存读取器类供后续使用
            self._reader_cache[suffix] = reader_class
            return reader_class()

        return None

    def _get_reader_class(self, suffix: str) -> Optional[Type[Reader]]:
        """将文件扩展名映射到读取器类"""
        # 定义文件扩展名到读取器名称的映射
        reader_map = {
            ".pdf": "PdfReader",
            ".docx": "DocxReader",
            ".pptx": "PptxReader",
            ".xlsx": "XlsxReader",
            ".epub": "EpubReader",
            ".txt": "TxtReader",
            # Markdown is plain text inside an archive; using TxtReader keeps
            # archive ingestion deterministic and avoids an optional NLP stack.
            ".md": "TxtReader",
            ".csv": "CSVReader",
            ".conf": "TxtReader",  # 配置文件按文本处理
            ".log": "TxtReader",  # 日志文件按文本处理
            ".ini": "TxtReader",  # ini文件按文本处理
            ".cfg": "TxtReader",  # cfg文件按文本处理
            # 各种编程语言文件使用代码读取器
            ".py": "CodeReader",
            ".js": "CodeReader",
            ".ts": "CodeReader",
            ".java": "CodeReader",
            ".cpp": "CodeReader",
            ".c": "CodeReader",
            ".h": "CodeReader",
            ".hpp": "CodeReader",
            ".cs": "CodeReader",
            ".go": "CodeReader",
            ".rb": "CodeReader",
            ".php": "CodeReader",
            ".swift": "CodeReader",
            ".kt": "CodeReader",
            ".rs": "CodeReader",
            ".sh": "CodeReader",
            ".html": "CodeReader",
            ".css": "CodeReader",
            ".sql": "CodeReader",
            # 数据格式文件
            ".json": "CodeReader",
            ".xml": "CodeReader",
            ".yaml": "CodeReader",
            ".yml": "CodeReader",
            # 7Z特定格式
            ".7z": "SevenZipReader",  # 支持嵌套7Z文件
        }

        # 获取对应的读取器名称
        reader_name = reader_map.get(suffix)
        if not reader_name:
            return None

        try:
            # 动态导入对应的读取器类
            if reader_name == "PdfReader":
                from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader

                return PdfReader
            elif reader_name == "DocxReader":
                from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader

                return DocxReader
            elif reader_name == "PptxReader":
                from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader

                return PptxReader
            elif reader_name == "XlsxReader":
                from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader

                return XlsxReader
            elif reader_name == "EpubReader":
                from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader

                return EpubReader
            elif reader_name == "TxtReader":
                from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader

                return TxtReader
            elif reader_name == "MarkdownReader":
                from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader

                return MarkdownReader
            elif reader_name == "CSVReader":
                from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader

                return CSVReader
            elif reader_name == "CodeReader":
                from agentuniverse.agent.action.knowledge.reader.file.code_reader import CodeReader

                return CodeReader
            elif reader_name == "SevenZipReader":
                # 返回自身类型以支持嵌套7Z文件
                return SevenZipReader
            else:
                return None
        except ImportError:
            # 如果导入失败，返回None
            return None
