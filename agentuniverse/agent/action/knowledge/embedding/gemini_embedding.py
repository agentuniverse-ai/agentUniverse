#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
from typing import List, Any

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
                raise ImportError(
                    "genai is required. Install with: pip install google-genai"
                ) from e

        model_name = self.embedding_model_name or "text-embedding-004"  # default model

        try:
            response = self.client.models.embed_content(
                model=model_name,
                contents=texts,
            )
            return [embedding.values for embedding in response.embeddings]
        except Exception as e:
            raise ValueError(f"Error generating embedding for text: {e}")

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get embeddings for a list of texts using the Gemini API."""
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    def _initialize_by_component_configer(self, embedding_configer: ComponentConfiger) -> 'Embedding':
        super()._initialize_by_component_configer(embedding_configer)
        if hasattr(embedding_configer, "gemini_api_key"):
            self.gemini_api_key = embedding_configer.gemini_api_key
        
        # Initialize client if API key is available
        if self.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_api_key)
            except ImportError as e:
                raise ImportError(
                    "genai is required. Install with: pip install google-genai"
                ) from e
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
        return self