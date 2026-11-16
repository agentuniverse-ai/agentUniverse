import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from langchain_core.runnables import RunnableLambda

import agentuniverse.agent.template.agent_template as agent_template_module
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class DummyTemplate(AgentTemplate):
    """Concrete template used to drive the shared execution helpers."""

    def input_keys(self):
        return ["input"]

    def output_keys(self):
        return ["output"]

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result


class FakeMemory:
    """Memory double that records what the template persists."""

    memory_key = "chat_history"

    def __init__(self):
        self.get_params = None
        self.calls = []

    def get(self, **kwargs):
        self.get_params = kwargs
        return []

    def add(self, messages, session_id=None, agent_id=None, **kwargs):
        self.calls.append({
            "messages": messages,
            "session_id": session_id,
            "agent_id": agent_id,
            "kwargs": kwargs,
        })


class FakePrompt:
    def as_langchain(self):
        return RunnableLambda(lambda _: "prompt")


class FakeLLM:
    def as_langchain_runnable(self, _params):
        return RunnableLambda(lambda _: "llm")


def make_template():
    template = DummyTemplate()
    template.agent_model = SimpleNamespace(
        info={"name": "DemoAgent"},
        profile={},
        memory={},
        llm_params=lambda: {},
    )
    return template


class AgentTemplateMemoryTest(unittest.TestCase):
    def make_inputs(self):
        input_object = InputObject({"input": "question", "session_id": "session-1"})
        agent_input = {
            "input": "question",
            "background": "",
            "session_id": "session-1",
            "agent_id": "DemoAgent",
        }
        return input_object, agent_input

    def test_async_path_persists_message_with_id_type_and_metadata(self):
        template = make_template()
        memory = FakeMemory()
        input_object, agent_input = self.make_inputs()

        with patch.object(agent_template_module, "process_llm_token"), \
                patch.object(AgentTemplate, "async_invoke_chain", new=AsyncMock(return_value="answer")):
            result = asyncio.run(
                template.customized_async_execute(
                    input_object, agent_input, memory, FakeLLM(), FakePrompt()
                )
            )

        self.assertEqual(result["output"], "answer")
        self.assertEqual(len(memory.calls), 1)
        call = memory.calls[0]
        self.assertEqual(call["session_id"], "session-1")
        self.assertEqual(call["agent_id"], "DemoAgent")
        message = call["messages"][0]
        self.assertTrue(message.id)
        self.assertEqual(message.type, "Q&A")
        self.assertEqual(message.source, "DemoAgent")
        self.assertEqual(message.content, "Human: question, AI: answer")
        self.assertEqual(message.metadata["session_id"], "session-1")
        self.assertEqual(message.metadata["agent_id"], "DemoAgent")
        self.assertEqual(message.metadata["type"], "Q&A")
        self.assertIn("timestamp", message.metadata)

    def test_async_path_without_memory_still_returns_output(self):
        template = make_template()
        input_object, agent_input = self.make_inputs()

        with patch.object(agent_template_module, "process_llm_token"), \
                patch.object(AgentTemplate, "async_invoke_chain", new=AsyncMock(return_value="answer")):
            result = asyncio.run(
                template.customized_async_execute(
                    input_object, agent_input, None, FakeLLM(), FakePrompt()
                )
            )

        self.assertEqual(result["output"], "answer")

    def test_sync_and_async_paths_persist_equivalent_messages(self):
        template = make_template()
        sync_memory = FakeMemory()
        async_memory = FakeMemory()

        sync_input, sync_agent_input = self.make_inputs()
        with patch.object(agent_template_module, "process_llm_token"), \
                patch.object(AgentTemplate, "invoke_chain", return_value="answer"):
            template.customized_execute(
                sync_input, sync_agent_input, sync_memory, FakeLLM(), FakePrompt()
            )

        async_input, async_agent_input = self.make_inputs()
        with patch.object(agent_template_module, "process_llm_token"), \
                patch.object(AgentTemplate, "async_invoke_chain", new=AsyncMock(return_value="answer")):
            asyncio.run(
                template.customized_async_execute(
                    async_input, async_agent_input, async_memory, FakeLLM(), FakePrompt()
                )
            )

        sync_message = sync_memory.calls[0]["messages"][0]
        async_message = async_memory.calls[0]["messages"][0]
        self.assertEqual(sync_message.type, async_message.type)
        self.assertEqual(sync_message.source, async_message.source)
        self.assertEqual(sync_message.content, async_message.content)
        self.assertEqual(
            {k: sync_message.metadata[k] for k in ("agent_id", "session_id", "type")},
            {k: async_message.metadata[k] for k in ("agent_id", "session_id", "type")},
        )


if __name__ == "__main__":
    unittest.main()