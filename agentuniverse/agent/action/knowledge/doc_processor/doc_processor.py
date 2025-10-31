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
    """Document processor base class for agentUniverse framework.
    
    DocProcessor is an abstract base class that defines the interface for document 
    processing components in the agentUniverse framework. Document processors can 
    transform, filter, or enhance documents before they are used by agents.
    
    This class provides a standardized way to process documents in the knowledge
    management pipeline, allowing for custom document transformations, filtering,
    and enhancement operations.
    
    Attributes:
        component_type (ComponentEnum): Enum value identifying this as a document 
            processor component. Always set to ComponentEnum.DOC_PROCESSOR.
        name (Optional[str]): Optional name identifier for the processor.
        description (Optional[str]): Optional description of the processor's 
            functionality.
    
    Example:
        >>> class TextCleaner(DocProcessor):
        ...     def _process_docs(self, docs, query=None):
        ...         return [Document(text=doc.text.strip()) for doc in docs]
        >>> 
        >>> processor = TextCleaner()
        >>> cleaned_docs = processor.process_docs(original_docs)
    
    Note:
        Subclasses must implement the `_process_docs` method to provide specific
        document processing logic.
    """

    component_type: ComponentEnum = ComponentEnum.DOC_PROCESSOR
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Process input documents and return processed document list.
        
        This is the main entry point for document processing. It delegates the
        actual processing logic to the `_process_docs` method which must be
        implemented by subclasses.
        
        Args:
            origin_docs (List[Document]): List of documents to be processed.
            query (Query, optional): Optional query object that may influence 
                the processing. Can be used for context-aware processing.
        
        Returns:
            List[Document]: List of processed documents. The number of documents
                may differ from the input list depending on the processing logic.
        
        Example:
            >>> processor = MyDocProcessor()
            >>> processed_docs = processor.process_docs(original_docs, query)
            >>> print(f"Processed {len(processed_docs)} documents")
        """
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

        This method configures the DocProcessor instance using the provided
        configuration object. It sets the name and description attributes
        from the configuration.

        Args:
            doc_processor_configer (ComponentConfiger): A configuration object 
                containing DocProcessor basic information including name and 
                description.
        
        Returns:
            DocProcessor: The configured DocProcessor instance (self).
        
        Example:
            >>> config = ComponentConfiger()
            >>> config.name = "text_cleaner"
            >>> config.description = "Cleans text documents"
            >>> processor = MyDocProcessor()
            >>> configured_processor = processor._initialize_by_component_configer(config)
        """
        self.name = doc_processor_configer.name
        self.description = doc_processor_configer.description
        return self
