# llama.cpp 使用

`LlamaCppLLM` 将 [llama.cpp](https://github.com/ggml-org/llama.cpp) 接入 agentUniverse。llama.cpp 是 **GGUF** 大模型的参考 C/C++ 推理引擎：其 `llama-server` 程序加载本地 `.gguf` 权重文件（Llama、Qwen、Mistral、Gemma 等）到本机 CPU/GPU 上运行，并通过内置的本地 API 服务器对外提供服务。

该服务器默认在 `http://localhost:8080/v1` 提供完全 **兼容 OpenAI** 的 Chat Completions 接口，因此 `LlamaCppLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置本地端点与鉴权信息即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

当您希望获得完全离线、保护隐私、零 API 成本且完全掌控推理参数的智能体运行时时，llama.cpp 是 agentUniverse 的理想选择。它与内置的 [ollama](Ollama使用.md) 组件以及 LM Studio 组件相互独立：llama-server 是另一个运行时（纯命令行服务器，没有图形界面和模型市场），默认端口也不同（8080 vs ollama 的 11434、LM Studio 的 1234）。

---

## 1. 启动 llama-server

构建或下载 llama.cpp 后，使用任意本地 GGUF 模型启动 `llama-server`：

```bash
# 在 llama.cpp 仓库根目录下（通过 make/cmake 构建完成后）
./llama-server -m models/qwen2.5-7b-instruct-q4_k_m.gguf -c 32768 --alias qwen2.5-7b-instruct --port 8080
```

- `-m` 指向要服务的 GGUF 文件。
- `-c` 设置服务器分配的上下文窗口 —— 请与下方 yaml 中的 `max_context_length` 保持一致。
- `--alias` 设置 OpenAI 兼容接口上报的模型标识符；不指定时使用文件名。
- `--port` 默认为 8080；使用其他端口时需同时调整 `LLAMACPP_API_BASE`。

可以通过 `curl http://localhost:8080/v1/models` 验证端点是否可用。

---

## 2. 创建相关文件

创建一个 yaml 文件，例如 `user_llamacpp_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_llamacpp_llm'
description: 'user llama.cpp llama-server llm powered by locally served GGUF models'
model_name: 'qwen2.5-7b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 32768
api_key: '${LLAMACPP_API_KEY}'
api_base: '${LLAMACPP_API_BASE}'
proxy: '${LLAMACPP_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.llamacpp_llm'
  class: 'LlamaCppLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/llamacpp_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'no-key'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${LLAMACPP_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="llamacpp"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 3. 选择模型

与云端厂商不同，llama-server **没有固定的模型目录**：您将服务器指向任意本地 GGUF 文件，并以任意 `--alias` 标识符（如 `qwen2.5-7b-instruct`、`llama-3.1-8b-instruct`、`mistral-7b`）对外提供服务。常见模型的上下文窗口如下：

| 模型别名（通过 `--alias` 指定）      | 上下文长度        |
| ---------------------------------- | ----------------- |
| `qwen2.5-7b-instruct`              | 32768             |
| `llama-3.1-8b-instruct`            | 131072            |
| `mistral-7b`                       | 32768             |
| 任意私有 GGUF 微调模型              | 取决于模型        |

由于模型别名完全由用户决定，`LlamaCppLLM` **不内置上下文长度表**，而是：

- **在 yaml 中设置 `max_context_length`** 为服务器启动时的窗口大小（即 `-c` 参数），该值优先级最高。
- 若未配置，`LlamaCppLLM` 会保守地回退到 8192 token 的默认值，保证 prompt 预算检查安全。

您可以运行 `curl http://localhost:8080/v1/models` 查看当前 llama-server 实际提供的模型标识符。

---

## 4. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

可选配置：`LLAMACPP_API_KEY`、`LLAMACPP_API_BASE`、`LLAMACPP_PROXY`

三个变量均为可选。未设置时，`LlamaCppLLM` 使用 `http://localhost:8080/v1`、占位 API 密钥以及不走代理。

### 4.1 通过 Python 代码配置

```python
import os
os.environ['LLAMACPP_API_BASE'] = 'http://localhost:8080/v1'
```

### 4.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
LLAMACPP_API_KEY=""
LLAMACPP_API_BASE="http://localhost:8080/v1"
LLAMACPP_PROXY=""
```

---

## 5. 无需 API KEY

本地 llama-server 不对请求做鉴权 —— 它接受任意 bearer token。但底层 OpenAI 客户端在缺少密钥时无法构造，因此 `LlamaCppLLM` 将 `api_key` 默认设为无害的占位值 `no-key`。

只有当 llama-server 前部署了带鉴权的网关时，才需要将 `LLAMACPP_API_KEY`（或 yaml 中的 `api_key` 字段）设置为真实令牌。

---

## 6. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.llamacpp_llm import LlamaCppLLM

llm = LlamaCppLLM(model_name='qwen2.5-7b-instruct')

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

由于 llama-server 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 7. Tips

- agentuniverse 源码中内置了一个 name 为 `default_llamacpp_llm` 的模板配置（`llamacpp_llm.yaml.example`）。使用您的 GGUF 模型启动 `llama-server`（默认端口 8080）、将模板重命名为 `llamacpp_llm.yaml` 后即可直接使用 —— 无需任何凭证。
- 请在 yaml 中将 `max_context_length` 设置为与服务器 `-c` 参数一致的值；新版 Llama 3.1 与 Qwen2.5 通常支持 32k-128k 窗口，agentUniverse 会用它来做 prompt 预算检查。
- llama-server、ollama 与 LM Studio 可以并行运行：三者默认端口不同（8080 vs 11434 vs 1234），因此可以通过 `LLAMACPP_API_BASE` / ollama 的 base URL / LM Studio 的 base URL 同时将多种运行时暴露给您的智能体。
- 局域网内远程机器运行 llama-server 时，以 `--host 0.0.0.0` 启动服务器，并将 `LLAMACPP_API_BASE` 指向 `http://<主机>:8080/v1`。
