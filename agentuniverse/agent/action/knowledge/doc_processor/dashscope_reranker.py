# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 15:48
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: dashscope_reranker.py

from typing import List, Optional
import dashscope
from http import HTTPStatus

import aiohttp

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

MODEL_NAME_MAP = {
    "gte_rerank": dashscope.TextReRank.Models.gte_rerank
}

DASHSCOPE_RERANK_URL = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"


class DashscopeReranker(DocProcessor):
    """Document reranker using Dashscope's TextReRank API.

    This processor reranks documents based on their relevance to a query
    using Dashscope's text reranking models.

    Attributes:
        model_name: The name of the reranking model to use.
        top_n: Maximum number of documents to return after reranking.
    """
    model_name: str = "gte_rerank"
    top_n: int = 10

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Rerank documents based on their relevance to the query.

        Args:
            origin_docs: List of documents to be reranked.
            query: Query object containing the search query string.

        Returns:
            List[Document]: Reranked documents sorted by relevance score.

        Raises:
            Exception: If query is missing or API call fails.
        """
        if not query or not query.query_str:
            raise Exception("Dashscope reranker need an origin string query.")
        if len(origin_docs) < 1:
            return origin_docs
        documents_texts = []
        for _doc in origin_docs:
            documents_texts.append(_doc.text)
        resp = dashscope.TextReRank.call(
            model=MODEL_NAME_MAP.get(self.model_name),
            query=query.query_str,
            documents=documents_texts,
            top_n=self.top_n,
            return_documents=False
        )
        if resp.status_code == HTTPStatus.OK:
            results = resp.output.results
        else:
            raise Exception(f"Dashscope rerank api call error: {resp}")
        return self._build_rerank_docs(origin_docs, results)

    async def _async_process_docs(self, origin_docs: List[Document],
                                  query: Query = None) -> List[Document]:
        """Async rerank using aiohttp to call the Dashscope API."""
        if not query or not query.query_str:
            raise Exception("Dashscope reranker need an origin string query.")
        if len(origin_docs) < 1:
            return origin_docs

        import os
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        documents_texts = [doc.text for doc in origin_docs]

        payload = {
            "model": MODEL_NAME_MAP.get(self.model_name, self.model_name),
            "input": {
                "query": query.query_str,
                "documents": documents_texts,
            },
            "parameters": {
                "top_n": self.top_n,
                "return_documents": False,
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                DASHSCOPE_RERANK_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                resp_json = await resp.json()

        output = resp_json.get("output")
        if not output:
            error_code = resp_json.get("code", "")
            error_message = resp_json.get("message", "")
            raise Exception(
                f"Dashscope rerank api call error: code={error_code}, message={error_message}"
            )

        results = output.get("results", [])
        return self._build_rerank_docs(origin_docs, results)

    @staticmethod
    def _build_rerank_docs(origin_docs: List[Document], results) -> List[Document]:
        """Build reranked document list from API results."""
        rerank_docs = []
        for _result in results:
            index = _result.index if hasattr(_result, 'index') else _result.get('index')
            score = _result.relevance_score if hasattr(_result, 'relevance_score') else _result.get('relevance_score')
            if origin_docs[index].metadata:
                origin_docs[index].metadata["relevance_score"] = score
            else:
                origin_docs[index].metadata = {"relevance_score": score}
            rerank_docs.append(origin_docs[index])
        return rerank_docs

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize reranker parameters from component configuration.
        
        Args:
            doc_processor_configer: Configuration object containing reranker parameters.
            
        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        return self
