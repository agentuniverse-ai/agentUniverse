# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/05
# @FileName: huggingface_embedding.py

import asyncio
from typing import Any, List, Optional

from pydantic import Field
from langchain_core.embeddings import Embeddings as LCEmbeddings

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

DEFAULT_HUGGINGFACE_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

class HuggingFaceEmbedding(Embedding):
    """The HuggingFace embedding class.

    It relies on `huggingface_hub.InferenceClient.feature_extraction` and therefore
    supports the HuggingFace Inference API, dedicated Inference Endpoints and self
    hosted Text Embeddings Inference(TEI) servers.

    Attributes:
        huggingface_api_key (Optional[str]): HuggingFace access token, read from the
            `HUGGINGFACE_API_KEY` or `HF_TOKEN` environment variable by default.
        huggingface_base_url (Optional[str]): Optional endpoint url, used when the model
            is served by an inference endpoint or a self hosted TEI server.
        embedding_model_name (Optional[str]): The HuggingFace model repo id.
        timeout (Optional[int]): Request timeout in seconds.
    """

    huggingface_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_API_KEY") or get_from_env("HF_TOKEN"))
    huggingface_base_url: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_BASE_URL"))

    embedding_model_name: Optional[str] = DEFAULT_HUGGINGFACE_EMBEDDING_MODEL
    embedding_dims: Optional[int] = None
    timeout: Optional[int] = Field(default=60)

    client: Any = None
    async_client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of input texts.

        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Extra feature extraction arguments, such as `normalize` or `truncate`.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()

        try:
            return [self._to_vector(self.client.feature_extraction(text, **kwargs)) for text in texts]
        except Exception as e:
            raise Exception(f"Failed to get embedding from HuggingFace API: {e}")

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously retrieve text embeddings for a list of input texts.

        Args:
            texts (List[str]): A list of input texts to be embedded.
            **kwargs: Extra feature extraction arguments, such as `normalize` or `truncate`.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call fails or if required configuration is missing.
        """
        self._initialize_clients()

        try:
            async def get_single_embedding(text: str) -> List[float]:
                return self._to_vector(await self.async_client.feature_extraction(text, **kwargs))

            return list(await asyncio.gather(*[get_single_embedding(text) for text in texts]))
        except Exception as e:
            raise Exception(f"Failed to get embedding from HuggingFace API: {e}")

    def as_langchain(self) -> Any:
        """Convert the HuggingFaceEmbedding instance to a LangChain embeddings instance."""
        if self.huggingface_base_url:
            # `langchain_community.HuggingFaceHubEmbeddings` is intentionally not used as a
            # fallback here, it calls the `InferenceClient.post` method which was removed in
            # huggingface_hub v1.0, so it raises an AttributeError at runtime.
            endpoint_clz = self._load_langchain_clz([
                ('langchain_huggingface', 'HuggingFaceEndpointEmbeddings'),
                ('langchain_community.embeddings', 'HuggingFaceEndpointEmbeddings'),
            ], required=False)
            if endpoint_clz is None:
                return _HuggingFaceLangchainEmbeddings(self)
            return endpoint_clz(
                model=self.huggingface_base_url,
                huggingfacehub_api_token=self.huggingface_api_key,
            )
        inference_clz = self._load_langchain_clz([
            ('langchain_huggingface', 'HuggingFaceInferenceAPIEmbeddings'),
            ('langchain_community.embeddings', 'HuggingFaceInferenceAPIEmbeddings'),
        ], required=False)
        if inference_clz is None:
            return _HuggingFaceLangchainEmbeddings(self)
        return inference_clz(
            api_key=self.huggingface_api_key,
            model_name=self.embedding_model_name,
        )

    @staticmethod
    def _load_langchain_clz(candidates: List[tuple], required: bool = True) -> Any:
        """Load the first available langchain embeddings class from the candidates."""
        import importlib
        for module_name, class_name in candidates:
            try:
                return getattr(importlib.import_module(module_name), class_name)
            except (ImportError, AttributeError):
                continue
        if not required:
            return None
        raise ImportError(
            "A langchain huggingface embeddings class is required, "
            "install with: pip install langchain-huggingface"
        )

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.

        Returns:
            Embedding: A HuggingFaceEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "huggingface_api_key"):
            self.huggingface_api_key = embedding_configer.huggingface_api_key
        if hasattr(embedding_configer, "huggingface_base_url"):
            self.huggingface_base_url = embedding_configer.huggingface_base_url
        if hasattr(embedding_configer, "timeout"):
            self.timeout = embedding_configer.timeout
        return self

    def _initialize_clients(self) -> None:
        """Lazily create the HuggingFace sync and async inference clients."""
        if self.client is not None and self.async_client is not None:
            return
        if not self.huggingface_base_url and not self.embedding_model_name:
            raise Exception("embedding_model_name is missing")

        try:
            from huggingface_hub import AsyncInferenceClient, InferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is required. Install with: pip install huggingface_hub"
            )

        # `model` and `base_url` are mutually exclusive in the huggingface inference client.
        if self.huggingface_base_url:
            client_args = {"base_url": self.huggingface_base_url}
        else:
            client_args = {"model": self.embedding_model_name}
        client_args["api_key"] = self.huggingface_api_key
        client_args["timeout"] = self.timeout

        if self.client is None:
            self.client = InferenceClient(**client_args)
        if self.async_client is None:
            self.async_client = AsyncInferenceClient(**client_args)

    @staticmethod
    def _to_vector(result: Any) -> List[float]:
        """Reduce the feature extraction result to a single sentence vector.

        The feature extraction route returns a sentence embedding for sentence
        similarity models, but token level embeddings for plain encoder models,
        in the latter case a mean pooling is applied.
        """
        if hasattr(result, "tolist"):
            result = result.tolist()
        if not isinstance(result, list) or len(result) == 0:
            raise Exception(f"Unexpected feature extraction result: {result}")

        # unwrap the batch dimension returned for a single input text.
        while isinstance(result[0], list) and len(result) == 1:
            result = result[0]

        if isinstance(result[0], (int, float)):
            return [float(value) for value in result]

        # token level embeddings, apply mean pooling over the token dimension.
        while isinstance(result[0][0], list):
            result = [token for sequence in result for token in sequence]
        token_count = len(result)
        return [float(sum(values)) / token_count for values in zip(*result)]


class _HuggingFaceLangchainEmbeddings(LCEmbeddings):
    """A langchain embeddings adapter delegating to the aU HuggingFaceEmbedding.

    It is used when no maintained langchain huggingface embeddings class is installed,
    so that `as_langchain` keeps working on any `huggingface_hub` version and always
    stays consistent with the component configuration.
    """

    def __init__(self, huggingface_embedding: 'HuggingFaceEmbedding'):
        self.huggingface_embedding = huggingface_embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.huggingface_embedding.get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.huggingface_embedding.get_embeddings([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.huggingface_embedding.async_get_embeddings(texts)

    async def aembed_query(self, text: str) -> List[float]:
        return (await self.huggingface_embedding.async_get_embeddings([text]))[0]
