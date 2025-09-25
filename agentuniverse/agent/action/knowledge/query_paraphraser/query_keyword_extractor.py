# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/12 15:44
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: query_keyword_extractor.py

from typing import Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import QueryParaphraser
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class QueryKeywordExtractor(QueryParaphraser):
    keyword_extractor: Optional[str] = "jieba_keyword_extractor"

    def query_paraphrase(self, origin_query: Query) -> Query:
        keyword_extractor_instance = DocProcessorManager().get_instance_obj(self.keyword_extractor)

        keywords = keyword_extractor_instance.process_docs([Document(text=origin_query.query_str)])[0].keywords

        origin_query.keywords.update(keywords)
        return origin_query

    def _initialize_by_component_configer(self, query_paraphraser_configer: ComponentConfiger) -> "QueryParaphraser":
        super()._initialize_by_component_configer(query_paraphraser_configer)
        if hasattr(query_paraphraser_configer, "keyword_extractor"):
            self.keyword_extractor = query_paraphraser_configer.keyword_extractor
        return self
