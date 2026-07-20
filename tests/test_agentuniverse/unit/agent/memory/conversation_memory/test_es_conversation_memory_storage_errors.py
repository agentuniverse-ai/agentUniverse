#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for ElasticsearchMemoryStorage error contracts.

The storage previously raised a bare \`Exception\` for every failure: a
missing es_url, a non-200 index creation, a failed delete, a failed bulk
add, and a failed search. Each now raises a precise exception that names
the index, the operation, the HTTP status, and the Elasticsearch error
body, so an operator can tell configuration errors (ValueError) from
runtime failures (RuntimeError) and locate the offending index.
"""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.memory.conversation_memory.memory_storage.es_conversation_memory_storage import \
    ElasticsearchMemoryStorage
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


def _make_storage() -> ElasticsearchMemoryStorage:
    """A storage whose client is mocked so we never touch ES.

    Built via the configer so the memory_converter is set up the same way as
    in production (DefaultMemoryConverter for ES does not subclass
    BaseMemoryConverter, so direct constructor assignment fails pydantic
    validation — the configer path is the supported way to set it).
    """
    from types import SimpleNamespace
    configer = SimpleNamespace(
        es_url="http://localhost:9200",
        es_index_name="memory",
        es_user=None, es_password=None, es_timeout=60,
    )
    storage = ElasticsearchMemoryStorage()
    # Patch _new_client / _init_es_index so construction does not touch ES.
    with patch.object(ElasticsearchMemoryStorage, "_new_client"):
        storage._initialize_by_component_configer(configer)
    storage.client = MagicMock()
    return storage


def _response(status_code: int, text: str = "error body", json_body=None):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    if json_body is not None:
        response.json.return_value = json_body
    return response


class TestElasticsearchMemoryStorageConfigErrors(unittest.TestCase):
    """Configuration problems raise ValueError, not a bare Exception."""

    def test_missing_es_url_raises_value_error(self) -> None:
        storage = ElasticsearchMemoryStorage(es_url=None, index_name="memory")
        configer = ComponentConfiger()
        # Patch _new_client so we isolate the configuration check.
        with patch.object(ElasticsearchMemoryStorage, "_new_client"):
            with self.assertRaises(ValueError) as ctx:
                storage._initialize_by_component_configer(configer)
        self.assertIn("es_url", str(ctx.exception))


class TestElasticsearchMemoryStorageRuntimeErrors(unittest.TestCase):
    """ES non-200 responses raise RuntimeError naming the index + status."""

    def test_create_index_failure_raises_runtime_error_with_status(self) -> None:
        storage = _make_storage()
        # First GET returns 404 (index missing), PUT to create returns 500.
        storage.client.get.return_value = _response(404)
        storage.client.put.return_value = _response(500, text="mapping error")
        with self.assertRaises(RuntimeError) as ctx:
            storage._init_es_index()
        msg = str(ctx.exception)
        self.assertIn("memory", msg)
        self.assertIn("500", msg)
        self.assertIn("mapping error", msg)

    def test_delete_failure_raises_runtime_error_with_url_and_status(self) -> None:
        storage = _make_storage()
        storage.client.post.return_value = _response(400, text="bad query")
        with self.assertRaises(RuntimeError) as ctx:
            storage.delete(session_id="s1")
        msg = str(ctx.exception)
        self.assertIn("memory", msg)
        self.assertIn("400", msg)
        self.assertIn("bad query", msg)
        self.assertIn("_delete_by_query", msg)

    def test_add_failure_raises_runtime_error_with_status(self) -> None:
        storage = _make_storage()
        storage.client.post.return_value = _response(413, text="too large")
        with patch(
            "agentuniverse.agent.memory.conversation_memory."
            "memory_storage.es_conversation_memory_storage.ConversationMessage"
        ) as conv:
            conv.check_and_convert_message.return_value = []
            with self.assertRaises(RuntimeError) as ctx:
                storage.add(message_list=[], session_id="s1")
        msg = str(ctx.exception)
        self.assertIn("memory", msg)
        self.assertIn("413", msg)
        self.assertIn("too large", msg)

    def test_retrieve_failure_raises_runtime_error_with_status(self) -> None:
        storage = _make_storage()
        storage.client.post.return_value = _response(401, text="unauthorized")
        with self.assertRaises(RuntimeError) as ctx:
            storage.get(session_id="s1")
        msg = str(ctx.exception)
        self.assertIn("memory", msg)
        self.assertIn("401", msg)
        self.assertIn("unauthorized", msg)
        self.assertIn("_search", msg)

    def test_errors_are_not_bare_exception(self) -> None:
        # The concrete type must be ValueError / RuntimeError, not Exception.
        storage = _make_storage()
        storage.client.post.return_value = _response(500)
        with patch(
            "agentuniverse.agent.memory.conversation_memory."
            "memory_storage.es_conversation_memory_storage.ConversationMessage"
        ) as conv:
            conv.check_and_convert_message.return_value = []
            try:
                storage.add(message_list=[], session_id="s1")
            except ValueError:
                pass
            except RuntimeError:
                pass
            except Exception as exc:  # noqa: BLE001 — the point of the test
                self.fail(
                    f"add() raised bare {type(exc).__name__}; expected "
                    "ValueError or RuntimeError")


if __name__ == "__main__":
    unittest.main(verbosity=2)
