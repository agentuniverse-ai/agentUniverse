# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 10:59
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: query_paraphraser.py

from abc import abstractmethod
from typing import Optional

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class QueryParaphraser(ComponentBase):
    """The basic class for query paraphraser."""

    component_type: ComponentEnum = ComponentEnum.QUERY_PARAPHRASER
    name: Optional[str] = None
    description: Optional[str] = None

    @abstractmethod
    def query_paraphrase(self, origin_query: Query) -> Query:
        """Paraphrase the origin query string to different style."""

    def _initialize_by_component_configer(self, query_paraphraser_config: ComponentConfiger) -> "QueryParaphraser":
        """Initialize the QueryParaphraser by the ComponentConfiger object.

        Args:
            query_paraphraser_config(ComponentConfiger): A configer contains query_paraphraser
            basic info.
        Returns:
            QueryParaphraser: A query_paraphraser instance.
        """
        if query_paraphraser_config.name:
            self.name = query_paraphraser_config.name
        if query_paraphraser_config.description:
            self.description = query_paraphraser_config.description

        return self
