# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/23 14:00
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: doc_processor.py

from abc import abstractmethod
from typing import List, Optional

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class DocProcessor(ComponentBase):
    """The basic class for doc processor.
    
    DocProcessor is an abstract base class that defines the interface for document 
    processing components in the agentUniverse framework. Document processors can 
    transform, filter, or enhance documents before they are used by agents.
    
    Attributes:
        component_type: Enum value identifying this as a document processor component.
        name: Optional name identifier for the processor.
        description: Optional description of the processor's functionality.
    """

    component_type: ComponentEnum = ComponentEnum.DOC_PROCESSOR
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Process input documents，return should also be a document list."""
        return self._process_docs(origin_docs, query)

    @abstractmethod
    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> \
            List[Document]:
        """Process input documents，return should also be a document list.
        
        This is the core implementation method that subclasses must override to 
        provide specific document processing logic. The method should transform 
        the input documents according to the processor's purpose and optionally 
        use the query for context-aware processing.
        
        Args:
            origin_docs: List of documents to be processed.
            query: Optional query object that may influence the processing.
            
        Returns:
            List[Document]: Processed documents.
        """
        pass

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) \
            -> 'DocProcessor':
        """Initialize the DocProcessor by the ComponentConfiger object.

        Args:
            doc_processor_configer(ComponentConfiger): A configer contains DocProcessor
            basic info.
        Returns:
            DocProcessor: A DocProcessor instance.
        """
        self.name = doc_processor_configer.name
        self.description = doc_processor_configer.description
        return self
