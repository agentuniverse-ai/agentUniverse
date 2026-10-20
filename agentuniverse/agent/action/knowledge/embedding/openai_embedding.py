# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/19 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_embedding.py

from typing import List, Optional, Any
import asyncio

from langchain_community.embeddings.openai import OpenAIEmbeddings
from openai import OpenAI, AsyncOpenAI, BadRequestError
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class OpenAIEmbedding(Embedding):
    """OpenAI embeddings with reusable SDK clients.

    Injected clients remain caller-owned. Close lazily created clients with
    close()/aclose(); await aclose() on the async client's operating loop before
    moving the component to another loop. Concurrent shutdown is not supported.
    """

    openai_client_args: Optional[dict] = None
    openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    client: Any = None
    async_client: Any = None
    dimensions: Optional[int] = None
    _owned_client: Any = None
    _owned_async_client: Any = None
    _async_loop: Any = None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get the OpenAI embeddings.

        Note:
            The `embedding_model_name` parameter of the openai embedding class must be provided.
            The `dimensions` parameter of the openai embedding class is optional.

         Args:
             texts (List[str]): A list of texts that need to be embedded.

         Returns:
             List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.

         Raises:
             ValueError: If texts exceed the embedding model token limit or missing some required parameters.
         """
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        if self.client is None:
            self.client = OpenAI(api_key=self.openai_api_key, **self.openai_client_args or {})
            self._owned_client = self.client
        try:
            if self.dimensions:
                response = self.client.embeddings.create(input=texts, model=self.embedding_model_name,
                                                         dimensions=self.dimensions)
            else:
                response = self.client.embeddings.create(input=texts, model=self.embedding_model_name)

            # Extract the embedding data from the response
            data = response.data

            # Return the embeddings as a list of lists of floats
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get the OpenAI embeddings.

        Note:
            The `embedding_model_name` parameter of the openai embedding class must be provided.
            The `dimensions` parameter of the openai embedding class is optional.

         Args:
             texts (List[str]): A list of texts that need to be embedded.

         Returns:
             List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.
         Raises:
             ValueError: If texts exceed the embedding model token limit or missing some required parameters.
         """
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        loop = asyncio.get_running_loop()
        if self.async_client is not None and self.async_client is self._owned_async_client:
            if self._async_loop is not loop:
                raise RuntimeError("Close the embedding client on its original event loop before reusing it on another event loop")
        if self.async_client is None:
            self.async_client = AsyncOpenAI(api_key=self.openai_api_key, **self.openai_client_args or {})
            self._owned_async_client = self.async_client
            self._async_loop = loop
        try:
            if self.dimensions:
                response = await self.async_client.embeddings.create(input=texts, model=self.embedding_model_name,
                                                                     dimensions=self.dimensions)
            else:
                response = await self.async_client.embeddings.create(input=texts, model=self.embedding_model_name)
            # Extract the embedding data from the response
            data = response.data

            # Return the embeddings as a list of lists of floats
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

    def close(self) -> None:
        """Close only the synchronous client created by this component."""
        if self._owned_client is not None:
            client = self._owned_client
            client.close()
            if self.client is client:
                self.client = None
            self._owned_client = None

    async def aclose(self) -> None:
        """Close the owned async client on its original operating event loop."""
        if self._owned_async_client is not None:
            if self._async_loop is not asyncio.get_running_loop():
                raise RuntimeError("Close the embedding client on its original event loop")
            client = self._owned_async_client
            await client.close()
            if self.async_client is client:
                self.async_client = None
            self._owned_async_client = None
            self._async_loop = None

    def as_langchain(self) -> OpenAIEmbeddings:
        """Convert the agentUniverse(aU) openai embedding class to the langchain openai embedding class."""
        client = self.client.embeddings if self.client else None
        async_client = self.async_client.embeddings if self.async_client else None
        return OpenAIEmbeddings(openai_api_key=self.openai_api_key,
                                client=client, async_client=async_client)

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) \
            -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding
            basic info.
        Returns:
            Embedding: A embedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "embedding_dims"):
            self.dimensions = embedding_configer.embedding_dims
        if hasattr(embedding_configer, "openai_client_args"):
            self.openai_client_args = embedding_configer.openai_client_args
        return self
