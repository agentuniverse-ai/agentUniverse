# DashScope embedding input order

`DashscopeEmbedding.get_embeddings()` and `async_get_embeddings()` return
dense vectors in the order of their input texts. For indexed responses, each
batch is ordered by `text_index` before vectors are appended to the result.
This also applies when the input spans several 25-text request batches.

The [official response schema](https://help.aliyun.com/en/model-studio/text-embedding-synchronous-api)
defines `text_index` as the corresponding input's position. For example, rows
with indices `[2, 0, 1]` must produce vectors in `[0, 1, 2]` order. Indices are
local to each request, so sorting the combined result would mix batches.

When any response row includes `text_index`, all rows must have unique integer
indices within that request's input range. Duplicate, missing, boolean,
non-integer, or out-of-range indices raise `ValueError` before vectors are
returned. Checking only the number of rows cannot detect these alignment errors.

Responses without index metadata retain their prior arrival order. Batching,
request parameters and API error propagation keep their existing behavior.

## 中文说明

同步和异步接口会依据每批响应中的 `text_index` 排列向量，再按请求批次依次合并，
使有效的索引响应与输入文本一一对应。超过25条文本时，索引会在各批内重新开始，
因此不能在合并结果后全局排序。

例如，响应条目的索引为 `[2, 0, 1]` 时，输出向量应按 `[0, 1, 2]` 排列。
只要响应中有条目携带 `text_index`，所有条目就必须提供当前批次范围内的唯一整数索引。
重复、缺失、布尔值、非整数或越界索引会触发 `ValueError`；仅检查返回数量无法发现这些错配。
未携带索引元数据的响应仍按原顺序返回；分批、请求参数及接口错误传播保持原有行为。
