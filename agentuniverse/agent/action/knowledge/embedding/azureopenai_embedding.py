# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2/16/25 9:50 PM
# @Author  : Xinyuan Xu
# @Email   : xuxinyuan2019@gmail.com
# @FileName: azureopenai_embedding.py

from typing import Any, Optional, List
from pydantic import Field

from openai import AzureOpenAI, AsyncAzureOpenAI

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class AzureOpenAIEmbedding(Embedding):
    """The Azure OpenAI embedding class."""

    azure_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY"))
    
    resource_name: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_RESOURCE_NAME"))

    azure_api_version: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_API_VERSION"))

    embedding_model_name: Optional[str] = None
    embedding_dims: Optional[int] = None

    client: Any = None
    async_client: Any = None


    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using Azure OpenAI API.
        Args:
            texts (List[str]): A list of input texts to be embedded.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()
        
        try:
            if self.embedding_dims is not None:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                    dimensions=self.embedding_dims
                )
            else:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name
                )
            return [item.embedding for item in response.data]

        except Exception as e:
            raise Exception(f"Failed to get embeddings: {e}")


    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using Azure OpenAI API asynchronously.
        Args:
            texts (List[str]): A list of input texts to be embedded.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()

        try:
            if self.embedding_dims is not None:
                response = await self.async_client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                    dimensions=self.embedding_dims
                )
            else:
                response = await self.async_client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name
                )
            return [item.embedding for item in response.data]

        except Exception as e:
            raise Exception(f"Failed to get embeddings: {e}")


    def as_langchain(self) -> Any:
        """
        Convert the AzureOpenAIEmbedding instance to a LangChainAzureOpenAIEmbedding instance.
        """
        self._initialize_clients()

        from langchain_community.embeddings.azure_openai import AzureOpenAIEmbeddings
        return AzureOpenAIEmbeddings(openai_api_key=self.azure_api_key, client=self.client.embeddings, async_client=self.async_client.embeddings, azure_endpoint=f"https://{self.resource_name}.openai.azure.com/")


    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """
        Initialize the embedding by the ComponentConfiger object.
        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.
        Returns:    
            Embedding: A AzureOpenAIEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "azure_api_key"):
            self.azure_api_key = embedding_configer.azure_api_key
        if hasattr(embedding_configer, "resource_name"):
            self.resource_name = embedding_configer.resource_name
        return self


    def _initialize_clients(self) -> None:
        if not self.azure_api_key:
            raise Exception("AZURE_OPENAI_API_KEY is missing")
        if not self.resource_name:
            raise Exception("AZURE_OPENAI_RESOURCE_NAME is missing")
        if not self.azure_api_version:
            raise Exception("AZURE_API_VERSION is missing")

        if self.client is None:
            self.client = AzureOpenAI(
                api_key=self.azure_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=f"https://{self.resource_name}.openai.azure.com"
            )
        if self.async_client is None:
            self.async_client = AsyncAzureOpenAI(
                api_key=self.azure_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=f"https://{self.resource_name}.openai.azure.com"
            )