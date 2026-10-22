# Novita AI 使用

`NovitaLLM` 将 [Novita AI](https://novita.ai) 的模型 API 接入 agentUniverse。Novita AI 是一站式推理平台，通过一个按量付费的 API 提供来自众多厂商的**开源权重**模型：Meta Llama（`meta-llama/llama-3.1-70b-instruct`）、DeepSeek（`deepseek/deepseek_v3`）、Qwen（`qwen/qwen-2.5-32b-instruct`）、Mistral（`mistralai/mistral-nemo`）等。

Novita 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.novita.ai/v3/openai`），因此 `NovitaLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Novita 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_novita_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_novita_llm'
description: 'user novita llm powered by the Novita AI open models'
model_name: 'meta-llama/llama-3.1-70b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NOVITA_API_KEY}'
api_base: 'https://api.novita.ai/v3/openai'
proxy: '${NOVITA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.novita_llm'
  class: 'NovitaLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/novita_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'novita-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${NOVITA_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="novita"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Novita 使用小写的 `组织/模型` 名称来标识模型，例如 `meta-llama/llama-3.1-70b-instruct`。下表列出了 Novita 上常见的模型及其上下文窗口大小（输入 + 输出 token），仅供参考。这些数值同样硬编码在 `NovitaLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                                   | 上下文长度        |
| ------------------------------------------ | ----------------- |
| `meta-llama/llama-3.1-405b-instruct`       | 131072 (128k)     |
| `meta-llama/llama-3.1-70b-instruct`        | 131072 (128k)     |
| `meta-llama/llama-3.1-8b-instruct`         | 131072 (128k)     |
| `meta-llama/llama-3.3-70b-instruct`        | 131072 (128k)     |
| `meta-llama/llama-3.2-3b-instruct`         | 131072 (128k)     |
| `deepseek/deepseek_v3`                     | 131072 (128k)     |
| `deepseek/deepseek_r1`                     | 131072 (128k)     |
| `qwen/qwen-2.5-72b-instruct`               | 32768 (32k)       |
| `qwen/qwen-2.5-32b-instruct`               | 32768 (32k)       |
| `mistralai/mistral-nemo`                   | 131072 (128k)     |

请以 [Novita AI 模型列表](https://novita.ai/models) 公布的最新模型目录为准（Novita 会持续上架和轮换模型）。如果某个模型不在上表中，`NovitaLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`NOVITA_API_KEY`
可选配置：`NOVITA_API_BASE`、`NOVITA_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['NOVITA_API_KEY'] = 'novita-***'
os.environ['NOVITA_API_BASE'] = 'https://api.novita.ai/v3/openai'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
NOVITA_API_KEY="novita-******"
NOVITA_API_BASE="https://api.novita.ai/v3/openai"
NOVITA_PROXY=""
```

---

## 4. NOVITA API KEY 获取

1. 注册并登录 [https://novita.ai](https://novita.ai)。
2. 进入控制台的 **Key Management** 密钥管理页面（`https://novita.ai/dashboard/keys`）。
3. 创建新的 API 密钥，复制生成的密钥，并赋值给 `NOVITA_API_KEY`。

计费、速率限制与免费额度说明详见 [Novita AI 官方文档](https://novita.ai/docs)与[定价页面](https://novita.ai/pricing)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.novita_llm import NovitaLLM

llm = NovitaLLM(model_name='meta-llama/llama-3.1-70b-instruct')

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

由于 Novita 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_novita_llm` 的模板配置（`novita_llm.yaml.example`），用户将其重命名为 `novita_llm.yaml` 并配置 `NOVITA_API_KEY` 之后即可直接使用。
- Novita 在同一个端点下提供众多开源模型，在 Llama、DeepSeek 与 Qwen 之间切换只需修改 `model_name`，无需为每个厂商分别注册账号或安装 SDK。
- Llama 3.1/3.3 与 DeepSeek-V3 系列提供 128k token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体。
