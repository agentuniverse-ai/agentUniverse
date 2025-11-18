# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 15:48
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: dashscope_reranker.py

from typing import List, Optional
import dashscope
from http import HTTPStatus

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

MODEL_NAME_MAP = {
    "gte_rerank": dashscope.TextReRank.Models.gte_rerank
}


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
        if len(origin_docs)<1:
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
        rerank_docs = []
        for _result in results:
            index = _result.index
            if origin_docs[index].metadata:
                origin_docs[index].metadata["relevance_score"] = _result.relevance_score
            else:
                origin_docs[index].metadata = {"relevance_score": _result.relevance_score}
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
