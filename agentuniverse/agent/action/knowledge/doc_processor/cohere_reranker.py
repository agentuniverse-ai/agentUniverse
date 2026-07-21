# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: cohere_reranker.py

"""
Cohere reranker — a knowledge post-processing DocProcessor.

Re-ranks recalled documents using the Cohere Rerank API. Sibling of the
merged ``JinaReranker`` (#646) and ``DashscopeReranker``; addresses the
*Rerank* direction of #248.
"""

import logging
from typing import List, Optional

import requests

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

logger = logging.getLogger(__name__)

_COHERE_RERANK_URL = "https://api.cohere.com/v2/rerank"


class CohereReranker(DocProcessor):
    """Cohere Rerank API post-processor.

    Attributes:
        api_key: Cohere API key. Falls back to the ``COHERE_API_KEY`` env var.
        model_name: Cohere rerank model (default ``rerank-multilingual-v3.0``).
        top_n: Maximum number of documents returned after reranking.
        request_timeout: Timeout in seconds for the rerank HTTP call.
        score_key: Optional metadata key under which each document's relevance
            score is stamped.
    """

    api_key: Optional[str] = None
    model_name: str = "rerank-multilingual-v3.0"
    top_n: int = 10
    request_timeout: int = 30
    score_key: Optional[str] = "rerank_score"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        if not origin_docs:
            return []
        if query is None or not query.query_str:
            logger.warning("CohereReranker needs a query string; returning docs unchanged.")
            return origin_docs
        if not self.api_key:
            raise ValueError(
                "CohereReranker requires an api_key. Set it on the component "
                "or via the COHERE_API_KEY environment variable.")

        effective_top_n = min(self.top_n, len(origin_docs))
        texts = [doc.text or "" for doc in origin_docs]

        try:
            response = requests.post(
                _COHERE_RERANK_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "query": query.query_str,
                    "documents": texts,
                    "top_n": effective_top_n,
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("Cohere rerank request timed out; returning docs unchanged.")
            return origin_docs
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Cohere rerank API returned status "
                f"{exc.response.status_code if exc.response is not None else '?'}: "
                f"{exc}") from exc
        except ValueError as exc:
            raise RuntimeError(
                f"Cohere rerank API returned a non-JSON body: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Cohere rerank API returned non-JSON response: {exc}") from exc

        results = data.get("results", [])
        reranked: List[Document] = []
        for item in results:
            idx = item.get("index")
            score = item.get("relevance_score")
            if idx is None or idx < 0 or idx >= len(origin_docs):
                continue
            doc = origin_docs[idx]
            if self.score_key and score is not None:
                meta = dict(doc.metadata or {})
                meta[self.score_key] = float(score)
                doc = Document(text=doc.text, metadata=meta, embedding=doc.embedding)
            reranked.append(doc)
        return reranked if reranked else origin_docs

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "CohereReranker":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "api_key"):
            self.api_key = doc_processor_configer.api_key
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "request_timeout"):
            self.request_timeout = doc_processor_configer.request_timeout
        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key
        if not self.api_key:
            self.api_key = get_from_env("COHERE_API_KEY")
        return self
