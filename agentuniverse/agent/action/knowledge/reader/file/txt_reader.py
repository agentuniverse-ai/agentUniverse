from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class LineTxtReader(Reader):
    def _load_data(self, fpath: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        dlist = []

        with open(fpath, "r", encoding="utf-8") as file:
            metadata = {"file_name": file.name}
            if ext_info is not None:
                metadata.update(ext_info)

            for line in file:
                dlist.append(Document(text=line, metadata=metadata or {}))

        return dlist


class TxtReader(Reader):
    """Txt reader."""

    def _load_data(self, fpath: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        with open(fpath, "r", encoding="utf-8") as file:
            metadata = {"file_name": file.name}
            if ext_info is not None:
                metadata.update(ext_info)

            txt = file.read()

        return [Document(text=txt, metadata=metadata or {})]
