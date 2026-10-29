# Embedding（向量化）

Embedding 组件负责将文本转换为向量，供 Store 进行相似度检索。agentUniverse 提供了抽象基类 `Embedding` 以及若干内置实现（OpenAI、Gemini、Ollama、DashScope 等）。本文档重点介绍 **Jina AI Embedding** 组件。

---

## Jina AI Embedding

`JinaEmbedding` 将 [Jina AI](https://jina.ai) 的 Embeddings API（`jina-embeddings-v3` 模型系列）接入 agentUniverse。Jina Embeddings v3 是一个多语言模型，支持可配置的输出维度，在检索任务上表现优秀。

与通过专用 SDK 调用的 OpenAI / DashScope Embedding 不同，Jina Embeddings API 是一个纯 JSON-over-HTTPS 端点，没有官方 Python 客户端，因此 `JinaEmbedding` 直接通过 `requests` 调用 `https://api.jina.ai/v1/embeddings`，并对外暴露 `Embedding` 基类要求的 `get_embeddings` / `async_get_embeddings` 方法。

### 1. 创建配置文件

新建一个 YAML 文件，例如 `jina_embedding.yaml`，填入以下内容。

```yaml
name: 'jina_embedding'
description: 'embedding use jina ai api'
embedding_model_name: 'jina-embeddings-v3'
api_key: '${JINA_API_KEY}'
api_base: 'https://api.jina.ai/v1/embeddings'
dimensions: 1024
request_timeout: 30
batch_size: 32
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.jina_embedding'
  class: 'JinaEmbedding'
```

**说明：** `api_key` 支持三种配置方式：

1. **直接填写字符串** —— 在配置文件中直接写入 API Key。
    ```yaml
    api_key: 'jina_***'
    ```
2. **环境变量占位符** —— 使用 `${VARIABLE_NAME}` 语法。
    ```yaml
    api_key: '${JINA_API_KEY}'
    ```
3. **自定义函数加载** —— 使用 `@FUNC` 注解。

### 2. 配置参数

| 参数                  | 说明                                                                  | 默认值                             |
| --------------------- | -------------------------------------------------------------------- | --------------------------------- |
| `embedding_model_name`| Jina Embedding 模型 ID。                                              | `jina-embeddings-v3`              |
| `api_key`             | Jina AI API Key，未配置时回退到 `JINA_API_KEY` 环境变量。             | -                                 |
| `api_base`            | Jina Embeddings 接口地址。                                            | `https://api.jina.ai/v1/embeddings` |
| `dimensions`          | 输出向量维度，jina-embeddings-v3 支持 32/64/128/256/512/768/1024。     | `1024`                            |
| `request_timeout`     | HTTP 调用超时时间（秒），必须为正数。                                  | `30`                              |
| `batch_size`          | 单次 API 调用发送的最大文本数量。                                      | `32`                              |

### 3. 环境配置

必填：`JINA_API_KEY`
选填：无。

#### 3.1 通过 Python 代码配置

```python
import os
os.environ['JINA_API_KEY'] = 'jina_***'
```

#### 3.2 通过配置文件配置

在项目 `config` 目录下的 `custom_key.toml` 文件中加入：

```toml
JINA_API_KEY="jina_***"
```

### 4. 获取 Jina API Key

1. 登录 [https://jina.ai](https://jina.ai)。
2. 进入 API Key 管理页面，创建新的 Key。
3. 复制生成的 Key，赋值给 `JINA_API_KEY`。

### 5. 在代码中使用

```python
from agentuniverse.agent.action.knowledge.embedding.jina_embedding import JinaEmbedding

embedding = JinaEmbedding()

# 同步
vectors = embedding.get_embeddings(['你好', '世界'])

# 异步
import asyncio
async def main():
    vecs = await embedding.async_get_embeddings(['你好', '世界'])
    print(len(vecs), len(vecs[0]))
asyncio.run(main())
```

返回值为浮点向量列表，与输入文本一一对应且顺序一致。向量可写入 `Document.embedding`，由任意 Store 实现进行检索。

### 6. 使用建议

- `jina-embeddings-v3` 为多语言模型，中英文检索均适用，是推荐默认值。
- 涉及多模态（图像）向量时，请改用 Jina CLIP embeddings 模型。
- `dimensions` 需与 Store / 索引期望的维度保持一致；建立索引后修改维度会使已有向量失效。
