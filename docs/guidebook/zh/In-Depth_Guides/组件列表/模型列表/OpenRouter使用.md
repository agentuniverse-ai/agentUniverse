# OpenRouter 使用

`OpenRouterLLM` 将 [OpenRouter](https://openrouter.ai) 接入 agentUniverse。OpenRouter 是一个统一的模型网关，通过单个 **兼容 OpenAI** 的 Chat Completions API 聚合了来自数十家提供商（OpenAI、Anthropic、Google、Meta、Mistral、DeepSeek、Qwen、xAI 等）的 **数百个大模型**，只需一个账号和一个 API Key 即可统一计费调用。模型使用带提供商前缀的路由名称，例如 `openai/gpt-4o-mini`、`anthropic/claude-3.5-sonnet`。

由于 OpenRouter API 完全兼容 OpenAI 协议，`OpenRouterLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 OpenRouter 的鉴权信息、API 基础地址以及可选的归因请求头即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_openrouter_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_openrouter_llm'
description: 'user llm routing to OpenRouter models'
model_name: 'openai/gpt-4o-mini'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${OPENROUTER_API_KEY}'
api_base: 'https://openrouter.ai/api/v1'
proxy: '${OPENROUTER_PROXY}'
http_referer: 'https://your-app.example.com'
app_title: 'Your App Name'
max_context_length: 128000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.openrouter_llm'
  class: 'OpenRouterLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/openrouter_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'sk-or-v1-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${OPENROUTER_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="openrouter"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

OpenRouter 路由到来自多家提供商的数百个模型，因此该组件中没有硬编码固定的模型表。请在 [OpenRouter 模型页面](https://openrouter.ai/models) 浏览完整的模型目录（含价格与上下文窗口），并将带前缀的路由名称填入 `model_name`，例如：

| 模型名称                               | 上下文长度 |
| -------------------------------------- | ---------- |
| `openai/gpt-4o-mini`                   | 128000     |
| `openai/gpt-4o`                        | 128000     |
| `anthropic/claude-3.5-sonnet`          | 200000     |
| `google/gemini-flash-1.5`              | 1000000    |
| `meta-llama/llama-3.1-70b-instruct`    | 131072     |
| `deepseek/deepseek-chat`               | 64000      |

**重要提示**：不同路由模型的上下文窗口差异很大，请将 yaml 中的 `max_context_length` 字段设置为所选模型的官方文档值（如上例所示）。若未配置，`OpenRouterLLM` 会保守地回退到 8192 token 的默认值，这可以保证 prompt 预算检查的安全性，但会限制大上下文模型的充分发挥。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`OPENROUTER_API_KEY`
可选配置：`OPENROUTER_API_BASE`、`OPENROUTER_PROXY`、`OPENROUTER_HTTP_REFERER`、`OPENROUTER_APP_TITLE`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['OPENROUTER_API_KEY'] = 'sk-or-v1-***'
os.environ['OPENROUTER_API_BASE'] = 'https://openrouter.ai/api/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
OPENROUTER_API_KEY="sk-or-v1-******"
OPENROUTER_API_BASE="https://openrouter.ai/api/v1"
OPENROUTER_PROXY=""
OPENROUTER_HTTP_REFERER="https://your-app.example.com"
OPENROUTER_APP_TITLE="Your App Name"
```

---

## 4. OpenRouter API KEY 获取

1. 登录 [https://openrouter.ai](https://openrouter.ai)。
2. 进入 **Settings -> Keys**（https://openrouter.ai/settings/keys）页面并创建新的密钥。
3. 复制生成的 `sk-or-v1-...` 密钥，并赋值给 `OPENROUTER_API_KEY`。

计费、速率限制与充值说明详见 [OpenRouter 官方文档](https://openrouter.ai/docs)。

---

## 5. 归因请求头（可选）

OpenRouter 可以将您的 API 流量归因到您的应用，并在公开的 [rankings 排行榜](https://openrouter.ai/rankings) 页面展示。如需启用，请配置以下可选字段（或对应的环境变量）：

- `http_referer`：作为 `HTTP-Referer` 请求头发送，通常填写您站点的 URL。
- `app_title`：作为 `X-Title` 请求头发送，即应用的可读名称。

两者均为可选；均未设置时不发送任何额外请求头。其他任意请求头仍可以通过 `OpenAIStyleLLM` 通用的 `extra_headers` yaml 配置项传入，且其中的条目优先级高于上述专用字段。

---

## 6. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.openrouter_llm import OpenRouterLLM

llm = OpenRouterLLM(model_name='openai/gpt-4o-mini', max_context_length=128000)

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

由于 OpenRouter 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 7. Tips

- agentuniverse 源码中内置了一个 name 为 `default_openrouter_llm` 的模板配置（`openrouter_llm.yaml.example`），用户将其重命名为 `openrouter_llm.yaml` 并配置 `OPENROUTER_API_KEY` 之后即可直接使用。
- 在不同提供商之间切换通常只需修改 `model_name`（例如从 `openai/gpt-4o-mini` 切换到 `anthropic/claude-3.5-sonnet`）并同步调整 `max_context_length`，密钥与 API 地址保持不变。
- 使用大上下文模型时（例如 1M token 的 `google/gemini-flash-1.5`）请务必调大 `max_context_length`；在默认 8192 回退值下，agentUniverse 估算的 prompt 预算会远小于模型实际支持的窗口。
