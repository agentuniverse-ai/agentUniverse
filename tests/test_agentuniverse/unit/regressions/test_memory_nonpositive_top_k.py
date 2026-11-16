from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.agent.memory.message import Message


def test_ram_memory_nonpositive_top_k_returns_no_messages():
    storage = RamMemoryStorage()
    storage.add([Message(type="human", content="hello")], "session-1", "agent-1")

    assert storage.get("session-1", "agent-1", top_k=0) == []
    assert storage.get("session-1", "agent-1", top_k=-1) == []
