# Cohere使用

`CohereLLM` 将 [Cohere](https://cohere.com) 的 API 接入 agentUniverse。Cohere 是 **Command** 系列大模型背后的企业级 LLM 公司，产品线包括提供 256k token 上下文窗口的旗舰模型 **command-a-03-2025**、面向检索增强（RAG）的 **command-r-plus** 与 **command-r**，以及高性价比的 **command-r7b**，在智能体工作流、工具调用与多语言 RAG 场景中表现出色。

Cohere 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.cohere.com/compatibility/v1`），因此 `CohereLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Cohere 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

说明：该地址是 Cohere 的 OpenAI 风格 *兼容* 接口，与其他 Cohere 组件（例如 Cohere rerank 文档处理器）使用的原生 Cohere 平台 API 相互独立。为本 LLM 配置的 `COHERE_API_BASE` 只作用于本组件。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_cohere_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_cohere_llm'
description: 'user cohere llm powered by the Cohere Command models'
model_name: 'command-a-03-2025'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${COHERE_API_KEY}'
api_base: 'https://api.cohere.com/compatibility/v1'
proxy: '${COHERE_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.cohere_llm'
  class: 'CohereLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/cohere_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'cohere-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${COHERE_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="cohere"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Cohere 会持续发布新的 Command 模型。下表列出了 Cohere 兼容 API 当前提供的对话模型及其上下文窗口大小（输入 + 输出 token，数值来自 Cohere 官方文档，仅供参考）。这些数值同样硬编码在 `CohereLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                | 上下文长度        |
| ----------------------- | ----------------- |
| `command-a-03-2025`     | 256000 (256k)     |
| `command-r-plus`        | 128000 (128k)     |
| `command-r`             | 128000 (128k)     |
| `command-r7b`           | 128000 (128k)     |

Cohere 为每个模型家族都会发布带日期的版本（`<模型名>-<月份>-<年份>`，例如 `command-r-plus-08-2024`、`command-r7b-12-2024`）。`CohereLLM` 会自动将日期后缀解析为基础模型家族的上下文窗口。

请以 [Cohere 官方模型文档](https://docs.cohere.com/docs/models) 公布的最新列表为准。如果某个模型不在上表中，`CohereLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`COHERE_API_KEY`
可选配置：`COHERE_API_BASE`、`COHERE_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['COHERE_API_KEY'] = 'cohere-***'
os.environ['COHERE_API_BASE'] = 'https://api.cohere.com/compatibility/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
COHERE_API_KEY="cohere-******"
COHERE_API_BASE="https://api.cohere.com/compatibility/v1"
COHERE_PROXY=""
```

---

## 4. Cohere API KEY 获取

1. 登录 [https://dashboard.cohere.com](https://dashboard.cohere.com)。
2. 进入 **API keys** 页面并创建新的密钥。
3. 复制生成的密钥，并赋值给 `COHERE_API_KEY`。

计费、速率限制与试用额度说明详见 [Cohere 官方文档](https://docs.cohere.com)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.cohere_llm import CohereLLM

llm = CohereLLM(model_name='command-a-03-2025')

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

由于 Cohere 兼容 API 与 OpenAI 协议兼容，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_cohere_llm` 的模板配置（`cohere_llm.yaml.example`），用户将其重命名为 `cohere_llm.yaml` 并配置 `COHERE_API_KEY` 之后即可直接使用。
- `command-a-03-2025` 提供 256k token 的上下文窗口，是复杂智能体工作流中最强的选择；`command-r-plus` / `command-r` 针对检索增强与工具调用优化，`command-r7b` 则以更低的延迟和成本换取一定的效果。
- Command 系列模型原生支持 23 种以上语言，非常适合需要覆盖非英语场景的 agentUniverse 智能体。
- 本 LLM 组件访问的是 OpenAI 兼容端点（`https://api.cohere.com/compatibility/v1`），与使用 Cohere 原生平台 API 的 Cohere rerank 文档处理器相互独立，两者可以在同一项目中并存配置。
