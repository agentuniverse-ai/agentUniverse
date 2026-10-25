# Protocol-faithful literal history

`ProtocolHistory` is an opt-in bridge for already observed chat messages. It keeps
modern assistant function calls and tool results through existing `Message`
storage, then prepares literal LangChain messages or OpenAI-compatible chat
dictionaries. It does not execute tools, fetch image URLs, interpolate stored
braces, compact history, or change the default `Message.as_langchain()` behavior.

## Store, reload, and use with the public prompt/LLM interface

```python
from agentuniverse.agent.memory.protocol_history import ProtocolHistory
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt

# memory_storage is an existing configured SqlAlchemyMemoryStorage.
observed = [
    {"role": "user", "content": "Look up literal {customer_id}"},
    {"role": "assistant", "content": None, "tool_calls": [
        {"id": "lookup-1", "type": "function", "function": {
            "name": "lookup", "arguments": '{"id":"{customer_id}"}'}}
    ]},
    {"role": "tool", "tool_call_id": "lookup-1", "content": "Not found"},
]
memory_storage.add(ProtocolHistory.from_wire(observed), session_id="s", agent_id="a")
history = memory_storage.get(session_id="s", agent_id="a", top_k=100)
prompt = ChatPrompt(messages=[
    Message(type="system", content="Respond in {language}."),
    Message(type="human", content="{input}"),
])
chain = prompt.as_langchain_with_history(history, history_index=1) | llm.as_langchain()
response = chain.invoke({"language": "English", "input": "Summarize the result."})
# await chain.ainvoke(...) uses the existing async adapter.
# Or pass ProtocolHistory.to_wire(history) to OpenAILLM.call/acall.
```

Copy an existing SQL wrapper/storage YAML and configure it normally; no new
storage class, schema, or automatic registration is required. The integration
test uses a real file-backed SQLite database, discards/reopens the wrapper, then
captures actual sync/async SDK requests at a loopback HTTP server. A selected
history must be chronologically ordered and include complete tool exchanges.
The bridge rejects an orphaned result or incomplete selection; it does not repair
the existing storage backend's ordering/window rules or retrieve omitted turns.

## Contract and compatibility

- Supported roles: system/user/assistant/tool; stored human/ai aliases map to
  user/assistant. Supported user blocks: text and image_url (url/detail). Unknown
  roles, blocks, provider-specific fields and legacy function_call are rejected.
- Function arguments remain the original JSON string, including Unicode and
  whitespace. They must decode to a finite JSON object. Multiple calls and
  out-of-order results within that pending group are supported, each exactly once.
- Storage fragments may be incomplete. Model-input conversion requires all calls
  resolved, no duplicate call IDs, and no non-tool messages interrupting a group.
- An `au_protocol_history` v1 metadata envelope carries tool fields and an optional
  original message ID. Supply `message_ids=[...]` separately; SQL row IDs do not
  overwrite that original ID. Ordinary existing messages need no envelope.
  Generic external exports which deliberately discard metadata are unsupported.
- Input objects are copied, not mutated. Defaults reject more than 256 messages
  or 2,000,000 serialized UTF-8 bytes. Limits reject rather than truncate and are
  not token estimates. Arbitrarily large caller-owned objects still exist before
  this validation; this is not a streaming ingestion or memory-isolation API.
- Old prompt templates remain templates. `as_langchain_with_history` explicitly
  inserts literal history at the requested template position; template variables
  are still substituted. Neither the bridge nor its envelope authenticates the
  provenance or trustworthiness of stored messages.
- With LangChain 0.1.20, an assistant tool-call message with empty-string content
  is transmitted as null by its existing adapter. `to_wire()` preserves the
  original string/null value; other wire fields are checked by request capture.

## Reproduce

See [the checked-in runner and evidence](../../../../../../tests/reproduction/protocol-history-bridge/README.md).
Tests use synthetic text, a disposable SQLite file and a localhost HTTP server;
they require no paid model provider and do not execute tools or load image URLs.
This is not JSONL archive migration, message pruning, automatic replay or a
replacement for existing role-alias/SQL-filter fixes.
