#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for two memory data-isolation bugs.

1. RamMemoryStorage.messages was a class-level mutable dict (``= dict()``),
   shared across every instance. Two agents with separate RamMemoryStorage
   instances (different storage names) wrote into the same dict, so agent A's
   session history leaked into agent B. The fix is a pydantic
   ``Field(default_factory=dict)`` so each instance gets its own dict.

2. SqliteConversationMemoryStorage.delete called ``query.filter(...)`` without
   reassigning the result. SQLAlchemy ``Query.filter()`` returns a new Query;
   the old code discarded it, so neither the agent_id filter nor the trace_id
   filter ever applied — delete() removed every row matching the session_id,
   or every row in the table when session_id was also None.
"""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.memory.memory_storage.ram_memory_storage import \
    RamMemoryStorage
from agentuniverse.agent.memory.message import Message


def _msg(content: str) -> Message:
    return Message(content=content)


class TestRamMemoryStorageInstanceIsolation(unittest.TestCase):
    """Each RamMemoryStorage instance must own its own messages dict."""

    def test_two_instances_do_not_share_messages(self) -> None:
        a = RamMemoryStorage()
        b = RamMemoryStorage()
        # Sanity: before any add, both are empty and distinct objects.
        self.assertIsNot(a.messages, b.messages)

        a.add([_msg("hello from A")], session_id="s1", agent_id="agent_a")
        # B must not see A's message.
        self.assertEqual(b.get(session_id="s1", agent_id="agent_a"), [])
        a_messages = a.get(session_id="s1", agent_id="agent_a")
        self.assertEqual(len(a_messages), 1)
        self.assertEqual(a_messages[0].content, "hello from A")

    def test_class_level_default_is_not_shared_after_repeated_construction(
        self) -> None:
        # Regression for the specific bug: a bare ``= dict()`` default is
        # constructed once at class-definition time and shared. Constructing
        # several instances and writing to one must not bleed into the others.
        instances = [RamMemoryStorage() for _ in range(5)]
        instances[0].add([_msg("only in instance 0")],
                         session_id="solo", agent_id="a")
        for i, inst in enumerate(instances[1:], start=1):
            self.assertEqual(
                inst.get(session_id="solo", agent_id="a"), [],
                f"instance {i} leaked data from instance 0")

    def test_delete_in_one_instance_does_not_affect_another(self) -> None:
        a = RamMemoryStorage()
        b = RamMemoryStorage()
        a.add([_msg("in A")], session_id="s1", agent_id="a1")
        b.add([_msg("in B")], session_id="s1", agent_id="a1")
        # Deleting in A must not touch B's store.
        a.delete(session_id="s1")
        self.assertEqual(a.get(session_id="s1", agent_id="a1"), [])
        self.assertEqual(len(b.get(session_id="s1", agent_id="a1")), 1)


class TestSqliteConversationMemoryDeleteFilter(unittest.TestCase):
    """delete() must actually apply its agent_id / trace_id filters.

    The bug was source-level: ``query.filter(...)`` returns a new Query, but
    the previous code discarded the return value, so the filter never
    applied. We assert the source reassigns the result before delete().
    """

    def test_source_reassigns_query_after_filter(self) -> None:
        import inspect
        from agentuniverse.agent.memory.conversation_memory.memory_storage.\
            sqlite_conversation_memory_storage import SqliteMemoryStorage

        source = inspect.getsource(SqliteMemoryStorage.delete)
        # The fix: both filter calls must reassign ``query =``. The bug was a
        # bare ``query.filter(...)`` whose return was discarded.
        self.assertIn("query = query.filter(agent_id_col)", source,
                      "agent_id filter must be reassigned to query")
        self.assertIn("query = query.filter(getattr(model_class, 'trace_id')",
                      source,
                      "trace_id filter must be reassigned to query")

    def test_source_does_not_contain_discarded_filter_calls(self) -> None:
        import inspect
        from agentuniverse.agent.memory.conversation_memory.memory_storage.\
            sqlite_conversation_memory_storage import SqliteMemoryStorage

        source = inspect.getsource(SqliteMemoryStorage.delete)
        # The buggy form: a bare 'query.filter(' that does not reassign. We
        # count occurrences of 'query = query.filter' vs bare 'query.filter'.
        reassigned = source.count("query = query.filter")
        self.assertGreaterEqual(reassigned, 2,
                                "both agent_id and trace_id filters must be "
                                "reassigned to query")


if __name__ == "__main__":
    unittest.main(verbosity=2)
