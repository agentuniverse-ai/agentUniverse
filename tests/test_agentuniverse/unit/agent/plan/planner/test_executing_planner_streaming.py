import unittest
from queue import Queue
from threading import Thread
from time import sleep
from types import SimpleNamespace
from typing import Any, ClassVar
from unittest.mock import patch

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.executing_planner import executing_planner as executing_module
from agentuniverse.agent.plan.planner.executing_planner.executing_planner import ExecutingPlanner


class FakeChain:
    """Minimal runnable used to observe how the planner drives the chain."""

    def __init__(self, chunks=None, result="AB", error=None):
        self.chunks = list(chunks if chunks is not None else ["A", "B"])
        self.result = result
        self.error = error
        self.invoke_calls = 0
        self.stream_calls = 0
        self.inputs = []
        self.configs = []

    def invoke(self, input=None, config=None, **kwargs):
        self.invoke_calls += 1
        self.inputs.append(input)
        self.configs.append(config)
        if self.error is not None:
            raise self.error
        return self.result

    def stream(self, input=None, config=None, **kwargs):
        self.stream_calls += 1
        self.inputs.append(input)
        self.configs.append(config)
        if self.error is not None:
            raise self.error
        yield from self.chunks

    def __or__(self, other):
        # The planner composes prompt | llm | parser.  The fake already
        # represents the fully composed chain, so further pipes are no-ops.
        return self


class FakePrompt:
    def __init__(self, chain):
        self.chain = chain

    def as_langchain(self):
        return self.chain


class FakeLLM:
    def __init__(self, chain):
        self.chain = chain
        self.llm_params = []

    def as_langchain_runnable(self, params):
        self.llm_params.append(params)
        return self.chain


class ExecutingPlannerHarness(ExecutingPlanner):
    """ExecutingPlanner with the model/prompt boundaries replaced by fakes.

    The real planner resolves memory, an LLM component and a prompt component
    through the component managers.  Those lookups are irrelevant to the
    streaming contract under test, so the subclass keeps the production
    ``invoke`` implementation and stubs only the surrounding steps.  Using a
    ClassVar avoids pydantic treating the fake chain as a model field.
    """

    chain: ClassVar[Any] = None
    actions: ClassVar[list] = []
    llms: ClassVar[list] = []

    def handle_memory(self, agent_model, planner_input):
        return None

    def handle_llm(self, agent_model):
        llm = FakeLLM(self.chain)
        self.llms.append(llm)
        return llm

    def handle_prompt(self, agent_model, planner_input):
        return FakePrompt(self.chain)

    def run_all_actions(self, agent_model, planner_input, input_object):
        self.actions.append(input_object.get_data("input"))


def build_model():
    """Return the small part of AgentModel that ExecutingPlanner touches."""
    return SimpleNamespace(profile={}, info={"name": "executing"}, llm_params=lambda: {"temperature": 0.1})


class ExecutingPlannerStreamingTest(unittest.TestCase):
    def setUp(self):
        ExecutingPlannerHarness.actions = []
        ExecutingPlannerHarness.llms = []
        self.chain = FakeChain()
        ExecutingPlannerHarness.chain = self.chain
        self.planner = ExecutingPlannerHarness()
        self.model = build_model()
        self.prompt_patch = patch.object(executing_module, "process_llm_token")
        self.prompt_patch.start()
        self.addCleanup(self.prompt_patch.stop)

    def invoke(self, payload):
        return self.planner.invoke(self.model, {"input": "question"}, InputObject(payload))

    def test_stream_emits_each_chunk_and_joins_the_result(self):
        """A configured output stream receives every token produced by the chain."""
        queue = Queue()
        result = self.invoke({"input": "question", "output_stream": queue})

        self.assertEqual(result["output"], "AB")
        self.assertEqual(self.chain.stream_calls, 1)
        self.assertEqual(self.chain.invoke_calls, 0)
        self.assertEqual(queue.qsize(), 2)

        first = queue.get_nowait()
        second = queue.get_nowait()
        self.assertEqual(first["type"], "token")
        self.assertEqual(first["data"]["chunk"], "A")
        self.assertEqual(second["data"]["chunk"], "B")
        self.assertEqual(first["data"]["agent_info"], {"name": "executing"})
        self.assertTrue(queue.empty())

    def test_stream_forwards_the_planner_input(self):
        """The chain receives the same input dictionary the planner received."""
        queue = Queue()
        payload = {"input": "question", "output_stream": queue, "extra": 7}
        self.planner.invoke(self.model, {"input": "question", "extra": 7}, InputObject(payload))

        self.assertEqual(self.chain.inputs, [{"input": "question", "extra": 7}])
        self.assertEqual(self.chain.configs, [{"configurable": {"session_id": "unused"}}])

    def test_stream_preserves_empty_chunks(self):
        """Empty chunks are valid stream events and are forwarded unchanged."""
        self.chain = FakeChain(chunks=["", "A", "", "B"])
        ExecutingPlannerHarness.chain = self.chain
        queue = Queue()

        result = self.invoke({"input": "question", "output_stream": queue})

        self.assertEqual(result["output"], "AB")
        self.assertEqual([queue.get_nowait()["data"]["chunk"] for _ in range(4)], ["", "A", "", "B"])

    def test_full_bounded_queue_keeps_the_complete_result(self):
        """A stalled consumer must not make a valid invocation fail."""
        queue = Queue(maxsize=1)
        queue.put_nowait({"type": "existing"})

        result = self.invoke({"input": "question", "output_stream": queue})

        self.assertEqual(result["output"], "AB")
        self.assertEqual(self.chain.stream_calls, 1)
        self.assertEqual(queue.get_nowait(), {"type": "existing"})
        self.assertTrue(queue.empty())

    def test_slow_consumer_receives_tokens_after_backpressure(self):
        queue = Queue(maxsize=1)
        queue.put_nowait({"type": "existing"})
        received = []

        def consume():
            sleep(0.05)
            received.append(queue.get(timeout=1))
            received.append(queue.get(timeout=1))

        consumer = Thread(target=consume)
        consumer.start()
        result = self.invoke({"input": "question", "output_stream": queue})
        consumer.join(timeout=2)

        self.assertFalse(consumer.is_alive())
        self.assertEqual(result["output"], "AB")
        self.assertEqual(received[0], {"type": "existing"})
        self.assertEqual(received[1]["data"]["chunk"], "A")
        self.assertEqual(queue.get_nowait()["data"]["chunk"], "B")

    def test_non_stream_invokes_the_chain_once(self):
        """Without an output stream the planner keeps the non-streaming path."""
        result = self.invoke({"input": "question"})

        self.assertEqual(result["output"], "AB")
        self.assertEqual(self.chain.invoke_calls, 1)
        self.assertEqual(self.chain.stream_calls, 0)
        self.assertEqual(self.chain.configs, [{"configurable": {"session_id": "unused"}}])

    def test_actions_run_before_the_llm_chain(self):
        """Tool and knowledge actions still execute before generation."""
        queue = Queue()
        self.invoke({"input": "question", "output_stream": queue})

        self.assertEqual(ExecutingPlannerHarness.actions, ["question"])
        self.assertEqual(self.chain.stream_calls, 1)

    def test_empty_chain_result_returns_empty_output(self):
        """A chain that emits no chunks produces an empty string, not None."""
        self.chain = FakeChain(chunks=[])
        ExecutingPlannerHarness.chain = self.chain

        result = self.invoke({"input": "question", "output_stream": Queue()})

        self.assertEqual(result["output"], "")

    def test_chain_errors_propagate_without_writing_a_result(self):
        """Provider failures are not swallowed by the streaming helper."""
        self.chain = FakeChain(error=RuntimeError("provider failed"))
        ExecutingPlannerHarness.chain = self.chain
        queue = Queue()

        with self.assertRaisesRegex(RuntimeError, "provider failed"):
            self.invoke({"input": "question", "output_stream": queue})

        self.assertEqual(queue.qsize(), 0)

    def test_llm_params_are_forwarded(self):
        """The planner still passes the agent LLM parameters into the runnable."""
        self.invoke({"input": "question", "output_stream": Queue()})
        self.assertEqual(len(ExecutingPlannerHarness.llms), 1)
        self.assertEqual(ExecutingPlannerHarness.llms[0].llm_params, [{"temperature": 0.1}])


if __name__ == "__main__":
    unittest.main()
