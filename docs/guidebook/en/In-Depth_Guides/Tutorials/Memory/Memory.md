# Memory

For stored tool exchanges and literal history, see the opt-in [Protocol History bridge](Protocol_History.md).

For agents, memory is a crucial component that allows them to remember past events. In most conversational and task
scenarios, we want the agents to integrate historical information to provide answers and communicate.

Just like human memory, an agent's memory can be simply divided into the following two categories:

* Short-term memory: Immediate contextual information during the agent's task execution, temporarily saving and
  manipulating a limited amount of memory information.
* Long-term memory: Real-time persistence of the agent's contextual information, always ensuring the provision of
  long-term memory information.

In this definition process, we will find that memory, in addition to its own definition, also relies on a series of
technologies such as vector storage and rapid retrieval.

Moreover, in addition to providing the agent with the ability to handle short-term and long-term contexts as mentioned
above, memory can also provide many significant functions. For example: by mining and processing memory, we can
accumulate memory into experiential knowledge; memory can record the "preferences" of users throughout the entire
operation process of the agent, and so on.

## Memory Architecture

In the agentUniverse, the overall architecture diagram of memory is shown as follows:

![agentUniverse memory architecture](../../../../_picture/memory.jpg)
Including multi-agent memory transfer, adding memory, retrieving memory, and pruning and compressing memory processes.

### Multi-Agent Memory Transfer Process

In the multi-agent memory transfer process, the `chat_history` parameter serves as the entry point. It carries specific
memory information from Agent A, tagged with the source (Agent A), and transfers it to Agent B. Agent B refers to
the `process_memory` method in the aU agent to read the memory information carried by `chat_history` and adds it to
Agent B's corresponding memory.

#### Multi-Agent Memory Transfer Code Example

During the runtime of Agent A, specific memory information is transferred to Agent B. For a specific application
example, you can refer to the [Multi-Agent Discussion Group](../../../Examples/Discussion_Group.md) in the aU sample project.

```python
from typing import List

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.agent_manager import AgentManager

memory_messages: List[Message] = [Message(content='hi, i am agent a, nice to meet you.', source='agent_a')]

agent_b: Agent = AgentManager().get_instance_obj('agent_b')
agent_b.run({'chat_history': memory_messages})
```

### Adding Memory Process

In the memory addition process, multiple memory_storage (memory storage) domain components configured in the memory
instance are obtained. The memory message list, agent ID (agent_id), session ID (session_id), source (memory source),
and other information are stored in multiple storages.

Currently, agentUniverse comes with three built-in memory storage
methods: [ChromaDB](../../../../../../agentuniverse/agent/memory/memory_storage/chroma_memory_storage.py), [SqlAlchemy](../../../../../../agentuniverse/agent/memory/memory_storage/sql_alchemy_memory_storage.py), [RamMemory](../../../../../../agentuniverse/agent/memory/memory_storage/ram_memory_storage.py).
Users can choose the appropriate memory storage method based on their actual needs.

Special Reminder: In the `pre_parse_input` method of the agent base class, aU will automatically read the `name`
configured for the current agent and set it as the `agent_id` in `agent_input`. The `session_id` needs to be passed in
by the user when executing the agent. The memory process can use the parameters parsed by `agent_input` as input
parameters.

```python
def pre_parse_input(self, input_object) -> dict:
    agent_input = dict()
    # Omitted code
    agent_input['agent_id'] = self.agent_model.info.get('name', '')
    agent_input['session_id'] = input_object.get_data('session_id') or ''
    # Omitted code
    return agent_input
```

### Memory Retrieval Process

In the memory retrieval process, the memory_retrieval_storage domain component configured in the memory instance is
obtained (if the user has not configured it, the first memory storage component in memory_storages is used by default).
Memory is retrieved based on the agent ID (agent_id), session ID (session_id), and source (memory source).

[ChromaDB](../../../../../../agentuniverse/agent/memory/memory_storage/chroma_memory_storage.py) can perform vector retrieval
based on the query,
[SqlAlchemy](../../../../../../agentuniverse/agent/memory/memory_storage/sql_alchemy_memory_storage.py)
and [RamMemory](../../../../../../agentuniverse/agent/memory/memory_storage/ram_memory_storage.py) filter based on
chronological conditions to retrieve the specified memory information.

### Memory Pruning and Compression Process

In the memory pruning and compression process, the `max_tokens` parameter in the memory instance (the maximum number of
tokens for memory in the prompt) is obtained. If the memory information obtained during the memory retrieval process
exceeds the maximum token count, it is pruned and compressed.

The `memory_compressor` (memory compression) domain component configured in the memory instance is obtained to compress
the pruned memory, summarize it, and synthesize the final memory information that meets the token count limit.

# Conclusion

So far, you have gained a preliminary understanding of the role of memory. In the next section, we will specifically
introduce to you the standard definition of memory components, how to create custom memories, and how to use memories.
