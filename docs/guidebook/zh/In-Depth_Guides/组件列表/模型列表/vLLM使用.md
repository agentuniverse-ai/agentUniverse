# vLLM 使用

`VLLMOpenAIStyleLLM` 将自部署的 [vLLM](https://docs.vllm.ai/) 推理服务接入 agentUniverse。vLLM 是一个高吞吐的大模型推理与服务引擎，是在自有基础设施上运行开源权重模型的热门选择：

- **高吞吐**：借助 PagedAttention 与连续批处理（continuous batching），吞吐量相比朴素的 HuggingFace Transformers 部署可提升数十倍。
- **显存高效**：PagedAttention 显著降低 KV cache 的显存浪费。
- **任意开源权重模型**：支持来自 HuggingFace hub 的 Llama、Qwen、Mistral、DeepSeek、GLM、Gemma 等数千个模型。
- **数据私有**：请求提示词不会离开您自己的服务器。

vLLM 提供完全 **兼容 OpenAI** 的 Chat Completions API（默认地址 `http://localhost:8000/v1`），因此 `VLLMOpenAIStyleLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置服务地址、可选的鉴权信息以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_vllm_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_vllm_llm'
description: 'user llm served by a local vLLM OpenAI-compatible server'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
max_tokens: 2048
temperature: 0.7
streaming: True
api_key: 'EMPTY'
api_base: '${VLLM_API_BASE}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.vllm_openai_style_llm'
  class: 'VLLMOpenAIStyleLLM'
```

`model_name` 必须与启动 vLLM 服务时使用的模型标识（即 `--model` 参数，例如 `meta-llama/Llama-3.1-8B-Instruct`）保持一致。示例工程中同时附带了一批开箱即用的配置，位于
`examples/sample_standard_app/intelligence/agentic/llm/buildin/vllm/` 与
`examples/sample_apps/toolkit_demo_app/intelligence/agentic/llm/buildin/vllm/`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入字符串。

    ```yaml
    api_base: 'http://localhost:8000/v1'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_base: '${VLLM_API_BASE}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载。

    ```yaml
    api_base: '@FUNC(load_api_base(model_name="vllm"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_base` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 模型选择

与云服务商不同，vLLM 服务可以托管 HuggingFace hub 上的**任意**模型，因此下表仅列出常用于 vLLM 部署的模型及其最大上下文窗口（输入 + 输出 token）。相同的取值也内置在 `VLLM_MAX_CONTEXT_LENGTH` 表中（`VLLMOpenAIStyleLLM.max_context_length()` 会查询该表），agentUniverse 无需访问服务即可正确估算 prompt 预算。

| 模型名称（HuggingFace id） | 上下文长度 |
| --------------------------- | ---------- |
| `meta-llama/Llama-2-7b-chat-hf` | 4096 |
| `meta-llama/Llama-2-70b-chat-hf` | 4096 |
| `meta-llama/Meta-Llama-3-8B-Instruct` | 8192 |
| `meta-llama/Meta-Llama-3-70B-Instruct` | 8192 |
| `meta-llama/Llama-3.1-8B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.1-70B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.1-405B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.3-70B-Instruct` | 131072 (128k) |
| `Qwen/Qwen2-7B-Instruct` | 32768 |
| `Qwen/Qwen2.5-7B-Instruct` | 32768 |
| `Qwen/Qwen2.5-72B-Instruct` | 32768 |
| `Qwen/Qwen3-8B` | 32768 |
| `Qwen/Qwen3-32B` | 32768 |
| `mistralai/Mistral-7B-Instruct-v0.2` | 32768 |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 32768 |
| `mistralai/Mixtral-8x22B-Instruct-v0.1` | 65536 |
| `google/gemma-2-9b-it` | 8192 |

**重要提示**：实际可用的上下文窗口由启动 vLLM 服务时的 `--max-model-len` 参数决定，可能小于模型的原生上限。如果您的模型不在上表中，或者启动服务时缩小了 `--max-model-len`，请在 yaml 中显式配置该值：

```yaml
max_context_length: 32768
```

显式配置的 `max_context_length` 优先级始终高于内置表格；未知模型会回退到一个保守的默认值 4096。

---

## 3. 环境配置

示例 yaml 使用了环境变量占位符，以下说明如何设置这些变量。

可选：`VLLM_API_BASE`（默认 `http://localhost:8000/v1`）、`VLLM_API_KEY`

本地启动的 vLLM 服务**不需要** API key；由于 OpenAI 客户端要求该字段非空，组件将 `api_key` 默认为占位字符串 `'EMPTY'`。仅当服务部署在带鉴权的网关之后时才需要设置 `VLLM_API_KEY`。

### 3.1 通过 Python 代码配置

```python
import os
os.environ['VLLM_API_BASE'] = 'http://localhost:8000/v1'
os.environ['VLLM_API_KEY'] = 'EMPTY'
```

### 3.2 通过配置文件配置

在项目 `config` 目录下的 `custom_key.toml` 文件中添加如下配置：

```toml
VLLM_API_BASE="http://localhost:8000/v1"
VLLM_API_KEY="EMPTY"
```

---

## 4. 启动 vLLM 服务

1. 安装 vLLM（参见[官方安装指南](https://docs.vllm.ai/en/latest/getting_started/installation.html)）：

    ```bash
    pip install vllm
    ```

2. 使用您选择的模型启动 OpenAI 兼容服务：

    ```bash
    python -m vllm.entrypoints.openai.api_server \
        --model meta-llama/Llama-3.1-8B-Instruct \
        --port 8000
    ```

3. （可选）通过 Docker 部署，适合生产机器：

    ```bash
    docker run --gpus all -p 8000:8000 --ipc=host \
        -v ~/.cache/huggingface:/root/.cache/huggingface \
        vllm/vllm-openai:latest \
        --model meta-llama/Llama-3.1-8B-Instruct
    ```

4. 在接入 agentUniverse 之前，先确认服务可访问：

    ```bash
    curl http://localhost:8000/v1/models
    ```

大模型可增加 `--tensor-parallel-size <GPU数量>`；为控制长上下文的显存占用可增加 `--max-model-len 32768`（并在组件中同步配置 `max_context_length`）。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.vllm_openai_style_llm import VLLMOpenAIStyleLLM

llm = VLLMOpenAIStyleLLM(model_name='meta-llama/Llama-3.1-8B-Instruct')

# 非流式
output = llm.call(messages=[{"role": "user", "content": "你好！"}])
print(output.text)

# 流式
for chunk in llm.call(messages=[{"role": "user", "content": "从 1 数到 5。"}], streaming=True):
    print(chunk.text, end='')

# 异步
import asyncio
async def main():
    out = await llm.acall(messages=[{"role": "user", "content": "你好！"}])
    print(out.text)
asyncio.run(main())
```

由于 vLLM 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的全部能力——工具调用、LangChain 集成、链路追踪——均可直接使用。

---

## 6. 使用技巧

- vLLM 服务端提供的扩展采样参数（例如 beam search 相关控制）应通过 yaml 中的 `ext_params` 或 `call`/`acall` 的 `extra_body` 关键字参数转发，基类 `OpenAIStyleLLM` 会将其合并进请求体。
- 建议启动服务时显式指定 `--max-model-len`，并在组件 yaml 中配置相同的 `max_context_length`，使 agentUniverse 的 prompt 预算与服务端实际接受的范围保持一致。
- 在单张消费级 GPU 上，`Qwen/Qwen2.5-7B-Instruct` 是中英双语 Agent 负载的稳妥默认选择；`meta-llama/Llama-3.1-8B-Instruct` 则是常见的通用起点。
- 示例工程自带 `vllm` 开箱即用实例（如 `vllm-llama-3.1-8b`、`vllm-qwen-2.5-7b`），设置好 `VLLM_API_BASE` 后即可在 Agent 配置中按名称直接引用。
