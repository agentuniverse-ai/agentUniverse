# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/23 10:00
# @Author  : agentuniverse
# @Email   : agentuniverse@example.com
# @FileName: minimax_embedding.py

from typing import List, Optional, Any

from langchain_community.embeddings.openai import OpenAIEmbeddings
from openai import OpenAI, AsyncOpenAI, BadRequestError
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class MiniMaxEmbedding(Embedding):
    """The MiniMax embedding class.

    MiniMax (https://api.minimaxi.com/) provides an OpenAI-compatible
    embeddings endpoint, so this class reuses the standard ``openai`` SDK
    while pointing ``base_url`` to the MiniMax endpoint.
    """

    openai_client_args: Optional[dict] = None
    minimax_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("MINIMAX_API_KEY"))
    minimax_api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("MINIMAX_API_BASE"))
    client: Any = None
    async_client: Any = None
    dimensions: Optional[int] = None

    def _build_client_args(self) -> dict:
        """Build the extra kwargs forwarded to the openai client.

        ``openai_client_args`` (if provided by the yaml) takes precedence,
        otherwise we fall back to the ``MINIMAX_API_BASE`` env var so the
        default MiniMax endpoint is used.
        """
        args = dict(self.openai_client_args or {})
        if "base_url" not in args and self.minimax_api_base:
            args["base_url"] = self.minimax_api_base
        return args

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get the MiniMax embeddings.

        Note:
            The ``embedding_model_name`` parameter must be provided
            (e.g. ``embo-01``). The ``dimensions`` parameter is optional.

        Args:
            texts (List[str]): A list of texts that need to be embedded.

        Returns:
            List[List[float]]: Each text gets a float list, and the result
            is a list of the results for each text.

        Raises:
            ValueError: If texts exceed the embedding model token limit or
            if some required parameters are missing.
        """
        self.client = OpenAI(api_key=self.minimax_api_key,
                             **self._build_client_args())
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        try:
            if self.dimensions:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                    dimensions=self.dimensions,
                )
            else:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                )

            data = response.data
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get the MiniMax embeddings.

        Args:
            texts (List[str]): A list of texts that need to be embedded.

        Returns:
            List[List[float]]: Each text gets a float list, and the result
            is a list of the results for each text.

        Raises:
            ValueError: If texts exceed the embedding model token limit or
            if some required parameters are missing.
        """
        self.async_client = AsyncOpenAI(api_key=self.minimax_api_key,
                                        **self._build_client_args())
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        try:
            if self.dimensions:
                response = await self.async_client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                    dimensions=self.dimensions,
                )
            else:
                response = await self.async_client.embeddings.create(
                    input=texts,
                    model=self.embedding_model_name,
                )
            data = response.data
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

    def as_langchain(self) -> OpenAIEmbeddings:
        """Convert the agentUniverse(aU) MiniMax embedding class to the
        langchain openai embedding class."""
        client = self.client.embeddings if self.client else None
        async_client = self.async_client.embeddings if self.async_client else None
        return OpenAIEmbeddings(openai_api_key=self.minimax_api_key,
                                client=client, async_client=async_client)

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) \
            -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer (ComponentConfiger): A configer contains
            embedding basic info.

        Returns:
            Embedding: An embedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "embedding_dims"):
            self.dimensions = embedding_configer.embedding_dims
        if hasattr(embedding_configer, "openai_client_args"):
            self.openai_client_args = embedding_configer.openai_client_args
        if hasattr(embedding_configer, "minimax_api_key"):
            self.minimax_api_key = embedding_configer.minimax_api_key
        if hasattr(embedding_configer, "minimax_api_base"):
            self.minimax_api_base = embedding_configer.minimax_api_base
        return self