# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 17:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_configer.py
from typing import Optional, List

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class MemoryConfiger(ComponentConfiger):
    """The MemoryConfiger class, which is used to load and manage the Memory configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the MemoryConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__type: Optional[str] = None
        self.__memory_key: Optional[str] = None
        self.__max_tokens: Optional[int] = None
        self.__memory_compressor: Optional[str] = None
        self.__memory_storages: Optional[List[str]] = None
        self.__memory_retrieval_storage: Optional[str] = None
        self.__memory_summarize_agent: Optional[str] = None

    @property
    def name(self) -> Optional[str]:
        """Return the name of the Memory."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the Memory."""
        return self.__description

    @property
    def type(self) -> Optional[str]:
        """Return the type of the Memory."""
        return self.__type

    @property
    def memory_key(self) -> Optional[str]:
        """Return the key of the Memory."""
        return self.__memory_key

    @property
    def max_tokens(self) -> Optional[int]:
        """Return memory tokens of the Memory."""
        return self.__max_tokens

    @property
    def memory_compressor(self) -> Optional[str]:
        """Return the compressor of the Memory."""
        return self.__memory_compressor

    @property
    def memory_storages(self) -> Optional[List[str]]:
        """Return the storages of the Memory."""
        return self.__memory_storages

    @property
    def memory_retrieval_storage(self) -> Optional[str]:
        """Return the retrieval storage of the Memory."""
        return self.__memory_retrieval_storage

    @property
    def memory_summarize_agent(self) -> Optional[str]:
        """Return the summarize agent of the Memory."""
        return self.__memory_summarize_agent

    def load(self) -> "MemoryConfiger":
        """Load the configuration by the Configer object.
        Returns:
            MemoryConfiger: the MemoryConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "MemoryConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            MemoryConfiger: the MemoryConfiger object
        """
        super().load_by_configer(configer)

        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            self.__type = configer.value.get("type")
            self.__memory_key = configer.value.get("memory_key")
            self.__max_tokens = configer.value.get("max_tokens")
            self.__memory_compressor = configer.value.get("memory_compressor")
            self.__memory_storages = configer.value.get("memory_storages")
            self.__memory_retrieval_storage = configer.value.get("memory_retrieval_storage")
            self.__memory_summarize_agent = configer.value.get("memory_summarize_agent")
        except Exception as e:
            raise Exception(f"Failed to parse the Memory configuration: {e}")
        return self
