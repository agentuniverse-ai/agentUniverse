# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 15:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: token_text_splitter.py
from typing import List, Optional
from langchain.text_splitter import TokenTextSplitter as Splitter

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class TokenTextSplitter(DocProcessor):
    """Splits text into chunks based on token count rather than characters."""
    chunk_size: int = 200
    chunk_overlap: int = 20
    encoding_name: str = 'gpt2'
    model_name: Optional[str] = None
    __splitter: Optional[Splitter] = None

    @property
    def splitter(self) -> Splitter:
        if not self.__splitter:
            self.__splitter = Splitter(
            encoding_name=self.encoding_name,
            model_name=self.model_name,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        return self.__splitter

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Split documents based on token count using the specified tokenizer.
        
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
        if hasattr(doc_processor_configer, "encoding_name"):
            self.encoding_name = doc_processor_configer.encoding_name
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        return self
