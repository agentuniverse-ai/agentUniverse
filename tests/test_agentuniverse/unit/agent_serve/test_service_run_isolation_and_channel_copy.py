#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for two concurrency / isolation bugs.

1. Service.run mutated the shared agent's agent_model.profile to override
   `streaming`. Service instances are singletons shared across concurrent
   requests, so two requests with different `streaming` flags raced and one
   won, producing the wrong output format. The fix takes a per-call copy
   before mutating.

2. LLMChannel.create_copy returned `self`, so `get_instance_obj(new_instance=True)`
   handed out the same shared instance and per-call state (client.base_url,
   ext_params) leaked across requests. The fix inherits the base-class
   `model_copy` behaviour.
"""

import unittest
from unittest.mock import MagicMock


class TestServiceRunDoesNotMutateSharedAgent(unittest.TestCase):
    """Service.run must not mutate the shared agent's profile."""

    def test_streaming_override_does_not_leak_to_shared_agent(self):
        from agentuniverse.agent_serve.service import Service

        # Build a Service with a mock agent whose agent_model.profile holds
        # an llm_model dict without 'streaming'.
        shared_agent = MagicMock()
        shared_agent.agent_model.profile = {
            "llm_model": {"name": "m", "temperature": 0.5},
        }
        # create_copy returns a distinct mock so the override lands on the
        # per-call copy, not the shared agent.
        per_call_agent = MagicMock()
        per_call_agent.agent_model.profile = {
            "llm_model": {"name": "m", "temperature": 0.5},
        }
        shared_agent.create_copy.return_value = per_call_agent

        service = Service()
        service.agent = shared_agent

        # Run with streaming=True.
        service.run(streaming=True)

        # The shared agent's profile must NOT carry streaming=True — that
        # would race with a concurrent non-streaming request.
        shared_llm = shared_agent.agent_model.profile["llm_model"]
        self.assertNotIn(
            "streaming", shared_llm,
            "Service.run must not mutate the shared agent's profile; a "
            "concurrent request would see the wrong streaming flag")
        # The per-call copy DID carry the override.
        per_call_llm = per_call_agent.agent_model.profile["llm_model"]
        self.assertTrue(per_call_llm.get("streaming"))

    def test_two_concurrent_streaming_flags_do_not_interfere(self):
        from agentuniverse.agent_serve.service import Service

        # Simulate two sequential run() calls with different streaming flags
        # on the same Service singleton. After both, the shared agent's
        # profile must still not carry either flag.
        shared_agent = MagicMock()
        shared_agent.agent_model.profile = {"llm_model": {"name": "m"}}

        def _make_copy():
            copy = MagicMock()
            copy.agent_model.profile = {"llm_model": {"name": "m"}}
            return copy

        shared_agent.create_copy.side_effect = _make_copy

        service = Service()
        service.agent = shared_agent

        service.run(streaming=True)
        service.run(streaming=False)

        shared_llm = shared_agent.agent_model.profile["llm_model"]
        self.assertNotIn("streaming", shared_llm)


class TestLLMChannelCreateCopyIsolation(unittest.TestCase):
    """create_copy must return a distinct instance, not `self`."""

    def test_create_copy_returns_distinct_instance(self):
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

        channel = LLMChannel(channel_model_name="m",
                             channel_api_base="http://original")
        copy = channel.create_copy()
        self.assertIsNot(copy, channel,
                         "create_copy must return a new instance; returning "
                         "`self` leaks per-call state across requests")
        self.assertEqual(copy.channel_api_base, "http://original")

    def test_copy_base_url_change_does_not_leak_to_original(self):
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

        channel = LLMChannel(channel_model_name="m",
                             channel_api_base="http://original")
        copy = channel.create_copy()
        # Mutate the copy's base_url the way _call does.
        copy.channel_api_base = "http://changed"
        self.assertEqual(channel.channel_api_base, "http://original",
                         "mutating the copy must not leak back to the original")

    def test_copy_gets_independent_client(self):
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

        channel = LLMChannel(channel_model_name="m",
                             channel_api_base="http://x")
        copy = channel.create_copy()
        # Both start with client=None; assigning on the copy must not affect
        # the original.
        copy.client = MagicMock()
        self.assertIsNone(channel.client,
                          "the copy's client assignment must not leak to the "
                          "original instance")


if __name__ == "__main__":
    unittest.main(verbosity=2)
