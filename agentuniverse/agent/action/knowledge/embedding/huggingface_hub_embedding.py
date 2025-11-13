#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/12 13:00
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: huggingface_hub_embedding.py

from typing import List, Optional, Any
import asyncio
from langchain_core.embeddings import Embeddings as LCEmbeddings

from huggingface_hub import InferenceClient, AsyncInferenceClient
from huggingface_hub.errors import InferenceTimeoutError, HfHubHTTPError
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

class HuggingFaceHubEmbeddingError(Exception):
    """Custom exception class for HuggingFaceHub embedding errors."""
    pass

class HuggingFaceHubEmbedding(Embedding):
    """The Hugging Face Hub embedding class using Inference API with native clients."""

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("HUGGINGFACE_HUB_API_TOKEN"))
    provider: Optional[str] = "hf-inference"
    timeout: Optional[float] = 60
    verify_ssl: Optional[bool] = True
    client: Any = None
    async_client: Any = None

    def __init__(self, **kwargs):
        """Initialize the Hugging Face embedding with native clients."""
        super().__init__(**kwargs)
        self._initialize_clients()

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Retrieve text embeddings for a list of input texts using Hugging Face Hub Inference API.

        Args:
            texts (List[str]): A list of texts that need to be embedded.
            **kwargs: Additional keyword arguments.

        Returns:
            List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.

        Raises:
            ValueError: If there missing some required parameters.
            HuggingFaceHubEmbeddingError: If there is an error during the embedding process.
        """
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        
        try:
            embeddings = []
            for text in texts:
                embedding = self.client.feature_extraction(
                    text=text,
                    model=self.embedding_model_name
                )
                # Convert numpy array to list
                embeddings.append(embedding.tolist())
            
            return embeddings
        except InferenceTimeoutError as e:
            raise HuggingFaceHubEmbeddingError(f"Model is unavailable or the request times out: {str(e)}") from e
        except HfHubHTTPError as e:
            raise HuggingFaceHubEmbeddingError(f"Request failed with an HTTP error status code other than HTTP 503: {str(e)}") from e
        except Exception as e:
            raise HuggingFaceHubEmbeddingError(f"Unexpected error getting embeddings from Hugging Face Hub: {str(e)}") from e

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get embeddings for a list of texts using Hugging Face Hub Inference API.

        Args:
            texts (List[str]): A list of texts that need to be embedded.
            **kwargs: Additional keyword arguments.

        Returns:
            List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.
            
        Raises:
            ValueError: If there missing some required parameters.
            HuggingFaceHubEmbeddingError: If there is an error during the embedding process.
        """
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        
        try:
            async def get_single_embedding(text: str) -> List[float]:
                embedding = await self.async_client.feature_extraction(
                    text=text,
                    model=self.embedding_model_name
                )
                # Convert numpy array to list
                return embedding.tolist()

            tasks = [get_single_embedding(text) for text in texts]
            embeddings = await asyncio.gather(*tasks)
            return embeddings
        except InferenceTimeoutError as e:
            raise HuggingFaceHubEmbeddingError(f"Model is unavailable or the request times out: {str(e)}") from e
        except HfHubHTTPError as e:
            raise HuggingFaceHubEmbeddingError(f"Request failed with an HTTP error status code other than HTTP 503: {str(e)}") from e
        except Exception as e:
            raise HuggingFaceHubEmbeddingError(f"Unexpected error getting embeddings from Hugging Face Hub: {str(e)}") from e

    def as_langchain(self) -> Any:
        """Convert the agentUniverse(aU) Hugging Face Hub embedding class to the langchain Hugging Face Hub embedding class."""
        class HuggingFaceHubLangchainEmbedding(LCEmbeddings):
            """Wrapper for HuggingFaceHub Embeddings to conform to Langchain's Embeddings interface."""
            huggingface_hub_embedding: HuggingFaceHubEmbedding  # Add an instance of HuggingFaceHubEmbedding

            def __init__(self, huggingface_hub_embedding: HuggingFaceHubEmbedding, **kwargs):
                super().__init__(**kwargs)  # Initialize the parent class
                self.huggingface_hub_embedding = huggingface_hub_embedding  # Store the HuggingFaceHubEmbedding instance

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return self.huggingface_hub_embedding.get_embeddings(texts)

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return self.huggingface_hub_embedding.get_embeddings([text])[0]

        return HuggingFaceHubLangchainEmbedding(huggingface_hub_embedding=self)  # Pass the instance of HuggingFaceHubEmbedding

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding basic info.
            
        Returns:
            Embedding: A embedding instance.
            
        Raises:
            ValueError: If the api_key is missing when initializing the embedding.
        """
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "api_key") and embedding_configer.api_key:
            self.api_key = embedding_configer.api_key
        if hasattr(embedding_configer, "timeout") and embedding_configer.timeout:
            self.timeout = embedding_configer.timeout
        if hasattr(embedding_configer, "provider") and embedding_configer.provider:
            self.provider = embedding_configer.provider
        if hasattr(embedding_configer, "verify_ssl") and embedding_configer.verify_ssl is not None:
            self.verify_ssl = embedding_configer.verify_ssl
        
        # Only reinitialize clients if we have an API key
        if self.api_key is not None:
            self._initialize_clients()
        return self

    def _initialize_clients(self) -> None:
        """Initialize the Hugging Face Hub Inference clients.

        Raises:
            ValueError: If the api_key is missing when initializing the clients.
        """
        if self.api_key is None:
            raise ValueError("Must provide `api_key` for Hugging Face Hub Inference")
        
        # Always recreate clients with current configuration
        self.client = InferenceClient(
            provider=self.provider if self.provider else "hf-inference",
            api_key=self.api_key,
            timeout=self.timeout if self.timeout else 60
        )
        
        # Configure SSL verification if needed
        if not self.verify_ssl:
            import ssl
            import httpx
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create custom httpx client with SSL verification disabled
            custom_http_client = httpx.Client(verify=ssl_context)
            custom_async_http_client = httpx.AsyncClient(verify=ssl_context)
            
            self.client = InferenceClient(
                provider=self.provider if self.provider else "hf-inference",
                api_key=self.api_key,
                timeout=self.timeout if self.timeout else 60,
                http_client=custom_http_client
            )
            
            self.async_client = AsyncInferenceClient(
                provider=self.provider if self.provider else "hf-inference",
                api_key=self.api_key,
                timeout=self.timeout if self.timeout else 60,
                http_client=custom_async_http_client
            )
        else:
            self.async_client = AsyncInferenceClient(
                provider=self.provider if self.provider else "hf-inference",
                api_key=self.api_key,
                timeout=self.timeout if self.timeout else 60
            )