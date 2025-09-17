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
        response = requests.get(web_pdf_url)
        if response.status_code == 200:
            # download the pdf file and convert it into a memory file.
            pdf_memory_file = BytesIO(response.content)
            try:
                from pdfminer.high_level import extract_text_to_fp
            except ImportError:
                raise ImportError("pdfminer.six is required to read PDF files: `pip install pdfminer.six`")
            # parse the pdf file and get the text content.
            with BytesIO() as output_string:
                extract_text_to_fp(pdf_memory_file, output_string, output_type="text", codec="utf-8")
                text = output_string.getvalue().decode("utf-8")
                return [Document(text=text, metadata={"source": web_pdf_url})]
