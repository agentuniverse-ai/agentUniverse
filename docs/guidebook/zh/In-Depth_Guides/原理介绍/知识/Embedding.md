# Embedding

agentUniverse 提供了多个内置的 embedding 组件，供 Knowledge 的 store 与 doc processor 对文本进行向量化。每个组件都以 `metadata.type: EMBEDDING` 注册，并对外提供 `get_embeddings(texts, input_type=...)` 及其异步版本。

## VoyageEmbedding

`VoyageEmbedding` 通过 Voyage AI 的 embeddings API（`https://api.voyageai.com/v1/embeddings`）生成文本向量。它支持 Voyage AI 的 embedding 模型家族，包括 `voyage-3`（默认）、`voyage-3-lite`、`voyage-3-large` 与 `voyage-large-2`。无需额外安装（`requests` 已是 agentUniverse 的核心依赖），仅需一个 Voyage AI 的 API Key。

注册一个指向 `agentuniverse.agent.action.knowledge.embedding.voyage_embedding.VoyageEmbedding` 的组件，然后在 store 或 processor 中按名称引用（例如 `embedding_model: voyage_embedding`）。API Key 从环境变量 `VOYAGE_API_KEY` 读取。

```yaml
name: 'voyage_embedding'
description: 'embedding via Voyage AI embeddings API'
embedding_model_name: 'voyage-3'
input_type: 'document'
request_timeout: 30
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.voyage_embedding'
  class: 'VoyageEmbedding'
```
- embedding_model_name：Voyage AI embedding 模型（默认 `voyage-3`）。
- input_type：`document` 或 `query`——Voyage AI 建议显式指定以获得最佳检索质量（默认 `document`）。
- request_timeout：HTTP 调用超时时间，单位秒（默认 30）。`requests` 默认无超时，若不设置，一旦 Voyage API 卡住，整步 embedding 会无限期挂起。

Voyage AI 建议告知 API 本次调用是为入库的文档生成向量，还是为检索的查询生成向量。组件上的 `input_type` 设置默认值；调用 `get_embeddings` 时可传 `input_type='query'` 进行覆盖。发生超时时，调用会为每条输入文本返回一个空向量，避免单次慢请求拖垮整条入库链路；HTTP 错误与非 JSON 响应会以 `RuntimeError` 抛出，缺少 API Key 则抛出 `ValueError`。
