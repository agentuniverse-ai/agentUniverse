import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Union, Optional, Dict, Type

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
import pdb

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
        # 尝试导入py7zr库
        try:
            import py7zr
        except ImportError:
            # 如果py7zr未安装，抛出导入错误
            raise ImportError(
                "py7zr is required to read 7Z files: "
                "`pip install py7zr`"
            )

        # 将字符串路径转换为Path对象
        if isinstance(file, str):
            file = Path(file)

        # 检查文件是否存在
        if not file.exists():
            raise FileNotFoundError(f"7Z file not found: {file}")

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
        import py7zr

        documents = []  # 存储提取的文档
        total_extracted = 0  # 已提取文件总大小
        file_count = 0  # 已处理文件计数
        with py7zr.SevenZipFile(str(sevenzip_path), 'r') as archive:
            archive.extractall(path=temp_dir)

        try:
            # 以只读模式打开7Z文件
            with py7zr.SevenZipFile(str(sevenzip_path), 'r') as archive:
                # 获取7Z文件中的所有条目
                entries = archive.getnames()
                
                # 获取每个文件的详细信息
                file_info_map = {}
                files_info = archive.list()
                
                for file_info in files_info:
                    file_info_map[file_info.filename] = file_info

                # 遍历每个条目
                for entry_name in entries:
                    #print(entry_name)
                    #if(entry_name=="config/app_config.yaml"):
                        #pdb.set_trace()
                    # 检查是否达到最大文件数限制
                    if file_count >= max_files:
                        break

                    # 跳过目录条目（7z中目录以/结尾）
                    if entry_name.endswith('/'):
                        continue
                    if '.' not in entry_name:
                        continue
                    if entry_name=='.':
                        continue

                    # 安全检查：跳过包含".."或绝对路径的文件名
                    if '..' in entry_name or entry_name.startswith('/'):
                        continue

                    # 获取文件信息
                    file_info = file_info_map.get(entry_name)
                    if not file_info:
                        continue

                    # 获取压缩后大小和未压缩大小
                    compressed_size = file_info.compressed or 0
                    uncompressed_size = file_info.uncompressed or 0

                    # 检查压缩比，防止压缩炸弹攻击
                    if compressed_size > 0:
                        ratio = uncompressed_size / compressed_size
                        if ratio > max_compression_ratio:
                            raise ValueError(
                                f"7Z entry has suspicious compression ratio: {entry_name}"
                            )

                    # 跳过超过单文件大小限制的文件
                    if uncompressed_size > max_file_size:
                        continue

                    # 检查是否超过总大小限制
                    if total_extracted + uncompressed_size > max_total_size:
                        break

                    # 为每个文件创建独立的解压目录
                    #extract_dir = os.path.join(temp_dir, f"extract_{file_count}")
                    extract_dir = temp_dir
                    os.makedirs(extract_dir, exist_ok=True)

                    try:
                        # 解压当前条目
                        #archive.extract(path=extract_dir, targets=[entry_name])
                        #archive.extract(entry_name,extract_dir)
                        
                        # 构建提取后的完整路径
                        extracted_path = Path(extract_dir) / entry_name
                        total_extracted += uncompressed_size
                        file_count += 1

                        # 构建完整路径（包含父路径信息）
                        full_path = os.path.join(parent_path, entry_name) if parent_path else entry_name

                        # 如果是嵌套的7Z文件且未达到最大深度，递归处理
                        if extracted_path.suffix.lower() == '.7z' and current_depth < max_depth:
                            nested_docs = self._process_7z(
                                sevenzip_path=extracted_path,
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
                            #print(extracted_path)
                            documents.extend(nested_docs)
                        else:
                            # 处理普通文件
                            doc = self._process_file(
                                file_path=extracted_path,
                                archive_path=full_path,
                                archive_root=archive_root,
                                archive_depth=current_depth,
                                base_metadata=base_metadata,
                            )
                            #print(extracted_path)
                            if doc:
                                documents.extend(doc)

                    except Exception as e:
                        # 跳过处理失败的文件，继续处理其他文件
                        continue

        except (py7zr.Bad7zFile, py7zr.exceptions.Bad7zFile) as e:
            raise ValueError(f"Failed to read 7Z file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing 7Z file: {str(e)}")

        return documents

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
            #pdb.set_trace()
            # 合并基础元数据
            metadata.update(base_metadata)

            # 使用对应的读取器加载文件数据
            documents = reader.load_data(file_path, ext_info=metadata)
            #print(len(documents))
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