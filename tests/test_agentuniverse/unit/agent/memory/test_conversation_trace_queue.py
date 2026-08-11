import queue
from unittest.mock import patch

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import (
    ConversationMemoryModule,
)


def test_trace_collection_does_not_fail_when_queue_is_full():
    module_class = ConversationMemoryModule.__wrapped__
    module = module_class.__new__(module_class)
    module.queue = queue.Queue(maxsize=1)
    module.queue.put_nowait(lambda: None)

    with patch(
        "agentuniverse.agent.memory.conversation_memory.conversation_memory_module."
        "FrameworkContextManager.get_context",
        return_value="context-id",
    ):
        module.add_trace_info(
            {"source": "agent", "type": "agent"},
            {"source": "tool", "type": "tool"},
            "input",
            {},
            "pair-id",
        )

    assert module.queue.qsize() == 1
