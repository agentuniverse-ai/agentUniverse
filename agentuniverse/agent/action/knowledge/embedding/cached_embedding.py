"""Opt-in bounded in-memory caching for deterministic embedding providers."""
import json
import math
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass, field
from threading import RLock
from typing import List

from langchain_core.embeddings import Embeddings
from pydantic import PrivateAttr, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager


def _option_key(value):
    """Encode supported option values without JSON's implicit type coercions."""
    def encode(item):
        kind = type(item)
        if item is None:
            return ["none"]
        if kind in (str, int, bool):
            return [kind.__name__, item]
        if kind is float:
            if not math.isfinite(item):
                raise ValueError("embedding options must contain finite numbers")
            return ["float", item.hex()]
        if kind in (list, tuple):
            return [kind.__name__, [encode(child) for child in item]]
        if kind is dict:
            if any(type(key) is not str for key in item):
                raise ValueError("embedding option mappings require string keys")
            # Preserve order as well: arbitrary provider options may be ordered.
            return ["dict", [[key, encode(child)] for key, child in item.items()]]
        raise TypeError("unsupported embedding option type: " + kind.__name__)
    try:
        return json.dumps(encode(value), ensure_ascii=True, separators=(",", ":"))
    except RecursionError as error:
        raise ValueError("embedding options must be acyclic and bounded in depth") from error


@dataclass
class _CacheState:
    cache: OrderedDict = field(default_factory=OrderedDict)
    lock: object = field(default_factory=RLock)
    backend: object = None
    generation: int = 0


class CachedEmbedding(Embedding):
    """Cache by backend identity, model, dimensions, version, options and text.

    Caller must bump cache_version when changing provider settings not exposed
    as model/dimensions. Concurrent misses may issue duplicate provider calls;
    there is no lock held across network IO and no cancellation of other calls.
    """
    backend_name: StrictStr = ""
    cache_version: StrictStr = ""
    max_entries: StrictInt = 1024
    _state: _CacheState = PrivateAttr(default_factory=_CacheState)

    def create_copy(self):
        """Copy configuration while sharing this registered component's cache.

        A normal manager lookup must not create a fresh cache or deepcopy locks.
        Namespace keys still isolate model/version/options; clearing a copy
        invalidates the shared cache and all its in-flight cache writes.
        """
        return self.model_copy(deep=False)

    def _validate_options(self):
        for value in (self.backend_name, self.cache_version):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("backend_name and cache_version must be nonblank")
        if type(self.max_entries) is not int or self.max_entries < 0:
            raise ValueError("max_entries must be a nonnegative integer")

    def clear_cache(self):
        """Discard retained texts/vectors. Does not cancel in-flight requests."""
        with self._state.lock:
            self._state.cache.clear()
            self._state.generation += 1

    def _prepare(self, texts, kwargs):
        self._validate_options()
        if not isinstance(texts, list) or any(not isinstance(text, str) for text in texts):
            raise ValueError("texts must be a list of strings")
        # Snapshot once for both key and provider call. Provider mutation cannot
        # alter caller-owned nested options or the already captured identity.
        call_options = deepcopy(kwargs)
        options = _option_key(call_options)
        backend = EmbeddingManager().get_instance_obj(self.backend_name, new_instance=False, strict=True)
        if not isinstance(backend, Embedding) or isinstance(backend, CachedEmbedding):
            raise ValueError("backend must be a non-caching Embedding component")
        found = {}
        missing = []
        with self._state.lock:
            if self._state.backend is not backend:
                self._state.backend = backend
                self._state.cache.clear()
                self._state.generation += 1
            namespace = (self._state.generation, backend.embedding_model_name, backend.embedding_dims,
                         self.cache_version, options)
            keys = [(namespace, text) for text in texts]
            while len(self._state.cache) > self.max_entries:
                self._state.cache.popitem(last=False)
            for key in dict.fromkeys(keys):
                if key in self._state.cache:
                    found[key] = self._state.cache[key]
                    self._state.cache.move_to_end(key)
                else:
                    missing.append(key)
        return backend, keys, found, missing, call_options

    def _finish(self, backend, keys, found, missing, vectors):
        if not isinstance(vectors, list) or len(vectors) != len(missing):
            raise ValueError("provider embedding count does not match missing texts")
        validated = []
        for vector in vectors:
            if not isinstance(vector, list) or not vector:
                raise ValueError("provider embeddings must be nonempty lists")
            if any(type(value) not in (int, float) or not math.isfinite(value) for value in vector):
                raise ValueError("provider embeddings must contain finite numbers")
            if backend.embedding_dims is not None and len(vector) != backend.embedding_dims:
                raise ValueError("provider embedding dimension mismatch")
            validated.append(tuple(vector))
        lengths = {len(vector) for vector in list(found.values()) + validated}
        if len(lengths) > 1:
            raise ValueError("provider embedding dimensions are inconsistent")
        # Validate the whole response before caching any part of the batch.
        with self._state.lock:
            for key, vector in zip(missing, validated):
                found[key] = vector
                if self.max_entries and key[0][0] == self._state.generation:
                    self._state.cache[key] = vector
                    self._state.cache.move_to_end(key)
            while len(self._state.cache) > self.max_entries:
                self._state.cache.popitem(last=False)
        return [list(found[key]) for key in keys]

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Embed cache misses synchronously; preserve duplicate input positions."""
        backend, keys, found, missing, call_options = self._prepare(texts, kwargs)
        vectors = backend.get_embeddings([key[1] for key in missing], **call_options) if missing else []
        return self._finish(backend, keys, found, missing, vectors)

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Await the provider's async method; exceptions/cancellation are not cached."""
        backend, keys, found, missing, call_options = self._prepare(texts, kwargs)
        vectors = await backend.async_get_embeddings([key[1] for key in missing], **call_options) if missing else []
        return self._finish(backend, keys, found, missing, vectors)

    def as_langchain(self):
        """Return an adapter using this cache for both query/document roles."""
        owner = self

        class Adapter(Embeddings):
            def embed_documents(self, texts):
                return owner.get_embeddings(texts, text_type="document")

            def embed_query(self, text):
                return owner.get_embeddings([text], text_type="query")[0]

            async def aembed_documents(self, texts):
                return await owner.async_get_embeddings(texts, text_type="document")

            async def aembed_query(self, text):
                return (await owner.async_get_embeddings([text], text_type="query"))[0]

        return Adapter()

    def _initialize_by_component_configer(self, config):
        names = ("backend_name", "cache_version", "max_entries")
        validated = CachedEmbedding(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        self.clear_cache()
        return self
