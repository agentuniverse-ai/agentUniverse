# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/31 14:25
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: web_pdf_reader.py
from io import BytesIO
from typing import ClassVar, List
import requests

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class WebPdfReader(Reader):
    """The agentUniverse(aU) web pdf reader.

    The pdf file will be downloaded and then parsed by `pdfminer.six`.
    """

    MAX_PDF_SIZE_BYTES: ClassVar[int] = 50 * 1024 * 1024
    DOWNLOAD_CHUNK_SIZE_BYTES: ClassVar[int] = 64 * 1024

    def _load_data(self, web_pdf_url: str) -> List[Document]:
        if web_pdf_url is None:
            return []

        pdf_memory_file = self._download_pdf(web_pdf_url)
        try:
            from pdfminer.high_level import extract_text_to_fp
        except ImportError:
            raise ImportError(
                "pdfminer.six is required to read PDF files: `pip install pdfminer.six`"
            )
        # parse the pdf file and get the text content.
        with BytesIO() as output_string:
            extract_text_to_fp(pdf_memory_file, output_string, output_type='text', codec='utf-8')
            text = output_string.getvalue().decode('utf-8')
            return [Document(text=text, metadata={"source": web_pdf_url})]

    def _download_pdf(self, web_pdf_url: str) -> BytesIO:
        """Download a PDF while enforcing a maximum in-memory size."""
        response = None
        try:
            response = requests.get(web_pdf_url, timeout=20, stream=True)
            response.raise_for_status()

            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                try:
                    declared_size = int(content_length)
                except (TypeError, ValueError):
                    declared_size = None
                if declared_size is not None and declared_size > self.MAX_PDF_SIZE_BYTES:
                    raise RuntimeError(
                        f"PDF from {web_pdf_url} exceeds the maximum download size "
                        f"of {self.MAX_PDF_SIZE_BYTES} bytes"
                    )

            pdf_memory_file = BytesIO()
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=self.DOWNLOAD_CHUNK_SIZE_BYTES):
                if not chunk:
                    continue
                downloaded_size += len(chunk)
                if downloaded_size > self.MAX_PDF_SIZE_BYTES:
                    raise RuntimeError(
                        f"PDF from {web_pdf_url} exceeds the maximum download size "
                        f"of {self.MAX_PDF_SIZE_BYTES} bytes"
                    )
                pdf_memory_file.write(chunk)
            pdf_memory_file.seek(0)
            return pdf_memory_file
        except requests.HTTPError as exc:
            status_code = getattr(exc.response, "status_code", None)
            status = f"HTTP {status_code}" if status_code is not None else "HTTP error"
            raise RuntimeError(f"Failed to fetch PDF from {web_pdf_url}: {status}") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch PDF from {web_pdf_url}: {exc}") from exc
        finally:
            if response is not None:
                response.close()
