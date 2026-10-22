# LM Studio 使用

`LMStudioLLM` 将 [LM Studio](https://lmstudio.ai) 接入 agentUniverse。LM Studio 是一款支持 Windows、macOS 与 Linux 的**完全本地化**大模型桌面运行时：它从 Hugging Face 下载 GGUF 权重（Llama、Qwen、Mistral、Gemma 等），加载到本机 CPU/GPU 上运行，并通过内置的本地 API 服务器对外提供服务。

该服务器默认在 `http://localhost:1234/v1` 提供完全 **兼容 OpenAI** 的 Chat Completions 接口，因此 `LMStudioLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置本地端点与鉴权信息即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

当您希望获得完全离线、保护隐私且零 API 成本的智能体运行时时，LM Studio 是 agentUniverse 的理想选择。它与内置的 [ollama](Ollama使用.md) 组件相互独立：LM Studio 是另一个桌面运行时，默认端口不同（1234 vs ollama 的 11434），并采用以图形界面为主的模型管理方式。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_lmstudio_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_lmstudio_llm'
description: 'user lm studio llm powered by locally served GGUF models'
model_name: 'qwen2.5-7b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 32768
api_key: '${LMSTUDIO_API_KEY}'
api_base: '${LMSTUDIO_API_BASE}'
proxy: '${LMSTUDIO_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.lmstudio_llm'
  class: 'LMStudioLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/lmstudio_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'lm-studio'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${LMSTUDIO_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="lmstudio"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

与云端厂商不同，LM Studio **没有固定的模型目录**：您在应用内从 Hugging Face 下载 GGUF 模型，并以 LM Studio 分配的标识符（如 `qwen2.5-7b-instruct`、`llama-3.1-8b-instruct`、`mistral-7b`）对外提供服务。常见下载模型的上下文窗口如下：

| 模型名称（LM Studio 中显示）       | 上下文长度        |
| ---------------------------------- | ----------------- |
| `qwen2.5-7b-instruct`              | 32768             |
| `llama-3.1-8b-instruct`            | 131072            |
| `mistral-7b`                       | 32768             |
| 任意私有 GGUF 微调模型              | 取决于模型        |

由于模型名称完全由用户决定，`LMStudioLLM` **不内置上下文长度表**，而是：

- **在 yaml 中设置 `max_context_length`** 为所下载模型的真实窗口大小（参见上方示例），该值优先级最高。
- 若未配置，`LMStudioLLM` 会保守地回退到 8192 token 的默认值，保证 prompt 预算检查安全。

您可以运行 `curl http://localhost:1234/v1/models` 或在应用的 **Local Server** 标签页中查看当前 LM Studio 实际提供的模型标识符。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

可选配置：`LMSTUDIO_API_KEY`、`LMSTUDIO_API_BASE`、`LMSTUDIO_PROXY`

三个变量均为可选。未设置时，`LMStudioLLM` 使用 `http://localhost:1234/v1`、占位 API 密钥以及不走代理。

### 3.1 通过 Python 代码配置

```python
import os
os.environ['LMSTUDIO_API_BASE'] = 'http://localhost:1234/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
LMSTUDIO_API_KEY=""
LMSTUDIO_API_BASE="http://localhost:1234/v1"
LMSTUDIO_PROXY=""
```

---

## 4. 无需 API KEY

本地 LM Studio 服务器不对请求做鉴权 —— 它接受任意 bearer token。但底层 OpenAI 客户端在缺少密钥时无法构造，因此 `LMStudioLLM` 将 `api_key` 默认设为无害的占位值 `lm-studio`。

只有当 LM Studio 服务器前部署了带鉴权的网关时，才需要将 `LMSTUDIO_API_KEY`（或 yaml 中的 `api_key` 字段）设置为真实令牌。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.lmstudio_llm import LMStudioLLM

llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')

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

由于 LM Studio 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_lmstudio_llm` 的模板配置（`lmstudio_llm.yaml.example`）。启动 LM Studio 本地服务器（**Developer -> Start Server**，默认端口 1234）、下载一个模型、将模板重命名为 `lmstudio_llm.yaml` 后即可直接使用 —— 无需任何凭证。
- 请在 yaml 中将 `max_context_length` 设置为与所下载模型匹配的值；新版 Llama 3.1 与 Qwen2.5 通常支持 32k-128k 窗口，agentUniverse 会用它来做 prompt 预算检查。
- LM Studio 与 ollama 可以并行运行：两者默认端口不同（1234 vs 11434），因此可以通过 `LMSTUDIO_API_BASE` / ollama 的 base URL 同时将两种运行时暴露给您的智能体。
- 局域网内远程机器运行 LM Studio 时，将 `LMSTUDIO_API_BASE` 指向 `http://<主机>:1234/v1`，并先在应用中开启 "Serve on Local Network"。
