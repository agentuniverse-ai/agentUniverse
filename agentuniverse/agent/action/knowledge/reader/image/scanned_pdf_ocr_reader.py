# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: scanned_pdf_ocr_reader.py
import logging
from typing import List, Optional, Dict, Union
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class ScannedPdfOCRReader(Reader):
    """Reader for scanned PDFs using page-level OCR.

    Strategy:
      1) Try to extract text with pypdf. If empty/None, fallback to OCR.
      2) OCR via PaddleOCR -> pytesseract -> easyocr.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        logger.info("ScannedPdfOCRReader start load file=%s", file)
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path) or not file.exists():
            raise ReaderLoadError(
                f"ScannedPdfOCRReader file not found: {file}",
                reader_name="ScannedPdfOCRReader",
                source=str(file),
            )

        texts: List[str] = []
        engines: List[str] = []
        try:
            import pypdf  # type: ignore
            logger.info("ScannedPdfOCRReader using pypdf first")
            with open(file, "rb") as fp:
                pdf = pypdf.PdfReader(fp)
                for i, page in enumerate(pdf.pages):
                    txt = page.extract_text() or ""
                    if txt.strip():
                        texts.append(txt)
                        engines.append("pypdf")
                    else:
                        ocr_txt, ocr_engine = self._ocr_pdf_page(file, i)
                        texts.append(ocr_txt)
                        engines.append(ocr_engine)
        except Exception as e:
            logger.debug("ScannedPdfOCRReader pypdf failed: %s", e)
            # If pypdf fails, OCR every page
            num_pages = self._count_pdf_pages(file)
            for i in range(num_pages):
                ocr_txt, ocr_engine = self._ocr_pdf_page(file, i)
                texts.append(ocr_txt)
                engines.append(ocr_engine)

        text_all = "\n\n".join(texts)
        engine_summary = ",".join(sorted(set(engines))) if engines else "unknown"
        metadata: Dict = {"source": "pdf", "file_name": file.name, "engine": engine_summary}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text_all, metadata=metadata)]

    def _count_pdf_pages(self, file: Path) -> int:
        try:
            import pypdf  # type: ignore
            with open(file, "rb") as fp:
                pdf = pypdf.PdfReader(fp)
                return len(pdf.pages)
        except Exception:
            return 0

    def _ocr_pdf_page(self, file: Path, page_index: int) -> (str, str):
        # Convert PDF page to image
        try:
            from pdf2image import convert_from_path  # type: ignore
        except Exception:
            raise ReaderDependencyError(
                "pdf2image is required for OCR on scanned PDFs",
                reader_name="ScannedPdfOCRReader",
                dependency="pdf2image",
                install_hint="pip install pdf2image (also install poppler system package)",
            )

        logger.info("ScannedPdfOCRReader converting page %d to image", page_index)
        images = convert_from_path(str(file), first_page=page_index + 1, last_page=page_index + 1)
        if not images:
            return "", "none"

        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR  # type: ignore
            logger.info("ScannedPdfOCRReader using PaddleOCR")
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(images[0], cls=True)
            lines = []
            for page in result:
                for line in page:
                    txt = line[1][0]
                    if txt:
                        lines.append(txt)
            return "\n".join(lines), "paddleocr"
        except Exception as e_paddle:
            logger.debug("ScannedPdfOCRReader PaddleOCR failed: %s", e_paddle)

        # Fallback to pytesseract
        try:
            import pytesseract  # type: ignore
            logger.info("ScannedPdfOCRReader using pytesseract")
            text = pytesseract.image_to_string(images[0], lang='chi_sim+eng')
            return text, "pytesseract"
        except Exception as e_tess:
            logger.debug("ScannedPdfOCRReader pytesseract failed: %s", e_tess)

        # Fallback to easyocr
        try:
            import easyocr  # type: ignore
            logger.info("ScannedPdfOCRReader using easyocr")
            reader = easyocr.Reader(['ch_sim', 'en'])
            result = reader.readtext(images[0], detail=0)
            return "\n".join(result), "easyocr"
        except Exception:
            return "", "unknown"
