# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
# @Time    : 2024/3/22 15:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge.py
import os
import re
import traceback
from copy import deepcopy
from typing import Optional, Dict, List, Any
from concurrent.futures import wait, ALL_COMPLETED

from langchain_core.utils.json import parse_json_markdown
from langchain.tools import Tool as LangchainTool

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import QueryParaphraser
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser_manager import QueryParaphraserManager
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.annotation.trace import trace_knowledge
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.agent_serve.web.thread_with_result import ThreadPoolExecutorWithReturnValue

# Metadata key under which :meth:`Knowledge.query_knowledge` stamps the store
# code that recalled each document. Fusion post-processors (e.g. the
# ReciprocalRankFusionProcessor) read this field via their ``channel_key``
# config to tell retrieval channels apart.
RECALL_CHANNEL_KEY = "recall_channel"


class Knowledge(ComponentBase):
    """
    The basic class for the knowledge model.

    Attributes:
        name (str): The name of the knowledge.

        description (str): The description of the knowledge.

        stores (List[str]): The stores for the knowledge, which are used to store knowledge
            and provide retrieval capabilities, such as ChromaDB store, Redis Store or Qdrant Store.

        query_paraphrasers (List[str]): Query paraphrasers used to paraphrase the original query string,
            such as extracting keywords and splitting into sub-queries.

        insert_processors (List[str]): DocProcessors used in the knowledge insertion step,
            such as text splitter and text cleaner.

        rag_router (str): RAG router used to decide which stores to use in
            the RAG step.

        post_processors (List[str]): DocProcessors used in the RAG step to process retrieved
            documents, such as reranking and filtering.

        readers (Dict[str, str]): The readers of the knowledge, which are used to load data and generate knowledge.
            Each reader refers to a specific file type.

        insert_executor (ThreadPoolExecutor): Used for performing insert and search
        operations concurrently in multiple stores.

        ext_info (Optional[Dict]): The extended information of the knowledge.
    """

    class Config:
        arbitrary_types_allowed = True

    name: str = ""
    description: Optional[str] = None
    stores: List[str] = []
    query_paraphrasers: List[str] = []
    insert_processors: List[str] = []
    update_processors: List[str] = []
    rag_router: str = "base_router"
    post_processors: List[str] = []
    readers: Dict[str, str] = dict()
    insert_executor: Optional[ThreadPoolExecutorWithReturnValue] = None
    query_executor: Optional[ThreadPoolExecutorWithReturnValue] = None
    tracing: Optional[bool] = None
    ext_info: Optional[Dict] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.KNOWLEDGE, **kwargs)
        self.insert_executor = ThreadPoolExecutorWithReturnValue(
            max_workers=5,
            thread_name_prefix="Knowledge store"
        )
        self.query_executor = ThreadPoolExecutorWithReturnValue(
            max_workers=10,
            thread_name_prefix="Knowledge query"
        )

    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        # check if source is a local file or remote url
        if kwargs.get("source_path"):
            source_path = kwargs.get("source_path")
        else:
            raise Exception("No file to load.")
        url_pattern = re.compile(
            r'^(https?:\/\/)?'
            r'((([a-zA-Z0-9]{1,256}\.[a-zA-Z0-9]{1,6})|'
            r'(\d{1,3}\.){3}\d{1,3})'
            r'(:\d{1,5})?)'
            r'(\/[a-zA-Z0-9@:%._\+~#=]*)*\/?'
            r'(\?[a-zA-Z0-9@:%._\+~#&//=]*)?$'
        )

        if url_pattern.match(source_path):
            source_type = "url"
        elif os.path.isfile(source_path):
            source_type = os.path.splitext(source_path)[1][1:]
        else:
            raise Exception(f"Knowledge load data error: Unknown source type:{source_path}")
        if source_type in self.readers:
            reader = ReaderManager().get_instance_obj(self.readers[source_type])
        else:
            reader = ReaderManager().get_file_default_reader(source_type)
        return reader.load_data(source_path)

    def _insert_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.insert_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs)
        return origin_docs

    def _update_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.update_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs)
        return origin_docs

    def _rag_post_process(self, origin_docs: List[Document], query: Query):
        for _processor_code in self.post_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs, query=query)
        return origin_docs

    def _channel_fusion_enabled(self) -> bool:
        """Return whether a configured post-processor opts into per-channel recall.

        A fusion processor (e.g. ``ReciprocalRankFusionProcessor``) declares a
        ``channel_key`` — the metadata field it reads to tell retrieval channels
        apart. Only when such a processor is present does :meth:`query_knowledge`
        keep per-channel copies of a document; otherwise it preserves the default
        retrieval contract and collapses cross-store duplicates to a single
        document, so an optional fusion processor can never change the output of
        pipelines that do not use it.
        """
        for _processor_code in self.post_processors:
            try:
                _processor = DocProcessorManager().get_instance_obj(_processor_code)
            except Exception:  # noqa: BLE001 - an unresolved processor is not channel-aware
                continue
            if getattr(_processor, "channel_key", None):
                return True
        return False

    def _paraphrase_query(self, origin_query: Query) -> Query:
        for _paraphraser_code in self.query_paraphrasers:
            query_paraphraser: QueryParaphraser = QueryParaphraserManager().get_instance_obj(
                _paraphraser_code)
            origin_query = query_paraphraser.query_paraphrase(origin_query)
        return origin_query

    def insert_knowledge(self, **kwargs) -> None:
        """Insert the knowledge.

        Load data by the reader and insert the documents into the store.
        """
        document_list: List[Document] = self._load_data(**kwargs)
        document_list = self._insert_process(document_list)
        futures = []
        if "stores" in kwargs:
            stores = kwargs["stores"]
        else:
            stores = self.stores
        for _store_code in stores:
            futures.append(
                self.insert_executor.submit(
                    StoreManager().get_instance_obj(_store_code, strict=True).insert_document,
                    document_list))
        wait(futures, return_when=ALL_COMPLETED)
        for future in futures:
            try:
                future.result()
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception occurred in knowledge insert: {e}")
        LOGGER.info("Knowledge insert complete.")

    def update_knowledge(self, **kwargs) -> None:
        """Update the knowledge.

        Load data by the reader and update the documents into the store.
        """
        document_list: List[Document] = self._load_data(**kwargs)
        document_list = self._update_process(document_list)
        futures = []
        if "stores" in kwargs:
            stores = kwargs["stores"]
        else:
            stores = self.stores
        for _store_code in stores:
            futures.append(
                self.insert_executor.submit(
                    StoreManager().get_instance_obj(_store_code, strict=True).update_document,
                    document_list))
        wait(futures, return_when=ALL_COMPLETED)
        for future in futures:
            try:
                future.result()
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception occurred in knowledge update: {e}")
        LOGGER.info("Knowledge update complete.")

    def _route_rag(self, query: Query):
        return RagRouterManager().get_instance_obj(self.rag_router, strict=True).rag_route(query, self.stores)

    @trace_knowledge
    def query_knowledge(self, **kwargs) -> List[Document]:
        """Query the knowledge.

        Query documents from the store and return the results.
        """
        query = Query(**kwargs)
        query = self._paraphrase_query(query)
        query_tasks = self._route_rag(query)

        futures = []
        for query_task in query_tasks:
            futures.append((
                self.query_executor.submit(
                    StoreManager().get_instance_obj(query_task[1], strict=True).query,
                    query_task[0]),
                query_task[1],
            ))
        wait([future for future, _ in futures], return_when=ALL_COMPLETED)
        # Channel-aware recall is opt-in: only when a configured post-processor
        # declares a channel_key (i.e. it is a fusion processor that needs to
        # tell retrieval channels apart) do we keep per-channel copies of a
        # document. Without such a processor the merge keeps the default
        # retrieval contract — a document recalled by several stores is
        # returned exactly once — so adding an optional fusion processor never
        # changes the output of pipelines that do not use it.
        preserve_channels = self._channel_fusion_enabled()
        retrieved_docs = {}
        for future, store_code in futures:
            try:
                task_result = future.result()
                for _doc in task_result:
                    if preserve_channels:
                        # Stamp the store code that recalled this document and
                        # de-duplicate per channel (id + channel): a document
                        # recalled by several stores is kept once per store,
                        # while a duplicate within the same store is dropped.
                        metadata = dict(_doc.metadata or {})
                        metadata[RECALL_CHANNEL_KEY] = store_code
                        _doc.metadata = metadata
                        dedup_identity = (_doc.id, store_code)
                    else:
                        # Default contract: collapse cross-store duplicates to
                        # a single document (first recall wins) and stamp no
                        # extra metadata, so the output matches master.
                        dedup_identity = _doc.id
                    if dedup_identity not in retrieved_docs:
                        retrieved_docs[dedup_identity] = _doc
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception occurred in knowledge query: {e}")
        retrieved_docs = list(retrieved_docs.values())
        retrieved_docs = self._rag_post_process(retrieved_docs, query)
        return retrieved_docs

    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        """Transfer list docs to llm input"""
        retrieved_texts = [doc.text for doc in retrieved_docs]
        return "\n=========================================\n".join(retrieved_texts)

    def _initialize_by_component_configer(self,
                                          knowledge_configer: ComponentConfiger) \
            -> 'Knowledge':
        """Initialize the reader by the ComponentConfiger object.

        Args:
            reader_configer(ComponentConfiger): A configer contains reader
            basic info.
        Returns:
            Reader: A reader instance.
        """
        if knowledge_configer.name:
            self.name = knowledge_configer.name
        if knowledge_configer.description:
            self.description = knowledge_configer.description
        if hasattr(knowledge_configer, "stores"):
            self.stores = knowledge_configer.stores
        if hasattr(knowledge_configer, "query_paraphrasers"):
            self.query_paraphrasers = knowledge_configer.query_paraphrasers
        if hasattr(knowledge_configer, "insert_processors"):
            self.insert_processors = knowledge_configer.insert_processors
        if hasattr(knowledge_configer, "update_processors"):
            self.update_processors = knowledge_configer.update_processors
        if hasattr(knowledge_configer, "rag_router"):
            self.rag_router = knowledge_configer.rag_router
        if hasattr(knowledge_configer, "post_processors"):
            self.post_processors = knowledge_configer.post_processors
        if hasattr(knowledge_configer, "readers"):
            self.readers = knowledge_configer.readers
        if hasattr(knowledge_configer, "tracing"):
            self.tracing = knowledge_configer.tracing
        return self

    def langchain_query(self, query: str) -> str:
        """Query the knowledge using LangChain.

        Query documents from the store and return the results.
        """
        parse_query = parse_json_markdown(query)
        knowledge = self.query_knowledge(**parse_query)
        return "This is Query Result:\n" + self.to_llm(knowledge)

    async def async_langchain_query(self, query: str) -> str:
        """Query the knowledge using LangChain.

        Query documents from the store and return the results.
        """
        parse_query = parse_json_markdown(query)
        knowledge = await asyncio.to_thread(self.query_knowledge, **parse_query)
        return "This is Query Result:\n" + self.to_llm(knowledge)

    def as_langchain_tool(self) -> LangchainTool:
        """Convert the Knowledge object to a LangChain tool.

        Returns:
            Any: the LangChain tool object
        """
        args_description = """
        This is a knowledge base tool, which stores the content you may need. To use this tool, you need to give a json string with the following format:
        ```json
        {
            "query_str": "<your query here>",
            "similarity_top_k": <number of results to return>,
        }
        ```
        """
        return LangchainTool(
            name=self.name,
            description=self.description or '' + args_description,
            func=self.langchain_query,
        )

    async def async_as_langchain_tool(self) -> LangchainTool:
        """Convert the Knowledge object to a LangChain tool.

        Returns:
            Any: the LangChain tool object
        """
        args_description = """
        This is a knowledge base tool, which stores the content you may need. To use this tool, you need to give a json string with the following format:
        ```json
        {
            "query_str": "<your query here>",
            "similarity_top_k": <number of results to return>,
        }
        ```
        """
        return LangchainTool(
            name=self.name,
            description=self.description or '' + args_description,
            func=self.async_langchain_query,
        )

    def create_copy(self):
        copied = self.model_copy()
        copied.stores = self.stores.copy()
        copied.query_paraphrasers = self.query_paraphrasers.copy()
        copied.insert_processors = self.insert_processors.copy()
        copied.update_processors = self.update_processors.copy()
        copied.post_processors = self.post_processors.copy()
        copied.readers = deepcopy(self.readers)
        if self.ext_info is not None:
            copied.ext_info = deepcopy(self.ext_info)
        return copied
