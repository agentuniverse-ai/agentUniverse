# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge.py
import os
import re
from copy import deepcopy
from typing import Optional, Dict, List, Any

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import QueryParaphraser
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser_manager import QueryParaphraserManager
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.annotation.trace import trace_knowledge
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.logging_util import LOGGER


class Knowledge(ComponentBase):
    """The basic class for the knowledge model.

    Knowledge manages the full lifecycle of knowledge data: loading,
    processing, storing, and retrieving documents for RAG pipelines.

    Storage resolution (in priority order):
        1. ``store`` (new, recommended) — a single Store name.
           All CRUD operations go through this one store.  It can be a
           simple store or a user-defined composite (e.g. a custom
           ``HybridKnowledgeStore`` with vector + SQL backends).
        2. ``stores`` (legacy) — if ``store`` is not set, these legacy
           fields are used.  A ``LegacyHybridKnowledgeStore`` is
           auto-constructed to wrap them, preserving the old fan-out-write
           / rag-router-read behavior behind a unified Store interface.

    Attributes:
        name: The name of the knowledge.
        description: The description of the knowledge.
        store: The name of the single Store to use (recommended).
        stores: (Deprecated) List of store names for write fan-out.
        query_paraphrasers: Query paraphrasers for the original query.
        insert_processors: DocProcessors for the knowledge insertion step.
        update_processors: DocProcessors for the knowledge update step.
        rag_router: RAG router for deciding which stores to query.
        post_processors: DocProcessors for post-processing retrieved docs.
        readers: Mapping of file type to reader instance name.
        ext_info: Extended information of the knowledge.
    """

    class Config:
        arbitrary_types_allowed = True

    name: str = ""
    description: Optional[str] = None

    # New: single store entry point (recommended)
    store: Optional[str] = None

    # Deprecated: legacy multi-store fields, kept for backward compatibility.
    # If store is set, these are ignored.
    stores: List[str] = []

    query_paraphrasers: List[str] = []
    insert_processors: List[str] = []
    update_processors: List[str] = []
    rag_router: str = "base_router"
    post_processors: List[str] = []
    readers: Dict[str, str] = dict()
    tracing: Optional[bool] = None
    ext_info: Optional[Dict] = None

    # Cached resolved store instance (not serialized)
    _resolved_store: Optional[Store] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.KNOWLEDGE, **kwargs)

    # ================================================================
    # Store resolution
    # ================================================================

    def _resolve_store(self) -> Optional[Store]:
        """Resolve the effective Store instance.

        Resolution order:
            1. If ``store`` is set → look it up from the manager.
            2. Else if legacy ``stores`` is set → build a
               ``LegacyHybridKnowledgeStore`` wrapping them.
            3. Otherwise → None.

        The result is cached in ``_resolved_store`` for the lifetime of
        this Knowledge instance.  Call ``_invalidate_store()`` if config
        changes.

        Returns:
            The resolved Store, or None if nothing is configured.
        """
        if self._resolved_store is not None:
            return self._resolved_store

        # Path 1: new single-store field
        if self.store:
            self._resolved_store = StoreManager().get_instance_obj(self.store)
            return self._resolved_store

        # Path 2: legacy multi-store → wrap in LegacyHybridKnowledgeStore
        if self.stores:
            from agentuniverse.agent.action.knowledge.store.hybrid_store import \
                LegacyHybridKnowledgeStore
            hybrid = LegacyHybridKnowledgeStore()
            hybrid.name = f'_legacy_hybrid_{self.name or "knowledge"}'
            hybrid.store_names = list(self.stores)
            hybrid.rag_router = self.rag_router
            hybrid.post_processors = list(self.post_processors)
            self._resolved_store = hybrid
            return self._resolved_store

        return None

    def _invalidate_store(self):
        """Clear cached store so next access re-resolves."""
        self._resolved_store = None

    # ================================================================
    # Internal pipeline helpers
    # ================================================================

    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the configured source."""
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

    async def _async_load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Async version of :meth:`_load_data`."""
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
        return await reader.async_load_data(source_path)

    def _insert_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.insert_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs)
        return origin_docs

    async def _async_insert_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.insert_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = await doc_processor.async_process_docs(origin_docs)
        return origin_docs

    def _update_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.update_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs)
        return origin_docs

    async def _async_update_process(self, origin_docs: List[Document]) -> List[Document]:
        for _processor_code in self.update_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = await doc_processor.async_process_docs(origin_docs)
        return origin_docs

    def _rag_post_process(self, origin_docs: List[Document], query: Query):
        for _processor_code in self.post_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = doc_processor.process_docs(origin_docs, query=query)
        return origin_docs

    async def _async_rag_post_process(self, origin_docs: List[Document], query: Query):
        for _processor_code in self.post_processors:
            doc_processor: DocProcessor = DocProcessorManager().get_instance_obj(_processor_code)
            origin_docs = await doc_processor.async_process_docs(origin_docs, query=query)
        return origin_docs

    def _paraphrase_query(self, origin_query: Query) -> Query:
        for _paraphraser_code in self.query_paraphrasers:
            query_paraphraser: QueryParaphraser = QueryParaphraserManager().get_instance_obj(
                _paraphraser_code)
            origin_query = query_paraphraser.query_paraphrase(origin_query)
        return origin_query

    async def _async_paraphrase_query(self, origin_query: Query) -> Query:
        for _paraphraser_code in self.query_paraphrasers:
            query_paraphraser: QueryParaphraser = QueryParaphraserManager().get_instance_obj(
                _paraphraser_code)
            origin_query = await query_paraphraser.async_query_paraphrase(origin_query)
        return origin_query

    # ================================================================
    # Insert
    # ================================================================

    def insert_knowledge(self, **kwargs) -> None:
        """Insert the knowledge.

        Load data by the reader and insert the documents into the store.
        """
        document_list: List[Document] = self._load_data(**kwargs)
        document_list = self._insert_process(document_list)

        resolved = self._resolve_store()
        if resolved:
            resolved.insert_document(document_list)
            LOGGER.info("Knowledge insert complete.")
        else:
            LOGGER.warning("No store configured for knowledge insert.")

    async def async_insert_knowledge(self, **kwargs) -> None:
        """Async version of :meth:`insert_knowledge`."""
        document_list: List[Document] = await self._async_load_data(**kwargs)
        document_list = await self._async_insert_process(document_list)

        resolved = self._resolve_store()
        if resolved:
            await resolved.async_insert_document(document_list)
            LOGGER.info("Knowledge insert complete.")
        else:
            LOGGER.warning("No store configured for knowledge insert.")

    # ================================================================
    # Update
    # ================================================================

    def update_knowledge(self, **kwargs) -> None:
        """Update the knowledge.

        Load data by the reader and update the documents in the store.
        """
        document_list: List[Document] = self._load_data(**kwargs)
        document_list = self._update_process(document_list)

        resolved = self._resolve_store()
        if resolved:
            resolved.update_document(document_list)
            LOGGER.info("Knowledge update complete.")
        else:
            LOGGER.warning("No store configured for knowledge update.")

    async def async_update_knowledge(self, **kwargs) -> None:
        """Async version of :meth:`update_knowledge`."""
        document_list: List[Document] = await self._async_load_data(**kwargs)
        document_list = await self._async_update_process(document_list)

        resolved = self._resolve_store()
        if resolved:
            await resolved.async_update_document(document_list)
            LOGGER.info("Knowledge update complete.")
        else:
            LOGGER.warning("No store configured for knowledge update.")

    # ================================================================
    # Query
    # ================================================================

    @trace_knowledge
    def query_knowledge(self, **kwargs) -> List[Document]:
        """Query the knowledge.

        Query documents from the store and return the results.
        """
        query = Query(**kwargs)
        query = self._paraphrase_query(query)

        resolved = self._resolve_store()
        if not resolved:
            LOGGER.warning("No store configured for knowledge query.")
            return []

        retrieved_docs = resolved.query(query)
        retrieved_docs = self._rag_post_process(retrieved_docs, query)
        return retrieved_docs

    async def async_query_knowledge(self, **kwargs) -> List[Document]:
        """Async version of :meth:`query_knowledge`."""
        query = Query(**kwargs)
        query = await self._async_paraphrase_query(query)

        resolved = self._resolve_store()
        if not resolved:
            LOGGER.warning("No store configured for knowledge query.")
            return []

        retrieved_docs = await resolved.async_query(query)
        retrieved_docs = await self._async_rag_post_process(retrieved_docs, query)
        return retrieved_docs

    # ================================================================
    # Utilities
    # ================================================================

    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        """Transfer list docs to llm input"""
        retrieved_texts = [doc.text for doc in retrieved_docs]
        return "\n=========================================\n".join(retrieved_texts)

    def as_tool_schema(self) -> dict:
        """Return the OpenAI function-calling schema when this knowledge is
        exposed as a tool.

        Subclasses can override this method to customise the tool name,
        description, or parameters schema.  For example, a knowledge base
        that supports filtering by date could add extra parameters::

            def as_tool_schema(self) -> dict:
                schema = super().as_tool_schema()
                schema['function']['parameters']['properties']['date_filter'] = {
                    'type': 'string',
                    'description': 'ISO date to filter documents by.',
                }
                return schema

        Returns:
            dict in OpenAI ``tools`` format::

                {
                    "type": "function",
                    "function": {
                        "name": "...",
                        "description": "...",
                        "parameters": { ... }
                    }
                }
        """
        from agentuniverse.agent.action.knowledge.knowledge_tool import (
            KNOWLEDGE_TOOL_PREFIX,
        )
        return {
            "type": "function",
            "function": {
                "name": f"{KNOWLEDGE_TOOL_PREFIX}{self.name}",
                "description": (
                    self.description
                    or f"Search the '{self.name}' knowledge base. "
                       f"Use this tool to retrieve relevant documents "
                       f"by providing a query string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "The search query to retrieve relevant "
                                "documents from the knowledge base."
                            ),
                        }
                    },
                    "required": ["query"],
                },
            },
        }

    # ================================================================
    # Configuration
    # ================================================================

    def _initialize_by_component_configer(self,
                                          knowledge_configer: ComponentConfiger) \
            -> 'Knowledge':
        """Initialize the knowledge by the ComponentConfiger object.

        Args:
            knowledge_configer(ComponentConfiger): A configer contains knowledge
            basic info.
        Returns:
            Knowledge: A knowledge instance.
        """
        if knowledge_configer.name:
            self.name = knowledge_configer.name
        if knowledge_configer.description:
            self.description = knowledge_configer.description
        if hasattr(knowledge_configer, "store"):
            self.store = knowledge_configer.store
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

        # Invalidate cached store so it re-resolves with new config
        self._invalidate_store()

        return self

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
        # Clear cached store on copy — each copy resolves independently
        copied._resolved_store = None
        return copied
