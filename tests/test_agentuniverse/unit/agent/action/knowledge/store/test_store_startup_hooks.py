# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for Store startup hooks and async client lifecycle contracts."""

import asyncio
from typing import Any
import unittest
import warnings
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.store.store import Store, _is_coroutine_callable
from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class SyncStore(Store):
    """Store with synchronous client factories."""

    def _new_client(self):
        self.client = "sync_client_instance"
        return self.client

    def _new_async_client(self):
        self.async_client = "sync_async_client_instance"
        return self.async_client


class AsyncCoroutineStore(Store):
    """Store with an async coroutine factory for async_client."""

    init_error: Any = None

    def _new_client(self):
        self.client = "sync_client_instance"
        return self.client

    async def _new_async_client(self):
        if self.init_error:
            raise self.init_error
        self.async_client = "async_coroutine_client_instance"
        return self.async_client

    async def _ensure_async_client(self):
        return self.async_client or await self._new_async_client()


class AsyncCallableObject:
    """Callable object whose __call__ is a coroutine function."""

    async def __call__(self):
        return "async_callable_client"


class AsyncCallableStore(Store):
    """Store whose _new_async_client is a callable object."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "_new_async_client", AsyncCallableObject())


class TestStoreStartupHooks(unittest.TestCase):
    """Verify that synchronous startup hooks handle client factories safely."""

    def setUp(self):
        self._orig_queue = list(POST_FORK_QUEUE)
        POST_FORK_QUEUE.clear()

    def tearDown(self):
        POST_FORK_QUEUE.clear()
        POST_FORK_QUEUE.extend(self._orig_queue)

    def test_is_coroutine_callable(self):
        """Verify _is_coroutine_callable distinguishes sync vs async callables."""
        def sync_fn():
            pass

        async def async_fn():
            pass

        self.assertFalse(_is_coroutine_callable(sync_fn))
        self.assertTrue(_is_coroutine_callable(async_fn))
        self.assertFalse(_is_coroutine_callable("not_callable"))
        self.assertFalse(_is_coroutine_callable(None))
        self.assertTrue(_is_coroutine_callable(AsyncCallableObject()))

    def test_sync_factories_registered_and_executed(self):
        """Synchronous client factories should be enqueued in POST_FORK_QUEUE."""
        store = SyncStore()
        configer = ComponentConfiger()
        configer.name = "test_sync_store"
        configer.description = "test sync store desc"

        store._initialize_by_component_configer(configer)

        # Both sync _new_client and sync _new_async_client must be in POST_FORK_QUEUE
        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        self.assertIn(store._new_client, registered_funcs)
        self.assertIn(store._new_async_client, registered_funcs)
        self.assertEqual(len(POST_FORK_QUEUE), 2)

        # Simulate synchronous startup queue execution (Gunicorn/Flask/bootstrap runner)
        for func, args, kwargs in POST_FORK_QUEUE:
            func(*args, **kwargs)

        self.assertEqual(store.client, "sync_client_instance")
        self.assertEqual(store.async_client, "sync_async_client_instance")

    def test_sync_async_client_factory_retained_in_post_fork(self):
        """Synchronous factories constructing async SDK clients must remain in POST_FORK_QUEUE."""
        class SyncAsyncSdkStore(Store):
            def _new_client(self):
                self.client = "sync_client"
                return self.client

            def _new_async_client(self):
                # Synchronous method that constructs an async SDK client
                self.async_client = "async_sdk_driver_instance"
                return self.async_client

        store = SyncAsyncSdkStore()
        configer = ComponentConfiger()
        store._initialize_by_component_configer(configer)

        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        self.assertIn(store._new_client, registered_funcs)
        self.assertIn(store._new_async_client, registered_funcs)
        self.assertEqual(len(POST_FORK_QUEUE), 2)

        for func, args, kwargs in POST_FORK_QUEUE:
            func(*args, **kwargs)

        self.assertEqual(store.client, "sync_client")
        self.assertEqual(store.async_client, "async_sdk_driver_instance")

    def test_coroutine_factory_not_enqueued_in_post_fork(self):
        """Coroutine factories should not be enqueued in synchronous startup hooks."""
        store = AsyncCoroutineStore()
        configer = ComponentConfiger()
        configer.name = "test_async_store"

        store._initialize_by_component_configer(configer)

        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        # Sync factory is enqueued
        self.assertIn(store._new_client, registered_funcs)
        # Async coroutine factory is NOT enqueued
        self.assertNotIn(store._new_async_client, registered_funcs)
        self.assertEqual(len(POST_FORK_QUEUE), 1)

    def test_warning_free_startup_when_queue_executed(self):
        """Executing startup hooks must produce no RuntimeWarning about unawaited coroutines."""
        store = AsyncCoroutineStore()
        configer = ComponentConfiger()
        configer.name = "test_async_store"

        store._initialize_by_component_configer(configer)

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            for func, args, kwargs in POST_FORK_QUEUE:
                func(*args, **kwargs)

        coroutine_warnings = [
            w for w in caught_warnings
            if issubclass(w.category, RuntimeWarning) and "coroutine" in str(w.message).lower()
        ]
        self.assertEqual(len(coroutine_warnings), 0)
        self.assertEqual(store.client, "sync_client_instance")
        # async_client is not eagerly initialized during startup
        self.assertIsNone(store.async_client)

    def test_deferred_initialization_on_active_event_loop(self):
        """True coroutine factories should run lazily when awaited on an active event loop."""
        store = AsyncCoroutineStore()
        configer = ComponentConfiger()
        store._initialize_by_component_configer(configer)

        self.assertIsNone(store.async_client)

        async def run_operation():
            return await store._ensure_async_client()

        client = asyncio.run(run_operation())
        self.assertEqual(client, "async_coroutine_client_instance")
        self.assertEqual(store.async_client, "async_coroutine_client_instance")

    def test_initialization_error_propagates_on_active_event_loop(self):
        """Initialization errors in coroutine factories must propagate to awaiting caller."""
        expected_error = ConnectionError("database connection timeout")
        store = AsyncCoroutineStore(init_error=expected_error)
        configer = ComponentConfiger()
        store._initialize_by_component_configer(configer)

        # Startup runner does not raise any error since coroutine was not enqueued
        for func, args, kwargs in POST_FORK_QUEUE:
            func(*args, **kwargs)

        async def run_operation():
            await store._ensure_async_client()

        with self.assertRaises(ConnectionError) as ctx:
            asyncio.run(run_operation())
        self.assertEqual(str(ctx.exception), "database connection timeout")

    def test_coroutine_callable_object_not_enqueued(self):
        """Async callable objects should also not be enqueued in POST_FORK_QUEUE."""
        store = AsyncCallableStore()
        configer = ComponentConfiger()
        store._initialize_by_component_configer(configer)

        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        self.assertNotIn(store._new_async_client, registered_funcs)

    def test_redis_vector_store_skips_coroutine_registration(self):
        """Verify RedisVectorStore's coroutine _new_async_client is not in POST_FORK_QUEUE."""
        from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore

        store = RedisVectorStore(
            connection_url="redis://localhost:6379",
            index_name="test_index",
            dimensions=128,
            create_index=False,
        )
        configer = ComponentConfiger()
        configer.name = "test_redis"
        with patch.object(store, "_validate_config"):
            store._initialize_by_component_configer(configer)

        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        self.assertIn(store._new_client, registered_funcs)
        self.assertNotIn(store._new_async_client, registered_funcs)

    def test_pgvector_store_skips_coroutine_registration(self):
        """Verify PGVectorStore's coroutine _new_async_client is not in POST_FORK_QUEUE."""
        from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore

        store = PGVectorStore(
            connection_url="postgresql://localhost:5432/test",
            table_name="test_table",
            dimensions=128,
            create_table=False,
        )
        configer = ComponentConfiger()
        configer.name = "test_pgvector"
        with patch.object(store, "_validate_config"):
            store._initialize_by_component_configer(configer)

        registered_funcs = [item[0] for item in POST_FORK_QUEUE]
        self.assertIn(store._new_client, registered_funcs)
        self.assertNotIn(store._new_async_client, registered_funcs)


if __name__ == "__main__":
    unittest.main()
