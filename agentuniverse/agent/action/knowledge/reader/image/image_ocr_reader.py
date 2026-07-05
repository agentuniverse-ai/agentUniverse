# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: image_ocr_reader.py
import logging
from typing import List, Optional, Dict, Union
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class ImageOCRReader(Reader):
    """OCR reader for image files.

    Preferred engine: PaddleOCR. Fallback: Tesseract or easyocr.
    Install tips:
      - pip install paddleocr paddlepaddle  (or CPU/GPU variant)
      - or pip install pytesseract pillow
      - or pip install easyocr
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        logger.info("ImageOCRReader start load file=%s", file)
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path) or not file.exists():
            raise ReaderLoadError(
                f"ImageOCRReader file not found: {file}",
                reader_name="ImageOCRReader",
                source=str(file),
            )

        text, engine = self._ocr(file)
        logger.info("ImageOCRReader extracted by %s, length=%d", engine, len(text))

        metadata: Dict = {"source": "image", "file_name": file.name, "engine": engine}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _ocr(self, file: Path) -> (str, str):
        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR  # type: ignore
            logger.debug("ImageOCRReader using PaddleOCR")
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(str(file), cls=True)
            lines: List[str] = []
            for page in result:
                for line in page:
                    txt = line[1][0]
                    if txt:
                        lines.append(txt)
            return "\n".join(lines), "paddleocr"
        except Exception as e_paddle:
            logger.debug("ImageOCRReader PaddleOCR failed: %s", e_paddle)

        # Fallback to pytesseract
        try:
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
            logger.debug("ImageOCRReader using pytesseract")
            img = Image.open(file)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return text, "pytesseract"
        except Exception as e_tess:
            logger.debug("ImageOCRReader pytesseract failed: %s", e_tess)

        # Fallback to easyocr
        try:
            import easyocr  # type: ignore
            logger.debug("ImageOCRReader using easyocr")
            reader = easyocr.Reader(['ch_sim', 'en'])
            result = reader.readtext(str(file), detail=0)
            return "\n".join(result), "easyocr"
        except Exception as e_easy:
            raise ReaderDependencyError(
                "No OCR engine available",
                reader_name="ImageOCRReader",
                dependency="paddleocr or pytesseract or easyocr",
                install_hint="pip install paddleocr paddlepaddle  OR  pip install pytesseract pillow  OR  pip install easyocr",
            )