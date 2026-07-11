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
from agentuniverse.base.util.logging.logging_util import LOGGER

# Mapping of URL domain patterns to the registered cloud reader component names.
# Each key is a lower-cased substring matched against the URL netloc.
URL_PATTERN_MAP = {
    "feishu.cn": "default_feishu_reader",
    "feishu.net": "default_feishu_reader",
    "larksuite.com": "default_feishu_reader",
    "yuque.com": "default_yuque_reader",
    "notion.so": "default_notion_reader",
    "notion.site": "default_notion_reader",
    "atlassian.net": "default_confluence_reader",
    "confluence": "default_confluence_reader",
    "docs.google.com": "default_google_docs_reader",
}


def _match_url_reader_name(url: str):
    """Return the registered cloud reader component name for the given url.

    Args:
        url (str): The cloud document url.

    Returns:
        Optional[str]: The matched reader component name, or ``None``.
    """
    if not url:
        return None
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc.lower()
    host = netloc.split(":")[0] if netloc else url.lower()
    for pattern, reader_name in URL_PATTERN_MAP.items():
        if pattern in host:
            return reader_name
    return None


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
        """Resolve the default cloud reader instance for a url.

        The url host is matched against :data:`URL_PATTERN_MAP`; the matching
        cloud reader (e.g. Feishu, Yuque, Notion, Confluence, Google Docs) is
        returned so callers do not need to pick the concrete reader manually.

        Args:
            url (str): The cloud document url.
            new_instance (bool): Whether to return a new reader instance.

        Returns:
            Optional[Reader]: A reader instance, or ``None`` if no platform
            matches or the resolved reader is unavailable.
        """
        reader_name = _match_url_reader_name(url)
        if not reader_name:
            return None
        try:
            return self.get_instance_obj(reader_name)
        except Exception as e:
            LOGGER.warning(
                f"ReaderManager failed to resolve url reader '{reader_name}': {e}"
            )
            return None
