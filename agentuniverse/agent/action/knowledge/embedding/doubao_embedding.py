# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/15 23:35
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: doubao_embedding.py

from typing import Any, List, Optional
from pydantic import Field
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

SUPPORTED_DIMENSIONS = {512, 1024, 2048}


class DoubaoEmbedding(Embedding):
    """The Doubao embedding class using Volcengine Ark Runtime."""

    ark_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("ARK_API_KEY"))
    endpoint_id: Optional[str] = Field(default_factory=lambda: get_from_env("ARK_ENDPOINT_ID"))
    client: Optional[Any] = None
    embedding_dims: Optional[int] = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts using Doubao API.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        if not self.client:
            if not self.ark_api_key:
                raise ValueError("ARK_API_KEY is required but not set")
            try:
                from volcenginesdkarkruntime import Ark
            except ImportError:
                raise ImportError("Ark is required. Install with: pip install volcengine-python-sdk[ark]")
            self.client = Ark(api_key=self.ark_api_key)
        if not self.endpoint_id:
            raise ValueError("endpoint_id is required but not set")

        def sliced_norm_l2(vec: List[float]) -> List[float]:
            if self.embedding_dims not in SUPPORTED_DIMENSIONS:
                raise ValueError(
                    f"Unsupported embedding dimension: {self.embedding_dims}. "
                    f"Supported dimensions are: {', '.join(SUPPORTED_DIMENSIONS)}"
                )
            import numpy as np

            norm = float(np.linalg.norm(vec[: self.embedding_dims]))
            return [v / norm for v in vec[: self.embedding_dims]]

        try:
            response = self.client.embeddings.create(model=self.endpoint_id, input=texts)
            if self.embedding_dims is None:
                return [data.embedding for data in response.data]
            return [sliced_norm_l2(data.embedding) for data in response.data]
        except Exception as e:
            raise Exception(f"Failed to get embedding from Doubao API: {str(e)}")

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        return self.get_embeddings(texts)

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> "Embedding":
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.
        Returns:
            Embedding: A DoubaoEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "ark_api_key"):
            self.ark_api_key = embedding_configer.ark_api_key
        if hasattr(embedding_configer, "endpoint_id"):
            self.endpoint_id = embedding_configer.endpoint_id
        if hasattr(embedding_configer, "embedding_dims"):
            self.embedding_dims = embedding_configer.embedding_dims
        if self.ark_api_key:
            try:
                from volcenginesdkarkruntime import Ark
            except ImportError:
                raise ImportError("Ark is required. Install with: pip install volcengine-python-sdk[ark]")
            self.client = Ark(api_key=self.ark_api_key)
        return self
