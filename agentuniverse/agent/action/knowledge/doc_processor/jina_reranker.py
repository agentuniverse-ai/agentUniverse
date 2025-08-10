# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/8/10 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: jina_reranker.py

from typing import List, Optional
import requests

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

api_base = "https://api.jina.ai/v1/rerank"

class JinaReranker(DocProcessor):
    """Document reranker using Jina AI's Rerank API.

    This processor reranks documents based on their relevance to a query
    using Jina AI's reranking models.
    """
    api_key: Optional[str] = None
    model_name: str = "jina-reranker-v2-base-multilingual"
    top_n: int = 10

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Rerank documents based on their relevance to the query.

        Args:
            origin_docs: List of documents to be reranked.
            query: Query object containing the search query string.

        Returns:
            List[Document]: Reranked documents sorted by relevance score.

        Raises:
            Exception: If the query is missing, the API key is not set, or the API call fails.
        """
        if not query or not query.query_str:
            raise Exception("Jina AI reranker needs an origin string query.")
        if not self.api_key:
            raise Exception(
                "Jina AI API key is not set. Please configure it in the component or environment variables.")
        if not origin_docs:
            return []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model_name,
            "query": query.query_str,
            "documents": [doc.text for doc in origin_docs],
            "top_n": self.top_n,
        }

        try:
            response = requests.post(api_base, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jina AI rerank API call error: {e}")

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