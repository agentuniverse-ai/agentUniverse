"""Opt-in, process-local exact-query caching around a registered store."""
import json
import math
import threading
import time
from collections import OrderedDict
from copy import deepcopy

from pydantic import Field, PrivateAttr, StrictBool, StrictFloat, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.document import Document


def _encoded(value):
    """Type-tag keys: never conflate bool/int/float, list/tuple or set/list.

    Unsupported objects, cycles and non-finite numbers bypass the cache. Dict
    order is retained because a provider may interpret ordered filter structures.
    """
    def tag(item):
        kind = type(item)
        if item is None:
            return ["null"]
        if kind in (bool, int, str):
            return [kind.__name__, item]
        if kind is float and math.isfinite(item):
            return ["float", item.hex()]
        if kind in (list, tuple):
            return [kind.__name__, [tag(child) for child in item]]
        if kind in (set, frozenset):
            children = [tag(child) for child in item]
            return [kind.__name__, sorted(children, key=lambda child: json.dumps(child, ensure_ascii=True))]
        if kind is dict and all(type(key) is str for key in item):
            return ["dict", [[key, tag(child)] for key, child in item.items()]]
        raise TypeError("uncacheable value")
    try:
        return json.dumps(tag(value), ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        return None


class CachedQueryStore(Store):
    """Cache exact successful query results; writes invalidate before and after.

    This is not a distributed consistency boundary. External writes/config changes
    require clear_cache or a new cache_revision; TTL merely bounds ordinary staleness.
    Backend methods remain responsible for concurrency, cancellation and timeouts.
    """
    backend_store: StrictStr = ""
    cache_revision: StrictStr = ""
    enabled: StrictBool = False
    ttl_seconds: StrictFloat = Field(default=30.0, gt=0, le=3600)
    max_entries: StrictInt = Field(default=128, ge=1)
    max_cache_bytes: StrictInt = Field(default=16 * 1024 * 1024, ge=1)
    max_entry_bytes: StrictInt = Field(default=256 * 1024, ge=1)
    max_key_bytes: StrictInt = Field(default=64 * 1024, ge=1)
    max_documents: StrictInt = Field(default=100, ge=1)
    _lock: object = PrivateAttr(default_factory=threading.RLock)
    _cache: object = PrivateAttr(default_factory=OrderedDict)
    _signature: object = PrivateAttr(default=None)
    _backend: object = PrivateAttr(default=None)
    _generation: int = PrivateAttr(default=0)
    _writers: int = PrivateAttr(default=0)
    _bytes: int = PrivateAttr(default=0)
    _hits: int = PrivateAttr(default=0)
    _misses: int = PrivateAttr(default=0)
    _bypasses: int = PrivateAttr(default=0)

    def _new_client(self):
        """Startup/post-fork hook; never inherit a parent's warm cache or lock.

        Like underlying store client setup, call only before serving requests.
        """
        self._lock = threading.RLock()
        self._cache = OrderedDict()
        self._signature = self._backend = None
        self._generation += 1
        self._writers = self._bytes = self._hits = self._misses = self._bypasses = 0

    def _options(self):
        if type(self.enabled) is not bool:
            raise ValueError("enabled must be boolean")
        for name in ("backend_store", "cache_revision"):
            value = getattr(self, name)
            if type(value) is not str or not value.strip() or len(value) > 256:
                raise ValueError(name + " must be a nonblank string up to 256 characters")
        if isinstance(self.ttl_seconds, bool) or not isinstance(self.ttl_seconds, (int, float)) or not math.isfinite(self.ttl_seconds) or not 0 < self.ttl_seconds <= 3600:
            raise ValueError("ttl_seconds must be finite and in (0, 3600]")
        names = ("max_entries", "max_cache_bytes", "max_entry_bytes", "max_key_bytes", "max_documents")
        for name in names:
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(name + " must be a positive integer")
        return (self.backend_store, self.cache_revision, self.enabled, self.ttl_seconds,
                *(getattr(self, name) for name in names))

    def _clear_locked(self):
        self._cache.clear()
        self._bytes = 0
        self._generation += 1

    def clear_cache(self):
        """Discard entries and prevent in-flight reads from repopulating them."""
        with self._lock:
            self._clear_locked()

    def cache_info(self):
        """Counters contain no query text, cache keys or document contents."""
        with self._lock:
            return {"entries": len(self._cache), "encoded_bytes": self._bytes,
                    "hits": self._hits, "misses": self._misses, "bypasses": self._bypasses,
                    "active_writes": self._writers}

    def _resolve(self):
        options = self._options()
        backend = StoreManager().get_instance_obj(options[0], new_instance=False, strict=True)
        if not isinstance(backend, Store) or isinstance(backend, CachedQueryStore):
            raise ValueError("backend_store must resolve to a non-cache Store; cache-wrapper chains are unsupported")
        with self._lock:
            if self._backend is not backend or self._signature != options:
                self._clear_locked()
                self._backend, self._signature = backend, options
        return backend, options

    def _lookup(self, mode, query, kwargs):
        backend, options = self._resolve()
        # Preserve arbitrary provider extension objects by delegating uncached.
        raw = _encoded([mode, query.__dict__, kwargs]) if options[2] and type(query) is Query else None
        with self._lock:
            token = self._generation
            if backend is not self._backend or options != self._signature or not options[2] or self._writers or raw is None or len(raw) > options[7]:
                self._bypasses += 1
                return backend, options, token, None, None
            now = time.monotonic()
            for key in list(self._cache):
                expires, _, size = self._cache[key]
                if expires <= now:
                    self._bytes -= size
                    del self._cache[key]
            if raw in self._cache:
                self._hits += 1
                self._cache.move_to_end(raw)
                return backend, options, token, raw, deepcopy(self._cache[raw][1])
            self._misses += 1
            return backend, options, token, raw, None

    def _finish(self, backend, options, token, key, result):
        if not isinstance(result, list) or any(not isinstance(doc, Document) for doc in result):
            raise TypeError("backend query must return a list of Documents")
        # Never hand out the cache-owned or backend-owned objects, including misses.
        output = deepcopy(result)
        if key is None or len(output) > options[8]:
            return output
        encoded = _encoded([doc.__dict__ for doc in output])
        if encoded is None:
            return output
        size = len(key) + len(encoded)
        if size > min(options[5], options[6]):
            return output
        snapshot = deepcopy(output)
        with self._lock:
            if self._writers or token != self._generation or backend is not self._backend or options != self._signature:
                return output
            if key in self._cache:
                self._bytes -= self._cache.pop(key)[2]
            while self._cache and (len(self._cache) >= options[4] or self._bytes + size > options[5]):
                self._bytes -= self._cache.popitem(last=False)[1][2]
            self._cache[key] = (time.monotonic() + options[3], snapshot, size)
            self._bytes += size
        return output

    def query(self, query: Query, **kwargs):
        backend, options, token, key, hit = self._lookup("sync", query, kwargs)
        if hit is not None:
            return hit
        result = backend.query(deepcopy(query), **deepcopy(kwargs))
        return self._finish(backend, options, token, key, result)

    async def async_query(self, query: Query, **kwargs):
        backend, options, token, key, hit = self._lookup("async", query, kwargs)
        if hit is not None:
            return hit
        result = await backend.async_query(deepcopy(query), **deepcopy(kwargs))
        return self._finish(backend, options, token, key, result)

    def _write_start(self):
        backend, _ = self._resolve()
        with self._lock:
            self._writers += 1
            self._clear_locked()
        return backend

    def _write_end(self):
        with self._lock:
            self._writers -= 1
            self._clear_locked()

    def _write(self, method, value, kwargs):
        backend = self._write_start()
        try:
            return getattr(backend, method)(value, **kwargs)
        finally:
            self._write_end()

    async def _async_write(self, method, value, kwargs):
        backend = self._write_start()
        try:
            return await getattr(backend, method)(value, **kwargs)
        finally:
            self._write_end()

    def insert_document(self, documents, **kwargs):
        return self._write("insert_document", documents, kwargs)

    def upsert_document(self, documents, **kwargs):
        return self._write("upsert_document", documents, kwargs)

    def update_document(self, documents, **kwargs):
        return self._write("update_document", documents, kwargs)

    def delete_document(self, document_id, **kwargs):
        return self._write("delete_document", document_id, kwargs)

    async def async_insert_document(self, documents, **kwargs):
        return await self._async_write("async_insert_document", documents, kwargs)

    async def async_upsert_document(self, documents, **kwargs):
        return await self._async_write("async_upsert_document", documents, kwargs)

    async def async_update_document(self, documents, **kwargs):
        return await self._async_write("async_update_document", documents, kwargs)

    async def async_delete_document(self, document_id, **kwargs):
        return await self._async_write("async_delete_document", document_id, kwargs)

    def _initialize_by_component_configer(self, config):
        names = ("backend_store", "cache_revision", "enabled", "ttl_seconds", "max_entries",
                 "max_cache_bytes", "max_entry_bytes", "max_key_bytes", "max_documents")
        validated = CachedQueryStore(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        self.clear_cache()
        return self
