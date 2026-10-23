# OpenAI embedding response alignment

The direct synchronous and asynchronous methods of `OpenAIEmbedding` and
`AzureOpenAIEmbedding` return vectors in input-index order, using each SDK
response record's `index`. For example, a response containing records indexed
`[2, 0, 1]` is returned as vectors `[vector_0, vector_1, vector_2]`. Repeated input
texts still have separate positions; no text-based deduplication is performed.

The adapters require exactly one record for each input position. Missing/extra
records, duplicate or out-of-range indices, and absent/non-integer indices are
rejected before returning a batch. Boolean indices are not integers for this
purpose. This prevents an incomplete or ambiguously aligned result from being
used as a valid vector batch. `OpenAIEmbedding` raises `ValueError` with an
`Invalid embedding response` message. Azure retains its existing exception
wrapper, so its message starts with `Failed to get embeddings:`.

The [OpenAI response schema](https://developers.openai.com/api/reference/python/resources/embeddings)
includes the integer `index` field. These checks protect the adapter boundary,
including OpenAI-compatible endpoints; they are not a claim that the hosted
OpenAI or Azure services currently return malformed or shuffled batches.
Providers and test doubles must supply the required indices. There is no
fallback to positional guessing when an index is missing.

Request configuration, client lifecycle, SDK base64 decoding, HTTP-error
handling and vector values remain unchanged. The helper does not validate
vector dimensions/numeric contents or alter `as_langchain()` behavior.

## 中文说明

`OpenAIEmbedding` 和 `AzureOpenAIEmbedding` 的直接同步、异步方法，按照响应
中的 `index` 恢复输入顺序。例如索引 `[2, 0, 1]` 对应的返回向量会按
`[0, 1, 2]` 排列；重复文本仍保留各自的输入位置。

返回记录必须与输入一一对应。记录数量不符、索引重复、越界、缺失或非整数时，
整个批次会报错，不猜测对应关系。布尔值不作为合法索引。OpenAI 适配器抛出
`ValueError`；Azure 保持原有异常包装。兼容服务与测试替身也需提供索引字段。

这是对适配器响应边界的保护，离线异常响应测试不代表官方线上服务存在该故障。
本改动不调整请求参数、客户端生命周期、HTTP 错误处理、向量数值或 LangChain
转换，也不新增向量维度和数值校验。
