# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 14:21
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: pdf_reader.py
import logging
from pathlib import Path
from typing import List, Optional, Dict, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class PdfReader(Reader):
    """PDF reader."""

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the pdf file.

        Note:
            `pypdf` is required to read PDF files: `pip install pypdf`
        """
        try:
            import pypdf
        except ImportError:
            raise ReaderDependencyError(
                "pypdf is required to read PDF files",
                reader_name="PdfReader",
                dependency="pypdf",
                install_hint="pip install pypdf",
            )
        if isinstance(file, str):
            file = Path(file)
        if not file.exists():
            raise ReaderLoadError(
                f"PDF file not found: {file}",
                reader_name="PdfReader",
                source=str(file),
            )

        logger.info("PdfReader start load file=%s", file)
        try:
            with open(file, "rb") as fp:
                # Create a PDF object
                pdf = pypdf.PdfReader(fp)

                # Get the number of pages in the PDF document
                num_pages = len(pdf.pages)

                # Iterate over every page
                docs = []
                for page in range(num_pages):
                    # Extract the text from the page
                    page_text = pdf.pages[page].extract_text()
                    page_label = pdf.page_labels[page]

                    metadata = {"page_label": page_label, "file_name": file.name}
                    if ext_info is not None:
                        metadata.update(ext_info)

                    docs.append(Document(text=page_text, metadata=metadata))
                logger.info("PdfReader extracted %d pages from %s", num_pages, file.name)
                return docs
        except (ReaderLoadError, ReaderDependencyError):
            raise
        except Exception as e:
            raise ReaderParseError(
                f"Failed to read PDF file: {e}",
                reader_name="PdfReader",
                source=str(file),
            ) from e
