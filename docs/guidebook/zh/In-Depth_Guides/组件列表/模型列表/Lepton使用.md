# Lepton AI 使用

`LeptonLLM` 将 [Lepton AI](https://lepton.ai) 的 API 接入 agentUniverse。Lepton AI（现已并入 NVIDIA DGX Cloud Lepton）是一个托管式 AI 平台，既提供自部署的开源模型（如 `llama3.1-8b`、`llama3.1-70b`、`mistral-7b`），也通过统一的 API 与计费体系提供第三方市场的模型（如 `gpt-4o-mini`）。

Lepton 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.lepton.run/api/v1`），因此 `LeptonLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Lepton 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_lepton_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_lepton_llm'
description: 'user lepton llm powered by the Lepton AI models'
model_name: 'llama3.1-8b'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${LEPTON_API_KEY}'
api_base: 'https://api.lepton.run/api/v1'
proxy: '${LEPTON_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.lepton_llm'
  class: 'LeptonLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/lepton_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'lepton-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${LEPTON_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="lepton"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Lepton 会持续上线新的自部署模型与市场模型。下表列出了 Lepton API 上的常用模型及其上下文窗口大小（输入 + 输出 token，为参考值）。这些数值同样硬编码在 `LeptonLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称       | 上下文长度       |
| -------------- | ---------------- |
| `llama3.1-8b`  | 131072 (128k)    |
| `llama3.1-70b` | 131072 (128k)    |
| `mistral-7b`   | 32768 (32k)      |
| `gpt-4o-mini`  | 131072 (128k)    |

该表为 **参考值而非穷尽列表**：市场模型与最新上线模型的上下文窗口可能差异较大，因此不在表中的模型会保守地回退到 8192 token。如需为这类模型声明精确上限，请在 yaml 中显式设置 `max_context_length` 字段——显式配置的值始终优先于内置表格。

请以 Lepton 控制台 / [官方 API 文档](https://docs.nvidia.com/dgx-cloud/lepton/reference/api) 公布的最新模型列表为准。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`LEPTON_API_KEY`
可选配置：`LEPTON_API_BASE`、`LEPTON_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['LEPTON_API_KEY'] = 'lepton-***'
os.environ['LEPTON_API_BASE'] = 'https://api.lepton.run/api/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
LEPTON_API_KEY="lepton-******"
LEPTON_API_BASE="https://api.lepton.run/api/v1"
LEPTON_PROXY=""
```

---

## 4. Lepton API KEY 获取

1. 登录 [https://dashboard.lepton.ai](https://dashboard.lepton.ai)。
2. 进入 **Settings -> API Tokens**（或 **Secret Keys**）页面并创建新的 workspace token。
3. 复制生成的密钥，并赋值给 `LEPTON_API_KEY`。

计费、速率限制与可用模型说明详见 [Lepton 官方 API 文档](https://docs.nvidia.com/dgx-cloud/lepton/reference/api)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.lepton_llm import LeptonLLM

llm = LeptonLLM(model_name='llama3.1-8b')

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

由于 Lepton 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_lepton_llm` 的模板配置（`lepton_llm.yaml.example`），用户将其重命名为 `lepton_llm.yaml` 并配置 `LEPTON_API_KEY` 之后即可直接使用。
- 较重的推理任务可选择 `llama3.1-70b`，低延迟、高吞吐的智能体场景可选择 `llama3.1-8b` / `mistral-7b`；两个 Llama 3.1 部署均提供 128k 上下文窗口。
- 对于尚未纳入内置上下文表的市场模型（如 `gpt-4o-mini`），建议在 yaml 中显式设置 `max_context_length`，以保证 prompt 预算估算准确。
