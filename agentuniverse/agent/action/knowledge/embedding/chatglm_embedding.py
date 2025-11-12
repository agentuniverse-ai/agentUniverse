# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 11/5/25 19:50
# @Author  : Ke Jiang
# @Email   : yitong.jk@antgroup.com
# @FileName: chatglm_embedding.py

import logging
from typing import Any, Optional, List, Dict
from pydantic import Field
from zai import ZhipuAiClient
from zai.core import APIStatusError, APITimeoutError
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


class ChatGLMEmbeddingError(Exception):
    """Custom exception class for ChatGLM embedding errors."""
    pass


class ChatGLMEmbedding(Embedding):
    """The ChatGLM embedding class."""

    chatglm_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("chatglm_api_key"))

    embedding_model_name: Optional[str] = None
    embedding_dims: Optional[int] = 1024

    client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using ChatGLM API.
        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Additional keyword arguments.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            ChatGLMEmbeddingError: If the API call fails or if required configuration is missing.
        """
        return self._get_embeddings(texts, **kwargs)

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using ChatGLM API asynchronously.
        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Additional keyword arguments.
        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.
        Raises:
            ChatGLMEmbeddingError: If the API call fails or if required configuration is missing.
        """
        return await self._async_get_embeddings(texts, **kwargs)

    def _get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using ChatGLM API.

        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Additional keyword arguments.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            ChatGLMEmbeddingError: If the API call fails or if required configuration is missing.
            ValueError: If texts is empty or embedding_model_name is not set.
        """
        if not texts:
            raise ValueError("Input texts cannot be empty")
        
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name must be set before making API calls")
        
        self._initialize_clients()
        params = self._build_api_params(texts, **kwargs)

        try:
            response = self.client.embeddings.create(**params)
            return [item.embedding for item in response.data]

        except APIStatusError as err:
            error_msg = f"ChatGLM API status error: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err
        except APITimeoutError as err:
            error_msg = f"ChatGLM API request timeout: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err
        except Exception as err:
            error_msg = f"ChatGLM API unexpected error: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err

    async def _async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using ChatGLM API asynchronously.

        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Additional keyword arguments.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            ChatGLMEmbeddingError: If the API call fails or if required configuration is missing.
            ValueError: If texts is empty or embedding_model_name is not set.
        """
        if not texts:
            raise ValueError("Input texts cannot be empty")
        
        if not self.embedding_model_name:
            raise ValueError("embedding_model_name must be set before making API calls")
        
        self._initialize_clients()
        params = self._build_api_params(texts, **kwargs)

        try:
            response = await self.client.embeddings.create(**params)
            return [item.embedding for item in response.data]

        except APIStatusError as err:
            error_msg = f"ChatGLM API status error: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err
        except APITimeoutError as err:
            error_msg = f"ChatGLM API request timeout: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err
        except Exception as err:
            error_msg = f"ChatGLM API unexpected error: {err}"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg) from err

    def _build_api_params(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """
        Build API parameters for the ChatGLM embedding request.

        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Any]: API parameters.

        Raises:
            ValueError: If texts is empty.
        """
        if not texts:
            raise ValueError("Input texts cannot be empty")
            
        params: Dict[str, Any] = {
            "input": texts,
            "model": self.embedding_model_name
        }

        # Add dimensions parameter if embedding_dims is specified
        if self.embedding_dims is not None:
            params["dimensions"] = self.embedding_dims

        # Add other possible parameters
        for key, value in kwargs.items():
            if key not in params:  # Avoid overriding required parameters
                params[key] = value

        return params

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """
        Initialize the embedding by the ComponentConfiger object.
        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.
        Returns:
            Embedding: A ChatGLMEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "chatglm_api_key"):
            self.chatglm_api_key = embedding_configer.chatglm_api_key
        if hasattr(embedding_configer, "embedding_dims"):
            self.embedding_dims = embedding_configer.embedding_dims
        return self

    def _initialize_clients(self) -> None:
        """Initialize ChatGLM client.
        
        Raises:
            ChatGLMEmbeddingError: If chatglm_api_key is not set.
        """
        if not self.chatglm_api_key:
            error_msg = "chatglm_api_key is missing"
            logger.error(error_msg)
            raise ChatGLMEmbeddingError(error_msg)

        if self.client is None:
            self.client = ZhipuAiClient(api_key=self.chatglm_api_key)
            logger.debug("ChatGLM client initialized successfully")