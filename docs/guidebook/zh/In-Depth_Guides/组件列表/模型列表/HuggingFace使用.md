# HuggingFace 使用

agentUniverse 的 HuggingFace 组件全部基于 **`huggingface_hub` 原生接口**实现（`InferenceClient` /
`AsyncInferenceClient`），而不是 OpenAI 兼容协议——后者已由 `OpenAIStyleLLM` 覆盖。这样可以直接使用
HuggingFace 原生能力，例如 Inference Providers 路由、TGI 的 `text_generation` 专属采样参数、
以及 TEI 的 `feature_extraction`。

支持的部署形态：

- **HF Inference Providers Router**：直接填 `model_name`，可选 `provider` 指定服务商
- **Inference Endpoints（专属推理端点）**：填 `huggingface_base_url`
- **自建 TGI / TEI 服务**：填 `huggingface_base_url`，如 `http://localhost:8080`

## 0. 安装依赖
`huggingface_hub` 是可选依赖：

```shell
pip install huggingface_hub
# 或者
poetry install --extras huggingface_ext
```

## 1. LLM 组件

组件类：`agentuniverse.llm.default.huggingface_llm.HuggingFaceLLM`

### 1.1 两种任务（task）

| task               | 底层接口                            | 适用场景                                     |
|--------------------|---------------------------------|------------------------------------------|
| `chat`（默认）         | `InferenceClient.chat_completion` | 对话模型，自动套用模型的 chat template，支持 Providers 路由 |
| `text_generation`  | `InferenceClient.text_generation` | TGI 原生续写路由，支持 chat 协议不具备的采样参数            |

### 1.2 chat 任务

创建一个 yaml 文件，例如 `user_huggingface_llm.yaml`：

```yaml
name: 'user_huggingface_llm'
description: 'huggingface chat llm via huggingface_hub'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
task: 'chat'
huggingface_api_key: '${HUGGINGFACE_API_KEY}'
# provider: 'auto'                                  # 可选，指定 HF 推理服务商
# huggingface_base_url: 'http://localhost:8080'     # 可选，指向专属端点或自建 TGI
max_tokens: 2048
temperature: 0.7
seed: 42
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_llm'
  class: 'HuggingFaceLLM'
```

**note:** `huggingface_api_key`、`huggingface_base_url`、`provider` 支持三种配置方法

1. 直接字符串值：
    ```yaml
    huggingface_api_key: 'hf_***'
    ```
2. 环境变量占位符：
    ```yaml
    huggingface_api_key: '${HUGGINGFACE_API_KEY}'
    ```
3. 自定义函数加载：
    ```yaml
    huggingface_api_key: '@FUNC(load_api_key(model_name="huggingface"))'
    ```

### 1.3 text_generation 任务与原生采样参数

`top_k`、`repetition_penalty`、`do_sample`、`best_of`、`typical_p`、`watermark` **不属于**
chat completions 协议（TGI 的 `ChatRequest` 中并不存在这些字段）。经实测，TGI、
`transformers serve` 等严格校验的后端在 chat 请求中收到这些字段会返回 **HTTP 422
Unexpected fields**。它们是 TGI 原生 `/generate` 路由的参数，因此需要使用 `task: 'text_generation'`：

```yaml
name: 'user_huggingface_tg_llm'
description: 'huggingface native text generation'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
task: 'text_generation'
huggingface_base_url: 'http://localhost:8080'
max_tokens: 512
temperature: 0.7
top_p: 0.9
top_k: 40
repetition_penalty: 1.1
do_sample: true
seed: 42
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_llm'
  class: 'HuggingFaceLLM'
```

参数兼容性一览：

| 参数                   | 说明                 | `task: 'chat'`                | `task: 'text_generation'` |
|----------------------|--------------------|-------------------------------|---------------------------|
| `max_tokens`         | 最大生成长度             | ✅                             | ✅（映射为 `max_new_tokens`）   |
| `temperature`        | 采样温度               | ✅                             | ✅                         |
| `top_p`              | 核采样                | ✅                             | ✅                         |
| `seed`               | 随机种子，用于结果复现        | ✅                             | ✅                         |
| `top_k`              | 只保留概率最高的 k 个 token | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |
| `repetition_penalty` | 重复惩罚系数             | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |
| `do_sample`          | 采样而非贪心解码           | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |
| `best_of`            | 生成多条取最优            | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |
| `typical_p`          | typical 解码         | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |
| `watermark`          | 输出水印               | ⚠️ 走 `extra_body`，严格后端会 422   | ✅                         |

> **说明**：`model_name` 与 `huggingface_base_url` 可以同时配置。此时请求会发往
> `huggingface_base_url`，而 `model_name` 仍会作为请求体中的模型字段发送——如果不发送，
> `huggingface_hub` 会把 URL 本身当作模型名，导致严格后端返回 400。

LLM 组件支持 `call` / `acall`、同步与异步流式，以及 `as_langchain()` 转换为 langchain 的
`BaseChatModel`（`HuggingFaceLangchainInstance`）。

## 2. Embedding 组件

组件类：`agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbedding`，
底层使用 `huggingface_hub` 原生的 `feature_extraction` 接口。

创建一个 yaml 文件，例如 `user_huggingface_embedding.yaml`：

```yaml
name: 'user_huggingface_embedding'
description: 'embedding use huggingface_hub feature extraction'
embedding_model_name: 'sentence-transformers/all-MiniLM-L6-v2'
huggingface_api_key: '${HUGGINGFACE_API_KEY}'
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.huggingface_embedding'
  class: 'HuggingFaceEmbedding'
```

若使用自建的 TEI（Text Embeddings Inference）服务或者专属推理端点，配置 `huggingface_base_url` 即可
（此时 `embedding_model_name` 不再参与请求）：

```yaml
name: 'user_tei_embedding'
description: 'embedding use self-hosted text embeddings inference'
huggingface_base_url: 'http://localhost:8080'
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.huggingface_embedding'
  class: 'HuggingFaceEmbedding'
```

Embedding 组件支持同步 `get_embeddings`、异步 `async_get_embeddings` 以及 `as_langchain()` 转换。
当模型返回的是 token 级向量时，组件会自动做均值池化（mean pooling）得到句向量。

> **note**：`as_langchain()` 优先使用 `langchain_huggingface`；未安装时会回退到组件自带的适配器。
> 不会使用 `langchain_community.HuggingFaceHubEmbeddings`，因为它依赖已在 `huggingface_hub` 1.x
> 中移除的 `InferenceClient.post`，运行时会抛 `AttributeError`。

## 3. 环境设置

必须配置：`HUGGINGFACE_API_KEY`（也兼容 `HF_TOKEN`）
可选配置：`HUGGINGFACE_BASE_URL`、`HUGGINGFACE_PROVIDER`

| 环境变量                    | 作用                                                  |
|-------------------------|-----------------------------------------------------|
| `HUGGINGFACE_API_KEY`   | HuggingFace 访问令牌，未设置时回退读取 `HF_TOKEN`                |
| `HF_TOKEN`              | HuggingFace 官方 SDK 通用令牌变量                           |
| `HUGGINGFACE_BASE_URL`  | 推理端点地址（Inference Endpoints 或自建 TGI / TEI）           |
| `HUGGINGFACE_PROVIDER`  | HF Router 的推理服务商，如 `auto`、`hf-inference`、`together` |

### 3.1 通过 python 代码配置
```python
import os
os.environ['HUGGINGFACE_API_KEY'] = 'hf_***'
os.environ['HUGGINGFACE_PROVIDER'] = 'auto'
```

### 3.2 通过配置文件配置
在项目的 config 目录下的 custom_key.toml 当中，添加配置：
```toml
HUGGINGFACE_API_KEY="hf_******"
HUGGINGFACE_BASE_URL=""
HUGGINGFACE_PROVIDER=""
```

## 4. HUGGINGFACE API KEY 获取
参考 HuggingFace 官方文档：https://huggingface.co/settings/tokens
