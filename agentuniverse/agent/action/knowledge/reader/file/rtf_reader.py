# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/13 14:13
# @Author  : jiawei
# @FileName: rtf_reader.py

from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding

from striprtf.striprtf import rtf_to_text

class RtfReader(Reader):
    """RTF reader."""

    def _load_data(self, fpath: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        encoding = detect_file_encoding(fpath)

        with open(fpath, 'r', encoding=encoding) as file:
            metadata = {"file_name": Path(file.name).name}
            if ext_info is not None:
                metadata.update(ext_info)

            rtf_content = file.read()
            txt = rtf_to_text(rtf_content)

        return [Document(text=txt, metadata=metadata or {})]

# if __name__ == "__main__":
#     # 自测case
#     test_file = Path("/Users/jiawei/Desktop/文本说明.rtf")
#     reader = RtfReader()
#     docs = reader._load_data(test_file)
#     for doc in docs:
#         print("文件名:", doc.metadata.get("file_name"))
#         print("内容如下:\n", doc.text)