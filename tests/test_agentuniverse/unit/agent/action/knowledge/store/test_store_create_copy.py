# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for #1183: Store.create_copy() must return an isolated copy.

Previously ``Store.create_copy()`` returned ``self``, so every
``get_instance_obj(new_instance=True)`` caller received the same shared Store
singleton, leaking per-runtime state across agents. The method now mirrors the
``LLM.create_copy()`` pattern: configuration is copied into a distinct instance
while the lazily-initialized (thread-safe) client connections are shared, never
duplicated.
"""

import unittest

from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.component.component_enum import ComponentEnum


class TestStoreCreateCopyIsolation(unittest.TestCase):
    def _make_store(self):
        store = Store(
            component_type=ComponentEnum.STORE,
            name="test_store",
            description="A test store",
        )
        # Simulate lazily-initialized clients (created post-fork in practice).
        store.client = object()
        store.async_client = object()
        return store

    def test_create_copy_returns_distinct_instance(self):
        """The copy must not be the same object as the original (issue #1183)."""
        store = self._make_store()
        copy = store.create_copy()
        self.assertIsNot(copy, store)

    def test_create_copy_preserves_config(self):
        """Copied instances keep the original configuration."""
        store = self._make_store()
        copy = store.create_copy()
        self.assertEqual(copy.name, store.name)
        self.assertEqual(copy.description, store.description)

    def test_create_copy_shares_clients(self):
        """Clients are thread-safe connections and must not be duplicated.

        This mirrors LLM.create_copy(), which explicitly shares ``client`` and
        ``async_client``. Duplicating a live connection is unsafe and would
        defeat the isolation the copy is meant to provide.
        """
        store = self._make_store()
        copy = store.create_copy()
        self.assertIs(copy.client, store.client)
        self.assertIs(copy.async_client, store.async_client)


if __name__ == "__main__":
    unittest.main()
