# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: hybrid_store.py
"""Composite knowledge store that delegates to multiple sub-stores.

``HybridKnowledgeStore`` is the user-facing base: it holds a list of child
store names and delegates every CRUD operation to *all* of them uniformly.
This is the recommended way for users to configure a multi-backend store
behind a single ``store`` field in Knowledge.

``LegacyHybridKnowledgeStore`` is a backward-compatible subclass
auto-created by ``Knowledge._resolve_store()`` when the deprecated
``stores`` (list) field is detected.  It preserves the original behaviour:
writes fan out to all children, reads go through a rag_router to select
which stores to query and then merge/deduplicate results.
"""
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from typing import Optional, List, Any

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER


class HybridKnowledgeStore(Store):
    """A composite Store that delegates all operations to sub-stores.

    Every CRUD method (insert / update / delete / query) is fanned out to
    *all* child stores.  For ``query``, results from all stores are merged
    and deduplicated by document id.

    Can be configured via YAML::

        name: 'my_hybrid_store'
        description: 'vector + kv hybrid'
        store_names:
          - chroma_store
          - sqlite_store
        metadata:
          type: 'STORE'
          module: agentuniverse.agent.action.knowledge.store.hybrid_store
          class: HybridKnowledgeStore

    Attributes:
        store_names: List of child store instance names.
    """

    store_names: Optional[List[str]] = []
    _executor: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def executor(self) -> ThreadPoolExecutor:
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=10,
                thread_name_prefix="HybridStore"
            )
        return self._executor

    def _initialize_by_component_configer(self, store_configer: ComponentConfiger) -> 'HybridKnowledgeStore':
        super()._initialize_by_component_configer(store_configer)
        if getattr(store_configer, 'store_names', None):
            self.store_names = store_configer.store_names
        return self

    def _iter_stores(self):
        """Yield resolved Store instances for all child stores."""
        for name in (self.store_names or []):
            store = StoreManager().get_instance_obj(name)
            if store:
                yield store

    # ================================================================
    # Synchronous interface
    # ================================================================

    def insert_document(self, documents: List[Document], **kwargs):
        """Fan out insert to all child stores."""
        futures = []
        for store in self._iter_stores():
            futures.append(self.executor.submit(store.insert_document, documents, **kwargs))
        wait(futures, return_when=ALL_COMPLETED)
        for future in futures:
            try:
                future.result()
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception in hybrid store insert: {e}")

    def update_document(self, documents: List[Document], **kwargs):
        """Fan out update to all child stores."""
        futures = []
        for store in self._iter_stores():
            futures.append(self.executor.submit(store.update_document, documents, **kwargs))
        wait(futures, return_when=ALL_COMPLETED)
        for future in futures:
            try:
                future.result()
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception in hybrid store update: {e}")

    def upsert_document(self, documents: List[Document], **kwargs):
        """Fan out upsert to all child stores."""
        futures = []
        for store in self._iter_stores():
            futures.append(self.executor.submit(store.upsert_document, documents, **kwargs))
        wait(futures, return_when=ALL_COMPLETED)
        for future in futures:
            try:
                future.result()
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception in hybrid store upsert: {e}")

    def delete_document(self, document_id: str, **kwargs):
        """Fan out delete to all child stores."""
        for store in self._iter_stores():
            try:
                store.delete_document(document_id, **kwargs)
            except Exception as e:
                LOGGER.error(f"Exception in hybrid store delete: {e}")

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query all child stores and merge/deduplicate results by doc id."""
        futures = []
        for store in self._iter_stores():
            futures.append(self.executor.submit(store.query, query, **kwargs))
        wait(futures, return_when=ALL_COMPLETED)

        retrieved_docs = {}
        for future in futures:
            try:
                result = future.result()
                for doc in result:
                    if doc.id not in retrieved_docs:
                        retrieved_docs[doc.id] = doc
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception in hybrid store query: {e}")
        return list(retrieved_docs.values())

    # ================================================================
    # Asynchronous interface
    # ================================================================

    async def async_insert_document(self, documents: List[Document], **kwargs):
        """Async fan out insert to all child stores."""
        tasks = [store.async_insert_document(documents, **kwargs) for store in self._iter_stores()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async hybrid store insert: {r}")

    async def async_update_document(self, documents: List[Document], **kwargs):
        """Async fan out update to all child stores."""
        tasks = [store.async_update_document(documents, **kwargs) for store in self._iter_stores()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async hybrid store update: {r}")

    async def async_upsert_document(self, documents: List[Document], **kwargs):
        """Async fan out upsert to all child stores."""
        tasks = [store.async_upsert_document(documents, **kwargs) for store in self._iter_stores()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async hybrid store upsert: {r}")

    async def async_delete_document(self, document_id: str, **kwargs):
        """Async fan out delete to all child stores."""
        tasks = [store.async_delete_document(document_id, **kwargs) for store in self._iter_stores()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async hybrid store delete: {r}")

    async def async_query(self, query: Query, **kwargs) -> List[Document]:
        """Async query all child stores and merge/deduplicate results."""
        tasks = [store.async_query(query, **kwargs) for store in self._iter_stores()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        retrieved_docs = {}
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async hybrid store query: {r}")
                continue
            for doc in r:
                if doc.id not in retrieved_docs:
                    retrieved_docs[doc.id] = doc
        return list(retrieved_docs.values())


class LegacyHybridKnowledgeStore(HybridKnowledgeStore):
    """Backward-compatible hybrid that uses rag_router for query routing.

    Writes fan out to all ``store_names`` (inherited from parent).
    Reads go through ``rag_router`` to determine which stores to query,
    then merge/deduplicate results — preserving the original Knowledge
    query behaviour.

    This class is auto-constructed by ``Knowledge._resolve_store()`` when
    the legacy ``stores`` (list) field is detected.

    Attributes:
        rag_router: The name of the RagRouter instance to use for query routing.
        post_processors: Doc processor names for post-processing query results.
    """

    rag_router: str = "base_router"
    post_processors: Optional[List[str]] = []

    def _route_and_query(self, query: Query, **kwargs) -> List[Document]:
        """Route query via rag_router and merge results from selected stores."""
        from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager

        query_tasks = RagRouterManager().get_instance_obj(
            self.rag_router
        ).rag_route(query, self.store_names or [])

        futures = []
        for q, store_name in query_tasks:
            store = StoreManager().get_instance_obj(store_name)
            if store:
                futures.append(self.executor.submit(store.query, q, **kwargs))

        wait(futures, return_when=ALL_COMPLETED)

        retrieved_docs = {}
        for future in futures:
            try:
                result = future.result()
                for doc in result:
                    if doc.id not in retrieved_docs:
                        retrieved_docs[doc.id] = doc
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Exception in legacy hybrid store query: {e}")
        return list(retrieved_docs.values())

    async def _async_route_and_query(self, query: Query, **kwargs) -> List[Document]:
        """Async route query via rag_router and merge results."""
        from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager

        query_tasks = await RagRouterManager().get_instance_obj(
            self.rag_router
        ).async_rag_route(query, self.store_names or [])

        tasks = []
        for q, store_name in query_tasks:
            store = StoreManager().get_instance_obj(store_name)
            if store:
                tasks.append(store.async_query(q, **kwargs))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        retrieved_docs = {}
        for r in results:
            if isinstance(r, Exception):
                LOGGER.error(f"Exception in async legacy hybrid store query: {r}")
                continue
            for doc in r:
                if doc.id not in retrieved_docs:
                    retrieved_docs[doc.id] = doc
        return list(retrieved_docs.values())

    # Override query to use rag_router
    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query using rag_router to select stores, then merge results."""
        return self._route_and_query(query, **kwargs)

    async def async_query(self, query: Query, **kwargs) -> List[Document]:
        """Async query using rag_router to select stores, then merge results."""
        return await self._async_route_and_query(query, **kwargs)
