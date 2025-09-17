# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:50
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: store.py
from typing import Any, List, Optional

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent_serve.web.post_fork_queue import add_post_fork


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
        # TODO: Store copy need to solve thread lock problem
        return self
