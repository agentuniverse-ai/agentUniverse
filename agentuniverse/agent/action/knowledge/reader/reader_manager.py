# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 11:41
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: reader_manager.py

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import \
    ComponentManagerBase, ComponentTypeVar
from agentuniverse.agent.action.knowledge.reader.reader import Reader


@singleton
class ReaderManager(ComponentManagerBase[Reader]):
    """A singleton manager class of the reader."""
    DEFAULT_READER = {
        "pdf": "default_pdf_reader",
        "pptx": "default_pptx_reader",
        "docx": "default_docx_reader",
        "txt": "default_txt_reader",
        "md": "default_markdown_reader",
        "markdown": "default_markdown_reader",
        "csv": "default_csv_reader",
        "json": "default_json_reader",
        "rar": "default_rar_reader",
        "zip": "default_zip_reader",
        "7z": "default_sevenzip_reader",
        "sevenzip": "default_sevenzip_reader",
        "xlsx": "xlsx_reader",
        "epub": "default_epub_reader",
        "py": "default_code_reader",
        "js": "default_code_reader",
        "ts": "default_code_reader",
        "java": "default_code_reader",
        "cpp": "default_code_reader",
        "c": "default_code_reader",
        "h": "default_code_reader",
        "hpp": "default_code_reader",
        "cs": "default_code_reader",
        "go": "default_code_reader",
        "rb": "default_code_reader",
        "php": "default_code_reader",
        "swift": "default_code_reader",
        "kt": "default_code_reader",
        "rs": "default_code_reader",
        "sh": "default_code_reader",
        "html": "default_code_reader",
        "css": "default_code_reader",
        "sql": "default_code_reader",
        "xml": "default_code_reader",
        "yaml": "default_code_reader",
        "yml": "default_code_reader",
        # extended defaults for web & images
        "url": "default_web_page_reader",
        "png": "default_image_ocr_reader",
        "jpg": "default_image_ocr_reader",
        "jpeg": "default_image_ocr_reader",
        "bmp": "default_image_ocr_reader",
        "tiff": "default_image_ocr_reader",
        "webp": "default_image_ocr_reader",
    }

    def __init__(self):
        super().__init__(ComponentEnum.READER)

    def get_file_default_reader(self,
                                file_type: str,
                                new_instance: bool = True) -> Reader | None:
        reader_name = self.DEFAULT_READER.get(file_type.lstrip('.'))
        if reader_name is None:
            return None
        return self.get_instance_obj(
            reader_name,
            new_instance=new_instance,
        )
