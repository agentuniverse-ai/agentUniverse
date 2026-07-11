# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: scanned_pdf_ocr_reader.py
"""Reader for scanned PDFs using page-level OCR.

Strategy:
  1) Try to extract text with pypdf. If empty/None, fallback to OCR.
  2) OCR via PaddleOCR -> pytesseract -> easyocr.

Optional dependencies (pypdf, pdf2image, OCR engines) are imported lazily.
Runtime options such as ``max_pages`` (maximum OCR page limit) and
``ocr_lang`` can be supplied through ``ext_info``.
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

_DEFAULT_MAX_PAGES = 50


class ScannedPdfOCRReader(Reader):
    """Reader for scanned PDFs using page-level OCR.

    Strategy:
      1) Try to extract text with pypdf. If empty/None, fallback to OCR.
      2) OCR via PaddleOCR -> pytesseract -> easyocr.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Run OCR on a scanned PDF and return the text as a Document.

        Args:
            file (Union[str, Path]): Path to the PDF file.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - max_pages (int): Maximum number of pages to OCR.
                - ocr_lang (str): Language hint forwarded to the OCR engine.

        Returns:
            List[Document]: Documents containing the extracted text.

        Raises:
            ReaderConfigError: If the file does not exist.
        """
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path) or not file.exists():
            raise ReaderConfigError(
                f"ScannedPdfOCRReader file not found: {file}",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"ScannedPdfOCRReader start load file={file}")

        max_pages = int((ext_info or {}).get("max_pages", _DEFAULT_MAX_PAGES))
        ocr_lang = (ext_info or {}).get("ocr_lang", "ch")

        texts: List[str] = []
        engines: List[str] = []
        try:
            import pypdf  # type: ignore
            LOGGER.debug("ScannedPdfOCRReader using pypdf first")
            with open(file, "rb") as fp:
                pdf = pypdf.PdfReader(fp)
                for i, page in enumerate(pdf.pages):
                    if i >= max_pages:
                        LOGGER.debug(f"ScannedPdfOCRReader reached max_pages={max_pages}, stopping")
                        break
                    txt = page.extract_text() or ""
                    if txt.strip():
                        texts.append(txt)
                        engines.append("pypdf")
                    else:
                        ocr_txt, ocr_engine = self._ocr_pdf_page(file, i, ocr_lang)
                        texts.append(ocr_txt)
                        engines.append(ocr_engine)
        except Exception as e:
            LOGGER.debug(f"ScannedPdfOCRReader pypdf failed: {e}")
            # If pypdf fails, OCR every page (up to max_pages)
            num_pages = min(self._count_pdf_pages(file), max_pages)
            for i in range(num_pages):
                ocr_txt, ocr_engine = self._ocr_pdf_page(file, i, ocr_lang)
                texts.append(ocr_txt)
                engines.append(ocr_engine)

        text_all = "\n\n".join(texts)
        engine_summary = ",".join(sorted(set(engines))) if engines else "unknown"
        metadata: Dict = {"source": "pdf", "file_name": file.name, "engine": engine_summary}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text_all, metadata=metadata)]

    def _count_pdf_pages(self, file: Path) -> int:
        """Count the number of pages in a PDF file.

        Args:
            file (Path): Path to the PDF file.

        Returns:
            int: The page count, or 0 if it cannot be determined.
        """
        try:
            import pypdf  # type: ignore
            with open(file, "rb") as fp:
                pdf = pypdf.PdfReader(fp)
                return len(pdf.pages)
        except Exception:
            return 0

    def _ocr_pdf_page(self, file: Path, page_index: int, ocr_lang: str = "ch") -> tuple:
        """Convert a single PDF page to an image and run OCR on it.

        Args:
            file (Path): Path to the PDF file.
            page_index (int): Zero-based index of the page to OCR.
            ocr_lang (str): Language hint forwarded to the OCR engine.

        Returns:
            tuple: The extracted (text, engine_name).

        Raises:
            ReaderDependencyError: If pdf2image is not installed.
        """
        try:
            from pdf2image import convert_from_path  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "pdf2image is required for scanned PDF OCR: "
                "`pip install pdf2image` (also install poppler).",
                reader_name=self.__class__.__name__,
            ) from e

        LOGGER.debug(f"ScannedPdfOCRReader converting page {page_index} to image")
        images = convert_from_path(str(file), first_page=page_index + 1, last_page=page_index + 1)
        if not images:
            return "", "none"

        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR  # type: ignore
            LOGGER.debug("ScannedPdfOCRReader using PaddleOCR")
            ocr = PaddleOCR(use_angle_cls=True, lang=ocr_lang)
            result = ocr.ocr(images[0], cls=True)
            lines = []
            for page in result:
                for line in page:
                    txt = line[1][0]
                    if txt:
                        lines.append(txt)
            return "\n".join(lines), "paddleocr"
        except Exception as e_paddle:
            LOGGER.debug(f"ScannedPdfOCRReader PaddleOCR failed: {e_paddle}")

        # Fallback to pytesseract
        try:
            import pytesseract  # type: ignore
            LOGGER.debug("ScannedPdfOCRReader using pytesseract")
            tess_lang = "chi_sim+eng" if ocr_lang in ("ch", "chi") else ocr_lang
            text = pytesseract.image_to_string(images[0], lang=tess_lang)
            return text, "pytesseract"
        except Exception as e_tess:
            LOGGER.debug(f"ScannedPdfOCRReader pytesseract failed: {e_tess}")

        # Fallback to easyocr
        try:
            import easyocr  # type: ignore
            LOGGER.debug("ScannedPdfOCRReader using easyocr")
            langs = ['ch_sim', 'en'] if ocr_lang in ("ch", "chi") else [ocr_lang]
            reader = easyocr.Reader(langs)
            result = reader.readtext(images[0], detail=0)
            return "\n".join(result), "easyocr"
        except Exception:
            return "", "unknown"
