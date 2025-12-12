#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/9 22:59
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: langchain_bridge_reader.py

import importlib
from typing import List, Any, Dict, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class LangchainBridgeReader(Reader):
    """Generic reader that wraps langchain_community.document_loaders.
    
    This reader can dynamically load and use any loader from langchain_community.document_loaders
    based on configuration.
    
    Attributes:
        loader_class (str): The class name of the langchain loader (e.g., "TextLoader")
        loader_module (str): The module path of the loader (e.g., "langchain_community.document_loaders.text")
        loader_params (Dict): Parameters to pass to the loader constructor
    """
    
    loader_class: Optional[str] = None
    loader_module: Optional[str] = None
    loader_params: Optional[Dict] = None

    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data using the configured langchain loader.
        
        Args:
            *args: Positional arguments to pass to the loader
            **kwargs: Keyword arguments to pass to the loader
            
        Returns:
            List of Document objects in agentUniverse format
        """
        if not self.loader_class or not self.loader_module:
            raise ValueError("LangchainReader requires loader_class and loader_module configuration")

        try:
            # Dynamically import the loader class
            module = importlib.import_module(self.loader_module)
            loader_cls = getattr(module, self.loader_class)

            # Merge constructor parameters
            constructor_params = self.loader_params.copy() if self.loader_params else {}
            constructor_params.update(kwargs)

            # Create loader instance
            loader = loader_cls(**constructor_params)

            # Load documents using langchain loader
            langchain_docs = loader.load()

            # Convert to agentUniverse Document format
            return Document.from_langchain_list(langchain_docs)

        except ImportError as e:
            raise ImportError(f"Failed to import loader {self.loader_class} from {self.loader_module}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading documents with {self.loader_class}: {e}")

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> 'Reader':
        """Initialize the reader by the ComponentConfiger object.

        Args:
            reader_configer(ComponentConfiger): A configer contains reader
            basic info.
        Returns:
            LangchainBridgeReader: A reader instance.
        """
        super()._initialize_by_component_configer(reader_configer)
        if hasattr(reader_configer, "loader_class"):
            self.loader_class = reader_configer.loader_class
        if hasattr(reader_configer, "loader_module"):
            self.loader_module = reader_configer.loader_module
        if hasattr(reader_configer, "loader_params"):
            self.loader_params = reader_configer.loader_params
        return self