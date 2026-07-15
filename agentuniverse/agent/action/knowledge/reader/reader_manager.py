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

    # Mapping of cloud-platform domain substrings to registered reader names.
    # Used by ``get_url_default_reader`` to auto-select a reader from a URL.
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

    def get_url_default_reader(self,
                               url: str,
                               new_instance: bool = False) -> Reader | None:
        """Return the appropriate cloud reader for *url*, or ``None``.

        Inspects the URL hostname and matches it against
        ``URL_PATTERN_MAP``.  The first entry whose domain key is a
        substring of the hostname wins.

        Args:
            url: Cloud document URL (e.g. a Feishu or Yuque link).
            new_instance: If ``True``, create a fresh reader instance
                instead of returning the cached singleton.

        Returns:
            A :class:`Reader` instance, or ``None`` if no pattern matches.
        """
        try:
            hostname = urlparse(url).hostname or ""
        except Exception:
            return None

        hostname = hostname.lower()
        for domain_key, reader_name in self.URL_PATTERN_MAP.items():
            if domain_key in hostname:
                return self.get_instance_obj(reader_name)
        return None
