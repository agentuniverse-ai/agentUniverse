# Neo4j document metadata

`Neo4jStore.insert_document`, `upsert_document`, and `update_document` store
document metadata in the `Document` node's `metadata` property as a JSON string.
Neo4j accepts maps as query parameters, but not as a single node property value
([Neo4j type documentation](https://neo4j.com/docs/cypher-manual/current/values-and-types/property-structural-constructed/)).
Previously, passing a metadata dictionary directly to `SET d.metadata = $metadata`
produced an unsupported property value, including for an empty dictionary.

## Representation and reading

- A dictionary is JSON-encoded without ASCII escaping, including nested objects,
  arrays, strings, numbers, booleans and JSON null values. `{}` is stored as `"{}"`.
- `metadata=None` remains a Cypher null: the property is absent/removed, not a
  string containing `"null"`.
- Non-JSON values (for example sets), circular references and non-finite numbers
  raise `ValueError`. Serialization validates the entire supplied batch before
  opening a session, so a later encoding error cannot leave earlier writes behind.
  This is not a transactional guarantee for subsequent database/network failures.
- The original documents and their metadata are not mutated. IDs, text,
  `MERGE` versus `MATCH`, parameter binding and session cleanup remain unchanged.

Queries still return a `GraphDocument` containing the raw result DataFrame; no
implicit conversion is applied to arbitrary Cypher results. To read metadata:

```python
import json

rows = store.execute_cypher(
    "MATCH (d:Document {id: $id}) RETURN d.metadata AS metadata",
    {"id": "document-1"},
)
value = rows.iloc[0]["metadata"]
metadata = json.loads(value) if value is not None else None
```

This change does not migrate existing externally written nodes, flatten metadata
into separate properties, install APOC, or add nested-property filtering. Clients
reading `d.metadata` should decode the JSON string explicitly.

## Testing

Install the optional `neo4j` driver and `pandas` in the test environment. Run the
offline serialization tests with:

```shell
python -m pytest -q tests/test_agentuniverse/unit/agent/action/knowledge/store/test_neo4j_document_metadata.py
```

For real round trips, start an expendable local Neo4j server with authentication
disabled and its Bolt port bound to localhost only. Set
`AU_NEO4J_METADATA_TEST_URI` to that server's URI, then run:

```shell
python -m pytest -q tests/test_agentuniverse/integration/test_neo4j_document_metadata_live.py
```

Without that variable, the live tests skip. The tests use new UUIDs and clean up
only their own nodes. They cover fresh creation, replacement, nested JSON, empty
objects, null removal, and the existing update-does-not-create behavior. No APOC
installation is required.

## 中文说明

Neo4j 允许字典作为查询参数，但不能把整个字典保存为单个节点属性。
新增、upsert 和更新文档现在统一把 metadata 字典保存为 JSON 字符串，
保留嵌套结构和中文；空字典保存为 `"{}"`，`None` 仍表示删除或不设置该属性。
不可 JSON 序列化的值在整批写入前报错，不静默转成字符串。
原始文档不会被修改。查询仍返回原始 DataFrame，读取 metadata 时需要显式
`json.loads`；不自动迁移外部节点，也不改变任意 Cypher 查询结果。
