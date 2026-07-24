# Groq 使用

`GroqLLM` 将 [Groq Cloud](https://groq.com) 推理引擎接入 agentUniverse。Groq 基于自研的 **LPU（Language Processing Unit）** 硬件运行一批主流开源大模型（Meta Llama 3.x、Google Gemma 2、Mistral Mixtral 等），其 token 生成速度通常比传统 GPU 推理服务快一个数量级。

Groq 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.groq.com/openai/v1`），因此 `GroqLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Groq 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_groq_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_groq_llm'
description: 'user groq llm powered by the Groq LPU inference engine'
model_name: 'llama-3.3-70b-versatile'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${GROQ_API_KEY}'
api_base: 'https://api.groq.com/openai/v1'
organization: '${GROQ_ORGANIZATION}'
proxy: '${GROQ_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.groq_llm'
  class: 'GroqLLM'
```

**note:** `api_key` / `api_base` / `organization` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'gsk_***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${GROQ_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="groq"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Groq 会不定期轮换其支持的模型列表。下表列出了常用模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `GroqLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                          | 上下文长度      |
| --------------------------------- | --------------- |
| `llama-3.3-70b-versatile`         | 131072 (128k)   |
| `llama-3.1-8b-instant`            | 131072 (128k)   |
| `llama-3.1-70b-versatile`         | 131072 (128k)   |
| `llama3-70b-8192`                 | 8192            |
| `llama3-8b-8192`                  | 8192            |
| `mixtral-8x7b-32768`              | 32768           |
| `gemma2-9b-it`                    | 8192            |
| `gemma-7b-it`                     | 8192            |

请以 [Groq 官方模型文档](https://console.groq.com/docs/models) 公布的最新列表为准。如果某个模型不在上表中，`GroqLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`GROQ_API_KEY`
可选配置：`GROQ_API_BASE`、`GROQ_PROXY`、`GROQ_ORGANIZATION`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['GROQ_API_KEY'] = 'gsk_***'
os.environ['GROQ_API_BASE'] = 'https://api.groq.com/openai/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
GROQ_API_KEY="gsk_******"
GROQ_API_BASE="https://api.groq.com/openai/v1"
GROQ_ORGANIZATION=""
GROQ_PROXY=""
```

---

## 4. GROQ API KEY 获取

1. 登录 [https://console.groq.com](https://console.groq.com)。
2. 进入 **API Keys** -> **Create API Key**。
3. 复制生成的 `gsk_...` 密钥，并赋值给 `GROQ_API_KEY`。

Groq 为开发阶段提供了较为充裕的免费额度，生产环境的速率限制与计费规则详见 [https://console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.groq_llm import GroqLLM

llm = GroqLLM(model_name='llama-3.3-70b-versatile')

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

由于 Groq 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 已经内置了一个 name 为 `default_groq_llm` 的 llm，用户在配置 `GROQ_API_KEY` 之后可以直接使用。
- Groq 最大的特点是延迟极低：70B 级别的模型也能以每秒数百 token 的速度流式输出，非常适合交互式 Agent 和快速原型验证。
- Groq 目前并不支持上游厂商的全部模型，在正式选型前请先到 [Groq 模型页面](https://console.groq.com/docs/models) 确认可用模型及废弃公告。
