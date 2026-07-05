# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 11:41
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: reader_manager.py

from urllib.parse import urlparse

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
        "sevenzip": "default_sevenzip_reader",
        # extended defaults for web & images
        "url": "default_web_page_reader",
        "png": "default_image_ocr_reader",
        "jpg": "default_image_ocr_reader",
        "jpeg": "default_image_ocr_reader",
        "bmp": "default_image_ocr_reader",
        "tiff": "default_image_ocr_reader",
        "webp": "default_image_ocr_reader",
    }

    # URL pattern → Reader instance name for automatic cloud platform routing
    URL_PATTERN_MAP: dict[str, str] = {
        "feishu.cn": "default_feishu_reader",
        "yuque.com": "default_yuque_reader",
        "notion.so": "default_notion_reader",
        "confluence": "default_confluence_reader",
        "docs.google.com": "default_google_docs_reader",
    }

    def __init__(self):
        super().__init__(ComponentEnum.READER)

    def get_file_default_reader(self,
                                file_type: str,
                                new_instance: bool = False) -> Reader | None:
        if file_type in self.DEFAULT_READER:
            return self.get_instance_obj(self.DEFAULT_READER[file_type])
        else:
            return None

    def get_url_default_reader(self, url: str, new_instance: bool = False) -> Reader | None:
        """Get the default cloud Reader for a URL via domain pattern matching.

        Args:
            url: The full URL to match against registered URL patterns.
            new_instance: If True, return a fresh copy of the Reader.

        Returns:
            Reader | None: The matched Reader instance, or None if no pattern matches.
        """
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            return None

        for pattern, reader_name in self.URL_PATTERN_MAP.items():
            if pattern in domain:
                return self.get_instance_obj(reader_name, new_instance=new_instance)
        return None
