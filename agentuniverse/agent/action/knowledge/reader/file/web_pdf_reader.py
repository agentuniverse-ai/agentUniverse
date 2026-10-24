# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/31 14:25
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: web_pdf_reader.py
from io import BytesIO

import requests

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class WebPdfReader(Reader):
    """The agentUniverse(aU) web pdf reader.

    The pdf file will be downloaded and then parsed by `pdfminer.six`.
    """

    max_file_size: int = 64 * 1024 * 1024
    stream_chunk_size: int = 1024 * 1024

    def _load_data(self, web_pdf_url: str) -> list[Document]:
        if web_pdf_url is None:
            return []

        self._validate_limits()
        try:
            from pdfminer.high_level import extract_text_to_fp
        except ImportError as exc:
            message = "pdfminer.six is required to read PDF files: `pip install pdfminer.six`"
            raise ImportError(message) from exc

        pdf_memory_file = self._download_pdf(web_pdf_url)
        # parse the pdf file and get the text content.
        with pdf_memory_file, BytesIO() as output_string:
            extract_text_to_fp(pdf_memory_file, output_string, output_type="text", codec="utf-8")
            text = output_string.getvalue().decode("utf-8")
            return [Document(text=text, metadata={"source": web_pdf_url})]

    def _validate_limits(self) -> None:
        if self.max_file_size <= 0:
            message = "max_file_size must be greater than zero"
            raise ValueError(message)
        if self.stream_chunk_size <= 0:
            message = "stream_chunk_size must be greater than zero"
            raise ValueError(message)

    def _download_pdf(self, web_pdf_url: str) -> BytesIO:
        response = None
        try:
            response = requests.get(web_pdf_url, timeout=20, stream=True)
            response.raise_for_status()
            self._validate_content_length(response, web_pdf_url)
            return self._read_response(response, web_pdf_url)
        except requests.HTTPError as exc:
            status_code = getattr(exc.response, "status_code", None)
            status = f"HTTP {status_code}" if status_code is not None else "HTTP error"
            message = f"Failed to fetch PDF from {web_pdf_url}: {status}"
            raise RuntimeError(message) from exc
        except requests.RequestException as exc:
            message = f"Failed to fetch PDF from {web_pdf_url}: {exc}"
            raise RuntimeError(message) from exc
        finally:
            if response is not None:
                response.close()

    def _validate_content_length(self, response: requests.Response, web_pdf_url: str) -> None:
        content_length = response.headers.get("Content-Length")
        if not content_length:
            return
        try:
            declared_size = int(content_length)
        except (TypeError, ValueError):
            return
        if declared_size > self.max_file_size:
            self._raise_oversized(web_pdf_url)

    def _read_response(self, response: requests.Response, web_pdf_url: str) -> BytesIO:
        pdf_memory_file = BytesIO()
        downloaded_size = 0
        try:
            for chunk in response.iter_content(chunk_size=self.stream_chunk_size):
                if not chunk:
                    continue
                downloaded_size += len(chunk)
                if downloaded_size > self.max_file_size:
                    self._raise_oversized(web_pdf_url)
                pdf_memory_file.write(chunk)
            pdf_memory_file.seek(0)
            return pdf_memory_file
        except Exception:
            pdf_memory_file.close()
            raise

    def _raise_oversized(self, web_pdf_url: str) -> None:
        message = f"PDF from {web_pdf_url} exceeds max_file_size ({self.max_file_size} bytes)"
        raise ValueError(message)
