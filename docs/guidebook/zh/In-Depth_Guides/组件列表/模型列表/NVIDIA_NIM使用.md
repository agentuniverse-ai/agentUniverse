# NVIDIA NIM 使用

`NvidiaNimLLM` 将 [NVIDIA NIM](https://build.nvidia.com) 的 API 接入 agentUniverse。NVIDIA NIM（NVIDIA Inference Microservices）是 NVIDIA AI Foundation 上的托管模型目录，以加速推理方式提供旗舰开源与社区模型，例如 `meta/llama-3.1-405b-instruct`、`nvidia/nemotron-4-340b-instruct` 和 `deepseek-ai/deepseek-r1`。

NIM 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://integrate.api.nvidia.com/v1`），因此 `NvidiaNimLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 NIM 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_nvidia_nim_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_nvidia_nim_llm'
description: 'user nvidia nim llm powered by the NVIDIA NIM models'
model_name: 'meta/llama-3.1-405b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NVIDIA_API_KEY}'
api_base: 'https://integrate.api.nvidia.com/v1'
proxy: '${NVIDIA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.nvidia_nim_llm'
  class: 'NvidiaNimLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/nvidia_nim_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'nvapi-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${NVIDIA_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="nvidia_nim"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

NVIDIA 会持续上线新的 NIM 端点。下表列出了 NIM API 上的常用模型及其上下文窗口大小（输入 + 输出 token，为参考值）。这些数值同样硬编码在 `NvidiaNimLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                          | 上下文长度       |
| --------------------------------- | ---------------- |
| `meta/llama-3.1-405b-instruct`    | 131072 (128k)    |
| `meta/llama-3.1-70b-instruct`     | 131072 (128k)    |
| `nvidia/nemotron-4-340b-instruct` | 4096 (4k)        |
| `deepseek-ai/deepseek-r1`         | 131072 (128k)    |

该表为 **参考值而非穷尽列表**：最新上线的 NIM 模型上下文窗口可能差异较大（例如 Nemotron-4 340B 仅提供 4k 窗口），因此不在表中的模型会保守地回退到 8192 token。如需为这类模型声明精确上限，请在 yaml 中显式设置 `max_context_length` 字段——显式配置的值始终优先于内置表格。

请以 [build.nvidia.com](https://build.nvidia.com) 模型页面公布的最新模型列表为准。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`NVIDIA_API_KEY`（同时兼容 NVIDIA 工具链使用的 `NVAPI_KEY` 别名作为回退）
可选配置：`NVIDIA_API_BASE`、`NVIDIA_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['NVIDIA_API_KEY'] = 'nvapi-***'
os.environ['NVIDIA_API_BASE'] = 'https://integrate.api.nvidia.com/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
NVIDIA_API_KEY="nvapi-******"
NVIDIA_API_BASE="https://integrate.api.nvidia.com/v1"
NVIDIA_PROXY=""
```

---

## 4. NVIDIA NIM API KEY 获取

1. 登录 [https://build.nvidia.com](https://build.nvidia.com)。
2. 选择任意模型并点击 **Get API Key**（或进入个人中心）生成密钥。
3. 复制生成的密钥（通常以 `nvapi-` 开头），并赋值给 `NVIDIA_API_KEY`。

新注册账户可获得试用积分；计费、速率限制与可用模型说明详见 [NVIDIA NIM 官方文档](https://docs.nvidia.com/nim/)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.nvidia_nim_llm import NvidiaNimLLM

llm = NvidiaNimLLM(model_name='meta/llama-3.1-405b-instruct')

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

由于 NIM 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_nvidia_nim_llm` 的模板配置（`nvidia_nim_llm.yaml.example`），用户将其重命名为 `nvidia_nim_llm.yaml` 并配置 `NVIDIA_API_KEY` 之后即可直接使用。
- 较重的推理任务可选择 `meta/llama-3.1-405b-instruct` 或 `deepseek-ai/deepseek-r1`（均为 128k 上下文窗口），低延迟智能体场景可选择 `meta/llama-3.1-70b-instruct`。
- 注意 `nvidia/nemotron-4-340b-instruct` 虽然参数量大，但仅提供 4k 上下文窗口；对于尚未纳入内置上下文表的 NIM 模型，建议在 yaml 中显式设置 `max_context_length`，以保证 prompt 预算估算准确。
