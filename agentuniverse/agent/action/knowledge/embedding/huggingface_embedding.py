#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-11-29
# @Author  : guangxu
# @Email   : guangxu.sgx@antgroup.com
# @FileName: huggingface_embedding.py

from typing import List, Optional, Any
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class HuggingFaceEmbedding(Embedding):
    """The Hugging Face embedding class using langchain-huggingface integration."""
    
    model_name: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
    )
    cache_folder: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_CACHE_FOLDER")
    )
    
    _langchain_embeddings: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Get the HuggingFace embeddings.
        
        Args:
            texts (List[str]): A list of texts that need to be embedded.
            
        Returns:
            List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.
        """
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError("HuggingFace Embeddings is required. Install with: pip install langchain-huggingface")
        
        if self._langchain_embeddings is None:
            model_kwargs = {}
            if self.cache_folder:
                model_kwargs["cache_folder"] = self.cache_folder
            
            self._langchain_embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                **model_kwargs
            )
        
        return [list(embedding) for embedding in self._langchain_embeddings.embed_documents(texts)]

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get the HuggingFace embeddings.
        
        Args:
            texts (List[str]): A list of texts that need to be embedded.
            
        Returns:
            List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.
        """
        # Import langchain_huggingface to ensure they're available
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError("HuggingFace Embeddings is required. Install with: pip install langchain-huggingface")
        
        # For API-based embeddings, we can delegate to the sync version
        # Since HuggingFace local models are compute-heavy, async doesn't provide benefit
        # However, for hub models that download remotely, there might be async utility
        # For now, just delegate to sync version
        return self.get_embeddings(texts, **kwargs)

    def as_langchain(self) -> Any:
        """Convert the agentUniverse(aU) huggingface embedding class to the langchain huggingface embedding class."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name=self.model_name)
        except ImportError:
            raise ImportError("HuggingFace Embeddings is required. Install with: pip install langchain-huggingface")
    
    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.
        
        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding
            basic info.
        Returns:
            Embedding: A embedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "model_name"):
            self.model_name = embedding_configer.model_name
        if hasattr(embedding_configer, "cache_folder"):
            self.cache_folder = embedding_configer.cache_folder
        return self