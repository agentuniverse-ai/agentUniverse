# GPUStack 使用

`GPUStackLLM` 将 [GPUStack](https://gpustack.ai) 接入 agentUniverse。GPUStack 是一个开源的 GPU 集群管理平台：它将多台机器（服务器、工作站、Apple 芯片 Mac 等）的 GPU 聚合为统一集群，把模型部署调度到可用设备上，并通过 GPUStack 服务器的网关对外提供所有已部署模型的服务。

该网关默认在 `http://localhost:80/v1` 提供完全 **兼容 OpenAI** 的 Chat Completions 接口，因此 `GPUStackLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置网关端点与鉴权信息即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

当您希望获得自建、可横向扩展的多 GPU 推理平台且零 API 成本时，GPUStack 是 agentUniverse 的理想选择：智能体可以通过一个稳定的 OpenAI 风格端点使用集群运维者部署的任意模型（Llama、Qwen、DeepSeek 等），而无需关心模型实际运行在哪块 GPU 上。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_gpustack_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_gpustack_llm'
description: 'user gpustack llm powered by models deployed on a self-hosted GPUStack gateway'
model_name: 'llama3.1-8b'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 131072
api_key: '${GPUSTACK_API_KEY}'
api_base: '${GPUSTACK_API_BASE}'
proxy: '${GPUSTACK_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.gpustack_llm'
  class: 'GPUStackLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/gpustack_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'gpustack'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${GPUSTACK_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="gpustack"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

与云端厂商不同，GPUStack **没有固定的模型目录**：由集群运维者在集群内部署模型，并以部署时指定的名称（如 `llama3.1-8b`、`qwen2.5-72b`、`deepseek-r1`）对外提供服务。常见部署模型的上下文窗口如下：

| 模型名称（GPUStack 中部署的名称） | 上下文长度        |
| ---------------------------------- | ----------------- |
| `llama3.1-8b`                      | 131072            |
| `qwen2.5-72b`                      | 32768             |
| `deepseek-r1`                      | 取决于模型        |
| 任意私有部署的微调模型              | 取决于模型        |

由于部署的模型名称完全由运维者决定，`GPUStackLLM` **不内置上下文长度表**，而是：

- **在 yaml 中设置 `max_context_length`** 为所部署模型的真实窗口大小（参见上方示例），该值优先级最高。
- 若未配置，`GPUStackLLM` 会保守地回退到 8192 token 的默认值，保证 prompt 预算检查安全。

您可以运行 `curl http://localhost:80/v1/models`（开启鉴权时携带 `Authorization: Bearer <API key>` 请求头）或在 GPUStack 界面的 "Models" 页面查看当前集群实际提供的模型。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

可选配置：`GPUSTACK_API_KEY`、`GPUSTACK_API_BASE`、`GPUSTACK_PROXY`

三个变量均为可选。未设置时，`GPUStackLLM` 使用 `http://localhost:80/v1`、占位 API 密钥以及不走代理。

### 3.1 通过 Python 代码配置

```python
import os
os.environ['GPUSTACK_API_BASE'] = 'http://localhost:80/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
GPUSTACK_API_KEY=""
GPUSTACK_API_BASE="http://localhost:80/v1"
GPUSTACK_PROXY=""
```

---

## 4. API KEY 说明

GPUStack 网关通常默认启用 API Key 鉴权（在 GPUStack 界面的 "API Keys" 页面创建），此时请将 `GPUSTACK_API_KEY`（或 yaml 中的 `api_key` 字段）设置为该密钥。

GPUStack 网关也可以以无鉴权方式运行（例如隔离的实验集群）。由于底层 OpenAI 客户端在缺少密钥时无法构造，此时 `GPUStackLLM` 将 `api_key` 默认设为无害的占位值 `gpustack` —— 无鉴权网关接受任意 bearer token，因此无需任何配置。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.gpustack_llm import GPUStackLLM

llm = GPUStackLLM(model_name='llama3.1-8b')

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

由于 GPUStack 网关兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentUniverse 源码中内置了一个 name 为 `default_gpustack_llm` 的模板配置（`gpustack_llm.yaml.example`）。在 GPUStack 集群中部署一个模型、开启鉴权时创建一个 API Key、将模板重命名为 `gpustack_llm.yaml` 后即可直接使用。
- 请在 yaml 中将 `max_context_length` 设置为与所部署模型匹配的值；新版 Llama 3.1 与 Qwen2.5 通常支持 32k-128k 窗口，agentUniverse 会用它来做 prompt 预算检查。
- 当 GPUStack 服务器不在本机或使用非默认端口时，将 `GPUSTACK_API_BASE` 指向您的网关地址，例如 `http://gpustack.internal:80/v1`。
- GPUStack 可以与其他本地运行时（ollama、LM Studio、vLLM）并行运行；各组件使用独立的 `*_API_BASE`，您的智能体可以同时接入多个推理平台。
