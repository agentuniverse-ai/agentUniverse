"""Regression tests for the non-semantic Chroma memory window."""

from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage
from agentuniverse.message.message import Message


class RecordingCollection:
    def __init__(self, messages):
        self.messages = messages

    def get(self, where=None):
        return {"ids": [str(i) for i in range(len(self.messages))], "documents": self.messages}


def test_get_returns_most_recent_window_in_time_order():
    messages = [Message(content=f"m{i}", gmt_created=i) for i in range(1, 5)]
    store = ChromaMemoryStorage(name="chroma")
    store._collection = RecordingCollection([m.content for m in messages])

    def fake_to_messages(result, sort_by_time=False):
        docs = result["documents"]
        pairs = sorted(zip(docs, range(len(docs))), key=lambda x: x[1])
        return [Message(content=content, gmt_created=i) for content, i in pairs]

    store.to_messages = fake_to_messages

    result = store.get(key="session", top_k=2)
    contents = [m.content for m in result]
    assert contents == ["m3", "m4"]
