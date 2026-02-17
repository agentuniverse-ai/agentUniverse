# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/8/10 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: jina_reranker.py

from typing import List, Optional
import requests

import aiohttp

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"


class JinaReranker(DocProcessor):
    """Document reranker using Jina AI's Rerank API.

    This processor reranks documents based on their relevance to a query
    using Jina AI's reranking models.
    """
    api_key: Optional[str] = None
    model_name: str = "jina-reranker-v2-base-multilingual"
    top_n: int = 10

    def _validate_inputs(self, origin_docs: List[Document], query: Query = None):
        if not query or not query.query_str:
            raise Exception("Jina AI reranker needs an origin string query.")
        if not self.api_key:
            raise Exception(
                "Jina AI API key is not set. Please configure it in the component or environment variables.")

    def _build_payload(self, origin_docs: List[Document], query: Query) -> dict:
        return {
            "model": self.model_name,
            "query": query.query_str,
            "documents": [doc.text for doc in origin_docs],
            "top_n": self.top_n,
        }

    def _build_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @staticmethod
    def _build_rerank_docs(origin_docs: List[Document], results: list) -> List[Document]:
        rerank_docs = []
        for result in results:
            index = result.get("index")
            relevance_score = result.get("relevance_score")
            if index is None or relevance_score is None:
                continue
            if origin_docs[index].metadata:
                origin_docs[index].metadata["relevance_score"] = relevance_score
            else:
                origin_docs[index].metadata = {"relevance_score": relevance_score}
            rerank_docs.append(origin_docs[index])
        return rerank_docs

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Rerank documents based on their relevance to the query."""
        self._validate_inputs(origin_docs, query)
        if not origin_docs:
            return []

        try:
            response = requests.post(
                JINA_RERANK_URL,
                headers=self._build_headers(),
                json=self._build_payload(origin_docs, query),
            )
            response.raise_for_status()
            results = response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jina AI rerank API call error: {e}")

        return self._build_rerank_docs(origin_docs, results)

    async def _async_process_docs(self, origin_docs: List[Document],
                                  query: Query = None) -> List[Document]:
        """Async rerank using aiohttp to call the Jina API."""
        self._validate_inputs(origin_docs, query)
        if not origin_docs:
            return []

        async with aiohttp.ClientSession() as session:
            async with session.post(
                JINA_RERANK_URL,
                headers=self._build_headers(),
                json=self._build_payload(origin_docs, query),
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                resp.raise_for_status()
                resp_json = await resp.json()

        results = resp_json.get("results", [])
        return self._build_rerank_docs(origin_docs, results)

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize reranker parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object for the doc processor.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        self.api_key = get_from_env("JINA_API_KEY")

        if hasattr(doc_processor_configer, "api_key"):
            self.api_key = doc_processor_configer.api_key
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n

        return self