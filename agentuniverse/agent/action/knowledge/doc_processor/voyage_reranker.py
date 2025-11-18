# !/usr/bin/env python3

# @Time    : 2025/11/17 22:30
# @Author  : hehaolan
# @Email   : hehaolan716@gmail.com
# @FileName: voyage_reranker.py


import requests

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env

api_base = "https://api.voyageai.com/v1/rerank"


class VoyageRerankerError(Exception):
    """Domain specific exception for Voyage reranker failures."""

    default_message = "Voyage reranker error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class VoyageMissingQueryError(VoyageRerankerError):
    default_message = "Voyage AI reranker needs an origin string query."

    def __init__(self):
        super().__init__(self.default_message)


class VoyageMissingAPIKeyError(VoyageRerankerError):
    default_message = "Voyage AI API key is not set. Please configure it in the component or environment variables."

    def __init__(self):
        super().__init__(self.default_message)


class VoyageAPIRequestError(VoyageRerankerError):
    def __init__(self, original_exc: Exception):
        super().__init__(f"Voyage AI rerank API call error: {original_exc}")
        self.original_exc = original_exc


class VoyageReranker(DocProcessor):
    """Document reranker using Voyage AI's Rerank API.

    This processor reranks documents based on their relevance to a query
    using Voyage AI's reranking models.


    Attributes:
        api_key: The API key for Voyage AI's Rerank API.
        model_name: The name of the reranking model to use.
        top_n: Maximum number of documents to return after reranking.
        truncation: Whether to truncate input to fit context length limit.
    """

    api_key: str | None = None
    model_name: str = "rerank-2.5"
    top_n: int = 10
    truncation: bool = True

    request_timeout: int = 10

    def _process_docs(self, origin_docs: list[Document], query: Query = None) -> list[Document]:
        """Rerank documents based on their relevance to the query.

        Args:
            origin_docs: List of documents to be reranked.
            query: Query object containing the search query string.

        Returns:
            List[Document]: Reranked documents sorted by relevance score.

        Raises:
            VoyageRerankerError: if validation fails or Voyage API returns an error.
        """
        if not query or not query.query_str:
            raise VoyageMissingQueryError()
        if not self.api_key:
            raise VoyageMissingAPIKeyError()
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
            "top_k": self.top_n,
            "truncation": self.truncation,
        }

        try:
            response = requests.post(
                api_base,
                headers=headers,
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            results = response.json().get("data", [])
        except requests.exceptions.RequestException as exc:
            raise VoyageAPIRequestError(exc) from exc

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

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> "DocProcessor":
        """Initialize reranker parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object for the doc processor.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        self.api_key = get_from_env("VOYAGE_API_KEY")

        if hasattr(doc_processor_configer, "api_key"):
            self.api_key = doc_processor_configer.api_key
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "truncation"):
            self.truncation = doc_processor_configer.truncation

        return self
