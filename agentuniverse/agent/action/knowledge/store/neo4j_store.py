#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 16:31
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: neo4j_store.py

import json
from typing import List, Any, Optional

try:
    from neo4j import GraphDatabase, AsyncGraphDatabase
    import pandas as pd
except ImportError:
    raise ImportError(
        "The functionality you are trying to use requires the neo4j and pandas package. "
        "You can install it by running: pip install neo4j pandas"
    )


from agentuniverse.agent.action.knowledge.store.graph_document import GraphDocument
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class Neo4jStore(Store):
    uri: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    driver: Any = None
    async_driver: Any = None

    def _new_client(self) -> Any:
        if self.database:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password), database=self.database)
        else:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def _new_async_client(self) -> Any:
        if self.database:
            self.async_driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password), database=self.database
            )
        else:
            self.async_driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def execute_cypher(self, query_str, param=None, return_data=True):
        df_result = self._execute_cypher(self.driver.session(), query_str, param, return_data)
        return df_result

    @staticmethod
    def _execute_cypher(session, query_str, param=None, return_data=True):
        df_result = pd.DataFrame()
        if param is None:
            result = session.run(query_str)
        else:
            result = session.run(query_str, **param)

        if return_data:
            result_list = []
            for resulti in result:
                result_list.append(dict(resulti))

            df_result = pd.DataFrame(result_list)
        session.close()
        return df_result

    def query(self, query: Query, **kwargs) -> List[Document]:
        query_type = query.ext_info.get("query_type", "")

        if query_type == "direct_cypher":
            cypher_query = query.query_str
            query_params = query.ext_info.get("query_params", {})
            records = self.execute_cypher(cypher_query, query_params)
            return self._records_to_documents(cypher_query, records)

        elif query_type == "llm_generate_cypher":
            schema_info = self._get_graph_schema_info()

            llm_cypher = self._llm_generate_cypher(query.query_str, schema_info)
            query_params = query.ext_info.get("query_params", {})
            records = self.execute_cypher(llm_cypher, query_params)
            return self._records_to_documents(query.query_str, records)

        elif query_type == "node_ids_query":
            node_ids = query.query_str
            if not node_ids:
                return []
            cypher_query = self._build_node_ids_query(json.loads(query.query_str))
            query_params = query.ext_info.get("query_params", {})
            records = self.execute_cypher(cypher_query, query_params)
            return self._records_to_documents(node_ids, records)
        else:
            raise NotImplementedError("This query type is not allowed in neo4j store.")

    def _records_to_documents(self, text, records: pd.DataFrame) -> List[Document]:
        documents = [GraphDocument(text=text, graph_data=records)]

        return documents

    def _get_graph_schema_info(self) -> dict:
        cypher = "CALL apoc.meta.schema() YIELD value RETURN value"
        session = self.driver.session()
        try:
            result = session.run(cypher)
            schema = [record["value"] for record in result]
            if schema:
                return schema[0]
            return {}
        finally:
            session.close()

    def _llm_generate_cypher(self, natural_language_query: str, schema_info: dict) -> str:
        return "MATCH (n) RETURN n LIMIT 10"

    def _build_node_ids_query(self, node_ids: List[int]) -> str:
        ids_str = ", ".join(str(i) for i in node_ids)
        return f"MATCH (n) WHERE id(n) IN [{ids_str}] RETURN n"

    def insert_document(self, documents: List[Document], **kwargs: Any):
        session = self.driver.session()
        try:
            for doc in documents:
                cypher = f"""
                MERGE (d:Document {{id: '{doc.id}'}})
                SET d.text = $text,
                    d.metadata = $metadata
                """
                session.run(cypher, text=doc.text, metadata=doc.metadata)
        finally:
            session.close()

    def upsert_document(self, documents: List[Document], **kwargs):
        self.insert_document(documents, **kwargs)

    def update_document(self, documents: List[Document], **kwargs):
        session = self.driver.session()
        try:
            for doc in documents:
                cypher = f"""
                MATCH (d:Document {{id: '{doc.id}'}})
                SET d.text = $text,
                    d.metadata = $metadata
                """
                session.run(cypher, text=doc.text, metadata=doc.metadata)
        finally:
            session.close()

    def _initialize_by_component_configer(self, neo4j_store_configer: ComponentConfiger) -> "Neo4jStore":
        super()._initialize_by_component_configer(neo4j_store_configer)
        if hasattr(neo4j_store_configer, "uri"):
            self.uri = neo4j_store_configer.uri
        if hasattr(neo4j_store_configer, "user"):
            self.user = neo4j_store_configer.user
        if hasattr(neo4j_store_configer, "password"):
            self.password = neo4j_store_configer.password
        if hasattr(neo4j_store_configer, "database"):
            self.database = neo4j_store_configer.database
        return self
