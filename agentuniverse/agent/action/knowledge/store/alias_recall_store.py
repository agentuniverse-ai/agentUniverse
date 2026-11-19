"""Sequential bounded glossary recall around an existing registered store."""
from copy import deepcopy

from pydantic import Field, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.rag_router.alias_query_router import AliasQueryRouter
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.store.document import Document


class AliasRecallStore(Store):
    """Original-first union of sequential literal-alias queries.

    Sequential within a call, not a cross-request database synchronization layer.
    The underlying store still owns its normal concurrency and timeout contract.
    """
    backend_store: StrictStr = ""
    planner: AliasQueryRouter = Field(default_factory=AliasQueryRouter)
    max_result_documents: StrictInt = Field(default=1000, ge=1, le=10000)
    max_result_chars: StrictInt = Field(default=2_000_000, ge=1)

    def _backend(self):
        if type(self.backend_store) is not str or not self.backend_store.strip():
            raise ValueError("backend_store must be a nonblank registered store name")
        if type(self.max_result_documents) is not int or not 1 <= self.max_result_documents <= 10000:
            raise ValueError("max_result_documents must be in [1,10000]")
        if type(self.max_result_chars) is not int or self.max_result_chars < 1:
            raise ValueError("max_result_chars must be a positive integer")
        self.planner._validate()
        store = StoreManager().get_instance_obj(self.backend_store, new_instance=False, strict=True)
        if not isinstance(store, Store) or isinstance(store, AliasRecallStore):
            raise ValueError("alias backend must be a non-alias Store; nested alias wrappers are unsupported")
        return store

    def _merge(self, output, seen, result):
        if not isinstance(result, list) or any(not isinstance(doc, Document) for doc in result):
            raise TypeError("alias backend must return a list of Documents")
        if len(result) > self.max_result_documents:
            raise ValueError("backend result exceeds max_result_documents")
        size = sum(len(doc.text or "") for doc in output)
        for doc in result:
            if type(doc.id) is not str or not doc.id:
                raise ValueError("backend results require nonempty string IDs")
            if doc.id not in seen:
                if len(output) >= self.max_result_documents:
                    raise ValueError("combined result exceeds max_result_documents")
                size += len(doc.text or "")
                if size > self.max_result_chars:
                    raise ValueError("combined result exceeds max_result_chars")
                seen.add(doc.id)
                output.append(deepcopy(doc))

    def query(self, query, **kwargs):
        backend = self._backend()
        routes = self.planner.rag_route(query, [self.backend_store])
        output, seen = [], set()
        for routed, _ in routes:
            self._merge(output, seen, backend.query(routed, **deepcopy(kwargs)))
        return output

    async def async_query(self, query, **kwargs):
        backend = self._backend()
        routes = self.planner.rag_route(query, [self.backend_store])
        output, seen = [], set()
        for routed, _ in routes:
            self._merge(output, seen, await backend.async_query(routed, **deepcopy(kwargs)))
        return output

    def insert_document(self, documents, **kwargs):
        return self._backend().insert_document(documents, **kwargs)

    def upsert_document(self, documents, **kwargs):
        return self._backend().upsert_document(documents, **kwargs)

    def update_document(self, documents, **kwargs):
        return self._backend().update_document(documents, **kwargs)

    def delete_document(self, document_id, **kwargs):
        return self._backend().delete_document(document_id, **kwargs)

    async def async_insert_document(self, documents, **kwargs):
        return await self._backend().async_insert_document(documents, **kwargs)

    async def async_upsert_document(self, documents, **kwargs):
        return await self._backend().async_upsert_document(documents, **kwargs)

    async def async_update_document(self, documents, **kwargs):
        return await self._backend().async_update_document(documents, **kwargs)

    async def async_delete_document(self, document_id, **kwargs):
        return await self._backend().async_delete_document(document_id, **kwargs)

    def _initialize_by_component_configer(self, config):
        planner = AliasQueryRouter().initialize_by_component_configer(config)
        backend = getattr(config, "backend_store", "")
        limit = getattr(config, "max_result_documents", 1000)
        characters = getattr(config, "max_result_chars", 2_000_000)
        if type(backend) is not str or not backend.strip() or type(limit) is not int or not 1 <= limit <= 10000:
            raise ValueError("invalid backend_store or max_result_documents")
        if type(characters) is not int or characters < 1:
            raise ValueError("invalid max_result_chars")
        super()._initialize_by_component_configer(config)
        self.backend_store, self.planner, self.max_result_documents = backend, planner, limit
        self.max_result_chars = characters
        return self
