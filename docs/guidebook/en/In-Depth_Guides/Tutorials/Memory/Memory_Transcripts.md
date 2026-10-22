# Portable memory transcripts

Conversation history can be exported to JSON Lines without depending on a
particular memory storage backend:

```python
from agentuniverse.agent.memory.transcript import (
    messages_from_jsonl,
    messages_to_jsonl,
)

payload = messages_to_jsonl(messages)
restored_messages = messages_from_jsonl(payload)
```

Each line is one complete `Message`. IDs, roles, text or multimodal content,
sources, and metadata are preserved. The loader accepts `str` or UTF-8 bytes
and ignores empty lines, which makes transcripts convenient for files and
append-only streams. Malformed JSON and invalid message records report the
failing line number.

The helpers only transform data; applications remain responsible for access
control and for removing sensitive content before exporting a transcript.
