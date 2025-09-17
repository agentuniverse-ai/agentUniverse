#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List, Any

from langchain_core.embeddings import Embeddings as LCEmbeddings
from pydantic import Field
from typing_extensions import Optional

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


# @Time : 2025/2/13 12:10
# @Author : wozhapen
# @mail : wozhapen@gmail.com
# @FileName :gemini_embedding.py


class GeminiEmbedding(Embedding):
    """Gemini Embedding class that inherits from the base Embedding class."""

    client: Any = None
    gemini_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_API_KEY"))

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Get embeddings for a list of texts using the Gemini API."""
        if not self.client:
            if not self.gemini_api_key:
                raise ValueError("GOOGLE_API_KEY is required but not set")
            try:
                from google import genai

                self.client = genai.Client(api_key=self.gemini_api_key)
            except ImportError as e:
                raise ImportError("genai is required. Install with: pip install google-genai") from e

        model_name = self.embedding_model_name or "text-embedding-004"  # default model

        try:
            response = self.client.models.embed_content(
                model=model_name,
                contents=texts,
                # gemini default 768, and only support 768
                # config=EmbedContentConfig(output_dimensionality=(self.embedding_dims or 768))
            )
            return [embedding.values for embedding in response.embeddings]
        except Exception as e:
            print(f"Error generating embedding for text: {texts}. Error: {e}")
            # Handle the error appropriately, e.g., return a zero vector or raise an exception
            raise ValueError(e)

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get embeddings for a list of texts using the Gemini API."""
        # This implementation is synchronous because the Gemini API does not currently offer an official asynchronous client for embedding.
        # Consider implementing async batching or utilizing a ThreadPoolExecutor to wrap the synchronous call for better concurrency.
        return self.get_embeddings(texts, **kwargs)

    def as_langchain(self) -> LCEmbeddings:
        """Convert to a Langchain Embedding class."""
        #  This can be implemented to return an instance of a custom class extending from `langchain_core.embeddings.Embeddings`.
        #  However, since we are already using `google.generativeai` directly, this might be redundant.

        class GeminiLangchainEmbedding(LCEmbeddings):
            """Wrapper for Gemini Embeddings to conform to Langchain's Embeddings interface."""

            gemini_embedding: GeminiEmbedding  # Add an instance of GeminiEmbedding

            def __init__(self, gemini_embedding: GeminiEmbedding, **kwargs):
                super().__init__(**kwargs)  # Initialize the parent class
                self.gemini_embedding = gemini_embedding  # Store the GeminiEmbedding instance

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return self.gemini_embedding.get_embeddings(texts)

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return self.gemini_embedding.get_embeddings([text])[0]

        return GeminiLangchainEmbedding(gemini_embedding=self)  # Pass the instance of GeminiEmbedding

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> "Embedding":
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "gemini_api_key"):
            self.gemini_api_key = embedding_configer.gemini_api_key

        # Initialize client if API key is available
        if self.gemini_api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.gemini_api_key)
            except ImportError as e:
                raise ImportError("genai is required. Install with: pip install google-genai") from e
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
        return self
