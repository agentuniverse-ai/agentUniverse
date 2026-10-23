import os
import re
import shutil
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple, Type, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

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
        # 将字符串路径转换为Path对象
        if isinstance(file, str):
            file = Path(file)

        # 检查文件是否存在
        if not file.exists():
            raise FileNotFoundError(f"7Z file not found: {file}")

        # 尝试导入py7zr库
        try:
            import py7zr
        except ImportError:
            # 如果py7zr未安装，抛出导入错误
            raise ImportError(
                "py7zr is required to read 7Z files: "
                "`pip install py7zr`"
            )

        # 创建临时目录用于解压文件
        temp_dir = tempfile.mkdtemp(prefix="7z_reader_")
        try:
            # 调用_process_7z方法处理7Z文件
            documents = self._process_7z(
                sevenzip_path=file,
                temp_dir=temp_dir,
                current_depth=0,  # 当前嵌套深度从0开始
                max_depth=max_depth,
                max_file_size=max_file_size,
                max_total_size=max_total_size,
                max_files=max_files,
                max_compression_ratio=max_compression_ratio,
                base_metadata=ext_info or {},  # 基础元数据
                archive_root=file.name,  # 归档根文件名
            )
            return documents
        finally:
            # 无论处理成功与否，都清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _process_7z(
        self,
        sevenzip_path: Path,
        temp_dir: str,
        current_depth: int,
        max_depth: int,
        max_file_size: int,
        max_total_size: int,
        max_files: int,
        max_compression_ratio: float,
        base_metadata: Dict,
        archive_root: str,
        parent_path: str = "",  # 父路径，用于构建完整路径
    ) -> List[Document]:
        """递归处理7Z归档文件"""
        documents, _, _ = self._process_7z_with_usage(
            sevenzip_path=sevenzip_path,
            temp_dir=temp_dir,
            current_depth=current_depth,
            max_depth=max_depth,
            max_file_size=max_file_size,
            max_total_size=max_total_size,
            max_files=max_files,
            max_compression_ratio=max_compression_ratio,
            base_metadata=base_metadata,
            archive_root=archive_root,
            parent_path=parent_path,
        )
        return documents

    def _process_7z_with_usage(
        self,
        sevenzip_path: Path,
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
    ) -> Tuple[List[Document], int, int]:
        """Process one archive and report the bytes and files consumed.

        Reporting usage lets a parent archive charge nested extraction against
        its own remaining ``max_total_size`` and ``max_files`` budgets before
        extracting any later member.
        """
        import py7zr

        documents = []
        total_extracted = 0
        file_count = 0
        try:
            with py7zr.SevenZipFile(str(sevenzip_path), 'r') as archive:
                # Validate every entry before extracting even the first member.
                safe_targets, expected_sizes = self._preflight_7z_entries(
                    archive=archive,
                    max_file_size=max_file_size,
                    max_total_size=max_total_size,
                    max_files=max_files,
                    max_compression_ratio=max_compression_ratio,
                )
                extract_dir = temp_dir
                os.makedirs(extract_dir, exist_ok=True)

                # Extract one validated target at a time. Nested archives can
                # consume arbitrary additional bytes, so extracting all outer
                # targets up front would bypass the aggregate limits.
                for entry_name in safe_targets:
                    uncompressed_size = expected_sizes[entry_name]
                    if file_count >= max_files:
                        break
                    if total_extracted + uncompressed_size > max_total_size:
                        break

                    try:
                        archive.extract(path=temp_dir, targets=[entry_name])
                    except Exception:
                        continue

                    # Path containment and size mismatches are security errors,
                    # so they must not be swallowed by the per-file fallback.
                    self._verify_extracted_files(
                        temp_dir, {entry_name: uncompressed_size}
                    )
                    total_extracted += uncompressed_size
                    file_count += 1

                    extracted_path = Path(extract_dir) / entry_name
                    full_path = (
                        os.path.join(parent_path, entry_name)
                        if parent_path
                        else entry_name
                    )

                    # The nested archive itself has already been charged above.
                    # Give the recursive call only what is left and then charge
                    # the bytes and files it actually consumed, so a later
                    # sibling starts from the updated parent totals instead of
                    # the original limits.
                    remaining_total = max_total_size - total_extracted
                    remaining_files = max_files - file_count

                    if extracted_path.suffix.lower() == '.7z':
                        if current_depth >= max_depth:
                            # Never fall back to _process_file() here: its
                            # SevenZipReader would reopen the archive with the
                            # default limits and bypass this parent's budget.
                            continue
                        nested_docs, nested_size, nested_files = (
                            self._process_7z_with_usage(
                                sevenzip_path=extracted_path,
                                temp_dir=temp_dir,
                                current_depth=current_depth + 1,
                                max_depth=max_depth,
                                max_file_size=max_file_size,
                                max_total_size=remaining_total,
                                max_files=remaining_files,
                                max_compression_ratio=max_compression_ratio,
                                base_metadata=base_metadata,
                                archive_root=archive_root,
                                parent_path=full_path,
                            )
                        )
                        documents.extend(nested_docs)
                        total_extracted += nested_size
                        file_count += nested_files
                        continue

                    try:
                        doc = self._process_file(
                            file_path=extracted_path,
                            archive_path=full_path,
                            archive_root=archive_root,
                            archive_depth=current_depth,
                            base_metadata=base_metadata,
                        )
                        if doc:
                            documents.extend(doc)
                    except Exception:
                        # Skip members that this reader cannot parse, but keep
                        # their extraction usage charged to the parent budget.
                        continue

        except (py7zr.Bad7zFile, py7zr.exceptions.Bad7zFile) as e:
            raise ValueError(f"Failed to read 7Z file: {str(e)}")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error processing 7Z file: {str(e)}")

        return documents, total_extracted, file_count

    @staticmethod
    def _validate_entry_name(entry_name: str) -> Optional[str]:
        """Validate one archive member name before it can reach extraction.

        The returned value is a normalized relative POSIX path. ``None`` means
        the entry only refers to the archive root and carries no file content.
        """
        if not entry_name:
            raise ValueError("7Z archive contains an empty entry name")
        if "\x00" in entry_name:
            raise ValueError(f"Unsafe 7Z entry name (NUL byte): {entry_name!r}")
        if "\\" in entry_name:
            raise ValueError(f"Unsafe 7Z entry name (backslash): {entry_name!r}")
        if entry_name.startswith("/"):
            raise ValueError(f"Unsafe 7Z entry name (absolute path): {entry_name!r}")
        if re.match(r"^[A-Za-z]:", entry_name):
            raise ValueError(
                f"Unsafe 7Z entry name (drive-qualified path): {entry_name!r}"
            )

        member_path = PurePosixPath(entry_name)
        if member_path.is_absolute():
            raise ValueError(f"Unsafe 7Z entry name (absolute path): {entry_name!r}")
        if ".." in member_path.parts:
            raise ValueError(f"Unsafe 7Z entry name (path traversal): {entry_name!r}")

        normalized_parts = [
            part for part in member_path.parts if part not in {"", "."}
        ]
        if not normalized_parts:
            return None
        return "/".join(normalized_parts)

    @staticmethod
    def _is_special_entry(file_info) -> bool:
        """Return whether metadata describes a symlink or non-regular entry."""
        if bool(getattr(file_info, "is_symlink", False)):
            return True
        for attribute in (
            "is_fifo",
            "is_socket",
            "is_block_device",
            "is_char_device",
            "is_device",
        ):
            if bool(getattr(file_info, attribute, False)):
                return True

        attributes = getattr(file_info, "attributes", None)
        if attributes is None:
            return False

        try:
            attributes = int(attributes)
        except (TypeError, ValueError):
            return True

        # FILE_ATTRIBUTE_REPARSE_POINT is used for Windows links and junctions.
        if attributes & 0x400:
            return True

        # py7zr stores Unix mode bits in the upper 16 bits on Unix. A zero
        # file-type mask means that the entry carries only portable attributes.
        mode = attributes >> 16
        if not mode:
            return False
        file_type = stat.S_IFMT(mode)
        return bool(file_type and file_type not in (stat.S_IFREG, stat.S_IFDIR))

    @staticmethod
    def _archive_requires_password(archive) -> bool:
        """Detect encrypted archives across supported py7zr versions."""
        needs_password = getattr(archive, "needs_password", None)
        if callable(needs_password):
            needs_password = needs_password()
        if needs_password:
            return True
        for attribute in ("password_protected", "is_encrypted"):
            value = getattr(archive, attribute, None)
            if callable(value):
                value = value()
            if value:
                return True
        return False

    def _preflight_7z_entries(
        self,
        archive,
        max_file_size: int,
        max_total_size: int,
        max_files: int,
        max_compression_ratio: float,
    ) -> Tuple[List[str], Dict[str, int]]:
        """Build an allowlist of safe members using metadata only.

        Unsafe names and entry types fail closed. Resource limits retain the
        reader's historical behavior: oversized members are skipped, while the
        first ``max_files`` members within ``max_total_size`` are selected.
        """
        if self._archive_requires_password(archive):
            raise ValueError("Encrypted 7Z archives are not supported")

        entries = archive.getnames()
        file_info_map = {info.filename: info for info in archive.list()}
        safe_targets: List[str] = []
        expected_sizes: Dict[str, int] = {}
        total_size = 0
        file_count = 0
        accepting_members = True
        aggregate_ratio = None
        aggregate_ratio_checked = False

        for entry_name in entries:
            normalized_name = self._validate_entry_name(entry_name)
            file_info = file_info_map.get(entry_name)
            if file_info is None:
                raise ValueError(
                    f"7Z archive metadata is missing for entry: {entry_name!r}"
                )

            if self._is_special_entry(file_info):
                raise ValueError(
                    "Unsafe 7Z entry type (symlink or special file): "
                    f"{entry_name!r}"
                )

            is_directory = bool(getattr(file_info, "is_directory", False))
            if is_directory or entry_name.endswith("/") or normalized_name is None:
                continue

            uncompressed_value = getattr(file_info, "uncompressed", None)
            if uncompressed_value is None:
                raise ValueError(
                    f"7Z entry is missing uncompressed size metadata: {entry_name!r}"
                )
            try:
                uncompressed_size = int(uncompressed_value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"7Z entry has invalid uncompressed size metadata: {entry_name!r}"
                ) from exc
            if uncompressed_size < 0:
                raise ValueError(
                    f"7Z entry has invalid size metadata: {entry_name!r}"
                )

            compressed_value = getattr(file_info, "compressed", None)
            if compressed_value is None:
                compressed_size = 0
            else:
                try:
                    compressed_size = int(compressed_value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"7Z entry has invalid compressed size metadata: {entry_name!r}"
                    ) from exc
                if compressed_size < 0:
                    raise ValueError(
                        f"7Z entry has invalid size metadata: {entry_name!r}"
                    )

            if uncompressed_size > 0 and compressed_size > 0:
                ratio = uncompressed_size / compressed_size
                if ratio > max_compression_ratio:
                    raise ValueError(
                        f"7Z entry has suspicious compression ratio: {entry_name}"
                    )
            elif uncompressed_size > 0:
                # Solid 7z blocks may not expose a per-file compressed size.
                # Fall back to the aggregate ratio, but never skip the check
                # merely because the metadata is absent.
                if not aggregate_ratio_checked:
                    aggregate_ratio = self._archive_compression_ratio(archive)
                    aggregate_ratio_checked = True
                if aggregate_ratio is None:
                    raise ValueError(
                        f"7Z entry is missing compressed size metadata: {entry_name!r}"
                    )
                if aggregate_ratio > max_compression_ratio:
                    raise ValueError(
                        "7Z archive has suspicious compression ratio: "
                        f"{aggregate_ratio:.2f}"
                    )

            if not accepting_members:
                continue
            if uncompressed_size > max_file_size:
                continue
            if file_count >= max_files:
                accepting_members = False
                continue
            if total_size + uncompressed_size > max_total_size:
                accepting_members = False
                continue

            safe_targets.append(entry_name)
            expected_sizes[entry_name] = uncompressed_size
            total_size += uncompressed_size
            file_count += 1

        return safe_targets, expected_sizes

    @staticmethod
    def _archive_compression_ratio(archive) -> Optional[float]:
        """Return the aggregate ratio when per-file compressed sizes are absent."""
        archiveinfo = getattr(archive, "archiveinfo", None)
        if not callable(archiveinfo):
            return None
        try:
            archive_info = archiveinfo()
            compressed_size = int(getattr(archive_info, "compressed", 0) or 0)
            uncompressed_size = int(
                getattr(archive_info, "uncompressed", 0) or 0
            )
        except (TypeError, ValueError, AttributeError):
            return None
        if compressed_size <= 0 or uncompressed_size < 0:
            return None
        return uncompressed_size / compressed_size

    @staticmethod
    def _verify_extracted_files(
        temp_dir: str, expected_sizes: Dict[str, int]
    ) -> None:
        """Confirm extracted members stayed inside ``temp_dir`` and match metadata."""
        base_dir = Path(temp_dir).resolve()
        for entry_name, expected_size in expected_sizes.items():
            destination = Path(temp_dir) / entry_name
            if destination.is_symlink():
                raise ValueError(
                    f"Extracted 7Z entry became a symlink: {entry_name!r}"
                )

            try:
                resolved_destination = destination.resolve(strict=True)
            except FileNotFoundError as exc:
                raise ValueError(
                    f"7Z entry was not extracted: {entry_name!r}"
                ) from exc

            try:
                resolved_destination.relative_to(base_dir)
            except ValueError as exc:
                raise ValueError(
                    "Extracted 7Z entry escaped the temporary directory: "
                    f"{entry_name!r}"
                ) from exc

            if not resolved_destination.is_file():
                raise ValueError(
                    f"Extracted 7Z entry is not a regular file: {entry_name!r}"
                )

            actual_size = resolved_destination.stat().st_size
            if actual_size != expected_size:
                raise ValueError(
                    "Extracted 7Z entry size does not match archive metadata: "
                    f"{entry_name!r} (expected {expected_size}, got {actual_size})"
                )

    def _process_file(
        self,
        file_path: Path,
        archive_path: str,
        archive_root: str,
        archive_depth: int,
        base_metadata: Dict,
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
            metadata = {
                "file_name": file_path.name,
                "file_path": f"{archive_root}::{archive_path}",  # 格式：根文件::内部路径
                "file_suffix": file_path.suffix.lower(),
                "archive_root": archive_root,
                "archive_path": archive_path,
                "archive_depth": archive_depth,
            }
            # 合并基础元数据
            metadata.update(base_metadata)

            # 使用对应的读取器加载文件数据
            documents = reader.load_data(file_path, ext_info=metadata)
            return documents

        except Exception as e:
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
            '.pdf': 'PdfReader',
            '.docx': 'DocxReader',
            '.pptx': 'PptxReader',
            '.xlsx': 'XlsxReader',
            '.epub': 'EpubReader',
            '.txt': 'TxtReader',
            '.md': 'MarkdownReader',
            '.csv': 'CSVReader',
            '.conf': 'TxtReader',  # 配置文件按文本处理
            '.log': 'TxtReader',   # 日志文件按文本处理
            '.ini': 'TxtReader',   # ini文件按文本处理
            '.cfg': 'TxtReader',   # cfg文件按文本处理
            # 各种编程语言文件使用代码读取器
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
            # 数据格式文件
            '.json': 'CodeReader',
            '.xml': 'CodeReader',
            '.yaml': 'CodeReader',
            '.yml': 'CodeReader',
            # 7Z特定格式
            '.7z': 'SevenZipReader',  # 支持嵌套7Z文件
        }

        # 获取对应的读取器名称
        reader_name = reader_map.get(suffix)
        if not reader_name:
            return None

        try:
            # 动态导入对应的读取器类
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
            elif reader_name == 'SevenZipReader':
                # 返回自身类型以支持嵌套7Z文件
                return SevenZipReader
            else:
                return None
        except ImportError:
            # 如果导入失败，返回None
            return None
