#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 13:55
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: memory_extract_configer.py

from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class MemoryExtractConfiger(ComponentConfiger):
    """The MemoryExtractConfiger class, which is used to load and manage the MemoryExtract configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the MemoryExtractConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__enabled: Optional[bool] = None
        self.__top_k: Optional[int] = None
        self.__max_workers: Optional[int] = None
        self.__memory_storage: Optional[str] = None
        self.__extract_prompt_version: Optional[str] = None
        self.__operation_prompt_version: Optional[str] = None
        self.__embedding_model: Optional[str] = None
        self.__extraction_llm: Optional[str] = None
        self.__operation_llm: Optional[str] = None
        self.__similarity_threshold: Optional[float] = None
        self.__max_memories_per_user: Optional[int] = None
        self.__max_memories_per_agent: Optional[int] = None

    @property
    def name(self) -> Optional[str]:
        """Return the name of the MemoryExtract."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the MemoryExtract."""
        return self.__description

    @property
    def enabled(self) -> Optional[bool]:
        """Return whether the MemoryExtract is enabled."""
        return self.__enabled

    @property
    def top_k(self) -> Optional[int]:
        """Return the top_k value for search."""
        return self.__top_k

    @property
    def max_workers(self) -> Optional[int]:
        """Return the max workers for thread pool."""
        return self.__max_workers

    @property
    def memory_storage(self) -> Optional[str]:
        """Return the memory storage name."""
        return self.__memory_storage

    @property
    def extract_prompt_version(self) -> Optional[str]:
        """Return the extract prompt version."""
        return self.__extract_prompt_version

    @property
    def operation_prompt_version(self) -> Optional[str]:
        """Return the operation prompt version."""
        return self.__operation_prompt_version

    @property
    def embedding_model(self) -> Optional[str]:
        """Return the embedding model name."""
        return self.__embedding_model

    @property
    def extraction_llm(self) -> Optional[str]:
        """Return the extraction LLM name."""
        return self.__extraction_llm

    @property
    def operation_llm(self) -> Optional[str]:
        """Return the operation LLM name."""
        return self.__operation_llm

    @property
    def similarity_threshold(self) -> Optional[float]:
        """Return the similarity threshold."""
        return self.__similarity_threshold

    @property
    def max_memories_per_user(self) -> Optional[int]:
        """Return the max memories per user."""
        return self.__max_memories_per_user

    @property
    def max_memories_per_agent(self) -> Optional[int]:
        """Return the max memories per agent."""
        return self.__max_memories_per_agent

    def load(self) -> 'MemoryExtractConfiger':
        """Load the configuration by the Configer object.
        
        Returns:
            MemoryExtractConfiger: The MemoryExtractConfiger object.
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> 'MemoryExtractConfiger':
        """Load the configuration by the Configer object.
        
        Args:
            configer (Configer): The Configer object.
            
        Returns:
            MemoryExtractConfiger: The MemoryExtractConfiger object.
            
        Raises:
            Exception: If configuration parsing fails.
        """
        super().load_by_configer(configer)

        try:
            configer_value: dict = configer.value
            self.__name = configer_value.get('name')
            self.__description = configer_value.get('description')
            self.__enabled = configer_value.get('enabled')
            self.__top_k = configer_value.get('top_k')
            self.__max_workers = configer_value.get('max_workers')
            self.__memory_storage = configer_value.get('memory_storage')
            self.__extract_prompt_version = configer_value.get('extract_prompt_version')
            self.__operation_prompt_version = configer_value.get('operation_prompt_version')
            self.__embedding_model = configer_value.get('embedding_model')
            self.__extraction_llm = configer_value.get('extraction_llm')
            self.__operation_llm = configer_value.get('operation_llm')
            self.__similarity_threshold = configer_value.get('similarity_threshold')
            self.__max_memories_per_user = configer_value.get('max_memories_per_user')
            self.__max_memories_per_agent = configer_value.get('max_memories_per_agent')
        except Exception as e:
            raise Exception(f"Failed to parse the MemoryExtract configuration from configer: {e}")
        return self
