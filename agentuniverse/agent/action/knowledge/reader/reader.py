# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 14:30
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: reader.py
import asyncio
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

    def load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""
        return self._load_data(*args, **kwargs)

    async def async_load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Async version of :meth:`load_data`.

        Default implementation delegates to the synchronous method via
        ``asyncio.to_thread``.  Subclasses with native async I/O should
        override this method.
        """
        return await asyncio.to_thread(self._load_data, *args, **kwargs)

    @abstractmethod
    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""

    def _initialize_by_component_configer(self,
                                         reader_configer: ComponentConfiger) \
            -> 'Reader':
        """Initialize the reader by the ComponentConfiger object.

        Args:
            reader_configer(ComponentConfiger): A configer contains reader
            basic info.
        Returns:
            Reader: A reader instance.
        """
        self.name = reader_configer.name
        self.description = reader_configer.description
        return self
