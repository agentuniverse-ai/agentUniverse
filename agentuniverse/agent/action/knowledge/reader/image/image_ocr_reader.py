# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: image_ocr_reader.py
"""OCR reader for image files.

Preferred engine: PaddleOCR. Fallback: Tesseract or easyocr. Optional OCR
engines are imported lazily so the reader can be registered without them
installed. Runtime options (e.g. ``ocr_lang``) can be supplied through
``ext_info`` when calling ``load_data``.

Install tips:
  - pip install paddleocr paddlepaddle  (or CPU/GPU variant)
  - or pip install pytesseract pillow
  - or pip install easyocr
"""
from pathlib import Path
from typing import Dict, List, Optional, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER


class ImageOCRReader(Reader):
    """OCR reader for image files.

    Preferred engine: PaddleOCR. Fallback: Tesseract or easyocr.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Run OCR on an image file and return the text as a Document.

        Args:
            file (Union[str, Path]): Path to the image file.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - ocr_lang (str): Language hint forwarded to the OCR engine.

        Returns:
            List[Document]: Documents containing the extracted OCR text.

        Raises:
            ReaderConfigError: If the file does not exist.
            ReaderDependencyError: If no OCR engine is available.
        """
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path) or not file.exists():
            raise ReaderConfigError(
                f"ImageOCRReader file not found: {file}",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"ImageOCRReader start load file={file}")

        ocr_lang = (ext_info or {}).get("ocr_lang", "ch")
        text, engine = self._ocr(file, ocr_lang)
        LOGGER.debug(f"ImageOCRReader extracted by {engine}, length={len(text)}")

        metadata: Dict = {"source": "image", "file_name": file.name, "engine": engine}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _ocr(self, file: Path, ocr_lang: str = "ch") -> tuple:
        """Extract text from an image using the first available OCR engine.

        Args:
            file (Path): Path to the image file.
            ocr_lang (str): Language hint forwarded to the OCR engine.

        Returns:
            tuple: The extracted (text, engine_name).

        Raises:
            ReaderDependencyError: If no OCR engine is available.
        """
        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR  # type: ignore
            LOGGER.debug("ImageOCRReader using PaddleOCR")
            ocr = PaddleOCR(use_angle_cls=True, lang=ocr_lang)
            result = ocr.ocr(str(file), cls=True)
            lines: List[str] = []
            for page in result:
                for line in page:
                    txt = line[1][0]
                    if txt:
                        lines.append(txt)
            return "\n".join(lines), "paddleocr"
        except Exception as e_paddle:
            LOGGER.debug(f"ImageOCRReader PaddleOCR failed: {e_paddle}")

        # Fallback to pytesseract
        try:
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
            LOGGER.debug("ImageOCRReader using pytesseract")
            img = Image.open(file)
            tess_lang = "chi_sim+eng" if ocr_lang in ("ch", "chi") else ocr_lang
            text = pytesseract.image_to_string(img, lang=tess_lang)
            return text, "pytesseract"
        except Exception as e_tess:
            LOGGER.debug(f"ImageOCRReader pytesseract failed: {e_tess}")

        # Fallback to easyocr
        try:
            import easyocr  # type: ignore
            LOGGER.debug("ImageOCRReader using easyocr")
            langs = ['ch_sim', 'en'] if ocr_lang in ("ch", "chi") else [ocr_lang]
            reader = easyocr.Reader(langs)
            result = reader.readtext(str(file), detail=0)
            return "\n".join(result), "easyocr"
        except Exception as e_easy:
            raise ReaderDependencyError(
                "No OCR engine available. Install one of: "
                "`pip install paddleocr paddlepaddle` or "
                "`pip install pytesseract pillow` or "
                "`pip install easyocr`",
                reader_name=self.__class__.__name__,
            ) from e_easy
