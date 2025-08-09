# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 14:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: character_text_splitter.py
from typing import List, Optional
from langchain.text_splitter import CharacterTextSplitter as Splitter

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class CharacterTextSplitter(DocProcessor):
    """Character-based text splitter for document processing.
    
    This class splits documents into smaller chunks based on character separators,
    with configurable chunk size and overlap parameters.
    
    Attributes:
        chunk_size: The size of each text chunk.
        chunk_overlap: The number of characters to overlap between chunks.
        separator: The character sequence used to split text.
        splitter: The underlying LangChain text splitter instance.
    """
    chunk_size: int = 200
    chunk_overlap: int = 20
    separator: str = "/n/n"
    __splitter: Optional[Splitter] = None


    @property
    def splitter(self) -> Splitter:
        if not self.__splitter:
            self.__splitter = Splitter(separator=self.separator,
                                 chunk_size=self.chunk_size,
                                 chunk_overlap=self.chunk_overlap)
        return self.__splitter


    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Process documents by splitting them into smaller chunks.
        
        Args:
            origin_docs: List of original documents to be processed.
            query: Optional query object that may influence the processing.
            
        Returns:
            List[Document]: List of processed document chunks.
        """
        lc_doc_list = self.splitter.split_documents(Document.as_langchain_list(
            origin_docs
        ))
        return Document.from_langchain_list(lc_doc_list)

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize the splitter using configuration from a ComponentConfiger.
        
        Args:
            doc_processor_configer: Configuration object containing splitter parameters.
            
        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "chunk_size"):
            self.chunk_size = doc_processor_configer.chunk_size
        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap
        if hasattr(doc_processor_configer, "separator"):
            self.separator = doc_processor_configer.separator
        return self
