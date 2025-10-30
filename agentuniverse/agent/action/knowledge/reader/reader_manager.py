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
