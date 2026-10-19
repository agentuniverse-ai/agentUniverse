from types import SimpleNamespace

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextWindow,
)


class RecordingCompressor:
    def __init__(self):
        self.target_tokens = None

    def compress(self, segments, target_tokens, **kwargs):
        self.target_tokens = target_tokens
        compressed = segments[0].model_copy(update={"tokens": target_tokens})
        return [compressed], SimpleNamespace()


class StubStore:
    def __init__(self, segment):
        self.segments = [segment]

    def prune(self, session_id, **kwargs):
        return 0

    def get(self, session_id, **kwargs):
        return self.segments

    def delete(self, session_id, **kwargs):
        self.segments = []

    def add(self, segments, **kwargs):
        self.segments = list(segments)


def test_compression_target_reserves_tokens_for_incoming_context():
    segment = ContextSegment(
        type=ContextType.CONVERSATION,
        content="existing",
        tokens=80,
        session_id="session",
    )
    window = ContextWindow(
        session_id="session",
        max_tokens=100,
        reserved_tokens=0,
        total_tokens=80,
        segment_ids=[segment.id],
    )
    compressor = RecordingCompressor()
    manager = ContextManager(name="manager")
    manager._hot_store = StubStore(segment)
    manager._compressor = compressor

    manager._make_room(window, needed_tokens=30)

    assert compressor.target_tokens == 70
    assert window.total_tokens == 70
