# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: image_ocr_reader.py
import logging
from typing import List, Optional, Dict, Union
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.reader import Reader
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
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path) or not file.exists():
            raise FileNotFoundError(f"ImageOCRReader file not found: {file}")

        text, engine = self._ocr(file)
        logger.debug("ImageOCRReader extracted by %s, length=%d", engine, len(text))

        metadata: Dict = {"source": "image", "file_name": file.name, "engine": engine}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _ocr(self, file: Path) -> (str, str):
        last_exc = None
        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR  # type: ignore
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(str(file), cls=True)
            lines: List[str] = []
            # PaddleOCR returns [[None]] or [[(box, (None, conf))]] for
            # low-confidence pages; the previous loop did `for line in page`
            # and `line[1][0]` unconditionally and raised TypeError, which
            # the outer except caught and silently downgraded to the next
            # engine without surfacing the cause.
            for page in result or []:
                if page is None:
                    continue
                for line in page:
                    if line is None or len(line) < 2 or line[1] is None:
                        continue
                    txt = line[1][0]
                    if txt:
                        lines.append(txt)
            return "\n".join(lines), "paddleocr"
        except Exception as e_paddle:
            last_exc = e_paddle
            logger.debug("ImageOCRReader PaddleOCR failed: %s", e_paddle,
                         exc_info=True)

        # Fallback to pytesseract
        try:
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
            img = Image.open(file)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return text, "pytesseract"
        except Exception as e_tess:
            last_exc = e_tess
            logger.debug("ImageOCRReader pytesseract failed: %s", e_tess,
                         exc_info=True)

        # Fallback to easyocr
        try:
            import easyocr  # type: ignore
            reader = easyocr.Reader(['ch_sim', 'en'])
            result = reader.readtext(str(file), detail=0)
            return "\n".join(result), "easyocr"
        except Exception as e_easy:
            last_exc = e_easy
            raise ImportError(
                "No OCR engine available. Install one of: "
                "`pip install paddleocr paddlepaddle` or "
                "`pip install pytesseract pillow` or "
                "`pip install easyocr`"
            ) from last_exc
