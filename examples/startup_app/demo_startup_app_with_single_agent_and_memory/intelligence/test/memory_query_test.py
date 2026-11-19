from typing import List

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def test_query_memory(s_id: str):
    """Print the input/output conversation messages stored for the given session.

    Args:
        s_id: The session id whose stored messages are queried.
    """
    memory_instance: Memory = MemoryManager().get_instance_obj('global_conversation_memory')
    messages: List[Message] = memory_instance.get(session_id=s_id, top_k=500, type=['input', 'output'])
    for message in messages:
        # print(message.trace_id)
        print(f"{message.metadata.get('timestamp')} {message.metadata.get('prefix')}: {message.content}")

def test_query_memory_with_trace_id(s_id: str):
    """Print the stored messages of a session filtered by a specific trace id.

    Args:
        s_id: The session id whose stored messages are queried.
    """
    memory_instance: Memory = MemoryManager().get_instance_obj('global_conversation_memory')
    messages: List[Message] = memory_instance.get(session_id=s_id, trace_id="39fbcb33aca8427cb59c37d6f39adc10",
                                                  type=['input', 'output'])
    for message in messages:
        # print(message.trace_id)
        print(f"{message.metadata.get('timestamp')} {message.metadata.get('prefix')}: {message.content}")



if __name__ == '__main__':
    s_id = "d369ff14-1ad4-4192-b624-18c8cf1a0c11"
    # test_query_memory(s_id)
    test_query_memory_with_trace_id(s_id)
