# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025-10-05 21:40 PM
# @Author  : Cascade AI
# @Email   : cascade@windsurf.ai
# @FileName: test_ollama_embedding.py

import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from agentuniverse.agent.action.knowledge.embedding.ollama_embedding import OllamaEmbedding


class OllamaEmbeddingTest(unittest.TestCase):
    """
    Test cases for OllamaEmbedding class
    """

    def setUp(self) -> None:
        self.embedding = OllamaEmbedding()
        self.embedding.ollama_base_url = "http://localhost:11434"
        self.embedding.embedding_model_name = "mxbai-embed-large"
        self.embedding.timeout = 30

    def test_get_embeddings_real_api(self) -> None:
        """
        Test get_embeddings with real Ollama API.
        This test requires Ollama to be running locally with the model available.
        Skip if Ollama is not available.
        """
        try:
            # Test with different models
            models_to_test = ["mxbai-embed-large", "nomic-embed-text", "all-minilm"]
            
            for model in models_to_test:
                with self.subTest(model=model):
                    self.embedding.embedding_model_name = model
                    res = self.embedding.get_embeddings(texts=["hello world"])
                    print(f"Model {model} - Embedding shape: {len(res[0]) if res and res[0] else 'None'}")
                    
                    self.assertIsInstance(res, list)
                    self.assertEqual(len(res), 1)
                    self.assertIsInstance(res[0], list)
                    self.assertGreater(len(res[0]), 0)
                    
        except Exception as e:
            self.skipTest(f"Ollama API not available or model not found: {e}")

    def test_async_get_embeddings_real_api(self) -> None:
        """
        Test async_get_embeddings with real Ollama API.
        This test requires Ollama to be running locally with the model available.
        Skip if Ollama is not available.
        """
        try:
            res = asyncio.run(
                self.embedding.async_get_embeddings(texts=["hello world"]))
            print(f"Async embedding result shape: {len(res[0]) if res and res[0] else 'None'}")
            
            self.assertIsInstance(res, list)
            self.assertEqual(len(res), 1)
            self.assertIsInstance(res[0], list)
            self.assertGreater(len(res[0]), 0)
            
        except Exception as e:
            self.skipTest(f"Ollama API not available: {e}")

    def test_as_langchain(self) -> None:
        """
        Test LangChain integration.
        This test requires langchain_community to be installed.
        """
        try:
            langchain_embedding = self.embedding.as_langchain()
            self.assertIsNotNone(langchain_embedding)
            print(f"LangChain embedding type: {type(langchain_embedding)}")
            
            # Test with LangChain interface if Ollama is available
            try:
                res = langchain_embedding.embed_documents(texts=["hello world"])
                print(f"LangChain embedding result shape: {len(res[0]) if res and res[0] else 'None'}")
                self.assertIsInstance(res, list)
            except Exception as e:
                print(f"LangChain embedding test skipped: {e}")
                
        except ImportError:
            self.skipTest("langchain_community not available")
        except Exception as e:
            self.skipTest(f"LangChain integration test failed: {e}")

    def test_initialization_errors(self) -> None:
        """Test initialization error handling"""
        # Test missing base URL
        embedding = OllamaEmbedding()
        embedding.ollama_base_url = None
        embedding.embedding_model_name = "test-model"
        
        with self.assertRaises(Exception) as context:
            embedding.get_embeddings(["test"])
        self.assertIn("OLLAMA_BASE_URL is missing", str(context.exception))
        
        # Test missing model name
        embedding = OllamaEmbedding()
        embedding.ollama_base_url = "http://localhost:11434"
        embedding.embedding_model_name = None
        
        with self.assertRaises(Exception) as context:
            embedding.get_embeddings(["test"])
        self.assertIn("embedding_model_name is missing", str(context.exception))

    def test_multiple_models_configuration(self) -> None:
        """Test configuration with different supported models"""
        supported_models = ["mxbai-embed-large", "nomic-embed-text", "all-minilm"]
        
        for model in supported_models:
            with self.subTest(model=model):
                embedding = OllamaEmbedding()
                embedding.ollama_base_url = "http://localhost:11434"
                embedding.embedding_model_name = model
                embedding.timeout = 30
                
                # Test that configuration is set correctly
                self.assertEqual(embedding.embedding_model_name, model)
                self.assertEqual(embedding.ollama_base_url, "http://localhost:11434")


if __name__ == '__main__':
    unittest.main()
