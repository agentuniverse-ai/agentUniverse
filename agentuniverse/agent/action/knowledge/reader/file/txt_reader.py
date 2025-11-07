from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


class LineTxtReader(Reader):

    def _load_data(self, fpath: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        dlist: List[Document] = []
        encoding = detect_file_encoding(fpath)

        with open(fpath, 'r', encoding=encoding) as file:
            metadata = {"file_name": Path(file.name).name}
            if ext_info is not None:
                metadata.update(ext_info)

            for line in file:
                dlist.append(Document(text=line, metadata=metadata or {}))

        return dlist


class TxtReader(Reader):
    """Txt reader."""

    def _load_data(self, fpath: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        encoding = detect_file_encoding(fpath)

        with open(fpath, 'r', encoding=encoding) as file:
            metadata = {"file_name": Path(file.name).name}
            if ext_info is not None:
                metadata.update(ext_info)

            txt = file.read()

        return [Document(text=txt, metadata=metadata or {})]
