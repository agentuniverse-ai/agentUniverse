# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List

# @Time    : 2024/7/31 16:19
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: recursive_character_text_splitter.py
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter as Splitter

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class RecursiveCharacterTextSplitter(DocProcessor):
    """Splits text recursively using a hierarchy of character separators."""
    chunk_size: int = 200
    chunk_overlap: int = 20
    separators: List[str] = ["\n\n", "\n", " ", ""]
    __splitter: Optional[Splitter] = None

    @property
    def splitter(self) -> Splitter:
        if not self.__splitter:
            self.__splitter = Splitter(separators=self.separators,
                                       chunk_size=self.chunk_size,
                                       chunk_overlap=self.chunk_overlap)
        return self.__splitter

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Split documents recursively using character separators.
        
        Args:
            origin_docs: List of documents to be split.
            query: Optional query object (not used in this processor).
            
        Returns:
            List of split document chunks.
        """
        lc_doc_list = self.splitter.split_documents(Document.as_langchain_list(
            origin_docs
        ))
        return Document.from_langchain_list(lc_doc_list)

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize splitter parameters from configuration.
        
        Args:
            doc_processor_configer: Configuration object containing splitter parameters.
            
        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "chunk_size"):
            self.chunk_size = doc_processor_configer.chunk_size
        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap
        if hasattr(doc_processor_configer, "separators"):
            self.separators = doc_processor_configer.separators
        return self







