# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 14:30
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: reader.py
from abc import abstractmethod
from typing import List, Any, Optional

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class Reader(ComponentBase):
    """The basic class for the knowledge reader."""
    component_type: ComponentEnum = ComponentEnum.READER
    name: Optional[str] = None
    description: Optional[str] = None
    # Soft upper bound (bytes) on a single file a reader will fully ingest.
    # Readers that stream can ignore it; readers that materialise the whole
    # file into memory (TxtReader, JsonReader, ...) check the on-disk size
    # before reading so a maliciously large input cannot OOM the process.
    # Defaults to 256 MB; override per-reader via the component configer.
    max_read_bytes: int = 256 * 1024 * 1024

    def load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""
        return self._load_data(*args, **kwargs)

    @abstractmethod
    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""

    def _check_file_size(self, fpath: Any) -> None:
        """Raise ValueError if ``fpath`` exceeds ``max_read_bytes``.

        Called by readers that materialise the whole file. A no-op when the
        path does not expose a size (e.g. a stream), so callers that already
        stream do not need to change anything.
        """
        try:
            size = fpath.stat().st_size if hasattr(fpath, "stat") else None
            if size is None and isinstance(fpath, str):
                import os
                size = os.path.getsize(fpath)
        except OSError:
            return
        if size is not None and size > self.max_read_bytes:
            raise ValueError(
                f"File {fpath!r} is {size} bytes which exceeds the reader's "
                f"max_read_bytes ({self.max_read_bytes}); raise the limit on "
                f"the reader component or split the input.")

    def _initialize_by_component_configer(self,
                                         reader_configer: ComponentConfiger) \
            -> 'Reader':
        """Initialize the reader by the ComponentConfiger object.

        Args:
            reader_configer(ComponentConfiger): A configer contains reader
            basic info.
        Returns:
            Reader instance.
        """
        self.name = reader_configer.name
        self.description = reader_configer.description
        if hasattr(reader_configer, "max_read_bytes"):
            self.max_read_bytes = reader_configer.max_read_bytes
        return self
