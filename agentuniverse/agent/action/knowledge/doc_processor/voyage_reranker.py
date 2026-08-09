# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: voyage_reranker.py

"""
Voyage AI reranker document processor.

Reranks recalled documents by their relevance to a Query using the Voyage AI
Rerank API (``https://api.voyageai.com/v1/rerank``). Voyage AI exposes a family
of rerank models such as ``rerank-2`` (default), ``rerank-2-lite``,
``rerank-2.5`` and ``rerank-2.5-lite``. An API key is required and can be
obtained from https://dash.voyageai.com/.

The structure mirrors the existing ``JinaReranker`` / ``DashscopeReranker``:
subclass :class:`DocProcessor`, override ``_process_docs`` to call the API,
and stamp the relevance score onto each kept document's metadata.
"""

import logging
from typing import List, Optional

import requests

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor \
    import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.util.env_util import get_from_env

logger = logging.getLogger(__name__)

# Voyage AI rerank endpoint. Kept as a module-level constant so the URL lives
# in exactly one place and is trivial to patch in unit tests.
_VOYAGE_RERANK_URL = "https://api.voyageai.com/v1/rerank"


class VoyageReranker(DocProcessor):
    """Document reranker using the Voyage AI Rerank API.

    This processor reranks documents based on their relevance to a query
    using Voyage AI's reranking models. The Voyage API returns results
    already sorted by descending relevance, so the kept documents are
    returned in that order.

    Attributes:
        api_key: Voyage AI API key. Falls back to the ``VOYAGE_API_KEY`` env
            var when not set on the component.
        model_name: Reranker model id (default ``rerank-2``).
        top_n: Maximum number of documents to return after reranking.
            Maps to the API's ``top_k`` parameter.
        request_timeout: Timeout in seconds for the rerank HTTP call. The
            ``requests`` library defaults to no timeout, so without this a
            stalled Voyage API would hang the whole rerank step indefinitely.
        score_key: Metadata key under which each kept document's relevance
            score is stamped (default ``rerank_score``).
    """

    api_key: Optional[str] = None
    model_name: str = "rerank-2"
    top_n: int = 10
    request_timeout: int = 30
    score_key: str = "rerank_score"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Rerank ``origin_docs`` by relevance to ``query``.

        Args:
            origin_docs: List of documents to be reranked.
            query: Query object carrying the search query string.

        Returns:
            List[Document]: Reranked documents sorted by descending relevance,
            each stamped with its relevance score under ``score_key``.

        Raises:
            Exception: If the query is missing, the API key is not set, or
                the API call fails (HTTP error / non-JSON body / transport
                error).
        """
        if not query or not query.query_str:
            raise Exception(
                "Voyage AI reranker needs an origin string query.")
        if not self.api_key:
            raise Exception(
                "Voyage AI API key is not set. Please configure it on the "
                "component or via the VOYAGE_API_KEY environment variable.")
        if not origin_docs:
            return []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # The Voyage API's "top_k" controls how many of the most relevant
        # documents are returned. We cap it at the number of input documents
        # so we never ask for more results than exist.
        effective_top_k = min(self.top_n, len(origin_docs))

        payload = {
            "model": self.model_name,
            "query": query.query_str,
            "documents": [doc.text for doc in origin_docs],
            "top_k": effective_top_k,
            "return_documents": False,
            "truncation": True,
        }

        try:
            response = requests.post(
                _VOYAGE_RERANK_URL, headers=headers, json=payload,
                timeout=self.request_timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Voyage AI rerank API call error: {e}")

        # Decode the body separately from the HTTP call. ``Response.json()``
        # raises ``requests.exceptions.JSONDecodeError`` on a non-JSON body
        # (e.g. an HTML error page from an upstream gateway). That exception
        # inherits from both ``RequestException`` and ``ValueError``, so a
        # single combined try block would misreport it as an API-call error;
        # isolating JSON decoding here surfaces it as a non-JSON response.
        try:
            results = response.json().get("data", [])
        except ValueError as e:
            raise Exception(
                f"Voyage AI rerank API returned a non-JSON response: {e}")

        rerank_docs: List[Document] = []
        for result in results:
            index = result.get("index")
            relevance_score = result.get("relevance_score")

            if index is None or relevance_score is None:
                continue
            if not isinstance(index, int) or index < 0 \
                    or index >= len(origin_docs):
                # Defensive: an out-of-range index would IndexError; skip it
                # rather than crash the whole rerank step.
                logger.warning(
                    "Voyage AI rerank returned out-of-range index %s", index)
                continue

            target_doc = origin_docs[index]
            metadata = dict(target_doc.metadata) \
                if target_doc.metadata else {}
            metadata[self.score_key] = relevance_score
            target_doc.metadata = metadata

            rerank_docs.append(target_doc)

        return rerank_docs

    def _initialize_by_component_configer(self,
                                          doc_processor_configer) \
            -> 'VoyageReranker':
        """Initialize reranker parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object for the doc
                processor.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        # The env var is the fallback; an explicit key in the YAML wins.
        self.api_key = get_from_env("VOYAGE_API_KEY")

        if hasattr(doc_processor_configer, "api_key"):
            self.api_key = doc_processor_configer.api_key
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key
        if hasattr(doc_processor_configer, "request_timeout"):
            self.request_timeout = self._validate_request_timeout(
                doc_processor_configer.request_timeout)

        return self

    @staticmethod
    def _validate_request_timeout(value) -> int:
        """Validate a configured request timeout.

        ``requests`` treats ``None`` as "no timeout" and accepts ``0`` /
        negative values without complaint, so a bad config must fail loudly
        here instead of hanging the rerank step or silently disabling the
        timeout. ``bool`` is a subclass of ``int`` (``True`` == 1) and is
        rejected explicitly so a YAML ``true`` does not silently become 1.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Exception(
                f"Voyage AI reranker request_timeout must be a positive "
                f"number, got {value!r}.")
        if value <= 0:
            raise Exception(
                f"Voyage AI reranker request_timeout must be a positive "
                f"number, got {value!r}.")
        return value
