# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: cohere_rerank.py

"""
Cohere rerank post-processor.

Reranks the documents recalled by a Store with the Cohere Rerank API (v2),
sorting them by their relevance to the Query. Addresses the *re-ranking*
direction of issue #248, alongside `DashscopeReranker` and `JinaReranker`.
"""

import os
from typing import List, Optional

import httpx
from pydantic import Field

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

COHERE_RERANK_API_BASE = "https://api.cohere.com/v2/rerank"


class CohereRerank(DocProcessor):
    """Document reranker using Cohere's Rerank API (v2).

    This processor reranks documents based on their relevance to a query
    using Cohere's rerank models, e.g. ``rerank-v3.5``.

    Attributes:
        api_key: Cohere API key. Falls back to the ``COHERE_API_KEY`` env var.
            An empty value is rejected at call time — it is never silently
            sent to the API as a bearer token.
        model_name: Cohere rerank model id.
        top_n: Maximum number of documents returned after reranking.
        max_chunks_per_doc: Optional Cohere option that splits each document
            into at most this many chunks before scoring; when ``None`` the
            parameter is omitted from the request so the API default applies.
        request_timeout: Timeout in seconds for the rerank HTTP call, so a
            stalled Cohere endpoint cannot hang the whole rerank step.
    """
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("COHERE_API_KEY"))
    model_name: str = "rerank-v3.5"
    top_n: int = 10
    max_chunks_per_doc: Optional[int] = None
    request_timeout: float = 30

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Rerank documents based on their relevance to the query.

        Degenerate inputs pass through without any API call: an empty
        document list is returned as-is, and a missing or empty query
        returns the documents unchanged in their original order (there is
        nothing to rank against).

        Args:
            origin_docs: List of documents to be reranked.
            query: Query object containing the search query string.

        Returns:
            List[Document]: Reranked documents sorted by relevance score,
            with each score stamped into the document's ``relevance_score``
            metadata key.

        Raises:
            Exception: If the API key is not set (or empty), or the API call
            fails (transport error, non-200 status, non-JSON body).
        """
        if not origin_docs:
            return []
        if not query or not query.query_str:
            return list(origin_docs)

        # ``os.getenv`` returns an empty string for a placeholder like
        # ``COHERE_API_KEY=""``; strip and reject it here so it is never
        # sent to the API.
        api_key = self.api_key.strip() if isinstance(self.api_key, str) \
            else None
        if not api_key:
            raise Exception(
                "Cohere rerank API key is not set. Please set the "
                "COHERE_API_KEY environment variable or the api_key "
                "attribute of the cohere_rerank component (an empty value "
                "is not accepted).")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": self.model_name,
            "query": query.query_str,
            "documents": [doc.text for doc in origin_docs],
            "top_n": self.top_n,
        }
        if self.max_chunks_per_doc is not None:
            payload["max_chunks_per_doc"] = self.max_chunks_per_doc

        try:
            response = httpx.post(COHERE_RERANK_API_BASE, headers=headers,
                                  json=payload,
                                  timeout=self.request_timeout)
        except httpx.TransportError as e:
            raise Exception(f"Cohere rerank API call error: {e}") from e

        # ``httpx.post`` does not raise on HTTP error statuses, so a non-200
        # must be surfaced here with the status code and response body.
        if response.status_code != 200:
            raise Exception(
                f"Cohere rerank API returned HTTP "
                f"{response.status_code}: {response.text[:500]}")

        # Decode the body separately from the HTTP call so a non-JSON body
        # (e.g. an HTML error page from an upstream gateway) is reported as
        # such instead of as a transport failure.
        try:
            results = response.json().get("results", [])
        except ValueError as e:
            raise Exception(
                f"Cohere rerank API returned a non-JSON response: {e}"
            ) from e

        rerank_docs = []
        for result in results:
            index = result.get("index")
            relevance_score = result.get("relevance_score")

            if index is None or relevance_score is None:
                continue
            if index < 0 or index >= len(origin_docs):
                continue

            if origin_docs[index].metadata:
                origin_docs[index].metadata["relevance_score"] = \
                    relevance_score
            else:
                origin_docs[index].metadata = {
                    "relevance_score": relevance_score}
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

        self.api_key = get_from_env("COHERE_API_KEY")

        if hasattr(doc_processor_configer, "api_key"):
            self.api_key = doc_processor_configer.api_key
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "max_chunks_per_doc"):
            self.max_chunks_per_doc = \
                doc_processor_configer.max_chunks_per_doc
        if hasattr(doc_processor_configer, "request_timeout"):
            self.request_timeout = doc_processor_configer.request_timeout

        return self
