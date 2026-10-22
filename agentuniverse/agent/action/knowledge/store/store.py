# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:50
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: store.py
import logging
from copy import deepcopy
from typing import Any, List, Optional

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent_serve.web.post_fork_queue import add_post_fork

logger = logging.getLogger(__name__)


class Store(ComponentBase):
    """The basic class for the knowledge store.

    Store of the knowledge, store class is used to store knowledge
    and provide retrieval capabilities,
    vector storage, such as ChromaDB store, Qdrant Store, or non-vector storage, such as Redis Store.
    """
    component_type: ComponentEnum = ComponentEnum.STORE
    name: Optional[str] = None
    description: Optional[str] = None
    client: Any = None
    async_client: Any = None

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def _new_client(self) -> Any:
        """Initialize the client，like database connection or local file create."""
        pass

    def _new_async_client(self) -> Any:
        """Initialize the async client."""
        pass

    def _initialize_by_component_configer(self,
                                         store_configer: ComponentConfiger) \
            -> 'Store':
        """Initialize the store by the ComponentConfiger object.

        Args:
            store_configer(ComponentConfiger): A configer contains store
            basic info. The client will be created in post fork due to
            conflicts that may occur in a multithreaded scenario.
        Returns:
            Store: A store instance.
        """
        if store_configer.name:
            self.name = store_configer.name
        if store_configer.description:
            self.description = store_configer.description
        add_post_fork(self._new_client)
        add_post_fork(self._new_async_client)
        return self

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query documents."""
        raise NotImplementedError

    async def async_query(self, query: Query, **kwargs) -> List[Document]:
        """Asynchronously query documents."""
        raise NotImplementedError

    def insert_document(self, documents: List[Document], **kwargs):
        """Insert documents into the store."""
        raise NotImplementedError

    async def async_insert_document(self, documents: List[Document], **kwargs):
        """Asynchronously insert documents into the store."""
        raise NotImplementedError

    def delete_document(self, document_id: str, **kwargs):
        """Delete the specific document by the document id."""
        raise NotImplementedError

    async def async_delete_document(self, document_id: str, **kwargs):
        """Asynchronously delete the specific document by the document id."""
        raise NotImplementedError

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert document into the store."""
        raise NotImplementedError

    async def async_upsert_document(self, documents: List[Document], **kwargs):
        """Asynchronously upsert documents into the store."""
        raise NotImplementedError

    def update_document(self, documents: List[Document], **kwargs):
        """Update document into the store."""
        raise NotImplementedError

    async def async_update_document(self, documents: List[Document], **kwargs):
        """Asynchronously update documents into the store."""
        raise NotImplementedError

    def create_copy(self):
        """Copy mutable store state while sharing live runtime resources.

        Every ``new_instance=True`` caller gets independent configuration
        and document state, including nested embeddings, keywords and
        metadata. Live resources stay shared by reference, at two levels:

        * ``client`` / ``async_client`` are always shared — their
          connections and locks must not be duplicated — and the deepcopy
          memo preserves references to them inside nested state (including
          aliases).
        * any *other* field whose value cannot be deep-copied falls back to
          the shared reference instead of failing the copy. Built-in
          subclasses keep opaque runtime resources outside the client
          fields — ``SQLiteStore`` holds its live ``sqlite3.Connection`` in
          ``conn``, ``FAISSStore`` holds a native index in ``faiss_index``
          — and such objects (connections, native handles, locks, sockets)
          are not picklable. Sharing them matches the client policy, and a
          component whose state is entirely copyable still receives a fully
          isolated copy.

        The fallback keeps ``create_copy`` compatible with every existing
        store implementation: an initialized built-in store must never
        start raising ``TypeError`` when a caller requests a new instance
        (review regression, issue #1183).
        """
        copied = self.model_copy()
        memo = {id(self.client): self.client, id(self.async_client): self.async_client}
        for name in type(self).model_fields:
            if name in ("client", "async_client"):
                # Live clients stay shared; the shallow copy already
                # references them.
                continue
            value = getattr(self, name, None)
            if value is None or id(value) in memo:
                continue
            try:
                setattr(copied, name, deepcopy(value, memo))
            except Exception as exc:
                # Uncopyable opaque runtime resource (live connection,
                # native index, lock, socket): share the reference,
                # mirroring the client policy.
                logger.debug(
                    "Store.create_copy shares uncopyable field %r by reference: %s", name, exc)
                continue
        private = getattr(self, "__pydantic_private__", None)
        if private:
            copied_private = {}
            for key, value in private.items():
                try:
                    copied_private[key] = deepcopy(value, memo)
                except Exception as exc:
                    # Same sharing fallback as model fields above.
                    logger.debug(
                        "Store.create_copy shares uncopyable private attribute %r by reference: %s",
                        key, exc)
                    copied_private[key] = value
            copied.__pydantic_private__ = copied_private
        return copied
