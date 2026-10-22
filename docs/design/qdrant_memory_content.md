# Qdrant memory content and metadata

QdrantMemoryStorage stores message metadata as top-level payload fields. The
payload key `content` is reserved for `Message.content`: it must not be replaced
by a same-named entry in `Message.metadata`.

For example, storing this message must preserve `actual message`:

```python
message = Message(
    content="actual message",
    metadata={"content": "source preview", "topic": "example"},
)
storage.add([message], session_id="example-session")
```

The stored content is also the source used for embedding. Previously the
metadata could overwrite the stored payload after the embedding was generated,
making the vector describe a different message. A dictionary-valued metadata
`content` could additionally fail Message validation while reading the batch.

The write path now applies the actual message content after metadata. This
preserves strings (including empty strings), structured content lists, and None.
Unrelated metadata and existing source/type/session/agent behavior are unchanged.
The caller's Message and metadata are not mutated.

## Compatibility and existing data

- Metadata `content` is not returned as a separate metadata entry. The reader
  already reserves and removes this key while reconstructing Message objects.
  Rename application metadata to a nonreserved key, such as `source_preview`,
  if that value must survive the round trip.
- This does not change the payload schema, vector format, IDs, filters, or
  retrieval ordering, and it does not fix other conversion failures.
- Existing points whose original content was overwritten cannot be recovered
  from the vector. Rewrite them from the original message source as needed;
  this fix only protects new writes and rewrites.

## Tests

`tests/test_agentuniverse/unit/agent/memory/test_qdrant_message_content.py`
uses the real qdrant-client local backend, both in-memory and reopened on-disk
storage. Only the external embedding provider is replaced with a deterministic
test implementation. No network server or credentials are required. The module
is skipped when the optional qdrant-client dependency is absent.

It covers conflicting string/dictionary metadata, structured/empty/None content,
mixed batches, repeated IDs, filters, no-collision controls and input immutability.

## 中文说明

Qdrant 消息 payload 的 `content` 是保留字段，必须来自 Message.content，不能被
metadata 的同名键覆盖。修复后正文与生成向量所用的内容保持一致；其他元数据、
会话筛选及消息对象不变。需要保存同名业务元数据时，请改用 source_preview 等键。
已被旧版本覆盖的正文无法从向量恢复，需从原始消息重新写入。
