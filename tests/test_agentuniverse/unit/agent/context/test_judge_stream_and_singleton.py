#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for judge_chain_stream RunnableBinding detection + context manager @singleton."""

import unittest


class TestJudgeChainStream(unittest.TestCase):

    def test_source_handles_runnable_binding(self):
        import inspect
        from agentuniverse.agent.agent import Agent
        src = inspect.getsource(Agent.judge_chain_stream)
        # Must check for RunnableBinding (.bound) and .kwargs['streaming']
        self.assertIn('"bound"', src,
                      "judge_chain_stream must unwrap RunnableBinding.bound")
        self.assertIn('"streaming"', src,
                      "judge_chain_stream must check kwargs for streaming flag")


class TestContextStoreManagerSingleton(unittest.TestCase):

    def test_has_singleton_decorator(self):
        import inspect
        from agentuniverse.agent.context.context_store_manager import \
            ContextStoreManager
        src = inspect.getsource(ContextStoreManager)
        # The module-level decorator must be present.
        import agentuniverse.agent.context.context_store_manager as mod
        mod_src = inspect.getsource(mod)
        self.assertIn("@singleton", mod_src,
                      "ContextStoreManager must be decorated with @singleton")


class TestContextManagerManagerSingleton(unittest.TestCase):

    def test_has_singleton_decorator(self):
        import inspect
        import agentuniverse.agent.context.context_manager_manager as mod
        mod_src = inspect.getsource(mod)
        self.assertIn("@singleton", mod_src,
                      "ContextManagerManager must be decorated with @singleton")


class TestSingletonInstanceSharing(unittest.TestCase):

    def test_context_store_manager_returns_same_instance(self):
        from agentuniverse.agent.context.context_store_manager import \
            ContextStoreManager
        a = ContextStoreManager()
        b = ContextStoreManager()
        self.assertIs(a, b,
                      "ContextStoreManager() must return the same instance "
                      "(singleton)")

    def test_context_manager_manager_returns_same_instance(self):
        from agentuniverse.agent.context.context_manager_manager import \
            ContextManagerManager
        a = ContextManagerManager()
        b = ContextManagerManager()
        self.assertIs(a, b,
                      "ContextManagerManager() must return the same instance "
                      "(singleton)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
