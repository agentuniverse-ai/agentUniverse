# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/31 14:25
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: web_pdf_reader.py
from io import BytesIO
from typing import List
import requests

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class WebPdfReader(Reader):
    """The agentUniverse(aU) web pdf reader.

    The pdf file will be downloaded and then parsed by `pdfminer.six`.
    """

    def _load_data(self, web_pdf_url: str) -> List[Document]:
        if web_pdf_url is None:
            return []
        try:
            response = requests.get(web_pdf_url, timeout=20)
            response.raise_for_status()
        except requests.HTTPError as exc:
            status_code = getattr(exc.response, "status_code", None)
            status = f"HTTP {status_code}" if status_code is not None else "HTTP error"
            raise RuntimeError(f"Failed to fetch PDF from {web_pdf_url}: {status}") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch PDF from {web_pdf_url}: {exc}") from exc

        # download the pdf file and convert it into a memory file.
        pdf_memory_file = BytesIO(response.content)
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
