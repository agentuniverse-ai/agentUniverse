import asyncio
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from agentuniverse.agent import agent as agent_module
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class DummyAgent(Agent):
    """Concrete Agent used to exercise the knowledge helpers in isolation."""

    def input_keys(self):
        return ["input"]

    def output_keys(self):
        return ["output"]

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result


class FakeKnowledge:
    """Synchronous knowledge base that records which thread served the query."""

    def __init__(self, name, barrier=None):
        self.name = name
        self.barrier = barrier
        self.thread_ids = []
        self.queries = []

    def query_knowledge(self, query_str, **kwargs):
        self.thread_ids.append(threading.get_ident())
        self.queries.append((query_str, kwargs))
        if self.barrier is not None:
            # Both queries must be in flight at the same time, otherwise the
            # first worker times out and the test fails.
            self.barrier.wait(timeout=5)
        return [SimpleNamespace(text=f"{self.name}:{query_str}")]

    def to_llm(self, documents):
        return "|".join(document.text for document in documents)


def patch_manager(lookup):
    """Patch the module-level KnowledgeManager symbol used by Agent.

    ``KnowledgeManager`` is wrapped by ``@singleton``, so the symbol itself is
    a factory function rather than a class.  Patching the class attribute is
    therefore impossible; the module reference is replaced with a factory that
    returns a manager double.
    """
    manager = MagicMock()
    manager.get_instance_obj.side_effect = lookup
    return patch.object(agent_module, "KnowledgeManager", return_value=manager), manager


class AsyncKnowledgeTest(unittest.TestCase):
    def setUp(self):
        self.agent = DummyAgent()
        # Empty knowledge configured on the agent model mirrors the default
        # runtime state and keeps the "no component" branch meaningful.
        self.agent.agent_model = SimpleNamespace(action={"knowledge": []})
        self.input_object = InputObject({"input": "question"})

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def test_queries_run_concurrently_off_the_event_loop_thread(self):
        """Both knowledge bases are queried in worker threads, in config order."""
        barrier = threading.Barrier(2)
        first = FakeKnowledge("first", barrier)
        second = FakeKnowledge("second", barrier)
        mapping = {"first": first, "second": second}

        patcher, _ = patch_manager(lambda name: mapping.get(name))
        with patcher:
            result = self.run_async(
                self.agent.async_invoke_knowledge(
                    "question", self.input_object, knowledge_names=["first", "second"]
                )
            )

        self.assertEqual(result, "first:question\n\nsecond:question")
        self.assertEqual(len(first.thread_ids), 1)
        self.assertEqual(len(second.thread_ids), 1)
        main_thread = threading.get_ident()
        self.assertNotEqual(first.thread_ids[0], main_thread)
        self.assertNotEqual(second.thread_ids[0], main_thread)
        self.assertEqual(first.queries[0][1]["input"], "question")
        self.assertEqual(second.queries[0][1]["input"], "question")

    def test_missing_knowledge_component_is_skipped(self):
        """A component name that resolves to None does not break the batch."""
        only = FakeKnowledge("only")
        mapping = {"only": only, "missing": None}

        patcher, _ = patch_manager(lambda name: mapping.get(name))
        with patcher:
            result = self.run_async(
                self.agent.async_invoke_knowledge(
                    "question", self.input_object, knowledge_names=["only", "missing"]
                )
            )

        self.assertEqual(result, "only:question")
        self.assertEqual(only.queries[0][0], "question")

    def test_empty_query_or_empty_component_list_returns_empty_string(self):
        """No component lookup happens when there is nothing to query."""
        patcher, manager = patch_manager(lambda name: None)
        with patcher:
            no_query = self.run_async(
                self.agent.async_invoke_knowledge("", self.input_object, knowledge_names=["only"])
            )
            no_names = self.run_async(
                self.agent.async_invoke_knowledge("question", self.input_object, knowledge_names=[])
            )

        self.assertEqual(no_query, "")
        self.assertEqual(no_names, "")
        manager.get_instance_obj.assert_not_called()

    def test_query_failure_propagates(self):
        """A failing vector store is not hidden by the async wrapper."""
        failing = FakeKnowledge("failing")
        failing.query_knowledge = MagicMock(side_effect=RuntimeError("store unavailable"))

        patcher, _ = patch_manager(lambda name: failing)
        with patcher:
            with self.assertRaisesRegex(RuntimeError, "store unavailable"):
                self.run_async(
                    self.agent.async_invoke_knowledge(
                        "question", self.input_object, knowledge_names=["failing"]
                    )
                )

    def test_agent_model_component_list_is_used_when_not_supplied(self):
        """The helper falls back to the agent configuration like the sync path."""
        configured = FakeKnowledge("configured")
        self.agent.agent_model = SimpleNamespace(action={"knowledge": ["configured"]})

        patcher, _ = patch_manager(lambda name: configured)
        with patcher:
            result = self.run_async(self.agent.async_invoke_knowledge("question", self.input_object))

        self.assertEqual(result, "configured:question")


class RagAgentTemplateAsyncTest(unittest.TestCase):
    def test_async_execute_awaits_async_knowledge_instead_of_sync_helper(self):
        """The async RAG path must not call the blocking knowledge helper."""
        template = RagAgentTemplate()
        input_object = InputObject({"input": "question"})
        agent_input = {"input": "question", "background": ""}

        async_knowledge = AsyncMock(return_value="knowledge-result")
        sync_knowledge = MagicMock(side_effect=AssertionError("sync knowledge helper was called"))
        async_tools = AsyncMock(return_value="tool-result")
        async_generate = AsyncMock(return_value={"output": "ok"})

        with patch.object(AgentTemplate, "async_invoke_tools", new=async_tools), \
                patch.object(AgentTemplate, "async_invoke_knowledge", new=async_knowledge), \
                patch.object(AgentTemplate, "invoke_knowledge", new=sync_knowledge), \
                patch.object(AgentTemplate, "customized_async_execute", new=async_generate):
            result = asyncio.run(
                template.customized_async_execute(input_object, agent_input, None, None, None)
            )

        self.assertEqual(result, {"output": "ok"})
        async_tools.assert_awaited_once_with(input_object)
        async_knowledge.assert_awaited_once_with("question", input_object)
        sync_knowledge.assert_not_called()
        self.assertEqual(agent_input["background"], "tool_res: tool-result \n\n knowledge_res: knowledge-result")


if __name__ == "__main__":
    unittest.main()