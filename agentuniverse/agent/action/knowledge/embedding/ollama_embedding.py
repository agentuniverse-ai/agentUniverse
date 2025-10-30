# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025-10-05 21:40 PM
# @Author  : Cascade AI
# @Email   : cascade@windsurf.ai
# @FileName: ollama_embedding.py

from typing import Any, Optional, List
from pydantic import Field
import httpx
import asyncio

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class OllamaEmbedding(Embedding):
    """The Ollama embedding class."""

    ollama_base_url: Optional[str] = Field(
        default_factory=lambda: get_from_env("OLLAMA_BASE_URL") or "http://localhost:11434")
    
    ollama_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("OLLAMA_API_KEY"))

    embedding_model_name: Optional[str] = None
    embedding_dims: Optional[int] = None
    timeout: Optional[int] = Field(default=30)

    client: Any = None
    async_client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using Ollama API.
        Args:
            texts (List[str]): A list of input texts to be embedded.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()
        
        try:
            embeddings = []
            for text in texts:
                response = self.client.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model_name,
                        "prompt": text
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["embedding"])
            
            return embeddings

        except Exception as e:
            raise Exception(f"Failed to get embeddings: {e}")

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using Ollama API asynchronously.
        Args:
            texts (List[str]): A list of input texts to be embedded.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()

        try:
            async def get_single_embedding(text: str) -> List[float]:
                response = await self.async_client.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model_name,
                        "prompt": text
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result["embedding"]

            tasks = [get_single_embedding(text) for text in texts]
            embeddings = await asyncio.gather(*tasks)
            return embeddings

        except Exception as e:
            raise Exception(f"Failed to get embeddings: {e}")

    def as_langchain(self) -> Any:
        """
        Convert the OllamaEmbedding instance to a LangChain OllamaEmbeddings instance.
        """
        self._initialize_clients()

        try:
            from langchain_community.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(
                base_url=self.ollama_base_url,
                model=self.embedding_model_name
            )
        except ImportError:
            raise Exception("langchain_community is required for LangChain integration")

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """
        Initialize the embedding by the ComponentConfiger object.
        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.
        Returns:    
            Embedding: A OllamaEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "ollama_base_url"):
            self.ollama_base_url = embedding_configer.ollama_base_url
        if hasattr(embedding_configer, "ollama_api_key"):
            self.ollama_api_key = embedding_configer.ollama_api_key
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self

    def _initialize_clients(self) -> None:
        if not self.ollama_base_url:
            raise Exception("OLLAMA_BASE_URL is missing")
        if not self.embedding_model_name:
            raise Exception("embedding_model_name is missing")

        headers = {}
        if self.ollama_api_key:
            headers["Authorization"] = f"Bearer {self.ollama_api_key}"

        if self.client is None:
            self.client = httpx.Client(
                base_url=self.ollama_base_url,
                headers=headers,
                timeout=self.timeout
            )
        if self.async_client is None:
            self.async_client = httpx.AsyncClient(
                base_url=self.ollama_base_url,
                headers=headers,
                timeout=self.timeout
            )
