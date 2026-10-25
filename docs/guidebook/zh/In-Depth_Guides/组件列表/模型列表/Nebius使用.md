# Nebius AI Studio 使用

`NebiusLLM` 将 [Nebius AI Studio](https://nebius.com/ai-studio) 的 API 接入 agentUniverse。AI Studio 是 Nebius Group 旗下的推理服务平台，通过一个按量付费的 API 提供来自众多厂商的**开源权重**模型：Meta Llama（`meta-llama/Meta-Llama-3.1-70B-Instruct`）、DeepSeek（`deepseek-ai/DeepSeek-V3`）、Qwen（`Qwen/Qwen2.5-32B-Instruct`）、Mistral（`mistralai/Mistral-Nemo-Instruct-2407`）等。

Nebius AI Studio 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.studio.nebius.com/v1`），因此 `NebiusLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Nebius 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_nebius_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_nebius_llm'
description: 'user nebius llm powered by the Nebius AI Studio open models'
model_name: 'meta-llama/Meta-Llama-3.1-70B-Instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NEBIUS_API_KEY}'
api_base: 'https://api.studio.nebius.com/v1'
proxy: '${NEBIUS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.nebius_llm'
  class: 'NebiusLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/nebius_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'nebius-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${NEBIUS_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="nebius"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Nebius AI Studio 使用完整的 `组织/模型` 名称来标识模型，例如 `meta-llama/Meta-Llama-3.1-70B-Instruct`。下表列出了 AI Studio 上常见的模型及其上下文窗口大小（输入 + 输出 token），仅供参考。这些数值同样硬编码在 `NebiusLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                                          | 上下文长度        |
| ------------------------------------------------- | ----------------- |
| `meta-llama/Meta-Llama-3.1-405B-Instruct`         | 131072 (128k)     |
| `meta-llama/Meta-Llama-3.1-70B-Instruct`          | 131072 (128k)     |
| `meta-llama/Meta-Llama-3.1-8B-Instruct`           | 131072 (128k)     |
| `meta-llama/Llama-3.3-70B-Instruct`               | 131072 (128k)     |
| `meta-llama/Llama-3.2-3B-Instruct`                | 131072 (128k)     |
| `deepseek-ai/DeepSeek-V3`                         | 131072 (128k)     |
| `deepseek-ai/DeepSeek-V3-0324`                    | 131072 (128k)     |
| `deepseek-ai/DeepSeek-R1`                         | 131072 (128k)     |
| `Qwen/Qwen2.5-32B-Instruct`                       | 131072 (128k)     |
| `Qwen/Qwen2.5-Coder-32B-Instruct`                 | 131072 (128k)     |
| `Qwen/QwQ-32B`                                    | 131072 (128k)     |
| `mistralai/Mistral-Nemo-Instruct-2407`            | 131072 (128k)     |
| `mistralai/Mixtral-8x22B-Instruct-v0.1`           | 65536 (64k)       |
| `microsoft/Phi-3.5-MoE-Instruct`                  | 131072 (128k)     |
| `google/gemma-2-27b-it`                           | 8192 (8k)         |

请以 [Nebius AI Studio 官方文档](https://docs.nebius.com/studio) 公布的最新模型目录为准（Nebius 会持续上架和轮换模型）。如果某个模型不在上表中，`NebiusLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`NEBIUS_API_KEY`
可选配置：`NEBIUS_API_BASE`、`NEBIUS_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['NEBIUS_API_KEY'] = 'nebius-***'
os.environ['NEBIUS_API_BASE'] = 'https://api.studio.nebius.com/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
NEBIUS_API_KEY="nebius-******"
NEBIUS_API_BASE="https://api.studio.nebius.com/v1"
NEBIUS_PROXY=""
```

---

## 4. NEBIUS API KEY 获取

1. 登录 [https://studio.nebius.ai](https://studio.nebius.ai)（也可通过 Nebius 控制台进入）。
2. 进入 **API Keys** 页面并创建新的密钥。
3. 复制生成的密钥，并赋值给 `NEBIUS_API_KEY`。

计费、速率限制与免费额度说明详见 [Nebius 官方文档](https://docs.nebius.com)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.nebius_llm import NebiusLLM

llm = NebiusLLM(model_name='meta-llama/Meta-Llama-3.1-70B-Instruct')

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

由于 Nebius AI Studio 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_nebius_llm` 的模板配置（`nebius_llm.yaml.example`），用户将其重命名为 `nebius_llm.yaml` 并配置 `NEBIUS_API_KEY` 之后即可直接使用。
- AI Studio 在同一个端点下提供众多开源模型，在 Llama、DeepSeek 与 Qwen 之间切换只需修改 `model_name`，无需为每个厂商分别注册账号或安装 SDK。
- Llama 3.1/3.3、DeepSeek-V3 与 Qwen2.5 系列提供 128k token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体。
